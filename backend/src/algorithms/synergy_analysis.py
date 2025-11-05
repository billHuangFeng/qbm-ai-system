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
from datetime import datetime
from ..logging_config import get_logger

logger = get_logger("synergy_analysis")


class SynergyAnalysis:
    """协同效应分析"""

    def __init__(self):
        self.synergy_effects = {}
        self.interaction_terms = {}
        self.synergy_models = {}

    def detect_synergy_effects(
        self, X: pd.DataFrame, y: pd.Series, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """检测协同效应"""
        try:
            synergy_results = {}

            # 1. 两两交互效应分析
            pairwise_synergy = self._analyze_pairwise_interactions(X, y, threshold)
            synergy_results["pairwise"] = pairwise_synergy

            # 2. 多项式特征分析
            polynomial_synergy = self._analyze_polynomial_interactions(X, y, threshold)
            synergy_results["polynomial"] = polynomial_synergy

            # 3. 随机森林特征重要性分析
            rf_synergy = self._analyze_rf_interactions(X, y, threshold)
            synergy_results["random_forest"] = rf_synergy

            # 4. 综合协同效应评分
            synergy_score = self._calculate_synergy_score(synergy_results)
            synergy_results["overall_score"] = synergy_score

            self.synergy_effects = synergy_results
            logger.info(f"协同效应分析完成，整体评分: {synergy_score:.4f}")

            return synergy_results

        except Exception as e:
            logger.error(f"协同效应检测失败: {e}")
            raise

    def _analyze_pairwise_interactions(
        self, X: pd.DataFrame, y: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """分析两两交互效应"""
        try:
            interactions = {}
            feature_names = X.columns.tolist()

            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i + 1 :], i + 1):
                    # 创建交互项
                    interaction_term = X[feature1] * X[feature2]

                    # 训练包含交互项的模型
                    X_with_interaction = X.copy()
                    X_with_interaction[f"{feature1}_x_{feature2}"] = interaction_term

                    # 比较有无交互项的模型性能
                    model_without = LinearRegression()
                    model_with = LinearRegression()

                    model_without.fit(X[[feature1, feature2]], y)
                    model_with.fit(
                        X_with_interaction[
                            [feature1, feature2, f"{feature1}_x_{feature2}"]
                        ],
                        y,
                    )

                    # 计算性能提升
                    r2_without = model_without.score(X[[feature1, feature2]], y)
                    r2_with = model_with.score(
                        X_with_interaction[
                            [feature1, feature2, f"{feature1}_x_{feature2}"]
                        ],
                        y,
                    )

                    improvement = r2_with - r2_without

                    if improvement > threshold:
                        interactions[f"{feature1}_x_{feature2}"] = {
                            "improvement": improvement,
                            "r2_without": r2_without,
                            "r2_with": r2_with,
                            "coefficient": model_with.coef_[-1],
                            "significance": self._calculate_significance(
                                X, y, interaction_term
                            ),
                        }

            logger.info(f"发现 {len(interactions)} 个显著的两两交互效应")
            return interactions

        except Exception as e:
            logger.error(f"两两交互效应分析失败: {e}")
            return {}

    def _analyze_polynomial_interactions(
        self, X: pd.DataFrame, y: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """分析多项式交互效应"""
        try:
            polynomial_results = {}

            # 生成多项式特征
            poly = PolynomialFeatures(
                degree=2, include_bias=False, interaction_only=True
            )
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
                    if " " in feature_name:  # 交互项
                        interaction_coeffs[feature_name] = {
                            "coefficient": model_poly.coef_[i],
                            "importance": abs(model_poly.coef_[i]),
                        }

                polynomial_results = {
                    "improvement": improvement,
                    "r2_linear": r2_linear,
                    "r2_poly": r2_poly,
                    "interaction_coefficients": interaction_coeffs,
                    "top_interactions": sorted(
                        interaction_coeffs.items(),
                        key=lambda x: x[1]["importance"],
                        reverse=True,
                    )[:10],
                }

            logger.info(f"多项式交互效应分析完成，性能提升: {improvement:.4f}")
            return polynomial_results

        except Exception as e:
            logger.error(f"多项式交互效应分析失败: {e}")
            return {}

    def _analyze_rf_interactions(
        self, X: pd.DataFrame, y: pd.Series, threshold: float
    ) -> Dict[str, Any]:
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
                feature: importance
                for feature, importance in feature_importance.items()
                if importance > mean_importance + std_importance
            }

            # 分析特征组合的重要性
            feature_combinations = self._analyze_feature_combinations(X, y, rf)

            rf_results = {
                "feature_importance": feature_importance,
                "high_importance_features": high_importance_features,
                "feature_combinations": feature_combinations,
                "importance_stats": {
                    "mean": mean_importance,
                    "std": std_importance,
                    "max": max(importance_values),
                    "min": min(importance_values),
                },
            }

            logger.info(
                f"随机森林交互效应分析完成，发现 {len(high_importance_features)} 个高重要性特征"
            )
            return rf_results

        except Exception as e:
            logger.error(f"随机森林交互效应分析失败: {e}")
            return {}

    def _analyze_feature_combinations(
        self, X: pd.DataFrame, y: pd.Series, rf: RandomForestRegressor
    ) -> Dict[str, Any]:
        """分析特征组合的重要性"""
        try:
            combinations = {}
            feature_names = X.columns.tolist()

            # 分析两两特征组合
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i + 1 :], i + 1):
                    # 创建组合特征
                    combined_feature = X[feature1] * X[feature2]

                    # 计算组合特征与目标变量的相关性
                    correlation = np.corrcoef(combined_feature, y)[0, 1]

                    # 计算组合特征的重要性
                    importance = abs(correlation) * (
                        rf.feature_importances_[i] + rf.feature_importances_[j]
                    )

                    combinations[f"{feature1}_x_{feature2}"] = {
                        "correlation": correlation,
                        "importance": importance,
                        "feature1_importance": rf.feature_importances_[i],
                        "feature2_importance": rf.feature_importances_[j],
                    }

            # 按重要性排序
            sorted_combinations = sorted(
                combinations.items(), key=lambda x: x[1]["importance"], reverse=True
            )

            return {
                "all_combinations": combinations,
                "top_combinations": sorted_combinations[:10],
            }

        except Exception as e:
            logger.error(f"特征组合分析失败: {e}")
            return {}

    def _calculate_significance(
        self, X: pd.DataFrame, y: pd.Series, interaction_term: pd.Series
    ) -> float:
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
            weights = {"pairwise": 0.4, "polynomial": 0.3, "random_forest": 0.3}

            # 两两交互效应评分
            if "pairwise" in synergy_results and synergy_results["pairwise"]:
                pairwise_count = len(synergy_results["pairwise"])
                pairwise_avg_improvement = np.mean(
                    [
                        result["improvement"]
                        for result in synergy_results["pairwise"].values()
                    ]
                )
                score += weights["pairwise"] * pairwise_count * pairwise_avg_improvement

            # 多项式交互效应评分
            if "polynomial" in synergy_results and synergy_results["polynomial"]:
                poly_improvement = synergy_results["polynomial"].get("improvement", 0)
                score += weights["polynomial"] * poly_improvement

            # 随机森林交互效应评分
            if "random_forest" in synergy_results and synergy_results["random_forest"]:
                rf_high_importance = len(
                    synergy_results["random_forest"].get("high_importance_features", {})
                )
                rf_avg_importance = (
                    synergy_results["random_forest"]
                    .get("importance_stats", {})
                    .get("mean", 0)
                )
                score += (
                    weights["random_forest"] * rf_high_importance * rf_avg_importance
                )

            return min(score, 1.0)  # 限制在0-1范围内

        except Exception as e:
            logger.error(f"协同效应评分计算失败: {e}")
            return 0.0

    def create_synergy_features(
        self, X: pd.DataFrame, synergy_threshold: float = 0.1
    ) -> pd.DataFrame:
        """创建协同效应特征"""
        try:
            X_enhanced = X.copy()

            # 添加两两交互项
            if "pairwise" in self.synergy_effects:
                for interaction_name, interaction_data in self.synergy_effects[
                    "pairwise"
                ].items():
                    if interaction_data["improvement"] > synergy_threshold:
                        feature1, feature2 = interaction_name.split("_x_")
                        X_enhanced[interaction_name] = X[feature1] * X[feature2]

            # 添加多项式特征
            if (
                "polynomial" in self.synergy_effects
                and self.synergy_effects["polynomial"]
            ):
                poly = PolynomialFeatures(
                    degree=2, include_bias=False, interaction_only=True
                )
                X_poly = poly.fit_transform(X)
                poly_feature_names = poly.get_feature_names_out(X.columns)

                for i, feature_name in enumerate(poly_feature_names):
                    if " " in feature_name:  # 交互项
                        X_enhanced[feature_name.replace(" ", "_")] = X_poly[:, i]

            logger.info(
                f"协同效应特征创建完成，新增 {len(X_enhanced.columns) - len(X.columns)} 个特征"
            )
            return X_enhanced

        except Exception as e:
            logger.error(f"协同效应特征创建失败: {e}")
            return X

    def get_synergy_insights(self) -> Dict[str, Any]:
        """获取协同效应洞察"""
        try:
            insights = {
                "overall_synergy_score": self.synergy_effects.get("overall_score", 0),
                "synergy_level": self._classify_synergy_level(
                    self.synergy_effects.get("overall_score", 0)
                ),
                "key_interactions": self._extract_key_interactions(),
                "recommendations": self._generate_recommendations(),
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
            if "pairwise" in self.synergy_effects:
                for name, data in self.synergy_effects["pairwise"].items():
                    if data["improvement"] > 0.1:
                        key_interactions.append(
                            {
                                "type": "pairwise",
                                "name": name,
                                "improvement": data["improvement"],
                                "coefficient": data["coefficient"],
                            }
                        )

            # 从多项式交互中提取
            if (
                "polynomial" in self.synergy_effects
                and self.synergy_effects["polynomial"]
            ):
                top_interactions = self.synergy_effects["polynomial"].get(
                    "top_interactions", []
                )
                for name, data in top_interactions[:5]:
                    key_interactions.append(
                        {
                            "type": "polynomial",
                            "name": name,
                            "coefficient": data["coefficient"],
                            "importance": data["importance"],
                        }
                    )

            # 按重要性排序
            key_interactions.sort(
                key=lambda x: x.get("improvement", x.get("importance", 0)), reverse=True
            )

            return key_interactions[:10]

        except Exception as e:
            logger.error(f"关键交互项提取失败: {e}")
            return []

    def _generate_recommendations(self) -> List[str]:
        """生成协同效应建议"""
        try:
            recommendations = []

            synergy_score = self.synergy_effects.get("overall_score", 0)

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

    # 新增核心方法
    def calculate_shapley_values(
        self, X: pd.DataFrame, y: pd.Series, model: Any = None
    ) -> Dict[str, Any]:
        """
        计算Shapley值来量化协同效应

        Args:
            X: 特征数据
            y: 目标变量
            model: 训练好的模型

        Returns:
            Shapley值分析结果
        """
        try:
            if model is None:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, y)

            shapley_values = {}
            feature_names = X.columns.tolist()

            # 计算每个特征的边际贡献
            for feature in feature_names:
                marginal_contributions = []

                # 计算所有可能的特征组合
                other_features = [f for f in feature_names if f != feature]

                for subset_size in range(len(other_features) + 1):
                    for subset in itertools.combinations(other_features, subset_size):
                        # 计算有该特征时的性能
                        features_with = list(subset) + [feature]
                        X_with = X[features_with]

                        # 计算无该特征时的性能
                        features_without = list(subset)
                        X_without = (
                            X[features_without]
                            if features_without
                            else X[[feature]].iloc[:, :0]
                        )

                        # 训练模型并计算性能
                        if len(features_with) > 0:
                            model_with = RandomForestRegressor(
                                n_estimators=50, random_state=42
                            )
                            model_with.fit(X_with, y)
                            score_with = model_with.score(X_with, y)
                        else:
                            score_with = 0

                        if len(features_without) > 0:
                            model_without = RandomForestRegressor(
                                n_estimators=50, random_state=42
                            )
                            model_without.fit(X_without, y)
                            score_without = model_without.score(X_without, y)
                        else:
                            score_without = 0

                        # 计算边际贡献
                        marginal_contribution = score_with - score_without
                        weight = 1.0 / (len(other_features) + 1)  # 权重
                        marginal_contributions.append(marginal_contribution * weight)

                # Shapley值是所有边际贡献的加权平均
                shapley_values[feature] = sum(marginal_contributions)

            # 计算协同效应
            synergy_effects = self._calculate_synergy_from_shapley(shapley_values, X, y)

            return {
                "shapley_values": shapley_values,
                "synergy_effects": synergy_effects,
                "feature_ranking": sorted(
                    shapley_values.items(), key=lambda x: x[1], reverse=True
                ),
            }

        except Exception as e:
            logger.error(f"Shapley值计算失败: {e}")
            return {}

    def _calculate_synergy_from_shapley(
        self, shapley_values: Dict[str, float], X: pd.DataFrame, y: pd.Series
    ) -> Dict[str, Any]:
        """从Shapley值计算协同效应"""
        try:
            synergy_effects = {}
            feature_names = X.columns.tolist()

            # 计算两两协同效应
            for i, feature1 in enumerate(feature_names):
                for j, feature2 in enumerate(feature_names[i + 1 :], i + 1):
                    # 计算单独特征的Shapley值之和
                    individual_sum = shapley_values[feature1] + shapley_values[feature2]

                    # 计算组合特征的Shapley值
                    combined_feature = X[feature1] * X[feature2]
                    X_combined = X.copy()
                    X_combined[f"{feature1}_x_{feature2}"] = combined_feature

                    # 训练包含组合特征的模型
                    model_combined = RandomForestRegressor(
                        n_estimators=50, random_state=42
                    )
                    model_combined.fit(X_combined, y)

                    # 计算组合特征的贡献
                    feature_importance = dict(
                        zip(X_combined.columns, model_combined.feature_importances_)
                    )
                    combined_importance = feature_importance.get(
                        f"{feature1}_x_{feature2}", 0
                    )

                    # 协同效应 = 组合贡献 - 单独贡献之和
                    synergy = combined_importance - individual_sum

                    if abs(synergy) > 0.01:  # 只记录显著的协同效应
                        synergy_effects[f"{feature1}_x_{feature2}"] = {
                            "synergy_value": synergy,
                            "individual_sum": individual_sum,
                            "combined_importance": combined_importance,
                            "synergy_type": "positive" if synergy > 0 else "negative",
                        }

            return synergy_effects

        except Exception as e:
            logger.error(f"协同效应计算失败: {e}")
            return {}

    def analyze_nonlinear_synergy(
        self, X: pd.DataFrame, y: pd.Series, degree: int = 3
    ) -> Dict[str, Any]:
        """
        分析非线性协同效应

        Args:
            X: 特征数据
            y: 目标变量
            degree: 多项式度数

        Returns:
            非线性协同效应分析结果
        """
        try:
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import Ridge

            nonlinear_results = {}

            # 生成不同度数的多项式特征
            for d in range(2, degree + 1):
                poly = PolynomialFeatures(degree=d, include_bias=False)
                X_poly = poly.fit_transform(X)

                # 训练多项式模型
                model_poly = Ridge(alpha=1.0)
                model_poly.fit(X_poly, y)

                # 训练线性模型
                model_linear = Ridge(alpha=1.0)
                model_linear.fit(X, y)

                # 计算性能提升
                r2_linear = model_linear.score(X, y)
                r2_poly = model_poly.score(X_poly, y)
                improvement = r2_poly - r2_linear

                # 分析非线性项的重要性
                poly_feature_names = poly.get_feature_names_out(X.columns)
                nonlinear_terms = {}

                for i, feature_name in enumerate(poly_feature_names):
                    if any(char.isdigit() for char in feature_name):  # 包含幂次的特征
                        nonlinear_terms[feature_name] = {
                            "coefficient": model_poly.coef_[i],
                            "importance": abs(model_poly.coef_[i]),
                        }

                nonlinear_results[f"degree_{d}"] = {
                    "improvement": improvement,
                    "r2_linear": r2_linear,
                    "r2_poly": r2_poly,
                    "nonlinear_terms": nonlinear_terms,
                    "top_nonlinear_terms": sorted(
                        nonlinear_terms.items(),
                        key=lambda x: x[1]["importance"],
                        reverse=True,
                    )[:10],
                }

            return nonlinear_results

        except Exception as e:
            logger.error(f"非线性协同效应分析失败: {e}")
            return {}

    def detect_threshold_synergy(
        self, X: pd.DataFrame, y: pd.Series, threshold_method: str = "quantile"
    ) -> Dict[str, Any]:
        """
        检测阈值协同效应

        Args:
            X: 特征数据
            y: 目标变量
            threshold_method: 阈值计算方法

        Returns:
            阈值协同效应分析结果
        """
        try:
            threshold_results = {}
            feature_names = X.columns.tolist()

            for feature in feature_names:
                # 计算阈值
                if threshold_method == "quantile":
                    threshold = X[feature].quantile(0.5)  # 中位数作为阈值
                elif threshold_method == "mean":
                    threshold = X[feature].mean()
                else:
                    threshold = X[feature].median()

                # 创建阈值特征
                X_threshold = X.copy()
                X_threshold[f"{feature}_above_threshold"] = (
                    X[feature] > threshold
                ).astype(int)

                # 计算阈值效应
                above_threshold = X[feature] > threshold
                below_threshold = X[feature] <= threshold

                if above_threshold.sum() > 0 and below_threshold.sum() > 0:
                    # 计算阈值上下的平均目标值
                    y_above = y[above_threshold].mean()
                    y_below = y[below_threshold].mean()

                    # 计算阈值效应强度
                    threshold_effect = abs(y_above - y_below)

                    # 计算阈值与其他特征的交互效应
                    interaction_effects = {}
                    for other_feature in feature_names:
                        if other_feature != feature:
                            # 计算阈值特征与其他特征的交互
                            interaction_term = (
                                X_threshold[f"{feature}_above_threshold"]
                                * X[other_feature]
                            )

                            # 计算交互效应
                            correlation = np.corrcoef(interaction_term, y)[0, 1]
                            interaction_effects[other_feature] = {
                                "correlation": correlation,
                                "strength": abs(correlation),
                            }

                    threshold_results[feature] = {
                        "threshold_value": threshold,
                        "threshold_effect": threshold_effect,
                        "y_above_threshold": y_above,
                        "y_below_threshold": y_below,
                        "interaction_effects": interaction_effects,
                        "top_interactions": sorted(
                            interaction_effects.items(),
                            key=lambda x: x[1]["strength"],
                            reverse=True,
                        )[:5],
                    }

            return threshold_results

        except Exception as e:
            logger.error(f"阈值协同效应检测失败: {e}")
            return {}

    def generate_synergy_report(self) -> Dict[str, Any]:
        """生成协同效应分析报告"""
        try:
            report = {
                "summary": {
                    "overall_synergy_score": self.synergy_effects.get(
                        "overall_score", 0
                    ),
                    "synergy_level": self._classify_synergy_level(
                        self.synergy_effects.get("overall_score", 0)
                    ),
                    "analysis_timestamp": datetime.now().isoformat(),
                },
                "detailed_analysis": self.synergy_effects,
                "key_findings": self._extract_key_interactions(),
                "recommendations": self._generate_recommendations(),
                "insights": self._generate_insights(),
            }

            return report

        except Exception as e:
            logger.error(f"协同效应报告生成失败: {e}")
            return {}

    def _generate_insights(self) -> List[str]:
        """生成协同效应洞察"""
        try:
            insights = []
            synergy_score = self.synergy_effects.get("overall_score", 0)

            # 基于协同效应水平的洞察
            if synergy_score >= 0.7:
                insights.append("系统表现出强烈的协同效应，特征间存在复杂的非线性关系")
                insights.append("建议使用集成模型或深度学习方法来捕捉这些复杂交互")
            elif synergy_score >= 0.4:
                insights.append("系统表现出中等的协同效应，部分特征组合具有增强效果")
                insights.append("建议重点分析高协同效应的特征组合")
            elif synergy_score >= 0.1:
                insights.append("系统表现出轻微的协同效应，存在一些特征交互")
                insights.append("建议进一步探索特征间的潜在关系")
            else:
                insights.append("系统协同效应较弱，特征间主要是线性关系")
                insights.append("建议使用线性模型或简单的机器学习方法")

            # 基于具体分析结果的洞察
            if "pairwise" in self.synergy_effects and self.synergy_effects["pairwise"]:
                pairwise_count = len(self.synergy_effects["pairwise"])
                insights.append(f"发现 {pairwise_count} 个显著的两两交互效应")

            if (
                "polynomial" in self.synergy_effects
                and self.synergy_effects["polynomial"]
            ):
                poly_improvement = self.synergy_effects["polynomial"].get(
                    "improvement", 0
                )
                insights.append(f"多项式特征可提升模型性能 {poly_improvement:.3f}")

            return insights

        except Exception as e:
            logger.error(f"洞察生成失败: {e}")
            return []
