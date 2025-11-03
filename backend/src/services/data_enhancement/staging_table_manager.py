"""
数据增强服务 - 暂存表管理
动态创建和管理暂存表

功能：
- 动态创建暂存表（基于数据类型和目标表结构）
- 数据迁移（暂存表 → 正式表）
- 暂存表清理（定期清理过期数据）
- 事务管理（确保数据一致性）
"""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import uuid
from datetime import datetime, timedelta

from ...security.database import SecureDatabaseService
from ...error_handling.unified import BMOSError, BusinessError
from ...services.base import BaseService, ServiceConfig

logger = logging.getLogger(__name__)


class StagingTableError(BMOSError):
    """暂存表管理错误"""
    pass


class StagingTableManager(BaseService):
    """暂存表管理服务"""
    
    def __init__(
        self,
        db_service: SecureDatabaseService,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, config=config)
        self.default_retention_days = 7  # 默认保留7天
    
    def generate_staging_table_name(
        self,
        data_type: str,
        tenant_id: str
    ) -> str:
        """
        生成暂存表名称
        
        Args:
            data_type: 数据类型（order/production/expense）
            tenant_id: 租户ID
            
        Returns:
            暂存表名称
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4()).replace("-", "")[:8]
        return f"staging_{data_type}_{timestamp}_{unique_id}"
    
    async def get_target_table_schema(
        self,
        target_table: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        获取目标表的结构
        
        Args:
            target_table: 目标表名
            tenant_id: 租户ID
            
        Returns:
            表结构信息
        """
        try:
            query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1
                  AND table_name = $2
                ORDER BY ordinal_position
            """
            
            # 获取schema（假设使用tenant schema）
            schema_name = f"tenant_{tenant_id.replace('-', '_')}"
            
            results = await self.db_service.execute_query(
                query,
                params=[schema_name, target_table],
                fetch_all=True
            )
            
            return results
            
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            raise StagingTableError(f"获取表结构失败: {e}")
    
    async def create_staging_table(
        self,
        data_type: str,
        target_table: str,
        tenant_id: str,
        schema: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        动态创建暂存表
        
        Args:
            data_type: 数据类型（order/production/expense）
            target_table: 目标表名
            tenant_id: 租户ID
            schema: 表结构（如果为None，则从目标表获取）
            
        Returns:
            创建结果
        """
        try:
            # 生成暂存表名
            staging_table_name = self.generate_staging_table_name(data_type, tenant_id)
            
            # 获取表结构
            if not schema:
                schema = await self.get_target_table_schema(target_table, tenant_id)
            
            if not schema:
                raise StagingTableError(f"无法获取目标表 {target_table} 的结构")
            
            # 构建CREATE TABLE语句
            schema_name = f"tenant_{tenant_id.replace('-', '_')}"
            column_definitions = []
            
            for col in schema:
                col_name = col["column_name"]
                col_type = col["data_type"]
                is_nullable = col["is_nullable"] == "YES"
                default = col.get("column_default")
                
                # 映射PostgreSQL数据类型
                type_mapping = {
                    "character varying": "VARCHAR",
                    "character": "CHAR",
                    "integer": "INTEGER",
                    "bigint": "BIGINT",
                    "numeric": "NUMERIC",
                    "decimal": "DECIMAL",
                    "double precision": "DOUBLE PRECISION",
                    "timestamp without time zone": "TIMESTAMP",
                    "timestamp with time zone": "TIMESTAMPTZ",
                    "date": "DATE",
                    "boolean": "BOOLEAN",
                    "text": "TEXT",
                    "uuid": "UUID"
                }
                
                pg_type = type_mapping.get(col_type.lower(), "TEXT")
                
                col_def = f'"{col_name}" {pg_type}'
                
                if not is_nullable and default is None:
                    col_def += " NOT NULL"
                
                if default:
                    col_def += f" DEFAULT {default}"
                
                column_definitions.append(col_def)
            
            # 添加元数据字段
            column_definitions.extend([
                '"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                '"tenant_id" VARCHAR(255)',
                '"status" VARCHAR(50) DEFAULT \'pending\''
            ])
            
            # 构建完整的CREATE TABLE语句
            create_sql = f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.{staging_table_name} (
                    {', '.join(column_definitions)}
                )
            """
            
            # 执行创建语句
            await self.db_service.execute_query(create_sql)
            
            logger.info(f"暂存表创建成功: {staging_table_name}")
            
            return {
                "staging_table_name": staging_table_name,
                "schema_name": schema_name,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "columns": len(column_definitions)
            }
            
        except Exception as e:
            logger.error(f"创建暂存表失败: {e}")
            raise StagingTableError(f"创建暂存表失败: {e}")
    
    async def insert_to_staging(
        self,
        staging_table_name: str,
        schema_name: str,
        records: List[Dict[str, Any]],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        插入数据到暂存表
        
        Args:
            staging_table_name: 暂存表名
            schema_name: Schema名
            records: 数据记录列表
            tenant_id: 租户ID
            
        Returns:
            插入结果
        """
        try:
            if not records:
                return {
                    "row_count": 0,
                    "status": "success"
                }
            
            # 转换为DataFrame
            df = pd.DataFrame(records)
            
            # 添加元数据
            df["tenant_id"] = tenant_id
            df["created_at"] = datetime.now()
            df["status"] = "pending"
            
            # 插入数据（使用批量插入）
            # 注意：这里简化处理，实际应该使用更安全的批量插入方法
            
            inserted_count = 0
            for record in df.to_dict('records'):
                # 构建INSERT语句
                columns = list(record.keys())
                values = list(record.values())
                placeholders = [f"${i+1}" for i in range(len(values))]
                
                insert_sql = f"""
                    INSERT INTO {schema_name}.{staging_table_name} 
                    ({', '.join(f'"{col}"' for col in columns)})
                    VALUES ({', '.join(placeholders)})
                """
                
                await self.db_service.execute_query(
                    insert_sql,
                    params=values
                )
                inserted_count += 1
            
            logger.info(f"插入 {inserted_count} 条记录到暂存表 {staging_table_name}")
            
            return {
                "row_count": inserted_count,
                "status": "success",
                "staging_table_name": staging_table_name
            }
            
        except Exception as e:
            logger.error(f"插入暂存表失败: {e}")
            raise StagingTableError(f"插入暂存表失败: {e}")
    
    async def migrate_to_target(
        self,
        staging_table_name: str,
        schema_name: str,
        target_table: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        从暂存表迁移数据到正式表
        
        Args:
            staging_table_name: 暂存表名
            schema_name: Schema名
            target_table: 目标表名
            tenant_id: 租户ID
            
        Returns:
            迁移结果
        """
        try:
            # 获取暂存表数据数量
            count_query = f"""
                SELECT COUNT(*) as count
                FROM {schema_name}.{staging_table_name}
                WHERE tenant_id = $1 AND status = 'pending'
            """
            
            count_result = await self.db_service.execute_query(
                count_query,
                params=[tenant_id],
                fetch_one=True
            )
            
            row_count = count_result.get("count", 0) if count_result else 0
            
            if row_count == 0:
                return {
                    "migrated_count": 0,
                    "status": "success",
                    "message": "暂存表中没有待迁移的数据"
                }
            
            # 获取目标表列名
            schema = await self.get_target_table_schema(target_table, tenant_id)
            target_columns = [col["column_name"] for col in schema if col["column_name"] not in ["created_at", "tenant_id", "status"]]
            
            # 构建INSERT ... SELECT语句
            staging_columns = ', '.join(f'"{col}"' for col in target_columns)
            target_columns_str = ', '.join(f'"{col}"' for col in target_columns)
            
            migrate_sql = f"""
                INSERT INTO {schema_name}.{target_table} 
                ({target_columns_str}, tenant_id, created_at)
                SELECT {staging_columns}, tenant_id, created_at
                FROM {schema_name}.{staging_table_name}
                WHERE tenant_id = $1 AND status = 'pending'
            """
            
            # 执行迁移（使用事务）
            operations = [
                {
                    "query": migrate_sql,
                    "params": [tenant_id]
                },
                {
                    "query": f"""
                        UPDATE {schema_name}.{staging_table_name}
                        SET status = 'migrated'
                        WHERE tenant_id = $1 AND status = 'pending'
                    """,
                    "params": [tenant_id]
                }
            ]
            
            try:
                await self.db_service.execute_transaction(operations)
            except Exception as e:
                logger.error(f"数据迁移事务失败: {e}")
                raise
            
            logger.info(f"从暂存表 {staging_table_name} 迁移 {row_count} 条记录到 {target_table}")
            
            return {
                "migrated_count": row_count,
                "status": "success",
                "staging_table_name": staging_table_name,
                "target_table": target_table
            }
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            raise StagingTableError(f"数据迁移失败: {e}")
    
    async def cleanup_staging_tables(
        self,
        tenant_id: str,
        retention_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        清理过期的暂存表
        
        Args:
            tenant_id: 租户ID
            retention_days: 保留天数（默认7天）
            
        Returns:
            清理结果
        """
        try:
            if retention_days is None:
                retention_days = self.default_retention_days
            
            schema_name = f"tenant_{tenant_id.replace('-', '_')}"
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # 查找所有暂存表
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = $1
                  AND table_name LIKE 'staging_%'
                  AND table_type = 'BASE TABLE'
            """
            
            staging_tables = await self.db_service.execute_query(
                query,
                params=[schema_name],
                fetch_all=True
            )
            
            cleaned_count = 0
            cleaned_tables = []
            
            for table_info in staging_tables:
                table_name = table_info["table_name"]
                
                # 检查表创建时间
                check_query = f"""
                    SELECT MIN(created_at) as oldest_date
                    FROM {schema_name}.{table_name}
                    WHERE tenant_id = $1
                """
                
                result = await self.db_service.execute_query(
                    check_query,
                    params=[tenant_id],
                    fetch_one=True
                )
                
                if result and result.get("oldest_date"):
                    oldest_date = result["oldest_date"]
                    if isinstance(oldest_date, str):
                        oldest_date = datetime.fromisoformat(oldest_date.replace('Z', '+00:00'))
                    
                    if oldest_date < cutoff_date:
                        # 删除表
                        drop_sql = f"DROP TABLE IF EXISTS {schema_name}.{table_name}"
                        await self.db_service.execute_query(drop_sql)
                        
                        cleaned_count += 1
                        cleaned_tables.append(table_name)
            
            logger.info(f"清理了 {cleaned_count} 个过期暂存表")
            
            return {
                "cleaned_count": cleaned_count,
                "cleaned_tables": cleaned_tables,
                "retention_days": retention_days
            }
            
        except Exception as e:
            logger.error(f"清理暂存表失败: {e}")
            raise StagingTableError(f"清理暂存表失败: {e}")
    
    async def manage_staging(
        self,
        data_type: str,
        tenant_id: str,
        operation: str,
        target_table: Optional[str] = None,
        staging_table_name: Optional[str] = None,
        records: Optional[List[Dict[str, Any]]] = None,
        retention_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        管理暂存表（统一接口）
        
        Args:
            data_type: 数据类型（order/production/expense）
            tenant_id: 租户ID
            operation: 操作类型（create/migrate/cleanup）
            target_table: 目标表名（create和migrate时需要）
            staging_table_name: 暂存表名（migrate时需要）
            records: 数据记录（create时需要）
            retention_days: 保留天数（cleanup时需要）
            
        Returns:
            操作结果
        """
        try:
            if operation == "create":
                if not target_table:
                    raise StagingTableError("create操作需要target_table参数")
                
                result = await self.create_staging_table(
                    data_type,
                    target_table,
                    tenant_id
                )
                
                staging_table_name = result["staging_table_name"]
                schema_name = result["schema_name"]
                
                # 如果有数据，插入到暂存表
                if records:
                    insert_result = await self.insert_to_staging(
                        staging_table_name,
                        schema_name,
                        records,
                        tenant_id
                    )
                    result["row_count"] = insert_result["row_count"]
                
                return result
            
            elif operation == "migrate":
                if not staging_table_name or not target_table:
                    raise StagingTableError("migrate操作需要staging_table_name和target_table参数")
                
                schema_name = f"tenant_{tenant_id.replace('-', '_')}"
                
                return await self.migrate_to_target(
                    staging_table_name,
                    schema_name,
                    target_table,
                    tenant_id
                )
            
            elif operation == "cleanup":
                return await self.cleanup_staging_tables(
                    tenant_id,
                    retention_days
                )
            
            else:
                raise StagingTableError(f"不支持的操作类型: {operation}")
            
        except Exception as e:
            logger.error(f"暂存表管理失败: {e}")
            raise StagingTableError(f"暂存表管理失败: {e}")

