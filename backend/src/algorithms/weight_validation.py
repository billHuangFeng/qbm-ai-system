"""
权重验证机制
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from scipy import stats
import logging
from ..logging_config import get_logger

logger = get_logger("weight_validation")

class WeightValidator:
    """权重验证器"""
    
    def __init__(self):
        self.validation_results = {}
        self.validation_history = {}
        self.performance_metrics = {}
    
    def validate_weights(self, X: pd.DataFrame, y: pd.Series, 
                        weights: Dict[str, float],
                        validation_methods: List[str] = None) -> Dict[str, Any]:
        """验证权重"""
        try:
            if validation_methods is None:
                validation_methods = ['cross_validation', 'bootstrap', 'time_series', 'stability']
            
            validation_results = {}
            
            # 1. 交叉验证
            if 'cross_validation' in validation_methods:
                cv_results = self._cross_validation_test(X, y, weights)
                validation_results['cross_validation'] = cv_results
            
            # 2. 自助法验证
            if 'bootstrap' in validation_methods:
                bootstrap_results = self._bootstrap_validation(X, y, weights)
                validation_results['bootstrap'] = bootstrap_results
            
            # 3. 时间序列验证
            if 'time_series' in validation_methods:
                ts_results = self._time_series_validation(X, y, weights)
                validation_results['time_series'] = ts_results
            
            # 4. 稳定性验证
            if 'stability' in validation_methods:
                stability_results = self._stability_validation(X, y, weights)
                validation_results['stability'] = stability_results
            
            # 5. 敏感性分析
            sensitivity_results = self._sensitivity_analysis(X, y, weights)
            validation_results['sensitivity'] = sensitivity_results
            
            # 6. 鲁棒性测试
            robustness_results = self._robustness_test(X, y, weights)
            validation_results['robustness'] = robustness_results
            
            # 7. 统计显著性测试
            significance_results = self._statistical_significance_test(X, y, weights)
            validation_results['significance'] = significance_results
            
            # 8. 综合验证评分
            overall_score = self._calculate_validation_score(validation_results)
            validation_results['overall_score'] = overall_score
            
            self.validation_results = validation_results
            logger.info(f"权重验证完成，综合评分: {overall_score:.4f}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"权重验证失败: {e}")
            raise
    
    def _cross_validation_test(self, X: pd.DataFrame, y: pd.Series, 
                             weights: Dict[str, float]) -> Dict[str, Any]:
        """交叉验证测试"""
        try:
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            
            # 原始模型交叉验证
            model_original = LinearRegression()
            cv_scores_original = cross_val_score(model_original, X, y, cv=5, scoring='r2')
            
            # 加权模型交叉验证
            model_weighted = LinearRegression()
            cv_scores_weighted = cross_val_score(model_weighted, X_weighted, y, cv=5, scoring='r2')
            
            # 计算改进
            improvement = np.mean(cv_scores_weighted) - np.mean(cv_scores_original)
            improvement_std = np.std(cv_scores_weighted - cv_scores_original)
            
            # 统计显著性测试
            t_stat, p_value = stats.ttest_rel(cv_scores_weighted, cv_scores_original)
            
            return {
                'original_scores': cv_scores_original.tolist(),
                'weighted_scores': cv_scores_weighted.tolist(),
                'original_mean': np.mean(cv_scores_original),
                'weighted_mean': np.mean(cv_scores_weighted),
                'improvement': improvement,
                'improvement_std': improvement_std,
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            
        except Exception as e:
            logger.error(f"交叉验证测试失败: {e}")
            return {}
    
    def _bootstrap_validation(self, X: pd.DataFrame, y: pd.Series, 
                            weights: Dict[str, float], n_bootstrap: int = 100) -> Dict[str, Any]:
        """自助法验证"""
        try:
            bootstrap_scores = []
            bootstrap_improvements = []
            
            for i in range(n_bootstrap):
                # 自助采样
                indices = np.random.choice(len(X), size=len(X), replace=True)
                X_bootstrap = X.iloc[indices]
                y_bootstrap = y.iloc[indices]
                
                # 原始模型
                model_original = LinearRegression()
                model_original.fit(X_bootstrap, y_bootstrap)
                score_original = model_original.score(X_bootstrap, y_bootstrap)
                
                # 加权模型
                X_weighted = self._apply_weights(X_bootstrap, weights)
                model_weighted = LinearRegression()
                model_weighted.fit(X_weighted, y_bootstrap)
                score_weighted = model_weighted.score(X_weighted, y_bootstrap)
                
                bootstrap_scores.append(score_weighted)
                bootstrap_improvements.append(score_weighted - score_original)
            
            # 计算置信区间
            confidence_interval = np.percentile(bootstrap_improvements, [2.5, 97.5])
            
            return {
                'bootstrap_scores': bootstrap_scores,
                'bootstrap_improvements': bootstrap_improvements,
                'mean_improvement': np.mean(bootstrap_improvements),
                'std_improvement': np.std(bootstrap_improvements),
                'confidence_interval': confidence_interval.tolist(),
                'positive_improvement_rate': np.mean(np.array(bootstrap_improvements) > 0)
            }
            
        except Exception as e:
            logger.error(f"自助法验证失败: {e}")
            return {}
    
    def _time_series_validation(self, X: pd.DataFrame, y: pd.Series, 
                               weights: Dict[str, float]) -> Dict[str, Any]:
        """时间序列验证"""
        try:
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            
            # 时间序列交叉验证
            tscv = TimeSeriesSplit(n_splits=5)
            
            original_scores = []
            weighted_scores = []
            
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # 原始模型
                model_original = LinearRegression()
                model_original.fit(X_train, y_train)
                score_original = model_original.score(X_test, y_test)
                original_scores.append(score_original)
                
                # 加权模型
                X_train_weighted = self._apply_weights(X_train, weights)
                X_test_weighted = self._apply_weights(X_test, weights)
                model_weighted = LinearRegression()
                model_weighted.fit(X_train_weighted, y_train)
                score_weighted = model_weighted.score(X_test_weighted, y_test)
                weighted_scores.append(score_weighted)
            
            # 计算时间序列性能
            improvement = np.mean(weighted_scores) - np.mean(original_scores)
            
            return {
                'original_scores': original_scores,
                'weighted_scores': weighted_scores,
                'original_mean': np.mean(original_scores),
                'weighted_mean': np.mean(weighted_scores),
                'improvement': improvement,
                'time_series_consistency': np.std(weighted_scores)
            }
            
        except Exception as e:
            logger.error(f"时间序列验证失败: {e}")
            return {}
    
    def _stability_validation(self, X: pd.DataFrame, y: pd.Series, 
                            weights: Dict[str, float]) -> Dict[str, Any]:
        """稳定性验证"""
        try:
            # 添加噪声测试稳定性
            noise_levels = [0.01, 0.05, 0.1, 0.2]
            stability_results = {}
            
            for noise_level in noise_levels:
                # 添加噪声
                X_noisy = X + np.random.normal(0, noise_level, X.shape)
                y_noisy = y + np.random.normal(0, noise_level, len(y))
                
                # 原始模型
                model_original = LinearRegression()
                model_original.fit(X_noisy, y_noisy)
                score_original = model_original.score(X_noisy, y_noisy)
                
                # 加权模型
                X_weighted = self._apply_weights(X_noisy, weights)
                model_weighted = LinearRegression()
                model_weighted.fit(X_weighted, y_noisy)
                score_weighted = model_weighted.score(X_weighted, y_noisy)
                
                stability_results[f'noise_{noise_level}'] = {
                    'original_score': score_original,
                    'weighted_score': score_weighted,
                    'improvement': score_weighted - score_original
                }
            
            # 计算稳定性指标
            improvements = [result['improvement'] for result in stability_results.values()]
            stability_score = 1 - np.std(improvements) / (np.mean(improvements) + 1e-8)
            
            return {
                'stability_results': stability_results,
                'stability_score': stability_score,
                'improvement_consistency': np.std(improvements),
                'mean_improvement': np.mean(improvements)
            }
            
        except Exception as e:
            logger.error(f"稳定性验证失败: {e}")
            return {}
    
    def _sensitivity_analysis(self, X: pd.DataFrame, y: pd.Series, 
                            weights: Dict[str, float]) -> Dict[str, Any]:
        """敏感性分析"""
        try:
            sensitivity_results = {}
            
            for feature, weight in weights.items():
                # 测试权重变化对性能的影响
                weight_changes = [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]
                performance_changes = []
                
                for change in weight_changes:
                    modified_weights = weights.copy()
                    modified_weights[feature] = weight * change
                    
                    # 归一化权重
                    total_weight = sum(modified_weights.values())
                    modified_weights = {k: v/total_weight for k, v in modified_weights.items()}
                    
                    # 测试性能
                    X_weighted = self._apply_weights(X, modified_weights)
                    model = LinearRegression()
                    model.fit(X_weighted, y)
                    score = model.score(X_weighted, y)
                    
                    performance_changes.append(score)
                
                # 计算敏感性
                sensitivity = np.std(performance_changes) / np.mean(performance_changes)
                sensitivity_results[feature] = {
                    'sensitivity': sensitivity,
                    'performance_changes': performance_changes,
                    'weight_changes': weight_changes
                }
            
            return {
                'feature_sensitivity': sensitivity_results,
                'overall_sensitivity': np.mean([result['sensitivity'] for result in sensitivity_results.values()]),
                'most_sensitive_feature': max(sensitivity_results.keys(), 
                                            key=lambda k: sensitivity_results[k]['sensitivity'])
            }
            
        except Exception as e:
            logger.error(f"敏感性分析失败: {e}")
            return {}
    
    def _robustness_test(self, X: pd.DataFrame, y: pd.Series, 
                       weights: Dict[str, float]) -> Dict[str, Any]:
        """鲁棒性测试"""
        try:
            # 测试不同数据子集的性能
            robustness_results = {}
            
            # 随机子集测试
            subset_sizes = [0.5, 0.7, 0.9]
            for size in subset_sizes:
                n_samples = int(len(X) * size)
                indices = np.random.choice(len(X), size=n_samples, replace=False)
                
                X_subset = X.iloc[indices]
                y_subset = y.iloc[indices]
                
                # 原始模型
                model_original = LinearRegression()
                model_original.fit(X_subset, y_subset)
                score_original = model_original.score(X_subset, y_subset)
                
                # 加权模型
                X_weighted = self._apply_weights(X_subset, weights)
                model_weighted = LinearRegression()
                model_weighted.fit(X_weighted, y_subset)
                score_weighted = model_weighted.score(X_weighted, y_subset)
                
                robustness_results[f'subset_{size}'] = {
                    'original_score': score_original,
                    'weighted_score': score_weighted,
                    'improvement': score_weighted - score_original
                }
            
            # 计算鲁棒性指标
            improvements = [result['improvement'] for result in robustness_results.values()]
            robustness_score = np.mean(improvements) / (np.std(improvements) + 1e-8)
            
            return {
                'robustness_results': robustness_results,
                'robustness_score': robustness_score,
                'improvement_consistency': np.std(improvements),
                'mean_improvement': np.mean(improvements)
            }
            
        except Exception as e:
            logger.error(f"鲁棒性测试失败: {e}")
            return {}
    
    def _statistical_significance_test(self, X: pd.DataFrame, y: pd.Series, 
                                     weights: Dict[str, float]) -> Dict[str, Any]:
        """统计显著性测试"""
        try:
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            
            # 原始模型
            model_original = LinearRegression()
            model_original.fit(X, y)
            y_pred_original = model_original.predict(X)
            residuals_original = y - y_pred_original
            
            # 加权模型
            model_weighted = LinearRegression()
            model_weighted.fit(X_weighted, y)
            y_pred_weighted = model_weighted.predict(X_weighted)
            residuals_weighted = y - y_pred_weighted
            
            # F检验（比较残差方差）
            f_stat, f_p_value = stats.f_oneway(residuals_original, residuals_weighted)
            
            # t检验（比较R²）
            r2_original = model_original.score(X, y)
            r2_weighted = model_weighted.score(X_weighted, y)
            
            # 计算R²的置信区间
            n = len(y)
            r2_original_ci = self._calculate_r2_confidence_interval(r2_original, n)
            r2_weighted_ci = self._calculate_r2_confidence_interval(r2_weighted, n)
            
            return {
                'f_statistic': f_stat,
                'f_p_value': f_p_value,
                'r2_original': r2_original,
                'r2_weighted': r2_weighted,
                'r2_improvement': r2_weighted - r2_original,
                'r2_original_ci': r2_original_ci,
                'r2_weighted_ci': r2_weighted_ci,
                'significant_improvement': f_p_value < 0.05
            }
            
        except Exception as e:
            logger.error(f"统计显著性测试失败: {e}")
            return {}
    
    def _calculate_r2_confidence_interval(self, r2: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
        """计算R²的置信区间"""
        try:
            # 使用Fisher Z变换
            z = 0.5 * np.log((1 + r2) / (1 - r2))
            se = 1 / np.sqrt(n - 3)
            
            alpha = 1 - confidence
            z_critical = stats.norm.ppf(1 - alpha/2)
            
            z_lower = z - z_critical * se
            z_upper = z + z_critical * se
            
            # 逆Fisher Z变换
            r2_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
            r2_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
            
            return (r2_lower, r2_upper)
            
        except Exception as e:
            logger.error(f"R²置信区间计算失败: {e}")
            return (0, 1)
    
    def _apply_weights(self, X: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """应用权重到特征"""
        X_weighted = X.copy()
        for feature, weight in weights.items():
            if feature in X_weighted.columns:
                X_weighted[feature] = X_weighted[feature] * weight
        return X_weighted
    
    def _calculate_validation_score(self, validation_results: Dict[str, Any]) -> float:
        """计算综合验证评分"""
        try:
            score = 0.0
            weights = {
                'cross_validation': 0.25,
                'bootstrap': 0.20,
                'time_series': 0.20,
                'stability': 0.15,
                'sensitivity': 0.10,
                'robustness': 0.10
            }
            
            # 交叉验证评分
            if 'cross_validation' in validation_results:
                cv_data = validation_results['cross_validation']
                if cv_data and 'improvement' in cv_data:
                    score += weights['cross_validation'] * max(0, cv_data['improvement'])
            
            # 自助法评分
            if 'bootstrap' in validation_results:
                bootstrap_data = validation_results['bootstrap']
                if bootstrap_data and 'positive_improvement_rate' in bootstrap_data:
                    score += weights['bootstrap'] * bootstrap_data['positive_improvement_rate']
            
            # 时间序列评分
            if 'time_series' in validation_results:
                ts_data = validation_results['time_series']
                if ts_data and 'improvement' in ts_data:
                    score += weights['time_series'] * max(0, ts_data['improvement'])
            
            # 稳定性评分
            if 'stability' in validation_results:
                stability_data = validation_results['stability']
                if stability_data and 'stability_score' in stability_data:
                    score += weights['stability'] * max(0, stability_data['stability_score'])
            
            # 敏感性评分（越低越好）
            if 'sensitivity' in validation_results:
                sensitivity_data = validation_results['sensitivity']
                if sensitivity_data and 'overall_sensitivity' in sensitivity_data:
                    sensitivity_score = 1 - min(1, sensitivity_data['overall_sensitivity'])
                    score += weights['sensitivity'] * sensitivity_score
            
            # 鲁棒性评分
            if 'robustness' in validation_results:
                robustness_data = validation_results['robustness']
                if robustness_data and 'robustness_score' in robustness_data:
                    score += weights['robustness'] * max(0, robustness_data['robustness_score'])
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"验证评分计算失败: {e}")
            return 0.0
    
    def get_validation_insights(self) -> Dict[str, Any]:
        """获取验证洞察"""
        try:
            insights = {
                'validation_results': self.validation_results,
                'validation_history': self.validation_history,
                'performance_metrics': self.performance_metrics,
                'recommendations': self._generate_validation_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"验证洞察获取失败: {e}")
            return {}
    
    def _generate_validation_recommendations(self) -> List[str]:
        """生成验证建议"""
        try:
            recommendations = []
            
            if self.validation_results:
                overall_score = self.validation_results.get('overall_score', 0)
                
                if overall_score >= 0.8:
                    recommendations.append("权重验证结果优秀，建议采用当前权重配置")
                    recommendations.append("建议定期监控权重性能，确保长期稳定性")
                elif overall_score >= 0.6:
                    recommendations.append("权重验证结果良好，建议进一步优化")
                    recommendations.append("考虑调整权重配置以提高性能")
                elif overall_score >= 0.4:
                    recommendations.append("权重验证结果一般，建议重新评估权重策略")
                    recommendations.append("考虑使用不同的权重计算方法")
                else:
                    recommendations.append("权重验证结果较差，建议重新设计权重策略")
                    recommendations.append("考虑使用更简单的模型或特征选择")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"验证建议生成失败: {e}")
            return []

