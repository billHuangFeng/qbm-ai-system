#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端服务是否运行
"""

import sys
import io
import urllib.request
import json
import time

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_backend():
    print("=" * 50)
    print("测试后端服务")
    print("=" * 50)
    print()
    
    url = "http://localhost:8000/health"
    
    print(f"[1] 检查端口 8000...")
    import subprocess
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True
    )
    if ":8000" in result.stdout and "LISTENING" in result.stdout:
        print("    [OK] 端口 8000 正在监听")
    else:
        print("    [ERROR] 端口 8000 未监听")
        return False
    
    print()
    print(f"[2] 检查健康检查端点: {url}")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            print("    [OK] 后端服务运行正常！")
            print()
            print("状态信息:")
            print(f"  - 状态: {data.get('status', 'unknown')}")
            print(f"  - 数据库: {data.get('database', 'unknown')}")
            print(f"  - Redis: {data.get('redis', 'unknown')}")
            print(f"  - 版本: {data.get('version', 'unknown')}")
            print()
            print("服务地址:")
            print("  - API: http://localhost:8000")
            print("  - 健康检查: http://localhost:8000/health")
            print("  - API文档: http://localhost:8000/docs")
            print("  - ReDoc: http://localhost:8000/redoc")
            print()
            return True
            
        except Exception as e:
            if i < max_retries - 1:
                print(f"    ⏳ 等待服务启动... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"    [ERROR] 服务未响应: {e}")
                print()
                print("可能的原因:")
                print("  1. 服务正在启动中，请稍等片刻")
                print("  2. 服务启动失败，请查看控制台错误信息")
                print("  3. 端口被占用，请检查是否有其他服务在使用8000端口")
                return False
    
    return False

if __name__ == "__main__":
    test_backend()

