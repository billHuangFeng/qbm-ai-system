"""
AI增强制定闭环API端点
提供决策对齐检查、基线生成、需求深度分析等API接口
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

from ...services.ai_planning_loop.ai_alignment_checker import AIAlignmentChecker
from ...services.ai_planning_loop.ai_baseline_generator import AIBaselineGenerator
from ...services.ai_planning_loop.ai_requirement_analyzer import AIRequirementAnalyzer
from ...services.database_service import DatabaseService
from ...services.enhanced_enterprise_memory import EnterpriseMemoryService
from ..dependencies import get_database_service, get_memory_service, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-planning", tags=["AI制定闭环"])

# ==================== 依赖注入 ====================

def get_alignment_checker(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIAlignmentChecker:
    """获取对齐检查服务实例"""
    return AIAlignmentChecker(db_service, memory_service)

def get_baseline_generator(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIBaselineGenerator:
    """获取基线生成服务实例"""
    return AIBaselineGenerator(db_service, memory_service)

def get_requirement_analyzer(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIRequirementAnalyzer:
    """获取需求分析服务实例"""
    return AIRequirementAnalyzer(db_service, memory_service)

# ==================== 请求/响应模型 ====================

class AlignmentCheckRequest(BaseModel):
    """对齐检查请求"""
    decision_id: str = Field(..., description="决策ID")
    check_type: str = Field("full_alignment", description="检查类型: full_alignment, resource_conflict, goal_consistency, circular_dependency")
    related_decision_ids: Optional[List[str]] = Field(None, description="相关决策ID列表")

class BaselineGenerationRequest(BaseModel):
    """基线生成请求"""
    decision_id: str = Field(..., description="决策ID")
    baseline_name: str = Field(..., description="基线名称")
    include_predictions: bool = Field(True, description="是否包含AI预测")
    prediction_periods: int = Field(4, description="预测周期数")

class RequirementAnalysisRequest(BaseModel):
    """需求分析请求"""
    requirement_id: str = Field(..., description="需求ID")
    analysis_type: str = Field("full", description="分析类型: full, similarity, threshold, optimization")

class AlignmentCheckResponse(BaseModel):
    """对齐检查响应"""
    success: bool
    check_id: str
    decision_id: str
    alignment_status: str
    alignment_score: float
    check_results: Dict[str, Any]
    alignment_suggestions: List[Dict[str, Any]]

class BaselineGenerationResponse(BaseModel):
    """基线生成响应"""
    success: bool
    baseline_id: str
    baseline_code: str
    baseline_name: str
    ai_predictions: Optional[Dict[str, Any]]
    ai_confidence: float

class RequirementAnalysisResponse(BaseModel):
    """需求分析响应"""
    success: bool
    requirement_id: str
    analysis_results: Dict[str, Any]

# ==================== API端点 ====================

@router.post("/check-alignment", response_model=AlignmentCheckResponse)
async def check_decision_alignment(
    request: AlignmentCheckRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIAlignmentChecker = Depends(get_alignment_checker)
):
    """检查决策对齐"""
    try:
        result = await service.check_decision_alignment(
            decision_id=request.decision_id,
            check_type=request.check_type,
            related_decision_ids=request.related_decision_ids
        )
        
        return result
        
    except Exception as e:
        logger.error(f"决策对齐检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"决策对齐检查失败: {str(e)}")

@router.post("/predict-conflicts")
async def predict_conflicts(
    request: AlignmentCheckRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIAlignmentChecker = Depends(get_alignment_checker)
):
    """预测决策冲突"""
    try:
        result = await service.check_decision_alignment(
            decision_id=request.decision_id,
            check_type="resource_conflict",
            related_decision_ids=request.related_decision_ids
        )
        
        return {
            "decision_id": request.decision_id,
            "conflicts": result.get("check_results", {}).get("conflicts", {}),
            "prediction": result
        }
        
    except Exception as e:
        logger.error(f"冲突预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"冲突预测失败: {str(e)}")

@router.post("/generate-baseline", response_model=BaselineGenerationResponse)
async def generate_baseline(
    request: BaselineGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIBaselineGenerator = Depends(get_baseline_generator)
):
    """生成决策基线"""
    try:
        result = await service.generate_baseline(
            decision_id=request.decision_id,
            baseline_name=request.baseline_name,
            include_predictions=request.include_predictions,
            prediction_periods=request.prediction_periods
        )
        
        return result
        
    except Exception as e:
        logger.error(f"基线生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"基线生成失败: {str(e)}")

@router.get("/baseline/{baseline_id}")
async def get_baseline_detail(
    baseline_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取基线详情"""
    try:
        baseline = await db_service.execute_one(
            """
            SELECT * FROM decision_baselines
            WHERE baseline_id = $1
            """,
            [baseline_id]
        )
        
        if not baseline:
            raise HTTPException(status_code=404, detail="基线不存在")
        
        return baseline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取基线详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取基线详情失败: {str(e)}")

@router.post("/analyze-requirement", response_model=RequirementAnalysisResponse)
async def analyze_requirement_depth(
    request: RequirementAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIRequirementAnalyzer = Depends(get_requirement_analyzer)
):
    """深度分析需求"""
    try:
        result = await service.analyze_requirement_depth(
            requirement_id=request.requirement_id,
            analysis_type=request.analysis_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"需求分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"需求分析失败: {str(e)}")

@router.get("/requirement/{requirement_id}/similar")
async def get_similar_requirements(
    requirement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIRequirementAnalyzer = Depends(get_requirement_analyzer),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取相似需求"""
    try:
        # 获取需求数据
        requirement = await db_service.execute_one(
            """
            SELECT * FROM decision_requirements
            WHERE requirement_id = $1
            """,
            [requirement_id]
        )
        
        if not requirement:
            raise HTTPException(status_code=404, detail="需求不存在")
        
        # 分析相似需求
        result = await service.analyze_requirement_depth(
            requirement_id=requirement_id,
            analysis_type="similarity"
        )
        
        return {
            "requirement_id": requirement_id,
            "similar_requirements": result.get("analysis_results", {}).get("similar_requirements", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取相似需求失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取相似需求失败: {str(e)}")

class OptimizeBaselineRequest(BaseModel):
    """优化基线请求"""
    baseline_id: str = Field(..., description="基线ID")
    constraints: Optional[Dict[str, Any]] = Field(None, description="优化约束条件")

@router.post("/optimize-baseline")
async def optimize_baseline(
    request: OptimizeBaselineRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIBaselineGenerator = Depends(get_baseline_generator),
    db_service: DatabaseService = Depends(get_database_service)
):
    """优化基线参数"""
    try:
        # 获取基线数据
        baseline = await db_service.execute_one(
            """
            SELECT * FROM decision_baselines WHERE baseline_id = $1
            """,
            [request.baseline_id]
        )
        
        if not baseline:
            raise HTTPException(status_code=404, detail="基线不存在")
        
        # 获取决策数据
        decision_id = baseline.get("decision_id")
        decision_data = await db_service.execute_one(
            """
            SELECT * FROM hierarchical_decisions WHERE decision_id = $1
            """,
            [decision_id]
        )
        
        # 获取历史基线数据
        historical_baselines = await db_service.execute_query(
            """
            SELECT baseline_data, ai_predicted_outcomes
            FROM decision_baselines
            WHERE decision_id = $1 AND baseline_id != $2
            ORDER BY frozen_at DESC
            LIMIT 20
            """,
            [decision_id, request.baseline_id]
        )
        
        # 调用优化方法
        baseline_data = baseline.get("baseline_data")
        if isinstance(baseline_data, str):
            baseline_data = json.loads(baseline_data)
        
        optimization_result = await service._optimize_baseline_parameters(
            baseline_data=baseline_data or {},
            historical_data=historical_baselines or []
        )
        
        # 更新基线优化建议
        if optimization_result:
            await db_service.execute_update(
                """
                UPDATE decision_baselines
                SET ai_optimization_suggestions = $1,
                    updated_at = NOW()
                WHERE baseline_id = $2
                """,
                [json.dumps(optimization_result), request.baseline_id]
            )
        
        return {
            "baseline_id": request.baseline_id,
            "optimization_status": "completed",
            "optimization_result": optimization_result,
            "message": "基线优化完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"基线优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"基线优化失败: {str(e)}")

@router.get("/alignment-report/{decision_id}")
async def get_alignment_report(
    decision_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取对齐检查报告"""
    try:
        checks = await db_service.execute_query(
            """
            SELECT * FROM decision_alignment_checks
            WHERE decision_id = $1
            ORDER BY checked_at DESC
            LIMIT 10
            """,
            [decision_id]
        )
        
        return {
            "decision_id": decision_id,
            "checks": checks or [],
            "count": len(checks) if checks else 0
        }
        
    except Exception as e:
        logger.error(f"获取对齐报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对齐报告失败: {str(e)}")

# （错误处理应由应用层配置，此处移除）

