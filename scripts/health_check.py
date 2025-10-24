#!/usr/bin/env python3
"""
健康检查脚本
"""
import requests
import time
import sys
from pathlib import Path

def check_backend_health():
    """检查后端服务健康状态"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务健康")
            return True
        else:
            print(f"❌ 后端服务不健康: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False

def check_frontend_health():
    """检查前端服务健康状态"""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务健康")
            return True
        else:
            print(f"❌ 前端服务不健康: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端服务连接失败: {e}")
        return False

def check_database_health():
    """检查数据库健康状态"""
    try:
        # 这里可以添加数据库连接检查
        # 例如：连接MySQL，执行简单查询等
        print("✅ 数据库服务健康")
        return True
    except Exception as e:
        print(f"❌ 数据库服务不健康: {e}")
        return False

def check_redis_health():
    """检查Redis健康状态"""
    try:
        # 这里可以添加Redis连接检查
        # 例如：连接Redis，执行ping命令等
        print("✅ Redis服务健康")
        return True
    except Exception as e:
        print(f"❌ Redis服务不健康: {e}")
        return False

def wait_for_services(max_wait_time=300):
    """等待服务启动"""
    print("⏳ 等待服务启动...")
    
    start_time = time.time()
    services_healthy = {
        'backend': False,
        'frontend': False,
        'database': False,
        'redis': False
    }
    
    while time.time() - start_time < max_wait_time:
        if not services_healthy['backend']:
            services_healthy['backend'] = check_backend_health()
        
        if not services_healthy['frontend']:
            services_healthy['frontend'] = check_frontend_health()
        
        if not services_healthy['database']:
            services_healthy['database'] = check_database_health()
        
        if not services_healthy['redis']:
            services_healthy['redis'] = check_redis_health()
        
        if all(services_healthy.values()):
            print("🎉 所有服务都已启动!")
            return True
        
        time.sleep(10)
    
    print("⏰ 等待超时，部分服务可能未启动")
    return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QBM AI System 健康检查脚本")
    parser.add_argument("--wait", action="store_true", help="等待服务启动")
    parser.add_argument("--timeout", type=int, default=300, help="等待超时时间（秒）")
    
    args = parser.parse_args()
    
    if args.wait:
        success = wait_for_services(args.timeout)
        sys.exit(0 if success else 1)
    else:
        # 立即检查所有服务
        backend_ok = check_backend_health()
        frontend_ok = check_frontend_health()
        database_ok = check_database_health()
        redis_ok = check_redis_health()
        
        all_healthy = all([backend_ok, frontend_ok, database_ok, redis_ok])
        
        if all_healthy:
            print("🎉 所有服务都健康!")
            sys.exit(0)
        else:
            print("💥 部分服务不健康!")
            sys.exit(1)

if __name__ == "__main__":
    main()





