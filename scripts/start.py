#!/usr/bin/env python3
"""
启动脚本
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def start_services():
    """启动所有服务"""
    print("🚀 启动QBM AI System...")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # 启动Docker Compose服务
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ 服务启动命令已执行")
        print("⏳ 等待服务完全启动...")
        
        # 等待服务启动
        time.sleep(30)
        
        # 运行健康检查
        health_check_script = project_root / "scripts" / "health_check.py"
        result = subprocess.run([sys.executable, str(health_check_script)], check=False)
        
        if result.returncode == 0:
            print("🎉 系统启动成功!")
            print("🌐 前端访问地址: http://localhost:8080")
            print("🔧 后端API地址: http://localhost:8000")
            print("📊 API文档地址: http://localhost:8000/docs")
        else:
            print("⚠️  系统启动完成，但健康检查未通过")
            print("请检查服务日志: docker-compose logs")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False

def stop_services():
    """停止所有服务"""
    print("🛑 停止QBM AI System...")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ 服务已停止")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 停止失败: {e}")
        return False

def restart_services():
    """重启所有服务"""
    print("🔄 重启QBM AI System...")
    
    if stop_services():
        time.sleep(5)
        return start_services()
    return False

def show_status():
    """显示服务状态"""
    print("📊 服务状态:")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        subprocess.run(["docker-compose", "ps"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取状态失败: {e}")

def show_logs():
    """显示服务日志"""
    print("📋 服务日志:")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        subprocess.run(["docker-compose", "logs", "--tail=50"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取日志失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QBM AI System 启动脚本")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "logs"], 
                       help="操作类型")
    
    args = parser.parse_args()
    
    if args.action == "start":
        success = start_services()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        success = stop_services()
        sys.exit(0 if success else 1)
    elif args.action == "restart":
        success = restart_services()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        show_status()
    elif args.action == "logs":
        show_logs()

if __name__ == "__main__":
    main()





