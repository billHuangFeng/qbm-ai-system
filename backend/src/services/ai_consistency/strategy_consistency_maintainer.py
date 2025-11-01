"""
AI策略一致性维护服务
 - 监测战略目标与执行决策的一致性
 - 识别战略漂移并给出校正建议
 - 维护权重、阈值与里程碑对齐
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import numpy as np
import pandas as pd

from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIStrategyConsistencyMaintainer:
    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ) -> None:
        self.db_service = db_service
        self.memory_service = memory_service
        logger.info("AIStrategyConsistencyMaintainer 初始化完成")

    async def maintain_strategy_consistency(
        self,
        strategic_objectives: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """综合评估战略一致性并返回校正建议"""
        try:
            alignment = self._evaluate_alignment(strategic_objectives, decisions)
            drift = self._detect_strategy_drift(strategic_objectives, decisions)
            suggestions = await self._generate_alignment_actions(alignment, drift)

            summary = {
                "overall_alignment": round(alignment.get("score", 0.7), 3),
                "drift_detected": drift.get("has_drift", False),
                "key_mismatches": alignment.get("mismatches", [])[:10],
                "suggestions": suggestions[:10],
            }

            return {"success": True, **summary}
        except Exception as e:
            logger.error(f"策略一致性维护失败: {e}")
            return {"success": False, "error": str(e)}

    async def monitor_drift(
        self,
        strategic_objectives: List[Dict[str, Any]],
        latest_metrics: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """监测战略漂移(指标背离、优先级漂移、节奏漂移)"""
        try:
            drift = self._simple_drift_check(strategic_objectives, latest_metrics)
            return {"success": True, **drift}
        except Exception as e:
            logger.error(f"漂移监测失败: {e}")
            return {"success": False, "error": str(e)}

    async def update_weights(
        self,
        objective_weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """更新战略权重（简单持久化示例）"""
        try:
            if not self.db_service:
                return {"success": True, "updated": len(objective_weights)}
            # 这里预留权重落库的示意接口（具体表结构可后续细化）
            return {"success": True, "updated": len(objective_weights)}
        except Exception as e:
            logger.error(f"更新权重失败: {e}")
            return {"success": False, "error": str(e)}

    # ---------------- 内部方法 ----------------

    def _evaluate_alignment(self, objectives: List[Dict[str, Any]], decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """粗粒度对齐评估：目标覆盖度、优先级一致性、里程碑匹配度"""
        try:
            obj_goals = set()
            for o in objectives:
                obj_goals.update(o.get("goals", []))

            covered = 0
            mismatches: List[Dict[str, Any]] = []

            for d in decisions:
                dgoals = set(d.get("goals", []))
                if dgoals & obj_goals:
                    covered += 1
                else:
                    mismatches.append({
                        "decision": d.get("decision_name", d.get("id")),
                        "issue": "no_objective_coverage",
                    })

            coverage_ratio = covered / max(1, len(decisions))
            score = 0.6 + 0.4 * coverage_ratio
            return {"score": float(score), "mismatches": mismatches}
        except Exception:
            return {"score": 0.7, "mismatches": []}

    def _detect_strategy_drift(self, objectives: List[Dict[str, Any]], decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于目标与执行之间的差距粗测漂移"""
        try:
            planned = sum(o.get("planned_value", 1) for o in objectives)
            executed = sum(d.get("expected_value", 1) for d in decisions)
            ratio = executed / max(1e-6, planned)
            has_drift = ratio < 0.8 or ratio > 1.2
            return {"has_drift": has_drift, "executed_to_planned": round(ratio, 3)}
        except Exception:
            return {"has_drift": False, "executed_to_planned": 1.0}

    def _simple_drift_check(self, objectives: List[Dict[str, Any]], metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于关键指标的简单漂移检测"""
        metric_map = {m.get("name"): m for m in metrics}
        drift_items: List[Dict[str, Any]] = []
        for o in objectives:
            key = o.get("key_metric")
            target = o.get("target")
            if key and key in metric_map and isinstance(target, (int, float)):
                val = metric_map[key].get("value")
                if isinstance(val, (int, float)) and (val < 0.8 * target or val > 1.2 * target):
                    drift_items.append({
                        "objective": o.get("name", "unknown"),
                        "metric": key,
                        "target": target,
                        "current": val,
                    })
        return {"has_drift": len(drift_items) > 0, "items": drift_items}

    async def _generate_alignment_actions(self, alignment: Dict[str, Any], drift: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        for m in alignment.get("mismatches", []):
            actions.append({
                "type": "objective_mapping",
                "title": "为决策补充目标映射",
                "content": f"决策 {m.get('decision')} 尚未覆盖任何战略目标，建议补齐目标映射。",
                "priority": "high",
            })

        for item in drift.get("items", []):
            actions.append({
                "type": "metric_correction",
                "title": "关键指标纠偏",
                "content": f"目标 {item.get('objective')} 的关键指标 {item.get('metric')} 偏离目标，建议制定纠偏计划。",
                "priority": "high",
            })

        # 引用企业记忆补充行动
        if self.memory_service:
            try:
                patterns = await self.memory_service.get_patterns("trend")
                for p in patterns[:3]:
                    pdict = p.dict() if hasattr(p, "dict") else p
                    actions.append({
                        "type": "memory_reference",
                        "title": "参考历史趋势建议",
                        "content": pdict.get("description", ""),
                        "priority": "medium",
                    })
            except Exception as e:
                logger.debug(f"加载企业记忆失败（可忽略）: {e}")

        # 去重+排序
        priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
        uniq = { (a.get("type"), a.get("title"), a.get("content")): a for a in actions }
        ordered = sorted(uniq.values(), key=lambda a: priority_order.get(a.get("priority", "medium"), 1), reverse=True)
        return ordered


