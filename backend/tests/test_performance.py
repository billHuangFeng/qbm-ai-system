"""
BMOS系统 - 性能测试套件
测试API端点的性能和并发处理能力
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import statistics
from unittest.mock import patch, Mock

from backend.src.api.endpoints import optimization, monitoring, tasks
from backend.src.security.auth import User, Permission

class TestAPIPerformance:
    """API性能测试"""
    
    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        return User(
            user_id="perf_test_user",
            username="perftest",
            email="perf@example.com",
            tenant_id="perf_tenant",
            role="manager",
            permissions=[Permission.WRITE_OPTIMIZATION, Permission.READ_OPTIMIZATION, Permission.READ_DATA]
        )
    
    @pytest.mark.asyncio
    async def test_optimization_endpoint_performance(self, mock_user):
        """测试优化建议端点性能"""
        optimization_data = {
            "recommendation_type": "performance",
            "title": "性能测试建议",
            "description": "这是一个性能测试",
            "priority": "medium"
        }
        
        # 测试单次请求性能
        start_time = time.time()
        
        with patch('backend.src.api.endpoints.optimization.get_db') as mock_db:
            mock_db.return_value.execute.return_value.fetchone.return_value = [123]
            
            with patch('backend.src.api.endpoints.optimization.require_permission') as mock_auth:
                mock_auth.return_value = mock_user
                
                await optimization.create_optimization(
                    optimization_data=optimization_data,
                    current_user=mock_user,
                    db=mock_db.return_value
                )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 性能断言：单次请求应该在100ms内完成
        assert response_time < 0.1, f"响应时间过长: {response_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoint_performance(self, mock_user):
        """测试监控端点性能"""
        # 测试健康检查性能
        start_time = time.time()
        
        with patch('backend.src.api.endpoints.monitoring.get_db') as mock_db:
            mock_db.return_value.execute.return_value.fetchone.return_value = [5]
            
            with patch('backend.src.api.endpoints.monitoring.require_permission') as mock_auth:
                mock_auth.return_value = mock_user
                
                with patch('backend.src.api.endpoints.monitoring.psutil') as mock_psutil:
                    mock_psutil.cpu_percent.return_value = 35.0
                    mock_psutil.virtual_memory.return_value = Mock(percent=60.0, available=8*1024**3)
                    mock_psutil.disk_usage.return_value = Mock(percent=45.0, free=120*1024**3)
                    
                    await monitoring.get_system_health(
                        current_user=mock_user,
                        db=mock_db.return_value
                    )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 性能断言：健康检查应该在50ms内完成
        assert response_time < 0.05, f"健康检查响应时间过长: {response_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, mock_user):
        """测试并发请求性能"""
        optimization_data = {
            "recommendation_type": "performance",
            "title": "并发测试建议",
            "description": "并发性能测试",
            "priority": "medium"
        }
        
        async def single_request():
            """单个请求"""
            with patch('backend.src.api.endpoints.optimization.get_db') as mock_db:
                mock_db.return_value.execute.return_value.fetchone.return_value = [123]
                
                with patch('backend.src.api.endpoints.optimization.require_permission') as mock_auth:
                    mock_auth.return_value = mock_user
                    
                    await optimization.create_optimization(
                        optimization_data=optimization_data,
                        current_user=mock_user,
                        db=mock_db.return_value
                    )
        
        # 并发执行10个请求
        concurrent_requests = 10
        start_time = time.time()
        
        await asyncio.gather(*[single_request() for _ in range(concurrent_requests)])
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_request = total_time / concurrent_requests
        
        # 性能断言：平均每个请求应该在200ms内完成
        assert avg_time_per_request < 0.2, f"并发请求平均响应时间过长: {avg_time_per_request:.3f}s"
        
        # 性能断言：总时间应该在2秒内完成
        assert total_time < 2.0, f"并发请求总时间过长: {total_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_memory_usage_performance(self, mock_user):
        """测试内存使用性能"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行多个请求
        optimization_data = {
            "recommendation_type": "performance",
            "title": "内存测试建议",
            "description": "内存使用测试",
            "priority": "medium"
        }
        
        for i in range(100):  # 执行100个请求
            with patch('backend.src.api.endpoints.optimization.get_db') as mock_db:
                mock_db.return_value.execute.return_value.fetchone.return_value = [i]
                
                with patch('backend.src.api.endpoints.optimization.require_permission') as mock_auth:
                    mock_auth.return_value = mock_user
                    
                    await optimization.create_optimization(
                        optimization_data=optimization_data,
                        current_user=mock_user,
                        db=mock_db.return_value
                    )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 性能断言：内存增长应该在100MB以内
        assert memory_increase < 100, f"内存使用增长过多: {memory_increase:.2f}MB"

class TestLoadTesting:
    """负载测试"""
    
    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        return User(
            user_id="load_test_user",
            username="loadtest",
            email="load@example.com",
            tenant_id="load_tenant",
            role="admin",
            permissions=[Permission.READ_DATA]
        )
    
    @pytest.mark.asyncio
    async def test_high_load_monitoring(self, mock_user):
        """测试高负载下的监控性能"""
        async def monitoring_request():
            """监控请求"""
            with patch('backend.src.api.endpoints.monitoring.get_db') as mock_db:
                mock_db.return_value.execute.return_value.fetchall.return_value = []
                
                with patch('backend.src.api.endpoints.monitoring.require_permission') as mock_auth:
                    mock_auth.return_value = mock_user
                    
                    await monitoring.get_monitoring_data(
                        current_user=mock_user,
                        db=mock_db.return_value,
                        hours=24
                    )
        
        # 高负载测试：50个并发请求
        concurrent_requests = 50
        start_time = time.time()
        
        tasks = [monitoring_request() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能断言：50个并发请求应该在5秒内完成
        assert total_time < 5.0, f"高负载测试时间过长: {total_time:.3f}s"
        
        # 计算QPS（每秒查询数）
        qps = concurrent_requests / total_time
        assert qps > 10, f"QPS过低: {qps:.2f}"
    
    @pytest.mark.asyncio
    async def test_stress_testing(self, mock_user):
        """压力测试"""
        optimization_data = {
            "recommendation_type": "stress",
            "title": "压力测试建议",
            "description": "压力测试",
            "priority": "high"
        }
        
        async def stress_request():
            """压力测试请求"""
            with patch('backend.src.api.endpoints.optimization.get_db') as mock_db:
                mock_db.return_value.execute.return_value.fetchone.return_value = [123]
                
                with patch('backend.src.api.endpoints.optimization.require_permission') as mock_auth:
                    mock_auth.return_value = mock_user
                    
                    await optimization.create_optimization(
                        optimization_data=optimization_data,
                        current_user=mock_user,
                        db=mock_db.return_value
                    )
        
        # 压力测试：100个并发请求
        concurrent_requests = 100
        start_time = time.time()
        
        tasks = [stress_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计成功率
        success_count = sum(1 for result in results if not isinstance(result, Exception))
        success_rate = success_count / concurrent_requests
        
        # 性能断言：成功率应该在95%以上
        assert success_rate >= 0.95, f"成功率过低: {success_rate:.2%}"
        
        # 性能断言：总时间应该在10秒内完成
        assert total_time < 10.0, f"压力测试时间过长: {total_time:.3f}s"

class TestScalability:
    """可扩展性测试"""
    
    @pytest.mark.asyncio
    async def test_response_time_scalability(self):
        """测试响应时间可扩展性"""
        mock_user = User(
            user_id="scale_test_user",
            username="scaletest",
            email="scale@example.com",
            tenant_id="scale_tenant",
            role="manager",
            permissions=[Permission.READ_DATA]
        )
        
        # 测试不同并发级别的响应时间
        concurrency_levels = [1, 5, 10, 20, 50]
        response_times = []
        
        for concurrency in concurrency_levels:
            async def single_request():
                with patch('backend.src.api.endpoints.monitoring.get_db') as mock_db:
                    mock_db.return_value.execute.return_value.fetchall.return_value = []
                    
                    with patch('backend.src.api.endpoints.monitoring.require_permission') as mock_auth:
                        mock_auth.return_value = mock_user
                        
                        start_time = time.time()
                        await monitoring.get_monitoring_data(
                            current_user=mock_user,
                            db=mock_db.return_value,
                            hours=24
                        )
                        end_time = time.time()
                        return end_time - start_time
            
            # 执行并发请求
            start_time = time.time()
            tasks = [single_request() for _ in range(concurrency)]
            individual_times = await asyncio.gather(*tasks)
            end_time = time.time()
            
            avg_response_time = statistics.mean(individual_times)
            response_times.append(avg_response_time)
        
        # 性能断言：响应时间增长应该是线性的，不应该指数增长
        for i in range(1, len(response_times)):
            time_ratio = response_times[i] / response_times[0]
            concurrency_ratio = concurrency_levels[i] / concurrency_levels[0]
            
            # 响应时间增长不应该超过并发增长的2倍
            assert time_ratio < concurrency_ratio * 2, f"响应时间增长过快: {time_ratio:.2f} vs {concurrency_ratio:.2f}"

# 测试配置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 运行性能测试的命令
# pytest backend/tests/test_performance.py -v --tb=short


