"""
分析结果API端点
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....database import get_db
from .auth import get_current_active_user
from ....services.ai_analysis_service import AIAnalysisService

router = APIRouter()
ai_analysis_service = AIAnalysisService()

class AnalysisRequest(BaseModel):
    data: List[Dict[str, Any]]

class ComprehensiveAnalysisRequest(BaseModel):
    customers: List[Dict[str, Any]] = []
    products: List[Dict[str, Any]] = []
    financials: List[Dict[str, Any]] = []
    market: List[Dict[str, Any]] = []
    text_data: List[Dict[str, Any]] = []

@router.post("/customers")
async def analyze_customers(
    request: AnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析客户数据
    """
    try:
        result = await ai_analysis_service.analyze_customers(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
async def analyze_products(
    request: AnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析产品数据
    """
    try:
        result = await ai_analysis_service.analyze_products(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/financials")
async def analyze_financials(
    request: AnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析财务数据
    """
    try:
        result = await ai_analysis_service.analyze_financials(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/market")
async def analyze_market(
    request: AnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析市场数据
    """
    try:
        result = await ai_analysis_service.analyze_market(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment")
async def analyze_sentiment(
    request: AnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析文本情感
    """
    try:
        result = await ai_analysis_service.analyze_text_sentiment(request.data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions")
async def predict_business_metrics(
    request: ComprehensiveAnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    预测业务指标
    """
    try:
        data = {
            'customers': request.customers,
            'products': request.products,
            'financials': request.financials,
            'market': request.market
        }
        result = await ai_analysis_service.predict_business_metrics(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comprehensive")
async def generate_comprehensive_report(
    request: ComprehensiveAnalysisRequest,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    生成综合分析报告
    """
    try:
        all_data = {
            'customers': request.customers,
            'products': request.products,
            'financials': request.financials,
            'market': request.market,
            'text_data': request.text_data
        }
        result = await ai_analysis_service.generate_comprehensive_report(all_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def read_analysis_results(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    获取分析结果列表
    """
    return {"message": "AI分析功能已实现，请使用相应的分析端点"}
