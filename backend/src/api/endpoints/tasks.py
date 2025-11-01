"""
任务管理相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ...security.database import SecureDatabaseService
from ...auth import get_current_user, require_permission, Permission, User
from ...error_handling.unified import BusinessError, handle_errors
from ...logging_config import get_logger
from ...tasks.task_queue import TaskManager, Task, TaskPriority, TaskStatus
from ...tasks.scheduler import SchedulerService, ScheduledJob, JobType
from ...cache.redis_cache import RedisCache
from ...config.unified import settings

router = APIRouter()
logger = get_logger("tasks_api")

# 依赖注入
async def get_redis_cache():
    """获取Redis缓存实例"""
    cache = RedisCache(settings.redis.redis_url, settings.redis.redis_password)
    await cache.connect()
    return cache

async def get_task_manager(cache: RedisCache = Depends(get_redis_cache)):
    """获取任务管理器实例"""
    return TaskManager(cache)

async def get_scheduler_service(cache: RedisCache = Depends(get_redis_cache)):
    """获取调度器服务实例"""
    return SchedulerService(cache)

# 请求模型
class TaskCreateRequest(BaseModel):
    task_name: str = Field(..., description="任务名称")
    task_data: Dict[str, Any] = Field(..., description="任务数据")
    queue_name: str = Field("default", description="队列名称")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    max_retries: int = Field(3, description="最大重试次数")
    retry_delay: int = Field(60, description="重试延迟（秒）")
    timeout: int = Field(300, description="超时时间（秒）")

class ScheduledJobCreateRequest(BaseModel):
    job_name: str = Field(..., description="任务名称")
    job_function: str = Field(..., description="任务函数名")
    job_type: JobType = Field(..., description="任务类型")
    job_args: List[Any] = Field([], description="任务参数")
    job_kwargs: Dict[str, Any] = Field({}, description="任务关键字参数")
    trigger_config: Dict[str, Any] = Field(..., description="触发器配置")
    max_instances: int = Field(1, description="最大实例数")
    misfire_grace_time: int = Field(60, description="错过执行宽限时间")

class TaskResponse(BaseModel):
    task_id: str
    task_name: str
    task_data: Dict[str, Any]
    priority: int
    max_retries: int
    retry_delay: int
    timeout: int
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int
    error_message: Optional[str]
    result: Optional[Any]
    progress: float

    class Config:
        from_attributes = True

class ScheduledJobResponse(BaseModel):
    job_id: str
    job_name: str
    job_type: str
    job_function: str
    job_args: List[Any]
    job_kwargs: Dict[str, Any]
    trigger_config: Dict[str, Any]
    max_instances: int
    misfire_grace_time: int
    status: str
    created_at: datetime
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    run_count: int
    success_count: int
    failure_count: int
    last_error: Optional[str]

    class Config:
        from_attributes = True

class TaskStatsResponse(BaseModel):
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    retrying_tasks: int
    total_runs: int
    total_successes: int
    total_failures: int
    success_rate: float

# API端点
@router.post("/enqueue", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@handle_errors
async def enqueue_task(
    request: TaskCreateRequest,
    current_user: User = Depends(require_permission(Permission.TASK_CREATE)),
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    添加任务到队列
    """
    try:
        task_id = await task_manager.enqueue_task(
            queue_name=request.queue_name,
            task_name=request.task_name,
            task_data=request.task_data,
            priority=request.priority,
            max_retries=request.max_retries,
            retry_delay=request.retry_delay,
            timeout=request.timeout
        )
        
        # 获取任务信息
        task = await task_manager.get_task(task_id)
        if not task:
            raise BusinessError(code="TASK_NOT_FOUND", message="任务创建失败")
        
        return TaskResponse(**task.to_dict())
        
    except Exception as e:
        logger.error(f"添加任务到队列失败: {e}", exc_info=True)
        raise BusinessError(code="TASK_ENQUEUE_FAILED", message=f"添加任务到队列失败: {e}")

@router.get("/{task_id}", response_model=TaskResponse)
@handle_errors
async def get_task(
    task_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    获取任务信息
    """
    task = await task_manager.get_task(task_id)
    if not task:
        raise BusinessError(
            code="TASK_NOT_FOUND",
            message="任务未找到",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return TaskResponse(**task.to_dict())

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors
async def cancel_task(
    task_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    取消任务
    """
    task = await task_manager.get_task(task_id)
    if not task:
        raise BusinessError(
            code="TASK_NOT_FOUND",
            message="任务未找到",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # 验证租户权限
    if task.tenant_id != current_user.tenant_id:
        raise BusinessError(
            code="ACCESS_DENIED",
            message="无权访问此任务",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # 检查任务状态
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise BusinessError(
            code="TASK_NOT_CANCELLABLE",
            message=f"任务已{task.status.value}，无法取消",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # 取消任务
    success = await task_manager.cancel_task(task_id)
    
    if not success:
        raise BusinessError(
            code="CANCEL_FAILED",
            message="取消任务失败",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    logger.info(f"任务已取消: {task_id}")
    return {"message": "任务已取消"}

@router.get("/", response_model=List[TaskResponse])
@handle_errors
async def get_all_tasks(
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    task_manager: TaskManager = Depends(get_task_manager),
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[TaskStatus] = None,
    queue_filter: Optional[str] = None
):
    """
    获取所有任务
    """
    try:
        # 获取所有任务
        all_tasks = await task_manager.get_all_tasks()
        
        # 应用过滤条件
        filtered_tasks = all_tasks
        
        # 按状态过滤
        if status_filter:
            filtered_tasks = [task for task in filtered_tasks if task.status == status_filter]
        
        # 按队列过滤
        if queue_filter:
            filtered_tasks = [task for task in filtered_tasks if task.queue_name == queue_filter]
        
        # 按租户过滤（确保数据隔离）
        tenant_tasks = [task for task in filtered_tasks if task.tenant_id == current_user.tenant_id]
        
        # 应用分页
        paginated_tasks = tenant_tasks[offset:offset + limit]
        
        # 转换为响应模型
        task_responses = []
        for task in paginated_tasks:
            task_responses.append(TaskResponse(
                task_id=task.task_id,
                task_name=task.task_name,
                queue_name=task.queue_name,
                status=task.status.value,
                priority=task.priority.value,
                created_at=task.created_at.isoformat() if task.created_at else None,
                started_at=task.started_at.isoformat() if task.started_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None,
                retry_count=task.retry_count,
                max_retries=task.max_retries,
                error_message=task.error_message,
                result=task.result,
                tenant_id=task.tenant_id
            ))
        
        logger.info(f"获取任务列表: {len(task_responses)} 条记录")
        return task_responses
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise BusinessError(f"获取任务列表失败: {str(e)}")

@router.get("/stats/overview", response_model=TaskStatsResponse)
@handle_errors
async def get_task_stats(
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    task_manager: TaskManager = Depends(get_task_manager)
):
    """
    获取任务统计信息
    """
    stats = await task_manager.get_stats()
    
    return TaskStatsResponse(
        total_tasks=stats.get("total_tasks", 0),
        pending_tasks=stats.get("pending_tasks", 0),
        running_tasks=stats.get("running_tasks", 0),
        completed_tasks=stats.get("completed_tasks", 0),
        failed_tasks=stats.get("failed_tasks", 0),
        cancelled_tasks=stats.get("cancelled_tasks", 0),
        retrying_tasks=stats.get("retrying_tasks", 0),
        total_runs=stats.get("total_runs", 0),
        total_successes=stats.get("total_successes", 0),
        total_failures=stats.get("total_failures", 0),
        success_rate=stats.get("success_rate", 0.0)
    )

# 定时任务相关端点
@router.post("/scheduled", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
@handle_errors
async def create_scheduled_job(
    request: ScheduledJobCreateRequest,
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    创建定时任务
    """
    try:
        if request.job_type == JobType.CRON:
            job_id = await scheduler_service.add_cron_job(
                job_name=request.job_name,
                function_name=request.job_function,
                cron_config=request.trigger_config,
                job_args=request.job_args,
                job_kwargs=request.job_kwargs,
                max_instances=request.max_instances,
                misfire_grace_time=request.misfire_grace_time
            )
        elif request.job_type == JobType.INTERVAL:
            job_id = await scheduler_service.add_interval_job(
                job_name=request.job_name,
                function_name=request.job_function,
                interval_config=request.trigger_config,
                job_args=request.job_args,
                job_kwargs=request.job_kwargs,
                max_instances=request.max_instances,
                misfire_grace_time=request.misfire_grace_time
            )
        elif request.job_type == JobType.DATE:
            run_date = datetime.fromisoformat(request.trigger_config["run_date"])
            job_id = await scheduler_service.add_date_job(
                job_name=request.job_name,
                function_name=request.job_function,
                run_date=run_date,
                job_args=request.job_args,
                job_kwargs=request.job_kwargs,
                max_instances=request.max_instances,
                misfire_grace_time=request.misfire_grace_time
            )
        else:
            raise BusinessError(code="INVALID_JOB_TYPE", message="无效的任务类型")
        
        # 获取任务信息
        job = await scheduler_service.get_job(job_id)
        if not job:
            raise BusinessError(code="JOB_NOT_FOUND", message="定时任务创建失败")
        
        return ScheduledJobResponse(**job.to_dict())
        
    except Exception as e:
        logger.error(f"创建定时任务失败: {e}", exc_info=True)
        raise BusinessError(code="SCHEDULED_JOB_CREATE_FAILED", message=f"创建定时任务失败: {e}")

@router.get("/scheduled/{job_id}", response_model=ScheduledJobResponse)
@handle_errors
async def get_scheduled_job(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    获取定时任务信息
    """
    job = await scheduler_service.get_job(job_id)
    if not job:
        raise BusinessError(
            code="JOB_NOT_FOUND",
            message="定时任务未找到",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return ScheduledJobResponse(**job.to_dict())

@router.get("/scheduled/", response_model=List[ScheduledJobResponse])
@handle_errors
async def get_all_scheduled_jobs(
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    获取所有定时任务
    """
    jobs = await scheduler_service.get_all_jobs()
    return [ScheduledJobResponse(**job.to_dict()) for job in jobs]

@router.delete("/scheduled/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors
async def remove_scheduled_job(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    删除定时任务
    """
    success = await scheduler_service.remove_job(job_id)
    if not success:
        raise BusinessError(
            code="JOB_REMOVE_FAILED",
            message="删除定时任务失败",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    return {"message": "定时任务已删除"}

@router.post("/scheduled/{job_id}/pause", status_code=status.HTTP_200_OK)
@handle_errors
async def pause_scheduled_job(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    暂停定时任务
    """
    success = await scheduler_service.pause_job(job_id)
    if not success:
        raise BusinessError(
            code="JOB_PAUSE_FAILED",
            message="暂停定时任务失败",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    return {"message": "定时任务已暂停"}

@router.post("/scheduled/{job_id}/resume", status_code=status.HTTP_200_OK)
@handle_errors
async def resume_scheduled_job(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.TASK_DELETE)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    恢复定时任务
    """
    success = await scheduler_service.resume_job(job_id)
    if not success:
        raise BusinessError(
            code="JOB_RESUME_FAILED",
            message="恢复定时任务失败",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    return {"message": "定时任务已恢复"}

@router.get("/scheduled/stats/overview")
@handle_errors
async def get_scheduler_stats(
    current_user: User = Depends(require_permission(Permission.TASK_READ)),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """
    获取调度器统计信息
    """
    stats = await scheduler_service.get_stats()
    return stats