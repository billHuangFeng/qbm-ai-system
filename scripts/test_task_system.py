#!/usr/bin/env python3
"""
BMOS系统 - 异步任务处理系统测试脚本
测试任务队列、调度器和任务处理功能
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# 将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.src.tasks.task_queue import TaskManager, TaskPriority, TaskStatus
from backend.src.tasks.scheduler import SchedulerService, JobType
from backend.src.tasks.handlers import BMOSTaskHandlers, setup_default_scheduled_jobs
from backend.src.cache.redis_cache import RedisCache
from backend.src.config.unified import settings
from backend.src.logging_config import get_logger

logger = get_logger("task_system_test")

class TaskSystemTester:
    """任务系统测试器"""
    
    def __init__(self):
        self.redis_cache = None
        self.task_manager = None
        self.scheduler_service = None
        self.task_handlers = None
    
    async def setup(self):
        """设置测试环境"""
        logger.info("设置任务系统测试环境...")
        
        # 初始化Redis缓存
        self.redis_cache = RedisCache(settings.redis.redis_url, settings.redis.redis_password)
        await self.redis_cache.connect()
        
        if not await self.redis_cache.health_check():
            raise Exception("Redis连接失败")
        
        # 初始化任务管理器
        self.task_manager = TaskManager(self.redis_cache)
        
        # 初始化调度器服务
        self.scheduler_service = SchedulerService(self.redis_cache)
        await self.scheduler_service.initialize()
        
        # 初始化任务处理器
        self.task_handlers = BMOSTaskHandlers(self.task_manager, self.scheduler_service)
        
        logger.info("测试环境设置完成")
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("清理测试环境...")
        
        if self.scheduler_service:
            await self.scheduler_service.shutdown()
        
        if self.redis_cache:
            await self.redis_cache.disconnect()
        
        logger.info("测试环境清理完成")
    
    async def test_task_queue_basic(self):
        """测试任务队列基本功能"""
        logger.info("=== 测试任务队列基本功能 ===")
        
        # 测试添加任务
        task_id = await self.task_manager.enqueue_task(
            queue_name="test_queue",
            task_name="data_processing",
            task_data={
                "data_source": "test_data.csv",
                "processing_type": "standard"
            },
            priority=TaskPriority.HIGH,
            max_retries=2,
            timeout=300
        )
        
        logger.info(f"添加任务成功: {task_id}")
        
        # 测试获取任务
        task = await self.task_manager.get_task(task_id)
        if task:
            logger.info(f"获取任务成功: {task.task_name}, 状态: {task.status.value}")
        else:
            logger.error("获取任务失败")
        
        # 测试任务统计
        stats = await self.task_manager.get_task_stats()
        logger.info(f"任务统计: {stats}")
        
        return task_id
    
    async def test_task_execution(self):
        """测试任务执行"""
        logger.info("=== 测试任务执行 ===")
        
        # 启动工作者
        await self.task_manager.start_workers("test_queue", worker_count=1)
        
        # 添加多个任务
        task_ids = []
        for i in range(3):
            task_id = await self.task_manager.enqueue_task(
                queue_name="test_queue",
                task_name="data_processing",
                task_data={
                    "data_source": f"test_data_{i}.csv",
                    "processing_type": "standard",
                    "task_index": i
                },
                priority=TaskPriority.NORMAL
            )
            task_ids.append(task_id)
            logger.info(f"添加任务 {i+1}: {task_id}")
        
        # 等待任务执行
        await asyncio.sleep(5)
        
        # 检查任务状态
        for task_id in task_ids:
            task = await self.task_manager.get_task(task_id)
            if task:
                logger.info(f"任务 {task_id} 状态: {task.status.value}")
                if task.result:
                    logger.info(f"任务结果: {task.result}")
        
        # 停止工作者
        await self.task_manager.stop_workers()
    
    async def test_scheduled_jobs(self):
        """测试定时任务"""
        logger.info("=== 测试定时任务 ===")
        
        # 添加间隔任务（每5秒执行一次）
        job_id = await self.scheduler_service.add_interval_job(
            job_name="测试间隔任务",
            function_name="hourly_data_sync",
            interval_config={"seconds": 5},
            max_instances=1,
            misfire_grace_time=10
        )
        
        logger.info(f"添加间隔任务: {job_id}")
        
        # 添加一次性任务（10秒后执行）
        run_date = datetime.now() + timedelta(seconds=10)
        one_time_job_id = await self.scheduler_service.add_date_job(
            job_name="测试一次性任务",
            function_name="system_cleanup",
            run_date=run_date,
            job_kwargs={"cleanup_type": "test"}
        )
        
        logger.info(f"添加一次性任务: {one_time_job_id}")
        
        # 等待任务执行
        logger.info("等待定时任务执行...")
        await asyncio.sleep(20)
        
        # 检查任务状态
        job = await self.scheduler_service.get_job(job_id)
        if job:
            logger.info(f"间隔任务状态: {job.status.value}, 执行次数: {job.run_count}")
        
        one_time_job = await self.scheduler_service.get_job(one_time_job_id)
        if one_time_job:
            logger.info(f"一次性任务状态: {one_time_job.status.value}")
        
        # 移除任务
        await self.scheduler_service.remove_job(job_id)
        await self.scheduler_service.remove_job(one_time_job_id)
        logger.info("定时任务测试完成")
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("=== 测试错误处理 ===")
        
        # 添加一个会失败的任务
        task_id = await self.task_manager.enqueue_task(
            queue_name="test_queue",
            task_name="nonexistent_handler",
            task_data={"test": "error"},
            max_retries=2,
            retry_delay=2
        )
        
        logger.info(f"添加会失败的任务: {task_id}")
        
        # 启动工作者
        await self.task_manager.start_workers("test_queue", worker_count=1)
        
        # 等待任务执行和重试
        await asyncio.sleep(10)
        
        # 检查任务状态
        task = await self.task_manager.get_task(task_id)
        if task:
            logger.info(f"失败任务状态: {task.status.value}")
            logger.info(f"重试次数: {task.retry_count}")
            logger.info(f"错误信息: {task.error_message}")
        
        # 停止工作者
        await self.task_manager.stop_workers()
    
    async def test_performance(self):
        """测试性能"""
        logger.info("=== 测试性能 ===")
        
        # 启动多个工作者
        await self.task_manager.start_workers("test_queue", worker_count=3)
        
        # 添加大量任务
        start_time = datetime.now()
        task_count = 50
        
        for i in range(task_count):
            await self.task_manager.enqueue_task(
                queue_name="test_queue",
                task_name="data_processing",
                task_data={
                    "data_source": f"perf_test_{i}.csv",
                    "processing_type": "fast"
                },
                priority=TaskPriority.NORMAL
            )
        
        logger.info(f"添加了 {task_count} 个任务")
        
        # 等待所有任务完成
        completed_count = 0
        while completed_count < task_count:
            await asyncio.sleep(1)
            stats = await self.task_manager.get_task_stats()
            completed_count = stats["completed_tasks"]
            logger.info(f"已完成任务: {completed_count}/{task_count}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"性能测试完成:")
        logger.info(f"  总任务数: {task_count}")
        logger.info(f"  总耗时: {duration:.2f} 秒")
        logger.info(f"  平均耗时: {duration/task_count:.3f} 秒/任务")
        logger.info(f"  吞吐量: {task_count/duration:.2f} 任务/秒")
        
        # 停止工作者
        await self.task_manager.stop_workers()
    
    async def run_all_tests(self):
        """运行所有测试"""
        try:
            await self.setup()
            
            # 基本功能测试
            await self.test_task_queue_basic()
            
            # 任务执行测试
            await self.test_task_execution()
            
            # 定时任务测试
            await self.test_scheduled_jobs()
            
            # 错误处理测试
            await self.test_error_handling()
            
            # 性能测试
            await self.test_performance()
            
            logger.info("=== 所有测试完成 ===")
            
        except Exception as e:
            logger.error(f"测试失败: {e}", exc_info=True)
        finally:
            await self.cleanup()

async def main():
    """主函数"""
    logger.info("开始BMOS异步任务处理系统测试")
    
    tester = TaskSystemTester()
    await tester.run_all_tests()
    
    logger.info("测试完成")

if __name__ == "__main__":
    asyncio.run(main())

