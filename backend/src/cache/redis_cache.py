"""
Redis缓存服务
提供高性能的缓存功能
"""

import redis.asyncio as redis
import json
import pickle
import logging
from typing import Any, Optional, Union, List, Dict
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from ..error_handling.unified import handle_errors, BMOSError, BusinessError
from ..logging_config import get_logger

logger = get_logger("redis_cache")

class RedisCache:
    """Redis缓存服务"""
    
    def __init__(self, redis_url: str, password: Optional[str] = None):
        self.redis_url = redis_url
        self.password = password
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        
    @handle_errors
    async def connect(self):
        """建立Redis连接"""
        try:
            # 解析Redis URL
            if self.password:
                # 如果URL中没有密码，添加密码
                if "://:" not in self.redis_url:
                    self.redis_url = self.redis_url.replace("://", f"://:{self.password}@")
            
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # 测试连接
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.is_connected = False
            raise BusinessError(
                code="REDIS_CONNECTION_FAILED",
                message=f"Redis连接失败: {str(e)}"
            )
    
    @handle_errors
    async def disconnect(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Redis连接已关闭")
    
    @handle_errors
    async def health_check(self) -> bool:
        """检查Redis连接健康状态"""
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False
    
    @handle_errors
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            serialize: 是否序列化
        """
        if not self.is_connected:
            raise BusinessError(
                code="REDIS_NOT_CONNECTED",
                message="Redis未连接"
            )
        
        try:
            # 序列化值
            if serialize:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_value = str(value)
            else:
                serialized_value = value
            
            # 设置缓存
            if ttl:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            
            logger.debug(f"设置缓存: {key}")
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            raise BusinessError(
                code="CACHE_SET_FAILED",
                message=f"设置缓存失败: {str(e)}"
            )
    
    @handle_errors
    async def get(
        self, 
        key: str, 
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            deserialize: 是否反序列化
            default: 默认值
        """
        if not self.is_connected:
            return default
        
        try:
            value = await self.redis_client.get(key)
            
            if value is None:
                return default
            
            # 反序列化值
            if deserialize:
                try:
                    # 尝试JSON反序列化
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # 如果不是JSON，返回原始值
                    return value
            else:
                return value
                
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return default
    
    @handle_errors
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            logger.debug(f"删除缓存: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    @handle_errors
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查缓存存在性失败: {e}")
            return False
    
    @handle_errors
    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        if not self.is_connected:
            return False
        
        try:
            result = await self.redis_client.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"设置缓存过期时间失败: {e}")
            return False
    
    @handle_errors
    async def ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        if not self.is_connected:
            return -1
        
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"获取缓存TTL失败: {e}")
            return -1
    
    @handle_errors
    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键列表"""
        if not self.is_connected:
            return []
        
        try:
            keys = await self.redis_client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            return []
    
    @handle_errors
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.flushdb()
            logger.info("Redis数据库已清空")
            return True
        except Exception as e:
            logger.error(f"清空数据库失败: {e}")
            return False
    
    @handle_errors
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        if not self.is_connected:
            return {}
        
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            for i, key in enumerate(keys):
                if values[i] is not None:
                    try:
                        result[key] = json.loads(values[i])
                    except (json.JSONDecodeError, TypeError):
                        result[key] = values[i]
            return result
        except Exception as e:
            logger.error(f"批量获取缓存失败: {e}")
            return {}
    
    @handle_errors
    async def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        if not self.is_connected:
            return False
        
        try:
            # 序列化值
            serialized_mapping = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[key] = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_mapping[key] = str(value)
            
            await self.redis_client.mset(serialized_mapping)
            
            # 设置过期时间
            if ttl:
                for key in mapping.keys():
                    await self.redis_client.expire(key, ttl)
            
            logger.debug(f"批量设置缓存: {len(mapping)} 个键")
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False
    
    @handle_errors
    async def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        if not self.is_connected:
            return 0
        
        try:
            result = await self.redis_client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"递增计数器失败: {e}")
            return 0
    
    @handle_errors
    async def decrement(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        if not self.is_connected:
            return 0
        
        try:
            result = await self.redis_client.decrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"递减计数器失败: {e}")
            return 0
    
    @handle_errors
    async def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """设置哈希字段"""
        if not self.is_connected:
            return 0
        
        try:
            # 序列化值
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[field] = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_mapping[field] = str(value)
            
            result = await self.redis_client.hset(name, mapping=serialized_mapping)
            return result
        except Exception as e:
            logger.error(f"设置哈希字段失败: {e}")
            return 0
    
    @handle_errors
    async def hget(self, name: str, key: str) -> Any:
        """获取哈希字段值"""
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis_client.hget(name, key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"获取哈希字段值失败: {e}")
            return None
    
    @handle_errors
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """获取所有哈希字段"""
        if not self.is_connected:
            return {}
        
        try:
            mapping = await self.redis_client.hgetall(name)
            result = {}
            for key, value in mapping.items():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            return result
        except Exception as e:
            logger.error(f"获取所有哈希字段失败: {e}")
            return {}
    
    @handle_errors
    async def lpush(self, name: str, *values: Any) -> int:
        """向列表左侧推入元素"""
        if not self.is_connected:
            return 0
        
        try:
            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            result = await self.redis_client.lpush(name, *serialized_values)
            return result
        except Exception as e:
            logger.error(f"推入列表元素失败: {e}")
            return 0
    
    @handle_errors
    async def rpop(self, name: str) -> Any:
        """从列表右侧弹出元素"""
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis_client.rpop(name)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"弹出列表元素失败: {e}")
            return None
    
    @handle_errors
    async def llen(self, name: str) -> int:
        """获取列表长度"""
        if not self.is_connected:
            return 0
        
        try:
            return await self.redis_client.llen(name)
        except Exception as e:
            logger.error(f"获取列表长度失败: {e}")
            return 0
    
    @handle_errors
    async def lrange(self, name: str, start: int, end: int) -> List[Any]:
        """获取列表范围内的元素"""
        if not self.is_connected:
            return []
        
        try:
            values = await self.redis_client.lrange(name, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            return result
        except Exception as e:
            logger.error(f"获取列表范围元素失败: {e}")
            return []

# 缓存装饰器
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """
    缓存函数结果的装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 键前缀
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cache_service = RedisCache("redis://localhost:6379/0")
            cached_result = await cache_service.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_service.set(cache_key, result, ttl)
            logger.debug(f"缓存存储: {cache_key}")
            
            return result
        return wrapper
    return decorator

# 缓存失效装饰器
def invalidate_cache(pattern: str):
    """
    缓存失效装饰器
    
    Args:
        pattern: 要失效的缓存键模式
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 失效缓存
            cache_service = RedisCache("redis://localhost:6379/0")
            keys = await cache_service.keys(pattern)
            for key in keys:
                await cache_service.delete(key)
            
            logger.debug(f"缓存失效: {pattern}")
            return result
        return wrapper
    return decorator

