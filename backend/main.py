"""
BMOS系统 - FastAPI应用主入口
作用: 提供模型训练、企业记忆、预测等API服务
状态: ✅ 实施中
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Optional, Dict, Any
import os
from datetime import datetime
import uuid

# 导入服务
from src.services.model_training_service import ModelTrainingService
from src.services.enterprise_memory_service import EnterpriseMemoryService
from src.services.database_service import DatabaseService
from src.services.cache_service import CacheService
from src.api.router import api_router
from src.api.dependencies import set_services, MockDatabaseService, MockCacheService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局服务实例
model_training_service = None
memory_service = None
db_service = None
cache_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global model_training_service, memory_service, db_service, cache_service
    
    # 启动时初始化服务
    logger.info("Initializing BMOS services...")
    
    # 初始化数据库服务（允许降级）
    try:
        db_service = DatabaseService()
        await db_service.initialize()
        logger.info("Database service initialized")
    except Exception as e:
        db_service = MockDatabaseService()
        logger.warning(f"Database service unavailable, using mock: {e}")

    # 初始化缓存服务（允许降级）
    try:
        cache_service = CacheService()
        await cache_service.initialize()
        logger.info("Cache service initialized")
    except Exception as e:
        cache_service = MockCacheService()
        logger.warning(f"Cache service unavailable, using mock: {e}")

    # 初始化业务服务（使用真实或Mock的后端服务）
    try:
        model_training_service = ModelTrainingService(db_service, cache_service)
        memory_service = EnterpriseMemoryService(db_service, cache_service)
        logger.info("Core services initialized (with possible degraded backends)")
    except Exception as e:
        model_training_service = None
        memory_service = None
        logger.error(f"Failed to initialize core services: {e}")
    
    # 设置全局服务实例供依赖注入使用
    try:
        set_services(
            model_training_service=model_training_service,
            memory_service=memory_service,
            db_service=db_service,
            cache_service=cache_service
        )
        logger.info("Global services registered for dependency injection")
    except Exception as e:
        logger.error(f"Failed to register global services: {e}")
    
    yield
    
    # 关闭时清理资源
    logger.info("Shutting down BMOS services...")
    if db_service:
        await db_service.close()
    if cache_service:
        await cache_service.close()

# 创建FastAPI应用
app = FastAPI(
    title="BMOS API",
    description="BMOS边际分析系统API服务\n\n注意: 当前环境支持无数据库(Mock)模式运行，用于端到端验收。",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全配置
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户信息"""
    # TODO: 实现JWT token验证
    # 暂时返回模拟用户
    return {
        "user_id": "test_user",
        "tenant_id": "test_tenant",
        "role": "admin"
    }

# 请求ID中间件（简易）
@app.middleware("http")
async def add_request_id_header(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = datetime.now()
    response = await call_next(request)
    duration_ms = (datetime.now() - start).total_seconds() * 1000
    try:
        logging.info("%s %s - %d ms - rid=%s", request.method, request.url.path, int(duration_ms), request_id)
    except Exception:
        pass
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = str(int(duration_ms))
    return response

# 全局异常处理（统一JSON响应）
@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    logging.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={
        "error": {"code": "internal_error", "message": "Internal server error"},
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
    })

@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "error": {"code": "http_error", "message": exc.detail},
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
    })

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mock_mode": {
            "database": db_service is None,
            "cache": cache_service is None
        },
        "services": {
            "database": "connected" if db_service else "disconnected",
            "cache": "connected" if cache_service else "disconnected",
            "model_training": "ready" if model_training_service else "not_ready",
            "memory_service": "ready" if memory_service else "not_ready"
        }
    }

# 注册API总路由（已在 src/api/router.py 内部选择性加载必要端点）
app.include_router(api_router)

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "BMOS API Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "mock_mode": {
            "database": db_service is None,
            "cache": cache_service is None
        },
        "endpoints": {
            "model_training": "/model-training",
            "enterprise_memory": "/enterprise-memory",
            "predictions": "/predictions",
            # "ai_copilot": "/ai-copilot",
            # "data_import": "/data-import",
            "auth": "/auth",
            "data_quality": "/data-quality",
            "scheduler": "/scheduler",
            "monitoring": "/monitoring",
            "optimization": "/optimization",
            "models": "/models",
            "ai_strategic": "/ai-strategic",
            "ai_planning": "/ai-planning"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
