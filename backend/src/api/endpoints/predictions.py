"""
BMOS系统 - 预测API端点
作用: 提供预测相关的REST API
状态: ✅ 实施中
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid

from ...services.model_training_service import ModelTrainingService
from ...services.enterprise_memory_service import EnterpriseMemoryService
from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService
from ..dependencies import (
    get_model_training_service as di_get_model_training_service,
    get_memory_service as di_get_memory_service,
    get_database_service as di_get_database_service,
    get_cache_service as di_get_cache_service,
)
from ...auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predictions", tags=["预测服务"])

# Pydantic模型定义
class PredictionRequest(BaseModel):
    """预测请求"""
    model_id: str = Field(..., description="模型ID")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    prediction_type: str = Field("single", description="预测类型: single, batch, timeseries")
    include_confidence: bool = Field(True, description="是否包含置信度")
    apply_memory: bool = Field(True, description="是否应用企业记忆")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_123",
                "input_data": {
                    "asset_investment": 1000000,
                    "capability_improvement": 0.15,
                    "market_condition": "good"
                },
                "prediction_type": "single",
                "include_confidence": True,
                "apply_memory": True
            }
        }

class BatchPredictionRequest(BaseModel):
    """批量预测请求"""
    model_id: str = Field(..., description="模型ID")
    input_batch: List[Dict[str, Any]] = Field(..., description="批量输入数据")
    include_confidence: bool = Field(True, description="是否包含置信度")
    apply_memory: bool = Field(True, description="是否应用企业记忆")
    
class TimeSeriesPredictionRequest(BaseModel):
    """时间序列预测请求"""
    model_id: str = Field(..., description="模型ID")
    historical_data: List[Dict[str, Any]] = Field(..., description="历史数据")
    forecast_periods: int = Field(12, description="预测期数")
    include_confidence_intervals: bool = Field(True, description="是否包含置信区间")
    
class PredictionResponse(BaseModel):
    """预测响应"""
    prediction_id: str = Field(..., description="预测ID")
    model_id: str = Field(..., description="模型ID")
    prediction_result: Dict[str, Any] = Field(..., description="预测结果")
    confidence_score: Optional[float] = Field(None, description="置信度分数")
    applied_memories: Optional[List[str]] = Field(None, description="应用的记忆ID")
    prediction_time: str = Field(..., description="预测时间")
    processing_time_ms: int = Field(..., description="处理时间(毫秒)")

class BatchPredictionResponse(BaseModel):
    """批量预测响应"""
    batch_id: str = Field(..., description="批量预测ID")
    model_id: str = Field(..., description="模型ID")
    predictions: List[PredictionResponse] = Field(..., description="预测结果列表")
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")

class TimeSeriesPredictionResponse(BaseModel):
    """时间序列预测响应"""
    prediction_id: str = Field(..., description="预测ID")
    model_id: str = Field(..., description="模型ID")
    forecast_data: List[Dict[str, Any]] = Field(..., description="预测数据")
    confidence_intervals: Optional[List[Dict[str, Any]]] = Field(None, description="置信区间")
    trend_analysis: Optional[Dict[str, Any]] = Field(None, description="趋势分析")
    prediction_time: str = Field(..., description="预测时间")

class PredictionHistory(BaseModel):
    """预测历史"""
    id: str
    model_id: str
    prediction_type: str
    input_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    confidence_score: Optional[float]
    actual_value: Optional[float]
    prediction_error: Optional[float]
    created_at: str

# 依赖注入
def get_model_training_service() -> ModelTrainingService:
    return di_get_model_training_service()

def get_memory_service() -> EnterpriseMemoryService:
    return di_get_memory_service()

def get_database_service() -> DatabaseService:
    return di_get_database_service()

def get_cache_service() -> CacheService:
    return di_get_cache_service()

@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """执行预测"""
    start_time = datetime.now()
    
    try:
        # 验证模型是否存在
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2 AND model_status = 'active'
        """, [request.model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在或未激活")
        
        # 生成预测ID
        prediction_id = str(uuid.uuid4())
        
        # 检查缓存
        cache_key = f"prediction:{request.model_id}:{hash(str(request.input_data))}"
        cached_result = await cache_service.get("prediction", cache_key)
        
        if cached_result:
            return PredictionResponse(**cached_result)
        
        # 执行基础预测
        base_prediction = await training_service.predict(
            model_id=request.model_id,
            input_data=request.input_data,
            tenant_id=current_user['tenant_id']
        )
        
        if not base_prediction['success']:
            raise HTTPException(
                status_code=500,
                detail=f"预测失败: {base_prediction.get('error', 'Unknown error')}"
            )
        
        prediction_result = base_prediction['prediction']
        applied_memories = []
        
        # 应用企业记忆
        if request.apply_memory:
            try:
                # 搜索相关记忆
                memory_search_result = await memory_service.retrieve_relevant_memories(
                    current_context={
                        "scenario": "prediction",
                        "model_type": model_info['model_type'],
                        "input_features": list(request.input_data.keys())
                    },
                    existing_memories=await get_existing_memories(current_user['tenant_id'], db_service),
                    min_confidence=0.7,
                    min_relevance=0.6
                )
                
                if memory_search_result:
                    # 应用记忆到预测
                    adjusted_prediction = await memory_service.apply_memory_to_prediction(
                        base_prediction=prediction_result,
                        memories=memory_search_result[:3]  # 最多应用3个记忆
                    )
                    
                    prediction_result = adjusted_prediction
                    applied_memories = [mem['id'] for mem in memory_search_result[:3]]
                    
            except Exception as e:
                logger.warning(f"Memory application failed: {e}")
                # 记忆应用失败不影响基础预测
        
        # 计算置信度
        confidence_score = None
        if request.include_confidence:
            confidence_score = await calculate_prediction_confidence(
                model_info,
                request.input_data,
                prediction_result,
                db_service
            )
        
        # 计算处理时间
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # 构建响应
        response = PredictionResponse(
            prediction_id=prediction_id,
            model_id=request.model_id,
            prediction_result=prediction_result,
            confidence_score=confidence_score,
            applied_memories=applied_memories if request.apply_memory else None,
            prediction_time=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
        
        # 缓存结果
        await cache_service.set("prediction", response.dict(), cache_key, ttl=300)
        
        # 记录预测历史
        await record_prediction_history(
            prediction_id=prediction_id,
            model_id=request.model_id,
            prediction_type=request.prediction_type,
            input_data=request.input_data,
            prediction_result=prediction_result,
            confidence_score=confidence_score,
            tenant_id=current_user['tenant_id'],
            user_id=current_user['user_id'],
            db_service=db_service
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def make_batch_prediction(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """执行批量预测"""
    try:
        # 验证模型
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2 AND model_status = 'active'
        """, [request.model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在或未激活")
        
        # 生成批量预测ID
        batch_id = str(uuid.uuid4())
        
        # 添加后台任务处理批量预测
        background_tasks.add_task(
            process_batch_prediction,
            batch_id,
            request,
            current_user,
            training_service,
            memory_service,
            db_service
        )
        
        return BatchPredictionResponse(
            batch_id=batch_id,
            model_id=request.model_id,
            predictions=[],
            total_count=len(request.input_batch),
            success_count=0,
            failed_count=0
        )
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")

@router.post("/predict/timeseries", response_model=TimeSeriesPredictionResponse)
async def make_timeseries_prediction(
    request: TimeSeriesPredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(get_model_training_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """执行时间序列预测"""
    try:
        # 验证模型
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2 AND model_type = 'timeseries'
        """, [request.model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="时间序列模型不存在")
        
        # 执行时间序列预测
        timeseries_result = await training_service.train_timeseries_model(
            historical_data=request.historical_data,
            forecast_periods=request.forecast_periods,
            include_confidence_intervals=request.include_confidence_intervals
        )
        
        if not timeseries_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"时间序列预测失败: {timeseries_result.get('error', 'Unknown error')}"
            )
        
        return TimeSeriesPredictionResponse(
            prediction_id=str(uuid.uuid4()),
            model_id=request.model_id,
            forecast_data=timeseries_result['forecast_data'],
            confidence_intervals=timeseries_result.get('confidence_intervals'),
            trend_analysis=timeseries_result.get('trend_analysis'),
            prediction_time=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Timeseries prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"时间序列预测失败: {str(e)}")

@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    model_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取预测历史"""
    try:
        query = """
            SELECT * FROM prediction_accuracy_log 
            WHERE tenant_id = $1
        """
        params = [current_user['tenant_id']]
        
        if model_id:
            query += " AND model_id = $2"
            params.append(model_id)
        
        query += " ORDER BY created_at DESC LIMIT $3 OFFSET $4"
        params.extend([limit, offset])
        
        history = await db_service.execute_query(query, params)
        
        return [PredictionHistory(**record) for record in history]
        
    except Exception as e:
        logger.error(f"Get prediction history failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取预测历史失败: {str(e)}")

@router.get("/accuracy/{model_id}")
async def get_model_accuracy(
    model_id: str,
    period_days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取模型准确度统计"""
    try:
        # 验证模型
        model_info = await db_service.execute_one("""
            SELECT * FROM model_parameters_storage 
            WHERE id = $1 AND tenant_id = $2
        """, [model_id, current_user['tenant_id']])
        
        if not model_info:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        # 获取准确度统计
        accuracy_stats = await db_service.execute_one("""
            SELECT 
                COUNT(*) as total_predictions,
                AVG(ABS(prediction_error)) as mean_absolute_error,
                STDDEV(prediction_error) as error_stddev,
                MIN(prediction_error) as min_error,
                MAX(prediction_error) as max_error,
                COUNT(CASE WHEN ABS(prediction_error) < 0.1 THEN 1 END) as accurate_predictions
            FROM prediction_accuracy_log 
            WHERE model_id = $1 AND tenant_id = $2 
            AND created_at >= NOW() - INTERVAL '%s days'
        """, [model_id, current_user['tenant_id']])
        
        if accuracy_stats['total_predictions'] > 0:
            accuracy_rate = accuracy_stats['accurate_predictions'] / accuracy_stats['total_predictions']
        else:
            accuracy_rate = 0
        
        return {
            "model_id": model_id,
            "period_days": period_days,
            "total_predictions": accuracy_stats['total_predictions'],
            "accuracy_rate": round(accuracy_rate, 4),
            "mean_absolute_error": round(accuracy_stats['mean_absolute_error'] or 0, 4),
            "error_stddev": round(accuracy_stats['error_stddev'] or 0, 4),
            "min_error": accuracy_stats['min_error'],
            "max_error": accuracy_stats['max_error'],
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get model accuracy failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型准确度失败: {str(e)}")

@router.post("/feedback")
async def submit_prediction_feedback(
    prediction_id: str,
    actual_value: float,
    feedback_notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """提交预测反馈"""
    try:
        # 获取预测记录
        prediction_record = await db_service.execute_one("""
            SELECT * FROM prediction_accuracy_log 
            WHERE id = $1 AND tenant_id = $2
        """, [prediction_id, current_user['tenant_id']])
        
        if not prediction_record:
            raise HTTPException(status_code=404, detail="预测记录不存在")
        
        # 计算预测误差
        predicted_value = prediction_record['predicted_value']
        prediction_error = actual_value - predicted_value
        
        # 更新预测记录
        await db_service.execute_update("""
            UPDATE prediction_accuracy_log 
            SET actual_value = $1, prediction_error = $2, feedback_notes = $3, updated_at = $4
            WHERE id = $5
        """, [actual_value, prediction_error, feedback_notes, datetime.now(), prediction_id])
        
        return {
            "success": True,
            "prediction_id": prediction_id,
            "predicted_value": predicted_value,
            "actual_value": actual_value,
            "prediction_error": prediction_error,
            "message": "预测反馈已提交"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit prediction feedback failed: {e}")
        raise HTTPException(status_code=500, detail=f"提交预测反馈失败: {str(e)}")

# 辅助函数
async def get_existing_memories(tenant_id: str, db_service: DatabaseService) -> List[Dict[str, Any]]:
    """获取现有记忆"""
    memories = await db_service.execute_query("""
        SELECT * FROM enterprise_memory 
        WHERE tenant_id = $1 AND is_active = true
        ORDER BY confidence_score DESC
    """, [tenant_id])
    
    return memories

async def calculate_prediction_confidence(
    model_info: Dict[str, Any],
    input_data: Dict[str, Any],
    prediction_result: Dict[str, Any],
    db_service: DatabaseService
) -> float:
    """计算预测置信度"""
    try:
        # 基于模型性能指标计算置信度
        base_confidence = model_info.get('accuracy_score', 0.8)
        
        # 基于输入数据质量调整置信度
        input_quality_score = 1.0
        for key, value in input_data.items():
            if value is None or value == "":
                input_quality_score -= 0.1
        
        # 基于历史预测准确度调整
        recent_accuracy = await db_service.execute_one("""
            SELECT AVG(ABS(prediction_error)) as avg_error
            FROM prediction_accuracy_log 
            WHERE model_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
        """, [model_info['id']])
        
        if recent_accuracy and recent_accuracy['avg_error']:
            accuracy_adjustment = max(0.5, 1.0 - recent_accuracy['avg_error'])
        else:
            accuracy_adjustment = 1.0
        
        final_confidence = base_confidence * input_quality_score * accuracy_adjustment
        return round(min(1.0, max(0.0, final_confidence)), 3)
        
    except Exception as e:
        logger.warning(f"Confidence calculation failed: {e}")
        return 0.8  # 默认置信度

async def record_prediction_history(
    prediction_id: str,
    model_id: str,
    prediction_type: str,
    input_data: Dict[str, Any],
    prediction_result: Dict[str, Any],
    confidence_score: Optional[float],
    tenant_id: str,
    user_id: str,
    db_service: DatabaseService
):
    """记录预测历史"""
    try:
        await db_service.execute_insert("""
            INSERT INTO prediction_accuracy_log (
                id, tenant_id, model_id, prediction_type,
                input_data, predicted_value, confidence_score,
                created_by, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, [
            prediction_id,
            tenant_id,
            model_id,
            prediction_type,
            input_data,
            prediction_result.get('value', 0),
            confidence_score,
            user_id,
            datetime.now()
        ])
    except Exception as e:
        logger.warning(f"Failed to record prediction history: {e}")

async def process_batch_prediction(
    batch_id: str,
    request: BatchPredictionRequest,
    current_user: Dict[str, Any],
    training_service: ModelTrainingService,
    memory_service: EnterpriseMemoryService,
    db_service: DatabaseService
):
    """处理批量预测"""
    # 批量预测的后台处理逻辑
    pass