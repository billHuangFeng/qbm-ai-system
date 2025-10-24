#!/usr/bin/env python3
"""
修复Windows浏览器访问Docker容器问题
"""
import subprocess
import time
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

def test_container_access():
    """测试容器访问"""
    print("=== 测试容器访问 ===")
    
    # 获取容器IP
    success, stdout, stderr = run_command('docker inspect bmos_frontend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    if not success:
        print("❌ 无法获取前端容器IP")
        return False
    
    frontend_ip = stdout.strip()
    print(f"前端容器IP: {frontend_ip}")
    
    # 测试容器内访问
    print("1. 测试容器内访问...")
    success, stdout, stderr = run_command(
        f'docker exec bmos_frontend node -e "const http = require(\'http\'); http.get(\'http://{frontend_ip}:3000\', (res) => {{ console.log(\'容器内状态码:\', res.statusCode); process.exit(0); }}).on(\'error\', (err) => {{ console.error(\'容器内错误:\', err.message); process.exit(1); }});"'
    )
    
    if success and "200" in stdout:
        print("✅ 容器内访问正常")
    else:
        print("❌ 容器内访问异常")
        return False
    
    # 测试宿主机访问
    print("2. 测试宿主机访问...")
    if check_port_accessibility(frontend_ip, 3000):
        print("✅ 宿主机端口可访问")
    else:
        print("❌ 宿主机端口不可访问")
        return False
    
    return True

def setup_port_forwarding():
    """设置端口转发"""
    print("\n=== 设置端口转发 ===")
    
    # 获取容器IP
    success, stdout, stderr = run_command('docker inspect bmos_frontend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    if not success:
        print("❌ 无法获取前端容器IP")
        return False
    
    frontend_ip = stdout.strip()
    
    success, stdout, stderr = run_command('docker inspect bmos_backend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"')
    if not success:
        print("❌ 无法获取后端容器IP")
        return False
    
    backend_ip = stdout.strip()
    
    print(f"前端容器IP: {frontend_ip}")
    print(f"后端容器IP: {backend_ip}")
    
    # 清除现有端口转发规则
    print("1. 清除现有端口转发规则...")
    run_command("netsh interface portproxy delete v4tov4 listenport=3000")
    run_command("netsh interface portproxy delete v4tov4 listenport=8000")
    
    # 添加新的端口转发规则
    print("2. 添加新的端口转发规则...")
    success1, _, _ = run_command(f"netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress={frontend_ip}")
    success2, _, _ = run_command(f"netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress={backend_ip}")
    
    if success1 and success2:
        print("✅ 端口转发设置成功")
        return True
    else:
        print("❌ 端口转发设置失败")
        return False

def test_localhost_access():
    """测试localhost访问"""
    print("\n=== 测试localhost访问 ===")
    
    # 测试前端
    print("1. 测试前端localhost访问...")
    if check_port_accessibility("localhost", 3000):
        print("✅ 前端localhost访问正常")
    else:
        print("❌ 前端localhost访问异常")
        return False
    
    # 测试后端
    print("2. 测试后端localhost访问...")
    if check_port_accessibility("localhost", 8000):
        print("✅ 后端localhost访问正常")
    else:
        print("❌ 后端localhost访问异常")
        return False
    
    return True

def create_browser_access_script():
    """创建浏览器访问脚本"""
    print("\n=== 创建浏览器访问脚本 ===")
    
    script_content = '''@echo off
echo ========================================
echo BMOS系统浏览器访问脚本
echo ========================================
echo.
echo 当前容器IP地址:
echo   前端容器: 172.21.0.4
echo   后端容器: 172.21.0.7
echo.
echo 访问方式:
echo   方案1: 使用localhost访问（推荐）
echo     前端界面: http://localhost:3000
echo     后端API: http://localhost:8000
echo     健康检查: http://localhost:8000/health
echo.
echo   方案2: 使用容器IP访问
echo     前端界面: http://172.21.0.4:3000
echo     后端API: http://172.21.0.7:8000
echo.
echo   方案3: 使用PowerShell测试
echo     Invoke-WebRequest -Uri "http://localhost:8000/health"
echo.
echo 按任意键打开前端界面...
pause > nul
start http://localhost:3000
echo.
echo 前端界面已打开！
echo.
echo 如果无法访问，请尝试:
echo 1. 以管理员身份运行此脚本
echo 2. 检查Windows防火墙设置
echo 3. 重启Docker Desktop
echo 4. 使用容器内访问方式
echo.
pause
'''
    
    with open('BMOS_BROWSER_ACCESS.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 浏览器访问脚本已创建: BMOS_BROWSER_ACCESS.bat")

def main():
    """主函数"""
    print("=== Windows浏览器访问Docker容器修复工具 ===\n")
    
    # 测试容器访问
    container_ok = test_container_access()
    
    if not container_ok:
        print("\n❌ 容器访问测试失败")
        return False
    
    # 设置端口转发
    port_forward_ok = setup_port_forwarding()
    
    if port_forward_ok:
        # 测试localhost访问
        localhost_ok = test_localhost_access()
        
        if localhost_ok:
            print("\n🎉 浏览器访问问题已解决！")
            print("\n✅ 现在可以使用以下方式访问:")
            print("   - 前端界面: http://localhost:3000")
            print("   - 后端API: http://localhost:8000")
            print("   - 健康检查: http://localhost:8000/health")
            
            # 创建浏览器访问脚本
            create_browser_access_script()
            
            return True
    
    # 创建浏览器访问脚本
    create_browser_access_script()
    
    print("\n⚠️ 浏览器访问问题需要手动解决")
    print("\n💡 建议操作:")
    print("1. 以管理员身份运行PowerShell")
    print("2. 执行端口转发命令")
    print("3. 检查Windows防火墙设置")
    print("4. 重启Docker Desktop")
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)




