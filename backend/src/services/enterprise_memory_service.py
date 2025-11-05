"""
BMOS系统 - 企业记忆服务
作用: 提取、存储、检索和应用企业记忆
状态: ✅ 实施中
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class EnterpriseMemoryService:
    """企业记忆服务"""

    def __init__(self, db_service=None, cache_service=None):
        self.db_service = db_service
        self.cache_service = cache_service
        self.memory_types = [
            "pattern",  # 模式
            "strategy",  # 策略
            "lesson_learned",  # 经验教训
            "optimization_rule",  # 优化规则
            "anomaly_pattern",  # 异常模式
            "threshold",  # 阈值
            "synergy_effect",  # 协同效应
        ]
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.memory_embeddings = {}

    def extract_memory_from_feedback(
        self,
        evaluation_data: Dict[str, Any],
        historical_evaluations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        从管理者评价中提取企业记忆

        Args:
            evaluation_data: 当前评价数据
            historical_evaluations: 历史评价数据

        Returns:
            提取的记忆列表
        """
        try:
            memories = []

            # 1. 提取指标调整模式
            if "metricAdjustments" in evaluation_data:
                patterns = self._extract_adjustment_patterns(
                    evaluation_data["metricAdjustments"], historical_evaluations
                )
                memories.extend(patterns)

            # 2. 提取评价原因模式
            if "evaluationContent" in evaluation_data:
                lessons = self._extract_lessons_learned(
                    evaluation_data["evaluationContent"], historical_evaluations
                )
                memories.extend(lessons)

            # 3. 提取实施计划模式
            if "implementationPlan" in evaluation_data:
                strategies = self._extract_strategies(
                    evaluation_data["implementationPlan"], historical_evaluations
                )
                memories.extend(strategies)

            return {
                "success": True,
                "memories": memories,
                "memory_count": len(memories),
            }

        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            return {"success": False, "error": str(e), "memories": []}

    def _extract_adjustment_patterns(
        self,
        metric_adjustments: List[Dict[str, Any]],
        historical_evaluations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """提取指标调整模式"""
        patterns = []

        # 统计常见的调整原因
        adjustment_reasons = []
        for adjustment in metric_adjustments:
            adjustment_reasons.append(adjustment.get("adjustmentReason", ""))

        if adjustment_reasons:
            most_common_reason = Counter(adjustment_reasons).most_common(1)[0]

            patterns.append(
                {
                    "memory_type": "pattern",
                    "memory_title": f"指标调整模式: {most_common_reason[0]}",
                    "memory_content": {
                        "pattern_type": "metric_adjustment",
                        "common_reason": most_common_reason[0],
                        "frequency": most_common_reason[1],
                        "adjustments": metric_adjustments,
                    },
                    "confidence_score": min(
                        most_common_reason[1] / 3.0, 1.0
                    ),  # 3次以上为高置信度
                    "source_type": "manager_feedback",
                }
            )

        return patterns

    def _extract_lessons_learned(
        self, evaluation_content: str, historical_evaluations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """提取经验教训"""
        lessons = []

        # 关键词提取(简化版,实际应该使用NLP)
        key_phrases = self._extract_key_phrases(evaluation_content)

        # 检查历史评价中是否有类似的教训
        similar_lessons = []
        for hist_eval in historical_evaluations:
            hist_content = hist_eval.get("evaluationContent", "")
            if self._are_similar(key_phrases, hist_content):
                similar_lessons.append(hist_eval)

        if similar_lessons:
            lessons.append(
                {
                    "memory_type": "lesson_learned",
                    "memory_title": f"经验教训: {key_phrases[0]}",
                    "memory_content": {
                        "lesson": evaluation_content,
                        "key_phrases": key_phrases,
                        "frequency": len(similar_lessons) + 1,
                    },
                    "confidence_score": min((len(similar_lessons) + 1) / 5.0, 1.0),
                    "source_type": "manager_feedback",
                }
            )

        return lessons

    def _extract_strategies(
        self,
        implementation_plan: Dict[str, Any],
        historical_evaluations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """提取实施策略"""
        strategies = []

        # 提取实施计划的关键信息
        duration = implementation_plan.get("duration", 0)
        responsible = implementation_plan.get("responsiblePerson", "")

        # 查找相似的历史策略
        similar_strategies = []
        for hist_eval in historical_evaluations:
            hist_plan = hist_eval.get("implementationPlan", {})
            if hist_plan and abs(hist_plan.get("duration", 0) - duration) < 10:
                similar_strategies.append(hist_eval)

        if similar_strategies:
            strategies.append(
                {
                    "memory_type": "strategy",
                    "memory_title": f"实施策略: {duration}天周期项目",
                    "memory_content": {
                        "implementation_plan": implementation_plan,
                        "typical_duration": duration,
                        "frequency": len(similar_strategies) + 1,
                    },
                    "confidence_score": min((len(similar_strategies) + 1) / 3.0, 1.0),
                    "source_type": "manager_feedback",
                }
            )

        return strategies

    def extract_memory_from_prediction_error(
        self, error_data: Dict[str, Any], historical_errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """从预测误差中提取记忆"""
        memories = []

        # 分析误差类型
        relative_error = error_data.get("relative_error", 0)
        error_causes = error_data.get("error_causes", [])

        # 提取异常模式
        if relative_error > 0.5:  # 50%以上误差为严重错误
            memories.append(
                {
                    "memory_type": "anomaly_pattern",
                    "memory_title": f"严重预测误差模式",
                    "memory_content": {
                        "error_severity": "high",
                        "error_causes": error_causes,
                        "typical_causes": self._extract_common_causes(
                            error_causes, historical_errors
                        ),
                    },
                    "confidence_score": 0.8,  # 严重错误记忆置信度高
                    "source_type": "prediction_error",
                }
            )

        return memories

    def retrieve_relevant_memories(
        self,
        current_context: Dict[str, Any],
        existing_memories: List[Dict[str, Any]],
        min_confidence: float = 0.7,
        min_relevance: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """
        检索相关的企业记忆

        Args:
            current_context: 当前业务上下文
            existing_memories: 现有记忆列表
            min_confidence: 最小置信度
            min_relevance: 最小相关性

        Returns:
            相关记忆列表
        """
        relevant_memories = []

        for memory in existing_memories:
            # 1. 检查置信度
            if memory.get("confidence_score", 0) < min_confidence:
                continue

            # 2. 计算相关性
            relevance = self._calculate_relevance(memory, current_context)

            if relevance >= min_relevance:
                relevant_memories.append({**memory, "relevance_score": relevance})

        # 按相关性和置信度排序
        relevant_memories.sort(
            key=lambda m: (m.get("relevance_score", 0) + m.get("confidence_score", 0))
            / 2,
            reverse=True,
        )

        return relevant_memories

    def apply_memory_to_prediction(
        self, base_prediction: Dict[str, Any], memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        将企业记忆应用到预测结果

        Args:
            base_prediction: 基础预测结果
            memories: 相关记忆列表

        Returns:
            调整后的预测结果
        """
        adjusted_prediction = base_prediction.copy()

        for memory in memories:
            memory_type = memory.get("memory_type")
            memory_content = memory.get("memory_content", {})

            if memory_type == "pattern":
                # 应用模式调整
                adjusted_prediction = self._apply_pattern_adjustment(
                    adjusted_prediction, memory_content
                )
            elif memory_type == "strategy":
                # 应用策略调整
                adjusted_prediction = self._apply_strategy_adjustment(
                    adjusted_prediction, memory_content
                )
            elif memory_type == "threshold":
                # 应用阈值调整
                adjusted_prediction = self._apply_threshold_adjustment(
                    adjusted_prediction, memory_content
                )

        return adjusted_prediction

    def track_memory_effectiveness(
        self, memory_id: str, application_result: Dict[str, Any], supabase_client: Any
    ) -> Dict[str, Any]:
        """
        追踪记忆应用效果

        Args:
            memory_id: 记忆ID
            application_result: 应用结果
            supabase_client: Supabase客户端

        Returns:
            追踪结果
        """
        try:
            # 保存应用历史
            application_history = {
                "memory_id": memory_id,
                "application_context": application_result.get("context_id"),
                "application_type": application_result.get("type"),
                "was_successful": application_result.get("success", False),
                "impact_score": application_result.get("impact", 0),
                "actual_result": application_result.get("actual"),
                "expected_result": application_result.get("expected"),
            }

            supabase_client.table("memory_application_history").insert(
                application_history
            ).execute()

            # 更新记忆统计
            self._update_memory_statistics(
                memory_id, application_result, supabase_client
            )

            return {"success": True, "memory_id": memory_id}

        except Exception as e:
            logger.error(f"Memory tracking failed: {e}")
            return {"success": False, "error": str(e)}

    def _update_memory_statistics(
        self, memory_id: str, application_result: Dict[str, Any], supabase_client: Any
    ):
        """更新记忆统计数据"""
        # 获取当前统计
        result = (
            supabase_client.table("enterprise_memory")
            .select("*")
            .eq("id", memory_id)
            .execute()
        )
        memory = result.data[0] if result.data else None

        if not memory:
            return

        # 更新统计
        new_applied_count = memory.get("applied_count", 0) + 1
        new_successful_count = memory.get("successful_application_count", 0)

        if application_result.get("success"):
            new_successful_count += 1

        new_success_rate = (
            new_successful_count / new_applied_count if new_applied_count > 0 else 0
        )

        # 更新数据库
        supabase_client.table("enterprise_memory").update(
            {
                "applied_count": new_applied_count,
                "successful_application_count": new_successful_count,
                "success_rate": new_success_rate,
                "last_applied_at": datetime.now().isoformat(),
            }
        ).eq("id", memory_id).execute()

    # 辅助方法
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键词(简化版)"""
        # 实际应该使用NLP库
        words = text.split()
        return [w for w in words if len(w) > 4][:5]  # 返回前5个长词

    def _are_similar(self, phrases: List[str], text: str) -> bool:
        """判断文本是否相似"""
        return any(phrase in text for phrase in phrases)

    def _extract_common_causes(
        self,
        current_causes: List[Dict[str, Any]],
        historical_errors: List[Dict[str, Any]],
    ) -> List[str]:
        """提取常见误差原因"""
        all_causes = []
        for error in historical_errors:
            all_causes.extend(error.get("error_causes", []))

        common_causes = Counter([c.get("reason") for c in all_causes])
        return [reason for reason, count in common_causes.most_common(3)]

    def _calculate_relevance(
        self, memory: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """计算记忆相关性"""
        # 简化版相关性计算
        relevance = 0.5  # 默认值

        memory_content = memory.get("memory_content", {})

        # 检查业务场景匹配
        if memory_content.get("business_scenario") == context.get("scenario"):
            relevance += 0.2

        # 检查部门匹配
        if memory_content.get("department") == context.get("department"):
            relevance += 0.2

        return min(relevance, 1.0)

    def _apply_pattern_adjustment(
        self, prediction: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用模式调整"""
        # 根据模式调整预测值
        adjustment_factor = pattern.get("adjustment_factor", 1.0)
        prediction["value"] *= adjustment_factor
        return prediction

    def _apply_strategy_adjustment(
        self, prediction: Dict[str, Any], strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用策略调整"""
        # 根据策略调整预测
        return prediction

    def _apply_threshold_adjustment(
        self, prediction: Dict[str, Any], threshold: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用阈值调整"""
        threshold_value = threshold.get("value")
        if prediction["value"] > threshold_value:
            prediction["risk_level"] = "high"
        return prediction

    # 新增核心方法
    def extract_memory_from_prediction_error(
        self, error_data: Dict[str, Any], historical_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        从预测误差中提取企业记忆

        Args:
            error_data: 当前误差数据
            historical_errors: 历史误差数据

        Returns:
            提取的记忆列表
        """
        try:
            memories = []

            # 1. 分析误差模式
            error_patterns = self._analyze_error_patterns(error_data, historical_errors)
            memories.extend(error_patterns)

            # 2. 提取异常模式
            anomaly_patterns = self._extract_anomaly_patterns(
                error_data, historical_errors
            )
            memories.extend(anomaly_patterns)

            # 3. 提取优化规则
            optimization_rules = self._extract_optimization_rules(
                error_data, historical_errors
            )
            memories.extend(optimization_rules)

            return {
                "success": True,
                "memories": memories,
                "memory_count": len(memories),
            }

        except Exception as e:
            logger.error(f"Error memory extraction failed: {e}")
            return {"success": False, "error": str(e), "memories": []}

    def retrieve_relevant_memories(
        self,
        current_context: Dict[str, Any],
        existing_memories: List[Dict[str, Any]],
        min_confidence: float = 0.7,
        min_relevance: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """
        检索相关的企业记忆

        Args:
            current_context: 当前业务上下文
            existing_memories: 现有记忆列表
            min_confidence: 最小置信度
            min_relevance: 最小相关性

        Returns:
            相关记忆列表
        """
        try:
            relevant_memories = []

            # 构建文本向量用于相似度计算
            memory_texts = []
            for memory in existing_memories:
                text = f"{memory.get('memory_title', '')} {memory.get('memory_description', '')}"
                memory_texts.append(text)

            if not memory_texts:
                return []

            # 计算文本相似度
            try:
                tfidf_matrix = self.vectorizer.fit_transform(memory_texts)
                context_text = f"{current_context.get('scenario', '')} {current_context.get('department', '')}"
                context_vector = self.vectorizer.transform([context_text])

                similarities = cosine_similarity(context_vector, tfidf_matrix)[0]
            except:
                similarities = [0.5] * len(existing_memories)  # 默认相似度

            for i, memory in enumerate(existing_memories):
                # 1. 检查置信度
                if memory.get("confidence_score", 0) < min_confidence:
                    continue

                # 2. 计算综合相关性
                text_similarity = similarities[i] if i < len(similarities) else 0.5
                context_relevance = self._calculate_context_relevance(
                    memory, current_context
                )
                combined_relevance = (text_similarity + context_relevance) / 2

                if combined_relevance >= min_relevance:
                    relevant_memories.append(
                        {
                            **memory,
                            "relevance_score": combined_relevance,
                            "text_similarity": text_similarity,
                            "context_relevance": context_relevance,
                        }
                    )

            # 按综合评分排序
            relevant_memories.sort(
                key=lambda m: (
                    m.get("relevance_score", 0) + m.get("confidence_score", 0)
                )
                / 2,
                reverse=True,
            )

            return relevant_memories

        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []

    def apply_memory_to_prediction(
        self, base_prediction: Dict[str, Any], memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        将企业记忆应用到预测结果

        Args:
            base_prediction: 基础预测结果
            memories: 相关记忆列表

        Returns:
            调整后的预测结果
        """
        try:
            adjusted_prediction = base_prediction.copy()
            applied_memories = []

            for memory in memories:
                memory_type = memory.get("memory_type")
                memory_content = memory.get("memory_content", {})
                confidence = memory.get("confidence_score", 0)

                # 只应用高置信度的记忆
                if confidence < 0.7:
                    continue

                adjustment_applied = False

                if memory_type == "pattern":
                    adjusted_prediction, applied = self._apply_pattern_adjustment(
                        adjusted_prediction, memory_content, confidence
                    )
                    adjustment_applied = applied

                elif memory_type == "strategy":
                    adjusted_prediction, applied = self._apply_strategy_adjustment(
                        adjusted_prediction, memory_content, confidence
                    )
                    adjustment_applied = applied

                elif memory_type == "threshold":
                    adjusted_prediction, applied = self._apply_threshold_adjustment(
                        adjusted_prediction, memory_content, confidence
                    )
                    adjustment_applied = applied

                elif memory_type == "optimization_rule":
                    adjusted_prediction, applied = self._apply_optimization_rule(
                        adjusted_prediction, memory_content, confidence
                    )
                    adjustment_applied = applied

                if adjustment_applied:
                    applied_memories.append(
                        {
                            "memory_id": memory.get("id"),
                            "memory_type": memory_type,
                            "adjustment_factor": memory_content.get(
                                "adjustment_factor", 1.0
                            ),
                            "confidence": confidence,
                        }
                    )

            # 添加调整记录
            adjusted_prediction["applied_memories"] = applied_memories
            adjusted_prediction["memory_adjustment_count"] = len(applied_memories)

            return adjusted_prediction

        except Exception as e:
            logger.error(f"Memory application failed: {e}")
            return base_prediction

    def track_memory_effectiveness(
        self, memory_id: str, application_result: Dict[str, Any], supabase_client: Any
    ) -> Dict[str, Any]:
        """
        追踪记忆应用效果

        Args:
            memory_id: 记忆ID
            application_result: 应用结果
            supabase_client: Supabase客户端

        Returns:
            追踪结果
        """
        try:
            # 保存应用历史
            application_history = {
                "memory_id": memory_id,
                "application_context": application_result.get("context_id"),
                "application_type": application_result.get(
                    "type", "prediction_adjustment"
                ),
                "was_successful": application_result.get("success", False),
                "impact_score": application_result.get("impact", 0),
                "actual_result": application_result.get("actual"),
                "expected_result": application_result.get("expected"),
                "applied_at": datetime.now().isoformat(),
            }

            supabase_client.table("memory_application_history").insert(
                application_history
            ).execute()

            # 更新记忆统计
            self._update_memory_statistics(
                memory_id, application_result, supabase_client
            )

            return {
                "success": True,
                "memory_id": memory_id,
                "tracking_result": application_history,
            }

        except Exception as e:
            logger.error(f"Memory tracking failed: {e}")
            return {"success": False, "error": str(e)}

    # 新增辅助方法
    def _analyze_error_patterns(
        self, error_data: Dict[str, Any], historical_errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析误差模式"""
        patterns = []

        error_type = error_data.get("error_type", "unknown")
        error_magnitude = error_data.get("relative_error", 0)

        # 统计相似误差
        similar_errors = [
            err
            for err in historical_errors
            if abs(err.get("relative_error", 0) - error_magnitude) < 0.1
        ]

        if len(similar_errors) >= 2:  # 至少3次相似误差才形成模式
            patterns.append(
                {
                    "memory_type": "pattern",
                    "memory_title": f"误差模式: {error_type}",
                    "memory_content": {
                        "error_type": error_type,
                        "typical_magnitude": error_magnitude,
                        "frequency": len(similar_errors) + 1,
                        "common_causes": self._extract_common_error_causes(
                            similar_errors
                        ),
                    },
                    "confidence_score": min((len(similar_errors) + 1) / 5.0, 1.0),
                    "source_type": "prediction_error",
                }
            )

        return patterns

    def _extract_anomaly_patterns(
        self, error_data: Dict[str, Any], historical_errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """提取异常模式"""
        patterns = []

        relative_error = error_data.get("relative_error", 0)

        # 严重异常模式
        if relative_error > 0.5:  # 50%以上误差
            patterns.append(
                {
                    "memory_type": "anomaly_pattern",
                    "memory_title": "严重预测异常模式",
                    "memory_content": {
                        "severity_level": "high",
                        "error_threshold": 0.5,
                        "typical_causes": self._extract_common_error_causes(
                            historical_errors
                        ),
                        "prevention_strategies": self._generate_prevention_strategies(
                            error_data
                        ),
                    },
                    "confidence_score": 0.9,  # 严重异常置信度高
                    "source_type": "prediction_error",
                }
            )

        return patterns

    def _extract_optimization_rules(
        self, error_data: Dict[str, Any], historical_errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """提取优化规则"""
        rules = []

        # 基于历史误差生成优化规则
        if len(historical_errors) >= 3:
            avg_error = np.mean(
                [err.get("relative_error", 0) for err in historical_errors]
            )

            if avg_error > 0.2:  # 平均误差超过20%
                rules.append(
                    {
                        "memory_type": "optimization_rule",
                        "memory_title": "预测模型优化规则",
                        "memory_content": {
                            "rule_type": "model_adjustment",
                            "adjustment_factor": 1 - avg_error,  # 根据平均误差调整
                            "trigger_condition": "high_average_error",
                            "optimization_strategy": "reduce_prediction_by_average_error",
                        },
                        "confidence_score": min(avg_error, 0.8),
                        "source_type": "prediction_error",
                    }
                )

        return rules

    def _calculate_context_relevance(
        self, memory: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """计算上下文相关性"""
        relevance = 0.5  # 基础相关性

        memory_content = memory.get("memory_content", {})

        # 业务场景匹配
        if memory_content.get("business_scenario") == context.get("scenario"):
            relevance += 0.3

        # 部门匹配
        if memory_content.get("department") == context.get("department"):
            relevance += 0.2

        # 时间匹配
        if memory_content.get("time_period") == context.get("time_period"):
            relevance += 0.1

        return min(relevance, 1.0)

    def _apply_pattern_adjustment(
        self, prediction: Dict[str, Any], pattern: Dict[str, Any], confidence: float
    ) -> Tuple[Dict[str, Any], bool]:
        """应用模式调整"""
        try:
            adjustment_factor = pattern.get("adjustment_factor", 1.0)
            # 根据置信度调整调整因子
            adjusted_factor = 1 + (adjustment_factor - 1) * confidence

            prediction["value"] *= adjusted_factor
            prediction["adjustment_applied"] = True
            prediction["adjustment_factor"] = adjusted_factor

            return prediction, True
        except:
            return prediction, False

    def _apply_strategy_adjustment(
        self, prediction: Dict[str, Any], strategy: Dict[str, Any], confidence: float
    ) -> Tuple[Dict[str, Any], bool]:
        """应用策略调整"""
        try:
            strategy_type = strategy.get("strategy_type", "conservative")

            if strategy_type == "conservative":
                prediction["value"] *= 0.9  # 保守策略
            elif strategy_type == "aggressive":
                prediction["value"] *= 1.1  # 激进策略

            prediction["strategy_applied"] = strategy_type
            return prediction, True
        except:
            return prediction, False

    def _apply_optimization_rule(
        self, prediction: Dict[str, Any], rule: Dict[str, Any], confidence: float
    ) -> Tuple[Dict[str, Any], bool]:
        """应用优化规则"""
        try:
            rule_type = rule.get("rule_type", "model_adjustment")
            adjustment_factor = rule.get("adjustment_factor", 1.0)

            if rule_type == "model_adjustment":
                prediction["value"] *= adjustment_factor
                prediction["optimization_applied"] = True

            return prediction, True
        except:
            return prediction, False

    def _extract_common_error_causes(self, errors: List[Dict[str, Any]]) -> List[str]:
        """提取常见误差原因"""
        causes = []
        for error in errors:
            causes.extend(error.get("error_causes", []))

        common_causes = Counter(causes)
        return [cause for cause, count in common_causes.most_common(3)]

    def _generate_prevention_strategies(self, error_data: Dict[str, Any]) -> List[str]:
        """生成预防策略"""
        strategies = ["增加数据验证", "调整模型参数", "增加特征工程", "使用集成模型"]
        return strategies[:2]  # 返回前2个策略
