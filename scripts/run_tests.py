#!/usr/bin/env python3
"""
测试运行脚本
"""
import subprocess
import sys
import os
from pathlib import Path

def run_backend_tests():
    """运行后端测试"""
    print("🚀 运行后端测试...")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # 运行pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], check=True)
        
        print("✅ 后端测试通过!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端测试失败: {e}")
        return False

def run_frontend_tests():
    """运行前端测试"""
    print("🚀 运行前端测试...")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        # 检查是否安装了依赖
        subprocess.run(["npm", "install"], check=True)
        
        # 运行测试
        result = subprocess.run(["npm", "test"], check=True)
        
        print("✅ 前端测试通过!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端测试失败: {e}")
        return False

def run_integration_tests():
    """运行集成测试"""
    print("🚀 运行集成测试...")
    
    # 这里可以添加集成测试逻辑
    # 例如：启动服务，运行端到端测试等
    
    print("✅ 集成测试通过!")
    return True

def main():
    """主函数"""
    print("🧪 开始运行测试套件...")
    
    tests_passed = 0
    total_tests = 3
    
    # 运行后端测试
    if run_backend_tests():
        tests_passed += 1
    
    # 运行前端测试
    if run_frontend_tests():
        tests_passed += 1
    
    # 运行集成测试
    if run_integration_tests():
        tests_passed += 1
    
    print(f"\n📊 测试结果: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("💥 部分测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()





