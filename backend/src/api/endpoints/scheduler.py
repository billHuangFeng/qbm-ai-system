"""
定时任务和调度系统API端点
提供任务管理、执行监控、统计报告等功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.task_scheduler import (
    TaskScheduler,
    Task,
    TaskExecution,
    TaskSchedule,
    TaskStatus,
    TaskPriority,
    ScheduleType
)
from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService
from ..api.dependencies import get_db_service, get_cache_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/scheduler", tags=["Task Scheduler"])

# Pydantic模型
class TaskCreateRequest(BaseModel):
    """任务创建请求模型"""
    name: str = Field(..., description="任务名称", min_length=1, max_length=100)
    description: str = Field(..., description="任务描述")
    function_name: str = Field(..., description="任务函数名")
    parameters: Dict[str, Any] = Field(..., description="任务参数")
    schedule_type: ScheduleType = Field(..., description="调度类型")
    schedule_config: Dict[str, Any] = Field(..., description="调度配置")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="任务优先级")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=60, description="重试延迟(秒)")
    timeout: int = Field(default=300, description="超时时间(秒)")

class TaskUpdateRequest(BaseModel):
    """任务更新请求模型"""
    name: Optional[str] = Field(None, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    parameters: Optional[Dict[str, Any]] = Field(None, description="任务参数")
    schedule_type: Optional[ScheduleType] = Field(None, description="调度类型")
    schedule_config: Optional[Dict[str, Any]] = Field(None, description="调度配置")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    max_retries: Optional[int] = Field(None, description="最大重试次数")
    retry_delay: Optional[int] = Field(None, description="重试延迟(秒)")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")

class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    name: str
    status: str
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None

class TaskInfoResponse(BaseModel):
    """任务信息响应模型"""
    task_id: str
    name: str
    description: str
    function_name: str
    schedule_type: str
    priority: int
    status: str
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    retry_count: int
    max_retries: int
    created_at: str
    updated_at: str

class ExecutionInfoResponse(BaseModel):
    """执行信息响应模型"""
    execution_id: str
    task_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: str
    execution_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class SchedulerStatsResponse(BaseModel):
    """调度器统计响应模型"""
    is_running: bool
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    queue_size: int
    registered_functions: int

# 全局变量存储服务实例
scheduler: Optional[TaskScheduler] = None

# 依赖注入
async def get_task_scheduler(
    db_service: DatabaseService = Depends(get_db_service),
    cache_service: CacheService = Depends(get_cache_service)
) -> TaskScheduler:
    """获取任务调度器实例"""
    global scheduler
    
    if scheduler is None:
        scheduler = TaskScheduler(db_service, cache_service)
        
        # 注册预定义任务函数
        from ...services.task_scheduler import (
            data_quality_check_task,
            model_training_task,
            data_import_task,
            report_generation_task,
            cleanup_task
        )
        
        scheduler.register_task_function("data_quality_check", data_quality_check_task)
        scheduler.register_task_function("model_training", model_training_task)
        scheduler.register_task_function("data_import", data_import_task)
        scheduler.register_task_function("report_generation", report_generation_task)
        scheduler.register_task_function("cleanup", cleanup_task)
        
        # 启动调度器
        await scheduler.start_scheduler()
    
    return scheduler

# API端点
@router.post("/tasks")
async def create_task(
    request: TaskCreateRequest,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    创建任务
    
    创建一个新的定时任务，支持多种调度类型。
    """
    try:
        task_id = await scheduler.create_task(
            name=request.name,
            description=request.description,
            function_name=request.function_name,
            parameters=request.parameters,
            schedule_type=request.schedule_type,
            schedule_config=request.schedule_config,
            priority=request.priority,
            max_retries=request.max_retries,
            retry_delay=request.retry_delay,
            timeout=request.timeout
        )
        
        return {
            "success": True,
            "message": "任务创建成功",
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"创建任务失败: {str(e)}"
        )

@router.get("/tasks")
async def get_task_list(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    获取任务列表
    
    查询所有任务，支持按状态过滤和分页。
    """
    try:
        task_status = TaskStatus(status) if status else None
        
        tasks = await scheduler.get_task_list(
            status=task_status,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "tasks": tasks,
            "total_count": len(tasks),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get task list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取任务列表失败: {str(e)}"
        )

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    获取任务详情
    
    获取指定任务的详细信息。
    """
    try:
        task_status = await scheduler.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=404,
                detail=f"任务 {task_id} 不存在"
            )
        
        return {
            "success": True,
            "task": task_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取任务详情失败: {str(e)}"
        )

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    request: TaskUpdateRequest,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    更新任务
    
    更新指定任务的配置信息。
    """
    try:
        # 过滤掉None值
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        success = await scheduler.update_task(task_id, **update_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="更新任务失败"
            )
        
        return {
            "success": True,
            "message": "任务更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新任务失败: {str(e)}"
        )

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    删除任务
    
    删除指定的任务（不能删除正在运行的任务）。
    """
    try:
        success = await scheduler.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="无法删除正在运行的任务"
            )
        
        return {
            "success": True,
            "message": "任务删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"删除任务失败: {str(e)}"
        )

@router.post("/tasks/{task_id}/execute")
async def execute_task(
    task_id: str,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    立即执行任务
    
    立即执行指定的任务，不等待调度时间。
    """
    try:
        success = await scheduler.execute_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="执行任务失败"
            )
        
        return {
            "success": True,
            "message": "任务已加入执行队列"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"执行任务失败: {str(e)}"
        )

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    取消任务
    
    取消指定任务，包括正在运行的任务。
    """
    try:
        success = await scheduler.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="取消任务失败"
            )
        
        return {
            "success": True,
            "message": "任务已取消"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取消任务失败: {str(e)}"
        )

@router.get("/tasks/{task_id}/executions")
async def get_execution_history(
    task_id: str,
    limit: int = 50,
    offset: int = 0,
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    获取任务执行历史
    
    查询指定任务的执行历史记录。
    """
    try:
        executions = await scheduler.get_execution_history(
            task_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "executions": executions,
            "total_count": len(executions),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get execution history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取执行历史失败: {str(e)}"
        )

@router.get("/stats")
async def get_scheduler_stats(
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    获取调度器统计信息
    
    返回调度器的运行状态和统计数据。
    """
    try:
        stats = await scheduler.get_scheduler_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get scheduler stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

@router.get("/functions")
async def get_registered_functions(
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    获取已注册的任务函数
    
    返回所有已注册的任务函数列表。
    """
    try:
        functions = list(scheduler.task_functions.keys())
        
        return {
            "success": True,
            "functions": functions,
            "total_count": len(functions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get registered functions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取任务函数列表失败: {str(e)}"
        )

@router.post("/start")
async def start_scheduler(
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    启动调度器
    
    启动任务调度器。
    """
    try:
        await scheduler.start_scheduler()
        
        return {
            "success": True,
            "message": "调度器已启动"
        }
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"启动调度器失败: {str(e)}"
        )

@router.post("/stop")
async def stop_scheduler(
    scheduler: TaskScheduler = Depends(get_task_scheduler)
):
    """
    停止调度器
    
    停止任务调度器（等待正在执行的任务完成）。
    """
    try:
        await scheduler.stop_scheduler()
        
        return {
            "success": True,
            "message": "调度器已停止"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"停止调度器失败: {str(e)}"
        )

@router.get("/types")
async def get_schedule_types():
    """
    获取调度类型列表
    
    返回所有可用的调度类型。
    """
    try:
        types = [
            {
                "value": schedule_type.value,
                "name": schedule_type.name,
                "description": _get_schedule_type_description(schedule_type)
            }
            for schedule_type in ScheduleType
        ]
        
        return {
            "success": True,
            "types": types,
            "total_count": len(types)
        }
        
    except Exception as e:
        logger.error(f"Failed to get schedule types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取调度类型失败: {str(e)}"
        )

@router.get("/priorities")
async def get_task_priorities():
    """
    获取任务优先级列表
    
    返回所有可用的任务优先级。
    """
    try:
        priorities = [
            {
                "value": priority.value,
                "name": priority.name,
                "description": _get_priority_description(priority)
            }
            for priority in TaskPriority
        ]
        
        return {
            "success": True,
            "priorities": priorities,
            "total_count": len(priorities)
        }
        
    except Exception as e:
        logger.error(f"Failed to get task priorities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取任务优先级失败: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    任务调度器健康检查
    """
    return {
        "status": "healthy",
        "service": "Task Scheduler",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 辅助函数
def _get_schedule_type_description(schedule_type: ScheduleType) -> str:
    """获取调度类型描述"""
    descriptions = {
        ScheduleType.ONCE: "一次性执行，执行后自动删除",
        ScheduleType.INTERVAL: "按指定间隔循环执行",
        ScheduleType.CRON: "使用Cron表达式指定执行时间",
        ScheduleType.DAILY: "每天在指定时间执行",
        ScheduleType.WEEKLY: "每周在指定日期和时间执行",
        ScheduleType.MONTHLY: "每月在指定日期和时间执行"
    }
    return descriptions.get(schedule_type, "未知类型")

def _get_priority_description(priority: TaskPriority) -> str:
    """获取优先级描述"""
    descriptions = {
        TaskPriority.LOW: "低优先级，最后执行",
        TaskPriority.NORMAL: "普通优先级，按正常顺序执行",
        TaskPriority.HIGH: "高优先级，优先执行",
        TaskPriority.CRITICAL: "紧急优先级，立即执行"
    }
    return descriptions.get(priority, "未知优先级")

# 错误处理
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return {
        "success": False,
        "error_code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.now().isoformat()
    }

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "success": False,
        "error_code": 500,
        "message": "内部服务器错误",
        "timestamp": datetime.now().isoformat()
    }

