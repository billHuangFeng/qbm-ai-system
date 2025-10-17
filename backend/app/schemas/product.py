"""
产品数据模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    """产品基础模型"""
    product_code: str = Field(..., min_length=1, max_length=50, description="产品编码")
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    product_category: Optional[str] = Field(None, max_length=100, description="产品类别")
    product_type: Optional[str] = Field(None, max_length=50, description="产品类型")
    description: Optional[str] = Field(None, description="产品描述")
    base_price: Optional[Decimal] = Field(None, description="基础价格")
    cost_price: Optional[Decimal] = Field(None, description="成本价格")
    profit_margin: Optional[Decimal] = Field(None, description="利润率")
    pricing_strategy: Optional[str] = Field(None, max_length=100, description="定价策略")
    target_market: Optional[str] = Field(None, max_length=200, description="目标市场")
    market_position: Optional[str] = Field(None, max_length=100, description="市场定位")
    competitive_position: Optional[str] = Field(None, max_length=100, description="竞争地位")
    lifecycle_stage: Optional[str] = Field(None, max_length=50, description="生命周期阶段")
    status: str = Field(default="active", max_length=20, description="状态")
    is_featured: bool = Field(default=False, description="是否推荐产品")

class ProductCreate(ProductBase):
    """创建产品模型"""
    key_features: Optional[List[str]] = Field(None, description="关键特性列表")
    technical_specs: Optional[Dict[str, Any]] = Field(None, description="技术规格")
    competitive_advantages: Optional[str] = Field(None, description="竞争优势")
    launch_date: Optional[datetime] = Field(None, description="上市时间")
    end_of_life_date: Optional[datetime] = Field(None, description="停产时间")
    quality_score: Optional[Decimal] = Field(None, description="质量评分")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    market_share: Optional[Decimal] = Field(None, description="市场份额")
    sales_volume: Optional[int] = Field(None, description="销售数量")
    revenue: Optional[Decimal] = Field(None, description="收入")

class ProductUpdate(BaseModel):
    """更新产品模型"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=200, description="产品名称")
    product_category: Optional[str] = Field(None, max_length=100, description="产品类别")
    product_type: Optional[str] = Field(None, max_length=50, description="产品类型")
    description: Optional[str] = Field(None, description="产品描述")
    key_features: Optional[List[str]] = Field(None, description="关键特性列表")
    technical_specs: Optional[Dict[str, Any]] = Field(None, description="技术规格")
    competitive_advantages: Optional[str] = Field(None, description="竞争优势")
    base_price: Optional[Decimal] = Field(None, description="基础价格")
    cost_price: Optional[Decimal] = Field(None, description="成本价格")
    profit_margin: Optional[Decimal] = Field(None, description="利润率")
    pricing_strategy: Optional[str] = Field(None, max_length=100, description="定价策略")
    target_market: Optional[str] = Field(None, max_length=200, description="目标市场")
    market_position: Optional[str] = Field(None, max_length=100, description="市场定位")
    competitive_position: Optional[str] = Field(None, max_length=100, description="竞争地位")
    lifecycle_stage: Optional[str] = Field(None, max_length=50, description="生命周期阶段")
    launch_date: Optional[datetime] = Field(None, description="上市时间")
    end_of_life_date: Optional[datetime] = Field(None, description="停产时间")
    quality_score: Optional[Decimal] = Field(None, description="质量评分")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    market_share: Optional[Decimal] = Field(None, description="市场份额")
    sales_volume: Optional[int] = Field(None, description="销售数量")
    revenue: Optional[Decimal] = Field(None, description="收入")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    is_featured: Optional[bool] = Field(None, description="是否推荐产品")

class ProductInDB(ProductBase):
    """数据库中的产品模型"""
    id: int
    key_features: Optional[List[str]] = None
    technical_specs: Optional[Dict[str, Any]] = None
    competitive_advantages: Optional[str] = None
    launch_date: Optional[datetime] = None
    end_of_life_date: Optional[datetime] = None
    quality_score: Optional[Decimal] = None
    customer_satisfaction: Optional[Decimal] = None
    market_share: Optional[Decimal] = None
    sales_volume: Optional[int] = None
    revenue: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Product(ProductBase):
    """产品响应模型"""
    id: int
    key_features: Optional[List[str]] = None
    technical_specs: Optional[Dict[str, Any]] = None
    competitive_advantages: Optional[str] = None
    launch_date: Optional[datetime] = None
    end_of_life_date: Optional[datetime] = None
    quality_score: Optional[Decimal] = None
    customer_satisfaction: Optional[Decimal] = None
    market_share: Optional[Decimal] = None
    sales_volume: Optional[int] = None
    revenue: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductStats(BaseModel):
    """产品统计信息"""
    total_products: int
    active_products: int
    featured_products: int
    total_revenue: Optional[Decimal] = None
    total_sales_volume: Optional[int] = None
    average_profit_margin: Optional[Decimal] = None
    average_quality_score: Optional[Decimal] = None
    average_customer_satisfaction: Optional[Decimal] = None
