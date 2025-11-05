"""
专家知识库 API 端点
提供知识管理、文档导入、搜索等功能
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from datetime import datetime

from ...services.expert_knowledge import (
    ExpertKnowledgeService,
    DocumentProcessingService,
    KnowledgeIntegrationService,
    KnowledgeSearchService,
)
from ...services.database_service import DatabaseService
from ...services.enterprise_memory_service import EnterpriseMemoryService
from ..dependencies import get_database_service, get_cache_service, get_memory_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expert-knowledge", tags=["专家知识库"])


# Pydantic 模型


class CreateKnowledgeRequest(BaseModel):
    """创建知识请求"""

    title: str = Field(..., min_length=1, max_length=500, description="知识标题")
    content: str = Field(..., min_length=1, description="知识内容")
    knowledge_type: str = Field(..., description="知识类型")
    domain_category: str = Field(..., description="领域分类")
    problem_type: str = Field(..., description="问题类型")
    summary: Optional[str] = Field(None, description="摘要")
    tags: Optional[List[str]] = Field(default=[], description="标签")
    source_type: str = Field(default="manual_entry", description="来源类型")
    source_reference: Optional[str] = Field(None, description="来源引用")
    is_public: bool = Field(default=False, description="是否公开")


class UpdateKnowledgeRequest(BaseModel):
    """更新知识请求"""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    knowledge_type: Optional[str] = None
    domain_category: Optional[str] = None
    problem_type: Optional[str] = None
    tags: Optional[List[str]] = None
    source_reference: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class SearchKnowledgeRequest(BaseModel):
    """搜索知识请求"""

    query: Optional[str] = Field(None, description="搜索关键词")
    domain_category: Optional[str] = None
    problem_type: Optional[str] = None
    knowledge_type: Optional[str] = None
    tags: Optional[List[str]] = None
    verification_status: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ApplyKnowledgeRequest(BaseModel):
    """应用知识请求"""

    application_context: str = Field(..., description="应用场景")
    application_type: str = Field(
        ..., description="应用方式: reference/reasoning/validation"
    )
    applied_content: str = Field(..., description="应用的知识内容摘要")
    decision_id: Optional[str] = None
    related_service: Optional[str] = None
    reasoning_excerpt: Optional[str] = None


class VerifyKnowledgeRequest(BaseModel):
    """验证知识请求"""

    verification_status: str = Field(
        ..., description="验证状态: pending/verified/rejected"
    )
    verification_notes: Optional[str] = None


# 依赖注入


async def get_expert_knowledge_service(
    db: DatabaseService = Depends(get_database_service),
) -> ExpertKnowledgeService:
    """获取专家知识服务"""
    return ExpertKnowledgeService(db_service=db)


async def get_document_processing_service() -> DocumentProcessingService:
    """获取文档处理服务"""
    return DocumentProcessingService()


async def get_knowledge_integration_service(
    knowledge_service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
    db: DatabaseService = Depends(get_database_service),
    memory: EnterpriseMemoryService = Depends(get_memory_service),
) -> KnowledgeIntegrationService:
    """获取知识集成服务"""
    search_service = KnowledgeSearchService(db_service=db)
    return KnowledgeIntegrationService(
        knowledge_service=knowledge_service,
        search_service=search_service,
        memory_service=memory,
    )


# 辅助函数（模拟用户信息）
def get_current_user_mock() -> Dict[str, Any]:
    """模拟获取当前用户（实际应使用认证依赖）"""
    return {"user_id": "test_user", "tenant_id": "test_tenant", "role": "admin"}


# API 端点


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    request: CreateKnowledgeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """创建知识条目"""
    try:
        result = await service.create_knowledge(
            tenant_id=current_user["tenant_id"],
            title=request.title,
            content=request.content,
            knowledge_type=request.knowledge_type,
            domain_category=request.domain_category,
            problem_type=request.problem_type,
            summary=request.summary,
            tags=request.tags,
            source_type=request.source_type,
            source_reference=request.source_reference,
            is_public=request.is_public,
            created_by=current_user["user_id"],
        )

        return {"success": True, "message": "知识创建成功", **result}

    except Exception as e:
        logger.error(f"创建知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识失败: {str(e)}",
        )


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_knowledge(
    file: UploadFile = File(...),
    title: str = Form(...),
    domain_category: str = Form(...),
    problem_type: str = Form(...),
    knowledge_type: str = Form(default="methodology"),
    source_reference: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON字符串
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    knowledge_service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
    doc_service: DocumentProcessingService = Depends(get_document_processing_service),
):
    """导入知识（从文件）"""
    try:
        import json
        import os
        from pathlib import Path

        # 解析标签
        tag_list = json.loads(tags) if tags else []

        # 保存上传的文件
        upload_dir = Path("uploads/expert_knowledge")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_ext = Path(file.filename).suffix.lower()
        safe_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / safe_filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 检测文件类型
        file_type = doc_service._detect_file_type(str(file_path))

        # 提取文本
        extract_result = await doc_service.extract_text_from_file(
            str(file_path), file_type
        )

        if not extract_result.get("success"):
            raise ValueError("文档文本提取失败")

        extracted_text = extract_result.get("full_text", "")
        if not extracted_text:
            raise ValueError("提取的文本为空")

        # 生成摘要
        summary = doc_service.generate_summary(extracted_text)

        # 提取关键概念（作为标签补充）
        key_concepts = doc_service.extract_key_concepts(extracted_text)
        all_tags = list(set(tag_list + key_concepts[:5]))  # 合并标签

        # 创建知识条目
        create_result = await knowledge_service.create_knowledge(
            tenant_id=current_user["tenant_id"],
            title=title,
            content=extracted_text,
            knowledge_type=knowledge_type,
            domain_category=domain_category,
            problem_type=problem_type,
            summary=summary,
            tags=all_tags,
            source_type="external_import",
            source_reference=source_reference,
            created_by=current_user["user_id"],
        )

        knowledge_id = create_result.get("knowledge_id")

        # 保存附件信息（这里应该保存到数据库，暂时仅记录日志）
        logger.info(f"文件已上传: {file_path}, 关联知识ID: {knowledge_id}")

        return {
            "success": True,
            "message": "知识导入成功",
            "knowledge_id": knowledge_id,
            "file_info": {
                "file_name": file.filename,
                "file_type": file_type,
                "file_size": len(content),
                "extracted_text_length": len(extracted_text),
            },
            "extracted_summary": summary,
            "extracted_tags": all_tags,
        }

    except Exception as e:
        logger.error(f"导入知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入知识失败: {str(e)}",
        )


@router.get("/{knowledge_id}")
async def get_knowledge(
    knowledge_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """获取知识详情"""
    try:
        knowledge = await service.get_knowledge_by_id(
            knowledge_id, current_user["tenant_id"]
        )

        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识不存在"
            )

        return {"success": True, "knowledge": knowledge}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识详情失败: {str(e)}",
        )


@router.put("/{knowledge_id}")
async def update_knowledge(
    knowledge_id: str,
    request: UpdateKnowledgeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """更新知识"""
    try:
        updates = request.dict(exclude_unset=True)

        result = await service.update_knowledge(
            knowledge_id=knowledge_id,
            tenant_id=current_user["tenant_id"],
            updates=updates,
        )

        return {"success": True, "message": "知识更新成功", **result}

    except Exception as e:
        logger.error(f"更新知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识失败: {str(e)}",
        )


@router.delete("/{knowledge_id}")
async def delete_knowledge(
    knowledge_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """删除知识（软删除）"""
    try:
        result = await service.delete_knowledge(knowledge_id, current_user["tenant_id"])

        return {"success": True, "message": "知识删除成功", **result}

    except Exception as e:
        logger.error(f"删除知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识失败: {str(e)}",
        )


@router.post("/search")
async def search_knowledge(
    request: SearchKnowledgeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """搜索知识"""
    try:
        result = await service.search_knowledge(
            tenant_id=current_user["tenant_id"],
            query=request.query,
            domain_category=request.domain_category,
            problem_type=request.problem_type,
            knowledge_type=request.knowledge_type,
            tags=request.tags,
            verification_status=request.verification_status,
            limit=request.limit,
            offset=request.offset,
        )

        return {"success": True, **result}

    except Exception as e:
        logger.error(f"搜索知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识失败: {str(e)}",
        )


@router.get("/{knowledge_id}/related")
async def get_related_knowledge(
    knowledge_id: str,
    limit: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """获取相关知识"""
    try:
        related = await service.get_related_knowledge(
            knowledge_id=knowledge_id, tenant_id=current_user["tenant_id"], limit=limit
        )

        return {"success": True, "related_knowledge": related, "count": len(related)}

    except Exception as e:
        logger.error(f"获取相关知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相关知识失败: {str(e)}",
        )


@router.post("/{knowledge_id}/apply")
async def apply_knowledge(
    knowledge_id: str,
    request: ApplyKnowledgeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """记录知识应用"""
    try:
        result = await service.apply_knowledge(
            knowledge_id=knowledge_id,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["user_id"],
            application_context=request.application_context,
            application_type=request.application_type,
            applied_content=request.applied_content,
            decision_id=request.decision_id,
            related_service=request.related_service,
            reasoning_excerpt=request.reasoning_excerpt,
        )

        return {"success": True, "message": "知识应用记录成功", **result}

    except Exception as e:
        logger.error(f"记录知识应用失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录知识应用失败: {str(e)}",
        )


@router.post("/{knowledge_id}/verify")
async def verify_knowledge(
    knowledge_id: str,
    request: VerifyKnowledgeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    service: ExpertKnowledgeService = Depends(get_expert_knowledge_service),
):
    """验证知识（严谨性检查）"""
    try:
        result = await service.verify_knowledge(
            knowledge_id=knowledge_id,
            tenant_id=current_user["tenant_id"],
            verified_by=current_user["user_id"],
            verification_status=request.verification_status,
            verification_notes=request.verification_notes,
        )

        return {"success": True, "message": "知识验证成功", **result}

    except Exception as e:
        logger.error(f"验证知识失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证知识失败: {str(e)}",
        )


@router.get("/categories/domains")
async def get_domain_categories():
    """获取领域分类列表"""
    return {
        "success": True,
        "categories": [
            "business_model",
            "cost_optimization",
            "resource_allocation",
            "capability_enhancement",
            "market_strategy",
            "product_design",
            "risk_management",
            "performance_measurement",
        ],
    }


@router.get("/categories/problem-types")
async def get_problem_types():
    """获取问题类型列表"""
    return {
        "success": True,
        "problem_types": [
            "decision_problem",
            "optimization_problem",
            "risk_problem",
            "innovation_problem",
            "retrospective_problem",
        ],
    }


@router.get("/categories/knowledge-types")
async def get_knowledge_types():
    """获取知识类型列表"""
    return {
        "success": True,
        "knowledge_types": [
            "theory",
            "methodology",
            "case_study",
            "tool_template",
            "best_practice",
            "warning",
        ],
    }


@router.post("/generate-reasoning-chain")
async def generate_reasoning_chain(
    decision_context: Dict[str, Any],
    include_data_evidence: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user_mock),
    integration_service: KnowledgeIntegrationService = Depends(
        get_knowledge_integration_service
    ),
):
    """生成推理链（结合专家知识+企业记忆+数据）"""
    try:
        reasoning_chain = await integration_service.generate_reasoning_chain(
            tenant_id=current_user["tenant_id"],
            decision_context=decision_context,
            include_data_evidence=include_data_evidence,
        )

        return {"success": True, "reasoning_chain": reasoning_chain}

    except Exception as e:
        logger.error(f"生成推理链失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成推理链失败: {str(e)}",
        )
