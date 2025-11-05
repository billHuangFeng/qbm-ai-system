"""
认证和授权API端点
提供用户注册、登录、权限管理等功能
"""

from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.auth_service import (
    AuthenticationService,
    AuthorizationService,
    UserRole,
    Permission,
    AuthResult,
    PermissionCheck,
)
from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService
from ..dependencies import get_database_service, get_cache_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="", tags=["Authentication & Authorization"])

# 安全方案
security = HTTPBearer()


# Pydantic模型
class UserRegistrationRequest(BaseModel):
    """用户注册请求模型"""

    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码", min_length=8, max_length=100)
    role: UserRole = Field(..., description="用户角色")
    tenant_id: str = Field(..., description="租户ID")


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    tenant_id: Optional[str] = Field(None, description="租户ID")


class TokenRefreshRequest(BaseModel):
    """令牌刷新请求模型"""

    refresh_token: str = Field(..., description="刷新令牌")


class PasswordChangeRequest(BaseModel):
    """密码修改请求模型"""

    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., description="新密码", min_length=8, max_length=100)


class UserUpdateRequest(BaseModel):
    """用户更新请求模型"""

    username: Optional[str] = Field(
        None, description="用户名", min_length=3, max_length=50
    )
    email: Optional[EmailStr] = Field(None, description="邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RoleUpdateRequest(BaseModel):
    """角色更新请求模型"""

    user_id: str = Field(..., description="用户ID")
    new_role: UserRole = Field(..., description="新角色")


class AuthResponse(BaseModel):
    """认证响应模型"""

    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class UserInfoResponse(BaseModel):
    """用户信息响应模型"""

    id: str
    username: str
    email: str
    role: str
    tenant_id: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    permissions: List[str]


class PermissionResponse(BaseModel):
    """权限响应模型"""

    has_permission: bool
    required_permission: str
    user_permissions: List[str]
    reason: Optional[str] = None


# 依赖注入
async def get_auth_service(
    db_service: DatabaseService = Depends(get_database_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> AuthenticationService:
    """获取认证服务实例"""
    secret_key = "your-secret-key"  # 从环境变量获取
    return AuthenticationService(db_service, cache_service, secret_key)


async def get_authz_service(
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> AuthorizationService:
    """获取授权服务实例"""
    return AuthorizationService(auth_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> Dict[str, Any]:
    """获取当前用户"""
    try:
        token = credentials.credentials
        auth_result = await auth_service.verify_token(token)

        if not auth_result.success:
            raise HTTPException(
                status_code=401,
                detail=auth_result.error or "认证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": auth_result.user.id,
            "username": auth_result.user.username,
            "email": auth_result.user.email,
            "role": auth_result.user.role.value,
            "tenant_id": auth_result.user.tenant_id,
            "permissions": [p.value for p in auth_result.user.permissions],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise HTTPException(
            status_code=401, detail="认证失败", headers={"WWW-Authenticate": "Bearer"}
        )


# API端点
@router.post("/register", response_model=AuthResponse)
async def register_user(
    request: UserRegistrationRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    用户注册

    创建新用户账户，支持多租户隔离。
    """
    try:
        # 执行用户注册
        auth_result = await auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role,
            tenant_id=request.tenant_id,
        )

        if not auth_result.success:
            raise HTTPException(status_code=400, detail=auth_result.error)

        # 记录注册日志（后台任务）
        background_tasks.add_task(
            log_user_registration,
            auth_result.user.id,
            request.username,
            request.email,
            request.role.value,
        )

        return AuthResponse(
            success=True,
            message="注册成功",
            user={
                "id": auth_result.user.id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "role": auth_result.user.role.value,
                "tenant_id": auth_result.user.tenant_id,
                "is_active": auth_result.user.is_active,
                "is_verified": auth_result.user.is_verified,
                "created_at": auth_result.user.created_at.isoformat(),
            },
            token=auth_result.token,
            refresh_token=auth_result.refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/login", response_model=AuthResponse)
async def login_user(
    request: UserLoginRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    用户登录

    验证用户凭据并返回访问令牌。
    """
    try:
        # 执行用户认证
        auth_result = await auth_service.authenticate_user(
            username=request.username,
            password=request.password,
            tenant_id=request.tenant_id,
        )

        if not auth_result.success:
            raise HTTPException(
                status_code=401,
                detail=auth_result.error,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 记录登录日志（后台任务）
        background_tasks.add_task(
            log_user_login, auth_result.user.id, request.username, request.tenant_id
        )

        return AuthResponse(
            success=True,
            message="登录成功",
            user={
                "id": auth_result.user.id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "role": auth_result.user.role.value,
                "tenant_id": auth_result.user.tenant_id,
                "is_active": auth_result.user.is_active,
                "is_verified": auth_result.user.is_verified,
                "last_login": (
                    auth_result.user.last_login.isoformat()
                    if auth_result.user.last_login
                    else None
                ),
            },
            token=auth_result.token,
            refresh_token=auth_result.refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    刷新访问令牌

    使用刷新令牌获取新的访问令牌。
    """
    try:
        # 刷新令牌
        auth_result = await auth_service.refresh_token(request.refresh_token)

        if not auth_result.success:
            raise HTTPException(
                status_code=401,
                detail=auth_result.error,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthResponse(
            success=True,
            message="令牌刷新成功",
            user={
                "id": auth_result.user.id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "role": auth_result.user.role.value,
                "tenant_id": auth_result.user.tenant_id,
            },
            token=auth_result.token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"令牌刷新失败: {str(e)}")


@router.post("/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    用户登出

    撤销当前用户的访问令牌。
    """
    try:
        token = credentials.credentials
        success = await auth_service.logout_user(current_user["id"], token)

        if not success:
            raise HTTPException(status_code=500, detail="登出失败")

        return {"success": True, "message": "登出成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    获取当前用户信息

    返回当前认证用户的详细信息。
    """
    try:
        # 获取完整用户信息
        user = await auth_service._get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return UserInfoResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            tenant_id=user.tenant_id,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            permissions=[p.value for p in user.permissions],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.put("/me")
async def update_current_user(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    更新当前用户信息

    更新当前用户的个人信息。
    """
    try:
        # 获取用户
        user = await auth_service._get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新字段
        if request.username is not None:
            user.username = request.username
        if request.email is not None:
            user.email = request.email
        if request.is_active is not None:
            user.is_active = request.is_active

        user.updated_at = datetime.now()

        # 保存更新
        success = await auth_service._update_user(user)
        if not success:
            raise HTTPException(status_code=500, detail="更新用户信息失败")

        return {"success": True, "message": "用户信息更新成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update current user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    修改密码

    修改当前用户的密码。
    """
    try:
        # 获取用户
        user = await auth_service._get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 验证当前密码
        if not auth_service._verify_password(
            request.current_password, user.password_hash
        ):
            raise HTTPException(status_code=400, detail="当前密码错误")

        # 更新密码
        user.password_hash = auth_service._hash_password(request.new_password)
        user.updated_at = datetime.now()

        # 保存更新
        success = await auth_service._update_user(user)
        if not success:
            raise HTTPException(status_code=500, detail="密码修改失败")

        return {"success": True, "message": "密码修改成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"密码修改失败: {str(e)}")


@router.get("/permissions")
async def get_user_permissions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    authz_service: AuthorizationService = Depends(get_authz_service),
):
    """
    获取用户权限列表

    返回当前用户的所有权限。
    """
    try:
        permissions = await authz_service.get_user_permissions(current_user["id"])

        return {
            "success": True,
            "permissions": [p.value for p in permissions],
            "total_count": len(permissions),
        }

    except Exception as e:
        logger.error(f"Failed to get user permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取权限列表失败: {str(e)}")


@router.post("/check-permission", response_model=PermissionResponse)
async def check_permission(
    permission: str,
    resource_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    检查用户权限

    检查当前用户是否具有指定权限。
    """
    try:
        # 解析权限
        try:
            required_permission = Permission(permission)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的权限: {permission}")

        # 检查权限
        permission_check = await auth_service.check_permission(
            current_user["id"], required_permission, resource_id
        )

        return PermissionResponse(
            has_permission=permission_check.has_permission,
            required_permission=permission_check.required_permission.value,
            user_permissions=[p.value for p in permission_check.user_permissions],
            reason=permission_check.reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check permission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"权限检查失败: {str(e)}")


@router.put("/role")
async def update_user_role(
    request: RoleUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    更新用户角色

    更新指定用户的角色（需要管理员权限）。
    """
    try:
        # 检查当前用户是否有权限更新角色
        permission_check = await auth_service.check_permission(
            current_user["id"], Permission.USER_UPDATE
        )

        if not permission_check.has_permission:
            raise HTTPException(status_code=403, detail="没有权限更新用户角色")

        # 更新用户角色
        success = await auth_service.update_user_role(
            request.user_id, request.new_role, current_user["id"]
        )

        if not success:
            raise HTTPException(status_code=500, detail="更新用户角色失败")

        return {
            "success": True,
            "message": f"用户角色已更新为 {request.new_role.value}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新用户角色失败: {str(e)}")


@router.get("/roles")
async def get_available_roles():
    """
    获取可用角色列表

    返回系统中所有可用的用户角色。
    """
    try:
        roles = [
            {
                "value": role.value,
                "name": role.name,
                "description": _get_role_description(role),
            }
            for role in UserRole
        ]

        return {"success": True, "roles": roles, "total_count": len(roles)}

    except Exception as e:
        logger.error(f"Failed to get available roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取角色列表失败: {str(e)}")


@router.get("/permissions")
async def get_available_permissions():
    """
    获取可用权限列表

    返回系统中所有可用的权限。
    """
    try:
        permissions = [
            {
                "value": permission.value,
                "name": permission.name,
                "description": _get_permission_description(permission),
            }
            for permission in Permission
        ]

        return {
            "success": True,
            "permissions": permissions,
            "total_count": len(permissions),
        }

    except Exception as e:
        logger.error(f"Failed to get available permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取权限列表失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    认证服务健康检查
    """
    return {
        "status": "healthy",
        "service": "Authentication & Authorization",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


# 辅助函数
def _get_role_description(role: UserRole) -> str:
    """获取角色描述"""
    descriptions = {
        UserRole.SUPER_ADMIN: "超级管理员，拥有所有权限",
        UserRole.ADMIN: "管理员，拥有大部分管理权限",
        UserRole.ANALYST: "分析师，可以进行数据分析和报告",
        UserRole.VIEWER: "查看者，只能查看数据",
        UserRole.GUEST: "访客，拥有最小权限",
    }
    return descriptions.get(role, "未知角色")


def _get_permission_description(permission: Permission) -> str:
    """获取权限描述"""
    descriptions = {
        Permission.USER_CREATE: "创建用户",
        Permission.USER_READ: "查看用户信息",
        Permission.USER_UPDATE: "更新用户信息",
        Permission.USER_DELETE: "删除用户",
        Permission.DATA_CREATE: "创建数据",
        Permission.DATA_READ: "查看数据",
        Permission.DATA_UPDATE: "更新数据",
        Permission.DATA_DELETE: "删除数据",
        Permission.DATA_IMPORT: "导入数据",
        Permission.DATA_EXPORT: "导出数据",
        Permission.ANALYSIS_CREATE: "创建分析",
        Permission.ANALYSIS_READ: "查看分析",
        Permission.ANALYSIS_UPDATE: "更新分析",
        Permission.ANALYSIS_DELETE: "删除分析",
        Permission.SYSTEM_CONFIG: "系统配置",
        Permission.SYSTEM_MONITOR: "系统监控",
        Permission.SYSTEM_LOG: "查看系统日志",
        Permission.TENANT_CREATE: "创建租户",
        Permission.TENANT_READ: "查看租户信息",
        Permission.TENANT_UPDATE: "更新租户信息",
        Permission.TENANT_DELETE: "删除租户",
    }
    return descriptions.get(permission, "未知权限")


# 后台任务函数
async def log_user_registration(user_id: str, username: str, email: str, role: str):
    """记录用户注册日志"""
    try:
        log_data = {
            "event": "user_registration",
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"User registration logged: {log_data}")

    except Exception as e:
        logger.error(f"Failed to log user registration: {str(e)}")


async def log_user_login(user_id: str, username: str, tenant_id: Optional[str]):
    """记录用户登录日志"""
    try:
        log_data = {
            "event": "user_login",
            "user_id": user_id,
            "username": username,
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"User login logged: {log_data}")

    except Exception as e:
        logger.error(f"Failed to log user login: {str(e)}")


# 错误处理
# @router.exception_handler(HTTPException)  # 注释掉，APIRouter不支持exception_handler
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return {
        "success": False,
        "error_code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.now().isoformat(),
    }


# @router.exception_handler(Exception)  # 注释掉，APIRouter不支持exception_handler
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "success": False,
        "error_code": 500,
        "message": "内部服务器错误",
        "timestamp": datetime.now().isoformat(),
    }
