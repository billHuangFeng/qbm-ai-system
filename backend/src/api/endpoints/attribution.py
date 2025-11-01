"""
Shapley归因API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging

from ...services.attribution_service import ShapleyAttributionService
from ...services.database_service import DatabaseService
from ..dependencies import get_database_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/attribution", tags=["归因分析"])


# Pydantic 模型
class Touchpoint(BaseModel):
    """触点模型"""
    id: str = Field(..., description="触点ID")
    type: str = Field(..., description="触点类型（media/channel/campaign等）")
    timestamp: str = Field(..., description="时间戳")
    cost: Optional[float] = Field(None, description="成本")
    quality_score: Optional[float] = Field(None, description="质量分数")


class ShapleyAttributionRequest(BaseModel):
    """Shapley归因请求"""
    order_id: str = Field(..., description="订单ID")
    touchpoints: List[Touchpoint] = Field(..., description="触点列表")
    conversion_value: float = Field(..., description="转化金额")
    method: Optional[str] = Field("monte_carlo", description="计算方法（exact/monte_carlo）")


class ShapleyAttributionResponse(BaseModel):
    """Shapley归因响应"""
    order_id: str
    attribution: Dict[str, float] = Field(..., description="归因权重，格式: {'touchpoint_id': weight}")
    method: str
    touchpoint_count: int


class BatchShapleyAttributionRequest(BaseModel):
    """批量Shapley归因请求"""
    orders: List[Dict] = Field(..., description="订单列表")
    touchpoint_journey: Dict[str, List[Dict]] = Field(..., description="触点旅程数据")


class BatchShapleyAttributionResponse(BaseModel):
    """批量Shapley归因响应"""
    results: Dict[str, Dict[str, float]] = Field(..., description="批量归因结果")


# 服务依赖
def get_attribution_service() -> ShapleyAttributionService:
    """获取Shapley归因服务"""
    return ShapleyAttributionService(n_samples=10000)


@router.post("/shapley", response_model=ShapleyAttributionResponse)
async def calculate_shapley_attribution(
    request: ShapleyAttributionRequest,
    service: ShapleyAttributionService = Depends(get_attribution_service)
):
    """
    计算单个订单的Shapley归因
    
    使用Shapley值方法计算多触点归因权重。
    对于触点数量 <= 10，使用完全枚举方法；否则使用蒙特卡洛采样。
    """
    try:
        # 转换触点数据格式
        touchpoints = [
            {
                'id': tp.id,
                'type': tp.type,
                'timestamp': tp.timestamp,
                'cost': tp.cost or 0.0,
                'quality_score': tp.quality_score
            }
            for tp in request.touchpoints
        ]
        
        # 计算Shapley归因
        attribution = service.calculate_shapley_attribution(
            touchpoints=touchpoints,
            conversion_value=request.conversion_value,
            method=request.method or "monte_carlo"
        )
        
        # 可选：保存到数据库
        # await save_attribution_to_db(request.order_id, attribution, db_service)
        
        return ShapleyAttributionResponse(
            order_id=request.order_id,
            attribution=attribution,
            method=request.method or "monte_carlo",
            touchpoint_count=len(touchpoints)
        )
        
    except Exception as e:
        logger.error(f"计算Shapley归因失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算归因失败: {str(e)}")


@router.post("/shapley/batch", response_model=BatchShapleyAttributionResponse)
async def batch_calculate_shapley_attribution(
    request: BatchShapleyAttributionRequest,
    service: ShapleyAttributionService = Depends(get_attribution_service)
):
    """
    批量计算订单的Shapley归因
    
    适用于需要批量处理多个订单的场景。
    """
    try:
        # 批量计算归因
        results = service.batch_calculate_attribution(
            orders=request.orders,
            touchpoint_journey=request.touchpoint_journey
        )
        
        return BatchShapleyAttributionResponse(results=results)
        
    except Exception as e:
        logger.error(f"批量计算Shapley归因失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量计算归因失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "attribution"}


