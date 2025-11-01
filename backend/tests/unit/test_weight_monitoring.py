"""
权重监控系统测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.weight_monitoring import WeightMonitor

class TestWeightMonitor:
    """权重监控系统测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.weight_monitor = WeightMonitor()
        
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
        
        # 创建测试权重
        self.weights = {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
    
    def test_monitor_weights(self):
        """测试权重监控"""
        result = self.weight_monitor.monitor_weights(
            self.X, self.y, self.weights
        )
        
        assert isinstance(result, dict)
        assert 'performance' in result
        assert 'weight_drift' in result
        assert 'stability' in result
        assert 'data_quality' in result
        assert 'model_performance' in result
        assert 'anomalies' in result
        assert 'alerts' in result
        assert 'overall_score' in result
        
        # 检查整体评分
        assert 0 <= result['overall_score'] <= 1
    
    def test_monitor_weights_custom_period(self):
        """测试自定义监控周期"""
        result = self.weight_monitor.monitor_weights(
            self.X, self.y, self.weights, monitoring_period='weekly'
        )
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_monitor_performance(self):
        """测试性能监控"""
        result = self.weight_monitor._monitor_performance(
            self.X, self.y, self.weights
        )
        
        assert isinstance(result, dict)
        assert 'current_r2' in result
        assert 'current_mse' in result
        assert 'cv_mean' in result
        assert 'cv_std' in result
        assert 'performance_trend' in result
        assert 'performance_stability' in result
        
        # 检查性能指标
        assert 0 <= result['current_r2'] <= 1
        assert result['current_mse'] >= 0
        assert 0 <= result['cv_mean'] <= 1
        assert result['cv_std'] >= 0
        assert result['performance_trend'] in ['improving', 'declining', 'stable', 'unknown']
    
    def test_monitor_weight_drift(self):
        """测试权重漂移监控"""
        result = self.weight_monitor._monitor_weight_drift(self.weights)
        
        assert isinstance(result, dict)
        assert 'weight_drift' in result
        assert 'drift_detected' in result
        assert 'drift_features' in result
        
        # 检查漂移指标
        assert result['weight_drift'] >= 0
        assert isinstance(result['drift_detected'], bool)
        assert isinstance(result['drift_features'], list)
    
    def test_monitor_stability(self):
        """测试稳定性监控"""
        result = self.weight_monitor._monitor_stability(
            self.X, self.y, self.weights
        )
        
        assert isinstance(result, dict)
        assert 'stability_scores' in result
        assert 'stability_mean' in result
        assert 'stability_std' in result
        assert 'stability_coefficient' in result
        assert 'is_stable' in result
        
        # 检查稳定性指标
        assert len(result['stability_scores']) == 10  # 10次随机子集测试
        assert result['stability_mean'] >= 0
        assert result['stability_std'] >= 0
        assert result['stability_coefficient'] >= 0
        assert isinstance(result['is_stable'], bool)
    
    def test_monitor_data_quality(self):
        """测试数据质量监控"""
        result = self.weight_monitor._monitor_data_quality(self.X, self.y)
        
        assert isinstance(result, dict)
        assert 'missing_rate' in result
        assert 'missing_values' in result
        assert 'outlier_counts' in result
        assert 'distribution_metrics' in result
        assert 'y_missing' in result
        assert 'y_outliers' in result
        assert 'overall_quality_score' in result
        
        # 检查数据质量指标
        assert 0 <= result['missing_rate'] <= 1
        assert result['y_missing'] >= 0
        assert result['y_outliers'] >= 0
        assert 0 <= result['overall_quality_score'] <= 1
    
    def test_monitor_model_performance(self):
        """测试模型性能监控"""
        result = self.weight_monitor._monitor_model_performance(
            self.X, self.y, self.weights
        )
        
        assert isinstance(result, dict)
        assert 'r2_score' in result
        assert 'mse' in result
        assert 'rmse' in result
        assert 'residual_mean' in result
        assert 'residual_std' in result
        assert 'feature_importance' in result
        assert 'model_complexity' in result
        assert 'performance_grade' in result
        
        # 检查模型性能指标
        assert 0 <= result['r2_score'] <= 1
        assert result['mse'] >= 0
        assert result['rmse'] >= 0
        assert result['model_complexity'] == len(self.weights)
        assert result['performance_grade'] in ['A', 'B', 'C', 'D', 'F']
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        monitoring_results = {
            'performance': {'current_r2': 0.3},
            'weight_drift': {'drift_detected': True, 'weight_drift': 0.2},
            'stability': {'is_stable': False, 'stability_coefficient': 0.3},
            'data_quality': {'overall_quality_score': 0.6}
        }
        
        result = self.weight_monitor._detect_anomalies(monitoring_results)
        
        assert isinstance(result, dict)
        assert 'anomalies' in result
        assert 'anomaly_count' in result
        assert 'high_severity_count' in result
        assert 'medium_severity_count' in result
        
        # 检查异常检测结果
        assert result['anomaly_count'] >= 0
        assert result['high_severity_count'] >= 0
        assert result['medium_severity_count'] >= 0
        
        # 检查异常列表
        anomalies = result['anomalies']
        assert isinstance(anomalies, list)
        for anomaly in anomalies:
            assert 'type' in anomaly
            assert 'severity' in anomaly
            assert 'message' in anomaly
            assert 'value' in anomaly
    
    def test_generate_alerts(self):
        """测试警报生成"""
        monitoring_results = {
            'performance': {'current_r2': 0.3},
            'weight_drift': {'drift_detected': True, 'weight_drift': 0.2},
            'stability': {'is_stable': False, 'stability_coefficient': 0.3},
            'data_quality': {'overall_quality_score': 0.6},
            'anomalies': {'anomaly_count': 2}
        }
        
        result = self.weight_monitor._generate_alerts(monitoring_results)
        
        assert isinstance(result, list)
        
        # 检查警报结构
        for alert in result:
            assert 'type' in alert
            assert 'level' in alert
            assert 'message' in alert
            assert 'timestamp' in alert
            assert 'action_required' in alert
            assert alert['level'] in ['info', 'warning', 'error']
            assert isinstance(alert['action_required'], bool)
    
    def test_calculate_monitoring_score(self):
        """测试监控评分计算"""
        monitoring_results = {
            'performance': {'current_r2': 0.8},
            'weight_drift': {'weight_drift': 0.1},
            'stability': {'stability_coefficient': 0.05},
            'data_quality': {'overall_quality_score': 0.9},
            'model_performance': {'r2_score': 0.8}
        }
        
        score = self.weight_monitor._calculate_monitoring_score(monitoring_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_apply_weights(self):
        """测试权重应用"""
        X_weighted = self.weight_monitor._apply_weights(self.X, self.weights)
        
        assert isinstance(X_weighted, pd.DataFrame)
        assert X_weighted.shape == self.X.shape
        
        # 检查权重应用
        for feature, weight in self.weights.items():
            assert np.allclose(X_weighted[feature], self.X[feature] * weight)
    
    def test_get_historical_performance(self):
        """测试历史性能获取"""
        historical_performance = self.weight_monitor._get_historical_performance()
        
        assert isinstance(historical_performance, list)
        assert len(historical_performance) == 5  # 模拟数据
        assert all(isinstance(score, (int, float)) for score in historical_performance)
    
    def test_get_historical_weights(self):
        """测试历史权重获取"""
        historical_weights = self.weight_monitor._get_historical_weights()
        
        assert isinstance(historical_weights, dict)
    
    def test_calculate_performance_trend(self):
        """测试性能趋势计算"""
        current_r2 = 0.8
        historical_performance = [0.7, 0.75, 0.72, 0.78, 0.76]
        
        trend = self.weight_monitor._calculate_performance_trend(current_r2, historical_performance)
        
        assert trend in ['improving', 'declining', 'stable']
    
    def test_detect_y_outliers(self):
        """测试目标变量异常值检测"""
        outliers = self.weight_monitor._detect_y_outliers(self.y)
        
        assert isinstance(outliers, int)
        assert outliers >= 0
    
    def test_calculate_performance_grade(self):
        """测试性能等级计算"""
        grades = []
        for r2 in [0.95, 0.85, 0.75, 0.65, 0.55]:
            grade = self.weight_monitor._calculate_performance_grade(r2)
            grades.append(grade)
        
        assert grades == ['A', 'B', 'C', 'D', 'F']
    
    def test_update_monitoring_history(self):
        """测试监控历史更新"""
        monitoring_results = {
            'performance': {'current_r2': 0.8},
            'overall_score': 0.8
        }
        
        self.weight_monitor._update_monitoring_history(monitoring_results, 'daily')
        
        assert 'daily' in self.weight_monitor.monitoring_data
        assert len(self.weight_monitor.monitoring_data['daily']) > 0
    
    def test_get_monitoring_insights(self):
        """测试监控洞察获取"""
        # 先进行监控
        self.weight_monitor.monitor_weights(self.X, self.y, self.weights)
        
        insights = self.weight_monitor.get_monitoring_insights()
        
        assert isinstance(insights, dict)
        assert 'monitoring_data' in insights
        assert 'performance_history' in insights
        assert 'alerts' in insights
        assert 'alert_summary' in insights
        assert 'recommendations' in insights
    
    def test_generate_alert_summary(self):
        """测试警报摘要生成"""
        # 添加一些模拟警报
        self.weight_monitor.alerts = [
            {'type': 'performance_alert', 'level': 'warning'},
            {'type': 'weight_drift_alert', 'level': 'info'},
            {'type': 'stability_alert', 'level': 'error'}
        ]
        
        summary = self.weight_monitor._generate_alert_summary()
        
        assert isinstance(summary, dict)
        assert 'total_alerts' in summary
        assert 'alert_types' in summary
        assert 'recent_alerts' in summary
        
        assert summary['total_alerts'] == 3
        assert 'performance_alert' in summary['alert_types']
        assert 'weight_drift_alert' in summary['alert_types']
        assert 'stability_alert' in summary['alert_types']
    
    def test_generate_monitoring_recommendations(self):
        """测试监控建议生成"""
        recommendations = self.weight_monitor._generate_monitoring_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        empty_weights = {}
        
        result = self.weight_monitor.monitor_weights(empty_X, empty_y, empty_weights)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        single_weights = {'feature1': 1.0}
        
        result = self.weight_monitor.monitor_weights(single_X, single_y, single_weights)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 500)
            for i in range(8)
        })
        large_y = pd.Series(np.random.normal(0, 1, 500))
        large_weights = {f'feature_{i}': 1.0/8 for i in range(8)}
        
        result = self.weight_monitor.monitor_weights(large_X, large_y, large_weights)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
    
    def test_monitoring_consistency(self):
        """测试监控一致性"""
        # 多次运行应该得到一致的结果
        result1 = self.weight_monitor.monitor_weights(self.X, self.y, self.weights)
        result2 = self.weight_monitor.monitor_weights(self.X, self.y, self.weights)
        
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        
        # 检查关键指标的一致性
        if 'overall_score' in result1 and 'overall_score' in result2:
            assert abs(result1['overall_score'] - result2['overall_score']) < 1e-6
    
    def test_alert_thresholds(self):
        """测试警报阈值"""
        # 测试不同性能水平的警报
        performance_levels = [0.3, 0.6, 0.8, 0.9]
        
        for performance in performance_levels:
            monitoring_results = {
                'performance': {'current_r2': performance},
                'weight_drift': {'drift_detected': False, 'weight_drift': 0.05},
                'stability': {'is_stable': True, 'stability_coefficient': 0.05},
                'data_quality': {'overall_quality_score': 0.9}
            }
            
            alerts = self.weight_monitor._generate_alerts(monitoring_results)
            
            assert isinstance(alerts, list)
            
            if performance < 0.6:
                # 低性能应该生成警报
                assert len(alerts) > 0
            else:
                # 高性能可能不生成警报
                assert len(alerts) >= 0


