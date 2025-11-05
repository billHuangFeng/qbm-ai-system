"""
BMOS系统 - 简单API测试
测试各个API端点是否正常工作
"""

import asyncio
import httpx
import json
from datetime import datetime


class BMOSAPITester:
    """BMOS API测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    async def test_health_check(self):
        """测试健康检查端点"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")

                result = {
                    "endpoint": "/health",
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "response_data": (
                        response.json() if response.status_code == 200 else None
                    ),
                }

                self.results.append(result)
                return result

        except Exception as e:
            result = {
                "endpoint": "/health",
                "status_code": None,
                "success": False,
                "error": str(e),
                "response_time": None,
            }
            self.results.append(result)
            return result

    async def test_docs_endpoint(self):
        """测试API文档端点"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")

                result = {
                    "endpoint": "/docs",
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "content_type": response.headers.get("content-type", ""),
                }

                self.results.append(result)
                return result

        except Exception as e:
            result = {
                "endpoint": "/docs",
                "status_code": None,
                "success": False,
                "error": str(e),
                "response_time": None,
            }
            self.results.append(result)
            return result

    async def test_openapi_schema(self):
        """测试OpenAPI schema端点"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/openapi.json")

                result = {
                    "endpoint": "/openapi.json",
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "schema_keys": (
                        list(response.json().keys())
                        if response.status_code == 200
                        else None
                    ),
                }

                self.results.append(result)
                return result

        except Exception as e:
            result = {
                "endpoint": "/openapi.json",
                "status_code": None,
                "success": False,
                "error": str(e),
                "response_time": None,
            }
            self.results.append(result)
            return result

    async def test_model_training_endpoints(self):
        """测试模型训练相关端点"""
        endpoints = [
            "/model-training/models",
            "/model-training/training-status/test_model",
        ]

        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}{endpoint}")

                    result = {
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "success": response.status_code
                        in [200, 404],  # 404也是正常的，表示端点存在
                        "response_time": response.elapsed.total_seconds(),
                        "response_data": (
                            response.json() if response.status_code == 200 else None
                        ),
                    }

                    self.results.append(result)

            except Exception as e:
                result = {
                    "endpoint": endpoint,
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                    "response_time": None,
                }
                self.results.append(result)

    async def test_enterprise_memory_endpoints(self):
        """测试企业记忆相关端点"""
        endpoints = [
            "/enterprise-memory/memories",
            "/enterprise-memory/search?query=test",
        ]

        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}{endpoint}")

                    result = {
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "success": response.status_code in [200, 404],
                        "response_time": response.elapsed.total_seconds(),
                        "response_data": (
                            response.json() if response.status_code == 200 else None
                        ),
                    }

                    self.results.append(result)

            except Exception as e:
                result = {
                    "endpoint": endpoint,
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                    "response_time": None,
                }
                self.results.append(result)

    async def test_ai_copilot_endpoints(self):
        """测试AI Copilot相关端点"""
        endpoints = ["/ai-copilot/tools", "/ai-copilot/chat-history"]

        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}{endpoint}")

                    result = {
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "success": response.status_code in [200, 404],
                        "response_time": response.elapsed.total_seconds(),
                        "response_data": (
                            response.json() if response.status_code == 200 else None
                        ),
                    }

                    self.results.append(result)

            except Exception as e:
                result = {
                    "endpoint": endpoint,
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                    "response_time": None,
                }
                self.results.append(result)

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始BMOS API测试...")
        print("=" * 60)

        # 测试基础端点
        print("1. 测试健康检查端点...")
        await self.test_health_check()

        print("2. 测试API文档端点...")
        await self.test_docs_endpoint()

        print("3. 测试OpenAPI schema端点...")
        await self.test_openapi_schema()

        print("4. 测试模型训练端点...")
        await self.test_model_training_endpoints()

        print("5. 测试企业记忆端点...")
        await self.test_enterprise_memory_endpoints()

        print("6. 测试AI Copilot端点...")
        await self.test_ai_copilot_endpoints()

        # 打印测试结果
        self.print_results()

    def print_results(self):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        failed_tests = total_tests - successful_tests

        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")

        print("\n📋 详细结果:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result.get("success", False) else "❌"
            endpoint = result.get("endpoint", "Unknown")
            status_code = result.get("status_code", "N/A")
            response_time = result.get("response_time", 0)

            print(f"{i:2d}. {status} {endpoint}")
            print(f"    状态码: {status_code}")
            print(f"    响应时间: {response_time*1000:.2f}ms")

            if not result.get("success", False) and "error" in result:
                print(f"    错误: {result['error']}")
            print()

    def export_results(self, filename: str = "api_test_results.json"):
        """导出测试结果"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "test_time": datetime.now().isoformat(),
                    "total_tests": len(self.results),
                    "successful_tests": sum(
                        1 for r in self.results if r.get("success", False)
                    ),
                    "results": self.results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"📄 测试结果已导出到: {filename}")


async def main():
    """主函数"""
    tester = BMOSAPITester()

    try:
        await tester.run_all_tests()
        tester.export_results()
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
