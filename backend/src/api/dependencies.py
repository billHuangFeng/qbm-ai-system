"""
BMOS系统 - 依赖注入配置
作用: 配置FastAPI的依赖注入
状态: ✅ 实施中
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import jwt
import os
from datetime import datetime, timedelta

# 安全配置
security = HTTPBearer()

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(data: Dict[str, Any]) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """获取当前用户信息"""
    token = credentials.credentials
    payload = verify_token(token)

    # 从payload中提取用户信息
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 这里应该从数据库获取用户详细信息
    # 暂时返回模拟数据
    return {
        "user_id": user_id,
        "tenant_id": payload.get("tenant_id", "default_tenant"),
        "role": payload.get("role", "user"),
        "permissions": payload.get("permissions", []),
        "email": payload.get("email", ""),
        "name": payload.get("name", ""),
    }


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取当前管理员用户"""
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return current_user


async def get_current_analyst_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取当前分析师用户"""
    if current_user.get("role") not in ["admin", "super_admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要分析师权限"
        )
    return current_user


# 服务依赖注入
from ..services.model_training_service import ModelTrainingService
from ..services.enterprise_memory_service import EnterpriseMemoryService
from ..services.database_service import DatabaseService
from ..services.cache_service import CacheService

# --- 模拟后端（数据库/缓存）在不可用时的空实现 ---
import asyncio


class MockDatabaseService:
    async def initialize(self):
        return None

    async def close(self):
        return None

    async def execute_query(self, query: str, params: dict | None = None):
        return None

    async def fetch_one(self, query: str, params: dict | None = None):
        return None

    async def fetch_all(self, query: str, params: dict | None = None):
        return []

    async def insert(self, table: str, data: dict):
        return {"id": "mock-id", **data}

    async def update(self, table: str, key: dict, data: dict):
        return {**key, **data}

    async def delete(self, table: str, key: dict):
        return 0


class MockCacheService:
    async def initialize(self):
        return None

    async def close(self):
        return None

    async def get(self, namespace: str, key: str):
        return None

    async def set(
        self, namespace: str, key: str, value, expire_seconds: int | None = None
    ):
        return True

    async def delete(self, namespace: str, key: str):
        return True


# 全局服务实例（在实际应用中应该使用依赖注入容器）
_model_training_service: Optional[ModelTrainingService] = None
_memory_service: Optional[EnterpriseMemoryService] = None
_db_service: Optional[DatabaseService] = None
_cache_service: Optional[CacheService] = None


def get_model_training_service() -> ModelTrainingService:
    """获取模型训练服务"""
    global _model_training_service
    if _model_training_service is None:
        # 无模型训练服务时，不阻塞，返回 503 由端点自行兜底或走模拟分支
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型训练服务未初始化",
        )
    return _model_training_service


def get_memory_service() -> EnterpriseMemoryService:
    """获取企业记忆服务"""
    global _memory_service
    if _memory_service is None:
        # 如果服务未初始化，创建一个临时的服务实例以支持无数据库模式
        db = get_database_service()
        cache = get_cache_service()
        _memory_service = EnterpriseMemoryService(db, cache)
    return _memory_service


def get_database_service() -> DatabaseService:
    """获取数据库服务"""
    global _db_service
    if _db_service is None:
        # 返回模拟数据库服务，支持无数据库模式
        return MockDatabaseService()  # type: ignore[return-value]
    return _db_service


def get_cache_service() -> CacheService:
    """获取缓存服务"""
    global _cache_service
    if _cache_service is None:
        # 返回模拟缓存服务，支持无缓存模式
        return MockCacheService()  # type: ignore[return-value]
    return _cache_service


def set_services(
    model_training_service: Optional[ModelTrainingService],
    memory_service: Optional[EnterpriseMemoryService],
    db_service: Optional[DatabaseService],
    cache_service: Optional[CacheService],
):
    """设置服务实例"""
    global _model_training_service, _memory_service, _db_service, _cache_service

    _model_training_service = model_training_service
    _memory_service = memory_service
    _db_service = db_service
    _cache_service = cache_service


# 租户权限检查
async def check_tenant_access(
    tenant_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> bool:
    """检查租户访问权限"""
    user_tenant_id = current_user.get("tenant_id")
    user_role = current_user.get("role")

    # 超级管理员可以访问所有租户
    if user_role == "super_admin":
        return True

    # 普通用户只能访问自己的租户
    if user_tenant_id == tenant_id:
        return True

    # 检查跨租户访问权限
    if user_role in ["admin", "analyst"]:
        # 这里应该检查跨租户访问表
        # 暂时允许管理员和分析师跨租户访问
        return True

    return False


async def require_tenant_access(tenant_id: str) -> Dict[str, Any]:
    """要求租户访问权限的依赖"""

    async def _check_access(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not await check_tenant_access(tenant_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权限访问租户 {tenant_id}",
            )
        return current_user

    return Depends(_check_access)


# 权限装饰器
def require_permission(permission: str):
    """要求特定权限的装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="需要用户认证"
                )

            user_permissions = current_user.get("permissions", [])
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要权限: {permission}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# 速率限制
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# 简单的内存速率限制器
_rate_limit_storage = defaultdict(list)


async def rate_limit(
    requests_per_minute: int = 60, requests_per_hour: int = 1000
) -> bool:
    """速率限制检查"""
    now = datetime.now()
    user_id = "default"  # 在实际应用中应该从请求中获取用户ID

    # 清理过期记录
    minute_ago = now - timedelta(minutes=1)
    hour_ago = now - timedelta(hours=1)

    _rate_limit_storage[user_id] = [
        req_time for req_time in _rate_limit_storage[user_id] if req_time > hour_ago
    ]

    # 检查分钟限制
    minute_requests = [
        req_time for req_time in _rate_limit_storage[user_id] if req_time > minute_ago
    ]

    if len(minute_requests) >= requests_per_minute:
        return False

    # 检查小时限制
    if len(_rate_limit_storage[user_id]) >= requests_per_hour:
        return False

    # 记录当前请求
    _rate_limit_storage[user_id].append(now)
    return True


async def check_rate_limit(
    requests_per_minute: int = 60, requests_per_hour: int = 1000
) -> None:
    """速率限制检查依赖"""
    if not await rate_limit(requests_per_minute, requests_per_hour):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )


# 请求日志记录
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def log_request(
    request: Request, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """记录请求日志"""
    logger.info(
        f"API请求: {request.method} {request.url.path} "
        f"用户: {current_user.get('user_id')} "
        f"租户: {current_user.get('tenant_id')} "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    return current_user


# 健康检查依赖
async def check_service_health() -> Dict[str, Any]:
    """检查服务健康状态"""
    health_status = {
        "database": "unknown",
        "cache": "unknown",
        "model_training": "unknown",
        "memory_service": "unknown",
    }

    try:
        # 检查数据库
        db_service = get_database_service()
        await db_service.execute_query("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"

    try:
        # 检查缓存
        cache_service = get_cache_service()
        await cache_service.get("health_check", "test")
        health_status["cache"] = "healthy"
    except Exception as e:
        health_status["cache"] = f"unhealthy: {str(e)}"

    try:
        # 检查模型训练服务
        model_service = get_model_training_service()
        health_status["model_training"] = "healthy"
    except Exception as e:
        health_status["model_training"] = f"unhealthy: {str(e)}"

    try:
        # 检查企业记忆服务
        memory_service = get_memory_service()
        health_status["memory_service"] = "healthy"
    except Exception as e:
        health_status["memory_service"] = f"unhealthy: {str(e)}"

    return health_status
