#!/usr/bin/env python3
"""
BMOS系统工作区脚本 - 绕过Windows Docker网络问题
"""
import subprocess
import json
import sys

def run_clickhouse_query(query):
    """通过Docker exec执行ClickHouse查询"""
    cmd = f'docker exec bmos_clickhouse clickhouse-client --query "{query}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def test_bmos_system():
    """测试BMOS系统"""
    print("=== BMOS系统测试 ===\n")
    
    # 测试基础连接
    success, result = run_clickhouse_query("SELECT 1")
    if success:
        print(f"ClickHouse连接正常: {result}")
    else:
        print(f"ClickHouse连接失败: {result}")
        return False
    
    # 测试数据库
    success, result = run_clickhouse_query("SHOW DATABASES")
    if success:
        print(f"数据库列表: {result}")
    else:
        print(f"数据库查询失败: {result}")
    
    # 测试BMOS表
    success, result = run_clickhouse_query("SHOW TABLES FROM bmos")
    if success:
        tables = result.split('\n')
        print(f"BMOS表数量: {len(tables)}")
        for table in tables[:5]:  # 显示前5个表
            if table.strip():
                print(f"  - {table}")
    else:
        print(f"BMOS表查询失败: {result}")
    
    # 测试示例数据
    success, result = run_clickhouse_query("SELECT COUNT(*) FROM bmos.dim_vpt")
    if success:
        print(f"VPT数据量: {result}")
    else:
        print(f"VPT数据查询失败: {result}")
    
    print("\n=== 测试完成 ===")
    return True

def run_custom_query(query):
    """运行自定义查询"""
    print(f"执行查询: {query}")
    success, result = run_clickhouse_query(query)
    if success:
        print(f"结果: {result}")
    else:
        print(f"错误: {result}")
    return success, result

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 如果有参数，执行自定义查询
        query = " ".join(sys.argv[1:])
        run_custom_query(query)
    else:
        # 否则运行系统测试
        test_bmos_system()

if __name__ == "__main__":
    main()





