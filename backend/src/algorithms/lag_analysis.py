"""
时间滞后分析算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
import logging
from ..logging_config import get_logger

logger = get_logger("lag_analysis")

class LagAnalysis:
    """时间滞后分析"""
    
    def __init__(self):
        self.lag_effects = {}
        self.optimal_lags = {}
        self.lag_models = {}
    
    def detect_lag_effects(self, X: pd.DataFrame, y: pd.Series, 
                          max_lag: int = 12, min_correlation: float = 0.1) -> Dict[str, Any]:
        """检测时间滞后效应"""
        try:
            lag_results = {}
            
            # 1. 交叉相关分析
            cross_correlation = self._analyze_cross_correlation(X, y, max_lag, min_correlation)
            lag_results['cross_correlation'] = cross_correlation
            
            # 2. 滞后回归分析
            lag_regression = self._analyze_lag_regression(X, y, max_lag)
            lag_results['lag_regression'] = lag_regression
            
            # 3. 格兰杰因果性检验
            granger_causality = self._analyze_granger_causality(X, y, max_lag)
            lag_results['granger_causality'] = granger_causality
            
            # 4. 最优滞后选择
            optimal_lags = self._select_optimal_lags(X, y, max_lag)
            lag_results['optimal_lags'] = optimal_lags
            
            # 5. 综合滞后效应评分
            lag_score = self._calculate_lag_score(lag_results)
            lag_results['overall_score'] = lag_score
            
            self.lag_effects = lag_results
            logger.info(f"时间滞后效应分析完成，整体评分: {lag_score:.4f}")
            
            return lag_results
            
        except Exception as e:
            logger.error(f"时间滞后效应检测失败: {e}")
            raise
    
    def _analyze_cross_correlation(self, X: pd.DataFrame, y: pd.Series, 
                                  max_lag: int, min_correlation: float) -> Dict[str, Any]:
        """分析交叉相关"""
        try:
            cross_corr_results = {}
            
            for feature in X.columns:
                feature_values = X[feature].values
                y_values = y.values
                
                # 计算不同滞后的相关系数
                correlations = []
                lags = []
                
                for lag in range(0, max_lag + 1):
                    if len(feature_values) > lag:
                        # 滞后特征值
                        lagged_feature = feature_values[:-lag] if lag > 0 else feature_values
                        # 对应的目标值
                        corresponding_y = y_values[lag:] if lag > 0 else y_values
                        
                        if len(lagged_feature) > 10:  # 确保有足够的样本
                            correlation = np.corrcoef(lagged_feature, corresponding_y)[0, 1]
                            
                            if not np.isnan(correlation) and abs(correlation) >= min_correlation:
                                correlations.append(correlation)
                                lags.append(lag)
                
                if correlations:
                    # 找到最大相关系数对应的滞后
                    max_corr_idx = np.argmax(np.abs(correlations))
                    optimal_lag = lags[max_corr_idx]
                    max_correlation = correlations[max_corr_idx]
                    
                    cross_corr_results[feature] = {
                        'correlations': dict(zip(lags, correlations)),
                        'optimal_lag': optimal_lag,
                        'max_correlation': max_correlation,
                        'lag_significance': self._calculate_lag_significance(
                            feature_values, y_values, optimal_lag
                        )
                    }
            
            logger.info(f"交叉相关分析完成，发现 {len(cross_corr_results)} 个特征的滞后效应")
            return cross_corr_results
            
        except Exception as e:
            logger.error(f"交叉相关分析失败: {e}")
            return {}
    
    def _analyze_lag_regression(self, X: pd.DataFrame, y: pd.Series, 
                              max_lag: int) -> Dict[str, Any]:
        """分析滞后回归"""
        try:
            lag_regression_results = {}
            
            for feature in X.columns:
                feature_values = X[feature].values
                y_values = y.values
                
                # 测试不同滞后的回归性能
                lag_performance = {}
                
                for lag in range(0, max_lag + 1):
                    if len(feature_values) > lag:
                        # 准备滞后数据
                        lagged_feature = feature_values[:-lag] if lag > 0 else feature_values
                        corresponding_y = y_values[lag:] if lag > 0 else y_values
                        
                        if len(lagged_feature) > 10:
                            # 训练回归模型
                            X_lag = lagged_feature.reshape(-1, 1)
                            model = LinearRegression()
                            model.fit(X_lag, corresponding_y)
                            
                            # 计算性能指标
                            y_pred = model.predict(X_lag)
                            r2 = r2_score(corresponding_y, y_pred)
                            mse = mean_squared_error(corresponding_y, y_pred)
                            
                            lag_performance[lag] = {
                                'r2': r2,
                                'mse': mse,
                                'coefficient': model.coef_[0],
                                'intercept': model.intercept_
                            }
                
                if lag_performance:
                    # 找到最佳滞后
                    best_lag = max(lag_performance.keys(), key=lambda k: lag_performance[k]['r2'])
                    best_performance = lag_performance[best_lag]
                    
                    lag_regression_results[feature] = {
                        'lag_performance': lag_performance,
                        'best_lag': best_lag,
                        'best_r2': best_performance['r2'],
                        'best_mse': best_performance['mse'],
                        'coefficient': best_performance['coefficient']
                    }
            
            logger.info(f"滞后回归分析完成，发现 {len(lag_regression_results)} 个特征的最佳滞后")
            return lag_regression_results
            
        except Exception as e:
            logger.error(f"滞后回归分析失败: {e}")
            return {}
    
    def _analyze_granger_causality(self, X: pd.DataFrame, y: pd.Series, 
                                 max_lag: int) -> Dict[str, Any]:
        """分析格兰杰因果性"""
        try:
            granger_results = {}
            
            for feature in X.columns:
                feature_values = X[feature].values
                y_values = y.values
                
                # 简化的格兰杰因果性检验
                causality_tests = {}
                
                for lag in range(1, max_lag + 1):
                    if len(feature_values) > lag:
                        # 准备数据
                        lagged_feature = feature_values[:-lag]
                        corresponding_y = y_values[lag:]
                        
                        if len(lagged_feature) > 20:  # 确保有足够的样本
                            # 无约束模型（包含滞后特征）
                            X_unrestricted = np.column_stack([
                                lagged_feature,
                                corresponding_y[:-1] if len(corresponding_y) > 1 else lagged_feature[:-1]
                            ])
                            y_unrestricted = corresponding_y[1:] if len(corresponding_y) > 1 else corresponding_y[1:]
                            
                            if len(X_unrestricted) > 10:
                                model_unrestricted = LinearRegression()
                                model_unrestricted.fit(X_unrestricted, y_unrestricted)
                                r2_unrestricted = model_unrestricted.score(X_unrestricted, y_unrestricted)
                                
                                # 约束模型（不包含滞后特征）
                                X_restricted = corresponding_y[:-1].reshape(-1, 1) if len(corresponding_y) > 1 else lagged_feature[:-1].reshape(-1, 1)
                                y_restricted = corresponding_y[1:] if len(corresponding_y) > 1 else corresponding_y[1:]
                                
                                if len(X_restricted) > 10:
                                    model_restricted = LinearRegression()
                                    model_restricted.fit(X_restricted, y_restricted)
                                    r2_restricted = model_restricted.score(X_restricted, y_restricted)
                                    
                                    # F统计量
                                    n = len(y_unrestricted)
                                    k = X_unrestricted.shape[1]
                                    f_stat = ((r2_unrestricted - r2_restricted) / 1) / ((1 - r2_unrestricted) / (n - k))
                                    
                                    # 简化的p值计算
                                    p_value = self._calculate_f_p_value(f_stat, 1, n - k)
                                    
                                    causality_tests[lag] = {
                                        'f_statistic': f_stat,
                                        'p_value': p_value,
                                        'r2_unrestricted': r2_unrestricted,
                                        'r2_restricted': r2_restricted,
                                        'causality': p_value < 0.05
                                    }
                
                if causality_tests:
                    # 找到最显著的滞后
                    significant_lags = {lag: test for lag, test in causality_tests.items() if test['causality']}
                    
                    if significant_lags:
                        best_lag = min(significant_lags.keys(), key=lambda k: significant_lags[k]['p_value'])
                        best_test = significant_lags[best_lag]
                        
                        granger_results[feature] = {
                            'causality_tests': causality_tests,
                            'significant_lags': significant_lags,
                            'best_lag': best_lag,
                            'best_p_value': best_test['p_value'],
                            'best_f_statistic': best_test['f_statistic'],
                            'causality': True
                        }
                    else:
                        granger_results[feature] = {
                            'causality_tests': causality_tests,
                            'significant_lags': {},
                            'causality': False
                        }
            
            logger.info(f"格兰杰因果性分析完成，发现 {len([r for r in granger_results.values() if r['causality']])} 个特征的因果性")
            return granger_results
            
        except Exception as e:
            logger.error(f"格兰杰因果性分析失败: {e}")
            return {}
    
    def _select_optimal_lags(self, X: pd.DataFrame, y: pd.Series, 
                           max_lag: int) -> Dict[str, int]:
        """选择最优滞后"""
        try:
            optimal_lags = {}
            
            for feature in X.columns:
                feature_values = X[feature].values
                y_values = y.values
                
                # 使用AIC准则选择最优滞后
                aic_scores = {}
                
                for lag in range(0, max_lag + 1):
                    if len(feature_values) > lag:
                        lagged_feature = feature_values[:-lag] if lag > 0 else feature_values
                        corresponding_y = y_values[lag:] if lag > 0 else y_values
                        
                        if len(lagged_feature) > 10:
                            # 训练模型
                            X_lag = lagged_feature.reshape(-1, 1)
                            model = LinearRegression()
                            model.fit(X_lag, corresponding_y)
                            
                            # 计算AIC
                            y_pred = model.predict(X_lag)
                            mse = mean_squared_error(corresponding_y, y_pred)
                            n = len(corresponding_y)
                            k = 2  # 截距 + 系数
                            
                            aic = n * np.log(mse) + 2 * k
                            aic_scores[lag] = aic
                
                if aic_scores:
                    optimal_lag = min(aic_scores.keys(), key=lambda k: aic_scores[k])
                    optimal_lags[feature] = optimal_lag
            
            logger.info(f"最优滞后选择完成，为 {len(optimal_lags)} 个特征选择了最优滞后")
            return optimal_lags
            
        except Exception as e:
            logger.error(f"最优滞后选择失败: {e}")
            return {}
    
    def _calculate_lag_significance(self, feature_values: np.ndarray, 
                                  y_values: np.ndarray, lag: int) -> float:
        """计算滞后显著性"""
        try:
            if lag == 0:
                return 1.0
            
            lagged_feature = feature_values[:-lag]
            corresponding_y = y_values[lag:]
            
            if len(lagged_feature) < 10:
                return 0.0
            
            # 计算相关系数
            correlation = np.corrcoef(lagged_feature, corresponding_y)[0, 1]
            
            if np.isnan(correlation):
                return 0.0
            
            # 计算t统计量
            n = len(lagged_feature)
            t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2))
            
            # 计算p值
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            
            return 1 - p_value  # 返回显著性水平
            
        except Exception as e:
            logger.error(f"滞后显著性计算失败: {e}")
            return 0.0
    
    def _calculate_f_p_value(self, f_stat: float, df1: int, df2: int) -> float:
        """计算F统计量的p值"""
        try:
            return 1 - stats.f.cdf(f_stat, df1, df2)
        except Exception as e:
            logger.error(f"F统计量p值计算失败: {e}")
            return 1.0
    
    def _calculate_lag_score(self, lag_results: Dict[str, Any]) -> float:
        """计算综合滞后效应评分"""
        try:
            score = 0.0
            weights = {'cross_correlation': 0.3, 'lag_regression': 0.3, 'granger_causality': 0.4}
            
            # 交叉相关评分
            if 'cross_correlation' in lag_results and lag_results['cross_correlation']:
                cross_corr_count = len(lag_results['cross_correlation'])
                cross_corr_avg = np.mean([
                    data['max_correlation'] for data in lag_results['cross_correlation'].values()
                ])
                score += weights['cross_correlation'] * cross_corr_count * cross_corr_avg
            
            # 滞后回归评分
            if 'lag_regression' in lag_results and lag_results['lag_regression']:
                lag_reg_count = len(lag_results['lag_regression'])
                lag_reg_avg = np.mean([
                    data['best_r2'] for data in lag_results['lag_regression'].values()
                ])
                score += weights['lag_regression'] * lag_reg_count * lag_reg_avg
            
            # 格兰杰因果性评分
            if 'granger_causality' in lag_results and lag_results['granger_causality']:
                granger_count = len([r for r in lag_results['granger_causality'].values() if r['causality']])
                score += weights['granger_causality'] * granger_count * 0.5  # 因果性得分为0.5
            
            return min(score, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            logger.error(f"滞后效应评分计算失败: {e}")
            return 0.0
    
    def create_lag_features(self, X: pd.DataFrame, 
                          lag_threshold: float = 0.1) -> pd.DataFrame:
        """创建滞后特征"""
        try:
            X_enhanced = X.copy()
            
            # 使用最优滞后创建特征
            if 'optimal_lags' in self.lag_effects:
                for feature, optimal_lag in self.lag_effects['optimal_lags'].items():
                    if optimal_lag > 0:
                        # 创建滞后特征
                        lagged_values = X[feature].shift(optimal_lag)
                        X_enhanced[f"{feature}_lag_{optimal_lag}"] = lagged_values
                        
                        # 创建滞后交互特征
                        X_enhanced[f"{feature}_lag_interaction"] = X[feature] * lagged_values
            
            # 使用交叉相关结果创建特征
            if 'cross_correlation' in self.lag_effects:
                for feature, data in self.lag_effects['cross_correlation'].items():
                    optimal_lag = data['optimal_lag']
                    max_correlation = data['max_correlation']
                    
                    if optimal_lag > 0 and abs(max_correlation) > lag_threshold:
                        lagged_values = X[feature].shift(optimal_lag)
                        X_enhanced[f"{feature}_corr_lag_{optimal_lag}"] = lagged_values
            
            # 使用滞后回归结果创建特征
            if 'lag_regression' in self.lag_effects:
                for feature, data in self.lag_effects['lag_regression'].items():
                    best_lag = data['best_lag']
                    best_r2 = data['best_r2']
                    
                    if best_lag > 0 and best_r2 > lag_threshold:
                        lagged_values = X[feature].shift(best_lag)
                        X_enhanced[f"{feature}_reg_lag_{best_lag}"] = lagged_values
            
            logger.info(f"滞后特征创建完成，新增 {len(X_enhanced.columns) - len(X.columns)} 个特征")
            return X_enhanced
            
        except Exception as e:
            logger.error(f"滞后特征创建失败: {e}")
            return X
    
    def get_lag_insights(self) -> Dict[str, Any]:
        """获取滞后效应洞察"""
        try:
            insights = {
                'overall_lag_score': self.lag_effects.get('overall_score', 0),
                'lag_level': self._classify_lag_level(self.lag_effects.get('overall_score', 0)),
                'key_lags': self._extract_key_lags(),
                'recommendations': self._generate_lag_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"滞后效应洞察获取失败: {e}")
            return {}
    
    def _classify_lag_level(self, score: float) -> str:
        """分类滞后效应水平"""
        if score >= 0.7:
            return "高滞后效应"
        elif score >= 0.4:
            return "中等滞后效应"
        elif score >= 0.1:
            return "低滞后效应"
        else:
            return "无显著滞后效应"
    
    def _extract_key_lags(self) -> List[Dict[str, Any]]:
        """提取关键滞后"""
        try:
            key_lags = []
            
            # 从交叉相关中提取
            if 'cross_correlation' in self.lag_effects:
                for feature, data in self.lag_effects['cross_correlation'].items():
                    if abs(data['max_correlation']) > 0.3:
                        key_lags.append({
                            'type': 'cross_correlation',
                            'feature': feature,
                            'lag': data['optimal_lag'],
                            'correlation': data['max_correlation'],
                            'significance': data['lag_significance']
                        })
            
            # 从滞后回归中提取
            if 'lag_regression' in self.lag_effects:
                for feature, data in self.lag_effects['lag_regression'].items():
                    if data['best_r2'] > 0.1:
                        key_lags.append({
                            'type': 'lag_regression',
                            'feature': feature,
                            'lag': data['best_lag'],
                            'r2': data['best_r2'],
                            'coefficient': data['coefficient']
                        })
            
            # 从格兰杰因果性中提取
            if 'granger_causality' in self.lag_effects:
                for feature, data in self.lag_effects['granger_causality'].items():
                    if data['causality']:
                        key_lags.append({
                            'type': 'granger_causality',
                            'feature': feature,
                            'lag': data['best_lag'],
                            'p_value': data['best_p_value'],
                            'f_statistic': data['best_f_statistic']
                        })
            
            # 按重要性排序
            key_lags.sort(key=lambda x: x.get('correlation', x.get('r2', x.get('f_statistic', 0))), reverse=True)
            
            return key_lags[:10]
            
        except Exception as e:
            logger.error(f"关键滞后提取失败: {e}")
            return []
    
    def _generate_lag_recommendations(self) -> List[str]:
        """生成滞后效应建议"""
        try:
            recommendations = []
            
            lag_score = self.lag_effects.get('overall_score', 0)
            
            if lag_score >= 0.7:
                recommendations.append("检测到高滞后效应，建议使用时间序列模型")
                recommendations.append("考虑在模型中包含滞后特征")
            elif lag_score >= 0.4:
                recommendations.append("检测到中等滞后效应，建议添加关键滞后特征")
                recommendations.append("考虑使用ARIMA或VAR模型")
            elif lag_score >= 0.1:
                recommendations.append("检测到低滞后效应，建议进一步分析时间关系")
                recommendations.append("考虑使用滑动窗口特征")
            else:
                recommendations.append("未检测到显著滞后效应，建议使用静态模型")
                recommendations.append("考虑检查数据的时间序列性质")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"滞后效应建议生成失败: {e}")
            return []


