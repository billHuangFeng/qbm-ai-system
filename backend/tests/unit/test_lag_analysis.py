"""
时间滞后分析测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.lag_analysis import LagAnalysis

class TestLagAnalysis:
    """时间滞后分析测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.lag_analysis = LagAnalysis()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有时间滞后效应的目标变量
        self.y = pd.Series(
            self.X['feature1'].shift(1).fillna(0) + 
            self.X['feature2'].shift(2).fillna(0) + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_detect_lag_effects(self):
        """测试时间滞后效应检测"""
        result = self.lag_analysis.detect_lag_effects(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'cross_correlation' in result
        assert 'lag_regression' in result
        assert 'granger_causality' in result
        assert 'optimal_lags' in result
        assert 'overall_score' in result
        
        # 检查整体评分
        assert 0 <= result['overall_score'] <= 1
    
    def test_analyze_cross_correlation(self):
        """测试交叉相关分析"""
        result = self.lag_analysis._analyze_cross_correlation(self.X, self.y, 5, 0.1)
        
        assert isinstance(result, dict)
        
        # 检查是否有滞后效应被发现
        if result:
            for feature, feature_data in result.items():
                assert 'correlations' in feature_data
                assert 'optimal_lag' in feature_data
                assert 'max_correlation' in feature_data
                assert 'lag_significance' in feature_data
    
    def test_analyze_lag_regression(self):
        """测试滞后回归分析"""
        result = self.lag_analysis._analyze_lag_regression(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'lag_performance' in feature_data
                assert 'best_lag' in feature_data
                assert 'best_r2' in feature_data
                assert 'best_mse' in feature_data
                assert 'coefficient' in feature_data
    
    def test_analyze_granger_causality(self):
        """测试格兰杰因果性分析"""
        result = self.lag_analysis._analyze_granger_causality(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'causality_tests' in feature_data
                assert 'significant_lags' in feature_data
                assert 'causality' in feature_data
    
    def test_select_optimal_lags(self):
        """测试最优滞后选择"""
        result = self.lag_analysis._select_optimal_lags(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, optimal_lag in result.items():
                assert isinstance(optimal_lag, int)
                assert 0 <= optimal_lag <= 5
    
    def test_calculate_lag_significance(self):
        """测试滞后显著性计算"""
        feature_values = np.random.normal(0, 1, 100)
        y_values = np.random.normal(0, 1, 100)
        
        significance = self.lag_analysis._calculate_lag_significance(
            feature_values, y_values, 1
        )
        
        assert isinstance(significance, float)
        assert 0 <= significance <= 1
    
    def test_calculate_f_p_value(self):
        """测试F统计量p值计算"""
        p_value = self.lag_analysis._calculate_f_p_value(2.0, 1, 10)
        
        assert isinstance(p_value, float)
        assert 0 <= p_value <= 1
    
    def test_calculate_lag_score(self):
        """测试滞后效应评分计算"""
        lag_results = {
            'cross_correlation': {'feature1': {'max_correlation': 0.5}},
            'lag_regression': {'feature1': {'best_r2': 0.6}},
            'granger_causality': {'feature1': {'causality': True}}
        }
        
        score = self.lag_analysis._calculate_lag_score(lag_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_create_lag_features(self):
        """测试滞后特征创建"""
        # 先检测滞后效应
        self.lag_analysis.detect_lag_effects(self.X, self.y)
        
        # 创建滞后特征
        X_enhanced = self.lag_analysis.create_lag_features(self.X, 0.1)
        
        assert isinstance(X_enhanced, pd.DataFrame)
        assert len(X_enhanced.columns) >= len(self.X.columns)
        assert all(col in X_enhanced.columns for col in self.X.columns)
    
    def test_get_lag_insights(self):
        """测试滞后效应洞察获取"""
        # 先检测滞后效应
        self.lag_analysis.detect_lag_effects(self.X, self.y)
        
        insights = self.lag_analysis.get_lag_insights()
        
        assert isinstance(insights, dict)
        assert 'overall_lag_score' in insights
        assert 'lag_level' in insights
        assert 'key_lags' in insights
        assert 'recommendations' in insights
        
        # 检查滞后效应水平
        assert insights['lag_level'] in ['高滞后效应', '中等滞后效应', '低滞后效应', '无显著滞后效应']
    
    def test_classify_lag_level(self):
        """测试滞后效应水平分类"""
        assert self.lag_analysis._classify_lag_level(0.8) == "高滞后效应"
        assert self.lag_analysis._classify_lag_level(0.5) == "中等滞后效应"
        assert self.lag_analysis._classify_lag_level(0.2) == "低滞后效应"
        assert self.lag_analysis._classify_lag_level(0.05) == "无显著滞后效应"
    
    def test_extract_key_lags(self):
        """测试关键滞后提取"""
        # 设置模拟数据
        self.lag_analysis.lag_effects = {
            'cross_correlation': {
                'feature1': {
                    'optimal_lag': 1,
                    'max_correlation': 0.5,
                    'lag_significance': 0.8
                }
            },
            'lag_regression': {
                'feature1': {
                    'best_lag': 1,
                    'r2': 0.6,
                    'coefficient': 0.5
                }
            },
            'granger_causality': {
                'feature1': {
                    'causality': True,
                    'best_lag': 1,
                    'best_p_value': 0.01,
                    'best_f_statistic': 5.0
                }
            }
        }
        
        key_lags = self.lag_analysis._extract_key_lags()
        
        assert isinstance(key_lags, list)
        if key_lags:
            for lag in key_lags:
                assert 'type' in lag
                assert 'feature' in lag
                assert 'lag' in lag
    
    def test_generate_lag_recommendations(self):
        """测试滞后效应建议生成"""
        # 设置不同评分水平的模拟数据
        self.lag_analysis.lag_effects = {'overall_score': 0.8}
        recommendations_high = self.lag_analysis._generate_lag_recommendations()
        
        self.lag_analysis.lag_effects = {'overall_score': 0.3}
        recommendations_low = self.lag_analysis._generate_lag_recommendations()
        
        assert isinstance(recommendations_high, list)
        assert isinstance(recommendations_low, list)
        assert len(recommendations_high) > 0
        assert len(recommendations_low) > 0
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.lag_analysis.detect_lag_effects(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert result['overall_score'] == 0.0
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.lag_analysis.detect_lag_effects(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_clear_lag_data(self):
        """测试明显滞后数据处理"""
        # 创建有明显滞后的数据
        clear_lag_X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100)
        })
        clear_lag_y = pd.Series(
            clear_lag_X['feature1'].shift(2).fillna(0) + 
            np.random.normal(0, 0.1, 100)
        )
        
        result = self.lag_analysis.detect_lag_effects(clear_lag_X, clear_lag_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 明显滞后数据应该检测到滞后效应
        assert result['overall_score'] > 0
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 1000)
            for i in range(5)
        })
        large_y = pd.Series(np.random.normal(0, 1, 1000))
        
        result = self.lag_analysis.detect_lag_effects(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_negative_lag_handling(self):
        """测试负滞后处理"""
        # 创建有负滞后的数据（未来值影响当前值）
        negative_lag_X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100)
        })
        negative_lag_y = pd.Series(
            negative_lag_X['feature1'].shift(-1).fillna(0) + 
            np.random.normal(0, 0.1, 100)
        )
        
        result = self.lag_analysis.detect_lag_effects(negative_lag_X, negative_lag_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_multiple_lag_effects(self):
        """测试多重滞后效应"""
        # 创建有多重滞后的数据
        multi_lag_X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100)
        })
        multi_lag_y = pd.Series(
            multi_lag_X['feature1'].shift(1).fillna(0) + 
            multi_lag_X['feature2'].shift(3).fillna(0) + 
            np.random.normal(0, 0.1, 100)
        )
        
        result = self.lag_analysis.detect_lag_effects(multi_lag_X, multi_lag_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 多重滞后数据应该检测到滞后效应
        assert result['overall_score'] > 0

