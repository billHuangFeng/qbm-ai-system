"""
认证相关API端点
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....database import get_db
from ....crud import user
from ....schemas import Token, UserLogin, User, UserCreate
from ....core.config import settings
from ....core.security import create_access_token, verify_password, get_password_hash

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用户登录获取访问令牌
    """
    # 验证用户凭据
    user_obj = user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active(user_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_obj.username, "user_id": user_obj.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    用户注册
    """
    # 检查用户名是否已存在
    user_obj = user.get_by_username(db, username=user_in.username)
    if user_obj:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    user_obj = user.get_by_email(db, email=user_in.email)
    if user_obj:
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )
    
    # 创建新用户
    user_obj = user.create(db, obj_in=user_in)
    return user_obj

@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前用户信息
    """
    return current_user

@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    password_data: dict
) -> Any:
    """
    修改密码
    """
    # 验证当前密码
    if not verify_password(password_data["current_password"], current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="当前密码错误"
        )
    
    # 更新密码
    user.update(
        db, 
        db_obj=current_user, 
        obj_in={"password": password_data["new_password"]}
    )
    
    return {"message": "密码修改成功"}

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_obj = user.get(db, id=user_id)
    if user_obj is None:
        raise credentials_exception
    return user_obj

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户
    """
    if not user.is_active(current_user):
        raise HTTPException(status_code=400, detail="用户账户已被禁用")
    return current_user

def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员用户
    """
    if not user.is_admin(current_user):
        raise HTTPException(
            status_code=400, 
            detail="权限不足，需要管理员权限"
        )
    return current_user
