"""
权重验证算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, validation_curve
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.optimize import minimize
import logging
from ..logging_config import get_logger

logger = get_logger("weight_validation")

class WeightValidation:
    """权重验证算法"""
    
    def __init__(self):
        self.validation_results = {}
        self.validation_metrics = {}
        self.weight_performance = {}
        self.validation_history = []
    
    def validate_weights(self, X: pd.DataFrame, y: pd.Series, 
                        weights: Dict[str, float],
                        validation_methods: List[str] = None) -> Dict[str, Any]:
        """验证权重"""
        try:
            if validation_methods is None:
                validation_methods = ['cross_validation', 'bootstrap', 'holdout', 'statistical']
            
            results = {}
            
            # 1. 交叉验证
            if 'cross_validation' in validation_methods:
                cv_results = self._cross_validation_validation(X, y, weights)
                results['cross_validation'] = cv_results
            
            # 2. Bootstrap验证
            if 'bootstrap' in validation_methods:
                bootstrap_results = self._bootstrap_validation(X, y, weights)
                results['bootstrap'] = bootstrap_results
            
            # 3. 留出法验证
            if 'holdout' in validation_methods:
                holdout_results = self._holdout_validation(X, y, weights)
                results['holdout'] = holdout_results
            
            # 4. 统计验证
            if 'statistical' in validation_methods:
                statistical_results = self._statistical_validation(X, y, weights)
                results['statistical'] = statistical_results
            
            # 5. 综合验证评分
            overall_score = self._calculate_validation_score(results)
            results['overall_score'] = overall_score
            
            # 6. 记录验证历史
            self.validation_history.append({
                'timestamp': pd.Timestamp.now(),
                'weights': weights,
                'methods': validation_methods,
                'results': results,
                'overall_score': overall_score
            })
            
            self.validation_results = results
            logger.info(f"权重验证完成，整体评分: {overall_score:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"权重验证失败: {e}")
            raise
    
    def _cross_validation_validation(self, X: pd.DataFrame, y: pd.Series, 
                                   weights: Dict[str, float]) -> Dict[str, Any]:
        """交叉验证验证"""
        try:
            cv_results = {}
            
            # 应用权重
            weights_array = np.array([weights.get(feature, 0) for feature in X.columns])
            X_weighted = X * weights_array
            
            # 交叉验证
            cv_scores = cross_val_score(
                LinearRegression(), X_weighted, y, 
                cv=5, scoring='neg_mean_squared_error'
            )
            
            cv_results['cv_scores'] = -cv_scores.tolist()  # 转换为正数
            cv_results['mean_cv_score'] = -cv_scores.mean()
            cv_results['std_cv_score'] = cv_scores.std()
            cv_results['cv_score_range'] = [cv_scores.min(), cv_scores.max()]
            
            # 计算R²交叉验证
            cv_r2_scores = cross_val_score(
                LinearRegression(), X_weighted, y, 
                cv=5, scoring='r2'
            )
            
            cv_results['cv_r2_scores'] = cv_r2_scores.tolist()
            cv_results['mean_cv_r2'] = cv_r2_scores.mean()
            cv_results['std_cv_r2'] = cv_r2_scores.std()
            
            # 计算MAE交叉验证
            cv_mae_scores = cross_val_score(
                LinearRegression(), X_weighted, y, 
                cv=5, scoring='neg_mean_absolute_error'
            )
            
            cv_results['cv_mae_scores'] = -cv_mae_scores.tolist()
            cv_results['mean_cv_mae'] = -cv_mae_scores.mean()
            cv_results['std_cv_mae'] = cv_mae_scores.std()
            
            logger.info("交叉验证验证完成")
            return cv_results
            
        except Exception as e:
            logger.error(f"交叉验证验证失败: {e}")
            return {}
    
    def _bootstrap_validation(self, X: pd.DataFrame, y: pd.Series, 
                             weights: Dict[str, float]) -> Dict[str, Any]:
        """Bootstrap验证"""
        try:
            bootstrap_results = {}
            
            # Bootstrap参数
            n_bootstrap = 100
            bootstrap_scores = []
            bootstrap_r2_scores = []
            bootstrap_mae_scores = []
            
            # 应用权重
            weights_array = np.array([weights.get(feature, 0) for feature in X.columns])
            
            for i in range(n_bootstrap):
                # 生成Bootstrap样本
                bootstrap_indices = np.random.choice(
                    len(X), size=len(X), replace=True
                )
                
                X_bootstrap = X.iloc[bootstrap_indices]
                y_bootstrap = y.iloc[bootstrap_indices]
                
                # 应用权重
                X_weighted = X_bootstrap * weights_array
                
                # 训练模型
                model = LinearRegression()
                model.fit(X_weighted, y_bootstrap)
                
                # 预测
                y_pred = model.predict(X_weighted)
                
                # 计算指标
                mse = mean_squared_error(y_bootstrap, y_pred)
                r2 = r2_score(y_bootstrap, y_pred)
                mae = mean_absolute_error(y_bootstrap, y_pred)
                
                bootstrap_scores.append(mse)
                bootstrap_r2_scores.append(r2)
                bootstrap_mae_scores.append(mae)
            
            bootstrap_results['bootstrap_scores'] = bootstrap_scores
            bootstrap_results['mean_bootstrap_score'] = np.mean(bootstrap_scores)
            bootstrap_results['std_bootstrap_score'] = np.std(bootstrap_scores)
            bootstrap_results['bootstrap_ci'] = [
                np.percentile(bootstrap_scores, 2.5),
                np.percentile(bootstrap_scores, 97.5)
            ]
            
            bootstrap_results['bootstrap_r2_scores'] = bootstrap_r2_scores
            bootstrap_results['mean_bootstrap_r2'] = np.mean(bootstrap_r2_scores)
            bootstrap_results['std_bootstrap_r2'] = np.std(bootstrap_r2_scores)
            
            bootstrap_results['bootstrap_mae_scores'] = bootstrap_mae_scores
            bootstrap_results['mean_bootstrap_mae'] = np.mean(bootstrap_mae_scores)
            bootstrap_results['std_bootstrap_mae'] = np.std(bootstrap_mae_scores)
            
            logger.info("Bootstrap验证完成")
            return bootstrap_results
            
        except Exception as e:
            logger.error(f"Bootstrap验证失败: {e}")
            return {}
    
    def _holdout_validation(self, X: pd.DataFrame, y: pd.Series, 
                          weights: Dict[str, float]) -> Dict[str, Any]:
        """留出法验证"""
        try:
            holdout_results = {}
            
            # 分割数据
            split_ratio = 0.8
            split_idx = int(len(X) * split_ratio)
            
            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = y.iloc[:split_idx]
            y_test = y.iloc[split_idx:]
            
            # 应用权重
            weights_array = np.array([weights.get(feature, 0) for feature in X.columns])
            X_train_weighted = X_train * weights_array
            X_test_weighted = X_test * weights_array
            
            # 训练模型
            model = LinearRegression()
            model.fit(X_train_weighted, y_train)
            
            # 预测
            y_train_pred = model.predict(X_train_weighted)
            y_test_pred = model.predict(X_test_weighted)
            
            # 计算指标
            train_mse = mean_squared_error(y_train, y_train_pred)
            test_mse = mean_squared_error(y_test, y_test_pred)
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            train_mae = mean_absolute_error(y_train, y_train_pred)
            test_mae = mean_absolute_error(y_test, y_test_pred)
            
            holdout_results['train_scores'] = {
                'mse': train_mse,
                'r2': train_r2,
                'mae': train_mae
            }
            
            holdout_results['test_scores'] = {
                'mse': test_mse,
                'r2': test_r2,
                'mae': test_mae
            }
            
            holdout_results['overfitting_ratio'] = test_mse / train_mse if train_mse > 0 else float('inf')
            holdout_results['generalization_gap'] = test_mse - train_mse
            
            logger.info("留出法验证完成")
            return holdout_results
            
        except Exception as e:
            logger.error(f"留出法验证失败: {e}")
            return {}
    
    def _statistical_validation(self, X: pd.DataFrame, y: pd.Series, 
                              weights: Dict[str, float]) -> Dict[str, Any]:
        """统计验证"""
        try:
            statistical_results = {}
            
            # 应用权重
            weights_array = np.array([weights.get(feature, 0) for feature in X.columns])
            X_weighted = X * weights_array
            
            # 训练模型
            model = LinearRegression()
            model.fit(X_weighted, y)
            
            # 预测
            y_pred = model.predict(X_weighted)
            residuals = y - y_pred
            
            # 1. 残差分析
            residual_analysis = self._analyze_residuals(residuals)
            statistical_results['residual_analysis'] = residual_analysis
            
            # 2. 权重显著性检验
            weight_significance = self._test_weight_significance(X_weighted, y, weights)
            statistical_results['weight_significance'] = weight_significance
            
            # 3. 模型假设检验
            model_assumptions = self._test_model_assumptions(X_weighted, y, residuals)
            statistical_results['model_assumptions'] = model_assumptions
            
            # 4. 权重稳定性检验
            weight_stability = self._test_weight_stability(X, y, weights)
            statistical_results['weight_stability'] = weight_stability
            
            logger.info("统计验证完成")
            return statistical_results
            
        except Exception as e:
            logger.error(f"统计验证失败: {e}")
            return {}
    
    def _analyze_residuals(self, residuals: pd.Series) -> Dict[str, Any]:
        """分析残差"""
        try:
            residual_analysis = {}
            
            # 1. 残差正态性检验
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            residual_analysis['normality_test'] = {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            }
            
            # 2. 残差自相关检验
            from statsmodels.stats.diagnostic import acorr_ljungbox
            try:
                ljungbox_result = acorr_ljungbox(residuals, lags=10, return_df=True)
                residual_analysis['autocorrelation_test'] = {
                    'ljungbox_statistic': ljungbox_result['lb_stat'].iloc[-1],
                    'ljungbox_p_value': ljungbox_result['lb_pvalue'].iloc[-1],
                    'has_autocorrelation': ljungbox_result['lb_pvalue'].iloc[-1] < 0.05
                }
            except:
                residual_analysis['autocorrelation_test'] = {
                    'ljungbox_statistic': 0,
                    'ljungbox_p_value': 1,
                    'has_autocorrelation': False
                }
            
            # 3. 残差异方差检验
            from statsmodels.stats.diagnostic import het_breuschpagan
            try:
                # 简化的异方差检验
                bp_stat, bp_p, _, _ = het_breuschpagan(residuals, np.ones((len(residuals), 1)))
                residual_analysis['heteroscedasticity_test'] = {
                    'breusch_pagan_statistic': bp_stat,
                    'breusch_pagan_p_value': bp_p,
                    'has_heteroscedasticity': bp_p < 0.05
                }
            except:
                residual_analysis['heteroscedasticity_test'] = {
                    'breusch_pagan_statistic': 0,
                    'breusch_pagan_p_value': 1,
                    'has_heteroscedasticity': False
                }
            
            # 4. 残差统计特征
            residual_analysis['statistics'] = {
                'mean': residuals.mean(),
                'std': residuals.std(),
                'skewness': residuals.skew(),
                'kurtosis': residuals.kurtosis(),
                'min': residuals.min(),
                'max': residuals.max()
            }
            
            return residual_analysis
            
        except Exception as e:
            logger.error(f"残差分析失败: {e}")
            return {}
    
    def _test_weight_significance(self, X_weighted: pd.DataFrame, y: pd.Series, 
                                weights: Dict[str, float]) -> Dict[str, Any]:
        """测试权重显著性"""
        try:
            weight_significance = {}
            
            # 训练模型
            model = LinearRegression()
            model.fit(X_weighted, y)
            
            # 计算标准误差
            y_pred = model.predict(X_weighted)
            residuals = y - y_pred
            mse = np.mean(residuals**2)
            
            # 计算协方差矩阵
            XTX = np.dot(X_weighted.T, X_weighted)
            try:
                XTX_inv = np.linalg.inv(XTX)
                cov_matrix = mse * XTX_inv
                
                # 计算标准误差
                se = np.sqrt(np.diag(cov_matrix))
                
                # t统计量
                t_stats = model.coef_ / se
                
                # p值
                p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), len(y) - len(X_weighted.columns)))
                
                # 为每个特征计算显著性
                for i, feature in enumerate(X_weighted.columns):
                    weight_significance[feature] = {
                        'coefficient': model.coef_[i],
                        'standard_error': se[i],
                        't_statistic': t_stats[i],
                        'p_value': p_values[i],
                        'is_significant': p_values[i] < 0.05,
                        'weight': weights.get(feature, 0)
                    }
                
            except np.linalg.LinAlgError:
                # 如果矩阵不可逆，使用简化方法
                for feature in X_weighted.columns:
                    weight_significance[feature] = {
                        'coefficient': 0,
                        'standard_error': 0,
                        't_statistic': 0,
                        'p_value': 1,
                        'is_significant': False,
                        'weight': weights.get(feature, 0)
                    }
            
            return weight_significance
            
        except Exception as e:
            logger.error(f"权重显著性检验失败: {e}")
            return {}
    
    def _test_model_assumptions(self, X_weighted: pd.DataFrame, y: pd.Series, 
                              residuals: pd.Series) -> Dict[str, Any]:
        """测试模型假设"""
        try:
            model_assumptions = {}
            
            # 1. 线性假设
            linear_assumption = self._test_linearity(X_weighted, y)
            model_assumptions['linearity'] = linear_assumption
            
            # 2. 独立性假设
            independence_assumption = self._test_independence(residuals)
            model_assumptions['independence'] = independence_assumption
            
            # 3. 同方差假设
            homoscedasticity_assumption = self._test_homoscedasticity(X_weighted, residuals)
            model_assumptions['homoscedasticity'] = homoscedasticity_assumption
            
            # 4. 正态性假设
            normality_assumption = self._test_normality(residuals)
            model_assumptions['normality'] = normality_assumption
            
            return model_assumptions
            
        except Exception as e:
            logger.error(f"模型假设检验失败: {e}")
            return {}
    
    def _test_linearity(self, X_weighted: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """测试线性假设"""
        try:
            # 使用残差图测试线性性
            model = LinearRegression()
            model.fit(X_weighted, y)
            y_pred = model.predict(X_weighted)
            residuals = y - y_pred
            
            # 计算残差与预测值的相关性
            correlation = np.corrcoef(y_pred, residuals)[0, 1]
            
            return {
                'residual_prediction_correlation': correlation,
                'is_linear': abs(correlation) < 0.1,
                'linearity_score': 1 - abs(correlation)
            }
            
        except Exception as e:
            logger.error(f"线性假设检验失败: {e}")
            return {'is_linear': False, 'linearity_score': 0}
    
    def _test_independence(self, residuals: pd.Series) -> Dict[str, Any]:
        """测试独立性假设"""
        try:
            # 使用Durbin-Watson检验
            from statsmodels.stats.diagnostic import durbin_watson
            
            dw_stat = durbin_watson(residuals)
            
            # DW统计量解释
            if dw_stat < 1.5:
                independence_level = "positive_autocorrelation"
            elif dw_stat > 2.5:
                independence_level = "negative_autocorrelation"
            else:
                independence_level = "independent"
            
            return {
                'durbin_watson_statistic': dw_stat,
                'independence_level': independence_level,
                'is_independent': 1.5 <= dw_stat <= 2.5,
                'independence_score': 1 - abs(dw_stat - 2) / 2
            }
            
        except Exception as e:
            logger.error(f"独立性假设检验失败: {e}")
            return {'is_independent': False, 'independence_score': 0}
    
    def _test_homoscedasticity(self, X_weighted: pd.DataFrame, residuals: pd.Series) -> Dict[str, Any]:
        """测试同方差假设"""
        try:
            # 使用Breusch-Pagan检验
            from statsmodels.stats.diagnostic import het_breuschpagan
            
            bp_stat, bp_p, _, _ = het_breuschpagan(residuals, X_weighted)
            
            return {
                'breusch_pagan_statistic': bp_stat,
                'breusch_pagan_p_value': bp_p,
                'is_homoscedastic': bp_p > 0.05,
                'homoscedasticity_score': 1 - bp_p
            }
            
        except Exception as e:
            logger.error(f"同方差假设检验失败: {e}")
            return {'is_homoscedastic': False, 'homoscedasticity_score': 0}
    
    def _test_normality(self, residuals: pd.Series) -> Dict[str, Any]:
        """测试正态性假设"""
        try:
            # 使用Shapiro-Wilk检验
            shapiro_stat, shapiro_p = stats.shapiro(residuals)
            
            # 使用Kolmogorov-Smirnov检验
            ks_stat, ks_p = stats.kstest(residuals, 'norm', args=(residuals.mean(), residuals.std()))
            
            return {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'ks_statistic': ks_stat,
                'ks_p_value': ks_p,
                'is_normal': shapiro_p > 0.05 and ks_p > 0.05,
                'normality_score': (1 - shapiro_p) * (1 - ks_p)
            }
            
        except Exception as e:
            logger.error(f"正态性假设检验失败: {e}")
            return {'is_normal': False, 'normality_score': 0}
    
    def _test_weight_stability(self, X: pd.DataFrame, y: pd.Series, 
                             weights: Dict[str, float]) -> Dict[str, Any]:
        """测试权重稳定性"""
        try:
            weight_stability = {}
            
            # 使用Bootstrap测试权重稳定性
            n_bootstrap = 50
            bootstrap_weights = {feature: [] for feature in X.columns}
            
            for i in range(n_bootstrap):
                # 生成Bootstrap样本
                bootstrap_indices = np.random.choice(
                    len(X), size=len(X), replace=True
                )
                
                X_bootstrap = X.iloc[bootstrap_indices]
                y_bootstrap = y.iloc[bootstrap_indices]
                
                # 应用权重
                weights_array = np.array([weights.get(feature, 0) for feature in X.columns])
                X_weighted = X_bootstrap * weights_array
                
                # 训练模型
                model = LinearRegression()
                model.fit(X_weighted, y_bootstrap)
                
                # 记录权重
                for j, feature in enumerate(X.columns):
                    bootstrap_weights[feature].append(model.coef_[j])
            
            # 计算权重稳定性指标
            for feature in X.columns:
                feature_weights = bootstrap_weights[feature]
                weight_stability[feature] = {
                    'mean_weight': np.mean(feature_weights),
                    'std_weight': np.std(feature_weights),
                    'cv_weight': np.std(feature_weights) / (np.mean(feature_weights) + 1e-8),
                    'weight_range': [np.min(feature_weights), np.max(feature_weights)],
                    'original_weight': weights.get(feature, 0),
                    'stability_score': 1 - np.std(feature_weights) / (np.mean(feature_weights) + 1e-8)
                }
            
            return weight_stability
            
        except Exception as e:
            logger.error(f"权重稳定性检验失败: {e}")
            return {}
    
    def _calculate_validation_score(self, results: Dict[str, Any]) -> float:
        """计算综合验证评分"""
        try:
            score = 0.0
            weights = {
                'cross_validation': 0.3,
                'bootstrap': 0.25,
                'holdout': 0.25,
                'statistical': 0.2
            }
            
            # 交叉验证评分
            if 'cross_validation' in results and results['cross_validation']:
                cv_results = results['cross_validation']
                if 'mean_cv_r2' in cv_results:
                    score += weights['cross_validation'] * max(0, cv_results['mean_cv_r2'])
            
            # Bootstrap评分
            if 'bootstrap' in results and results['bootstrap']:
                bootstrap_results = results['bootstrap']
                if 'mean_bootstrap_r2' in bootstrap_results:
                    score += weights['bootstrap'] * max(0, bootstrap_results['mean_bootstrap_r2'])
            
            # 留出法评分
            if 'holdout' in results and results['holdout']:
                holdout_results = results['holdout']
                if 'test_scores' in holdout_results and 'r2' in holdout_results['test_scores']:
                    score += weights['holdout'] * max(0, holdout_results['test_scores']['r2'])
            
            # 统计验证评分
            if 'statistical' in results and results['statistical']:
                statistical_results = results['statistical']
                statistical_score = self._calculate_statistical_score(statistical_results)
                score += weights['statistical'] * statistical_score
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"验证评分计算失败: {e}")
            return 0.0
    
    def _calculate_statistical_score(self, statistical_results: Dict[str, Any]) -> float:
        """计算统计验证评分"""
        try:
            score = 0.0
            
            # 残差分析评分
            if 'residual_analysis' in statistical_results:
                residual_analysis = statistical_results['residual_analysis']
                if 'normality_test' in residual_analysis:
                    if residual_analysis['normality_test']['is_normal']:
                        score += 0.25
            
            # 模型假设评分
            if 'model_assumptions' in statistical_results:
                model_assumptions = statistical_results['model_assumptions']
                
                if 'linearity' in model_assumptions and model_assumptions['linearity']['is_linear']:
                    score += 0.25
                
                if 'independence' in model_assumptions and model_assumptions['independence']['is_independent']:
                    score += 0.25
                
                if 'homoscedasticity' in model_assumptions and model_assumptions['homoscedasticity']['is_homoscedastic']:
                    score += 0.25
            
            return score
            
        except Exception as e:
            logger.error(f"统计验证评分计算失败: {e}")
            return 0.0
    
    def compare_weight_sets(self, X: pd.DataFrame, y: pd.Series, 
                           weight_sets: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """比较多组权重"""
        try:
            comparison_results = {}
            
            # 验证每组权重
            for weight_set_name, weights in weight_sets.items():
                validation_results = self.validate_weights(X, y, weights)
                comparison_results[weight_set_name] = {
                    'weights': weights,
                    'validation_results': validation_results,
                    'overall_score': validation_results.get('overall_score', 0)
                }
            
            # 排序比较
            sorted_weight_sets = sorted(
                comparison_results.items(),
                key=lambda x: x[1]['overall_score'],
                reverse=True
            )
            
            comparison_results['ranking'] = [
                {
                    'rank': i + 1,
                    'weight_set_name': name,
                    'overall_score': results['overall_score']
                }
                for i, (name, results) in enumerate(sorted_weight_sets)
            ]
            
            # 最佳权重集
            if sorted_weight_sets:
                best_weight_set = sorted_weight_sets[0]
                comparison_results['best_weight_set'] = {
                    'name': best_weight_set[0],
                    'weights': best_weight_set[1]['weights'],
                    'score': best_weight_set[1]['overall_score']
                }
            
            logger.info(f"权重集比较完成，比较了 {len(weight_sets)} 组权重")
            return comparison_results
            
        except Exception as e:
            logger.error(f"权重集比较失败: {e}")
            return {}
    
    def get_validation_insights(self) -> Dict[str, Any]:
        """获取验证洞察"""
        try:
            insights = {
                'validation_summary': self._summarize_validation_results(),
                'weight_performance': self._analyze_weight_performance(),
                'validation_trends': self._analyze_validation_trends(),
                'recommendations': self._generate_validation_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"验证洞察获取失败: {e}")
            return {}
    
    def _summarize_validation_results(self) -> Dict[str, Any]:
        """总结验证结果"""
        try:
            summary = {
                'total_validations': len(self.validation_history),
                'average_score': 0,
                'best_score': 0,
                'worst_score': 1,
                'validation_methods_used': set()
            }
            
            if self.validation_history:
                scores = [validation['overall_score'] for validation in self.validation_history]
                summary['average_score'] = np.mean(scores)
                summary['best_score'] = max(scores)
                summary['worst_score'] = min(scores)
                
                for validation in self.validation_history:
                    summary['validation_methods_used'].update(validation['methods'])
            
            return summary
            
        except Exception as e:
            logger.error(f"验证结果总结失败: {e}")
            return {}
    
    def _analyze_weight_performance(self) -> Dict[str, Any]:
        """分析权重性能"""
        try:
            performance_analysis = {}
            
            if self.validation_history:
                # 分析权重分布
                all_weights = {}
                for validation in self.validation_history:
                    for feature, weight in validation['weights'].items():
                        if feature not in all_weights:
                            all_weights[feature] = []
                        all_weights[feature].append(weight)
                
                # 计算每个特征的权重统计
                feature_stats = {}
                for feature, weights in all_weights.items():
                    feature_stats[feature] = {
                        'mean_weight': np.mean(weights),
                        'std_weight': np.std(weights),
                        'min_weight': np.min(weights),
                        'max_weight': np.max(weights),
                        'weight_range': np.max(weights) - np.min(weights)
                    }
                
                performance_analysis['feature_weight_stats'] = feature_stats
                
                # 分析权重与性能的关系
                weight_performance_correlation = {}
                for feature in all_weights.keys():
                    weights = all_weights[feature]
                    scores = [validation['overall_score'] for validation in self.validation_history]
                    
                    if len(weights) == len(scores):
                        correlation = np.corrcoef(weights, scores)[0, 1]
                        weight_performance_correlation[feature] = {
                            'correlation': correlation,
                            'correlation_strength': abs(correlation),
                            'is_positive': correlation > 0
                        }
                
                performance_analysis['weight_performance_correlation'] = weight_performance_correlation
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"权重性能分析失败: {e}")
            return {}
    
    def _analyze_validation_trends(self) -> Dict[str, Any]:
        """分析验证趋势"""
        try:
            trends_analysis = {}
            
            if len(self.validation_history) > 1:
                # 时间趋势
                timestamps = [validation['timestamp'] for validation in self.validation_history]
                scores = [validation['overall_score'] for validation in self.validation_history]
                
                # 计算趋势
                if len(scores) > 1:
                    trend_slope = np.polyfit(range(len(scores)), scores, 1)[0]
                    trend_direction = "improving" if trend_slope > 0 else "declining" if trend_slope < 0 else "stable"
                    
                    trends_analysis['score_trend'] = {
                        'slope': trend_slope,
                        'direction': trend_direction,
                        'trend_strength': abs(trend_slope)
                    }
                
                # 方法使用趋势
                method_usage = {}
                for validation in self.validation_history:
                    for method in validation['methods']:
                        if method not in method_usage:
                            method_usage[method] = 0
                        method_usage[method] += 1
                
                trends_analysis['method_usage'] = method_usage
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"验证趋势分析失败: {e}")
            return {}
    
    def _generate_validation_recommendations(self) -> List[str]:
        """生成验证建议"""
        try:
            recommendations = []
            
            if self.validation_history:
                # 基于平均分数生成建议
                avg_score = np.mean([validation['overall_score'] for validation in self.validation_history])
                
                if avg_score < 0.3:
                    recommendations.append("验证分数较低，建议重新优化权重")
                    recommendations.append("检查数据质量和模型假设")
                elif avg_score < 0.6:
                    recommendations.append("验证分数中等，建议使用正则化方法")
                    recommendations.append("考虑使用集成方法提高稳定性")
                else:
                    recommendations.append("验证分数较高，权重表现良好")
                    recommendations.append("建议定期重新验证权重")
                
                # 基于趋势生成建议
                if len(self.validation_history) > 1:
                    scores = [validation['overall_score'] for validation in self.validation_history]
                    if scores[-1] < scores[0]:
                        recommendations.append("验证分数呈下降趋势，建议检查数据变化")
                    elif scores[-1] > scores[0]:
                        recommendations.append("验证分数呈上升趋势，权重优化效果良好")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"验证建议生成失败: {e}")
            return []
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        try:
            report = {
                'summary': {
                    'validation_timestamp': pd.Timestamp.now().isoformat(),
                    'total_validations': len(self.validation_history),
                    'current_validation_score': self.validation_results.get('overall_score', 0)
                },
                'current_validation': self.validation_results,
                'insights': self.get_validation_insights(),
                'validation_history': self.validation_history
            }
            
            return report
            
        except Exception as e:
            logger.error(f"验证报告生成失败: {e}")
            return {}