"""
缓存策略和管理器
提供智能缓存策略和缓存管理功能
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

from .redis_cache import RedisCache
from ..error_handling.unified import handle_errors, BusinessError
from ..logging_config import get_logger

logger = get_logger("cache_manager")

class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少频率使用
    TTL = "ttl"  # 基于时间过期
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BACK = "write_back"  # 写回
    WRITE_AROUND = "write_around"  # 写绕过

class CacheLevel(Enum):
    """缓存级别"""
    L1 = "l1"  # 内存缓存
    L2 = "l2"  # Redis缓存
    L3 = "l3"  # 数据库缓存

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        self.memory_cache: Dict[str, Any] = {}
        self.cache_stats: Dict[str, Dict[str, int]] = {}
        self.cache_policies: Dict[str, Dict[str, Any]] = {}
        
    @handle_errors
    async def initialize(self):
        """初始化缓存管理器"""
        await self.redis_cache.connect()
        logger.info("缓存管理器初始化完成")
    
    @handle_errors
    async def shutdown(self):
        """关闭缓存管理器"""
        await self.redis_cache.disconnect()
        self.memory_cache.clear()
        logger.info("缓存管理器已关闭")
    
    def _generate_cache_key(
        self, 
        prefix: str, 
        *args, 
        **kwargs
    ) -> str:
        """生成缓存键"""
        # 将参数序列化为字符串
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        
        # 生成哈希值
        hash_value = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{hash_value}"
    
    def _get_cache_policy(self, key: str) -> Dict[str, Any]:
        """获取缓存策略"""
        return self.cache_policies.get(key, {
            "strategy": CacheStrategy.TTL,
            "ttl": 3600,
            "level": CacheLevel.L2,
            "max_size": 1000
        })
    
    def _update_cache_stats(self, key: str, operation: str):
        """更新缓存统计"""
        if key not in self.cache_stats:
            self.cache_stats[key] = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "deletes": 0,
                "last_access": time.time()
            }
        
        self.cache_stats[key][operation] += 1
        self.cache_stats[key]["last_access"] = time.time()
    
    @handle_errors
    async def get(
        self, 
        key: str, 
        default: Any = None,
        use_memory: bool = True
    ) -> Any:
        """获取缓存值"""
        policy = self._get_cache_policy(key)
        
        # L1缓存（内存）
        if use_memory and policy["level"] in [CacheLevel.L1, CacheLevel.L2]:
            if key in self.memory_cache:
                self._update_cache_stats(key, "hits")
                logger.debug(f"L1缓存命中: {key}")
                return self.memory_cache[key]
        
        # L2缓存（Redis）
        if policy["level"] in [CacheLevel.L2, CacheLevel.L3]:
            value = await self.redis_cache.get(key, default=default)
            if value is not None:
                self._update_cache_stats(key, "hits")
                
                # 更新L1缓存
                if use_memory and policy["level"] == CacheLevel.L2:
                    self.memory_cache[key] = value
                
                logger.debug(f"L2缓存命中: {key}")
                return value
        
        # 缓存未命中
        self._update_cache_stats(key, "misses")
        logger.debug(f"缓存未命中: {key}")
        return default
    
    @handle_errors
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        strategy: Optional[CacheStrategy] = None
    ) -> bool:
        """设置缓存值"""
        policy = self._get_cache_policy(key)
        
        # 使用策略或默认TTL
        cache_ttl = ttl or policy["ttl"]
        cache_strategy = strategy or policy["strategy"]
        
        success = True
        
        # L1缓存（内存）
        if policy["level"] in [CacheLevel.L1, CacheLevel.L2]:
            self.memory_cache[key] = value
            
            # 检查内存缓存大小限制
            if len(self.memory_cache) > policy["max_size"]:
                await self._evict_memory_cache(cache_strategy)
        
        # L2缓存（Redis）
        if policy["level"] in [CacheLevel.L2, CacheLevel.L3]:
            success = await self.redis_cache.set(key, value, cache_ttl)
        
        if success:
            self._update_cache_stats(key, "sets")
            logger.debug(f"缓存设置成功: {key}")
        
        return success
    
    @handle_errors
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        success = True
        
        # 删除L1缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 删除L2缓存
        redis_success = await self.redis_cache.delete(key)
        success = success and redis_success
        
        if success:
            self._update_cache_stats(key, "deletes")
            logger.debug(f"缓存删除成功: {key}")
        
        return success
    
    @handle_errors
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        # 检查L1缓存
        if key in self.memory_cache:
            return True
        
        # 检查L2缓存
        return await self.redis_cache.exists(key)
    
    @handle_errors
    async def clear(self, pattern: str = "*") -> int:
        """清空缓存"""
        cleared_count = 0
        
        # 清空L1缓存
        if pattern == "*":
            self.memory_cache.clear()
            cleared_count += len(self.memory_cache)
        else:
            # 按模式清空L1缓存
            keys_to_remove = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
            for key in keys_to_remove:
                del self.memory_cache[key]
            cleared_count += len(keys_to_remove)
        
        # 清空L2缓存
        redis_keys = await self.redis_cache.keys(pattern)
        for key in redis_keys:
            await self.redis_cache.delete(key)
        cleared_count += len(redis_keys)
        
        logger.info(f"清空缓存完成: {cleared_count} 个键")
        return cleared_count
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """匹配键模式"""
        if pattern == "*":
            return True
        
        # 简单的通配符匹配
        if "*" in pattern:
            import fnmatch
            return fnmatch.fnmatch(key, pattern)
        
        return key == pattern
    
    @handle_errors
    async def _evict_memory_cache(self, strategy: CacheStrategy):
        """内存缓存淘汰"""
        if strategy == CacheStrategy.LRU:
            # 最近最少使用
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.cache_stats.get(k, {}).get("last_access", 0)
            )
            del self.memory_cache[oldest_key]
            logger.debug(f"LRU淘汰: {oldest_key}")
        
        elif strategy == CacheStrategy.LFU:
            # 最少频率使用
            least_frequent_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.cache_stats.get(k, {}).get("hits", 0)
            )
            del self.memory_cache[least_frequent_key]
            logger.debug(f"LFU淘汰: {least_frequent_key}")
    
    @handle_errors
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_hits = sum(stats.get("hits", 0) for stats in self.cache_stats.values())
        total_misses = sum(stats.get("misses", 0) for stats in self.cache_stats.values())
        total_sets = sum(stats.get("sets", 0) for stats in self.cache_stats.values())
        total_deletes = sum(stats.get("deletes", 0) for stats in self.cache_stats.values())
        
        hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "total_keys": len(self.cache_stats),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "total_sets": total_sets,
            "total_deletes": total_deletes,
            "hit_rate": hit_rate,
            "cache_stats": self.cache_stats
        }
    
    @handle_errors
    async def set_cache_policy(
        self, 
        key_pattern: str, 
        policy: Dict[str, Any]
    ):
        """设置缓存策略"""
        self.cache_policies[key_pattern] = policy
        logger.info(f"设置缓存策略: {key_pattern} -> {policy}")
    
    @handle_errors
    async def warm_up_cache(self, warm_up_data: Dict[str, Any]):
        """预热缓存"""
        logger.info("开始缓存预热...")
        
        for key, value in warm_up_data.items():
            await self.set(key, value)
        
        logger.info(f"缓存预热完成: {len(warm_up_data)} 个键")

# 缓存装饰器
def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    strategy: CacheStrategy = CacheStrategy.TTL,
    level: CacheLevel = CacheLevel.L2
):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 键前缀
        strategy: 缓存策略
        level: 缓存级别
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_manager = CacheManager(RedisCache("redis://localhost:6379/0"))
            cache_key = cache_manager._generate_cache_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # 设置缓存策略
            await cache_manager.set_cache_policy(cache_key, {
                "strategy": strategy,
                "ttl": ttl,
                "level": level,
                "max_size": 1000
            })
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.set(cache_key, result, ttl, strategy)
            logger.debug(f"缓存存储: {cache_key}")
            
            return result
        return wrapper
    return decorator

# 缓存失效装饰器
def cache_invalidate(pattern: str):
    """
    缓存失效装饰器
    
    Args:
        pattern: 要失效的缓存键模式
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 失效缓存
            cache_manager = CacheManager(RedisCache("redis://localhost:6379/0"))
            await cache_manager.clear(pattern)
            
            logger.debug(f"缓存失效: {pattern}")
            return result
        return wrapper
    return decorator

# 缓存刷新装饰器
def cache_refresh(
    ttl: int = 3600,
    key_prefix: str = "",
    strategy: CacheStrategy = CacheStrategy.TTL,
    level: CacheLevel = CacheLevel.L2
):
    """
    缓存刷新装饰器
    
    执行函数后刷新缓存
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 刷新缓存
            cache_manager = CacheManager(RedisCache("redis://localhost:6379/0"))
            cache_key = cache_manager._generate_cache_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # 设置缓存策略
            await cache_manager.set_cache_policy(cache_key, {
                "strategy": strategy,
                "ttl": ttl,
                "level": level,
                "max_size": 1000
            })
            
            # 存储到缓存
            await cache_manager.set(cache_key, result, ttl, strategy)
            logger.debug(f"缓存刷新: {cache_key}")
            
            return result
        return wrapper
    return decorator

