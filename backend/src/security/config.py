"""
BMOS系统 - 安全配置管理
统一管理所有安全相关的配置和密钥
"""

import os
import secrets
from typing import Optional
from pydantic import BaseSettings, validator
import logging

logger = logging.getLogger(__name__)


class SecuritySettings(BaseSettings):
    """安全配置类"""

    # JWT配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # 密码策略
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special_chars: bool = True

    # 会话管理
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 5

    # 安全头配置
    enable_cors: bool = True
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    enable_csrf: bool = True
    enable_rate_limiting: bool = True

    # 文件上传安全
    max_file_size_mb: int = 10
    allowed_file_types: list = [".csv", ".xlsx", ".json", ".pdf"]
    scan_uploaded_files: bool = True

    # API安全
    api_rate_limit_per_minute: int = 60
    api_rate_limit_burst: int = 100

    # 数据库安全
    enable_query_logging: bool = False
    max_query_execution_time: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("jwt_secret_key")
    def validate_jwt_secret_key(cls, v):
        if not v or v == "your-secret-key-here":
            raise ValueError("JWT_SECRET_KEY must be set and not use default value")
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v

    @validator("cors_origins")
    def validate_cors_origins(cls, v):
        if "*" in v:
            logger.warning(
                "CORS origins contains wildcard (*), this may be a security risk"
            )
        return v

    @validator("password_min_length")
    def validate_password_min_length(cls, v):
        if v < 8:
            raise ValueError("Password minimum length must be at least 8 characters")
        return v


def generate_secure_secret_key() -> str:
    """生成安全的密钥"""
    return secrets.token_urlsafe(32)


def validate_password_strength(
    password: str, settings: SecuritySettings
) -> tuple[bool, list[str]]:
    """验证密码强度"""
    errors = []

    if len(password) < settings.password_min_length:
        errors.append(f"密码长度至少需要{settings.password_min_length}个字符")

    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        errors.append("密码必须包含大写字母")

    if settings.password_require_lowercase and not any(c.islower() for c in password):
        errors.append("密码必须包含小写字母")

    if settings.password_require_numbers and not any(c.isdigit() for c in password):
        errors.append("密码必须包含数字")

    if settings.password_require_special_chars and not any(
        c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
    ):
        errors.append("密码必须包含特殊字符")

    return len(errors) == 0, errors


def sanitize_sql_input(input_value: str) -> str:
    """清理SQL输入，防止注入"""
    if not isinstance(input_value, str):
        return str(input_value)

    # 移除危险字符
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    sanitized = input_value

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()


def validate_file_upload(
    file_name: str, file_size: int, settings: SecuritySettings
) -> tuple[bool, str]:
    """验证文件上传安全性"""

    # 检查文件大小
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"文件大小超过限制 ({settings.max_file_size_mb}MB)"

    # 检查文件类型
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in settings.allowed_file_types:
        return False, f"不支持的文件类型: {file_ext}"

    # 检查文件名
    if any(
        char in file_name for char in ["..", "/", "\\", ":", "*", "?", "<", ">", "|"]
    ):
        return False, "文件名包含非法字符"

    return True, "文件验证通过"


# 全局安全配置实例
security_settings = SecuritySettings()

# 导出常用函数
__all__ = [
    "SecuritySettings",
    "security_settings",
    "generate_secure_secret_key",
    "validate_password_strength",
    "sanitize_sql_input",
    "validate_file_upload",
]
