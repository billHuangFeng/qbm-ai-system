"""
协同效应分析算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import itertools
import logging
from ..logging_config import get_logger

logger = get_logger("synergy_analysis")

class SynergyAnalysis:
    """协同效应分析"""
    
    def __init__(self):
        self.synergy_effects = {}
        self.interaction_terms = {}
        self.synergy_models = {}
    
    def detect_synergy_effects(self, X: pd.DataFrame, y: pd.Series, 
                             threshold: float = 0.1) -> Dict[str, Any]:
        """检测协同效应"""
        try:
            synergy_results = {}
            
            # 1. 两两交互效应分析
            pairwise_synergy = self._analyze_pairwise_interactions(X, y, threshold)
            synergy_results['pairwise'] = pairwise_synergy
            
            # 2. 多项式特征分析
            polynomial_synergy = self._analyze_polynomial_interactions(X, y, threshold)
            synergy_results['polynomial'] = polynomial_synergy
            
            # 3. 随机森林特征重要性分析
            rf_synergy = self._analyze_rf_interactions(X, y, threshold)
            synergy_results['random_forest'] = rf_synergy
            
            # 4. 综合协同效应评分
            synergy_score = self._calculate_synergy_score(synergy_results)
            synergy_results['overall_score'] = synergy_score
            
            self.synergy_effects = synergy_results
            logger.info(f"协同效应分析完成，整体评分: {synergy_score:.4f}")
            
            return synergy_results
            
        except Exception as e:
            logger.error(f"协同效应检测失败: {e}")
            raise
    
    def _analyze_pairwise_interactions(self, X: pd.DataFrame, y: pd.Series, 
                                     threshold: float) -> Dict[str, Any]:
        """分析两两交互效应"""
        try:
            interactions = {}
            feature_names = X.columns.tolist()
            
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i+1:], i+1):
                    # 创建交互项
                    interaction_term = X[feature1] * X[feature2]
                    
                    # 训练包含交互项的模型
                    X_with_interaction = X.copy()
                    X_with_interaction[f"{feature1}_x_{feature2}"] = interaction_term
                    
                    # 比较有无交互项的模型性能
                    model_without = LinearRegression()
                    model_with = LinearRegression()
                    
                    model_without.fit(X[[feature1, feature2]], y)
                    model_with.fit(X_with_interaction[[feature1, feature2, f"{feature1}_x_{feature2}"]], y)
                    
                    # 计算性能提升
                    r2_without = model_without.score(X[[feature1, feature2]], y)
                    r2_with = model_with.score(X_with_interaction[[feature1, feature2, f"{feature1}_x_{feature2}"]], y)
                    
                    improvement = r2_with - r2_without
                    
                    if improvement > threshold:
                        interactions[f"{feature1}_x_{feature2}"] = {
                            'improvement': improvement,
                            'r2_without': r2_without,
                            'r2_with': r2_with,
                            'coefficient': model_with.coef_[-1],
                            'significance': self._calculate_significance(X, y, interaction_term)
                        }
            
            logger.info(f"发现 {len(interactions)} 个显著的两两交互效应")
            return interactions
            
        except Exception as e:
            logger.error(f"两两交互效应分析失败: {e}")
            return {}
    
    def _analyze_polynomial_interactions(self, X: pd.DataFrame, y: pd.Series, 
                                       threshold: float) -> Dict[str, Any]:
        """分析多项式交互效应"""
        try:
            polynomial_results = {}
            
            # 生成多项式特征
            poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
            X_poly = poly.fit_transform(X)
            poly_feature_names = poly.get_feature_names_out(X.columns)
            
            # 训练多项式模型
            model_poly = LinearRegression()
            model_poly.fit(X_poly, y)
            
            # 训练线性模型
            model_linear = LinearRegression()
            model_linear.fit(X, y)
            
            # 计算性能提升
            r2_linear = model_linear.score(X, y)
            r2_poly = model_poly.score(X_poly, y)
            improvement = r2_poly - r2_linear
            
            if improvement > threshold:
                # 分析交互项系数
                interaction_coeffs = {}
                for i, feature_name in enumerate(poly_feature_names):
                    if ' ' in feature_name:  # 交互项
                        interaction_coeffs[feature_name] = {
                            'coefficient': model_poly.coef_[i],
                            'importance': abs(model_poly.coef_[i])
                        }
                
                polynomial_results = {
                    'improvement': improvement,
                    'r2_linear': r2_linear,
                    'r2_poly': r2_poly,
                    'interaction_coefficients': interaction_coeffs,
                    'top_interactions': sorted(interaction_coeffs.items(), 
                                             key=lambda x: x[1]['importance'], reverse=True)[:10]
                }
            
            logger.info(f"多项式交互效应分析完成，性能提升: {improvement:.4f}")
            return polynomial_results
            
        except Exception as e:
            logger.error(f"多项式交互效应分析失败: {e}")
            return {}
    
    def _analyze_rf_interactions(self, X: pd.DataFrame, y: pd.Series, 
                               threshold: float) -> Dict[str, Any]:
        """使用随机森林分析交互效应"""
        try:
            # 训练随机森林模型
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            # 获取特征重要性
            feature_importance = dict(zip(X.columns, rf.feature_importances_))
            
            # 分析特征重要性分布
            importance_values = list(feature_importance.values())
            mean_importance = np.mean(importance_values)
            std_importance = np.std(importance_values)
            
            # 识别高重要性特征
            high_importance_features = {
                feature: importance for feature, importance in feature_importance.items()
                if importance > mean_importance + std_importance
            }
            
            # 分析特征组合的重要性
            feature_combinations = self._analyze_feature_combinations(X, y, rf)
            
            rf_results = {
                'feature_importance': feature_importance,
                'high_importance_features': high_importance_features,
                'feature_combinations': feature_combinations,
                'importance_stats': {
                    'mean': mean_importance,
                    'std': std_importance,
                    'max': max(importance_values),
                    'min': min(importance_values)
                }
            }
            
            logger.info(f"随机森林交互效应分析完成，发现 {len(high_importance_features)} 个高重要性特征")
            return rf_results
            
        except Exception as e:
            logger.error(f"随机森林交互效应分析失败: {e}")
            return {}
    
    def _analyze_feature_combinations(self, X: pd.DataFrame, y: pd.Series, 
                                    rf: RandomForestRegressor) -> Dict[str, Any]:
        """分析特征组合的重要性"""
        try:
            combinations = {}
            feature_names = X.columns.tolist()
            
            # 分析两两特征组合
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i+1:], i+1):
                    # 创建组合特征
                    combined_feature = X[feature1] * X[feature2]
                    
                    # 计算组合特征与目标变量的相关性
                    correlation = np.corrcoef(combined_feature, y)[0, 1]
                    
                    # 计算组合特征的重要性
                    importance = abs(correlation) * (rf.feature_importances_[i] + rf.feature_importances_[j])
                    
                    combinations[f"{feature1}_x_{feature2}"] = {
                        'correlation': correlation,
                        'importance': importance,
                        'feature1_importance': rf.feature_importances_[i],
                        'feature2_importance': rf.feature_importances_[j]
                    }
            
            # 按重要性排序
            sorted_combinations = sorted(combinations.items(), 
                                       key=lambda x: x[1]['importance'], reverse=True)
            
            return {
                'all_combinations': combinations,
                'top_combinations': sorted_combinations[:10]
            }
            
        except Exception as e:
            logger.error(f"特征组合分析失败: {e}")
            return {}
    
    def _calculate_significance(self, X: pd.DataFrame, y: pd.Series, 
                              interaction_term: pd.Series) -> float:
        """计算交互项的显著性"""
        try:
            from scipy import stats
            
            # 计算交互项与目标变量的相关系数
            correlation, p_value = stats.pearsonr(interaction_term, y)
            
            # 返回显著性水平（1 - p_value）
            return 1 - p_value
            
        except Exception as e:
            logger.error(f"显著性计算失败: {e}")
            return 0.0
    
    def _calculate_synergy_score(self, synergy_results: Dict[str, Any]) -> float:
        """计算综合协同效应评分"""
        try:
            score = 0.0
            weights = {'pairwise': 0.4, 'polynomial': 0.3, 'random_forest': 0.3}
            
            # 两两交互效应评分
            if 'pairwise' in synergy_results and synergy_results['pairwise']:
                pairwise_count = len(synergy_results['pairwise'])
                pairwise_avg_improvement = np.mean([
                    result['improvement'] for result in synergy_results['pairwise'].values()
                ])
                score += weights['pairwise'] * pairwise_count * pairwise_avg_improvement
            
            # 多项式交互效应评分
            if 'polynomial' in synergy_results and synergy_results['polynomial']:
                poly_improvement = synergy_results['polynomial'].get('improvement', 0)
                score += weights['polynomial'] * poly_improvement
            
            # 随机森林交互效应评分
            if 'random_forest' in synergy_results and synergy_results['random_forest']:
                rf_high_importance = len(synergy_results['random_forest'].get('high_importance_features', {}))
                rf_avg_importance = synergy_results['random_forest'].get('importance_stats', {}).get('mean', 0)
                score += weights['random_forest'] * rf_high_importance * rf_avg_importance
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"协同效应评分计算失败: {e}")
            return 0.0
    
    def create_synergy_features(self, X: pd.DataFrame, 
                              synergy_threshold: float = 0.1) -> pd.DataFrame:
        """创建协同效应特征"""
        try:
            X_enhanced = X.copy()
            
            # 添加两两交互项
            if 'pairwise' in self.synergy_effects:
                for interaction_name, interaction_data in self.synergy_effects['pairwise'].items():
                    if interaction_data['improvement'] > synergy_threshold:
                        feature1, feature2 = interaction_name.split('_x_')
                        X_enhanced[interaction_name] = X[feature1] * X[feature2]
            
            # 添加多项式特征
            if 'polynomial' in self.synergy_effects and self.synergy_effects['polynomial']:
                poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
                X_poly = poly.fit_transform(X)
                poly_feature_names = poly.get_feature_names_out(X.columns)
                
                for i, feature_name in enumerate(poly_feature_names):
                    if ' ' in feature_name:  # 交互项
                        X_enhanced[feature_name.replace(' ', '_')] = X_poly[:, i]
            
            logger.info(f"协同效应特征创建完成，新增 {len(X_enhanced.columns) - len(X.columns)} 个特征")
            return X_enhanced
            
        except Exception as e:
            logger.error(f"协同效应特征创建失败: {e}")
            return X
    
    def get_synergy_insights(self) -> Dict[str, Any]:
        """获取协同效应洞察"""
        try:
            insights = {
                'overall_synergy_score': self.synergy_effects.get('overall_score', 0),
                'synergy_level': self._classify_synergy_level(self.synergy_effects.get('overall_score', 0)),
                'key_interactions': self._extract_key_interactions(),
                'recommendations': self._generate_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"协同效应洞察获取失败: {e}")
            return {}
    
    def _classify_synergy_level(self, score: float) -> str:
        """分类协同效应水平"""
        if score >= 0.7:
            return "高协同效应"
        elif score >= 0.4:
            return "中等协同效应"
        elif score >= 0.1:
            return "低协同效应"
        else:
            return "无显著协同效应"
    
    def _extract_key_interactions(self) -> List[Dict[str, Any]]:
        """提取关键交互项"""
        try:
            key_interactions = []
            
            # 从两两交互中提取
            if 'pairwise' in self.synergy_effects:
                for name, data in self.synergy_effects['pairwise'].items():
                    if data['improvement'] > 0.1:
                        key_interactions.append({
                            'type': 'pairwise',
                            'name': name,
                            'improvement': data['improvement'],
                            'coefficient': data['coefficient']
                        })
            
            # 从多项式交互中提取
            if 'polynomial' in self.synergy_effects and self.synergy_effects['polynomial']:
                top_interactions = self.synergy_effects['polynomial'].get('top_interactions', [])
                for name, data in top_interactions[:5]:
                    key_interactions.append({
                        'type': 'polynomial',
                        'name': name,
                        'coefficient': data['coefficient'],
                        'importance': data['importance']
                    })
            
            # 按重要性排序
            key_interactions.sort(key=lambda x: x.get('improvement', x.get('importance', 0)), reverse=True)
            
            return key_interactions[:10]
            
        except Exception as e:
            logger.error(f"关键交互项提取失败: {e}")
            return []
    
    def _generate_recommendations(self) -> List[str]:
        """生成协同效应建议"""
        try:
            recommendations = []
            
            synergy_score = self.synergy_effects.get('overall_score', 0)
            
            if synergy_score >= 0.7:
                recommendations.append("检测到高协同效应，建议在模型中重点考虑交互项")
                recommendations.append("考虑使用多项式回归或集成模型来捕捉复杂交互")
            elif synergy_score >= 0.4:
                recommendations.append("检测到中等协同效应，建议添加关键交互项")
                recommendations.append("考虑使用特征工程来增强模型性能")
            elif synergy_score >= 0.1:
                recommendations.append("检测到低协同效应，建议进一步分析特征关系")
                recommendations.append("考虑使用更复杂的模型来捕捉潜在交互")
            else:
                recommendations.append("未检测到显著协同效应，建议检查数据质量")
                recommendations.append("考虑使用线性模型或简单的机器学习方法")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"建议生成失败: {e}")
            return []

