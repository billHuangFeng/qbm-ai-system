"""
BMOS系统 - 数据库管理模块
提供数据库连接和基本操作功能
"""

import asyncio
import asyncpg
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False

    async def initialize(self):
        """初始化数据库连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url, min_size=5, max_size=20, command_timeout=30
            )
            self._connected = True
            logger.info("数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
            raise

    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            self._connected = False
            logger.info("数据库连接池已关闭")

    def health_check(self) -> bool:
        """健康检查"""
        return self._connected and self.pool is not None

    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """执行查询"""
        if not self.pool:
            raise Exception("数据库连接池未初始化")

        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch(query, *args)
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise

    async def execute_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """执行单行查询"""
        if not self.pool:
            raise Exception("数据库连接池未初始化")

        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, *args)
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"单行查询执行失败: {e}")
            raise

    async def execute(self, query: str, *args) -> str:
        """执行命令"""
        if not self.pool:
            raise Exception("数据库连接池未初始化")

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *args)
                return result
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            raise


# 全局数据库管理器实例
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global db_manager
    if not db_manager:
        raise Exception("数据库管理器未初始化")
    return db_manager


async def init_db_manager(database_url: str):
    """初始化数据库管理器"""
    global db_manager
    db_manager = DatabaseManager(database_url)
    await db_manager.initialize()


async def close_db_manager():
    """关闭数据库管理器"""
    global db_manager
    if db_manager:
        await db_manager.close()
        db_manager = None
