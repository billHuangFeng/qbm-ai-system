"""
BMOS模型训练API端点 - 增强版
提供完整的模型训练、评估、预测和管理功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime
import asyncio
import pandas as pd
import numpy as np

from ..services.enhanced_model_training import (
    ModelTrainingService, 
    ModelConfig, 
    TrainingResult, 
    ModelPrediction,
    model_training_service
)
from ..services.enhanced_data_import import data_import_service
from ..api.dependencies import get_current_user
from ..models.base import User

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/model-training", tags=["模型训练"])

@router.post("/train", response_model=TrainingResult)
async def train_model(
    config: ModelConfig,
    data_file: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    训练机器学习模型
    
    - **config**: 模型配置
    - **data_file**: 数据文件名（可选，使用已上传的文件）
    - **current_user**: 当前用户
    
    返回训练结果
    """
    try:
        logger.info(f"用户 {current_user.username} 开始训练模型: {config.algorithm}")
        
        # 获取数据
        if data_file:
            # 使用已上传的文件
            file_path = data_import_service.upload_dir / data_file
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="数据文件不存在")
            
            df = await data_import_service.parse_file(str(file_path))
        else:
            # 使用演示数据
            df = create_demo_data(config.model_type)
        
        # 训练模型
        result = await model_training_service.train_complete_model(df, config)
        
        logger.info(f"模型训练完成: {result.model_id}")
        return result
        
    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型训练失败: {str(e)}")

@router.post("/train-from-upload")
async def train_model_from_upload(
    file: UploadFile = File(...),
    algorithm: str = "random_forest_classifier",
    target_column: str = "target",
    feature_columns: Optional[List[str]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    从上传的文件训练模型
    
    - **file**: 数据文件
    - **algorithm**: 算法名称
    - **target_column**: 目标列名
    - **feature_columns**: 特征列名（可选，自动检测）
    - **parameters**: 模型参数（可选）
    - **current_user**: 当前用户
    
    返回训练结果
    """
    try:
        logger.info(f"用户 {current_user.username} 从上传文件训练模型: {algorithm}")
        
        # 上传并解析文件
        upload_result = await data_import_service.import_data(file)
        if not upload_result.success:
            raise HTTPException(status_code=400, detail=f"文件处理失败: {upload_result.message}")
        
        # 解析数据
        df = await data_import_service.parse_file(upload_result.file_path)
        
        # 自动检测特征列
        if not feature_columns:
            feature_columns = [col for col in df.columns if col != target_column]
        
        # 创建配置
        config = ModelConfig(
            model_type="classification" if algorithm.endswith('_classifier') else "regression",
            algorithm=algorithm,
            target_column=target_column,
            feature_columns=feature_columns,
            parameters=parameters or {}
        )
        
        # 训练模型
        result = await model_training_service.train_complete_model(df, config)
        
        logger.info(f"模型训练完成: {result.model_id}")
        return result
        
    except Exception as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型训练失败: {str(e)}")

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_models(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取已训练的模型列表
    
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回模型列表
    """
    try:
        logger.info(f"用户 {current_user.username} 查询模型列表")
        
        models = model_training_service.get_model_list()
        
        # 限制返回数量
        if limit > 0:
            models = models[:limit]
        
        return models
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@router.get("/models/{model_id}")
async def get_model_info(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取模型详细信息
    
    - **model_id**: 模型ID
    - **current_user**: 当前用户
    
    返回模型信息
    """
    try:
        logger.info(f"用户 {current_user.username} 查询模型: {model_id}")
        
        model, model_info = model_training_service.load_model(model_id)
        
        return {
            "model_info": model_info,
            "model_type": str(type(model).__name__),
            "is_loaded": True
        }
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=404, detail=f"模型不存在: {model_id}")

@router.post("/models/{model_id}/predict")
async def predict_with_model(
    model_id: str,
    features: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    使用模型进行预测
    
    - **model_id**: 模型ID
    - **features**: 特征数据
    - **current_user**: 当前用户
    
    返回预测结果
    """
    try:
        logger.info(f"用户 {current_user.username} 使用模型 {model_id} 进行预测")
        
        # 加载模型
        model, model_info = model_training_service.load_model(model_id)
        
        # 准备特征数据
        feature_df = pd.DataFrame([features])
        
        # 确保特征列顺序正确
        config = model_info['config']
        expected_features = config['feature_columns']
        
        # 检查特征
        missing_features = [f for f in expected_features if f not in features]
        if missing_features:
            raise HTTPException(
                status_code=400, 
                detail=f"缺少特征: {missing_features}"
            )
        
        # 重新排列特征
        feature_df = feature_df[expected_features]
        
        # 预测
        prediction = model_training_service.predict(model, feature_df)
        
        logger.info(f"预测完成: {prediction.prediction}")
        
        return {
            "model_id": model_id,
            "prediction": prediction.prediction,
            "confidence": prediction.confidence,
            "probabilities": prediction.probabilities,
            "feature_contributions": prediction.feature_contributions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"模型预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型预测失败: {str(e)}")

@router.post("/models/{model_id}/batch-predict")
async def batch_predict_with_model(
    model_id: str,
    features_list: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """
    批量预测
    
    - **model_id**: 模型ID
    - **features_list**: 特征数据列表
    - **current_user**: 当前用户
    
    返回批量预测结果
    """
    try:
        logger.info(f"用户 {current_user.username} 使用模型 {model_id} 进行批量预测: {len(features_list)} 条")
        
        # 加载模型
        model, model_info = model_training_service.load_model(model_id)
        
        # 准备特征数据
        feature_df = pd.DataFrame(features_list)
        
        # 确保特征列顺序正确
        config = model_info['config']
        expected_features = config['feature_columns']
        
        # 检查特征
        missing_features = [f for f in expected_features if f not in feature_df.columns]
        if missing_features:
            raise HTTPException(
                status_code=400, 
                detail=f"缺少特征: {missing_features}"
            )
        
        # 重新排列特征
        feature_df = feature_df[expected_features]
        
        # 批量预测
        predictions = model.predict(feature_df)
        
        # 获取置信度（如果是分类模型）
        confidences = None
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(feature_df)
            confidences = [float(np.max(proba)) for proba in probas]
        
        results = []
        for i, pred in enumerate(predictions):
            result = {
                "index": i,
                "prediction": float(pred) if isinstance(pred, (int, float)) else pred,
                "confidence": confidences[i] if confidences else None
            }
            results.append(result)
        
        logger.info(f"批量预测完成: {len(results)} 条结果")
        
        return {
            "model_id": model_id,
            "total_predictions": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"批量预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量预测失败: {str(e)}")

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    删除模型
    
    - **model_id**: 模型ID
    - **current_user**: 当前用户
    
    返回删除结果
    """
    try:
        logger.info(f"用户 {current_user.username} 删除模型: {model_id}")
        
        success = model_training_service.delete_model(model_id)
        
        if success:
            return {"message": "模型删除成功", "model_id": model_id}
        else:
            raise HTTPException(status_code=404, detail="模型不存在")
        
    except Exception as e:
        logger.error(f"模型删除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模型删除失败: {str(e)}")

@router.get("/algorithms")
async def get_supported_algorithms():
    """
    获取支持的算法列表
    
    返回支持的算法和参数
    """
    try:
        algorithms = {}
        
        for algo_name, algo_class in model_training_service.supported_algorithms.items():
            algorithms[algo_name] = {
                "name": algo_name,
                "class": algo_class.__name__,
                "type": "classification" if algo_name.endswith('_classifier') else "regression",
                "default_parameters": model_training_service.default_parameters.get(algo_name, {}),
                "description": get_algorithm_description(algo_name)
            }
        
        return {
            "supported_algorithms": algorithms,
            "total_count": len(algorithms)
        }
        
    except Exception as e:
        logger.error(f"获取算法列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取算法列表失败: {str(e)}")

@router.post("/demo-train")
async def demo_train_model(
    model_type: str = "classification",
    algorithm: str = "random_forest_classifier",
    current_user: User = Depends(get_current_user)
):
    """
    演示模型训练
    
    - **model_type**: 模型类型 (classification/regression)
    - **algorithm**: 算法名称
    - **current_user**: 当前用户
    
    返回演示训练结果
    """
    try:
        logger.info(f"用户 {current_user.username} 开始演示训练: {algorithm}")
        
        # 创建演示数据
        df = create_demo_data(model_type)
        
        # 创建配置
        config = ModelConfig(
            model_type=model_type,
            algorithm=algorithm,
            target_column="target",
            feature_columns=[col for col in df.columns if col != "target"],
            parameters={"n_estimators": 50, "max_depth": 5}
        )
        
        # 训练模型
        result = await model_training_service.train_complete_model(df, config)
        
        logger.info(f"演示训练完成: {result.model_id}")
        
        return {
            "message": "演示训练完成",
            "result": result,
            "demo_data_info": {
                "rows": len(df),
                "columns": list(df.columns),
                "target_distribution": df["target"].value_counts().to_dict() if model_type == "classification" else None
            }
        }
        
    except Exception as e:
        logger.error(f"演示训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"演示训练失败: {str(e)}")

@router.get("/stats")
async def get_training_stats(
    current_user: User = Depends(get_current_user)
):
    """
    获取训练统计信息
    
    - **current_user**: 当前用户
    
    返回统计信息
    """
    try:
        logger.info(f"用户 {current_user.username} 查询训练统计")
        
        models = model_training_service.get_model_list()
        
        # 计算统计信息
        total_models = len(models)
        algorithms = {}
        model_types = {"classification": 0, "regression": 0}
        
        for model in models:
            algo = model['config']['algorithm']
            model_type = model['config']['model_type']
            
            algorithms[algo] = algorithms.get(algo, 0) + 1
            model_types[model_type] = model_types.get(model_type, 0) + 1
        
        # 最近7天的训练
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_models = [
            m for m in models 
            if datetime.fromisoformat(m['created_at']) > week_ago
        ]
        
        return {
            "total_models": total_models,
            "algorithms": algorithms,
            "model_types": model_types,
            "recent_models_7days": len(recent_models),
            "models_directory": str(model_training_service.models_dir),
            "supported_algorithms": list(model_training_service.supported_algorithms.keys())
        }
        
    except Exception as e:
        logger.error(f"获取训练统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取训练统计失败: {str(e)}")

# 辅助函数
def create_demo_data(model_type: str) -> pd.DataFrame:
    """创建演示数据"""
    import numpy as np
    
    np.random.seed(42)
    n_samples = 500
    
    if model_type == "classification":
        df = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples),
            'feature4': np.random.normal(0, 1, n_samples),
            'target': np.random.choice(['A', 'B', 'C'], n_samples)
        })
    else:  # regression
        df = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples),
            'feature4': np.random.normal(0, 1, n_samples),
            'target': np.random.normal(0, 1, n_samples)
        })
    
    return df

def get_algorithm_description(algorithm: str) -> str:
    """获取算法描述"""
    descriptions = {
        "random_forest_classifier": "随机森林分类器 - 集成学习，适合分类任务",
        "random_forest_regressor": "随机森林回归器 - 集成学习，适合回归任务",
        "xgboost_classifier": "XGBoost分类器 - 梯度提升，高性能分类",
        "xgboost_regressor": "XGBoost回归器 - 梯度提升，高性能回归",
        "lightgbm_classifier": "LightGBM分类器 - 轻量级梯度提升，快速训练",
        "lightgbm_regressor": "LightGBM回归器 - 轻量级梯度提升，快速训练"
    }
    return descriptions.get(algorithm, "未知算法")

# 健康检查端点
@router.get("/health")
async def health_check():
    """模型训练服务健康检查"""
    try:
        # 检查模型目录
        models_dir_exists = model_training_service.models_dir.exists()
        
        # 检查权限
        can_write = os.access(model_training_service.models_dir, os.W_OK)
        
        return {
            "status": "healthy" if models_dir_exists and can_write else "unhealthy",
            "models_directory": str(model_training_service.models_dir),
            "directory_exists": models_dir_exists,
            "can_write": can_write,
            "supported_algorithms": list(model_training_service.supported_algorithms.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


