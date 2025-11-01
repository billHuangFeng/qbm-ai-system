"""
BMOS系统 - 通用异常处理装饰器
统一异常处理模式，消除代码重复
"""

from functools import wraps
from typing import Callable, Any, Optional
import logging
from datetime import datetime

from .enhanced import (
    BMOSBaseException, BMOSValidationError, BMOSDatabaseError,
    BMOSBusinessError, BMOSAuthenticationError, BMOSAuthorizationError,
    BMOSExternalServiceError, BMOSConfigurationError, BMOSResourceError
)

logger = logging.getLogger(__name__)

def handle_service_errors(
    default_message: str = "操作失败",
    log_errors: bool = True,
    reraise: bool = True,
    suppress_unknown: bool = False
):
    """
    服务层异常处理装饰器
    
    Args:
        default_message: 默认错误消息
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
        suppress_unknown: 是否抑制未知异常
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BMOSBaseException:
                # BMOS异常直接重新抛出
                raise
            except ValueError as e:
                # 值错误转换为验证错误
                error = BMOSValidationError(
                    message=f"输入验证失败: {str(e)}",
                    details={"field": "unknown"}
                )
                if log_errors:
                    logger.warning(f"Validation error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except KeyError as e:
                # 键错误转换为资源错误
                error = BMOSResourceError(
                    message=f"缺少必要参数: {str(e)}",
                    details={"missing_key": str(e)}
                )
                if log_errors:
                    logger.error(f"Missing key error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except ConnectionError as e:
                # 连接错误转换为外部服务错误
                error = BMOSExternalServiceError(
                    message=f"服务连接失败: {str(e)}",
                    details={"error_type": "connection_error"}
                )
                if log_errors:
                    logger.error(f"Connection error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except TimeoutError as e:
                # 超时错误转换为外部服务错误
                error = BMOSExternalServiceError(
                    message=f"服务超时: {str(e)}",
                    details={"error_type": "timeout_error"}
                )
                if log_errors:
                    logger.error(f"Timeout error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except PermissionError as e:
                # 权限错误转换为授权错误
                error = BMOSAuthorizationError(
                    message=f"权限不足: {str(e)}",
                    details={"error_type": "permission_error"}
                )
                if log_errors:
                    logger.warning(f"Permission error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except FileNotFoundError as e:
                # 文件未找到错误转换为资源错误
                error = BMOSResourceError(
                    message=f"资源未找到: {str(e)}",
                    details={"error_type": "file_not_found"}
                )
                if log_errors:
                    logger.error(f"File not found error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except Exception as e:
                # 其他异常转换为业务错误
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                
                if suppress_unknown:
                    return None
                
                if reraise:
                    raise BMOSBusinessError(
                        message=f"{default_message}: {str(e)}",
                        details={"error_type": "unexpected_error"}
                    )
                else:
                    return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BMOSBaseException:
                # BMOS异常直接重新抛出
                raise
            except ValueError as e:
                # 值错误转换为验证错误
                error = BMOSValidationError(
                    message=f"输入验证失败: {str(e)}",
                    details={"field": "unknown"}
                )
                if log_errors:
                    logger.warning(f"Validation error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except KeyError as e:
                # 键错误转换为资源错误
                error = BMOSResourceError(
                    message=f"缺少必要参数: {str(e)}",
                    details={"missing_key": str(e)}
                )
                if log_errors:
                    logger.error(f"Missing key error in {func.__name__}: {e}")
                if reraise:
                    raise error
                else:
                    return None
            except Exception as e:
                # 其他异常转换为业务错误
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                
                if suppress_unknown:
                    return None
                
                if reraise:
                    raise BMOSBusinessError(
                        message=f"{default_message}: {str(e)}",
                        details={"error_type": "unexpected_error"}
                    )
                else:
                    return None
        
        # 根据函数类型返回相应的包装器
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def handle_api_errors(
    default_message: str = "API调用失败",
    status_code: int = 500,
    log_errors: bool = True
):
    """
    API层异常处理装饰器
    
    Args:
        default_message: 默认错误消息
        status_code: 默认HTTP状态码
        log_errors: 是否记录错误日志
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BMOSValidationError as e:
                if log_errors:
                    logger.warning(f"Validation error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail={"code": e.code, "message": e.message}
                )
            except BMOSDatabaseError as e:
                if log_errors:
                    logger.error(f"Database error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=500,
                    detail={"code": e.code, "message": "数据库操作失败"}
                )
            except BMOSAuthenticationError as e:
                if log_errors:
                    logger.warning(f"Authentication error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=401,
                    detail={"code": e.code, "message": e.message}
                )
            except BMOSAuthorizationError as e:
                if log_errors:
                    logger.warning(f"Authorization error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403,
                    detail={"code": e.code, "message": e.message}
                )
            except BMOSResourceError as e:
                if log_errors:
                    logger.error(f"Resource error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=404,
                    detail={"code": e.code, "message": e.message}
                )
            except BMOSBusinessError as e:
                if log_errors:
                    logger.error(f"Business error in {func.__name__}: {e.message}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=status_code,
                    detail={"code": e.code, "message": e.message}
                )
            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=status_code,
                    detail={"code": "INTERNAL_SERVER_ERROR", "message": default_message}
                )
        
        return wrapper
    
    return decorator

# 使用示例：
# 
# @handle_service_errors(default_message="服务调用失败")
# async def my_service_function():
#     # 业务逻辑
#     pass
#
# @handle_api_errors(default_message="API调用失败", status_code=500)
# async def my_api_endpoint():
#     # API逻辑
#     pass

