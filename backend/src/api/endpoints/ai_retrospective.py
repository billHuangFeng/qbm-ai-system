"""
AI复盘闭环服务API端点
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...services.ai_retrospective import (
    AIRetrospectiveDataCollector,
    AIRetrospectiveAnalyzer,
    AIRetrospectiveRecommender
)
from ...services.database_service import DatabaseService
from ...services.enhanced_enterprise_memory import EnterpriseMemoryService
from ..dependencies import get_database_service, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-retrospective", tags=["AI Retrospective"])

# ==================== 请求/响应模型 ====================

class RetrospectiveSessionCreate(BaseModel):
    """创建复盘会话请求"""
    session_name: str = Field(..., description="会话名称")
    session_type: str = Field(..., description="会话类型: decision, project, quarterly, annual")
    session_description: Optional[str] = Field(None, description="会话描述")
    decision_id: Optional[str] = Field(None, description="关联决策ID")
    strategic_objective_id: Optional[str] = Field(None, description="关联战略目标ID")
    okr_id: Optional[str] = Field(None, description="关联OKR ID")
    period_start: Optional[str] = Field(None, description="周期开始日期")
    period_end: Optional[str] = Field(None, description="周期结束日期")


class DecisionOutcomeCollectionRequest(BaseModel):
    """决策执行结果收集请求"""
    session_id: str = Field(..., description="复盘会话ID")
    decision_id: str = Field(..., description="决策ID")
    outcome_data: Dict[str, Any] = Field(..., description="执行结果数据")


class MetricMonitoringRequest(BaseModel):
    """指标监控请求"""
    session_id: str = Field(..., description="复盘会话ID")
    metric_id: str = Field(..., description="指标ID")
    time_range: Optional[Dict[str, str]] = Field(None, description="时间范围")


class AnomalyDetectionRequest(BaseModel):
    """异常检测请求"""
    session_id: str = Field(..., description="复盘会话ID")
    data: List[Dict[str, Any]] = Field(..., description="待检测数据")
    anomaly_type: str = Field("threshold", description="异常检测类型: threshold, statistical, pattern")


class UserFeedbackRequest(BaseModel):
    """用户反馈请求"""
    session_id: str = Field(..., description="复盘会话ID")
    feedback_data: Dict[str, Any] = Field(..., description="反馈数据")
    text: Optional[str] = Field(None, description="反馈文本")
    type: Optional[str] = Field("general", description="反馈类型")
    rating: Optional[float] = Field(None, description="评分")


class RootCauseAnalysisRequest(BaseModel):
    """根因分析请求"""
    session_id: str = Field(..., description="复盘会话ID")
    issue_data: Dict[str, Any] = Field(..., description="问题数据")
    analysis_depth: str = Field("comprehensive", description="分析深度: basic, comprehensive, deep")


class PatternIdentificationRequest(BaseModel):
    """模式识别请求"""
    session_id: str = Field(..., description="复盘会话ID")
    historical_data: List[Dict[str, Any]] = Field(..., description="历史数据")
    pattern_type: str = Field("all", description="模式类型: temporal, correlation, sequential, all")


class SuccessFactorExtractionRequest(BaseModel):
    """成功因素提取请求"""
    session_id: str = Field(..., description="复盘会话ID")
    success_cases: List[Dict[str, Any]] = Field(..., description="成功案例列表")


class FailureReasonAnalysisRequest(BaseModel):
    """失败原因分析请求"""
    session_id: str = Field(..., description="复盘会话ID")
    failure_cases: List[Dict[str, Any]] = Field(..., description="失败案例列表")


class ImprovementSuggestionRequest(BaseModel):
    """改进建议生成请求"""
    session_id: str = Field(..., description="复盘会话ID")
    analysis_results: Dict[str, Any] = Field(..., description="复盘分析结果")
    focus_areas: Optional[List[str]] = Field(None, description="重点关注领域")


class BestPracticeRequest(BaseModel):
    """最佳实践推荐请求"""
    session_id: str = Field(..., description="复盘会话ID")
    context: Dict[str, Any] = Field(..., description="上下文信息")


class ProcessOptimizationRequest(BaseModel):
    """流程优化建议请求"""
    session_id: str = Field(..., description="复盘会话ID")
    current_process: Dict[str, Any] = Field(..., description="当前流程描述")


class RiskAlertRequest(BaseModel):
    """风险预警请求"""
    session_id: str = Field(..., description="复盘会话ID")
    risk_indicators: List[Dict[str, Any]] = Field(..., description="风险指标列表")


# ==================== 依赖注入 ====================

async def get_data_collector(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIRetrospectiveDataCollector:
    """获取数据收集服务实例"""
    return AIRetrospectiveDataCollector(
        db_service=db_service,
        memory_service=memory_service
    )


async def get_retrospective_analyzer(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIRetrospectiveAnalyzer:
    """获取复盘分析服务实例"""
    return AIRetrospectiveAnalyzer(
        db_service=db_service,
        memory_service=memory_service
    )


# ==================== 数据收集端点 ====================

@router.post("/collect-decision-outcome")
async def collect_decision_outcome(
    request: DecisionOutcomeCollectionRequest,
    collector: AIRetrospectiveDataCollector = Depends(get_data_collector)
):
    """收集决策执行结果"""
    try:
        result = await collector.collect_decision_outcomes(
            decision_id=request.decision_id,
            session_id=request.session_id,
            outcome_data=request.outcome_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data_id": result.get("data_id"),
                "quality_score": result.get("quality_score"),
                "deviation_analysis": result.get("deviation_analysis")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "收集失败")
            )
    except Exception as e:
        logger.error(f"收集决策执行结果失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/monitor-metric")
async def monitor_metric(
    request: MetricMonitoringRequest,
    collector: AIRetrospectiveDataCollector = Depends(get_data_collector)
):
    """监控关键指标变化"""
    try:
        time_range = None
        if request.time_range:
            time_range = {
                "start": datetime.fromisoformat(request.time_range["start"]),
                "end": datetime.fromisoformat(request.time_range["end"])
            }
        
        result = await collector.monitor_metric_changes(
            metric_id=request.metric_id,
            session_id=request.session_id,
            time_range=time_range
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data_id": result.get("data_id"),
                "quality_score": result.get("quality_score"),
                "trend_analysis": result.get("trend_analysis"),
                "anomalies_detected": result.get("anomalies_detected", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "监控失败")
            )
    except Exception as e:
        logger.error(f"监控指标变化失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/detect-anomalies")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    collector: AIRetrospectiveDataCollector = Depends(get_data_collector)
):
    """异常事件智能识别"""
    try:
        result = await collector.detect_anomalies(
            data=request.data,
            session_id=request.session_id,
            anomaly_type=request.anomaly_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data_id": result.get("data_id"),
                "quality_score": result.get("quality_score"),
                "anomaly_count": result.get("anomaly_count", 0),
                "anomaly_rate": result.get("anomaly_rate", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "异常检测失败")
            )
    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/collect-feedback")
async def collect_feedback(
    request: UserFeedbackRequest,
    collector: AIRetrospectiveDataCollector = Depends(get_data_collector)
):
    """收集用户反馈"""
    try:
        feedback_data = request.feedback_data.copy()
        if request.text:
            feedback_data["text"] = request.text
        if request.type:
            feedback_data["type"] = request.type
        if request.rating is not None:
            feedback_data["rating"] = request.rating
        
        result = await collector.collect_user_feedback(
            session_id=request.session_id,
            feedback_data=feedback_data
        )
        
        if result.get("success"):
            return {
                "success": True,
                "data_id": result.get("data_id"),
                "quality_score": result.get("quality_score"),
                "sentiment": result.get("sentiment", {})
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "收集反馈失败")
            )
    except Exception as e:
        logger.error(f"收集用户反馈失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/data/{session_id}")
async def get_retrospective_data(
    session_id: str,
    data_type: Optional[str] = None,
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取复盘数据"""
    try:
        query = """
            SELECT * FROM retrospective_data
            WHERE session_id = $1
        """
        params = [session_id]
        
        if data_type:
            query += " AND data_type = $2"
            params.append(data_type)
        
        query += " ORDER BY collected_at DESC"
        
        result = await db_service.execute_query(query, params)
        
        return {
            "success": True,
            "session_id": session_id,
            "data_count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"获取复盘数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== 分析端点 ====================

@router.post("/analyze-root-cause")
async def analyze_root_cause(
    request: RootCauseAnalysisRequest,
    analyzer: AIRetrospectiveAnalyzer = Depends(get_retrospective_analyzer)
):
    """执行根因分析"""
    try:
        result = await analyzer.analyze_root_causes(
            issue_data=request.issue_data,
            session_id=request.session_id,
            analysis_depth=request.analysis_depth
        )
        
        if result.get("success"):
            return {
                "success": True,
                "insight_id": result.get("insight_id"),
                "root_causes": result.get("root_causes", []),
                "causal_chains": result.get("causal_chains", []),
                "confidence": result.get("confidence", 0.0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "根因分析失败")
            )
    except Exception as e:
        logger.error(f"根因分析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/identify-patterns")
async def identify_patterns(
    request: PatternIdentificationRequest,
    analyzer: AIRetrospectiveAnalyzer = Depends(get_retrospective_analyzer)
):
    """识别模式"""
    try:
        result = await analyzer.identify_patterns(
            historical_data=request.historical_data,
            session_id=request.session_id,
            pattern_type=request.pattern_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "insight_id": result.get("insight_id"),
                "patterns": result.get("patterns", {}),
                "pattern_scores": result.get("pattern_scores", {}),
                "confidence": result.get("confidence", 0.0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "模式识别失败")
            )
    except Exception as e:
        logger.error(f"模式识别失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/extract-success-factors")
async def extract_success_factors(
    request: SuccessFactorExtractionRequest,
    analyzer: AIRetrospectiveAnalyzer = Depends(get_retrospective_analyzer)
):
    """提取成功因素"""
    try:
        result = await analyzer.extract_success_factors(
            success_cases=request.success_cases,
            session_id=request.session_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "insight_id": result.get("insight_id"),
                "success_factors": result.get("success_factors", []),
                "factor_scores": result.get("factor_scores", {}),
                "best_practices": result.get("best_practices", []),
                "confidence": result.get("confidence", 0.0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "成功因素提取失败")
            )
    except Exception as e:
        logger.error(f"提取成功因素失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/analyze-failure-reasons")
async def analyze_failure_reasons(
    request: FailureReasonAnalysisRequest,
    analyzer: AIRetrospectiveAnalyzer = Depends(get_retrospective_analyzer)
):
    """分析失败原因"""
    try:
        result = await analyzer.analyze_failure_reasons(
            failure_cases=request.failure_cases,
            session_id=request.session_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "insight_id": result.get("insight_id"),
                "failure_patterns": result.get("failure_patterns", []),
                "failure_chains": result.get("failure_chains", []),
                "risk_factors": result.get("risk_factors", []),
                "confidence": result.get("confidence", 0.0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "失败原因分析失败")
            )
    except Exception as e:
        logger.error(f"分析失败原因失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/insights/{session_id}")
async def get_retrospective_insights(
    session_id: str,
    insight_type: Optional[str] = None,
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取复盘洞察"""
    try:
        query = """
            SELECT * FROM retrospective_insights
            WHERE session_id = $1
        """
        params = [session_id]
        
        if insight_type:
            query += " AND insight_type = $2"
            params.append(insight_type)
        
        query += " ORDER BY created_at DESC"
        
        result = await db_service.execute_query(query, params)
        
        return {
                "success": True,
                "session_id": session_id,
                "insight_count": len(result),
                "insights": result
            }
    except Exception as e:
        logger.error(f"获取复盘洞察失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def get_retrospective_recommender(
    db_service: DatabaseService = Depends(get_database_service),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service)
) -> AIRetrospectiveRecommender:
    """获取复盘建议生成服务实例"""
    return AIRetrospectiveRecommender(
        db_service=db_service,
        memory_service=memory_service
    )


# ==================== 建议生成端点 ====================

@router.post("/generate-improvements")
async def generate_improvements(
    request: ImprovementSuggestionRequest,
    recommender: AIRetrospectiveRecommender = Depends(get_retrospective_recommender)
):
    """生成改进建议"""
    try:
        result = await recommender.generate_improvement_suggestions(
            analysis_results=request.analysis_results,
            session_id=request.session_id,
            focus_areas=request.focus_areas
        )
        
        if result.get("success"):
            return {
                "success": True,
                "recommendation_count": result.get("recommendation_count", 0),
                "recommendation_ids": result.get("recommendation_ids", []),
                "recommendations": result.get("recommendations", [])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "生成改进建议失败")
            )
    except Exception as e:
        logger.error(f"生成改进建议失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/recommend-best-practices")
async def recommend_best_practices(
    request: BestPracticeRequest,
    recommender: AIRetrospectiveRecommender = Depends(get_retrospective_recommender)
):
    """推荐最佳实践"""
    try:
        result = await recommender.recommend_best_practices(
            context=request.context,
            session_id=request.session_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "practice_count": result.get("practice_count", 0),
                "practice_ids": result.get("practice_ids", []),
                "practices": result.get("practices", [])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "推荐最佳实践失败")
            )
    except Exception as e:
        logger.error(f"推荐最佳实践失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/suggest-process-optimizations")
async def suggest_process_optimizations(
    request: ProcessOptimizationRequest,
    recommender: AIRetrospectiveRecommender = Depends(get_retrospective_recommender)
):
    """生成流程优化建议"""
    try:
        result = await recommender.suggest_process_optimizations(
            current_process=request.current_process,
            session_id=request.session_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "optimization_count": result.get("optimization_count", 0),
                "optimization_ids": result.get("optimization_ids", []),
                "optimizations": result.get("optimizations", [])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "生成流程优化建议失败")
            )
    except Exception as e:
        logger.error(f"生成流程优化建议失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/create-risk-alerts")
async def create_risk_alerts(
    request: RiskAlertRequest,
    recommender: AIRetrospectiveRecommender = Depends(get_retrospective_recommender)
):
    """创建风险预警"""
    try:
        result = await recommender.create_risk_alerts(
            risk_indicators=request.risk_indicators,
            session_id=request.session_id
        )
        
        if result.get("success"):
            return {
                "success": True,
                "alert_count": result.get("alert_count", 0),
                "alert_ids": result.get("alert_ids", []),
                "alerts": result.get("alerts", [])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "创建风险预警失败")
            )
    except Exception as e:
        logger.error(f"创建风险预警失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/recommendations/{session_id}")
async def get_recommendations(
    session_id: str,
    recommendation_type: Optional[str] = None,
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取建议列表"""
    try:
        query = """
            SELECT * FROM retrospective_recommendations
            WHERE session_id = $1
        """
        params = [session_id]
        
        if recommendation_type:
            query += " AND recommendation_type = $2"
            params.append(recommendation_type)
        
        query += " ORDER BY created_at DESC"
        
        result = await db_service.execute_query(query, params)
        
        return {
            "success": True,
            "session_id": session_id,
            "recommendation_count": len(result),
            "recommendations": result
        }
    except Exception as e:
        logger.error(f"获取建议列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
