#!/usr/bin/env python3
"""
BMOS系统 - 快速测试脚本
提供一键运行所有测试的功能
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{description}")
    print(f"命令: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        print(f"输出: {e.stdout}")
        print(f"错误: {e.stderr}")
        return False

def check_environment():
    """检查测试环境"""
    print(f"\n检查测试环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print("Python版本过低，需要3.8+")
        return False
    print(f"Python版本: {python_version.major}.{python_version.minor}")
    
    # 检查pytest
    try:
        import pytest
        print(f"pytest版本: {pytest.__version__}")
    except ImportError:
        print("pytest未安装")
        return False
    
    # 检查项目结构
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / "backend" / "tests"
    if not tests_dir.exists():
        print("测试目录不存在")
        return False
    print("测试目录存在")
    
    return True

def install_dependencies():
    """安装测试依赖"""
    print("\n安装测试依赖...")
    
    dependencies = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "httpx",
        "psutil"
    ]
    
    for dep in dependencies:
        print(f"安装 {dep}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{dep} 安装成功")
        else:
            print(f"{dep} 安装失败: {result.stderr}")
            return False
    
    return True

def run_tests(test_type="all", verbose=False):
    """运行测试"""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    tests_dir = backend_dir / "tests"
    
    # 切换到backend目录
    os.chdir(backend_dir)
    
    # 设置Python路径
    os.environ["PYTHONPATH"] = str(backend_dir)
    
    # 构建pytest命令
    cmd_parts = ["python", "-m", "pytest"]
    
    if verbose:
        cmd_parts.append("-v")
    
    # 根据测试类型选择测试文件
    if test_type == "api":
        cmd_parts.append("tests/test_api_endpoints.py")
    elif test_type == "performance":
        cmd_parts.append("tests/test_performance.py")
    elif test_type == "security":
        cmd_parts.append("tests/test_security.py")
    elif test_type == "comprehensive":
        cmd_parts.append("tests/test_comprehensive.py")
    else:  # all
        cmd_parts.append("tests/")
    
    # 添加覆盖率选项
    cmd_parts.extend(["--cov=src", "--cov-report=term-missing"])
    
    command = " ".join(cmd_parts)
    
    return run_command(command, f"运行{test_type}测试")

def run_coverage_report():
    """生成覆盖率报告"""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    
    os.chdir(backend_dir)
    os.environ["PYTHONPATH"] = str(backend_dir)
    
    # 生成HTML覆盖率报告
    command = "python -m pytest tests/ --cov=src --cov-report=html --cov-report=term"
    
    success = run_command(command, "生成覆盖率报告")
    
    if success:
        html_report = backend_dir / "htmlcov" / "index.html"
        if html_report.exists():
            print(f"\n覆盖率报告已生成: {html_report}")
            print("在浏览器中打开查看详细报告")
    
    return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="BMOS系统测试脚本")
    parser.add_argument("--type", choices=["all", "api", "performance", "security", "comprehensive"], 
                       default="all", help="测试类型")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--install", action="store_true", help="安装依赖")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--check", action="store_true", help="检查环境")
    
    args = parser.parse_args()
    
    print("BMOS系统测试脚本")
    print("=" * 50)
    
    # 检查环境
    if args.check:
        if not check_environment():
            print("环境检查失败")
            return 1
        print("环境检查通过")
        return 0
    
    # 安装依赖
    if args.install:
        if not install_dependencies():
            print("依赖安装失败")
            return 1
        print("依赖安装完成")
        return 0
    
    # 检查环境
    if not check_environment():
        print("环境检查失败，请先运行: python test_runner.py --check")
        return 1
    
    # 运行测试
    if args.coverage:
        success = run_coverage_report()
    else:
        success = run_tests(args.type, args.verbose)
    
    if success:
        print(f"\n{args.type}测试完成")
        return 0
    else:
        print(f"\n{args.type}测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
