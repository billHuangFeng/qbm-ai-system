"""
AI影响优化器
基于影响传播分析进行路径优化、资源分配与冲突缓解
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np

from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIInfluenceOptimizer:
    """AI影响优化器"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ) -> None:
        self.db_service = db_service
        self.memory_service = memory_service
        logger.info("AI影响优化器初始化完成")

    async def optimize_influence_paths(
        self,
        influence_report: Dict[str, Any],
        objective: str = "maximize_impact",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """根据影响分析结果进行路径优化"""
        try:
            paths = influence_report.get("propagation_paths", [])
            strengths = influence_report.get("influence_strengths", {})
            budget = (constraints or {}).get("budget", None)

            scored = []
            for p in paths:
                score = p.get("total_influence", 0)
                for node_id in p.get("influence_chain", []):
                    score += strengths.get(node_id, 0) * 0.2
                scored.append((score, p))

            scored.sort(key=lambda x: x[0], reverse=True)
            selected = [p for _, p in scored[:10]]

            return {
                "success": True,
                "objective": objective,
                "selected_paths": selected,
                "total_score": float(sum(s for s, _ in scored[:10]))
            }
        except Exception as e:
            logger.error(f"影响路径优化失败: {e}")
            return {"success": False, "error": str(e)}

    async def allocate_resources_for_max_impact(
        self,
        decisions: List[Dict[str, Any]],
        total_budget: float,
    ) -> Dict[str, Any]:
        """面向最大影响的资源分配（比例启发式）"""
        try:
            weights = []
            for d in decisions:
                importance = float(d.get("importance", 1.0))
                connections = int(d.get("connection_count", 1))
                weight = max(0.1, importance * (1 + 0.1 * connections))
                weights.append(weight)
            weight_sum = sum(weights) or 1.0

            allocations = []
            for d, w in zip(decisions, weights):
                amount = total_budget * (w / weight_sum)
                allocations.append({
                    "decision_id": d.get("id"),
                    "allocated_budget": round(amount, 2)
                })

            return {"success": True, "allocations": allocations, "total_budget": total_budget}
        except Exception as e:
            logger.error(f"资源分配失败: {e}")
            return {"success": False, "error": str(e)}

    async def mitigate_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """基于冲突列表给出缓解建议"""
        try:
            suggestions: List[Dict[str, Any]] = []
            for c in conflicts:
                ctype = c.get("type")
                if ctype == "resource_conflict":
                    suggestions.append({
                        "action": "stagger_schedule",
                        "reason": "资源超配，建议错峰排期或增加产能",
                        "priority": "high"
                    })
                elif ctype == "timeline_conflict":
                    suggestions.append({
                        "action": "adjust_milestones",
                        "reason": "时间重叠，建议调整里程碑避免瓶颈",
                        "priority": "medium"
                    })
                elif ctype == "goal_conflict":
                    suggestions.append({
                        "action": "clarify_goal_priority",
                        "reason": "目标过度聚集，建议明确优先级与分工",
                        "priority": "high"
                    })
                else:
                    suggestions.append({
                        "action": "workshop_alignment",
                        "reason": "组织对齐研讨，降低不确定性",
                        "priority": "low"
                    })

            priority_order = {"high": 2, "medium": 1, "low": 0}
            uniq = { (s["action"], s["reason"]): s for s in suggestions }
            ordered = sorted(uniq.values(), key=lambda x: priority_order.get(x.get("priority", "medium"), 1), reverse=True)

            return {"success": True, "remediation_actions": ordered[:10]}
        except Exception as e:
            logger.error(f"冲突缓解建议失败: {e}")
            return {"success": False, "error": str(e)}


