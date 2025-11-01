#!/usr/bin/env python3
"""
配置VPN绕过Docker网络
"""
import subprocess
import sys

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

def get_docker_networks():
    """获取Docker网络信息"""
    print("=== 获取Docker网络信息 ===")
    
    # 获取Docker网络
    success, stdout, stderr = run_command("docker network ls")
    if not success:
        print("❌ 无法获取Docker网络信息")
        return []
    
    print("Docker网络列表:")
    print(stdout)
    
    # 获取具体网络信息
    success, stdout, stderr = run_command("docker network inspect bmos_network")
    if success:
        print("BMOS网络信息:")
        print(stdout)
    
    return []

def configure_route_bypass():
    """配置路由绕过"""
    print("\n=== 配置路由绕过 ===")
    
    # Docker网络段
    docker_networks = [
        "172.17.0.0/16",
        "172.18.0.0/16", 
        "172.19.0.0/16",
        "172.20.0.0/16",
        "172.21.0.0/16",
        "172.22.0.0/16"
    ]
    
    print("正在配置Docker网络段绕过...")
    
    for network in docker_networks:
        # 添加路由规则
        cmd = f"route add {network} 127.0.0.1 metric 1"
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ {network} 路由配置成功")
        else:
            if "对象已存在" in stderr or "already exists" in stderr.lower():
                print(f"⚠️ {network} 路由已存在")
            else:
                print(f"❌ {network} 路由配置失败: {stderr}")
    
    # 配置localhost绕过
    print("\n配置localhost绕过...")
    localhost_routes = [
        "127.0.0.1/32",
        "localhost"
    ]
    
    for route in localhost_routes:
        cmd = f"route add {route} 127.0.0.1 metric 1"
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ {route} 路由配置成功")
        else:
            if "对象已存在" in stderr or "already exists" in stderr.lower():
                print(f"⚠️ {route} 路由已存在")
            else:
                print(f"❌ {route} 路由配置失败: {stderr}")

def show_current_routes():
    """显示当前路由"""
    print("\n=== 当前路由表 ===")
    
    success, stdout, stderr = run_command("route print")
    if success:
        print("路由表:")
        lines = stdout.split('\n')
        docker_routes = [line for line in lines if '172.17' in line or '172.18' in line or '172.19' in line or '172.20' in line or '172.21' in line or '172.22' in line]
        
        if docker_routes:
            print("Docker相关路由:")
            for route in docker_routes:
                print(f"  {route.strip()}")
        else:
            print("未找到Docker相关路由")
    else:
        print("❌ 无法获取路由表")

def create_vpn_config_guide():
    """创建VPN配置指南"""
    print("\n=== 创建VPN配置指南 ===")
    
    guide_content = '''# VPN绕过Docker网络配置指南

## 🎯 问题描述
VPN导致无法访问Docker容器中的前端服务

## 🔧 解决方案

### 方案1: LetsVPN配置（推荐）

#### 步骤1: 打开LetsVPN设置
1. 右键点击系统托盘中的LetsVPN图标
2. 选择"设置"或"Preferences"
3. 找到"网络设置"或"Network Settings"

#### 步骤2: 配置本地网络绕过
1. 找到"本地网络绕过"、"LAN Bypass"或"Local Network"选项
2. 启用该功能
3. 添加以下网络段：
   ```
   172.17.0.0/16
   172.18.0.0/16
   172.19.0.0/16
   172.20.0.0/16
   172.21.0.0/16
   172.22.0.0/16
   127.0.0.1/32
   localhost
   ```

#### 步骤3: 保存并重启VPN
1. 保存设置
2. 断开VPN连接
3. 重新连接VPN

### 方案2: 其他VPN软件配置

#### OpenVPN
在配置文件中添加：
```
route 172.17.0.0 255.255.0.0 net_gateway
route 172.18.0.0 255.255.0.0 net_gateway
route 172.19.0.0 255.255.0.0 net_gateway
route 172.20.0.0 255.255.0.0 net_gateway
route 172.21.0.0 255.255.0.0 net_gateway
route 172.22.0.0 255.255.0.0 net_gateway
```

#### WireGuard
在配置文件中添加：
```
[Peer]
AllowedIPs = 172.17.0.0/16, 172.18.0.0/16, 172.19.0.0/16, 172.20.0.0/16, 172.21.0.0/16, 172.22.0.0/16
```

### 方案3: Windows路由表配置

#### 手动配置
以管理员身份运行PowerShell，执行：
```powershell
route add 172.17.0.0 mask 255.255.0.0 127.0.0.1 metric 1
route add 172.18.0.0 mask 255.255.0.0 127.0.0.1 metric 1
route add 172.19.0.0 mask 255.255.0.0 127.0.0.1 metric 1
route add 172.20.0.0 mask 255.255.0.0 127.0.0.1 metric 1
route add 172.21.0.0 mask 255.255.0.0 127.0.0.1 metric 1
route add 172.22.0.0 mask 255.255.0.0 127.0.0.1 metric 1
```

#### 自动配置
运行脚本：
```bash
python scripts/configure_vpn_bypass.py
```

## 🧪 测试验证

配置完成后，运行测试：
```bash
python test_simple.py
```

## 🛠️ 故障排除

### 如果配置后仍然无法访问
1. 重启VPN客户端
2. 重启Docker Desktop
3. 检查Windows防火墙设置
4. 使用容器内访问方式

### 如果路由配置失败
1. 确保以管理员身份运行
2. 检查路由是否已存在
3. 手动删除冲突的路由

## 🎯 推荐操作顺序

1. **首选**: 配置VPN软件的本地网络绕过
2. **备选**: 使用Windows路由表配置
3. **临时**: 使用容器内访问方式
4. **测试**: 验证配置是否生效

## 📝 注意事项

- 配置后需要重启VPN才能生效
- 某些VPN软件可能不支持本地网络绕过
- 路由配置在重启后可能丢失，需要重新配置
- 建议先备份当前网络配置
'''
    
    with open('VPN_BYPASS_CONFIG_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ VPN配置指南已创建: VPN_BYPASS_CONFIG_GUIDE.md")

def main():
    """主函数"""
    print("=== VPN绕过Docker网络配置工具 ===\n")
    
    # 检查管理员权限
    try:
        run_command("net session >nul 2>&1")
    except:
        print("❌ 需要管理员权限运行此脚本")
        print("请以管理员身份运行PowerShell，然后执行此脚本")
        return False
    
    # 获取Docker网络信息
    get_docker_networks()
    
    # 配置路由绕过
    configure_route_bypass()
    
    # 显示当前路由
    show_current_routes()
    
    # 创建配置指南
    create_vpn_config_guide()
    
    print("\n=== 配置完成 ===")
    print("\n💡 下一步操作:")
    print("1. 重启VPN客户端")
    print("2. 运行测试: python test_simple.py")
    print("3. 如果仍有问题，查看配置指南: VPN_BYPASS_CONFIG_GUIDE.md")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)






