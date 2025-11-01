#!/usr/bin/env python3
"""
测试VPN环境下的BMOS系统访问
"""
import requests
import socket
import subprocess

def test_network_connectivity():
    """测试网络连通性"""
    print("=== 测试网络连通性 ===")
    
    # 测试容器IP连通性
    print("1. 测试容器IP连通性...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('172.21.0.4', 3000))
        sock.close()
        if result == 0:
            print("✅ 前端容器IP连通")
        else:
            print("❌ 前端容器IP不通")
    except Exception as e:
        print(f"❌ 前端容器IP测试失败: {e}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('172.21.0.7', 8000))
        sock.close()
        if result == 0:
            print("✅ 后端容器IP连通")
        else:
            print("❌ 后端容器IP不通")
    except Exception as e:
        print(f"❌ 后端容器IP测试失败: {e}")
    
    # 测试localhost连通性
    print("\n2. 测试localhost连通性...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 3000))
        sock.close()
        if result == 0:
            print("✅ 前端localhost连通")
        else:
            print("❌ 前端localhost不通")
    except Exception as e:
        print(f"❌ 前端localhost测试失败: {e}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            print("✅ 后端localhost连通")
        else:
            print("❌ 后端localhost不通")
    except Exception as e:
        print(f"❌ 后端localhost测试失败: {e}")

def test_http_access():
    """测试HTTP访问"""
    print("\n=== 测试HTTP访问 ===")
    
    # 测试后端API
    print("1. 测试后端API...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ 后端API访问成功")
            print(f"   状态码: {response.status_code}")
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
        else:
            print(f"❌ 前端服务访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端服务访问失败: {e}")
    
    # 测试容器IP访问
    print("\n3. 测试容器IP访问...")
    try:
        response = requests.get('http://172.21.0.4:3000', timeout=10)
        if response.status_code == 200:
            print("✅ 前端容器IP访问成功")
        else:
            print(f"❌ 前端容器IP访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端容器IP访问失败: {e}")

def get_network_info():
    """获取网络信息"""
    print("\n=== 网络信息 ===")
    
    # 获取路由表
    print("1. 路由表信息...")
    try:
        result = subprocess.run(['route', 'print'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 路由表获取成功")
            # 查找Docker相关路由
            lines = result.stdout.split('\n')
            docker_routes = [line for line in lines if '172.21' in line or 'Docker' in line]
            if docker_routes:
                print("   Docker相关路由:")
                for route in docker_routes[:3]:  # 只显示前3个
                    print(f"   {route.strip()}")
            else:
                print("   未找到Docker相关路由")
        else:
            print("❌ 路由表获取失败")
    except Exception as e:
        print(f"❌ 路由表获取失败: {e}")
    
    # 获取网络适配器
    print("\n2. 网络适配器信息...")
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 网络适配器信息获取成功")
            # 查找VPN相关适配器
            lines = result.stdout.split('\n')
            vpn_adapters = [line for line in lines if 'VPN' in line or 'TAP' in line or 'OpenVPN' in line]
            if vpn_adapters:
                print("   检测到VPN适配器:")
                for adapter in vpn_adapters[:3]:  # 只显示前3个
                    print(f"   {adapter.strip()}")
            else:
                print("   未检测到明显的VPN适配器")
        else:
            print("❌ 网络适配器信息获取失败")
    except Exception as e:
        print(f"❌ 网络适配器信息获取失败: {e}")

def main():
    """主函数"""
    print("=== VPN环境下的BMOS系统访问测试 ===\n")
    
    # 测试网络连通性
    test_network_connectivity()
    
    # 测试HTTP访问
    test_http_access()
    
    # 获取网络信息
    get_network_info()
    
    print("\n=== 测试完成 ===")
    print("\n💡 VPN问题解决建议:")
    print("1. 临时关闭VPN测试访问")
    print("2. 配置VPN绕过Docker网络段")
    print("3. 使用容器内访问方式")
    print("4. 配置VPN的本地网络绕过")

if __name__ == "__main__":
    main()





