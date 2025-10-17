"""
用户数据模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    is_active: bool = Field(default=True, description="是否激活")
    is_admin: bool = Field(default=False, description="是否管理员")

class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")

class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_admin: Optional[bool] = Field(None, description="是否管理员")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")

class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    password_hash: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    """用户响应模型"""
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class UserChangePassword(BaseModel):
    """修改密码模型"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
