"""
自定义异常类
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class QBMException(Exception):
    """QBM系统基础异常类"""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(QBMException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": value}
        )

class AuthenticationError(QBMException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(QBMException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR"
        )

class TenantError(QBMException):
    """租户相关异常"""
    
    def __init__(self, message: str, tenant_id: str = None):
        super().__init__(
            message=message,
            code="TENANT_ERROR",
            details={"tenant_id": tenant_id}
        )

class DataQualityError(QBMException):
    """数据质量异常"""
    
    def __init__(self, message: str, quality_score: float = None):
        super().__init__(
            message=message,
            code="DATA_QUALITY_ERROR",
            details={"quality_score": quality_score}
        )

class ModelError(QBMException):
    """模型相关异常"""
    
    def __init__(self, message: str, model_id: str = None):
        super().__init__(
            message=message,
            code="MODEL_ERROR",
            details={"model_id": model_id}
        )

class PredictionError(QBMException):
    """预测相关异常"""
    
    def __init__(self, message: str, prediction_id: str = None):
        super().__init__(
            message=message,
            code="PREDICTION_ERROR",
            details={"prediction_id": prediction_id}
        )

class OptimizationError(QBMException):
    """优化相关异常"""
    
    def __init__(self, message: str, recommendation_id: str = None):
        super().__init__(
            message=message,
            code="OPTIMIZATION_ERROR",
            details={"recommendation_id": recommendation_id}
        )

class DatabaseError(QBMException):
    """数据库异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details={"operation": operation}
        )

class CacheError(QBMException):
    """缓存异常"""
    
    def __init__(self, message: str, key: str = None):
        super().__init__(
            message=message,
            code="CACHE_ERROR",
            details={"key": key}
        )

class ExternalServiceError(QBMException):
    """外部服务异常"""
    
    def __init__(self, message: str, service: str = None):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )

# 异常处理器
def handle_qbm_exception(exc: QBMException) -> HTTPException:
    """处理QBM异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    
    # 根据异常类型设置状态码
    if isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, TenantError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, DataQualityError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, ModelError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, PredictionError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, OptimizationError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, DatabaseError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, CacheError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, ExternalServiceError):
        status_code = status.HTTP_502_BAD_GATEWAY
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

# 异常装饰器
def handle_exceptions(func):
    """异常处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except QBMException as e:
            raise handle_qbm_exception(e)
        except Exception as e:
            # 处理未预期的异常
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "内部服务器错误",
                    "code": "INTERNAL_SERVER_ERROR",
                    "details": {"message": str(e)}
                }
            )
    return wrapper


