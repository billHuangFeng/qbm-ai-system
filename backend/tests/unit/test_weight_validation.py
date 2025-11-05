"""
权重验证机制测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from backend.src.algorithms.weight_validation import WeightValidator


class TestWeightValidator:
    """权重验证器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.weight_validator = WeightValidator()

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

        # 创建有明确权重关系的目标变量
        self.y = pd.Series(
            self.X["feature1"] * 2
            + self.X["feature2"] * 1.5
            + self.X["feature3"] * 0.5
            + np.random.normal(0, 0.1, n_samples)
        )

        # 创建测试权重
        self.weights = {"feature1": 0.5, "feature2": 0.3, "feature3": 0.2}

    def test_validate_weights(self):
        """测试权重验证"""
        result = self.weight_validator.validate_weights(self.X, self.y, self.weights)

        assert isinstance(result, dict)
        assert "cross_validation" in result
        assert "bootstrap" in result
        assert "time_series" in result
        assert "stability" in result
        assert "sensitivity" in result
        assert "robustness" in result
        assert "significance" in result
        assert "overall_score" in result

        # 检查整体评分
        assert 0 <= result["overall_score"] <= 1

    def test_validate_weights_custom_methods(self):
        """测试自定义验证方法"""
        result = self.weight_validator.validate_weights(
            self.X,
            self.y,
            self.weights,
            validation_methods=["cross_validation", "bootstrap"],
        )

        assert isinstance(result, dict)
        assert "cross_validation" in result
        assert "bootstrap" in result
        assert "overall_score" in result

    def test_cross_validation_test(self):
        """测试交叉验证"""
        result = self.weight_validator._cross_validation_test(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "original_scores" in result
        assert "weighted_scores" in result
        assert "original_mean" in result
        assert "weighted_mean" in result
        assert "improvement" in result
        assert "t_statistic" in result
        assert "p_value" in result
        assert "significant" in result

        # 检查分数列表
        assert len(result["original_scores"]) == 5  # 5折交叉验证
        assert len(result["weighted_scores"]) == 5

    def test_bootstrap_validation(self):
        """测试自助法验证"""
        result = self.weight_validator._bootstrap_validation(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "bootstrap_scores" in result
        assert "bootstrap_improvements" in result
        assert "mean_improvement" in result
        assert "std_improvement" in result
        assert "confidence_interval" in result
        assert "positive_improvement_rate" in result

        # 检查自助法结果
        assert len(result["bootstrap_scores"]) == 100  # 默认100次自助法
        assert len(result["bootstrap_improvements"]) == 100
        assert 0 <= result["positive_improvement_rate"] <= 1

    def test_time_series_validation(self):
        """测试时间序列验证"""
        result = self.weight_validator._time_series_validation(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "original_scores" in result
        assert "weighted_scores" in result
        assert "original_mean" in result
        assert "weighted_mean" in result
        assert "improvement" in result
        assert "time_series_consistency" in result

        # 检查时间序列结果
        assert len(result["original_scores"]) == 5  # 5折时间序列交叉验证
        assert len(result["weighted_scores"]) == 5

    def test_stability_validation(self):
        """测试稳定性验证"""
        result = self.weight_validator._stability_validation(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "stability_results" in result
        assert "stability_score" in result
        assert "improvement_consistency" in result
        assert "mean_improvement" in result

        # 检查稳定性结果
        stability_results = result["stability_results"]
        assert "noise_0.01" in stability_results
        assert "noise_0.05" in stability_results
        assert "noise_0.1" in stability_results
        assert "noise_0.2" in stability_results

    def test_sensitivity_analysis(self):
        """测试敏感性分析"""
        result = self.weight_validator._sensitivity_analysis(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "feature_sensitivity" in result
        assert "overall_sensitivity" in result
        assert "most_sensitive_feature" in result

        # 检查特征敏感性
        feature_sensitivity = result["feature_sensitivity"]
        for feature in self.X.columns:
            assert feature in feature_sensitivity
            assert "sensitivity" in feature_sensitivity[feature]
            assert "performance_changes" in feature_sensitivity[feature]
            assert "weight_changes" in feature_sensitivity[feature]

    def test_robustness_test(self):
        """测试鲁棒性测试"""
        result = self.weight_validator._robustness_test(self.X, self.y, self.weights)

        assert isinstance(result, dict)
        assert "robustness_results" in result
        assert "robustness_score" in result
        assert "improvement_consistency" in result
        assert "mean_improvement" in result

        # 检查鲁棒性结果
        robustness_results = result["robustness_results"]
        assert "subset_0.5" in robustness_results
        assert "subset_0.7" in robustness_results
        assert "subset_0.9" in robustness_results

    def test_statistical_significance_test(self):
        """测试统计显著性测试"""
        result = self.weight_validator._statistical_significance_test(
            self.X, self.y, self.weights
        )

        assert isinstance(result, dict)
        assert "f_statistic" in result
        assert "f_p_value" in result
        assert "r2_original" in result
        assert "r2_weighted" in result
        assert "r2_improvement" in result
        assert "r2_original_ci" in result
        assert "r2_weighted_ci" in result
        assert "significant_improvement" in result

        # 检查统计结果
        assert isinstance(result["f_statistic"], (int, float))
        assert 0 <= result["f_p_value"] <= 1
        assert 0 <= result["r2_original"] <= 1
        assert 0 <= result["r2_weighted"] <= 1
        assert isinstance(result["significant_improvement"], bool)

    def test_calculate_r2_confidence_interval(self):
        """测试R²置信区间计算"""
        r2 = 0.8
        n = 100

        ci = self.weight_validator._calculate_r2_confidence_interval(r2, n)

        assert isinstance(ci, tuple)
        assert len(ci) == 2
        assert ci[0] <= ci[1]  # 下界应该小于上界
        assert 0 <= ci[0] <= 1
        assert 0 <= ci[1] <= 1

    def test_apply_weights(self):
        """测试权重应用"""
        X_weighted = self.weight_validator._apply_weights(self.X, self.weights)

        assert isinstance(X_weighted, pd.DataFrame)
        assert X_weighted.shape == self.X.shape

        # 检查权重应用
        for feature, weight in self.weights.items():
            assert np.allclose(X_weighted[feature], self.X[feature] * weight)

    def test_calculate_validation_score(self):
        """测试验证评分计算"""
        validation_results = {
            "cross_validation": {"improvement": 0.1},
            "bootstrap": {"positive_improvement_rate": 0.8},
            "time_series": {"improvement": 0.05},
            "stability": {"stability_score": 0.9},
            "sensitivity": {"overall_sensitivity": 0.2},
            "robustness": {"robustness_score": 0.7},
        }

        score = self.weight_validator._calculate_validation_score(validation_results)

        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_get_validation_insights(self):
        """测试验证洞察获取"""
        # 先进行验证
        self.weight_validator.validate_weights(self.X, self.y, self.weights)

        insights = self.weight_validator.get_validation_insights()

        assert isinstance(insights, dict)
        assert "validation_results" in insights
        assert "validation_history" in insights
        assert "performance_metrics" in insights
        assert "recommendations" in insights

    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        empty_weights = {}

        result = self.weight_validator.validate_weights(empty_X, empty_y, empty_weights)

        assert isinstance(result, dict)
        assert "overall_score" in result

    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({"feature1": [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        single_weights = {"feature1": 1.0}

        result = self.weight_validator.validate_weights(
            single_X, single_y, single_weights
        )

        assert isinstance(result, dict)
        assert "overall_score" in result

    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame(
            {f"feature_{i}": np.random.normal(0, 1, 500) for i in range(8)}
        )
        large_y = pd.Series(np.random.normal(0, 1, 500))
        large_weights = {f"feature_{i}": 1.0 / 8 for i in range(8)}

        result = self.weight_validator.validate_weights(large_X, large_y, large_weights)

        assert isinstance(result, dict)
        assert "overall_score" in result

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
        high_corr_weights = {"feature1": 0.6, "feature2": 0.4}

        result = self.weight_validator.validate_weights(
            high_corr_X, high_corr_y, high_corr_weights
        )

        assert isinstance(result, dict)
        assert "overall_score" in result
        # 高相关性数据应该通过验证
        assert result["overall_score"] > 0

    def test_weight_effectiveness(self):
        """测试权重有效性"""
        # 创建明显有效的权重
        effective_weights = {"feature1": 0.8, "feature2": 0.2, "feature3": 0.0}

        result = self.weight_validator.validate_weights(
            self.X, self.y, effective_weights
        )

        assert isinstance(result, dict)
        assert "overall_score" in result
        # 有效权重应该得到高分
        assert result["overall_score"] > 0.5

    def test_weight_ineffectiveness(self):
        """测试权重无效性"""
        # 创建明显无效的权重
        ineffective_weights = {"feature1": 0.0, "feature2": 0.0, "feature3": 1.0}

        result = self.weight_validator.validate_weights(
            self.X, self.y, ineffective_weights
        )

        assert isinstance(result, dict)
        assert "overall_score" in result
        # 无效权重应该得到低分
        assert result["overall_score"] < 0.5

    def test_validation_consistency(self):
        """测试验证一致性"""
        # 多次运行应该得到一致的结果
        result1 = self.weight_validator.validate_weights(self.X, self.y, self.weights)
        result2 = self.weight_validator.validate_weights(self.X, self.y, self.weights)

        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

        # 检查关键指标的一致性
        if "overall_score" in result1 and "overall_score" in result2:
            assert abs(result1["overall_score"] - result2["overall_score"]) < 1e-6

    def test_different_validation_methods(self):
        """测试不同验证方法"""
        methods = ["cross_validation", "bootstrap", "time_series", "stability"]

        for method in methods:
            result = self.weight_validator.validate_weights(
                self.X, self.y, self.weights, validation_methods=[method]
            )

            assert isinstance(result, dict)
            assert method in result
            assert "overall_score" in result

    def test_validation_thresholds(self):
        """测试验证阈值"""
        # 测试不同权重的验证结果
        weights_list = [
            {"feature1": 0.8, "feature2": 0.2, "feature3": 0.0},
            {"feature1": 0.5, "feature2": 0.3, "feature3": 0.2},
            {"feature1": 0.2, "feature2": 0.3, "feature3": 0.5},
        ]

        scores = []
        for weights in weights_list:
            result = self.weight_validator.validate_weights(self.X, self.y, weights)
            scores.append(result["overall_score"])

        # 检查分数差异
        assert len(scores) == len(weights_list)
        assert all(0 <= score <= 1 for score in scores)
