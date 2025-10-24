"""
动态权重计算测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.dynamic_weights import DynamicWeightCalculator

class TestDynamicWeightCalculator:
    """动态权重计算器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.weight_calculator = DynamicWeightCalculator()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有明确权重关系的目标变量
        self.y = pd.Series(
            self.X['feature1'] * 2 + 
            self.X['feature2'] * 1.5 + 
            self.X['feature3'] * 0.5 + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_calculate_dynamic_weights_correlation(self):
        """测试基于相关性的动态权重计算"""
        result = self.weight_calculator.calculate_dynamic_weights(
            self.X, self.y, method='correlation'
        )
        
        assert isinstance(result, dict)
        assert 'correlation' in result
        assert 'normalized' in result
        assert 'stability' in result
        assert 'effectiveness' in result
        assert 'overall_score' in result
        
        # 检查相关性权重
        correlation_weights = result['correlation']
        assert isinstance(correlation_weights, dict)
        assert len(correlation_weights) == len(self.X.columns)
        
        # 检查权重归一化
        normalized_weights = result['normalized']
        assert isinstance(normalized_weights, dict)
    
    def test_calculate_dynamic_weights_importance(self):
        """测试基于重要性的动态权重计算"""
        result = self.weight_calculator.calculate_dynamic_weights(
            self.X, self.y, method='importance'
        )
        
        assert isinstance(result, dict)
        assert 'importance' in result
        
        # 检查重要性权重
        importance_weights = result['importance']
        assert isinstance(importance_weights, dict)
        assert len(importance_weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in importance_weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_calculate_dynamic_weights_regression(self):
        """测试基于回归系数的动态权重计算"""
        result = self.weight_calculator.calculate_dynamic_weights(
            self.X, self.y, method='regression'
        )
        
        assert isinstance(result, dict)
        assert 'regression' in result
        
        # 检查回归权重
        regression_weights = result['regression']
        assert isinstance(regression_weights, dict)
        assert len(regression_weights) == len(self.X.columns)
    
    def test_calculate_dynamic_weights_time_series(self):
        """测试基于时间序列的动态权重计算"""
        result = self.weight_calculator.calculate_dynamic_weights(
            self.X, self.y, method='time_series'
        )
        
        assert isinstance(result, dict)
        assert 'time_series' in result
        
        # 检查时间序列权重
        time_series_weights = result['time_series']
        assert isinstance(time_series_weights, dict)
        assert len(time_series_weights) == len(self.X.columns)
    
    def test_calculate_dynamic_weights_comprehensive(self):
        """测试综合动态权重计算"""
        result = self.weight_calculator.calculate_dynamic_weights(
            self.X, self.y, method='comprehensive'
        )
        
        assert isinstance(result, dict)
        assert 'comprehensive' in result
        assert 'normalized' in result
        
        # 检查综合权重
        comprehensive_weights = result['comprehensive']
        assert isinstance(comprehensive_weights, dict)
        assert len(comprehensive_weights) == len(self.X.columns)
    
    def test_calculate_correlation_weights(self):
        """测试相关性权重计算"""
        weights = self.weight_calculator._calculate_correlation_weights(self.X, self.y)
        
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_calculate_importance_weights(self):
        """测试重要性权重计算"""
        weights = self.weight_calculator._calculate_importance_weights(self.X, self.y)
        
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_calculate_regression_weights(self):
        """测试回归系数权重计算"""
        weights = self.weight_calculator._calculate_regression_weights(self.X, self.y)
        
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_calculate_time_series_weights(self):
        """测试时间序列权重计算"""
        weights = self.weight_calculator._calculate_time_series_weights(self.X, self.y)
        
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_calculate_comprehensive_weights(self):
        """测试综合权重计算"""
        weights = self.weight_calculator._calculate_comprehensive_weights(self.X, self.y)
        
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重值
        for feature, weight in weights.items():
            assert isinstance(weight, (int, float))
            assert weight >= 0
    
    def test_normalize_weights(self):
        """测试权重归一化"""
        weight_results = {
            'correlation': {'feature1': 0.8, 'feature2': 0.6, 'feature3': 0.4},
            'importance': {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
        }
        
        normalized = self.weight_calculator._normalize_weights(weight_results)
        
        assert isinstance(normalized, dict)
        assert 'correlation' in normalized
        assert 'importance' in normalized
        
        # 检查归一化后的权重和
        for method, weights in normalized.items():
            if isinstance(weights, dict):
                total_weight = sum(weights.values())
                assert abs(total_weight - 1.0) < 1e-6  # 权重和应该接近1
    
    def test_analyze_weight_stability(self):
        """测试权重稳定性分析"""
        weight_results = {
            'correlation': {'feature1': 0.8, 'feature2': 0.6, 'feature3': 0.4},
            'importance': {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
        }
        
        stability = self.weight_calculator._analyze_weight_stability(weight_results)
        
        assert isinstance(stability, dict)
        
        # 检查稳定性指标
        for method, metrics in stability.items():
            if isinstance(metrics, dict):
                assert 'mean_weight' in metrics
                assert 'std_weight' in metrics
                assert 'max_weight' in metrics
                assert 'min_weight' in metrics
    
    def test_validate_weight_effectiveness(self):
        """测试权重有效性验证"""
        weights = {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
        
        effectiveness = self.weight_calculator._validate_weight_effectiveness(
            self.X, self.y, {'final': weights}
        )
        
        assert isinstance(effectiveness, dict)
        assert 'r2_improvement' in effectiveness
        assert 'mse_improvement' in effectiveness
        assert 'r2_weighted' in effectiveness
        assert 'r2_original' in effectiveness
    
    def test_optimize_weights(self):
        """测试权重优化"""
        result = self.weight_calculator.optimize_weights(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'optimized_weights' in result
        assert 'optimization_success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查优化后的权重
        optimized_weights = result['optimized_weights']
        assert isinstance(optimized_weights, dict)
        assert len(optimized_weights) == len(self.X.columns)
        
        # 检查权重和
        total_weight = sum(optimized_weights.values())
        assert abs(total_weight - 1.0) < 1e-6
    
    def test_update_weights(self):
        """测试权重更新"""
        previous_weights = {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
        
        updated_weights = self.weight_calculator.update_weights(
            self.X, self.y, previous_weights, update_rate=0.1
        )
        
        assert isinstance(updated_weights, dict)
        assert len(updated_weights) == len(self.X.columns)
        
        # 检查权重和
        total_weight = sum(updated_weights.values())
        assert abs(total_weight - 1.0) < 1e-6
    
    def test_get_weight_insights(self):
        """测试权重洞察获取"""
        # 先计算权重
        self.weight_calculator.calculate_dynamic_weights(self.X, self.y)
        
        insights = self.weight_calculator.get_weight_insights()
        
        assert isinstance(insights, dict)
        assert 'weight_history' in insights
        assert 'optimization_results' in insights
        assert 'weight_models' in insights
        assert 'recommendations' in insights
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.weight_calculator.calculate_dynamic_weights(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.weight_calculator.calculate_dynamic_weights(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_high_correlation_data(self):
        """测试高相关性数据处理"""
        # 创建高相关性的数据
        high_corr_X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100)
        })
        high_corr_y = pd.Series(high_corr_X['feature1'] * 2 + high_corr_X['feature2'] * 1.5)
        
        result = self.weight_calculator.calculate_dynamic_weights(high_corr_X, high_corr_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 高相关性数据应该检测到权重效应
        assert result['overall_score'] > 0
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 1000)
            for i in range(10)
        })
        large_y = pd.Series(np.random.normal(0, 1, 1000))
        
        result = self.weight_calculator.calculate_dynamic_weights(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_weight_consistency(self):
        """测试权重一致性"""
        # 多次运行应该得到一致的结果
        result1 = self.weight_calculator.calculate_dynamic_weights(self.X, self.y)
        result2 = self.weight_calculator.calculate_dynamic_weights(self.X, self.y)
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        
        # 检查关键指标的一致性
        if 'overall_score' in result1 and 'overall_score' in result2:
            assert abs(result1['overall_score'] - result2['overall_score']) < 1e-6
    
    def test_different_objectives(self):
        """测试不同优化目标"""
        # 测试R²目标
        result_r2 = self.weight_calculator.optimize_weights(self.X, self.y, objective='r2')
        assert isinstance(result_r2, dict)
        
        # 测试MSE目标
        result_mse = self.weight_calculator.optimize_weights(self.X, self.y, objective='mse')
        assert isinstance(result_mse, dict)
        
        # 检查结果结构
        for result in [result_r2, result_mse]:
            assert 'optimized_weights' in result
            assert 'r2_score' in result
            assert 'mse_score' in result

