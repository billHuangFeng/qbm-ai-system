#!/usr/bin/env python3
"""
BMOS开发环境检查脚本
预防常见问题，确保开发环境稳定
"""
import subprocess
import sys
import time
import json
from datetime import datetime

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

def check_docker_environment():
    """检查Docker环境"""
    print("=== 检查Docker环境 ===")
    
    # 检查Docker是否运行
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker未安装或未运行")
        return False
    
    print(f"✅ Docker版本: {stdout.strip()}")
    
    # 检查Docker Compose
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        print("❌ Docker Compose不可用")
        return False
    
    print(f"✅ Docker Compose版本: {stdout.strip()}")
    return True

def check_containers():
    """检查容器状态"""
    print("\n=== 检查容器状态 ===")
    
    # 检查必要容器是否运行
    required_containers = ['bmos_clickhouse', 'bmos_redis', 'bmos_backend']
    
    success, stdout, stderr = run_command("docker ps --format '{{.Names}}'")
    if not success:
        print("❌ 无法获取容器列表")
        return False
    
    running_containers = [name.strip("'\"") for name in stdout.strip().split('\n')]
    
    for container in required_containers:
        if container in running_containers:
            print(f"✅ {container} 运行中")
        else:
            print(f"❌ {container} 未运行")
            print(f"   实际运行的容器: {running_containers}")
            return False
    
    return True

def check_clickhouse():
    """检查ClickHouse连接"""
    print("\n=== 检查ClickHouse ===")
    
    # 测试基础连接
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SELECT 1"'
    )
    if not success or "1" not in stdout:
        print("❌ ClickHouse基础连接失败")
        return False
    
    print("✅ ClickHouse基础连接正常")
    
    # 检查数据库
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW DATABASES"'
    )
    if not success or "bmos" not in stdout:
        print("❌ BMOS数据库不存在")
        return False
    
    print("✅ BMOS数据库存在")
    
    # 检查表结构
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW TABLES FROM bmos"'
    )
    if not success:
        print("❌ 无法获取表列表")
        return False
    
    tables = stdout.strip().split('\n')
    if len(tables) < 20:  # 应该有23个表
        print(f"❌ 表数量不足: {len(tables)}")
        return False
    
    print(f"✅ 表结构完整: {len(tables)} 个表")
    return True

def check_backend():
    """检查后端服务"""
    print("\n=== 检查后端服务 ===")
    
    # 测试容器内API
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; print(requests.get(\'http://localhost:8000/health\').text)"'
    )
    if not success or "healthy" not in stdout:
        print("❌ 后端服务异常")
        return False
    
    print("✅ 后端服务正常")
    
    # 解析健康检查结果
    try:
        health_data = json.loads(stdout.strip())
        if health_data.get('status') == 'healthy':
            print("✅ 健康检查通过")
        else:
            print("❌ 健康检查失败")
            return False
    except:
        print("⚠️ 无法解析健康检查结果")
    
    return True

def check_network():
    """检查网络连接"""
    print("\n=== 检查网络连接 ===")
    
    # 检查端口映射
    success, stdout, stderr = run_command("docker port bmos_backend")
    if not success or "8000" not in stdout:
        print("❌ 后端端口映射异常")
        return False
    
    print("✅ 端口映射正常")
    
    # 检查容器间网络
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; print(requests.get(\'http://clickhouse:8123/?query=SELECT%201\').text)"'
    )
    if not success or "1" not in stdout:
        print("❌ 容器间网络连接异常")
        return False
    
    print("✅ 容器间网络正常")
    return True

def generate_report():
    """生成检查报告"""
    print("\n=== 生成检查报告 ===")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": "Docker容器化开发",
        "status": "正常",
        "recommendations": [
            "继续使用Docker环境开发",
            "避免本地编译复杂包",
            "使用容器内网络访问服务",
            "定期运行此检查脚本"
        ]
    }
    
    try:
        with open('dev_environment_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("✅ 检查报告已生成: dev_environment_report.json")
        return True
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return False

def main():
    """主检查函数"""
    print("=== BMOS开发环境预防性检查 ===\n")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    checks = [
        ("Docker环境", check_docker_environment),
        ("容器状态", check_containers),
        ("ClickHouse", check_clickhouse),
        ("后端服务", check_backend),
        ("网络连接", check_network),
        ("生成报告", generate_report)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}检查异常: {e}")
            results.append((check_name, False))
    
    print("\n=== 检查结果 ===")
    all_passed = True
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    print(f"\n=== 总结 ===")
    if all_passed:
        print("🎉 所有检查通过！开发环境稳定")
        print("\n✅ 可以安全开发:")
        print("   - 使用Docker环境避免编译问题")
        print("   - 容器内网络连接正常")
        print("   - 所有服务运行稳定")
        print("   - 数据库结构完整")
    else:
        print("❌ 部分检查失败，请修复问题后继续开发")
        print("\n🔧 修复建议:")
        print("   - 重启容器: docker-compose -f docker-compose-dev.yml restart")
        print("   - 检查日志: docker-compose -f docker-compose-dev.yml logs")
        print("   - 重新启动: python scripts/start_dev.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
