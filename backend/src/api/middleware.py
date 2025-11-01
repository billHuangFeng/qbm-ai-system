"""
API中间件配置
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from typing import Callable
from .auth import TenantAuthMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI):
    """设置所有中间件"""
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.qbm.com"]
    )
    
    # Gzip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求结束
        logger.info(
            f"请求完成: {request.method} {request.url} "
            f"状态码: {response.status_code} "
            f"处理时间: {process_time:.4f}s"
        )
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    # 租户中间件
    @app.middleware("http")
    async def tenant_middleware(request: Request, call_next: Callable):
        # 从请求头或路径中提取租户ID
        tenant_id = request.headers.get("X-Tenant-ID")
        
        if not tenant_id:
            # 从URL路径中提取租户ID
            path_parts = request.url.path.split("/")
            if len(path_parts) > 2 and path_parts[1] == "api":
                tenant_id = path_parts[2]
        
        # 将租户ID添加到请求状态
        request.state.tenant_id = tenant_id
        
        # 处理请求
        response = await call_next(request)
        
        return response
    
    # 错误处理中间件
    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"请求处理错误: {e}", exc_info=True)
            
            # 返回标准错误响应
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "内部服务器错误",
                    "message": "请求处理过程中发生错误",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
    
    # 请求ID中间件
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next: Callable):
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

# 自定义中间件类
class RateLimitMiddleware:
    """速率限制中间件"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def __call__(self, request: Request, call_next: Callable):
        client_ip = request.client.host
        current_time = time.time()
        
        # 清理过期的请求记录
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > current_time - self.window_seconds for t in times)
        }
        
        # 检查当前IP的请求次数
        if client_ip in self.requests:
            recent_requests = [
                t for t in self.requests[client_ip]
                if t > current_time - self.window_seconds
            ]
            if len(recent_requests) >= self.max_requests:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"error": "请求过于频繁，请稍后再试"}
                )
        
        # 记录当前请求
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        return response

class TenantIsolationMiddleware:
    """租户隔离中间件"""
    
    async def __call__(self, request: Request, call_next: Callable):
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if tenant_id:
            # 设置数据库搜索路径到租户Schema
            # 这里需要在数据库连接中实现
            logger.info(f"设置租户上下文: {tenant_id}")
        
        response = await call_next(request)
        return response

# 全局中间件实例
rate_limit_middleware = RateLimitMiddleware()
tenant_isolation_middleware = TenantIsolationMiddleware()




