"""
认证相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from ...database import get_db
from ...auth import (
    auth_manager, get_current_user, create_user_token, 
    refresh_access_token, User, UserRole
)

router = APIRouter()

# 请求模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    tenant_id: str
    status: str

    class Config:
        from_attributes = True

# 注册端点
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在"
        )
    
    # 创建新用户
    hashed_password = auth_manager.get_password_hash(user_data.password)
    new_user = User(
        tenant_id="tenant_001",  # 默认租户，实际应用中应该从请求中获取
        user_id=f"user_{len(db.query(User).all()) + 1}",
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        created_by="system"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        tenant_id=new_user.tenant_id,
        status=new_user.status
    )

# 登录端点
@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = auth_manager.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已被禁用"
        )
    
    # 创建令牌
    tokens = create_user_token(user)
    return TokenResponse(**tokens)

# 刷新令牌端点
@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """刷新访问令牌"""
    try:
        new_access_token = refresh_access_token(refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
        status=current_user.status
    )

# 修改密码端点
@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not auth_manager.verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.password_hash = auth_manager.get_password_hash(new_password)
    db.commit()
    
    return {"message": "密码修改成功"}

# 登出端点
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，这里应该将令牌加入黑名单
    return {"message": "登出成功"}

# 获取用户权限
@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user)
):
    """获取用户权限"""
    permissions = auth_manager.get_user_permissions(current_user)
    return {
        "permissions": permissions,
        "role": current_user.role
    }


