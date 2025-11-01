"""
企业记忆相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ...auth import get_current_user
from ...services.enterprise_memory_service import EnterpriseMemoryService
from ...error_handling.unified import handle_errors, BusinessError
from ...logging_config import get_logger

router = APIRouter(prefix="/memories", tags=["memories"])
logger = get_logger("memories_api")

# 请求模型
class MemoryExtractionRequest(BaseModel):
    evaluation_data: Dict[str, Any] = Field(..., description="评价数据")
    tenant_id: str = Field(..., description="租户ID")
    extraction_type: str = Field(default="automatic", description="提取类型")

class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="搜索查询")
    memory_type: Optional[str] = Field(None, description="记忆类型")
    limit: int = Field(default=10, description="结果数量限制")

class MemoryFeedbackRequest(BaseModel):
    memory_id: str = Field(..., description="记忆ID")
    feedback_type: str = Field(..., description="反馈类型")
    feedback_content: str = Field(..., description="反馈内容")
    rating: Optional[float] = Field(None, description="评分")

# 响应模型
class MemoryResponse(BaseModel):
    id: str
    memory_type: str
    content: str
    keywords: List[str]
    confidence_score: float
    usage_count: int
    last_used: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class MemoryExtractionResponse(BaseModel):
    memory_id: str
    extracted_memories: List[MemoryResponse]
    extraction_summary: Dict[str, Any]
    created_at: str

    class Config:
        from_attributes = True

# 提取企业记忆
@router.post("/extract", response_model=MemoryExtractionResponse)
@handle_errors
async def extract_memories(
    request: MemoryExtractionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """从评价数据中提取企业记忆"""
    try:
        memory_id = str(uuid.uuid4())
        
        # 提取企业记忆
        extraction_result = await memory_service.extract_memories_from_evaluation(
            evaluation_data=request.evaluation_data,
            tenant_id=request.tenant_id,
            extraction_type=request.extraction_type
        )
        
        # 创建记忆响应
        extracted_memories = [
            MemoryResponse(
                id=memory["id"],
                memory_type=memory["memory_type"],
                content=memory["content"],
                keywords=memory["keywords"],
                confidence_score=memory["confidence_score"],
                usage_count=memory["usage_count"],
                last_used=memory["last_used"],
                created_at=memory["created_at"],
                updated_at=memory["updated_at"]
            )
            for memory in extraction_result.get("memories", [])
        ]
        
        return MemoryExtractionResponse(
            memory_id=memory_id,
            extracted_memories=extracted_memories,
            extraction_summary=extraction_result.get("summary", {}),
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"企业记忆提取失败: {e}")
        raise BusinessError(
            code="MEMORY_EXTRACTION_FAILED",
            message=f"企业记忆提取失败: {str(e)}"
        )

# 搜索企业记忆
@router.post("/search", response_model=List[MemoryResponse])
@handle_errors
async def search_memories(
    request: MemorySearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """搜索企业记忆"""
    try:
        search_results = await memory_service.search_memories(
            query=request.query,
            tenant_id=current_user["tenant_id"],
            memory_type=request.memory_type,
            limit=request.limit
        )
        
        return [
            MemoryResponse(
                id=memory["id"],
                memory_type=memory["memory_type"],
                content=memory["content"],
                keywords=memory["keywords"],
                confidence_score=memory["confidence_score"],
                usage_count=memory["usage_count"],
                last_used=memory["last_used"],
                created_at=memory["created_at"],
                updated_at=memory["updated_at"]
            )
            for memory in search_results
        ]
        
    except Exception as e:
        logger.error(f"企业记忆搜索失败: {e}")
        raise BusinessError(
            code="MEMORY_SEARCH_FAILED",
            message=f"企业记忆搜索失败: {str(e)}"
        )

# 获取企业记忆列表
@router.get("/", response_model=List[MemoryResponse])
@handle_errors
async def get_memories(
    memory_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """获取企业记忆列表"""
    try:
        memories = await memory_service.get_memories_by_tenant(
            tenant_id=current_user["tenant_id"],
            memory_type=memory_type,
            limit=limit,
            offset=offset
        )
        
        return [
            MemoryResponse(
                id=memory["id"],
                memory_type=memory["memory_type"],
                content=memory["content"],
                keywords=memory["keywords"],
                confidence_score=memory["confidence_score"],
                usage_count=memory["usage_count"],
                last_used=memory["last_used"],
                created_at=memory["created_at"],
                updated_at=memory["updated_at"]
            )
            for memory in memories
        ]
        
    except Exception as e:
        logger.error(f"获取企业记忆列表失败: {e}")
        raise BusinessError(
            code="MEMORY_LIST_FAILED",
            message=f"获取企业记忆列表失败: {str(e)}"
        )

# 获取单个企业记忆
@router.get("/{memory_id}", response_model=MemoryResponse)
@handle_errors
async def get_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """获取单个企业记忆"""
    try:
        memory = await memory_service.get_memory_by_id(
            memory_id=memory_id,
            tenant_id=current_user["tenant_id"]
        )
        
        if not memory:
            raise BusinessError(
                code="MEMORY_NOT_FOUND",
                message="企业记忆不存在"
            )
        
        return MemoryResponse(
            id=memory["id"],
            memory_type=memory["memory_type"],
            content=memory["content"],
            keywords=memory["keywords"],
            confidence_score=memory["confidence_score"],
            usage_count=memory["usage_count"],
            last_used=memory["last_used"],
            created_at=memory["created_at"],
            updated_at=memory["updated_at"]
        )
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取企业记忆失败: {e}")
        raise BusinessError(
            code="MEMORY_RETRIEVAL_FAILED",
            message=f"获取企业记忆失败: {str(e)}"
        )

# 更新企业记忆
@router.put("/{memory_id}", response_model=MemoryResponse)
@handle_errors
async def update_memory(
    memory_id: str,
    content: str,
    keywords: List[str],
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """更新企业记忆"""
    try:
        # 检查记忆是否存在
        memory = await memory_service.get_memory_by_id(
            memory_id=memory_id,
            tenant_id=current_user["tenant_id"]
        )
        if not memory:
            raise BusinessError(
                code="MEMORY_NOT_FOUND",
                message="企业记忆不存在"
            )
        
        # 更新记忆
        updated_memory = await memory_service.update_memory(
            memory_id=memory_id,
            tenant_id=current_user["tenant_id"],
            content=content,
            keywords=keywords
        )
        
        return MemoryResponse(
            id=updated_memory["id"],
            memory_type=updated_memory["memory_type"],
            content=updated_memory["content"],
            keywords=updated_memory["keywords"],
            confidence_score=updated_memory["confidence_score"],
            usage_count=updated_memory["usage_count"],
            last_used=updated_memory["last_used"],
            created_at=updated_memory["created_at"],
            updated_at=updated_memory["updated_at"]
        )
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"更新企业记忆失败: {e}")
        raise BusinessError(
            code="MEMORY_UPDATE_FAILED",
            message=f"更新企业记忆失败: {str(e)}"
        )

# 删除企业记忆
@router.delete("/{memory_id}")
@handle_errors
async def delete_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """删除企业记忆"""
    try:
        # 检查记忆是否存在
        memory = await memory_service.get_memory_by_id(
            memory_id=memory_id,
            tenant_id=current_user["tenant_id"]
        )
        if not memory:
            raise BusinessError(
                code="MEMORY_NOT_FOUND",
                message="企业记忆不存在"
            )
        
        # 删除记忆
        await memory_service.delete_memory(
            memory_id=memory_id,
            tenant_id=current_user["tenant_id"]
        )
        
        return {"success": True, "message": "企业记忆删除成功"}
        
    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"删除企业记忆失败: {e}")
        raise BusinessError(
            code="MEMORY_DELETE_FAILED",
            message=f"删除企业记忆失败: {str(e)}"
        )

# 记录反馈
@router.post("/feedback", response_model=Dict[str, Any])
@handle_errors
async def record_feedback(
    request: MemoryFeedbackRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """记录企业记忆反馈"""
    try:
        # 记录反馈
        feedback_result = await memory_service.record_feedback(
            memory_id=request.memory_id,
            feedback_type=request.feedback_type,
            feedback_content=request.feedback_content,
            rating=request.rating,
            tenant_id=current_user["tenant_id"]
        )
        
        return {
            "success": True,
            "feedback_id": feedback_result.get("feedback_id"),
            "message": "反馈记录成功"
        }
        
    except Exception as e:
        logger.error(f"记录反馈失败: {e}")
        raise BusinessError(
            code="FEEDBACK_RECORD_FAILED",
            message=f"记录反馈失败: {str(e)}"
        )

# 获取企业记忆统计
@router.get("/stats", response_model=Dict[str, Any])
@handle_errors
async def get_memory_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """获取企业记忆统计"""
    try:
        stats = await memory_service.get_memory_stats(
            tenant_id=current_user["tenant_id"]
        )
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取企业记忆统计失败: {e}")
        raise BusinessError(
            code="MEMORY_STATS_FAILED",
            message=f"获取企业记忆统计失败: {str(e)}"
        )

# 应用企业记忆
@router.post("/apply", response_model=Dict[str, Any])
@handle_errors
async def apply_memory(
    memory_id: str,
    context: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(lambda: EnterpriseMemoryService())
):
    """应用企业记忆"""
    try:
        # 应用记忆
        application_result = await memory_service.apply_memory(
            memory_id=memory_id,
            context=context,
            tenant_id=current_user["tenant_id"]
        )
        
        return {
            "success": True,
            "application_result": application_result,
            "message": "企业记忆应用成功"
        }
        
    except Exception as e:
        logger.error(f"应用企业记忆失败: {e}")
        raise BusinessError(
            code="MEMORY_APPLICATION_FAILED",
            message=f"应用企业记忆失败: {str(e)}"
        )
