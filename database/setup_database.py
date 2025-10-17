"""
数据库设置脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_database():
    """设置数据库"""
    print("开始设置数据库...")
    
    # 检查Python依赖
    try:
        import pymysql
        import sqlalchemy
        from dotenv import load_dotenv
        print("Python依赖检查通过")
    except ImportError as e:
        print(f"缺少Python依赖: {e}")
        print("请运行: pip install pymysql sqlalchemy python-dotenv")
        return False
    
    # 检查MySQL是否运行
    try:
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='password'
        )
        connection.close()
        print("MySQL连接检查通过")
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        print("请确保MySQL服务正在运行，并且用户名密码正确")
        return False
    
    # 运行数据库初始化
    try:
        print("正在初始化数据库...")
        from init_database import main as init_main
        init_main()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    
    # 运行示例数据创建
    try:
        print("正在创建示例数据...")
        from seeds.sample_data import main as seed_main
        seed_main()
        print("示例数据创建完成")
    except Exception as e:
        print(f"示例数据创建失败: {e}")
        return False
    
    print("数据库设置完成！")
    return True

def main():
    """主函数"""
    if setup_database():
        print("\n数据库设置成功！")
        print("您现在可以启动应用程序了。")
    else:
        print("\n数据库设置失败！")
        print("请检查错误信息并重试。")

if __name__ == "__main__":
    main()
