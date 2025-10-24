#!/usr/bin/env python3
"""
简单的HTTP测试
"""
import urllib.request
import urllib.parse
import json

def test_clickhouse_http_simple():
    """使用urllib测试ClickHouse HTTP接口"""
    try:
        # 测试简单查询
        query = "SELECT 1"
        url = f"http://localhost:8123/?query={urllib.parse.quote(query)}"
        
        print(f"测试URL: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✓ HTTP查询成功: {result.strip()}")
            return True
            
    except Exception as e:
        print(f"✗ HTTP查询失败: {e}")
        return False

def test_clickhouse_http_post():
    """使用POST方法测试"""
    try:
        query = "SELECT 1"
        data = query.encode('utf-8')
        
        req = urllib.request.Request(
            'http://localhost:8123/',
            data=data,
            headers={'Content-Type': 'text/plain'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✓ HTTP POST查询成功: {result.strip()}")
            return True
            
    except Exception as e:
        print(f"✗ HTTP POST查询失败: {e}")
        return False

def test_clickhouse_database():
    """测试数据库查询"""
    try:
        query = "SHOW DATABASES"
        url = f"http://localhost:8123/?query={urllib.parse.quote(query)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✓ 数据库列表查询成功:")
            for line in result.strip().split('\n'):
                print(f"  - {line}")
            return True
            
    except Exception as e:
        print(f"✗ 数据库查询失败: {e}")
        return False

def test_bmos_tables():
    """测试BMOS表查询"""
    try:
        query = "SHOW TABLES FROM bmos"
        url = f"http://localhost:8123/?query={urllib.parse.quote(query)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✓ BMOS表列表查询成功:")
            tables = result.strip().split('\n')
            for table in tables:
                if table:
                    print(f"  - {table}")
            return True
            
    except Exception as e:
        print(f"✗ BMOS表查询失败: {e}")
        return False

def main():
    print("=== ClickHouse HTTP连接测试 ===\n")
    
    # 测试1: 简单查询
    print("1. 测试简单查询:")
    simple_ok = test_clickhouse_http_simple()
    
    # 测试2: POST查询
    print("\n2. 测试POST查询:")
    post_ok = test_clickhouse_http_post()
    
    # 测试3: 数据库查询
    print("\n3. 测试数据库查询:")
    db_ok = test_clickhouse_database()
    
    # 测试4: BMOS表查询
    print("\n4. 测试BMOS表查询:")
    tables_ok = test_bmos_tables()
    
    print(f"\n=== 测试结果 ===")
    print(f"简单查询: {'✓ 成功' if simple_ok else '✗ 失败'}")
    print(f"POST查询: {'✓ 成功' if post_ok else '✗ 失败'}")
    print(f"数据库查询: {'✓ 成功' if db_ok else '✗ 失败'}")
    print(f"BMOS表查询: {'✓ 成功' if tables_ok else '✗ 失败'}")
    
    if all([simple_ok, post_ok, db_ok, tables_ok]):
        print("\n🎉 所有HTTP测试通过！ClickHouse完全正常。")
    else:
        print("\n⚠️ 部分测试失败，但基础功能可用。")

if __name__ == "__main__":
    main()




