#!/usr/bin/env python3
"""
BMOS系统 - 配置验证脚本
验证环境变量配置是否正确
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.src.config.unified import ConfigManager, Settings
from backend.src.logging_config import get_logger

logger = get_logger("config_validator")

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.settings
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """验证所有配置"""
        logger.info("开始配置验证...")
        
        # 验证各个配置模块
        self.validate_database_config()
        self.validate_redis_config()
        self.validate_security_config()
        self.validate_application_config()
        self.validate_file_config()
        self.validate_monitoring_config()
        
        # 输出结果
        self.print_results()
        
        return len(self.errors) == 0
    
    def validate_database_config(self):
        """验证数据库配置"""
        logger.info("验证数据库配置...")
        
        db_config = self.settings.database
        
        # 检查必需的配置
        if not db_config.database_url:
            self.errors.append("数据库URL未配置")
        
        if not db_config.postgres_host:
            self.errors.append("PostgreSQL主机未配置")
        
        if not db_config.postgres_password:
            self.errors.append("PostgreSQL密码未配置")
        
        # 检查端口范围
        if not (1 <= db_config.postgres_port <= 65535):
            self.errors.append(f"PostgreSQL端口无效: {db_config.postgres_port}")
        
        # 检查连接池配置
        if db_config.pool_min_size < 1:
            self.errors.append("数据库连接池最小大小必须大于0")
        
        if db_config.pool_max_size < db_config.pool_min_size:
            self.errors.append("数据库连接池最大大小必须大于等于最小大小")
    
    def validate_redis_config(self):
        """验证Redis配置"""
        logger.info("验证Redis配置...")
        
        redis_config = self.settings.redis
        
        if not redis_config.redis_url:
            self.errors.append("Redis URL未配置")
        
        # 检查Redis URL格式
        if not redis_config.redis_url.startswith(('redis://', 'rediss://')):
            self.errors.append("Redis URL格式无效")
    
    def validate_security_config(self):
        """验证安全配置"""
        logger.info("验证安全配置...")
        
        security_config = self.settings.security
        
        # 检查JWT密钥
        if not security_config.jwt_secret_key:
            self.errors.append("JWT密钥未配置")
        elif security_config.jwt_secret_key == "your-secret-key-here":
            self.errors.append("JWT密钥使用默认值，存在安全风险")
        elif len(security_config.jwt_secret_key) < 32:
            self.errors.append("JWT密钥长度不足32字符")
        
        # 检查密码策略
        if security_config.password_min_length < 8:
            self.warnings.append("密码最小长度建议设置为8或以上")
        
        # 检查CORS配置
        if "*" in security_config.cors_origins:
            self.warnings.append("CORS配置包含通配符，生产环境建议限制具体域名")
        
        # 检查文件上传限制
        if security_config.max_file_size_mb > 100:
            self.warnings.append("文件上传大小限制较大，可能影响性能")
    
    def validate_application_config(self):
        """验证应用配置"""
        logger.info("验证应用配置...")
        
        app_config = self.settings.application
        
        # 检查环境配置
        if app_config.environment.value == "production" and app_config.debug:
            self.errors.append("生产环境不应启用DEBUG模式")
        
        # 检查端口配置
        if not (1 <= app_config.api_port <= 65535):
            self.errors.append(f"API端口无效: {app_config.api_port}")
        
        # 检查日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if app_config.log_level.value not in valid_log_levels:
            self.errors.append(f"日志级别无效: {app_config.log_level.value}")
    
    def validate_file_config(self):
        """验证文件配置"""
        logger.info("验证文件配置...")
        
        file_config = self.settings.file
        
        # 检查上传目录
        if file_config.upload_dir:
            upload_path = Path(file_config.upload_dir)
            if not upload_path.exists():
                try:
                    upload_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建上传目录: {upload_path}")
                except Exception as e:
                    self.errors.append(f"无法创建上传目录: {e}")
            elif not upload_path.is_dir():
                self.errors.append(f"上传路径不是目录: {upload_path}")
    
    def validate_monitoring_config(self):
        """验证监控配置"""
        logger.info("验证监控配置...")
        
        monitoring_config = self.settings.monitoring
        
        # 检查监控端口
        if monitoring_config.enable_metrics:
            if not (1 <= monitoring_config.metrics_port <= 65535):
                self.errors.append(f"监控端口无效: {monitoring_config.metrics_port}")
    
    def print_results(self):
        """输出验证结果"""
        print("\n" + "="*60)
        print("BMOS系统配置验证结果")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个错误:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 配置验证通过，未发现问题")
        
        print("\n" + "="*60)
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("\n配置摘要:")
        print(f"  应用名称: {self.settings.application.app_name}")
        print(f"  应用版本: {self.settings.application.app_version}")
        print(f"  运行环境: {self.settings.application.environment.value}")
        print(f"  API端口: {self.settings.application.api_port}")
        print(f"  数据库: {self.settings.database.postgres_host}:{self.settings.database.postgres_port}")
        print(f"  Redis: {self.settings.redis.redis_url}")
        print(f"  日志级别: {self.settings.application.log_level.value}")

def main():
    """主函数"""
    print("BMOS系统配置验证工具")
    print("="*60)
    
    try:
        validator = ConfigValidator()
        
        # 打印配置摘要
        validator.print_config_summary()
        
        # 验证配置
        is_valid = validator.validate_all()
        
        if is_valid:
            print("\n✅ 配置验证成功，系统可以启动")
            sys.exit(0)
        else:
            print("\n❌ 配置验证失败，请修复错误后重试")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"配置验证过程中发生错误: {e}")
        print(f"\n❌ 配置验证失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


