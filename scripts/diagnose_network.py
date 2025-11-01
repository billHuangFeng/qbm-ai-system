#!/usr/bin/env python3
"""
Windows Docker网络诊断脚本
"""
import subprocess
import socket
import time
import requests
from datetime import datetime

def run_command(cmd, shell=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)

def test_port_connectivity(host, port):
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_http_connectivity(url, timeout=10):
    """测试HTTP连接"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.text[:100]
    except Exception as e:
        return False, str(e)

def diagnose_docker_network():
    """诊断Docker网络问题"""
    print("=== Windows Docker网络诊断 ===\n")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. 检查Docker Desktop状态
    print("1. 检查Docker Desktop状态:")
    success, stdout, stderr = run_command("docker info")
    if success:
        print("   ✓ Docker Desktop运行正常")
        # 检查是否使用WSL2
        if "WSL" in stdout:
            print("   ✓ 使用WSL2后端")
        else:
            print("   ⚠️ 未使用WSL2后端")
    else:
        print(f"   ✗ Docker Desktop异常: {stderr}")
        return False
    
    # 2. 检查容器状态
    print("\n2. 检查容器状态:")
    success, stdout, stderr = run_command("docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'")
    if success:
        print("   容器列表:")
        for line in stdout.strip().split('\n')[1:]:  # 跳过表头
            if line.strip():
                print(f"   {line}")
    else:
        print(f"   ✗ 无法获取容器状态: {stderr}")
    
    # 3. 测试端口连接
    print("\n3. 测试端口连接:")
    ports_to_test = [
        ("localhost", 8123, "ClickHouse HTTP"),
        ("localhost", 9000, "ClickHouse TCP"),
        ("localhost", 6380, "Redis")
    ]
    
    for host, port, service in ports_to_test:
        if test_port_connectivity(host, port):
            print(f"   ✓ {service} ({host}:{port}) 连接正常")
        else:
            print(f"   ✗ {service} ({host}:{port}) 连接失败")
    
    # 4. 测试HTTP连接
    print("\n4. 测试HTTP连接:")
    http_tests = [
        ("http://localhost:8123/?query=SELECT%201", "ClickHouse HTTP查询"),
        ("http://localhost:8123/ping", "ClickHouse Ping")
    ]
    
    for url, description in http_tests:
        success, response = test_http_connectivity(url)
        if success:
            print(f"   ✓ {description}: {response}")
        else:
            print(f"   ✗ {description}: {response}")
    
    # 5. 检查Windows网络配置
    print("\n5. 检查Windows网络配置:")
    
    # 检查Hyper-V
    success, stdout, stderr = run_command("dism /online /get-featureinfo /featurename:Microsoft-Hyper-V")
    if "State : Enabled" in stdout:
        print("   ✓ Hyper-V已启用")
    else:
        print("   ⚠️ Hyper-V未启用")
    
    # 检查WSL2
    success, stdout, stderr = run_command("wsl --list --verbose")
    if success:
        print("   WSL2发行版:")
        for line in stdout.strip().split('\n')[1:]:  # 跳过表头
            if line.strip():
                print(f"     {line}")
    
    # 6. 检查防火墙
    print("\n6. 检查防火墙状态:")
    success, stdout, stderr = run_command("netsh advfirewall show allprofiles state")
    if success:
        print("   防火墙状态:")
        for line in stdout.strip().split('\n'):
            if "State" in line:
                print(f"     {line.strip()}")
    
    # 7. 提供解决方案
    print("\n=== 解决方案建议 ===")
    print("如果遇到网络连接问题，请尝试以下解决方案:")
    print("\n方案1: 重启Docker Desktop")
    print("  1. 右键点击系统托盘中的Docker图标")
    print("  2. 选择 'Restart Docker Desktop'")
    print("  3. 等待重启完成")
    
    print("\n方案2: 切换到WSL2后端")
    print("  1. 打开Docker Desktop设置")
    print("  2. 进入 General 页面")
    print("  3. 确保 'Use the WSL 2 based engine' 已勾选")
    print("  4. 重启Docker Desktop")
    
    print("\n方案3: 重置网络设置")
    print("  1. 在Docker Desktop设置中进入 Resources > Network")
    print("  2. 点击 'Reset to defaults'")
    print("  3. 重启Docker Desktop")
    
    print("\n方案4: 使用容器内部测试")
    print("  1. 运行: docker exec bmos_clickhouse clickhouse-client --query 'SELECT 1'")
    print("  2. 如果容器内部正常，说明是宿主机网络问题")
    
    print("\n方案5: 使用不同的端口")
    print("  1. 修改docker-compose.yml中的端口映射")
    print("  2. 例如: '8124:8123' 而不是 '8123:8123'")
    
    return True

def test_alternative_connection():
    """测试替代连接方法"""
    print("\n=== 替代连接测试 ===")
    
    # 测试Docker exec方式
    print("1. 测试Docker exec连接:")
    success, stdout, stderr = run_command("docker exec bmos_clickhouse clickhouse-client --query 'SELECT 1'")
    if success:
        print(f"   ✓ Docker exec连接成功: {stdout.strip()}")
    else:
        print(f"   ✗ Docker exec连接失败: {stderr}")
    
    # 测试容器内部HTTP
    print("\n2. 测试容器内部HTTP:")
    success, stdout, stderr = run_command("docker exec bmos_clickhouse curl -s 'http://localhost:8123/?query=SELECT%201'")
    if success:
        print(f"   ✓ 容器内部HTTP成功: {stdout.strip()}")
    else:
        print(f"   ✗ 容器内部HTTP失败: {stderr}")

def main():
    """主函数"""
    try:
        diagnose_docker_network()
        test_alternative_connection()
        
        print("\n=== 诊断完成 ===")
        print("如果问题仍然存在，请:")
        print("1. 检查Docker Desktop是否使用WSL2后端")
        print("2. 尝试重启Docker Desktop")
        print("3. 检查Windows防火墙设置")
        print("4. 考虑使用容器内部连接进行开发")
        
    except Exception as e:
        print(f"诊断过程中出现错误: {e}")

if __name__ == "__main__":
    main()





