#!/usr/bin/env python3
"""
测试localhost访问BMOS系统
"""
import requests
import time

def test_localhost_access():
    """测试localhost访问"""
    print("=== 测试localhost访问BMOS系统 ===\n")
    
    # 测试后端API
    print("1. 测试后端API...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ 后端API访问成功")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text[:100]}...")
        else:
            print(f"❌ 后端API访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端API访问失败: {e}")
    
    # 测试前端服务
    print("\n2. 测试前端服务...")
    try:
        response = requests.get('http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ 前端服务访问成功")
            print(f"   状态码: {response.status_code}")
            print(f"   内容类型: {response.headers.get('content-type', 'unknown')}")
            print(f"   内容长度: {len(response.text)} 字节")
        else:
            print(f"❌ 前端服务访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端服务访问失败: {e}")
    
    # 测试API代理
    print("\n3. 测试API代理...")
    try:
        response = requests.get('http://localhost:3000/api/v1/bmos/status', timeout=10)
        if response.status_code == 200:
            print("✅ API代理访问成功")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text[:100]}...")
        else:
            print(f"❌ API代理访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ API代理访问失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n💡 如果测试失败，请:")
    print("1. 以管理员身份运行 run_as_admin.bat")
    print("2. 检查Windows防火墙设置")
    print("3. 重启Docker Desktop")

if __name__ == "__main__":
    test_localhost_access()





