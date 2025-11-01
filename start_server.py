#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动QBM AI System测试服务器
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="QBM AI System",
    description="AI增强的商业模式量化分析系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "QBM AI System API", 
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "not_connected",
            "ai_engine": "ready"
        }
    }

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "test": "success", 
        "data": {
            "value": 123,
            "message": "API工作正常"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API状态"""
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/",
            "/health", 
            "/test",
            "/api/status",
            "/docs"
        ],
        "features": [
            "FastAPI框架",
            "CORS支持",
            "自动API文档",
            "健康检查"
        ]
    }

if __name__ == "__main__":
    print("QBM AI System 测试服务器")
    print("=" * 40)
    print("服务器启动中...")
    print("访问地址:")
    print("  - 主页: http://localhost:8000/")
    print("  - 健康检查: http://localhost:8000/health")
    print("  - 测试端点: http://localhost:8000/test")
    print("  - API状态: http://localhost:8000/api/status")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 交互式API: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 40)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")







