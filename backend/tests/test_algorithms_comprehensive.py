"""
算法单元测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.algorithms.synergy_analysis import SynergyAnalysis
from src.algorithms.threshold_analysis import ThresholdAnalysis
from src.algorithms.lag_analysis import LagAnalysis
from src.algorithms.advanced_relationships import AdvancedRelationships
from src.algorithms.dynamic_weights import DynamicWeights
from src.algorithms.weight_optimization import WeightOptimization
from src.algorithms.weight_validation import WeightValidation
from src.algorithms.weight_monitoring import WeightMonitoring


@pytest.fixture
def sample_data():
    """生成测试数据"""
    np.random.seed(42)
    n_samples = 200

    # 创建有协同效应的数据
    feature_1 = np.random.normal(10, 2, n_samples)
    feature_2 = np.random.normal(5, 1, n_samples)
    feature_3 = np.random.normal(8, 1.5, n_samples)

    # 目标变量包含协同效应
    target = (
        2 * feature_1
        + 1.5 * feature_2
        + 1 * feature_3
        + 0.5 * feature_1 * feature_2  # 协同效应
        + 0.3 * np.sin(feature_3)  # 非线性效应
        + np.random.normal(0, 1, n_samples)
    )

    data = {
        "feature_1": feature_1,
        "feature_2": feature_2,
        "feature_3": feature_3,
        "target": target,
    }

    return pd.DataFrame(data)


@pytest.fixture
def time_series_data():
    """生成时间序列测试数据"""
    np.random.seed(42)
    dates = pd.date_range(start="2020-01-01", end="2023-12-31", freq="D")
    n_samples = len(dates)

    # 创建有趋势和季节性的时间序列
    trend = np.linspace(100, 200, n_samples)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(n_samples) / 365.25)
    noise = np.random.normal(0, 5, n_samples)

    values = trend + seasonal + noise

    data = {
        "date": dates,
        "value": values,
        "feature_1": np.random.normal(10, 2, n_samples),
        "feature_2": np.random.normal(5, 1, n_samples),
    }

    return pd.DataFrame(data)


class TestSynergyAnalysis:
    """协同效应分析测试"""

    def test_detect_synergy_effects(self, sample_data):
        """测试协同效应检测"""
        synergy_analysis = SynergyAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = synergy_analysis.detect_synergy_effects(X, y)

        # 验证返回结果结构
        assert "overall_score" in results
        assert "pairwise_interactions" in results
        assert "polynomial_interactions" in results
        assert "random_forest_interactions" in results
        assert "shapley_values" in results

        # 验证分数范围
        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

        # 验证协同效应检测
        assert len(results["pairwise_interactions"]) > 0
        assert len(results["polynomial_interactions"]) > 0

    def test_calculate_shapley_values(self, sample_data):
        """测试Shapley值计算"""
        synergy_analysis = SynergyAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        shapley_values = synergy_analysis.calculate_shapley_values(X, y)

        assert "feature_contributions" in shapley_values
        assert "interaction_contributions" in shapley_values
        assert "synergy_scores" in shapley_values

        # 验证Shapley值属性
        contributions = shapley_values["feature_contributions"]
        assert len(contributions) == 3  # 3个特征
        assert all(isinstance(v, float) for v in contributions.values())

    def test_create_synergy_features(self, sample_data):
        """测试协同特征创建"""
        synergy_analysis = SynergyAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 先检测协同效应
        synergy_analysis.detect_synergy_effects(X, y)

        # 创建协同特征
        X_enhanced = synergy_analysis.create_synergy_features(X)

        assert len(X_enhanced.columns) >= len(X.columns)
        assert all(col in X_enhanced.columns for col in X.columns)

    def test_get_synergy_insights(self, sample_data):
        """测试协同效应洞察"""
        synergy_analysis = SynergyAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        synergy_analysis.detect_synergy_effects(X, y)
        insights = synergy_analysis.get_synergy_insights()

        assert "overall_synergy_score" in insights
        assert "synergy_level" in insights
        assert "key_interactions" in insights
        assert "recommendations" in insights

        assert isinstance(insights["overall_synergy_score"], float)
        assert isinstance(insights["synergy_level"], str)
        assert isinstance(insights["key_interactions"], list)
        assert isinstance(insights["recommendations"], list)


class TestThresholdAnalysis:
    """阈值分析测试"""

    def test_detect_threshold_effects(self, sample_data):
        """测试阈值效应检测"""
        threshold_analysis = ThresholdAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = threshold_analysis.detect_threshold_effects(X, y)

        assert "overall_score" in results
        assert "tree_thresholds" in results
        assert "piecewise_regression" in results
        assert "random_forest_thresholds" in results

        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

    def test_detect_multiple_thresholds(self, sample_data):
        """测试多阈值检测"""
        threshold_analysis = ThresholdAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = threshold_analysis.detect_multiple_thresholds(X, y)

        assert "multiple_thresholds" in results
        assert "threshold_combinations" in results
        assert "multi_threshold_score" in results

        assert isinstance(results["multi_threshold_score"], float)
        assert 0 <= results["multi_threshold_score"] <= 1

    def test_analyze_threshold_stability(self, sample_data):
        """测试阈值稳定性分析"""
        threshold_analysis = ThresholdAnalysis()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = threshold_analysis.analyze_threshold_stability(X, y)

        assert "stability_analysis" in results
        assert "stability_scores" in results
        assert "stable_thresholds" in results

        assert isinstance(results["stability_scores"], dict)
        assert all(isinstance(v, float) for v in results["stability_scores"].values())


class TestLagAnalysis:
    """滞后分析测试"""

    def test_detect_lag_effects(self, time_series_data):
        """测试滞后效应检测"""
        lag_analysis = LagAnalysis()

        X = time_series_data[["feature_1", "feature_2"]]
        y = time_series_data["value"]

        results = lag_analysis.detect_lag_effects(X, y, max_lag=12)

        assert "overall_score" in results
        assert "cross_correlation" in results
        assert "lag_regression" in results
        assert "granger_causality" in results
        assert "optimal_lags" in results

        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

    def test_create_lag_features(self, time_series_data):
        """测试滞后特征创建"""
        lag_analysis = LagAnalysis()

        X = time_series_data[["feature_1", "feature_2"]]
        y = time_series_data["value"]

        # 先检测滞后效应
        lag_analysis.detect_lag_effects(X, y)

        # 创建滞后特征
        X_enhanced = lag_analysis.create_lag_features(X)

        assert len(X_enhanced.columns) >= len(X.columns)
        assert all(col in X_enhanced.columns for col in X.columns)


class TestAdvancedRelationships:
    """高级关系分析测试"""

    def test_analyze_complex_relationships(self, sample_data):
        """测试复杂关系分析"""
        advanced_relationships = AdvancedRelationships()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = advanced_relationships.analyze_complex_relationships(X, y)

        assert "overall_score" in results
        assert "linear" in results
        assert "nonlinear" in results
        assert "interaction" in results
        assert "hierarchical" in results
        assert "causal" in results

        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

    def test_create_relationship_features(self, sample_data):
        """测试关系特征创建"""
        advanced_relationships = AdvancedRelationships()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 先分析关系
        advanced_relationships.analyze_complex_relationships(X, y)

        # 创建关系特征
        X_enhanced = advanced_relationships.create_relationship_features(X)

        assert len(X_enhanced.columns) >= len(X.columns)
        assert all(col in X_enhanced.columns for col in X.columns)


class TestDynamicWeights:
    """动态权重测试"""

    def test_calculate_dynamic_weights(self, sample_data):
        """测试动态权重计算"""
        dynamic_weights = DynamicWeights()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = dynamic_weights.calculate_dynamic_weights(X, y)

        assert "overall_score" in results
        assert "correlation_weights" in results
        assert "importance_weights" in results
        assert "regression_weights" in results
        assert "time_series_weights" in results
        assert "normalized" in results

        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

        # 验证归一化权重
        normalized = results["normalized"]
        assert "final" in normalized
        final_weights = normalized["final"]
        assert abs(sum(final_weights.values()) - 1.0) < 1e-6  # 权重和应该接近1

    def test_optimize_weights(self, sample_data):
        """测试权重优化"""
        dynamic_weights = DynamicWeights()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = dynamic_weights.optimize_weights(X, y)

        assert "optimization_result" in results
        assert "optimized_weights" in results
        assert "optimization_score" in results

        assert isinstance(results["optimization_score"], float)
        assert 0 <= results["optimization_score"] <= 1


class TestWeightOptimization:
    """权重优化测试"""

    def test_optimize_weights(self, sample_data):
        """测试权重优化"""
        weight_optimizer = WeightOptimization()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = weight_optimizer.optimize_weights(X, y)

        assert "gradient_descent" in results
        assert "genetic_algorithm" in results
        assert "bayesian" in results
        assert "grid_search" in results
        assert "ensemble" in results

        # 验证每种方法的结果
        for method in [
            "gradient_descent",
            "genetic_algorithm",
            "bayesian",
            "grid_search",
        ]:
            if method in results:
                method_results = results[method]
                assert "mse" in method_results
                assert "optimal_weights" in method_results["mse"]

    def test_optimize_weights_with_validation(self, sample_data):
        """测试带验证的权重优化"""
        weight_optimizer = WeightOptimization()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        results = weight_optimizer.optimize_weights_with_validation(X, y)

        assert "gradient_descent" in results or "genetic_algorithm" in results

        # 验证交叉验证结果
        for method, method_results in results.items():
            assert "cv_scores" in method_results
            assert "mean_cv_score" in method_results
            assert "std_cv_score" in method_results
            assert "best_cv_weights" in method_results


class TestWeightValidation:
    """权重验证测试"""

    def test_validate_weights(self, sample_data):
        """测试权重验证"""
        weight_validator = WeightValidation()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 创建测试权重
        weights = {"feature_1": 0.4, "feature_2": 0.35, "feature_3": 0.25}

        results = weight_validator.validate_weights(X, y, weights)

        assert "overall_score" in results
        assert "cross_validation" in results
        assert "bootstrap" in results
        assert "holdout" in results
        assert "statistical" in results

        assert isinstance(results["overall_score"], float)
        assert 0 <= results["overall_score"] <= 1

    def test_compare_weight_sets(self, sample_data):
        """测试权重集比较"""
        weight_validator = WeightValidation()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 创建多个权重集
        weight_sets = {
            "equal_weights": {"feature_1": 0.33, "feature_2": 0.33, "feature_3": 0.34},
            "feature_1_heavy": {"feature_1": 0.7, "feature_2": 0.2, "feature_3": 0.1},
            "feature_2_heavy": {"feature_1": 0.2, "feature_2": 0.7, "feature_3": 0.1},
        }

        results = weight_validator.compare_weight_sets(X, y, weight_sets)

        assert "ranking" in results
        assert "best_weight_set" in results

        # 验证排序
        ranking = results["ranking"]
        assert len(ranking) == 3
        assert all("rank" in item for item in ranking)
        assert all("weight_set_name" in item for item in ranking)
        assert all("overall_score" in item for item in ranking)


class TestWeightMonitoring:
    """权重监控测试"""

    def test_monitor_weights(self, sample_data):
        """测试权重监控"""
        weight_monitor = WeightMonitoring()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 创建测试权重
        weights = {"feature_1": 0.4, "feature_2": 0.35, "feature_3": 0.25}

        results = weight_monitor.monitor_weights(X, y, weights)

        assert "weight_drift" in results
        assert "performance_monitoring" in results
        assert "stability_monitoring" in results
        assert "anomaly_detection" in results
        assert "trend_analysis" in results

        # 验证漂移检测
        drift_results = results["weight_drift"]
        assert "drift_detected" in drift_results
        assert "drift_score" in drift_results
        assert isinstance(drift_results["drift_detected"], bool)
        assert isinstance(drift_results["drift_score"], float)

    def test_monitoring_history(self, sample_data):
        """测试监控历史"""
        weight_monitor = WeightMonitoring()

        X = sample_data[["feature_1", "feature_2", "feature_3"]]
        y = sample_data["target"]

        # 模拟多次监控
        weights_1 = {"feature_1": 0.4, "feature_2": 0.35, "feature_3": 0.25}
        weights_2 = {"feature_1": 0.45, "feature_2": 0.3, "feature_3": 0.25}
        weights_3 = {"feature_1": 0.5, "feature_2": 0.25, "feature_3": 0.25}

        weight_monitor.monitor_weights(X, y, weights_1)
        weight_monitor.monitor_weights(X, y, weights_2)
        weight_monitor.monitor_weights(X, y, weights_3)

        # 验证监控历史
        assert len(weight_monitor.monitoring_history) == 3

        # 获取监控洞察
        insights = weight_monitor.get_monitoring_insights()
        assert "monitoring_summary" in insights
        assert "weight_performance" in insights
        assert "validation_trends" in insights
        assert "recommendations" in insights


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_data(self):
        """测试空数据"""
        synergy_analysis = SynergyAnalysis()

        X = pd.DataFrame()
        y = pd.Series(dtype=float)

        with pytest.raises((ValueError, IndexError)):
            synergy_analysis.detect_synergy_effects(X, y)

    def test_single_feature(self):
        """测试单特征数据"""
        np.random.seed(42)
        X = pd.DataFrame({"feature_1": np.random.normal(10, 2, 100)})
        y = pd.Series(np.random.normal(20, 3, 100))

        synergy_analysis = SynergyAnalysis()
        results = synergy_analysis.detect_synergy_effects(X, y)

        # 单特征情况下应该能正常处理
        assert "overall_score" in results
        assert isinstance(results["overall_score"], float)

    def test_constant_target(self):
        """测试常数目标变量"""
        np.random.seed(42)
        X = pd.DataFrame(
            {
                "feature_1": np.random.normal(10, 2, 100),
                "feature_2": np.random.normal(5, 1, 100),
            }
        )
        y = pd.Series([20] * 100)  # 常数目标

        threshold_analysis = ThresholdAnalysis()

        # 常数目标应该能处理，但可能返回低分数
        results = threshold_analysis.detect_threshold_effects(X, y)
        assert "overall_score" in results
        assert isinstance(results["overall_score"], float)

    def test_high_dimensional_data(self):
        """测试高维数据"""
        np.random.seed(42)
        n_features = 50
        n_samples = 200

        X = pd.DataFrame(
            {
                f"feature_{i}": np.random.normal(0, 1, n_samples)
                for i in range(n_features)
            }
        )
        y = pd.Series(np.random.normal(0, 1, n_samples))

        dynamic_weights = DynamicWeights()

        # 高维数据应该能处理
        results = dynamic_weights.calculate_dynamic_weights(X, y)
        assert "overall_score" in results
        assert isinstance(results["overall_score"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
