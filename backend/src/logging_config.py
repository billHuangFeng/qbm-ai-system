"""
BMOS系统 - 统一日志配置
提供统一的日志配置和管理功能
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

class BMOSFormatter(logging.Formatter):
    """BMOS自定义日志格式化器"""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        
        # 构建格式字符串
        format_parts = []
        if include_timestamp:
            format_parts.append("%(asctime)s")
        if include_level:
            format_parts.append("[%(levelname)s]")
        format_parts.extend(["%(name)s", "-", "%(message)s"])
        
        super().__init__(" ".join(format_parts))
    
    def format(self, record):
        # 添加自定义字段
        record.timestamp = datetime.now().isoformat()
        record.service = getattr(record, 'service', 'unknown')
        record.request_id = getattr(record, 'request_id', None)
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加自定义字段
        if hasattr(record, 'service'):
            log_entry["service"] = record.service
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'tenant_id'):
            log_entry["tenant_id"] = record.tenant_id
        
        return json.dumps(log_entry, ensure_ascii=False)

class BMOSLogger:
    """BMOS日志管理器"""
    
    def __init__(self):
        self.loggers = {}
        self.handlers = {}
        self.formatters = {}
    
    def get_logger(self, name: str, level: str = "INFO") -> logging.Logger:
        """获取日志器"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(BMOSFormatter())
            logger.addHandler(console_handler)
            
            # 文件处理器（如果配置了日志文件）
            log_file = self._get_log_file_path()
            if log_file:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(JSONFormatter())
                logger.addHandler(file_handler)
        
        self.loggers[name] = logger
        return logger
    
    def _get_log_file_path(self) -> Optional[str]:
        """获取日志文件路径"""
        # 从环境变量或配置文件获取日志文件路径
        import os
        log_file = os.getenv('LOG_FILE_PATH')
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            return str(log_path)
        return None
    
    def configure_logging(self, config: dict):
        """配置日志系统"""
        # 设置根日志级别
        root_level = config.get('root_level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, root_level.upper()))
        
        # 配置特定模块的日志级别
        loggers_config = config.get('loggers', {})
        for logger_name, logger_config in loggers_config.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, logger_config.get('level', 'INFO').upper()))
            
            # 禁用传播到父日志器
            if logger_config.get('propagate', True) is False:
                logger.propagate = False
    
    def add_context(self, logger: logging.Logger, **context):
        """添加上下文信息到日志器"""
        # 创建适配器来添加上下文
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                # 添加上下文到extra
                kwargs['extra'] = kwargs.get('extra', {})
                kwargs['extra'].update(context)
                return msg, kwargs
        
        return ContextAdapter(logger, context)

# 全局日志管理器实例
_logger_manager = BMOSLogger()

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """获取日志器（便捷函数）"""
    return _logger_manager.get_logger(name, level)

def configure_logging(config: dict):
    """配置日志系统（便捷函数）"""
    _logger_manager.configure_logging(config)

def add_log_context(logger: logging.Logger, **context):
    """添加上下文信息（便捷函数）"""
    return _logger_manager.add_context(logger, **context)

# 默认配置
DEFAULT_LOGGING_CONFIG = {
    "root_level": "INFO",
    "loggers": {
        "bmos": {
            "level": "DEBUG",
            "propagate": False
        },
        "bmos.security": {
            "level": "INFO",
            "propagate": True
        },
        "bmos.performance": {
            "level": "INFO",
            "propagate": True
        },
        "bmos.algorithms": {
            "level": "DEBUG",
            "propagate": True
        },
        "bmos.services": {
            "level": "INFO",
            "propagate": True
        },
        "uvicorn": {
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "propagate": False
        }
    }
}

# 初始化默认配置
configure_logging(DEFAULT_LOGGING_CONFIG)