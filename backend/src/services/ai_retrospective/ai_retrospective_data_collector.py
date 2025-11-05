"""
AI复盘数据收集服务
自动收集复盘相关数据，包括决策执行结果、指标变化、异常事件和用户反馈
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from uuid import uuid4

from ...algorithms.threshold_analysis import ThresholdAnalysis
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIRetrospectiveDataCollector:
    """AI复盘数据收集服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        # 初始化AI算法
        self.threshold_analyzer = ThresholdAnalysis()

        logger.info("AI复盘数据收集服务初始化完成")

    async def collect_decision_outcomes(
        self, decision_id: str, session_id: str, outcome_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        收集决策执行结果

        Args:
            decision_id: 决策ID
            session_id: 复盘会话ID
            outcome_data: 执行结果数据

        Returns:
            收集结果
        """
        try:
            logger.info(
                f"开始收集决策执行结果: decision_id={decision_id}, session_id={session_id}"
            )

            # 1. 获取决策基线用于对比
            baseline = await self._get_decision_baseline(decision_id)

            # 2. 计算执行偏差
            deviation_analysis = self._calculate_deviation(outcome_data, baseline)

            # 3. 构建数据内容
            data_content = {
                "decision_id": decision_id,
                "outcome_data": outcome_data,
                "baseline_comparison": deviation_analysis,
                "collection_timestamp": datetime.now().isoformat(),
            }

            # 4. 评估数据质量
            quality_score = self._evaluate_data_quality(data_content)

            # 5. 保存到数据库
            data_id = await self._save_retrospective_data(
                session_id=session_id,
                data_type="decision_outcome",
                data_content=data_content,
                data_source="decision_execution",
                quality_score=quality_score,
            )

            # 6. 记录到企业记忆
            if self.memory_service:
                await self._record_to_memory(
                    memory_type="decision_outcome",
                    content=data_content,
                    tags=["retrospective", "decision", "outcome"],
                )

            return {
                "success": True,
                "data_id": data_id,
                "quality_score": quality_score,
                "deviation_analysis": deviation_analysis,
            }

        except Exception as e:
            logger.error(f"收集决策执行结果失败: {e}")
            return {"success": False, "error": str(e)}

    async def monitor_metric_changes(
        self,
        metric_id: str,
        session_id: str,
        time_range: Optional[Dict[str, datetime]] = None,
    ) -> Dict[str, Any]:
        """
        监控关键指标变化

        Args:
            metric_id: 指标ID
            session_id: 复盘会话ID
            time_range: 时间范围 (start, end)

        Returns:
            监控结果
        """
        try:
            logger.info(
                f"开始监控指标变化: metric_id={metric_id}, session_id={session_id}"
            )

            # 1. 获取指标历史数据
            if time_range is None:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)
            else:
                start_time = time_range.get(
                    "start", datetime.now() - timedelta(days=30)
                )
                end_time = time_range.get("end", datetime.now())

            historical_data = await self._get_metric_history(
                metric_id, start_time, end_time
            )

            if not historical_data or len(historical_data) < 2:
                return {"success": False, "error": "历史数据不足"}

            # 2. 转换为DataFrame进行分析
            df = pd.DataFrame(historical_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

            # 3. 计算变化趋势
            trend_analysis = self._analyze_metric_trend(df)

            # 4. 检测异常变化
            anomaly_detection = await self._detect_metric_anomalies(df)

            # 5. 构建数据内容
            data_content = {
                "metric_id": metric_id,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "trend_analysis": trend_analysis,
                "anomaly_detection": anomaly_detection,
                "data_points": len(df),
            }

            # 6. 评估数据质量
            quality_score = self._evaluate_data_quality(data_content)

            # 7. 保存到数据库
            data_id = await self._save_retrospective_data(
                session_id=session_id,
                data_type="metric_change",
                data_content=data_content,
                data_source="metric_monitoring",
                quality_score=quality_score,
                event_timestamp=end_time,
            )

            return {
                "success": True,
                "data_id": data_id,
                "quality_score": quality_score,
                "trend_analysis": trend_analysis,
                "anomalies_detected": len(anomaly_detection.get("anomalies", [])),
            }

        except Exception as e:
            logger.error(f"监控指标变化失败: {e}")
            return {"success": False, "error": str(e)}

    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        session_id: str,
        anomaly_type: str = "threshold",
    ) -> Dict[str, Any]:
        """
        异常事件智能识别

        Args:
            data: 待检测数据
            session_id: 复盘会话ID
            anomaly_type: 异常检测类型 ('threshold', 'statistical', 'pattern')

        Returns:
            异常检测结果
        """
        try:
            logger.info(
                f"开始异常检测: data_count={len(data)}, anomaly_type={anomaly_type}"
            )

            if not data or len(data) < 3:
                return {"success": False, "error": "数据量不足，无法进行异常检测"}

            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 根据类型选择检测方法
            if anomaly_type == "threshold":
                anomalies = await self._detect_threshold_anomalies(df)
            elif anomaly_type == "statistical":
                anomalies = await self._detect_statistical_anomalies(df)
            else:
                anomalies = await self._detect_pattern_anomalies(df)

            # 构建数据内容
            data_content = {
                "anomaly_type": anomaly_type,
                "anomalies": anomalies,
                "total_data_points": len(df),
                "anomaly_count": len(anomalies),
                "anomaly_rate": len(anomalies) / len(df) if len(df) > 0 else 0,
            }

            # 评估数据质量
            quality_score = self._evaluate_data_quality(data_content)

            # 保存到数据库
            data_id = await self._save_retrospective_data(
                session_id=session_id,
                data_type="anomaly",
                data_content=data_content,
                data_source="anomaly_detection",
                quality_score=quality_score,
            )

            return {
                "success": True,
                "data_id": data_id,
                "quality_score": quality_score,
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
                "anomaly_rate": data_content["anomaly_rate"],
            }

        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return {"success": False, "error": str(e)}

    async def collect_user_feedback(
        self, session_id: str, feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        收集用户反馈

        Args:
            session_id: 复盘会话ID
            feedback_data: 用户反馈数据

        Returns:
            收集结果
        """
        try:
            logger.info(f"开始收集用户反馈: session_id={session_id}")

            # 1. 验证反馈数据
            validated_feedback = self._validate_feedback(feedback_data)

            # 2. 分析反馈情感（如果有文本）
            if "text" in validated_feedback:
                sentiment_analysis = await self._analyze_feedback_sentiment(
                    validated_feedback["text"]
                )
                validated_feedback["sentiment"] = sentiment_analysis

            # 3. 构建数据内容
            data_content = {
                "feedback_data": validated_feedback,
                "collection_timestamp": datetime.now().isoformat(),
                "feedback_type": validated_feedback.get("type", "general"),
            }

            # 4. 评估数据质量
            quality_score = self._evaluate_data_quality(data_content)

            # 5. 保存到数据库
            data_id = await self._save_retrospective_data(
                session_id=session_id,
                data_type="user_feedback",
                data_content=data_content,
                data_source="user_input",
                quality_score=quality_score,
            )

            # 6. 记录到企业记忆
            if self.memory_service:
                await self._record_to_memory(
                    memory_type="user_feedback",
                    content=data_content,
                    tags=[
                        "retrospective",
                        "feedback",
                        validated_feedback.get("type", "general"),
                    ],
                )

            return {
                "success": True,
                "data_id": data_id,
                "quality_score": quality_score,
                "sentiment": validated_feedback.get("sentiment", {}),
            }

        except Exception as e:
            logger.error(f"收集用户反馈失败: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 辅助方法 ====================

    async def _get_decision_baseline(
        self, decision_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取决策基线"""
        try:
            if not self.db_service:
                return None

            query = """
                SELECT * FROM decision_baselines
                WHERE decision_id = $1
                ORDER BY created_at DESC
                LIMIT 1
            """
            result = await self.db_service.execute_query(query, [decision_id])
            return result[0] if result else None
        except Exception as e:
            logger.warning(f"获取决策基线失败: {e}")
            return None

    def _calculate_deviation(
        self, outcome_data: Dict[str, Any], baseline: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算执行偏差"""
        if not baseline:
            return {"has_baseline": False, "deviation_percentage": None}

        baseline_values = baseline.get("baseline_values", {})
        deviations = {}

        for key, actual_value in outcome_data.items():
            if key in baseline_values:
                baseline_value = baseline_values[key]
                if isinstance(actual_value, (int, float)) and isinstance(
                    baseline_value, (int, float)
                ):
                    if baseline_value != 0:
                        deviation = (
                            (actual_value - baseline_value) / baseline_value
                        ) * 100
                        deviations[key] = {
                            "actual": actual_value,
                            "baseline": baseline_value,
                            "deviation": deviation,
                            "deviation_percentage": round(deviation, 2),
                        }

        return {
            "has_baseline": True,
            "deviations": deviations,
            "overall_deviation": (
                np.mean([abs(d["deviation"]) for d in deviations.values()])
                if deviations
                else 0
            ),
        }

    async def _get_metric_history(
        self, metric_id: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """获取指标历史数据"""
        try:
            if not self.db_service:
                return []

            query = """
                SELECT metric_value, recorded_at as timestamp
                FROM north_star_metric_values
                WHERE metric_id = $1
                AND recorded_at BETWEEN $2 AND $3
                ORDER BY recorded_at ASC
            """
            result = await self.db_service.execute_query(
                query, [metric_id, start_time, end_time]
            )
            return result
        except Exception as e:
            logger.warning(f"获取指标历史数据失败: {e}")
            return []

    def _analyze_metric_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析指标趋势"""
        if len(df) < 2:
            return {"trend": "insufficient_data"}

        values = df["metric_value"].values

        # 计算简单趋势
        first_half = np.mean(values[: len(values) // 2])
        second_half = np.mean(values[len(values) // 2 :])

        trend_direction = "increasing" if second_half > first_half else "decreasing"
        trend_strength = (
            abs((second_half - first_half) / first_half) if first_half != 0 else 0
        )

        return {
            "trend": trend_direction,
            "trend_strength": round(trend_strength, 4),
            "current_value": float(values[-1]),
            "average_value": float(np.mean(values)),
            "volatility": float(np.std(values)),
        }

    async def _detect_metric_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检测指标异常"""
        try:
            if len(df) < 5:
                return {"anomalies": [], "method": "insufficient_data"}

            values = df["metric_value"].values

            # 使用统计方法检测异常阈值
            mean_val = np.mean(values)
            std_val = np.std(values)

            # 计算异常阈值
            upper_threshold = mean_val + 2 * std_val
            lower_threshold = mean_val - 2 * std_val

            anomalies = []
            for idx, value in enumerate(values):
                if value > upper_threshold or value < lower_threshold:
                    anomalies.append(
                        {
                            "index": int(idx),
                            "value": float(value),
                            "timestamp": (
                                df.iloc[idx]["timestamp"].isoformat()
                                if "timestamp" in df.columns
                                else None
                            ),
                            "type": "high" if value > upper_threshold else "low",
                        }
                    )

            return {
                "anomalies": anomalies,
                "method": "statistical_threshold",
                "upper_threshold": float(upper_threshold),
                "lower_threshold": float(lower_threshold),
            }
        except Exception as e:
            logger.warning(f"检测指标异常失败: {e}")
            return {"anomalies": [], "method": "error", "error": str(e)}

    async def _detect_threshold_anomalies(
        self, df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """使用阈值方法检测异常"""
        anomalies = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            values = df[col].values

            # 使用统计方法计算阈值
            upper = np.percentile(values, 95)
            lower = np.percentile(values, 5)

            for idx in df.index:
                value = df.loc[idx, col]
                if value > upper or value < lower:
                    anomalies.append(
                        {
                            "column": col,
                            "index": int(idx),
                            "value": float(value),
                            "threshold": {"upper": float(upper), "lower": float(lower)},
                        }
                    )

        return anomalies

    async def _detect_statistical_anomalies(
        self, df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """使用统计方法检测异常"""
        anomalies = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            values = df[col].values
            mean_val = np.mean(values)
            std_val = np.std(values)

            # Z-score方法
            z_scores = (
                np.abs((values - mean_val) / std_val)
                if std_val > 0
                else np.zeros_like(values)
            )

            for idx, z_score in enumerate(z_scores):
                if z_score > 2.5:  # 阈值
                    anomalies.append(
                        {
                            "column": col,
                            "index": int(idx),
                            "value": float(values[idx]),
                            "z_score": float(z_score),
                            "method": "z_score",
                        }
                    )

        return anomalies

    async def _detect_pattern_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """使用模式匹配方法检测异常"""
        # 简化的模式检测（实际可以更复杂）
        anomalies = await self._detect_statistical_anomalies(df)
        return anomalies

    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证反馈数据"""
        validated = feedback_data.copy()

        # 确保必要字段存在
        if "text" not in validated:
            validated["text"] = ""
        if "type" not in validated:
            validated["type"] = "general"
        if "rating" not in validated:
            validated["rating"] = None

        return validated

    async def _analyze_feedback_sentiment(self, text: str) -> Dict[str, Any]:
        """分析反馈情感（简化实现）"""
        # 简化实现，实际可以集成NLP模型
        positive_words = ["好", "优秀", "满意", "棒", "不错"]
        negative_words = ["差", "糟糕", "不满意", "问题", "失败"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.8, 0.5 + positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(0.2, 0.5 - negative_count * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_words": positive_count,
            "negative_words": negative_count,
        }

    def _evaluate_data_quality(self, data_content: Dict[str, Any]) -> float:
        """评估数据质量"""
        score = 1.0

        # 检查数据完整性
        if not data_content:
            return 0.0

        # 检查必要字段
        required_fields = []
        for field in required_fields:
            if field not in data_content:
                score -= 0.2

        # 检查数据格式
        try:
            json.dumps(data_content)  # 确保可以序列化
        except:
            score -= 0.3

        return max(0.0, min(1.0, score))

    async def _save_retrospective_data(
        self,
        session_id: str,
        data_type: str,
        data_content: Dict[str, Any],
        data_source: str,
        quality_score: float,
        event_timestamp: Optional[datetime] = None,
    ) -> str:
        """保存复盘数据到数据库"""
        try:
            if not self.db_service:
                return str(uuid4())

            data_id = str(uuid4())

            query = """
                INSERT INTO retrospective_data (
                    id, session_id, data_type, data_content, data_source,
                    data_quality_score, collected_at, event_timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """

            result = await self.db_service.execute_query(
                query,
                [
                    data_id,
                    session_id,
                    data_type,
                    json.dumps(data_content),
                    data_source,
                    quality_score,
                    datetime.now(),
                    event_timestamp or datetime.now(),
                ],
            )

            return data_id
        except Exception as e:
            logger.error(f"保存复盘数据失败: {e}")
            return str(uuid4())

    async def _record_to_memory(
        self, memory_type: str, content: Dict[str, Any], tags: List[str]
    ):
        """记录到企业记忆"""
        try:
            if self.memory_service:
                await self.memory_service.store_experience(
                    experience_type=memory_type, content=content, tags=tags
                )
        except Exception as e:
            logger.warning(f"记录到企业记忆失败: {e}")
