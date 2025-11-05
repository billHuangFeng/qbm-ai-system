"""
AI驱动北极星指标推荐服务
集成DynamicWeights优化指标权重
集成ARIMAModel预测指标趋势
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

from ...algorithms.dynamic_weights import DynamicWeightCalculator
from ...algorithms.time_series import ARIMAModel, VARModel
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AINorthStarService:
    """AI驱动北极星指标推荐服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        # 初始化AI算法
        self.weight_calculator = DynamicWeightCalculator()
        self.arima_model = ARIMAModel(order=(1, 1, 1))

        logger.info("AI驱动北极星指标服务初始化完成")

    async def create_north_star_metric(
        self,
        metric_name: str,
        metric_description: str,
        strategic_objective_id: str,
        metric_type: str,
        target_value: Optional[float] = None,
        calculation_formula: Optional[str] = None,
        measurement_frequency: str = "monthly",
        **kwargs,
    ) -> Dict[str, Any]:
        """创建北极星指标"""
        try:
            # 1. 插入基础数据
            metric_code = await self._generate_metric_code()

            if self.db_service:
                metric_id = await self.db_service.execute_insert(
                    """
                    INSERT INTO north_star_metrics
                    (metric_name, metric_description, metric_code, strategic_objective_id,
                     metric_type, target_value, calculation_formula, measurement_frequency,
                     status, is_primary)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING metric_id
                    """,
                    [
                        metric_name,
                        metric_description,
                        metric_code,
                        strategic_objective_id,
                        metric_type,
                        target_value,
                        calculation_formula,
                        measurement_frequency,
                        "active",
                        kwargs.get("is_primary", False),
                    ],
                )
            else:
                metric_id = "mock_metric_id"

            # 2. AI优化权重
            ai_weight = await self._calculate_ai_weight(
                metric_id, strategic_objective_id
            )

            # 3. AI趋势预测
            trend_prediction = await self._predict_trend(metric_id)

            # 4. 更新AI分析结果
            if self.db_service and metric_id:
                await self.db_service.execute_update(
                    """
                    UPDATE north_star_metrics
                    SET ai_weight = $1,
                        ai_weight_history = $2,
                        ai_trend_prediction = $3,
                        ai_recommendation_priority = $4
                    WHERE metric_id = $5
                    """,
                    [
                        ai_weight.get("weight", 0.5),
                        json.dumps([ai_weight]),
                        json.dumps(trend_prediction),
                        ai_weight.get("priority", 5),
                        metric_id,
                    ],
                )

            return {
                "success": True,
                "metric_id": metric_id,
                "metric_code": metric_code,
                "ai_weight": ai_weight,
                "trend_prediction": trend_prediction,
            }

        except Exception as e:
            logger.error(f"创建北极星指标失败: {e}")
            raise

    async def _calculate_ai_weight(
        self, metric_id: str, strategic_objective_id: str
    ) -> Dict[str, Any]:
        """AI计算指标权重"""
        try:
            # 1. 获取相关指标数据用于权重计算
            if self.db_service:
                # 获取同一战略目标下的所有指标
                related_metrics = await self.db_service.execute_query(
                    """
                    SELECT metric_id, metric_name, target_value, current_value, ai_weight
                    FROM north_star_metrics
                    WHERE strategic_objective_id = $1 AND status = 'active'
                    """,
                    [strategic_objective_id],
                )

                # 获取历史数据用于动态权重计算
                history_data = await self.db_service.execute_query(
                    """
                    SELECT metric_id, measurement_date, metric_value
                    FROM north_star_metric_history
                    WHERE metric_id IN (
                        SELECT metric_id FROM north_star_metrics
                        WHERE strategic_objective_id = $1 AND status = 'active'
                    )
                    AND measurement_date >= NOW() - INTERVAL '90 days'
                    ORDER BY metric_id, measurement_date
                    """,
                    [strategic_objective_id],
                )
            else:
                related_metrics = []
                history_data = []

            # 2. 准备数据用于DynamicWeightCalculator
            if len(related_metrics) > 1 and history_data:
                try:
                    # 将历史数据转换为DataFrame
                    history_df = pd.DataFrame(history_data)
                    if not history_df.empty:
                        history_df["measurement_date"] = pd.to_datetime(
                            history_df["measurement_date"]
                        )

                        # 透视表：每行是一个时间点，每列是一个指标
                        pivot_df = history_df.pivot_table(
                            index="measurement_date",
                            columns="metric_id",
                            values="metric_value",
                            aggfunc="mean",
                        )

                        if len(pivot_df.columns) > 1 and len(pivot_df) >= 10:
                            # 准备目标变量：使用指标达成度（target_value - current_value的绝对值）
                            metric_info = {m["metric_id"]: m for m in related_metrics}

                            # 创建目标变量：各指标的重要性（基于与目标的差距）
                            target_data = []
                            feature_columns = []

                            for col in pivot_df.columns:
                                if col in metric_info:
                                    metric = metric_info[col]
                                    target_val = metric.get("target_value")
                                    current_val = metric.get("current_value")

                                    if (
                                        target_val is not None
                                        and current_val is not None
                                    ):
                                        # 目标变量：目标与当前值的差距（差距越大，越重要）
                                        importance = (
                                            abs(target_val - current_val)
                                            if target_val != 0
                                            else abs(current_val)
                                        )
                                        target_data.append(importance)
                                        feature_columns.append(col)

                            if len(feature_columns) > 1 and len(target_data) == len(
                                feature_columns
                            ):
                                # 创建特征矩阵（使用最近N期的平均值）
                                X_data = (
                                    pivot_df[feature_columns].ffill().bfill().fillna(0)
                                )

                                if len(X_data) >= 10:
                                    # 使用最近N期的平均值作为特征
                                    n_periods = min(30, len(X_data))
                                    X_avg = X_data.tail(n_periods).mean()

                                    # 创建DataFrame和Series
                                    X = pd.DataFrame(
                                        [X_avg.values], columns=feature_columns
                                    )
                                    y = pd.Series(target_data, index=feature_columns)

                                    # 使用DynamicWeightCalculator计算权重
                                    weight_results = self.weight_calculator.calculate_dynamic_weights(
                                        X,
                                        y,
                                        method="comprehensive",
                                        update_frequency="monthly",
                                    )

                                    # 提取最终权重
                                    normalized_weights = weight_results.get(
                                        "normalized", {}
                                    )
                                    final_weights = normalized_weights.get("final", {})

                                    if final_weights and metric_id in final_weights:
                                        metric_weight = final_weights[metric_id]
                                        effectiveness = weight_results.get(
                                            "effectiveness", {}
                                        )

                                        return {
                                            "weight": float(metric_weight),
                                            "priority": min(
                                                10, max(1, int(metric_weight * 20))
                                            ),  # 转换为1-10的优先级
                                            "calculation_method": "dynamic_weights_comprehensive",
                                            "weight_details": {
                                                "correlation": normalized_weights.get(
                                                    "correlation", {}
                                                ).get(metric_id, 0),
                                                "importance": normalized_weights.get(
                                                    "importance", {}
                                                ).get(metric_id, 0),
                                                "regression": normalized_weights.get(
                                                    "regression", {}
                                                ).get(metric_id, 0),
                                                "time_series": normalized_weights.get(
                                                    "time_series", {}
                                                ).get(metric_id, 0),
                                            },
                                            "effectiveness": {
                                                "r2_improvement": effectiveness.get(
                                                    "r2_improvement", 0
                                                ),
                                                "effectiveness_score": effectiveness.get(
                                                    "effectiveness_score", 0
                                                ),
                                            },
                                            "stability": weight_results.get(
                                                "stability", {}
                                            ),
                                            "timestamp": datetime.now().isoformat(),
                                        }

                except Exception as e:
                    logger.warning(
                        f"使用DynamicWeightCalculator计算权重失败: {e}，回退到简化方法"
                    )

            # 3. 回退到简化的权重计算（基于目标差距）
            if len(related_metrics) > 1:
                metric_data = []
                target_data = []
                for metric in related_metrics:
                    if (
                        metric.get("target_value") is not None
                        and metric.get("current_value") is not None
                    ):
                        metric_data.append(
                            {
                                "metric_id": metric.get("metric_id"),
                                "target": metric.get("target_value"),
                                "current": metric.get("current_value"),
                            }
                        )
                        # 目标差距越大，权重越高
                        gap = abs(
                            metric.get("target_value", 0)
                            - metric.get("current_value", 0)
                        )
                        # 归一化：使用相对差距
                        target_val = abs(metric.get("target_value", 0))
                        if target_val > 0:
                            gap_ratio = gap / target_val
                        else:
                            gap_ratio = abs(metric.get("current_value", 0))
                        target_data.append(gap_ratio)

                if metric_data and target_data:
                    weights = {}
                    total_importance = sum(target_data)

                    for i, metric in enumerate(metric_data):
                        if total_importance > 0:
                            weight = target_data[i] / total_importance
                        else:
                            weight = 1.0 / len(metric_data)
                        weights[metric["metric_id"]] = weight

                    metric_weight = weights.get(metric_id, 0.5)
                else:
                    metric_weight = 0.5
            else:
                # 只有一个指标，默认权重为1.0
                metric_weight = 1.0

            return {
                "weight": float(metric_weight),
                "priority": min(
                    10, max(1, int(metric_weight * 20))
                ),  # 转换为1-10的优先级
                "calculation_method": "simplified_gap_based",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"AI权重计算失败: {e}")
            return {
                "weight": 0.5,
                "priority": 5,
                "calculation_method": "default",
                "timestamp": datetime.now().isoformat(),
            }

    async def _predict_trend(self, metric_id: str) -> Dict[str, Any]:
        """AI预测指标趋势"""
        try:
            # 1. 获取历史数据
            if self.db_service:
                history_data = await self.db_service.execute_query(
                    """
                    SELECT measurement_date, metric_value
                    FROM north_star_metric_history
                    WHERE metric_id = $1
                    ORDER BY measurement_date DESC
                    LIMIT 30
                    """,
                    [metric_id],
                )
            else:
                history_data = []

            if not history_data or len(history_data) < 10:
                # 数据不足，返回默认预测
                return {
                    "prediction_method": "insufficient_data",
                    "predicted_value": None,
                    "confidence": 0.3,
                    "forecast_periods": 3,
                }

            # 2. 准备时间序列数据
            df = pd.DataFrame(history_data)
            df["measurement_date"] = pd.to_datetime(df["measurement_date"])
            df = df.sort_values("measurement_date")
            time_series = df["metric_value"].values

            # 3. 使用ARIMA模型预测
            try:
                # 创建时间序列
                ts_series = pd.Series(time_series, index=df["measurement_date"].values)

                # 尝试使用不同的ARIMA订单，选择最佳模型
                best_arima = None
                best_aic = float("inf")
                orders_to_try = [(1, 1, 1), (1, 1, 0), (0, 1, 1), (2, 1, 1), (1, 2, 1)]

                for order in orders_to_try:
                    try:
                        arima = ARIMAModel(order=order)
                        arima.fit(ts_series)

                        # 检查模型质量（通过AIC）
                        if hasattr(arima.fitted_model, "aic"):
                            aic = arima.fitted_model.aic
                            if aic < best_aic:
                                best_aic = aic
                                best_arima = arima
                    except Exception as order_error:
                        logger.debug(f"ARIMA({order})拟合失败: {order_error}")
                        continue

                # 如果找到最佳模型，使用它进行预测
                if best_arima:
                    # 预测未来3个周期
                    forecast, lower, upper = best_arima.predict_interval(
                        steps=3, alpha=0.05
                    )

                    # 计算模型评估指标（如果有足够数据）
                    model_quality = {}
                    if len(time_series) >= 20:
                        try:
                            # 使用后20%的数据作为验证集
                            split_idx = int(len(time_series) * 0.8)
                            train_data = ts_series[:split_idx]
                            test_data = ts_series[split_idx:]

                            # 重新训练并评估
                            eval_arima = ARIMAModel(order=best_arima.order)
                            eval_arima.fit(train_data)
                            eval_results = eval_arima.evaluate(test_data)
                            model_quality = eval_results
                        except Exception:
                            pass

                    return {
                        "prediction_method": "arima",
                        "arima_order": best_arima.order,
                        "predicted_values": (
                            forecast.tolist()
                            if hasattr(forecast, "tolist")
                            else list(forecast)
                        ),
                        "confidence_intervals": {
                            "lower": (
                                lower.tolist()
                                if hasattr(lower, "tolist")
                                else list(lower)
                            ),
                            "upper": (
                                upper.tolist()
                                if hasattr(upper, "tolist")
                                else list(upper)
                            ),
                        },
                        "confidence": 0.8,
                        "model_quality": model_quality,
                        "forecast_periods": 3,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    raise ValueError("无法找到合适的ARIMA模型")

            except Exception as e:
                logger.warning(f"ARIMA模型预测失败: {e}，使用简单线性预测")
                # 使用简单线性预测
                if len(time_series) >= 2:
                    trend = (time_series[-1] - time_series[0]) / len(time_series)
                    last_value = time_series[-1]
                    predicted_values = [
                        float(last_value + trend * (i + 1)) for i in range(3)
                    ]
                    return {
                        "prediction_method": "linear",
                        "predicted_values": predicted_values,
                        "confidence": 0.6,
                        "forecast_periods": 3,
                    }
                else:
                    return {
                        "prediction_method": "insufficient_data",
                        "predicted_value": (
                            float(time_series[-1]) if len(time_series) > 0 else None
                        ),
                        "confidence": 0.3,
                        "forecast_periods": 3,
                    }

        except Exception as e:
            logger.error(f"趋势预测失败: {e}")
            return {"prediction_method": "error", "error": str(e), "confidence": 0.0}

    async def recommend_metrics(
        self, strategic_objective_id: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """AI推荐北极星指标"""
        try:
            recommendations = []

            # 1. 从企业记忆系统获取最佳实践
            if self.memory_service:
                try:
                    patterns = await self.memory_service.search_similar_patterns(
                        query=f"strategic objective {strategic_objective_id}", limit=10
                    )
                    for pattern in patterns[:5]:
                        pattern_dict = (
                            pattern.dict() if hasattr(pattern, "dict") else pattern
                        )
                        recommendations.append(
                            {
                                "metric_name": pattern_dict.get(
                                    "description", "推荐指标"
                                ),
                                "metric_type": "recommended",
                                "source": "enterprise_memory",
                                "confidence": pattern_dict.get("confidence", 0.6),
                                "rationale": "基于历史成功模式推荐",
                            }
                        )
                except Exception as e:
                    logger.warning(f"从企业记忆系统获取推荐失败: {e}")

            # 2. 基于战略目标类型推荐标准指标
            if self.db_service:
                objective = await self.db_service.execute_one(
                    """
                    SELECT objective_type, objective_content
                    FROM strategic_objectives
                    WHERE objective_id = $1
                    """,
                    [strategic_objective_id],
                )

                if objective:
                    obj_type = objective.get("objective_type", "")
                    # 根据目标类型推荐相应的指标
                    standard_metrics = self._get_standard_metrics_by_type(obj_type)
                    recommendations.extend(standard_metrics)

            # 3. 按置信度排序
            recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)

            return recommendations[:10]  # 返回Top 10

        except Exception as e:
            logger.error(f"推荐指标失败: {e}")
            return []

    def _get_standard_metrics_by_type(
        self, objective_type: str
    ) -> List[Dict[str, Any]]:
        """根据目标类型获取标准指标"""
        metric_templates = {
            "mission": [
                {
                    "metric_name": "使命达成度",
                    "metric_type": "completion",
                    "source": "standard_template",
                    "confidence": 0.8,
                    "rationale": "标准使命类指标",
                },
                {
                    "metric_name": "使命认知度",
                    "metric_type": "awareness",
                    "source": "standard_template",
                    "confidence": 0.7,
                    "rationale": "标准使命类指标",
                },
            ],
            "vision": [
                {
                    "metric_name": "愿景实现进度",
                    "metric_type": "progress",
                    "source": "standard_template",
                    "confidence": 0.8,
                    "rationale": "标准愿景类指标",
                }
            ],
            "strategic_goal": [
                {
                    "metric_name": "战略目标达成率",
                    "metric_type": "achievement",
                    "source": "standard_template",
                    "confidence": 0.9,
                    "rationale": "标准战略目标类指标",
                },
                {
                    "metric_name": "战略里程碑完成度",
                    "metric_type": "milestone",
                    "source": "standard_template",
                    "confidence": 0.7,
                    "rationale": "标准战略目标类指标",
                },
            ],
        }

        return metric_templates.get(objective_type, [])

    async def _generate_metric_code(self) -> str:
        """生成指标编码"""
        if self.db_service:
            try:
                result = await self.db_service.execute_one(
                    """
                    SELECT COUNT(*) as count
                    FROM north_star_metrics
                    WHERE metric_code LIKE 'NSM_%'
                    """
                )
                count = result.get("count", 0) if result else 0
                return f"NSM_{count + 1:06d}"
            except Exception:
                pass

        # 默认编码
        return f"NSM_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    async def update_metric_value(
        self,
        metric_id: str,
        metric_value: float,
        measurement_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """更新指标值并记录历史"""
        try:
            if not measurement_date:
                measurement_date = datetime.now().date().isoformat()

            # 1. 更新当前值
            if self.db_service:
                await self.db_service.execute_update(
                    """
                    UPDATE north_star_metrics
                    SET current_value = $1, updated_at = NOW()
                    WHERE metric_id = $2
                    """,
                    [metric_value, metric_id],
                )

                # 2. 记录历史值
                await self.db_service.execute_insert(
                    """
                    INSERT INTO north_star_metric_history
                    (metric_id, measurement_date, metric_value)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (metric_id, measurement_date) DO UPDATE
                    SET metric_value = EXCLUDED.metric_value
                    RETURNING history_id
                    """,
                    [metric_id, measurement_date, metric_value],
                )

                # 3. 重新计算AI权重和趋势
                metric = await self.db_service.execute_one(
                    """
                    SELECT strategic_objective_id FROM north_star_metrics
                    WHERE metric_id = $1
                    """,
                    [metric_id],
                )

                if metric:
                    ai_weight = await self._calculate_ai_weight(
                        metric_id, metric.get("strategic_objective_id")
                    )
                    trend_prediction = await self._predict_trend(metric_id)

                    await self.db_service.execute_update(
                        """
                        UPDATE north_star_metrics
                        SET ai_weight = $1,
                            ai_trend_prediction = $2
                        WHERE metric_id = $3
                        """,
                        [
                            ai_weight.get("weight", 0.5),
                            json.dumps(trend_prediction),
                            metric_id,
                        ],
                    )

            return {
                "success": True,
                "metric_id": metric_id,
                "updated_value": metric_value,
                "measurement_date": measurement_date,
            }

        except Exception as e:
            logger.error(f"更新指标值失败: {e}")
            raise

    async def get_north_star_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """获取北极星指标详情"""
        try:
            if not self.db_service:
                return None

            result = await self.db_service.execute_one(
                """
                SELECT * FROM north_star_metrics
                WHERE metric_id = $1
                """,
                [metric_id],
            )

            return result

        except Exception as e:
            logger.error(f"获取北极星指标失败: {e}")
            return None

    async def get_all_primary_metrics(self) -> List[Dict[str, Any]]:
        """获取所有主要北极星指标"""
        try:
            if not self.db_service:
                return []

            results = await self.db_service.execute_query(
                """
                SELECT * FROM north_star_metrics
                WHERE is_primary = true AND status = 'active'
                ORDER BY ai_weight DESC
                """
            )

            return results

        except Exception as e:
            logger.error(f"获取主要指标失败: {e}")
            return []

    async def batch_update_metric_values(
        self, updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量更新指标值"""
        try:
            results = []
            errors = []

            for update in updates:
                try:
                    metric_id = update.get("metric_id")
                    metric_value = update.get("metric_value")
                    measurement_date = update.get("measurement_date")

                    if not metric_id or metric_value is None:
                        errors.append(
                            {
                                "update": update,
                                "error": "缺少必要参数：metric_id 或 metric_value",
                            }
                        )
                        continue

                    result = await self.update_metric_value(
                        metric_id=metric_id,
                        metric_value=metric_value,
                        measurement_date=measurement_date,
                    )
                    results.append(result)

                except Exception as e:
                    errors.append({"update": update, "error": str(e)})
                    logger.error(f"批量更新中的单个指标更新失败: {e}")

            return {
                "success": len(errors) == 0,
                "updated_count": len(results),
                "error_count": len(errors),
                "results": results,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"批量更新指标值失败: {e}")
            raise

    async def calculate_metric_health_score(self, metric_id: str) -> Dict[str, Any]:
        """计算指标健康度评分"""
        try:
            if not self.db_service:
                return {"health_score": 0.5, "status": "unknown"}

            # 获取指标信息
            metric = await self.get_north_star_metric(metric_id)
            if not metric:
                return {"health_score": 0.0, "status": "not_found"}

            # 获取历史数据
            history_data = await self.db_service.execute_query(
                """
                SELECT measurement_date, metric_value
                FROM north_star_metric_history
                WHERE metric_id = $1
                ORDER BY measurement_date DESC
                LIMIT 30
                """,
                [metric_id],
            )

            target_value = metric.get("target_value")
            current_value = metric.get("current_value") or 0

            # 计算多个维度的健康度
            health_factors = {}

            # 1. 目标达成度
            if target_value is not None and target_value != 0:
                achievement_rate = (
                    min(1.0, abs(current_value / target_value))
                    if target_value > 0
                    else 0
                )
                health_factors["achievement"] = achievement_rate
            else:
                health_factors["achievement"] = 0.5

            # 2. 趋势健康度（基于预测）
            try:
                trend = await self._predict_trend(metric_id)
                if trend.get("prediction_method") == "arima":
                    predicted_values = trend.get("predicted_values", [])
                    if predicted_values and len(predicted_values) > 0:
                        # 如果预测值是上升趋势且目标更高，或下降趋势且目标更低，则健康
                        trend_direction = predicted_values[-1] - predicted_values[0]
                        if target_value and current_value:
                            target_gap = target_value - current_value
                            # 趋势方向与目标方向一致为健康
                            if (target_gap > 0 and trend_direction > 0) or (
                                target_gap < 0 and trend_direction < 0
                            ):
                                health_factors["trend"] = 0.8
                            else:
                                health_factors["trend"] = 0.3
                        else:
                            health_factors["trend"] = 0.5
                    else:
                        health_factors["trend"] = 0.5
                else:
                    health_factors["trend"] = 0.5
            except Exception:
                health_factors["trend"] = 0.5

            # 3. 数据完整性
            if history_data and len(history_data) >= 10:
                health_factors["data_completeness"] = min(1.0, len(history_data) / 30)
            else:
                health_factors["data_completeness"] = (
                    len(history_data) / 10 if history_data else 0
                )

            # 4. 稳定性（基于历史数据波动）
            if history_data and len(history_data) >= 5:
                values = [h["metric_value"] for h in history_data]
                if len(values) > 1:
                    std_dev = np.std(values)
                    mean_val = np.mean(values)
                    cv = std_dev / mean_val if mean_val != 0 else 0
                    # 变异系数越小越稳定
                    stability = max(0, 1 - min(cv, 1.0))
                    health_factors["stability"] = stability
                else:
                    health_factors["stability"] = 0.5
            else:
                health_factors["stability"] = 0.3

            # 5. AI权重（权重越高越重要，健康度可相应提高）
            ai_weight = metric.get("ai_weight") or 0.5
            health_factors["importance"] = ai_weight

            # 综合健康度评分（加权平均）
            weights = {
                "achievement": 0.35,
                "trend": 0.25,
                "data_completeness": 0.15,
                "stability": 0.15,
                "importance": 0.10,
            }

            health_score = sum(
                health_factors.get(factor, 0) * weight
                for factor, weight in weights.items()
            )

            # 确定健康状态
            if health_score >= 0.8:
                status = "excellent"
            elif health_score >= 0.6:
                status = "good"
            elif health_score >= 0.4:
                status = "fair"
            else:
                status = "poor"

            return {
                "health_score": float(health_score),
                "status": status,
                "factors": health_factors,
                "weights": weights,
                "recommendations": self._generate_health_recommendations(
                    health_factors, status
                ),
            }

        except Exception as e:
            logger.error(f"计算指标健康度评分失败: {e}")
            return {"health_score": 0.0, "status": "error", "error": str(e)}

    def _generate_health_recommendations(
        self, factors: Dict[str, float], status: str
    ) -> List[str]:
        """生成健康度改进建议"""
        recommendations = []

        if factors.get("achievement", 0) < 0.5:
            recommendations.append("指标达成度较低，建议制定明确的改进计划")

        if factors.get("trend", 0) < 0.4:
            recommendations.append("指标趋势不佳，建议分析原因并采取行动")

        if factors.get("data_completeness", 0) < 0.7:
            recommendations.append("历史数据不足，建议定期更新指标值以提升预测准确性")

        if factors.get("stability", 0) < 0.5:
            recommendations.append("指标波动较大，建议分析波动原因并稳定指标")

        if status == "poor":
            recommendations.append("指标整体健康度较低，建议全面审查指标定义和目标设定")
        elif status == "fair":
            recommendations.append("指标健康度有待提升，建议关注薄弱环节")

        return recommendations

    async def compare_metrics(self, metric_ids: List[str]) -> Dict[str, Any]:
        """对比多个指标"""
        try:
            if not self.db_service or len(metric_ids) < 2:
                return {"error": "需要至少2个指标进行对比"}

            metrics_info = []
            for metric_id in metric_ids:
                metric = await self.get_north_star_metric(metric_id)
                if metric:
                    health = await self.calculate_metric_health_score(metric_id)
                    metrics_info.append(
                        {
                            "metric_id": metric_id,
                            "metric_info": metric,
                            "health_score": health,
                        }
                    )

            if len(metrics_info) < 2:
                return {"error": "无法获取足够的指标信息进行对比"}

            # 对比分析
            comparison = {
                "metrics": metrics_info,
                "comparison_summary": {
                    "total_metrics": len(metrics_info),
                    "avg_health_score": float(
                        np.mean(
                            [m["health_score"]["health_score"] for m in metrics_info]
                        )
                    ),
                    "best_metric": max(
                        metrics_info, key=lambda x: x["health_score"]["health_score"]
                    ),
                    "worst_metric": min(
                        metrics_info, key=lambda x: x["health_score"]["health_score"]
                    ),
                },
                "insights": self._generate_comparison_insights(metrics_info),
            }

            return comparison

        except Exception as e:
            logger.error(f"指标对比失败: {e}")
            return {"error": str(e)}

    def _generate_comparison_insights(
        self, metrics_info: List[Dict[str, Any]]
    ) -> List[str]:
        """生成对比洞察"""
        insights = []

        if len(metrics_info) >= 2:
            health_scores = [m["health_score"]["health_score"] for m in metrics_info]
            score_range = max(health_scores) - min(health_scores)

            if score_range > 0.3:
                insights.append("指标间健康度差异较大，建议关注健康度较低的指标")
            else:
                insights.append("指标健康度较为均衡")

            # 分析趋势
            trend_statuses = [
                m["health_score"].get("factors", {}).get("trend", 0.5)
                for m in metrics_info
            ]
            positive_trends = sum(1 for t in trend_statuses if t > 0.6)
            if positive_trends == len(metrics_info):
                insights.append("所有指标趋势良好")
            elif positive_trends == 0:
                insights.append("所有指标趋势需要关注")
            else:
                insights.append(f"{positive_trends}/{len(metrics_info)}个指标趋势良好")

        return insights
