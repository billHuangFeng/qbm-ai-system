"""
BMOS系统 - 优化后的主应用
集成所有安全、性能和错误处理优化
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

# 导入统一配置
from src.config.unified import ConfigManager

# 导入统一错误处理
from src.error_handling.unified import (
    BMOSError,
    BusinessError,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    business_error_handler,
)

# 导入日志配置
from src.logging_config import get_logger

# 导入数据库服务
from src.security.database import SecureDatabaseService

# 导入任务管理服务
from src.tasks.task_queue import TaskManager
from src.tasks.scheduler import SchedulerService
from src.tasks.handlers import BMOSTaskHandlers, setup_default_scheduled_jobs

# 导入API路由
from src.api.router import api_router

# 导入依赖
from src.api.dependencies import (
    get_db_service,
    get_cache_service,
    get_model_training_service,
    get_memory_service,
    get_ai_copilot_service,
    get_data_import_etl,
    get_data_quality_service,
    get_scheduler_service,
    get_monitoring_service,
)

# 导入缓存相关
from src.cache.redis_cache import RedisCache
from src.cache.cache_manager import CacheManager
from src.cache.middleware import (
    CacheMiddleware,
    CacheControlMiddleware,
    CacheInvalidationMiddleware,
)

# 初始化配置管理器
config_manager = ConfigManager()
settings = config_manager.settings

# 配置日志
logger = get_logger("main_optimized")

# 初始化数据库和Redis服务 (在应用生命周期中管理连接)
db_service_instance = SecureDatabaseService(settings.database.database_url)
cache_service_instance = RedisCache(
    settings.redis.redis_url, settings.redis.redis_password
)
cache_manager_instance = CacheManager(cache_service_instance)

# 初始化任务管理服务
task_manager_instance = TaskManager(cache_service_instance)
scheduler_service_instance = SchedulerService(cache_service_instance)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(
        f"启动 {settings.application.app_name} v{settings.application.app_version}..."
    )

    # 1. 初始化数据库连接池
    await db_service_instance.connect()
    if not await db_service_instance.health_check():
        logger.critical("数据库连接失败，应用无法启动。")
        raise Exception("数据库连接失败")
    logger.info("数据库连接成功。")

    # 2. 初始化Redis连接
    await cache_service_instance.connect()
    if not await cache_service_instance.health_check():
        logger.warning("Redis连接失败，缓存功能可能受限。")
    else:
        logger.info("Redis连接成功。")

    # 3. 初始化缓存管理器
    await cache_manager_instance.initialize()
    logger.info("缓存管理器初始化完成。")

    # 4. 初始化任务管理服务
    await scheduler_service_instance.initialize()
    logger.info("调度器服务初始化完成。")

    # 启动默认队列的工作者
    await task_manager_instance.start_workers("default", worker_count=2)
    logger.info("任务队列工作者启动完成。")

    # 5. 初始化任务处理器
    task_handlers = BMOSTaskHandlers(task_manager_instance, scheduler_service_instance)
    await setup_default_scheduled_jobs(scheduler_service_instance)
    logger.info("任务处理器和默认定时任务初始化完成。")

    # 6. 预加载模型或企业记忆 (如果需要)
    # 例如: await get_model_training_service().load_all_active_models()
    # 例如: await get_memory_service().load_all_memories_to_cache()

    logger.info(f"{settings.application.app_name} 启动完成。")
    yield
    logger.info(f"关闭 {settings.application.app_name}...")

    # 1. 停止任务管理服务
    await task_manager_instance.stop_workers()
    logger.info("任务队列工作者已停止。")

    # 2. 关闭调度器服务
    await scheduler_service_instance.shutdown()
    logger.info("调度器服务已关闭。")

    # 3. 关闭缓存管理器
    await cache_manager_instance.shutdown()
    # 4. 关闭Redis连接
    await cache_service_instance.disconnect()
    # 5. 关闭数据库连接池
    await db_service_instance.disconnect()
    logger.info(f"{settings.application.app_name} 关闭完成。")


# 创建FastAPI应用
app = FastAPI(
    title=settings.application.app_name,
    version=settings.application.app_version,
    description="BMOS (Business Model Optimization System) 是一个基于AI的边际分析系统，通过机器学习模型和企业记忆机制，实现'越用越聪明'的智能决策支持。",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置缓存中间件
cache_rules = {
    "/api/v1/models": {"enabled": True, "ttl": 300},
    "/api/v1/predictions": {"enabled": True, "ttl": 60},
    "/api/v1/memories": {"enabled": True, "ttl": 600},
    "/api/v1/data": {"enabled": True, "ttl": 120},
}

app.add_middleware(
    CacheMiddleware,
    cache_manager=cache_manager_instance,
    cache_rules=cache_rules,
    default_ttl=300,
)

app.add_middleware(CacheControlMiddleware)
app.add_middleware(CacheInvalidationMiddleware, cache_manager=cache_manager_instance)

# 配置TrustedHostMiddleware (生产环境建议开启)
if settings.application.environment.value == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.security.trusted_hosts
    )

# 注册全局异常处理器
app.add_exception_handler(BusinessError, business_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 注册API路由
app.include_router(api_router, prefix=settings.application.api_v1_str)


@app.get("/", summary="根路径", tags=["System"])
async def root():
    """
    BMOS AI System API 根路径。
    """
    return {
        "message": "BMOS AI System API",
        "version": settings.application.app_version,
    }


@app.get("/health", summary="健康检查", tags=["System"])
async def health_check(
    db_service: SecureDatabaseService = Depends(get_db_service),
    cache_service: RedisCache = Depends(get_cache_service),
) -> Dict[str, Any]:
    """
    执行系统健康检查。

    检查项目:
    - 数据库连接状态
    - Redis连接状态
    - 系统资源使用情况
    """
    try:
        # 检查数据库连接
        db_healthy = await db_service.health_check()

        # 检查Redis连接
        cache_healthy = await cache_service.health_check()

        # 检查系统状态
        system_healthy = db_healthy and cache_healthy

        return {
            "status": "healthy" if system_healthy else "unhealthy",
            "database": db_healthy,
            "redis": cache_healthy,
            "timestamp": datetime.now().isoformat(),
            "version": settings.application.app_version,
        }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "database": False,
            "redis": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "version": settings.application.app_version,
        }


if __name__ == "__main__":
    uvicorn.run(
        "main_optimized:app",
        host=settings.application.api_host,
        port=settings.application.api_port,
        reload=settings.application.debug,
        log_level=settings.application.log_level.value.lower(),
    )
