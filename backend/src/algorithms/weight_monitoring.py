"""
权重监控算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.signal import find_peaks
import logging
from ..logging_config import get_logger

logger = get_logger("weight_monitoring")

class WeightMonitoring:
    """权重监控算法"""
    
    def __init__(self):
        self.monitoring_data = {}
        self.alert_thresholds = {}
        self.monitoring_history = []
        self.performance_metrics = {}
        self.drift_detection = {}
    
    def monitor_weights(self, X: pd.DataFrame, y: pd.Series, 
                        weights: Dict[str, float],
                        monitoring_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """监控权重"""
        try:
            if monitoring_config is None:
                monitoring_config = {
                    'drift_threshold': 0.1,
                    'performance_threshold': 0.05,
                    'stability_window': 10,
                    'alert_enabled': True
                }
            
            results = {}
            
            # 1. 权重漂移检测
            drift_results = self._detect_weight_drift(weights, monitoring_config)
            results['weight_drift'] = drift_results
            
            # 2. 性能监控
            performance_results = self._monitor_performance(X, y, weights, monitoring_config)
            results['performance_monitoring'] = performance_results
            
            # 3. 稳定性监控
            stability_results = self._monitor_stability(weights, monitoring_config)
            results['stability_monitoring'] = stability_results
            
            # 4. 异常检测
            anomaly_results = self._detect_anomalies(weights, monitoring_config)
            results['anomaly_detection'] = anomaly_results
            
            # 5. 趋势分析
            trend_results = self._analyze_trends(weights, monitoring_config)
            results['trend_analysis'] = trend_results
            
            # 6. 生成警报
            if monitoring_config.get('alert_enabled', True):
                alerts = self._generate_alerts(results, monitoring_config)
                results['alerts'] = alerts
            
            # 7. 记录监控历史
            self.monitoring_history.append({
                'timestamp': pd.Timestamp.now(),
                'weights': weights,
                'config': monitoring_config,
                'results': results
            })
            
            self.monitoring_data = results
            logger.info("权重监控完成")
            
            return results
            
        except Exception as e:
            logger.error(f"权重监控失败: {e}")
            raise
    
    def _detect_weight_drift(self, current_weights: Dict[str, float], 
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """检测权重漂移"""
        try:
            drift_results = {}
            
            if not self.monitoring_history:
                # 首次监控，建立基线
                drift_results['status'] = 'baseline_established'
                drift_results['drift_detected'] = False
                drift_results['drift_score'] = 0.0
                return drift_results
            
            # 获取历史权重
            historical_weights = []
            for record in self.monitoring_history[-config.get('stability_window', 10):]:
                historical_weights.append(record['weights'])
            
            if not historical_weights:
                return drift_results
            
            # 计算权重漂移
            drift_scores = {}
            total_drift = 0.0
            
            for feature in current_weights.keys():
                current_weight = current_weights[feature]
                historical_weights_feature = [hw.get(feature, 0) for hw in historical_weights]
                
                if historical_weights_feature:
                    # 计算统计漂移
                    mean_historical = np.mean(historical_weights_feature)
                    std_historical = np.std(historical_weights_feature)
                    
                    if std_historical > 0:
                        # Z-score漂移
                        z_score = abs(current_weight - mean_historical) / std_historical
                        drift_scores[feature] = z_score
                        total_drift += z_score
                    else:
                        # 如果历史权重无变化，使用绝对差异
                        drift_scores[feature] = abs(current_weight - mean_historical)
                        total_drift += abs(current_weight - mean_historical)
            
            # 计算平均漂移分数
            avg_drift = total_drift / len(current_weights) if current_weights else 0
            
            # 判断是否检测到漂移
            drift_threshold = config.get('drift_threshold', 0.1)
            drift_detected = avg_drift > drift_threshold
            
            drift_results['status'] = 'drift_detected' if drift_detected else 'stable'
            drift_results['drift_detected'] = drift_detected
            drift_results['drift_score'] = avg_drift
            drift_results['feature_drift_scores'] = drift_scores
            drift_results['drift_threshold'] = drift_threshold
            
            # 识别最漂移的特征
            if drift_scores:
                max_drift_feature = max(drift_scores.keys(), key=lambda k: drift_scores[k])
                drift_results['max_drift_feature'] = {
                    'feature': max_drift_feature,
                    'drift_score': drift_scores[max_drift_feature],
                    'current_weight': current_weights[max_drift_feature]
                }
            
            logger.info(f"权重漂移检测完成，平均漂移分数: {avg_drift:.4f}")
            return drift_results
            
        except Exception as e:
            logger.error(f"权重漂移检测失败: {e}")
            return {}
    
    def _monitor_performance(self, X: pd.DataFrame, y: pd.Series, 
                           current_weights: Dict[str, float],
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """监控性能"""
        try:
            performance_results = {}
            
            # 计算当前性能
            weights_array = np.array([current_weights.get(feature, 0) for feature in X.columns])
            X_weighted = X * weights_array
            
            model = LinearRegression()
            model.fit(X_weighted, y)
            y_pred = model.predict(X_weighted)
            
            current_mse = mean_squared_error(y, y_pred)
            current_r2 = r2_score(y, y_pred)
            current_mae = mean_absolute_error(y, y_pred)
            
            performance_results['current_performance'] = {
                'mse': current_mse,
                'r2': current_r2,
                'mae': current_mae
            }
            
            # 与历史性能比较
            if self.monitoring_history:
                historical_performance = []
                for record in self.monitoring_history[-config.get('stability_window', 10):]:
                    if 'performance_monitoring' in record['results']:
                        perf = record['results']['performance_monitoring']['current_performance']
                        historical_performance.append(perf)
                
                if historical_performance:
                    # 计算性能变化
                    historical_mse = [p['mse'] for p in historical_performance]
                    historical_r2 = [p['r2'] for p in historical_performance]
                    historical_mae = [p['mae'] for p in historical_performance]
                    
                    mse_change = current_mse - np.mean(historical_mse)
                    r2_change = current_r2 - np.mean(historical_r2)
                    mae_change = current_mae - np.mean(historical_mae)
                    
                    performance_results['performance_change'] = {
                        'mse_change': mse_change,
                        'r2_change': r2_change,
                        'mae_change': mae_change,
                        'performance_degraded': mse_change > config.get('performance_threshold', 0.05)
                    }
                    
                    # 性能趋势
                    if len(historical_performance) > 1:
                        mse_trend = np.polyfit(range(len(historical_mse)), historical_mse, 1)[0]
                        r2_trend = np.polyfit(range(len(historical_r2)), historical_r2, 1)[0]
                        
                        performance_results['performance_trend'] = {
                            'mse_trend': mse_trend,
                            'r2_trend': r2_trend,
                            'trend_direction': 'improving' if r2_trend > 0 else 'declining'
                        }
            
            logger.info("性能监控完成")
            return performance_results
            
        except Exception as e:
            logger.error(f"性能监控失败: {e}")
            return {}
    
    def _monitor_stability(self, current_weights: Dict[str, float], 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """监控稳定性"""
        try:
            stability_results = {}
            
            if not self.monitoring_history:
                stability_results['status'] = 'insufficient_data'
                return stability_results
            
            # 获取历史权重
            historical_weights = []
            for record in self.monitoring_history[-config.get('stability_window', 10):]:
                historical_weights.append(record['weights'])
            
            if not historical_weights:
                stability_results['status'] = 'insufficient_data'
                return stability_results
            
            # 计算权重稳定性指标
            stability_metrics = {}
            overall_stability = 0.0
            
            for feature in current_weights.keys():
                feature_weights = [hw.get(feature, 0) for hw in historical_weights]
                
                if len(feature_weights) > 1:
                    # 计算变异系数
                    mean_weight = np.mean(feature_weights)
                    std_weight = np.std(feature_weights)
                    cv = std_weight / (mean_weight + 1e-8)
                    
                    # 计算权重范围
                    weight_range = np.max(feature_weights) - np.min(feature_weights)
                    
                    # 计算稳定性分数
                    stability_score = 1 - min(cv, 1.0)  # 限制在0-1范围内
                    
                    stability_metrics[feature] = {
                        'mean_weight': mean_weight,
                        'std_weight': std_weight,
                        'cv': cv,
                        'weight_range': weight_range,
                        'stability_score': stability_score
                    }
                    
                    overall_stability += stability_score
            
            # 计算平均稳定性
            avg_stability = overall_stability / len(current_weights) if current_weights else 0
            
            # 分类稳定性水平
            if avg_stability >= 0.8:
                stability_level = 'high'
            elif avg_stability >= 0.6:
                stability_level = 'medium'
            elif avg_stability >= 0.4:
                stability_level = 'low'
            else:
                stability_level = 'very_low'
            
            stability_results['overall_stability'] = avg_stability
            stability_results['stability_level'] = stability_level
            stability_results['feature_stability'] = stability_metrics
            
            # 识别最不稳定的特征
            if stability_metrics:
                min_stability_feature = min(stability_metrics.keys(), 
                                          key=lambda k: stability_metrics[k]['stability_score'])
                stability_results['least_stable_feature'] = {
                    'feature': min_stability_feature,
                    'stability_score': stability_metrics[min_stability_feature]['stability_score'],
                    'cv': stability_metrics[min_stability_feature]['cv']
                }
            
            logger.info(f"稳定性监控完成，平均稳定性: {avg_stability:.4f}")
            return stability_results
            
        except Exception as e:
            logger.error(f"稳定性监控失败: {e}")
            return {}
    
    def _detect_anomalies(self, current_weights: Dict[str, float], 
                         config: Dict[str, Any]) -> Dict[str, Any]:
        """检测异常"""
        try:
            anomaly_results = {}
            
            if not self.monitoring_history:
                anomaly_results['status'] = 'insufficient_data'
                return anomaly_results
            
            # 获取历史权重
            historical_weights = []
            for record in self.monitoring_history[-config.get('stability_window', 10):]:
                historical_weights.append(record['weights'])
            
            if not historical_weights:
                anomaly_results['status'] = 'insufficient_data'
                return anomaly_results
            
            # 检测异常权重
            anomalies = {}
            total_anomalies = 0
            
            for feature in current_weights.keys():
                current_weight = current_weights[feature]
                feature_weights = [hw.get(feature, 0) for hw in historical_weights]
                
                if len(feature_weights) > 2:
                    # 使用IQR方法检测异常
                    q1 = np.percentile(feature_weights, 25)
                    q3 = np.percentile(feature_weights, 75)
                    iqr = q3 - q1
                    
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    is_anomaly = current_weight < lower_bound or current_weight > upper_bound
                    
                    if is_anomaly:
                        anomalies[feature] = {
                            'current_weight': current_weight,
                            'lower_bound': lower_bound,
                            'upper_bound': upper_bound,
                            'anomaly_type': 'outlier',
                            'severity': 'high' if abs(current_weight - np.mean(feature_weights)) > 2 * np.std(feature_weights) else 'medium'
                        }
                        total_anomalies += 1
                    
                    # 使用Z-score检测异常
                    mean_weight = np.mean(feature_weights)
                    std_weight = np.std(feature_weights)
                    
                    if std_weight > 0:
                        z_score = abs(current_weight - mean_weight) / std_weight
                        
                        if z_score > 2.5:  # 2.5 sigma规则
                            if feature not in anomalies:
                                anomalies[feature] = {}
                            anomalies[feature]['z_score'] = z_score
                            anomalies[feature]['z_score_anomaly'] = True
            
            anomaly_results['anomalies_detected'] = total_anomalies > 0
            anomaly_results['total_anomalies'] = total_anomalies
            anomaly_results['anomaly_details'] = anomalies
            
            # 检测权重分布异常
            if len(historical_weights) > 5:
                distribution_anomaly = self._detect_distribution_anomaly(current_weights, historical_weights)
                anomaly_results['distribution_anomaly'] = distribution_anomaly
            
            logger.info(f"异常检测完成，发现 {total_anomalies} 个异常")
            return anomaly_results
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return {}
    
    def _detect_distribution_anomaly(self, current_weights: Dict[str, float], 
                                    historical_weights: List[Dict[str, float]]) -> Dict[str, Any]:
        """检测分布异常"""
        try:
            # 计算当前权重的分布特征
            current_values = list(current_weights.values())
            current_mean = np.mean(current_values)
            current_std = np.std(current_values)
            current_skewness = stats.skew(current_values)
            current_kurtosis = stats.kurtosis(current_values)
            
            # 计算历史权重的分布特征
            historical_values = []
            for hw in historical_weights:
                historical_values.extend(list(hw.values()))
            
            historical_mean = np.mean(historical_values)
            historical_std = np.std(historical_values)
            historical_skewness = stats.skew(historical_values)
            historical_kurtosis = stats.kurtosis(historical_values)
            
            # 比较分布特征
            mean_change = abs(current_mean - historical_mean) / (historical_std + 1e-8)
            std_change = abs(current_std - historical_std) / (historical_std + 1e-8)
            skewness_change = abs(current_skewness - historical_skewness)
            kurtosis_change = abs(current_kurtosis - historical_kurtosis)
            
            # 判断是否异常
            is_distribution_anomaly = (
                mean_change > 2 or 
                std_change > 2 or 
                skewness_change > 1 or 
                kurtosis_change > 1
            )
            
            return {
                'is_anomaly': is_distribution_anomaly,
                'current_distribution': {
                    'mean': current_mean,
                    'std': current_std,
                    'skewness': current_skewness,
                    'kurtosis': current_kurtosis
                },
                'historical_distribution': {
                    'mean': historical_mean,
                    'std': historical_std,
                    'skewness': historical_skewness,
                    'kurtosis': historical_kurtosis
                },
                'distribution_changes': {
                    'mean_change': mean_change,
                    'std_change': std_change,
                    'skewness_change': skewness_change,
                    'kurtosis_change': kurtosis_change
                }
            }
            
        except Exception as e:
            logger.error(f"分布异常检测失败: {e}")
            return {'is_anomaly': False}
    
    def _analyze_trends(self, current_weights: Dict[str, float], 
                       config: Dict[str, Any]) -> Dict[str, Any]:
        """分析趋势"""
        try:
            trend_results = {}
            
            if not self.monitoring_history or len(self.monitoring_history) < 3:
                trend_results['status'] = 'insufficient_data'
                return trend_results
            
            # 获取历史权重
            historical_weights = []
            for record in self.monitoring_history[-config.get('stability_window', 10):]:
                historical_weights.append(record['weights'])
            
            if len(historical_weights) < 3:
                trend_results['status'] = 'insufficient_data'
                return trend_results
            
            # 分析每个特征的趋势
            feature_trends = {}
            overall_trends = []
            
            for feature in current_weights.keys():
                feature_weights = [hw.get(feature, 0) for hw in historical_weights]
                
                if len(feature_weights) >= 3:
                    # 计算趋势斜率
                    x = np.arange(len(feature_weights))
                    slope, intercept = np.polyfit(x, feature_weights, 1)
                    
                    # 计算趋势强度
                    correlation = np.corrcoef(x, feature_weights)[0, 1]
                    trend_strength = abs(correlation)
                    
                    # 分类趋势
                    if slope > 0.01:
                        trend_direction = 'increasing'
                    elif slope < -0.01:
                        trend_direction = 'decreasing'
                    else:
                        trend_direction = 'stable'
                    
                    feature_trends[feature] = {
                        'slope': slope,
                        'intercept': intercept,
                        'correlation': correlation,
                        'trend_strength': trend_strength,
                        'trend_direction': trend_direction,
                        'current_weight': current_weights[feature]
                    }
                    
                    overall_trends.append(slope)
            
            # 计算整体趋势
            if overall_trends:
                avg_trend = np.mean(overall_trends)
                trend_volatility = np.std(overall_trends)
                
                if avg_trend > 0.01:
                    overall_direction = 'increasing'
                elif avg_trend < -0.01:
                    overall_direction = 'decreasing'
                else:
                    overall_direction = 'stable'
                
                trend_results['overall_trend'] = {
                    'average_slope': avg_trend,
                    'trend_volatility': trend_volatility,
                    'trend_direction': overall_direction
                }
            
            trend_results['feature_trends'] = feature_trends
            
            # 识别显著趋势
            significant_trends = []
            for feature, trend_data in feature_trends.items():
                if trend_data['trend_strength'] > 0.7:  # 强趋势
                    significant_trends.append({
                        'feature': feature,
                        'trend_direction': trend_data['trend_direction'],
                        'trend_strength': trend_data['trend_strength'],
                        'slope': trend_data['slope']
                    })
            
            trend_results['significant_trends'] = significant_trends
            
            logger.info(f"趋势分析完成，发现 {len(significant_trends)} 个显著趋势")
            return trend_results
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {}
    
    def _generate_alerts(self, monitoring_results: Dict[str, Any], 
                        config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成警报"""
        try:
            alerts = []
            
            # 权重漂移警报
            if 'weight_drift' in monitoring_results:
                drift_data = monitoring_results['weight_drift']
                if drift_data.get('drift_detected', False):
                    alerts.append({
                        'type': 'weight_drift',
                        'severity': 'high' if drift_data['drift_score'] > 0.2 else 'medium',
                        'message': f"检测到权重漂移，平均漂移分数: {drift_data['drift_score']:.4f}",
                        'details': drift_data
                    })
            
            # 性能下降警报
            if 'performance_monitoring' in monitoring_results:
                perf_data = monitoring_results['performance_monitoring']
                if 'performance_change' in perf_data:
                    perf_change = perf_data['performance_change']
                    if perf_change.get('performance_degraded', False):
                        alerts.append({
                            'type': 'performance_degradation',
                            'severity': 'high',
                            'message': f"检测到性能下降，MSE变化: {perf_change['mse_change']:.4f}",
                            'details': perf_change
                        })
            
            # 稳定性警报
            if 'stability_monitoring' in monitoring_results:
                stability_data = monitoring_results['stability_monitoring']
                if stability_data.get('stability_level') in ['low', 'very_low']:
                    alerts.append({
                        'type': 'low_stability',
                        'severity': 'medium',
                        'message': f"权重稳定性较低: {stability_data['stability_level']}",
                        'details': stability_data
                    })
            
            # 异常警报
            if 'anomaly_detection' in monitoring_results:
                anomaly_data = monitoring_results['anomaly_detection']
                if anomaly_data.get('anomalies_detected', False):
                    alerts.append({
                        'type': 'anomaly_detected',
                        'severity': 'high',
                        'message': f"检测到 {anomaly_data['total_anomalies']} 个异常权重",
                        'details': anomaly_data
                    })
            
            # 趋势警报
            if 'trend_analysis' in monitoring_results:
                trend_data = monitoring_results['trend_analysis']
                if 'significant_trends' in trend_data:
                    significant_trends = trend_data['significant_trends']
                    if len(significant_trends) > 0:
                        alerts.append({
                            'type': 'significant_trend',
                            'severity': 'low',
                            'message': f"检测到 {len(significant_trends)} 个显著趋势",
                            'details': significant_trends
                        })
            
            logger.info(f"生成 {len(alerts)} 个警报")
            return alerts
            
        except Exception as e:
            logger.error(f"警报生成失败: {e}")
            return []
    
    def get_monitoring_insights(self) -> Dict[str, Any]:
        """获取监控洞察"""
        try:
            insights = {
                'monitoring_summary': self._summarize_monitoring_results(),
                'performance_analysis': self._analyze_monitoring_performance(),
                'alert_analysis': self._analyze_alerts(),
                'recommendations': self._generate_monitoring_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"监控洞察获取失败: {e}")
            return {}
    
    def _summarize_monitoring_results(self) -> Dict[str, Any]:
        """总结监控结果"""
        try:
            summary = {
                'total_monitoring_sessions': len(self.monitoring_history),
                'average_drift_score': 0,
                'average_stability': 0,
                'total_alerts': 0,
                'monitoring_period': None
            }
            
            if self.monitoring_history:
                # 计算平均漂移分数
                drift_scores = []
                stability_scores = []
                alert_counts = []
                
                for record in self.monitoring_history:
                    if 'weight_drift' in record['results']:
                        drift_score = record['results']['weight_drift'].get('drift_score', 0)
                        drift_scores.append(drift_score)
                    
                    if 'stability_monitoring' in record['results']:
                        stability = record['results']['stability_monitoring'].get('overall_stability', 0)
                        stability_scores.append(stability)
                    
                    if 'alerts' in record['results']:
                        alert_count = len(record['results']['alerts'])
                        alert_counts.append(alert_count)
                
                if drift_scores:
                    summary['average_drift_score'] = np.mean(drift_scores)
                
                if stability_scores:
                    summary['average_stability'] = np.mean(stability_scores)
                
                if alert_counts:
                    summary['total_alerts'] = sum(alert_counts)
                
                # 监控时间段
                if len(self.monitoring_history) > 1:
                    start_time = self.monitoring_history[0]['timestamp']
                    end_time = self.monitoring_history[-1]['timestamp']
                    summary['monitoring_period'] = {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat(),
                        'duration_days': (end_time - start_time).days
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"监控结果总结失败: {e}")
            return {}
    
    def _analyze_monitoring_performance(self) -> Dict[str, Any]:
        """分析监控性能"""
        try:
            performance_analysis = {}
            
            if self.monitoring_history:
                # 分析性能趋势
                performance_scores = []
                for record in self.monitoring_history:
                    if 'performance_monitoring' in record['results']:
                        perf = record['results']['performance_monitoring']['current_performance']
                        performance_scores.append(perf['r2'])
                
                if len(performance_scores) > 1:
                    performance_trend = np.polyfit(range(len(performance_scores)), performance_scores, 1)[0]
                    performance_analysis['performance_trend'] = {
                        'slope': performance_trend,
                        'direction': 'improving' if performance_trend > 0 else 'declining',
                        'trend_strength': abs(performance_trend)
                    }
                
                # 分析性能稳定性
                if performance_scores:
                    performance_analysis['performance_stability'] = {
                        'mean_r2': np.mean(performance_scores),
                        'std_r2': np.std(performance_scores),
                        'cv_r2': np.std(performance_scores) / (np.mean(performance_scores) + 1e-8),
                        'min_r2': np.min(performance_scores),
                        'max_r2': np.max(performance_scores)
                    }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"监控性能分析失败: {e}")
            return {}
    
    def _analyze_alerts(self) -> Dict[str, Any]:
        """分析警报"""
        try:
            alert_analysis = {}
            
            if self.monitoring_history:
                # 统计警报类型
                alert_types = {}
                alert_severities = {}
                
                for record in self.monitoring_history:
                    if 'alerts' in record['results']:
                        for alert in record['results']['alerts']:
                            alert_type = alert['type']
                            alert_severity = alert['severity']
                            
                            if alert_type not in alert_types:
                                alert_types[alert_type] = 0
                            alert_types[alert_type] += 1
                            
                            if alert_severity not in alert_severities:
                                alert_severities[alert_severity] = 0
                            alert_severities[alert_severity] += 1
                
                alert_analysis['alert_types'] = alert_types
                alert_analysis['alert_severities'] = alert_severities
                
                # 计算警报频率
                total_sessions = len(self.monitoring_history)
                total_alerts = sum(alert_types.values()) if alert_types else 0
                alert_analysis['alert_frequency'] = total_alerts / total_sessions if total_sessions > 0 else 0
            
            return alert_analysis
            
        except Exception as e:
            logger.error(f"警报分析失败: {e}")
            return {}
    
    def _generate_monitoring_recommendations(self) -> List[str]:
        """生成监控建议"""
        try:
            recommendations = []
            
            if self.monitoring_history:
                # 基于平均漂移分数生成建议
                drift_scores = []
                for record in self.monitoring_history:
                    if 'weight_drift' in record['results']:
                        drift_score = record['results']['weight_drift'].get('drift_score', 0)
                        drift_scores.append(drift_score)
                
                if drift_scores:
                    avg_drift = np.mean(drift_scores)
                    if avg_drift > 0.2:
                        recommendations.append("平均漂移分数较高，建议增加监控频率")
                        recommendations.append("考虑使用更稳定的权重优化方法")
                    elif avg_drift > 0.1:
                        recommendations.append("检测到中等程度的权重漂移，建议定期重新优化")
                
                # 基于稳定性生成建议
                stability_scores = []
                for record in self.monitoring_history:
                    if 'stability_monitoring' in record['results']:
                        stability = record['results']['stability_monitoring'].get('overall_stability', 0)
                        stability_scores.append(stability)
                
                if stability_scores:
                    avg_stability = np.mean(stability_scores)
                    if avg_stability < 0.4:
                        recommendations.append("权重稳定性较低，建议使用正则化方法")
                        recommendations.append("考虑使用集成方法提高稳定性")
                
                # 基于警报频率生成建议
                alert_counts = []
                for record in self.monitoring_history:
                    if 'alerts' in record['results']:
                        alert_count = len(record['results']['alerts'])
                        alert_counts.append(alert_count)
                
                if alert_counts:
                    avg_alerts = np.mean(alert_counts)
                    if avg_alerts > 2:
                        recommendations.append("警报频率较高，建议检查数据质量和模型假设")
                    elif avg_alerts > 1:
                        recommendations.append("检测到一些警报，建议调整监控阈值")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"监控建议生成失败: {e}")
            return []
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """生成监控报告"""
        try:
            report = {
                'summary': {
                    'monitoring_timestamp': pd.Timestamp.now().isoformat(),
                    'total_monitoring_sessions': len(self.monitoring_history),
                    'current_monitoring_status': self.monitoring_data.get('weight_drift', {}).get('status', 'unknown')
                },
                'current_monitoring': self.monitoring_data,
                'insights': self.get_monitoring_insights(),
                'monitoring_history': self.monitoring_history
            }
            
            return report
            
        except Exception as e:
            logger.error(f"监控报告生成失败: {e}")
            return {}