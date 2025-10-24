"""
动态权重计算算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize
from scipy.stats import pearsonr
import logging
from ..logging_config import get_logger

logger = get_logger("dynamic_weights")

class DynamicWeightCalculator:
    """动态权重计算器"""
    
    def __init__(self):
        self.weight_history = {}
        self.optimization_results = {}
        self.weight_models = {}
    
    def calculate_dynamic_weights(self, X: pd.DataFrame, y: pd.Series, 
                                method: str = 'correlation', 
                                update_frequency: str = 'monthly') -> Dict[str, Any]:
        """计算动态权重"""
        try:
            weight_results = {}
            
            # 1. 基于相关性的权重计算
            if method == 'correlation':
                correlation_weights = self._calculate_correlation_weights(X, y)
                weight_results['correlation'] = correlation_weights
            
            # 2. 基于重要性的权重计算
            elif method == 'importance':
                importance_weights = self._calculate_importance_weights(X, y)
                weight_results['importance'] = importance_weights
            
            # 3. 基于回归系数的权重计算
            elif method == 'regression':
                regression_weights = self._calculate_regression_weights(X, y)
                weight_results['regression'] = regression_weights
            
            # 4. 基于时间序列的权重计算
            elif method == 'time_series':
                time_series_weights = self._calculate_time_series_weights(X, y)
                weight_results['time_series'] = time_series_weights
            
            # 5. 综合权重计算
            elif method == 'comprehensive':
                comprehensive_weights = self._calculate_comprehensive_weights(X, y)
                weight_results['comprehensive'] = comprehensive_weights
            
            # 6. 权重归一化
            normalized_weights = self._normalize_weights(weight_results)
            weight_results['normalized'] = normalized_weights
            
            # 7. 权重稳定性分析
            stability_analysis = self._analyze_weight_stability(weight_results)
            weight_results['stability'] = stability_analysis
            
            # 8. 权重有效性验证
            effectiveness = self._validate_weight_effectiveness(X, y, normalized_weights)
            weight_results['effectiveness'] = effectiveness
            
            self.weight_history[update_frequency] = weight_results
            logger.info(f"动态权重计算完成: {method}, 更新频率: {update_frequency}")
            
            return weight_results
            
        except Exception as e:
            logger.error(f"动态权重计算失败: {e}")
            raise
    
    def _calculate_correlation_weights(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """基于相关性计算权重"""
        try:
            correlation_weights = {}
            
            for feature in X.columns:
                # 计算特征与目标变量的相关系数
                correlation, p_value = pearsonr(X[feature], y)
                
                # 使用相关系数的绝对值作为权重
                weight = abs(correlation)
                
                # 考虑显著性
                if p_value < 0.05:  # 显著相关
                    weight *= 1.2
                elif p_value < 0.1:  # 边际显著
                    weight *= 1.1
                
                correlation_weights[feature] = weight
            
            logger.info(f"相关性权重计算完成: {len(correlation_weights)} 个特征")
            return correlation_weights
            
        except Exception as e:
            logger.error(f"相关性权重计算失败: {e}")
            return {}
    
    def _calculate_importance_weights(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """基于重要性计算权重"""
        try:
            # 使用随机森林计算特征重要性
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            importance_weights = dict(zip(X.columns, rf.feature_importances_))
            
            logger.info(f"重要性权重计算完成: {len(importance_weights)} 个特征")
            return importance_weights
            
        except Exception as e:
            logger.error(f"重要性权重计算失败: {e}")
            return {}
    
    def _calculate_regression_weights(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """基于回归系数计算权重"""
        try:
            # 训练线性回归模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 使用回归系数的绝对值作为权重
            regression_weights = dict(zip(X.columns, np.abs(model.coef_)))
            
            logger.info(f"回归系数权重计算完成: {len(regression_weights)} 个特征")
            return regression_weights
            
        except Exception as e:
            logger.error(f"回归系数权重计算失败: {e}")
            return {}
    
    def _calculate_time_series_weights(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """基于时间序列计算权重"""
        try:
            time_series_weights = {}
            
            for feature in X.columns:
                # 计算特征与目标变量的时间序列相关性
                feature_values = X[feature].values
                y_values = y.values
                
                # 计算不同滞后的相关性
                max_lag = min(10, len(feature_values) // 4)
                correlations = []
                
                for lag in range(max_lag + 1):
                    if len(feature_values) > lag:
                        lagged_feature = feature_values[:-lag] if lag > 0 else feature_values
                        corresponding_y = y_values[lag:] if lag > 0 else y_values
                        
                        if len(lagged_feature) > 10:
                            correlation = np.corrcoef(lagged_feature, corresponding_y)[0, 1]
                            if not np.isnan(correlation):
                                correlations.append(abs(correlation))
                
                # 使用最大相关性作为权重
                if correlations:
                    weight = max(correlations)
                else:
                    weight = 0.0
                
                time_series_weights[feature] = weight
            
            logger.info(f"时间序列权重计算完成: {len(time_series_weights)} 个特征")
            return time_series_weights
            
        except Exception as e:
            logger.error(f"时间序列权重计算失败: {e}")
            return {}
    
    def _calculate_comprehensive_weights(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """综合权重计算"""
        try:
            # 计算各种权重
            correlation_weights = self._calculate_correlation_weights(X, y)
            importance_weights = self._calculate_importance_weights(X, y)
            regression_weights = self._calculate_regression_weights(X, y)
            time_series_weights = self._calculate_time_series_weights(X, y)
            
            # 综合权重（加权平均）
            comprehensive_weights = {}
            weights = {
                'correlation': 0.3,
                'importance': 0.3,
                'regression': 0.2,
                'time_series': 0.2
            }
            
            for feature in X.columns:
                comprehensive_weight = (
                    correlation_weights.get(feature, 0) * weights['correlation'] +
                    importance_weights.get(feature, 0) * weights['importance'] +
                    regression_weights.get(feature, 0) * weights['regression'] +
                    time_series_weights.get(feature, 0) * weights['time_series']
                )
                comprehensive_weights[feature] = comprehensive_weight
            
            logger.info(f"综合权重计算完成: {len(comprehensive_weights)} 个特征")
            return comprehensive_weights
            
        except Exception as e:
            logger.error(f"综合权重计算失败: {e}")
            return {}
    
    def _normalize_weights(self, weight_results: Dict[str, Any]) -> Dict[str, float]:
        """权重归一化"""
        try:
            normalized_weights = {}
            
            # 获取所有权重方法的结果
            all_weights = {}
            for method, weights in weight_results.items():
                if isinstance(weights, dict):
                    all_weights[method] = weights
            
            if not all_weights:
                return {}
            
            # 对每种方法的结果进行归一化
            for method, weights in all_weights.items():
                if weights:
                    # 计算权重总和
                    total_weight = sum(weights.values())
                    
                    if total_weight > 0:
                        # 归一化权重
                        normalized_method_weights = {
                            feature: weight / total_weight
                            for feature, weight in weights.items()
                        }
                        normalized_weights[method] = normalized_method_weights
            
            # 计算综合归一化权重
            if len(normalized_weights) > 1:
                # 使用所有方法的平均权重
                feature_names = list(normalized_weights[list(normalized_weights.keys())[0]].keys())
                final_weights = {}
                
                for feature in feature_names:
                    avg_weight = np.mean([
                        normalized_weights[method].get(feature, 0)
                        for method in normalized_weights.keys()
                    ])
                    final_weights[feature] = avg_weight
                
                # 最终归一化
                total_final_weight = sum(final_weights.values())
                if total_final_weight > 0:
                    final_weights = {
                        feature: weight / total_final_weight
                        for feature, weight in final_weights.items()
                    }
                
                normalized_weights['final'] = final_weights
            
            logger.info(f"权重归一化完成: {len(normalized_weights)} 种方法")
            return normalized_weights
            
        except Exception as e:
            logger.error(f"权重归一化失败: {e}")
            return {}
    
    def _analyze_weight_stability(self, weight_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析权重稳定性"""
        try:
            stability_analysis = {}
            
            # 获取归一化权重
            normalized_weights = weight_results.get('normalized', {})
            
            if not normalized_weights:
                return stability_analysis
            
            # 分析每种方法的权重分布
            for method, weights in normalized_weights.items():
                if isinstance(weights, dict) and weights:
                    weight_values = list(weights.values())
                    
                    stability_analysis[method] = {
                        'mean_weight': np.mean(weight_values),
                        'std_weight': np.std(weight_values),
                        'max_weight': np.max(weight_values),
                        'min_weight': np.min(weight_values),
                        'weight_range': np.max(weight_values) - np.min(weight_values),
                        'coefficient_of_variation': np.std(weight_values) / np.mean(weight_values) if np.mean(weight_values) > 0 else 0
                    }
            
            # 分析权重一致性
            if len(normalized_weights) > 1:
                methods = list(normalized_weights.keys())
                consistency_scores = {}
                
                for i, method1 in enumerate(methods):
                    for method2 in methods[i+1:]:
                        weights1 = normalized_weights[method1]
                        weights2 = normalized_weights[method2]
                        
                        # 计算权重相关性
                        common_features = set(weights1.keys()) & set(weights2.keys())
                        if common_features:
                            weights1_values = [weights1[f] for f in common_features]
                            weights2_values = [weights2[f] for f in common_features]
                            
                            correlation = np.corrcoef(weights1_values, weights2_values)[0, 1]
                            consistency_scores[f"{method1}_vs_{method2}"] = correlation
                
                stability_analysis['consistency'] = consistency_scores
            
            logger.info(f"权重稳定性分析完成")
            return stability_analysis
            
        except Exception as e:
            logger.error(f"权重稳定性分析失败: {e}")
            return {}
    
    def _validate_weight_effectiveness(self, X: pd.DataFrame, y: pd.Series, 
                                     normalized_weights: Dict[str, Any]) -> Dict[str, Any]:
        """验证权重有效性"""
        try:
            effectiveness = {}
            
            # 获取最终权重
            final_weights = normalized_weights.get('final', {})
            
            if not final_weights:
                return effectiveness
            
            # 创建加权特征
            X_weighted = X.copy()
            for feature, weight in final_weights.items():
                X_weighted[feature] = X[feature] * weight
            
            # 训练加权模型
            model_weighted = LinearRegression()
            model_weighted.fit(X_weighted, y)
            
            # 训练原始模型
            model_original = LinearRegression()
            model_original.fit(X, y)
            
            # 比较性能
            r2_weighted = model_weighted.score(X_weighted, y)
            r2_original = model_original.score(X, y)
            
            mse_weighted = mean_squared_error(y, model_weighted.predict(X_weighted))
            mse_original = mean_squared_error(y, model_original.predict(X))
            
            effectiveness = {
                'r2_improvement': r2_weighted - r2_original,
                'mse_improvement': mse_original - mse_weighted,
                'r2_weighted': r2_weighted,
                'r2_original': r2_original,
                'mse_weighted': mse_weighted,
                'mse_original': mse_original,
                'effectiveness_score': (r2_weighted - r2_original) * 100
            }
            
            logger.info(f"权重有效性验证完成: R²改进 {effectiveness['r2_improvement']:.4f}")
            return effectiveness
            
        except Exception as e:
            logger.error(f"权重有效性验证失败: {e}")
            return {}
    
    def optimize_weights(self, X: pd.DataFrame, y: pd.Series, 
                       objective: str = 'r2', 
                       constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """优化权重"""
        try:
            # 定义目标函数
            def objective_function(weights):
                # 确保权重为正
                weights = np.abs(weights)
                
                # 创建加权特征
                X_weighted = X.copy()
                for i, feature in enumerate(X.columns):
                    X_weighted[feature] = X[feature] * weights[i]
                
                # 训练模型
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)  # 负号因为要最大化R²
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 初始权重
            initial_weights = np.ones(len(X.columns))
            
            # 约束条件
            bounds = [(0.01, 10.0) for _ in range(len(X.columns))]  # 权重范围
            
            # 优化
            result = minimize(
                objective_function,
                initial_weights,
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 1000}
            )
            
            # 归一化优化后的权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 创建权重字典
            weight_dict = dict(zip(X.columns, optimized_weights))
            
            # 验证优化结果
            X_optimized = X.copy()
            for feature, weight in weight_dict.items():
                X_optimized[feature] = X[feature] * weight
            
            model_optimized = LinearRegression()
            model_optimized.fit(X_optimized, y)
            
            optimization_results = {
                'optimized_weights': weight_dict,
                'optimization_success': result.success,
                'optimization_message': result.message,
                'final_objective': -result.fun,
                'iterations': result.nit,
                'r2_score': model_optimized.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model_optimized.predict(X_optimized))
            }
            
            self.optimization_results = optimization_results
            logger.info(f"权重优化完成: R² = {optimization_results['r2_score']:.4f}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"权重优化失败: {e}")
            return {}
    
    def update_weights(self, X: pd.DataFrame, y: pd.Series, 
                      previous_weights: Dict[str, float],
                      update_rate: float = 0.1) -> Dict[str, float]:
        """更新权重"""
        try:
            # 计算新权重
            new_weights = self._calculate_comprehensive_weights(X, y)
            
            if not new_weights:
                return previous_weights
            
            # 平滑更新
            updated_weights = {}
            for feature in X.columns:
                old_weight = previous_weights.get(feature, 0.0)
                new_weight = new_weights.get(feature, old_weight)
                
                # 指数移动平均
                updated_weight = (1 - update_rate) * old_weight + update_rate * new_weight
                updated_weights[feature] = updated_weight
            
            # 归一化
            total_weight = sum(updated_weights.values())
            if total_weight > 0:
                updated_weights = {
                    feature: weight / total_weight
                    for feature, weight in updated_weights.items()
                }
            
            logger.info(f"权重更新完成: 更新率 {update_rate}")
            return updated_weights
            
        except Exception as e:
            logger.error(f"权重更新失败: {e}")
            return previous_weights
    
    def get_weight_insights(self) -> Dict[str, Any]:
        """获取权重洞察"""
        try:
            insights = {
                'weight_history': self.weight_history,
                'optimization_results': self.optimization_results,
                'weight_models': self.weight_models,
                'recommendations': self._generate_weight_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"权重洞察获取失败: {e}")
            return {}
    
    def _generate_weight_recommendations(self) -> List[str]:
        """生成权重建议"""
        try:
            recommendations = []
            
            # 基于优化结果生成建议
            if self.optimization_results:
                r2_score = self.optimization_results.get('r2_score', 0)
                
                if r2_score > 0.8:
                    recommendations.append("权重优化效果良好，建议定期更新权重")
                elif r2_score > 0.6:
                    recommendations.append("权重优化有一定效果，建议进一步调优")
                else:
                    recommendations.append("权重优化效果有限，建议检查数据质量")
            
            # 基于权重历史生成建议
            if self.weight_history:
                recommendations.append("建议建立权重监控机制，定期评估权重变化")
                recommendations.append("考虑使用多种权重计算方法进行交叉验证")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"权重建议生成失败: {e}")
            return []

