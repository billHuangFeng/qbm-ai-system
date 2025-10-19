"""
BMOS系统维度表Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

# 价值主张维度表
class VPTCreate(BaseModel):
    vpt_id: str = Field(..., description="价值主张ID")
    vpt_name: str = Field(..., description="价值主张名称")
    category: Optional[str] = Field(None, description="类别")
    definition: Optional[str] = Field(None, description="定义")
    owner: Optional[str] = Field(None, description="负责人")

class VPTUpdate(BaseModel):
    vpt_name: Optional[str] = None
    category: Optional[str] = None
    definition: Optional[str] = None
    owner: Optional[str] = None

class VPTResponse(BaseModel):
    vpt_id: str
    vpt_name: str
    category: Optional[str]
    definition: Optional[str]
    owner: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True

# 产品特性维度表
class PFTCreate(BaseModel):
    pft_id: str = Field(..., description="产品特性ID")
    pft_name: str = Field(..., description="产品特性名称")
    unit: Optional[str] = Field(None, description="单位")
    module: Optional[str] = Field(None, description="模块")

class PFTUpdate(BaseModel):
    pft_name: Optional[str] = None
    unit: Optional[str] = None
    module: Optional[str] = None

class PFTResponse(BaseModel):
    pft_id: str
    pft_name: str
    unit: Optional[str]
    module: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True

# 活动维度表
class ActivityCreate(BaseModel):
    activity_id: str = Field(..., description="活动ID")
    activity_name: str = Field(..., description="活动名称")
    type: Optional[str] = Field(None, description="类型")
    vpt_list: Optional[List[str]] = Field(None, description="价值主张列表")
    pft_list: Optional[List[str]] = Field(None, description="产品特性列表")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    dept: Optional[str] = Field(None, description="部门")

class ActivityUpdate(BaseModel):
    activity_name: Optional[str] = None
    type: Optional[str] = None
    vpt_list: Optional[List[str]] = None
    pft_list: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    dept: Optional[str] = None

class ActivityResponse(BaseModel):
    activity_id: str
    activity_name: str
    type: Optional[str]
    vpt_list: Optional[List[str]]
    pft_list: Optional[List[str]]
    start_date: Optional[date]
    end_date: Optional[date]
    dept: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True

# 媒体渠道维度表
class MediaChannelCreate(BaseModel):
    media_id: str = Field(..., description="媒体ID")
    media_name: str = Field(..., description="媒体名称")
    type: Optional[str] = Field(None, description="类型")
    vpt_list: Optional[List[str]] = Field(None, description="价值主张列表")
    pft_list: Optional[List[str]] = Field(None, description="产品特性列表")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")

class MediaChannelUpdate(BaseModel):
    media_name: Optional[str] = None
    type: Optional[str] = None
    vpt_list: Optional[List[str]] = None
    pft_list: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class MediaChannelResponse(BaseModel):
    media_id: str
    media_name: str
    type: Optional[str]
    vpt_list: Optional[List[str]]
    pft_list: Optional[List[str]]
    start_date: Optional[date]
    end_date: Optional[date]
    create_time: datetime

    class Config:
        from_attributes = True

# 转化渠道维度表
class ConvChannelCreate(BaseModel):
    conv_id: str = Field(..., description="转化渠道ID")
    conv_name: str = Field(..., description="转化渠道名称")
    platform: Optional[str] = Field(None, description="平台")
    vpt_list: Optional[List[str]] = Field(None, description="价值主张列表")
    pft_list: Optional[List[str]] = Field(None, description="产品特性列表")

class ConvChannelUpdate(BaseModel):
    conv_name: Optional[str] = None
    platform: Optional[str] = None
    vpt_list: Optional[List[str]] = None
    pft_list: Optional[List[str]] = None

class ConvChannelResponse(BaseModel):
    conv_id: str
    conv_name: str
    platform: Optional[str]
    vpt_list: Optional[List[str]]
    pft_list: Optional[List[str]]
    create_time: datetime

    class Config:
        from_attributes = True

# SKU维度表
class SKUCreate(BaseModel):
    sku_id: str = Field(..., description="SKU ID")
    sku_name: str = Field(..., description="SKU名称")
    category: Optional[str] = Field(None, description="类别")
    pft_list: Optional[List[str]] = Field(None, description="产品特性列表")

class SKUUpdate(BaseModel):
    sku_name: Optional[str] = None
    category: Optional[str] = None
    pft_list: Optional[List[str]] = None

class SKUResponse(BaseModel):
    sku_id: str
    sku_name: str
    category: Optional[str]
    pft_list: Optional[List[str]]
    create_time: datetime

    class Config:
        from_attributes = True

# 客户维度表
class CustomerCreate(BaseModel):
    customer_id: str = Field(..., description="客户ID")
    first_media_id: Optional[str] = Field(None, description="首次媒体ID")
    first_conv_id: Optional[str] = Field(None, description="首次转化渠道ID")
    reg_date: Optional[date] = Field(None, description="注册日期")
    customer_segment: Optional[str] = Field(None, description="客户细分")

class CustomerUpdate(BaseModel):
    first_media_id: Optional[str] = None
    first_conv_id: Optional[str] = None
    reg_date: Optional[date] = None
    customer_segment: Optional[str] = None

class CustomerResponse(BaseModel):
    customer_id: str
    first_media_id: Optional[str]
    first_conv_id: Optional[str]
    reg_date: Optional[date]
    customer_segment: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True

# 日期维度表
class DateCreate(BaseModel):
    date_key: date = Field(..., description="日期键")
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    week: int = Field(..., description="周")
    day: int = Field(..., description="日")
    quarter: int = Field(..., description="季度")
    is_weekend: int = Field(..., description="是否周末")

class DateResponse(BaseModel):
    date_key: date
    year: int
    month: int
    week: int
    day: int
    quarter: int
    is_weekend: int

    class Config:
        from_attributes = True

# 供应商维度表
class SupplierCreate(BaseModel):
    supp_id: str = Field(..., description="供应商ID")
    supp_name: str = Field(..., description="供应商名称")
    category: Optional[str] = Field(None, description="类别")

class SupplierUpdate(BaseModel):
    supp_name: Optional[str] = None
    category: Optional[str] = None

class SupplierResponse(BaseModel):
    supp_id: str
    supp_name: str
    category: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True


