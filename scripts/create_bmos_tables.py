#!/usr/bin/env python3
"""
创建BMOS系统核心表结构
使用ClickHouse客户端直接执行SQL
"""
import subprocess
import sys
import os
from pathlib import Path

def run_clickhouse_query(query):
    """执行ClickHouse查询"""
    try:
        # 使用docker exec执行ClickHouse客户端
        cmd = [
            'docker', 'exec', 'bmos_clickhouse',
            'clickhouse-client', '--query', query
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "查询超时"
    except Exception as e:
        return False, str(e)

def create_database():
    """创建BMOS数据库"""
    print("1. 创建BMOS数据库...")
    success, output = run_clickhouse_query("CREATE DATABASE IF NOT EXISTS bmos")
    if success:
        print("   ✓ 数据库创建成功")
        return True
    else:
        print(f"   ✗ 数据库创建失败: {output}")
        return False

def execute_sql_file():
    """执行SQL文件"""
    print("2. 执行BMOS表结构SQL...")
    
    sql_file = Path(__file__).parent.parent / "database" / "clickhouse" / "schema" / "bmos_core_tables.sql"
    
    if not sql_file.exists():
        print(f"   ✗ SQL文件不存在: {sql_file}")
        return False
    
    try:
        # 读取SQL文件内容
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（按分号分割）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        total_count = len(sql_statements)
        
        for i, statement in enumerate(sql_statements, 1):
            if not statement:
                continue
                
            print(f"   执行语句 {i}/{total_count}...")
            success, output = run_clickhouse_query(statement)
            
            if success:
                success_count += 1
                print(f"   ✓ 语句 {i} 执行成功")
            else:
                print(f"   ✗ 语句 {i} 执行失败: {output}")
                # 继续执行其他语句，不中断
        
        print(f"   ✓ 成功执行 {success_count}/{total_count} 个SQL语句")
        return success_count > 0
        
    except Exception as e:
        print(f"   ✗ 执行SQL文件失败: {e}")
        return False

def verify_tables():
    """验证表是否创建成功"""
    print("3. 验证表创建...")
    
    # 检查维度表
    dim_tables = [
        'dim_vpt', 'dim_pft', 'dim_activity', 'dim_media_channel',
        'dim_conv_channel', 'dim_sku', 'dim_customer', 'dim_date', 'dim_supplier'
    ]
    
    # 检查桥接表
    bridge_tables = [
        'bridge_media_vpt', 'bridge_conv_vpt', 'bridge_sku_pft',
        'bridge_vpt_pft', 'bridge_attribution'
    ]
    
    # 检查事实表
    fact_tables = [
        'fact_order', 'fact_voice', 'fact_cost', 'fact_supplier', 'fact_produce'
    ]
    
    all_tables = dim_tables + bridge_tables + fact_tables
    
    success_count = 0
    for table in all_tables:
        success, output = run_clickhouse_query(f"SHOW TABLES FROM bmos LIKE '{table}'")
        if success and table in output:
            print(f"   ✓ 表 {table} 创建成功")
            success_count += 1
        else:
            print(f"   ✗ 表 {table} 创建失败")
    
    print(f"   ✓ 成功创建 {success_count}/{len(all_tables)} 个表")
    return success_count == len(all_tables)

def insert_sample_data():
    """插入示例数据"""
    print("4. 插入示例数据...")
    
    # 插入VPT示例数据
    vpt_data = """
    INSERT INTO bmos.dim_vpt (vpt_id, vpt_name, vpt_category, vpt_description, owner) VALUES
    ('vpt001', '极速交付', 'delivery', '承诺24小时发货', 'supply_chain'),
    ('vpt002', '品质保证', 'quality', '100%正品保证', 'product'),
    ('vpt003', '贴心服务', 'service', '7x24小时客服', 'customer_service'),
    ('vpt004', '价格优势', 'price', '全网最低价保证', 'marketing'),
    ('vpt005', '技术创新', 'innovation', '行业领先技术', 'rd')
    """
    
    success, output = run_clickhouse_query(vpt_data)
    if success:
        print("   ✓ VPT示例数据插入成功")
    else:
        print(f"   ✗ VPT示例数据插入失败: {output}")
    
    # 插入PFT示例数据
    pft_data = """
    INSERT INTO bmos.dim_pft (pft_id, pft_name, pft_category, pft_description, unit, module) VALUES
    ('pft001', '响应速度', 'performance', '系统响应时间', 'ms', 'backend'),
    ('pft002', '界面友好', 'ui', '用户界面易用性', 'score', 'frontend'),
    ('pft003', '数据安全', 'security', '数据加密保护', 'level', 'security'),
    ('pft004', '扩展性', 'scalability', '系统扩展能力', 'capacity', 'infrastructure'),
    ('pft005', '稳定性', 'reliability', '系统运行稳定性', 'uptime', 'infrastructure')
    """
    
    success, output = run_clickhouse_query(pft_data)
    if success:
        print("   ✓ PFT示例数据插入成功")
    else:
        print(f"   ✗ PFT示例数据插入失败: {output}")
    
    # 插入客户示例数据
    customer_data = """
    INSERT INTO bmos.dim_customer (customer_id, customer_segment, region, age_group, gender, first_media_id, first_conv_id, reg_date) VALUES
    ('cust001', '高价值客户', '北京', '25-35', '女', 'douyin', 'tmall', '2024-01-15'),
    ('cust002', '新客户', '上海', '18-25', '男', 'xiaohongshu', 'jd', '2024-02-20'),
    ('cust003', '流失客户', '广州', '35-45', '女', 'wechat', 'official', '2023-12-10'),
    ('cust004', '高价值客户', '深圳', '25-35', '男', 'baidu', 'tmall', '2024-01-08'),
    ('cust005', '新客户', '杭州', '18-25', '女', 'douyin', 'jd', '2024-03-01')
    """
    
    success, output = run_clickhouse_query(customer_data)
    if success:
        print("   ✓ 客户示例数据插入成功")
    else:
        print(f"   ✗ 客户示例数据插入失败: {output}")
    
    return True

def main():
    """主函数"""
    print("=== BMOS系统表结构创建 ===\n")
    
    # 检查ClickHouse容器是否运行
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=bmos_clickhouse', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        if 'bmos_clickhouse' not in result.stdout:
            print("✗ ClickHouse容器未运行，请先启动容器")
            return False
    except Exception as e:
        print(f"✗ 检查容器状态失败: {e}")
        return False
    
    # 执行创建步骤
    steps = [
        create_database,
        execute_sql_file,
        verify_tables,
        insert_sample_data
    ]
    
    success_count = 0
    for step in steps:
        try:
            if step():
                success_count += 1
            print()  # 空行分隔
        except Exception as e:
            print(f"✗ 步骤执行失败: {e}\n")
    
    print(f"=== 创建结果 ===")
    print(f"成功完成 {success_count}/{len(steps)} 个步骤")
    
    if success_count == len(steps):
        print("\n🎉 BMOS系统表结构创建完成！")
        print("\n下一步建议:")
        print("1. 开发后端API服务")
        print("2. 实现Shapley归因引擎")
        print("3. 开发前端管理界面")
        return True
    else:
        print("\n❌ 部分步骤失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

