"""
缓存中间件
为FastAPI应用提供缓存功能
"""

import time
import hashlib
import json
from typing import Any, Dict, List, Optional, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .cache_manager import CacheManager, CacheStrategy, CacheLevel
from .redis_cache import RedisCache
from ..error_handling.unified import handle_errors, BusinessError
from ..logging_config import get_logger

logger = get_logger("cache_middleware")

class CacheMiddleware(BaseHTTPMiddleware):
    """缓存中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        cache_manager: CacheManager,
        cache_rules: Optional[Dict[str, Dict[str, Any]]] = None,
        default_ttl: int = 300,
        excluded_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.cache_manager = cache_manager
        self.cache_rules = cache_rules or {}
        self.default_ttl = default_ttl
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否应该缓存
        if not self._should_cache(request):
            return await call_next(request)
        
        # 生成缓存键
        cache_key = self._generate_cache_key(request)
        
        try:
            # 尝试从缓存获取响应
            cached_response = await self.cache_manager.get(cache_key)
            
            if cached_response is not None:
                logger.debug(f"缓存命中: {request.url}")
                return self._create_response_from_cache(cached_response)
            
            # 执行请求
            response = await call_next(request)
            
            # 缓存响应
            if self._should_cache_response(response):
                await self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"缓存中间件错误: {e}")
            # 发生错误时直接执行请求
            return await call_next(request)
    
    def _should_cache(self, request: Request) -> bool:
        """判断是否应该缓存请求"""
        # 只缓存GET请求
        if request.method != "GET":
            return False
        
        # 检查排除路径
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return False
        
        # 检查是否有缓存规则
        path = request.url.path
        if path in self.cache_rules:
            return self.cache_rules[path].get("enabled", True)
        
        return True
    
    def _should_cache_response(self, response: Response) -> bool:
        """判断是否应该缓存响应"""
        # 只缓存成功的响应
        if response.status_code != 200:
            return False
        
        # 检查Content-Type
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return False
        
        return True
    
    def _generate_cache_key(self, request: Request) -> str:
        """生成缓存键"""
        # 包含路径、查询参数和请求头
        key_data = {
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": {
                "authorization": request.headers.get("authorization"),
                "accept": request.headers.get("accept"),
                "accept-language": request.headers.get("accept-language")
            }
        }
        
        # 生成哈希值
        key_string = json.dumps(key_data, sort_keys=True)
        hash_value = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"http_cache:{hash_value}"
    
    def _create_response_from_cache(self, cached_data: Dict[str, Any]) -> Response:
        """从缓存数据创建响应"""
        return JSONResponse(
            content=cached_data["content"],
            status_code=cached_data["status_code"],
            headers=cached_data["headers"]
        )
    
    async def _cache_response(self, cache_key: str, response: Response):
        """缓存响应"""
        try:
            # 读取响应内容
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # 解析JSON内容
            try:
                content = json.loads(body.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return  # 无法解析JSON，不缓存
            
            # 准备缓存数据
            cache_data = {
                "content": content,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cached_at": time.time()
            }
            
            # 获取缓存规则
            ttl = self._get_cache_ttl(response.url.path)
            
            # 存储到缓存
            await self.cache_manager.set(cache_key, cache_data, ttl)
            logger.debug(f"响应已缓存: {cache_key}")
            
        except Exception as e:
            logger.error(f"缓存响应失败: {e}")
    
    def _get_cache_ttl(self, path: str) -> int:
        """获取缓存TTL"""
        if path in self.cache_rules:
            return self.cache_rules[path].get("ttl", self.default_ttl)
        return self.default_ttl

class CacheControlMiddleware(BaseHTTPMiddleware):
    """缓存控制中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        cache_control_rules: Optional[Dict[str, str]] = None
    ):
        super().__init__(app)
        self.cache_control_rules = cache_control_rules or {
            "/api/v1/models": "public, max-age=300",
            "/api/v1/predictions": "private, max-age=60",
            "/api/v1/memories": "public, max-age=600",
            "/api/v1/data": "private, max-age=120"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        response = await call_next(request)
        
        # 添加缓存控制头
        path = request.url.path
        for pattern, cache_control in self.cache_control_rules.items():
            if path.startswith(pattern):
                response.headers["Cache-Control"] = cache_control
                break
        
        return response

class CacheInvalidationMiddleware(BaseHTTPMiddleware):
    """缓存失效中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        cache_manager: CacheManager,
        invalidation_rules: Optional[Dict[str, List[str]]] = None
    ):
        super().__init__(app)
        self.cache_manager = cache_manager
        self.invalidation_rules = invalidation_rules or {
            "POST /api/v1/models": ["http_cache:*"],
            "PUT /api/v1/models": ["http_cache:*"],
            "DELETE /api/v1/models": ["http_cache:*"],
            "POST /api/v1/predictions": ["http_cache:*"],
            "POST /api/v1/memories": ["http_cache:*"],
            "PUT /api/v1/memories": ["http_cache:*"],
            "DELETE /api/v1/memories": ["http_cache:*"],
            "POST /api/v1/data": ["http_cache:*"],
            "PUT /api/v1/data": ["http_cache:*"],
            "DELETE /api/v1/data": ["http_cache:*"]
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        response = await call_next(request)
        
        # 检查是否需要失效缓存
        method_path = f"{request.method} {request.url.path}"
        
        if method_path in self.invalidation_rules:
            patterns = self.invalidation_rules[method_path]
            
            for pattern in patterns:
                try:
                    await self.cache_manager.clear(pattern)
                    logger.debug(f"缓存失效: {pattern}")
                except Exception as e:
                    logger.error(f"缓存失效失败: {e}")
        
        return response

# 缓存装饰器
def cache_endpoint(
    ttl: int = 300,
    key_prefix: str = "",
    strategy: CacheStrategy = CacheStrategy.TTL,
    level: CacheLevel = CacheLevel.L2
):
    """
    端点缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 键前缀
        strategy: 缓存策略
        level: 缓存级别
    """
    def decorator(func):
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
                logger.debug(f"端点缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.set(cache_key, result, ttl, strategy)
            logger.debug(f"端点缓存存储: {cache_key}")
            
            return result
        return wrapper
    return decorator

# 缓存失效装饰器
def invalidate_endpoint_cache(pattern: str):
    """
    端点缓存失效装饰器
    
    Args:
        pattern: 要失效的缓存键模式
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 失效缓存
            cache_manager = CacheManager(RedisCache("redis://localhost:6379/0"))
            await cache_manager.clear(pattern)
            
            logger.debug(f"端点缓存失效: {pattern}")
            return result
        return wrapper
    return decorator

# 缓存预热装饰器
def warm_up_cache(warm_up_data: Dict[str, Any]):
    """
    缓存预热装饰器
    
    Args:
        warm_up_data: 预热数据
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 预热缓存
            cache_manager = CacheManager(RedisCache("redis://localhost:6379/0"))
            await cache_manager.warm_up_cache(warm_up_data)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator


