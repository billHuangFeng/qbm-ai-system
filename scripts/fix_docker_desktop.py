#!/usr/bin/env python3
"""
修复Docker Desktop启动问题
"""
import subprocess
import time
import os

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

def check_docker_desktop_status():
    """检查Docker Desktop状态"""
    print("=== 检查Docker Desktop状态 ===")
    
    # 检查Docker Desktop进程
    print("1. 检查Docker Desktop进程...")
    success, stdout, stderr = run_command("tasklist | findstr Docker")
    if success and "Docker" in stdout:
        print("✅ Docker Desktop进程运行中")
        print(f"   进程: {stdout.strip()}")
    else:
        print("❌ Docker Desktop进程未运行")
    
    # 检查Docker服务
    print("2. 检查Docker服务...")
    success, stdout, stderr = run_command("sc query com.docker.service")
    if success:
        print("✅ Docker服务状态:")
        print(f"   {stdout.strip()}")
    else:
        print("❌ 无法查询Docker服务")
    
    return True

def restart_docker_desktop():
    """重启Docker Desktop"""
    print("\n=== 重启Docker Desktop ===")
    
    # 停止Docker Desktop
    print("1. 停止Docker Desktop...")
    run_command("taskkill /f /im Docker Desktop.exe")
    run_command("taskkill /f /im com.docker.backend.exe")
    run_command("taskkill /f /im com.docker.proxy.exe")
    time.sleep(5)
    
    # 启动Docker Desktop
    print("2. 启动Docker Desktop...")
    docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if os.path.exists(docker_path):
        run_command(f'"{docker_path}"')
        print("✅ Docker Desktop启动命令已执行")
    else:
        print("❌ 找不到Docker Desktop安装路径")
        return False
    
    # 等待启动
    print("3. 等待Docker Desktop启动...")
    for i in range(30):
        time.sleep(2)
        success, stdout, stderr = run_command("docker --version")
        if success:
            print("✅ Docker Desktop启动成功")
            return True
        print(f"   等待中... ({i+1}/30)")
    
    print("❌ Docker Desktop启动超时")
    return False

def test_docker_after_restart():
    """重启后测试Docker"""
    print("\n=== 重启后测试Docker ===")
    
    # 测试Docker命令
    print("1. 测试Docker命令...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        print("✅ Docker命令正常")
        print(f"   版本: {stdout.strip()}")
    else:
        print("❌ Docker命令异常")
        return False
    
    # 测试Docker Compose
    print("2. 测试Docker Compose...")
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print("✅ Docker Compose正常")
        print(f"   版本: {stdout.strip()}")
    else:
        print("❌ Docker Compose异常")
        return False
    
    # 测试Docker服务
    print("3. 测试Docker服务...")
    success, stdout, stderr = run_command("docker ps")
    if success:
        print("✅ Docker服务正常")
        print("   容器列表:")
        print(f"   {stdout.strip()}")
    else:
        print("❌ Docker服务异常")
        print(f"   错误: {stderr}")
        return False
    
    return True

def start_bmos_containers():
    """启动BMOS容器"""
    print("\n=== 启动BMOS容器 ===")
    
    # 启动容器
    print("1. 启动BMOS容器...")
    success, stdout, stderr = run_command("docker-compose -f docker-compose-dev.yml up -d")
    if success:
        print("✅ BMOS容器启动成功")
    else:
        print("❌ BMOS容器启动失败")
        print(f"   错误: {stderr}")
        return False
    
    # 等待容器启动
    print("2. 等待容器启动...")
    time.sleep(10)
    
    # 检查容器状态
    print("3. 检查容器状态...")
    success, stdout, stderr = run_command("docker ps --format 'table {{.Names}}\\t{{.Status}}'")
    if success:
        print("✅ 容器状态:")
        print(f"   {stdout.strip()}")
    else:
        print("❌ 无法获取容器状态")
        return False
    
    return True

def create_docker_fix_guide():
    """创建Docker修复指南"""
    print("\n=== 创建Docker修复指南 ===")
    
    guide_content = '''# Docker Desktop修复指南

## 问题描述
Docker Desktop无法启动: "Docker Desktop is unable to start"

## 解决方案

### 方案1: 重启Docker Desktop
1. 右键点击系统托盘中的Docker图标
2. 选择 "Restart Docker Desktop"
3. 等待重启完成（约2-3分钟）

### 方案2: 手动重启Docker服务
```powershell
# 以管理员身份运行PowerShell
net stop com.docker.service
net start com.docker.service
```

### 方案3: 重启计算机
如果上述方案无效，重启计算机

### 方案4: 重新安装Docker Desktop
1. 卸载Docker Desktop
2. 重启计算机
3. 重新安装Docker Desktop

## 预防措施
1. 定期重启Docker Desktop
2. 避免同时运行多个虚拟化软件
3. 确保Windows更新到最新版本

## 系统要求
- Windows 10 版本 1903 或更高版本
- 启用Hyper-V或WSL2
- 至少4GB RAM
- 至少2GB可用磁盘空间
'''
    
    with open('DOCKER_DESKTOP_FIX_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Docker修复指南已创建: DOCKER_DESKTOP_FIX_GUIDE.md")

def main():
    """主函数"""
    print("=== Docker Desktop修复工具 ===\n")
    
    # 检查Docker Desktop状态
    check_docker_desktop_status()
    
    # 重启Docker Desktop
    restart_ok = restart_docker_desktop()
    
    if restart_ok:
        # 测试Docker
        docker_ok = test_docker_after_restart()
        
        if docker_ok:
            # 启动BMOS容器
            containers_ok = start_bmos_containers()
            
            if containers_ok:
                print("\n🎉 Docker Desktop修复成功！")
                print("✅ BMOS系统已重新启动")
                print("现在可以正常使用系统了")
                return True
    
    # 创建修复指南
    create_docker_fix_guide()
    
    print("\n⚠️ Docker Desktop需要手动修复")
    print("\n💡 建议操作:")
    print("1. 右键点击系统托盘中的Docker图标")
    print("2. 选择 'Restart Docker Desktop'")
    print("3. 等待重启完成")
    print("4. 重新运行测试")
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)




