"""
系统监控相关API端点
"""

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...auth import get_current_user, require_permission, Permission, User
from ..dependencies import get_database_service
from ...services.database_service import DatabaseService
from ...error_handling.decorators import handle_api_errors
from ...logging_config import get_logger

router = APIRouter()
logger = get_logger("monitoring_endpoints")


# 请求模型
class MonitoringResponse(BaseModel):
    id: int
    tenant_id: str
    model_id: str
    metric_name: str
    metric_value: float
    metric_date: str
    threshold_value: Optional[float]
    is_alert: bool
    alert_message: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# 获取监控数据
@router.get("/", response_model=List[MonitoringResponse])
@handle_api_errors
async def get_monitoring_data(
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: DatabaseService = Depends(get_database_service),
    model_id: Optional[str] = None,
    metric_name: Optional[str] = None,
    hours: int = 24,
):
    """获取监控数据"""
    try:
        # 构建查询
        query = """
            SELECT id, tenant_id, model_id, metric_name, metric_value, metric_date,
                   threshold_value, is_alert, alert_message, created_at
            FROM monitoring_metrics
            WHERE tenant_id = $1
        """
        params = [current_user.tenant_id]

        # 添加时间过滤
        start_time = datetime.now() - timedelta(hours=hours)
        query += " AND metric_date >= $" + str(len(params) + 1)
        params.append(start_time)

        # 添加模型过滤
        if model_id:
            query += " AND model_id = $" + str(len(params) + 1)
            params.append(model_id)

        # 添加指标过滤
        if metric_name:
            query += " AND metric_name = $" + str(len(params) + 1)
            params.append(metric_name)

        # 添加排序
        query += " ORDER BY metric_date DESC LIMIT 1000"

        # 执行查询
        result = await db.execute(query, params)
        rows = result.fetchall()

        # 构建响应
        monitoring_data = []
        for row in rows:
            monitoring_data.append(
                MonitoringResponse(
                    id=row[0],
                    tenant_id=row[1],
                    model_id=row[2],
                    metric_name=row[3],
                    metric_value=row[4],
                    metric_date=row[5].isoformat() if row[5] else None,
                    threshold_value=row[6],
                    is_alert=row[7],
                    alert_message=row[8],
                    created_at=row[9].isoformat() if row[9] else None,
                )
            )

        logger.info(f"获取监控数据: {len(monitoring_data)} 条记录")
        return monitoring_data

    except Exception as e:
        logger.error(f"获取监控数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取监控数据失败: {str(e)}",
        )


# 获取系统健康状态
@router.get("/health")
@handle_api_errors
async def get_system_health(
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: DatabaseService = Depends(get_database_service),
):
    """获取系统健康状态"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {},
        }

        # 检查数据库连接
        try:
            await db.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = "unhealthy"
            logger.error(f"Database health check failed: {str(e)}")

        # 检查Redis连接（如果有缓存服务）
        try:
            import redis

            redis_client = redis.Redis(host="localhost", port=6379, db=0)
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = "unavailable"
            logger.warning(f"Redis health check failed: {str(e)}")

        # 检查模型服务
        try:
            # 查询活跃模型数量
            result = await db.execute(
                "SELECT COUNT(*) FROM model_parameters_storage WHERE tenant_id = $1 AND model_status = 'active'",
                [current_user.tenant_id],
            )
            active_models = result.fetchone()[0]
            health_status["services"]["models"] = f"healthy ({active_models} active)"
        except Exception as e:
            health_status["services"]["models"] = "unhealthy"
            logger.error(f"Models health check failed: {str(e)}")

        # 获取系统资源使用情况
        if psutil:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            memory_percent = memory.percent
            disk_percent = disk.percent
            memory_available_gb = round(memory.available / (1024**3), 2)
            disk_free_gb = round(disk.free / (1024**3), 2)
        else:
            cpu_percent = 0.0
            memory_percent = 0.0
            disk_percent = 0.0
            memory_available_gb = None
            disk_free_gb = None

        health_status["resources"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "memory_available_gb": memory_available_gb,
            "disk_free_gb": disk_free_gb,
        }

        # 判断整体健康状态
        unhealthy_services = [
            service
            for service, status in health_status["services"].items()
            if "unhealthy" in status
        ]
        if unhealthy_services:
            health_status["status"] = "degraded"
        if (
            cpu_percent > 90
            or (memory_percent and memory_percent > 90)
            or (disk_percent and disk_percent > 90)
        ):
            health_status["status"] = "warning"

        logger.info(f"System health check completed: {health_status['status']}")
        return health_status

    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System health check failed: {str(e)}",
        )


# 获取性能指标
@router.get("/metrics")
@handle_api_errors
async def get_performance_metrics(
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: DatabaseService = Depends(get_database_service),
    hours: int = 24,
):
    """获取性能指标"""
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "tenant_id": current_user.tenant_id,
            "period_hours": hours,
        }

        # 查询模型性能指标
        start_time = datetime.now() - timedelta(hours=hours)

        # 1. 获取模型训练统计
        training_query = """
            SELECT 
                COUNT(*) as total_trainings,
                AVG(accuracy) as avg_accuracy,
                AVG(training_time) as avg_training_time
            FROM model_training_history
            WHERE tenant_id = $1 AND created_at >= $2
        """
        result = await db.execute(training_query, [current_user.tenant_id, start_time])
        training_stats = result.fetchone()

        metrics["model_training"] = {
            "total_trainings": training_stats[0] if training_stats else 0,
            "average_accuracy": (
                round(training_stats[1], 4)
                if training_stats and training_stats[1]
                else 0
            ),
            "average_training_time_seconds": (
                round(training_stats[2], 2)
                if training_stats and training_stats[2]
                else 0
            ),
        }

        # 2. 获取预测统计
        prediction_query = """
            SELECT 
                COUNT(*) as total_predictions,
                AVG(prediction_time) as avg_prediction_time,
                AVG(confidence_score) as avg_confidence
            FROM predictions
            WHERE tenant_id = $1 AND created_at >= $2
        """
        result = await db.execute(
            prediction_query, [current_user.tenant_id, start_time]
        )
        prediction_stats = result.fetchone()

        metrics["predictions"] = {
            "total_predictions": prediction_stats[0] if prediction_stats else 0,
            "average_prediction_time_seconds": (
                round(prediction_stats[1], 3)
                if prediction_stats and prediction_stats[1]
                else 0
            ),
            "average_confidence": (
                round(prediction_stats[2], 4)
                if prediction_stats and prediction_stats[2]
                else 0
            ),
        }

        # 3. 获取数据导入统计
        import_query = """
            SELECT 
                COUNT(*) as total_imports,
                SUM(total_records) as total_records,
                AVG(processing_time) as avg_processing_time
            FROM data_import_logs
            WHERE tenant_id = $1 AND created_at >= $2
        """
        result = await db.execute(import_query, [current_user.tenant_id, start_time])
        import_stats = result.fetchone()

        metrics["data_import"] = {
            "total_imports": import_stats[0] if import_stats else 0,
            "total_records": import_stats[1] if import_stats else 0,
            "average_processing_time_seconds": (
                round(import_stats[2], 2) if import_stats and import_stats[2] else 0
            ),
        }

        # 4. 获取API调用统计
        api_query = """
            SELECT 
                COUNT(*) as total_calls,
                COUNT(DISTINCT endpoint) as unique_endpoints,
                AVG(response_time) as avg_response_time
            FROM api_call_logs
            WHERE tenant_id = $1 AND created_at >= $2
        """
        result = await db.execute(api_query, [current_user.tenant_id, start_time])
        api_stats = result.fetchone()

        metrics["api_calls"] = {
            "total_calls": api_stats[0] if api_stats else 0,
            "unique_endpoints": api_stats[1] if api_stats else 0,
            "average_response_time_ms": (
                round(api_stats[2], 2) if api_stats and api_stats[2] else 0
            ),
        }

        # 5. 获取活跃模型数量
        models_query = """
            SELECT COUNT(*) 
            FROM model_parameters_storage 
            WHERE tenant_id = $1 AND model_status = 'active'
        """
        result = await db.execute(models_query, [current_user.tenant_id])
        active_models = result.fetchone()[0]

        metrics["active_models"] = active_models

        # 6. 获取数据质量指标
        quality_query = """
            SELECT 
                AVG(overall_score) as avg_quality_score,
                COUNT(*) as quality_checks
            FROM data_quality_reports
            WHERE tenant_id = $1 AND generated_at >= $2
        """
        result = await db.execute(quality_query, [current_user.tenant_id, start_time])
        quality_stats = result.fetchone()

        metrics["data_quality"] = {
            "average_score": (
                round(quality_stats[0], 2) if quality_stats and quality_stats[0] else 0
            ),
            "total_checks": quality_stats[1] if quality_stats else 0,
        }

        logger.info(
            f"Performance metrics retrieved for tenant: {current_user.tenant_id}"
        )
        return metrics

    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取性能指标失败: {str(e)}",
        )
