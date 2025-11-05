"""
学习模块 API 端点
提供课程、学习路径、进度、练习和测试功能
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...services.expert_knowledge import LearningService
from ...services.database_service import DatabaseService
from ..dependencies import get_database_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["学习模块"])


# Pydantic 模型


class CreateCourseRequest(BaseModel):
    """创建课程请求"""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    knowledge_ids: Optional[List[str]] = []
    modules: Optional[List[Dict[str, Any]]] = []
    estimated_hours: Optional[float] = None
    difficulty_level: str = Field(default="beginner")
    prerequisites: Optional[List[str]] = []
    cover_image_url: Optional[str] = None


class CreateLearningPathRequest(BaseModel):
    """创建学习路径请求"""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    objective: Optional[str] = None
    course_ids: List[str] = Field(..., description="课程ID序列")
    target_audience: Optional[str] = None
    estimated_total_hours: Optional[float] = None


class UpdateProgressRequest(BaseModel):
    """更新学习进度请求"""

    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SubmitExerciseRequest(BaseModel):
    """提交练习答案请求"""

    answer: Any = Field(..., description="答案（格式取决于题型）")


class SubmitTestRequest(BaseModel):
    """提交测试请求"""

    answers: Dict[str, Any] = Field(..., description="答案字典 {exercise_id: answer}")
    time_spent_minutes: int = Field(..., ge=0)


# 依赖注入


async def get_learning_service(
    db: DatabaseService = Depends(get_database_service),
) -> LearningService:
    """获取学习服务"""
    return LearningService(db_service=db)


def get_current_user_mock() -> Dict[str, Any]:
    """模拟获取当前用户"""
    return {"user_id": "test_user", "tenant_id": "test_tenant", "role": "admin"}


# ========== 文档浏览端点 ==========


@router.get("/knowledge/{knowledge_id}")
async def browse_knowledge(
    knowledge_id: str, current_user: Dict[str, Any] = Depends(get_current_user_mock)
):
    """浏览知识文档"""
    try:
        # 这里应该调用 ExpertKnowledgeService，暂时简化
        return {
            "success": True,
            "message": "浏览知识文档功能，需要集成 ExpertKnowledgeService",
            "knowledge_id": knowledge_id,
        }
    except Exception as e:
        logger.error(f"浏览知识文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"浏览知识文档失败: {str(e)}",
        )


# ========== 课程体系端点 ==========


@router.post("/courses/", status_code=status.HTTP_201_CREATED)
async def create_course(
    request: CreateCourseRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """创建课程"""
    try:
        result = await service.create_course(
            tenant_id=current_user["tenant_id"],
            title=request.title,
            description=request.description,
            knowledge_ids=request.knowledge_ids,
            modules=request.modules,
            estimated_hours=request.estimated_hours,
            difficulty_level=request.difficulty_level,
            prerequisites=request.prerequisites,
            cover_image_url=request.cover_image_url,
            created_by=current_user["user_id"],
        )

        return {"success": True, "message": "课程创建成功", **result}

    except Exception as e:
        logger.error(f"创建课程失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建课程失败: {str(e)}",
        )


@router.get("/courses/")
async def list_courses(
    is_published: Optional[bool] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取课程列表"""
    try:
        result = await service.list_courses(
            tenant_id=current_user["tenant_id"],
            is_published=is_published,
            difficulty_level=difficulty_level,
            limit=limit,
            offset=offset,
        )

        return {"success": True, **result}

    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取课程列表失败: {str(e)}",
        )


@router.get("/courses/{course_id}")
async def get_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取课程详情"""
    try:
        course = await service.get_course_by_id(course_id, current_user["tenant_id"])

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在"
            )

        return {"success": True, "course": course}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取课程详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取课程详情失败: {str(e)}",
        )


@router.post("/courses/{course_id}/enroll")
async def enroll_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """注册课程"""
    try:
        result = await service.start_learning(
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            course_id=course_id,
        )

        return {"success": True, "message": "课程注册成功", **result}

    except Exception as e:
        logger.error(f"注册课程失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册课程失败: {str(e)}",
        )


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取学习进度"""
    try:
        progress = await service.get_learning_progress(
            user_id=current_user["user_id"], course_id=course_id
        )

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="学习记录不存在"
            )

        return {"success": True, "progress": progress}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取学习进度失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习进度失败: {str(e)}",
        )


# ========== 学习路径端点 ==========


@router.post("/paths/", status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    request: CreateLearningPathRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """创建学习路径"""
    try:
        result = await service.create_learning_path(
            tenant_id=current_user["tenant_id"],
            title=request.title,
            description=request.description,
            objective=request.objective,
            course_ids=request.course_ids,
            target_audience=request.target_audience,
            estimated_total_hours=request.estimated_total_hours,
            created_by=current_user["user_id"],
        )

        return {"success": True, "message": "学习路径创建成功", **result}

    except Exception as e:
        logger.error(f"创建学习路径失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建学习路径失败: {str(e)}",
        )


@router.get("/paths/")
async def list_learning_paths(
    is_published: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取学习路径列表"""
    try:
        # 这里应该实现列表查询，暂时简化
        return {"success": True, "message": "学习路径列表功能待完善", "paths": []}
    except Exception as e:
        logger.error(f"获取学习路径列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习路径列表失败: {str(e)}",
        )


@router.get("/paths/{path_id}")
async def get_learning_path(
    path_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取学习路径详情"""
    try:
        path = await service.get_learning_path_by_id(path_id, current_user["tenant_id"])

        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在"
            )

        return {"success": True, "path": path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取学习路径详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习路径详情失败: {str(e)}",
        )


@router.post("/paths/{path_id}/start")
async def start_learning_path(
    path_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """开始学习路径"""
    try:
        # 获取路径信息
        path = await service.get_learning_path_by_id(path_id, current_user["tenant_id"])

        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="学习路径不存在"
            )

        # 注册第一个课程
        course_ids = path.get("course_ids", [])
        if not course_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="学习路径中没有课程"
            )

        # 注册第一个课程
        first_course_id = course_ids[0]
        result = await service.start_learning(
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            course_id=first_course_id,
        )

        return {
            "success": True,
            "message": "学习路径开始成功",
            "path_id": path_id,
            "first_course_id": first_course_id,
            **result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"开始学习路径失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始学习路径失败: {str(e)}",
        )


# ========== 交互式学习端点 ==========


@router.get("/courses/{course_id}/exercises")
async def get_exercises(
    course_id: str,
    knowledge_id: Optional[str] = None,
    exercise_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取练习题"""
    try:
        exercises = await service.get_exercises(
            course_id=course_id, knowledge_id=knowledge_id, exercise_type=exercise_type
        )

        return {"success": True, "exercises": exercises, "count": len(exercises)}

    except Exception as e:
        logger.error(f"获取练习题失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取练习题失败: {str(e)}",
        )


@router.post("/exercises/{exercise_id}/submit")
async def submit_exercise(
    exercise_id: str,
    request: SubmitExerciseRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """提交练习答案"""
    try:
        result = await service.submit_exercise_answer(
            exercise_id=exercise_id,
            user_id=current_user["user_id"],
            answer=request.answer,
        )

        return {"success": True, "message": "答案提交成功", **result}

    except Exception as e:
        logger.error(f"提交练习答案失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交练习答案失败: {str(e)}",
        )


@router.get("/courses/{course_id}/tests")
async def get_test(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """获取测试"""
    try:
        test = await service.get_test_by_course(course_id)

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="测试不存在"
            )

        return {"success": True, "test": test}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取测试失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试失败: {str(e)}",
        )


@router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: str,
    request: SubmitTestRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """提交测试"""
    try:
        result = await service.submit_test(
            test_id=test_id,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            answers=request.answers,
            time_spent_minutes=request.time_spent_minutes,
        )

        return {"success": True, "message": "测试提交成功", **result}

    except Exception as e:
        logger.error(f"提交测试失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交测试失败: {str(e)}",
        )


@router.post("/courses/{course_id}/progress")
async def update_learning_progress(
    course_id: str,
    request: UpdateProgressRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: LearningService = Depends(get_learning_service),
):
    """更新学习进度"""
    try:
        result = await service.update_learning_progress(
            user_id=current_user["user_id"],
            course_id=course_id,
            progress_percentage=request.progress_percentage,
            time_spent_minutes=request.time_spent_minutes,
            notes=request.notes,
        )

        return {"success": True, "message": "学习进度更新成功", **result}

    except Exception as e:
        logger.error(f"更新学习进度失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新学习进度失败: {str(e)}",
        )
