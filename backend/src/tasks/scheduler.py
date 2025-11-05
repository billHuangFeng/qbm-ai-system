"""
定时任务调度器
基于APScheduler实现定时任务调度
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from ..cache.redis_cache import RedisCache
from ..error_handling.unified import handle_errors, BusinessError
from ..logging_config import get_logger

logger = get_logger("scheduler")


class JobStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(Enum):
    """任务类型枚举"""

    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"


class ScheduledJob:
    """定时任务类"""

    def __init__(
        self,
        job_id: str,
        job_name: str,
        job_type: JobType,
        job_function: str,
        job_args: List[Any] = None,
        job_kwargs: Dict[str, Any] = None,
        trigger_config: Dict[str, Any] = None,
        max_instances: int = 1,
        misfire_grace_time: int = 60,
    ):
        self.job_id = job_id
        self.job_name = job_name
        self.job_type = job_type
        self.job_function = job_function
        self.job_args = job_args or []
        self.job_kwargs = job_kwargs or {}
        self.trigger_config = trigger_config or {}
        self.max_instances = max_instances
        self.misfire_grace_time = misfire_grace_time
        self.status = JobStatus.PENDING
        self.created_at = datetime.now()
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "job_type": self.job_type.value,
            "job_function": self.job_function,
            "job_args": self.job_args,
            "job_kwargs": self.job_kwargs,
            "trigger_config": self.trigger_config,
            "max_instances": self.max_instances,
            "misfire_grace_time": self.misfire_grace_time,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledJob":
        """从字典创建任务"""
        job = cls(
            job_id=data["job_id"],
            job_name=data["job_name"],
            job_type=JobType(data["job_type"]),
            job_function=data["job_function"],
            job_args=data["job_args"],
            job_kwargs=data["job_kwargs"],
            trigger_config=data["trigger_config"],
            max_instances=data["max_instances"],
            misfire_grace_time=data["misfire_grace_time"],
        )
        job.status = JobStatus(data["status"])
        job.created_at = datetime.fromisoformat(data["created_at"])
        job.last_run = (
            datetime.fromisoformat(data["last_run"]) if data["last_run"] else None
        )
        job.next_run = (
            datetime.fromisoformat(data["next_run"]) if data["next_run"] else None
        )
        job.run_count = data["run_count"]
        job.success_count = data["success_count"]
        job.failure_count = data["failure_count"]
        job.last_error = data["last_error"]
        return job


class SchedulerService:
    """调度器服务"""

    def __init__(self, redis_cache: RedisCache):
        self.redis_cache = redis_cache
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.job_functions: Dict[str, Callable] = {}
        self.jobs: Dict[str, ScheduledJob] = {}
        self.is_running = False

    @handle_errors
    async def initialize(self):
        """初始化调度器"""
        # 配置作业存储
        jobstores = {
            "default": RedisJobStore(host="localhost", port=6379, db=1, password=None)
        }

        # 配置执行器
        executors = {"default": AsyncIOExecutor()}

        # 创建调度器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores, executors=executors, timezone="Asia/Shanghai"
        )

        # 启动调度器
        self.scheduler.start()
        self.is_running = True

        logger.info("调度器初始化完成")

    @handle_errors
    async def shutdown(self):
        """关闭调度器"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("调度器已关闭")

    @handle_errors
    async def register_function(self, function_name: str, function: Callable):
        """注册任务函数"""
        self.job_functions[function_name] = function
        logger.info(f"注册任务函数: {function_name}")

    @handle_errors
    async def add_cron_job(
        self,
        job_name: str,
        function_name: str,
        cron_config: Dict[str, Any],
        job_args: List[Any] = None,
        job_kwargs: Dict[str, Any] = None,
        max_instances: int = 1,
        misfire_grace_time: int = 60,
    ) -> str:
        """添加Cron任务"""
        job_id = str(uuid.uuid4())

        # 创建任务对象
        job = ScheduledJob(
            job_id=job_id,
            job_name=job_name,
            job_type=JobType.CRON,
            job_function=function_name,
            job_args=job_args or [],
            job_kwargs=job_kwargs or {},
            trigger_config=cron_config,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
        )

        # 创建触发器
        trigger = CronTrigger(**cron_config)

        # 添加任务到调度器
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            args=[job_id],
            id=job_id,
            name=job_name,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            replace_existing=True,
        )

        # 存储任务信息
        self.jobs[job_id] = job
        await self.redis_cache.set(f"scheduled_job:{job_id}", job.to_dict(), ttl=86400)

        logger.info(f"添加Cron任务: {job_name} ({job_id})")
        return job_id

    @handle_errors
    async def add_interval_job(
        self,
        job_name: str,
        function_name: str,
        interval_config: Dict[str, Any],
        job_args: List[Any] = None,
        job_kwargs: Dict[str, Any] = None,
        max_instances: int = 1,
        misfire_grace_time: int = 60,
    ) -> str:
        """添加间隔任务"""
        job_id = str(uuid.uuid4())

        # 创建任务对象
        job = ScheduledJob(
            job_id=job_id,
            job_name=job_name,
            job_type=JobType.INTERVAL,
            job_function=function_name,
            job_args=job_args or [],
            job_kwargs=job_kwargs or {},
            trigger_config=interval_config,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
        )

        # 创建触发器
        trigger = IntervalTrigger(**interval_config)

        # 添加任务到调度器
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            args=[job_id],
            id=job_id,
            name=job_name,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            replace_existing=True,
        )

        # 存储任务信息
        self.jobs[job_id] = job
        await self.redis_cache.set(f"scheduled_job:{job_id}", job.to_dict(), ttl=86400)

        logger.info(f"添加间隔任务: {job_name} ({job_id})")
        return job_id

    @handle_errors
    async def add_date_job(
        self,
        job_name: str,
        function_name: str,
        run_date: datetime,
        job_args: List[Any] = None,
        job_kwargs: Dict[str, Any] = None,
        max_instances: int = 1,
        misfire_grace_time: int = 60,
    ) -> str:
        """添加一次性任务"""
        job_id = str(uuid.uuid4())

        # 创建任务对象
        job = ScheduledJob(
            job_id=job_id,
            job_name=job_name,
            job_type=JobType.DATE,
            job_function=function_name,
            job_args=job_args or [],
            job_kwargs=job_kwargs or {},
            trigger_config={"run_date": run_date.isoformat()},
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
        )

        # 创建触发器
        trigger = DateTrigger(run_date=run_date)

        # 添加任务到调度器
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            args=[job_id],
            id=job_id,
            name=job_name,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            replace_existing=True,
        )

        # 存储任务信息
        self.jobs[job_id] = job
        await self.redis_cache.set(f"scheduled_job:{job_id}", job.to_dict(), ttl=86400)

        logger.info(f"添加一次性任务: {job_name} ({job_id})")
        return job_id

    @handle_errors
    async def remove_job(self, job_id: str) -> bool:
        """移除任务"""
        try:
            # 从调度器移除
            self.scheduler.remove_job(job_id)

            # 从内存移除
            if job_id in self.jobs:
                del self.jobs[job_id]

            # 从Redis移除
            await self.redis_cache.delete(f"scheduled_job:{job_id}")

            logger.info(f"移除任务: {job_id}")
            return True

        except Exception as e:
            logger.error(f"移除任务失败: {e}")
            return False

    @handle_errors
    async def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)

            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.CANCELLED
                await self.redis_cache.set(
                    f"scheduled_job:{job_id}", self.jobs[job_id].to_dict(), ttl=86400
                )

            logger.info(f"暂停任务: {job_id}")
            return True

        except Exception as e:
            logger.error(f"暂停任务失败: {e}")
            return False

    @handle_errors
    async def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)

            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.PENDING
                await self.redis_cache.set(
                    f"scheduled_job:{job_id}", self.jobs[job_id].to_dict(), ttl=86400
                )

            logger.info(f"恢复任务: {job_id}")
            return True

        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            return False

    @handle_errors
    async def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """获取任务信息"""
        if job_id in self.jobs:
            return self.jobs[job_id]

        # 从Redis获取
        job_data = await self.redis_cache.get(f"scheduled_job:{job_id}")
        if job_data:
            return ScheduledJob.from_dict(job_data)

        return None

    @handle_errors
    async def get_all_jobs(self) -> List[ScheduledJob]:
        """获取所有任务"""
        jobs = []

        # 从内存获取
        for job in self.jobs.values():
            jobs.append(job)

        # 从Redis获取
        job_keys = await self.redis_cache.keys("scheduled_job:*")
        for key in job_keys:
            job_id = key.replace("scheduled_job:", "")
            if job_id not in self.jobs:
                job_data = await self.redis_cache.get(key)
                if job_data:
                    jobs.append(ScheduledJob.from_dict(job_data))

        return jobs

    @handle_errors
    async def _execute_job(self, job_id: str):
        """执行任务"""
        try:
            # 获取任务信息
            job = await self.get_job(job_id)
            if not job:
                logger.error(f"任务不存在: {job_id}")
                return

            # 更新任务状态
            job.status = JobStatus.RUNNING
            job.last_run = datetime.now()
            job.run_count += 1

            # 获取任务函数
            function = self.job_functions.get(job.job_function)
            if not function:
                raise BusinessError(
                    code="JOB_FUNCTION_NOT_FOUND",
                    message=f"任务函数不存在: {job.job_function}",
                )

            # 执行任务
            logger.info(f"开始执行任务: {job.job_name} ({job_id})")
            result = await function(*job.job_args, **job.job_kwargs)

            # 更新任务状态
            job.status = JobStatus.COMPLETED
            job.success_count += 1
            job.last_error = None

            logger.info(f"任务执行成功: {job.job_name} ({job_id})")

        except Exception as e:
            # 更新任务状态
            if job:
                job.status = JobStatus.FAILED
                job.failure_count += 1
                job.last_error = str(e)

            logger.error(f"任务执行失败: {job_id} - {e}")

        finally:
            # 保存任务状态
            if job:
                self.jobs[job_id] = job
                await self.redis_cache.set(
                    f"scheduled_job:{job_id}", job.to_dict(), ttl=86400
                )

    @handle_errors
    async def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计"""
        jobs = await self.get_all_jobs()

        total_jobs = len(jobs)
        running_jobs = len([j for j in jobs if j.status == JobStatus.RUNNING])
        completed_jobs = len([j for j in jobs if j.status == JobStatus.COMPLETED])
        failed_jobs = len([j for j in jobs if j.status == JobStatus.FAILED])

        total_runs = sum(j.run_count for j in jobs)
        total_successes = sum(j.success_count for j in jobs)
        total_failures = sum(j.failure_count for j in jobs)

        return {
            "total_jobs": total_jobs,
            "running_jobs": running_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_runs": total_runs,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "success_rate": total_successes / total_runs if total_runs > 0 else 0,
            "is_running": self.is_running,
        }


# 定时任务装饰器
def scheduled_job(
    job_type: JobType,
    trigger_config: Dict[str, Any],
    job_name: Optional[str] = None,
    max_instances: int = 1,
    misfire_grace_time: int = 60,
):
    """
    定时任务装饰器

    Args:
        job_type: 任务类型
        trigger_config: 触发器配置
        job_name: 任务名称
        max_instances: 最大实例数
        misfire_grace_time: 错过执行宽限时间
    """

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        # 标记为定时任务
        wrapper._is_scheduled_job = True
        wrapper._job_type = job_type
        wrapper._trigger_config = trigger_config
        wrapper._job_name = job_name or func.__name__
        wrapper._max_instances = max_instances
        wrapper._misfire_grace_time = misfire_grace_time

        return wrapper

    return decorator


# Cron任务装饰器
def cron_job(
    year: Optional[Union[int, str]] = None,
    month: Optional[Union[int, str]] = None,
    day: Optional[Union[int, str]] = None,
    week: Optional[Union[int, str]] = None,
    day_of_week: Optional[Union[int, str]] = None,
    hour: Optional[Union[int, str]] = None,
    minute: Optional[Union[int, str]] = None,
    second: Optional[Union[int, str]] = None,
    job_name: Optional[str] = None,
    max_instances: int = 1,
    misfire_grace_time: int = 60,
):
    """
    Cron任务装饰器

    Args:
        year: 年
        month: 月
        day: 日
        week: 周
        day_of_week: 星期几
        hour: 小时
        minute: 分钟
        second: 秒
        job_name: 任务名称
        max_instances: 最大实例数
        misfire_grace_time: 错过执行宽限时间
    """
    trigger_config = {
        "year": year,
        "month": month,
        "day": day,
        "week": week,
        "day_of_week": day_of_week,
        "hour": hour,
        "minute": minute,
        "second": second,
    }

    # 移除None值
    trigger_config = {k: v for k, v in trigger_config.items() if v is not None}

    return scheduled_job(
        job_type=JobType.CRON,
        trigger_config=trigger_config,
        job_name=job_name,
        max_instances=max_instances,
        misfire_grace_time=misfire_grace_time,
    )


# 间隔任务装饰器
def interval_job(
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    job_name: Optional[str] = None,
    max_instances: int = 1,
    misfire_grace_time: int = 60,
):
    """
    间隔任务装饰器

    Args:
        weeks: 周数
        days: 天数
        hours: 小时数
        minutes: 分钟数
        seconds: 秒数
        job_name: 任务名称
        max_instances: 最大实例数
        misfire_grace_time: 错过执行宽限时间
    """
    trigger_config = {
        "weeks": weeks,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }

    return scheduled_job(
        job_type=JobType.INTERVAL,
        trigger_config=trigger_config,
        job_name=job_name,
        max_instances=max_instances,
        misfire_grace_time=misfire_grace_time,
    )
