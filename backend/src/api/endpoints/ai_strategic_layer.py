"""
AI增强战略层API端点
提供战略目标、北极星指标、OKR和决策需求的AI增强功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.ai_strategic_layer.ai_strategic_objectives_service import AIStrategicObjectivesService
from ...services.ai_strategic_layer.ai_north_star_service import AINorthStarService
from ...services.ai_strategic_layer.ai_okr_service import AIOKRService
from ...services.ai_strategic_layer.ai_decision_requirements_service import AIDecisionRequirementsService
from ...services.database_service import DatabaseService
from ...services.enhanced_enterprise_memory import EnterpriseMemoryService
from ..dependencies import get_current_user, get_database_service, get_memory_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/ai-strategic", tags=["AI Strategic Layer"])

# 服务依赖
def get_strategic_objectives_service(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIStrategicObjectivesService:
    """获取战略目标服务"""
    return AIStrategicObjectivesService(db_service=db_service, memory_service=memory_service)

def get_north_star_service(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AINorthStarService:
    """获取北极星指标服务"""
    return AINorthStarService(db_service=db_service, memory_service=memory_service)

def get_okr_service(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIOKRService:
    """获取OKR服务"""
    return AIOKRService(db_service=db_service, memory_service=memory_service)

def get_decision_requirements_service(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIDecisionRequirementsService:
    """获取决策需求服务"""
    return AIDecisionRequirementsService(db_service=db_service, memory_service=memory_service)

# ==================== Request/Response Models ====================

class SynergyAnalysisRequest(BaseModel):
    """协同效应分析请求"""
    objective_id: str = Field(..., description="目标ID")
    related_objective_ids: Optional[List[str]] = Field(None, description="相关目标ID列表")

class SynergyAnalysisResponse(BaseModel):
    """协同效应分析响应"""
    objective_id: str
    synergy_score: float
    synergy_analysis: Dict[str, Any]
    related_objectives: List[Dict[str, Any]]

class MetricRecommendationRequest(BaseModel):
    """指标推荐请求"""
    strategic_objective_id: str = Field(..., description="战略目标ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class MetricRecommendationResponse(BaseModel):
    """指标推荐响应"""
    strategic_objective_id: str
    recommendations: List[Dict[str, Any]]
    total_count: int

class ConflictPredictionRequest(BaseModel):
    """冲突预测请求"""
    decision_ids: List[str] = Field(..., description="决策ID列表")
    check_type: Optional[str] = Field("full_alignment", description="检查类型")

class ConflictPredictionResponse(BaseModel):
    """冲突预测响应"""
    conflicts: List[Dict[str, Any]]
    conflict_count: int
    overall_risk_level: str

class BaselineGenerationRequest(BaseModel):
    """基线生成请求"""
    decision_id: str = Field(..., description="决策ID")
    baseline_name: Optional[str] = Field(None, description="基线名称")
    include_predictions: bool = Field(True, description="是否包含AI预测")

class BaselineGenerationResponse(BaseModel):
    """基线生成响应"""
    baseline_id: str
    baseline_code: str
    baseline_data: Dict[str, Any]
    ai_predictions: Optional[Dict[str, Any]] = None

class CreateOKRRequest(BaseModel):
    """创建OKR请求"""
    okr_name: str = Field(..., description="OKR名称")
    objective_statement: str = Field(..., description="目标陈述")
    strategic_objective_id: str = Field(..., description="战略目标ID")
    period_type: str = Field(..., description="周期类型: quarterly, annual, custom")
    period_start: str = Field(..., description="周期开始日期")
    period_end: str = Field(..., description="周期结束日期")
    owner_id: Optional[str] = Field(None, description="负责人ID")
    owner_name: Optional[str] = Field(None, description="负责人名称")
    okr_description: Optional[str] = Field(None, description="OKR描述")

class CreateKeyResultRequest(BaseModel):
    """创建关键结果请求"""
    okr_id: str = Field(..., description="OKR ID")
    kr_name: str = Field(..., description="关键结果名称")
    kr_statement: str = Field(..., description="关键结果陈述")
    kr_type: str = Field(..., description="KR类型: metric, milestone, deliverable")
    target_value: Optional[float] = Field(None, description="目标值")
    current_value: Optional[float] = Field(None, description="当前值")
    unit: Optional[str] = Field(None, description="单位")
    weight: float = Field(1.0, description="权重")
    owner_id: Optional[str] = Field(None, description="负责人ID")
    owner_name: Optional[str] = Field(None, description="负责人名称")

class CreateRequirementRequest(BaseModel):
    """创建需求请求"""
    requirement_title: str = Field(..., description="需求标题")
    requirement_description: str = Field(..., description="需求描述")
    requirement_type: str = Field(..., description="需求类型: strategic, tactical, operational, emergency")
    parent_decision_id: str = Field(..., description="父决策ID")
    strategic_objective_id: Optional[str] = Field(None, description="战略目标ID")
    requester_id: str = Field(..., description="申请人ID")
    requester_name: str = Field(..., description="申请人名称")
    requester_department: Optional[str] = Field(None, description="申请人部门")
    requirement_category: Optional[str] = Field(None, description="需求类别")
    required_by_date: Optional[str] = Field(None, description="需求截止日期")
    priority_level: int = Field(5, description="优先级等级 1-10")

class CreateMetricRequest(BaseModel):
    """创建指标请求"""
    metric_name: str = Field(..., description="指标名称")
    metric_description: str = Field(..., description="指标描述")
    strategic_objective_id: str = Field(..., description="战略目标ID")
    metric_type: str = Field(..., description="指标类型")
    target_value: Optional[float] = Field(None, description="目标值")
    calculation_formula: Optional[str] = Field(None, description="计算公式")
    measurement_frequency: str = Field("monthly", description="测量频率")
    is_primary: bool = Field(False, description="是否主要指标")

class UpdateKRProgressRequest(BaseModel):
    """更新KR进度请求"""
    current_value: Optional[float] = Field(None, description="当前值")
    current_progress: Optional[float] = Field(None, description="当前进度 0-100")
    status: Optional[str] = Field(None, description="状态")

# ==================== API Endpoints ====================

@router.post("/analyze-synergy", response_model=SynergyAnalysisResponse)
async def analyze_synergy(
    request: SynergyAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIStrategicObjectivesService = Depends(get_strategic_objectives_service)
):
    """AI协同效应分析"""
    try:
        # 这里需要调用AIStrategicObjectivesService的协同效应分析方法
        # 由于原服务中没有公开的analyze_synergy方法，我们需要获取目标信息后进行分析
        
        # 获取目标信息
        if service.db_service:
            objective = await service.db_service.execute_one(
                """
                SELECT * FROM strategic_objectives
                WHERE objective_id = $1
                """,
                [request.objective_id]
            )
            
            if not objective:
                raise HTTPException(status_code=404, detail="目标不存在")
            
            # 获取协同效应分析结果（如果已存在）
            synergy_analysis = objective.get("synergy_analysis")
            if synergy_analysis and isinstance(synergy_analysis, str):
                import json
                synergy_analysis = json.loads(synergy_analysis)
            elif not synergy_analysis:
                synergy_analysis = {
                    "synergy_score": 0.5,
                    "analysis": "无协同效应数据",
                    "related_objectives": []
                }
            
            return SynergyAnalysisResponse(
                objective_id=request.objective_id,
                synergy_score=objective.get("synergy_score", 0.5),
                synergy_analysis=synergy_analysis,
                related_objectives=synergy_analysis.get("related_objectives", [])
            )
        else:
            raise HTTPException(status_code=503, detail="数据库服务未初始化")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"协同效应分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"协同效应分析失败: {str(e)}")

@router.post("/recommend-metrics", response_model=MetricRecommendationResponse)
async def recommend_metrics(
    request: MetricRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AINorthStarService = Depends(get_north_star_service)
):
    """AI指标推荐"""
    try:
        recommendations = await service.recommend_metrics(
            strategic_objective_id=request.strategic_objective_id,
            context=request.context
        )
        
        return MetricRecommendationResponse(
            strategic_objective_id=request.strategic_objective_id,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"指标推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"指标推荐失败: {str(e)}")

@router.post("/predict-conflicts", response_model=ConflictPredictionResponse)
async def predict_conflicts(
    request: ConflictPredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """AI冲突预测"""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="数据库服务未初始化")
        
        conflicts = []
        
        # 获取决策信息
        decisions = await db_service.execute_query(
            """
            SELECT * FROM hierarchical_decisions
            WHERE decision_id = ANY($1)
            """,
            [request.decision_ids]
        )
        
        if len(decisions) < 2:
            return ConflictPredictionResponse(
                conflicts=[],
                conflict_count=0,
                overall_risk_level="low"
            )
        
        # 简单的冲突检测（基于目标、资源等）
        # 这里可以集成更复杂的冲突检测算法
        for i, decision1 in enumerate(decisions):
            for decision2 in decisions[i+1:]:
                # 检查资源冲突
                # 检查目标冲突
                # 检查时间冲突
                # 这里简化处理
                conflicts.append({
                    "decision1_id": decision1.get("decision_id"),
                    "decision2_id": decision2.get("decision_id"),
                    "conflict_type": "potential",
                    "severity": "medium",
                    "description": "可能存在资源或目标冲突",
                    "recommendation": "建议进行详细对齐检查"
                })
        
        overall_risk = "high" if len(conflicts) > 3 else "medium" if len(conflicts) > 0 else "low"
        
        return ConflictPredictionResponse(
            conflicts=conflicts,
            conflict_count=len(conflicts),
            overall_risk_level=overall_risk
        )
        
    except Exception as e:
        logger.error(f"冲突预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"冲突预测失败: {str(e)}")

@router.post("/generate-baseline", response_model=BaselineGenerationResponse)
async def generate_baseline(
    request: BaselineGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """AI基线生成"""
    try:
        if not db_service:
            raise HTTPException(status_code=503, detail="数据库服务未初始化")
        
        # 获取决策信息
        decision = await db_service.execute_one(
            """
            SELECT * FROM hierarchical_decisions
            WHERE decision_id = $1
            """,
            [request.decision_id]
        )
        
        if not decision:
            raise HTTPException(status_code=404, detail="决策不存在")
        
        # 生成基线数据
        baseline_name = request.baseline_name or f"Baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        baseline_code = f"BL_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 构建基线数据快照
        baseline_data = {
            "decision_id": decision.get("decision_id"),
            "decision_title": decision.get("decision_title"),
            "decision_content": decision.get("decision_content"),
            "target_kpis": decision.get("target_kpis", []),
            "budget_allocation": decision.get("budget_allocation", {}),
            "frozen_at": datetime.now().isoformat(),
            "frozen_by": current_user.get("user_id", "")
        }
        
        ai_predictions = None
        if request.include_predictions:
            # 这里可以集成VARModel或LightGBM进行预测
            ai_predictions = {
                "prediction_method": "baseline",
                "confidence": 0.7,
                "predicted_outcomes": {}
            }
        
        # 插入基线记录
        baseline_id = await db_service.execute_insert(
            """
            INSERT INTO decision_baselines
            (baseline_name, baseline_code, decision_id, baseline_data,
             target_kpis, budget_allocation, ai_predicted_outcomes,
             ai_baseline_confidence, frozen_by, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING baseline_id
            """,
            [
                baseline_name,
                baseline_code,
                request.decision_id,
                baseline_data,
                baseline_data.get("target_kpis", []),
                baseline_data.get("budget_allocation", {}),
                ai_predictions,
                0.7,
                current_user.get("user_id", ""),
                "active"
            ]
        )
        
        return BaselineGenerationResponse(
            baseline_id=baseline_id,
            baseline_code=baseline_code,
            baseline_data=baseline_data,
            ai_predictions=ai_predictions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"基线生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"基线生成失败: {str(e)}")

# ==================== 辅助端点 ====================

@router.get("/okr/{okr_id}/prediction")
async def get_okr_prediction(
    okr_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """获取OKR达成概率预测"""
    try:
        okr = await service.get_okr(okr_id)
        
        if not okr:
            raise HTTPException(status_code=404, detail="OKR不存在")
        
        prediction = okr.get("ai_achievement_prediction")
        if isinstance(prediction, str):
            import json
            prediction = json.loads(prediction)
        
        return {
            "okr_id": okr_id,
            "achievement_probability": okr.get("ai_achievement_probability", 0.5),
            "prediction_details": prediction or {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKR预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取OKR预测失败: {str(e)}")

@router.get("/requirement/{requirement_id}/priority")
async def get_requirement_priority(
    requirement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIDecisionRequirementsService = Depends(get_decision_requirements_service)
):
    """获取需求优先级分析"""
    try:
        requirement = await service.get_requirement(requirement_id)
        
        if not requirement:
            raise HTTPException(status_code=404, detail="需求不存在")
        
        priority_analysis = requirement.get("ai_priority_analysis")
        if isinstance(priority_analysis, str):
            import json
            priority_analysis = json.loads(priority_analysis)
        
        return {
            "requirement_id": requirement_id,
            "priority_score": requirement.get("ai_priority_score", 0.5),
            "priority_level": priority_analysis.get("priority_level", 5) if priority_analysis else 5,
            "analysis_details": priority_analysis or {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取需求优先级失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取需求优先级失败: {str(e)}")

@router.get("/metric/{metric_id}/health")
async def get_metric_health(
    metric_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AINorthStarService = Depends(get_north_star_service)
):
    """获取指标健康度评分"""
    try:
        health_score = await service.calculate_metric_health_score(metric_id)
        
        return health_score
        
    except Exception as e:
        logger.error(f"获取指标健康度失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指标健康度失败: {str(e)}")

# ==================== CRUD端点 ====================

@router.post("/okr/create")
async def create_okr(
    request: CreateOKRRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """创建OKR"""
    try:
        result = await service.create_okr(
            okr_name=request.okr_name,
            objective_statement=request.objective_statement,
            strategic_objective_id=request.strategic_objective_id,
            period_type=request.period_type,
            period_start=request.period_start,
            period_end=request.period_end,
            owner_id=request.owner_id or current_user.get("user_id", ""),
            owner_name=request.owner_name or current_user.get("name", ""),
            okr_description=request.okr_description
        )
        
        return result
        
    except Exception as e:
        logger.error(f"创建OKR失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建OKR失败: {str(e)}")

@router.post("/okr/{okr_id}/key-result/create")
async def create_key_result(
    okr_id: str,
    request: CreateKeyResultRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """创建关键结果"""
    try:
        result = await service.create_key_result(
            okr_id=okr_id,
            kr_name=request.kr_name,
            kr_statement=request.kr_statement,
            kr_type=request.kr_type,
            target_value=request.target_value,
            current_value=request.current_value,
            unit=request.unit,
            weight=request.weight,
            owner_id=request.owner_id or current_user.get("user_id", ""),
            owner_name=request.owner_name or current_user.get("name", "")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"创建关键结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建关键结果失败: {str(e)}")

@router.post("/okr/{okr_id}/key-result/{kr_id}/update-progress")
async def update_kr_progress(
    okr_id: str,
    kr_id: str,
    request: UpdateKRProgressRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """更新关键结果进度"""
    try:
        result = await service.update_key_result_progress(
            kr_id=kr_id,
            current_value=request.current_value,
            current_progress=request.current_progress,
            status=request.status
        )
        
        return result
        
    except Exception as e:
        logger.error(f"更新KR进度失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新KR进度失败: {str(e)}")

@router.post("/requirement/create")
async def create_requirement(
    request: CreateRequirementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIDecisionRequirementsService = Depends(get_decision_requirements_service)
):
    """创建决策需求"""
    try:
        result = await service.create_requirement(
            requirement_title=request.requirement_title,
            requirement_description=request.requirement_description,
            requirement_type=request.requirement_type,
            parent_decision_id=request.parent_decision_id,
            strategic_objective_id=request.strategic_objective_id,
            requester_id=request.requester_id or current_user.get("user_id", ""),
            requester_name=request.requester_name or current_user.get("name", ""),
            requester_department=request.requester_department,
            requirement_category=request.requirement_category,
            required_by_date=request.required_by_date,
            priority_level=request.priority_level
        )
        
        return result
        
    except Exception as e:
        logger.error(f"创建需求失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建需求失败: {str(e)}")

@router.post("/metric/create")
async def create_metric(
    request: CreateMetricRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AINorthStarService = Depends(get_north_star_service)
):
    """创建北极星指标"""
    try:
        result = await service.create_north_star_metric(
            metric_name=request.metric_name,
            metric_description=request.metric_description,
            strategic_objective_id=request.strategic_objective_id,
            metric_type=request.metric_type,
            target_value=request.target_value,
            calculation_formula=request.calculation_formula,
            measurement_frequency=request.measurement_frequency,
            is_primary=request.is_primary
        )
        
        return result
        
    except Exception as e:
        logger.error(f"创建指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建指标失败: {str(e)}")

@router.get("/okr/{okr_id}")
async def get_okr_detail(
    okr_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """获取OKR详情"""
    try:
        okr = await service.get_okr(okr_id)
        
        if not okr:
            raise HTTPException(status_code=404, detail="OKR不存在")
        
        return okr
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取OKR详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取OKR详情失败: {str(e)}")

@router.get("/okr/by-objective/{strategic_objective_id}")
async def get_okrs_by_objective(
    strategic_objective_id: str,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIOKRService = Depends(get_okr_service)
):
    """获取指定战略目标下的所有OKR"""
    try:
        okrs = await service.get_okrs_by_objective(
            strategic_objective_id=strategic_objective_id,
            status=status
        )
        
        return {
            "strategic_objective_id": strategic_objective_id,
            "okrs": okrs,
            "count": len(okrs)
        }
        
    except Exception as e:
        logger.error(f"获取OKR列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取OKR列表失败: {str(e)}")

@router.get("/requirement/{requirement_id}")
async def get_requirement_detail(
    requirement_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AIDecisionRequirementsService = Depends(get_decision_requirements_service)
):
    """获取需求详情"""
    try:
        requirement = await service.get_requirement(requirement_id)
        
        if not requirement:
            raise HTTPException(status_code=404, detail="需求不存在")
        
        return requirement
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取需求详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取需求详情失败: {str(e)}")

@router.get("/metric/{metric_id}")
async def get_metric_detail(
    metric_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: AINorthStarService = Depends(get_north_star_service)
):
    """获取指标详情"""
    try:
        metric = await service.get_north_star_metric(metric_id)
        
        if not metric:
            raise HTTPException(status_code=404, detail="指标不存在")
        
        return metric
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指标详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取指标详情失败: {str(e)}")

# （错误处理应由应用层配置，此处移除）

