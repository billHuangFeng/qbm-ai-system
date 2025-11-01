"""
高级关系识别测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.advanced_relationships import AdvancedRelationshipAnalysis

class TestAdvancedRelationshipAnalysis:
    """高级关系识别分析测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.relationship_analysis = AdvancedRelationshipAnalysis()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples),
            'feature4': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有复杂关系的目标变量
        self.y = pd.Series(
            self.X['feature1'] * self.X['feature2'] + 
            np.sin(self.X['feature3']) + 
            self.X['feature4']**2 + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_identify_advanced_relationships(self):
        """测试高级关系识别"""
        result = self.relationship_analysis.identify_advanced_relationships(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'ensemble' in result
        assert 'neural_network' in result
        assert 'feature_interactions' in result
        assert 'nonlinear' in result
        assert 'overall_score' in result
        
        # 检查整体评分
        assert 0 <= result['overall_score'] <= 1
    
    def test_analyze_ensemble_relationships(self):
        """测试集成模型关系分析"""
        result = self.relationship_analysis._analyze_ensemble_relationships(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        assert 'random_forest' in result
        assert 'xgboost' in result
        assert 'lightgbm' in result
        assert 'gradient_boosting' in result
        assert 'best_model' in result
        
        # 检查每个模型的结果
        for model_name in ['random_forest', 'xgboost', 'lightgbm', 'gradient_boosting']:
            if model_name in result:
                model_data = result[model_name]
                assert 'model' in model_data
                assert 'cv_scores' in model_data
                assert 'mean_cv_score' in model_data
                assert 'std_cv_score' in model_data
                assert 'feature_importance' in model_data
                assert 'r2_score' in model_data
    
    def test_analyze_neural_relationships(self):
        """测试神经网络关系分析"""
        result = self.relationship_analysis._analyze_neural_relationships(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        assert 'mlp_shallow' in result
        assert 'mlp_deep' in result
        assert 'mlp_wide' in result
        assert 'best_model' in result
        
        # 检查每个神经网络的结果
        for model_name in ['mlp_shallow', 'mlp_deep', 'mlp_wide']:
            if model_name in result:
                model_data = result[model_name]
                assert 'model' in model_data
                assert 'cv_scores' in model_data
                assert 'mean_cv_score' in model_data
                assert 'std_cv_score' in model_data
                assert 'r2_score' in model_data
                assert 'training_loss' in model_data
    
    def test_analyze_feature_interactions(self):
        """测试特征交互关系分析"""
        result = self.relationship_analysis._analyze_feature_interactions(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'pairwise' in result
        assert 'triple' in result
        assert 'combinations' in result
    
    def test_analyze_pairwise_interactions(self):
        """测试两两特征交互分析"""
        result = self.relationship_analysis._analyze_pairwise_interactions(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'all_interactions' in result
        assert 'top_interactions' in result
        
        if result['all_interactions']:
            for interaction_name, interaction_data in result['all_interactions'].items():
                assert 'correlation' in interaction_data
                assert 'improvement' in interaction_data
                assert 'r2_without' in interaction_data
                assert 'r2_with' in interaction_data
                assert 'coefficient' in interaction_data
                assert 'significance' in interaction_data
    
    def test_analyze_triple_interactions(self):
        """测试三特征交互分析"""
        result = self.relationship_analysis._analyze_triple_interactions(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'all_triple_interactions' in result
        assert 'top_triple_interactions' in result
        
        if result['all_triple_interactions']:
            for interaction_name, interaction_data in result['all_triple_interactions'].items():
                assert 'correlation' in interaction_data
                assert 'features' in interaction_data
                assert 'significance' in interaction_data
    
    def test_analyze_feature_combinations(self):
        """测试特征组合分析"""
        result = self.relationship_analysis._analyze_feature_combinations(self.X, self.y)
        
        assert isinstance(result, dict)
        
        if result:
            assert 'high_importance_features' in result
            assert 'feature_combinations' in result
            assert 'feature_importance' in result
    
    def test_analyze_nonlinear_relationships(self):
        """测试非线性关系分析"""
        result = self.relationship_analysis._analyze_nonlinear_relationships(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        assert 'polynomial_degree_2' in result
        assert 'log_transformations' in result
        assert 'exponential_transformations' in result
        
        # 检查多项式结果
        if 'polynomial_degree_2' in result:
            poly_data = result['polynomial_degree_2']
            assert 'model' in poly_data
            assert 'cv_scores' in poly_data
            assert 'mean_cv_score' in poly_data
            assert 'std_cv_score' in poly_data
            assert 'r2_score' in poly_data
            assert 'feature_names' in poly_data
    
    def test_analyze_log_transformations(self):
        """测试对数变换分析"""
        # 创建正数数据
        positive_X = pd.DataFrame({
            'feature1': np.abs(np.random.normal(1, 0.5, 100)),
            'feature2': np.abs(np.random.normal(1, 0.5, 100))
        })
        positive_y = pd.Series(np.random.normal(0, 1, 100))
        
        result = self.relationship_analysis._analyze_log_transformations(positive_X, positive_y, 5)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'cv_scores' in feature_data
                assert 'mean_cv_score' in feature_data
                assert 'std_cv_score' in feature_data
                assert 'r2_score' in feature_data
                assert 'original_r2' in feature_data
                assert 'improvement' in feature_data
    
    def test_analyze_exponential_transformations(self):
        """测试指数变换分析"""
        result = self.relationship_analysis._analyze_exponential_transformations(self.X, self.y, 5)
        
        assert isinstance(result, dict)
        
        if result:
            for feature, feature_data in result.items():
                assert 'cv_scores' in feature_data
                assert 'mean_cv_score' in feature_data
                assert 'std_cv_score' in feature_data
                assert 'r2_score' in feature_data
                assert 'original_r2' in feature_data
                assert 'improvement' in feature_data
    
    def test_calculate_relationship_score(self):
        """测试关系评分计算"""
        relationship_results = {
            'ensemble': {'model1': {'mean_cv_score': 0.7}},
            'neural_network': {'model1': {'mean_cv_score': 0.6}},
            'feature_interactions': {
                'pairwise': {'top_interactions': [('f1_x_f2', {'significance': 0.5})]},
                'triple': {'top_triple_interactions': [('f1_x_f2_x_f3', {'significance': 0.3})]}
            },
            'nonlinear': {'model1': {'mean_cv_score': 0.5}}
        }
        
        score = self.relationship_analysis._calculate_relationship_score(relationship_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_get_relationship_insights(self):
        """测试关系洞察获取"""
        # 先识别高级关系
        self.relationship_analysis.identify_advanced_relationships(self.X, self.y)
        
        insights = self.relationship_analysis.get_relationship_insights()
        
        assert isinstance(insights, dict)
        assert 'overall_relationship_score' in insights
        assert 'relationship_level' in insights
        assert 'key_relationships' in insights
        assert 'recommendations' in insights
        
        # 检查关系水平
        assert insights['relationship_level'] in ['高复杂度关系', '中等复杂度关系', '低复杂度关系', '简单线性关系']
    
    def test_classify_relationship_level(self):
        """测试关系水平分类"""
        assert self.relationship_analysis._classify_relationship_level(0.9) == "高复杂度关系"
        assert self.relationship_analysis._classify_relationship_level(0.7) == "中等复杂度关系"
        assert self.relationship_analysis._classify_relationship_level(0.4) == "低复杂度关系"
        assert self.relationship_analysis._classify_relationship_level(0.2) == "简单线性关系"
    
    def test_extract_key_relationships(self):
        """测试关键关系提取"""
        # 设置模拟数据
        self.relationship_analysis.relationship_insights = {
            'ensemble': {
                'random_forest': {'mean_cv_score': 0.8},
                'xgboost': {'mean_cv_score': 0.7}
            },
            'neural_network': {
                'mlp_deep': {'mean_cv_score': 0.75}
            },
            'feature_interactions': {
                'pairwise': {
                    'top_interactions': [
                        ('f1_x_f2', {'significance': 0.6})
                    ]
                }
            }
        }
        
        key_relationships = self.relationship_analysis._extract_key_relationships()
        
        assert isinstance(key_relationships, list)
        if key_relationships:
            for relationship in key_relationships:
                assert 'type' in relationship
                assert 'model' in relationship or 'interaction' in relationship
                assert 'score' in relationship or 'significance' in relationship
                assert 'importance' in relationship
    
    def test_generate_relationship_recommendations(self):
        """测试关系建议生成"""
        # 设置不同评分水平的模拟数据
        self.relationship_analysis.relationship_insights = {'overall_score': 0.9}
        recommendations_high = self.relationship_analysis._generate_relationship_recommendations()
        
        self.relationship_analysis.relationship_insights = {'overall_score': 0.3}
        recommendations_low = self.relationship_analysis._generate_relationship_recommendations()
        
        assert isinstance(recommendations_high, list)
        assert isinstance(recommendations_low, list)
        assert len(recommendations_high) > 0
        assert len(recommendations_low) > 0
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.relationship_analysis.identify_advanced_relationships(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert result['overall_score'] == 0.0
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.relationship_analysis.identify_advanced_relationships(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_clear_nonlinear_data(self):
        """测试明显非线性数据处理"""
        # 创建有明显非线性关系的数据
        nonlinear_X = pd.DataFrame({
            'feature1': np.linspace(-2, 2, 100),
            'feature2': np.linspace(-2, 2, 100)
        })
        nonlinear_y = pd.Series(
            nonlinear_X['feature1']**2 + 
            np.sin(nonlinear_X['feature2']) + 
            np.random.normal(0, 0.1, 100)
        )
        
        result = self.relationship_analysis.identify_advanced_relationships(nonlinear_X, nonlinear_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        # 明显非线性数据应该检测到复杂关系
        assert result['overall_score'] > 0
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 500)
            for i in range(8)
        })
        large_y = pd.Series(np.random.normal(0, 1, 500))
        
        result = self.relationship_analysis.identify_advanced_relationships(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_high_dimensional_data(self):
        """测试高维数据处理"""
        # 创建高维数据
        high_dim_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 100)
            for i in range(20)
        })
        high_dim_y = pd.Series(np.random.normal(0, 1, 100))
        
        result = self.relationship_analysis.identify_advanced_relationships(high_dim_X, high_dim_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_correlated_features(self):
        """测试相关特征处理"""
        # 创建相关特征
        base_feature = np.random.normal(0, 1, 100)
        correlated_X = pd.DataFrame({
            'feature1': base_feature,
            'feature2': base_feature + np.random.normal(0, 0.1, 100),
            'feature3': base_feature * 2 + np.random.normal(0, 0.1, 100)
        })
        correlated_y = pd.Series(np.random.normal(0, 1, 100))
        
        result = self.relationship_analysis.identify_advanced_relationships(correlated_X, correlated_y)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result



