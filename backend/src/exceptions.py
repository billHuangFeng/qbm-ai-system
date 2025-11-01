"""
BMOS系统 - 自定义异常类
提供系统特定的异常类型
"""

from typing import Any, Dict, Optional

class BMOSBaseException(Exception):
    """BMOS系统基础异常类"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ModelError(BMOSBaseException):
    """模型相关错误"""
    pass

class ValidationError(BMOSBaseException):
    """数据验证错误"""
    pass

class DatabaseError(BMOSBaseException):
    """数据库操作错误"""
    pass

class AuthenticationError(BMOSBaseException):
    """认证错误"""
    pass

class AuthorizationError(BMOSBaseException):
    """授权错误"""
    pass

class BusinessLogicError(BMOSBaseException):
    """业务逻辑错误"""
    pass

class ExternalServiceError(BMOSBaseException):
    """外部服务错误"""
    pass

class ConfigurationError(BMOSBaseException):
    """配置错误"""
    pass

class DataQualityError(BMOSBaseException):
    """数据质量错误"""
    pass

class AlgorithmError(BMOSBaseException):
    """算法执行错误"""
    pass

class MemoryError(BMOSBaseException):
    """企业记忆错误"""
    pass

class PredictionError(BMOSBaseException):
    """预测错误"""
    pass

class OptimizationError(BMOSBaseException):
    """优化错误"""
    pass

class MonitoringError(BMOSBaseException):
    """监控错误"""
    pass

class SchedulerError(BMOSBaseException):
    """调度器错误"""
    pass

class ImportError(BMOSBaseException):
    """数据导入错误"""
    pass

class ExportError(BMOSBaseException):
    """数据导出错误"""
    pass

class CacheError(BMOSBaseException):
    """缓存错误"""
    pass

class FileError(BMOSBaseException):
    """文件操作错误"""
    pass

class NetworkError(BMOSBaseException):
    """网络错误"""
    pass

class TimeoutError(BMOSBaseException):
    """超时错误"""
    pass

class ResourceError(BMOSBaseException):
    """资源错误"""
    pass

class ConcurrencyError(BMOSBaseException):
    """并发错误"""
    pass

class VersionError(BMOSBaseException):
    """版本错误"""
    pass

class MigrationError(BMOSBaseException):
    """迁移错误"""
    pass

class BackupError(BMOSBaseException):
    """备份错误"""
    pass

class RestoreError(BMOSBaseException):
    """恢复错误"""
    pass

class AuditError(BMOSBaseException):
    """审计错误"""
    pass

class ComplianceError(BMOSBaseException):
    """合规错误"""
    pass

class SecurityError(BMOSBaseException):
    """安全错误"""
    pass

class PerformanceError(BMOSBaseException):
    """性能错误"""
    pass

class ScalabilityError(BMOSBaseException):
    """可扩展性错误"""
    pass

class MaintenanceError(BMOSBaseException):
    """维护错误"""
    pass

class DeploymentError(BMOSBaseException):
    """部署错误"""
    pass

class TestingError(BMOSBaseException):
    """测试错误"""
    pass

class DocumentationError(BMOSBaseException):
    """文档错误"""
    pass

class SupportError(BMOSBaseException):
    """支持错误"""
    pass

# 异常处理工具函数
def handle_exception(func):
    """异常处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BMOSBaseException:
            raise
        except Exception as e:
            raise BMOSBaseException(f"未处理的异常: {str(e)}")
    return wrapper

def create_error_response(error: BMOSBaseException) -> Dict[str, Any]:
    """创建错误响应"""
    return {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": error.message,
            "details": error.details
        }
    }

# 异常映射
EXCEPTION_MAPPING = {
    ValueError: ValidationError,
    TypeError: ValidationError,
    KeyError: ValidationError,
    AttributeError: ValidationError,
    IndexError: ValidationError,
    FileNotFoundError: FileError,
    PermissionError: FileError,
    ConnectionError: NetworkError,
    TimeoutError: TimeoutError,
    MemoryError: ResourceError,
    OSError: SystemError,
}

def map_exception(exception: Exception) -> BMOSBaseException:
    """映射标准异常到BMOS异常"""
    exception_type = type(exception)
    
    if exception_type in EXCEPTION_MAPPING:
        bmos_exception_class = EXCEPTION_MAPPING[exception_type]
        return bmos_exception_class(str(exception))
    
    return BMOSBaseException(f"未映射的异常: {str(exception)}")