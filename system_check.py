#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统状态检查脚本 - QBM AI System
"""
import os
import sys
import subprocess
import requests
import json
from datetime import datetime

def check_python_environment():
    """检查Python环境"""
    print("检查Python环境...")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查关键包
    packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pymysql', 
        'pandas', 'sklearn', 'requests', 'pydantic'
    ]
    
    missing_packages = []
    for package in packages:
        try:
            __import__(package)
            print(f"[OK] {package} 已安装")
        except ImportError:
            print(f"[FAIL] {package} 未安装")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    
    required_dirs = [
        'backend', 'frontend', 'ai_engine', 'database', 'scripts'
    ]
    
    required_files = [
        'start_server.py', 'basic_test.py', 'test_api.py',
        'docker-compose.yml', 'README.md'
    ]
    
    all_good = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] 目录 {dir_name} 存在")
        else:
            print(f"[FAIL] 目录 {dir_name} 不存在")
            all_good = False
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"[OK] 文件 {file_name} 存在")
        else:
            print(f"[FAIL] 文件 {file_name} 不存在")
            all_good = False
    
    return all_good

def check_backend_structure():
    """检查后端结构"""
    print("\n检查后端结构...")
    
    backend_dirs = [
        'backend/app', 'backend/app/api', 'backend/app/models',
        'backend/app/crud', 'backend/app/schemas', 'backend/app/core'
    ]
    
    backend_files = [
        'backend/app/main.py', 'backend/app/database.py',
        'backend/requirements.txt'
    ]
    
    all_good = True
    
    for dir_name in backend_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] 后端目录 {dir_name} 存在")
        else:
            print(f"[FAIL] 后端目录 {dir_name} 不存在")
            all_good = False
    
    for file_name in backend_files:
        if os.path.exists(file_name):
            print(f"[OK] 后端文件 {file_name} 存在")
        else:
            print(f"[FAIL] 后端文件 {file_name} 不存在")
            all_good = False
    
    return all_good

def check_frontend_structure():
    """检查前端结构"""
    print("\n检查前端结构...")
    
    frontend_dirs = [
        'frontend/src', 'frontend/src/components', 'frontend/src/views',
        'frontend/src/api', 'frontend/src/store', 'frontend/src/router'
    ]
    
    frontend_files = [
        'frontend/package.json', 'frontend/vite.config.js',
        'frontend/src/main.js'
    ]
    
    all_good = True
    
    for dir_name in frontend_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] 前端目录 {dir_name} 存在")
        else:
            print(f"[FAIL] 前端目录 {dir_name} 不存在")
            all_good = False
    
    for file_name in frontend_files:
        if os.path.exists(file_name):
            print(f"[OK] 前端文件 {file_name} 存在")
        else:
            print(f"[FAIL] 前端文件 {file_name} 不存在")
            all_good = False
    
    return all_good

def check_ai_engine_structure():
    """检查AI引擎结构"""
    print("\n检查AI引擎结构...")
    
    ai_dirs = [
        'ai_engine', 'ai_engine/analyzers', 'ai_engine/utils',
        'ai_engine/models', 'ai_engine/predictors'
    ]
    
    ai_files = [
        'ai_engine/__init__.py', 'ai_engine/utils/data_processor.py'
    ]
    
    all_good = True
    
    for dir_name in ai_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] AI引擎目录 {dir_name} 存在")
        else:
            print(f"[FAIL] AI引擎目录 {dir_name} 不存在")
            all_good = False
    
    for file_name in ai_files:
        if os.path.exists(file_name):
            print(f"[OK] AI引擎文件 {file_name} 存在")
        else:
            print(f"[FAIL] AI引擎文件 {file_name} 不存在")
            all_good = False
    
    return all_good

def check_docker_environment():
    """检查Docker环境"""
    print("\n检查Docker环境...")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] Docker已安装: {result.stdout.strip()}")
        else:
            print("[FAIL] Docker未正确安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("[FAIL] Docker未安装或无法访问")
        return False
    
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] Docker Compose已安装: {result.stdout.strip()}")
        else:
            print("[FAIL] Docker Compose未正确安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("[FAIL] Docker Compose未安装或无法访问")
        return False
    
    return True

def check_api_server():
    """检查API服务器状态"""
    print("\n检查API服务器状态...")
    
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/health",
        "http://localhost:8000/test"
    ]
    
    server_running = False
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                print(f"[OK] API端点 {endpoint} 响应正常")
                server_running = True
            else:
                print(f"[FAIL] API端点 {endpoint} 响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[INFO] API端点 {endpoint} 无法连接（服务器可能未启动）")
        except Exception as e:
            print(f"[FAIL] API端点 {endpoint} 测试失败: {e}")
    
    return server_running

def check_file_sizes():
    """检查关键文件大小"""
    print("\n检查关键文件大小...")
    
    files_to_check = [
        'start_server.py', 'basic_test.py', 'test_api.py',
        'backend/app/main.py', 'frontend/package.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path}: {size} 字节")
        else:
            print(f"[FAIL] {file_path}: 文件不存在")

def generate_system_report():
    """生成系统报告"""
    print("\n" + "=" * 60)
    print("QBM AI System 系统状态报告")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        ("Python环境", check_python_environment),
        ("项目结构", check_project_structure),
        ("后端结构", check_backend_structure),
        ("前端结构", check_frontend_structure),
        ("AI引擎结构", check_ai_engine_structure),
        ("Docker环境", check_docker_environment),
        ("API服务器", check_api_server),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        try:
            if check_func():
                passed += 1
                print(f"[PASS] {check_name} 检查通过")
            else:
                print(f"[FAIL] {check_name} 检查失败")
        except Exception as e:
            print(f"[ERROR] {check_name} 检查异常: {e}")
    
    # 文件大小检查
    print(f"\n--- 文件大小检查 ---")
    check_file_sizes()
    
    # 总结
    print("\n" + "=" * 60)
    print("系统状态总结:")
    print(f"总检查项: {total}")
    print(f"通过检查: {passed}")
    print(f"失败检查: {total - passed}")
    print(f"通过率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n[SUCCESS] 系统状态良好，所有检查都通过！")
    elif passed >= total * 0.8:
        print("\n[WARNING] 系统基本正常，但有一些问题需要关注")
    else:
        print("\n[ERROR] 系统存在严重问题，需要修复")
    
    print("\n建议:")
    if passed < total:
        print("1. 检查失败的组件并修复")
        print("2. 确保所有依赖都已正确安装")
        print("3. 验证项目文件完整性")
    else:
        print("1. 系统运行正常，可以开始使用")
        print("2. 可以启动完整测试")
        print("3. 建议定期运行系统检查")

def main():
    """主函数"""
    print("QBM AI System 系统状态检查")
    print("=" * 60)
    
    generate_system_report()

if __name__ == "__main__":
    main()







