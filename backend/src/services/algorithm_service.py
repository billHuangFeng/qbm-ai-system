"""
核心算法服务
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from ..algorithms import (
    SynergyAnalysis, ThresholdAnalysis, LagAnalysis, AdvancedRelationshipAnalysis,
    DynamicWeightCalculator, WeightOptimizer, WeightValidator, WeightMonitor
)
from ..logging_config import get_logger

logger = get_logger("algorithm_service")

class AlgorithmService:
    """核心算法服务"""
    
    def __init__(self):
        self.synergy_analysis = SynergyAnalysis()
        self.threshold_analysis = ThresholdAnalysis()
        self.lag_analysis = LagAnalysis()
        self.advanced_relationships = AdvancedRelationshipAnalysis()
        self.dynamic_weights = DynamicWeightCalculator()
        self.weight_optimizer = WeightOptimizer()
        self.weight_validator = WeightValidator()
        self.weight_monitor = WeightMonitor()
        
        self.analysis_results = {}
        self.optimization_history = {}
        self.monitoring_data = {}
    
    def analyze_data_relationships(self, X: pd.DataFrame, y: pd.Series, 
                                 analysis_types: List[str] = None) -> Dict[str, Any]:
        """分析数据关系"""
        try:
            if analysis_types is None:
                analysis_types = ['synergy', 'threshold', 'lag', 'advanced']
            
            analysis_results = {}
            
            # 1. 协同效应分析
            if 'synergy' in analysis_types:
                synergy_results = self.synergy_analysis.detect_synergy_effects(X, y)
                analysis_results['synergy'] = synergy_results
                
                # 创建协同效应特征
                X_synergy = self.synergy_analysis.create_synergy_features(X)
                analysis_results['synergy_features'] = X_synergy
            
            # 2. 阈值效应分析
            if 'threshold' in analysis_types:
                threshold_results = self.threshold_analysis.detect_threshold_effects(X, y)
                analysis_results['threshold'] = threshold_results
                
                # 创建阈值特征
                X_threshold = self.threshold_analysis.create_threshold_features(X)
                analysis_results['threshold_features'] = X_threshold
            
            # 3. 时间滞后分析
            if 'lag' in analysis_types:
                lag_results = self.lag_analysis.detect_lag_effects(X, y)
                analysis_results['lag'] = lag_results
                
                # 创建滞后特征
                X_lag = self.lag_analysis.create_lag_features(X)
                analysis_results['lag_features'] = X_lag
            
            # 4. 高级关系识别
            if 'advanced' in analysis_types:
                advanced_results = self.advanced_relationships.identify_advanced_relationships(X, y)
                analysis_results['advanced'] = advanced_results
            
            # 5. 综合特征工程
            X_enhanced = self._create_enhanced_features(X, analysis_results)
            analysis_results['enhanced_features'] = X_enhanced
            
            # 6. 综合分析评分
            overall_score = self._calculate_analysis_score(analysis_results)
            analysis_results['overall_score'] = overall_score
            
            self.analysis_results = analysis_results
            logger.info(f"数据关系分析完成，综合评分: {overall_score:.4f}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"数据关系分析失败: {e}")
            raise
    
    def optimize_weights(self, X: pd.DataFrame, y: pd.Series, 
                       optimization_method: str = 'comprehensive',
                       validation_methods: List[str] = None) -> Dict[str, Any]:
        """优化权重"""
        try:
            if validation_methods is None:
                validation_methods = ['cross_validation', 'bootstrap', 'stability']
            
            optimization_results = {}
            
            # 1. 计算动态权重
            dynamic_weights = self.dynamic_weights.calculate_dynamic_weights(
                X, y, method='comprehensive'
            )
            optimization_results['dynamic_weights'] = dynamic_weights
            
            # 2. 权重优化
            optimized_weights = self.weight_optimizer.optimize_weights(
                X, y, method=optimization_method
            )
            optimization_results['optimized_weights'] = optimized_weights
            
            # 3. 权重验证
            if 'final' in dynamic_weights.get('normalized', {}):
                final_weights = dynamic_weights['normalized']['final']
            else:
                final_weights = optimized_weights.get('best_result', {}).get('weights', {})
            
            validation_results = self.weight_validator.validate_weights(
                X, y, final_weights, validation_methods
            )
            optimization_results['validation'] = validation_results
            
            # 4. 权重监控
            monitoring_results = self.weight_monitor.monitor_weights(
                X, y, final_weights
            )
            optimization_results['monitoring'] = monitoring_results
            
            # 5. 综合优化评分
            overall_score = self._calculate_optimization_score(optimization_results)
            optimization_results['overall_score'] = overall_score
            
            self.optimization_history[optimization_method] = optimization_results
            logger.info(f"权重优化完成，综合评分: {overall_score:.4f}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"权重优化失败: {e}")
            raise
    
    def predict_with_optimized_weights(self, X: pd.DataFrame, y: pd.Series, 
                                     X_test: pd.DataFrame, 
                                     weights: Dict[str, float]) -> Dict[str, Any]:
        """使用优化权重进行预测"""
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
            
            # 应用权重
            X_weighted = self._apply_weights(X, weights)
            X_test_weighted = self._apply_weights(X_test, weights)
            
            # 训练多个模型
            models = {
                'linear_regression': LinearRegression(),
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
            }
            
            predictions = {}
            model_performance = {}
            
            for model_name, model in models.items():
                # 训练模型
                model.fit(X_weighted, y)
                
                # 预测
                y_pred = model.predict(X_test_weighted)
                predictions[model_name] = y_pred.tolist()
                
                # 评估性能（如果有测试标签）
                if hasattr(y, 'iloc') and len(y) > 0:
                    # 使用部分训练数据进行验证
                    n_val = min(20, len(y) // 4)
                    X_val = X_weighted.iloc[:n_val]
                    y_val = y.iloc[:n_val]
                    X_train = X_weighted.iloc[n_val:]
                    y_train = y.iloc[n_val:]
                    
                    model.fit(X_train, y_train)
                    y_val_pred = model.predict(X_val)
                    
                    model_performance[model_name] = {
                        'r2_score': r2_score(y_val, y_val_pred),
                        'mse': mean_squared_error(y_val, y_val_pred),
                        'mae': mean_absolute_error(y_val, y_val_pred)
                    }
            
            # 集成预测
            ensemble_prediction = np.mean([pred for pred in predictions.values()], axis=0)
            predictions['ensemble'] = ensemble_prediction.tolist()
            
            return {
                'predictions': predictions,
                'model_performance': model_performance,
                'weights_used': weights,
                'feature_importance': self._calculate_feature_importance(weights)
            }
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise
    
    def get_algorithm_insights(self) -> Dict[str, Any]:
        """获取算法洞察"""
        try:
            insights = {
                'analysis_results': self.analysis_results,
                'optimization_history': self.optimization_history,
                'monitoring_data': self.monitoring_data,
                'recommendations': self._generate_algorithm_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"算法洞察获取失败: {e}")
            return {}
    
    def _create_enhanced_features(self, X: pd.DataFrame, 
                                analysis_results: Dict[str, Any]) -> pd.DataFrame:
        """创建增强特征"""
        try:
            X_enhanced = X.copy()
            
            # 添加协同效应特征
            if 'synergy_features' in analysis_results:
                synergy_features = analysis_results['synergy_features']
                for col in synergy_features.columns:
                    if col not in X_enhanced.columns:
                        X_enhanced[col] = synergy_features[col]
            
            # 添加阈值特征
            if 'threshold_features' in analysis_results:
                threshold_features = analysis_results['threshold_features']
                for col in threshold_features.columns:
                    if col not in X_enhanced.columns:
                        X_enhanced[col] = threshold_features[col]
            
            # 添加滞后特征
            if 'lag_features' in analysis_results:
                lag_features = analysis_results['lag_features']
                for col in lag_features.columns:
                    if col not in X_enhanced.columns:
                        X_enhanced[col] = lag_features[col]
            
            logger.info(f"增强特征创建完成，从 {len(X.columns)} 个特征增加到 {len(X_enhanced.columns)} 个特征")
            return X_enhanced
            
        except Exception as e:
            logger.error(f"增强特征创建失败: {e}")
            return X
    
    def _apply_weights(self, X: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """应用权重到特征"""
        try:
            X_weighted = X.copy()
            for feature, weight in weights.items():
                if feature in X_weighted.columns:
                    X_weighted[feature] = X_weighted[feature] * weight
            return X_weighted
            
        except Exception as e:
            logger.error(f"权重应用失败: {e}")
            return X
    
    def _calculate_analysis_score(self, analysis_results: Dict[str, Any]) -> float:
        """计算分析评分"""
        try:
            score = 0.0
            weights = {'synergy': 0.3, 'threshold': 0.3, 'lag': 0.2, 'advanced': 0.2}
            
            # 协同效应评分
            if 'synergy' in analysis_results:
                synergy_score = analysis_results['synergy'].get('overall_score', 0)
                score += weights['synergy'] * synergy_score
            
            # 阈值效应评分
            if 'threshold' in analysis_results:
                threshold_score = analysis_results['threshold'].get('overall_score', 0)
                score += weights['threshold'] * threshold_score
            
            # 滞后效应评分
            if 'lag' in analysis_results:
                lag_score = analysis_results['lag'].get('overall_score', 0)
                score += weights['lag'] * lag_score
            
            # 高级关系评分
            if 'advanced' in analysis_results:
                advanced_score = analysis_results['advanced'].get('overall_score', 0)
                score += weights['advanced'] * advanced_score
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"分析评分计算失败: {e}")
            return 0.0
    
    def _calculate_optimization_score(self, optimization_results: Dict[str, Any]) -> float:
        """计算优化评分"""
        try:
            score = 0.0
            weights = {'dynamic_weights': 0.3, 'optimized_weights': 0.3, 'validation': 0.2, 'monitoring': 0.2}
            
            # 动态权重评分
            if 'dynamic_weights' in optimization_results:
                dynamic_score = optimization_results['dynamic_weights'].get('overall_score', 0)
                score += weights['dynamic_weights'] * dynamic_score
            
            # 优化权重评分
            if 'optimized_weights' in optimization_results:
                optimized_score = optimization_results['optimized_weights'].get('best_result', {}).get('r2_score', 0)
                score += weights['optimized_weights'] * optimized_score
            
            # 验证评分
            if 'validation' in optimization_results:
                validation_score = optimization_results['validation'].get('overall_score', 0)
                score += weights['validation'] * validation_score
            
            # 监控评分
            if 'monitoring' in optimization_results:
                monitoring_score = optimization_results['monitoring'].get('overall_score', 0)
                score += weights['monitoring'] * monitoring_score
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"优化评分计算失败: {e}")
            return 0.0
    
    def _calculate_feature_importance(self, weights: Dict[str, float]) -> Dict[str, Any]:
        """计算特征重要性"""
        try:
            if not weights:
                return {}
            
            # 归一化权重
            total_weight = sum(weights.values())
            if total_weight > 0:
                normalized_weights = {k: v/total_weight for k, v in weights.items()}
            else:
                normalized_weights = weights
            
            # 计算重要性统计
            weight_values = list(normalized_weights.values())
            
            return {
                'weights': normalized_weights,
                'max_weight': max(weight_values),
                'min_weight': min(weight_values),
                'mean_weight': np.mean(weight_values),
                'std_weight': np.std(weight_values),
                'weight_range': max(weight_values) - min(weight_values)
            }
            
        except Exception as e:
            logger.error(f"特征重要性计算失败: {e}")
            return {}
    
    def _generate_algorithm_recommendations(self) -> List[str]:
        """生成算法建议"""
        try:
            recommendations = []
            
            # 基于分析结果的建议
            if self.analysis_results:
                overall_score = self.analysis_results.get('overall_score', 0)
                
                if overall_score >= 0.8:
                    recommendations.append("数据关系分析结果优秀，建议采用当前分析结果")
                    recommendations.append("建议定期更新分析以保持模型性能")
                elif overall_score >= 0.6:
                    recommendations.append("数据关系分析结果良好，建议进一步优化")
                    recommendations.append("考虑使用更复杂的特征工程方法")
                elif overall_score >= 0.4:
                    recommendations.append("数据关系分析结果一般，建议重新评估数据质量")
                    recommendations.append("考虑使用不同的分析方法")
                else:
                    recommendations.append("数据关系分析结果较差，建议检查数据预处理")
                    recommendations.append("考虑使用更简单的模型")
            
            # 基于优化历史的建议
            if self.optimization_history:
                recommendations.append("建议建立自动化的权重优化机制")
                recommendations.append("建议定期监控权重变化和模型性能")
            
            # 通用建议
            recommendations.append("建议使用多种算法进行交叉验证")
            recommendations.append("建议建立模型性能基准和监控体系")
            recommendations.append("建议定期更新和优化算法参数")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"算法建议生成失败: {e}")
            return []

