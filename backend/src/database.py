"""
数据库配置和连接管理
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting"
)
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "postgresql+asyncpg://qbm_user:qbm_password@localhost:5432/qbm_historical_fitting"
)

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 创建同步引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # 生产环境设为False
)

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()

# 多租户Schema管理
TENANT_SCHEMAS = {
    "tenant_001": "enterprise_001",
    "tenant_002": "enterprise_002",
    # 可以动态添加更多租户
}

def get_tenant_schema(tenant_id: str) -> str:
    """获取租户对应的Schema名称"""
    return TENANT_SCHEMAS.get(tenant_id, f"tenant_{tenant_id}")

def create_tenant_schema(tenant_id: str) -> str:
    """为租户创建Schema"""
    schema_name = f"tenant_{tenant_id}"
    if schema_name not in TENANT_SCHEMAS.values():
        TENANT_SCHEMAS[tenant_id] = schema_name
    return schema_name

# 数据库连接管理
class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
    
    def get_sync_session(self):
        """获取同步会话"""
        return SessionLocal()
    
    def get_async_session(self):
        """获取异步会话"""
        return AsyncSessionLocal()
    
    async def create_tables(self):
        """创建所有表"""
        async with async_engine.begin() as conn:
            # 这里将导入所有模型并创建表
            # 暂时跳过，等模型定义完成后再实现
            logger.info("数据表创建功能待实现")
            pass
    
    async def drop_tables(self):
        """删除所有表"""
        async with async_engine.begin() as conn:
            # 删除所有表
            logger.info("数据表删除功能待实现")
            pass
    
    def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 依赖注入函数
def get_db():
    """获取数据库会话（同步）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """获取数据库会话（异步）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 多租户中间件
class TenantMiddleware:
    """多租户中间件"""
    
    @staticmethod
    def set_tenant_context(tenant_id: str):
        """设置租户上下文"""
        schema_name = get_tenant_schema(tenant_id)
        # 设置搜索路径到租户Schema
        return f"SET search_path TO {schema_name}, public"
    
    @staticmethod
    def get_tenant_from_request(request):
        """从请求中提取租户ID"""
        # 从请求头或路径中提取租户ID
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            # 从URL路径中提取
            path_parts = request.url.path.split("/")
            if len(path_parts) > 2 and path_parts[1] == "api":
                tenant_id = path_parts[2]
        
        return tenant_id

# 数据库迁移管理
class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.migrations_dir = "database/migrations"
    
    def create_migration(self, name: str) -> str:
        """创建新的迁移文件"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # 创建迁移文件模板
        template = f"""-- Migration: {name}
-- Created: {datetime.datetime.now().isoformat()}

-- Up migration
BEGIN;

-- Add your migration SQL here

COMMIT;

-- Down migration (rollback)
-- BEGIN;
-- 
-- -- Add your rollback SQL here
-- 
-- COMMIT;
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        logger.info(f"创建迁移文件: {filepath}")
        return filepath
    
    def run_migrations(self):
        """运行所有待执行的迁移"""
        # 这里将实现迁移执行逻辑
        logger.info("迁移执行功能待实现")
        pass
    
    def rollback_migration(self, migration_name: str):
        """回滚指定的迁移"""
        # 这里将实现迁移回滚逻辑
        logger.info(f"回滚迁移: {migration_name}")
        pass

# 全局迁移管理器实例
migration_manager = MigrationManager()


