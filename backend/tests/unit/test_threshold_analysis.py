"""
阈值效应分析测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.threshold_analysis import ThresholdAnalysis

class TestThresholdAnalysis:
    """阈值效应分析测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.threshold_analysis = ThresholdAnalysis()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有阈值效应的目标变量
        threshold = 0.5
        self.y = pd.Series(
            np.where(self.X['feature1'] > threshold, 
                    self.X['feature1'] * 2, 
                    self.X['feature1']) + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_detect_threshold_effects(self):
        """测试阈值效应检测"""
        result = self.threshold_analysis.detect_threshold_effects(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'decision_tree' in result
        assert 'piecewise_regression' in result
        assert 'random_forest' in result
        assert 'overall_score' in result
        
        # 检查整体评分
        assert 0 <= result['overall_score'] <= 1
    
    def test_detect_tree_thresholds(self):
        """测试决策树阈值检测"""
        result = self.threshold_analysis._detect_tree_thresholds(self.X, self.y, 10)
        
        assert isinstance(result, dict)
        
        # 检查是否有阈值被发现
        if result:
            for feature, feature_data in result.items():
                assert 'thresholds' in feature_data
                assert 'effectiveness' in feature_data
                assert 'tree_depth' in feature_data
                assert 'n_leaves' in feature_data
    
    def test_extract_tree_thresholds(self):
        """测试从决策树中提取阈值"""
        from sklearn.tree import DecisionTreeRegressor
        
        # 创建简单的决策树
        tree = DecisionTreeRegressor(max_depth=2, random_state=42)
        tree.fit(self.X[['feature1']], self.y)
        
        thresholds = self.threshold_analysis._extract_tree_thresholds(tree, 'feature1')
        
        assert isinstance(thresholds, list)
        # 阈值应该是数值
        for threshold in thresholds:
            assert isinstance(threshold, (int, float))
    
    def test_evaluate_threshold_effectiveness(self):
        """测试阈值有效性评估"""
        result = self.threshold_analysis._evaluate_threshold_effectiveness(
            self.X, self.y, 'feature1', [0.5, 1.0]
        )
        
        assert isinstance(result, dict)
        
        for threshold_name, threshold_data in result.items():
            assert 'improvement' in threshold_data
            assert 'r2_baseline' in threshold_data
            assert 'r2_segmented' in threshold_data
            assert 'coefficient' in threshold_data
    
    def test_analyze_piecewise_regression(self):
        """测试分段回归分析"""
        result = self.threshold_analysis._analyze_piecewise_regression(self.X, self.y, 10)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'optimal_threshold' in feature_data
                assert 'segment_model' in feature_data
                assert 'performance' in feature_data
    
    def test_find_optimal_threshold(self):
        """测试最优阈值寻找"""
        optimal_threshold = self.threshold_analysis._find_optimal_threshold(
            self.X, self.y, 'feature1', 10
        )
        
        if optimal_threshold is not None:
            assert isinstance(optimal_threshold, (int, float))
            assert self.X['feature1'].min() <= optimal_threshold <= self.X['feature1'].max()
    
    def test_calculate_piecewise_score(self):
        """测试分段模型得分计算"""
        score = self.threshold_analysis._calculate_piecewise_score(
            self.X, self.y, 'feature1', 0.5
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_create_piecewise_model(self):
        """测试分段模型创建"""
        model_data = self.threshold_analysis._create_piecewise_model(
            self.X, self.y, 'feature1', 0.5
        )
        
        assert isinstance(model_data, dict)
        if model_data:
            assert 'model' in model_data
            assert 'threshold' in model_data
            assert 'below_threshold_coef' in model_data
            assert 'above_threshold_coef' in model_data
            assert 'threshold_effect' in model_data
            assert 'intercept' in model_data
    
    def test_evaluate_piecewise_model(self):
        """测试分段模型性能评估"""
        performance = self.threshold_analysis._evaluate_piecewise_model(
            self.X, self.y, 'feature1', 0.5
        )
        
        assert isinstance(performance, dict)
        assert 'r2_piecewise' in performance
        assert 'r2_baseline' in performance
        assert 'r2_improvement' in performance
        assert 'mse_piecewise' in performance
        assert 'mse_baseline' in performance
        assert 'mse_improvement' in performance
    
    def test_analyze_rf_thresholds(self):
        """测试随机森林阈值分析"""
        result = self.threshold_analysis._analyze_rf_thresholds(self.X, self.y, 10)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'best_threshold' in feature_data
                assert 'improvement' in feature_data
                assert 'all_scores' in feature_data
    
    def test_calculate_threshold_score(self):
        """测试阈值效应评分计算"""
        threshold_results = {
            'decision_tree': {'feature1': {'effectiveness': {'threshold_0.5': {'improvement': 0.1}}}},
            'piecewise_regression': {'feature1': {'performance': {'r2_improvement': 0.2}}},
            'random_forest': {'feature1': {'improvement': 0.15}}
        }
        
        score = self.threshold_analysis._calculate_threshold_score(threshold_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_create_threshold_features(self):
        """测试阈值特征创建"""
        # 先检测阈值效应
        self.threshold_analysis.detect_threshold_effects(self.X, self.y)
        
        # 创建阈值特征
        X_enhanced = self.threshold_analysis.create_threshold_features(self.X, 0.05)
        
        assert isinstance(X_enhanced, pd.DataFrame)
        assert len(X_enhanced.columns) >= len(self.X.columns)
        assert all(col in X_enhanced.columns for col in self.X.columns)
    
    def test_get_threshold_insights(self):
        """测试阈值效应洞察获取"""
        # 先检测阈值效应
        self.threshold_analysis.detect_threshold_effects(self.X, self.y)
        
        insights = self.threshold_analysis.get_threshold_insights()
        
        assert isinstance(insights, dict)
        assert 'overall_threshold_score' in insights
        assert 'threshold_level' in insights
        assert 'key_thresholds' in insights
        assert 'recommendations' in insights
        
        # 检查阈值效应水平
        assert insights['threshold_level'] in ['高阈值效应', '中等阈值效应', '低阈值效应', '无显著阈值效应']
    
    def test_classify_threshold_level(self):
        """测试阈值效应水平分类"""
        assert self.threshold_analysis._classify_threshold_level(0.8) == "高阈值效应"
        assert self.threshold_analysis._classify_threshold_level(0.5) == "中等阈值效应"
        assert self.threshold_analysis._classify_threshold_level(0.2) == "低阈值效应"
        assert self.threshold_analysis._classify_threshold_level(0.05) == "无显著阈值效应"
    
    def test_extract_key_thresholds(self):
        """测试关键阈值提取"""
        # 设置模拟数据
        self.threshold_analysis.thresholds = {
            'decision_tree': {
                'feature1': {
                    'effectiveness': {
                        'threshold_0.5': {'improvement': 0.15}
                    }
                }
            },
            'piecewise_regression': {
                'feature1': {
                    'optimal_threshold': 0.5,
                    'performance': {'r2_improvement': 0.2}
                }
            },
            'random_forest': {
                'feature1': {
                    'best_threshold': 0.5,
                    'improvement': 0.1
                }
            }
        }
        
        key_thresholds = self.threshold_analysis._extract_key_thresholds()
        
        assert isinstance(key_thresholds, list)
        if key_thresholds:
            for threshold in key_thresholds:
                assert 'type' in threshold
                assert 'feature' in threshold
                assert 'threshold' in threshold
                assert 'improvement' in threshold
    
    def test_generate_threshold_recommendations(self):
        """测试阈值效应建议生成"""
        # 设置不同评分水平的模拟数据
        self.threshold_analysis.thresholds = {'overall_score': 0.8}
        recommendations_high = self.threshold_analysis._generate_threshold_recommendations()
        
        self.threshold_analysis.thresholds = {'overall_score': 0.3}
        recommendations_low = self.threshold_analysis._generate_threshold_recommendations()
        
        assert isinstance(recommendations_high, list)
        assert isinstance(recommendations_low, list)
        assert len(recommendations_high) > 0
        assert len(recommendations_low) > 0
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.threshold_analysis.detect_threshold_effects(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert result['overall_score'] == 0.0
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.threshold_analysis.detect_threshold_effects(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_clear_threshold_data(self):
        """测试明显阈值数据处理"""
        # 创建有明显阈值的数据
        clear_threshold_X = pd.DataFrame({
            'feature1': np.concatenate([np.random.normal(-2, 0.5, 50), 
                                       np.random.normal(2, 0.5, 50)])
        })
        clear_threshold_y = pd.Series(
            np.where(clear_threshold_X['feature1'] > 0, 
                    clear_threshold_X['feature1'] * 3, 
                    clear_threshold_X['feature1'])
        )
        
        result = self.threshold_analysis.detect_threshold_effects(clear_threshold_X, clear_threshold_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 明显阈值数据应该检测到阈值效应
        assert result['overall_score'] > 0
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 1000)
            for i in range(5)
        })
        large_y = pd.Series(np.random.normal(0, 1, 1000))
        
        result = self.threshold_analysis.detect_threshold_effects(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result



