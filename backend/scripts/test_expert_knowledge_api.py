"""
专家知识库API测试脚本
测试主要API端点的功能
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8081"


def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(test_name, success, message="", response=None):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"      {message}")
    if response and not success:
        try:
            print(f"      响应: {response.text[:200]}")
        except:
            pass


def test_health_check():
    """测试健康检查端点"""
    print_header("测试1: 健康检查")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200

        if success:
            data = response.json()
            print_result("健康检查", True, f"状态: {data.get('status', 'unknown')}")
            if "mock_mode" in data:
                print(
                    f"      Mock模式: 数据库={data['mock_mode'].get('database', False)}, 缓存={data['mock_mode'].get('cache', False)}"
                )
        else:
            print_result("健康检查", False, f"状态码: {response.status_code}")

        return success
    except Exception as e:
        print_result("健康检查", False, f"错误: {e}")
        return False


def test_root_endpoint():
    """测试根端点"""
    print_header("测试2: API根端点")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        success = response.status_code == 200

        if success:
            data = response.json()
            print_result("根端点", True, f"版本: {data.get('version', 'unknown')}")

            # 检查专家知识库端点是否存在
            endpoints = data.get("endpoints", {})
            if "expert-knowledge" in str(endpoints) or "/expert-knowledge" in str(data):
                print("      ✅ 专家知识库端点已注册")
            else:
                print("      ⚠️ 专家知识库端点未在根端点中列出（可能正常）")
        else:
            print_result("根端点", False, f"状态码: {response.status_code}")

        return success
    except Exception as e:
        print_result("根端点", False, f"错误: {e}")
        return False


def test_create_knowledge():
    """测试创建知识端点"""
    print_header("测试3: 创建知识")

    try:
        knowledge_data = {
            "title": "成本优化方法论测试",
            "summary": "这是一个测试知识条目，用于验证API功能",
            "content": "成本优化的核心原则包括：1. 识别成本驱动因素 2. 优化资源配置 3. 提高运营效率",
            "knowledge_type": "methodology",
            "domain_category": "cost_optimization",
            "problem_type": "optimization_problem",
            "tags": ["成本", "优化", "方法论", "测试"],
            "source_reference": "测试文档 - 2025-01",
            "is_active": True,
        }

        response = requests.post(
            f"{BASE_URL}/expert-knowledge/",
            json=knowledge_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        success = response.status_code in [200, 201]

        if success:
            data = response.json()
            knowledge_id = data.get("id") or data.get("knowledge", {}).get("id")
            print_result("创建知识", True, f"知识ID: {knowledge_id}")
            return knowledge_id
        else:
            print_result("创建知识", False, f"状态码: {response.status_code}", response)
            return None

    except Exception as e:
        print_result("创建知识", False, f"错误: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_search_knowledge():
    """测试搜索知识端点"""
    print_header("测试4: 搜索知识")

    try:
        search_params = {
            "query": "成本优化",
            "domain_category": "cost_optimization",
            "problem_type": "optimization_problem",
            "limit": 10,
        }

        response = requests.post(
            f"{BASE_URL}/expert-knowledge/search",
            json=search_params,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        success = response.status_code == 200

        if success:
            data = response.json()
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict):
                count = len(data.get("results", [])) if "results" in data else 0
            else:
                count = 0

            print_result("搜索知识", True, f"找到 {count} 条知识")
            return True
        else:
            print_result("搜索知识", False, f"状态码: {response.status_code}", response)
            return False

    except Exception as e:
        print_result("搜索知识", False, f"错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_get_categories():
    """测试获取分类端点"""
    print_header("测试5: 获取分类信息")

    endpoints_to_test = [
        ("/expert-knowledge/categories/domains", "领域分类"),
        ("/expert-knowledge/categories/problem-types", "问题类型"),
        ("/expert-knowledge/categories/knowledge-types", "知识类型"),
    ]

    results = []

    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            success = response.status_code == 200

            if success:
                data = response.json()
                count = (
                    len(data.get("categories", []))
                    if isinstance(data, dict)
                    else len(data) if isinstance(data, list) else 0
                )
                print_result(f"获取{name}", True, f"找到 {count} 个分类")
                results.append(True)
            else:
                print_result(f"获取{name}", False, f"状态码: {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(f"获取{name}", False, f"错误: {e}")
            results.append(False)

    return all(results)


def test_generate_reasoning_chain():
    """测试推理链生成端点"""
    print_header("测试6: 生成推理链")

    try:
        context = {
            "domain_category": "resource_allocation",
            "problem_type": "decision_problem",
            "description": "需要决定资源投入方向，优化成本结构",
            "data_evidence": {"summary": "数据分析显示成本结构需要优化"},
        }

        response = requests.post(
            f"{BASE_URL}/expert-knowledge/generate-reasoning-chain",
            json=context,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )

        success = response.status_code == 200

        if success:
            data = response.json()
            reasoning_chain = data.get("reasoning_chain", {})
            steps_count = len(reasoning_chain.get("reasoning_steps", []))

            print_result("生成推理链", True, f"生成了 {steps_count} 个推理步骤")
            if "conclusion" in reasoning_chain:
                conclusion = reasoning_chain["conclusion"]
                print(f"      结论摘要: {conclusion.get('summary', '')[:100]}...")
            return True
        else:
            print_result(
                "生成推理链", False, f"状态码: {response.status_code}", response
            )
            return False

    except Exception as e:
        print_result("生成推理链", False, f"错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_learning_api():
    """测试学习模块API"""
    print_header("测试7: 学习模块API")

    try:
        # 测试创建课程
        course_data = {
            "title": "商业模式优化课程",
            "description": "深入学习商业模式优化的理论与方法",
            "difficulty_level": "intermediate",
            "estimated_hours": 8.0,
        }

        response = requests.post(
            f"{BASE_URL}/learning/courses/",
            json=course_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        success = response.status_code in [200, 201]

        if success:
            data = response.json()
            course_id = data.get("course_id") or data.get("id")
            print_result("创建课程", True, f"课程ID: {course_id}")
            return True
        else:
            print_result("创建课程", False, f"状态码: {response.status_code}", response)
            return False

    except Exception as e:
        print_result("学习模块API", False, f"错误: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  专家知识库API测试")
    print("=" * 70)
    print(f"\n测试服务器: {BASE_URL}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = {}

    # 运行所有测试
    test_results["健康检查"] = test_health_check()
    test_results["根端点"] = test_root_endpoint()
    test_results["创建知识"] = test_create_knowledge() is not None
    test_results["搜索知识"] = test_search_knowledge()
    test_results["获取分类"] = test_get_categories()
    test_results["生成推理链"] = test_generate_reasoning_chain()
    test_results["学习模块"] = test_learning_api()

    # 打印总结
    print_header("测试总结")

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} | {test_name}")

    print(f"\n总计: {passed_tests}/{total_tests} 个测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有API测试通过！")
        print(f"\n📖 API文档: {BASE_URL}/docs")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} 个测试失败，请检查API服务")
        print(f"\n💡 提示: 确保服务正在运行: {BASE_URL}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
