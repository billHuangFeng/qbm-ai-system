"""
BMOS系统 - 安全认证服务
提供安全的用户认证和授权功能
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from passlib.context import CryptContext
import logging

from ..security.config import security_settings, validate_password_strength
from ..security.database import SecureDatabaseService
from ..exceptions import AuthenticationError, AuthorizationError, ValidationError

logger = logging.getLogger(__name__)


class SecureAuthService:
    """安全认证服务"""

    def __init__(self, db_service: SecureDatabaseService):
        self.db_service = db_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.settings = security_settings

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
        tenant_id: str = None,
    ) -> Dict[str, Any]:
        """安全用户注册"""

        # 验证输入
        await self._validate_registration_input(username, email, password)

        # 检查用户是否已存在
        existing_user = await self.db_service.safe_select(
            "users", ["id"], "username = $1 OR email = $2", [username, email]
        )

        if existing_user:
            raise ValidationError("用户名或邮箱已存在")

        # 验证密码强度
        is_valid, errors = validate_password_strength(password, self.settings)
        if not is_valid:
            raise ValidationError(f"密码不符合要求: {', '.join(errors)}")

        # 加密密码
        password_hash = self._hash_password(password)

        # 创建用户
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "tenant_id": tenant_id,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        try:
            user = await self.db_service.safe_insert("users", user_data)

            # 生成令牌
            token = await self._generate_access_token(user)
            refresh_token = await self._generate_refresh_token(user)

            logger.info(f"用户注册成功: {username}")

            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "tenant_id": user["tenant_id"],
                    "is_active": user["is_active"],
                    "is_verified": user["is_verified"],
                },
                "token": token,
                "refresh_token": refresh_token,
                "expires_in": self.settings.jwt_access_token_expire_minutes * 60,
            }

        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            raise AuthenticationError(f"用户注册失败: {e}")

    async def authenticate_user(
        self, username: str, password: str, tenant_id: str = None
    ) -> Dict[str, Any]:
        """安全用户认证"""

        # 获取用户
        users = await self.db_service.safe_select(
            "users", ["*"], "username = $1 AND is_active = true", [username]
        )

        if not users:
            raise AuthenticationError("用户名或密码错误")

        user = users[0]

        # 检查租户
        if tenant_id and user["tenant_id"] != tenant_id:
            raise AuthenticationError("用户不属于指定租户")

        # 验证密码
        if not self._verify_password(password, user["password_hash"]):
            raise AuthenticationError("用户名或密码错误")

        # 更新最后登录时间
        await self.db_service.safe_update(
            "users", {"last_login": datetime.now()}, "id = $1", [user["id"]]
        )

        # 生成令牌
        token = await self._generate_access_token(user)
        refresh_token = await self._generate_refresh_token(user)

        logger.info(f"用户登录成功: {username}")

        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "tenant_id": user["tenant_id"],
                "is_active": user["is_active"],
                "is_verified": user["is_verified"],
            },
            "token": token,
            "refresh_token": refresh_token,
            "expires_in": self.settings.jwt_access_token_expire_minutes * 60,
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新访问令牌"""

        try:
            # 验证刷新令牌
            payload = jwt.decode(
                refresh_token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )

            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("无效的刷新令牌")

            # 获取用户
            users = await self.db_service.safe_select(
                "users", ["*"], "id = $1 AND is_active = true", [user_id]
            )

            if not users:
                raise AuthenticationError("用户不存在或已被禁用")

            user = users[0]

            # 生成新的访问令牌
            token = await self._generate_access_token(user)

            return {
                "success": True,
                "token": token,
                "expires_in": self.settings.jwt_access_token_expire_minutes * 60,
            }

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("刷新令牌已过期")
        except jwt.JWTError:
            raise AuthenticationError("无效的刷新令牌")
        except Exception as e:
            logger.error(f"令牌刷新失败: {e}")
            raise AuthenticationError(f"令牌刷新失败: {e}")

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """验证访问令牌"""

        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )

            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("无效的令牌")

            # 获取用户信息
            users = await self.db_service.safe_select(
                "users", ["*"], "id = $1 AND is_active = true", [user_id]
            )

            if not users:
                raise AuthenticationError("用户不存在或已被禁用")

            user = users[0]

            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "tenant_id": user["tenant_id"],
                    "is_active": user["is_active"],
                    "is_verified": user["is_verified"],
                },
                "payload": payload,
            }

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.JWTError:
            raise AuthenticationError("无效的令牌")
        except Exception as e:
            logger.error(f"令牌验证失败: {e}")
            raise AuthenticationError(f"令牌验证失败: {e}")

    async def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """安全修改密码"""

        # 获取用户
        users = await self.db_service.safe_select(
            "users", ["password_hash"], "id = $1 AND is_active = true", [user_id]
        )

        if not users:
            raise AuthenticationError("用户不存在")

        user = users[0]

        # 验证旧密码
        if not self._verify_password(old_password, user["password_hash"]):
            raise AuthenticationError("旧密码错误")

        # 验证新密码强度
        is_valid, errors = validate_password_strength(new_password, self.settings)
        if not is_valid:
            raise ValidationError(f"新密码不符合要求: {', '.join(errors)}")

        # 加密新密码
        new_password_hash = self._hash_password(new_password)

        # 更新密码
        await self.db_service.safe_update(
            "users",
            {"password_hash": new_password_hash, "updated_at": datetime.now()},
            "id = $1",
            [user_id],
        )

        logger.info(f"用户密码修改成功: {user_id}")
        return True

    async def logout_user(self, user_id: str, token: str) -> bool:
        """用户登出"""

        # 将令牌加入黑名单（可选）
        # 这里可以实现令牌黑名单机制

        logger.info(f"用户登出: {user_id}")
        return True

    def _hash_password(self, password: str) -> str:
        """加密密码"""
        return self.pwd_context.hash(password)

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(password, hashed_password)

    async def _generate_access_token(self, user: Dict[str, Any]) -> str:
        """生成访问令牌"""
        expire = datetime.utcnow() + timedelta(
            minutes=self.settings.jwt_access_token_expire_minutes
        )

        payload = {
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        return jwt.encode(
            payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm
        )

    async def _generate_refresh_token(self, user: Dict[str, Any]) -> str:
        """生成刷新令牌"""
        expire = datetime.utcnow() + timedelta(
            days=self.settings.jwt_refresh_token_expire_days
        )

        payload = {
            "sub": str(user["id"]),
            "username": user["username"],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        return jwt.encode(
            payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm
        )

    async def _validate_registration_input(
        self, username: str, email: str, password: str
    ):
        """验证注册输入"""

        if not username or len(username) < 3:
            raise ValidationError("用户名至少需要3个字符")

        if not email or "@" not in email:
            raise ValidationError("邮箱格式不正确")

        if not password:
            raise ValidationError("密码不能为空")

        # 检查用户名是否包含特殊字符
        if any(char in username for char in [" ", "@", "#", "$", "%", "^", "&", "*"]):
            raise ValidationError("用户名不能包含特殊字符")


# 权限检查装饰器
def require_permission(permission: str):
    """权限检查装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以实现权限检查逻辑
            # 从JWT令牌中获取用户权限
            # 检查用户是否有指定权限
            pass

        return wrapper

    return decorator


# 角色检查装饰器
def require_role(role: str):
    """角色检查装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以实现角色检查逻辑
            pass

        return wrapper

    return decorator
