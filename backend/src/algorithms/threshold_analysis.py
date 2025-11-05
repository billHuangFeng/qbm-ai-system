"""
阈值效应分析算法
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import logging
from datetime import datetime
from ..logging_config import get_logger

logger = get_logger("threshold_analysis")


class ThresholdAnalysis:
    """阈值效应分析"""

    def __init__(self):
        self.thresholds = {}
        self.segment_models = {}
        self.threshold_insights = {}

    def detect_threshold_effects(
        self, X: pd.DataFrame, y: pd.Series, min_samples: int = 30
    ) -> Dict[str, Any]:
        """检测阈值效应"""
        try:
            threshold_results = {}

            # 1. 决策树阈值检测
            tree_thresholds = self._detect_tree_thresholds(X, y, min_samples)
            threshold_results["decision_tree"] = tree_thresholds

            # 2. 分段回归分析
            piecewise_regression = self._analyze_piecewise_regression(X, y, min_samples)
            threshold_results["piecewise_regression"] = piecewise_regression

            # 3. 随机森林阈值分析
            rf_thresholds = self._analyze_rf_thresholds(X, y, min_samples)
            threshold_results["random_forest"] = rf_thresholds

            # 4. 综合阈值效应评分
            threshold_score = self._calculate_threshold_score(threshold_results)
            threshold_results["overall_score"] = threshold_score

            self.thresholds = threshold_results
            logger.info(f"阈值效应分析完成，整体评分: {threshold_score:.4f}")

            return threshold_results

        except Exception as e:
            logger.error(f"阈值效应检测失败: {e}")
            raise

    def _detect_tree_thresholds(
        self, X: pd.DataFrame, y: pd.Series, min_samples: int
    ) -> Dict[str, Any]:
        """使用决策树检测阈值"""
        try:
            tree_results = {}

            for feature in X.columns:
                # 训练决策树
                tree = DecisionTreeRegressor(
                    min_samples_split=min_samples,
                    min_samples_leaf=min_samples // 2,
                    random_state=42,
                )
                tree.fit(X[[feature]], y)

                # 提取分割点
                thresholds = self._extract_tree_thresholds(tree, feature)

                if thresholds:
                    # 评估阈值效果
                    threshold_effectiveness = self._evaluate_threshold_effectiveness(
                        X, y, feature, thresholds
                    )

                    tree_results[feature] = {
                        "thresholds": thresholds,
                        "effectiveness": threshold_effectiveness,
                        "tree_depth": tree.get_depth(),
                        "n_leaves": tree.get_n_leaves(),
                    }

            logger.info(f"决策树阈值检测完成，发现 {len(tree_results)} 个特征的阈值")
            return tree_results

        except Exception as e:
            logger.error(f"决策树阈值检测失败: {e}")
            return {}

    def _extract_tree_thresholds(
        self, tree: DecisionTreeRegressor, feature: str
    ) -> List[float]:
        """从决策树中提取阈值"""
        try:
            thresholds = []

            def extract_thresholds_recursive(node, depth=0):
                if tree.tree_.children_left[node] != tree.tree_.children_right[node]:
                    # 内部节点
                    threshold = tree.tree_.threshold[node]
                    thresholds.append(threshold)

                    # 递归处理子节点
                    extract_thresholds_recursive(
                        tree.tree_.children_left[node], depth + 1
                    )
                    extract_thresholds_recursive(
                        tree.tree_.children_right[node], depth + 1
                    )

            extract_thresholds_recursive(0)

            return sorted(list(set(thresholds)))

        except Exception as e:
            logger.error(f"阈值提取失败: {e}")
            return []

    def _evaluate_threshold_effectiveness(
        self, X: pd.DataFrame, y: pd.Series, feature: str, thresholds: List[float]
    ) -> Dict[str, float]:
        """评估阈值有效性"""
        try:
            effectiveness = {}

            for threshold in thresholds:
                # 创建分段特征
                X_segmented = X.copy()
                X_segmented[f"{feature}_above_threshold"] = (
                    X[feature] > threshold
                ).astype(int)
                X_segmented[f"{feature}_interaction"] = (
                    X[feature] * X_segmented[f"{feature}_above_threshold"]
                )

                # 训练分段模型
                model = LinearRegression()
                model.fit(
                    X_segmented[
                        [
                            feature,
                            f"{feature}_above_threshold",
                            f"{feature}_interaction",
                        ]
                    ],
                    y,
                )

                # 计算R²提升
                r2_baseline = (
                    LinearRegression().fit(X[[feature]], y).score(X[[feature]], y)
                )
                r2_segmented = model.score(
                    X_segmented[
                        [
                            feature,
                            f"{feature}_above_threshold",
                            f"{feature}_interaction",
                        ]
                    ],
                    y,
                )

                improvement = r2_segmented - r2_baseline

                effectiveness[f"threshold_{threshold:.4f}"] = {
                    "improvement": improvement,
                    "r2_baseline": r2_baseline,
                    "r2_segmented": r2_segmented,
                    "coefficient": model.coef_[2],  # 交互项系数
                }

            return effectiveness

        except Exception as e:
            logger.error(f"阈值有效性评估失败: {e}")
            return {}

    def _analyze_piecewise_regression(
        self, X: pd.DataFrame, y: pd.Series, min_samples: int
    ) -> Dict[str, Any]:
        """分析分段回归"""
        try:
            piecewise_results = {}

            for feature in X.columns:
                # 寻找最优分割点
                optimal_threshold = self._find_optimal_threshold(
                    X, y, feature, min_samples
                )

                if optimal_threshold is not None:
                    # 创建分段模型
                    segment_model = self._create_piecewise_model(
                        X, y, feature, optimal_threshold
                    )

                    # 评估分段模型性能
                    performance = self._evaluate_piecewise_model(
                        X, y, feature, optimal_threshold
                    )

                    piecewise_results[feature] = {
                        "optimal_threshold": optimal_threshold,
                        "segment_model": segment_model,
                        "performance": performance,
                    }

            logger.info(
                f"分段回归分析完成，发现 {len(piecewise_results)} 个特征的最优阈值"
            )
            return piecewise_results

        except Exception as e:
            logger.error(f"分段回归分析失败: {e}")
            return {}

    def _find_optimal_threshold(
        self, X: pd.DataFrame, y: pd.Series, feature: str, min_samples: int
    ) -> Optional[float]:
        """寻找最优阈值"""
        try:
            feature_values = X[feature].values
            sorted_values = np.sort(feature_values)

            # 在合理范围内搜索阈值
            min_val = sorted_values[min_samples]
            max_val = sorted_values[-min_samples]

            # 生成候选阈值
            candidate_thresholds = np.linspace(min_val, max_val, 20)

            best_threshold = None
            best_score = -np.inf

            for threshold in candidate_thresholds:
                # 确保每个分段有足够的样本
                below_threshold = X[feature] <= threshold
                above_threshold = X[feature] > threshold

                if (
                    below_threshold.sum() >= min_samples
                    and above_threshold.sum() >= min_samples
                ):
                    # 计算分段模型的R²
                    score = self._calculate_piecewise_score(X, y, feature, threshold)

                    if score > best_score:
                        best_score = score
                        best_threshold = threshold

            return best_threshold

        except Exception as e:
            logger.error(f"最优阈值搜索失败: {e}")
            return None

    def _calculate_piecewise_score(
        self, X: pd.DataFrame, y: pd.Series, feature: str, threshold: float
    ) -> float:
        """计算分段模型得分"""
        try:
            # 创建分段特征
            X_segmented = X.copy()
            X_segmented[f"{feature}_above_threshold"] = (X[feature] > threshold).astype(
                int
            )
            X_segmented[f"{feature}_interaction"] = (
                X[feature] * X_segmented[f"{feature}_above_threshold"]
            )

            # 训练分段模型
            model = LinearRegression()
            model.fit(
                X_segmented[
                    [feature, f"{feature}_above_threshold", f"{feature}_interaction"]
                ],
                y,
            )

            # 计算R²
            r2 = model.score(
                X_segmented[
                    [feature, f"{feature}_above_threshold", f"{feature}_interaction"]
                ],
                y,
            )

            return r2

        except Exception as e:
            logger.error(f"分段模型得分计算失败: {e}")
            return 0.0

    def _create_piecewise_model(
        self, X: pd.DataFrame, y: pd.Series, feature: str, threshold: float
    ) -> Dict[str, Any]:
        """创建分段模型"""
        try:
            # 创建分段特征
            X_segmented = X.copy()
            X_segmented[f"{feature}_above_threshold"] = (X[feature] > threshold).astype(
                int
            )
            X_segmented[f"{feature}_interaction"] = (
                X[feature] * X_segmented[f"{feature}_above_threshold"]
            )

            # 训练模型
            model = LinearRegression()
            model.fit(
                X_segmented[
                    [feature, f"{feature}_above_threshold", f"{feature}_interaction"]
                ],
                y,
            )

            # 计算分段系数
            below_coef = model.coef_[0]  # 基础系数
            above_coef = model.coef_[0] + model.coef_[2]  # 基础系数 + 交互系数
            threshold_effect = model.coef_[1]  # 阈值效应

            return {
                "model": model,
                "threshold": threshold,
                "below_threshold_coef": below_coef,
                "above_threshold_coef": above_coef,
                "threshold_effect": threshold_effect,
                "intercept": model.intercept_,
            }

        except Exception as e:
            logger.error(f"分段模型创建失败: {e}")
            return {}

    def _evaluate_piecewise_model(
        self, X: pd.DataFrame, y: pd.Series, feature: str, threshold: float
    ) -> Dict[str, float]:
        """评估分段模型性能"""
        try:
            # 创建分段特征
            X_segmented = X.copy()
            X_segmented[f"{feature}_above_threshold"] = (X[feature] > threshold).astype(
                int
            )
            X_segmented[f"{feature}_interaction"] = (
                X[feature] * X_segmented[f"{feature}_above_threshold"]
            )

            # 训练分段模型
            model = LinearRegression()
            model.fit(
                X_segmented[
                    [feature, f"{feature}_above_threshold", f"{feature}_interaction"]
                ],
                y,
            )

            # 训练基线模型
            baseline_model = LinearRegression()
            baseline_model.fit(X[[feature]], y)

            # 计算性能指标
            y_pred_piecewise = model.predict(
                X_segmented[
                    [feature, f"{feature}_above_threshold", f"{feature}_interaction"]
                ]
            )
            y_pred_baseline = baseline_model.predict(X[[feature]])

            r2_piecewise = r2_score(y, y_pred_piecewise)
            r2_baseline = r2_score(y, y_pred_baseline)

            mse_piecewise = mean_squared_error(y, y_pred_piecewise)
            mse_baseline = mean_squared_error(y, y_pred_baseline)

            return {
                "r2_piecewise": r2_piecewise,
                "r2_baseline": r2_baseline,
                "r2_improvement": r2_piecewise - r2_baseline,
                "mse_piecewise": mse_piecewise,
                "mse_baseline": mse_baseline,
                "mse_improvement": mse_baseline - mse_piecewise,
            }

        except Exception as e:
            logger.error(f"分段模型性能评估失败: {e}")
            return {}

    def _analyze_rf_thresholds(
        self, X: pd.DataFrame, y: pd.Series, min_samples: int
    ) -> Dict[str, Any]:
        """使用随机森林分析阈值"""
        try:
            rf_results = {}

            # 训练随机森林
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)

            # 分析每个特征的阈值
            for feature in X.columns:
                # 获取特征值范围
                feature_values = X[feature].values
                min_val, max_val = feature_values.min(), feature_values.max()

                # 生成候选阈值
                candidate_thresholds = np.linspace(min_val, max_val, 20)

                threshold_scores = []
                for threshold in candidate_thresholds:
                    # 创建分段特征
                    X_segmented = X.copy()
                    X_segmented[f"{feature}_above_threshold"] = (
                        X[feature] > threshold
                    ).astype(int)

                    # 训练包含分段特征的模型
                    rf_segmented = RandomForestRegressor(
                        n_estimators=50, random_state=42
                    )
                    rf_segmented.fit(X_segmented, y)

                    # 计算性能提升
                    r2_original = rf.score(X, y)
                    r2_segmented = rf_segmented.score(X_segmented, y)

                    improvement = r2_segmented - r2_original
                    threshold_scores.append((threshold, improvement))

                # 选择最佳阈值
                if threshold_scores:
                    best_threshold, best_improvement = max(
                        threshold_scores, key=lambda x: x[1]
                    )

                    if best_improvement > 0.01:  # 至少1%的改进
                        rf_results[feature] = {
                            "best_threshold": best_threshold,
                            "improvement": best_improvement,
                            "all_scores": threshold_scores,
                        }

            logger.info(f"随机森林阈值分析完成，发现 {len(rf_results)} 个特征的阈值")
            return rf_results

        except Exception as e:
            logger.error(f"随机森林阈值分析失败: {e}")
            return {}

    def _calculate_threshold_score(self, threshold_results: Dict[str, Any]) -> float:
        """计算综合阈值效应评分"""
        try:
            score = 0.0
            weights = {
                "decision_tree": 0.4,
                "piecewise_regression": 0.4,
                "random_forest": 0.2,
            }

            # 决策树阈值评分
            if (
                "decision_tree" in threshold_results
                and threshold_results["decision_tree"]
            ):
                tree_count = len(threshold_results["decision_tree"])
                tree_avg_effectiveness = np.mean(
                    [
                        np.mean(
                            [
                                effect["improvement"]
                                for effect in feature_data["effectiveness"].values()
                            ]
                        )
                        for feature_data in threshold_results["decision_tree"].values()
                    ]
                )
                score += weights["decision_tree"] * tree_count * tree_avg_effectiveness

            # 分段回归评分
            if (
                "piecewise_regression" in threshold_results
                and threshold_results["piecewise_regression"]
            ):
                piecewise_count = len(threshold_results["piecewise_regression"])
                piecewise_avg_improvement = np.mean(
                    [
                        feature_data["performance"]["r2_improvement"]
                        for feature_data in threshold_results[
                            "piecewise_regression"
                        ].values()
                    ]
                )
                score += (
                    weights["piecewise_regression"]
                    * piecewise_count
                    * piecewise_avg_improvement
                )

            # 随机森林阈值评分
            if (
                "random_forest" in threshold_results
                and threshold_results["random_forest"]
            ):
                rf_count = len(threshold_results["random_forest"])
                rf_avg_improvement = np.mean(
                    [
                        feature_data["improvement"]
                        for feature_data in threshold_results["random_forest"].values()
                    ]
                )
                score += weights["random_forest"] * rf_count * rf_avg_improvement

            return min(score, 1.0)  # 限制在0-1范围内

        except Exception as e:
            logger.error(f"阈值效应评分计算失败: {e}")
            return 0.0

    def create_threshold_features(
        self, X: pd.DataFrame, threshold_threshold: float = 0.05
    ) -> pd.DataFrame:
        """创建阈值特征"""
        try:
            X_enhanced = X.copy()

            # 添加决策树阈值特征
            if "decision_tree" in self.thresholds:
                for feature, feature_data in self.thresholds["decision_tree"].items():
                    for threshold_name, threshold_data in feature_data[
                        "effectiveness"
                    ].items():
                        if threshold_data["improvement"] > threshold_threshold:
                            threshold_value = float(threshold_name.split("_")[1])
                            X_enhanced[f"{feature}_above_{threshold_value:.4f}"] = (
                                X[feature] > threshold_value
                            ).astype(int)
                            X_enhanced[
                                f"{feature}_interaction_{threshold_value:.4f}"
                            ] = (
                                X[feature]
                                * X_enhanced[f"{feature}_above_{threshold_value:.4f}"]
                            )

            # 添加分段回归阈值特征
            if "piecewise_regression" in self.thresholds:
                for feature, feature_data in self.thresholds[
                    "piecewise_regression"
                ].items():
                    threshold = feature_data["optimal_threshold"]
                    X_enhanced[f"{feature}_above_threshold"] = (
                        X[feature] > threshold
                    ).astype(int)
                    X_enhanced[f"{feature}_interaction"] = (
                        X[feature] * X_enhanced[f"{feature}_above_threshold"]
                    )

            # 添加随机森林阈值特征
            if "random_forest" in self.thresholds:
                for feature, feature_data in self.thresholds["random_forest"].items():
                    threshold = feature_data["best_threshold"]
                    X_enhanced[f"{feature}_above_rf_threshold"] = (
                        X[feature] > threshold
                    ).astype(int)
                    X_enhanced[f"{feature}_rf_interaction"] = (
                        X[feature] * X_enhanced[f"{feature}_above_rf_threshold"]
                    )

            logger.info(
                f"阈值特征创建完成，新增 {len(X_enhanced.columns) - len(X.columns)} 个特征"
            )
            return X_enhanced

        except Exception as e:
            logger.error(f"阈值特征创建失败: {e}")
            return X

    def get_threshold_insights(self) -> Dict[str, Any]:
        """获取阈值效应洞察"""
        try:
            insights = {
                "overall_threshold_score": self.thresholds.get("overall_score", 0),
                "threshold_level": self._classify_threshold_level(
                    self.thresholds.get("overall_score", 0)
                ),
                "key_thresholds": self._extract_key_thresholds(),
                "recommendations": self._generate_threshold_recommendations(),
            }

            return insights

        except Exception as e:
            logger.error(f"阈值效应洞察获取失败: {e}")
            return {}

    def _classify_threshold_level(self, score: float) -> str:
        """分类阈值效应水平"""
        if score >= 0.7:
            return "高阈值效应"
        elif score >= 0.4:
            return "中等阈值效应"
        elif score >= 0.1:
            return "低阈值效应"
        else:
            return "无显著阈值效应"

    def _extract_key_thresholds(self) -> List[Dict[str, Any]]:
        """提取关键阈值"""
        try:
            key_thresholds = []

            # 从决策树阈值中提取
            if "decision_tree" in self.thresholds:
                for feature, feature_data in self.thresholds["decision_tree"].items():
                    for threshold_name, threshold_data in feature_data[
                        "effectiveness"
                    ].items():
                        if threshold_data["improvement"] > 0.1:
                            threshold_value = float(threshold_name.split("_")[1])
                            key_thresholds.append(
                                {
                                    "type": "decision_tree",
                                    "feature": feature,
                                    "threshold": threshold_value,
                                    "improvement": threshold_data["improvement"],
                                }
                            )

            # 从分段回归中提取
            if "piecewise_regression" in self.thresholds:
                for feature, feature_data in self.thresholds[
                    "piecewise_regression"
                ].items():
                    performance = feature_data["performance"]
                    if performance["r2_improvement"] > 0.05:
                        key_thresholds.append(
                            {
                                "type": "piecewise_regression",
                                "feature": feature,
                                "threshold": feature_data["optimal_threshold"],
                                "improvement": performance["r2_improvement"],
                            }
                        )

            # 从随机森林阈值中提取
            if "random_forest" in self.thresholds:
                for feature, feature_data in self.thresholds["random_forest"].items():
                    if feature_data["improvement"] > 0.05:
                        key_thresholds.append(
                            {
                                "type": "random_forest",
                                "feature": feature,
                                "threshold": feature_data["best_threshold"],
                                "improvement": feature_data["improvement"],
                            }
                        )

            # 按改进程度排序
            key_thresholds.sort(key=lambda x: x["improvement"], reverse=True)

            return key_thresholds[:10]

        except Exception as e:
            logger.error(f"关键阈值提取失败: {e}")
            return []

    def _generate_threshold_recommendations(self) -> List[str]:
        """生成阈值效应建议"""
        try:
            recommendations = []

            threshold_score = self.thresholds.get("overall_score", 0)

            if threshold_score >= 0.7:
                recommendations.append("检测到高阈值效应，建议使用分段回归模型")
                recommendations.append("考虑在业务决策中设置关键阈值点")
            elif threshold_score >= 0.4:
                recommendations.append("检测到中等阈值效应，建议添加阈值特征")
                recommendations.append("考虑使用决策树或随机森林模型")
            elif threshold_score >= 0.1:
                recommendations.append("检测到低阈值效应，建议进一步分析特征分布")
                recommendations.append("考虑使用非线性模型来捕捉阈值效应")
            else:
                recommendations.append("未检测到显著阈值效应，建议使用线性模型")
                recommendations.append("考虑检查数据质量和特征工程")

            return recommendations

        except Exception as e:
            logger.error(f"阈值效应建议生成失败: {e}")
            return []

    # 新增核心方法
    def detect_multiple_thresholds(
        self, X: pd.DataFrame, y: pd.Series, max_thresholds: int = 3
    ) -> Dict[str, Any]:
        """
        检测多个阈值点

        Args:
            X: 特征数据
            y: 目标变量
            max_thresholds: 最大阈值数量

        Returns:
            多阈值分析结果
        """
        try:
            multi_threshold_results = {}

            for feature in X.columns:
                # 使用决策树检测多个阈值
                tree = DecisionTreeRegressor(
                    max_depth=max_thresholds + 1, min_samples_split=20, random_state=42
                )
                tree.fit(X[[feature]], y)

                # 提取所有阈值
                thresholds = self._extract_tree_thresholds(tree, feature)

                if len(thresholds) > 1:
                    # 评估多阈值模型
                    multi_threshold_performance = self._evaluate_multi_threshold_model(
                        X, y, feature, thresholds
                    )

                    multi_threshold_results[feature] = {
                        "thresholds": thresholds,
                        "performance": multi_threshold_performance,
                        "segment_count": len(thresholds) + 1,
                    }

            return multi_threshold_results

        except Exception as e:
            logger.error(f"多阈值检测失败: {e}")
            return {}

    def _evaluate_multi_threshold_model(
        self, X: pd.DataFrame, y: pd.Series, feature: str, thresholds: List[float]
    ) -> Dict[str, float]:
        """评估多阈值模型性能"""
        try:
            # 创建分段特征
            X_segmented = X.copy()

            # 为每个阈值创建分段特征
            for i, threshold in enumerate(thresholds):
                X_segmented[f"{feature}_segment_{i}"] = (X[feature] > threshold).astype(
                    int
                )

            # 创建交互项
            for i, threshold in enumerate(thresholds):
                X_segmented[f"{feature}_interaction_{i}"] = (
                    X[feature] * X_segmented[f"{feature}_segment_{i}"]
                )

            # 训练多阈值模型
            feature_columns = [feature] + [
                f"{feature}_segment_{i}" for i in range(len(thresholds))
            ]
            feature_columns += [
                f"{feature}_interaction_{i}" for i in range(len(thresholds))
            ]

            model = LinearRegression()
            model.fit(X_segmented[feature_columns], y)

            # 训练基线模型
            baseline_model = LinearRegression()
            baseline_model.fit(X[[feature]], y)

            # 计算性能提升
            r2_multi = model.score(X_segmented[feature_columns], y)
            r2_baseline = baseline_model.score(X[[feature]], y)

            return {
                "r2_multi_threshold": r2_multi,
                "r2_baseline": r2_baseline,
                "improvement": r2_multi - r2_baseline,
                "coefficients": model.coef_.tolist(),
                "intercept": model.intercept_,
            }

        except Exception as e:
            logger.error(f"多阈值模型评估失败: {e}")
            return {}

    def analyze_threshold_stability(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        feature: str,
        threshold: float,
        bootstrap_samples: int = 100,
    ) -> Dict[str, Any]:
        """
        分析阈值稳定性

        Args:
            X: 特征数据
            y: 目标变量
            feature: 特征名
            threshold: 阈值
            bootstrap_samples: 自助采样次数

        Returns:
            阈值稳定性分析结果
        """
        try:
            stability_results = {
                "threshold_stability": [],
                "performance_stability": [],
                "coefficient_stability": [],
            }

            for _ in range(bootstrap_samples):
                # 自助采样
                sample_indices = np.random.choice(len(X), size=len(X), replace=True)
                X_sample = X.iloc[sample_indices]
                y_sample = y.iloc[sample_indices]

                # 重新计算最优阈值
                optimal_threshold = self._find_optimal_threshold(
                    X_sample, y_sample, feature, 20
                )

                if optimal_threshold is not None:
                    stability_results["threshold_stability"].append(optimal_threshold)

                    # 计算性能
                    performance = self._calculate_piecewise_score(
                        X_sample, y_sample, feature, optimal_threshold
                    )
                    stability_results["performance_stability"].append(performance)

                    # 计算系数
                    model = self._create_piecewise_model(
                        X_sample, y_sample, feature, optimal_threshold
                    )
                    if model:
                        stability_results["coefficient_stability"].append(
                            model["below_threshold_coef"]
                        )

            # 计算稳定性指标
            threshold_std = (
                np.std(stability_results["threshold_stability"])
                if stability_results["threshold_stability"]
                else 0
            )
            performance_std = (
                np.std(stability_results["performance_stability"])
                if stability_results["performance_stability"]
                else 0
            )
            coefficient_std = (
                np.std(stability_results["coefficient_stability"])
                if stability_results["coefficient_stability"]
                else 0
            )

            return {
                "threshold_stability": {
                    "mean": (
                        np.mean(stability_results["threshold_stability"])
                        if stability_results["threshold_stability"]
                        else threshold
                    ),
                    "std": threshold_std,
                    "cv": (
                        threshold_std
                        / np.mean(stability_results["threshold_stability"])
                        if stability_results["threshold_stability"]
                        else 0
                    ),
                },
                "performance_stability": {
                    "mean": (
                        np.mean(stability_results["performance_stability"])
                        if stability_results["performance_stability"]
                        else 0
                    ),
                    "std": performance_std,
                    "cv": (
                        performance_std
                        / np.mean(stability_results["performance_stability"])
                        if stability_results["performance_stability"]
                        else 0
                    ),
                },
                "coefficient_stability": {
                    "mean": (
                        np.mean(stability_results["coefficient_stability"])
                        if stability_results["coefficient_stability"]
                        else 0
                    ),
                    "std": coefficient_std,
                    "cv": (
                        coefficient_std
                        / np.mean(stability_results["coefficient_stability"])
                        if stability_results["coefficient_stability"]
                        else 0
                    ),
                },
                "stability_score": self._calculate_stability_score(
                    threshold_std, performance_std, coefficient_std
                ),
            }

        except Exception as e:
            logger.error(f"阈值稳定性分析失败: {e}")
            return {}

    def _calculate_stability_score(
        self, threshold_std: float, performance_std: float, coefficient_std: float
    ) -> float:
        """计算稳定性评分"""
        try:
            # 标准化标准差
            threshold_cv = (
                threshold_std / 100 if threshold_std > 0 else 0
            )  # 假设阈值范围100
            performance_cv = (
                performance_std / 1 if performance_std > 0 else 0
            )  # R²范围0-1
            coefficient_cv = (
                coefficient_std / 10 if coefficient_std > 0 else 0
            )  # 假设系数范围10

            # 稳定性评分 = 1 - 平均变异系数
            avg_cv = (threshold_cv + performance_cv + coefficient_cv) / 3
            stability_score = max(0, 1 - avg_cv)

            return stability_score

        except Exception as e:
            logger.error(f"稳定性评分计算失败: {e}")
            return 0.0

    def detect_threshold_interactions(
        self, X: pd.DataFrame, y: pd.Series
    ) -> Dict[str, Any]:
        """
        检测阈值间的交互效应

        Args:
            X: 特征数据
            y: 目标变量

        Returns:
            阈值交互效应分析结果
        """
        try:
            interaction_results = {}
            feature_names = X.columns.tolist()

            # 检测两两特征的阈值交互
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i + 1 :], i + 1):
                    # 获取两个特征的最优阈值
                    threshold1 = self._find_optimal_threshold(X, y, feature1, 20)
                    threshold2 = self._find_optimal_threshold(X, y, feature2, 20)

                    if threshold1 is not None and threshold2 is not None:
                        # 创建阈值交互特征
                        X_interaction = X.copy()
                        X_interaction[f"{feature1}_above_threshold"] = (
                            X[feature1] > threshold1
                        ).astype(int)
                        X_interaction[f"{feature2}_above_threshold"] = (
                            X[feature2] > threshold2
                        ).astype(int)
                        X_interaction[f"threshold_interaction"] = (
                            X_interaction[f"{feature1}_above_threshold"]
                            * X_interaction[f"{feature2}_above_threshold"]
                        )

                        # 训练交互模型
                        feature_columns = [
                            feature1,
                            feature2,
                            f"{feature1}_above_threshold",
                            f"{feature2}_above_threshold",
                            "threshold_interaction",
                        ]

                        model = LinearRegression()
                        model.fit(X_interaction[feature_columns], y)

                        # 训练无交互模型
                        model_no_interaction = LinearRegression()
                        model_no_interaction.fit(X_interaction[feature_columns[:-1]], y)

                        # 计算交互效应
                        r2_with_interaction = model.score(
                            X_interaction[feature_columns], y
                        )
                        r2_without_interaction = model_no_interaction.score(
                            X_interaction[feature_columns[:-1]], y
                        )

                        interaction_effect = (
                            r2_with_interaction - r2_without_interaction
                        )

                        if abs(interaction_effect) > 0.01:  # 只记录显著的交互效应
                            interaction_results[f"{feature1}_x_{feature2}"] = {
                                "threshold1": threshold1,
                                "threshold2": threshold2,
                                "interaction_effect": interaction_effect,
                                "r2_with_interaction": r2_with_interaction,
                                "r2_without_interaction": r2_without_interaction,
                                "interaction_coefficient": model.coef_[-1],
                            }

            return interaction_results

        except Exception as e:
            logger.error(f"阈值交互效应检测失败: {e}")
            return {}

    def generate_threshold_report(self) -> Dict[str, Any]:
        """生成阈值分析报告"""
        try:
            report = {
                "summary": {
                    "overall_threshold_score": self.thresholds.get("overall_score", 0),
                    "threshold_level": self._classify_threshold_level(
                        self.thresholds.get("overall_score", 0)
                    ),
                    "analysis_timestamp": datetime.now().isoformat(),
                },
                "detailed_analysis": self.thresholds,
                "key_findings": self._extract_key_thresholds(),
                "recommendations": self._generate_threshold_recommendations(),
                "insights": self._generate_threshold_insights(),
            }

            return report

        except Exception as e:
            logger.error(f"阈值分析报告生成失败: {e}")
            return {}

    def _generate_threshold_insights(self) -> List[str]:
        """生成阈值效应洞察"""
        try:
            insights = []
            threshold_score = self.thresholds.get("overall_score", 0)

            # 基于阈值效应水平的洞察
            if threshold_score >= 0.7:
                insights.append(
                    "系统表现出强烈的阈值效应，特征在不同区间表现出不同的行为模式"
                )
                insights.append("建议使用分段回归或决策树模型来捕捉这些阈值效应")
            elif threshold_score >= 0.4:
                insights.append("系统表现出中等的阈值效应，部分特征存在关键转折点")
                insights.append("建议重点分析高阈值效应的特征，设置业务阈值")
            elif threshold_score >= 0.1:
                insights.append("系统表现出轻微的阈值效应，存在一些特征转折点")
                insights.append("建议进一步探索特征的非线性关系")
            else:
                insights.append("系统阈值效应较弱，特征主要表现为线性关系")
                insights.append("建议使用线性模型或简单的机器学习方法")

            # 基于具体分析结果的洞察
            if "decision_tree" in self.thresholds and self.thresholds["decision_tree"]:
                tree_count = len(self.thresholds["decision_tree"])
                insights.append(f"决策树分析发现 {tree_count} 个特征存在阈值效应")

            if (
                "piecewise_regression" in self.thresholds
                and self.thresholds["piecewise_regression"]
            ):
                piecewise_count = len(self.thresholds["piecewise_regression"])
                insights.append(f"分段回归分析发现 {piecewise_count} 个特征的最优阈值")

            return insights

        except Exception as e:
            logger.error(f"阈值洞察生成失败: {e}")
            return []
