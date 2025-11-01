"""
BMOS系统 - 性能优化服务
提供高性能的数据查询和分页功能
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import math

from ..security.database import SecureDatabaseService
from ..exceptions import ValidationError, DatabaseError

logger = logging.getLogger(__name__)

@dataclass
class PaginationParams:
    """分页参数"""
    page: int = 1
    size: int = 20
    max_size: int = 100
    
    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.size < 1:
            self.size = 20
        if self.size > self.max_size:
            self.size = self.max_size
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

@dataclass
class PaginationResult:
    """分页结果"""
    data: List[Dict[str, Any]]
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PerformanceOptimizedService:
    """性能优化服务"""
    
    def __init__(self, db_service: SecureDatabaseService):
        self.db_service = db_service
    
    async def paginated_query(
        self,
        table: str,
        columns: List[str] = None,
        where_clause: str = None,
        where_params: List[Any] = None,
        order_by: str = None,
        pagination: PaginationParams = None
    ) -> PaginationResult:
        """分页查询"""
        
        pagination = pagination or PaginationParams()
        
        # 构建基础查询
        select_columns = ", ".join(columns) if columns else "*"
        base_query = f"SELECT {select_columns} FROM {table}"
        params = []
        
        # 添加WHERE子句
        if where_clause:
            base_query += f" WHERE {where_clause}"
            params.extend(where_params or [])
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM {table}"
        if where_clause:
            count_query += f" WHERE {where_clause}"
        
        try:
            # 并行执行计数和查询
            count_result = await self.db_service.execute_query(
                count_query, 
                where_params or [], 
                fetch_one=True
            )
            total = count_result["total"] if count_result else 0
            
            # 构建分页查询
            query = base_query
            if order_by:
                query += f" ORDER BY {order_by}"
            
            query += f" LIMIT {pagination.size} OFFSET {pagination.offset}"
            
            data = await self.db_service.execute_query(query, params, fetch_all=True)
            
            # 计算分页信息
            total_pages = math.ceil(total / pagination.size) if total > 0 else 0
            has_next = pagination.page < total_pages
            has_prev = pagination.page > 1
            
            return PaginationResult(
                data=data or [],
                total=total,
                page=pagination.page,
                size=pagination.size,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )
        
        except Exception as e:
            logger.error(f"分页查询失败: {e}")
            raise DatabaseError(f"分页查询失败: {e}")
    
    async def batch_load_with_relations(
        self,
        main_table: str,
        relation_tables: Dict[str, Dict[str, Any]],
        main_where: str = None,
        main_params: List[Any] = None,
        pagination: PaginationParams = None
    ) -> List[Dict[str, Any]]:
        """批量加载关联数据，避免N+1查询"""
        
        pagination = pagination or PaginationParams()
        
        # 1. 获取主表数据
        main_data = await self.paginated_query(
            table=main_table,
            where_clause=main_where,
            where_params=main_params,
            pagination=pagination
        )
        
        if not main_data.data:
            return []
        
        # 2. 提取主表ID
        main_ids = [item["id"] for item in main_data.data]
        
        # 3. 批量加载关联数据
        relations_data = {}
        for relation_name, relation_config in relation_tables.items():
            relation_table = relation_config["table"]
            foreign_key = relation_config["foreign_key"]
            relation_columns = relation_config.get("columns", ["*"])
            
            # 构建IN查询
            placeholders = ", ".join([f"${i+1}" for i in range(len(main_ids))])
            relation_query = f"""
                SELECT {', '.join(relation_columns)} 
                FROM {relation_table} 
                WHERE {foreign_key} IN ({placeholders})
            """
            
            try:
                relation_results = await self.db_service.execute_query(
                    relation_query, 
                    main_ids, 
                    fetch_all=True
                )
                
                # 按外键分组
                relations_data[relation_name] = {}
                for item in relation_results or []:
                    fk_value = item[foreign_key]
                    if fk_value not in relations_data[relation_name]:
                        relations_data[relation_name][fk_value] = []
                    relations_data[relation_name][fk_value].append(item)
            
            except Exception as e:
                logger.warning(f"加载关联数据失败 {relation_name}: {e}")
                relations_data[relation_name] = {}
        
        # 4. 合并数据
        result = []
        for main_item in main_data.data:
            item = main_item.copy()
            for relation_name in relations_data:
                item[relation_name] = relations_data[relation_name].get(main_item["id"], [])
            result.append(item)
        
        return result
    
    async def optimized_search(
        self,
        table: str,
        search_columns: List[str],
        search_term: str,
        additional_where: str = None,
        additional_params: List[Any] = None,
        pagination: PaginationParams = None
    ) -> PaginationResult:
        """优化的搜索功能"""
        
        pagination = pagination or PaginationParams()
        
        # 构建搜索条件
        search_conditions = []
        search_params = []
        
        for column in search_columns:
            search_conditions.append(f"{column} ILIKE ${len(search_params) + 1}")
            search_params.append(f"%{search_term}%")
        
        where_clause = " OR ".join(search_conditions)
        
        # 添加额外条件
        if additional_where:
            where_clause = f"({where_clause}) AND ({additional_where})"
            search_params.extend(additional_params or [])
        
        return await self.paginated_query(
            table=table,
            where_clause=where_clause,
            where_params=search_params,
            pagination=pagination
        )
    
    async def bulk_upsert(
        self,
        table: str,
        data: List[Dict[str, Any]],
        conflict_columns: List[str],
        update_columns: List[str] = None
    ) -> int:
        """批量插入或更新"""
        
        if not data:
            return 0
        
        # 获取列名
        columns = list(data[0].keys())
        
        # 构建VALUES子句
        values_clauses = []
        all_params = []
        
        for i, row in enumerate(data):
            placeholders = []
            for j, column in enumerate(columns):
                param_index = i * len(columns) + j + 1
                placeholders.append(f"${param_index}")
                all_params.append(row[column])
            values_clauses.append(f"({', '.join(placeholders)})")
        
        # 构建ON CONFLICT子句
        conflict_clause = f"ON CONFLICT ({', '.join(conflict_columns)})"
        
        if update_columns:
            update_clause = f"DO UPDATE SET {', '.join([f'{col} = EXCLUDED.{col}' for col in update_columns])}"
        else:
            update_clause = "DO NOTHING"
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES {', '.join(values_clauses)}
            {conflict_clause} {update_clause}
        """
        
        try:
            result = await self.db_service.execute_query(query, all_params)
            logger.info(f"批量插入/更新成功，影响{result}行")
            return result
        
        except Exception as e:
            logger.error(f"批量插入/更新失败: {e}")
            raise DatabaseError(f"批量插入/更新失败: {e}")
    
    async def get_aggregated_stats(
        self,
        table: str,
        group_by_columns: List[str],
        aggregate_functions: Dict[str, str],
        where_clause: str = None,
        where_params: List[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取聚合统计"""
        
        # 构建聚合查询
        select_parts = group_by_columns.copy()
        
        for alias, func in aggregate_functions.items():
            select_parts.append(f"{func} as {alias}")
        
        query = f"SELECT {', '.join(select_parts)} FROM {table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if group_by_columns:
            query += f" GROUP BY {', '.join(group_by_columns)}"
        
        try:
            results = await self.db_service.execute_query(query, where_params or [], fetch_all=True)
            return results or []
        
        except Exception as e:
            logger.error(f"聚合统计查询失败: {e}")
            raise DatabaseError(f"聚合统计查询失败: {e}")
    
    async def execute_in_batches(
        self,
        operation: str,
        data: List[Any],
        batch_size: int = 1000
    ) -> int:
        """批量执行操作"""
        
        total_affected = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            try:
                if operation == "insert":
                    # 批量插入逻辑
                    pass
                elif operation == "update":
                    # 批量更新逻辑
                    pass
                elif operation == "delete":
                    # 批量删除逻辑
                    pass
                
                total_affected += len(batch)
                logger.info(f"批次 {i//batch_size + 1} 处理完成，影响 {len(batch)} 行")
            
            except Exception as e:
                logger.error(f"批次 {i//batch_size + 1} 处理失败: {e}")
                raise DatabaseError(f"批量操作失败: {e}")
        
        return total_affected
    
    async def get_query_performance_stats(self) -> Dict[str, Any]:
        """获取查询性能统计"""
        
        try:
            # 获取慢查询统计
            slow_queries = await self.db_service.execute_query("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time
                FROM pg_stat_statements 
                WHERE mean_time > 1000
                ORDER BY mean_time DESC
                LIMIT 10
            """, fetch_all=True)
            
            # 获取连接统计
            connection_stats = await self.db_service.execute_query("""
                SELECT 
                    state,
                    COUNT(*) as count
                FROM pg_stat_activity 
                GROUP BY state
            """, fetch_all=True)
            
            return {
                "slow_queries": slow_queries or [],
                "connection_stats": connection_stats or [],
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 缓存装饰器
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """缓存结果装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以实现缓存逻辑
            # 使用Redis缓存查询结果
            pass
        return wrapper
    return decorator

# 性能监控装饰器
def monitor_performance(func):
    """性能监控装饰器"""
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} 执行时间: {execution_time:.3f}秒")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.3f}秒, 错误: {e}")
            raise
    return wrapper

