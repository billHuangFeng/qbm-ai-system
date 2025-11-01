"""
数据预处理单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.data_preprocessing import DataPreprocessingService
from src.models.historical_data import HistoricalData

class TestDataPreprocessingService:
    """测试数据预处理服务"""
    
    def setup_method(self):
        """测试前设置"""
        self.service = DataPreprocessingService()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self):
        """创建样本数据"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
        data = []
        
        for i, date in enumerate(dates):
            data.append({
                'tenant_id': 'tenant_001',
                'data_id': f'data_{i}',
                'data_type': 'asset',
                'data_date': date,
                'period_type': 'monthly',
                'rd_asset': 1000 + i * 100 + np.random.normal(0, 50),
                'design_asset': 2000 + i * 150 + np.random.normal(0, 75),
                'production_asset': 3000 + i * 200 + np.random.normal(0, 100),
                'marketing_asset': 1500 + i * 80 + np.random.normal(0, 40),
                'delivery_asset': 1200 + i * 60 + np.random.normal(0, 30),
                'channel_asset': 800 + i * 40 + np.random.normal(0, 20),
                'rd_capability': 0.7 + i * 0.01 + np.random.normal(0, 0.05),
                'design_capability': 0.8 + i * 0.015 + np.random.normal(0, 0.08),
                'production_capability': 0.75 + i * 0.012 + np.random.normal(0, 0.06),
                'marketing_capability': 0.65 + i * 0.008 + np.random.normal(0, 0.04),
                'delivery_capability': 0.85 + i * 0.005 + np.random.normal(0, 0.03),
                'channel_capability': 0.70 + i * 0.010 + np.random.normal(0, 0.05)
            })
        
        return pd.DataFrame(data)
    
    def test_detect_outliers_iqr(self):
        """测试IQR异常值检测"""
        # 添加异常值
        test_data = self.sample_data.copy()
        test_data.loc[0, 'rd_asset'] = 50000  # 异常值
        
        outliers = self.service.detect_outliers_iqr(test_data, 'rd_asset')
        
        assert len(outliers) > 0
        assert 0 in outliers.index  # 异常值索引应该被检测到
    
    def test_detect_outliers_zscore(self):
        """测试Z-score异常值检测"""
        # 添加异常值
        test_data = self.sample_data.copy()
        test_data.loc[0, 'rd_asset'] = 50000  # 异常值
        
        outliers = self.service.detect_outliers_zscore(test_data, 'rd_asset', threshold=3)
        
        assert len(outliers) > 0
        assert 0 in outliers.index
    
    def test_handle_missing_values_mean(self):
        """测试均值填充缺失值"""
        test_data = self.sample_data.copy()
        test_data.loc[0:2, 'rd_asset'] = np.nan  # 创建缺失值
        
        filled_data = self.service.handle_missing_values(test_data, 'rd_asset', method='mean')
        
        assert not filled_data['rd_asset'].isna().any()
        assert filled_data['rd_asset'].iloc[0] == filled_data['rd_asset'].iloc[1]
    
    def test_handle_missing_values_median(self):
        """测试中位数填充缺失值"""
        test_data = self.sample_data.copy()
        test_data.loc[0:2, 'rd_asset'] = np.nan  # 创建缺失值
        
        filled_data = self.service.handle_missing_values(test_data, 'rd_asset', method='median')
        
        assert not filled_data['rd_asset'].isna().any()
    
    def test_handle_missing_values_forward_fill(self):
        """测试前向填充缺失值"""
        test_data = self.sample_data.copy()
        test_data.loc[1:3, 'rd_asset'] = np.nan  # 创建缺失值
        
        filled_data = self.service.handle_missing_values(test_data, 'rd_asset', method='forward_fill')
        
        assert not filled_data['rd_asset'].isna().any()
        assert filled_data['rd_asset'].iloc[1] == filled_data['rd_asset'].iloc[0]
    
    def test_standardize_data(self):
        """测试数据标准化"""
        test_data = self.sample_data.copy()
        
        standardized_data = self.service.standardize_data(test_data, ['rd_asset', 'design_asset'])
        
        # 检查标准化后的数据
        assert abs(standardized_data['rd_asset'].mean()) < 0.01  # 均值接近0
        assert abs(standardized_data['rd_asset'].std() - 1.0) < 0.01  # 标准差接近1
    
    def test_normalize_data(self):
        """测试数据归一化"""
        test_data = self.sample_data.copy()
        
        normalized_data = self.service.normalize_data(test_data, ['rd_asset', 'design_asset'])
        
        # 检查归一化后的数据
        assert normalized_data['rd_asset'].min() >= 0
        assert normalized_data['rd_asset'].max() <= 1
    
    def test_validate_data_quality(self):
        """测试数据质量验证"""
        test_data = self.sample_data.copy()
        
        quality_report = self.service.validate_data_quality(test_data)
        
        assert 'completeness' in quality_report
        assert 'consistency' in quality_report
        assert 'accuracy' in quality_report
        assert 'overall_score' in quality_report
        
        assert 0 <= quality_report['overall_score'] <= 1
    
    def test_preprocess_pipeline(self):
        """测试完整的数据预处理流水线"""
        test_data = self.sample_data.copy()
        
        # 添加一些缺失值和异常值
        test_data.loc[0, 'rd_asset'] = np.nan
        test_data.loc[1, 'design_asset'] = 50000  # 异常值
        
        preprocessed_data = self.service.preprocess_pipeline(
            test_data,
            target_columns=['rd_asset', 'design_asset', 'production_asset'],
            handle_outliers=True,
            handle_missing=True,
            standardize=True
        )
        
        assert not preprocessed_data.isna().any().any()
        assert len(preprocessed_data) > 0
    
    def test_feature_engineering(self):
        """测试特征工程"""
        test_data = self.sample_data.copy()
        
        engineered_data = self.service.feature_engineering(test_data)
        
        # 检查是否创建了新特征
        expected_features = ['rd_asset_trend', 'design_asset_trend', 'total_assets', 'asset_ratio']
        for feature in expected_features:
            assert feature in engineered_data.columns
    
    def test_data_validation_rules(self):
        """测试数据验证规则"""
        test_data = self.sample_data.copy()
        
        # 测试正数验证
        test_data.loc[0, 'rd_asset'] = -100  # 负数
        validation_result = self.service.validate_data_rules(test_data)
        
        assert not validation_result['is_valid']
        assert 'rd_asset' in validation_result['errors']
    
    def test_data_quality_scoring(self):
        """测试数据质量评分"""
        test_data = self.sample_data.copy()
        
        quality_score = self.service.calculate_data_quality_score(test_data)
        
        assert 0 <= quality_score <= 1
        assert isinstance(quality_score, float)
    
    def test_outlier_treatment_options(self):
        """测试异常值处理选项"""
        test_data = self.sample_data.copy()
        test_data.loc[0, 'rd_asset'] = 50000  # 异常值
        
        # 测试删除异常值
        cleaned_data = self.service.treat_outliers(test_data, 'rd_asset', method='remove')
        assert len(cleaned_data) < len(test_data)
        
        # 测试替换异常值
        replaced_data = self.service.treat_outliers(test_data, 'rd_asset', method='replace')
        assert len(replaced_data) == len(test_data)
        assert replaced_data.loc[0, 'rd_asset'] != 50000
    
    def test_data_transformation(self):
        """测试数据转换"""
        test_data = self.sample_data.copy()
        
        # 测试对数转换
        transformed_data = self.service.transform_data(test_data, 'rd_asset', method='log')
        assert 'rd_asset_log' in transformed_data.columns
        
        # 测试平方根转换
        transformed_data = self.service.transform_data(test_data, 'design_asset', method='sqrt')
        assert 'design_asset_sqrt' in transformed_data.columns
    
    def test_data_splitting(self):
        """测试数据分割"""
        test_data = self.sample_data.copy()
        
        train_data, test_data = self.service.split_data(test_data, test_size=0.2)
        
        assert len(train_data) + len(test_data) == len(self.sample_data)
        assert len(test_data) / len(self.sample_data) == pytest.approx(0.2, rel=0.1)
    
    def test_cross_validation_split(self):
        """测试交叉验证分割"""
        test_data = self.sample_data.copy()
        
        cv_splits = self.service.cross_validation_split(test_data, n_splits=5)
        
        assert len(cv_splits) == 5
        for train_idx, val_idx in cv_splits:
            assert len(train_idx) + len(val_idx) == len(test_data)
    
    def test_data_imputation_strategies(self):
        """测试数据插补策略"""
        test_data = self.sample_data.copy()
        test_data.loc[0:2, 'rd_asset'] = np.nan
        
        # 测试KNN插补
        knn_imputed = self.service.impute_missing_values(test_data, 'rd_asset', method='knn')
        assert not knn_imputed['rd_asset'].isna().any()
        
        # 测试迭代插补
        iterative_imputed = self.service.impute_missing_values(test_data, 'rd_asset', method='iterative')
        assert not iterative_imputed['rd_asset'].isna().any()
    
    def test_data_quality_metrics(self):
        """测试数据质量指标"""
        test_data = self.sample_data.copy()
        
        metrics = self.service.calculate_quality_metrics(test_data)
        
        assert 'completeness' in metrics
        assert 'consistency' in metrics
        assert 'accuracy' in metrics
        assert 'timeliness' in metrics
        
        for metric, value in metrics.items():
            assert 0 <= value <= 1



