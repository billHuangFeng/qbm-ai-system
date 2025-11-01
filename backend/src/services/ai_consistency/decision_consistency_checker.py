"""
AI决策一致性检查服务
 - 策略合规性检查
 - 冲突/矛盾检测
 - 纠偏建议
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np

from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIDecisionConsistencyChecker:
    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ) -> None:
        self.db_service = db_service
        self.memory_service = memory_service
        logger.info("AIDecisionConsistencyChecker 初始化完成")

    async def check_policy_compliance(
        self,
        decision: Dict[str, Any],
        policies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """检查决策是否符合组织策略/约束"""
        try:
            if policies is None:
                policies = await self._load_active_policies()

            violations: List[Dict[str, Any]] = []
            for rule in policies:
                v = self._evaluate_rule(decision, rule)
                if v is not None:
                    violations.append(v)

            compliance_score = max(0.0, 1.0 - 0.2 * len(violations))
            return {
                "compliance_score": float(round(compliance_score, 3)),
                "violations": violations,
            }
        except Exception as e:
            logger.error(f"策略合规检查失败: {e}")
            return {"compliance_score": 0.0, "violations": [], "error": str(e)}

    async def detect_inconsistencies(
        self,
        decision: Dict[str, Any],
        related_decisions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """检测与历史或并行决策的不一致与冲突"""
        try:
            if related_decisions is None:
                related_decisions = await self._load_related_decisions(decision)

            conflicts: List[Dict[str, Any]] = []
            conflict_score = 0.0

            cur_resources = decision.get("resources", {})
            cur_goals = set(decision.get("goals", []))
            cur_timeline = decision.get("timeline", {})

            for rd in related_decisions:
                # 资源冲突
                for rtype, amount in cur_resources.items():
                    if amount and rd.get("resources", {}).get(rtype):
                        conflicts.append({
                            "type": "resource_conflict",
                            "resource": rtype,
                            "current": amount,
                            "related": rd["resources"][rtype],
                        })
                        conflict_score += 0.1

                # 目标方向矛盾
                rd_goals = set(rd.get("goals", []))
                if cur_goals and rd_goals and cur_goals.isdisjoint(rd_goals):
                    conflicts.append({
                        "type": "goal_divergence",
                        "current_goals": list(cur_goals),
                        "related_goals": list(rd_goals),
                    })
                    conflict_score += 0.2

                # 时序冲突
                if cur_timeline and rd.get("timeline"):
                    if self._overlap_timeline(cur_timeline, rd["timeline"]):
                        conflicts.append({
                            "type": "timeline_overlap",
                            "current_timeline": cur_timeline,
                            "related_timeline": rd["timeline"],
                        })
                        conflict_score += 0.1

            return {
                "conflict_probability": float(min(1.0, round(conflict_score, 3))),
                "conflicts": conflicts,
                "related_count": len(related_decisions or []),
            }
        except Exception as e:
            logger.error(f"不一致检测失败: {e}")
            return {"conflict_probability": 1.0, "conflicts": [], "error": str(e)}

    async def suggest_remediations(
        self,
        decision: Dict[str, Any],
        findings: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """基于检查结果生成纠偏建议"""
        suggestions: List[Dict[str, Any]] = []

        # 基于冲突类型的规则化建议
        for c in findings.get("conflicts", []):
            ctype = c.get("type")
            if ctype == "resource_conflict":
                suggestions.append({
                    "type": "reallocate_resources",
                    "title": "调整资源分配",
                    "content": f"资源 {c.get('resource')} 出现并发占用，建议协同排期或增补资源。",
                    "priority": "high",
                })
            elif ctype == "goal_divergence":
                suggestions.append({
                    "type": "align_goals",
                    "title": "目标对齐会议",
                    "content": "与相关团队组织快速对齐会，统一目标方向或拆分阶段性目标。",
                    "priority": "high",
                })
            elif ctype == "timeline_overlap":
                suggestions.append({
                    "type": "reschedule",
                    "title": "调整时序",
                    "content": "存在时间重叠，建议调整里程碑或采用并行可行的交付策略。",
                    "priority": "medium",
                })

        # 引用企业记忆中的协同策略
        if self.memory_service:
            try:
                query = f"决策一致性 纠偏建议 {decision.get('decision_name', '')}"
                patterns = await self.memory_service.search_similar_patterns(query, limit=3)
                for p in patterns:
                    p_dict = p.dict() if hasattr(p, "dict") else p
                    suggestions.append({
                        "type": "memory_based",
                        "title": "历史经验建议",
                        "content": p_dict.get("description", ""),
                        "priority": "medium",
                    })
            except Exception as e:
                logger.warning(f"获取企业记忆建议失败: {e}")

        # 去重并按优先级排序
        priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        dedup = { (s.get("type"), s.get("title"), s.get("content")): s for s in suggestions }
        ordered = sorted(dedup.values(), key=lambda s: priority_order.get(s.get("priority", "medium"), 1), reverse=True)
        return ordered[:10]

    # ----------------- 内部方法 -----------------

    async def _load_active_policies(self) -> List[Dict[str, Any]]:
        """从数据库加载当前生效的策略规则（简单JSON规则）"""
        if not self.db_service:
            return []
        try:
            query = """
                SELECT rule_id, rule_name, rule_definition
                FROM consistency_policies
                WHERE is_active = true
            """
            rows = await self.db_service.execute_query(query, [])
            policies: List[Dict[str, Any]] = []
            for r in rows or []:
                definition = r.get("rule_definition") or {}
                policies.append({
                    "id": r.get("rule_id"),
                    "name": r.get("rule_name"),
                    "definition": definition,
                })
            return policies
        except Exception as e:
            logger.warning(f"加载策略失败，使用空规则集: {e}")
            return []

    async def _load_related_decisions(self, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据上下文加载相关决策（同目标、同资源或同周期）"""
        if not self.db_service:
            return []
        try:
            goal = (decision.get("goals") or [None])[0]
            query = """
                SELECT id, name as decision_name, goals, resources, timeline
                FROM decisions
                WHERE $1 = ANY(goals)
                ORDER BY created_at DESC
                LIMIT 20
            """
            rows = await self.db_service.execute_query(query, [goal])
            return rows or []
        except Exception as e:
            logger.warning(f"加载相关决策失败: {e}")
            return []

    def _evaluate_rule(self, decision: Dict[str, Any], rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """简单规则引擎：基于JSON定义校验一两个条件"""
        try:
            definition = rule.get("definition") or rule.get("definition") or rule.get("rule") or {}
            constraints = definition.get("constraints", [])
            for c in constraints:
                field = c.get("field")
                op = c.get("op")
                value = c.get("value")
                cur = decision
                for part in (field or '').split('.'):
                    if part:
                        cur = (cur or {}).get(part)
                if op == "max" and isinstance(cur, (int, float)) and cur > value:
                    return {"rule": rule.get("name"), "field": field, "type": "max_violation", "current": cur, "limit": value}
                if op == "min" and isinstance(cur, (int, float)) and cur < value:
                    return {"rule": rule.get("name"), "field": field, "type": "min_violation", "current": cur, "limit": value}
                if op == "required" and (cur is None or cur == ""):
                    return {"rule": rule.get("name"), "field": field, "type": "required_missing"}
        except Exception as e:
            logger.debug(f"规则评估异常: {e}")
        return None

    def _overlap_timeline(self, tl1: Dict[str, Any], tl2: Dict[str, Any]) -> bool:
        try:
            s1 = pd.to_datetime(tl1.get("start"))
            e1 = pd.to_datetime(tl1.get("end"))
            s2 = pd.to_datetime(tl2.get("start"))
            e2 = pd.to_datetime(tl2.get("end"))
            return max(s1, s2) <= min(e1, e2)
        except Exception:
            return False


