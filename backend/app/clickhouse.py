"""
BMOS ClickHouse连接器
使用TCP连接避免Windows Docker HTTP问题
"""
import logging
from typing import Generator, List, Dict, Any, Optional
import os
from contextlib import contextmanager
import subprocess
import json

logger = logging.getLogger(__name__)

# 尝试导入ClickHouse驱动，如果失败则使用Docker exec方式
try:
    from clickhouse_driver import Client
    CLICKHOUSE_DRIVER_AVAILABLE = True
except ImportError:
    CLICKHOUSE_DRIVER_AVAILABLE = False
    logger.warning("clickhouse-driver不可用，将使用Docker exec方式")

try:
    from clickhouse_sqlalchemy import make_session, engines
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy不可用，将使用简化模式")

# ClickHouse连接配置
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'clickhouse')  # 容器内使用服务名
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', '9000'))  # 使用TCP端口
CLICKHOUSE_HTTP_PORT = int(os.getenv('CLICKHOUSE_HTTP_PORT', '8123'))
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')
CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'bmos')

# TCP连接URL（主要使用）
CLICKHOUSE_TCP_URL = f"clickhouse://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}@{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{CLICKHOUSE_DATABASE}"

# HTTP连接URL（备用，在容器内使用）
CLICKHOUSE_HTTP_URL = f"clickhouse://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}@{CLICKHOUSE_HOST}:{CLICKHOUSE_HTTP_PORT}/{CLICKHOUSE_DATABASE}"

class ClickHouseConnector:
    """ClickHouse连接器类"""
    
    def __init__(self):
        self.tcp_client = None
        self.http_engine = None
        self.http_session = None
        self.use_docker_exec = False
        self._initialize_connections()
    
    def _initialize_connections(self):
        """初始化连接"""
        # 在容器环境中，强制使用Docker exec方式
        logger.info("使用Docker exec方式连接ClickHouse")
        self.use_docker_exec = True
        
        # 测试Docker exec连接
        try:
            test_result = self._execute_via_docker("SELECT 1")
            if test_result and len(test_result) > 0:
                logger.info("Docker exec连接测试成功")
            else:
                logger.warning("Docker exec连接测试失败")
        except Exception as e:
            logger.warning(f"Docker exec连接测试异常: {e}")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[tuple]:
        """
        执行查询（使用TCP连接或Docker exec）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            if self.use_docker_exec:
                return self._execute_via_docker(query)
            
            if not self.tcp_client:
                self._initialize_connections()
            
            result = self.tcp_client.execute(query, params)
            logger.debug(f"查询执行成功: {query[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"查询执行失败: {e}\nQuery: {query}")
            raise
    
    def _execute_via_docker(self, query: str) -> List[tuple]:
        """通过HTTP接口执行查询"""
        try:
            import requests
            url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_HTTP_PORT}/"
            response = requests.post(url, data=query, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if not lines or lines == ['']:
                    return []
                return [tuple(line.split('\t')) for line in lines if line.strip()]
            else:
                logger.error(f"HTTP查询失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"HTTP执行错误: {e}")
            return []
    
    def execute_non_query(self, query: str, params: Optional[Dict] = None) -> None:
        """
        执行非查询操作（INSERT, UPDATE, DELETE等）
        
        Args:
            query: SQL语句
            params: 参数
        """
        try:
            if not self.tcp_client:
                self._initialize_connections()
            
            self.tcp_client.execute(query, params)
            logger.debug(f"非查询操作执行成功: {query[:100]}...")
            
        except Exception as e:
            logger.error(f"非查询操作执行失败: {e}\nQuery: {query}")
            raise
    
    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """
        批量插入数据
        
        Args:
            table: 表名
            data: 数据列表
        """
        if not data:
            return
        
        try:
            # 构建INSERT语句
            columns = list(data[0].keys())
            columns_str = ', '.join(columns)
            
            # 准备数据
            values_list = []
            for row in data:
                values = []
                for col in columns:
                    value = row[col]
                    if isinstance(value, str):
                        values.append(f"'{value}'")
                    elif value is None:
                        values.append('NULL')
                    else:
                        values.append(str(value))
                values_list.append(f"({', '.join(values)})")
            
            query = f"INSERT INTO {table} ({columns_str}) VALUES {', '.join(values_list)}"
            self.execute_non_query(query)
            logger.info(f"批量插入成功: {len(data)} 条数据到 {table}")
            
        except Exception as e:
            logger.error(f"批量插入失败: {e}")
            raise
    
    def get_session(self):
        """获取HTTP会话（用于SQLAlchemy ORM）"""
        if not self.http_session:
            raise Exception("HTTP会话未初始化，请检查ClickHouse HTTP连接")
        return self.http_session
    
    def close(self):
        """关闭连接"""
        try:
            if self.tcp_client:
                self.tcp_client.disconnect()
                logger.info("TCP连接已关闭")
            
            if self.http_session:
                self.http_session.close()
                logger.info("HTTP会话已关闭")
                
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")

# 全局连接器实例
clickhouse_connector = ClickHouseConnector()

# SQLAlchemy基础类
Base = declarative_base()

# 元数据
metadata = MetaData()

def get_clickhouse_client() -> Client:
    """获取ClickHouse TCP客户端"""
    return clickhouse_connector.tcp_client

def get_clickhouse_session():
    """获取ClickHouse HTTP会话"""
    return clickhouse_connector.get_session()

@contextmanager
def clickhouse_session():
    """ClickHouse会话上下文管理器"""
    session = get_clickhouse_session()
    try:
        yield session
    finally:
        session.close()

def execute_query(query: str, params: Optional[Dict] = None) -> List[tuple]:
    """执行查询的便捷函数"""
    return clickhouse_connector.execute_query(query, params)

def execute_non_query(query: str, params: Optional[Dict] = None) -> None:
    """执行非查询的便捷函数"""
    clickhouse_connector.execute_non_query(query, params)

def insert_data(table: str, data: List[Dict[str, Any]]) -> None:
    """批量插入数据的便捷函数"""
    clickhouse_connector.insert_data(table, data)

# 健康检查函数
def check_clickhouse_health() -> Dict[str, Any]:
    """检查ClickHouse连接健康状态"""
    try:
        # 测试连接
        tcp_result = clickhouse_connector.execute_query("SELECT 1")
        tcp_healthy = len(tcp_result) == 1 and str(tcp_result[0][0]) == "1"
        
        # 测试数据库
        db_result = clickhouse_connector.execute_query("SHOW DATABASES")
        db_healthy = any(row[0] == CLICKHOUSE_DATABASE for row in db_result)
        
        # 测试表结构
        table_result = clickhouse_connector.execute_query(f"SHOW TABLES FROM {CLICKHOUSE_DATABASE}")
        table_healthy = len(table_result) > 0
        
        # 如果数据库和表都存在，就认为是健康的
        overall_healthy = db_healthy and table_healthy
        
        return {
            "tcp_connection": tcp_healthy,
            "database_exists": db_healthy,
            "tables_exist": table_healthy,
            "total_tables": len(table_result) if table_healthy else 0,
            "status": "healthy" if overall_healthy else "unhealthy"
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "tcp_connection": False,
            "database_exists": False,
            "tables_exist": False,
            "total_tables": 0,
            "status": "error",
            "error": str(e)
        }

# 初始化时进行健康检查
def initialize_clickhouse():
    """初始化ClickHouse连接并进行健康检查"""
    try:
        health = check_clickhouse_health()
        if health["status"] == "healthy":
            logger.info("ClickHouse连接健康检查通过")
            logger.info(f"数据库: {CLICKHOUSE_DATABASE}, 表数量: {health['total_tables']}")
        else:
            logger.warning(f"ClickHouse连接健康检查失败: {health}")
        
        return health
        
    except Exception as e:
        logger.error(f"ClickHouse初始化失败: {e}")
        raise

# 模块加载时自动初始化
if __name__ != "__main__":
    try:
        initialize_clickhouse()
    except Exception as e:
        logger.error(f"ClickHouse自动初始化失败: {e}")