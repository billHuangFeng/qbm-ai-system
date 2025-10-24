"""
日志配置
"""

import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any

# 日志配置字典
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/qbm_system.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/qbm_errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/qbm_system.json",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "qbm_system": {
            "level": "INFO",
            "handlers": ["console", "file", "json_file"],
            "propagate": False
        },
        "qbm_system.errors": {
            "level": "ERROR",
            "handlers": ["error_file"],
            "propagate": False
        },
        "qbm_system.auth": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "qbm_system.database": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "qbm_system.models": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "qbm_system.predictions": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "qbm_system.optimization": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "qbm_system.monitoring": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

class QBMLogger:
    """QBM系统日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"qbm_system.{name}")
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(message, extra=kwargs)

def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 应用日志配置
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # 创建主日志记录器
    main_logger = logging.getLogger("qbm_system")
    main_logger.info("日志系统初始化完成")

def get_logger(name: str) -> QBMLogger:
    """获取日志记录器"""
    return QBMLogger(name)

# 日志装饰器
def log_function_call(logger: QBMLogger):
    """函数调用日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"调用函数: {func.__name__}", function=func.__name__, args=args, kwargs=kwargs)
            try:
                result = func(*args, **kwargs)
                logger.info(f"函数执行成功: {func.__name__}", function=func.__name__, result=result)
                return result
            except Exception as e:
                logger.error(f"函数执行失败: {func.__name__}", function=func.__name__, error=str(e))
                raise
        return wrapper
    return decorator

def log_performance(logger: QBMLogger):
    """性能日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.info(f"开始执行: {func.__name__}", function=func.__name__)
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                logger.info(
                    f"执行完成: {func.__name__}",
                    function=func.__name__,
                    execution_time=execution_time
                )
                return result
            except Exception as e:
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                logger.error(
                    f"执行失败: {func.__name__}",
                    function=func.__name__,
                    execution_time=execution_time,
                    error=str(e)
                )
                raise
        return wrapper
    return decorator

# 审计日志
class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("audit")
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any] = None):
        """记录用户操作"""
        self.logger.info(
            f"用户操作: {action}",
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {}
        )
    
    def log_data_access(self, user_id: str, data_type: str, operation: str, tenant_id: str):
        """记录数据访问"""
        self.logger.info(
            f"数据访问: {operation}",
            user_id=user_id,
            data_type=data_type,
            operation=operation,
            tenant_id=tenant_id
        )
    
    def log_model_operation(self, user_id: str, model_id: str, operation: str, details: Dict[str, Any] = None):
        """记录模型操作"""
        self.logger.info(
            f"模型操作: {operation}",
            user_id=user_id,
            model_id=model_id,
            operation=operation,
            details=details or {}
        )
    
    def log_prediction(self, user_id: str, prediction_id: str, model_id: str, input_data: Dict[str, Any]):
        """记录预测操作"""
        self.logger.info(
            f"预测操作: {prediction_id}",
            user_id=user_id,
            prediction_id=prediction_id,
            model_id=model_id,
            input_data=input_data
        )

# 全局审计日志记录器
audit_logger = AuditLogger()


