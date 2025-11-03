"""
BMOS系统 - 数据库服务
作用: 封装数据库连接和操作
状态: ✅ 实施中
"""

import asyncpg
import redis.asyncio as redis
from typing import Optional, Dict, Any, List
import logging
import os
from contextlib import asynccontextmanager
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        
    async def initialize(self):
        """初始化数据库连接"""
        try:
            # PostgreSQL连接池
            self.pool = await asyncpg.create_pool(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', 5432)),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'password'),
                database=os.getenv('POSTGRES_DB', 'bmos'),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Redis连接
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True
            )
            
            # 测试连接
            await self.test_connections()
            
            logger.info("Database services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database services: {e}")
            raise
    
    async def test_connections(self):
        """测试数据库连接"""
        # 测试PostgreSQL
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1
        
        # 测试Redis
        await self.redis_client.ping()
        
        logger.info("Database connections tested successfully")
    
    async def close(self):
        """关闭数据库连接"""
        if self.pool:
            await self.pool.close()
        if self.redis_client:
            await self.redis_client.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        async with self.get_connection() as conn:
            try:
                rows = await conn.fetch(query, *(params or []))
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def execute_one(self, query: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """执行查询返回单行"""
        async with self.get_connection() as conn:
            try:
                row = await conn.fetchrow(query, *(params or []))
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def execute_insert(self, query: str, params: List[Any] = None) -> str:
        """执行插入返回ID"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetchval(query, *(params or []))
                return str(result)
            except Exception as e:
                logger.error(f"Insert execution failed: {e}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def execute_update(self, query: str, params: List[Any] = None) -> int:
        """执行更新返回影响行数"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(query, *(params or []))
                return int(result.split()[-1])  # 解析 "UPDATE 1" 中的数字
            except Exception as e:
                logger.error(f"Update execution failed: {e}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_cache(self, key: str) -> Optional[str]:
        """获取缓存"""
        if not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    async def set_cache(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    async def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False


