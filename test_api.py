#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 测试QBM AI System的API端点
"""
import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread

def start_server():
    """启动服务器"""
    print("启动测试服务器...")
    try:
        # 启动服务器进程
        server_process = subprocess.Popen([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'start_server.py')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        return server_process
    except Exception as e:
        print(f"启动服务器失败: {e}")
        return None

def test_api_endpoint(url, expected_status=200):
    """测试API端点"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"[OK] {url} - 状态码: {response.status_code}")
            try:
                data = response.json()
                print(f"    响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except:
                print(f"    响应内容: {response.text[:100]}...")
            return True
        else:
            print(f"[FAIL] {url} - 状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {url} - 连接失败")
        return False
    except Exception as e:
        print(f"[FAIL] {url} - 错误: {e}")
        return False

def main():
    """主函数"""
    print("QBM AI System API测试")
    print("=" * 50)
    
    # 启动服务器
    server_process = start_server()
    if not server_process:
        print("无法启动服务器，测试终止")
        return
    
    try:
        # 等待服务器完全启动
        print("等待服务器启动...")
        time.sleep(2)
        
        # 测试API端点
        endpoints = [
            "http://localhost:8000/",
            "http://localhost:8000/health", 
            "http://localhost:8000/test",
            "http://localhost:8000/api/status"
        ]
        
        passed = 0
        total = len(endpoints)
        
        print("\n开始测试API端点...")
        for endpoint in endpoints:
            if test_api_endpoint(endpoint):
                passed += 1
            print()  # 空行分隔
        
        # 输出测试结果
        print("=" * 50)
        print("API测试结果:")
        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {total - passed}")
        print(f"成功率: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n所有API测试通过！")
            print("\n可以访问以下地址:")
            print("  - 主页: http://localhost:8000/")
            print("  - API文档: http://localhost:8000/docs")
            print("  - 交互式API: http://localhost:8000/redoc")
            
            # 保持服务器运行
            print("\n服务器正在运行，按 Ctrl+C 停止...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在停止服务器...")
        else:
            print(f"\n有 {total - passed} 个API测试失败")
    
    finally:
        # 停止服务器
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("服务器已停止")

if __name__ == "__main__":
    main()





