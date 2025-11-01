"""
时间序列模型算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
from ..logging_config import get_logger

logger = get_logger("time_series")

class ARIMAModel:
    """ARIMA时间序列模型"""
    
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1), **kwargs):
        self.order = order
        self.model = None
        self.is_fitted = False
        self.fitted_model = None
    
    def fit(self, data: pd.Series):
        """训练模型"""
        try:
            # 检查数据平稳性
            if not self._is_stationary(data):
                logger.warning("数据非平稳，建议进行差分处理")
            
            # 训练ARIMA模型
            self.model = ARIMA(data, order=self.order)
            self.fitted_model = self.model.fit()
            self.is_fitted = True
            
            logger.info(f"ARIMA模型训练完成: {self.order}")
        except Exception as e:
            logger.error(f"ARIMA模型训练失败: {e}")
            raise
    
    def predict(self, steps: int = 1) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            forecast = self.fitted_model.forecast(steps=steps)
            return forecast
        except Exception as e:
            logger.error(f"ARIMA模型预测失败: {e}")
            raise
    
    def predict_interval(self, steps: int = 1, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """预测区间"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            forecast = self.fitted_model.get_forecast(steps=steps)
            forecast_ci = forecast.conf_int(alpha=alpha)
            
            mean_forecast = forecast.predicted_mean
            lower_bound = forecast_ci.iloc[:, 0]
            upper_bound = forecast_ci.iloc[:, 1]
            
            return mean_forecast, lower_bound, upper_bound
        except Exception as e:
            logger.error(f"ARIMA模型预测区间失败: {e}")
            raise
    
    def evaluate(self, test_data: pd.Series) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            predictions = self.predict(len(test_data))
            mse = mean_squared_error(test_data, predictions)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test_data, predictions)
            r2 = r2_score(test_data, predictions)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"ARIMA模型评估失败: {e}")
            raise
    
    def _is_stationary(self, data: pd.Series) -> bool:
        """检查数据平稳性"""
        try:
            result = adfuller(data.dropna())
            return result[1] < 0.05  # p-value < 0.05 表示平稳
        except Exception as e:
            logger.error(f"平稳性检验失败: {e}")
            return False
    
    def get_model_summary(self) -> str:
        """获取模型摘要"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return str(self.fitted_model.summary())
        except Exception as e:
            logger.error(f"获取模型摘要失败: {e}")
            raise
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取模型参数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return {
                'order': self.order,
                'aic': self.fitted_model.aic,
                'bic': self.fitted_model.bic,
                'params': self.fitted_model.params.to_dict()
            }
        except Exception as e:
            logger.error(f"获取模型参数失败: {e}")
            raise

class VARModel:
    """向量自回归模型"""
    
    def __init__(self, maxlags: int = 15, **kwargs):
        self.maxlags = maxlags
        self.model = None
        self.is_fitted = False
        self.fitted_model = None
    
    def fit(self, data: pd.DataFrame):
        """训练模型"""
        try:
            # 检查数据平稳性
            for column in data.columns:
                if not self._is_stationary(data[column]):
                    logger.warning(f"列 {column} 非平稳，建议进行差分处理")
            
            # 训练VAR模型
            self.model = VAR(data)
            self.fitted_model = self.model.fit(maxlags=self.maxlags)
            self.is_fitted = True
            
            logger.info(f"VAR模型训练完成: {self.maxlags} 阶")
        except Exception as e:
            logger.error(f"VAR模型训练失败: {e}")
            raise
    
    def predict(self, steps: int = 1) -> pd.DataFrame:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            forecast = self.fitted_model.forecast(steps=steps)
            return pd.DataFrame(forecast, columns=self.model.endog_names)
        except Exception as e:
            logger.error(f"VAR模型预测失败: {e}")
            raise
    
    def predict_interval(self, steps: int = 1, alpha: float = 0.05) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """预测区间"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            forecast = self.fitted_model.forecast_interval(steps=steps, alpha=alpha)
            
            mean_forecast = pd.DataFrame(forecast[0], columns=self.model.endog_names)
            lower_bound = pd.DataFrame(forecast[1], columns=self.model.endog_names)
            upper_bound = pd.DataFrame(forecast[2], columns=self.model.endog_names)
            
            return mean_forecast, lower_bound, upper_bound
        except Exception as e:
            logger.error(f"VAR模型预测区间失败: {e}")
            raise
    
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """评估模型"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            predictions = self.predict(len(test_data))
            
            # 计算整体评估指标
            mse = mean_squared_error(test_data.values.flatten(), predictions.values.flatten())
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test_data.values.flatten(), predictions.values.flatten())
            r2 = r2_score(test_data.values.flatten(), predictions.values.flatten())
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
        except Exception as e:
            logger.error(f"VAR模型评估失败: {e}")
            raise
    
    def _is_stationary(self, data: pd.Series) -> bool:
        """检查数据平稳性"""
        try:
            result = adfuller(data.dropna())
            return result[1] < 0.05
        except Exception as e:
            logger.error(f"平稳性检验失败: {e}")
            return False
    
    def get_model_summary(self) -> str:
        """获取模型摘要"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return str(self.fitted_model.summary())
        except Exception as e:
            logger.error(f"获取模型摘要失败: {e}")
            raise
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取模型参数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            return {
                'maxlags': self.maxlags,
                'aic': self.fitted_model.aic,
                'bic': self.fitted_model.bic,
                'params': self.fitted_model.params.to_dict()
            }
        except Exception as e:
            logger.error(f"获取模型参数失败: {e}")
            raise
    
    def get_granger_causality(self) -> Dict[str, Any]:
        """获取格兰杰因果性检验"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        
        try:
            # 这里需要实现格兰杰因果性检验
            # 由于statsmodels的VAR模型没有直接的格兰杰因果性检验方法
            # 这里返回一个占位符
            return {
                'causality_tests': {},
                'note': '格兰杰因果性检验需要额外实现'
            }
        except Exception as e:
            logger.error(f"格兰杰因果性检验失败: {e}")
            raise




