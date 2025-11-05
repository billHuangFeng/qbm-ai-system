"""
算法集成测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from backend.src.services.algorithm_service import AlgorithmService


class TestAlgorithmIntegration:
    """算法集成测试类"""

    def setup_method(self):
        """测试前准备"""
        self.algorithm_service = AlgorithmService()

        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, n_samples),
                "feature2": np.random.normal(0, 1, n_samples),
                "feature3": np.random.normal(0, 1, n_samples),
            }
        )

        # 创建有明确关系的目标变量
        self.y = pd.Series(
            self.X["feature1"] * 2
            + self.X["feature2"] * 1.5
            + self.X["feature3"] * 0.5
            + np.random.normal(0, 0.1, n_samples)
        )

    def test_analyze_data_relationships(self):
        """测试数据关系分析集成"""
        result = self.algorithm_service.analyze_data_relationships(
            self.X, self.y, ["synergy", "threshold", "lag", "advanced"]
        )

        assert isinstance(result, dict)
        assert "synergy" in result
        assert "threshold" in result
        assert "lag" in result
        assert "advanced" in result
        assert "enhanced_features" in result
        assert "overall_score" in result

        # 检查增强特征
        enhanced_features = result["enhanced_features"]
        assert isinstance(enhanced_features, pd.DataFrame)
        assert len(enhanced_features.columns) >= len(self.X.columns)

    def test_optimize_weights(self):
        """测试权重优化集成"""
        result = self.algorithm_service.optimize_weights(
            self.X, self.y, "comprehensive", ["cross_validation", "bootstrap"]
        )

        assert isinstance(result, dict)
        assert "dynamic_weights" in result
        assert "optimized_weights" in result
        assert "validation" in result
        assert "monitoring" in result
        assert "overall_score" in result

        # 检查动态权重
        dynamic_weights = result["dynamic_weights"]
        assert isinstance(dynamic_weights, dict)
        assert "normalized" in dynamic_weights

        # 检查优化权重
        optimized_weights = result["optimized_weights"]
        assert isinstance(optimized_weights, dict)
        assert "best_result" in optimized_weights

        # 检查验证结果
        validation = result["validation"]
        assert isinstance(validation, dict)
        assert "overall_score" in validation

        # 检查监控结果
        monitoring = result["monitoring"]
        assert isinstance(monitoring, dict)
        assert "overall_score" in monitoring

    def test_predict_with_optimized_weights(self):
        """测试使用优化权重进行预测"""
        # 先优化权重
        optimization_result = self.algorithm_service.optimize_weights(self.X, self.y)

        # 获取优化后的权重
        if "final" in optimization_result["dynamic_weights"].get("normalized", {}):
            weights = optimization_result["dynamic_weights"]["normalized"]["final"]
        else:
            weights = optimization_result["optimized_weights"]["best_result"]["weights"]

        # 创建测试数据
        X_test = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, 20),
                "feature2": np.random.normal(0, 1, 20),
                "feature3": np.random.normal(0, 1, 20),
            }
        )

        # 执行预测
        result = self.algorithm_service.predict_with_optimized_weights(
            self.X, self.y, X_test, weights
        )

        assert isinstance(result, dict)
        assert "predictions" in result
        assert "model_performance" in result
        assert "weights_used" in result
        assert "feature_importance" in result

        # 检查预测结果
        predictions = result["predictions"]
        assert "linear_regression" in predictions
        assert "random_forest" in predictions
        assert "ensemble" in predictions

        # 检查预测长度
        for model_name, pred in predictions.items():
            assert isinstance(pred, list)
            assert len(pred) == len(X_test)

    def test_get_algorithm_insights(self):
        """测试算法洞察获取"""
        # 先执行一些分析
        self.algorithm_service.analyze_data_relationships(self.X, self.y)
        self.algorithm_service.optimize_weights(self.X, self.y)

        # 获取洞察
        insights = self.algorithm_service.get_algorithm_insights()

        assert isinstance(insights, dict)
        assert "analysis_results" in insights
        assert "optimization_history" in insights
        assert "monitoring_data" in insights
        assert "recommendations" in insights

        # 检查建议
        recommendations = insights["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_create_enhanced_features(self):
        """测试增强特征创建"""
        # 模拟分析结果
        analysis_results = {
            "synergy_features": pd.DataFrame(
                {"feature1_x_feature2": np.random.normal(0, 1, len(self.X))}
            ),
            "threshold_features": pd.DataFrame(
                {"feature1_above_0.5": np.random.normal(0, 1, len(self.X))}
            ),
            "lag_features": pd.DataFrame(
                {"feature1_lag_1": np.random.normal(0, 1, len(self.X))}
            ),
        }

        enhanced_features = self.algorithm_service._create_enhanced_features(
            self.X, analysis_results
        )

        assert isinstance(enhanced_features, pd.DataFrame)
        assert len(enhanced_features.columns) > len(self.X.columns)
        assert all(col in enhanced_features.columns for col in self.X.columns)

    def test_apply_weights(self):
        """测试权重应用"""
        weights = {"feature1": 0.5, "feature2": 0.3, "feature3": 0.2}

        X_weighted = self.algorithm_service._apply_weights(self.X, weights)

        assert isinstance(X_weighted, pd.DataFrame)
        assert X_weighted.shape == self.X.shape

        # 检查权重应用
        for feature, weight in weights.items():
            assert np.allclose(X_weighted[feature], self.X[feature] * weight)

    def test_calculate_analysis_score(self):
        """测试分析评分计算"""
        analysis_results = {
            "synergy": {"overall_score": 0.8},
            "threshold": {"overall_score": 0.7},
            "lag": {"overall_score": 0.6},
            "advanced": {"overall_score": 0.9},
        }

        score = self.algorithm_service._calculate_analysis_score(analysis_results)

        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0.7  # 应该是一个较高的分数

    def test_calculate_optimization_score(self):
        """测试优化评分计算"""
        optimization_results = {
            "dynamic_weights": {"overall_score": 0.8},
            "optimized_weights": {"best_result": {"r2_score": 0.85}},
            "validation": {"overall_score": 0.9},
            "monitoring": {"overall_score": 0.75},
        }

        score = self.algorithm_service._calculate_optimization_score(
            optimization_results
        )

        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0.8  # 应该是一个较高的分数

    def test_calculate_feature_importance(self):
        """测试特征重要性计算"""
        weights = {"feature1": 0.5, "feature2": 0.3, "feature3": 0.2}

        importance = self.algorithm_service._calculate_feature_importance(weights)

        assert isinstance(importance, dict)
        assert "weights" in importance
        assert "max_weight" in importance
        assert "min_weight" in importance
        assert "mean_weight" in importance
        assert "std_weight" in importance
        assert "weight_range" in importance

        # 检查权重归一化
        normalized_weights = importance["weights"]
        assert abs(sum(normalized_weights.values()) - 1.0) < 1e-6

    def test_generate_algorithm_recommendations(self):
        """测试算法建议生成"""
        # 设置一些分析结果
        self.algorithm_service.analysis_results = {"overall_score": 0.8}
        self.algorithm_service.optimization_history = {"method1": {}}

        recommendations = self.algorithm_service._generate_algorithm_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0

    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)

        # 测试分析
        result = self.algorithm_service.analyze_data_relationships(empty_X, empty_y)
        assert isinstance(result, dict)

        # 测试优化
        result = self.algorithm_service.optimize_weights(empty_X, empty_y)
        assert isinstance(result, dict)

    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({"feature1": [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])

        # 测试分析
        result = self.algorithm_service.analyze_data_relationships(single_X, single_y)
        assert isinstance(result, dict)

        # 测试优化
        result = self.algorithm_service.optimize_weights(single_X, single_y)
        assert isinstance(result, dict)

    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame(
            {f"feature_{i}": np.random.normal(0, 1, 500) for i in range(10)}
        )
        large_y = pd.Series(np.random.normal(0, 1, 500))

        # 测试分析
        result = self.algorithm_service.analyze_data_relationships(large_X, large_y)
        assert isinstance(result, dict)

        # 测试优化
        result = self.algorithm_service.optimize_weights(large_X, large_y)
        assert isinstance(result, dict)

    def test_high_correlation_data(self):
        """测试高相关性数据处理"""
        # 创建高相关性的数据
        high_corr_X = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, 100),
                "feature2": np.random.normal(0, 1, 100),
            }
        )
        high_corr_y = pd.Series(
            high_corr_X["feature1"] * 2 + high_corr_X["feature2"] * 1.5
        )

        # 测试分析
        result = self.algorithm_service.analyze_data_relationships(
            high_corr_X, high_corr_y
        )
        assert isinstance(result, dict)
        assert result["overall_score"] > 0

        # 测试优化
        result = self.algorithm_service.optimize_weights(high_corr_X, high_corr_y)
        assert isinstance(result, dict)
        assert result["overall_score"] > 0

    def test_different_analysis_types(self):
        """测试不同分析类型"""
        analysis_types_list = [
            ["synergy"],
            ["threshold"],
            ["lag"],
            ["advanced"],
            ["synergy", "threshold"],
            ["synergy", "lag", "advanced"],
        ]

        for analysis_types in analysis_types_list:
            result = self.algorithm_service.analyze_data_relationships(
                self.X, self.y, analysis_types
            )
            assert isinstance(result, dict)
            assert "overall_score" in result

    def test_different_optimization_methods(self):
        """测试不同优化方法"""
        optimization_methods = [
            "gradient_descent",
            "genetic_algorithm",
            "simulated_annealing",
            "particle_swarm",
            "bayesian",
            "comprehensive",
        ]

        for method in optimization_methods:
            result = self.algorithm_service.optimize_weights(self.X, self.y, method)
            assert isinstance(result, dict)
            assert "overall_score" in result

    def test_different_validation_methods(self):
        """测试不同验证方法"""
        validation_methods_list = [
            ["cross_validation"],
            ["bootstrap"],
            ["time_series"],
            ["stability"],
            ["cross_validation", "bootstrap"],
            ["cross_validation", "bootstrap", "stability"],
        ]

        for validation_methods in validation_methods_list:
            result = self.algorithm_service.optimize_weights(
                self.X, self.y, validation_methods=validation_methods
            )
            assert isinstance(result, dict)
            assert "validation" in result

    def test_integration_workflow(self):
        """测试完整集成工作流"""
        # 1. 数据关系分析
        analysis_result = self.algorithm_service.analyze_data_relationships(
            self.X, self.y, ["synergy", "threshold", "lag", "advanced"]
        )
        assert analysis_result["overall_score"] > 0

        # 2. 权重优化
        optimization_result = self.algorithm_service.optimize_weights(
            self.X, self.y, "comprehensive", ["cross_validation", "bootstrap"]
        )
        assert optimization_result["overall_score"] > 0

        # 3. 获取优化后的权重
        if "final" in optimization_result["dynamic_weights"].get("normalized", {}):
            weights = optimization_result["dynamic_weights"]["normalized"]["final"]
        else:
            weights = optimization_result["optimized_weights"]["best_result"]["weights"]

        # 4. 使用权重进行预测
        X_test = pd.DataFrame(
            {
                "feature1": np.random.normal(0, 1, 20),
                "feature2": np.random.normal(0, 1, 20),
                "feature3": np.random.normal(0, 1, 20),
            }
        )

        prediction_result = self.algorithm_service.predict_with_optimized_weights(
            self.X, self.y, X_test, weights
        )
        assert "predictions" in prediction_result

        # 5. 获取算法洞察
        insights = self.algorithm_service.get_algorithm_insights()
        assert "recommendations" in insights

        # 验证整个工作流的完整性
        assert analysis_result is not None
        assert optimization_result is not None
        assert prediction_result is not None
        assert insights is not None
