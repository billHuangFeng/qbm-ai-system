"""
高级关系分析算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from scipy import stats
from scipy.optimize import minimize
import logging
from ..logging_config import get_logger

logger = get_logger("advanced_relationships")

class AdvancedRelationships:
    """高级关系分析"""
    
    def __init__(self):
        self.relationship_models = {}
        self.relationship_scores = {}
        self.feature_interactions = {}
        self.nonlinear_patterns = {}
    
    def analyze_complex_relationships(self, X: pd.DataFrame, y: pd.Series,
                                   relationship_types: List[str] = None) -> Dict[str, Any]:
        """分析复杂关系"""
        try:
            if relationship_types is None:
                relationship_types = ['linear', 'nonlinear', 'interaction', 'hierarchical', 'causal']
            
            results = {}
            
            # 1. 线性关系分析
            if 'linear' in relationship_types:
                linear_results = self._analyze_linear_relationships(X, y)
                results['linear'] = linear_results
            
            # 2. 非线性关系分析
            if 'nonlinear' in relationship_types:
                nonlinear_results = self._analyze_nonlinear_relationships(X, y)
                results['nonlinear'] = nonlinear_results
            
            # 3. 交互关系分析
            if 'interaction' in relationship_types:
                interaction_results = self._analyze_interaction_relationships(X, y)
                results['interaction'] = interaction_results
            
            # 4. 层次关系分析
            if 'hierarchical' in relationship_types:
                hierarchical_results = self._analyze_hierarchical_relationships(X, y)
                results['hierarchical'] = hierarchical_results
            
            # 5. 因果关系分析
            if 'causal' in relationship_types:
                causal_results = self._analyze_causal_relationships(X, y)
                results['causal'] = causal_results
            
            # 6. 综合关系评分
            overall_score = self._calculate_relationship_score(results)
            results['overall_score'] = overall_score
            
            self.relationship_scores = results
            logger.info(f"复杂关系分析完成，整体评分: {overall_score:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"复杂关系分析失败: {e}")
            raise
    
    def _analyze_linear_relationships(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析线性关系"""
        try:
            linear_results = {}
            
            # 1. 简单线性回归
            simple_linear = {}
            for feature in X.columns:
                X_feature = X[feature].values.reshape(-1, 1)
                model = LinearRegression()
                model.fit(X_feature, y)
                
                y_pred = model.predict(X_feature)
                r2 = r2_score(y, y_pred)
                mse = mean_squared_error(y, y_pred)
                
                simple_linear[feature] = {
                    'coefficient': model.coef_[0],
                    'intercept': model.intercept_,
                    'r2': r2,
                    'mse': mse,
                    'correlation': np.corrcoef(X[feature], y)[0, 1]
                }
            
            linear_results['simple_linear'] = simple_linear
            
            # 2. 多元线性回归
            X_scaled = StandardScaler().fit_transform(X)
            model_multiple = LinearRegression()
            model_multiple.fit(X_scaled, y)
            
            y_pred_multiple = model_multiple.predict(X_scaled)
            r2_multiple = r2_score(y, y_pred_multiple)
            mse_multiple = mean_squared_error(y, y_pred_multiple)
            
            linear_results['multiple_linear'] = {
                'coefficients': dict(zip(X.columns, model_multiple.coef_)),
                'intercept': model_multiple.intercept_,
                'r2': r2_multiple,
                'mse': mse_multiple,
                'feature_importance': dict(zip(X.columns, np.abs(model_multiple.coef_)))
            }
            
            # 3. 正则化线性回归
            regularization_results = {}
            for reg_type in ['ridge', 'lasso', 'elastic']:
                if reg_type == 'ridge':
                    model = Ridge(alpha=1.0)
                elif reg_type == 'lasso':
                    model = Lasso(alpha=0.1)
                else:  # elastic
                    model = ElasticNet(alpha=0.1, l1_ratio=0.5)
                
                model.fit(X_scaled, y)
                y_pred_reg = model.predict(X_scaled)
                
                regularization_results[reg_type] = {
                    'coefficients': dict(zip(X.columns, model.coef_)),
                    'intercept': model.intercept_,
                    'r2': r2_score(y, y_pred_reg),
                    'mse': mean_squared_error(y, y_pred_reg),
                    'feature_importance': dict(zip(X.columns, np.abs(model.coef_)))
                }
            
            linear_results['regularization'] = regularization_results
            
            logger.info(f"线性关系分析完成，发现 {len(simple_linear)} 个特征的线性关系")
            return linear_results
            
        except Exception as e:
            logger.error(f"线性关系分析失败: {e}")
            return {}
    
    def _analyze_nonlinear_relationships(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析非线性关系"""
        try:
            nonlinear_results = {}
            
            # 1. 多项式特征分析
            polynomial_results = {}
            for degree in [2, 3]:
                poly_features = {}
                for feature in X.columns:
                    X_feature = X[feature].values.reshape(-1, 1)
                    
                    # 创建多项式特征
                    X_poly = np.column_stack([X_feature**i for i in range(1, degree + 1)])
                    
                    model = LinearRegression()
                    model.fit(X_poly, y)
                    
                    y_pred = model.predict(X_poly)
                    r2 = r2_score(y, y_pred)
                    
                    poly_features[feature] = {
                        'degree': degree,
                        'coefficients': model.coef_.tolist(),
                        'intercept': model.intercept_,
                        'r2': r2,
                        'improvement': r2 - np.corrcoef(X[feature], y)[0, 1]**2
                    }
                
                polynomial_results[f'degree_{degree}'] = poly_features
            
            nonlinear_results['polynomial'] = polynomial_results
            
            # 2. 树模型分析
            tree_results = {}
            
            # Random Forest
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X, y)
            y_pred_rf = rf_model.predict(X)
            
            tree_results['random_forest'] = {
                'r2': r2_score(y, y_pred_rf),
                'mse': mean_squared_error(y, y_pred_rf),
                'feature_importance': dict(zip(X.columns, rf_model.feature_importances_))
            }
            
            # Gradient Boosting
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            gb_model.fit(X, y)
            y_pred_gb = gb_model.predict(X)
            
            tree_results['gradient_boosting'] = {
                'r2': r2_score(y, y_pred_gb),
                'mse': mean_squared_error(y, y_pred_gb),
                'feature_importance': dict(zip(X.columns, gb_model.feature_importances_))
            }
            
            nonlinear_results['tree_models'] = tree_results
            
            # 3. 神经网络分析
            neural_results = {}
            
            # MLP Regressor
            mlp_model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
            mlp_model.fit(X, y)
            y_pred_mlp = mlp_model.predict(X)
            
            neural_results['mlp'] = {
                'r2': r2_score(y, y_pred_mlp),
                'mse': mean_squared_error(y, y_pred_mlp),
                'n_iter': mlp_model.n_iter_,
                'loss': mlp_model.loss_
            }
            
            nonlinear_results['neural_networks'] = neural_results
            
            # 4. 非线性模式检测
            nonlinear_patterns = self._detect_nonlinear_patterns(X, y)
            nonlinear_results['patterns'] = nonlinear_patterns
            
            logger.info(f"非线性关系分析完成，发现多种非线性模式")
            return nonlinear_results
            
        except Exception as e:
            logger.error(f"非线性关系分析失败: {e}")
            return {}
    
    def _analyze_interaction_relationships(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析交互关系"""
        try:
            interaction_results = {}
            
            # 1. 两两交互分析
            pairwise_interactions = {}
            features = X.columns.tolist()
            
            for i, feature1 in enumerate(features):
                for j, feature2 in enumerate(features[i+1:], i+1):
                    # 创建交互特征
                    interaction_feature = X[feature1] * X[feature2]
                    
                    # 分析交互效应
                    X_interaction = np.column_stack([
                        X[feature1].values,
                        X[feature2].values,
                        interaction_feature.values
                    ])
                    
                    model = LinearRegression()
                    model.fit(X_interaction, y)
                    
                    y_pred = model.predict(X_interaction)
                    r2 = r2_score(y, y_pred)
                    
                    # 计算交互项的显著性
                    interaction_coef = model.coef_[2]
                    interaction_significance = self._calculate_interaction_significance(
                        X[feature1], X[feature2], interaction_feature, y
                    )
                    
                    pairwise_interactions[f"{feature1}_x_{feature2}"] = {
                        'feature1': feature1,
                        'feature2': feature2,
                        'interaction_coefficient': interaction_coef,
                        'r2': r2,
                        'significance': interaction_significance,
                        'effect_size': abs(interaction_coef) * np.std(interaction_feature)
                    }
            
            interaction_results['pairwise'] = pairwise_interactions
            
            # 2. 高阶交互分析
            higher_order_interactions = self._analyze_higher_order_interactions(X, y)
            interaction_results['higher_order'] = higher_order_interactions
            
            # 3. 条件交互分析
            conditional_interactions = self._analyze_conditional_interactions(X, y)
            interaction_results['conditional'] = conditional_interactions
            
            logger.info(f"交互关系分析完成，发现 {len(pairwise_interactions)} 个两两交互")
            return interaction_results
            
        except Exception as e:
            logger.error(f"交互关系分析失败: {e}")
            return {}
    
    def _analyze_hierarchical_relationships(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析层次关系"""
        try:
            hierarchical_results = {}
            
            # 1. 特征层次分析
            feature_hierarchy = self._build_feature_hierarchy(X, y)
            hierarchical_results['feature_hierarchy'] = feature_hierarchy
            
            # 2. 模型层次分析
            model_hierarchy = self._build_model_hierarchy(X, y)
            hierarchical_results['model_hierarchy'] = model_hierarchy
            
            # 3. 决策层次分析
            decision_hierarchy = self._analyze_decision_hierarchy(X, y)
            hierarchical_results['decision_hierarchy'] = decision_hierarchy
            
            logger.info("层次关系分析完成")
            return hierarchical_results
            
        except Exception as e:
            logger.error(f"层次关系分析失败: {e}")
            return {}
    
    def _analyze_causal_relationships(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析因果关系"""
        try:
            causal_results = {}
            
            # 1. 格兰杰因果性检验
            granger_results = {}
            for feature in X.columns:
                granger_test = self._granger_causality_test(X[feature], y)
                granger_results[feature] = granger_test
            
            causal_results['granger'] = granger_results
            
            # 2. 工具变量分析
            iv_results = self._instrumental_variable_analysis(X, y)
            causal_results['instrumental_variables'] = iv_results
            
            # 3. 倾向性评分匹配
            psm_results = self._propensity_score_matching(X, y)
            causal_results['propensity_score'] = psm_results
            
            logger.info("因果关系分析完成")
            return causal_results
            
        except Exception as e:
            logger.error(f"因果关系分析失败: {e}")
            return {}
    
    def _detect_nonlinear_patterns(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """检测非线性模式"""
        try:
            patterns = {}
            
            for feature in X.columns:
                feature_values = X[feature].values
                y_values = y.values
                
                # 1. 分段线性模式
                piecewise_pattern = self._detect_piecewise_pattern(feature_values, y_values)
                patterns[f"{feature}_piecewise"] = piecewise_pattern
                
                # 2. 周期性模式
                cyclical_pattern = self._detect_cyclical_pattern(feature_values, y_values)
                patterns[f"{feature}_cyclical"] = cyclical_pattern
                
                # 3. 阈值模式
                threshold_pattern = self._detect_threshold_pattern(feature_values, y_values)
                patterns[f"{feature}_threshold"] = threshold_pattern
            
            return patterns
            
        except Exception as e:
            logger.error(f"非线性模式检测失败: {e}")
            return {}
    
    def _detect_piecewise_pattern(self, x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """检测分段线性模式"""
        try:
            # 使用决策树找到最优分割点
            from sklearn.tree import DecisionTreeRegressor
            
            X_reshaped = x.reshape(-1, 1)
            tree = DecisionTreeRegressor(max_depth=3, random_state=42)
            tree.fit(X_reshaped, y)
            
            # 提取分割点
            thresholds = tree.tree_.threshold[tree.tree_.threshold != -2]
            
            if len(thresholds) > 0:
                return {
                    'type': 'piecewise',
                    'thresholds': thresholds.tolist(),
                    'n_segments': len(thresholds) + 1,
                    'r2': tree.score(X_reshaped, y)
                }
            else:
                return {'type': 'linear', 'thresholds': [], 'n_segments': 1, 'r2': 0}
                
        except Exception as e:
            logger.error(f"分段模式检测失败: {e}")
            return {'type': 'unknown', 'thresholds': [], 'n_segments': 1, 'r2': 0}
    
    def _detect_cyclical_pattern(self, x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """检测周期性模式"""
        try:
            # 使用FFT检测周期性
            fft = np.fft.fft(y)
            freqs = np.fft.fftfreq(len(y))
            
            # 找到主要频率
            power = np.abs(fft)**2
            dominant_freq_idx = np.argmax(power[1:len(power)//2]) + 1
            dominant_freq = freqs[dominant_freq_idx]
            
            if abs(dominant_freq) > 0.01:  # 有意义的频率
                period = 1 / abs(dominant_freq)
                return {
                    'type': 'cyclical',
                    'period': period,
                    'frequency': dominant_freq,
                    'power': power[dominant_freq_idx]
                }
            else:
                return {'type': 'non_cyclical', 'period': 0, 'frequency': 0, 'power': 0}
                
        except Exception as e:
            logger.error(f"周期性模式检测失败: {e}")
            return {'type': 'unknown', 'period': 0, 'frequency': 0, 'power': 0}
    
    def _detect_threshold_pattern(self, x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """检测阈值模式"""
        try:
            # 使用分位数作为候选阈值
            thresholds = np.percentile(x, [25, 50, 75])
            best_threshold = None
            best_r2 = 0
            
            for threshold in thresholds:
                # 创建分段特征
                segment1_mask = x <= threshold
                segment2_mask = x > threshold
                
                if np.sum(segment1_mask) > 5 and np.sum(segment2_mask) > 5:
                    # 拟合分段模型
                    X_segment1 = x[segment1_mask].reshape(-1, 1)
                    y_segment1 = y[segment1_mask]
                    X_segment2 = x[segment2_mask].reshape(-1, 1)
                    y_segment2 = y[segment2_mask]
                    
                    model1 = LinearRegression()
                    model2 = LinearRegression()
                    
                    model1.fit(X_segment1, y_segment1)
                    model2.fit(X_segment2, y_segment2)
                    
                    # 计算整体R²
                    y_pred1 = model1.predict(X_segment1)
                    y_pred2 = model2.predict(X_segment2)
                    
                    y_pred = np.concatenate([y_pred1, y_pred2])
                    y_true = np.concatenate([y_segment1, y_segment2])
                    
                    r2 = r2_score(y_true, y_pred)
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_threshold = threshold
            
            if best_threshold is not None:
                return {
                    'type': 'threshold',
                    'threshold': best_threshold,
                    'r2': best_r2,
                    'n_segments': 2
                }
            else:
                return {'type': 'no_threshold', 'threshold': 0, 'r2': 0, 'n_segments': 1}
                
        except Exception as e:
            logger.error(f"阈值模式检测失败: {e}")
            return {'type': 'unknown', 'threshold': 0, 'r2': 0, 'n_segments': 1}
    
    def _analyze_higher_order_interactions(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析高阶交互"""
        try:
            higher_order_results = {}
            
            # 三阶交互分析
            features = X.columns.tolist()
            triple_interactions = {}
            
            for i, f1 in enumerate(features):
                for j, f2 in enumerate(features[i+1:], i+1):
                    for k, f3 in enumerate(features[j+1:], j+1):
                        # 创建三阶交互特征
                        triple_feature = X[f1] * X[f2] * X[f3]
                        
                        # 分析三阶交互效应
                        X_triple = np.column_stack([
                            X[f1].values,
                            X[f2].values,
                            X[f3].values,
                            triple_feature.values
                        ])
                        
                        model = LinearRegression()
                        model.fit(X_triple, y)
                        
                        y_pred = model.predict(X_triple)
                        r2 = r2_score(y, y_pred)
                        
                        triple_interactions[f"{f1}_x_{f2}_x_{f3}"] = {
                            'features': [f1, f2, f3],
                            'interaction_coefficient': model.coef_[3],
                            'r2': r2,
                            'effect_size': abs(model.coef_[3]) * np.std(triple_feature)
                        }
            
            higher_order_results['triple'] = triple_interactions
            
            return higher_order_results
            
        except Exception as e:
            logger.error(f"高阶交互分析失败: {e}")
            return {}
    
    def _analyze_conditional_interactions(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析条件交互"""
        try:
            conditional_results = {}
            
            # 基于分位数的条件交互
            features = X.columns.tolist()
            
            for f1 in features:
                for f2 in features:
                    if f1 != f2:
                        # 基于f1的中位数分割
                        median_f1 = X[f1].median()
                        high_f1_mask = X[f1] > median_f1
                        low_f1_mask = X[f1] <= median_f1
                        
                        # 高f1条件下的f2效应
                        if np.sum(high_f1_mask) > 5:
                            X_high = X[high_f1_mask][f2].values.reshape(-1, 1)
                            y_high = y[high_f1_mask]
                            
                            model_high = LinearRegression()
                            model_high.fit(X_high, y_high)
                            
                            y_pred_high = model_high.predict(X_high)
                            r2_high = r2_score(y_high, y_pred_high)
                            
                            conditional_results[f"{f2}_given_high_{f1}"] = {
                                'condition': f'high_{f1}',
                                'coefficient': model_high.coef_[0],
                                'r2': r2_high,
                                'n_samples': len(y_high)
                            }
                        
                        # 低f1条件下的f2效应
                        if np.sum(low_f1_mask) > 5:
                            X_low = X[low_f1_mask][f2].values.reshape(-1, 1)
                            y_low = y[low_f1_mask]
                            
                            model_low = LinearRegression()
                            model_low.fit(X_low, y_low)
                            
                            y_pred_low = model_low.predict(X_low)
                            r2_low = r2_score(y_low, y_pred_low)
                            
                            conditional_results[f"{f2}_given_low_{f1}"] = {
                                'condition': f'low_{f1}',
                                'coefficient': model_low.coef_[0],
                                'r2': r2_low,
                                'n_samples': len(y_low)
                            }
            
            return conditional_results
            
        except Exception as e:
            logger.error(f"条件交互分析失败: {e}")
            return {}
    
    def _build_feature_hierarchy(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """构建特征层次"""
        try:
            # 使用随机森林计算特征重要性
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X, y)
            
            feature_importance = dict(zip(X.columns, rf_model.feature_importances_))
            
            # 按重要性排序
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            # 构建层次结构
            hierarchy = {
                'level_1': sorted_features[:len(sorted_features)//3],  # 高重要性
                'level_2': sorted_features[len(sorted_features)//3:2*len(sorted_features)//3],  # 中重要性
                'level_3': sorted_features[2*len(sorted_features)//3:],  # 低重要性
                'feature_importance': feature_importance
            }
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"特征层次构建失败: {e}")
            return {}
    
    def _build_model_hierarchy(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """构建模型层次"""
        try:
            model_hierarchy = {}
            
            # 简单模型
            simple_models = {}
            
            # 线性回归
            lr_model = LinearRegression()
            lr_model.fit(X, y)
            y_pred_lr = lr_model.predict(X)
            
            simple_models['linear_regression'] = {
                'r2': r2_score(y, y_pred_lr),
                'mse': mean_squared_error(y, y_pred_lr),
                'complexity': 'low'
            }
            
            # 多项式回归（2次）
            from sklearn.preprocessing import PolynomialFeatures
            poly_features = PolynomialFeatures(degree=2, include_bias=False)
            X_poly = poly_features.fit_transform(X)
            
            poly_model = LinearRegression()
            poly_model.fit(X_poly, y)
            y_pred_poly = poly_model.predict(X_poly)
            
            simple_models['polynomial_regression'] = {
                'r2': r2_score(y, y_pred_poly),
                'mse': mean_squared_error(y, y_pred_poly),
                'complexity': 'medium'
            }
            
            model_hierarchy['simple'] = simple_models
            
            # 复杂模型
            complex_models = {}
            
            # 随机森林
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X, y)
            y_pred_rf = rf_model.predict(X)
            
            complex_models['random_forest'] = {
                'r2': r2_score(y, y_pred_rf),
                'mse': mean_squared_error(y, y_pred_rf),
                'complexity': 'high'
            }
            
            # 神经网络
            mlp_model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
            mlp_model.fit(X, y)
            y_pred_mlp = mlp_model.predict(X)
            
            complex_models['neural_network'] = {
                'r2': r2_score(y, y_pred_mlp),
                'mse': mean_squared_error(y, y_pred_mlp),
                'complexity': 'high'
            }
            
            model_hierarchy['complex'] = complex_models
            
            return model_hierarchy
            
        except Exception as e:
            logger.error(f"模型层次构建失败: {e}")
            return {}
    
    def _analyze_decision_hierarchy(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """分析决策层次"""
        try:
            decision_hierarchy = {}
            
            # 使用决策树分析决策路径
            from sklearn.tree import DecisionTreeRegressor, export_text
            
            tree_model = DecisionTreeRegressor(max_depth=5, random_state=42)
            tree_model.fit(X, y)
            
            # 提取决策路径
            tree_rules = export_text(tree_model, feature_names=X.columns.tolist())
            
            decision_hierarchy['decision_tree'] = {
                'rules': tree_rules,
                'depth': tree_model.get_depth(),
                'n_leaves': tree_model.get_n_leaves(),
                'r2': tree_model.score(X, y)
            }
            
            # 分析决策重要性
            feature_importance = dict(zip(X.columns, tree_model.feature_importances_))
            decision_hierarchy['decision_importance'] = feature_importance
            
            return decision_hierarchy
            
        except Exception as e:
            logger.error(f"决策层次分析失败: {e}")
            return {}
    
    def _granger_causality_test(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """格兰杰因果性检验"""
        try:
            # 简化的格兰杰因果性检验
            max_lag = min(5, len(x) // 4)
            
            causality_results = {}
            
            for lag in range(1, max_lag + 1):
                if len(x) > lag:
                    # 准备数据
                    x_lagged = x[:-lag].values
                    y_current = y[lag:].values
                    
                    if len(x_lagged) > 10:
                        # 无约束模型
                        X_unrestricted = np.column_stack([x_lagged, y_current[:-1] if len(y_current) > 1 else x_lagged[:-1]])
                        y_unrestricted = y_current[1:] if len(y_current) > 1 else y_current[1:]
                        
                        if len(X_unrestricted) > 5:
                            model_unrestricted = LinearRegression()
                            model_unrestricted.fit(X_unrestricted, y_unrestricted)
                            r2_unrestricted = model_unrestricted.score(X_unrestricted, y_unrestricted)
                            
                            # 约束模型
                            X_restricted = y_current[:-1].reshape(-1, 1) if len(y_current) > 1 else x_lagged[:-1].reshape(-1, 1)
                            y_restricted = y_current[1:] if len(y_current) > 1 else y_current[1:]
                            
                            if len(X_restricted) > 5:
                                model_restricted = LinearRegression()
                                model_restricted.fit(X_restricted, y_restricted)
                                r2_restricted = model_restricted.score(X_restricted, y_restricted)
                                
                                # F统计量
                                n = len(y_unrestricted)
                                k = X_unrestricted.shape[1]
                                f_stat = ((r2_unrestricted - r2_restricted) / 1) / ((1 - r2_unrestricted) / (n - k))
                                
                                causality_results[f'lag_{lag}'] = {
                                    'f_statistic': f_stat,
                                    'r2_unrestricted': r2_unrestricted,
                                    'r2_restricted': r2_restricted,
                                    'causality': f_stat > 2.0  # 简化的显著性判断
                                }
            
            return causality_results
            
        except Exception as e:
            logger.error(f"格兰杰因果性检验失败: {e}")
            return {}
    
    def _instrumental_variable_analysis(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """工具变量分析"""
        try:
            # 简化的工具变量分析
            iv_results = {}
            
            for feature in X.columns:
                # 使用其他特征作为工具变量
                other_features = [f for f in X.columns if f != feature]
                
                if len(other_features) > 0:
                    # 第一阶段：用工具变量预测内生变量
                    X_iv = X[other_features].values
                    y_endogenous = X[feature].values
                    
                    model_stage1 = LinearRegression()
                    model_stage1.fit(X_iv, y_endogenous)
                    y_pred_stage1 = model_stage1.predict(X_iv)
                    
                    # 第二阶段：用预测值回归目标变量
                    model_stage2 = LinearRegression()
                    model_stage2.fit(y_pred_stage1.reshape(-1, 1), y)
                    y_pred_stage2 = model_stage2.predict(y_pred_stage1.reshape(-1, 1))
                    
                    iv_results[feature] = {
                        'stage1_r2': model_stage1.score(X_iv, y_endogenous),
                        'stage2_r2': model_stage2.score(y_pred_stage1.reshape(-1, 1), y),
                        'iv_coefficient': model_stage2.coef_[0],
                        'iv_intercept': model_stage2.intercept_
                    }
            
            return iv_results
            
        except Exception as e:
            logger.error(f"工具变量分析失败: {e}")
            return {}
    
    def _propensity_score_matching(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """倾向性评分匹配"""
        try:
            # 简化的倾向性评分匹配
            psm_results = {}
            
            # 创建二分类目标（基于中位数）
            y_median = y.median()
            y_binary = (y > y_median).astype(int)
            
            # 计算倾向性评分
            from sklearn.linear_model import LogisticRegression
            
            logit_model = LogisticRegression(random_state=42)
            logit_model.fit(X, y_binary)
            propensity_scores = logit_model.predict_proba(X)[:, 1]
            
            psm_results['propensity_scores'] = {
                'mean_score': np.mean(propensity_scores),
                'std_score': np.std(propensity_scores),
                'min_score': np.min(propensity_scores),
                'max_score': np.max(propensity_scores)
            }
            
            # 基于倾向性评分的匹配效果
            matched_pairs = self._create_matched_pairs(propensity_scores, y_binary)
            psm_results['matching'] = matched_pairs
            
            return psm_results
            
        except Exception as e:
            logger.error(f"倾向性评分匹配失败: {e}")
            return {}
    
    def _create_matched_pairs(self, propensity_scores: np.ndarray, y_binary: np.ndarray) -> Dict[str, Any]:
        """创建匹配对"""
        try:
            # 简化的匹配算法
            treatment_indices = np.where(y_binary == 1)[0]
            control_indices = np.where(y_binary == 0)[0]
            
            matched_pairs = []
            used_controls = set()
            
            for treat_idx in treatment_indices:
                treat_score = propensity_scores[treat_idx]
                
                # 找到最接近的控制组
                best_control = None
                best_distance = float('inf')
                
                for control_idx in control_indices:
                    if control_idx not in used_controls:
                        control_score = propensity_scores[control_idx]
                        distance = abs(treat_score - control_score)
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_control = control_idx
                
                if best_control is not None and best_distance < 0.1:  # 匹配阈值
                    matched_pairs.append({
                        'treatment': treat_idx,
                        'control': best_control,
                        'distance': best_distance
                    })
                    used_controls.add(best_control)
            
            return {
                'n_pairs': len(matched_pairs),
                'matching_rate': len(matched_pairs) / len(treatment_indices),
                'avg_distance': np.mean([pair['distance'] for pair in matched_pairs]) if matched_pairs else 0
            }
            
        except Exception as e:
            logger.error(f"匹配对创建失败: {e}")
            return {'n_pairs': 0, 'matching_rate': 0, 'avg_distance': 0}
    
    def _calculate_interaction_significance(self, x1: pd.Series, x2: pd.Series, 
                                          interaction: pd.Series, y: pd.Series) -> float:
        """计算交互项显著性"""
        try:
            # 使用t检验计算交互项的显著性
            X_interaction = np.column_stack([
                x1.values,
                x2.values,
                interaction.values
            ])
            
            model = LinearRegression()
            model.fit(X_interaction, y)
            
            # 计算标准误差
            y_pred = model.predict(X_interaction)
            residuals = y - y_pred
            mse = np.mean(residuals**2)
            
            # 简化的标准误差计算
            n = len(y)
            se_interaction = np.sqrt(mse / n)
            
            # t统计量
            t_stat = model.coef_[2] / se_interaction
            
            # p值（简化计算）
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 3))
            
            return 1 - p_value  # 返回显著性水平
            
        except Exception as e:
            logger.error(f"交互项显著性计算失败: {e}")
            return 0.0
    
    def _calculate_relationship_score(self, results: Dict[str, Any]) -> float:
        """计算综合关系评分"""
        try:
            score = 0.0
            weights = {
                'linear': 0.2,
                'nonlinear': 0.3,
                'interaction': 0.25,
                'hierarchical': 0.15,
                'causal': 0.1
            }
            
            # 线性关系评分
            if 'linear' in results and results['linear']:
                linear_score = self._calculate_linear_score(results['linear'])
                score += weights['linear'] * linear_score
            
            # 非线性关系评分
            if 'nonlinear' in results and results['nonlinear']:
                nonlinear_score = self._calculate_nonlinear_score(results['nonlinear'])
                score += weights['nonlinear'] * nonlinear_score
            
            # 交互关系评分
            if 'interaction' in results and results['interaction']:
                interaction_score = self._calculate_interaction_score(results['interaction'])
                score += weights['interaction'] * interaction_score
            
            # 层次关系评分
            if 'hierarchical' in results and results['hierarchical']:
                hierarchical_score = self._calculate_hierarchical_score(results['hierarchical'])
                score += weights['hierarchical'] * hierarchical_score
            
            # 因果关系评分
            if 'causal' in results and results['causal']:
                causal_score = self._calculate_causal_score(results['causal'])
                score += weights['causal'] * causal_score
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"关系评分计算失败: {e}")
            return 0.0
    
    def _calculate_linear_score(self, linear_results: Dict[str, Any]) -> float:
        """计算线性关系评分"""
        try:
            if 'multiple_linear' in linear_results:
                r2 = linear_results['multiple_linear']['r2']
                return min(r2, 1.0)
            return 0.0
        except Exception as e:
            logger.error(f"线性关系评分计算失败: {e}")
            return 0.0
    
    def _calculate_nonlinear_score(self, nonlinear_results: Dict[str, Any]) -> float:
        """计算非线性关系评分"""
        try:
            score = 0.0
            
            if 'tree_models' in nonlinear_results:
                tree_models = nonlinear_results['tree_models']
                if 'random_forest' in tree_models:
                    score += tree_models['random_forest']['r2'] * 0.5
                if 'gradient_boosting' in tree_models:
                    score += tree_models['gradient_boosting']['r2'] * 0.5
            
            return min(score, 1.0)
        except Exception as e:
            logger.error(f"非线性关系评分计算失败: {e}")
            return 0.0
    
    def _calculate_interaction_score(self, interaction_results: Dict[str, Any]) -> float:
        """计算交互关系评分"""
        try:
            if 'pairwise' in interaction_results:
                pairwise_interactions = interaction_results['pairwise']
                if pairwise_interactions:
                    avg_r2 = np.mean([interaction['r2'] for interaction in pairwise_interactions.values()])
                    return min(avg_r2, 1.0)
            return 0.0
        except Exception as e:
            logger.error(f"交互关系评分计算失败: {e}")
            return 0.0
    
    def _calculate_hierarchical_score(self, hierarchical_results: Dict[str, Any]) -> float:
        """计算层次关系评分"""
        try:
            if 'feature_hierarchy' in hierarchical_results:
                hierarchy = hierarchical_results['feature_hierarchy']
                if 'feature_importance' in hierarchy:
                    importance_values = list(hierarchy['feature_importance'].values())
                    if importance_values:
                        return min(np.mean(importance_values) * 2, 1.0)  # 放大重要性
            return 0.0
        except Exception as e:
            logger.error(f"层次关系评分计算失败: {e}")
            return 0.0
    
    def _calculate_causal_score(self, causal_results: Dict[str, Any]) -> float:
        """计算因果关系评分"""
        try:
            if 'granger' in causal_results:
                granger_results = causal_results['granger']
                causal_count = 0
                total_count = 0
                
                for feature_results in granger_results.values():
                    for lag_result in feature_results.values():
                        if isinstance(lag_result, dict) and 'causality' in lag_result:
                            total_count += 1
                            if lag_result['causality']:
                                causal_count += 1
                
                if total_count > 0:
                    return causal_count / total_count
            return 0.0
        except Exception as e:
            logger.error(f"因果关系评分计算失败: {e}")
            return 0.0
    
    def create_relationship_features(self, X: pd.DataFrame, 
                                   relationship_threshold: float = 0.1) -> pd.DataFrame:
        """创建关系特征"""
        try:
            X_enhanced = X.copy()
            
            # 基于交互关系创建特征
            if 'interaction' in self.relationship_scores:
                interaction_results = self.relationship_scores['interaction']
                
                if 'pairwise' in interaction_results:
                    for interaction_name, interaction_data in interaction_results['pairwise'].items():
                        if interaction_data['r2'] > relationship_threshold:
                            feature1 = interaction_data['feature1']
                            feature2 = interaction_data['feature2']
                            
                            # 创建交互特征
                            X_enhanced[f"{feature1}_x_{feature2}"] = X[feature1] * X[feature2]
                            
                            # 创建比率特征
                            if X[feature2].min() > 0:
                                X_enhanced[f"{feature1}_div_{feature2}"] = X[feature1] / X[feature2]
            
            # 基于非线性模式创建特征
            if 'nonlinear' in self.relationship_scores:
                nonlinear_results = self.relationship_scores['nonlinear']
                
                if 'patterns' in nonlinear_results:
                    for pattern_name, pattern_data in nonlinear_results['patterns'].items():
                        if pattern_data.get('type') == 'threshold' and pattern_data.get('r2', 0) > relationship_threshold:
                            feature_name = pattern_name.split('_threshold')[0]
                            threshold = pattern_data['threshold']
                            
                            # 创建阈值特征
                            X_enhanced[f"{feature_name}_above_threshold"] = (X[feature_name] > threshold).astype(int)
            
            logger.info(f"关系特征创建完成，新增 {len(X_enhanced.columns) - len(X.columns)} 个特征")
            return X_enhanced
            
        except Exception as e:
            logger.error(f"关系特征创建失败: {e}")
            return X
    
    def get_relationship_insights(self) -> Dict[str, Any]:
        """获取关系分析洞察"""
        try:
            insights = {
                'overall_relationship_score': self.relationship_scores.get('overall_score', 0),
                'relationship_level': self._classify_relationship_level(
                    self.relationship_scores.get('overall_score', 0)
                ),
                'key_relationships': self._extract_key_relationships(),
                'recommendations': self._generate_relationship_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"关系分析洞察获取失败: {e}")
            return {}
    
    def _classify_relationship_level(self, score: float) -> str:
        """分类关系水平"""
        if score >= 0.8:
            return "高复杂度关系"
        elif score >= 0.6:
            return "中等复杂度关系"
        elif score >= 0.4:
            return "低复杂度关系"
        else:
            return "简单关系"
    
    def _extract_key_relationships(self) -> List[Dict[str, Any]]:
        """提取关键关系"""
        try:
            key_relationships = []
            
            # 从线性关系中提取
            if 'linear' in self.relationship_scores:
                linear_results = self.relationship_scores['linear']
                if 'multiple_linear' in linear_results:
                    multiple_linear = linear_results['multiple_linear']
                    if multiple_linear['r2'] > 0.3:
                        key_relationships.append({
                            'type': 'linear',
                            'r2': multiple_linear['r2'],
                            'description': f"多元线性关系，R² = {multiple_linear['r2']:.3f}"
                        })
            
            # 从交互关系中提取
            if 'interaction' in self.relationship_scores:
                interaction_results = self.relationship_scores['interaction']
                if 'pairwise' in interaction_results:
                    for interaction_name, interaction_data in interaction_results['pairwise'].items():
                        if interaction_data['r2'] > 0.2:
                            key_relationships.append({
                                'type': 'interaction',
                                'features': [interaction_data['feature1'], interaction_data['feature2']],
                                'r2': interaction_data['r2'],
                                'description': f"{interaction_data['feature1']} × {interaction_data['feature2']} 交互效应"
                            })
            
            # 从因果关系中提取
            if 'causal' in self.relationship_scores:
                causal_results = self.relationship_scores['causal']
                if 'granger' in causal_results:
                    for feature, granger_data in causal_results['granger'].items():
                        for lag_name, lag_data in granger_data.items():
                            if isinstance(lag_data, dict) and lag_data.get('causality', False):
                                key_relationships.append({
                                    'type': 'causal',
                                    'feature': feature,
                                    'lag': lag_name,
                                    'description': f"{feature} 对目标变量的格兰杰因果关系"
                                })
            
            # 按重要性排序
            key_relationships.sort(key=lambda x: x.get('r2', 0), reverse=True)
            
            return key_relationships[:10]
            
        except Exception as e:
            logger.error(f"关键关系提取失败: {e}")
            return []
    
    def _generate_relationship_recommendations(self) -> List[str]:
        """生成关系分析建议"""
        try:
            recommendations = []
            
            relationship_score = self.relationship_scores.get('overall_score', 0)
            
            if relationship_score >= 0.8:
                recommendations.append("检测到高复杂度关系，建议使用集成模型")
                recommendations.append("考虑使用深度学习模型处理复杂交互")
                recommendations.append("建议进行特征工程和特征选择")
            elif relationship_score >= 0.6:
                recommendations.append("检测到中等复杂度关系，建议使用树模型")
                recommendations.append("考虑添加交互特征")
                recommendations.append("建议使用正则化方法防止过拟合")
            elif relationship_score >= 0.4:
                recommendations.append("检测到低复杂度关系，建议使用线性模型")
                recommendations.append("考虑添加多项式特征")
                recommendations.append("建议进行特征重要性分析")
            else:
                recommendations.append("检测到简单关系，建议使用基础线性模型")
                recommendations.append("建议进行特征相关性分析")
                recommendations.append("考虑数据预处理和标准化")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"关系分析建议生成失败: {e}")
            return []
    
    def generate_relationship_report(self) -> Dict[str, Any]:
        """生成关系分析报告"""
        try:
            report = {
                'summary': {
                    'overall_score': self.relationship_scores.get('overall_score', 0),
                    'relationship_level': self._classify_relationship_level(
                        self.relationship_scores.get('overall_score', 0)
                    ),
                    'analysis_timestamp': pd.Timestamp.now().isoformat()
                },
                'detailed_results': self.relationship_scores,
                'insights': self.get_relationship_insights(),
                'recommendations': self._generate_relationship_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"关系分析报告生成失败: {e}")
            return {}