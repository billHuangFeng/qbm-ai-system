"""
权重优化算法测试
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.algorithms.weight_optimization import WeightOptimizer

class TestWeightOptimizer:
    """权重优化器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.weight_optimizer = WeightOptimizer()
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples)
        })
        
        # 创建有明确权重关系的目标变量
        self.y = pd.Series(
            self.X['feature1'] * 2 + 
            self.X['feature2'] * 1.5 + 
            self.X['feature3'] * 0.5 + 
            np.random.normal(0, 0.1, n_samples)
        )
    
    def test_optimize_weights_gradient_descent(self):
        """测试梯度下降优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent'
        )
        
        assert isinstance(result, dict)
        assert 'gradient_descent' in result
        assert 'best_result' in result
        
        # 检查梯度下降结果
        gd_result = result['gradient_descent']
        assert 'weights' in gd_result
        assert 'success' in gd_result
        assert 'r2_score' in gd_result
        assert 'mse_score' in gd_result
        
        # 检查权重
        weights = gd_result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
        
        # 检查权重和
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 1e-6
    
    def test_optimize_weights_genetic_algorithm(self):
        """测试遗传算法优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='genetic_algorithm'
        )
        
        assert isinstance(result, dict)
        assert 'genetic_algorithm' in result
        
        # 检查遗传算法结果
        ga_result = result['genetic_algorithm']
        assert 'weights' in ga_result
        assert 'success' in ga_result
        assert 'r2_score' in ga_result
        assert 'mse_score' in ga_result
        
        # 检查权重
        weights = ga_result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_optimize_weights_simulated_annealing(self):
        """测试模拟退火优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='simulated_annealing'
        )
        
        assert isinstance(result, dict)
        assert 'simulated_annealing' in result
        
        # 检查模拟退火结果
        sa_result = result['simulated_annealing']
        assert 'weights' in sa_result
        assert 'success' in sa_result
        assert 'r2_score' in sa_result
        assert 'mse_score' in sa_result
        
        # 检查权重
        weights = sa_result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_optimize_weights_particle_swarm(self):
        """测试粒子群优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='particle_swarm'
        )
        
        assert isinstance(result, dict)
        assert 'particle_swarm' in result
        
        # 检查粒子群结果
        pso_result = result['particle_swarm']
        assert 'weights' in pso_result
        assert 'success' in pso_result
        assert 'r2_score' in pso_result
        assert 'mse_score' in pso_result
        
        # 检查权重
        weights = pso_result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_optimize_weights_bayesian(self):
        """测试贝叶斯优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='bayesian'
        )
        
        assert isinstance(result, dict)
        assert 'bayesian' in result
        
        # 检查贝叶斯结果
        bayesian_result = result['bayesian']
        assert 'weights' in bayesian_result
        assert 'success' in bayesian_result
        assert 'r2_score' in bayesian_result
        assert 'mse_score' in bayesian_result
        
        # 检查权重
        weights = bayesian_result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_optimize_weights_comprehensive(self):
        """测试综合优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='comprehensive'
        )
        
        assert isinstance(result, dict)
        assert 'comprehensive' in result
        assert 'best_result' in result
        
        # 检查综合结果
        comprehensive_result = result['comprehensive']
        assert 'best_method' in comprehensive_result
        assert 'all_results' in comprehensive_result
        assert 'weights' in comprehensive_result
        
        # 检查最佳结果
        best_result = result['best_result']
        assert 'weights' in best_result
        assert 'r2_score' in best_result
        assert 'mse_score' in best_result
    
    def test_optimize_weights_constrained(self):
        """测试约束优化"""
        constraints = {
            'sum_constraint': 1.0,
            'weight_bounds': [(0.01, 5.0) for _ in range(len(self.X.columns))]
        }
        
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent', constraints=constraints
        )
        
        assert isinstance(result, dict)
        assert 'constrained' in result
        
        # 检查约束结果
        constrained_result = result['constrained']
        assert 'weights' in constrained_result
        assert 'constraints_satisfied' in constrained_result
    
    def test_optimize_weights_multi_objective(self):
        """测试多目标优化"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent'
        )
        
        assert isinstance(result, dict)
        assert 'multi_objective' in result
        
        # 检查多目标结果
        multi_result = result['multi_objective']
        assert 'weights' in multi_result
        assert 'r2_score' in multi_result
        assert 'mse_score' in multi_result
        assert 'mae_score' in multi_result
    
    def test_gradient_descent_optimization(self):
        """测试梯度下降优化实现"""
        result = self.weight_optimizer._gradient_descent_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_genetic_algorithm_optimization(self):
        """测试遗传算法优化实现"""
        result = self.weight_optimizer._genetic_algorithm_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_simulated_annealing_optimization(self):
        """测试模拟退火优化实现"""
        result = self.weight_optimizer._simulated_annealing_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_particle_swarm_optimization(self):
        """测试粒子群优化实现"""
        result = self.weight_optimizer._particle_swarm_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_bayesian_optimization(self):
        """测试贝叶斯优化实现"""
        result = self.weight_optimizer._bayesian_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'success' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_comprehensive_optimization(self):
        """测试综合优化实现"""
        result = self.weight_optimizer._comprehensive_optimization(
            self.X, self.y, 'r2', 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'best_method' in result
        assert 'all_results' in result
        assert 'weights' in result
        
        # 检查所有结果
        all_results = result['all_results']
        assert isinstance(all_results, dict)
        assert len(all_results) > 0
    
    def test_constrained_optimization(self):
        """测试约束优化实现"""
        constraints = {
            'sum_constraint': 1.0,
            'weight_bounds': [(0.01, 5.0) for _ in range(len(self.X.columns))]
        }
        
        result = self.weight_optimizer._constrained_optimization(
            self.X, self.y, 'r2', constraints, 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'constraints_satisfied' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_multi_objective_optimization(self):
        """测试多目标优化实现"""
        result = self.weight_optimizer._multi_objective_optimization(
            self.X, self.y, 100
        )
        
        assert isinstance(result, dict)
        assert 'method' in result
        assert 'weights' in result
        assert 'r2_score' in result
        assert 'mse_score' in result
        assert 'mae_score' in result
        
        # 检查权重
        weights = result['weights']
        assert isinstance(weights, dict)
        assert len(weights) == len(self.X.columns)
    
    def test_apply_weights(self):
        """测试权重应用"""
        weights = {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}
        
        X_weighted = self.weight_optimizer._apply_weights(self.X, weights)
        
        assert isinstance(X_weighted, pd.DataFrame)
        assert X_weighted.shape == self.X.shape
        
        # 检查权重应用
        for feature, weight in weights.items():
            assert np.allclose(X_weighted[feature], self.X[feature] * weight)
    
    def test_select_best_result(self):
        """测试最佳结果选择"""
        optimization_results = {
            'method1': {'r2_score': 0.8, 'weights': {'feature1': 0.5, 'feature2': 0.3, 'feature3': 0.2}},
            'method2': {'r2_score': 0.9, 'weights': {'feature1': 0.6, 'feature2': 0.3, 'feature3': 0.1}},
            'method3': {'r2_score': 0.7, 'weights': {'feature1': 0.4, 'feature2': 0.4, 'feature3': 0.2}}
        }
        
        best_result = self.weight_optimizer._select_best_result(optimization_results)
        
        assert isinstance(best_result, dict)
        assert 'weights' in best_result
        assert 'r2_score' in best_result
        
        # 检查是否选择了最佳结果
        assert best_result['r2_score'] == 0.9
    
    def test_get_optimization_insights(self):
        """测试优化洞察获取"""
        # 先进行优化
        self.weight_optimizer.optimize_weights(self.X, self.y)
        
        insights = self.weight_optimizer.get_optimization_insights()
        
        assert isinstance(insights, dict)
        assert 'optimization_history' in insights
        assert 'best_weights' in insights
        assert 'optimization_metrics' in insights
        assert 'recommendations' in insights
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        empty_X = pd.DataFrame()
        empty_y = pd.Series(dtype=float)
        
        result = self.weight_optimizer.optimize_weights(empty_X, empty_y)
        
        assert isinstance(result, dict)
        assert 'best_result' in result
    
    def test_single_feature_handling(self):
        """测试单特征处理"""
        single_X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
        single_y = pd.Series([2, 4, 6, 8, 10])
        
        result = self.weight_optimizer.optimize_weights(single_X, single_y)
        
        assert isinstance(result, dict)
        assert 'best_result' in result
    
    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 创建较大的数据集
        large_X = pd.DataFrame({
            f'feature_{i}': np.random.normal(0, 1, 500)
            for i in range(8)
        })
        large_y = pd.Series(np.random.normal(0, 1, 500))
        
        result = self.weight_optimizer.optimize_weights(large_X, large_y)
        
        assert isinstance(result, dict)
        assert 'best_result' in result
    
    def test_different_objectives(self):
        """测试不同优化目标"""
        # 测试R²目标
        result_r2 = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent', objective='r2'
        )
        assert isinstance(result_r2, dict)
        
        # 测试MSE目标
        result_mse = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent', objective='mse'
        )
        assert isinstance(result_mse, dict)
        
        # 检查结果结构
        for result in [result_r2, result_mse]:
            assert 'best_result' in result
            best_result = result['best_result']
            assert 'weights' in best_result
            assert 'r2_score' in best_result
            assert 'mse_score' in best_result
    
    def test_optimization_convergence(self):
        """测试优化收敛性"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent', max_iterations=1000
        )
        
        assert isinstance(result, dict)
        assert 'best_result' in result
        
        best_result = result['best_result']
        assert 'success' in best_result
        assert 'iterations' in best_result
        
        # 检查是否成功收敛
        assert best_result['success'] is True
    
    def test_weight_bounds(self):
        """测试权重边界"""
        result = self.weight_optimizer.optimize_weights(
            self.X, self.y, method='gradient_descent'
        )
        
        assert isinstance(result, dict)
        assert 'best_result' in result
        
        best_result = result['best_result']
        weights = best_result['weights']
        
        # 检查权重边界
        for feature, weight in weights.items():
            assert 0.01 <= weight <= 10.0  # 默认边界



