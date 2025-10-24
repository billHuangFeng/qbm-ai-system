"""
协同效应分析测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.synergy_analysis import SynergyAnalysis

class TestSynergyAnalysis:
    """协同效应分析测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.synergy_analysis = SynergyAnalysis()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有协同效应的目标变量
        self.y = pd.Series(
            self.X['feature1'] * self.X['feature2'] + 
            self.X['feature3'] + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_detect_synergy_effects(self):
        """测试协同效应检测"""
        result = self.synergy_analysis.detect_synergy_effects(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'pairwise' in result
        assert 'polynomial' in result
        assert 'random_forest' in result
        assert 'overall_score' in result
        
        # 检查整体评分
        assert 0 <= result['overall_score'] <= 1
    
    def test_analyze_pairwise_interactions(self):
        """测试两两交互效应分析"""
        result = self.synergy_analysis._analyze_pairwise_interactions(self.X, self.y, 0.1)
        
        assert isinstance(result, dict)
        
        # 检查是否有交互效应被发现
        if result:
            for interaction_name, interaction_data in result.items():
                assert 'improvement' in interaction_data
                assert 'r2_without' in interaction_data
                assert 'r2_with' in interaction_data
                assert 'coefficient' in interaction_data
                assert 'significance' in interaction_data
    
    def test_analyze_polynomial_interactions(self):
        """测试多项式交互效应分析"""
        result = self.synergy_analysis._analyze_polynomial_interactions(self.X, self.y, 0.1)
        
        assert isinstance(result, dict)
        
        if result:
            assert 'improvement' in result
            assert 'r2_linear' in result
            assert 'r2_poly' in result
            assert 'interaction_coefficients' in result
            assert 'top_interactions' in result
    
    def test_analyze_rf_interactions(self):
        """测试随机森林交互效应分析"""
        result = self.synergy_analysis._analyze_rf_interactions(self.X, self.y, 0.1)
        
        assert isinstance(result, dict)
        
        if result:
            assert 'feature_importance' in result
            assert 'high_importance_features' in result
            assert 'feature_combinations' in result
            assert 'importance_stats' in result
    
    def test_calculate_synergy_score(self):
        """测试协同效应评分计算"""
        synergy_results = {
            'pairwise': {'interaction1': {'improvement': 0.1}},
            'polynomial': {'improvement': 0.2},
            'random_forest': {'importance_stats': {'mean': 0.1}}
        }
        
        score = self.synergy_analysis._calculate_synergy_score(synergy_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_create_synergy_features(self):
        """测试协同效应特征创建"""
        # 先检测协同效应
        self.synergy_analysis.detect_synergy_effects(self.X, self.y)
        
        # 创建协同效应特征
        X_enhanced = self.synergy_analysis.create_synergy_features(self.X, 0.1)
        
        assert isinstance(X_enhanced, pd.DataFrame)
        assert len(X_enhanced.columns) >= len(self.X.columns)
        assert all(col in X_enhanced.columns for col in self.X.columns)
    
    def test_get_synergy_insights(self):
        """测试协同效应洞察获取"""
        # 先检测协同效应
        self.synergy_analysis.detect_synergy_effects(self.X, self.y)
        
        insights = self.synergy_analysis.get_synergy_insights()
        
        assert isinstance(insights, dict)
        assert 'overall_synergy_score' in insights
        assert 'synergy_level' in insights
        assert 'key_interactions' in insights
        assert 'recommendations' in insights
        
        # 检查协同效应水平
        assert insights['synergy_level'] in ['高协同效应', '中等协同效应', '低协同效应', '无显著协同效应']
    
    def test_classify_synergy_level(self):
        """测试协同效应水平分类"""
        assert self.synergy_analysis._classify_synergy_level(0.8) == "高协同效应"
        assert self.synergy_analysis._classify_synergy_level(0.5) == "中等协同效应"
        assert self.synergy_analysis._classify_synergy_level(0.2) == "低协同效应"
        assert self.synergy_analysis._classify_synergy_level(0.05) == "无显著协同效应"
    
    def test_extract_key_interactions(self):
        """测试关键交互项提取"""
        # 设置模拟数据
        self.synergy_analysis.synergy_effects = {
            'pairwise': {
                'feature1_x_feature2': {'improvement': 0.15, 'coefficient': 0.5}
            },
            'polynomial': {
                'top_interactions': [
                    ('feature1 feature2', {'coefficient': 0.3, 'importance': 0.4})
                ]
            }
        }
        
        key_interactions = self.synergy_analysis._extract_key_interactions()
        
        assert isinstance(key_interactions, list)
        if key_interactions:
            for interaction in key_interactions:
                assert 'type' in interaction
                assert 'name' in interaction
                assert 'improvement' in interaction or 'coefficient' in interaction
    
    def test_generate_recommendations(self):
        """测试建议生成"""
        # 设置不同评分水平的模拟数据
        self.synergy_analysis.synergy_effects = {'overall_score': 0.8}
        recommendations_high = self.synergy_analysis._generate_recommendations()
        
        self.synergy_analysis.synergy_effects = {'overall_score': 0.3}
        recommendations_low = self.synergy_analysis._generate_recommendations()
        
        assert isinstance(recommendations_high, list)
        assert isinstance(recommendations_low, list)
        assert len(recommendations_high) > 0
        assert len(recommendations_low) > 0
    
    def test_calculate_significance(self):
        """测试显著性计算"""
        feature_values = np.random.normal(0, 1, 100)
        y_values = np.random.normal(0, 1, 100)
        interaction_term = feature_values * y_values
        
        significance = self.synergy_analysis._calculate_significance(
            pd.DataFrame({'feature': feature_values}), 
            pd.Series(y_values), 
            pd.Series(interaction_term)
        )
        
        assert isinstance(significance, float)
        assert 0 <= significance <= 1
    
    def test_analyze_feature_combinations(self):
        """测试特征组合分析"""
        result = self.synergy_analysis._analyze_feature_combinations(self.X, self.y, Mock())
        
        assert isinstance(result, dict)
        if result:
            assert 'all_combinations' in result
            assert 'top_combinations' in result
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.synergy_analysis.detect_synergy_effects(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert result['overall_score'] == 0.0
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.synergy_analysis.detect_synergy_effects(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_high_correlation_data(self):
        """测试高相关性数据处理"""
        # 创建高相关性的数据
        high_corr_X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100)
        })
        high_corr_y = pd.Series(high_corr_X['feature1'] * high_corr_X['feature2'])
        
        result = self.synergy_analysis.detect_synergy_effects(high_corr_X, high_corr_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 高相关性数据应该检测到协同效应
        assert result['overall_score'] > 0
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 1000)
            for i in range(10)
        })
        large_y = pd.Series(np.random.normal(0, 1, 1000))
        
        result = self.synergy_analysis.detect_synergy_effects(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result

