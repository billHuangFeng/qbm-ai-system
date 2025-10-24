"""
环境配置管理
"""

import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "QBM历史数据拟合优化系统"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "postgresql://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting"
    async_database_url: str = "postgresql+asyncpg://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # 多租户配置
    max_tenants: int = 100
    default_tenant_schema: str = "tenant_"
    
    # 机器学习配置
    model_storage_path: str = "./models"
    max_training_data_size: int = 1000000
    model_cache_size: int = 100
    
    # 性能配置
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600
    
    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 安全配置
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    trusted_hosts: list = ["localhost", "127.0.0.1", "*.qbm.com"]
    
    # 文件上传配置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".csv", ".xlsx", ".json"]
    
    # 邮件配置
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # 通知配置
    enable_notifications: bool = True
    notification_channels: list = ["email", "webhook"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 全局配置实例
settings = Settings()

# 环境特定配置
class DevelopmentSettings(Settings):
    """开发环境配置"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "postgresql://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting_dev"
    redis_url: str = "redis://localhost:6379/1"

class ProductionSettings(Settings):
    """生产环境配置"""
    debug: bool = False
    log_level: str = "WARNING"
    database_url: str = os.getenv("DATABASE_URL", "postgresql://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "your-production-secret-key")

class TestingSettings(Settings):
    """测试环境配置"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "postgresql://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting_test"
    redis_url: str = "redis://localhost:6379/2"

def get_settings() -> Settings:
    """获取环境配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# 获取当前环境配置
current_settings = get_settings()


