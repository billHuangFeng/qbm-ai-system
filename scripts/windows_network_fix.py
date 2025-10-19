#!/usr/bin/env python3
"""
Windows Docker网络问题终极解决方案
"""
import subprocess
import time
import json

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

def restart_docker_containers():
    """重启Docker容器"""
    print("=== 重启Docker容器 ===")
    
    # 停止所有容器
    print("1. 停止所有容器...")
    run_command("docker-compose -f docker-compose-dev.yml down")
    time.sleep(5)
    
    # 启动所有容器
    print("2. 启动所有容器...")
    success, stdout, stderr = run_command("docker-compose -f docker-compose-dev.yml up -d")
    if not success:
        print(f"❌ 容器启动失败: {stderr}")
        return False
    
    print("✅ 容器重启完成")
    
    # 等待服务启动
    print("3. 等待服务启动...")
    time.sleep(10)
    
    return True

def setup_port_forwarding():
    """设置端口转发"""
    print("\n=== 设置端口转发 ===")
    
    # 获取容器IP
    print("1. 获取容器IP地址...")
    
    success, stdout, stderr = run_command('docker inspect bmos_frontend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    if not success:
        print("❌ 无法获取前端容器IP")
        return False
    frontend_ip = stdout.strip()
    print(f"前端容器IP: {frontend_ip}")
    
    success, stdout, stderr = run_command('docker inspect bmos_backend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    if not success:
        print("❌ 无法获取后端容器IP")
        return False
    backend_ip = stdout.strip()
    print(f"后端容器IP: {backend_ip}")
    
    # 设置端口转发
    print("2. 设置端口转发...")
    
    # 清除现有端口转发规则
    run_command("netsh interface portproxy delete v4tov4 listenport=3000")
    run_command("netsh interface portproxy delete v4tov4 listenport=8000")
    
    # 添加新的端口转发规则
    success1, _, _ = run_command(f"netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress={frontend_ip}")
    success2, _, _ = run_command(f"netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress={backend_ip}")
    
    if success1 and success2:
        print("✅ 端口转发设置成功")
        return True
    else:
        print("❌ 端口转发设置失败")
        return False

def test_access():
    """测试访问"""
    print("\n=== 测试访问 ===")
    
    # 测试后端健康检查
    print("1. 测试后端健康检查...")
    success, stdout, stderr = run_command('docker exec bmos_backend python -c "import requests; print(requests.get(\'http://localhost:8000/health\').text)"')
    if success and "healthy" in stdout:
        print("✅ 后端服务正常")
    else:
        print("❌ 后端服务异常")
        return False
    
    # 测试前端服务
    print("2. 测试前端服务...")
    success, stdout, stderr = run_command('docker exec bmos_frontend node -e "const http = require(\'http\'); http.get(\'http://localhost:3000\', (res) => { console.log(\'Status:\', res.statusCode); process.exit(0); }).on(\'error\', (err) => { console.error(err.message); process.exit(1); });"')
    if success and "Status:" in stdout:
        print("✅ 前端服务正常")
    else:
        print("❌ 前端服务异常")
        return False
    
    return True

def create_access_script():
    """创建访问脚本"""
    print("\n=== 创建访问脚本 ===")
    
    # 获取容器IP
    success, stdout, stderr = run_command('docker inspect bmos_frontend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    frontend_ip = stdout.strip() if success else "172.21.0.5"
    
    success, stdout, stderr = run_command('docker inspect bmos_backend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    backend_ip = stdout.strip() if success else "172.21.0.4"
    
    # 创建访问脚本
    script_content = f'''@echo off
echo ========================================
echo BMOS系统访问脚本
echo ========================================
echo.
echo 方案1: 使用容器IP访问（推荐）
echo   前端界面: http://{frontend_ip}:3000
echo   后端API: http://{backend_ip}:8000
echo   健康检查: http://{backend_ip}:8000/health
echo.
echo 方案2: 使用localhost访问（如果端口转发成功）
echo   前端界面: http://localhost:3000
echo   后端API: http://localhost:8000
echo   健康检查: http://localhost:8000/health
echo.
echo 方案3: 使用PowerShell测试
echo   Invoke-WebRequest -Uri "http://{backend_ip}:8000/health"
echo.
echo 按任意键打开前端界面...
pause > nul
start http://{frontend_ip}:3000
'''
    
    with open('access_bmos.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 访问脚本已创建: access_bmos.bat")
    return True

def main():
    """主函数"""
    print("=== Windows Docker网络问题终极解决方案 ===\n")
    
    # 1. 重启容器
    if not restart_docker_containers():
        print("❌ 容器重启失败")
        return False
    
    # 2. 测试服务
    if not test_access():
        print("❌ 服务测试失败")
        return False
    
    # 3. 设置端口转发
    port_forward_ok = setup_port_forwarding()
    
    # 4. 创建访问脚本
    create_access_script()
    
    # 5. 显示结果
    print("\n=== 解决方案完成 ===")
    print("🎉 系统已准备就绪！")
    print("\n📋 访问方式:")
    print("1. 运行 access_bmos.bat 脚本")
    print("2. 或直接使用容器IP访问:")
    print("   - 前端: http://172.21.0.5:3000")
    print("   - 后端: http://172.21.0.4:8000")
    
    if port_forward_ok:
        print("3. 或使用localhost访问:")
        print("   - 前端: http://localhost:3000")
        print("   - 后端: http://localhost:8000")
    
    print("\n💡 如果仍然无法访问，请:")
    print("   1. 以管理员身份运行此脚本")
    print("   2. 重启Docker Desktop")
    print("   3. 检查Windows防火墙设置")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

