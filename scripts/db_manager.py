"""
数据库管理脚本
"""
import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.init_database import main as init_db
from database.seeds.sample_data import main as seed_data

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    try:
        init_db()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    return True

def seed_database():
    """创建示例数据"""
    print("创建示例数据...")
    try:
        seed_data()
        print("示例数据创建成功！")
    except Exception as e:
        print(f"示例数据创建失败: {e}")
        return False
    return True

def reset_database():
    """重置数据库"""
    print("重置数据库...")
    try:
        # 删除所有表
        from backend.app.database import drop_tables
        drop_tables()
        print("数据库表删除成功")
        
        # 重新初始化
        init_database()
        seed_database()
        print("数据库重置成功！")
    except Exception as e:
        print(f"数据库重置失败: {e}")
        return False
    return True

def backup_database():
    """备份数据库"""
    print("备份数据库...")
    try:
        import subprocess
        from datetime import datetime
        
        # 创建备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_qbm_ai_system_{timestamp}.sql"
        
        # 执行备份命令
        cmd = [
            "mysqldump",
            "-h", "localhost",
            "-u", "root",
            "-ppassword",
            "qbm_ai_system"
        ]
        
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
        
        print(f"数据库备份成功: {backup_file}")
    except Exception as e:
        print(f"数据库备份失败: {e}")
        return False
    return True

def restore_database(backup_file):
    """恢复数据库"""
    print(f"恢复数据库: {backup_file}")
    try:
        import subprocess
        
        # 执行恢复命令
        cmd = [
            "mysql",
            "-h", "localhost",
            "-u", "root",
            "-ppassword",
            "qbm_ai_system"
        ]
        
        with open(backup_file, 'r') as f:
            subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE)
        
        print("数据库恢复成功！")
    except Exception as e:
        print(f"数据库恢复失败: {e}")
        return False
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("action", choices=["init", "seed", "reset", "backup", "restore"], 
                       help="要执行的操作")
    parser.add_argument("--backup-file", help="备份文件路径（用于恢复操作）")
    
    args = parser.parse_args()
    
    if args.action == "init":
        success = init_database()
    elif args.action == "seed":
        success = seed_database()
    elif args.action == "reset":
        success = reset_database()
    elif args.action == "backup":
        success = backup_database()
    elif args.action == "restore":
        if not args.backup_file:
            print("错误: 恢复操作需要指定备份文件路径")
            return
        success = restore_database(args.backup_file)
    
    if success:
        print("操作完成！")
    else:
        print("操作失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
