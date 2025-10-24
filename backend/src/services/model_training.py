"""
模型训练服务
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import lightgbm as lgb
from sklearn.neural_network import MLPRegressor
import joblib
import os
from datetime import datetime
import logging
from ..exceptions import ModelError, ValidationError
from ..logging_config import get_logger

logger = get_logger("model_training")

class ModelTrainingService:
    """模型训练服务"""
    
    def __init__(self):
        self.models = {}
        self.training_history = {}
        self.model_versions = {}
    
    def train_linear_regression(self, X: pd.DataFrame, y: pd.Series, 
                              test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """训练线性回归模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # 保存模型
            model_id = f"linear_regression_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            
            result = {
                'model_id': model_id,
                'model_type': 'linear_regression',
                'metrics': metrics,
                'feature_importance': dict(zip(X.columns, model.coef_)),
                'model': model
            }
            
            logger.info(f"线性回归模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"线性回归模型训练失败: {e}")
            raise ModelError(f"线性回归模型训练失败: {e}")
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series, 
                          n_estimators: int = 100, max_depth: int = 10,
                          test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """训练随机森林模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state
            )
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # 保存模型
            model_id = f"random_forest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            
            result = {
                'model_id': model_id,
                'model_type': 'random_forest',
                'metrics': metrics,
                'feature_importance': dict(zip(X.columns, model.feature_importances_)),
                'model': model
            }
            
            logger.info(f"随机森林模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"随机森林模型训练失败: {e}")
            raise ModelError(f"随机森林模型训练失败: {e}")
    
    def train_xgboost(self, X: pd.DataFrame, y: pd.Series, 
                     n_estimators: int = 100, max_depth: int = 6,
                     learning_rate: float = 0.1, test_size: float = 0.2, 
                     random_state: int = 42) -> Dict[str, Any]:
        """训练XGBoost模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model = xgb.XGBRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=random_state
            )
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # 保存模型
            model_id = f"xgboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            
            result = {
                'model_id': model_id,
                'model_type': 'xgboost',
                'metrics': metrics,
                'feature_importance': dict(zip(X.columns, model.feature_importances_)),
                'model': model
            }
            
            logger.info(f"XGBoost模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"XGBoost模型训练失败: {e}")
            raise ModelError(f"XGBoost模型训练失败: {e}")
    
    def train_lightgbm(self, X: pd.DataFrame, y: pd.Series, 
                      n_estimators: int = 100, max_depth: int = 6,
                      learning_rate: float = 0.1, test_size: float = 0.2, 
                      random_state: int = 42) -> Dict[str, Any]:
        """训练LightGBM模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model = lgb.LGBMRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=random_state,
                verbose=-1
            )
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # 保存模型
            model_id = f"lightgbm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            
            result = {
                'model_id': model_id,
                'model_type': 'lightgbm',
                'metrics': metrics,
                'feature_importance': dict(zip(X.columns, model.feature_importances_)),
                'model': model
            }
            
            logger.info(f"LightGBM模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"LightGBM模型训练失败: {e}")
            raise ModelError(f"LightGBM模型训练失败: {e}")
    
    def train_mlp(self, X: pd.DataFrame, y: pd.Series, 
                  hidden_layer_sizes: Tuple = (100, 50), max_iter: int = 1000,
                  test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """训练多层感知机模型"""
        try:
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练模型
            model = MLPRegressor(
                hidden_layer_sizes=hidden_layer_sizes,
                max_iter=max_iter,
                random_state=random_state
            )
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            metrics = self._calculate_metrics(y_test, y_pred)
            
            # 保存模型
            model_id = f"mlp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            
            result = {
                'model_id': model_id,
                'model_type': 'mlp',
                'metrics': metrics,
                'feature_importance': None,  # MLP没有特征重要性
                'model': model
            }
            
            logger.info(f"MLP模型训练完成: {model_id}")
            return result
            
        except Exception as e:
            logger.error(f"MLP模型训练失败: {e}")
            raise ModelError(f"MLP模型训练失败: {e}")
    
    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """计算评估指标"""
        try:
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
            
        except Exception as e:
            logger.error(f"评估指标计算失败: {e}")
            raise ModelError(f"评估指标计算失败: {e}")
    
    def cross_validate(self, model: Any, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> List[float]:
        """交叉验证"""
        try:
            scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
            logger.info(f"交叉验证完成: {cv} 折，平均分数: {scores.mean():.4f}")
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"交叉验证失败: {e}")
            raise ModelError(f"交叉验证失败: {e}")
    
    def tune_hyperparameters(self, model: Any, X: pd.DataFrame, y: pd.Series, 
                           param_grid: Dict[str, List], cv: int = 3) -> Tuple[Dict[str, Any], float]:
        """超参数调优"""
        try:
            grid_search = GridSearchCV(
                model, param_grid, cv=cv, scoring='r2', n_jobs=-1
            )
            grid_search.fit(X, y)
            
            best_params = grid_search.best_params_
            best_score = grid_search.best_score_
            
            logger.info(f"超参数调优完成: {best_params}, 最佳分数: {best_score:.4f}")
            return best_params, best_score
            
        except Exception as e:
            logger.error(f"超参数调优失败: {e}")
            raise ModelError(f"超参数调优失败: {e}")
    
    def save_model(self, model: Any, filepath: str) -> str:
        """保存模型"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存模型
            joblib.dump(model, filepath)
            
            logger.info(f"模型保存成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
            raise ModelError(f"模型保存失败: {e}")
    
    def load_model(self, filepath: str) -> Any:
        """加载模型"""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"模型文件不存在: {filepath}")
            
            model = joblib.load(filepath)
            
            logger.info(f"模型加载成功: {filepath}")
            return model
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise ModelError(f"模型加载失败: {e}")
    
    def compare_models(self, models: List[Any], X: pd.DataFrame, y: pd.Series, cv: int = 5) -> List[Dict[str, Any]]:
        """比较模型性能"""
        try:
            results = []
            
            for model in models:
                # 交叉验证
                cv_scores = self.cross_validate(model, X, y, cv)
                
                # 训练模型
                model.fit(X, y)
                
                # 预测
                y_pred = model.predict(X)
                metrics = self._calculate_metrics(y, y_pred)
                
                result = {
                    'model_name': model.__class__.__name__,
                    'cv_scores': cv_scores,
                    'mean_score': np.mean(cv_scores),
                    'std_score': np.std(cv_scores),
                    'metrics': metrics
                }
                
                results.append(result)
            
            # 按平均分数排序
            results.sort(key=lambda x: x['mean_score'], reverse=True)
            
            logger.info(f"模型比较完成: {len(results)} 个模型")
            return results
            
        except Exception as e:
            logger.error(f"模型比较失败: {e}")
            raise ModelError(f"模型比较失败: {e}")
    
    def select_features(self, model: Any, X: pd.DataFrame, y: pd.Series, k: int = 10) -> List[str]:
        """特征选择"""
        try:
            from sklearn.feature_selection import SelectKBest, f_regression
            
            # 特征选择
            selector = SelectKBest(score_func=f_regression, k=k)
            X_selected = selector.fit_transform(X, y)
            
            # 获取选中的特征
            selected_features = X.columns[selector.get_support()].tolist()
            
            logger.info(f"特征选择完成: 从 {len(X.columns)} 个特征中选择 {len(selected_features)} 个")
            return selected_features
            
        except Exception as e:
            logger.error(f"特征选择失败: {e}")
            raise ModelError(f"特征选择失败: {e}")
    
    def validate_model(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """验证模型"""
        try:
            # 预测
            y_pred = model.predict(X)
            
            # 计算残差
            residuals = y - y_pred
            
            # 计算指标
            metrics = self._calculate_metrics(y, y_pred)
            
            result = {
                'predictions': y_pred.tolist(),
                'metrics': metrics,
                'residuals': residuals.tolist(),
                'residual_mean': residuals.mean(),
                'residual_std': residuals.std()
            }
            
            logger.info(f"模型验证完成: R² = {metrics['r2']:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"模型验证失败: {e}")
            raise ModelError(f"模型验证失败: {e}")
    
    def interpret_model(self, model: Any, feature_names: List[str]) -> Dict[str, Any]:
        """解释模型"""
        try:
            interpretation = {
                'feature_importance': None,
                'coefficients': None,
                'model_type': model.__class__.__name__
            }
            
            # 获取特征重要性
            if hasattr(model, 'feature_importances_'):
                interpretation['feature_importance'] = dict(zip(feature_names, model.feature_importances_))
            
            # 获取系数
            if hasattr(model, 'coef_'):
                interpretation['coefficients'] = dict(zip(feature_names, model.coef_))
            
            logger.info(f"模型解释完成: {model.__class__.__name__}")
            return interpretation
            
        except Exception as e:
            logger.error(f"模型解释失败: {e}")
            raise ModelError(f"模型解释失败: {e}")
    
    def create_ensemble(self, base_models: List[Any], method: str = 'voting') -> Any:
        """创建集成模型"""
        try:
            if method == 'voting':
                from sklearn.ensemble import VotingRegressor
                ensemble = VotingRegressor([(f'model_{i}', model) for i, model in enumerate(base_models)])
            elif method == 'stacking':
                from sklearn.ensemble import StackingRegressor
                ensemble = StackingRegressor(
                    estimators=[(f'model_{i}', model) for i, model in enumerate(base_models)],
                    final_estimator=LinearRegression()
                )
            else:
                raise ValidationError(f"不支持的集成方法: {method}")
            
            logger.info(f"集成模型创建完成: {method}")
            return ensemble
            
        except Exception as e:
            logger.error(f"集成模型创建失败: {e}")
            raise ModelError(f"集成模型创建失败: {e}")
    
    def monitor_model_performance(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """监控模型性能"""
        try:
            # 预测
            y_pred = model.predict(X)
            
            # 计算性能指标
            metrics = self._calculate_metrics(y, y_pred)
            
            # 计算数据漂移
            data_drift = self._calculate_data_drift(X)
            
            # 计算模型漂移
            model_drift = self._calculate_model_drift(y, y_pred)
            
            result = {
                'performance_metrics': metrics,
                'data_drift': data_drift,
                'model_drift': model_drift,
                'monitoring_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"模型性能监控完成")
            return result
            
        except Exception as e:
            logger.error(f"模型性能监控失败: {e}")
            raise ModelError(f"模型性能监控失败: {e}")
    
    def _calculate_data_drift(self, X: pd.DataFrame) -> Dict[str, float]:
        """计算数据漂移"""
        try:
            drift_scores = {}
            for column in X.columns:
                if X[column].dtype in ['int64', 'float64']:
                    # 计算统计特征
                    mean_val = X[column].mean()
                    std_val = X[column].std()
                    
                    # 简单的漂移检测（基于统计特征变化）
                    drift_scores[column] = abs(mean_val) + abs(std_val)
            
            return drift_scores
            
        except Exception as e:
            logger.error(f"数据漂移计算失败: {e}")
            return {}
    
    def _calculate_model_drift(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """计算模型漂移"""
        try:
            # 计算预测误差的分布
            errors = y_true - y_pred
            error_mean = errors.mean()
            error_std = errors.std()
            
            return {
                'error_mean': error_mean,
                'error_std': error_std,
                'drift_score': abs(error_mean) + abs(error_std)
            }
            
        except Exception as e:
            logger.error(f"模型漂移计算失败: {e}")
            return {}
    
    def retrain_model(self, model: Any, X: pd.DataFrame, y: pd.Series) -> Any:
        """重训练模型"""
        try:
            # 创建新模型实例
            new_model = model.__class__(**model.get_params())
            new_model.fit(X, y)
            
            logger.info(f"模型重训练完成: {model.__class__.__name__}")
            return new_model
            
        except Exception as e:
            logger.error(f"模型重训练失败: {e}")
            raise ModelError(f"模型重训练失败: {e}")
    
    def create_model_version(self, model: Any, version: str, description: str) -> Dict[str, Any]:
        """创建模型版本"""
        try:
            version_info = {
                'version': version,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'model_type': model.__class__.__name__,
                'model_params': model.get_params() if hasattr(model, 'get_params') else {}
            }
            
            self.model_versions[version] = version_info
            
            logger.info(f"模型版本创建完成: {version}")
            return version_info
            
        except Exception as e:
            logger.error(f"模型版本创建失败: {e}")
            raise ModelError(f"模型版本创建失败: {e}")


