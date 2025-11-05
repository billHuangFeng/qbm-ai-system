"""
BMOS系统 - 统一错误处理机制
提供标准化的错误处理和响应格式
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict, Optional, Union
import logging
import traceback
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """错误代码枚举"""

    # 通用错误
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"

    # 业务错误
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    DATA_CONFLICT = "DATA_CONFLICT"
    OPERATION_FAILED = "OPERATION_FAILED"

    # 认证授权错误
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"

    # 数据错误
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    DATA_VALIDATION_FAILED = "DATA_VALIDATION_FAILED"
    DATA_CONSTRAINT_VIOLATION = "DATA_CONSTRAINT_VIOLATION"

    # 外部服务错误
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

    # 文件操作错误
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_TYPE_NOT_SUPPORTED = "FILE_TYPE_NOT_SUPPORTED"


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BMOSError(Exception):
    """BMOS系统基础错误类"""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.severity = severity
        self.user_message = user_message or message
        self.timestamp = datetime.now()
        super().__init__(self.message)


class BusinessError(BMOSError):
    """业务逻辑错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_LOGIC_ERROR,
            details=details,
            severity=ErrorSeverity.MEDIUM,
        )


class ValidationError(BMOSError):
    """数据验证错误"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        validation_details = details or {}
        if field:
            validation_details["field"] = field

        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details=validation_details,
            severity=ErrorSeverity.LOW,
        )


class AuthenticationError(BMOSError):
    """认证错误"""

    def __init__(
        self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHENTICATION_FAILED,
            details=details,
            severity=ErrorSeverity.HIGH,
            user_message="用户名或密码错误",
        )


class AuthorizationError(BMOSError):
    """授权错误"""

    def __init__(
        self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHORIZATION_DENIED,
            details=details,
            severity=ErrorSeverity.HIGH,
            user_message="您没有权限执行此操作",
        )


class DatabaseError(BMOSError):
    """数据库错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.DATA_CONSTRAINT_VIOLATION,
            details=details,
            severity=ErrorSeverity.HIGH,
        )


class ExternalServiceError(BMOSError):
    """外部服务错误"""

    def __init__(
        self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        service_details = details or {}
        service_details["service"] = service_name

        super().__init__(
            message=f"外部服务 {service_name} 错误: {message}",
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            details=service_details,
            severity=ErrorSeverity.MEDIUM,
        )


class ErrorResponse:
    """统一错误响应格式"""

    def __init__(
        self,
        error: BMOSError,
        request_id: Optional[str] = None,
        include_debug: bool = False,
    ):
        self.error = error
        self.request_id = request_id
        self.include_debug = include_debug

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        response = {
            "success": False,
            "error": {
                "code": self.error.code.value,
                "message": self.error.user_message,
                "severity": self.error.severity.value,
                "timestamp": self.error.timestamp.isoformat(),
            },
        }

        if self.request_id:
            response["request_id"] = self.request_id

        if self.error.details:
            response["error"]["details"] = self.error.details

        if self.include_debug:
            response["error"]["debug"] = {
                "internal_message": self.error.message,
                "traceback": traceback.format_exc(),
            }

        return response


class ErrorHandler:
    """错误处理器"""

    def __init__(self, include_debug: bool = False):
        self.include_debug = include_debug

    def handle_bmos_error(
        self, error: BMOSError, request_id: Optional[str] = None
    ) -> JSONResponse:
        """处理BMOS错误"""

        # 记录错误日志
        self._log_error(error)

        # 确定HTTP状态码
        status_code = self._get_http_status_code(error.code)

        # 创建错误响应
        error_response = ErrorResponse(error, request_id, self.include_debug)

        return JSONResponse(status_code=status_code, content=error_response.to_dict())

    def handle_validation_error(
        self, error: RequestValidationError, request_id: Optional[str] = None
    ) -> JSONResponse:
        """处理验证错误"""

        # 提取验证错误详情
        validation_details = []
        for err in error.errors():
            validation_details.append(
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )

        bmos_error = ValidationError(
            message="请求数据验证失败",
            details={"validation_errors": validation_details},
        )

        return self.handle_bmos_error(bmos_error, request_id)

    def handle_http_exception(
        self, error: HTTPException, request_id: Optional[str] = None
    ) -> JSONResponse:
        """处理HTTP异常"""

        # 根据状态码确定错误类型
        if error.status_code == status.HTTP_401_UNAUTHORIZED:
            bmos_error = AuthenticationError()
        elif error.status_code == status.HTTP_403_FORBIDDEN:
            bmos_error = AuthorizationError()
        elif error.status_code == status.HTTP_404_NOT_FOUND:
            bmos_error = BMOSError(
                message="资源不存在",
                code=ErrorCode.NOT_FOUND,
                user_message="请求的资源不存在",
            )
        else:
            bmos_error = BMOSError(
                message=str(error.detail), code=ErrorCode.INTERNAL_SERVER_ERROR
            )

        return self.handle_bmos_error(bmos_error, request_id)

    def handle_generic_exception(
        self, error: Exception, request_id: Optional[str] = None
    ) -> JSONResponse:
        """处理通用异常"""

        # 记录错误日志
        logger.error(f"未处理的异常: {str(error)}", exc_info=True)

        bmos_error = BMOSError(
            message="内部服务器错误",
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"original_error": str(error)},
            severity=ErrorSeverity.CRITICAL,
            user_message="系统内部错误，请稍后重试",
        )

        return self.handle_bmos_error(bmos_error, request_id)

    def _log_error(self, error: BMOSError):
        """记录错误日志"""

        log_level = self._get_log_level(error.severity)

        log_message = f"BMOS错误: {error.code.value} - {error.message}"
        if error.details:
            log_message += f" | 详情: {error.details}"

        if log_level == logging.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif log_level == logging.ERROR:
            logger.error(log_message, exc_info=True)
        elif log_level == logging.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        severity_map = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }
        return severity_map.get(severity, logging.ERROR)

    def _get_http_status_code(self, error_code: ErrorCode) -> int:
        """获取HTTP状态码"""
        status_map = {
            ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ErrorCode.AUTHENTICATION_FAILED: status.HTTP_401_UNAUTHORIZED,
            ErrorCode.AUTHORIZATION_DENIED: status.HTTP_403_FORBIDDEN,
            ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ErrorCode.DATA_NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ErrorCode.DATA_CONFLICT: status.HTTP_409_CONFLICT,
            ErrorCode.EXTERNAL_SERVICE_ERROR: status.HTTP_502_BAD_GATEWAY,
            ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCode.TIMEOUT_ERROR: status.HTTP_504_GATEWAY_TIMEOUT,
            ErrorCode.FILE_SIZE_EXCEEDED: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            ErrorCode.FILE_TYPE_NOT_SUPPORTED: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        }
        return status_map.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# 全局错误处理器
error_handler = ErrorHandler(include_debug=False)


# FastAPI异常处理器
async def bmos_exception_handler(request: Request, exc: BMOSError) -> JSONResponse:
    """BMOS异常处理器"""
    request_id = getattr(request.state, "request_id", None)
    return error_handler.handle_bmos_error(exc, request_id)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """验证异常处理器"""
    request_id = getattr(request.state, "request_id", None)
    return error_handler.handle_validation_error(exc, request_id)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    request_id = getattr(request.state, "request_id", None)
    return error_handler.handle_http_exception(exc, request_id)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    request_id = getattr(request.state, "request_id", None)
    return error_handler.handle_generic_exception(exc, request_id)


# 错误处理装饰器
def handle_errors(func):
    """错误处理装饰器"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BMOSError as e:
            raise e
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
            raise BMOSError(
                message=f"函数 {func.__name__} 执行失败: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                severity=ErrorSeverity.HIGH,
            )

    return wrapper


# 业务错误装饰器
def business_error_handler(func):
    """业务错误处理装饰器"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BMOSError:
            raise
        except Exception as e:
            logger.error(f"业务逻辑错误 {func.__name__}: {str(e)}", exc_info=True)
            raise BusinessError(f"业务逻辑执行失败: {str(e)}")

    return wrapper
