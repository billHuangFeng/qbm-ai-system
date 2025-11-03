"""
BMOS系统 - 模型训练API端点
作用: 提供模型训练相关的REST API
状态: ✅ 实施中
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid

from ...services.model_training_service import ModelTrainingService
from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService
from ..dependencies import (
    get_model_training_service as di_get_model_training_service,
    get_database_service as di_get_database_service,
    get_cache_service as di_get_cache_service,
)
from ...auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["模型训练"])

# Pydantic模型定义
class TrainingRequest(BaseModel):
    """模型训练请求"""
    model_type: str = Field(..., description="模型类型: marginal_analysis, timeseries, npv, capability_value")
    target_variable: str = Field(..., description="目标变量名")
    features: List[str] = Field(..., description="特征列表")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="超参数")
    training_data_period: Optional[str] = Field(None, description="训练数据时间范围")
    
    class Config:
        schema_extra = {
            "example": {
                "model_type": "marginal_analysis",
                "target_variable": "revenue",
                "features": ["asset_investment", "capability_improvement"],
                "hyperparameters": {
                    "rf_n_estimators": 100,
                    "rf_max_depth": 10
                },
                "training_data_period": "2024-01-01 to 2024-12-31"
            }
        }

class RetrainRequest(BaseModel):
    """模型重训练请求"""
    model_id: str = Field(..., description="模型ID")
    update_strategy: str = Field("incremental", description="更新策略: incremental, full_retrain")
    feedback_data: Optional[Dict[str, Any]] = Field(None, description="反馈数据")
    
class PredictionRequest(BaseModel):
    """预测请求"""
    model_id: str = Field(..., description="模型ID")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    
class TrainingResponse(BaseModel):
    """训练响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="状态: queued, training, completed, failed")
    estimated_time: Optional[str] = Field(None, description="预计完成时间")
    message: str = Field(..., description="消息")

class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    model_type: str
    model_version: str
    model_name: str
    accuracy_score: Optional[float]
    r_squared: Optional[float]
    mae: Optional[float]
    rmse: Optional[float]
    training_data_size: Optional[int]
    last_training_date: Optional[str]
    model_status: str
    is_production: bool

# 依赖注入
def get_model_training_service() -> ModelTrainingService:
    return di_get_model_training_service()

def get_database_service() -> DatabaseService:
    return di_get_database_service()

def get_cache_service() -> CacheService:
    return di_get_cache_service()

@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """训练新模型"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 验证请求
        if not request.features:
            raise HTTPException(status_code=400, detail="特征列表不能为空")
        
        if request.model_type not in ['marginal_analysis', 'timeseries', 'npv', 'capability_value']:
            raise HTTPException(status_code=400, detail="不支持的模型类型")
        
        # 记录训练任务
        await db_service.execute_insert("""
            INSERT INTO model_training_history (
                id, tenant_id, model_type, model_version, training_trigger,
                training_data_period, training_data_size, feature_count,
                hyperparameters, training_status, started_at, trained_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """, [
            task_id,
            current_user['tenant_id'],
            request.model_type,
            f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'manual',
            request.training_data_period,
            0,  # 将在训练完成后更新
            len(request.features),
            request.hyperparameters or {},
            'training',
            datetime.now(),
            current_user['user_id']
        ])
        
        # 添加后台训练任务
        background_tasks.add_task(
            execute_training_task,
            task_id,
            request,
            current_user,
            training_service,
            db_service
        )
        
        return TrainingResponse(
            task_id=task_id,
            status="queued",
            estimated_time="10-15分钟",
            message="模型训练任务已提交"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise HTTPException(status_code=500, detail=f"训练失败: {str(e)}")

@router.post("/retrain", response_model=TrainingResponse)
async def retrain_model(
    request: RetrainRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """重训练模型"""
    try:
        # 验证模型是否存在
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2
        """, [request.model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        # 生成新任务ID
        task_id = str(uuid.uuid4())
        
        # 记录重训练任务
        await db_service.execute_insert("""
            INSERT INTO model_training_history (
                id, tenant_id, model_type, model_version, training_trigger,
                training_status, started_at, trained_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, [
            task_id,
            current_user['tenant_id'],
            model_info['model_type'],
            f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'feedback_retrain',
            'training',
            datetime.now(),
            current_user['user_id']
        ])
        
        # 添加后台重训练任务
        background_tasks.add_task(
            execute_retraining_task,
            task_id,
            request,
            current_user,
            training_service,
            db_service
        )
        
        return TrainingResponse(
            task_id=task_id,
            status="queued",
            estimated_time="5-10分钟",
            message="模型重训练任务已提交"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")
        raise HTTPException(status_code=500, detail=f"重训练失败: {str(e)}")

@router.get("/{model_id}", response_model=ModelInfo)
async def get_model_info(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取模型信息"""
    try:
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2
        """, [model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        return ModelInfo(**model_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model info failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

@router.get("/", response_model=List[ModelInfo])
async def list_models(
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """列出模型"""
    try:
        query = "SELECT * FROM model_parameters_storage WHERE tenant_id = $1"
        params = [current_user['tenant_id']]
        
        if model_type:
            query += " AND model_type = $2"
            params.append(model_type)
        
        if status:
            query += f" AND model_status = ${len(params) + 1}"
            params.append(status)
        
        query += " ORDER BY last_training_date DESC"
        
        models = await db_service.execute_query(query, params)
        
        return [ModelInfo(**model) for model in models]
        
    except Exception as e:
        logger.error(f"List models failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@router.post("/{model_id}/predict")
async def predict(
    model_id: str,
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """使用模型进行预测"""
    try:
        # 检查缓存
        cache_key = f"prediction:{model_id}:{hash(str(request.input_data))}"
        cached_result = await cache_service.get("prediction", cache_key)
        
        if cached_result:
            return cached_result
        
        # 执行预测
        prediction_result = await training_service.predict(
            model_id=model_id,
            input_data=request.input_data,
            tenant_id=current_user['tenant_id']
        )
        
        # 缓存结果
        await cache_service.set("prediction", prediction_result, cache_key, ttl=300)
        
        return prediction_result
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@router.get("/{model_id}/status")
async def get_training_status(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取训练状态"""
    try:
        training_info = await db_service.execute_one("""
            SELECT training_status, started_at, completed_at, error_message
            FROM model_training_history 
            WHERE id = $1 AND tenant_id = $2
        """, [model_id, current_user['tenant_id']])
        
        if not training_info:
            raise HTTPException(status_code=404, detail="训练任务不存在")
        
        return {
            "status": training_info['training_status'],
            "started_at": training_info['started_at'],
            "completed_at": training_info['completed_at'],
            "error_message": training_info.get('error_message'),
            "duration": _calculate_duration(
                training_info['started_at'],
                training_info['completed_at']
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get training status failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取训练状态失败: {str(e)}")

# 后台任务函数
async def execute_training_task(
    task_id: str,
    request: TrainingRequest,
    current_user: Dict[str, Any],
    training_service: ModelTrainingService,
    db_service: DatabaseService
):
    """执行训练任务"""
    try:
        # 更新状态为训练中
        await db_service.execute_update("""
            UPDATE model_training_history 
            SET training_status = 'training' 
            WHERE id = $1
        """, [task_id])
        
        # 获取训练数据
        training_data = await get_training_data(
            current_user['tenant_id'],
            request.training_data_period,
            request.features,
            request.target_variable,
            db_service
        )
        
        # 执行训练
        training_result = await training_service.train_marginal_analysis_model(
            training_data=training_data,
            target_variable=request.target_variable,
            features=request.features,
            hyperparameters=request.hyperparameters
        )
        
        if training_result['success']:
            # 保存模型参数
            model_id = await training_service.save_model_parameters(
                model=training_result['model'],
                model_type=request.model_type,
                model_version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                training_result=training_result,
                tenant_id=current_user['tenant_id'],
                supabase_client=db_service
            )
            
            # 更新训练历史
            await db_service.execute_update("""
                UPDATE model_training_history 
                SET training_status = 'completed', 
                    completed_at = $1,
                    training_data_size = $2,
                    accuracy_score = $3,
                    r_squared = $4,
                    mae = $5,
                    rmse = $6
                WHERE id = $7
            """, [
                datetime.now(),
                training_result['training_data_size'],
                training_result['scores']['r2'],
                training_result['scores']['r2'],
                training_result['scores']['mae'],
                training_result['scores']['rmse'],
                task_id
            ])
        else:
            # 训练失败
            await db_service.execute_update("""
                UPDATE model_training_history 
                SET training_status = 'failed',
                    error_message = $1,
                    completed_at = $2
                WHERE id = $3
            """, [
                training_result.get('error', 'Unknown error'),
                datetime.now(),
                task_id
            ])
            
    except Exception as e:
        logger.error(f"Training task failed: {e}")
        await db_service.execute_update("""
            UPDATE model_training_history 
            SET training_status = 'failed',
                error_message = $1,
                completed_at = $2
            WHERE id = $3
        """, [str(e), datetime.now(), task_id])

async def execute_retraining_task(
    task_id: str,
    request: RetrainRequest,
    current_user: Dict[str, Any],
    training_service: ModelTrainingService,
    db_service: DatabaseService
):
    """执行重训练任务"""
    # 类似execute_training_task的实现
    pass

async def get_training_data(
    tenant_id: str,
    period: Optional[str],
    features: List[str],
    target_variable: str,
    db_service: DatabaseService
):
    """获取训练数据"""
    # 根据period和features从数据库获取训练数据
    # 这里需要根据实际的数据表结构来实现
    pass

def _calculate_duration(start_time: datetime, end_time: Optional[datetime]) -> Optional[str]:
    """计算训练时长"""
    if not end_time:
        return None
    
    duration = end_time - start_time
    return str(duration)

