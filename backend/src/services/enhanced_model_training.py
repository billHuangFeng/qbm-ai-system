"""
BMOS模型训练服务 - 增强版
实现完整的机器学习模型训练、评估和部署功能
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import json
import logging
import pickle
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)

class ModelConfig(BaseModel):
    """模型配置"""
    model_type: str = Field(..., description="模型类型")
    algorithm: str = Field(..., description="算法名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="模型参数")
    target_column: str = Field(..., description="目标列名")
    feature_columns: List[str] = Field(..., description="特征列名")
    test_size: float = Field(default=0.2, description="测试集比例")
    random_state: int = Field(default=42, description="随机种子")

class TrainingResult(BaseModel):
    """训练结果"""
    model_id: str
    model_name: str
    algorithm: str
    training_status: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    r2_score: Optional[float] = None
    cross_val_scores: List[float] = []
    feature_importance: Dict[str, float] = {}
    training_time: float
    training_samples: int
    validation_samples: int
    model_path: str
    created_at: datetime

class ModelPrediction(BaseModel):
    """模型预测结果"""
    prediction: Union[float, int, str, List[Union[float, int, str]]]
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    feature_contributions: Optional[Dict[str, float]] = None

class ModelTrainingService:
    """模型训练服务"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # 支持的算法
        self.supported_algorithms = {
            "random_forest_classifier": RandomForestClassifier,
            "random_forest_regressor": RandomForestRegressor,
            "xgboost_classifier": xgb.XGBClassifier,
            "xgboost_regressor": xgb.XGBRegressor,
            "lightgbm_classifier": lgb.LGBMClassifier,
            "lightgbm_regressor": lgb.LGBMRegressor
        }
        
        # 默认参数
        self.default_parameters = {
            "random_forest_classifier": {
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            },
            "random_forest_regressor": {
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            },
            "xgboost_classifier": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42
            },
            "xgboost_regressor": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42
            },
            "lightgbm_classifier": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42
            },
            "lightgbm_regressor": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42
            }
        }
    
    def prepare_data(self, df: pd.DataFrame, config: ModelConfig) -> Tuple[pd.DataFrame, pd.Series]:
        """准备训练数据"""
        try:
            # 检查列是否存在
            all_columns = config.feature_columns + [config.target_column]
            missing_columns = [col for col in all_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"缺少列: {missing_columns}")
            
            # 选择特征和目标
            X = df[config.feature_columns].copy()
            y = df[config.target_column].copy()
            
            # 处理缺失值
            X = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else X.mode().iloc[0])
            y = y.fillna(y.mean() if y.dtype in ['int64', 'float64'] else y.mode().iloc[0])
            
            # 处理分类变量
            for col in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
            
            # 处理目标变量（如果是分类）
            if y.dtype == 'object':
                le_target = LabelEncoder()
                y = le_target.fit_transform(y.astype(str))
            
            logger.info(f"数据准备完成: 特征 {X.shape}, 目标 {y.shape}")
            return X, y
            
        except Exception as e:
            logger.error(f"数据准备失败: {str(e)}")
            raise
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, config: ModelConfig) -> Tuple[Any, Dict[str, Any]]:
        """训练模型"""
        try:
            start_time = datetime.now()
            
            # 获取算法类
            if config.algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的算法: {config.algorithm}")
            
            algorithm_class = self.supported_algorithms[config.algorithm]
            
            # 合并默认参数和用户参数
            params = self.default_parameters[config.algorithm].copy()
            params.update(config.parameters)
            
            # 创建模型
            model = algorithm_class(**params)
            
            # 训练模型
            model.fit(X, y)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # 获取特征重要性
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, model.feature_importances_))
            
            logger.info(f"模型训练完成: {config.algorithm}, 耗时: {training_time:.2f}秒")
            
            return model, {
                "training_time": training_time,
                "feature_importance": feature_importance,
                "parameters": params
            }
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            raise
    
    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, 
                      config: ModelConfig) -> Dict[str, Any]:
        """评估模型"""
        try:
            # 预测
            y_pred = model.predict(X_test)
            
            # 计算指标
            metrics = {}
            
            # 分类指标
            if config.algorithm.endswith('_classifier'):
                metrics['accuracy'] = accuracy_score(y_test, y_pred)
                metrics['precision'] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                metrics['recall'] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                # 获取预测概率
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)
                    metrics['probabilities'] = y_proba.tolist()
            
            # 回归指标
            elif config.algorithm.endswith('_regressor'):
                metrics['mse'] = mean_squared_error(y_test, y_pred)
                metrics['r2_score'] = r2_score(y_test, y_pred)
                metrics['rmse'] = np.sqrt(metrics['mse'])
            
            logger.info(f"模型评估完成: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"模型评估失败: {str(e)}")
            raise
    
    def cross_validate_model(self, model: Any, X: pd.DataFrame, y: pd.Series, 
                           cv: int = 5) -> List[float]:
        """交叉验证"""
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy' if 'classifier' in str(type(model)) else 'r2')
            logger.info(f"交叉验证完成: {scores}")
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"交叉验证失败: {str(e)}")
            return []
    
    def save_model(self, model: Any, config: ModelConfig, metrics: Dict[str, Any], 
                  model_id: str) -> str:
        """保存模型"""
        try:
            # 创建模型目录
            model_dir = self.models_dir / model_id
            model_dir.mkdir(exist_ok=True)
            
            # 保存模型
            model_path = model_dir / "model.pkl"
            joblib.dump(model, model_path)
            
            # 保存配置和指标
            model_info = {
                "model_id": model_id,
                "config": config.dict(),
                "metrics": metrics,
                "created_at": datetime.now().isoformat(),
                "model_path": str(model_path)
            }
            
            info_path = model_dir / "model_info.json"
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(model_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模型保存成功: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"模型保存失败: {str(e)}")
            raise
    
    def load_model(self, model_id: str) -> Tuple[Any, Dict[str, Any]]:
        """加载模型"""
        try:
            model_dir = self.models_dir / model_id
            
            # 加载模型
            model_path = model_dir / "model.pkl"
            model = joblib.load(model_path)
            
            # 加载信息
            info_path = model_dir / "model_info.json"
            with open(info_path, 'r', encoding='utf-8') as f:
                model_info = json.load(f)
            
            logger.info(f"模型加载成功: {model_id}")
            return model, model_info
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise
    
    def predict(self, model: Any, X: pd.DataFrame) -> ModelPrediction:
        """模型预测"""
        try:
            # 预测
            prediction = model.predict(X)
            
            # 获取置信度（分类模型）
            confidence = None
            probabilities = None
            
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                confidence = float(np.max(proba))
                probabilities = dict(zip(model.classes_, proba[0]))
            
            # 获取特征贡献（如果支持）
            feature_contributions = None
            if hasattr(model, 'feature_importances_'):
                feature_contributions = dict(zip(X.columns, model.feature_importances_))
            
            # 处理预测结果
            if len(prediction) == 1:
                pred_value = float(prediction[0])
            else:
                pred_value = prediction.tolist()
            
            # 处理概率字典的键类型
            if probabilities:
                probabilities = {str(k): float(v) for k, v in probabilities.items()}
            
            return ModelPrediction(
                prediction=pred_value,
                confidence=confidence,
                probabilities=probabilities,
                feature_contributions=feature_contributions
            )
            
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            raise
    
    async def train_complete_model(self, df: pd.DataFrame, config: ModelConfig) -> TrainingResult:
        """完整的模型训练流程"""
        try:
            model_id = f"{config.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"开始训练模型: {model_id}")
            
            # 1. 准备数据
            X, y = self.prepare_data(df, config)
            
            # 2. 划分训练测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state
            )
            
            # 3. 训练模型
            model, training_info = self.train_model(X_train, y_train, config)
            
            # 4. 评估模型
            metrics = self.evaluate_model(model, X_test, y_test, config)
            
            # 5. 交叉验证
            cv_scores = self.cross_validate_model(model, X_train, y_train)
            
            # 6. 保存模型
            model_path = self.save_model(model, config, metrics, model_id)
            
            # 7. 创建训练结果
            result = TrainingResult(
                model_id=model_id,
                model_name=f"{config.algorithm}_{config.target_column}",
                algorithm=config.algorithm,
                training_status="completed",
                accuracy=metrics.get('accuracy'),
                precision=metrics.get('precision'),
                recall=metrics.get('recall'),
                f1_score=metrics.get('f1_score'),
                mse=metrics.get('mse'),
                r2_score=metrics.get('r2_score'),
                cross_val_scores=cv_scores,
                feature_importance=training_info['feature_importance'],
                training_time=training_info['training_time'],
                training_samples=len(X_train),
                validation_samples=len(X_test),
                model_path=model_path,
                created_at=datetime.now()
            )
            
            logger.info(f"模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"完整训练流程失败: {str(e)}")
            raise
    
    def get_model_list(self) -> List[Dict[str, Any]]:
        """获取模型列表"""
        try:
            models = []
            
            for model_dir in self.models_dir.iterdir():
                if model_dir.is_dir():
                    info_path = model_dir / "model_info.json"
                    if info_path.exists():
                        with open(info_path, 'r', encoding='utf-8') as f:
                            model_info = json.load(f)
                        models.append(model_info)
            
            # 按创建时间排序
            models.sort(key=lambda x: x['created_at'], reverse=True)
            return models
            
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return []
    
    def delete_model(self, model_id: str) -> bool:
        """删除模型"""
        try:
            model_dir = self.models_dir / model_id
            
            if model_dir.exists():
                import shutil
                shutil.rmtree(model_dir)
                logger.info(f"模型删除成功: {model_id}")
                return True
            else:
                logger.warning(f"模型不存在: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"模型删除失败: {str(e)}")
            return False

# 创建全局实例
model_training_service = ModelTrainingService()

# 示例使用函数
async def demo_model_training():
    """演示模型训练功能"""
    print("BMOS模型训练服务演示")
    print("=" * 50)
    
    # 创建示例数据
    np.random.seed(42)
    n_samples = 1000
    
    # 分类数据
    classification_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(0, 1, n_samples),
        'feature3': np.random.normal(0, 1, n_samples),
        'target': np.random.choice(['A', 'B', 'C'], n_samples)
    })
    
    # 回归数据
    regression_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(0, 1, n_samples),
        'feature3': np.random.normal(0, 1, n_samples),
        'target': np.random.normal(0, 1, n_samples)
    })
    
    print(f"分类数据形状: {classification_data.shape}")
    print(f"回归数据形状: {regression_data.shape}")
    
    # 测试分类模型
    print("\n1. 测试分类模型训练:")
    config_classification = ModelConfig(
        model_type="classification",
        algorithm="random_forest_classifier",
        target_column="target",
        feature_columns=["feature1", "feature2", "feature3"],
        parameters={"n_estimators": 50, "max_depth": 5}
    )
    
    result_classification = await model_training_service.train_complete_model(
        classification_data, config_classification
    )
    
    print(f"分类模型训练完成:")
    print(f"  模型ID: {result_classification.model_id}")
    print(f"  准确率: {result_classification.accuracy:.3f}")
    print(f"  训练时间: {result_classification.training_time:.2f}秒")
    
    # 测试回归模型
    print("\n2. 测试回归模型训练:")
    config_regression = ModelConfig(
        model_type="regression",
        algorithm="random_forest_regressor",
        target_column="target",
        feature_columns=["feature1", "feature2", "feature3"],
        parameters={"n_estimators": 50, "max_depth": 5}
    )
    
    result_regression = await model_training_service.train_complete_model(
        regression_data, config_regression
    )
    
    print(f"回归模型训练完成:")
    print(f"  模型ID: {result_regression.model_id}")
    print(f"  R2分数: {result_regression.r2_score:.3f}")
    print(f"  训练时间: {result_regression.training_time:.2f}秒")
    
    # 测试模型预测
    print("\n3. 测试模型预测:")
    model, model_info = model_training_service.load_model(result_classification.model_id)
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'feature1': [0.5, -0.3, 1.2],
        'feature2': [0.8, -1.1, 0.4],
        'feature3': [-0.2, 0.7, -0.9]
    })
    
    prediction = model_training_service.predict(model, test_data)
    print(f"预测结果: {prediction.prediction}")
    if prediction.confidence:
        print(f"置信度: {prediction.confidence:.3f}")
    
    # 获取模型列表
    print("\n4. 获取模型列表:")
    models = model_training_service.get_model_list()
    print(f"已训练模型数量: {len(models)}")
    
    for i, model in enumerate(models[:2]):  # 只显示前2个
        print(f"  {i+1}. {model['model_id']} - {model['config']['algorithm']}")
    
    print("\n模型训练服务演示完成!")

if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_model_training())
