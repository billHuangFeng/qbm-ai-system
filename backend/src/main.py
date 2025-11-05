"""
BMOS系统 - 主应用（已废弃）
请使用 main_optimized.py 作为主应用入口
"""

import warnings

warnings.warn(
    "src/main.py 已废弃，请使用 main_optimized.py 作为主应用入口",
    DeprecationWarning,
    stacklevel=2,
)

# 重定向到优化后的主应用
from main_optimized import app

__all__ = ["app"]


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "QBM历史数据拟合优化系统",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "qbm-historical-data-fitting",
        "version": "0.1.0",
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
            "monitoring",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
