"""
BMOS系统 - 性能基准测试脚本
测试各个API端点的性能和响应时间
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Tuple
import httpx
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    status_codes: Dict[int, int]
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    throughput: float  # requests per second
    errors: List[str]

class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[BenchmarkResult] = []
    
    async def benchmark_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        data: Any = None,
        num_requests: int = 100,
        concurrency: int = 10
    ) -> BenchmarkResult:
        """对单个端点进行基准测试"""
        
        response_times = []
        status_codes = {}
        errors = []
        successful = 0
        failed = 0
        
        async def single_request(client: httpx.AsyncClient, request_id: int):
            nonlocal successful, failed
            
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers or {},
                        timeout=30.0
                    )
                elif method == "POST":
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        headers=headers or {},
                        json=data,
                        timeout=30.0
                    )
                elif method == "PUT":
                    response = await client.put(
                        f"{self.base_url}{endpoint}",
                        headers=headers or {},
                        json=data,
                        timeout=30.0
                    )
                elif method == "DELETE":
                    response = await client.delete(
                        f"{self.base_url}{endpoint}",
                        headers=headers or {},
                        timeout=30.0
                    )
                
                elapsed_time = time.time() - start_time
                response_times.append(elapsed_time)
                
                status_code = response.status_code
                status_codes[status_code] = status_codes.get(status_code, 0) + 1
                
                if 200 <= status_code < 300:
                    successful += 1
                else:
                    failed += 1
                    errors.append(f"Request {request_id}: Status {status_code}")
                    
            except Exception as e:
                failed += 1
                elapsed_time = time.time() - start_time
                response_times.append(elapsed_time)
                errors.append(f"Request {request_id}: {str(e)}")
        
        # 执行并发请求
        async with httpx.AsyncClient() as client:
            tasks = []
            for i in range(num_requests):
                task = single_request(client, i)
                tasks.append(task)
                
                # 控制并发数
                if len(tasks) >= concurrency:
                    await asyncio.gather(*tasks)
                    tasks = []
            
            if tasks:
                await asyncio.gather(*tasks)
        
        # 计算统计信息
        if response_times:
            sorted_times = sorted(response_times)
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = 0
        
        total_time = sum(response_times) if response_times else 0
        throughput = num_requests / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            endpoint=endpoint,
            method=method,
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            response_times=response_times,
            status_codes=status_codes,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            throughput=throughput,
            errors=errors
        )
        
        self.results.append(result)
        return result
    
    def print_results(self):
        """打印测试结果"""
        print("\n" + "="*80)
        print("性能基准测试结果")
        print("="*80)
        
        for result in self.results:
            print(f"\n端点: {result.method} {result.endpoint}")
            print(f"总请求数: {result.total_requests}")
            print(f"成功请求: {result.successful_requests}")
            print(f"失败请求: {result.failed_requests}")
            print(f"成功率: {result.successful_requests/result.total_requests*100:.2f}%")
            print(f"\n响应时间统计:")
            print(f"  平均: {result.avg_response_time*1000:.2f}ms")
            print(f"  中位数: {result.median_response_time*1000:.2f}ms")
            print(f"  P95: {result.p95_response_time*1000:.2f}ms")
            print(f"  P99: {result.p99_response_time*1000:.2f}ms")
            print(f"  最小: {result.min_response_time*1000:.2f}ms")
            print(f"  最大: {result.max_response_time*1000:.2f}ms")
            print(f"\n吞吐量: {result.throughput:.2f} req/s")
            print(f"\n状态码分布:")
            for code, count in result.status_codes.items():
                print(f"  {code}: {count}")
            
            if result.errors:
                print(f"\n错误 ({len(result.errors)}):")
                for error in result.errors[:5]:  # 只显示前5个错误
                    print(f"  {error}")
                if len(result.errors) > 5:
                    print(f"  ... 还有 {len(result.errors) - 5} 个错误")
    
    def export_results(self, filename: str = "benchmark_results.json"):
        """导出测试结果"""
        data = []
        for result in self.results:
            data.append({
                "endpoint": result.endpoint,
                "method": result.method,
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "success_rate": result.successful_requests / result.total_requests * 100,
                "avg_response_time_ms": round(result.avg_response_time * 1000, 2),
                "median_response_time_ms": round(result.median_response_time * 1000, 2),
                "p95_response_time_ms": round(result.p95_response_time * 1000, 2),
                "p99_response_time_ms": round(result.p99_response_time * 1000, 2),
                "min_response_time_ms": round(result.min_response_time * 1000, 2),
                "max_response_time_ms": round(result.max_response_time * 1000, 2),
                "throughput_rps": round(result.throughput, 2),
                "status_codes": result.status_codes,
                "error_count": len(result.errors),
                "timestamp": datetime.now().isoformat()
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n结果已导出到 {filename}")

async def run_benchmarks():
    """运行所有基准测试"""
    
    benchmark = PerformanceBenchmark()
    
    # 配置认证令牌（需要先登录获取）
    token = "your_token_here"  # TODO: 从登录接口获取
    headers = {"Authorization": f"Bearer {token}"}
    
    print("开始性能基准测试...\n")
    
    # 1. 测试健康检查端点
    print("1. 测试健康检查端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/health",
        method="GET",
        num_requests=100,
        concurrency=10
    )
    
    # 2. 测试数据导入端点
    print("2. 测试数据导入端点...")
    # await benchmark.benchmark_endpoint(
    #     endpoint="/data-import/upload",
    #     method="POST",
    #     headers=headers,
    #     num_requests=50,
    #     concurrency=5
    # )
    
    # 3. 测试模型训练端点
    print("3. 测试模型训练端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/model-training/models",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 4. 测试企业记忆端点
    print("4. 测试企业记忆端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/enterprise-memory/memories",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 5. 测试AI Copilot端点
    print("5. 测试AI Copilot端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/ai-copilot/tools",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 6. 测试数据质量端点
    print("6. 测试数据质量端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/data-quality/metrics",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 7. 测试调度器端点
    print("7. 测试调度器端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/scheduler/stats",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 8. 测试监控端点
    print("8. 测试监控端点...")
    await benchmark.benchmark_endpoint(
        endpoint="/monitoring/metrics",
        method="GET",
        headers=headers,
        num_requests=100,
        concurrency=10
    )
    
    # 打印结果
    benchmark.print_results()
    
    # 导出结果
    benchmark.export_results()

# 定义性能目标
PERFORMANCE_TARGETS = {
    "health_check": {
        "p95_response_time_ms": 10,
        "p99_response_time_ms": 50,
        "throughput_rps": 1000
    },
    "data_import": {
        "p95_response_time_ms": 2000,
        "p99_response_time_ms": 5000,
        "throughput_rps": 10
    },
    "model_training": {
        "p95_response_time_ms": 5000,
        "p99_response_time_ms": 10000,
        "throughput_rps": 5
    },
    "enterprise_memory": {
        "p95_response_time_ms": 100,
        "p99_response_time_ms": 200,
        "throughput_rps": 100
    },
    "ai_copilot": {
        "p95_response_time_ms": 5000,
        "p99_response_time_ms": 10000,
        "throughput_rps": 5
    },
    "data_quality": {
        "p95_response_time_ms": 1000,
        "p99_response_time_ms": 2000,
        "throughput_rps": 20
    },
    "scheduler": {
        "p95_response_time_ms": 100,
        "p99_response_time_ms": 200,
        "throughput_rps": 100
    },
    "monitoring": {
        "p95_response_time_ms": 50,
        "p99_response_time_ms": 100,
        "throughput_rps": 200
    }
}

def check_performance_targets(benchmark: PerformanceBenchmark):
    """检查性能是否达到目标"""
    print("\n" + "="*80)
    print("性能目标检查")
    print("="*80)
    
    for result in benchmark.results:
        endpoint_key = result.endpoint.split('/')[1] if '/' in result.endpoint else result.endpoint
        
        if endpoint_key in PERFORMANCE_TARGETS:
            targets = PERFORMANCE_TARGETS[endpoint_key]
            
            print(f"\n端点: {result.endpoint}")
            
            p95_target = targets["p95_response_time_ms"]
            p95_actual = result.p95_response_time * 1000
            p95_status = "✓" if p95_actual <= p95_target else "✗"
            print(f"  P95响应时间: {p95_status} 目标: {p95_target}ms, 实际: {p95_actual:.2f}ms")
            
            p99_target = targets["p99_response_time_ms"]
            p99_actual = result.p99_response_time * 1000
            p99_status = "✓" if p99_actual <= p99_target else "✗"
            print(f"  P99响应时间: {p99_status} 目标: {p99_target}ms, 实际: {p99_actual:.2f}ms")
            
            throughput_target = targets["throughput_rps"]
            throughput_actual = result.throughput
            throughput_status = "✓" if throughput_actual >= throughput_target else "✗"
            print(f"  吞吐量: {throughput_status} 目标: {throughput_target} req/s, 实际: {throughput_actual:.2f} req/s")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
    
    # 注意: 需要从实际的benchmark对象获取结果
    # check_performance_targets(benchmark)

