"""
数据管理相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from ...database import get_db
from ...auth import get_current_user, require_permission, Permission, User
from ...models import HistoricalData

router = APIRouter()

# 请求模型
class HistoricalDataCreate(BaseModel):
    data_type: str
    data_date: datetime
    period_type: str
    rd_asset: Optional[float] = None
    design_asset: Optional[float] = None
    production_asset: Optional[float] = None
    marketing_asset: Optional[float] = None
    delivery_asset: Optional[float] = None
    channel_asset: Optional[float] = None
    rd_capability: Optional[float] = None
    design_capability: Optional[float] = None
    production_capability: Optional[float] = None
    marketing_capability: Optional[float] = None
    delivery_capability: Optional[float] = None
    channel_capability: Optional[float] = None
    product_intrinsic_value: Optional[float] = None
    customer_cognitive_value: Optional[float] = None
    customer_experiential_value: Optional[float] = None
    product_feature_valuation: Optional[float] = None
    product_cost_advantage: Optional[float] = None
    first_order_revenue: Optional[float] = None
    repurchase_revenue: Optional[float] = None
    upsell_revenue: Optional[float] = None
    total_revenue: Optional[float] = None
    profit: Optional[float] = None
    product_efficiency: Optional[float] = None
    production_efficiency: Optional[float] = None
    rd_efficiency: Optional[float] = None
    marketing_efficiency: Optional[float] = None
    delivery_efficiency: Optional[float] = None
    channel_efficiency: Optional[float] = None
    data_source: Optional[str] = None
    raw_data: Optional[dict] = None
    metadata: Optional[dict] = None

class HistoricalDataUpdate(BaseModel):
    rd_asset: Optional[float] = None
    design_asset: Optional[float] = None
    production_asset: Optional[float] = None
    marketing_asset: Optional[float] = None
    delivery_asset: Optional[float] = None
    channel_asset: Optional[float] = None
    rd_capability: Optional[float] = None
    design_capability: Optional[float] = None
    production_capability: Optional[float] = None
    marketing_capability: Optional[float] = None
    delivery_capability: Optional[float] = None
    channel_capability: Optional[float] = None
    product_intrinsic_value: Optional[float] = None
    customer_cognitive_value: Optional[float] = None
    customer_experiential_value: Optional[float] = None
    product_feature_valuation: Optional[float] = None
    product_cost_advantage: Optional[float] = None
    first_order_revenue: Optional[float] = None
    repurchase_revenue: Optional[float] = None
    upsell_revenue: Optional[float] = None
    total_revenue: Optional[float] = None
    profit: Optional[float] = None
    product_efficiency: Optional[float] = None
    production_efficiency: Optional[float] = None
    rd_efficiency: Optional[float] = None
    marketing_efficiency: Optional[float] = None
    delivery_efficiency: Optional[float] = None
    channel_efficiency: Optional[float] = None
    data_source: Optional[str] = None
    raw_data: Optional[dict] = None
    metadata: Optional[dict] = None

class HistoricalDataResponse(BaseModel):
    id: int
    tenant_id: str
    data_id: str
    data_type: str
    data_date: datetime
    period_type: str
    rd_asset: Optional[float]
    design_asset: Optional[float]
    production_asset: Optional[float]
    marketing_asset: Optional[float]
    delivery_asset: Optional[float]
    channel_asset: Optional[float]
    rd_capability: Optional[float]
    design_capability: Optional[float]
    production_capability: Optional[float]
    marketing_capability: Optional[float]
    delivery_capability: Optional[float]
    channel_capability: Optional[float]
    product_intrinsic_value: Optional[float]
    customer_cognitive_value: Optional[float]
    customer_experiential_value: Optional[float]
    product_feature_valuation: Optional[float]
    product_cost_advantage: Optional[float]
    first_order_revenue: Optional[float]
    repurchase_revenue: Optional[float]
    upsell_revenue: Optional[float]
    total_revenue: Optional[float]
    profit: Optional[float]
    product_efficiency: Optional[float]
    production_efficiency: Optional[float]
    rd_efficiency: Optional[float]
    marketing_efficiency: Optional[float]
    delivery_efficiency: Optional[float]
    channel_efficiency: Optional[float]
    data_source: Optional[str]
    data_quality_score: Optional[float]
    raw_data: Optional[dict]
    metadata: Optional[dict]
    is_validated: str
    validation_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 创建历史数据
@router.post("/historical", response_model=HistoricalDataResponse)
async def create_historical_data(
    data: HistoricalDataCreate,
    current_user: User = Depends(require_permission(Permission.WRITE_DATA)),
    db: Session = Depends(get_db)
):
    """创建历史数据"""
    import uuid
    
    # 创建历史数据记录
    historical_data = HistoricalData(
        tenant_id=current_user.tenant_id,
        data_id=str(uuid.uuid4()),
        data_type=data.data_type,
        data_date=data.data_date,
        period_type=data.period_type,
        rd_asset=data.rd_asset,
        design_asset=data.design_asset,
        production_asset=data.production_asset,
        marketing_asset=data.marketing_asset,
        delivery_asset=data.delivery_asset,
        channel_asset=data.channel_asset,
        rd_capability=data.rd_capability,
        design_capability=data.design_capability,
        production_capability=data.production_capability,
        marketing_capability=data.marketing_capability,
        delivery_capability=data.delivery_capability,
        channel_capability=data.channel_capability,
        product_intrinsic_value=data.product_intrinsic_value,
        customer_cognitive_value=data.customer_cognitive_value,
        customer_experiential_value=data.customer_experiential_value,
        product_feature_valuation=data.product_feature_valuation,
        product_cost_advantage=data.product_cost_advantage,
        first_order_revenue=data.first_order_revenue,
        repurchase_revenue=data.repurchase_revenue,
        upsell_revenue=data.upsell_revenue,
        total_revenue=data.total_revenue,
        profit=data.profit,
        product_efficiency=data.product_efficiency,
        production_efficiency=data.production_efficiency,
        rd_efficiency=data.rd_efficiency,
        marketing_efficiency=data.marketing_efficiency,
        delivery_efficiency=data.delivery_efficiency,
        channel_efficiency=data.channel_efficiency,
        data_source=data.data_source,
        raw_data=data.raw_data,
        metadata=data.metadata,
        created_by=current_user.user_id
    )
    
    # 验证数据质量
    historical_data.validate_data_quality()
    
    db.add(historical_data)
    db.commit()
    db.refresh(historical_data)
    
    return HistoricalDataResponse.from_orm(historical_data)

# 获取历史数据列表
@router.get("/historical", response_model=List[HistoricalDataResponse])
async def get_historical_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    data_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: Session = Depends(get_db)
):
    """获取历史数据列表"""
    query = db.query(HistoricalData).filter(
        HistoricalData.tenant_id == current_user.tenant_id
    )
    
    if data_type:
        query = query.filter(HistoricalData.data_type == data_type)
    
    if start_date:
        query = query.filter(HistoricalData.data_date >= start_date)
    
    if end_date:
        query = query.filter(HistoricalData.data_date <= end_date)
    
    historical_data = query.offset(skip).limit(limit).all()
    
    return [HistoricalDataResponse.from_orm(data) for data in historical_data]

# 获取单个历史数据
@router.get("/historical/{data_id}", response_model=HistoricalDataResponse)
async def get_historical_data_by_id(
    data_id: str,
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: Session = Depends(get_db)
):
    """获取单个历史数据"""
    historical_data = db.query(HistoricalData).filter(
        HistoricalData.data_id == data_id,
        HistoricalData.tenant_id == current_user.tenant_id
    ).first()
    
    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史数据不存在"
        )
    
    return HistoricalDataResponse.from_orm(historical_data)

# 更新历史数据
@router.put("/historical/{data_id}", response_model=HistoricalDataResponse)
async def update_historical_data(
    data_id: str,
    data: HistoricalDataUpdate,
    current_user: User = Depends(require_permission(Permission.WRITE_DATA)),
    db: Session = Depends(get_db)
):
    """更新历史数据"""
    historical_data = db.query(HistoricalData).filter(
        HistoricalData.data_id == data_id,
        HistoricalData.tenant_id == current_user.tenant_id
    ).first()
    
    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史数据不存在"
        )
    
    # 更新字段
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(historical_data, field, value)
    
    historical_data.updated_by = current_user.user_id
    
    # 重新验证数据质量
    historical_data.validate_data_quality()
    
    db.commit()
    db.refresh(historical_data)
    
    return HistoricalDataResponse.from_orm(historical_data)

# 删除历史数据
@router.delete("/historical/{data_id}")
async def delete_historical_data(
    data_id: str,
    current_user: User = Depends(require_permission(Permission.WRITE_DATA)),
    db: Session = Depends(get_db)
):
    """删除历史数据"""
    historical_data = db.query(HistoricalData).filter(
        HistoricalData.data_id == data_id,
        HistoricalData.tenant_id == current_user.tenant_id
    ).first()
    
    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史数据不存在"
        )
    
    db.delete(historical_data)
    db.commit()
    
    return {"message": "历史数据删除成功"}

# 批量创建历史数据
@router.post("/historical/batch", response_model=List[HistoricalDataResponse])
async def create_historical_data_batch(
    data_list: List[HistoricalDataCreate],
    current_user: User = Depends(require_permission(Permission.WRITE_DATA)),
    db: Session = Depends(get_db)
):
    """批量创建历史数据"""
    import uuid
    
    historical_data_list = []
    for data in data_list:
        historical_data = HistoricalData(
            tenant_id=current_user.tenant_id,
            data_id=str(uuid.uuid4()),
            data_type=data.data_type,
            data_date=data.data_date,
            period_type=data.period_type,
            rd_asset=data.rd_asset,
            design_asset=data.design_asset,
            production_asset=data.production_asset,
            marketing_asset=data.marketing_asset,
            delivery_asset=data.delivery_asset,
            channel_asset=data.channel_asset,
            rd_capability=data.rd_capability,
            design_capability=data.design_capability,
            production_capability=data.production_capability,
            marketing_capability=data.marketing_capability,
            delivery_capability=data.delivery_capability,
            channel_capability=data.channel_capability,
            product_intrinsic_value=data.product_intrinsic_value,
            customer_cognitive_value=data.customer_cognitive_value,
            customer_experiential_value=data.customer_experiential_value,
            product_feature_valuation=data.product_feature_valuation,
            product_cost_advantage=data.product_cost_advantage,
            first_order_revenue=data.first_order_revenue,
            repurchase_revenue=data.repurchase_revenue,
            upsell_revenue=data.upsell_revenue,
            total_revenue=data.total_revenue,
            profit=data.profit,
            product_efficiency=data.product_efficiency,
            production_efficiency=data.production_efficiency,
            rd_efficiency=data.rd_efficiency,
            marketing_efficiency=data.marketing_efficiency,
            delivery_efficiency=data.delivery_efficiency,
            channel_efficiency=data.channel_efficiency,
            data_source=data.data_source,
            raw_data=data.raw_data,
            metadata=data.metadata,
            created_by=current_user.user_id
        )
        
        # 验证数据质量
        historical_data.validate_data_quality()
        historical_data_list.append(historical_data)
    
    db.add_all(historical_data_list)
    db.commit()
    
    return [HistoricalDataResponse.from_orm(data) for data in historical_data_list]

# 数据质量报告
@router.get("/historical/quality-report")
async def get_data_quality_report(
    current_user: User = Depends(require_permission(Permission.READ_DATA)),
    db: Session = Depends(get_db)
):
    """获取数据质量报告"""
    # 获取数据质量统计
    quality_stats = db.query(HistoricalData).filter(
        HistoricalData.tenant_id == current_user.tenant_id
    ).all()
    
    total_records = len(quality_stats)
    if total_records == 0:
        return {
            "total_records": 0,
            "quality_score": 0,
            "quality_distribution": {}
        }
    
    # 计算质量分数分布
    quality_distribution = {}
    total_quality_score = 0
    
    for data in quality_stats:
        quality_score = data.data_quality_score or 0
        total_quality_score += quality_score
        
        if quality_score >= 0.9:
            quality_distribution["excellent"] = quality_distribution.get("excellent", 0) + 1
        elif quality_score >= 0.7:
            quality_distribution["good"] = quality_distribution.get("good", 0) + 1
        elif quality_score >= 0.5:
            quality_distribution["fair"] = quality_distribution.get("fair", 0) + 1
        else:
            quality_distribution["poor"] = quality_distribution.get("poor", 0) + 1
    
    average_quality_score = total_quality_score / total_records
    
    return {
        "total_records": total_records,
        "quality_score": round(average_quality_score, 2),
        "quality_distribution": quality_distribution
    }


