"""
模型管理相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import pandas as pd
import numpy as np

from ...auth import get_current_user
from ...services.model_training_service import ModelTrainingService
from ...services.algorithm_service import AlgorithmService
from ...error_handling.unified import handle_errors, BusinessError
from ...logging_config import get_logger

router = APIRouter(prefix="/models", tags=["models"])
logger = get_logger("models_api")

# 创建服务实例
algorithm_service = AlgorithmService()


# 请求模型
class ModelCreate(BaseModel):
    model_name: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型")
    target_variable: str = Field(..., description="目标变量")
    features: List[str] = Field(..., description="特征列表")
    hyperparameters: Dict[str, Any] = Field(default={}, description="超参数")
    training_data: Dict[str, Any] = Field(..., description="训练数据")


class ModelUpdate(BaseModel):
    model_name: str = Field(None, description="模型名称")
    description: str = Field(None, description="模型描述")
    hyperparameters: Dict[str, Any] = Field(None, description="超参数")


class ModelTrainingRequest(BaseModel):
    model_type: str = Field(..., description="模型类型")
    target_variable: str = Field(..., description="目标变量")
    features: List[str] = Field(..., description="特征列表")
    hyperparameters: Dict[str, Any] = Field(default={}, description="超参数")
    training_data: Dict[str, Any] = Field(..., description="训练数据")


# 响应模型
class ModelResponse(BaseModel):
    id: str
    model_name: str
    model_type: str
    target_variable: str
    features: List[str]
    hyperparameters: Dict[str, Any]
    model_status: str
    accuracy_score: float
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# 创建模型
@router.post("/", response_model=ModelResponse)
@handle_errors
async def create_model(
    model_data: ModelCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """创建新模型"""
    try:
        # 创建模型记录
        model_id = str(uuid.uuid4())

        # 调用模型训练服务
        result = await training_service.train_model(
            model_id=model_id,
            model_type=model_data.model_type,
            target_variable=model_data.target_variable,
            features=model_data.features,
            hyperparameters=model_data.hyperparameters,
            training_data=model_data.training_data,
            tenant_id=current_user["tenant_id"],
        )

        return ModelResponse(
            id=model_id,
            model_name=model_data.model_name,
            model_type=model_data.model_type,
            target_variable=model_data.target_variable,
            features=model_data.features,
            hyperparameters=model_data.hyperparameters,
            model_status="active",
            accuracy_score=result.get("accuracy", 0.0),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"模型创建失败: {e}")
        raise BusinessError(
            code="MODEL_CREATION_FAILED", message=f"模型创建失败: {str(e)}"
        )


# 获取模型列表
@router.get("/", response_model=List[ModelResponse])
@handle_errors
async def get_models(
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """获取模型列表"""
    try:
        models = await training_service.get_models_by_tenant(current_user["tenant_id"])

        return [
            ModelResponse(
                id=model["id"],
                model_name=model.get("model_name", f"model_{model['id'][:8]}"),
                model_type=model["model_type"],
                target_variable=model["target_variable"],
                features=model["features"],
                hyperparameters=model["hyperparameters"],
                model_status=model["model_status"],
                accuracy_score=model.get("accuracy_score", 0.0),
                created_at=model["created_at"],
                updated_at=model["updated_at"],
            )
            for model in models
        ]
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise BusinessError(
            code="MODEL_LIST_FAILED", message=f"获取模型列表失败: {str(e)}"
        )


# 获取单个模型
@router.get("/{model_id}", response_model=ModelResponse)
@handle_errors
async def get_model(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """获取单个模型"""
    try:
        model = await training_service.get_model_by_id(
            model_id, current_user["tenant_id"]
        )

        if not model:
            raise BusinessError(code="MODEL_NOT_FOUND", message="模型不存在")

        return ModelResponse(
            id=model["id"],
            model_name=model.get("model_name", f"model_{model['id'][:8]}"),
            model_type=model["model_type"],
            target_variable=model["target_variable"],
            features=model["features"],
            hyperparameters=model["hyperparameters"],
            model_status=model["model_status"],
            accuracy_score=model.get("accuracy_score", 0.0),
            created_at=model["created_at"],
            updated_at=model["updated_at"],
        )
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取模型失败: {e}")
        raise BusinessError(
            code="MODEL_RETRIEVAL_FAILED", message=f"获取模型失败: {str(e)}"
        )


# 更新模型
@router.put("/{model_id}", response_model=ModelResponse)
@handle_errors
async def update_model(
    model_id: str,
    model_data: ModelUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """更新模型"""
    try:
        # 检查模型是否存在
        model = await training_service.get_model_by_id(
            model_id, current_user["tenant_id"]
        )
        if not model:
            raise BusinessError(code="MODEL_NOT_FOUND", message="模型不存在")

        # 更新模型
        updated_model = await training_service.update_model(
            model_id=model_id,
            tenant_id=current_user["tenant_id"],
            model_name=model_data.model_name,
            description=model_data.description,
            hyperparameters=model_data.hyperparameters,
        )

        return ModelResponse(
            id=updated_model["id"],
            model_name=updated_model.get(
                "model_name", f"model_{updated_model['id'][:8]}"
            ),
            model_type=updated_model["model_type"],
            target_variable=updated_model["target_variable"],
            features=updated_model["features"],
            hyperparameters=updated_model["hyperparameters"],
            model_status=updated_model["model_status"],
            accuracy_score=updated_model.get("accuracy_score", 0.0),
            created_at=updated_model["created_at"],
            updated_at=updated_model["updated_at"],
        )
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"更新模型失败: {e}")
        raise BusinessError(
            code="MODEL_UPDATE_FAILED", message=f"更新模型失败: {str(e)}"
        )


# 删除模型
@router.delete("/{model_id}")
@handle_errors
async def delete_model(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """删除模型"""
    try:
        # 检查模型是否存在
        model = await training_service.get_model_by_id(
            model_id, current_user["tenant_id"]
        )
        if not model:
            raise BusinessError(code="MODEL_NOT_FOUND", message="模型不存在")

        # 删除模型
        await training_service.delete_model(model_id, current_user["tenant_id"])

        return {"success": True, "message": "模型删除成功"}
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"删除模型失败: {e}")
        raise BusinessError(
            code="MODEL_DELETE_FAILED", message=f"删除模型失败: {str(e)}"
        )


# 训练模型
@router.post("/train", response_model=Dict[str, Any])
@handle_errors
async def train_model(
    request: ModelTrainingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    training_service: ModelTrainingService = Depends(lambda: ModelTrainingService()),
):
    """训练模型"""
    try:
        model_id = str(uuid.uuid4())

        # 训练模型
        result = await training_service.train_model(
            model_id=model_id,
            model_type=request.model_type,
            target_variable=request.target_variable,
            features=request.features,
            hyperparameters=request.hyperparameters,
            training_data=request.training_data,
            tenant_id=current_user["tenant_id"],
        )

        return {
            "success": True,
            "model_id": model_id,
            "accuracy": result.get("accuracy", 0.0),
            "message": "模型训练成功",
        }
    except Exception as e:
        logger.error(f"模型训练失败: {e}")
        raise BusinessError(
            code="MODEL_TRAINING_FAILED", message=f"模型训练失败: {str(e)}"
        )


# 数据关系分析
@router.post("/analyze")
@handle_errors
async def analyze_data_relationships(
    data: Dict[str, Any],
    analysis_types: Optional[List[str]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """分析数据关系"""
    try:
        # 解析数据
        X = pd.DataFrame(data.get("features", {}))
        y = pd.Series(data.get("target", []))

        if X.empty or y.empty:
            raise BusinessError(code="INVALID_DATA", message="数据不能为空")

        # 执行分析
        results = algorithm_service.analyze_data_relationships(X, y, analysis_types)

        return {"success": True, "analysis_results": results, "status": "completed"}

    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"数据关系分析失败: {e}")
        raise BusinessError(
            code="ANALYSIS_FAILED", message=f"数据关系分析失败: {str(e)}"
        )


# 权重优化
@router.post("/optimize-weights")
@handle_errors
async def optimize_weights(
    data: Dict[str, Any],
    optimization_method: str = "comprehensive",
    validation_methods: Optional[List[str]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """优化权重"""
    try:
        # 解析数据
        X = pd.DataFrame(data.get("features", {}))
        y = pd.Series(data.get("target", []))

        if X.empty or y.empty:
            raise BusinessError(code="INVALID_DATA", message="数据不能为空")

        # 执行权重优化
        results = algorithm_service.optimize_weights(
            X, y, optimization_method, validation_methods
        )

        return {"success": True, "optimization_results": results, "status": "completed"}

    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"权重优化失败: {e}")
        raise BusinessError(
            code="OPTIMIZATION_FAILED", message=f"权重优化失败: {str(e)}"
        )


# 使用优化权重进行预测
@router.post("/predict")
@handle_errors
async def predict_with_optimized_weights(
    data: Dict[str, Any],
    weights: Dict[str, float],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """使用优化权重进行预测"""
    try:
        # 解析数据
        X = pd.DataFrame(data.get("features", {}))
        y = pd.Series(data.get("target", []))
        X_test = pd.DataFrame(data.get("test_features", {}))

        if X.empty or y.empty or X_test.empty:
            raise BusinessError(code="INVALID_DATA", message="数据不能为空")

        # 执行预测
        results = algorithm_service.predict_with_optimized_weights(
            X, y, X_test, weights
        )

        return {"success": True, "predictions": results, "status": "completed"}

    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"预测失败: {e}")
        raise BusinessError(code="PREDICTION_FAILED", message=f"预测失败: {str(e)}")


# 获取算法洞察
@router.get("/insights")
@handle_errors
async def get_algorithm_insights(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """获取算法洞察"""
    try:
        insights = algorithm_service.get_algorithm_insights()

        return {"success": True, "insights": insights, "status": "completed"}

    except Exception as e:
        logger.error(f"获取算法洞察失败: {e}")
        raise BusinessError(
            code="INSIGHTS_FAILED", message=f"获取算法洞察失败: {str(e)}"
        )
