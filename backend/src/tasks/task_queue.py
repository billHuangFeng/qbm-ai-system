"""
异步任务队列系统
基于Redis实现分布式任务队列
"""

import asyncio
import json
import uuid
import time
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import traceback

from ..cache.redis_cache import RedisCache
from ..error_handling.unified import handle_errors, BusinessError
from ..logging_config import get_logger

logger = get_logger("task_queue")

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Task:
    """任务类"""
    
    def __init__(
        self,
        task_id: str,
        task_name: str,
        task_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        timeout: int = 300
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.task_data = task_data
        self.priority = priority
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0
        self.error_message: Optional[str] = None
        self.result: Optional[Any] = None
        self.progress = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "task_data": self.task_data,
            "priority": self.priority.value,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "result": self.result,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务"""
        task = cls(
            task_id=data["task_id"],
            task_name=data["task_name"],
            task_data=data["task_data"],
            priority=TaskPriority(data["priority"]),
            max_retries=data["max_retries"],
            retry_delay=data["retry_delay"],
            timeout=data["timeout"]
        )
        task.status = TaskStatus(data["status"])
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.started_at = datetime.fromisoformat(data["started_at"]) if data["started_at"] else None
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None
        task.retry_count = data["retry_count"]
        task.error_message = data["error_message"]
        task.result = data["result"]
        task.progress = data["progress"]
        return task

class TaskQueue:
    """任务队列"""
    
    def __init__(self, redis_cache: RedisCache, queue_name: str = "default"):
        self.redis_cache = redis_cache
        self.queue_name = queue_name
        self.task_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.workers: List[asyncio.Task] = []
        
    @handle_errors
    async def register_handler(self, task_name: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_name] = handler
        logger.info(f"注册任务处理器: {task_name}")
    
    @handle_errors
    async def enqueue(
        self,
        task_name: str,
        task_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        timeout: int = 300
    ) -> str:
        """添加任务到队列"""
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_name=task_name,
            task_data=task_data,
            priority=priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout
        )
        
        # 存储任务信息
        await self.redis_cache.set(
            f"task:{task_id}",
            task.to_dict(),
            ttl=86400  # 24小时
        )
        
        # 添加到队列
        queue_key = f"queue:{self.queue_name}"
        await self.redis_cache.lpush(
            queue_key,
            task_id
        )
        
        logger.info(f"任务已添加到队列: {task_id} ({task_name})")
        return task_id
    
    @handle_errors
    async def dequeue(self) -> Optional[Task]:
        """从队列获取任务"""
        queue_key = f"queue:{self.queue_name}"
        
        # 使用阻塞式弹出，超时1秒
        try:
            task_id = await self.redis_cache.rpop(queue_key)
            if not task_id:
                return None
            
            # 获取任务信息
            task_data = await self.redis_cache.get(f"task:{task_id}")
            if not task_data:
                logger.warning(f"任务信息不存在: {task_id}")
                return None
            
            task = Task.from_dict(task_data)
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # 更新任务状态
            await self.redis_cache.set(f"task:{task_id}", task.to_dict(), ttl=86400)
            
            return task
            
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None
    
    @handle_errors
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            return None
        
        return Task.from_dict(task_data)
    
    @handle_errors
    async def update_task(self, task: Task):
        """更新任务信息"""
        await self.redis_cache.set(f"task:{task.task_id}", task.to_dict(), ttl=86400)
    
    @handle_errors
    async def complete_task(self, task_id: str, result: Any = None):
        """完成任务"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            logger.warning(f"任务不存在: {task_id}")
            return
        
        task = Task.from_dict(task_data)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        task.progress = 100.0
        
        await self.redis_cache.set(f"task:{task_id}", task.to_dict(), ttl=86400)
        logger.info(f"任务完成: {task_id}")
    
    @handle_errors
    async def fail_task(self, task_id: str, error_message: str):
        """标记任务失败"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            logger.warning(f"任务不存在: {task_id}")
            return
        
        task = Task.from_dict(task_data)
        task.error_message = error_message
        
        # 检查是否需要重试
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            
            # 延迟重试
            await asyncio.sleep(task.retry_delay)
            
            # 重新加入队列
            queue_key = f"queue:{self.queue_name}"
            await self.redis_cache.lpush(queue_key, task_id)
            
            logger.info(f"任务重试: {task_id} (第{task.retry_count}次)")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            logger.error(f"任务失败: {task_id} - {error_message}")
        
        await self.redis_cache.set(f"task:{task_id}", task.to_dict(), ttl=86400)
    
    @handle_errors
    async def cancel_task(self, task_id: str):
        """取消任务"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            logger.warning(f"任务不存在: {task_id}")
            return
        
        task = Task.from_dict(task_data)
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        await self.redis_cache.set(f"task:{task_id}", task.to_dict(), ttl=86400)
        logger.info(f"任务已取消: {task_id}")
    
    @handle_errors
    async def get_queue_size(self) -> int:
        """获取队列大小"""
        queue_key = f"queue:{self.queue_name}"
        return await self.redis_cache.llen(queue_key)
    
    @handle_errors
    async def get_task_stats(self) -> Dict[str, int]:
        """获取任务统计"""
        # 这里可以实现更复杂的统计逻辑
        return {
            "queue_size": await self.get_queue_size(),
            "total_tasks": len(self.task_handlers)
        }

class TaskWorker:
    """任务工作者"""
    
    def __init__(self, task_queue: TaskQueue, worker_id: str):
        self.task_queue = task_queue
        self.worker_id = worker_id
        self.is_running = False
        self.current_task: Optional[Task] = None
    
    @handle_errors
    async def start(self):
        """启动工作者"""
        self.is_running = True
        logger.info(f"任务工作者启动: {self.worker_id}")
        
        while self.is_running:
            try:
                # 获取任务
                task = await self.task_queue.dequeue()
                if not task:
                    await asyncio.sleep(1)  # 没有任务时等待
                    continue
                
                self.current_task = task
                logger.info(f"工作者 {self.worker_id} 开始处理任务: {task.task_id}")
                
                # 执行任务
                await self._execute_task(task)
                
            except Exception as e:
                logger.error(f"工作者 {self.worker_id} 处理任务时发生错误: {e}")
                if self.current_task:
                    await self.task_queue.fail_task(self.current_task.task_id, str(e))
            
            finally:
                self.current_task = None
    
    @handle_errors
    async def stop(self):
        """停止工作者"""
        self.is_running = False
        logger.info(f"任务工作者停止: {self.worker_id}")
    
    @handle_errors
    async def _execute_task(self, task: Task):
        """执行任务"""
        try:
            # 获取任务处理器
            handler = self.task_queue.task_handlers.get(task.task_name)
            if not handler:
                raise BusinessError(
                    code="TASK_HANDLER_NOT_FOUND",
                    message=f"任务处理器不存在: {task.task_name}"
                )
            
            # 执行任务
            result = await handler(task.task_data)
            
            # 标记任务完成
            await self.task_queue.complete_task(task.task_id, result)
            
        except Exception as e:
            # 标记任务失败
            await self.task_queue.fail_task(task.task_id, str(e))
            raise

class TaskManager:
    """任务管理器"""
    
    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        self.queues: Dict[str, TaskQueue] = {}
        self.workers: List[TaskWorker] = []
        self.is_running = False
    
    @handle_errors
    async def create_queue(self, queue_name: str) -> TaskQueue:
        """创建任务队列"""
        queue = TaskQueue(self.redis_cache, queue_name)
        self.queues[queue_name] = queue
        logger.info(f"创建任务队列: {queue_name}")
        return queue
    
    @handle_errors
    async def get_queue(self, queue_name: str) -> Optional[TaskQueue]:
        """获取任务队列"""
        return self.queues.get(queue_name)
    
    @handle_errors
    async def register_handler(
        self, 
        queue_name: str, 
        task_name: str, 
        handler: Callable
    ):
        """注册任务处理器"""
        queue = self.queues.get(queue_name)
        if not queue:
            queue = await self.create_queue(queue_name)
        
        await queue.register_handler(task_name, handler)
    
    @handle_errors
    async def enqueue_task(
        self,
        queue_name: str,
        task_name: str,
        task_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        timeout: int = 300
    ) -> str:
        """添加任务到队列"""
        queue = self.queues.get(queue_name)
        if not queue:
            queue = await self.create_queue(queue_name)
        
        return await queue.enqueue(
            task_name=task_name,
            task_data=task_data,
            priority=priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout
        )
    
    @handle_errors
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            return None
        
        return Task.from_dict(task_data)
    
    @handle_errors
    async def start_workers(self, queue_name: str, worker_count: int = 1):
        """启动工作者"""
        queue = self.queues.get(queue_name)
        if not queue:
            logger.error(f"队列不存在: {queue_name}")
            return
        
        for i in range(worker_count):
            worker_id = f"{queue_name}_worker_{i}"
            worker = TaskWorker(queue, worker_id)
            self.workers.append(worker)
            
            # 启动工作者
            asyncio.create_task(worker.start())
        
        logger.info(f"启动 {worker_count} 个工作者处理队列: {queue_name}")
    
    @handle_errors
    async def stop_workers(self):
        """停止所有工作者"""
        for worker in self.workers:
            await worker.stop()
        
        self.workers.clear()
        logger.info("所有工作者已停止")
    
    @handle_errors
    async def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        tasks = []
        
        # 从Redis获取所有任务键
        task_keys = await self.redis_cache.keys("task:*")
        for key in task_keys:
            task_data = await self.redis_cache.get(key)
            if task_data:
                tasks.append(Task.from_dict(task_data))
        
        return tasks
    
    @handle_errors
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task_data = await self.redis_cache.get(f"task:{task_id}")
        if not task_data:
            return False
        
        task = Task.from_dict(task_data)
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        await self.redis_cache.set(f"task:{task_id}", task.to_dict(), ttl=86400)
        logger.info(f"任务已取消: {task_id}")
        return True
    
    @handle_errors
    async def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计"""
        tasks = await self.get_all_tasks()
        
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
        running_tasks = len([t for t in tasks if t.status == TaskStatus.RUNNING])
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in tasks if t.status == TaskStatus.FAILED])
        cancelled_tasks = len([t for t in tasks if t.status == TaskStatus.CANCELLED])
        retrying_tasks = len([t for t in tasks if t.status == TaskStatus.RETRYING])
        
        total_runs = sum(t.retry_count + 1 for t in tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED])
        total_successes = completed_tasks
        total_failures = failed_tasks
        
        success_rate = total_successes / total_runs if total_runs > 0 else 0.0
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "cancelled_tasks": cancelled_tasks,
            "retrying_tasks": retrying_tasks,
            "total_runs": total_runs,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": success_rate
        }

    @handle_errors
    async def get_stats(self) -> Dict[str, Any]:
        """获取任务管理器统计"""
        stats = {
            "queues": {},
            "workers": len(self.workers),
            "is_running": self.is_running
        }
        
        for queue_name, queue in self.queues.items():
            stats["queues"][queue_name] = await queue.get_task_stats()
        
        # 添加全局任务统计
        global_stats = await self.get_task_stats()
        stats.update(global_stats)
        
        return stats

# 任务装饰器
def task_handler(queue_name: str = "default"):
    """
    任务处理器装饰器
    
    Args:
        queue_name: 队列名称
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # 标记为任务处理器
        wrapper._is_task_handler = True
        wrapper._queue_name = queue_name
        wrapper._task_name = func.__name__
        
        return wrapper
    return decorator

# 异步任务装饰器
def async_task(
    queue_name: str = "default",
    priority: TaskPriority = TaskPriority.NORMAL,
    max_retries: int = 3,
    retry_delay: int = 60,
    timeout: int = 300
):
    """
    异步任务装饰器
    
    Args:
        queue_name: 队列名称
        priority: 任务优先级
        max_retries: 最大重试次数
        retry_delay: 重试延迟
        timeout: 超时时间
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # 创建任务数据
            task_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            # 添加到任务队列
            task_manager = TaskManager(RedisCache("redis://localhost:6379/0"))
            task_id = await task_manager.enqueue_task(
                queue_name=queue_name,
                task_name=func.__name__,
                task_data=task_data,
                priority=priority,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout
            )
            
            return task_id
        
        return wrapper
    return decorator
