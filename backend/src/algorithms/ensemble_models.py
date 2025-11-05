"""
集成模型算法
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any, List, Optional
import xgboost as xgb
import lightgbm as lgb
import logging
from ..logging_config import get_logger

logger = get_logger("ensemble_models")


class RandomForestModel:
    """随机森林模型"""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            **kwargs,
        )
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("随机森林模型训练完成")
        except Exception as e:
            logger.error(f"随机森林模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"随机森林模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"随机森林模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return dict(zip(self.feature_names, self.model.feature_importances_))
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            raise

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

            return {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise


class XGBoostModel:
    """XGBoost模型"""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            **kwargs,
        )
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("XGBoost模型训练完成")
        except Exception as e:
            logger.error(f"XGBoost模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"XGBoost模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"XGBoost模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return dict(zip(self.feature_names, self.model.feature_importances_))
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            raise

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

            return {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise


class LightGBMModel:
    """LightGBM模型"""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = lgb.LGBMRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            verbose=-1,
            **kwargs,
        )
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("LightGBM模型训练完成")
        except Exception as e:
            logger.error(f"LightGBM模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"LightGBM模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"LightGBM模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return dict(zip(self.feature_names, self.model.feature_importances_))
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            raise

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

            return {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise


class GradientBoostingModel:
    """梯度提升模型"""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 3,
        learning_rate: float = 0.1,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            **kwargs,
        )
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            self.feature_names = X.columns.tolist()
            self.model.fit(X, y)
            self.is_fitted = True
            logger.info("梯度提升模型训练完成")
        except Exception as e:
            logger.error(f"梯度提升模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"梯度提升模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"梯度提升模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return dict(zip(self.feature_names, self.model.feature_importances_))
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            raise

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

            return {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise
