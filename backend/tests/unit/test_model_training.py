"""
模型训练单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch
from src.services.model_training import ModelTrainingService
from src.algorithms.linear_models import LinearRegressionModel
from src.algorithms.ensemble_models import RandomForestModel, XGBoostModel
from src.algorithms.neural_networks import MLPModel

class TestModelTrainingService:
    """测试模型训练服务"""
    
    def setup_method(self):
        """测试前设置"""
        self.service = ModelTrainingService()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self):
        """创建样本数据"""
        np.random.seed(42)
        n_samples = 1000
        
        # 创建特征数据
        X = np.random.randn(n_samples, 10)
        
        # 创建目标变量（线性关系 + 噪声）
        y = 2 * X[:, 0] + 3 * X[:, 1] - 1.5 * X[:, 2] + np.random.normal(0, 0.1, n_samples)
        
        # 创建DataFrame
        feature_names = [f'feature_{i}' for i in range(10)]
        data = pd.DataFrame(X, columns=feature_names)
        data['target'] = y
        
        return data
    
    def test_linear_regression_training(self):
        """测试线性回归模型训练"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 测试预测
        predictions = model.predict(X[:10])
        assert len(predictions) == 10
        assert all(isinstance(p, (int, float)) for p in predictions)
        
        # 测试模型评估
        score = model.score(X, y)
        assert 0 <= score <= 1
    
    def test_random_forest_training(self):
        """测试随机森林模型训练"""
        model = RandomForestModel(n_estimators=100, random_state=42)
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 测试预测
        predictions = model.predict(X[:10])
        assert len(predictions) == 10
        
        # 测试特征重要性
        feature_importance = model.get_feature_importance()
        assert len(feature_importance) == len(X.columns)
        assert all(0 <= imp <= 1 for imp in feature_importance.values())
    
    def test_xgboost_training(self):
        """测试XGBoost模型训练"""
        model = XGBoostModel(n_estimators=100, random_state=42)
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 测试预测
        predictions = model.predict(X[:10])
        assert len(predictions) == 10
        
        # 测试特征重要性
        feature_importance = model.get_feature_importance()
        assert len(feature_importance) == len(X.columns)
    
    def test_mlp_training(self):
        """测试多层感知机模型训练"""
        model = MLPModel(hidden_layer_sizes=(50, 25), random_state=42)
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 测试预测
        predictions = model.predict(X[:10])
        assert len(predictions) == 10
    
    def test_model_evaluation_metrics(self):
        """测试模型评估指标"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 分割数据
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 训练模型
        model.fit(X_train, y_train)
        
        # 评估模型
        metrics = model.evaluate(X_test, y_test)
        
        assert 'mse' in metrics
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics
        
        assert metrics['mse'] >= 0
        assert metrics['rmse'] >= 0
        assert metrics['mae'] >= 0
        assert 0 <= metrics['r2'] <= 1
    
    def test_cross_validation(self):
        """测试交叉验证"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 执行交叉验证
        cv_scores = self.service.cross_validate(model, X, y, cv=5)
        
        assert len(cv_scores) == 5
        assert all(0 <= score <= 1 for score in cv_scores)
    
    def test_hyperparameter_tuning(self):
        """测试超参数调优"""
        model = RandomForestModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 定义参数网格
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [5, 10]
        }
        
        # 执行网格搜索
        best_params, best_score = self.service.tune_hyperparameters(
            model, X, y, param_grid, cv=3
        )
        
        assert best_params is not None
        assert best_score >= 0
        assert 'n_estimators' in best_params
        assert 'max_depth' in best_params
    
    def test_model_persistence(self):
        """测试模型持久化"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 保存模型
        model_path = "test_model.pkl"
        self.service.save_model(model, model_path)
        
        # 加载模型
        loaded_model = self.service.load_model(model_path)
        
        # 测试加载的模型
        predictions_original = model.predict(X[:5])
        predictions_loaded = loaded_model.predict(X[:5])
        
        assert np.allclose(predictions_original, predictions_loaded)
    
    def test_model_comparison(self):
        """测试模型比较"""
        models = [
            LinearRegressionModel(),
            RandomForestModel(n_estimators=50),
            XGBoostModel(n_estimators=50)
        ]
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 比较模型性能
        comparison_results = self.service.compare_models(models, X, y, cv=3)
        
        assert len(comparison_results) == len(models)
        assert all('model_name' in result for result in comparison_results)
        assert all('cv_scores' in result for result in comparison_results)
        assert all('mean_score' in result for result in comparison_results)
    
    def test_feature_selection(self):
        """测试特征选择"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 执行特征选择
        selected_features = self.service.select_features(model, X, y, k=5)
        
        assert len(selected_features) == 5
        assert all(feature in X.columns for feature in selected_features)
    
    def test_model_validation(self):
        """测试模型验证"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 分割数据
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 训练模型
        model.fit(X_train, y_train)
        
        # 验证模型
        validation_result = self.service.validate_model(model, X_test, y_test)
        
        assert 'predictions' in validation_result
        assert 'metrics' in validation_result
        assert 'residuals' in validation_result
        
        assert len(validation_result['predictions']) == len(y_test)
        assert len(validation_result['residuals']) == len(y_test)
    
    def test_model_interpretation(self):
        """测试模型解释"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 获取模型解释
        interpretation = self.service.interpret_model(model, X.columns)
        
        assert 'feature_importance' in interpretation
        assert 'coefficients' in interpretation
        assert len(interpretation['feature_importance']) == len(X.columns)
    
    def test_model_ensemble(self):
        """测试模型集成"""
        base_models = [
            LinearRegressionModel(),
            RandomForestModel(n_estimators=50),
            XGBoostModel(n_estimators=50)
        ]
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 创建集成模型
        ensemble_model = self.service.create_ensemble(base_models)
        
        # 训练集成模型
        ensemble_model.fit(X, y)
        
        # 测试预测
        predictions = ensemble_model.predict(X[:10])
        assert len(predictions) == 10
    
    def test_model_monitoring(self):
        """测试模型监控"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 监控模型性能
        monitoring_result = self.service.monitor_model_performance(model, X, y)
        
        assert 'performance_metrics' in monitoring_result
        assert 'data_drift' in monitoring_result
        assert 'model_drift' in monitoring_result
    
    def test_model_retraining(self):
        """测试模型重训练"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 初始训练
        model.fit(X, y)
        initial_score = model.score(X, y)
        
        # 模拟新数据
        new_X = X + np.random.normal(0, 0.1, X.shape)
        new_y = y + np.random.normal(0, 0.1, y.shape)
        
        # 重训练模型
        retrained_model = self.service.retrain_model(model, new_X, new_y)
        
        # 测试重训练后的模型
        new_score = retrained_model.score(new_X, new_y)
        assert new_score >= 0
    
    def test_model_versioning(self):
        """测试模型版本管理"""
        model = LinearRegressionModel()
        
        X = self.sample_data.drop('target', axis=1)
        y = self.sample_data['target']
        
        # 训练模型
        model.fit(X, y)
        
        # 创建模型版本
        version_info = self.service.create_model_version(model, "v1.0", "Initial model")
        
        assert 'version' in version_info
        assert 'created_at' in version_info
        assert 'description' in version_info
        assert version_info['version'] == "v1.0"


