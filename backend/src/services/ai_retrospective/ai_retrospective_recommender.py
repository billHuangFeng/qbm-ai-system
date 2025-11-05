"""
AI复盘建议生成服务
基于复盘结果生成改进建议、最佳实践推荐、流程优化建议和风险预警
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import pandas as pd
import numpy as np
from uuid import uuid4

from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIRetrospectiveRecommender:
    """AI复盘建议生成服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        logger.info("AI复盘建议生成服务初始化完成")

    async def generate_improvement_suggestions(
        self,
        analysis_results: Dict[str, Any],
        session_id: str,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        基于复盘结果生成改进建议

        Args:
            analysis_results: 复盘分析结果
            session_id: 复盘会话ID
            focus_areas: 重点关注领域

        Returns:
            改进建议列表
        """
        try:
            logger.info(f"开始生成改进建议: session_id={session_id}")

            suggestions = []

            # 1. 从根因分析生成建议
            if "root_causes" in analysis_results:
                root_cause_suggestions = await self._suggestions_from_root_causes(
                    analysis_results["root_causes"], session_id
                )
                suggestions.extend(root_cause_suggestions)

            # 2. 从失败模式生成建议
            if "failure_patterns" in analysis_results:
                failure_suggestions = await self._suggestions_from_failures(
                    analysis_results["failure_patterns"], session_id
                )
                suggestions.extend(failure_suggestions)

            # 3. 从成功因素生成建议
            if "success_factors" in analysis_results:
                success_suggestions = await self._suggestions_from_success(
                    analysis_results["success_factors"], session_id
                )
                suggestions.extend(success_suggestions)

            # 4. 从企业记忆获取建议
            memory_suggestions = await self._get_memory_based_suggestions(
                analysis_results, session_id
            )
            suggestions.extend(memory_suggestions)

            # 4.5 从专家知识获取建议（理论支撑）
            expert_knowledge_suggestions = await self._get_expert_knowledge_suggestions(
                analysis_results, session_id
            )
            suggestions.extend(expert_knowledge_suggestions)

            # 5. 评估和排序建议
            evaluated_suggestions = self._evaluate_and_rank_suggestions(
                suggestions, focus_areas
            )

            # 6. 保存建议到数据库
            recommendation_ids = []
            for suggestion in evaluated_suggestions[:10]:  # 保存前10个建议
                rec_id = await self._save_recommendation(
                    session_id=session_id,
                    recommendation_type=suggestion["type"],
                    recommendation_title=suggestion.get("title", ""),
                    recommendation_content=suggestion["content"],
                    priority=suggestion["priority"],
                    expected_impact=suggestion.get("expected_impact", "medium"),
                    implementation_difficulty=suggestion.get("difficulty", "medium"),
                )
                recommendation_ids.append(rec_id)

            return {
                "success": True,
                "recommendation_count": len(evaluated_suggestions),
                "recommendation_ids": recommendation_ids,
                "recommendations": evaluated_suggestions[:10],  # 返回前10个
            }

        except Exception as e:
            logger.error(f"生成改进建议失败: {e}")
            return {"success": False, "error": str(e)}

    async def recommend_best_practices(
        self, context: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """
        最佳实践智能推荐

        Args:
            context: 上下文信息
            session_id: 复盘会话ID

        Returns:
            最佳实践推荐列表
        """
        try:
            logger.info(f"开始推荐最佳实践: session_id={session_id}")

            practices = []

            # 1. 从企业记忆获取最佳实践
            if self.memory_service:
                memory_practices = await self._get_memory_practices(context)
                practices.extend(memory_practices)

            # 2. 从成功案例提取实践
            if "success_cases" in context:
                extracted_practices = await self._extract_practices_from_success(
                    context["success_cases"]
                )
                practices.extend(extracted_practices)

            # 3. 评估实践相关性
            relevant_practices = self._evaluate_practice_relevance(practices, context)

            # 4. 保存到数据库
            practice_ids = []
            for practice in relevant_practices[:5]:  # 保存前5个
                rec_id = await self._save_recommendation(
                    session_id=session_id,
                    recommendation_type="best_practice",
                    recommendation_title=practice.get("title", ""),
                    recommendation_content=practice["content"],
                    priority="high",
                    expected_impact=practice.get("impact", "high"),
                )
                practice_ids.append(rec_id)

            return {
                "success": True,
                "practice_count": len(relevant_practices),
                "practice_ids": practice_ids,
                "practices": relevant_practices[:5],
            }

        except Exception as e:
            logger.error(f"推荐最佳实践失败: {e}")
            return {"success": False, "error": str(e)}

    async def suggest_process_optimizations(
        self, current_process: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """
        流程优化建议生成

        Args:
            current_process: 当前流程描述
            session_id: 复盘会话ID

        Returns:
            流程优化建议
        """
        try:
            logger.info(f"开始生成流程优化建议: session_id={session_id}")

            optimizations = []

            # 1. 识别流程瓶颈
            bottlenecks = await self._identify_bottlenecks(current_process)

            # 2. 生成优化建议
            for bottleneck in bottlenecks:
                optimization = await self._generate_optimization_suggestion(
                    bottleneck, current_process
                )
                optimizations.append(optimization)

            # 3. 评估优化效果
            evaluated_optimizations = self._evaluate_optimization_impact(
                optimizations, current_process
            )

            # 4. 保存到数据库
            optimization_ids = []
            for opt in evaluated_optimizations[:5]:
                rec_id = await self._save_recommendation(
                    session_id=session_id,
                    recommendation_type="process_optimization",
                    recommendation_title=opt.get("title", ""),
                    recommendation_content=opt["content"],
                    priority=opt.get("priority", "medium"),
                    expected_impact=opt.get("impact", "medium"),
                    implementation_difficulty=opt.get("difficulty", "medium"),
                )
                optimization_ids.append(rec_id)

            return {
                "success": True,
                "optimization_count": len(evaluated_optimizations),
                "optimization_ids": optimization_ids,
                "optimizations": evaluated_optimizations[:5],
            }

        except Exception as e:
            logger.error(f"生成流程优化建议失败: {e}")
            return {"success": False, "error": str(e)}

    async def create_risk_alerts(
        self, risk_indicators: List[Dict[str, Any]], session_id: str
    ) -> Dict[str, Any]:
        """
        风险预警机制

        Args:
            risk_indicators: 风险指标列表
            session_id: 复盘会话ID

        Returns:
            风险预警列表
        """
        try:
            logger.info(
                f"开始创建风险预警: session_id={session_id}, risk_count={len(risk_indicators)}"
            )

            alerts = []

            # 1. 评估每个风险指标
            for indicator in risk_indicators:
                risk_level = self._assess_risk_level(indicator)

                if risk_level in ["high", "critical"]:
                    alert = {
                        "risk_indicator": indicator,
                        "risk_level": risk_level,
                        "alert_message": self._generate_alert_message(
                            indicator, risk_level
                        ),
                        "recommended_actions": await self._recommend_risk_actions(
                            indicator, risk_level
                        ),
                    }
                    alerts.append(alert)

            # 2. 按风险级别排序
            alerts.sort(
                key=lambda x: ["low", "medium", "high", "critical"].index(
                    x["risk_level"]
                ),
                reverse=True,
            )

            # 3. 保存到数据库
            alert_ids = []
            for alert in alerts:
                rec_id = await self._save_recommendation(
                    session_id=session_id,
                    recommendation_type="risk_alert",
                    recommendation_title=f"风险预警: {alert['risk_indicator'].get('name', '未知风险')}",
                    recommendation_content=alert["alert_message"],
                    priority=alert["risk_level"],
                    expected_impact=(
                        "high"
                        if alert["risk_level"] in ["high", "critical"]
                        else "medium"
                    ),
                )
                alert_ids.append(rec_id)

            return {
                "success": True,
                "alert_count": len(alerts),
                "alert_ids": alert_ids,
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"创建风险预警失败: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 辅助方法 ====================

    async def _suggestions_from_root_causes(
        self, root_causes: List[Dict[str, Any]], session_id: str
    ) -> List[Dict[str, Any]]:
        """从根因生成建议"""
        suggestions = []

        for cause in root_causes:
            cause_type = cause.get("type", "unknown")
            cause_desc = cause.get("cause", "")

            if cause_type == "structural":
                suggestions.append(
                    {
                        "type": "structural_improvement",
                        "title": f"结构性问题改进: {cause_desc}",
                        "content": f"识别到结构性问题：{cause_desc}。建议：1) 重新审视组织结构 2) 优化流程设计 3) 加强跨部门协作",
                        "priority": "high",
                        "expected_impact": "high",
                        "difficulty": "hard",
                    }
                )
            elif cause_type == "metric":
                suggestions.append(
                    {
                        "type": "metric_monitoring",
                        "title": f"指标监控加强: {cause_desc}",
                        "content": f"建议加强以下指标的监控：{cause.get('affected_metrics', [])}",
                        "priority": "medium",
                        "expected_impact": "medium",
                        "difficulty": "easy",
                    }
                )

        return suggestions

    async def _suggestions_from_failures(
        self, failure_patterns: List[Dict[str, Any]], session_id: str
    ) -> List[Dict[str, Any]]:
        """从失败模式生成建议"""
        suggestions = []

        for pattern in failure_patterns:
            if pattern.get("percentage", 0) > 0.3:  # 超过30%的失败率
                suggestions.append(
                    {
                        "type": "failure_prevention",
                        "title": f"预防失败模式: {pattern.get('pattern', '未知')}",
                        "content": f"检测到高频失败模式：{pattern.get('pattern')}，出现频率{pattern.get('percentage', 0)*100:.1f}%。建议：1) 建立预警机制 2) 制定预防措施 3) 加强过程监控",
                        "priority": "high",
                        "expected_impact": "high",
                        "difficulty": "medium",
                    }
                )

        return suggestions

    async def _suggestions_from_success(
        self, success_factors: List[Dict[str, Any]], session_id: str
    ) -> List[Dict[str, Any]]:
        """从成功因素生成建议"""
        suggestions = []

        for factor in success_factors:
            if factor.get("importance") == "high":
                suggestions.append(
                    {
                        "type": "success_replication",
                        "title": f"复制成功因素: {factor.get('factor', '未知')}",
                        "content": f"建议保持和强化成功因素：{factor.get('factor')}，当前值：{factor.get('value')}",
                        "priority": "medium",
                        "expected_impact": "high",
                        "difficulty": "easy",
                    }
                )

        return suggestions

    async def _get_memory_based_suggestions(
        self, analysis_results: Dict[str, Any], session_id: str
    ) -> List[Dict[str, Any]]:
        """从企业记忆获取建议"""
        suggestions = []

        try:
            if self.memory_service:
                # 从企业记忆查找相似情况和建议
                query = json.dumps(analysis_results)
                patterns = await self.memory_service.search_similar_patterns(
                    query, limit=5
                )

                for pattern in patterns:
                    pattern_dict = (
                        pattern.dict() if hasattr(pattern, "dict") else pattern
                    )
                    suggestions.append(
                        {
                            "type": "memory_based",
                            "title": f"历史经验建议",
                            "content": pattern_dict.get("description", ""),
                            "priority": "medium",
                            "confidence": pattern_dict.get("confidence", 0.5),
                        }
                    )
        except Exception as e:
            logger.warning(f"从企业记忆获取建议失败: {e}")

        return suggestions

    async def _get_expert_knowledge_suggestions(
        self, analysis_results: Dict[str, Any], session_id: str
    ) -> List[Dict[str, Any]]:
        """从专家知识获取建议（理论支撑）"""
        suggestions = []

        try:
            # 尝试获取专家知识服务
            from ...services.expert_knowledge import (
                KnowledgeIntegrationService,
                ExpertKnowledgeService,
                KnowledgeSearchService,
            )
            from ...services.database_service import DatabaseService
            from ...services.enterprise_memory_service import EnterpriseMemoryService

            # 构建搜索上下文
            context_description = ""
            if "root_causes" in analysis_results:
                root_causes = analysis_results["root_causes"]
                context_description += f"根因: {', '.join([rc.get('cause', '') for rc in root_causes[:3]])} "

            if "failure_patterns" in analysis_results:
                failure_patterns = analysis_results["failure_patterns"]
                context_description += f"失败模式: {', '.join([fp.get('pattern', '') for fp in failure_patterns[:2]])}"

            # 尝试获取知识集成服务（如果有）
            if self.db_service:
                try:
                    knowledge_service = ExpertKnowledgeService(
                        db_service=self.db_service
                    )
                    search_service = KnowledgeSearchService(db_service=self.db_service)

                    integration_service = KnowledgeIntegrationService(
                        knowledge_service=knowledge_service,
                        search_service=search_service,
                        memory_service=self.memory_service,
                    )

                    # 获取租户ID（如果有）
                    tenant_id = getattr(self, "_tenant_id", "default_tenant")

                    # 搜索专家知识
                    expert_knowledge = await integration_service.search_relevant_knowledge(
                        tenant_id=tenant_id,
                        context={
                            "domain_category": "risk_management",  # 复盘通常与风险管理相关
                            "problem_type": "retrospective_problem",
                            "description": context_description or "复盘改进建议",
                        },
                        limit=5,
                    )

                    # 转换为建议格式
                    for knowledge in expert_knowledge:
                        suggestions.append(
                            {
                                "type": "expert_knowledge",
                                "title": f"专家建议: {knowledge.get('title', '')}",
                                "content": f"{knowledge.get('summary', '')}。来源：{knowledge.get('source_reference', '专家知识库')}",
                                "priority": (
                                    "high"
                                    if knowledge.get("verification_status")
                                    == "verified"
                                    else "medium"
                                ),
                                "confidence": (
                                    0.8
                                    if knowledge.get("verification_status")
                                    == "verified"
                                    else 0.6
                                ),
                                "source": "expert_knowledge",
                                "expert_knowledge_id": knowledge.get("id"),
                                "expected_impact": "high",
                                "difficulty": "medium",
                            }
                        )

                except Exception as e:
                    logger.warning(f"从专家知识系统获取建议失败: {e}")
            else:
                logger.warning("数据库服务未初始化，无法获取专家知识建议")

        except ImportError:
            logger.warning("专家知识服务未导入，跳过专家知识建议")
        except Exception as e:
            logger.warning(f"获取专家知识建议失败: {e}")

        return suggestions

    def _evaluate_and_rank_suggestions(
        self, suggestions: List[Dict[str, Any]], focus_areas: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """评估和排序建议"""
        # 计算综合得分
        for suggestion in suggestions:
            priority_score = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
                suggestion.get("priority", "medium"), 2
            )
            impact_score = {"high": 3, "medium": 2, "low": 1}.get(
                suggestion.get("expected_impact", "medium"), 2
            )

            # 如果与关注领域相关，加分
            relevance_bonus = 1.0
            if focus_areas:
                for area in focus_areas:
                    if area.lower() in suggestion.get("content", "").lower():
                        relevance_bonus = 1.2
                        break

            suggestion["score"] = (
                priority_score * 0.4 + impact_score * 0.6
            ) * relevance_bonus

        # 按得分排序
        suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
        return suggestions

    async def _get_memory_practices(
        self, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """从企业记忆获取最佳实践"""
        practices = []

        try:
            if self.memory_service:
                # 查找成功模式
                patterns = await self.memory_service.get_patterns("success")

                for pattern in patterns[:5]:  # 取前5个
                    pattern_dict = (
                        pattern.dict() if hasattr(pattern, "dict") else pattern
                    )
                    practices.append(
                        {
                            "title": pattern_dict.get("description", ""),
                            "content": pattern_dict.get("description", ""),
                            "confidence": pattern_dict.get("confidence", 0.5),
                            "impact": "high",
                        }
                    )
        except Exception as e:
            logger.warning(f"获取记忆实践失败: {e}")

        return practices

    async def _extract_practices_from_success(
        self, success_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """从成功案例提取实践"""
        practices = []

        # 简化实现：提取共同的成功特征作为实践
        if success_cases:
            common_keys = set()
            for case in success_cases:
                common_keys.update(case.keys())

            for key in common_keys:
                if key not in ["id", "timestamp"]:
                    values = [case.get(key) for case in success_cases if key in case]
                    if len(set(values)) == 1:  # 所有案例都有相同值
                        practices.append(
                            {
                                "title": f"成功实践: {key}",
                                "content": f"在所有成功案例中都保持了{key}={values[0]}",
                                "confidence": 0.8,
                                "impact": "high",
                            }
                        )

        return practices

    def _evaluate_practice_relevance(
        self, practices: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """评估实践相关性"""
        for practice in practices:
            # 简化相关性评估
            relevance = 0.5

            # 如果实践内容与上下文相关，提高相关性
            context_str = json.dumps(context).lower()
            practice_str = practice.get("content", "").lower()

            if any(keyword in practice_str for keyword in context_str.split()[:5]):
                relevance = 0.8

            practice["relevance"] = relevance

        # 按相关性排序
        practices.sort(key=lambda x: x.get("relevance", 0.5), reverse=True)
        return practices

    async def _identify_bottlenecks(
        self, process: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别流程瓶颈"""
        bottlenecks = []

        # 简化实现：基于流程描述识别可能的瓶颈
        process_steps = process.get("steps", [])

        if len(process_steps) > 5:
            bottlenecks.append(
                {
                    "type": "complexity",
                    "description": "流程步骤过多，可能导致执行效率低",
                    "location": "整体流程",
                }
            )

        return bottlenecks

    async def _generate_optimization_suggestion(
        self, bottleneck: Dict[str, Any], current_process: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成优化建议"""
        return {
            "title": f"优化: {bottleneck.get('type', '未知')}",
            "content": f"针对{bottleneck.get('description', '')}，建议：1) 简化流程 2) 自动化处理 3) 并行化执行",
            "priority": "medium",
            "impact": "medium",
            "difficulty": "medium",
        }

    def _evaluate_optimization_impact(
        self, optimizations: List[Dict[str, Any]], current_process: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """评估优化效果"""
        # 简化实现：根据优先级和难度评估
        for opt in optimizations:
            priority = opt.get("priority", "medium")
            difficulty = opt.get("difficulty", "medium")

            # 高优先级、低难度 = 高影响
            if priority == "high" and difficulty == "easy":
                opt["impact"] = "high"
            elif priority == "high" and difficulty == "hard":
                opt["impact"] = "medium"
            else:
                opt["impact"] = "medium"

        return optimizations

    def _assess_risk_level(self, indicator: Dict[str, Any]) -> str:
        """评估风险级别"""
        risk_score = indicator.get("risk_score", 0.5)

        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_alert_message(
        self, indicator: Dict[str, Any], risk_level: str
    ) -> str:
        """生成预警消息"""
        indicator_name = indicator.get("name", "未知风险")
        return f"⚠️ {risk_level.upper()}风险预警: {indicator_name}。风险评分: {indicator.get('risk_score', 0):.2f}。建议立即采取行动。"

    async def _recommend_risk_actions(
        self, indicator: Dict[str, Any], risk_level: str
    ) -> List[str]:
        """推荐风险应对行动"""
        actions = []

        if risk_level in ["high", "critical"]:
            actions.append("立即召开风险评估会议")
            actions.append("制定应急响应计划")
            actions.append("加强监控和预警")

        return actions

    async def _save_recommendation(
        self,
        session_id: str,
        recommendation_type: str,
        recommendation_title: str,
        recommendation_content: str,
        priority: str,
        expected_impact: Optional[str] = None,
        implementation_difficulty: Optional[str] = None,
    ) -> str:
        """保存建议到数据库"""
        try:
            if not self.db_service:
                return str(uuid4())

            recommendation_id = str(uuid4())

            query = """
                INSERT INTO retrospective_recommendations (
                    id, session_id, recommendation_type, recommendation_title,
                    recommendation_content, priority, expected_impact,
                    implementation_difficulty, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """

            result = await self.db_service.execute_query(
                query,
                [
                    recommendation_id,
                    session_id,
                    recommendation_type,
                    recommendation_title,
                    recommendation_content,
                    priority,
                    expected_impact or "medium",
                    implementation_difficulty or "medium",
                    datetime.now(),
                ],
            )

            return recommendation_id
        except Exception as e:
            logger.error(f"保存建议失败: {e}")
            return str(uuid4())
