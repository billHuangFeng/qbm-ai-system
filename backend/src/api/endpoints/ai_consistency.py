"""
AI一致性引擎 API
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...services.ai_consistency import AIDecisionConsistencyChecker, AIStrategyConsistencyMaintainer
from ...services.database_service import DatabaseService
from ...services.enhanced_enterprise_memory import EnterpriseMemoryService
from ..dependencies import get_database_service, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-consistency", tags=["AI一致性引擎"])


class DecisionPayload(BaseModel):
    decision: Dict[str, Any] = Field(..., description="当前决策数据")
    related_decisions: Optional[List[Dict[str, Any]]] = Field(None, description="相关决策（可选）")
    policies: Optional[List[Dict[str, Any]]] = Field(None, description="策略规则（可选）")


async def get_consistency_checker(
    db: DatabaseService = Depends(get_database_service),
    memory: EnterpriseMemoryService = Depends(get_memory_service),
) -> AIDecisionConsistencyChecker:
    return AIDecisionConsistencyChecker(db_service=db, memory_service=memory)


async def get_strategy_maintainer(
    db: DatabaseService = Depends(get_database_service),
    memory: EnterpriseMemoryService = Depends(get_memory_service),
) -> AIStrategyConsistencyMaintainer:
    return AIStrategyConsistencyMaintainer(db_service=db, memory_service=memory)


@router.post("/check-policy")
async def check_policy(payload: DecisionPayload, svc: AIDecisionConsistencyChecker = Depends(get_consistency_checker)):
    try:
        result = await svc.check_policy_compliance(decision=payload.decision, policies=payload.policies)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"策略合规检查失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/detect-inconsistencies")
async def detect_inconsistencies(payload: DecisionPayload, svc: AIDecisionConsistencyChecker = Depends(get_consistency_checker)):
    try:
        result = await svc.detect_inconsistencies(decision=payload.decision, related_decisions=payload.related_decisions)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"不一致检测失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class RemediationPayload(BaseModel):
    decision: Dict[str, Any]
    findings: Dict[str, Any]


@router.post("/suggest-remediations")
async def suggest_remediations(payload: RemediationPayload, svc: AIDecisionConsistencyChecker = Depends(get_consistency_checker)):
    try:
        suggestions = await svc.suggest_remediations(decision=payload.decision, findings=payload.findings)
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"纠偏建议生成失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class StrategyMaintainPayload(BaseModel):
    strategic_objectives: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]


@router.post("/strategy/maintain")
async def strategy_maintain(payload: StrategyMaintainPayload, svc: AIStrategyConsistencyMaintainer = Depends(get_strategy_maintainer)):
    try:
        result = await svc.maintain_strategy_consistency(
            strategic_objectives=payload.strategic_objectives,
            decisions=payload.decisions,
        )
        return result
    except Exception as e:
        logger.error(f"策略一致性维护失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class StrategyDriftPayload(BaseModel):
    strategic_objectives: List[Dict[str, Any]]
    latest_metrics: List[Dict[str, Any]]


@router.post("/strategy/monitor-drift")
async def strategy_monitor_drift(payload: StrategyDriftPayload, svc: AIStrategyConsistencyMaintainer = Depends(get_strategy_maintainer)):
    try:
        result = await svc.monitor_drift(
            strategic_objectives=payload.strategic_objectives,
            latest_metrics=payload.latest_metrics,
        )
        return result
    except Exception as e:
        logger.error(f"策略漂移监测失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


