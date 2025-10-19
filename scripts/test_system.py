#!/usr/bin/env python3
"""
系统测试启动脚本 - QBM AI System
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_service_status():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    services = [
        ("后端服务", "http://localhost:8000/health"),
        ("前端服务", "http://localhost:8080"),
        ("数据库", "docker exec qbm-mysql mysqladmin -u root -ppassword status"),
        ("Redis", "docker exec qbm-redis redis-cli ping")
    ]
    
    all_healthy = True
    for service_name, check_command in services:
        try:
            if check_command.startswith("http"):
                import requests
                response = requests.get(check_command, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {service_name}: 正常")
                else:
                    print(f"  ❌ {service_name}: 异常 (HTTP {response.status_code})")
                    all_healthy = False
            else:
                result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {service_name}: 正常")
                else:
                    print(f"  ❌ {service_name}: 异常")
                    all_healthy = False
        except Exception as e:
            print(f"  ❌ {service_name}: 检查失败 - {e}")
            all_healthy = False
    
    return all_healthy

def main():
    """主函数"""
    print("QBM AI System 系统测试")
    print("=" * 50)
    
    # 检查是否在项目根目录
    if not Path("docker-compose.yml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 选择测试类型
    print("请选择测试类型:")
    print("1. 快速测试 (推荐)")
    print("2. 完整测试")
    print("3. 生成测试数据")
    print("4. 启动系统")
    print("5. 停止系统")
    print("6. 重启系统")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    if choice == "1":
        # 快速测试
        print("\n🚀 开始快速测试...")
        
        # 检查服务状态
        if not check_service_status():
            print("\n⚠️  服务状态异常，请先启动系统")
            print("启动命令: python scripts/start.py start")
            return
        
        # 运行快速测试
        if run_command("python scripts/quick_test.py", "快速测试"):
            print("\n🎉 快速测试完成！")
        else:
            print("\n❌ 快速测试失败，请检查系统状态")
    
    elif choice == "2":
        # 完整测试
        print("\n🚀 开始完整测试...")
        
        # 检查服务状态
        if not check_service_status():
            print("\n⚠️  服务状态异常，请先启动系统")
            return
        
        # 运行完整测试套件
        if run_command("python scripts/run_tests.py", "完整测试"):
            print("\n🎉 完整测试完成！")
        else:
            print("\n❌ 完整测试失败，请检查系统状态")
    
    elif choice == "3":
        # 生成测试数据
        print("\n🚀 生成测试数据...")
        if run_command("python scripts/generate_test_data.py", "测试数据生成"):
            print("\n🎉 测试数据生成完成！")
            print("📁 测试数据位置: test_data/")
        else:
            print("\n❌ 测试数据生成失败")
    
    elif choice == "4":
        # 启动系统
        print("\n🚀 启动系统...")
        if run_command("python scripts/start.py start", "系统启动"):
            print("\n🎉 系统启动完成！")
            print("⏳ 等待服务完全启动...")
            time.sleep(30)
            
            # 检查服务状态
            if check_service_status():
                print("\n✅ 所有服务启动成功！")
                print("\n🌐 访问地址:")
                print("前端: http://localhost:8080")
                print("后端: http://localhost:8000")
                print("文档: http://localhost:8000/docs")
                print("账户: admin / admin123")
            else:
                print("\n⚠️  部分服务启动异常，请检查日志")
        else:
            print("\n❌ 系统启动失败")
    
    elif choice == "5":
        # 停止系统
        print("\n🛑 停止系统...")
        if run_command("python scripts/start.py stop", "系统停止"):
            print("\n✅ 系统已停止")
        else:
            print("\n❌ 系统停止失败")
    
    elif choice == "6":
        # 重启系统
        print("\n🔄 重启系统...")
        
        # 停止系统
        print("停止现有服务...")
        run_command("python scripts/start.py stop", "系统停止")
        
        # 等待
        time.sleep(5)
        
        # 启动系统
        print("启动服务...")
        if run_command("python scripts/start.py start", "系统启动"):
            print("\n🎉 系统重启完成！")
            print("⏳ 等待服务完全启动...")
            time.sleep(30)
            
            # 检查服务状态
            if check_service_status():
                print("\n✅ 所有服务重启成功！")
            else:
                print("\n⚠️  部分服务重启异常，请检查日志")
        else:
            print("\n❌ 系统重启失败")
    
    else:
        print("❌ 无效选择，请输入1-6")
        return
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()


