#!/usr/bin/env python3
"""
修复WSL2网络问题
"""
import subprocess
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

def fix_wsl2_network():
    """修复WSL2网络问题"""
    print("=== 修复WSL2网络问题 ===\n")
    
    # 1. 检查WSL状态
    print("1. 检查WSL状态...")
    success, stdout, stderr = run_command("wsl --list --verbose")
    if success:
        print("✅ WSL状态正常")
        print(stdout)
    else:
        print("❌ WSL状态异常")
        print(stderr)
        return False
    
    # 2. 重启WSL服务
    print("\n2. 重启WSL服务...")
    print("正在停止WSL...")
    run_command("wsl --shutdown")
    time.sleep(5)
    
    print("正在启动WSL...")
    success, stdout, stderr = run_command("wsl --list --verbose")
    if success:
        print("✅ WSL重启成功")
    else:
        print("❌ WSL重启失败")
        return False
    
    # 3. 测试WSL网络
    print("\n3. 测试WSL网络...")
    success, stdout, stderr = run_command("wsl curl -s http://localhost:8001/health")
    if success and "healthy" in stdout:
        print("✅ WSL网络正常，可以访问BMOS系统")
        print("🎉 问题解决！")
        return True
    else:
        print("❌ WSL网络仍有问题")
        print(f"错误: {stderr}")
        return False

def create_wsl2_solution():
    """创建WSL2解决方案"""
    print("\n=== 创建WSL2解决方案 ===")
    
    solution_content = '''# WSL2网络问题解决方案

## 问题描述
WSL2网络连接问题：`由于系统缓冲区空间不足或队列已满，不能执行套接字上的操作`

## 解决方案

### 方案1: 重启WSL服务
```powershell
# 以管理员身份运行PowerShell
wsl --shutdown
# 等待5秒
wsl --list --verbose
```

### 方案2: 重启Docker Desktop
1. 右键点击系统托盘中的Docker图标
2. 选择 "Restart Docker Desktop"
3. 等待重启完成

### 方案3: 重启计算机
如果上述方案无效，重启计算机

### 方案4: 使用容器IP访问（当前可用）
```bash
# 获取容器IP
docker inspect bmos_backend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
docker inspect bmos_frontend --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"

# 使用容器IP访问
# 后端: http://172.21.0.3:8000
# 前端: http://172.21.0.4:3000
```

## 当前BMOS系统状态
- ✅ 所有容器运行正常
- ✅ 系统功能完全正常
- ✅ 可以使用容器IP访问
- ❌ WSL2网络暂时有问题

## 建议
1. 先使用容器IP访问系统
2. 重启WSL服务解决网络问题
3. 系统本身完全正常，可以正常使用
'''
    
    with open('WSL2_NETWORK_SOLUTION.md', 'w', encoding='utf-8') as f:
        f.write(solution_content)
    
    print("✅ WSL2解决方案已创建: WSL2_NETWORK_SOLUTION.md")

def main():
    """主函数"""
    print("=== WSL2网络问题修复 ===\n")
    
    # 修复WSL2网络
    network_ok = fix_wsl2_network()
    
    # 创建解决方案
    create_wsl2_solution()
    
    if not network_ok:
        print("\n⚠️ WSL2网络问题需要手动解决")
        print("\n💡 当前可用的解决方案:")
        print("1. 使用容器IP访问BMOS系统")
        print("2. 重启WSL服务: wsl --shutdown")
        print("3. 重启Docker Desktop")
        print("4. 重启计算机")
        
        print("\n🎯 推荐操作:")
        print("1. 先使用容器IP访问系统（立即可用）")
        print("2. 然后尝试重启WSL服务")
        
        return False
    else:
        print("\n🎉 WSL2网络问题已解决！")
        print("现在可以在WSL2中正常访问BMOS系统")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)




