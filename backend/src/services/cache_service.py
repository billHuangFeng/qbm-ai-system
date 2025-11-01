"""
BMOS系统 - 缓存服务
作用: 封装Redis缓存操作
状态: ✅ 实施中
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Dict, Any, Union
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = {
            'user_session': 3600,      # 1小时
            'tenant_config': 1800,     # 30分钟
            'model_result': 300,        # 5分钟
            'query_result': 60,        # 1分钟
            'prediction': 300,         # 5分钟
            'memory': 1800,            # 30分钟
        }
    
    async def initialize(self):
        """初始化缓存服务"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            # 测试连接
            await self.redis_client.ping()
            
            logger.info("Cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache service: {e}")
            raise
    
    async def close(self):
        """关闭缓存连接"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_string = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, cache_type: str, *args) -> Optional[Any]:
        """获取缓存"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(cache_type, *args)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    async def set(self, cache_type: str, data: Any, *args, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(cache_type, *args)
            cache_ttl = ttl or self.cache_ttl.get(cache_type, 60)
            
            await self.redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(data, default=str)
            )
            return True
            
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    async def delete(self, cache_type: str, *args) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(cache_type, *args)
            await self.redis_client.delete(cache_key)
            return True
            
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False
    
    async def exists(self, cache_type: str, *args) -> bool:
        """检查缓存是否存在"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(cache_type, *args)
            return await self.redis_client.exists(cache_key) > 0
            
        except Exception as e:
            logger.warning(f"Cache exists check failed: {e}")
            return False
    
    async def get_or_set(self, cache_type: str, fetch_func, *args, ttl: Optional[int] = None) -> Any:
        """获取缓存，如果不存在则设置"""
        cached_data = await self.get(cache_type, *args)
        
        if cached_data is not None:
            return cached_data
        
        # 缓存不存在，执行获取函数
        data = await fetch_func()
        
        # 设置缓存
        await self.set(cache_type, data, *args, ttl=ttl)
        
        return data
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "hit_rate": self._calculate_hit_rate(info)
            }
            
        except Exception as e:
            logger.warning(f"Cache stats failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """计算缓存命中率"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)


