"""
高级关系识别算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import logging
from ..logging_config import get_logger

logger = get_logger("advanced_relationships")

class AdvancedRelationshipAnalysis:
    """高级关系识别分析"""
    
    def __init__(self):
        self.relationship_models = {}
        self.relationship_insights = {}
        self.feature_importance = {}
    
    def identify_advanced_relationships(self, X: pd.DataFrame, y: pd.Series, 
                                      cv_folds: int = 5) -> Dict[str, Any]:
        """识别高级关系"""
        try:
            relationship_results = {}
            
            # 1. 集成模型关系识别
            ensemble_relationships = self._analyze_ensemble_relationships(X, y, cv_folds)
            relationship_results['ensemble'] = ensemble_relationships
            
            # 2. 神经网络关系识别
            neural_relationships = self._analyze_neural_relationships(X, y, cv_folds)
            relationship_results['neural_network'] = neural_relationships
            
            # 3. 特征交互关系识别
            feature_interactions = self._analyze_feature_interactions(X, y)
            relationship_results['feature_interactions'] = feature_interactions
            
            # 4. 非线性关系识别
            nonlinear_relationships = self._analyze_nonlinear_relationships(X, y, cv_folds)
            relationship_results['nonlinear'] = nonlinear_relationships
            
            # 5. 综合关系评分
            relationship_score = self._calculate_relationship_score(relationship_results)
            relationship_results['overall_score'] = relationship_score
            
            self.relationship_insights = relationship_results
            logger.info(f"高级关系识别完成，整体评分: {relationship_score:.4f}")
            
            return relationship_results
            
        except Exception as e:
            logger.error(f"高级关系识别失败: {e}")
            raise
    
    def _analyze_ensemble_relationships(self, X: pd.DataFrame, y: pd.Series, 
                                      cv_folds: int) -> Dict[str, Any]:
        """分析集成模型关系"""
        try:
            ensemble_results = {}
            
            # 随机森林
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            rf_cv_scores = cross_val_score(rf, X, y, cv=cv_folds, scoring='r2')
            
            ensemble_results['random_forest'] = {
                'model': rf,
                'cv_scores': rf_cv_scores.tolist(),
                'mean_cv_score': rf_cv_scores.mean(),
                'std_cv_score': rf_cv_scores.std(),
                'feature_importance': dict(zip(X.columns, rf.feature_importances_)),
                'r2_score': rf.score(X, y)
            }
            
            # XGBoost
            xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
            xgb_model.fit(X, y)
            xgb_cv_scores = cross_val_score(xgb_model, X, y, cv=cv_folds, scoring='r2')
            
            ensemble_results['xgboost'] = {
                'model': xgb_model,
                'cv_scores': xgb_cv_scores.tolist(),
                'mean_cv_score': xgb_cv_scores.mean(),
                'std_cv_score': xgb_cv_scores.std(),
                'feature_importance': dict(zip(X.columns, xgb_model.feature_importances_)),
                'r2_score': xgb_model.score(X, y)
            }
            
            # LightGBM
            lgb_model = lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
            lgb_model.fit(X, y)
            lgb_cv_scores = cross_val_score(lgb_model, X, y, cv=cv_folds, scoring='r2')
            
            ensemble_results['lightgbm'] = {
                'model': lgb_model,
                'cv_scores': lgb_cv_scores.tolist(),
                'mean_cv_score': lgb_cv_scores.mean(),
                'std_cv_score': lgb_cv_scores.std(),
                'feature_importance': dict(zip(X.columns, lgb_model.feature_importances_)),
                'r2_score': lgb_model.score(X, y)
            }
            
            # 梯度提升
            gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
            gb.fit(X, y)
            gb_cv_scores = cross_val_score(gb, X, y, cv=cv_folds, scoring='r2')
            
            ensemble_results['gradient_boosting'] = {
                'model': gb,
                'cv_scores': gb_cv_scores.tolist(),
                'mean_cv_score': gb_cv_scores.mean(),
                'std_cv_score': gb_cv_scores.std(),
                'feature_importance': dict(zip(X.columns, gb.feature_importances_)),
                'r2_score': gb.score(X, y)
            }
            
            # 找出最佳模型
            best_model_name = max(ensemble_results.keys(), 
                                key=lambda k: ensemble_results[k]['mean_cv_score'])
            ensemble_results['best_model'] = best_model_name
            
            logger.info(f"集成模型关系分析完成，最佳模型: {best_model_name}")
            return ensemble_results
            
        except Exception as e:
            logger.error(f"集成模型关系分析失败: {e}")
            return {}
    
    def _analyze_neural_relationships(self, X: pd.DataFrame, y: pd.Series, 
                                    cv_folds: int) -> Dict[str, Any]:
        """分析神经网络关系"""
        try:
            neural_results = {}
            
            # 标准化数据
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
            
            # 浅层神经网络
            mlp_shallow = MLPRegressor(
                hidden_layer_sizes=(50,),
                max_iter=1000,
                random_state=42
            )
            mlp_shallow.fit(X_scaled, y)
            mlp_shallow_cv_scores = cross_val_score(mlp_shallow, X_scaled, y, cv=cv_folds, scoring='r2')
            
            neural_results['mlp_shallow'] = {
                'model': mlp_shallow,
                'cv_scores': mlp_shallow_cv_scores.tolist(),
                'mean_cv_score': mlp_shallow_cv_scores.mean(),
                'std_cv_score': mlp_shallow_cv_scores.std(),
                'r2_score': mlp_shallow.score(X_scaled, y),
                'training_loss': mlp_shallow.loss_curve_.tolist() if hasattr(mlp_shallow, 'loss_curve_') else []
            }
            
            # 深层神经网络
            mlp_deep = MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                max_iter=1000,
                random_state=42
            )
            mlp_deep.fit(X_scaled, y)
            mlp_deep_cv_scores = cross_val_score(mlp_deep, X_scaled, y, cv=cv_folds, scoring='r2')
            
            neural_results['mlp_deep'] = {
                'model': mlp_deep,
                'cv_scores': mlp_deep_cv_scores.tolist(),
                'mean_cv_score': mlp_deep_cv_scores.mean(),
                'std_cv_score': mlp_deep_cv_scores.std(),
                'r2_score': mlp_deep.score(X_scaled, y),
                'training_loss': mlp_deep.loss_curve_.tolist() if hasattr(mlp_deep, 'loss_curve_') else []
            }
            
            # 宽神经网络
            mlp_wide = MLPRegressor(
                hidden_layer_sizes=(200, 100),
                max_iter=1000,
                random_state=42
            )
            mlp_wide.fit(X_scaled, y)
            mlp_wide_cv_scores = cross_val_score(mlp_wide, X_scaled, y, cv=cv_folds, scoring='r2')
            
            neural_results['mlp_wide'] = {
                'model': mlp_wide,
                'cv_scores': mlp_wide_cv_scores.tolist(),
                'mean_cv_score': mlp_wide_cv_scores.mean(),
                'std_cv_score': mlp_wide_cv_scores.std(),
                'r2_score': mlp_wide.score(X_scaled, y),
                'training_loss': mlp_wide.loss_curve_.tolist() if hasattr(mlp_wide, 'loss_curve_') else []
            }
            
            # 找出最佳神经网络
            best_neural_name = max(neural_results.keys(), 
                                 key=lambda k: neural_results[k]['mean_cv_score'])
            neural_results['best_model'] = best_neural_name
            
            logger.info(f"神经网络关系分析完成，最佳模型: {best_neural_name}")
            return neural_results
            
        except Exception as e:
            logger.error(f"神经网络关系分析失败: {e}")
            return {}
    
    def _analyze_feature_interactions(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析特征交互关系"""
        try:
            interaction_results = {}
            
            # 两两特征交互分析
            pairwise_interactions = self._analyze_pairwise_interactions(X, y)
            interaction_results['pairwise'] = pairwise_interactions
            
            # 三特征交互分析
            triple_interactions = self._analyze_triple_interactions(X, y)
            interaction_results['triple'] = triple_interactions
            
            # 特征组合分析
            feature_combinations = self._analyze_feature_combinations(X, y)
            interaction_results['combinations'] = feature_combinations
            
            logger.info(f"特征交互关系分析完成")
            return interaction_results
            
        except Exception as e:
            logger.error(f"特征交互关系分析失败: {e}")
            return {}
    
    def _analyze_pairwise_interactions(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析两两特征交互"""
        try:
            pairwise_results = {}
            feature_names = X.columns.tolist()
            
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i+1:], i+1):
                    # 创建交互项
                    interaction_term = X[feature1] * X[feature2]
                    
                    # 计算交互项与目标变量的相关性
                    correlation = np.corrcoef(interaction_term, y)[0, 1]
                    
                    # 训练包含交互项的模型
                    X_with_interaction = X[[feature1, feature2]].copy()
                    X_with_interaction[f"{feature1}_x_{feature2}"] = interaction_term
                    
                    model = LinearRegression()
                    model.fit(X_with_interaction, y)
                    
                    # 计算性能提升
                    r2_without = LinearRegression().fit(X[[feature1, feature2]], y).score(X[[feature1, feature2]], y)
                    r2_with = model.score(X_with_interaction, y)
                    improvement = r2_with - r2_without
                    
                    if abs(correlation) > 0.1 or improvement > 0.01:
                        pairwise_results[f"{feature1}_x_{feature2}"] = {
                            'correlation': correlation,
                            'improvement': improvement,
                            'r2_without': r2_without,
                            'r2_with': r2_with,
                            'coefficient': model.coef_[-1],
                            'significance': abs(correlation) * improvement
                        }
            
            # 按重要性排序
            sorted_interactions = sorted(pairwise_results.items(), 
                                       key=lambda x: x[1]['significance'], reverse=True)
            
            return {
                'all_interactions': pairwise_results,
                'top_interactions': sorted_interactions[:20]
            }
            
        except Exception as e:
            logger.error(f"两两特征交互分析失败: {e}")
            return {}
    
    def _analyze_triple_interactions(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析三特征交互"""
        try:
            triple_results = {}
            feature_names = X.columns.tolist()
            
            # 限制特征数量以避免组合爆炸
            if len(feature_names) > 10:
                # 选择前10个最重要的特征
                rf = RandomForestRegressor(n_estimators=50, random_state=42)
                rf.fit(X, y)
                feature_importance = dict(zip(feature_names, rf.feature_importances_))
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
                feature_names = [f[0] for f in top_features]
            
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i+1:], i+1):
                    for k, feature3 in enumerate(feature_names[j+1:], j+1):
                        # 创建三特征交互项
                        triple_interaction = X[feature1] * X[feature2] * X[feature3]
                        
                        # 计算交互项与目标变量的相关性
                        correlation = np.corrcoef(triple_interaction, y)[0, 1]
                        
                        if abs(correlation) > 0.15:  # 更高的阈值
                            triple_results[f"{feature1}_x_{feature2}_x_{feature3}"] = {
                                'correlation': correlation,
                                'features': [feature1, feature2, feature3],
                                'significance': abs(correlation)
                            }
            
            # 按重要性排序
            sorted_triple = sorted(triple_results.items(), 
                                 key=lambda x: x[1]['significance'], reverse=True)
            
            return {
                'all_triple_interactions': triple_results,
                'top_triple_interactions': sorted_triple[:10]
            }
            
        except Exception as e:
            logger.error(f"三特征交互分析失败: {e}")
            return {}
    
    def _analyze_feature_combinations(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析特征组合"""
        try:
            combination_results = {}
            
            # 使用随机森林分析特征组合
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            # 获取特征重要性
            feature_importance = dict(zip(X.columns, rf.feature_importances_))
            
            # 分析高重要性特征的组合
            high_importance_features = [f for f, imp in feature_importance.items() if imp > np.mean(list(feature_importance.values()))]
            
            if len(high_importance_features) >= 2:
                # 分析高重要性特征的两两组合
                combinations = []
                for i, feature1 in enumerate(high_importance_features):
                    for j, feature2 in enumerate(high_importance_features[i+1:], i+1):
                        # 创建组合特征
                        combination = X[feature1] + X[feature2]
                        
                        # 计算组合特征与目标变量的相关性
                        correlation = np.corrcoef(combination, y)[0, 1]
                        
                        combinations.append({
                            'features': [feature1, feature2],
                            'correlation': correlation,
                            'importance_sum': feature_importance[feature1] + feature_importance[feature2]
                        })
                
                # 按相关性排序
                combinations.sort(key=lambda x: abs(x['correlation']), reverse=True)
                
                combination_results = {
                    'high_importance_features': high_importance_features,
                    'feature_combinations': combinations[:10],
                    'feature_importance': feature_importance
                }
            
            return combination_results
            
        except Exception as e:
            logger.error(f"特征组合分析失败: {e}")
            return {}
    
    def _analyze_nonlinear_relationships(self, X: pd.DataFrame, y: pd.Series, 
                                       cv_folds: int) -> Dict[str, Any]:
        """分析非线性关系"""
        try:
            nonlinear_results = {}
            
            # 多项式特征分析
            from sklearn.preprocessing import PolynomialFeatures
            
            # 二次多项式
            poly2 = PolynomialFeatures(degree=2, include_bias=False)
            X_poly2 = poly2.fit_transform(X)
            poly2_feature_names = poly2.get_feature_names_out(X.columns)
            
            model_poly2 = LinearRegression()
            model_poly2.fit(X_poly2, y)
            poly2_cv_scores = cross_val_score(model_poly2, X_poly2, y, cv=cv_folds, scoring='r2')
            
            nonlinear_results['polynomial_degree_2'] = {
                'model': model_poly2,
                'cv_scores': poly2_cv_scores.tolist(),
                'mean_cv_score': poly2_cv_scores.mean(),
                'std_cv_score': poly2_cv_scores.std(),
                'r2_score': model_poly2.score(X_poly2, y),
                'feature_names': poly2_feature_names.tolist()
            }
            
            # 三次多项式（如果特征数量不太多）
            if len(X.columns) <= 5:
                poly3 = PolynomialFeatures(degree=3, include_bias=False)
                X_poly3 = poly3.fit_transform(X)
                poly3_feature_names = poly3.get_feature_names_out(X.columns)
                
                model_poly3 = LinearRegression()
                model_poly3.fit(X_poly3, y)
                poly3_cv_scores = cross_val_score(model_poly3, X_poly3, y, cv=cv_folds, scoring='r2')
                
                nonlinear_results['polynomial_degree_3'] = {
                    'model': model_poly3,
                    'cv_scores': poly3_cv_scores.tolist(),
                    'mean_cv_score': poly3_cv_scores.mean(),
                    'std_cv_score': poly3_cv_scores.std(),
                    'r2_score': model_poly3.score(X_poly3, y),
                    'feature_names': poly3_feature_names.tolist()
                }
            
            # 对数变换分析
            log_results = self._analyze_log_transformations(X, y, cv_folds)
            nonlinear_results['log_transformations'] = log_results
            
            # 指数变换分析
            exp_results = self._analyze_exponential_transformations(X, y, cv_folds)
            nonlinear_results['exponential_transformations'] = exp_results
            
            logger.info(f"非线性关系分析完成")
            return nonlinear_results
            
        except Exception as e:
            logger.error(f"非线性关系分析失败: {e}")
            return {}
    
    def _analyze_log_transformations(self, X: pd.DataFrame, y: pd.Series, 
                                   cv_folds: int) -> Dict[str, Any]:
        """分析对数变换"""
        try:
            log_results = {}
            
            for feature in X.columns:
                # 确保特征值为正
                if (X[feature] > 0).all():
                    # 对数变换
                    X_log = X.copy()
                    X_log[f"{feature}_log"] = np.log(X[feature])
                    
                    # 训练模型
                    model = LinearRegression()
                    model.fit(X_log[[feature, f"{feature}_log"]], y)
                    cv_scores = cross_val_score(model, X_log[[feature, f"{feature}_log"]], y, cv=cv_folds, scoring='r2')
                    
                    # 比较性能
                    model_original = LinearRegression()
                    model_original.fit(X[[feature]], y)
                    original_r2 = model_original.score(X[[feature]], y)
                    
                    log_results[feature] = {
                        'cv_scores': cv_scores.tolist(),
                        'mean_cv_score': cv_scores.mean(),
                        'std_cv_score': cv_scores.std(),
                        'r2_score': model.score(X_log[[feature, f"{feature}_log"]], y),
                        'original_r2': original_r2,
                        'improvement': model.score(X_log[[feature, f"{feature}_log"]], y) - original_r2
                    }
            
            return log_results
            
        except Exception as e:
            logger.error(f"对数变换分析失败: {e}")
            return {}
    
    def _analyze_exponential_transformations(self, X: pd.DataFrame, y: pd.Series, 
                                           cv_folds: int) -> Dict[str, Any]:
        """分析指数变换"""
        try:
            exp_results = {}
            
            for feature in X.columns:
                # 指数变换
                X_exp = X.copy()
                X_exp[f"{feature}_exp"] = np.exp(X[feature])
                
                # 训练模型
                model = LinearRegression()
                model.fit(X_exp[[feature, f"{feature}_exp"]], y)
                cv_scores = cross_val_score(model, X_exp[[feature, f"{feature}_exp"]], y, cv=cv_folds, scoring='r2')
                
                # 比较性能
                model_original = LinearRegression()
                model_original.fit(X[[feature]], y)
                original_r2 = model_original.score(X[[feature]], y)
                
                exp_results[feature] = {
                    'cv_scores': cv_scores.tolist(),
                    'mean_cv_score': cv_scores.mean(),
                    'std_cv_score': cv_scores.std(),
                    'r2_score': model.score(X_exp[[feature, f"{feature}_exp"]], y),
                    'original_r2': original_r2,
                    'improvement': model.score(X_exp[[feature, f"{feature}_exp"]], y) - original_r2
                }
            
            return exp_results
            
        except Exception as e:
            logger.error(f"指数变换分析失败: {e}")
            return {}
    
    def _calculate_relationship_score(self, relationship_results: Dict[str, Any]) -> float:
        """计算综合关系评分"""
        try:
            score = 0.0
            weights = {'ensemble': 0.3, 'neural_network': 0.3, 'feature_interactions': 0.2, 'nonlinear': 0.2}
            
            # 集成模型评分
            if 'ensemble' in relationship_results and relationship_results['ensemble']:
                ensemble_scores = [data['mean_cv_score'] for data in relationship_results['ensemble'].values() 
                                 if isinstance(data, dict) and 'mean_cv_score' in data]
                if ensemble_scores:
                    score += weights['ensemble'] * np.mean(ensemble_scores)
            
            # 神经网络评分
            if 'neural_network' in relationship_results and relationship_results['neural_network']:
                neural_scores = [data['mean_cv_score'] for data in relationship_results['neural_network'].values() 
                               if isinstance(data, dict) and 'mean_cv_score' in data]
                if neural_scores:
                    score += weights['neural_network'] * np.mean(neural_scores)
            
            # 特征交互评分
            if 'feature_interactions' in relationship_results and relationship_results['feature_interactions']:
                interaction_count = 0
                if 'pairwise' in relationship_results['feature_interactions']:
                    interaction_count += len(relationship_results['feature_interactions']['pairwise'].get('top_interactions', []))
                if 'triple' in relationship_results['feature_interactions']:
                    interaction_count += len(relationship_results['feature_interactions']['triple'].get('top_triple_interactions', []))
                
                score += weights['feature_interactions'] * min(interaction_count / 10, 1.0)
            
            # 非线性关系评分
            if 'nonlinear' in relationship_results and relationship_results['nonlinear']:
                nonlinear_scores = [data['mean_cv_score'] for data in relationship_results['nonlinear'].values() 
                                  if isinstance(data, dict) and 'mean_cv_score' in data]
                if nonlinear_scores:
                    score += weights['nonlinear'] * np.mean(nonlinear_scores)
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"关系评分计算失败: {e}")
            return 0.0
    
    def get_relationship_insights(self) -> Dict[str, Any]:
        """获取关系洞察"""
        try:
            insights = {
                'overall_relationship_score': self.relationship_insights.get('overall_score', 0),
                'relationship_level': self._classify_relationship_level(self.relationship_insights.get('overall_score', 0)),
                'key_relationships': self._extract_key_relationships(),
                'recommendations': self._generate_relationship_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"关系洞察获取失败: {e}")
            return {}
    
    def _classify_relationship_level(self, score: float) -> str:
        """分类关系水平"""
        if score >= 0.8:
            return "高复杂度关系"
        elif score >= 0.6:
            return "中等复杂度关系"
        elif score >= 0.3:
            return "低复杂度关系"
        else:
            return "简单线性关系"
    
    def _extract_key_relationships(self) -> List[Dict[str, Any]]:
        """提取关键关系"""
        try:
            key_relationships = []
            
            # 从集成模型中提取
            if 'ensemble' in self.relationship_insights:
                for model_name, model_data in self.relationship_insights['ensemble'].items():
                    if isinstance(model_data, dict) and 'mean_cv_score' in model_data:
                        key_relationships.append({
                            'type': 'ensemble',
                            'model': model_name,
                            'score': model_data['mean_cv_score'],
                            'importance': 'high' if model_data['mean_cv_score'] > 0.7 else 'medium'
                        })
            
            # 从神经网络中提取
            if 'neural_network' in self.relationship_insights:
                for model_name, model_data in self.relationship_insights['neural_network'].items():
                    if isinstance(model_data, dict) and 'mean_cv_score' in model_data:
                        key_relationships.append({
                            'type': 'neural_network',
                            'model': model_name,
                            'score': model_data['mean_cv_score'],
                            'importance': 'high' if model_data['mean_cv_score'] > 0.7 else 'medium'
                        })
            
            # 从特征交互中提取
            if 'feature_interactions' in self.relationship_insights:
                interactions = self.relationship_insights['feature_interactions']
                if 'pairwise' in interactions and 'top_interactions' in interactions['pairwise']:
                    for interaction_name, interaction_data in interactions['pairwise']['top_interactions'][:5]:
                        key_relationships.append({
                            'type': 'feature_interaction',
                            'interaction': interaction_name,
                            'significance': interaction_data['significance'],
                            'importance': 'high' if interaction_data['significance'] > 0.5 else 'medium'
                        })
            
            # 按重要性排序
            key_relationships.sort(key=lambda x: x.get('score', x.get('significance', 0)), reverse=True)
            
            return key_relationships[:10]
            
        except Exception as e:
            logger.error(f"关键关系提取失败: {e}")
            return []
    
    def _generate_relationship_recommendations(self) -> List[str]:
        """生成关系建议"""
        try:
            recommendations = []
            
            relationship_score = self.relationship_insights.get('overall_score', 0)
            
            if relationship_score >= 0.8:
                recommendations.append("检测到高复杂度关系，建议使用集成模型或深度神经网络")
                recommendations.append("考虑使用特征工程来增强模型性能")
                recommendations.append("建议进行详细的特征交互分析")
            elif relationship_score >= 0.6:
                recommendations.append("检测到中等复杂度关系，建议使用随机森林或XGBoost")
                recommendations.append("考虑添加多项式特征")
                recommendations.append("建议分析特征交互效应")
            elif relationship_score >= 0.3:
                recommendations.append("检测到低复杂度关系，建议使用线性模型或浅层神经网络")
                recommendations.append("考虑使用特征选择来简化模型")
                recommendations.append("建议检查数据质量和特征工程")
            else:
                recommendations.append("检测到简单线性关系，建议使用线性回归")
                recommendations.append("考虑使用正则化方法防止过拟合")
                recommendations.append("建议检查数据预处理步骤")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"关系建议生成失败: {e}")
            return []

