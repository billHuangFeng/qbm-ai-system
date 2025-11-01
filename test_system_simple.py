#!/usr/bin/env python3
"""
BMOS系统简单连接测试
不依赖复杂的Python包，使用基本的HTTP请求测试
"""
import requests
import json
import time
from datetime import datetime

def test_clickhouse_http():
    """通过HTTP接口测试ClickHouse"""
    try:
        # 测试ClickHouse HTTP接口
        url = "http://localhost:8123"
        
        # 简单查询测试
        response = requests.get(url, params={'query': 'SELECT 1'}, timeout=5)
        if response.status_code == 200:
            print("✓ ClickHouse HTTP接口连接成功")
            print(f"  响应: {response.text.strip()}")
            return True
        else:
            print(f"✗ ClickHouse HTTP接口连接失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ ClickHouse HTTP接口连接错误: {e}")
        return False

def test_redis_connection():
    """测试Redis连接（通过telnet方式）"""
    try:
        import socket
        
        # 尝试连接Redis
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 6380))
        sock.close()
        
        if result == 0:
            print("✓ Redis端口连接成功")
            return True
        else:
            print("✗ Redis端口连接失败")
            return False
            
    except Exception as e:
        print(f"✗ Redis连接测试错误: {e}")
        return False

def test_clickhouse_database_creation():
    """测试ClickHouse数据库创建"""
    try:
        # 创建测试数据库
        url = "http://localhost:8123"
        
        # 创建数据库
        create_db_query = "CREATE DATABASE IF NOT EXISTS bmos"
        response = requests.get(url, params={'query': create_db_query}, timeout=10)
        
        if response.status_code == 200:
            print("✓ 数据库 'bmos' 创建成功")
            
            # 测试创建表
            create_table_query = """
            CREATE TABLE IF NOT EXISTS bmos.test_table (
                id UInt32,
                name String,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY id
            """
            response = requests.get(url, params={'query': create_table_query}, timeout=10)
            
            if response.status_code == 200:
                print("✓ 测试表创建成功")
                
                # 插入测试数据
                insert_query = "INSERT INTO bmos.test_table (id, name) VALUES (1, 'test')"
                response = requests.get(url, params={'query': insert_query}, timeout=10)
                
                if response.status_code == 200:
                    print("✓ 测试数据插入成功")
                    
                    # 查询测试数据
                    select_query = "SELECT * FROM bmos.test_table"
                    response = requests.get(url, params={'query': select_query}, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✓ 测试数据查询成功: {response.text.strip()}")
                        return True
                    else:
                        print(f"✗ 测试数据查询失败: {response.status_code}")
                        return False
                else:
                    print(f"✗ 测试数据插入失败: {response.status_code}")
                    return False
            else:
                print(f"✗ 测试表创建失败: {response.status_code}")
                return False
        else:
            print(f"✗ 数据库创建失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ ClickHouse数据库测试错误: {e}")
        return False

def test_bmos_schema_creation():
    """测试BMOS核心表结构创建"""
    try:
        url = "http://localhost:8123"
        
        # 创建VPT维度表
        vpt_table_query = """
        CREATE TABLE IF NOT EXISTS bmos.dim_vpt (
            vpt_id String,
            vpt_name String,
            vpt_category String,
            vpt_description String,
            created_at DateTime DEFAULT now(),
            updated_at DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY (vpt_id)
        """
        
        response = requests.get(url, params={'query': vpt_table_query}, timeout=10)
        if response.status_code == 200:
            print("✓ VPT维度表创建成功")
        else:
            print(f"✗ VPT维度表创建失败: {response.status_code}")
            return False
        
        # 创建订单事实表
        order_table_query = """
        CREATE TABLE IF NOT EXISTS bmos.fact_order (
            order_id String,
            customer_id String,
            sku_id String,
            conv_channel_id String,
            order_date Date,
            order_timestamp DateTime,
            quantity UInt32,
            price_per_unit Float64,
            total_revenue Float64,
            total_cost Float64,
            profit Float64,
            order_status String,
            payment_method String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(order_date)
        ORDER BY (order_id, customer_id, sku_id, order_timestamp)
        """
        
        response = requests.get(url, params={'query': order_table_query}, timeout=10)
        if response.status_code == 200:
            print("✓ 订单事实表创建成功")
        else:
            print(f"✗ 订单事实表创建失败: {response.status_code}")
            return False
        
        # 插入测试数据
        test_vpt_data = """
        INSERT INTO bmos.dim_vpt (vpt_id, vpt_name, vpt_category, vpt_description) VALUES
        ('vpt001', '极速交付', 'delivery', '承诺24小时发货'),
        ('vpt002', '品质保证', 'quality', '100%正品保证'),
        ('vpt003', '贴心服务', 'service', '7x24小时客服')
        """
        
        response = requests.get(url, params={'query': test_vpt_data}, timeout=10)
        if response.status_code == 200:
            print("✓ 测试VPT数据插入成功")
        else:
            print(f"✗ 测试VPT数据插入失败: {response.status_code}")
            return False
        
        # 查询验证
        select_query = "SELECT * FROM bmos.dim_vpt ORDER BY vpt_id"
        response = requests.get(url, params={'query': select_query}, timeout=10)
        if response.status_code == 200:
            print(f"✓ VPT数据查询成功:")
            print(f"  {response.text.strip()}")
            return True
        else:
            print(f"✗ VPT数据查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ BMOS表结构测试错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=== BMOS系统连接测试 ===\n")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 测试1: ClickHouse HTTP连接
    print("1. 测试ClickHouse HTTP连接:")
    clickhouse_ok = test_clickhouse_http()
    
    # 测试2: Redis连接
    print("\n2. 测试Redis连接:")
    redis_ok = test_redis_connection()
    
    # 测试3: ClickHouse数据库操作
    if clickhouse_ok:
        print("\n3. 测试ClickHouse数据库操作:")
        db_ok = test_clickhouse_database_creation()
    else:
        db_ok = False
    
    # 测试4: BMOS核心表结构
    if db_ok:
        print("\n4. 测试BMOS核心表结构:")
        schema_ok = test_bmos_schema_creation()
    else:
        schema_ok = False
    
    # 总结
    print(f"\n=== 测试结果总结 ===")
    print(f"ClickHouse连接: {'✓ 成功' if clickhouse_ok else '✗ 失败'}")
    print(f"Redis连接: {'✓ 成功' if redis_ok else '✗ 失败'}")
    print(f"数据库操作: {'✓ 成功' if db_ok else '✗ 失败'}")
    print(f"BMOS表结构: {'✓ 成功' if schema_ok else '✗ 失败'}")
    
    if all([clickhouse_ok, redis_ok, db_ok, schema_ok]):
        print("\n🎉 所有测试通过！BMOS系统基础环境就绪。")
        print("\n下一步建议:")
        print("1. 创建完整的BMOS表结构")
        print("2. 开发后端API服务")
        print("3. 实现Shapley归因引擎")
        print("4. 开发前端管理界面")
    else:
        print("\n❌ 部分测试失败，请检查服务状态。")
        if not clickhouse_ok:
            print("   - 检查ClickHouse容器是否正常运行")
        if not redis_ok:
            print("   - 检查Redis容器是否正常运行")

if __name__ == "__main__":
    main()





