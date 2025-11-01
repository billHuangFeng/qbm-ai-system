"""
AI影响传播引擎 API
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...services.ai_influence import AIInfluencePropagator, AIInfluenceOptimizer
from ...services.database_service import DatabaseService
from ...services.enhanced_enterprise_memory import EnterpriseMemoryService
from ..dependencies import get_database_service, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-influence", tags=["AI影响传播引擎"])


class SourceDecision(BaseModel):
    id: Optional[str] = None
    goals: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None
    importance: Optional[float] = 1.0
    timeline: Optional[Dict[str, Any]] = None


class AnalyzePropagationRequest(BaseModel):
    source_decision: SourceDecision
    propagation_depth: int = Field(3, ge=1, le=10)
    time_horizon: int = Field(30, ge=1, le=365)


class ImpactRequest(BaseModel):
    decision_id: str
    target_metrics: List[str]
    time_range: Optional[Dict[str, str]] = None


class ConflictDetectRequest(BaseModel):
    decisions: List[Dict[str, Any]]


class OptimizePathsRequest(BaseModel):
    influence_report: Dict[str, Any]
    objective: str = "maximize_impact"
    constraints: Optional[Dict[str, Any]] = None


class AllocateResourcesRequest(BaseModel):
    decisions: List[Dict[str, Any]]
    total_budget: float


class MitigateConflictsRequest(BaseModel):
    conflicts: List[Dict[str, Any]]


async def get_propagator(
    db: DatabaseService = Depends(get_database_service),
    memory: EnterpriseMemoryService = Depends(get_memory_service),
) -> AIInfluencePropagator:
    return AIInfluencePropagator(db_service=db, memory_service=memory)


async def get_optimizer(
    db: DatabaseService = Depends(get_database_service),
    memory: EnterpriseMemoryService = Depends(get_memory_service),
) -> AIInfluenceOptimizer:
    return AIInfluenceOptimizer(db_service=db, memory_service=memory)


@router.post("/analyze-propagation")
async def analyze_propagation(req: AnalyzePropagationRequest, svc: AIInfluencePropagator = Depends(get_propagator)):
    try:
        result = await svc.analyze_influence_propagation(
            source_decision=req.source_decision.dict(),
            propagation_depth=req.propagation_depth,
            time_horizon=req.time_horizon,
        )
        return result
    except Exception as e:
        logger.error(f"影响传播分析失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/impact")
async def calculate_impact(req: ImpactRequest, svc: AIInfluencePropagator = Depends(get_propagator)):
    try:
        result = await svc.calculate_influence_impact(
            decision_id=req.decision_id,
            target_metrics=req.target_metrics,
            time_range=req.time_range,
        )
        return result
    except Exception as e:
        logger.error(f"影响冲击计算失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/detect-conflicts")
async def detect_conflicts(req: ConflictDetectRequest, svc: AIInfluencePropagator = Depends(get_propagator)):
    try:
        result = await svc.detect_influence_conflicts(decisions=req.decisions)
        return result
    except Exception as e:
        logger.error(f"影响冲突检测失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/optimize-paths")
async def optimize_paths(req: OptimizePathsRequest, optimizer: AIInfluenceOptimizer = Depends(get_optimizer)):
    try:
        result = await optimizer.optimize_influence_paths(
            influence_report=req.influence_report,
            objective=req.objective,
            constraints=req.constraints,
        )
        return result
    except Exception as e:
        logger.error(f"影响路径优化失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/allocate-resources")
async def allocate_resources(req: AllocateResourcesRequest, optimizer: AIInfluenceOptimizer = Depends(get_optimizer)):
    try:
        result = await optimizer.allocate_resources_for_max_impact(
            decisions=req.decisions,
            total_budget=req.total_budget,
        )
        return result
    except Exception as e:
        logger.error(f"资源分配失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mitigate-conflicts")
async def mitigate_conflicts(req: MitigateConflictsRequest, optimizer: AIInfluenceOptimizer = Depends(get_optimizer)):
    try:
        result = await optimizer.mitigate_conflicts(conflicts=req.conflicts)
        return result
    except Exception as e:
        logger.error(f"冲突缓解失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


