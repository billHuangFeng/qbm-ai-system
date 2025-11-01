#!/usr/bin/env python3
"""
修复Windows Docker网络访问问题
"""
import subprocess
import time
import requests
import socket

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

def check_port_accessibility(host, port):
    """检查端口是否可访问"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_http_access(url):
    """测试HTTP访问"""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def fix_windows_docker_network():
    """修复Windows Docker网络问题"""
    print("=== 修复Windows Docker网络访问问题 ===\n")
    
    # 1. 检查Docker Desktop状态
    print("1. 检查Docker Desktop状态...")
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker未运行，请启动Docker Desktop")
        return False
    
    print("✅ Docker Desktop运行正常")
    
    # 2. 检查容器状态
    print("\n2. 检查容器状态...")
    containers = ['bmos_frontend', 'bmos_backend', 'bmos_clickhouse', 'bmos_redis']
    
    for container in containers:
        success, stdout, stderr = run_command(f'docker ps --filter "name={container}" --format "{{{{.Names}}}}"')
        if success and container in stdout:
            print(f"✅ {container} 运行中")
        else:
            print(f"❌ {container} 未运行")
            return False
    
    # 3. 检查端口映射
    print("\n3. 检查端口映射...")
    success, stdout, stderr = run_command("docker port bmos_frontend")
    if success and "3000" in stdout:
        print("✅ 前端端口映射正常")
    else:
        print("❌ 前端端口映射异常")
        return False
    
    success, stdout, stderr = run_command("docker port bmos_backend")
    if success and "8000" in stdout:
        print("✅ 后端端口映射正常")
    else:
        print("❌ 后端端口映射异常")
        return False
    
    # 4. 测试容器内部服务
    print("\n4. 测试容器内部服务...")
    
    # 测试后端
    success, stdout, stderr = run_command(
        'docker exec bmos_backend python -c "import requests; print(requests.get(\'http://localhost:8000/health\').text)"'
    )
    if success and "healthy" in stdout:
        print("✅ 后端服务内部正常")
    else:
        print("❌ 后端服务内部异常")
        return False
    
    # 测试前端
    success, stdout, stderr = run_command(
        'docker exec bmos_frontend node -e "const http = require(\'http\'); http.get(\'http://0.0.0.0:3000\', (res) => { console.log(\'OK\'); process.exit(0); }).on(\'error\', (err) => { console.error(err.message); process.exit(1); });"'
    )
    if success and "OK" in stdout:
        print("✅ 前端服务内部正常")
    else:
        print("❌ 前端服务内部异常")
        print(f"   错误: {stderr}")
    
    # 5. 测试宿主机访问
    print("\n5. 测试宿主机访问...")
    
    # 测试端口连通性
    backend_port_ok = check_port_accessibility('localhost', 8000)
    frontend_port_ok = check_port_accessibility('localhost', 3000)
    
    print(f"后端端口8000连通性: {'✅ 可访问' if backend_port_ok else '❌ 不可访问'}")
    print(f"前端端口3000连通性: {'✅ 可访问' if frontend_port_ok else '❌ 不可访问'}")
    
    # 测试HTTP访问
    if backend_port_ok:
        success, response = test_http_access('http://localhost:8000/health')
        if success:
            print("✅ 后端HTTP访问正常")
        else:
            print("❌ 后端HTTP访问异常")
            print(f"   错误: {response}")
    
    if frontend_port_ok:
        success, response = test_http_access('http://localhost:3000')
        if success:
            print("✅ 前端HTTP访问正常")
        else:
            print("❌ 前端HTTP访问异常")
            print(f"   错误: {response}")
    
    # 6. 提供解决方案
    print("\n=== 解决方案 ===")
    
    if not backend_port_ok or not frontend_port_ok:
        print("🔧 Windows Docker网络问题解决方案:")
        print("\n方案1: 重启Docker Desktop")
        print("   1. 右键点击系统托盘中的Docker图标")
        print("   2. 选择 'Restart Docker Desktop'")
        print("   3. 等待重启完成")
        
        print("\n方案2: 使用容器内部网络")
        print("   1. 在容器内访问服务:")
        print("      - 后端: docker exec bmos_backend curl http://localhost:8000/health")
        print("      - 前端: docker exec bmos_frontend curl http://localhost:3000")
        
        print("\n方案3: 使用Docker网络IP")
        print("   1. 获取容器IP:")
        print("      docker inspect bmos_frontend | grep IPAddress")
        print("      docker inspect bmos_backend | grep IPAddress")
        print("   2. 使用容器IP访问服务")
        
        print("\n方案4: 使用端口转发")
        print("   1. 使用PowerShell端口转发:")
        print("      netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=172.21.0.5")
        print("      netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.21.0.6")
        
        return False
    else:
        print("🎉 网络访问正常！")
        print("\n✅ 可以正常访问:")
        print("   - 前端界面: http://localhost:3000")
        print("   - 后端API: http://localhost:8000")
        print("   - 健康检查: http://localhost:8000/health")
        return True

def get_container_ips():
    """获取容器IP地址"""
    print("\n=== 容器IP地址 ===")
    
    containers = ['bmos_frontend', 'bmos_backend', 'bmos_clickhouse', 'bmos_redis']
    
    for container in containers:
        success, stdout, stderr = run_command(f'docker inspect {container} --format "{{{{.NetworkSettings.IPAddress}}}}"')
        if success and stdout.strip():
            ip = stdout.strip()
            print(f"{container}: {ip}")
        else:
            print(f"{container}: 无法获取IP")

def main():
    """主函数"""
    print("=== Windows Docker网络问题诊断和修复 ===\n")
    
    # 修复网络问题
    network_ok = fix_windows_docker_network()
    
    # 获取容器IP
    get_container_ips()
    
    if not network_ok:
        print("\n⚠️ 网络访问存在问题，请尝试上述解决方案")
        print("\n💡 推荐方案:")
        print("   1. 重启Docker Desktop")
        print("   2. 如果问题持续，使用容器内部网络进行开发")
        return False
    else:
        print("\n🎉 网络访问正常，可以开始使用系统！")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)






