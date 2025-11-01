#!/usr/bin/env python3
"""
直接测试ClickHouse连接
"""
import socket
import time

def test_clickhouse_tcp():
    """测试ClickHouse TCP连接"""
    try:
        # 测试9000端口（原生协议）
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 9000))
        sock.close()
        
        if result == 0:
            print("✓ ClickHouse TCP端口9000连接成功")
            return True
        else:
            print("✗ ClickHouse TCP端口9000连接失败")
            return False
    except Exception as e:
        print(f"✗ ClickHouse TCP连接错误: {e}")
        return False

def test_clickhouse_http():
    """测试ClickHouse HTTP连接"""
    try:
        # 测试8123端口（HTTP接口）
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8123))
        sock.close()
        
        if result == 0:
            print("✓ ClickHouse HTTP端口8123连接成功")
            return True
        else:
            print("✗ ClickHouse HTTP端口8123连接失败")
            return False
    except Exception as e:
        print(f"✗ ClickHouse HTTP连接错误: {e}")
        return False

def test_clickhouse_with_requests():
    """使用requests库测试ClickHouse HTTP"""
    try:
        import requests
        
        # 等待ClickHouse完全启动
        time.sleep(2)
        
        # 测试简单查询
        url = "http://localhost:8123"
        params = {'query': 'SELECT 1'}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ ClickHouse HTTP查询成功: {response.text.strip()}")
            return True
        else:
            print(f"✗ ClickHouse HTTP查询失败: {response.status_code}")
            return False
            
    except ImportError:
        print("✗ requests库未安装，跳过HTTP测试")
        return False
    except Exception as e:
        print(f"✗ ClickHouse HTTP查询错误: {e}")
        return False

def main():
    print("=== ClickHouse连接测试 ===\n")
    
    # 测试1: TCP连接
    print("1. 测试ClickHouse TCP连接:")
    tcp_ok = test_clickhouse_tcp()
    
    # 测试2: HTTP连接
    print("\n2. 测试ClickHouse HTTP连接:")
    http_ok = test_clickhouse_http()
    
    # 测试3: HTTP查询
    print("\n3. 测试ClickHouse HTTP查询:")
    query_ok = test_clickhouse_with_requests()
    
    print(f"\n=== 测试结果 ===")
    print(f"TCP连接: {'✓ 成功' if tcp_ok else '✗ 失败'}")
    print(f"HTTP连接: {'✓ 成功' if http_ok else '✗ 失败'}")
    print(f"HTTP查询: {'✓ 成功' if query_ok else '✗ 失败'}")
    
    if tcp_ok and http_ok:
        print("\n🎉 ClickHouse基础连接正常！")
        if query_ok:
            print("🎉 ClickHouse HTTP查询也正常！可以继续开发。")
        else:
            print("⚠️ HTTP查询有问题，但TCP连接正常，可以继续开发。")
    else:
        print("\n❌ ClickHouse连接有问题，请检查Docker配置。")

if __name__ == "__main__":
    main()






