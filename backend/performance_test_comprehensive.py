"""
BMOS系统性能测试脚本
测试系统在不同负载下的表现
"""

import asyncio
import time
import statistics
import json
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class BMOSPerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    async def test_single_request(self, endpoint, method="GET", data=None, timeout=30):
        """测试单个请求的性能"""
        async with httpx.AsyncClient(timeout=timeout) as client:
            start_time = time.time()
            try:
                if method == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = await client.post(f"{self.base_url}{endpoint}", json=data)
                elif method == "PUT":
                    response = await client.put(f"{self.base_url}{endpoint}", json=data)
                elif method == "DELETE":
                    response = await client.delete(f"{self.base_url}{endpoint}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_size": len(response.content) if response.content else 0
                }
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                return {
                    "success": False,
                    "response_time": response_time,
                    "error": str(e),
                    "status_code": None,
                    "response_size": 0
                }
    
    async def test_concurrent_requests(self, endpoint, method="GET", data=None, 
                                     concurrent_users=10, requests_per_user=10):
        """测试并发请求性能"""
        print(f"测试并发性能: {concurrent_users}个用户, 每个用户{requests_per_user}个请求")
        
        async def user_simulation():
            user_results = []
            for _ in range(requests_per_user):
                result = await self.test_single_request(endpoint, method, data)
                user_results.append(result)
                # 添加小延迟模拟真实用户行为
                await asyncio.sleep(0.1)
            return user_results
        
        start_time = time.time()
        
        # 创建并发任务
        tasks = [user_simulation() for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计结果
        all_requests = []
        for user_results in all_results:
            all_requests.extend(user_results)
        
        successful_requests = [r for r in all_requests if r["success"]]
        failed_requests = [r for r in all_requests if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        total_requests = len(all_requests)
        success_rate = len(successful_requests) / total_requests * 100 if total_requests > 0 else 0
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        
        return {
            "endpoint": endpoint,
            "method": method,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": total_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": success_rate,
            "total_time": total_time,
            "requests_per_second": requests_per_second,
            "avg_response_time": avg_response_time,
            "median_response_time": median_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "errors": [r["error"] for r in failed_requests] if failed_requests else []
        }
    
    async def test_data_import_performance(self):
        """测试数据导入性能"""
        print("\n=== 数据导入性能测试 ===")
        
        # 创建测试数据
        test_data_sizes = [100, 500, 1000, 2000]
        results = []
        
        for size in test_data_sizes:
            print(f"测试数据大小: {size}行")
            
            # 生成测试数据
            test_df = pd.DataFrame({
                'id': range(1, size + 1),
                'feature1': np.random.randn(size),
                'feature2': np.random.randn(size),
                'feature3': np.random.randn(size),
                'target': np.random.randint(0, 2, size)
            })
            
            # 转换为CSV字符串
            csv_data = test_df.to_csv(index=False)
            
            # 测试上传性能
            start_time = time.time()
            try:
                async with httpx.AsyncClient() as client:
                    files = {'file': ('test_data.csv', csv_data, 'text/csv')}
                    response = await client.post(f"{self.base_url}/api/v1/data-import/upload", files=files)
                    upload_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        results.append({
                            "data_size": size,
                            "upload_time": upload_time,
                            "throughput": size / upload_time,  # 行/秒
                            "success": True
                        })
                    else:
                        results.append({
                            "data_size": size,
                            "upload_time": upload_time,
                            "throughput": 0,
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })
            except Exception as e:
                upload_time = time.time() - start_time
                results.append({
                    "data_size": size,
                    "upload_time": upload_time,
                    "throughput": 0,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def test_model_training_performance(self):
        """测试模型训练性能"""
        print("\n=== 模型训练性能测试 ===")
        
        # 测试不同数据大小的训练性能
        test_sizes = [100, 500, 1000, 2000]
        algorithms = ["random_forest_classifier", "xgboost_classifier", "lightgbm_classifier"]
        results = []
        
        for size in test_sizes:
            for algorithm in algorithms:
                print(f"测试 {algorithm} 在 {size} 样本上的性能")
                
                # 准备训练数据
                training_data = {
                    "samples": size,
                    "features": 5,
                    "target_column": "target",
                    "algorithm": algorithm,
                    "test_size": 0.2
                }
                
                start_time = time.time()
                try:
                    async with httpx.AsyncClient(timeout=60) as client:
                        # 生成数据
                        response1 = await client.post(
                            f"{self.base_url}/api/v1/model-training/generate-data",
                            json=training_data
                        )
                        
                        if response1.status_code == 200:
                            data_info = response1.json()
                            
                            # 准备数据
                            prepare_data = {
                                "data": data_info["data"],
                                "target_column": "target"
                            }
                            response2 = await client.post(
                                f"{self.base_url}/api/v1/model-training/prepare-data",
                                json=prepare_data
                            )
                            
                            if response2.status_code == 200:
                                prepared_data = response2.json()
                                
                                # 训练模型
                                train_data = {
                                    "algorithm": algorithm,
                                    "X": prepared_data["X"],
                                    "y": prepared_data["y"],
                                    "params": {}
                                }
                                response3 = await client.post(
                                    f"{self.base_url}/api/v1/model-training/train",
                                    json=train_data
                                )
                                
                                training_time = time.time() - start_time
                                
                                if response3.status_code == 200:
                                    model_info = response3.json()
                                    results.append({
                                        "algorithm": algorithm,
                                        "data_size": size,
                                        "training_time": training_time,
                                        "accuracy": model_info.get("accuracy", 0),
                                        "success": True
                                    })
                                else:
                                    results.append({
                                        "algorithm": algorithm,
                                        "data_size": size,
                                        "training_time": time.time() - start_time,
                                        "accuracy": 0,
                                        "success": False,
                                        "error": f"Training failed: HTTP {response3.status_code}"
                                    })
                            else:
                                results.append({
                                    "algorithm": algorithm,
                                    "data_size": size,
                                    "training_time": time.time() - start_time,
                                    "accuracy": 0,
                                    "success": False,
                                    "error": f"Data preparation failed: HTTP {response2.status_code}"
                                })
                        else:
                            results.append({
                                "algorithm": algorithm,
                                "data_size": size,
                                "training_time": time.time() - start_time,
                                "accuracy": 0,
                                "success": False,
                                "error": f"Data generation failed: HTTP {response1.status_code}"
                            })
                except Exception as e:
                    results.append({
                        "algorithm": algorithm,
                        "data_size": size,
                        "training_time": time.time() - start_time,
                        "accuracy": 0,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    async def test_enterprise_memory_performance(self):
        """测试企业记忆性能"""
        print("\n=== 企业记忆性能测试 ===")
        
        # 测试不同数据大小的记忆提取性能
        test_sizes = [100, 500, 1000, 2000]
        results = []
        
        for size in test_sizes:
            print(f"测试企业记忆在 {size} 样本上的性能")
            
            # 生成测试数据
            test_df = pd.DataFrame({
                'feature1': np.random.randn(size),
                'feature2': np.random.randn(size),
                'feature3': np.random.randn(size),
                'target': np.random.randint(0, 2, size)
            })
            
            # 测试模式提取性能
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    extract_data = {
                        "data": test_df.to_dict('records'),
                        "target_column": "target"
                    }
                    response = await client.post(
                        f"{self.base_url}/api/v1/enterprise-memory/extract-patterns",
                        json=extract_data
                    )
                    
                    extraction_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        patterns_info = response.json()
                        results.append({
                            "data_size": size,
                            "extraction_time": extraction_time,
                            "patterns_count": len(patterns_info.get("patterns", [])),
                            "success": True
                        })
                    else:
                        results.append({
                            "data_size": size,
                            "extraction_time": extraction_time,
                            "patterns_count": 0,
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })
            except Exception as e:
                results.append({
                    "data_size": size,
                    "extraction_time": time.time() - start_time,
                    "patterns_count": 0,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def run_comprehensive_performance_test(self):
        """运行综合性能测试"""
        print("BMOS系统综合性能测试")
        print("=" * 50)
        
        # 1. 基础API性能测试
        print("\n1. 基础API性能测试")
        basic_endpoints = [
            ("/health", "GET"),
            ("/api/v1/status", "GET"),
            ("/docs", "GET")
        ]
        
        for endpoint, method in basic_endpoints:
            print(f"测试 {method} {endpoint}")
            result = await self.test_concurrent_requests(
                endpoint, method, 
                concurrent_users=5, 
                requests_per_user=10
            )
            self.results[f"basic_{endpoint.replace('/', '_')}"] = result
        
        # 2. 数据导入性能测试
        print("\n2. 数据导入性能测试")
        data_import_results = await self.test_data_import_performance()
        self.results["data_import"] = data_import_results
        
        # 3. 模型训练性能测试
        print("\n3. 模型训练性能测试")
        model_training_results = await self.test_model_training_performance()
        self.results["model_training"] = model_training_results
        
        # 4. 企业记忆性能测试
        print("\n4. 企业记忆性能测试")
        memory_results = await self.test_enterprise_memory_performance()
        self.results["enterprise_memory"] = memory_results
        
        # 5. 高并发压力测试
        print("\n5. 高并发压力测试")
        stress_test_configs = [
            {"users": 10, "requests": 5},
            {"users": 20, "requests": 5},
            {"users": 50, "requests": 3},
            {"users": 100, "requests": 2}
        ]
        
        for config in stress_test_configs:
            print(f"压力测试: {config['users']}用户, 每用户{config['requests']}请求")
            result = await self.test_concurrent_requests(
                "/health", "GET",
                concurrent_users=config["users"],
                requests_per_user=config["requests"]
            )
            self.results[f"stress_test_{config['users']}users"] = result
        
        return self.results
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        print("\n" + "=" * 50)
        print("BMOS系统性能测试报告")
        print("=" * 50)
        
        # 基础API性能
        print("\n1. 基础API性能:")
        for key, result in self.results.items():
            if key.startswith("basic_"):
                print(f"  {result['endpoint']}:")
                print(f"    成功率: {result['success_rate']:.1f}%")
                print(f"    平均响应时间: {result['avg_response_time']:.1f}ms")
                print(f"    95%响应时间: {result['p95_response_time']:.1f}ms")
                print(f"    吞吐量: {result['requests_per_second']:.1f} req/s")
        
        # 数据导入性能
        if "data_import" in self.results:
            print("\n2. 数据导入性能:")
            for result in self.results["data_import"]:
                if result["success"]:
                    print(f"  {result['data_size']}行数据:")
                    print(f"    上传时间: {result['upload_time']:.2f}s")
                    print(f"    吞吐量: {result['throughput']:.1f} 行/s")
                else:
                    print(f"  {result['data_size']}行数据: 失败 - {result['error']}")
        
        # 模型训练性能
        if "model_training" in self.results:
            print("\n3. 模型训练性能:")
            for result in self.results["model_training"]:
                if result["success"]:
                    print(f"  {result['algorithm']} ({result['data_size']}样本):")
                    print(f"    训练时间: {result['training_time']:.2f}s")
                    print(f"    准确率: {result['accuracy']:.3f}")
                else:
                    print(f"  {result['algorithm']} ({result['data_size']}样本): 失败 - {result['error']}")
        
        # 企业记忆性能
        if "enterprise_memory" in self.results:
            print("\n4. 企业记忆性能:")
            for result in self.results["enterprise_memory"]:
                if result["success"]:
                    print(f"  {result['data_size']}样本:")
                    print(f"    提取时间: {result['extraction_time']:.2f}s")
                    print(f"    模式数量: {result['patterns_count']}")
                else:
                    print(f"  {result['data_size']}样本: 失败 - {result['error']}")
        
        # 压力测试结果
        print("\n5. 压力测试结果:")
        for key, result in self.results.items():
            if key.startswith("stress_test_"):
                print(f"  {result['concurrent_users']}并发用户:")
                print(f"    成功率: {result['success_rate']:.1f}%")
                print(f"    平均响应时间: {result['avg_response_time']:.1f}ms")
                print(f"    吞吐量: {result['requests_per_second']:.1f} req/s")
                if result['errors']:
                    print(f"    错误: {len(result['errors'])}个")
        
        # 保存详细结果到文件
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n详细结果已保存到: performance_test_results.json")

async def main():
    """主测试函数"""
    tester = BMOSPerformanceTester()
    
    try:
        # 运行综合性能测试
        await tester.run_comprehensive_performance_test()
        
        # 生成性能报告
        tester.generate_performance_report()
        
        print("\n性能测试完成!")
        
    except Exception as e:
        print(f"性能测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

