"""
认证和授权框架
"""

from __future__ import annotations

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .services.database_service import DatabaseService
from .api.dependencies import get_database_service

# from .models import User  # User模型需要定义或从其他地方导入
from typing import TYPE_CHECKING, Any as _Any

if TYPE_CHECKING:
    from .models import User
else:
    # 供外部导入类型名使用，避免运行时导入循环/缺失
    User = _Any  # type: ignore
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


# 用户角色定义
class UserRole:
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"
    VIEWER = "viewer"


# 权限定义
class Permission:
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    READ_MODELS = "read:models"
    WRITE_MODELS = "write:models"
    READ_PREDICTIONS = "read:predictions"
    WRITE_PREDICTIONS = "write:predictions"
    READ_OPTIMIZATION = "read:optimization"
    WRITE_OPTIMIZATION = "write:optimization"
    MANAGE_USERS = "manage:users"
    MANAGE_TENANTS = "manage:tenants"


# 角色权限映射
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.READ_MODELS,
        Permission.WRITE_MODELS,
        Permission.READ_PREDICTIONS,
        Permission.WRITE_PREDICTIONS,
        Permission.READ_OPTIMIZATION,
        Permission.WRITE_OPTIMIZATION,
        Permission.MANAGE_USERS,
        Permission.MANAGE_TENANTS,
    ],
    UserRole.ANALYST: [
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.READ_MODELS,
        Permission.WRITE_MODELS,
        Permission.READ_PREDICTIONS,
        Permission.WRITE_PREDICTIONS,
        Permission.READ_OPTIMIZATION,
        Permission.WRITE_OPTIMIZATION,
    ],
    UserRole.USER: [
        Permission.READ_DATA,
        Permission.READ_MODELS,
        Permission.READ_PREDICTIONS,
        Permission.READ_OPTIMIZATION,
    ],
    UserRole.VIEWER: [
        Permission.READ_DATA,
        Permission.READ_MODELS,
        Permission.READ_PREDICTIONS,
        Permission.READ_OPTIMIZATION,
    ],
}


class AuthManager:
    """认证管理器"""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的Token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """认证用户"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def get_user_permissions(self, user: User) -> list:
        """获取用户权限"""
        return ROLE_PERMISSIONS.get(user.role, [])

    def has_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有特定权限"""
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions


# 全局认证管理器实例
auth_manager = AuthManager()


# 依赖注入函数
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DatabaseService = Depends(get_database_service),
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_tenant(user: User = Depends(get_current_user)) -> str:
    """获取当前租户ID"""
    return user.tenant_id


def require_permission(permission: str):
    """权限装饰器"""

    def permission_checker(user: User = Depends(get_current_user)):
        if not auth_manager.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"缺少权限: {permission}"
            )
        return user

    return permission_checker


def require_role(role: str):
    """角色装饰器"""

    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"需要角色: {role}"
            )
        return user

    return role_checker


# 多租户中间件
class TenantAuthMiddleware:
    """租户认证中间件"""

    @staticmethod
    def validate_tenant_access(user: User, tenant_id: str) -> bool:
        """验证用户是否有访问指定租户的权限"""
        # 管理员可以访问所有租户
        if user.role == UserRole.ADMIN:
            return True

        # 其他用户只能访问自己的租户
        return user.tenant_id == tenant_id

    @staticmethod
    def get_tenant_from_user(user: User) -> str:
        """从用户获取租户ID"""
        return user.tenant_id


# 认证异常
class AuthenticationError(Exception):
    """认证异常"""

    pass


class AuthorizationError(Exception):
    """授权异常"""

    pass


# 用户会话管理
class UserSession:
    """用户会话管理"""

    def __init__(self, user: User, token: str):
        self.user = user
        self.token = token
        self.permissions = auth_manager.get_user_permissions(user)
        self.tenant_id = user.tenant_id

    def has_permission(self, permission: str) -> bool:
        """检查是否有权限"""
        return permission in self.permissions

    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.user.role == UserRole.ADMIN

    def can_access_tenant(self, tenant_id: str) -> bool:
        """是否可以访问指定租户"""
        return TenantAuthMiddleware.validate_tenant_access(self.user, tenant_id)


# 登录和注册相关函数
def create_user_token(user: User) -> Dict[str, str]:
    """创建用户令牌"""
    access_token = auth_manager.create_access_token(
        data={"sub": user.user_id, "tenant_id": user.tenant_id, "role": user.role}
    )
    refresh_token = auth_manager.create_refresh_token(
        data={"sub": user.user_id, "tenant_id": user.tenant_id, "role": user.role}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token: str) -> str:
    """刷新访问令牌"""
    payload = auth_manager.verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )

    return auth_manager.create_access_token(
        data={
            "sub": payload["sub"],
            "tenant_id": payload["tenant_id"],
            "role": payload["role"],
        }
    )
