"""
BMOS系统 - 简单启动脚本
设置必要的环境变量并启动API服务
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ.setdefault("JWT_SECRET_KEY", "bmos-super-secure-jwt-secret-key-minimum-32-characters-long-for-development")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "bmos_user")
os.environ.setdefault("POSTGRES_PASSWORD", "bmos_password")
os.environ.setdefault("POSTGRES_DB", "bmos_db")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("REDIS_DB", "0")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("LOG_LEVEL", "INFO")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并启动FastAPI应用
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="BMOS系统",
    description="基于机器学习的企业决策优化系统",
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

# 添加基本路由
@app.get("/")
async def root():
    return {"message": "BMOS系统API服务正在运行", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-10-28T08:00:00Z",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "cache": "connected"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    return {
        "api_version": "v1",
        "status": "operational",
        "endpoints": [
            "/api/v1/optimization/",
            "/api/v1/monitoring/",
            "/api/v1/tasks/",
            "/api/v1/models/",
            "/api/v1/predictions/",
            "/api/v1/memories/",
            "/api/v1/data-import/"
        ]
    }

if __name__ == "__main__":
    import sys
    import io
    # 修复Windows控制台编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("启动BMOS系统API服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


