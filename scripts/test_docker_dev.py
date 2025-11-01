#!/usr/bin/env python3
"""
测试Docker开发环境
"""
import subprocess
import sys
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

def test_clickhouse():
    """测试ClickHouse"""
    print("测试ClickHouse连接...")
    
    # 测试TCP连接
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"'
    )
    if success and "1" in stdout:
        print("✅ ClickHouse TCP连接正常")
    else:
        print(f"❌ ClickHouse TCP连接失败: {stderr}")
        return False
    
    # 测试数据库
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW DATABASES"'
    )
    if success and "bmos" in stdout:
        print("✅ BMOS数据库存在")
    else:
        print(f"❌ BMOS数据库不存在: {stderr}")
        return False
    
    return True

def test_redis():
    """测试Redis"""
    print("\n测试Redis连接...")
    
    success, stdout, stderr = run_command(
        'docker exec bmos_redis redis-cli ping'
    )
    if success and "PONG" in stdout:
        print("✅ Redis连接正常")
        return True
    else:
        print(f"❌ Redis连接失败: {stderr}")
        return False

def test_backend():
    """测试后端服务"""
    print("\n测试后端服务...")
    
    # 等待服务启动
    print("等待后端服务启动...")
    for i in range(30):
        success, stdout, stderr = run_command("curl -s http://localhost:8000/health", timeout=5)
        if success and "healthy" in stdout:
            print("✅ 后端服务正常")
            return True
        time.sleep(2)
    
    print("❌ 后端服务启动超时")
    return False

def test_api():
    """测试API端点"""
    print("\n测试API端点...")
    
    # 测试根路径
    success, stdout, stderr = run_command("curl -s http://localhost:8000/")
    if success and "BMOS" in stdout:
        print("✅ 根路径API正常")
    else:
        print(f"❌ 根路径API失败: {stderr}")
        return False
    
    # 测试健康检查
    success, stdout, stderr = run_command("curl -s http://localhost:8000/health")
    if success and "healthy" in stdout:
        print("✅ 健康检查API正常")
    else:
        print(f"❌ 健康检查API失败: {stderr}")
        return False
    
    # 测试BMOS状态
    success, stdout, stderr = run_command("curl -s http://localhost:8000/api/v1/bmos/status")
    if success and "BMOS" in stdout:
        print("✅ BMOS状态API正常")
    else:
        print(f"❌ BMOS状态API失败: {stderr}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=== BMOS Docker开发环境测试 ===\n")
    
    tests = [
        ("ClickHouse", test_clickhouse),
        ("Redis", test_redis),
        ("Backend", test_backend),
        ("API", test_api)
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
        print("🎉 所有测试通过！Docker开发环境正常")
        print("\n✅ 可以开始开发:")
        print("   - 后端API: http://localhost:8000")
        print("   - API文档: http://localhost:8000/docs")
        print("   - 无需担心Windows编译问题")
    else:
        print("❌ 部分测试失败，请检查Docker环境")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






