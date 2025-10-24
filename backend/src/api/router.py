"""
API路由配置
"""

from fastapi import APIRouter
from .endpoints import auth, data, models, predictions, optimization, monitoring

# 创建主API路由器
api_router = APIRouter()

# 认证相关路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

# 数据相关路由
api_router.include_router(
    data.router,
    prefix="/data",
    tags=["数据管理"]
)

# 模型相关路由
api_router.include_router(
    models.router,
    prefix="/models",
    tags=["模型管理"]
)

# 预测相关路由
api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["预测分析"]
)

# 优化建议相关路由
api_router.include_router(
    optimization.router,
    prefix="/optimization",
    tags=["优化建议"]
)

# 监控相关路由
api_router.include_router(
    monitoring.router,
    prefix="/monitoring",
    tags=["系统监控"]
)


