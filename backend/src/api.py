"""
BMOS系统 - API路由模块
提供API路由和中间件配置
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import List

# 创建API路由器
api_router = APIRouter()

@api_router.get("/")
async def root():
    """根路径"""
    return {"message": "BMOS API", "status": "running"}

@api_router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "BMOS API"}

def setup_middleware(app: FastAPI):
    """设置中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 受信任主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.bmos.com"]
    )
    
    return app


