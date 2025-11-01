#!/usr/bin/env python3
"""
BMOS开发环境启动脚本
解决Windows编译问题，使用Docker容器化开发
"""
import subprocess
import time
import sys
import os

def run_command(cmd, timeout=60):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, 
            timeout=timeout, encoding='utf-8', errors='ignore'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """检查Docker是否运行"""
    print("检查Docker状态...")
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker未安装或未运行")
        return False
    
    print(f"✅ Docker版本: {stdout.strip()}")
    return True

def start_containers():
    """启动开发容器"""
    print("\n启动开发容器...")
    
    # 停止现有容器
    print("停止现有容器...")
    run_command("docker-compose -f docker-compose-dev.yml down")
    
    # 启动容器
    print("启动新容器...")
    success, stdout, stderr = run_command("docker-compose -f docker-compose-dev.yml up -d")
    
    if not success:
        print(f"❌ 容器启动失败: {stderr}")
        return False
    
    print("✅ 容器启动成功")
    return True

def wait_for_services():
    """等待服务启动"""
    print("\n等待服务启动...")
    
    services = [
        ("ClickHouse", "docker exec bmos_clickhouse clickhouse-client --query 'SELECT 1'"),
        ("Redis", "docker exec bmos_redis redis-cli ping"),
        ("Backend", "curl -f http://localhost:8000/health")
    ]
    
    for service_name, check_cmd in services:
        print(f"等待 {service_name} 启动...")
        max_retries = 30
        for i in range(max_retries):
            success, stdout, stderr = run_command(check_cmd, timeout=5)
            if success:
                print(f"✅ {service_name} 启动成功")
                break
            else:
                if i < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"❌ {service_name} 启动超时")
                    return False
    
    return True

def test_system():
    """测试系统功能"""
    print("\n测试系统功能...")
    
    # 测试ClickHouse连接
    success, stdout, stderr = run_command(
        'docker exec bmos_clickhouse clickhouse-client --query "SHOW DATABASES"'
    )
    if success and "bmos" in stdout:
        print("✅ ClickHouse数据库连接正常")
    else:
        print("❌ ClickHouse数据库连接失败")
        return False
    
    # 测试后端API
    success, stdout, stderr = run_command("curl -s http://localhost:8000/health")
    if success and "healthy" in stdout:
        print("✅ 后端API服务正常")
    else:
        print("❌ 后端API服务异常")
        return False
    
    return True

def show_status():
    """显示系统状态"""
    print("\n=== BMOS开发环境状态 ===")
    
    # 显示容器状态
    success, stdout, stderr = run_command("docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'")
    if success:
        print("容器状态:")
        print(stdout)
    
    # 显示服务URL
    print("\n服务访问地址:")
    print("  - 后端API: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - ClickHouse HTTP: http://localhost:8123")
    print("  - ClickHouse TCP: localhost:9000")
    print("  - Redis: localhost:6380")
    
    print("\n开发命令:")
    print("  - 查看日志: docker-compose -f docker-compose-dev.yml logs -f")
    print("  - 重启服务: docker-compose -f docker-compose-dev.yml restart")
    print("  - 停止服务: docker-compose -f docker-compose-dev.yml down")

def main():
    """主函数"""
    print("=== BMOS开发环境启动 ===")
    print("解决Windows编译问题，使用Docker容器化开发\n")
    
    # 检查Docker
    if not check_docker():
        sys.exit(1)
    
    # 启动容器
    if not start_containers():
        sys.exit(1)
    
    # 等待服务启动
    if not wait_for_services():
        sys.exit(1)
    
    # 测试系统
    if not test_system():
        sys.exit(1)
    
    # 显示状态
    show_status()
    
    print("\n🎉 BMOS开发环境启动成功！")
    print("现在可以开始开发，无需担心Windows编译问题。")

if __name__ == "__main__":
    main()





