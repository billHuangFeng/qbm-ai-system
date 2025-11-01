#!/usr/bin/env python3
"""
BMOS模型测试脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.clickhouse import clickhouse_connector, check_clickhouse_health
from app.models.bmos import ALL_MODELS, ALL_MODEL_MAP, MODEL_GROUPS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_clickhouse_connection():
    """测试ClickHouse连接"""
    print("=== 测试ClickHouse连接 ===")
    
    health = check_clickhouse_health()
    print(f"连接状态: {health['status']}")
    print(f"TCP连接: {'✓' if health['tcp_connection'] else '✗'}")
    print(f"数据库存在: {'✓' if health['database_exists'] else '✗'}")
    print(f"表结构: {'✓' if health['tables_exist'] else '✗'}")
    print(f"表数量: {health['total_tables']}")
    
    if health['status'] != 'healthy':
        print("❌ ClickHouse连接不健康，请检查服务状态")
        return False
    
    print("✅ ClickHouse连接正常")
    return True

def test_model_imports():
    """测试模型导入"""
    print("\n=== 测试模型导入 ===")
    
    try:
        # 测试维度表模型
        print(f"维度表模型数量: {len(MODEL_GROUPS['dimensions'])}")
        for model in MODEL_GROUPS['dimensions']:
            print(f"  - {model.__tablename__}: {model.__name__}")
        
        # 测试事实表模型
        print(f"事实表模型数量: {len(MODEL_GROUPS['facts'])}")
        for model in MODEL_GROUPS['facts']:
            print(f"  - {model.__tablename__}: {model.__name__}")
        
        # 测试桥接表模型
        print(f"桥接表模型数量: {len(MODEL_GROUPS['bridges'])}")
        for model in MODEL_GROUPS['bridges']:
            print(f"  - {model.__tablename__}: {model.__name__}")
        
        print(f"总模型数量: {len(ALL_MODELS)}")
        print("✅ 模型导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        return False

def test_table_structure():
    """测试表结构"""
    print("\n=== 测试表结构 ===")
    
    try:
        # 获取所有表
        tables_result = clickhouse_connector.execute_query("SHOW TABLES FROM bmos")
        existing_tables = [row[0] for row in tables_result]
        
        print(f"ClickHouse中的表: {len(existing_tables)}")
        for table in existing_tables:
            print(f"  - {table}")
        
        # 检查模型对应的表是否存在
        model_tables = [model.__tablename__ for model in ALL_MODELS]
        missing_tables = set(model_tables) - set(existing_tables)
        
        if missing_tables:
            print(f"❌ 缺少表: {missing_tables}")
            return False
        
        print("✅ 所有模型对应的表都存在")
        return True
        
    except Exception as e:
        print(f"❌ 表结构测试失败: {e}")
        return False

def test_sample_queries():
    """测试示例查询"""
    print("\n=== 测试示例查询 ===")
    
    try:
        # 测试维度表查询
        print("1. 测试维度表查询...")
        vpt_result = clickhouse_connector.execute_query("SELECT COUNT(*) FROM bmos.dim_vpt")
        print(f"   VPT数据量: {vpt_result[0][0]}")
        
        customer_result = clickhouse_connector.execute_query("SELECT COUNT(*) FROM bmos.dim_customer")
        print(f"   客户数据量: {customer_result[0][0]}")
        
        # 测试事实表查询
        print("2. 测试事实表查询...")
        order_result = clickhouse_connector.execute_query("SELECT COUNT(*) FROM bmos.fact_order")
        print(f"   订单数据量: {order_result[0][0]}")
        
        voice_result = clickhouse_connector.execute_query("SELECT COUNT(*) FROM bmos.fact_voice")
        print(f"   客户声音数据量: {voice_result[0][0]}")
        
        # 测试桥接表查询
        print("3. 测试桥接表查询...")
        bridge_result = clickhouse_connector.execute_query("SELECT COUNT(*) FROM bmos.bridge_attribution")
        print(f"   归因数据量: {bridge_result[0][0]}")
        
        print("✅ 示例查询成功")
        return True
        
    except Exception as e:
        print(f"❌ 示例查询失败: {e}")
        return False

def test_data_insertion():
    """测试数据插入"""
    print("\n=== 测试数据插入 ===")
    
    try:
        # 测试VPT数据插入
        test_vpt_data = [{
            'vpt_id': 'test_vpt_001',
            'vpt_name': '测试价值主张',
            'vpt_category': 'test',
            'vpt_description': '这是一个测试价值主张',
            'owner': 'test_user'
        }]
        
        clickhouse_connector.insert_data('bmos.dim_vpt', test_vpt_data)
        print("✅ VPT数据插入成功")
        
        # 验证插入
        result = clickhouse_connector.execute_query(
            "SELECT vpt_name FROM bmos.dim_vpt WHERE vpt_id = 'test_vpt_001'"
        )
        if result and result[0][0] == '测试价值主张':
            print("✅ 数据验证成功")
        else:
            print("❌ 数据验证失败")
            return False
        
        # 清理测试数据
        clickhouse_connector.execute_non_query(
            "ALTER TABLE bmos.dim_vpt DELETE WHERE vpt_id = 'test_vpt_001'"
        )
        print("✅ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据插入测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== BMOS模型测试 ===\n")
    
    tests = [
        ("ClickHouse连接", test_clickhouse_connection),
        ("模型导入", test_model_imports),
        ("表结构", test_table_structure),
        ("示例查询", test_sample_queries),
        ("数据插入", test_data_insertion)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    print("\n=== 测试结果 ===")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n=== 总结 ===")
    if all_passed:
        print("🎉 所有模型测试通过！")
        print("\n✅ 可以继续开发:")
        print("   - ORM模型已就绪")
        print("   - 数据库连接正常")
        print("   - 表结构完整")
        print("   - 数据操作正常")
    else:
        print("❌ 部分测试失败，请检查问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





