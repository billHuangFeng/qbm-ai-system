"""
商业模式数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

class ValuePropositionBase(BaseModel):
    """价值主张基础模式"""
    name: str = Field(..., description="价值主张名称")
    description: Optional[str] = Field(None, description="价值主张描述")
    target_customer_segment: Optional[str] = Field(None, description="目标客户群体")
    unique_value: Optional[str] = Field(None, description="独特价值")
    value_drivers: Optional[Dict[str, Any]] = Field(None, description="价值驱动因素")
    
    # 价值主张指标
    awareness_score: Optional[Decimal] = Field(None, description="认知度评分")
    acceptance_rate: Optional[Decimal] = Field(None, description="接纳率")
    experience_quality: Optional[Decimal] = Field(None, description="体验质量")
    conversion_rate: Optional[Decimal] = Field(None, description="转化率")
    retention_rate: Optional[Decimal] = Field(None, description="留存率")
    advocacy_score: Optional[Decimal] = Field(None, description="推荐度")
    
    status: str = Field("active", description="状态")

class ValuePropositionCreate(ValuePropositionBase):
    """创建价值主张模式"""
    pass

class ValuePropositionUpdate(BaseModel):
    """更新价值主张模式"""
    name: Optional[str] = Field(None, description="价值主张名称")
    description: Optional[str] = Field(None, description="价值主张描述")
    target_customer_segment: Optional[str] = Field(None, description="目标客户群体")
    unique_value: Optional[str] = Field(None, description="独特价值")
    value_drivers: Optional[Dict[str, Any]] = Field(None, description="价值驱动因素")
    
    # 价值主张指标
    awareness_score: Optional[Decimal] = Field(None, description="认知度评分")
    acceptance_rate: Optional[Decimal] = Field(None, description="接纳率")
    experience_quality: Optional[Decimal] = Field(None, description="体验质量")
    conversion_rate: Optional[Decimal] = Field(None, description="转化率")
    retention_rate: Optional[Decimal] = Field(None, description="留存率")
    advocacy_score: Optional[Decimal] = Field(None, description="推荐度")
    
    status: Optional[str] = Field(None, description="状态")

class ValuePropositionResponse(ValuePropositionBase):
    """价值主张响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CustomerCognitionBase(BaseModel):
    """客户认知基础模式"""
    customer_id: int = Field(..., description="客户ID")
    value_proposition_id: int = Field(..., description="价值主张ID")
    
    # 认知指标
    awareness_level: Optional[Decimal] = Field(None, description="认知水平")
    awareness_channel: Optional[str] = Field(None, description="认知渠道")
    awareness_date: Optional[datetime] = Field(None, description="认知时间")
    
    # 接纳指标
    acceptance_level: Optional[Decimal] = Field(None, description="接纳水平")
    acceptance_barriers: Optional[Dict[str, Any]] = Field(None, description="接纳障碍")
    acceptance_date: Optional[datetime] = Field(None, description="接纳时间")
    
    # 体验指标
    experience_quality_score: Optional[Decimal] = Field(None, description="体验质量评分")
    experience_touchpoints: Optional[Dict[str, Any]] = Field(None, description="体验触点")
    experience_feedback: Optional[str] = Field(None, description="体验反馈")
    experience_date: Optional[datetime] = Field(None, description="体验时间")
    
    # 价值实现指标
    value_realization_score: Optional[Decimal] = Field(None, description="价值实现评分")
    value_realization_date: Optional[datetime] = Field(None, description="价值实现时间")

class CustomerCognitionCreate(CustomerCognitionBase):
    """创建客户认知模式"""
    pass

class CustomerCognitionUpdate(BaseModel):
    """更新客户认知模式"""
    # 认知指标
    awareness_level: Optional[Decimal] = Field(None, description="认知水平")
    awareness_channel: Optional[str] = Field(None, description="认知渠道")
    awareness_date: Optional[datetime] = Field(None, description="认知时间")
    
    # 接纳指标
    acceptance_level: Optional[Decimal] = Field(None, description="接纳水平")
    acceptance_barriers: Optional[Dict[str, Any]] = Field(None, description="接纳障碍")
    acceptance_date: Optional[datetime] = Field(None, description="接纳时间")
    
    # 体验指标
    experience_quality_score: Optional[Decimal] = Field(None, description="体验质量评分")
    experience_touchpoints: Optional[Dict[str, Any]] = Field(None, description="体验触点")
    experience_feedback: Optional[str] = Field(None, description="体验反馈")
    experience_date: Optional[datetime] = Field(None, description="体验时间")
    
    # 价值实现指标
    value_realization_score: Optional[Decimal] = Field(None, description="价值实现评分")
    value_realization_date: Optional[datetime] = Field(None, description="价值实现时间")

class CustomerCognitionResponse(CustomerCognitionBase):
    """客户认知响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductValueAlignmentBase(BaseModel):
    """产品价值对齐基础模式"""
    product_id: int = Field(..., description="产品ID")
    value_proposition_id: int = Field(..., description="价值主张ID")
    
    # 对齐指标
    alignment_score: Optional[Decimal] = Field(None, description="对齐评分")
    feature_contribution: Optional[Dict[str, Any]] = Field(None, description="特性贡献度")
    value_fulfillment_rate: Optional[Decimal] = Field(None, description="价值实现率")
    
    # 产品特性与价值的关系
    feature_value_mapping: Optional[Dict[str, Any]] = Field(None, description="特性价值映射")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="性能指标")

class ProductValueAlignmentCreate(ProductValueAlignmentBase):
    """创建产品价值对齐模式"""
    pass

class ProductValueAlignmentUpdate(BaseModel):
    """更新产品价值对齐模式"""
    # 对齐指标
    alignment_score: Optional[Decimal] = Field(None, description="对齐评分")
    feature_contribution: Optional[Dict[str, Any]] = Field(None, description="特性贡献度")
    value_fulfillment_rate: Optional[Decimal] = Field(None, description="价值实现率")
    
    # 产品特性与价值的关系
    feature_value_mapping: Optional[Dict[str, Any]] = Field(None, description="特性价值映射")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="性能指标")

class ProductValueAlignmentResponse(ProductValueAlignmentBase):
    """产品价值对齐响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResourceCapabilityBase(BaseModel):
    """资源能力基础模式"""
    name: str = Field(..., description="资源能力名称")
    type: Optional[str] = Field(None, description="类型")
    category: Optional[str] = Field(None, description="类别")
    description: Optional[str] = Field(None, description="描述")
    
    # 资源指标
    current_level: Optional[Decimal] = Field(None, description="当前水平")
    required_level: Optional[Decimal] = Field(None, description="需求水平")
    utilization_rate: Optional[Decimal] = Field(None, description="利用率")
    efficiency_score: Optional[Decimal] = Field(None, description="效率评分")
    
    # 能力指标
    capability_level: Optional[Decimal] = Field(None, description="能力水平")
    capability_gap: Optional[Decimal] = Field(None, description="能力缺口")
    development_potential: Optional[Decimal] = Field(None, description="发展潜力")
    
    # 价值交付指标
    value_delivery_ratio: Optional[Decimal] = Field(None, description="价值交付比率")
    cost_effectiveness: Optional[Decimal] = Field(None, description="成本效益")
    
    status: str = Field("active", description="状态")

class ResourceCapabilityCreate(ResourceCapabilityBase):
    """创建资源能力模式"""
    pass

class ResourceCapabilityUpdate(BaseModel):
    """更新资源能力模式"""
    name: Optional[str] = Field(None, description="资源能力名称")
    type: Optional[str] = Field(None, description="类型")
    category: Optional[str] = Field(None, description="类别")
    description: Optional[str] = Field(None, description="描述")
    
    # 资源指标
    current_level: Optional[Decimal] = Field(None, description="当前水平")
    required_level: Optional[Decimal] = Field(None, description="需求水平")
    utilization_rate: Optional[Decimal] = Field(None, description="利用率")
    efficiency_score: Optional[Decimal] = Field(None, description="效率评分")
    
    # 能力指标
    capability_level: Optional[Decimal] = Field(None, description="能力水平")
    capability_gap: Optional[Decimal] = Field(None, description="能力缺口")
    development_potential: Optional[Decimal] = Field(None, description="发展潜力")
    
    # 价值交付指标
    value_delivery_ratio: Optional[Decimal] = Field(None, description="价值交付比率")
    cost_effectiveness: Optional[Decimal] = Field(None, description="成本效益")
    
    status: Optional[str] = Field(None, description="状态")

class ResourceCapabilityResponse(ResourceCapabilityBase):
    """资源能力响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ValueDeliveryBase(BaseModel):
    """价值交付基础模式"""
    resource_capability_id: int = Field(..., description="资源能力ID")
    customer_id: int = Field(..., description="客户ID")
    
    # 价值交付指标
    value_delivered: Optional[Decimal] = Field(None, description="交付价值")
    delivery_quality: Optional[Decimal] = Field(None, description="交付质量")
    delivery_efficiency: Optional[Decimal] = Field(None, description="交付效率")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    
    # 资源投入指标
    resource_investment: Optional[Decimal] = Field(None, description="资源投入")
    investment_efficiency: Optional[Decimal] = Field(None, description="投资效率")
    roi: Optional[Decimal] = Field(None, description="投资回报率")
    
    delivery_date: Optional[datetime] = Field(None, description="交付时间")

class ValueDeliveryCreate(ValueDeliveryBase):
    """创建价值交付模式"""
    pass

class ValueDeliveryUpdate(BaseModel):
    """更新价值交付模式"""
    # 价值交付指标
    value_delivered: Optional[Decimal] = Field(None, description="交付价值")
    delivery_quality: Optional[Decimal] = Field(None, description="交付质量")
    delivery_efficiency: Optional[Decimal] = Field(None, description="交付效率")
    customer_satisfaction: Optional[Decimal] = Field(None, description="客户满意度")
    
    # 资源投入指标
    resource_investment: Optional[Decimal] = Field(None, description="资源投入")
    investment_efficiency: Optional[Decimal] = Field(None, description="投资效率")
    roi: Optional[Decimal] = Field(None, description="投资回报率")
    
    delivery_date: Optional[datetime] = Field(None, description="交付时间")

class ValueDeliveryResponse(ValueDeliveryBase):
    """价值交付响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvestmentValueBase(BaseModel):
    """投资价值基础模式"""
    investment_category: Optional[str] = Field(None, description="投资类别")
    investment_type: Optional[str] = Field(None, description="投资类型")
    description: Optional[str] = Field(None, description="投资描述")
    
    # 投资指标
    investment_amount: Optional[Decimal] = Field(None, description="投资金额")
    investment_date: Optional[datetime] = Field(None, description="投资时间")
    expected_return: Optional[Decimal] = Field(None, description="预期回报")
    actual_return: Optional[Decimal] = Field(None, description="实际回报")
    
    # 价值增量指标
    value_increase: Optional[Decimal] = Field(None, description="价值增量")
    marginal_investment: Optional[Decimal] = Field(None, description="边际投资")
    marginal_value: Optional[Decimal] = Field(None, description="边际价值")
    
    # ROI指标
    roi: Optional[Decimal] = Field(None, description="投资回报率")
    payback_period: Optional[int] = Field(None, description="回收期(月)")
    npv: Optional[Decimal] = Field(None, description="净现值")

class InvestmentValueCreate(InvestmentValueBase):
    """创建投资价值模式"""
    pass

class InvestmentValueUpdate(BaseModel):
    """更新投资价值模式"""
    investment_category: Optional[str] = Field(None, description="投资类别")
    investment_type: Optional[str] = Field(None, description="投资类型")
    description: Optional[str] = Field(None, description="投资描述")
    
    # 投资指标
    investment_amount: Optional[Decimal] = Field(None, description="投资金额")
    investment_date: Optional[datetime] = Field(None, description="投资时间")
    expected_return: Optional[Decimal] = Field(None, description="预期回报")
    actual_return: Optional[Decimal] = Field(None, description="实际回报")
    
    # 价值增量指标
    value_increase: Optional[Decimal] = Field(None, description="价值增量")
    marginal_investment: Optional[Decimal] = Field(None, description="边际投资")
    marginal_value: Optional[Decimal] = Field(None, description="边际价值")
    
    # ROI指标
    roi: Optional[Decimal] = Field(None, description="投资回报率")
    payback_period: Optional[int] = Field(None, description="回收期(月)")
    npv: Optional[Decimal] = Field(None, description="净现值")

class InvestmentValueResponse(InvestmentValueBase):
    """投资价值响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BusinessModelAnalysisRequest(BaseModel):
    """商业模式分析请求模式"""
    analysis_period: str = Field(..., description="分析周期")
    include_customers: bool = Field(True, description="包含客户数据")
    include_products: bool = Field(True, description="包含产品数据")
    include_resources: bool = Field(True, description="包含资源数据")
    include_investments: bool = Field(True, description="包含投资数据")
    
    # 过滤条件
    customer_filters: Optional[Dict[str, Any]] = Field(None, description="客户过滤条件")
    product_filters: Optional[Dict[str, Any]] = Field(None, description="产品过滤条件")
    resource_filters: Optional[Dict[str, Any]] = Field(None, description="资源过滤条件")
    investment_filters: Optional[Dict[str, Any]] = Field(None, description="投资过滤条件")

class BusinessModelAnalysisResponse(BaseModel):
    """商业模式分析响应模式"""
    analysis_id: int
    analysis_type: str
    analysis_period: str
    results: Dict[str, Any]
    key_insights: str
    recommendations: str
    analysis_date: datetime
    
    class Config:
        from_attributes = True

class BusinessModelDashboardResponse(BaseModel):
    """商业模式仪表盘响应模式"""
    value_propositions: Dict[str, Any]
    customer_cognitions: Dict[str, Any]
    resource_capabilities: Dict[str, Any]
    investments: Dict[str, Any]
    
    class Config:
        from_attributes = True


