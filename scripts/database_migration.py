"""
BMOS系统 - 数据库迁移脚本
提供数据库版本控制和迁移功能
"""

import asyncio
import asyncpg
from typing import List, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """数据库迁移器"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.migrations_dir = Path("database/migrations")
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
    
    async def connect(self):
        """连接到数据库"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            logger.info("已连接到数据库")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            await self.connection.close()
            logger.info("已断开数据库连接")
    
    async def ensure_migration_table(self):
        """确保迁移记录表存在"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
        await self.connection.execute(create_table_sql)
        logger.info("迁移记录表已确保存在")
    
    async def get_applied_migrations(self) -> List[str]:
        """获取已应用的迁移版本"""
        try:
            rows = await self.connection.fetch("SELECT version FROM schema_migrations ORDER BY applied_at")
            return [row['version'] for row in rows]
        except Exception as e:
            logger.error(f"获取已应用迁移失败: {e}")
            return []
    
    async def mark_migration_applied(self, version: str, name: str):
        """标记迁移已应用"""
        try:
            await self.connection.execute(
                "INSERT INTO schema_migrations (version, name, applied_at) VALUES ($1, $2, NOW())",
                version, name
            )
            logger.info(f"迁移 {version} 已标记为已应用")
        except Exception as e:
            logger.error(f"标记迁移失败: {e}")
            raise
    
    async def apply_migration(self, version: str, name: str, sql: str):
        """应用迁移"""
        try:
            logger.info(f"应用迁移: {version} - {name}")
            
            # 在事务中执行
            async with self.connection.transaction():
                await self.connection.execute(sql)
                await self.mark_migration_applied(version, name)
            
            logger.info(f"迁移 {version} 应用成功")
        except Exception as e:
            logger.error(f"应用迁移失败: {e}")
            raise
    
    async def rollback_migration(self, version: str):
        """回滚迁移"""
        try:
            logger.info(f"回滚迁移: {version}")
            
            # 获取迁移文件中的回滚SQL
            migration_file = self.migrations_dir / f"{version}_rollback.sql"
            
            if migration_file.exists():
                rollback_sql = migration_file.read_text(encoding='utf-8')
                
                async with self.connection.transaction():
                    await self.connection.execute(rollback_sql)
                    await self.connection.execute(
                        "DELETE FROM schema_migrations WHERE version = $1", version
                    )
                
                logger.info(f"迁移 {version} 回滚成功")
            else:
                logger.warning(f"未找到回滚文件: {migration_file}")
        
        except Exception as e:
            logger.error(f"回滚迁移失败: {e}")
            raise
    
    async def migrate(self):
        """执行所有待应用的迁移"""
        try:
            await self.connect()
            await self.ensure_migration_table()
            
            applied_migrations = await self.get_applied_migrations()
            logger.info(f"已应用的迁移版本: {applied_migrations}")
            
            # 获取所有迁移文件
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            
            for migration_file in migration_files:
                version = migration_file.stem
                
                # 跳过回滚文件和已应用的迁移
                if version.endswith("_rollback") or version in applied_migrations:
                    continue
                
                logger.info(f"发现待应用迁移: {version}")
                
                # 读取迁移SQL
                migration_sql = migration_file.read_text(encoding='utf-8')
                
                # 应用迁移
                await self.apply_migration(
                    version=version,
                    name=migration_file.name,
                    sql=migration_sql
                )
            
            logger.info("所有迁移已应用完成")
        
        except Exception as e:
            logger.error(f"迁移过程出错: {e}")
            raise
        
        finally:
            await self.disconnect()
    
    def create_migration(self, name: str) -> str:
        """创建新的迁移文件"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version = f"{timestamp}_{name}"
        
        migration_file = self.migrations_dir / f"{version}.sql"
        rollback_file = self.migrations_dir / f"{version}_rollback.sql"
        
        # 创建迁移文件
        migration_file.write_text("""-- 迁移名称: {name}
-- 创建时间: {timestamp}

-- TODO: 编写迁移SQL

""".format(name=name, timestamp=datetime.now().isoformat()))
        
        # 创建回滚文件
        rollback_file.write_text("""-- 回滚迁移: {name}
-- 创建时间: {timestamp}

-- TODO: 编写回滚SQL

""".format(name=name, timestamp=datetime.now().isoformat()))
        
        logger.info(f"已创建迁移文件: {migration_file}")
        logger.info(f"已创建回滚文件: {rollback_file}")
        
        return str(migration_file)

# 预定义的迁移
MIGRATION_001_INITIAL_SCHEMA = """
-- 初始化数据库架构
-- 版本: 001_initial_schema

-- 创建原始数据暂存表
CREATE TABLE IF NOT EXISTS raw_data_staging (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    tenant_id VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建表头索引
CREATE INDEX IF NOT EXISTS idx_raw_data_staging_uploaded_at ON raw_data_staging(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""

MIGRATION_002_BMOS_CORE_TABLES = """
-- BMOS核心表
-- 版本: 002_bmos_core_tables

-- 创建价值主张标签表
CREATE TABLE IF NOT EXISTS dim_vpt (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tenant_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建客户维度表
CREATE TABLE IF NOT EXISTS dim_customer (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    category VARCHAR(100),
    region VARCHAR(100),
    tenant_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建订单事实表
CREATE TABLE IF NOT EXISTS fact_order (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(18, 2) NOT NULL,
    status VARCHAR(50),
    tenant_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_fact_order_customer_id ON fact_order(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_order_order_date ON fact_order(order_date);
CREATE INDEX IF NOT EXISTS idx_dim_customer_customer_id ON dim_customer(customer_id);
"""

MIGRATION_003_LEARNING_SYSTEM = """
-- 学习系统表
-- 版本: 003_learning_system

-- 创建企业记忆表
CREATE TABLE IF NOT EXISTS enterprise_memory (
    id SERIAL PRIMARY KEY,
    memory_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    context JSONB,
    tags VARCHAR[],
    tenant_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    applied_count INTEGER NOT NULL DEFAULT 0
);

-- 创建预测准确度日志表
CREATE TABLE IF NOT EXISTS prediction_accuracy_log (
    id SERIAL PRIMARY KEY,
    prediction_id VARCHAR(100) NOT NULL,
    model_id VARCHAR(100),
    actual_value DECIMAL(18, 4),
    predicted_value DECIMAL(18, 4),
    error DECIMAL(18, 4),
    error_percentage DECIMAL(10, 4),
    tenant_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_enterprise_memory_tags ON enterprise_memory USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_enterprise_memory_created_at ON enterprise_memory(created_at);
CREATE INDEX IF NOT EXISTS idx_prediction_accuracy_log_prediction_id ON prediction_accuracy_log(prediction_id);
"""

MIGRATION_004_MODEL_TRAINING = """
-- 模型训练表
-- 版本: 004_model_training

-- 创建模型参数存储表
CREATE TABLE IF NOT EXISTS model_parameters_storage (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) UNIQUE NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    training_metrics JSONB,
    feature_importances JSONB,
    tenant_id VARCHAR(100),
    trained_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 创建模型训练历史表
CREATE TABLE IF NOT EXISTS model_training_history (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    training_session_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    metrics JSONB,
    error_message TEXT,
    tenant_id VARCHAR(100)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_model_parameters_storage_model_id ON model_parameters_storage(model_id);
CREATE INDEX IF NOT EXISTS idx_model_training_history_model_id ON model_training_history(model_id);
CREATE INDEX IF NOT EXISTS idx_model_training_history_status ON model_training_history(status);
"""

async def run_migrations():
    """运行所有迁移"""
    # 从环境变量或配置文件获取数据库URL
    database_url = "postgresql://user:password@localhost:5432/bmos"
    
    migrator = DatabaseMigrator(database_url)
    
    try:
        await migrator.migrate()
        logger.info("所有迁移已成功应用")
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migrations())


