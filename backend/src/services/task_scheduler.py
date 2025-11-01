"""
定时任务和调度系统
提供任务调度、执行监控、失败重试等功能
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import traceback
from croniter import croniter
import schedule
import threading
import time

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 正在执行
    COMPLETED = "completed"    # 执行完成
    FAILED = "failed"         # 执行失败
    CANCELLED = "cancelled"    # 已取消
    RETRYING = "retrying"      # 重试中

class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class ScheduleType(Enum):
    """调度类型枚举"""
    ONCE = "once"              # 一次性执行
    INTERVAL = "interval"      # 间隔执行
    CRON = "cron"              # Cron表达式
    DAILY = "daily"            # 每日执行
    WEEKLY = "weekly"          # 每周执行
    MONTHLY = "monthly"        # 每月执行

@dataclass
class Task:
    """任务模型"""
    id: str
    name: str
    description: str
    function_name: str
    parameters: Dict[str, Any]
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    priority: TaskPriority
    max_retries: int
    retry_delay: int  # 重试延迟（秒）
    timeout: int      # 超时时间（秒）
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    error_message: Optional[str] = None

@dataclass
class TaskExecution:
    """任务执行记录"""
    id: str
    task_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class TaskSchedule:
    """任务调度配置"""
    task_id: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service
        
        # 任务注册表
        self.task_functions = {}
        
        # 任务队列
        self.task_queue = asyncio.Queue()
        
        # 执行中的任务
        self.running_tasks = {}
        
        # 调度器状态
        self.is_running = False
        self.scheduler_thread = None
        
        # 任务统计
        self.task_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "running_tasks": 0
        }
    
    def register_task_function(self, name: str, func: Callable):
        """注册任务函数"""
        self.task_functions[name] = func
        logger.info(f"Registered task function: {name}")
    
    async def start_scheduler(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        # 启动任务执行器
        asyncio.create_task(self._task_executor())
        
        # 启动调度器线程
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Task scheduler started")
    
    async def stop_scheduler(self):
        """停止调度器"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        
        # 等待所有任务完成
        while self.running_tasks:
            await asyncio.sleep(1)
        
        # 停止调度器线程
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Task scheduler stopped")
    
    async def create_task(
        self,
        name: str,
        description: str,
        function_name: str,
        parameters: Dict[str, Any],
        schedule_type: ScheduleType,
        schedule_config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        timeout: int = 300
    ) -> str:
        """创建任务"""
        try:
            # 检查任务函数是否存在
            if function_name not in self.task_functions:
                raise ValueError(f"Task function '{function_name}' not registered")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 计算下次执行时间
            next_run = self._calculate_next_run(schedule_type, schedule_config)
            
            # 创建任务
            task = Task(
                id=task_id,
                name=name,
                description=description,
                function_name=function_name,
                parameters=parameters,
                schedule_type=schedule_type,
                schedule_config=schedule_config,
                priority=priority,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                next_run=next_run
            )
            
            # 保存任务到数据库
            await self._save_task(task)
            
            # 创建调度配置
            schedule_config_obj = TaskSchedule(
                task_id=task_id,
                schedule_type=schedule_type,
                schedule_config=schedule_config,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await self._save_schedule(schedule_config_obj)
            
            logger.info(f"Created task: {task_id} - {name}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    async def update_task(
        self,
        task_id: str,
        **kwargs
    ) -> bool:
        """更新任务"""
        try:
            # 获取任务
            task = await self._get_task_by_id(task_id)
            if not task:
                return False
            
            # 更新任务属性
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            
            # 重新计算下次执行时间
            if 'schedule_type' in kwargs or 'schedule_config' in kwargs:
                task.next_run = self._calculate_next_run(
                    task.schedule_type,
                    task.schedule_config
                )
            
            # 保存更新
            await self._update_task(task)
            
            logger.info(f"Updated task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task: {str(e)}")
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            # 检查任务是否正在运行
            if task_id in self.running_tasks:
                logger.warning(f"Cannot delete running task: {task_id}")
                return False
            
            # 删除任务
            success = await self._delete_task(task_id)
            
            if success:
                logger.info(f"Deleted task: {task_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete task: {str(e)}")
            return False
    
    async def execute_task(self, task_id: str) -> bool:
        """立即执行任务"""
        try:
            # 获取任务
            task = await self._get_task_by_id(task_id)
            if not task:
                return False
            
            # 检查任务函数是否存在
            if task.function_name not in self.task_functions:
                logger.error(f"Task function '{task.function_name}' not found")
                return False
            
            # 创建执行记录
            execution_id = str(uuid.uuid4())
            execution = TaskExecution(
                id=execution_id,
                task_id=task_id,
                started_at=datetime.now(),
                status=TaskStatus.RUNNING
            )
            
            # 保存执行记录
            await self._save_execution(execution)
            
            # 添加到运行队列
            await self.task_queue.put((task, execution))
            
            logger.info(f"Queued task for execution: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute task: {str(e)}")
            return False
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            # 检查任务是否正在运行
            if task_id in self.running_tasks:
                # 取消正在运行的任务
                task_coroutine = self.running_tasks[task_id]
                task_coroutine.cancel()
                del self.running_tasks[task_id]
            
            # 更新任务状态
            task = await self._get_task_by_id(task_id)
            if task:
                task.status = TaskStatus.CANCELLED
                task.updated_at = datetime.now()
                await self._update_task(task)
            
            logger.info(f"Cancelled task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task: {str(e)}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            task = await self._get_task_by_id(task_id)
            if not task:
                return None
            
            return {
                "task_id": task.id,
                "name": task.name,
                "status": task.status.value,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "error_message": task.error_message,
                "last_result": task.last_result
            }
            
        except Exception as e:
            logger.error(f"Failed to get task status: {str(e)}")
            return None
    
    async def get_task_list(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取任务列表"""
        try:
            tasks = await self._get_tasks_from_storage(status, limit, offset)
            
            return [
                {
                    "task_id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "function_name": task.function_name,
                    "schedule_type": task.schedule_type.value,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "next_run": task.next_run.isoformat() if task.next_run else None,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]
            
        except Exception as e:
            logger.error(f"Failed to get task list: {str(e)}")
            return []
    
    async def get_execution_history(
        self,
        task_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取任务执行历史"""
        try:
            executions = await self._get_executions_from_storage(task_id, limit, offset)
            
            return [
                {
                    "execution_id": execution.id,
                    "task_id": execution.task_id,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "status": execution.status.value,
                    "execution_time": execution.execution_time,
                    "result": execution.result,
                    "error_message": execution.error_message
                }
                for execution in executions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {str(e)}")
            return []
    
    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        try:
            # 更新统计信息
            await self._update_task_stats()
            
            return {
                "is_running": self.is_running,
                "total_tasks": self.task_stats["total_tasks"],
                "completed_tasks": self.task_stats["completed_tasks"],
                "failed_tasks": self.task_stats["failed_tasks"],
                "running_tasks": len(self.running_tasks),
                "queue_size": self.task_queue.qsize(),
                "registered_functions": len(self.task_functions)
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler stats: {str(e)}")
            return {}
    
    # ==================== 私有方法 ====================
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self.is_running:
            try:
                # 检查需要执行的任务
                asyncio.run(self._check_scheduled_tasks())
                
                # 等待1秒
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")
                time.sleep(5)
    
    async def _check_scheduled_tasks(self):
        """检查需要执行的任务"""
        try:
            # 获取所有活跃的任务
            active_tasks = await self._get_active_tasks()
            
            current_time = datetime.now()
            
            for task in active_tasks:
                # 检查是否到了执行时间
                if task.next_run and task.next_run <= current_time:
                    # 检查任务是否正在运行
                    if task.id not in self.running_tasks:
                        # 执行任务
                        await self.execute_task(task.id)
                        
                        # 更新下次执行时间
                        task.next_run = self._calculate_next_run(
                            task.schedule_type,
                            task.schedule_config
                        )
                        task.updated_at = datetime.now()
                        
                        await self._update_task(task)
                        
        except Exception as e:
            logger.error(f"Failed to check scheduled tasks: {str(e)}")
    
    async def _task_executor(self):
        """任务执行器"""
        while self.is_running:
            try:
                # 从队列获取任务
                task, execution = await self.task_queue.get()
                
                # 执行任务
                await self._execute_task_async(task, execution)
                
            except Exception as e:
                logger.error(f"Task executor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _execute_task_async(self, task: Task, execution: TaskExecution):
        """异步执行任务"""
        try:
            # 添加到运行任务列表
            self.running_tasks[task.id] = asyncio.current_task()
            
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.now()
            task.updated_at = datetime.now()
            await self._update_task(task)
            
            # 获取任务函数
            task_func = self.task_functions[task.function_name]
            
            # 执行任务
            start_time = time.time()
            
            try:
                # 设置超时
                result = await asyncio.wait_for(
                    self._call_task_function(task_func, task.parameters),
                    timeout=task.timeout
                )
                
                execution_time = time.time() - start_time
                
                # 任务执行成功
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.now()
                execution.result = {"success": True, "data": result}
                execution.execution_time = execution_time
                
                task.status = TaskStatus.COMPLETED
                task.last_result = execution.result
                task.retry_count = 0
                task.error_message = None
                
                # 更新统计
                self.task_stats["completed_tasks"] += 1
                
            except asyncio.TimeoutError:
                # 任务超时
                execution_time = time.time() - start_time
                
                execution.status = TaskStatus.FAILED
                execution.completed_at = datetime.now()
                execution.error_message = f"Task timeout after {task.timeout} seconds"
                execution.execution_time = execution_time
                
                await self._handle_task_failure(task, execution)
                
            except Exception as e:
                # 任务执行失败
                execution_time = time.time() - start_time
                
                execution.status = TaskStatus.FAILED
                execution.completed_at = datetime.now()
                execution.error_message = str(e)
                execution.execution_time = execution_time
                
                await self._handle_task_failure(task, execution)
            
            # 更新执行记录
            await self._update_execution(execution)
            
            # 更新任务
            task.updated_at = datetime.now()
            await self._update_task(task)
            
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            
            # 更新执行记录
            execution.status = TaskStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error_message = str(e)
            await self._update_execution(execution)
            
        finally:
            # 从运行任务列表移除
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def _call_task_function(self, func: Callable, parameters: Dict[str, Any]):
        """调用任务函数"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(**parameters)
            else:
                # 在线程池中运行同步函数
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: func(**parameters))
                
        except Exception as e:
            logger.error(f"Task function call failed: {str(e)}")
            raise
    
    async def _handle_task_failure(self, task: Task, execution: TaskExecution):
        """处理任务失败"""
        try:
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                # 可以重试
                task.status = TaskStatus.RETRYING
                task.error_message = execution.error_message
                
                # 安排重试
                retry_time = datetime.now() + timedelta(seconds=task.retry_delay)
                task.next_run = retry_time
                
                logger.info(f"Task {task.id} will retry at {retry_time}")
                
            else:
                # 重试次数用完
                task.status = TaskStatus.FAILED
                task.error_message = execution.error_message
                
                logger.error(f"Task {task.id} failed after {task.max_retries} retries")
            
            # 更新统计
            self.task_stats["failed_tasks"] += 1
            
        except Exception as e:
            logger.error(f"Failed to handle task failure: {str(e)}")
    
    def _calculate_next_run(self, schedule_type: ScheduleType, schedule_config: Dict[str, Any]) -> Optional[datetime]:
        """计算下次执行时间"""
        try:
            current_time = datetime.now()
            
            if schedule_type == ScheduleType.ONCE:
                # 一次性执行
                return None
            
            elif schedule_type == ScheduleType.INTERVAL:
                # 间隔执行
                interval = schedule_config.get("interval", 60)  # 默认60秒
                return current_time + timedelta(seconds=interval)
            
            elif schedule_type == ScheduleType.CRON:
                # Cron表达式
                cron_expr = schedule_config.get("cron", "0 0 * * *")
                cron = croniter(cron_expr, current_time)
                return cron.get_next(datetime)
            
            elif schedule_type == ScheduleType.DAILY:
                # 每日执行
                time_str = schedule_config.get("time", "00:00")
                hour, minute = map(int, time_str.split(":"))
                
                next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= current_time:
                    next_run += timedelta(days=1)
                
                return next_run
            
            elif schedule_type == ScheduleType.WEEKLY:
                # 每周执行
                weekday = schedule_config.get("weekday", 0)  # 0=Monday
                time_str = schedule_config.get("time", "00:00")
                hour, minute = map(int, time_str.split(":"))
                
                days_ahead = weekday - current_time.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                
                next_run = current_time + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                return next_run
            
            elif schedule_type == ScheduleType.MONTHLY:
                # 每月执行
                day = schedule_config.get("day", 1)
                time_str = schedule_config.get("time", "00:00")
                hour, minute = map(int, time_str.split(":"))
                
                next_run = current_time.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= current_time:
                    # 下个月
                    if current_time.month == 12:
                        next_run = next_run.replace(year=current_time.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=current_time.month + 1)
                
                return next_run
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate next run: {str(e)}")
            return None
    
    # ==================== 数据库操作 ====================
    
    async def _save_task(self, task: Task) -> bool:
        """保存任务到数据库"""
        try:
            # 这里可以实现保存到数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to save task: {str(e)}")
            return False
    
    async def _get_task_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        try:
            # 这里可以从数据库获取任务
            # 暂时返回None
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task by ID: {str(e)}")
            return None
    
    async def _update_task(self, task: Task) -> bool:
        """更新任务"""
        try:
            # 这里可以实现更新数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task: {str(e)}")
            return False
    
    async def _delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            # 这里可以实现删除数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task: {str(e)}")
            return False
    
    async def _get_tasks_from_storage(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """从存储中获取任务列表"""
        try:
            # 这里可以从数据库获取任务列表
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logger.error(f"Failed to get tasks from storage: {str(e)}")
            return []
    
    async def _get_active_tasks(self) -> List[Task]:
        """获取活跃的任务"""
        try:
            # 这里可以从数据库获取活跃任务
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logger.error(f"Failed to get active tasks: {str(e)}")
            return []
    
    async def _save_schedule(self, schedule: TaskSchedule) -> bool:
        """保存调度配置"""
        try:
            # 这里可以实现保存到数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to save schedule: {str(e)}")
            return False
    
    async def _save_execution(self, execution: TaskExecution) -> bool:
        """保存执行记录"""
        try:
            # 这里可以实现保存到数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to save execution: {str(e)}")
            return False
    
    async def _update_execution(self, execution: TaskExecution) -> bool:
        """更新执行记录"""
        try:
            # 这里可以实现更新数据库的逻辑
            # 暂时返回True
            return True
            
        except Exception as e:
            logger.error(f"Failed to update execution: {str(e)}")
            return False
    
    async def _get_executions_from_storage(
        self,
        task_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[TaskExecution]:
        """从存储中获取执行记录"""
        try:
            # 这里可以从数据库获取执行记录
            # 暂时返回空列表
            return []
            
        except Exception as e:
            logger.error(f"Failed to get executions from storage: {str(e)}")
            return []
    
    async def _update_task_stats(self):
        """更新任务统计信息"""
        try:
            # 这里可以从数据库更新统计信息
            # 暂时跳过
            pass
            
        except Exception as e:
            logger.error(f"Failed to update task stats: {str(e)}")

# ==================== 预定义任务函数 ====================

async def data_quality_check_task(dataset_id: str, dataset_name: str):
    """数据质量检查任务"""
    try:
        logger.info(f"Running data quality check for dataset: {dataset_name}")
        
        # 这里可以调用数据质量检查服务
        # result = await data_quality_service.check_data_quality(dataset_id, dataset_name)
        
        return {"success": True, "message": f"Data quality check completed for {dataset_name}"}
        
    except Exception as e:
        logger.error(f"Data quality check task failed: {str(e)}")
        raise

async def model_training_task(model_type: str, training_data: str):
    """模型训练任务"""
    try:
        logger.info(f"Running model training for type: {model_type}")
        
        # 这里可以调用模型训练服务
        # result = await model_training_service.train_model(model_type, training_data)
        
        return {"success": True, "message": f"Model training completed for {model_type}"}
        
    except Exception as e:
        logger.error(f"Model training task failed: {str(e)}")
        raise

async def data_import_task(file_path: str, target_table: str):
    """数据导入任务"""
    try:
        logger.info(f"Running data import from {file_path} to {target_table}")
        
        # 这里可以调用数据导入服务
        # result = await data_import_service.import_data(file_path, target_table)
        
        return {"success": True, "message": f"Data import completed from {file_path}"}
        
    except Exception as e:
        logger.error(f"Data import task failed: {str(e)}")
        raise

async def report_generation_task(report_type: str, parameters: Dict[str, Any]):
    """报告生成任务"""
    try:
        logger.info(f"Running report generation for type: {report_type}")
        
        # 这里可以调用报告生成服务
        # result = await report_service.generate_report(report_type, parameters)
        
        return {"success": True, "message": f"Report generation completed for {report_type}"}
        
    except Exception as e:
        logger.error(f"Report generation task failed: {str(e)}")
        raise

async def cleanup_task(cleanup_type: str, retention_days: int):
    """清理任务"""
    try:
        logger.info(f"Running cleanup for type: {cleanup_type}")
        
        # 这里可以调用清理服务
        # result = await cleanup_service.cleanup_data(cleanup_type, retention_days)
        
        return {"success": True, "message": f"Cleanup completed for {cleanup_type}"}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise

