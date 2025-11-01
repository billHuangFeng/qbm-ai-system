"""
BMOS系统 - 统一配置管理
提供统一的配置管理，支持多环境配置
"""

import os
import json
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    
    # PostgreSQL配置
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="password", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="bmos", env="POSTGRES_DB")
    
    # 连接池配置
    pool_min_size: int = Field(default=5, env="DB_POOL_MIN_SIZE")
    pool_max_size: int = Field(default=20, env="DB_POOL_MAX_SIZE")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    @property
    def database_url(self) -> str:
        """数据库连接URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def async_database_url(self) -> str:
        """异步数据库连接URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class RedisConfig(BaseSettings):
    """Redis配置"""
    
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # 连接配置
    redis_timeout: int = Field(default=5, env="REDIS_TIMEOUT")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class SecurityConfig(BaseSettings):
    """安全配置"""
    
    # JWT配置
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # 密码策略
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_special_chars: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL_CHARS")
    
    # CORS配置
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        """验证JWT密钥"""
        if not v:
            raise ValueError("JWT_SECRET_KEY must be set")
        
        # 检查是否为默认值
        default_keys = [
            "your-super-secure-jwt-secret-key-minimum-32-characters-long",
            "secret",
            "password",
            "123456",
            "jwt_secret_key"
        ]
        
        if v in default_keys:
            raise ValueError("JWT_SECRET_KEY must not use default values")
        
        # 检查长度
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        
        # 检查复杂度
        if v.isalpha() or v.isdigit():
            raise ValueError("JWT_SECRET_KEY must contain mixed characters")
        
        return v
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        """验证CORS配置"""
        if not v:
            return ["http://localhost:3000"]
        
        # 在生产环境中不允许使用通配符
        if "*" in v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("CORS origins cannot use wildcard in production")
        
        return v
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # 速率限制
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    @validator('jwt_secret_key')
    def validate_jwt_secret_key(cls, v):
        if not v or v == "your-secret-key-here":
            raise ValueError("JWT_SECRET_KEY must be set and not use default value")
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class ApplicationConfig(BaseSettings):
    """应用配置"""
    
    # 基本信息
    app_name: str = Field(default="BMOS AI System", env="PROJECT_NAME")
    app_version: str = Field(default="1.0.0", env="PROJECT_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API配置
    api_v1_str: str = Field(default="/api/v1", env="API_V1_STR")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # 日志配置
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    log_rotation_size: str = Field(default="10MB", env="LOG_ROTATION_SIZE")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # 性能配置
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    worker_timeout: int = Field(default=300, env="WORKER_TIMEOUT")
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    # 缓存配置
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class FileConfig(BaseSettings):
    """文件配置"""
    
    # 文件上传
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE")
    allowed_file_types: List[str] = Field(default=[".csv", ".xlsx", ".json"], env="ALLOWED_FILE_TYPES")
    
    # 文件存储
    storage_type: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, minio
    storage_bucket: Optional[str] = Field(default=None, env="STORAGE_BUCKET")
    storage_endpoint: Optional[str] = Field(default=None, env="STORAGE_ENDPOINT")
    
    @validator('allowed_file_types', pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class MonitoringConfig(BaseSettings):
    """监控配置"""
    
    # Prometheus配置
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # 健康检查
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    # 告警配置
    enable_alerts: bool = Field(default=True, env="ENABLE_ALERTS")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class Settings(BaseSettings):
    """统一配置类"""
    
    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()
    application: ApplicationConfig = ApplicationConfig()
    file: FileConfig = FileConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        # 验证环境相关配置
        if self.application.environment == Environment.PRODUCTION:
            if self.application.debug:
                logger.warning("生产环境不应启用DEBUG模式")
            
            if "*" in self.security.cors_origins:
                logger.warning("生产环境不应使用CORS通配符")
        
        # 验证文件路径
        if self.file.upload_dir and not os.path.exists(self.file.upload_dir):
            try:
                os.makedirs(self.file.upload_dir, exist_ok=True)
                logger.info(f"创建上传目录: {self.file.upload_dir}")
            except Exception as e:
                logger.error(f"无法创建上传目录: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "database": self.database.dict(),
            "redis": self.redis.dict(),
            "security": self.security.dict(),
            "application": self.application.dict(),
            "file": self.file.dict(),
            "monitoring": self.monitoring.dict()
        }
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        config_dict = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """从文件加载配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls(**config_dict)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._settings: Optional[Settings] = None
    
    @property
    def settings(self) -> Settings:
        """获取配置实例"""
        if self._settings is None:
            self._settings = self._load_settings()
        return self._settings
    
    def _load_settings(self) -> Settings:
        """加载配置"""
        try:
            if self.config_file and os.path.exists(self.config_file):
                logger.info(f"从文件加载配置: {self.config_file}")
                return Settings.load_from_file(self.config_file)
            else:
                logger.info("从环境变量加载配置")
                return Settings()
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    def reload(self):
        """重新加载配置"""
        self._settings = None
        logger.info("配置已重新加载")
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self.settings.database
    
    def get_redis_config(self) -> RedisConfig:
        """获取Redis配置"""
        return self.settings.redis
    
    def get_security_config(self) -> SecurityConfig:
        """获取安全配置"""
        return self.settings.security
    
    def get_application_config(self) -> ApplicationConfig:
        """获取应用配置"""
        return self.settings.application
    
    def get_file_config(self) -> FileConfig:
        """获取文件配置"""
        return self.settings.file
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """获取监控配置"""
        return self.settings.monitoring
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.settings.application.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.settings.application.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.settings.application.environment == Environment.TESTING

# 全局配置管理器
config_manager = ConfigManager()

# 便捷访问函数
def get_settings() -> Settings:
    """获取配置"""
    return config_manager.settings

def get_database_config() -> DatabaseConfig:
    """获取数据库配置"""
    return config_manager.get_database_config()

def get_redis_config() -> RedisConfig:
    """获取Redis配置"""
    return config_manager.get_redis_config()

def get_security_config() -> SecurityConfig:
    """获取安全配置"""
    return config_manager.get_security_config()

def get_application_config() -> ApplicationConfig:
    """获取应用配置"""
    return config_manager.get_application_config()

def get_file_config() -> FileConfig:
    """获取文件配置"""
    return config_manager.get_file_config()

def get_monitoring_config() -> MonitoringConfig:
    """获取监控配置"""
    return config_manager.get_monitoring_config()

def is_development() -> bool:
    """是否为开发环境"""
    return config_manager.is_development()

def is_production() -> bool:
    """是否为生产环境"""
    return config_manager.is_production()

def is_testing() -> bool:
    """是否为测试环境"""
    return config_manager.is_testing()
