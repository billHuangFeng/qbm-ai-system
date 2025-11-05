"""
权重优化算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize, differential_evolution, basinhopping
from scipy import stats
import logging
from ..logging_config import get_logger

logger = get_logger("weight_optimization")


class WeightOptimization:
    """权重优化算法"""

    def __init__(self):
        self.optimization_results = {}
        self.optimal_weights = {}
        self.optimization_history = []
        self.constraints = {}
        self.objective_functions = {}

    def optimize_weights(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        optimization_methods: List[str] = None,
        objective_functions: List[str] = None,
        constraints: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """优化权重"""
        try:
            if optimization_methods is None:
                optimization_methods = [
                    "gradient_descent",
                    "genetic_algorithm",
                    "bayesian",
                    "grid_search",
                ]

            if objective_functions is None:
                objective_functions = ["mse", "mae", "r2", "custom"]

            if constraints is None:
                constraints = {
                    "sum_to_one": True,
                    "non_negative": True,
                    "bounds": (0, 1),
                }

            self.constraints = constraints

            results = {}

            # 1. 梯度下降优化
            if "gradient_descent" in optimization_methods:
                gd_results = self._gradient_descent_optimization(
                    X, y, objective_functions
                )
                results["gradient_descent"] = gd_results

            # 2. 遗传算法优化
            if "genetic_algorithm" in optimization_methods:
                ga_results = self._genetic_algorithm_optimization(
                    X, y, objective_functions
                )
                results["genetic_algorithm"] = ga_results

            # 3. 贝叶斯优化
            if "bayesian" in optimization_methods:
                bayesian_results = self._bayesian_optimization(
                    X, y, objective_functions
                )
                results["bayesian"] = bayesian_results

            # 4. 网格搜索优化
            if "grid_search" in optimization_methods:
                grid_results = self._grid_search_optimization(X, y, objective_functions)
                results["grid_search"] = grid_results

            # 5. 集成优化结果
            ensemble_results = self._ensemble_optimization_results(results)
            results["ensemble"] = ensemble_results

            # 6. 优化历史记录
            self.optimization_history.append(
                {
                    "timestamp": pd.Timestamp.now(),
                    "methods": optimization_methods,
                    "objectives": objective_functions,
                    "results": results,
                }
            )

            self.optimization_results = results
            logger.info(f"权重优化完成，使用了 {len(optimization_methods)} 种方法")

            return results

        except Exception as e:
            logger.error(f"权重优化失败: {e}")
            raise

    def _gradient_descent_optimization(
        self, X: pd.DataFrame, y: pd.Series, objective_functions: List[str]
    ) -> Dict[str, Any]:
        """梯度下降优化"""
        try:
            gd_results = {}

            for objective in objective_functions:
                # 初始化权重
                n_features = len(X.columns)
                initial_weights = np.ones(n_features) / n_features

                # 定义目标函数
                def objective_func(weights):
                    return self._calculate_objective(X, y, weights, objective)

                # 定义约束
                constraints = []
                if self.constraints.get("sum_to_one", True):
                    constraints.append({"type": "eq", "fun": lambda w: np.sum(w) - 1})

                if self.constraints.get("non_negative", True):
                    bounds = [(0, 1) for _ in range(n_features)]
                else:
                    bounds = self.constraints.get("bounds", (0, 1))
                    bounds = [bounds for _ in range(n_features)]

                # 执行优化
                result = minimize(
                    objective_func,
                    initial_weights,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints,
                    options={"maxiter": 1000},
                )

                gd_results[objective] = {
                    "optimal_weights": dict(zip(X.columns, result.x)),
                    "objective_value": result.fun,
                    "success": result.success,
                    "iterations": result.nit,
                    "message": result.message,
                }

            logger.info("梯度下降优化完成")
            return gd_results

        except Exception as e:
            logger.error(f"梯度下降优化失败: {e}")
            return {}

    def _genetic_algorithm_optimization(
        self, X: pd.DataFrame, y: pd.Series, objective_functions: List[str]
    ) -> Dict[str, Any]:
        """遗传算法优化"""
        try:
            ga_results = {}

            for objective in objective_functions:
                n_features = len(X.columns)

                # 定义目标函数
                def objective_func(weights):
                    return self._calculate_objective(X, y, weights, objective)

                # 定义边界
                bounds = []
                for i in range(n_features):
                    if self.constraints.get("non_negative", True):
                        bounds.append((0, 1))
                    else:
                        bounds.append(self.constraints.get("bounds", (0, 1)))

                # 执行遗传算法优化
                result = differential_evolution(
                    objective_func, bounds, maxiter=1000, popsize=15, seed=42
                )

                # 归一化权重（如果需要）
                optimal_weights = result.x
                if self.constraints.get("sum_to_one", True):
                    optimal_weights = optimal_weights / np.sum(optimal_weights)

                ga_results[objective] = {
                    "optimal_weights": dict(zip(X.columns, optimal_weights)),
                    "objective_value": result.fun,
                    "success": result.success,
                    "iterations": result.nit,
                    "message": result.message,
                }

            logger.info("遗传算法优化完成")
            return ga_results

        except Exception as e:
            logger.error(f"遗传算法优化失败: {e}")
            return {}

    def _bayesian_optimization(
        self, X: pd.DataFrame, y: pd.Series, objective_functions: List[str]
    ) -> Dict[str, Any]:
        """贝叶斯优化"""
        try:
            bayesian_results = {}

            for objective in objective_functions:
                n_features = len(X.columns)

                # 定义目标函数
                def objective_func(weights):
                    return self._calculate_objective(X, y, weights, objective)

                # 使用basinhopping进行全局优化
                initial_weights = np.ones(n_features) / n_features

                result = basinhopping(
                    objective_func,
                    initial_weights,
                    niter=100,
                    minimizer_kwargs={
                        "method": "L-BFGS-B",
                        "bounds": [(0, 1) for _ in range(n_features)],
                    },
                )

                # 归一化权重（如果需要）
                optimal_weights = result.x
                if self.constraints.get("sum_to_one", True):
                    optimal_weights = optimal_weights / np.sum(optimal_weights)

                bayesian_results[objective] = {
                    "optimal_weights": dict(zip(X.columns, optimal_weights)),
                    "objective_value": result.fun,
                    "success": result.success,
                    "iterations": result.nit,
                    "message": result.message,
                }

            logger.info("贝叶斯优化完成")
            return bayesian_results

        except Exception as e:
            logger.error(f"贝叶斯优化失败: {e}")
            return {}

    def _grid_search_optimization(
        self, X: pd.DataFrame, y: pd.Series, objective_functions: List[str]
    ) -> Dict[str, Any]:
        """网格搜索优化"""
        try:
            grid_results = {}

            for objective in objective_functions:
                n_features = len(X.columns)

                # 创建网格搜索参数
                param_grid = {}
                for i, feature in enumerate(X.columns):
                    # 简化的网格搜索，使用较少的点
                    param_grid[f"weight_{i}"] = np.linspace(0, 1, 11)  # 0到1，步长0.1

                # 由于网格搜索在高维空间中计算量巨大，这里使用简化的方法
                # 使用随机搜索代替完整网格搜索
                best_weights = None
                best_score = float("inf")

                for _ in range(1000):  # 随机搜索1000次
                    # 生成随机权重
                    weights = np.random.random(n_features)

                    # 归一化权重
                    if self.constraints.get("sum_to_one", True):
                        weights = weights / np.sum(weights)

                    # 计算目标函数值
                    score = self._calculate_objective(X, y, weights, objective)

                    if score < best_score:
                        best_score = score
                        best_weights = weights

                grid_results[objective] = {
                    "optimal_weights": dict(zip(X.columns, best_weights)),
                    "objective_value": best_score,
                    "success": True,
                    "iterations": 1000,
                    "message": "Random search completed",
                }

            logger.info("网格搜索优化完成")
            return grid_results

        except Exception as e:
            logger.error(f"网格搜索优化失败: {e}")
            return {}

    def _ensemble_optimization_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """集成优化结果"""
        try:
            ensemble_results = {}

            # 收集所有目标函数的结果
            objectives = set()
            for method_results in results.values():
                objectives.update(method_results.keys())

            for objective in objectives:
                method_scores = []
                method_weights = []

                # 收集每个方法的结果
                for method_name, method_results in results.items():
                    if objective in method_results:
                        method_scores.append(
                            method_results[objective]["objective_value"]
                        )
                        method_weights.append(
                            method_results[objective]["optimal_weights"]
                        )

                if method_scores and method_weights:
                    # 选择最佳方法
                    best_method_idx = np.argmin(method_scores)
                    best_weights = method_weights[best_method_idx]

                    # 计算集成权重（加权平均）
                    ensemble_weights = {}
                    for feature in best_weights.keys():
                        weighted_sum = 0
                        weight_sum = 0

                        for i, method_weight in enumerate(method_weights):
                            # 使用性能倒数作为权重
                            method_weight_value = 1 / (method_scores[i] + 1e-8)
                            weighted_sum += method_weight[feature] * method_weight_value
                            weight_sum += method_weight_value

                        ensemble_weights[feature] = weighted_sum / weight_sum

                    # 归一化集成权重
                    if self.constraints.get("sum_to_one", True):
                        total_weight = sum(ensemble_weights.values())
                        ensemble_weights = {
                            k: v / total_weight for k, v in ensemble_weights.items()
                        }

                    ensemble_results[objective] = {
                        "ensemble_weights": ensemble_weights,
                        "best_method_score": min(method_scores),
                        "ensemble_score": self._calculate_objective(
                            pd.DataFrame(),
                            pd.Series(),
                            list(ensemble_weights.values()),
                            objective,
                        ),
                        "method_scores": dict(zip(results.keys(), method_scores)),
                    }

            logger.info("集成优化结果完成")
            return ensemble_results

        except Exception as e:
            logger.error(f"集成优化结果失败: {e}")
            return {}

    def _calculate_objective(
        self, X: pd.DataFrame, y: pd.Series, weights: np.ndarray, objective: str
    ) -> float:
        """计算目标函数值"""
        try:
            if len(X) == 0 or len(y) == 0:
                # 如果没有数据，返回权重分布的熵
                return -np.sum(weights * np.log(weights + 1e-8))

            # 应用权重到特征
            X_weighted = X * weights

            # 训练模型
            model = LinearRegression()
            model.fit(X_weighted, y)

            # 预测
            y_pred = model.predict(X_weighted)

            # 计算目标函数
            if objective == "mse":
                return mean_squared_error(y, y_pred)
            elif objective == "mae":
                return mean_absolute_error(y, y_pred)
            elif objective == "r2":
                return -r2_score(y, y_pred)  # 负号因为我们要最小化
            elif objective == "custom":
                # 自定义目标函数：MSE + 权重稀疏性惩罚
                mse = mean_squared_error(y, y_pred)
                sparsity_penalty = 0.1 * np.sum(np.abs(weights))
                return mse + sparsity_penalty
            else:
                return mean_squared_error(y, y_pred)

        except Exception as e:
            logger.error(f"目标函数计算失败: {e}")
            return float("inf")

    def optimize_weights_with_validation(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        cv_folds: int = 5,
        optimization_methods: List[str] = None,
    ) -> Dict[str, Any]:
        """带交叉验证的权重优化"""
        try:
            if optimization_methods is None:
                optimization_methods = ["gradient_descent", "genetic_algorithm"]

            cv_results = {}

            for method in optimization_methods:
                method_cv_scores = []
                method_cv_weights = []

                # 交叉验证
                from sklearn.model_selection import KFold

                kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)

                for train_idx, val_idx in kf.split(X):
                    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

                    # 优化权重
                    if method == "gradient_descent":
                        method_results = self._gradient_descent_optimization(
                            X_train, y_train, ["mse"]
                        )
                    elif method == "genetic_algorithm":
                        method_results = self._genetic_algorithm_optimization(
                            X_train, y_train, ["mse"]
                        )
                    else:
                        continue

                    if "mse" in method_results:
                        optimal_weights = method_results["mse"]["optimal_weights"]
                        weights_array = np.array(list(optimal_weights.values()))

                        # 在验证集上评估
                        X_val_weighted = X_val * weights_array
                        model = LinearRegression()
                        model.fit(X_val_weighted, y_val)
                        y_val_pred = model.predict(X_val_weighted)
                        val_score = mean_squared_error(y_val, y_val_pred)

                        method_cv_scores.append(val_score)
                        method_cv_weights.append(optimal_weights)

                if method_cv_scores:
                    cv_results[method] = {
                        "cv_scores": method_cv_scores,
                        "cv_weights": method_cv_weights,
                        "mean_cv_score": np.mean(method_cv_scores),
                        "std_cv_score": np.std(method_cv_scores),
                        "best_cv_score": min(method_cv_scores),
                        "best_cv_weights": method_cv_weights[
                            np.argmin(method_cv_scores)
                        ],
                    }

            logger.info(
                f"交叉验证权重优化完成，使用了 {len(optimization_methods)} 种方法"
            )
            return cv_results

        except Exception as e:
            logger.error(f"交叉验证权重优化失败: {e}")
            return {}

    def optimize_weights_with_constraints(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        feature_groups: Dict[str, List[str]] = None,
        group_constraints: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """带分组约束的权重优化"""
        try:
            if feature_groups is None:
                feature_groups = {"all": X.columns.tolist()}

            if group_constraints is None:
                group_constraints = {}

            constrained_results = {}

            # 为每个分组优化权重
            for group_name, features in feature_groups.items():
                if not features:
                    continue

                X_group = X[features]

                # 定义分组约束
                group_constraint = group_constraints.get(group_name, 1.0)

                # 优化权重
                optimization_results = self.optimize_weights(
                    X_group,
                    y,
                    optimization_methods=["gradient_descent"],
                    objective_functions=["mse"],
                )

                if (
                    "gradient_descent" in optimization_results
                    and "mse" in optimization_results["gradient_descent"]
                ):
                    optimal_weights = optimization_results["gradient_descent"]["mse"][
                        "optimal_weights"
                    ]

                    # 应用分组约束
                    constrained_weights = {}
                    for feature, weight in optimal_weights.items():
                        constrained_weights[feature] = weight * group_constraint

                    constrained_results[group_name] = {
                        "features": features,
                        "constraint": group_constraint,
                        "optimal_weights": constrained_weights,
                        "objective_value": optimization_results["gradient_descent"][
                            "mse"
                        ]["objective_value"],
                    }

            logger.info(f"分组约束权重优化完成，处理了 {len(feature_groups)} 个分组")
            return constrained_results

        except Exception as e:
            logger.error(f"分组约束权重优化失败: {e}")
            return {}

    def optimize_weights_with_regularization(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        regularization_params: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """带正则化的权重优化"""
        try:
            if regularization_params is None:
                regularization_params = {
                    "l1_penalty": 0.1,
                    "l2_penalty": 0.1,
                    "elastic_ratio": 0.5,
                }

            regularization_results = {}

            # L1正则化
            l1_results = self._optimize_with_l1_regularization(
                X, y, regularization_params["l1_penalty"]
            )
            regularization_results["l1"] = l1_results

            # L2正则化
            l2_results = self._optimize_with_l2_regularization(
                X, y, regularization_params["l2_penalty"]
            )
            regularization_results["l2"] = l2_results

            # Elastic Net正则化
            elastic_results = self._optimize_with_elastic_regularization(
                X,
                y,
                regularization_params["l1_penalty"],
                regularization_params["elastic_ratio"],
            )
            regularization_results["elastic"] = elastic_results

            logger.info("正则化权重优化完成")
            return regularization_results

        except Exception as e:
            logger.error(f"正则化权重优化失败: {e}")
            return {}

    def _optimize_with_l1_regularization(
        self, X: pd.DataFrame, y: pd.Series, l1_penalty: float
    ) -> Dict[str, Any]:
        """L1正则化优化"""
        try:
            n_features = len(X.columns)
            initial_weights = np.ones(n_features) / n_features

            def objective_func(weights):
                # MSE + L1惩罚
                X_weighted = X * weights
                model = LinearRegression()
                model.fit(X_weighted, y)
                y_pred = model.predict(X_weighted)
                mse = mean_squared_error(y, y_pred)
                l1_penalty_term = l1_penalty * np.sum(np.abs(weights))
                return mse + l1_penalty_term

            # 约束
            constraints = []
            if self.constraints.get("sum_to_one", True):
                constraints.append({"type": "eq", "fun": lambda w: np.sum(w) - 1})

            bounds = [(0, 1) for _ in range(n_features)]

            result = minimize(
                objective_func,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 1000},
            )

            return {
                "optimal_weights": dict(zip(X.columns, result.x)),
                "objective_value": result.fun,
                "success": result.success,
                "l1_penalty": l1_penalty,
            }

        except Exception as e:
            logger.error(f"L1正则化优化失败: {e}")
            return {}

    def _optimize_with_l2_regularization(
        self, X: pd.DataFrame, y: pd.Series, l2_penalty: float
    ) -> Dict[str, Any]:
        """L2正则化优化"""
        try:
            n_features = len(X.columns)
            initial_weights = np.ones(n_features) / n_features

            def objective_func(weights):
                # MSE + L2惩罚
                X_weighted = X * weights
                model = LinearRegression()
                model.fit(X_weighted, y)
                y_pred = model.predict(X_weighted)
                mse = mean_squared_error(y, y_pred)
                l2_penalty_term = l2_penalty * np.sum(weights**2)
                return mse + l2_penalty_term

            # 约束
            constraints = []
            if self.constraints.get("sum_to_one", True):
                constraints.append({"type": "eq", "fun": lambda w: np.sum(w) - 1})

            bounds = [(0, 1) for _ in range(n_features)]

            result = minimize(
                objective_func,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 1000},
            )

            return {
                "optimal_weights": dict(zip(X.columns, result.x)),
                "objective_value": result.fun,
                "success": result.success,
                "l2_penalty": l2_penalty,
            }

        except Exception as e:
            logger.error(f"L2正则化优化失败: {e}")
            return {}

    def _optimize_with_elastic_regularization(
        self, X: pd.DataFrame, y: pd.Series, l1_penalty: float, elastic_ratio: float
    ) -> Dict[str, Any]:
        """Elastic Net正则化优化"""
        try:
            n_features = len(X.columns)
            initial_weights = np.ones(n_features) / n_features

            def objective_func(weights):
                # MSE + Elastic Net惩罚
                X_weighted = X * weights
                model = LinearRegression()
                model.fit(X_weighted, y)
                y_pred = model.predict(X_weighted)
                mse = mean_squared_error(y, y_pred)

                l1_term = l1_penalty * elastic_ratio * np.sum(np.abs(weights))
                l2_term = l1_penalty * (1 - elastic_ratio) * np.sum(weights**2)

                return mse + l1_term + l2_term

            # 约束
            constraints = []
            if self.constraints.get("sum_to_one", True):
                constraints.append({"type": "eq", "fun": lambda w: np.sum(w) - 1})

            bounds = [(0, 1) for _ in range(n_features)]

            result = minimize(
                objective_func,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 1000},
            )

            return {
                "optimal_weights": dict(zip(X.columns, result.x)),
                "objective_value": result.fun,
                "success": result.success,
                "l1_penalty": l1_penalty,
                "elastic_ratio": elastic_ratio,
            }

        except Exception as e:
            logger.error(f"Elastic Net正则化优化失败: {e}")
            return {}

    def get_optimization_insights(self) -> Dict[str, Any]:
        """获取优化洞察"""
        try:
            insights = {
                "optimization_summary": self._summarize_optimization_results(),
                "weight_stability": self._analyze_weight_stability(),
                "convergence_analysis": self._analyze_convergence(),
                "recommendations": self._generate_optimization_recommendations(),
            }

            return insights

        except Exception as e:
            logger.error(f"优化洞察获取失败: {e}")
            return {}

    def _summarize_optimization_results(self) -> Dict[str, Any]:
        """总结优化结果"""
        try:
            summary = {
                "total_methods": len(self.optimization_results),
                "best_method": None,
                "best_score": float("inf"),
                "method_comparison": {},
            }

            for method_name, method_results in self.optimization_results.items():
                if method_name == "ensemble":
                    continue

                method_scores = []
                for objective, result in method_results.items():
                    if "objective_value" in result:
                        method_scores.append(result["objective_value"])

                if method_scores:
                    avg_score = np.mean(method_scores)
                    summary["method_comparison"][method_name] = {
                        "average_score": avg_score,
                        "best_score": min(method_scores),
                        "worst_score": max(method_scores),
                        "score_std": np.std(method_scores),
                    }

                    if avg_score < summary["best_score"]:
                        summary["best_score"] = avg_score
                        summary["best_method"] = method_name

            return summary

        except Exception as e:
            logger.error(f"优化结果总结失败: {e}")
            return {}

    def _analyze_weight_stability(self) -> Dict[str, Any]:
        """分析权重稳定性"""
        try:
            stability_analysis = {}

            # 收集所有权重
            all_weights = {}
            for method_name, method_results in self.optimization_results.items():
                if method_name == "ensemble":
                    continue

                for objective, result in method_results.items():
                    if "optimal_weights" in result:
                        for feature, weight in result["optimal_weights"].items():
                            if feature not in all_weights:
                                all_weights[feature] = []
                            all_weights[feature].append(weight)

            # 计算每个特征的权重稳定性
            feature_stability = {}
            for feature, weights in all_weights.items():
                if len(weights) > 1:
                    feature_stability[feature] = {
                        "mean_weight": np.mean(weights),
                        "std_weight": np.std(weights),
                        "cv_weight": np.std(weights) / (np.mean(weights) + 1e-8),
                        "weight_range": [np.min(weights), np.max(weights)],
                    }

            stability_analysis["feature_stability"] = feature_stability

            # 计算整体稳定性
            if feature_stability:
                cv_values = [data["cv_weight"] for data in feature_stability.values()]
                stability_analysis["overall_stability"] = {
                    "mean_cv": np.mean(cv_values),
                    "std_cv": np.std(cv_values),
                    "stability_level": self._classify_stability_level(
                        np.mean(cv_values)
                    ),
                }

            return stability_analysis

        except Exception as e:
            logger.error(f"权重稳定性分析失败: {e}")
            return {}

    def _analyze_convergence(self) -> Dict[str, Any]:
        """分析收敛性"""
        try:
            convergence_analysis = {}

            for method_name, method_results in self.optimization_results.items():
                if method_name == "ensemble":
                    continue

                method_convergence = {}
                for objective, result in method_results.items():
                    if "iterations" in result:
                        method_convergence[objective] = {
                            "iterations": result["iterations"],
                            "success": result.get("success", False),
                            "convergence_rate": 1.0 / (result["iterations"] + 1e-8),
                        }

                convergence_analysis[method_name] = method_convergence

            return convergence_analysis

        except Exception as e:
            logger.error(f"收敛性分析失败: {e}")
            return {}

    def _classify_stability_level(self, cv_value: float) -> str:
        """分类稳定性水平"""
        if cv_value < 0.1:
            return "高稳定性"
        elif cv_value < 0.3:
            return "中等稳定性"
        elif cv_value < 0.5:
            return "低稳定性"
        else:
            return "不稳定"

    def _generate_optimization_recommendations(self) -> List[str]:
        """生成优化建议"""
        try:
            recommendations = []

            # 基于优化结果生成建议
            if self.optimization_results:
                summary = self._summarize_optimization_results()

                if summary.get("best_method"):
                    recommendations.append(
                        f"推荐使用 {summary['best_method']} 方法进行权重优化"
                    )

                stability = self._analyze_weight_stability()
                if "overall_stability" in stability:
                    stability_level = stability["overall_stability"]["stability_level"]
                    if stability_level == "不稳定":
                        recommendations.append("权重稳定性较低，建议增加正则化约束")
                    elif stability_level == "低稳定性":
                        recommendations.append("权重稳定性一般，建议使用集成方法")

                # 基于收敛性生成建议
                convergence = self._analyze_convergence()
                for method_name, method_conv in convergence.items():
                    avg_iterations = np.mean(
                        [conv["iterations"] for conv in method_conv.values()]
                    )
                    if avg_iterations > 500:
                        recommendations.append(
                            f"{method_name} 方法收敛较慢，建议调整参数"
                        )

            return recommendations

        except Exception as e:
            logger.error(f"优化建议生成失败: {e}")
            return []

    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        try:
            report = {
                "summary": {
                    "optimization_timestamp": pd.Timestamp.now().isoformat(),
                    "total_methods": len(self.optimization_results),
                    "optimization_history_count": len(self.optimization_history),
                },
                "detailed_results": self.optimization_results,
                "insights": self.get_optimization_insights(),
                "optimization_history": self.optimization_history,
            }

            return report

        except Exception as e:
            logger.error(f"优化报告生成失败: {e}")
            return {}
