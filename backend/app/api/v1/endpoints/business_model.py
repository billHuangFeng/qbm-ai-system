"""
商业模式分析API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging

from ....core.security import get_current_user
from ....models.user import User
from ....models.business_model import (
    ValueProposition, CustomerCognition, ProductValueAlignment,
    ResourceCapability, ValueDelivery, ProductDevelopment,
    InvestmentValue, ValueAnalysis
)
from ....crud.business_model import (
    value_proposition_crud, customer_cognition_crud,
    product_value_alignment_crud, resource_capability_crud,
    value_delivery_crud, product_development_crud,
    investment_value_crud, value_analysis_crud
)
from ....schemas.business_model import (
    ValuePropositionCreate, ValuePropositionUpdate, ValuePropositionResponse,
    CustomerCognitionCreate, CustomerCognitionUpdate, CustomerCognitionResponse,
    BusinessModelAnalysisRequest, BusinessModelAnalysisResponse
)
from ....ai_engine.business_model_core import BusinessModelAnalyzer, BusinessModelDashboard

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/value-propositions", response_model=List[ValuePropositionResponse])
async def get_value_propositions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """获取价值主张列表"""
    try:
        value_propositions = await value_proposition_crud.get_multi(
            skip=skip, limit=limit
        )
        return value_propositions
    except Exception as e:
        logger.error(f"获取价值主张列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取价值主张列表失败")

@router.post("/value-propositions", response_model=ValuePropositionResponse)
async def create_value_proposition(
    value_proposition: ValuePropositionCreate,
    current_user: User = Depends(get_current_user)
):
    """创建价值主张"""
    try:
        created_vp = await value_proposition_crud.create(value_proposition)
        return created_vp
    except Exception as e:
        logger.error(f"创建价值主张失败: {e}")
        raise HTTPException(status_code=500, detail="创建价值主张失败")

@router.get("/value-propositions/{vp_id}", response_model=ValuePropositionResponse)
async def get_value_proposition(
    vp_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取价值主张详情"""
    try:
        value_proposition = await value_proposition_crud.get(vp_id)
        if not value_proposition:
            raise HTTPException(status_code=404, detail="价值主张不存在")
        return value_proposition
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取价值主张详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取价值主张详情失败")

@router.put("/value-propositions/{vp_id}", response_model=ValuePropositionResponse)
async def update_value_proposition(
    vp_id: int,
    value_proposition: ValuePropositionUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新价值主张"""
    try:
        updated_vp = await value_proposition_crud.update(vp_id, value_proposition)
        if not updated_vp:
            raise HTTPException(status_code=404, detail="价值主张不存在")
        return updated_vp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新价值主张失败: {e}")
        raise HTTPException(status_code=500, detail="更新价值主张失败")

@router.delete("/value-propositions/{vp_id}")
async def delete_value_proposition(
    vp_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除价值主张"""
    try:
        deleted = await value_proposition_crud.delete(vp_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="价值主张不存在")
        return {"message": "价值主张删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除价值主张失败: {e}")
        raise HTTPException(status_code=500, detail="删除价值主张失败")

@router.get("/customer-cognitions", response_model=List[CustomerCognitionResponse])
async def get_customer_cognitions(
    customer_id: Optional[int] = Query(None),
    value_proposition_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """获取客户认知列表"""
    try:
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        if value_proposition_id:
            filters["value_proposition_id"] = value_proposition_id
        
        cognitions = await customer_cognition_crud.get_multi(
            skip=skip, limit=limit, filters=filters
        )
        return cognitions
    except Exception as e:
        logger.error(f"获取客户认知列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取客户认知列表失败")

@router.post("/customer-cognitions", response_model=CustomerCognitionResponse)
async def create_customer_cognition(
    cognition: CustomerCognitionCreate,
    current_user: User = Depends(get_current_user)
):
    """创建客户认知记录"""
    try:
        created_cognition = await customer_cognition_crud.create(cognition)
        return created_cognition
    except Exception as e:
        logger.error(f"创建客户认知记录失败: {e}")
        raise HTTPException(status_code=500, detail="创建客户认知记录失败")

@router.get("/resource-capabilities", response_model=List[Dict[str, Any]])
async def get_resource_capabilities(
    type: Optional[str] = Query(None, description="类型: resource 或 capability"),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """获取资源能力列表"""
    try:
        filters = {}
        if type:
            filters["type"] = type
        if category:
            filters["category"] = category
        
        resources = await resource_capability_crud.get_multi(
            skip=skip, limit=limit, filters=filters
        )
        return resources
    except Exception as e:
        logger.error(f"获取资源能力列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取资源能力列表失败")

@router.get("/investment-values", response_model=List[Dict[str, Any]])
async def get_investment_values(
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """获取投资价值列表"""
    try:
        filters = {}
        if category:
            filters["investment_category"] = category
        if start_date:
            filters["investment_date__gte"] = start_date
        if end_date:
            filters["investment_date__lte"] = end_date
        
        investments = await investment_value_crud.get_multi(
            skip=skip, limit=limit, filters=filters
        )
        return investments
    except Exception as e:
        logger.error(f"获取投资价值列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取投资价值列表失败")

@router.post("/analysis/comprehensive", response_model=BusinessModelAnalysisResponse)
async def comprehensive_business_model_analysis(
    analysis_request: BusinessModelAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """综合商业模式分析"""
    try:
        # 获取分析所需的数据
        data = await _get_analysis_data(analysis_request)
        
        # 执行分析
        dashboard = BusinessModelDashboard()
        analysis_results = dashboard.generate_comprehensive_analysis(data)
        
        # 保存分析结果
        analysis_record = ValueAnalysis(
            analysis_type="comprehensive",
            analysis_period=analysis_request.analysis_period,
            analysis_results=analysis_results,
            key_insights=_extract_key_insights(analysis_results),
            recommendations=_generate_recommendations(analysis_results),
            analysis_date=datetime.utcnow()
        )
        
        saved_analysis = await value_analysis_crud.create(analysis_record)
        
        return BusinessModelAnalysisResponse(
            analysis_id=saved_analysis.id,
            analysis_type="comprehensive",
            analysis_period=analysis_request.analysis_period,
            results=analysis_results,
            key_insights=_extract_key_insights(analysis_results),
            recommendations=_generate_recommendations(analysis_results),
            analysis_date=saved_analysis.analysis_date
        )
        
    except Exception as e:
        logger.error(f"综合商业模式分析失败: {e}")
        raise HTTPException(status_code=500, detail="综合商业模式分析失败")

@router.get("/analysis/value-proposition-cognition")
async def analyze_value_proposition_cognition(
    value_proposition_id: Optional[int] = Query(None),
    customer_segment: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """分析价值主张认知"""
    try:
        # 获取客户认知数据
        filters = {}
        if value_proposition_id:
            filters["value_proposition_id"] = value_proposition_id
        
        cognitions = await customer_cognition_crud.get_multi(filters=filters)
        
        if not cognitions:
            return {"message": "没有找到相关的认知数据"}
        
        # 转换为DataFrame进行分析
        cognition_data = pd.DataFrame([cognition.dict() for cognition in cognitions])
        
        # 执行分析
        analyzer = BusinessModelAnalyzer()
        results = analyzer.analyze_value_proposition_cognition(cognition_data)
        
        return results
        
    except Exception as e:
        logger.error(f"价值主张认知分析失败: {e}")
        raise HTTPException(status_code=500, detail="价值主张认知分析失败")

@router.get("/analysis/customer-acceptance")
async def analyze_customer_acceptance(
    value_proposition_id: Optional[int] = Query(None),
    customer_segment: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """分析客户接纳程度"""
    try:
        # 获取客户认知数据
        filters = {}
        if value_proposition_id:
            filters["value_proposition_id"] = value_proposition_id
        
        cognitions = await customer_cognition_crud.get_multi(filters=filters)
        
        if not cognitions:
            return {"message": "没有找到相关的认知数据"}
        
        # 转换为DataFrame进行分析
        cognition_data = pd.DataFrame([cognition.dict() for cognition in cognitions])
        
        # 执行分析
        analyzer = BusinessModelAnalyzer()
        results = analyzer.analyze_customer_acceptance(cognition_data)
        
        return results
        
    except Exception as e:
        logger.error(f"客户接纳程度分析失败: {e}")
        raise HTTPException(status_code=500, detail="客户接纳程度分析失败")

@router.get("/analysis/customer-experience")
async def analyze_customer_experience(
    customer_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """分析客户体验程度"""
    try:
        # 获取客户认知数据
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        
        cognitions = await customer_cognition_crud.get_multi(filters=filters)
        
        if not cognitions:
            return {"message": "没有找到相关的体验数据"}
        
        # 获取产品数据
        product_filters = {}
        if product_id:
            product_filters["id"] = product_id
        
        products = await product_value_alignment_crud.get_multi(filters=product_filters)
        
        # 转换为DataFrame进行分析
        cognition_data = pd.DataFrame([cognition.dict() for cognition in cognitions])
        product_data = pd.DataFrame([product.dict() for product in products])
        
        # 执行分析
        analyzer = BusinessModelAnalyzer()
        results = analyzer.analyze_customer_experience(cognition_data, product_data)
        
        return results
        
    except Exception as e:
        logger.error(f"客户体验程度分析失败: {e}")
        raise HTTPException(status_code=500, detail="客户体验程度分析失败")

@router.get("/analysis/incremental-value")
async def analyze_incremental_value(
    investment_category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """分析价值增量"""
    try:
        # 获取投资数据
        investment_filters = {}
        if investment_category:
            investment_filters["investment_category"] = investment_category
        if start_date:
            investment_filters["investment_date__gte"] = start_date
        if end_date:
            investment_filters["investment_date__lte"] = end_date
        
        investments = await investment_value_crud.get_multi(filters=investment_filters)
        
        if not investments:
            return {"message": "没有找到相关的投资数据"}
        
        # 获取价值数据
        value_filters = {}
        if start_date:
            value_filters["created_at__gte"] = start_date
        if end_date:
            value_filters["created_at__lte"] = end_date
        
        values = await value_delivery_crud.get_multi(filters=value_filters)
        
        # 转换为DataFrame进行分析
        investment_data = pd.DataFrame([investment.dict() for investment in investments])
        value_data = pd.DataFrame([value.dict() for value in values])
        
        # 执行分析
        analyzer = BusinessModelAnalyzer()
        results = analyzer.analyze_incremental_value(investment_data, value_data)
        
        return results
        
    except Exception as e:
        logger.error(f"价值增量分析失败: {e}")
        raise HTTPException(status_code=500, detail="价值增量分析失败")

@router.get("/analysis/dashboard")
async def get_business_model_dashboard(
    current_user: User = Depends(get_current_user)
):
    """获取商业模式仪表盘数据"""
    try:
        # 获取关键指标
        dashboard_data = {
            "value_propositions": {
                "total_count": await value_proposition_crud.count(),
                "active_count": await value_proposition_crud.count(filters={"status": "active"})
            },
            "customer_cognitions": {
                "total_count": await customer_cognition_crud.count(),
                "high_awareness_count": await customer_cognition_crud.count(
                    filters={"awareness_level__gte": 4.0}
                )
            },
            "resource_capabilities": {
                "total_count": await resource_capability_crud.count(),
                "high_efficiency_count": await resource_capability_crud.count(
                    filters={"efficiency_score__gte": 4.0}
                )
            },
            "investments": {
                "total_count": await investment_value_crud.count(),
                "total_amount": await _get_total_investment_amount(),
                "average_roi": await _get_average_roi()
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"获取商业模式仪表盘数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取商业模式仪表盘数据失败")

async def _get_analysis_data(request: BusinessModelAnalysisRequest) -> Dict[str, pd.DataFrame]:
    """获取分析所需的数据"""
    data = {}
    
    # 获取客户数据
    if request.include_customers:
        customers = await customer_cognition_crud.get_multi()
        data["customers"] = pd.DataFrame([c.dict() for c in customers])
    
    # 获取产品数据
    if request.include_products:
        products = await product_value_alignment_crud.get_multi()
        data["products"] = pd.DataFrame([p.dict() for p in products])
    
    # 获取资源能力数据
    if request.include_resources:
        resources = await resource_capability_crud.get_multi()
        data["resources"] = pd.DataFrame([r.dict() for r in resources])
    
    # 获取投资数据
    if request.include_investments:
        investments = await investment_value_crud.get_multi()
        data["investments"] = pd.DataFrame([i.dict() for i in investments])
    
    return data

def _extract_key_insights(results: Dict[str, Any]) -> str:
    """提取关键洞察"""
    insights = []
    
    # 从分析结果中提取关键洞察
    if "value_proposition_cognition" in results:
        vp_cognition = results["value_proposition_cognition"]
        if "awareness_distribution" in vp_cognition:
            high_awareness = vp_cognition["awareness_distribution"].get("high_awareness", 0)
            insights.append(f"高认知度客户占比: {high_awareness:.1%}")
    
    if "customer_acceptance" in results:
        acceptance = results["customer_acceptance"]
        if "acceptance_metrics" in acceptance:
            overall_rate = acceptance["acceptance_metrics"].get("overall_acceptance_rate", 0)
            insights.append(f"整体接纳率: {overall_rate:.1%}")
    
    return "; ".join(insights) if insights else "暂无关键洞察"

def _generate_recommendations(results: Dict[str, Any]) -> str:
    """生成建议"""
    recommendations = []
    
    # 基于分析结果生成建议
    if "value_proposition_cognition" in results:
        recommendations.append("建议加强价值主张的传播和认知建设")
    
    if "customer_acceptance" in results:
        recommendations.append("建议优化客户接纳流程，减少接纳障碍")
    
    if "incremental_value" in results:
        recommendations.append("建议优化投资组合，提升价值增量")
    
    return "; ".join(recommendations) if recommendations else "暂无具体建议"

async def _get_total_investment_amount() -> float:
    """获取总投资金额"""
    try:
        investments = await investment_value_crud.get_multi()
        return sum(investment.investment_amount for investment in investments)
    except:
        return 0.0

async def _get_average_roi() -> float:
    """获取平均ROI"""
    try:
        investments = await investment_value_crud.get_multi()
        if not investments:
            return 0.0
        return sum(investment.roi for investment in investments) / len(investments)
    except:
        return 0.0


