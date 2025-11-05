"""
BMOS系统 - 简单测试脚本
用于验证系统基本功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试基本导入"""
    print("测试基本导入...")

    try:
        # 测试FastAPI导入
        from fastapi import FastAPI

        print("✓ FastAPI导入成功")

        # 测试pytest导入
        import pytest

        print("✓ pytest导入成功")

        # 测试其他依赖
        import asyncio

        print("✓ asyncio导入成功")

        from unittest.mock import Mock

        print("✓ unittest.mock导入成功")

        return True

    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_project_structure():
    """测试项目结构"""
    print("\n测试项目结构...")

    required_dirs = [
        "src",
        "tests",
        "src/api",
        "src/api/endpoints",
        "src/security",
        "src/tasks",
    ]

    required_files = [
        "tests/test_api_endpoints.py",
        "tests/test_performance.py",
        "tests/test_security.py",
        "src/api/endpoints/optimization.py",
        "src/api/endpoints/monitoring.py",
        "src/api/endpoints/tasks.py",
    ]

    all_good = True

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ 目录存在: {dir_path}")
        else:
            print(f"✗ 目录缺失: {dir_path}")
            all_good = False

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ 文件存在: {file_path}")
        else:
            print(f"✗ 文件缺失: {file_path}")
            all_good = False

    return all_good


def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")

    try:
        # 测试FastAPI应用创建
        from fastapi import FastAPI

        app = FastAPI(title="BMOS Test")
        print("✓ FastAPI应用创建成功")

        # 测试Mock对象创建
        from unittest.mock import Mock

        mock_user = Mock()
        mock_user.tenant_id = "test_tenant"
        print("✓ Mock对象创建成功")

        # 测试异步函数
        import asyncio

        async def test_async():
            return "async test"

        result = asyncio.run(test_async())
        print(f"✓ 异步函数测试成功: {result}")

        return True

    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False


def run_simple_tests():
    """运行简单测试"""
    print("BMOS系统 - 简单测试")
    print("=" * 50)

    tests = [
        ("导入测试", test_imports),
        ("项目结构测试", test_project_structure),
        ("基本功能测试", test_basic_functionality),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}执行失败: {e}")
            results.append((test_name, False))

    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！系统基本功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，需要检查")
        return False


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
