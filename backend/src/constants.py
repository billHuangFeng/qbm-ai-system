"""
BMOS系统 - 常量管理
统一管理系统中的所有常量
"""

from enum import Enum
from typing import List, Dict, Any

class Constants:
    """系统常量"""
    
    # 应用配置
    APP_NAME = "BMOS AI System"
    APP_VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    RETRY_BACKOFF_FACTOR = 2.0
    
    # 超时配置
    DEFAULT_TIMEOUT = 300  # 5分钟
    API_TIMEOUT = 30  # 30秒
    DATABASE_TIMEOUT = 10  # 10秒
    REDIS_TIMEOUT = 5  # 5秒
    
    # 缓存配置
    DEFAULT_CACHE_TTL = 3600  # 1小时
    SHORT_CACHE_TTL = 300  # 5分钟
    LONG_CACHE_TTL = 86400  # 24小时
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_PAGE_SIZE = 1
    
    # 文件配置
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = ['.csv', '.xlsx', '.json', '.txt']
    UPLOAD_DIR = "./uploads"
    
    # 数据库配置
    DB_POOL_MIN_SIZE = 5
    DB_POOL_MAX_SIZE = 20
    DB_POOL_TIMEOUT = 30
    
    # Redis配置
    REDIS_MAX_CONNECTIONS = 20
    REDIS_CONNECTION_TIMEOUT = 5
    
    # 任务配置
    TASK_MAX_WORKERS = 5
    TASK_DEFAULT_TIMEOUT = 300
    TASK_MAX_RETRIES = 3
    TASK_RETRY_DELAY = 60
    
    # 安全配置
    JWT_MIN_SECRET_LENGTH = 32
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    
    # 日志配置
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 监控配置
    METRICS_INTERVAL = 60  # 60秒
    HEALTH_CHECK_INTERVAL = 30  # 30秒
    
    # 业务配置
    MAX_MODELS_PER_TENANT = 100
    MAX_PREDICTIONS_PER_REQUEST = 1000
    MAX_MEMORY_ENTRIES_PER_TENANT = 10000
    
    # 算法配置
    DEFAULT_TRAINING_DATA_SIZE = 10000
    MIN_TRAINING_DATA_SIZE = 100
    MAX_FEATURES = 1000
    
    # 数据质量配置
    MIN_DATA_QUALITY_SCORE = 0.7
    MAX_MISSING_DATA_RATIO = 0.3
    MAX_OUTLIER_RATIO = 0.1

class ErrorCodes:
    """错误代码常量"""
    
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # 验证错误
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # 认证授权错误
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # 数据库错误
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    DATABASE_QUERY_FAILED = "DATABASE_QUERY_FAILED"
    DATABASE_CONSTRAINT_VIOLATION = "DATABASE_CONSTRAINT_VIOLATION"
    
    # 业务错误
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    OPERATION_FAILED = "OPERATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # 外部服务错误
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    
    # 文件操作错误
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_TYPE_NOT_SUPPORTED = "FILE_TYPE_NOT_SUPPORTED"
    
    # 配置错误
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    MISSING_CONFIGURATION = "MISSING_CONFIGURATION"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"

class StatusCodes:
    """状态代码常量"""
    
    # 成功状态
    SUCCESS = "success"
    COMPLETED = "completed"
    PROCESSING = "processing"
    
    # 失败状态
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    
    # 等待状态
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    
    # 模型状态
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    
    # 数据状态
    VALIDATING = "validating"
    VALIDATED = "validated"
    IMPORTING = "importing"
    IMPORTED = "imported"

class TaskPriorities:
    """任务优先级常量"""
    
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    
    PRIORITY_NAMES = {
        LOW: "low",
        NORMAL: "normal",
        HIGH: "high",
        CRITICAL: "critical"
    }

class CacheKeys:
    """缓存键常量"""
    
    # 用户相关
    USER_SESSION = "user:session:{user_id}"
    USER_PERMISSIONS = "user:permissions:{user_id}"
    
    # 模型相关
    MODEL_CACHE = "model:{model_id}"
    MODEL_PREDICTIONS = "model:predictions:{model_id}"
    
    # 数据相关
    DATA_CACHE = "data:{table_name}:{key}"
    DATA_QUALITY = "data:quality:{table_name}"
    
    # 任务相关
    TASK_STATUS = "task:status:{task_id}"
    TASK_RESULT = "task:result:{task_id}"
    
    # 系统相关
    SYSTEM_HEALTH = "system:health"
    SYSTEM_METRICS = "system:metrics"

class DatabaseTables:
    """数据库表名常量"""
    
    # 用户相关
    USERS = "users"
    USER_SESSIONS = "user_sessions"
    USER_PERMISSIONS = "user_permissions"
    
    # 租户相关
    TENANTS = "tenants"
    TENANT_SETTINGS = "tenant_settings"
    
    # 模型相关
    MODELS = "models"
    MODEL_VERSIONS = "model_versions"
    MODEL_PARAMETERS = "model_parameters"
    
    # 预测相关
    PREDICTIONS = "predictions"
    PREDICTION_RESULTS = "prediction_results"
    
    # 数据相关
    DATA_IMPORTS = "data_imports"
    DATA_QUALITY_CHECKS = "data_quality_checks"
    
    # 企业记忆相关
    ENTERPRISE_MEMORIES = "enterprise_memories"
    MEMORY_FEEDBACK = "memory_feedback"
    
    # 任务相关
    TASKS = "tasks"
    TASK_LOGS = "task_logs"
    SCHEDULED_JOBS = "scheduled_jobs"
    
    # 系统相关
    SYSTEM_LOGS = "system_logs"
    SYSTEM_METRICS = "system_metrics"

class APIEndpoints:
    """API端点常量"""
    
    # 认证相关
    AUTH_LOGIN = "/auth/login"
    AUTH_LOGOUT = "/auth/logout"
    AUTH_REFRESH = "/auth/refresh"
    AUTH_REGISTER = "/auth/register"
    
    # 用户相关
    USERS_ME = "/users/me"
    USERS_UPDATE = "/users/update"
    USERS_DELETE = "/users/delete"
    
    # 模型相关
    MODELS_LIST = "/models"
    MODELS_CREATE = "/models"
    MODELS_TRAIN = "/models/train"
    MODELS_PREDICT = "/models/predict"
    MODELS_DELETE = "/models/{model_id}"
    
    # 预测相关
    PREDICTIONS_CREATE = "/predictions"
    PREDICTIONS_LIST = "/predictions"
    PREDICTIONS_RESULT = "/predictions/{prediction_id}"
    
    # 数据相关
    DATA_IMPORT = "/data/import"
    DATA_VALIDATE = "/data/validate"
    DATA_QUALITY = "/data/quality"
    
    # 企业记忆相关
    MEMORIES_EXTRACT = "/memories/extract"
    MEMORIES_SEARCH = "/memories/search"
    MEMORIES_FEEDBACK = "/memories/feedback"
    
    # 任务相关
    TASKS_ENQUEUE = "/tasks/enqueue"
    TASKS_STATUS = "/tasks/{task_id}"
    TASKS_CANCEL = "/tasks/{task_id}"
    
    # 系统相关
    HEALTH_CHECK = "/health"
    SYSTEM_METRICS = "/system/metrics"
    SYSTEM_LOGS = "/system/logs"

class EnvironmentVariables:
    """环境变量常量"""
    
    # 数据库
    DATABASE_URL = "DATABASE_URL"
    POSTGRES_HOST = "POSTGRES_HOST"
    POSTGRES_PORT = "POSTGRES_PORT"
    POSTGRES_USER = "POSTGRES_USER"
    POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
    POSTGRES_DB = "POSTGRES_DB"
    
    # Redis
    REDIS_URL = "REDIS_URL"
    REDIS_HOST = "REDIS_HOST"
    REDIS_PORT = "REDIS_PORT"
    REDIS_PASSWORD = "REDIS_PASSWORD"
    REDIS_DB = "REDIS_DB"
    
    # 应用
    ENVIRONMENT = "ENVIRONMENT"
    DEBUG = "DEBUG"
    LOG_LEVEL = "LOG_LEVEL"
    API_HOST = "API_HOST"
    API_PORT = "API_PORT"
    
    # 安全
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ALGORITHM = "JWT_ALGORITHM"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = "JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    
    # CORS
    CORS_ORIGINS = "CORS_ORIGINS"
    CORS_ALLOW_CREDENTIALS = "CORS_ALLOW_CREDENTIALS"
    CORS_ALLOW_METHODS = "CORS_ALLOW_METHODS"
    CORS_ALLOW_HEADERS = "CORS_ALLOW_HEADERS"
    
    # 文件
    UPLOAD_DIR = "UPLOAD_DIR"
    MAX_FILE_SIZE = "MAX_FILE_SIZE"
    
    # 外部服务
    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    
    # 监控
    GRAFANA_PASSWORD = "GRAFANA_PASSWORD"
    PROMETHEUS_ENABLED = "PROMETHEUS_ENABLED"

class DefaultValues:
    """默认值常量"""
    
    # 数据库默认值
    DEFAULT_DB_HOST = "localhost"
    DEFAULT_DB_PORT = 5432
    DEFAULT_DB_USER = "postgres"
    DEFAULT_DB_NAME = "bmos"
    
    # Redis默认值
    DEFAULT_REDIS_HOST = "localhost"
    DEFAULT_REDIS_PORT = 6379
    DEFAULT_REDIS_DB = 0
    
    # 应用默认值
    DEFAULT_API_HOST = "0.0.0.0"
    DEFAULT_API_PORT = 8000
    DEFAULT_LOG_LEVEL = "INFO"
    
    # 安全默认值
    DEFAULT_JWT_ALGORITHM = "HS256"
    DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DEFAULT_JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # CORS默认值
    DEFAULT_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
    DEFAULT_CORS_ALLOW_CREDENTIALS = True
    DEFAULT_CORS_ALLOW_METHODS = ["*"]
    DEFAULT_CORS_ALLOW_HEADERS = ["*"]

# 导出所有常量
__all__ = [
    'Constants',
    'ErrorCodes', 
    'StatusCodes',
    'TaskPriorities',
    'CacheKeys',
    'DatabaseTables',
    'APIEndpoints',
    'EnvironmentVariables',
    'DefaultValues'
]

