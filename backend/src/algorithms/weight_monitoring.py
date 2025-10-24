"""
权重监控系统
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import logging
from ..logging_config import get_logger

logger = get_logger("weight_monitoring")

class WeightMonitor:
    """权重监控系统"""
    
    def __init__(self):
        self.monitoring_data = {}
        self.performance_history = {}
        self.alert_thresholds = {
            'performance_degradation': 0.05,
            'weight_drift': 0.1,
            'stability_threshold': 0.8
        }
        self.alerts = []
    
    def monitor_weights(self, X: pd.DataFrame, y: pd.Series, 
                       weights: Dict[str, float],
                       monitoring_period: str = 'daily') -> Dict[str, Any]:
        """监控权重"""
        try:
            monitoring_results = {}
            
            # 1. 性能监控
            performance_monitoring = self._monitor_performance(X, y, weights)
            monitoring_results['performance'] = performance_monitoring
            
            # 2. 权重漂移监控
            weight_drift_monitoring = self._monitor_weight_drift(weights)
            monitoring_results['weight_drift'] = weight_drift_monitoring
            
            # 3. 稳定性监控
            stability_monitoring = self._monitor_stability(X, y, weights)
            monitoring_results['stability'] = stability_monitoring
            
            # 4. 数据质量监控
            data_quality_monitoring = self._monitor_data_quality(X, y)
            monitoring_results['data_quality'] = data_quality_monitoring
            
            # 5. 模型性能监控
            model_performance_monitoring = self._monitor_model_performance(X, y, weights)
            monitoring_results['model_performance'] = model_performance_monitoring
            
            # 6. 异常检测
            anomaly_detection = self._detect_anomalies(monitoring_results)
            monitoring_results['anomalies'] = anomaly_detection
            
            # 7. 生成警报
            alerts = self._generate_alerts(monitoring_results)
            monitoring_results['alerts'] = alerts
            
            # 8. 综合监控评分
            overall_score = self._calculate_monitoring_score(monitoring_results)
            monitoring_results['overall_score'] = overall_score
            
            # 更新监控历史
            self._update_monitoring_history(monitoring_results, monitoring_period)
            
            logger.info(f"权重监控完成，综合评分: {overall_score:.4f}")
            return monitoring_results
            
        except Exception as e:
            logger.error(f"权重监控失败: {e}")
            raise
    
    def _monitor_performance(self, X: pd.DataFrame, y: pd.Series, 
                           weights: Dict[str, float]) -> Dict[str, Any]:
        """监控性能"""
        try:
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            
            # 当前性能
            model = LinearRegression()
            model.fit(X_weighted, y)
            current_r2 = model.score(X_weighted, y)
            current_mse = mean_squared_error(y, model.predict(X_weighted))
            
            # 交叉验证性能
            cv_scores = cross_val_score(model, X_weighted, y, cv=5, scoring='r2')
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            
            # 与历史性能比较
            historical_performance = self._get_historical_performance()
            performance_trend = self._calculate_performance_trend(current_r2, historical_performance)
            
            return {
                'current_r2': current_r2,
                'current_mse': current_mse,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'performance_trend': performance_trend,
                'performance_stability': 1 - cv_std / (cv_mean + 1e-8)
            }
            
        except Exception as e:
            logger.error(f"性能监控失败: {e}")
            return {}
    
    def _monitor_weight_drift(self, current_weights: Dict[str, float]) -> Dict[str, Any]:
        """监控权重漂移"""
        try:
            # 获取历史权重
            historical_weights = self._get_historical_weights()
            
            if not historical_weights:
                return {
                    'weight_drift': 0.0,
                    'drift_detected': False,
                    'drift_features': []
                }
            
            # 计算权重漂移
            weight_drifts = {}
            drift_features = []
            
            for feature in current_weights.keys():
                if feature in historical_weights:
                    current_weight = current_weights[feature]
                    historical_weight = historical_weights[feature]
                    
                    # 计算相对漂移
                    if historical_weight > 0:
                        drift = abs(current_weight - historical_weight) / historical_weight
                        weight_drifts[feature] = drift
                        
                        if drift > self.alert_thresholds['weight_drift']:
                            drift_features.append(feature)
            
            # 计算总体漂移
            overall_drift = np.mean(list(weight_drifts.values())) if weight_drifts else 0.0
            
            return {
                'weight_drift': overall_drift,
                'drift_detected': overall_drift > self.alert_thresholds['weight_drift'],
                'drift_features': drift_features,
                'feature_drifts': weight_drifts
            }
            
        except Exception as e:
            logger.error(f"权重漂移监控失败: {e}")
            return {}
    
    def _monitor_stability(self, X: pd.DataFrame, y: pd.Series, 
                          weights: Dict[str, float]) -> Dict[str, Any]:
        """监控稳定性"""
        try:
            # 测试不同数据子集的稳定性
            stability_scores = []
            
            # 随机子集测试
            for i in range(10):
                # 随机选择80%的数据
                n_samples = int(len(X) * 0.8)
                indices = np.random.choice(len(X), size=n_samples, replace=False)
                
                X_subset = X.iloc[indices]
                y_subset = y.iloc[indices]
                
                # 应用权重
                X_weighted = self._apply_weights(X_subset, weights)
                
                # 训练模型
                model = LinearRegression()
                model.fit(X_weighted, y_subset)
                score = model.score(X_weighted, y_subset)
                
                stability_scores.append(score)
            
            # 计算稳定性指标
            stability_mean = np.mean(stability_scores)
            stability_std = np.std(stability_scores)
            stability_coefficient = stability_std / (stability_mean + 1e-8)
            
            return {
                'stability_scores': stability_scores,
                'stability_mean': stability_mean,
                'stability_std': stability_std,
                'stability_coefficient': stability_coefficient,
                'is_stable': stability_coefficient < 0.1
            }
            
        except Exception as e:
            logger.error(f"稳定性监控失败: {e}")
            return {}
    
    def _monitor_data_quality(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """监控数据质量"""
        try:
            data_quality_metrics = {}
            
            # 缺失值检查
            missing_values = X.isnull().sum()
            missing_rate = missing_values.sum() / (X.shape[0] * X.shape[1])
            
            # 异常值检查
            outlier_counts = {}
            for feature in X.columns:
                if X[feature].dtype in ['int64', 'float64']:
                    Q1 = X[feature].quantile(0.25)
                    Q3 = X[feature].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = ((X[feature] < lower_bound) | (X[feature] > upper_bound)).sum()
                    outlier_counts[feature] = outliers
            
            # 数据分布检查
            distribution_metrics = {}
            for feature in X.columns:
                if X[feature].dtype in ['int64', 'float64']:
                    skewness = X[feature].skew()
                    kurtosis = X[feature].kurtosis()
                    distribution_metrics[feature] = {
                        'skewness': skewness,
                        'kurtosis': kurtosis
                    }
            
            # 目标变量质量
            y_missing = y.isnull().sum()
            y_outliers = self._detect_y_outliers(y)
            
            return {
                'missing_rate': missing_rate,
                'missing_values': missing_values.to_dict(),
                'outlier_counts': outlier_counts,
                'distribution_metrics': distribution_metrics,
                'y_missing': y_missing,
                'y_outliers': y_outliers,
                'overall_quality_score': 1 - missing_rate - np.mean(list(outlier_counts.values())) / len(X)
            }
            
        except Exception as e:
            logger.error(f"数据质量监控失败: {e}")
            return {}
    
    def _monitor_model_performance(self, X: pd.DataFrame, y: pd.Series, 
                                 weights: Dict[str, float]) -> Dict[str, Any]:
        """监控模型性能"""
        try:
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            
            # 训练模型
            model = LinearRegression()
            model.fit(X_weighted, y)
            
            # 性能指标
            y_pred = model.predict(X_weighted)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            
            # 残差分析
            residuals = y - y_pred
            residual_mean = np.mean(residuals)
            residual_std = np.std(residuals)
            
            # 特征重要性（基于权重）
            feature_importance = {feature: weight for feature, weight in weights.items()}
            
            # 模型复杂度
            model_complexity = len(weights)
            
            return {
                'r2_score': r2,
                'mse': mse,
                'rmse': rmse,
                'residual_mean': residual_mean,
                'residual_std': residual_std,
                'feature_importance': feature_importance,
                'model_complexity': model_complexity,
                'performance_grade': self._calculate_performance_grade(r2)
            }
            
        except Exception as e:
            logger.error(f"模型性能监控失败: {e}")
            return {}
    
    def _detect_anomalies(self, monitoring_results: Dict[str, Any]) -> Dict[str, Any]:
        """检测异常"""
        try:
            anomalies = []
            
            # 性能异常检测
            if 'performance' in monitoring_results:
                performance_data = monitoring_results['performance']
                if performance_data.get('current_r2', 0) < 0.5:
                    anomalies.append({
                        'type': 'performance_anomaly',
                        'severity': 'high',
                        'message': '模型性能严重下降',
                        'value': performance_data.get('current_r2', 0)
                    })
            
            # 权重漂移异常检测
            if 'weight_drift' in monitoring_results:
                drift_data = monitoring_results['weight_drift']
                if drift_data.get('drift_detected', False):
                    anomalies.append({
                        'type': 'weight_drift_anomaly',
                        'severity': 'medium',
                        'message': '检测到权重漂移',
                        'value': drift_data.get('weight_drift', 0)
                    })
            
            # 稳定性异常检测
            if 'stability' in monitoring_results:
                stability_data = monitoring_results['stability']
                if not stability_data.get('is_stable', True):
                    anomalies.append({
                        'type': 'stability_anomaly',
                        'severity': 'medium',
                        'message': '模型稳定性不足',
                        'value': stability_data.get('stability_coefficient', 0)
                    })
            
            # 数据质量异常检测
            if 'data_quality' in monitoring_results:
                quality_data = monitoring_results['data_quality']
                if quality_data.get('overall_quality_score', 1) < 0.8:
                    anomalies.append({
                        'type': 'data_quality_anomaly',
                        'severity': 'high',
                        'message': '数据质量下降',
                        'value': quality_data.get('overall_quality_score', 1)
                    })
            
            return {
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'high_severity_count': len([a for a in anomalies if a['severity'] == 'high']),
                'medium_severity_count': len([a for a in anomalies if a['severity'] == 'medium'])
            }
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return {}
    
    def _generate_alerts(self, monitoring_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成警报"""
        try:
            alerts = []
            
            # 性能警报
            if 'performance' in monitoring_results:
                performance_data = monitoring_results['performance']
                if performance_data.get('current_r2', 0) < 0.6:
                    alerts.append({
                        'type': 'performance_alert',
                        'level': 'warning',
                        'message': f"模型性能下降: R² = {performance_data.get('current_r2', 0):.4f}",
                        'timestamp': datetime.now().isoformat(),
                        'action_required': True
                    })
            
            # 权重漂移警报
            if 'weight_drift' in monitoring_results:
                drift_data = monitoring_results['weight_drift']
                if drift_data.get('drift_detected', False):
                    alerts.append({
                        'type': 'weight_drift_alert',
                        'level': 'info',
                        'message': f"检测到权重漂移: {drift_data.get('weight_drift', 0):.4f}",
                        'timestamp': datetime.now().isoformat(),
                        'action_required': False
                    })
            
            # 稳定性警报
            if 'stability' in monitoring_results:
                stability_data = monitoring_results['stability']
                if not stability_data.get('is_stable', True):
                    alerts.append({
                        'type': 'stability_alert',
                        'level': 'warning',
                        'message': f"模型稳定性不足: {stability_data.get('stability_coefficient', 0):.4f}",
                        'timestamp': datetime.now().isoformat(),
                        'action_required': True
                    })
            
            # 数据质量警报
            if 'data_quality' in monitoring_results:
                quality_data = monitoring_results['data_quality']
                if quality_data.get('overall_quality_score', 1) < 0.8:
                    alerts.append({
                        'type': 'data_quality_alert',
                        'level': 'error',
                        'message': f"数据质量下降: {quality_data.get('overall_quality_score', 1):.4f}",
                        'timestamp': datetime.now().isoformat(),
                        'action_required': True
                    })
            
            # 异常警报
            if 'anomalies' in monitoring_results:
                anomaly_data = monitoring_results['anomalies']
                if anomaly_data.get('anomaly_count', 0) > 0:
                    alerts.append({
                        'type': 'anomaly_alert',
                        'level': 'error',
                        'message': f"检测到 {anomaly_data.get('anomaly_count', 0)} 个异常",
                        'timestamp': datetime.now().isoformat(),
                        'action_required': True
                    })
            
            # 更新警报历史
            self.alerts.extend(alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"警报生成失败: {e}")
            return []
    
    def _calculate_monitoring_score(self, monitoring_results: Dict[str, Any]) -> float:
        """计算综合监控评分"""
        try:
            score = 0.0
            weights = {
                'performance': 0.3,
                'weight_drift': 0.2,
                'stability': 0.2,
                'data_quality': 0.2,
                'model_performance': 0.1
            }
            
            # 性能评分
            if 'performance' in monitoring_results:
                performance_data = monitoring_results['performance']
                r2_score = performance_data.get('current_r2', 0)
                score += weights['performance'] * r2_score
            
            # 权重漂移评分（漂移越小越好）
            if 'weight_drift' in monitoring_results:
                drift_data = monitoring_results['weight_drift']
                drift_score = 1 - min(1, drift_data.get('weight_drift', 0))
                score += weights['weight_drift'] * drift_score
            
            # 稳定性评分
            if 'stability' in monitoring_results:
                stability_data = monitoring_results['stability']
                stability_score = 1 - min(1, stability_data.get('stability_coefficient', 0))
                score += weights['stability'] * stability_score
            
            # 数据质量评分
            if 'data_quality' in monitoring_results:
                quality_data = monitoring_results['data_quality']
                quality_score = quality_data.get('overall_quality_score', 1)
                score += weights['data_quality'] * quality_score
            
            # 模型性能评分
            if 'model_performance' in monitoring_results:
                model_data = monitoring_results['model_performance']
                model_score = model_data.get('r2_score', 0)
                score += weights['model_performance'] * model_score
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"监控评分计算失败: {e}")
            return 0.0
    
    def _apply_weights(self, X: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """应用权重到特征"""
        X_weighted = X.copy()
        for feature, weight in weights.items():
            if feature in X_weighted.columns:
                X_weighted[feature] = X_weighted[feature] * weight
        return X_weighted
    
    def _get_historical_performance(self) -> List[float]:
        """获取历史性能数据"""
        # 这里应该从数据库或文件系统获取历史性能数据
        # 为了演示，返回模拟数据
        return [0.8, 0.82, 0.79, 0.81, 0.83]
    
    def _get_historical_weights(self) -> Dict[str, float]:
        """获取历史权重数据"""
        # 这里应该从数据库或文件系统获取历史权重数据
        # 为了演示，返回模拟数据
        return {}
    
    def _calculate_performance_trend(self, current_r2: float, historical_performance: List[float]) -> str:
        """计算性能趋势"""
        if not historical_performance:
            return 'unknown'
        
        recent_avg = np.mean(historical_performance[-3:]) if len(historical_performance) >= 3 else np.mean(historical_performance)
        
        if current_r2 > recent_avg + 0.02:
            return 'improving'
        elif current_r2 < recent_avg - 0.02:
            return 'declining'
        else:
            return 'stable'
    
    def _detect_y_outliers(self, y: pd.Series) -> int:
        """检测目标变量异常值"""
        Q1 = y.quantile(0.25)
        Q3 = y.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((y < lower_bound) | (y > upper_bound)).sum()
        return outliers
    
    def _calculate_performance_grade(self, r2: float) -> str:
        """计算性能等级"""
        if r2 >= 0.9:
            return 'A'
        elif r2 >= 0.8:
            return 'B'
        elif r2 >= 0.7:
            return 'C'
        elif r2 >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _update_monitoring_history(self, monitoring_results: Dict[str, Any], period: str):
        """更新监控历史"""
        timestamp = datetime.now().isoformat()
        
        if period not in self.monitoring_data:
            self.monitoring_data[period] = []
        
        self.monitoring_data[period].append({
            'timestamp': timestamp,
            'results': monitoring_results
        })
        
        # 保持最近30天的数据
        cutoff_date = datetime.now() - timedelta(days=30)
        self.monitoring_data[period] = [
            entry for entry in self.monitoring_data[period]
            if datetime.fromisoformat(entry['timestamp']) > cutoff_date
        ]
    
    def get_monitoring_insights(self) -> Dict[str, Any]:
        """获取监控洞察"""
        try:
            insights = {
                'monitoring_data': self.monitoring_data,
                'performance_history': self.performance_history,
                'alerts': self.alerts,
                'alert_summary': self._generate_alert_summary(),
                'recommendations': self._generate_monitoring_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"监控洞察获取失败: {e}")
            return {}
    
    def _generate_alert_summary(self) -> Dict[str, Any]:
        """生成警报摘要"""
        try:
            if not self.alerts:
                return {'total_alerts': 0, 'alert_types': {}}
            
            alert_types = {}
            for alert in self.alerts:
                alert_type = alert['type']
                if alert_type not in alert_types:
                    alert_types[alert_type] = 0
                alert_types[alert_type] += 1
            
            return {
                'total_alerts': len(self.alerts),
                'alert_types': alert_types,
                'recent_alerts': self.alerts[-10:]  # 最近10个警报
            }
            
        except Exception as e:
            logger.error(f"警报摘要生成失败: {e}")
            return {}
    
    def _generate_monitoring_recommendations(self) -> List[str]:
        """生成监控建议"""
        try:
            recommendations = []
            
            if self.alerts:
                high_priority_alerts = [alert for alert in self.alerts if alert['level'] == 'error']
                if high_priority_alerts:
                    recommendations.append("检测到高优先级警报，建议立即处理")
                
                warning_alerts = [alert for alert in self.alerts if alert['level'] == 'warning']
                if warning_alerts:
                    recommendations.append("检测到警告级别警报，建议关注并处理")
            
            recommendations.append("建议定期检查监控数据，确保系统稳定运行")
            recommendations.append("建议设置自动化的权重更新机制")
            recommendations.append("建议建立性能基准，便于异常检测")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"监控建议生成失败: {e}")
            return []

