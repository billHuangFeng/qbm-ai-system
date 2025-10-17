"""
数据库初始化脚本
"""
import os
import sys
import pymysql
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import engine, create_tables
from backend.app.models import *

# 加载环境变量
load_dotenv()

def create_database():
    """创建数据库"""
    # 获取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "qbm_ai_system")
    
    # 连接MySQL服务器（不指定数据库）
    connection = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {db_name} 创建成功")
            
            # 使用数据库
            cursor.execute(f"USE {db_name}")
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"当前数据库中的表: {[table[0] for table in tables]}")
            
    finally:
        connection.close()

def init_tables():
    """初始化数据表"""
    try:
        # 创建所有表
        create_tables()
        print("数据表创建成功")
        
        # 验证表是否创建成功
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"创建的表: {tables}")
            
    except Exception as e:
        print(f"创建数据表时出错: {e}")
        raise

def check_database_connection():
    """检查数据库连接"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("数据库连接成功")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    # 检查数据库连接
    if not check_database_connection():
        print("正在创建数据库...")
        create_database()
    
    # 初始化数据表
    init_tables()
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    main()
