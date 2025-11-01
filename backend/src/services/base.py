"""
BMOS系统 - 基础服务类
提供通用的服务基类，减少重复代码
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

from ..security.database import SecureDatabaseService
from ..security.config import security_settings
from ..error_handling.unified import BMOSError, BusinessError, handle_errors, business_error_handler

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class ServiceConfig:
    """服务配置"""
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_logging: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0

class BaseService(ABC):
    """基础服务类"""
    
    def __init__(
        self, 
        db_service: SecureDatabaseService,
        cache_service: Optional[Any] = None,
        config: Optional[ServiceConfig] = None
    ):
        self.db_service = db_service
        self.cache_service = cache_service
        self.config = config or ServiceConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @handle_errors
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            db_healthy = await self.db_service.health_check()
            cache_healthy = await self._check_cache_health() if self.cache_service else True
            
            return {
                "service": self.__class__.__name__,
                "status": "healthy" if db_healthy and cache_healthy else "unhealthy",
                "database": "connected" if db_healthy else "disconnected",
                "cache": "connected" if cache_healthy else "disconnected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                "service": self.__class__.__name__,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_cache_health(self) -> bool:
        """检查缓存健康状态"""
        try:
            if self.cache_service:
                await self.cache_service.ping()
                return True
        except Exception as e:
            self.logger.warning(f"缓存健康检查失败: {e}")
        return False
    
    @handle_errors
    async def get_by_id(self, table: str, id_value: Any, columns: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """根据ID获取记录"""
        return await self.db_service.safe_select(
            table=table,
            columns=columns,
            where_clause="id = $1",
            where_params=[id_value]
        )
    
    @handle_errors
    async def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建记录"""
        return await self.db_service.safe_insert(table, data)
    
    @handle_errors
    async def update_record(self, table: str, id_value: Any, data: Dict[str, Any]) -> int:
        """更新记录"""
        data["updated_at"] = datetime.now()
        return await self.db_service.safe_update(
            table=table,
            data=data,
            where_clause="id = $1",
            where_params=[id_value]
        )
    
    @handle_errors
    async def delete_record(self, table: str, id_value: Any) -> int:
        """删除记录"""
        return await self.db_service.safe_delete(
            table=table,
            where_clause="id = $1",
            where_params=[id_value]
        )
    
    @handle_errors
    async def list_records(
        self, 
        table: str, 
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """列出记录"""
        return await self.db_service.safe_select(
            table=table,
            where_clause=where_clause,
            where_params=where_params,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
    
    async def _get_cached(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.config.enable_caching or not self.cache_service:
            return None
        
        try:
            return await self.cache_service.get(key)
        except Exception as e:
            self.logger.warning(f"获取缓存失败: {e}")
            return None
    
    async def _set_cached(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.config.enable_caching or not self.cache_service:
            return False
        
        try:
            await self.cache_service.set(key, value, ttl or self.config.cache_ttl)
            return True
        except Exception as e:
            self.logger.warning(f"设置缓存失败: {e}")
            return False
    
    async def _retry_operation(self, operation, *args, **kwargs):
        """重试操作"""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    self.logger.warning(f"操作失败，重试 {attempt + 1}/{self.config.max_retries}: {e}")
                else:
                    self.logger.error(f"操作最终失败: {e}")
        
        raise last_exception

class CRUDService(BaseService, Generic[T]):
    """CRUD服务基类"""
    
    def __init__(
        self, 
        db_service: SecureDatabaseService,
        table_name: str,
        cache_service: Optional[Any] = None,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, cache_service, config)
        self.table_name = table_name
    
    @business_error_handler
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建记录"""
        # 添加创建时间
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        
        result = await self.create_record(self.table_name, data)
        
        # 清除相关缓存
        await self._clear_related_cache()
        
        return result
    
    @business_error_handler
    async def get_by_id(self, id_value: Any) -> Optional[Dict[str, Any]]:
        """根据ID获取记录"""
        cache_key = f"{self.table_name}:{id_value}"
        
        # 尝试从缓存获取
        cached_result = await self._get_cached(cache_key)
        if cached_result:
            return cached_result
        
        # 从数据库获取
        result = await self.get_by_id(self.table_name, id_value)
        
        # 缓存结果
        if result:
            await self._set_cached(cache_key, result)
        
        return result
    
    @business_error_handler
    async def update(self, id_value: Any, data: Dict[str, Any]) -> bool:
        """更新记录"""
        affected_rows = await self.update_record(self.table_name, id_value, data)
        
        if affected_rows > 0:
            # 清除相关缓存
            await self._clear_related_cache()
            await self._clear_record_cache(id_value)
            return True
        
        return False
    
    @business_error_handler
    async def delete(self, id_value: Any) -> bool:
        """删除记录"""
        affected_rows = await self.delete_record(self.table_name, id_value)
        
        if affected_rows > 0:
            # 清除相关缓存
            await self._clear_related_cache()
            await self._clear_record_cache(id_value)
            return True
        
        return False
    
    @business_error_handler
    async def list_all(
        self, 
        where_clause: Optional[str] = None,
        where_params: Optional[List[Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """列出所有记录"""
        cache_key = self._generate_list_cache_key(where_clause, where_params, order_by, limit, offset)
        
        # 尝试从缓存获取
        cached_result = await self._get_cached(cache_key)
        if cached_result:
            return cached_result
        
        # 从数据库获取
        result = await self.list_records(
            table=self.table_name,
            where_clause=where_clause,
            where_params=where_params,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        
        # 缓存结果
        await self._set_cached(cache_key, result)
        
        return result
    
    async def _clear_record_cache(self, id_value: Any):
        """清除单条记录缓存"""
        cache_key = f"{self.table_name}:{id_value}"
        if self.cache_service:
            await self.cache_service.delete(cache_key)
    
    async def _clear_related_cache(self):
        """清除相关缓存"""
        if self.cache_service:
            # 清除列表缓存
            pattern = f"{self.table_name}:list:*"
            await self.cache_service.delete_pattern(pattern)
    
    def _generate_list_cache_key(
        self, 
        where_clause: Optional[str], 
        where_params: Optional[List[Any]], 
        order_by: Optional[str], 
        limit: Optional[int], 
        offset: Optional[int]
    ) -> str:
        """生成列表缓存键"""
        key_parts = [self.table_name, "list"]
        
        if where_clause:
            key_parts.append(f"where:{hash(where_clause)}")
        if where_params:
            key_parts.append(f"params:{hash(str(where_params))}")
        if order_by:
            key_parts.append(f"order:{hash(order_by)}")
        if limit:
            key_parts.append(f"limit:{limit}")
        if offset:
            key_parts.append(f"offset:{offset}")
        
        return ":".join(key_parts)

class BusinessService(BaseService):
    """业务服务基类"""
    
    def __init__(
        self, 
        db_service: SecureDatabaseService,
        cache_service: Optional[Any] = None,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, cache_service, config)
    
    @abstractmethod
    async def process_business_logic(self, *args, **kwargs) -> Any:
        """处理业务逻辑（子类必须实现）"""
        pass
    
    @business_error_handler
    async def execute_business_operation(self, operation_name: str, *args, **kwargs) -> Any:
        """执行业务操作"""
        self.logger.info(f"开始执行业务操作: {operation_name}")
        
        try:
            result = await self.process_business_logic(*args, **kwargs)
            self.logger.info(f"业务操作 {operation_name} 执行成功")
            return result
        except Exception as e:
            self.logger.error(f"业务操作 {operation_name} 执行失败: {e}")
            raise BusinessError(f"业务操作 {operation_name} 执行失败: {e}")
    
    async def validate_business_rules(self, data: Dict[str, Any]) -> List[str]:
        """验证业务规则（子类可重写）"""
        return []
    
    async def pre_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理数据（子类可重写）"""
        return data
    
    async def post_process(self, result: Any) -> Any:
        """后处理结果（子类可重写）"""
        return result

class CacheableService(BaseService):
    """可缓存服务基类"""
    
    def __init__(
        self, 
        db_service: SecureDatabaseService,
        cache_service: Optional[Any] = None,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, cache_service, config)
        self.cache_prefix = self.__class__.__name__.lower()
    
    def _get_cache_key(self, operation: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [self.cache_prefix, operation]
        
        # 添加参数到缓存键
        if args:
            key_parts.append(f"args:{hash(str(args))}")
        if kwargs:
            key_parts.append(f"kwargs:{hash(str(sorted(kwargs.items())))}")
        
        return ":".join(key_parts)
    
    async def cached_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """缓存操作"""
        cache_key = self._get_cache_key(operation_name, *args, **kwargs)
        
        # 尝试从缓存获取
        cached_result = await self._get_cached(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 执行操作
        result = await operation_func(*args, **kwargs)
        
        # 缓存结果
        await self._set_cached(cache_key, result)
        
        return result
    
    async def invalidate_cache(self, pattern: Optional[str] = None):
        """使缓存失效"""
        if not self.cache_service:
            return
        
        if pattern:
            await self.cache_service.delete_pattern(pattern)
        else:
            await self.cache_service.delete_pattern(f"{self.cache_prefix}:*")

# 服务工厂
class ServiceFactory:
    """服务工厂"""
    
    _services = {}
    
    @classmethod
    def register_service(cls, name: str, service_class):
        """注册服务"""
        cls._services[name] = service_class
    
    @classmethod
    def create_service(cls, name: str, *args, **kwargs):
        """创建服务实例"""
        if name not in cls._services:
            raise ValueError(f"未注册的服务: {name}")
        
        service_class = cls._services[name]
        return service_class(*args, **kwargs)
    
    @classmethod
    def get_registered_services(cls):
        """获取已注册的服务"""
        return list(cls._services.keys())

# 服务注册装饰器
def register_service(name: str):
    """服务注册装饰器"""
    def decorator(cls):
        ServiceFactory.register_service(name, cls)
        return cls
    return decorator

