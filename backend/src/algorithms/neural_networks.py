"""
神经网络模型算法
"""

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any, List, Optional, Tuple
import logging
from ..logging_config import get_logger

logger = get_logger("neural_networks")


class MLPModel:
    """多层感知机模型"""

    def __init__(
        self,
        hidden_layer_sizes: Tuple = (100,),
        max_iter: int = 1000,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
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
            logger.info("MLP模型训练完成")
        except Exception as e:
            logger.error(f"MLP模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"MLP模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"MLP模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性（MLP没有直接的特征重要性）"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            # 使用权重矩阵计算特征重要性
            weights = self.model.coefs_[0]  # 第一层权重
            importance = np.abs(weights).mean(axis=1)  # 计算平均重要性

            return dict(zip(self.feature_names, importance))
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

    def get_training_loss(self) -> List[float]:
        """获取训练损失"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.loss_curve_.tolist()
        except Exception as e:
            logger.error(f"获取训练损失失败: {e}")
            raise

    def get_network_structure(self) -> Dict[str, Any]:
        """获取网络结构"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return {
                "hidden_layer_sizes": self.model.hidden_layer_sizes,
                "n_layers": len(self.model.coefs_),
                "n_features": self.model.n_features_in_,
                "n_outputs": self.model.n_outputs_,
            }
        except Exception as e:
            logger.error(f"获取网络结构失败: {e}")
            raise


class DeepMLPModel:
    """深度多层感知机模型"""

    def __init__(
        self,
        hidden_layer_sizes: Tuple = (200, 100, 50),
        max_iter: int = 2000,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
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
            logger.info("深度MLP模型训练完成")
        except Exception as e:
            logger.error(f"深度MLP模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"深度MLP模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"深度MLP模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            # 使用第一层权重计算特征重要性
            weights = self.model.coefs_[0]
            importance = np.abs(weights).mean(axis=1)

            return dict(zip(self.feature_names, importance))
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

    def get_training_loss(self) -> List[float]:
        """获取训练损失"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.loss_curve_.tolist()
        except Exception as e:
            logger.error(f"获取训练损失失败: {e}")
            raise

    def get_network_structure(self) -> Dict[str, Any]:
        """获取网络结构"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return {
                "hidden_layer_sizes": self.model.hidden_layer_sizes,
                "n_layers": len(self.model.coefs_),
                "n_features": self.model.n_features_in_,
                "n_outputs": self.model.n_outputs_,
            }
        except Exception as e:
            logger.error(f"获取网络结构失败: {e}")
            raise


class WideMLPModel:
    """宽多层感知机模型"""

    def __init__(
        self,
        hidden_layer_sizes: Tuple = (500, 200),
        max_iter: int = 1500,
        random_state: int = 42,
        **kwargs,
    ):
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
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
            logger.info("宽MLP模型训练完成")
        except Exception as e:
            logger.error(f"宽MLP模型训练失败: {e}")
            raise

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"宽MLP模型预测失败: {e}")
            raise

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """计算R²分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.score(X, y)
        except Exception as e:
            logger.error(f"宽MLP模型评分失败: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            weights = self.model.coefs_[0]
            importance = np.abs(weights).mean(axis=1)

            return dict(zip(self.feature_names, importance))
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

    def get_training_loss(self) -> List[float]:
        """获取训练损失"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return self.model.loss_curve_.tolist()
        except Exception as e:
            logger.error(f"获取训练损失失败: {e}")
            raise

    def get_network_structure(self) -> Dict[str, Any]:
        """获取网络结构"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        try:
            return {
                "hidden_layer_sizes": self.model.hidden_layer_sizes,
                "n_layers": len(self.model.coefs_),
                "n_features": self.model.n_features_in_,
                "n_outputs": self.model.n_outputs_,
            }
        except Exception as e:
            logger.error(f"获取网络结构失败: {e}")
            raise
