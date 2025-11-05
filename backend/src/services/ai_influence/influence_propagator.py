"""
AI影响传播分析器
分析决策影响传播路径、计算影响强度、预测连锁反应
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from uuid import uuid4

from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIInfluencePropagator:
    """AI影响传播分析器"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        logger.info("AI影响传播分析器初始化完成")

    async def analyze_influence_propagation(
        self,
        source_decision: Dict[str, Any],
        propagation_depth: int = 3,
        time_horizon: int = 30,
    ) -> Dict[str, Any]:
        """
        分析决策影响传播路径

        Args:
            source_decision: 源决策数据
            propagation_depth: 传播深度
            time_horizon: 时间范围（天）

        Returns:
            影响传播分析结果
        """
        try:
            logger.info(f"开始影响传播分析: decision_id={source_decision.get('id')}")

            # 1. 构建影响网络图
            influence_network = await self._build_influence_network(source_decision)

            # 2. 计算影响强度
            influence_strengths = self._calculate_influence_strengths(
                influence_network, source_decision
            )

            # 3. 预测传播路径
            propagation_paths = await self._predict_propagation_paths(
                influence_network, propagation_depth
            )

            # 4. 分析连锁反应
            cascade_effects = await self._analyze_cascade_effects(
                propagation_paths, time_horizon
            )

            # 5. 识别关键节点
            critical_nodes = self._identify_critical_nodes(
                influence_network, influence_strengths
            )

            # 6. 生成影响报告
            influence_report = {
                "source_decision": source_decision,
                "influence_network": influence_network,
                "influence_strengths": influence_strengths,
                "propagation_paths": propagation_paths,
                "cascade_effects": cascade_effects,
                "critical_nodes": critical_nodes,
                "analysis_timestamp": datetime.now().isoformat(),
            }

            # 7. 保存分析结果
            analysis_id = await self._save_influence_analysis(influence_report)

            return {
                "success": True,
                "analysis_id": analysis_id,
                "influence_network_size": len(influence_network),
                "propagation_paths_count": len(propagation_paths),
                "critical_nodes_count": len(critical_nodes),
                "max_influence_strength": (
                    max(influence_strengths.values()) if influence_strengths else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"影响传播分析失败: {e}")
            return {"success": False, "error": str(e)}

    async def calculate_influence_impact(
        self,
        decision_id: str,
        target_metrics: List[str],
        time_range: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        计算决策对目标指标的影响

        Args:
            decision_id: 决策ID
            target_metrics: 目标指标列表
            time_range: 时间范围

        Returns:
            影响计算结果
        """
        try:
            logger.info(f"开始计算影响冲击: decision_id={decision_id}")

            # 1. 获取历史数据
            historical_data = await self._get_historical_metrics(
                target_metrics, time_range
            )

            # 2. 计算影响系数
            impact_coefficients = self._calculate_impact_coefficients(
                historical_data, decision_id
            )

            # 3. 预测未来影响
            future_impacts = await self._predict_future_impacts(
                impact_coefficients, target_metrics
            )

            # 4. 评估影响风险
            risk_assessment = self._assess_impact_risks(future_impacts)

            return {
                "success": True,
                "decision_id": decision_id,
                "impact_coefficients": impact_coefficients,
                "future_impacts": future_impacts,
                "risk_assessment": risk_assessment,
            }

        except Exception as e:
            logger.error(f"影响冲击计算失败: {e}")
            return {"success": False, "error": str(e)}

    async def detect_influence_conflicts(
        self, decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        检测决策间的影响冲突

        Args:
            decisions: 决策列表

        Returns:
            冲突检测结果
        """
        try:
            logger.info(f"开始检测影响冲突: decisions_count={len(decisions)}")

            conflicts = []

            # 1. 检测资源冲突
            resource_conflicts = self._detect_resource_conflicts(decisions)
            conflicts.extend(resource_conflicts)

            # 2. 检测目标冲突
            goal_conflicts = self._detect_goal_conflicts(decisions)
            conflicts.extend(goal_conflicts)

            # 3. 检测时序冲突
            timeline_conflicts = self._detect_timeline_conflicts(decisions)
            conflicts.extend(timeline_conflicts)

            # 4. 检测影响链冲突
            influence_conflicts = await self._detect_influence_chain_conflicts(
                decisions
            )
            conflicts.extend(influence_conflicts)

            # 5. 评估冲突严重性
            conflict_severity = self._assess_conflict_severity(conflicts)

            return {
                "success": True,
                "conflicts": conflicts,
                "conflict_count": len(conflicts),
                "severity_distribution": conflict_severity,
            }

        except Exception as e:
            logger.error(f"影响冲突检测失败: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 辅助方法 ====================

    async def _build_influence_network(
        self, source_decision: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """构建影响网络图"""
        network = []

        # 简化实现：基于决策属性构建网络
        source_id = source_decision.get("id", "unknown")

        # 添加源节点
        network.append(
            {
                "node_id": source_id,
                "node_type": "decision",
                "influence_weight": 1.0,
                "connections": [],
            }
        )

        # 查找相关决策
        if self.db_service:
            try:
                query = """
                    SELECT id, name, goals, resources, timeline
                    FROM decisions
                    WHERE id != $1
                    ORDER BY created_at DESC
                    LIMIT 20
                """
                related_decisions = await self.db_service.execute_query(
                    query, [source_id]
                )

                for decision in related_decisions:
                    # 计算关联度
                    similarity = self._calculate_decision_similarity(
                        source_decision, decision
                    )

                    if similarity > 0.3:  # 相似度阈值
                        network.append(
                            {
                                "node_id": decision["id"],
                                "node_type": "decision",
                                "influence_weight": similarity,
                                "connections": [source_id],
                            }
                        )

                        # 更新源节点的连接
                        network[0]["connections"].append(decision["id"])

            except Exception as e:
                logger.warning(f"构建影响网络失败: {e}")

        return network

    def _calculate_decision_similarity(
        self, decision1: Dict[str, Any], decision2: Dict[str, Any]
    ) -> float:
        """计算决策相似度"""
        try:
            # 目标相似度
            goals1 = set(decision1.get("goals", []))
            goals2 = set(decision2.get("goals", []))
            goal_similarity = len(goals1 & goals2) / max(len(goals1 | goals2), 1)

            # 资源相似度
            resources1 = set(decision1.get("resources", {}).keys())
            resources2 = set(decision2.get("resources", {}).keys())
            resource_similarity = len(resources1 & resources2) / max(
                len(resources1 | resources2), 1
            )

            # 综合相似度
            similarity = goal_similarity * 0.6 + resource_similarity * 0.4
            return round(similarity, 3)

        except Exception:
            return 0.0

    def _calculate_influence_strengths(
        self, influence_network: List[Dict[str, Any]], source_decision: Dict[str, Any]
    ) -> Dict[str, float]:
        """计算影响强度"""
        strengths = {}

        for node in influence_network:
            node_id = node["node_id"]
            base_weight = node["influence_weight"]

            # 基于连接数调整强度
            connection_count = len(node.get("connections", []))
            connection_factor = 1.0 + (connection_count * 0.1)

            # 基于决策重要性调整
            importance = source_decision.get("importance", 1.0)
            importance_factor = 1.0 + (importance * 0.2)

            final_strength = base_weight * connection_factor * importance_factor
            strengths[node_id] = round(min(final_strength, 1.0), 3)

        return strengths

    async def _predict_propagation_paths(
        self, influence_network: List[Dict[str, Any]], max_depth: int
    ) -> List[Dict[str, Any]]:
        """预测传播路径"""
        paths = []

        # 简化实现：基于网络结构生成路径
        for node in influence_network:
            if node["node_type"] == "decision":
                path = {
                    "path_id": str(uuid4()),
                    "source_node": node["node_id"],
                    "path_length": 1,
                    "influence_chain": [node["node_id"]],
                    "total_influence": node["influence_weight"],
                }
                paths.append(path)

        return paths[: max_depth * 5]  # 限制路径数量

    async def _analyze_cascade_effects(
        self, propagation_paths: List[Dict[str, Any]], time_horizon: int
    ) -> List[Dict[str, Any]]:
        """分析连锁反应"""
        cascade_effects = []

        for path in propagation_paths:
            # 计算级联强度
            cascade_strength = path["total_influence"] * 0.8  # 衰减因子

            # 预测影响时间
            estimated_delay = min(time_horizon, 7)  # 简化：假设7天内生效

            effect = {
                "cascade_id": str(uuid4()),
                "path_id": path["path_id"],
                "cascade_strength": round(cascade_strength, 3),
                "estimated_delay_days": estimated_delay,
                "risk_level": (
                    "high"
                    if cascade_strength > 0.7
                    else "medium" if cascade_strength > 0.4 else "low"
                ),
            }
            cascade_effects.append(effect)

        return cascade_effects

    def _identify_critical_nodes(
        self,
        influence_network: List[Dict[str, Any]],
        influence_strengths: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """识别关键节点"""
        critical_nodes = []

        for node in influence_network:
            node_id = node["node_id"]
            strength = influence_strengths.get(node_id, 0.0)
            connection_count = len(node.get("connections", []))

            # 关键节点标准：高影响强度 + 多连接
            if strength > 0.6 and connection_count > 2:
                critical_nodes.append(
                    {
                        "node_id": node_id,
                        "node_type": node["node_type"],
                        "influence_strength": strength,
                        "connection_count": connection_count,
                        "criticality_score": round(strength * connection_count, 3),
                    }
                )

        # 按关键性排序
        critical_nodes.sort(key=lambda x: x["criticality_score"], reverse=True)
        return critical_nodes[:10]  # 返回前10个关键节点

    async def _get_historical_metrics(
        self, target_metrics: List[str], time_range: Optional[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """获取历史指标数据"""
        if not self.db_service:
            return []

        try:
            query = """
                SELECT metric_name, metric_value, recorded_at
                FROM metrics
                WHERE metric_name = ANY($1)
            """
            params = [target_metrics]

            if time_range:
                query += " AND recorded_at BETWEEN $2 AND $3"
                params.extend([time_range["start"], time_range["end"]])

            query += " ORDER BY recorded_at DESC"

            return await self.db_service.execute_query(query, params)

        except Exception as e:
            logger.warning(f"获取历史指标失败: {e}")
            return []

    def _calculate_impact_coefficients(
        self, historical_data: List[Dict[str, Any]], decision_id: str
    ) -> Dict[str, float]:
        """计算影响系数"""
        coefficients = {}

        # 按指标分组
        metric_data = {}
        for record in historical_data:
            metric_name = record.get("metric_name")
            if metric_name not in metric_data:
                metric_data[metric_name] = []
            metric_data[metric_name].append(record.get("metric_value", 0))

        # 计算每个指标的影响系数
        for metric_name, values in metric_data.items():
            if len(values) > 1:
                # 简化：使用标准差作为影响系数
                coefficient = np.std(values) / max(np.mean(values), 1e-6)
                coefficients[metric_name] = round(coefficient, 3)
            else:
                coefficients[metric_name] = 0.1  # 默认值

        return coefficients

    async def _predict_future_impacts(
        self, impact_coefficients: Dict[str, float], target_metrics: List[str]
    ) -> Dict[str, Any]:
        """预测未来影响"""
        future_impacts = {}

        for metric in target_metrics:
            coefficient = impact_coefficients.get(metric, 0.1)

            # 简化预测：基于系数预测影响
            predicted_impact = coefficient * 0.8  # 衰减因子

            future_impacts[metric] = {
                "predicted_change": round(predicted_impact, 3),
                "confidence": round(min(coefficient * 2, 1.0), 3),
                "time_to_impact": "7-14 days",  # 简化
            }

        return future_impacts

    def _assess_impact_risks(self, future_impacts: Dict[str, Any]) -> Dict[str, Any]:
        """评估影响风险"""
        high_risk_metrics = []
        medium_risk_metrics = []

        for metric, impact in future_impacts.items():
            change = abs(impact.get("predicted_change", 0))
            confidence = impact.get("confidence", 0)

            risk_score = change * confidence

            if risk_score > 0.6:
                high_risk_metrics.append(metric)
            elif risk_score > 0.3:
                medium_risk_metrics.append(metric)

        return {
            "high_risk_count": len(high_risk_metrics),
            "medium_risk_count": len(medium_risk_metrics),
            "high_risk_metrics": high_risk_metrics,
            "medium_risk_metrics": medium_risk_metrics,
            "overall_risk_level": (
                "high"
                if high_risk_metrics
                else "medium" if medium_risk_metrics else "low"
            ),
        }

    def _detect_resource_conflicts(
        self, decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测资源冲突"""
        conflicts = []

        # 统计资源使用情况
        resource_usage = {}
        for decision in decisions:
            resources = decision.get("resources", {})
            for resource_type, amount in resources.items():
                if resource_type not in resource_usage:
                    resource_usage[resource_type] = []
                resource_usage[resource_type].append(
                    {"decision_id": decision.get("id"), "amount": amount}
                )

        # 检测冲突
        for resource_type, usages in resource_usage.items():
            if len(usages) > 1:
                total_demand = sum(u["amount"] for u in usages)
                # 假设资源容量有限
                capacity = total_demand * 1.2  # 20%缓冲

                if total_demand > capacity:
                    conflicts.append(
                        {
                            "type": "resource_conflict",
                            "resource_type": resource_type,
                            "total_demand": total_demand,
                            "available_capacity": capacity,
                            "conflicting_decisions": [u["decision_id"] for u in usages],
                        }
                    )

        return conflicts

    def _detect_goal_conflicts(
        self, decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测目标冲突"""
        conflicts = []

        # 收集所有目标
        all_goals = {}
        for decision in decisions:
            goals = decision.get("goals", [])
            for goal in goals:
                if goal not in all_goals:
                    all_goals[goal] = []
                all_goals[goal].append(decision.get("id"))

        # 检测目标冲突（简化：目标数量过多）
        for goal, decision_ids in all_goals.items():
            if len(decision_ids) > 3:  # 超过3个决策关注同一目标
                conflicts.append(
                    {
                        "type": "goal_conflict",
                        "goal": goal,
                        "conflicting_decisions": decision_ids,
                        "conflict_reason": "too_many_decisions_focusing_on_same_goal",
                    }
                )

        return conflicts

    def _detect_timeline_conflicts(
        self, decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测时序冲突"""
        conflicts = []

        # 检查时间重叠
        for i, decision1 in enumerate(decisions):
            timeline1 = decision1.get("timeline", {})
            if not timeline1.get("start") or not timeline1.get("end"):
                continue

            for j, decision2 in enumerate(decisions[i + 1 :], i + 1):
                timeline2 = decision2.get("timeline", {})
                if not timeline2.get("start") or not timeline2.get("end"):
                    continue

                # 检查时间重叠
                if self._timelines_overlap(timeline1, timeline2):
                    conflicts.append(
                        {
                            "type": "timeline_conflict",
                            "decision1_id": decision1.get("id"),
                            "decision2_id": decision2.get("id"),
                            "overlap_period": {
                                "start": max(timeline1["start"], timeline2["start"]),
                                "end": min(timeline1["end"], timeline2["end"]),
                            },
                        }
                    )

        return conflicts

    def _timelines_overlap(
        self, timeline1: Dict[str, Any], timeline2: Dict[str, Any]
    ) -> bool:
        """检查时间线是否重叠"""
        try:
            start1 = pd.to_datetime(timeline1["start"])
            end1 = pd.to_datetime(timeline1["end"])
            start2 = pd.to_datetime(timeline2["start"])
            end2 = pd.to_datetime(timeline2["end"])

            return max(start1, start2) <= min(end1, end2)
        except Exception:
            return False

    async def _detect_influence_chain_conflicts(
        self, decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检测影响链冲突"""
        conflicts = []

        # 简化实现：检测循环依赖
        for i, decision1 in enumerate(decisions):
            for j, decision2 in enumerate(decisions[i + 1 :], i + 1):
                # 检查是否存在相互影响
                if self._has_mutual_influence(decision1, decision2):
                    conflicts.append(
                        {
                            "type": "influence_chain_conflict",
                            "decision1_id": decision1.get("id"),
                            "decision2_id": decision2.get("id"),
                            "conflict_reason": "mutual_influence_detected",
                        }
                    )

        return conflicts

    def _has_mutual_influence(
        self, decision1: Dict[str, Any], decision2: Dict[str, Any]
    ) -> bool:
        """检查是否存在相互影响"""
        # 简化实现：基于目标重叠判断
        goals1 = set(decision1.get("goals", []))
        goals2 = set(decision2.get("goals", []))

        return len(goals1 & goals2) > 0

    def _assess_conflict_severity(
        self, conflicts: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """评估冲突严重性分布"""
        severity_count = {"high": 0, "medium": 0, "low": 0}

        for conflict in conflicts:
            conflict_type = conflict.get("type", "")

            if conflict_type in ["resource_conflict", "influence_chain_conflict"]:
                severity_count["high"] += 1
            elif conflict_type in ["goal_conflict", "timeline_conflict"]:
                severity_count["medium"] += 1
            else:
                severity_count["low"] += 1

        return severity_count

    async def _save_influence_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """保存影响分析结果"""
        try:
            if not self.db_service:
                return str(uuid4())

            analysis_id = str(uuid4())

            query = """
                INSERT INTO influence_analyses (
                    id, analysis_data, created_at
                ) VALUES ($1, $2, $3)
                RETURNING id
            """

            await self.db_service.execute_query(
                query, [analysis_id, json.dumps(analysis_data), datetime.now()]
            )

            return analysis_id

        except Exception as e:
            logger.error(f"保存影响分析失败: {e}")
            return str(uuid4())
