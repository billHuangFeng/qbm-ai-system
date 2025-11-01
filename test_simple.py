#!/usr/bin/env python3
import requests

print("测试前端服务:")
try:
    r = requests.get('http://localhost:3000')
    print(f"状态码: {r.status_code}")
    print(f"内容类型: {r.headers.get('content-type', 'unknown')}")
    print(f"内容长度: {len(r.text)} 字节")
    print("✅ 前端服务访问成功")
except Exception as e:
    print(f"❌ 前端服务访问失败: {e}")

print("\n测试后端API:")
try:
    r = requests.get('http://localhost:8000/health')
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text[:100]}...")
    print("✅ 后端API访问成功")
except Exception as e:
    print(f"❌ 后端API访问失败: {e}")






