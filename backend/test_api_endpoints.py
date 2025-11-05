#!/usr/bin/env python3
"""
BMOS API测试脚本
测试API端点的基本功能
"""

import requests
import json
import time
import sys
from typing import Dict, Any


class BMOSAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        data: Dict[Any, Any] = None,
        headers: Dict[str, str] = None,
    ) -> bool:
        """测试单个API端点"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(
                    url, json=data, headers=headers, timeout=10
                )
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                print(f"[ERROR] 不支持的HTTP方法: {method}")
                return False

            success = response.status_code == expected_status
            status = "PASS" if success else "FAIL"

            print(f"[{status}] {method} {endpoint} - 状态码: {response.status_code}")

            if not success:
                print(
                    f"      期望状态码: {expected_status}, 实际状态码: {response.status_code}"
                )
                if response.text:
                    print(f"      响应内容: {response.text[:200]}...")

            self.results.append(
                {
                    "method": method,
                    "endpoint": endpoint,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "success": success,
                    "response_time": response.elapsed.total_seconds(),
                }
            )

            return success

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] 连接失败: {url}")
            return False
        except requests.exceptions.Timeout:
            print(f"[ERROR] 请求超时: {url}")
            return False
        except Exception as e:
            print(f"[ERROR] 请求异常: {e}")
            return False

    def run_all_tests(self):
        """运行所有API测试"""
        print("BMOS API测试开始")
        print("=" * 50)

        # 基础健康检查
        print("\n1. 基础健康检查:")
        self.test_endpoint("GET", "/health")
        self.test_endpoint("GET", "/api/v1/status")

        # API文档
        print("\n2. API文档:")
        self.test_endpoint("GET", "/docs", 200)
        self.test_endpoint("GET", "/redoc", 200)

        # 认证相关
        print("\n3. 认证相关:")
        self.test_endpoint("POST", "/api/v1/auth/login", 422)  # 缺少参数，期望422
        self.test_endpoint("POST", "/api/v1/auth/register", 422)  # 缺少参数，期望422

        # 模型管理
        print("\n4. 模型管理:")
        self.test_endpoint("GET", "/api/v1/models", 200)
        self.test_endpoint("POST", "/api/v1/models", 422)  # 缺少参数，期望422

        # 预测服务
        print("\n5. 预测服务:")
        self.test_endpoint("GET", "/api/v1/predictions", 200)
        self.test_endpoint("POST", "/api/v1/predictions", 422)  # 缺少参数，期望422

        # 数据管理
        print("\n6. 数据管理:")
        self.test_endpoint("GET", "/api/v1/data", 200)
        self.test_endpoint("POST", "/api/v1/data", 422)  # 缺少参数，期望422

        # 数据导入
        print("\n7. 数据导入:")
        self.test_endpoint("GET", "/api/v1/data-import", 200)
        self.test_endpoint("POST", "/api/v1/data-import", 422)  # 缺少参数，期望422

        # 企业记忆
        print("\n8. 企业记忆:")
        self.test_endpoint("GET", "/api/v1/memories", 200)
        self.test_endpoint("POST", "/api/v1/memories", 422)  # 缺少参数，期望422

        # 任务管理
        print("\n9. 任务管理:")
        self.test_endpoint("GET", "/api/v1/tasks", 200)
        self.test_endpoint("POST", "/api/v1/tasks", 422)  # 缺少参数，期望422

        # 监控服务
        print("\n10. 监控服务:")
        self.test_endpoint("GET", "/api/v1/monitoring", 200)
        self.test_endpoint("GET", "/api/v1/monitoring/health", 200)
        self.test_endpoint("GET", "/api/v1/monitoring/metrics", 200)

        # 优化服务
        print("\n11. 优化服务:")
        self.test_endpoint("GET", "/api/v1/optimization", 200)
        self.test_endpoint("POST", "/api/v1/optimization", 422)  # 缺少参数，期望422

        # AI Copilot
        print("\n12. AI Copilot:")
        self.test_endpoint("POST", "/api/v1/ai-copilot/chat", 422)  # 缺少参数，期望422

        self.print_summary()

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("测试总结:")

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        if total_tests > 0:
            print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        else:
            print("通过率: 0.0%")

        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.results:
                if not result["success"]:
                    print(
                        f"  - {result['method']} {result['endpoint']} "
                        f"(期望: {result['expected_status']}, 实际: {result['actual_status']})"
                    )

        # 计算平均响应时间
        avg_response_time = sum(r["response_time"] for r in self.results) / total_tests
        print(f"\n平均响应时间: {avg_response_time:.3f}秒")

        print("\n" + "=" * 50)


def main():
    """主函数"""
    print("BMOS API测试工具")
    print("正在测试API服务...")

    # 等待服务启动
    print("等待API服务启动...")
    time.sleep(2)

    tester = BMOSAPITester()
    tester.run_all_tests()

    # 返回退出码
    failed_tests = sum(1 for r in tester.results if not r["success"])
    sys.exit(0 if failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
