"""
权重优化算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from scipy.optimize import minimize, differential_evolution, dual_annealing
from scipy.optimize import LinearConstraint, NonlinearConstraint
import logging
from ..logging_config import get_logger

logger = get_logger("weight_optimization")

class WeightOptimizer:
    """权重优化器"""
    
    def __init__(self):
        self.optimization_history = {}
        self.best_weights = {}
        self.optimization_metrics = {}
    
    def optimize_weights(self, X: pd.DataFrame, y: pd.Series, 
                        method: str = 'gradient_descent',
                        objective: str = 'r2',
                        constraints: Optional[Dict[str, Any]] = None,
                        max_iterations: int = 1000) -> Dict[str, Any]:
        """优化权重"""
        try:
            optimization_results = {}
            
            # 1. 梯度下降优化
            if method == 'gradient_descent':
                gd_results = self._gradient_descent_optimization(X, y, objective, max_iterations)
                optimization_results['gradient_descent'] = gd_results
            
            # 2. 遗传算法优化
            elif method == 'genetic_algorithm':
                ga_results = self._genetic_algorithm_optimization(X, y, objective, max_iterations)
                optimization_results['genetic_algorithm'] = ga_results
            
            # 3. 模拟退火优化
            elif method == 'simulated_annealing':
                sa_results = self._simulated_annealing_optimization(X, y, objective, max_iterations)
                optimization_results['simulated_annealing'] = sa_results
            
            # 4. 粒子群优化
            elif method == 'particle_swarm':
                pso_results = self._particle_swarm_optimization(X, y, objective, max_iterations)
                optimization_results['particle_swarm'] = pso_results
            
            # 5. 贝叶斯优化
            elif method == 'bayesian':
                bayesian_results = self._bayesian_optimization(X, y, objective, max_iterations)
                optimization_results['bayesian'] = bayesian_results
            
            # 6. 综合优化
            elif method == 'comprehensive':
                comprehensive_results = self._comprehensive_optimization(X, y, objective, max_iterations)
                optimization_results['comprehensive'] = comprehensive_results
            
            # 7. 约束优化
            if constraints:
                constrained_results = self._constrained_optimization(X, y, objective, constraints, max_iterations)
                optimization_results['constrained'] = constrained_results
            
            # 8. 多目标优化
            multi_objective_results = self._multi_objective_optimization(X, y, max_iterations)
            optimization_results['multi_objective'] = multi_objective_results
            
            # 9. 选择最佳结果
            best_result = self._select_best_result(optimization_results)
            optimization_results['best_result'] = best_result
            
            self.optimization_history[method] = optimization_results
            logger.info(f"权重优化完成: {method}, 最佳R² = {best_result.get('r2_score', 0):.4f}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"权重优化失败: {e}")
            raise
    
    def _gradient_descent_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                     objective: str, max_iterations: int) -> Dict[str, Any]:
        """梯度下降优化"""
        try:
            def objective_function(weights):
                weights = np.abs(weights)  # 确保权重为正
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 初始权重
            initial_weights = np.ones(len(X.columns))
            
            # 梯度下降优化
            result = minimize(
                objective_function,
                initial_weights,
                method='L-BFGS-B',
                bounds=[(0.01, 10.0) for _ in range(len(X.columns))],
                options={'maxiter': max_iterations}
            )
            
            # 归一化权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'gradient_descent',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': result.success,
                'iterations': result.nit,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'objective_value': result.fun
            }
            
        except Exception as e:
            logger.error(f"梯度下降优化失败: {e}")
            return {}
    
    def _genetic_algorithm_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                      objective: str, max_iterations: int) -> Dict[str, Any]:
        """遗传算法优化"""
        try:
            def objective_function(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 遗传算法优化
            result = differential_evolution(
                objective_function,
                bounds=[(0.01, 10.0) for _ in range(len(X.columns))],
                maxiter=max_iterations // 10,  # 遗传算法迭代次数较少
                seed=42
            )
            
            # 归一化权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'genetic_algorithm',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': result.success,
                'iterations': result.nit,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'objective_value': result.fun
            }
            
        except Exception as e:
            logger.error(f"遗传算法优化失败: {e}")
            return {}
    
    def _simulated_annealing_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                         objective: str, max_iterations: int) -> Dict[str, Any]:
        """模拟退火优化"""
        try:
            def objective_function(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 模拟退火优化
            result = dual_annealing(
                objective_function,
                bounds=[(0.01, 10.0) for _ in range(len(X.columns))],
                maxiter=max_iterations,
                seed=42
            )
            
            # 归一化权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'simulated_annealing',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': result.success,
                'iterations': result.nit,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'objective_value': result.fun
            }
            
        except Exception as e:
            logger.error(f"模拟退火优化失败: {e}")
            return {}
    
    def _particle_swarm_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                    objective: str, max_iterations: int) -> Dict[str, Any]:
        """粒子群优化"""
        try:
            # 简化的粒子群优化实现
            n_particles = 20
            n_dimensions = len(X.columns)
            
            # 初始化粒子
            particles = np.random.uniform(0.01, 10.0, (n_particles, n_dimensions))
            velocities = np.random.uniform(-1, 1, (n_particles, n_dimensions))
            
            # 个体最佳位置
            personal_best = particles.copy()
            personal_best_scores = np.full(n_particles, np.inf)
            
            # 全局最佳位置
            global_best = particles[0].copy()
            global_best_score = np.inf
            
            def evaluate_particle(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 粒子群优化主循环
            for iteration in range(max_iterations):
                for i in range(n_particles):
                    # 评估粒子
                    score = evaluate_particle(particles[i])
                    
                    # 更新个体最佳
                    if score < personal_best_scores[i]:
                        personal_best_scores[i] = score
                        personal_best[i] = particles[i].copy()
                    
                    # 更新全局最佳
                    if score < global_best_score:
                        global_best_score = score
                        global_best = particles[i].copy()
                
                # 更新粒子和速度
                for i in range(n_particles):
                    # 更新速度
                    r1, r2 = np.random.random(2)
                    velocities[i] = (0.9 * velocities[i] + 
                                    0.5 * r1 * (personal_best[i] - particles[i]) +
                                    0.5 * r2 * (global_best - particles[i]))
                    
                    # 更新位置
                    particles[i] += velocities[i]
                    
                    # 边界约束
                    particles[i] = np.clip(particles[i], 0.01, 10.0)
            
            # 归一化最佳权重
            optimized_weights = global_best
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'particle_swarm',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': True,
                'iterations': max_iterations,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'objective_value': global_best_score
            }
            
        except Exception as e:
            logger.error(f"粒子群优化失败: {e}")
            return {}
    
    def _bayesian_optimization(self, X: pd.DataFrame, y: pd.Series, 
                             objective: str, max_iterations: int) -> Dict[str, Any]:
        """贝叶斯优化"""
        try:
            # 简化的贝叶斯优化实现
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import RBF
            
            def objective_function(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 初始采样
            n_initial = 10
            X_samples = np.random.uniform(0.01, 10.0, (n_initial, len(X.columns)))
            y_samples = np.array([objective_function(x) for x in X_samples])
            
            # 贝叶斯优化主循环
            best_x = X_samples[np.argmin(y_samples)]
            best_y = np.min(y_samples)
            
            for iteration in range(max_iterations - n_initial):
                # 训练高斯过程
                gp = GaussianProcessRegressor(
                    kernel=RBF(length_scale=1.0),
                    random_state=42
                )
                gp.fit(X_samples, y_samples)
                
                # 获取下一个采样点（使用期望改进）
                def acquisition_function(x):
                    x = x.reshape(1, -1)
                    mean, std = gp.predict(x, return_std=True)
                    return -(mean - 1.96 * std)  # 期望改进
                
                # 优化获取函数
                result = minimize(
                    acquisition_function,
                    np.random.uniform(0.01, 10.0, len(X.columns)),
                    method='L-BFGS-B',
                    bounds=[(0.01, 10.0) for _ in range(len(X.columns))]
                )
                
                # 评估新点
                new_x = result.x
                new_y = objective_function(new_x)
                
                # 更新样本
                X_samples = np.vstack([X_samples, new_x])
                y_samples = np.append(y_samples, new_y)
                
                # 更新最佳点
                if new_y < best_y:
                    best_x = new_x
                    best_y = new_y
            
            # 归一化最佳权重
            optimized_weights = best_x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'bayesian',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': True,
                'iterations': max_iterations,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'objective_value': best_y
            }
            
        except Exception as e:
            logger.error(f"贝叶斯优化失败: {e}")
            return {}
    
    def _comprehensive_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                  objective: str, max_iterations: int) -> Dict[str, Any]:
        """综合优化"""
        try:
            # 运行多种优化方法
            methods = ['gradient_descent', 'genetic_algorithm', 'simulated_annealing']
            results = {}
            
            for method in methods:
                if method == 'gradient_descent':
                    results[method] = self._gradient_descent_optimization(X, y, objective, max_iterations)
                elif method == 'genetic_algorithm':
                    results[method] = self._genetic_algorithm_optimization(X, y, objective, max_iterations)
                elif method == 'simulated_annealing':
                    results[method] = self._simulated_annealing_optimization(X, y, objective, max_iterations)
            
            # 选择最佳结果
            best_method = max(results.keys(), key=lambda k: results[k].get('r2_score', 0))
            best_result = results[best_method]
            
            return {
                'method': 'comprehensive',
                'best_method': best_method,
                'all_results': results,
                'weights': best_result['weights'],
                'r2_score': best_result['r2_score'],
                'mse_score': best_result['mse_score']
            }
            
        except Exception as e:
            logger.error(f"综合优化失败: {e}")
            return {}
    
    def _constrained_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                objective: str, constraints: Dict[str, Any],
                                max_iterations: int) -> Dict[str, Any]:
        """约束优化"""
        try:
            def objective_function(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                
                if objective == 'r2':
                    return -model.score(X_weighted, y)
                elif objective == 'mse':
                    y_pred = model.predict(X_weighted)
                    return mean_squared_error(y, y_pred)
                else:
                    return -model.score(X_weighted, y)
            
            # 定义约束
            constraints_list = []
            
            # 权重和约束
            if 'sum_constraint' in constraints:
                sum_value = constraints['sum_constraint']
                constraints_list.append(LinearConstraint(
                    np.ones(len(X.columns)), 
                    sum_value * 0.9, 
                    sum_value * 1.1
                ))
            
            # 权重范围约束
            bounds = [(0.01, 10.0) for _ in range(len(X.columns))]
            if 'weight_bounds' in constraints:
                bounds = constraints['weight_bounds']
            
            # 非线性约束
            if 'nonlinear_constraints' in constraints:
                for constraint_func in constraints['nonlinear_constraints']:
                    constraints_list.append(NonlinearConstraint(
                        constraint_func, 
                        -np.inf, 
                        0
                    ))
            
            # 约束优化
            result = minimize(
                objective_function,
                np.ones(len(X.columns)),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': max_iterations}
            )
            
            # 归一化权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            
            return {
                'method': 'constrained',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': result.success,
                'iterations': result.nit,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, model.predict(X_optimized)),
                'constraints_satisfied': result.success
            }
            
        except Exception as e:
            logger.error(f"约束优化失败: {e}")
            return {}
    
    def _multi_objective_optimization(self, X: pd.DataFrame, y: pd.Series, 
                                    max_iterations: int) -> Dict[str, Any]:
        """多目标优化"""
        try:
            def multi_objective_function(weights):
                weights = np.abs(weights)
                X_weighted = self._apply_weights(X, weights)
                
                model = LinearRegression()
                model.fit(X_weighted, y)
                y_pred = model.predict(X_weighted)
                
                # 多个目标函数
                r2 = model.score(X_weighted, y)
                mse = mean_squared_error(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                
                # 多目标加权和
                return -r2 + 0.1 * mse + 0.01 * mae
            
            # 多目标优化
            result = minimize(
                multi_objective_function,
                np.ones(len(X.columns)),
                method='L-BFGS-B',
                bounds=[(0.01, 10.0) for _ in range(len(X.columns))],
                options={'maxiter': max_iterations}
            )
            
            # 归一化权重
            optimized_weights = result.x
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            # 评估结果
            X_optimized = self._apply_weights(X, optimized_weights)
            model = LinearRegression()
            model.fit(X_optimized, y)
            y_pred = model.predict(X_optimized)
            
            return {
                'method': 'multi_objective',
                'weights': dict(zip(X.columns, optimized_weights)),
                'success': result.success,
                'iterations': result.nit,
                'r2_score': model.score(X_optimized, y),
                'mse_score': mean_squared_error(y, y_pred),
                'mae_score': mean_absolute_error(y, y_pred),
                'objective_value': result.fun
            }
            
        except Exception as e:
            logger.error(f"多目标优化失败: {e}")
            return {}
    
    def _apply_weights(self, X: pd.DataFrame, weights: np.ndarray) -> pd.DataFrame:
        """应用权重到特征"""
        X_weighted = X.copy()
        for i, feature in enumerate(X.columns):
            X_weighted[feature] = X[feature] * weights[i]
        return X_weighted
    
    def _select_best_result(self, optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """选择最佳优化结果"""
        try:
            best_result = None
            best_score = -np.inf
            
            for method, result in optimization_results.items():
                if isinstance(result, dict) and 'r2_score' in result:
                    if result['r2_score'] > best_score:
                        best_score = result['r2_score']
                        best_result = result
            
            if best_result is None:
                # 如果没有找到有效结果，返回默认结果
                best_result = {
                    'method': 'default',
                    'weights': {col: 1.0/len(optimization_results) for col in optimization_results.keys()},
                    'r2_score': 0.0,
                    'mse_score': np.inf
                }
            
            return best_result
            
        except Exception as e:
            logger.error(f"最佳结果选择失败: {e}")
            return {}
    
    def get_optimization_insights(self) -> Dict[str, Any]:
        """获取优化洞察"""
        try:
            insights = {
                'optimization_history': self.optimization_history,
                'best_weights': self.best_weights,
                'optimization_metrics': self.optimization_metrics,
                'recommendations': self._generate_optimization_recommendations()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"优化洞察获取失败: {e}")
            return {}
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """生成优化建议"""
        try:
            recommendations = []
            
            if self.optimization_history:
                recommendations.append("建议定期进行权重优化以保持模型性能")
                recommendations.append("考虑使用多种优化方法进行交叉验证")
                recommendations.append("监控优化结果的一致性，避免过度优化")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"优化建议生成失败: {e}")
            return []

