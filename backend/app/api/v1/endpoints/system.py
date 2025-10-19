from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from typing import Dict, Any
import psutil
import time
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/status")
async def system_status():
    """获取系统状态"""
    try:
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_total": disk.total,
                "disk_free": disk.free
            },
            "services": {
                "backend": "running",
                "database": "connected",
                "redis": "connected",
                "ai_engine": "ready"
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")

@router.get("/metrics")
async def system_metrics():
    """获取系统性能指标"""
    try:
        # 获取网络统计
        net_io = psutil.net_io_counters()
        
        # 获取进程信息
        process = psutil.Process(os.getpid())
        
        return {
            "performance": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "process_memory": process.memory_info().rss,
                "process_cpu": process.cpu_percent()
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {str(e)}")

@router.get("/logs")
async def system_logs(
    limit: int = 100,
    level: str = "INFO",
    current_user: User = Depends(get_current_user)
):
    """获取系统日志"""
    # 这里应该从日志文件或日志服务中获取日志
    # 目前返回模拟数据
    logs = [
        {
            "timestamp": "2024-01-15 10:30:15",
            "level": "INFO",
            "message": "用户登录成功",
            "user_id": 1,
            "ip": "192.168.1.100"
        },
        {
            "timestamp": "2024-01-15 10:25:30",
            "level": "WARNING",
            "message": "数据库连接池使用率较高",
            "user_id": None,
            "ip": None
        },
        {
            "timestamp": "2024-01-15 10:20:45",
            "level": "INFO",
            "message": "数据导入完成",
            "user_id": 1,
            "ip": "192.168.1.100"
        }
    ]
    
    # 根据级别过滤日志
    if level != "ALL":
        logs = [log for log in logs if log["level"] == level]
    
    return {
        "logs": logs[:limit],
        "total": len(logs),
        "timestamp": time.time()
    }

@router.get("/database/status")
async def database_status(db: Session = Depends(get_db)):
    """检查数据库连接状态"""
    try:
        # 执行简单查询测试数据库连接
        result = db.execute("SELECT 1").fetchone()
        
        return {
            "status": "connected",
            "message": "数据库连接正常",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"数据库连接失败: {str(e)}",
            "timestamp": time.time()
        }

@router.get("/redis/status")
async def redis_status():
    """检查Redis连接状态"""
    try:
        # 这里应该检查Redis连接
        # 目前返回模拟数据
        return {
            "status": "connected",
            "message": "Redis连接正常",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Redis连接失败: {str(e)}",
            "timestamp": time.time()
        }

@router.get("/ai-engine/status")
async def ai_engine_status():
    """检查AI引擎状态"""
    try:
        # 这里应该检查AI引擎状态
        # 目前返回模拟数据
        return {
            "status": "ready",
            "message": "AI引擎就绪",
            "models_loaded": ["customer_analyzer", "product_analyzer", "financial_analyzer"],
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI引擎状态异常: {str(e)}",
            "timestamp": time.time()
        }

@router.post("/maintenance/backup")
async def create_backup(
    current_user: User = Depends(get_current_user)
):
    """创建数据备份"""
    try:
        # 这里应该实现实际的备份逻辑
        # 目前返回模拟响应
        return {
            "status": "success",
            "message": "数据备份已创建",
            "backup_id": f"backup_{int(time.time())}",
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份创建失败: {str(e)}")

@router.post("/maintenance/cleanup")
async def cleanup_system(
    cleanup_type: str = "logs",
    current_user: User = Depends(get_current_user)
):
    """系统清理"""
    try:
        # 这里应该实现实际的清理逻辑
        # 目前返回模拟响应
        return {
            "status": "success",
            "message": f"{cleanup_type}清理完成",
            "cleaned_items": 150,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统清理失败: {str(e)}")


