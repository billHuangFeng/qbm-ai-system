"""
认证和授权系统
实现JWT认证、角色权限管理、多租户隔离等功能
"""

import asyncio
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import uuid

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"      # 超级管理员
    ADMIN = "admin"                  # 管理员
    ANALYST = "analyst"              # 分析师
    VIEWER = "viewer"                # 查看者
    GUEST = "guest"                  # 访客

class Permission(Enum):
    """权限枚举"""
    # 用户管理权限
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 数据管理权限
    DATA_CREATE = "data:create"
    DATA_READ = "data:read"
    DATA_UPDATE = "data:update"
    DATA_DELETE = "data:delete"
    DATA_IMPORT = "data:import"
    DATA_EXPORT = "data:export"
    
    # 分析权限
    ANALYSIS_CREATE = "analysis:create"
    ANALYSIS_READ = "analysis:read"
    ANALYSIS_UPDATE = "analysis:update"
    ANALYSIS_DELETE = "analysis:delete"
    
    # 系统管理权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_LOG = "system:log"
    
    # 租户管理权限
    TENANT_CREATE = "tenant:create"
    TENANT_READ = "tenant:read"
    TENANT_UPDATE = "tenant:update"
    TENANT_DELETE = "tenant:delete"
    
    # 任务管理权限
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_EXECUTE = "task:execute"
    
    # 模型管理权限
    MODEL_CREATE = "model:create"
    MODEL_READ = "model:read"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    MODEL_TRAIN = "model:train"
    MODEL_PREDICT = "model:predict"
    
    # 预测权限
    PREDICTION_CREATE = "prediction:create"
    PREDICTION_READ = "prediction:read"
    PREDICTION_UPDATE = "prediction:update"
    PREDICTION_DELETE = "prediction:delete"
    
    # 企业记忆权限
    MEMORY_CREATE = "memory:create"
    MEMORY_READ = "memory:read"
    MEMORY_UPDATE = "memory:update"
    MEMORY_DELETE = "memory:delete"
    
    # 数据导入权限
    DATA_IMPORT_CREATE = "data_import:create"
    DATA_IMPORT_READ = "data_import:read"
    DATA_IMPORT_UPDATE = "data_import:update"
    DATA_IMPORT_DELETE = "data_import:delete"
    
    # AI助手权限
    AI_COPILOT_CREATE = "ai_copilot:create"
    AI_COPILOT_READ = "ai_copilot:read"
    AI_COPILOT_UPDATE = "ai_copilot:update"
    AI_COPILOT_DELETE = "ai_copilot:delete"

class AuthStatus(Enum):
    """认证状态枚举"""
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class User:
    """用户模型"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    tenant_id: str
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    permissions: List[Permission] = None

@dataclass
class TokenPayload:
    """JWT Token载荷"""
    user_id: str
    username: str
    email: str
    role: str
    tenant_id: str
    permissions: List[str]
    iat: datetime
    exp: datetime
    jti: str  # JWT ID

@dataclass
class AuthResult:
    """认证结果"""
    success: bool
    user: Optional[User] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    error: Optional[str] = None
    status: AuthStatus = AuthStatus.UNAUTHENTICATED

@dataclass
class PermissionCheck:
    """权限检查结果"""
    has_permission: bool
    required_permission: Permission
    user_permissions: List[Permission]
    reason: Optional[str] = None

class AuthenticationService:
    """认证服务"""
    
    def __init__(self, db_service, cache_service, secret_key: str):
        self.db_service = db_service
        self.cache_service = cache_service
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # 密码加密上下文
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # 角色权限映射
        self.role_permissions = self._setup_role_permissions()
    
    def _setup_role_permissions(self) -> Dict[UserRole, List[Permission]]:
        """设置角色权限映射"""
        return {
            UserRole.SUPER_ADMIN: list(Permission),  # 所有权限
            
            UserRole.ADMIN: [
                # 用户管理
                Permission.USER_CREATE, Permission.USER_READ, 
                Permission.USER_UPDATE, Permission.USER_DELETE,
                # 数据管理
                Permission.DATA_CREATE, Permission.DATA_READ,
                Permission.DATA_UPDATE, Permission.DATA_DELETE,
                Permission.DATA_IMPORT, Permission.DATA_EXPORT,
                # 分析权限
                Permission.ANALYSIS_CREATE, Permission.ANALYSIS_READ,
                Permission.ANALYSIS_UPDATE, Permission.ANALYSIS_DELETE,
                # 系统管理
                Permission.SYSTEM_MONITOR, Permission.SYSTEM_LOG,
                # 租户管理
                Permission.TENANT_READ, Permission.TENANT_UPDATE
            ],
            
            UserRole.ANALYST: [
                # 数据管理
                Permission.DATA_READ, Permission.DATA_IMPORT, Permission.DATA_EXPORT,
                # 分析权限
                Permission.ANALYSIS_CREATE, Permission.ANALYSIS_READ,
                Permission.ANALYSIS_UPDATE, Permission.ANALYSIS_DELETE,
                # 系统监控
                Permission.SYSTEM_MONITOR
            ],
            
            UserRole.VIEWER: [
                # 只读权限
                Permission.DATA_READ, Permission.ANALYSIS_READ,
                Permission.SYSTEM_MONITOR
            ],
            
            UserRole.GUEST: [
                # 最小权限
                Permission.DATA_READ
            ]
        }
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole,
        tenant_id: str,
        created_by: Optional[str] = None
    ) -> AuthResult:
        """注册用户"""
        try:
            # 检查用户名是否已存在
            existing_user = await self._get_user_by_username(username)
            if existing_user:
                return AuthResult(
                    success=False,
                    error="用户名已存在",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 检查邮箱是否已存在
            existing_email = await self._get_user_by_email(email)
            if existing_email:
                return AuthResult(
                    success=False,
                    error="邮箱已存在",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 验证租户权限
            if created_by:
                creator = await self._get_user_by_id(created_by)
                if not creator or not self._can_create_user(creator, role, tenant_id):
                    return AuthResult(
                        success=False,
                        error="没有权限创建此角色的用户",
                        status=AuthStatus.UNAUTHENTICATED
                    )
            
            # 创建用户
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                tenant_id=tenant_id,
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                permissions=self.role_permissions.get(role, [])
            )
            
            # 保存用户到数据库
            await self._save_user(user)
            
            # 生成访问令牌
            token = await self._generate_access_token(user)
            refresh_token = await self._generate_refresh_token(user)
            
            return AuthResult(
                success=True,
                user=user,
                token=token,
                refresh_token=refresh_token,
                status=AuthStatus.AUTHENTICATED
            )
            
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return AuthResult(
                success=False,
                error=f"注册失败: {str(e)}",
                status=AuthStatus.UNAUTHENTICATED
            )
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        tenant_id: Optional[str] = None
    ) -> AuthResult:
        """用户认证"""
        try:
            # 获取用户
            user = await self._get_user_by_username(username)
            if not user:
                return AuthResult(
                    success=False,
                    error="用户名或密码错误",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 检查用户状态
            if not user.is_active:
                return AuthResult(
                    success=False,
                    error="用户账户已被禁用",
                    status=AuthStatus.REVOKED
                )
            
            # 检查租户
            if tenant_id and user.tenant_id != tenant_id:
                return AuthResult(
                    success=False,
                    error="用户不属于指定租户",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 验证密码
            if not self._verify_password(password, user.password_hash):
                return AuthResult(
                    success=False,
                    error="用户名或密码错误",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            await self._update_user(user)
            
            # 生成令牌
            token = await self._generate_access_token(user)
            refresh_token = await self._generate_refresh_token(user)
            
            # 缓存用户会话
            await self._cache_user_session(user.id, token)
            
            return AuthResult(
                success=True,
                user=user,
                token=token,
                refresh_token=refresh_token,
                status=AuthStatus.AUTHENTICATED
            )
            
        except Exception as e:
            logger.error(f"User authentication failed: {str(e)}")
            return AuthResult(
                success=False,
                error=f"认证失败: {str(e)}",
                status=AuthStatus.UNAUTHENTICATED
            )
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            payload = self._decode_token(refresh_token)
            if not payload:
                return AuthResult(
                    success=False,
                    error="无效的刷新令牌",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 获取用户
            user = await self._get_user_by_id(payload["user_id"])
            if not user or not user.is_active:
                return AuthResult(
                    success=False,
                    error="用户不存在或已被禁用",
                    status=AuthStatus.REVOKED
                )
            
            # 生成新的访问令牌
            new_token = await self._generate_access_token(user)
            
            return AuthResult(
                success=True,
                user=user,
                token=new_token,
                status=AuthStatus.AUTHENTICATED
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return AuthResult(
                success=False,
                error=f"令牌刷新失败: {str(e)}",
                status=AuthStatus.UNAUTHENTICATED
            )
    
    async def logout_user(self, user_id: str, token: str) -> bool:
        """用户登出"""
        try:
            # 从缓存中移除用户会话
            await self._remove_user_session(user_id, token)
            
            # 将令牌加入黑名单
            await self._blacklist_token(token)
            
            return True
            
        except Exception as e:
            logger.error(f"User logout failed: {str(e)}")
            return False
    
    async def verify_token(self, token: str) -> AuthResult:
        """验证令牌"""
        try:
            # 检查令牌黑名单
            if await self._is_token_blacklisted(token):
                return AuthResult(
                    success=False,
                    error="令牌已被撤销",
                    status=AuthStatus.REVOKED
                )
            
            # 解码令牌
            payload = self._decode_token(token)
            if not payload:
                return AuthResult(
                    success=False,
                    error="无效的令牌",
                    status=AuthStatus.UNAUTHENTICATED
                )
            
            # 检查令牌是否过期
            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                return AuthResult(
                    success=False,
                    error="令牌已过期",
                    status=AuthStatus.EXPIRED
                )
            
            # 获取用户
            user = await self._get_user_by_id(payload["user_id"])
            if not user or not user.is_active:
                return AuthResult(
                    success=False,
                    error="用户不存在或已被禁用",
                    status=AuthStatus.REVOKED
                )
            
            return AuthResult(
                success=True,
                user=user,
                status=AuthStatus.AUTHENTICATED
            )
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return AuthResult(
                success=False,
                error=f"令牌验证失败: {str(e)}",
                status=AuthStatus.UNAUTHENTICATED
            )
    
    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> PermissionCheck:
        """检查用户权限"""
        try:
            # 获取用户
            user = await self._get_user_by_id(user_id)
            if not user or not user.is_active:
                return PermissionCheck(
                    has_permission=False,
                    required_permission=permission,
                    user_permissions=[],
                    reason="用户不存在或已被禁用"
                )
            
            # 获取用户权限
            user_permissions = self.role_permissions.get(user.role, [])
            
            # 检查权限
            has_permission = permission in user_permissions
            
            # 特殊权限检查（如跨租户访问）
            if not has_permission and permission == Permission.DATA_READ:
                has_permission = await self._check_cross_tenant_access(user, resource_id)
            
            return PermissionCheck(
                has_permission=has_permission,
                required_permission=permission,
                user_permissions=user_permissions,
                reason=None if has_permission else "权限不足"
            )
            
        except Exception as e:
            logger.error(f"Permission check failed: {str(e)}")
            return PermissionCheck(
                has_permission=False,
                required_permission=permission,
                user_permissions=[],
                reason=f"权限检查失败: {str(e)}"
            )
    
    async def update_user_role(
        self,
        user_id: str,
        new_role: UserRole,
        updated_by: str
    ) -> bool:
        """更新用户角色"""
        try:
            # 检查更新者权限
            updater = await self._get_user_by_id(updated_by)
            if not updater or not self._can_update_user_role(updater, new_role):
                return False
            
            # 获取用户
            user = await self._get_user_by_id(user_id)
            if not user:
                return False
            
            # 更新角色
            user.role = new_role
            user.permissions = self.role_permissions.get(new_role, [])
            user.updated_at = datetime.now()
            
            # 保存更新
            await self._update_user(user)
            
            # 清除用户会话缓存
            await self._clear_user_sessions(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"User role update failed: {str(e)}")
            return False
    
    # ==================== 私有方法 ====================
    
    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(password, hashed_password)
    
    async def _generate_access_token(self, user: User) -> str:
        """生成访问令牌"""
        now = datetime.now()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            tenant_id=user.tenant_id,
            permissions=[p.value for p in user.permissions],
            iat=now,
            exp=expire,
            jti=str(uuid.uuid4())
        )
        
        token = jwt.encode(
            asdict(payload),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return token
    
    async def _generate_refresh_token(self, user: User) -> str:
        """生成刷新令牌"""
        now = datetime.now()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user.id,
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": str(uuid.uuid4())
        }
        
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return token
    
    def _decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        try:
            # 先从缓存获取
            cached_user = await self.cache_service.get(f"user:{user_id}")
            if cached_user:
                return User(**cached_user)
            
            # 从数据库获取
            query = "SELECT * FROM user_profiles WHERE id = :user_id"
            result = await self.db_service.execute_query(query, {"user_id": user_id})
            
            if result:
                user_data = result[0]
                user = User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=user_data["password_hash"],
                    role=UserRole(user_data["role"]),
                    tenant_id=user_data["tenant_id"],
                    is_active=user_data["is_active"],
                    is_verified=user_data["is_verified"],
                    last_login=user_data.get("last_login"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
                
                # 缓存用户信息
                await self.cache_service.set(
                    f"user:{user_id}",
                    asdict(user),
                    expire=3600  # 1小时
                )
                
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None
    
    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            query = "SELECT * FROM user_profiles WHERE username = :username"
            result = await self.db_service.execute_query(query, {"username": username})
            
            if result:
                user_data = result[0]
                return User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=user_data["password_hash"],
                    role=UserRole(user_data["role"]),
                    tenant_id=user_data["tenant_id"],
                    is_active=user_data["is_active"],
                    is_verified=user_data["is_verified"],
                    last_login=user_data.get("last_login"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by username: {str(e)}")
            return None
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            query = "SELECT * FROM user_profiles WHERE email = :email"
            result = await self.db_service.execute_query(query, {"email": email})
            
            if result:
                user_data = result[0]
                return User(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=user_data["password_hash"],
                    role=UserRole(user_data["role"]),
                    tenant_id=user_data["tenant_id"],
                    is_active=user_data["is_active"],
                    is_verified=user_data["is_verified"],
                    last_login=user_data.get("last_login"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None
    
    async def _save_user(self, user: User) -> bool:
        """保存用户"""
        try:
            query = """
            INSERT INTO user_profiles 
            (id, username, email, password_hash, role, tenant_id, is_active, is_verified, created_at, updated_at)
            VALUES (:id, :username, :email, :password_hash, :role, :tenant_id, :is_active, :is_verified, :created_at, :updated_at)
            """
            
            await self.db_service.execute_query(query, {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "tenant_id": user.tenant_id,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user: {str(e)}")
            return False
    
    async def _update_user(self, user: User) -> bool:
        """更新用户"""
        try:
            query = """
            UPDATE user_profiles 
            SET username = :username, email = :email, password_hash = :password_hash,
                role = :role, tenant_id = :tenant_id, is_active = :is_active,
                is_verified = :is_verified, last_login = :last_login, updated_at = :updated_at
            WHERE id = :id
            """
            
            await self.db_service.execute_query(query, {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "tenant_id": user.tenant_id,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login": user.last_login,
                "updated_at": user.updated_at
            })
            
            # 清除缓存
            await self.cache_service.delete(f"user:{user.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            return False
    
    async def _cache_user_session(self, user_id: str, token: str) -> bool:
        """缓存用户会话"""
        try:
            session_data = {
                "user_id": user_id,
                "token": token,
                "created_at": datetime.now().isoformat()
            }
            
            await self.cache_service.set(
                f"session:{user_id}:{token}",
                session_data,
                expire=self.access_token_expire_minutes * 60
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache user session: {str(e)}")
            return False
    
    async def _remove_user_session(self, user_id: str, token: str) -> bool:
        """移除用户会话"""
        try:
            await self.cache_service.delete(f"session:{user_id}:{token}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove user session: {str(e)}")
            return False
    
    async def _clear_user_sessions(self, user_id: str) -> bool:
        """清除用户所有会话"""
        try:
            # 这里可以实现清除用户所有会话的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear user sessions: {str(e)}")
            return False
    
    async def _blacklist_token(self, token: str) -> bool:
        """将令牌加入黑名单"""
        try:
            payload = self._decode_token(token)
            if payload:
                expire_time = payload.get("exp", 0)
                current_time = datetime.now().timestamp()
                
                if expire_time > current_time:
                    ttl = int(expire_time - current_time)
                    await self.cache_service.set(
                        f"blacklist:{token}",
                        True,
                        expire=ttl
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            return False
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        try:
            blacklisted = await self.cache_service.get(f"blacklist:{token}")
            return blacklisted is not None
            
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {str(e)}")
            return False
    
    def _can_create_user(self, creator: User, target_role: UserRole, tenant_id: str) -> bool:
        """检查是否可以创建用户"""
        # 超级管理员可以创建任何用户
        if creator.role == UserRole.SUPER_ADMIN:
            return True
        
        # 管理员只能创建分析师和查看者
        if creator.role == UserRole.ADMIN:
            return target_role in [UserRole.ANALYST, UserRole.VIEWER, UserRole.GUEST]
        
        # 其他角色不能创建用户
        return False
    
    def _can_update_user_role(self, updater: User, target_role: UserRole) -> bool:
        """检查是否可以更新用户角色"""
        # 超级管理员可以更新任何角色
        if updater.role == UserRole.SUPER_ADMIN:
            return True
        
        # 管理员只能更新为分析师和查看者
        if updater.role == UserRole.ADMIN:
            return target_role in [UserRole.ANALYST, UserRole.VIEWER, UserRole.GUEST]
        
        # 其他角色不能更新用户角色
        return False
    
    async def _check_cross_tenant_access(self, user: User, resource_id: Optional[str]) -> bool:
        """检查跨租户访问权限"""
        try:
            # 检查用户是否有跨租户访问权限
            query = """
            SELECT * FROM cross_tenant_access 
            WHERE user_id = :user_id AND resource_id = :resource_id AND is_active = true
            """
            
            result = await self.db_service.execute_query(query, {
                "user_id": user.id,
                "resource_id": resource_id
            })
            
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Failed to check cross tenant access: {str(e)}")
            return False

class AuthorizationService:
    """授权服务"""
    
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
    
    async def authorize_request(
        self,
        token: str,
        required_permission: Permission,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> bool:
        """授权请求"""
        try:
            # 验证令牌
            auth_result = await self.auth_service.verify_token(token)
            if not auth_result.success:
                return False
            
            user = auth_result.user
            
            # 检查租户隔离
            if tenant_id and user.tenant_id != tenant_id:
                # 检查跨租户访问权限
                if not await self.auth_service._check_cross_tenant_access(user, resource_id):
                    return False
            
            # 检查权限
            permission_check = await self.auth_service.check_permission(
                user.id,
                required_permission,
                resource_id
            )
            
            return permission_check.has_permission
            
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}")
            return False
    
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """获取用户权限列表"""
        try:
            user = await self.auth_service._get_user_by_id(user_id)
            if not user:
                return []
            
            return self.auth_service.role_permissions.get(user.role, [])
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {str(e)}")
            return []
    
    async def check_resource_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> bool:
        """检查资源访问权限"""
        try:
            # 这里可以实现更细粒度的资源访问控制
            # 例如：用户只能访问自己创建的资源，或者有特定标签的资源
            
            user = await self.auth_service._get_user_by_id(user_id)
            if not user:
                return False
            
            # 超级管理员可以访问所有资源
            if user.role == UserRole.SUPER_ADMIN:
                return True
            
            # 管理员可以访问租户内的所有资源
            if user.role == UserRole.ADMIN:
                return True
            
            # 其他角色需要检查具体的资源权限
            # 这里可以实现更复杂的逻辑
            
            return True
            
        except Exception as e:
            logger.error(f"Resource access check failed: {str(e)}")
            return False
