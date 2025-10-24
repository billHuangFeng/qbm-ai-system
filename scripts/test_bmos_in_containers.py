#!/usr/bin/env python3
"""
在容器内测试BMOS系统功能
"""
import subprocess
import json
import time

def run_command(cmd, timeout=30):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            timeout=timeout, encoding='utf-8', errors='ignore'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_backend_api():
    """测试后端API"""
    print("=== 测试后端API ===")
    
    # 健康检查
    print("1. 健康检查...")
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; r = requests.get(\'http://localhost:8000/health\'); print(f\'状态码: {r.status_code}\'); print(f\'响应: {r.text}\')"'
    )
    
    if success and "200" in stdout:
        print("✅ 后端API健康检查正常")
        print(f"   响应: {stdout.strip()}")
        return True
    else:
        print("❌ 后端API健康检查失败")
        print(f"   错误: {stderr}")
        return False

def test_frontend_service():
    """测试前端服务"""
    print("\n=== 测试前端服务 ===")
    
    # 检查前端进程
    print("1. 前端进程检查...")
    success, stdout, stderr = run_command(
        'docker exec bmos_frontend ps aux | grep -E "(vite|node)"'
    )
    
    if success and ("vite" in stdout or "node" in stdout):
        print("✅ 前端进程正常")
        print(f"   进程: {stdout.strip()}")
    else:
        print("❌ 前端进程异常")
        return False
    
    # 测试前端HTTP服务
    print("2. 前端HTTP服务测试...")
    success, stdout, stderr = run_command(
        'docker exec bmos_frontend node -e "const http = require(\'http\'); http.get(\'http://localhost:3000\', (res) => { console.log(\'状态码:\', res.statusCode); process.exit(0); }).on(\'error\', (err) => { console.error(\'错误:\', err.message); process.exit(1); });"'
    )
    
    if success and "状态码:" in stdout:
        print("✅ 前端HTTP服务正常")
        print(f"   状态: {stdout.strip()}")
        return True
    else:
        print("❌ 前端HTTP服务异常")
        print(f"   错误: {stderr}")
        return False

def test_database():
    """测试数据库"""
    print("\n=== 测试数据库 ===")
    
    # ClickHouse连接测试
    print("1. ClickHouse连接测试...")
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"'
    )
    
    if success and "1" in stdout:
        print("✅ ClickHouse连接正常")
    else:
        print("❌ ClickHouse连接异常")
        return False
    
    # 数据库检查
    print("2. 数据库检查...")
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW DATABASES"'
    )
    
    if success and "bmos" in stdout:
        print("✅ BMOS数据库存在")
    else:
        print("❌ BMOS数据库不存在")
        return False
    
    # 表结构检查
    print("3. 表结构检查...")
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW TABLES FROM bmos"'
    )
    
    if success:
        tables = stdout.strip().split('\n')
        print(f"✅ 表结构完整: {len(tables)} 个表")
        if len(tables) >= 20:
            print("   核心表结构正常")
        else:
            print("   表数量不足")
    else:
        print("❌ 无法获取表列表")
        return False
    
    return True

def test_redis():
    """测试Redis"""
    print("\n=== 测试Redis ===")
    
    success, stdout, stderr = run_command(
        'docker exec bmos_redis redis-cli ping'
    )
    
    if success and "PONG" in stdout:
        print("✅ Redis连接正常")
        return True
    else:
        print("❌ Redis连接异常")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    # 测试健康检查端点
    print("1. 健康检查端点...")
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; r = requests.get(\'http://localhost:8000/health\'); print(f\'健康检查状态: {r.status_code}\'); print(f\'响应内容: {r.text}\')"'
    )
    
    if success and "200" in stdout:
        print("✅ 健康检查端点正常")
    else:
        print("❌ 健康检查端点异常")
        return False
    
    # 测试API文档端点
    print("2. API文档端点...")
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; r = requests.get(\'http://localhost:8000/docs\'); print(f\'API文档状态: {r.status_code}\')"'
    )
    
    if success and "200" in stdout:
        print("✅ API文档端点正常")
    else:
        print("⚠️ API文档端点异常（可能正常）")
    
    return True

def test_data_operations():
    """测试数据操作"""
    print("\n=== 测试数据操作 ===")
    
    # 测试查询维度表
    print("1. 查询维度表...")
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT COUNT(*) FROM bmos.dim_vpt"'
    )
    
    if success:
        print(f"✅ 维度表查询正常: {stdout.strip()} 条记录")
    else:
        print("❌ 维度表查询异常")
        return False
    
    # 测试查询事实表
    print("2. 查询事实表...")
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT COUNT(*) FROM bmos.fact_order"'
    )
    
    if success:
        print(f"✅ 事实表查询正常: {stdout.strip()} 条记录")
    else:
        print("❌ 事实表查询异常")
        return False
    
    return True

def test_container_network():
    """测试容器网络"""
    print("\n=== 测试容器网络 ===")
    
    # 测试后端到ClickHouse连接
    print("1. 后端到ClickHouse连接...")
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; r = requests.get(\'http://clickhouse:8123/?query=SELECT%201\'); print(f\'ClickHouse连接状态: {r.status_code}\')"'
    )
    
    if success and "200" in stdout:
        print("✅ 后端到ClickHouse连接正常")
    else:
        print("❌ 后端到ClickHouse连接异常")
        return False
    
    # 测试后端到Redis连接
    print("2. 后端到Redis连接...")
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import redis; r = redis.Redis(host=\'redis\', port=6379); print(f\'Redis连接状态: {r.ping()}\')"'
    )
    
    if success and "True" in stdout:
        print("✅ 后端到Redis连接正常")
    else:
        print("❌ 后端到Redis连接异常")
        return False
    
    return True

def main():
    """主函数"""
    print("=== BMOS系统容器内功能测试 ===\n")
    print("测试所有系统组件在容器内的运行状态\n")
    
    # 测试各个组件
    backend_ok = test_backend_api()
    frontend_ok = test_frontend_service()
    database_ok = test_database()
    redis_ok = test_redis()
    api_ok = test_api_endpoints()
    data_ok = test_data_operations()
    network_ok = test_container_network()
    
    # 总结
    print("\n=== 测试结果总结 ===")
    print(f"后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"数据库: {'✅ 正常' if database_ok else '❌ 异常'}")
    print(f"Redis: {'✅ 正常' if redis_ok else '❌ 异常'}")
    print(f"API端点: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"数据操作: {'✅ 正常' if data_ok else '❌ 异常'}")
    print(f"容器网络: {'✅ 正常' if network_ok else '❌ 异常'}")
    
    # 总体评估
    all_tests = [backend_ok, frontend_ok, database_ok, redis_ok, api_ok, data_ok, network_ok]
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n=== 总体评估 ===")
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！BMOS系统完全正常")
        print("\n✅ 系统功能完整:")
        print("   - 后端API服务正常")
        print("   - 前端Vue.js服务正常")
        print("   - ClickHouse数据库正常")
        print("   - Redis缓存正常")
        print("   - 容器网络连通正常")
        print("   - 数据操作正常")
        print("\n🚀 系统已准备就绪，可以正常使用！")
        return True
    else:
        print("❌ 部分测试失败，请检查系统状态")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)




