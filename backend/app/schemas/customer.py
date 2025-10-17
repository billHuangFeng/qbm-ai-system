"""
客户数据模型
"""
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class CustomerBase(BaseModel):
    """客户基础模型"""
    customer_code: str = Field(..., min_length=1, max_length=50, description="客户编码")
    customer_name: str = Field(..., min_length=1, max_length=200, description="客户名称")
    customer_type: Optional[str] = Field(None, max_length=50, description="客户类型")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    company_size: Optional[str] = Field(None, max_length=50, description="公司规模")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    country: str = Field(default="中国", max_length=50, description="国家")
    postal_code: Optional[str] = Field(None, max_length=20, description="邮政编码")
    status: str = Field(default="active", max_length=20, description="状态")
    is_vip: bool = Field(default=False, description="是否VIP客户")

class CustomerCreate(CustomerBase):
    """创建客户模型"""
    customer_value_score: Optional[Decimal] = Field(None, description="客户价值评分")
    customer_lifetime_value: Optional[Decimal] = Field(None, description="客户生命周期价值")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    customer_retention_rate: Optional[Decimal] = Field(None, description="客户留存率")
    first_contact_date: Optional[datetime] = Field(None, description="首次接触时间")
    last_contact_date: Optional[datetime] = Field(None, description="最后联系时间")

class CustomerUpdate(BaseModel):
    """更新客户模型"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200, description="客户名称")
    customer_type: Optional[str] = Field(None, max_length=50, description="客户类型")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    company_size: Optional[str] = Field(None, max_length=50, description="公司规模")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    country: Optional[str] = Field(None, max_length=50, description="国家")
    postal_code: Optional[str] = Field(None, max_length=20, description="邮政编码")
    customer_value_score: Optional[Decimal] = Field(None, description="客户价值评分")
    customer_lifetime_value: Optional[Decimal] = Field(None, description="客户生命周期价值")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    customer_retention_rate: Optional[Decimal] = Field(None, description="客户留存率")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    is_vip: Optional[bool] = Field(None, description="是否VIP客户")
    first_contact_date: Optional[datetime] = Field(None, description="首次接触时间")
    last_contact_date: Optional[datetime] = Field(None, description="最后联系时间")

class CustomerInDB(CustomerBase):
    """数据库中的客户模型"""
    id: int
    customer_value_score: Optional[Decimal] = None
    customer_lifetime_value: Optional[Decimal] = None
    customer_satisfaction: Optional[Decimal] = None
    customer_retention_rate: Optional[Decimal] = None
    first_contact_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Customer(CustomerBase):
    """客户响应模型"""
    id: int
    customer_value_score: Optional[Decimal] = None
    customer_lifetime_value: Optional[Decimal] = None
    customer_satisfaction: Optional[Decimal] = None
    customer_retention_rate: Optional[Decimal] = None
    first_contact_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerStats(BaseModel):
    """客户统计信息"""
    total_customers: int
    active_customers: int
    vip_customers: int
    average_value_score: Optional[Decimal] = None
    average_lifetime_value: Optional[Decimal] = None
    average_satisfaction: Optional[Decimal] = None
    average_retention_rate: Optional[Decimal] = None
