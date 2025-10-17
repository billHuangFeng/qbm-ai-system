"""
通用数据模型
"""
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

class ResponseModel(BaseModel):
    """通用响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$", description="排序方向")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = None

class HealthCheck(BaseModel):
    """健康检查"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
