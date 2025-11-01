"""
线性模型算法
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any, List, Optional
import logging
from ..logging_config import get_logger

logger = get_logger("linear_models")

class LinearRegressionModel:
    """线性回归模型"""
    
    def __init__(self, **kwargs):
        self.model = LinearRegression(**kwargs)
        self.is_fitted = False
        self.feature_names = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("线性回归模型训练完成")
        except Exception as e:
            logger.error(f"线性回归模型训练失败: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"线性回归模型预测失败: {e}")
            raise
    
    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"线性回归模型评分失败: {e}")
            raise
    
    def get_coefficients(self) -> Dict[str, float]:
        """获取系数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return dict(zip(self.feature_names, self.model.coef_))
        except Exception as e:
            logger.error(f"获取系数失败: {e}")
            raise
    
    def get_intercept(self) -> float:
        """获取截距"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        return self.model.intercept_
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            y_pred = self.predict(X)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise

class RidgeModel:
    """岭回归模型"""
    
    def __init__(self, alpha: float = 1.0, **kwargs):
        self.model = Ridge(alpha=alpha, **kwargs)
        self.is_fitted = False
        self.feature_names = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("岭回归模型训练完成")
        except Exception as e:
            logger.error(f"岭回归模型训练失败: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"岭回归模型预测失败: {e}")
            raise
    
    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"岭回归模型评分失败: {e}")
            raise
    
    def get_coefficients(self) -> Dict[str, float]:
        """获取系数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return dict(zip(self.feature_names, self.model.coef_))
        except Exception as e:
            logger.error(f"获取系数失败: {e}")
            raise
    
    def get_intercept(self) -> float:
        """获取截距"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        return self.model.intercept_
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            y_pred = self.predict(X)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise

class LassoModel:
    """Lasso回归模型"""
    
    def __init__(self, alpha: float = 1.0, **kwargs):
        self.model = Lasso(alpha=alpha, **kwargs)
        self.is_fitted = False
        self.feature_names = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("Lasso回归模型训练完成")
        except Exception as e:
            logger.error(f"Lasso回归模型训练失败: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"Lasso回归模型预测失败: {e}")
            raise
    
    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"Lasso回归模型评分失败: {e}")
            raise
    
    def get_coefficients(self) -> Dict[str, float]:
        """获取系数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return dict(zip(self.feature_names, self.model.coef_))
        except Exception as e:
            logger.error(f"获取系数失败: {e}")
            raise
    
    def get_intercept(self) -> float:
        """获取截距"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        return self.model.intercept_
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            y_pred = self.predict(X)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise

class ElasticNetModel:
    """弹性网络回归模型"""
    
    def __init__(self, alpha: float = 1.0, l1_ratio: float = 0.5, **kwargs):
        self.model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, **kwargs)
        self.is_fitted = False
        self.feature_names = None
    
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("弹性网络回归模型训练完成")
        except Exception as e:
            logger.error(f"弹性网络回归模型训练失败: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"弹性网络回归模型预测失败: {e}")
            raise
    
    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"弹性网络回归模型评分失败: {e}")
            raise
    
    def get_coefficients(self) -> Dict[str, float]:
        """获取系数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return dict(zip(self.feature_names, self.model.coef_))
        except Exception as e:
            logger.error(f"获取系数失败: {e}")
            raise
    
    def get_intercept(self) -> float:
        """获取截距"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        return self.model.intercept_
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            y_pred = self.predict(X)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise




