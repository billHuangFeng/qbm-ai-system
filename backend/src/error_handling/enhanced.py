"""
BMOS系统 - 改进的异常处理系统
提供更精确的异常类型和处理机制
"""

from typing import Any, Dict, Optional, Union
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BMOSBaseException(Exception):
    """BMOS基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.severity = severity
        self.details = details or {}
        self.context = context or {}
        self.timestamp = datetime.now()
        self._log_error()
    
    def _log_error(self):
        """记录错误日志"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(self.severity, logging.ERROR)
        
        logger.log(
            log_level,
            f"BMOS Error [{self.code}]: {self.message}",
            extra={
                "error_code": self.code,
                "severity": self.severity.value,
                "details": self.details,
                "context": self.context
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

# 特定异常类型
class BMOSValidationError(BMOSBaseException):
    """验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            details={"field": field} if field else {},
            **kwargs
        )

class BMOSDatabaseError(BMOSBaseException):
    """数据库错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            severity=ErrorSeverity.HIGH,
            details={"operation": operation} if operation else {},
            **kwargs
        )

class BMOSBusinessError(BMOSBaseException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, business_rule: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="BUSINESS_ERROR",
            severity=ErrorSeverity.MEDIUM,
            details={"business_rule": business_rule} if business_rule else {},
            **kwargs
        )

class BMOSAuthenticationError(BMOSBaseException):
    """认证错误"""
    
    def __init__(self, message: str, auth_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            severity=ErrorSeverity.HIGH,
            details={"auth_type": auth_type} if auth_type else {},
            **kwargs
        )

class BMOSAuthorizationError(BMOSBaseException):
    """授权错误"""
    
    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            severity=ErrorSeverity.HIGH,
            details={"resource": resource} if resource else {},
            **kwargs
        )

class BMOSExternalServiceError(BMOSBaseException):
    """外部服务错误"""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            details={"service": service} if service else {},
            **kwargs
        )

class BMOSConfigurationError(BMOSBaseException):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            details={"config_key": config_key} if config_key else {},
            **kwargs
        )

class BMOSResourceError(BMOSBaseException):
    """资源错误"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            code="RESOURCE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            details={"resource_type": resource_type} if resource_type else {},
            **kwargs
        )

# 异常处理装饰器
def handle_exceptions(
    default_error: str = "操作失败",
    log_errors: bool = True,
    reraise: bool = True
):
    """
    异常处理装饰器
    
    Args:
        default_error: 默认错误消息
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BMOSBaseException:
                # BMOS异常直接重新抛出
                raise
            except ValueError as e:
                # 值错误转换为验证错误
                raise BMOSValidationError(f"输入验证失败: {str(e)}")
            except KeyError as e:
                # 键错误转换为资源错误
                raise BMOSResourceError(f"缺少必要参数: {str(e)}")
            except ConnectionError as e:
                # 连接错误转换为外部服务错误
                raise BMOSExternalServiceError(f"服务连接失败: {str(e)}")
            except TimeoutError as e:
                # 超时错误转换为外部服务错误
                raise BMOSExternalServiceError(f"服务超时: {str(e)}")
            except Exception as e:
                # 其他异常转换为业务错误
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise BMOSBusinessError(f"{default_error}: {str(e)}")
                else:
                    return None
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BMOSBaseException:
                # BMOS异常直接重新抛出
                raise
            except ValueError as e:
                # 值错误转换为验证错误
                raise BMOSValidationError(f"输入验证失败: {str(e)}")
            except KeyError as e:
                # 键错误转换为资源错误
                raise BMOSResourceError(f"缺少必要参数: {str(e)}")
            except ConnectionError as e:
                # 连接错误转换为外部服务错误
                raise BMOSExternalServiceError(f"服务连接失败: {str(e)}")
            except TimeoutError as e:
                # 超时错误转换为外部服务错误
                raise BMOSExternalServiceError(f"服务超时: {str(e)}")
            except Exception as e:
                # 其他异常转换为业务错误
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise BMOSBusinessError(f"{default_error}: {str(e)}")
                else:
                    return None
        
        # 根据函数类型返回相应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# 异常映射
EXCEPTION_MAPPING = {
    ValueError: BMOSValidationError,
    KeyError: BMOSResourceError,
    ConnectionError: BMOSExternalServiceError,
    TimeoutError: BMOSExternalServiceError,
    FileNotFoundError: BMOSResourceError,
    PermissionError: BMOSAuthorizationError,
}

def map_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> BMOSBaseException:
    """将标准异常映射为BMOS异常"""
    exception_type = type(exception)
    
    if exception_type in EXCEPTION_MAPPING:
        bmos_exception_class = EXCEPTION_MAPPING[exception_type]
        return bmos_exception_class(
            message=str(exception),
            context=context or {}
        )
    else:
        return BMOSBusinessError(
            message=str(exception),
            context=context or {}
        )

# 错误统计
class ErrorTracker:
    """错误统计跟踪器"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: list = []
    
    def track_error(self, error: BMOSBaseException):
        """跟踪错误"""
        self.error_counts[error.code] = self.error_counts.get(error.code, 0) + 1
        self.error_history.append({
            "timestamp": error.timestamp,
            "code": error.code,
            "severity": error.severity.value,
            "message": error.message
        })
        
        # 保持历史记录在合理范围内
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }

# 全局错误跟踪器
error_tracker = ErrorTracker()

# 增强的异常处理函数
def handle_bmos_exception(error: BMOSBaseException) -> Dict[str, Any]:
    """处理BMOS异常"""
    # 跟踪错误
    error_tracker.track_error(error)
    
    # 返回错误信息
    return {
        "success": False,
        "error": error.to_dict()
    }

def handle_standard_exception(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """处理标准异常"""
    bmos_error = map_exception(error, context)
    return handle_bmos_exception(bmos_error)


