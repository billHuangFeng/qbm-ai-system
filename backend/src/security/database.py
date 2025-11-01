"""
BMOS系统 - 安全数据库操作
提供安全的数据库操作方法，防止SQL注入
"""

import asyncpg
from typing import Any, List, Dict, Optional, Union
import logging
from ..security.config import sanitize_sql_input
from ..exceptions import DatabaseError, ValidationError

logger = logging.getLogger(__name__)

class SecureDatabaseService:
    """安全数据库服务"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """初始化数据库连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )
            logger.info("数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise DatabaseError(f"数据库连接失败: {e}")
    
    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            logger.info("数据库连接池已关闭")
    
    async def execute_query(
        self, 
        query: str, 
        params: Optional[List[Any]] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Union[None, Dict[str, Any], List[Dict[str, Any]]]:
        """安全执行SQL查询"""
        
        if not self.pool:
            raise DatabaseError("数据库连接池未初始化")
        
        # 验证查询类型
        query_type = self._get_query_type(query)
        
        try:
            async with self.pool.acquire() as conn:
                if fetch_one:
                    if query_type == "SELECT":
                        result = await conn.fetchrow(query, *(params or []))
                        return dict(result) if result else None
                    else:
                        raise ValidationError("fetch_one只能用于SELECT查询")
                
                elif fetch_all:
                    if query_type == "SELECT":
                        results = await conn.fetch(query, *(params or []))
                        return [dict(row) for row in results]
                    else:
                        raise ValidationError("fetch_all只能用于SELECT查询")
                
                else:
                    # INSERT, UPDATE, DELETE
                    result = await conn.execute(query, *(params or []))
                    return result
        
        except asyncpg.exceptions.UniqueViolationError as e:
            logger.warning(f"唯一约束违反: {e}")
            raise DatabaseError("数据已存在，违反唯一约束")
        
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            logger.warning(f"外键约束违反: {e}")
            raise DatabaseError("外键约束违反")
        
        except asyncpg.exceptions.CheckViolationError as e:
            logger.warning(f"检查约束违反: {e}")
            raise DatabaseError("数据不符合约束条件")
        
        except Exception as e:
            logger.error(f"数据库查询失败: {e}")
            raise DatabaseError(f"数据库操作失败: {e}")
    
    async def execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """执行事务操作"""
        if not self.pool:
            raise DatabaseError("数据库连接池未初始化")
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for operation in operations:
                        query = operation.get("query")
                        params = operation.get("params", [])
                        
                        if not query:
                            raise ValidationError("事务操作缺少查询语句")
                        
                        await conn.execute(query, *params)
            
            logger.info(f"事务执行成功，包含{len(operations)}个操作")
            return True
        
        except Exception as e:
            logger.error(f"事务执行失败: {e}")
            raise DatabaseError(f"事务执行失败: {e}")
    
    async def batch_insert(
        self, 
        table: str, 
        columns: List[str], 
        data: List[List[Any]]
    ) -> int:
        """批量插入数据"""
        if not data:
            return 0
        
        # 构建安全的INSERT语句
        placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    result = await conn.executemany(query, data)
                    logger.info(f"批量插入成功，影响{result}行")
                    return result
        
        except Exception as e:
            logger.error(f"批量插入失败: {e}")
            raise DatabaseError(f"批量插入失败: {e}")
    
    async def safe_select(
        self,
        table: str,
        columns: List[str] = None,
        where_clause: str = None,
        where_params: List[Any] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None
    ) -> List[Dict[str, Any]]:
        """安全的SELECT查询"""
        
        # 构建查询
        select_columns = ", ".join(columns) if columns else "*"
        query = f"SELECT {select_columns} FROM {table}"
        params = []
        
        # 添加WHERE子句
        if where_clause:
            query += f" WHERE {where_clause}"
            params.extend(where_params or [])
        
        # 添加ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"
        
        # 添加LIMIT和OFFSET
        if limit:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
        
        return await self.execute_query(query, params, fetch_all=True)
    
    async def safe_insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """安全的INSERT操作"""
        
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join([f"${i+1}" for i in range(len(values))])
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
        
        result = await self.execute_query(query, values, fetch_one=True)
        return result
    
    async def safe_update(
        self,
        table: str,
        data: Dict[str, Any],
        where_clause: str,
        where_params: List[Any]
    ) -> int:
        """安全的UPDATE操作"""
        
        set_clauses = []
        params = []
        
        for i, (column, value) in enumerate(data.items()):
            set_clauses.append(f"{column} = ${i+1}")
            params.append(value)
        
        # 添加WHERE参数
        where_param_start = len(params) + 1
        for i, param in enumerate(where_params):
            params.append(param)
        
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"
        
        result = await self.execute_query(query, params)
        return result
    
    async def safe_delete(
        self,
        table: str,
        where_clause: str,
        where_params: List[Any]
    ) -> int:
        """安全的DELETE操作"""
        
        query = f"DELETE FROM {table} WHERE {where_clause}"
        result = await self.execute_query(query, where_params)
        return result
    
    def _get_query_type(self, query: str) -> str:
        """获取查询类型"""
        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            result = await self.execute_query("SELECT 1", fetch_one=True)
            return result is not None
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

# 全局数据库服务实例
db_service: Optional[SecureDatabaseService] = None

async def get_db_service() -> SecureDatabaseService:
    """获取数据库服务实例"""
    global db_service
    if not db_service:
        raise DatabaseError("数据库服务未初始化")
    return db_service

async def init_db_service(database_url: str):
    """初始化数据库服务"""
    global db_service
    db_service = SecureDatabaseService(database_url)
    await db_service.initialize()

async def close_db_service():
    """关闭数据库服务"""
    global db_service
    if db_service:
        await db_service.close()
        db_service = None

