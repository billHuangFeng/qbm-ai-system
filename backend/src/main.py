"""
QBM历史数据拟合优化系统 - 主应用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from contextlib import asynccontextmanager
from .database import db_manager
from .api import api_router, setup_middleware

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("启动QBM历史数据拟合优化系统...")
    
    # 初始化数据库连接
    if not db_manager.health_check():
        logger.error("数据库连接失败")
        raise Exception("数据库连接失败")
    
    # 初始化Redis连接
    # 加载预训练模型等
    
    yield
    
    # 关闭时执行
    logger.info("关闭QBM历史数据拟合优化系统...")

# 创建FastAPI应用
app = FastAPI(
    title="QBM历史数据拟合优化系统",
    description="基于机器学习的边际影响分析系统",
    version="0.1.0",
    lifespan=lifespan
)

# 设置中间件
setup_middleware(app)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "QBM历史数据拟合优化系统",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "qbm-historical-data-fitting",
        "version": "0.1.0"
    }

@app.get("/api/v1/status")
async def api_status():
    """API状态检查"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": [
            "data_preprocessing",
            "model_training", 
            "prediction",
            "optimization",
            "monitoring"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
