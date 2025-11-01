"""
BMOS系统 - API路由配置
作用: 配置所有API路由
状态: ✅ 实施中
"""

from fastapi import FastAPI
from .endpoints import model_training, enterprise_memory, predictions

def configure_routes(app: FastAPI):
    """配置API路由"""
    
    # 模型训练API
    app.include_router(
        model_training.router,
        prefix="/api/v1",
        tags=["模型训练"]
    )
    
    # 企业记忆API
    app.include_router(
        enterprise_memory.router,
        prefix="/api/v1",
        tags=["企业记忆"]
    )
    
    # 预测API
    app.include_router(
        predictions.router,
        prefix="/api/v1",
        tags=["预测服务"]
    )
    
    return app