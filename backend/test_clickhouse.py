#!/usr/bin/env python3
"""
简单的ClickHouse连接测试
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_clickhouse_connection():
    """测试ClickHouse连接"""
    try:
        # 尝试导入clickhouse_driver
        from clickhouse_driver import Client
        print("✓ clickhouse_driver 导入成功")
        
        # 创建客户端连接
        client = Client(host='localhost', port=9000)
        print("✓ ClickHouse客户端创建成功")
        
        # 测试连接
        result = client.execute('SELECT 1')
        print(f"✓ ClickHouse连接测试成功: {result}")
        
        # 测试数据库
        databases = client.execute('SHOW DATABASES')
        print(f"✓ 可用数据库: {[db[0] for db in databases]}")
        
        # 创建测试数据库
        client.execute('CREATE DATABASE IF NOT EXISTS bmos')
        print("✓ 数据库 'bmos' 创建成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        print("请安装: pip install clickhouse-driver")
        return False
    except Exception as e:
        print(f"✗ 连接错误: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        print("✓ redis 导入成功")
        
        # 连接到Redis (使用端口6380)
        r = redis.Redis(host='localhost', port=6380, decode_responses=True)
        
        # 测试连接
        r.ping()
        print("✓ Redis连接测试成功")
        
        # 测试设置和获取
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✓ Redis读写测试成功: {value}")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        print("请安装: pip install redis")
        return False
    except Exception as e:
        print(f"✗ 连接错误: {e}")
        return False

def main():
    """主函数"""
    print("=== BMOS系统连接测试 ===\n")
    
    print("1. 测试ClickHouse连接:")
    clickhouse_ok = test_clickhouse_connection()
    
    print("\n2. 测试Redis连接:")
    redis_ok = test_redis_connection()
    
    print(f"\n=== 测试结果 ===")
    print(f"ClickHouse: {'✓ 成功' if clickhouse_ok else '✗ 失败'}")
    print(f"Redis: {'✓ 成功' if redis_ok else '✗ 失败'}")
    
    if clickhouse_ok and redis_ok:
        print("\n🎉 所有服务连接正常！可以继续下一步测试。")
    else:
        print("\n❌ 部分服务连接失败，请检查服务状态。")

if __name__ == "__main__":
    main()

