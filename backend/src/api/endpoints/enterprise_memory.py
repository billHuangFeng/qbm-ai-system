"""
BMOS系统 - 企业记忆API端点
作用: 提供企业记忆相关的REST API
状态: ✅ 实施中
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid

from ...services.enterprise_memory_service import EnterpriseMemoryService
from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService
from ..dependencies import (
    get_memory_service as di_get_memory_service,
    get_database_service as di_get_database_service,
    get_cache_service as di_get_cache_service,
)
from ...auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memories", tags=["企业记忆"])

# Pydantic模型定义
class MemoryExtractionRequest(BaseModel):
    """记忆提取请求"""
    evaluation_data: Dict[str, Any] = Field(..., description="评价数据")
    historical_evaluations: Optional[List[Dict[str, Any]]] = Field([], description="历史评价数据")
    
    class Config:
        schema_extra = {
            "example": {
                "evaluation_data": {
                    "evaluationType": "adjust",
                    "metricAdjustments": [
                        {
                            "metricName": "revenue",
                            "adjustmentReason": "市场环境变化"
                        }
                    ],
                    "evaluationContent": "需要根据市场环境调整预测模型"
                },
                "historical_evaluations": []
            }
        }

class MemorySearchRequest(BaseModel):
    """记忆搜索请求"""
    context: Dict[str, Any] = Field(..., description="当前业务上下文")
    memory_type: Optional[str] = Field(None, description="记忆类型")
    min_confidence: Optional[float] = Field(0.7, description="最小置信度")
    min_relevance: Optional[float] = Field(0.6, description="最小相关性")
    limit: Optional[int] = Field(10, description="返回数量限制")
    
    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "scenario": "revenue_prediction",
                    "department": "sales",
                    "time_period": "2024-Q1"
                },
                "memory_type": "pattern",
                "min_confidence": 0.7,
                "min_relevance": 0.6,
                "limit": 10
            }
        }

class MemoryApplicationRequest(BaseModel):
    """记忆应用请求"""
    base_prediction: Dict[str, Any] = Field(..., description="基础预测结果")
    memory_ids: List[str] = Field(..., description="要应用的记忆ID列表")
    
class MemoryTrackingRequest(BaseModel):
    """记忆追踪请求"""
    memory_id: str = Field(..., description="记忆ID")
    application_result: Dict[str, Any] = Field(..., description="应用结果")

class MemoryInfo(BaseModel):
    """记忆信息"""
    id: str
    memory_type: str
    memory_category: Optional[str]
    memory_title: str
    memory_description: Optional[str]
    memory_content: Dict[str, Any]
    source_type: str
    source_reference_id: Optional[str]
    confidence_score: float
    success_rate: Optional[float]
    applied_count: int
    created_at: str
    last_applied_at: Optional[str]
    is_active: bool

class MemorySearchResult(BaseModel):
    """记忆搜索结果"""
    memories: List[MemoryInfo]
    total_count: int
    search_context: Dict[str, Any]

class MemoryExtractionResult(BaseModel):
    """记忆提取结果"""
    success: bool
    memories: List[MemoryInfo]
    memory_count: int
    message: str

# 依赖注入
def get_memory_service() -> EnterpriseMemoryService:
    return di_get_memory_service()

def get_database_service() -> DatabaseService:
    return di_get_database_service()

def get_cache_service() -> CacheService:
    return di_get_cache_service()

@router.post("/extract", response_model=MemoryExtractionResult)
async def extract_memory_from_feedback(
    request: MemoryExtractionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """从管理者评价中提取企业记忆"""
    try:
        # 执行记忆提取
        extraction_result = await memory_service.extract_memory_from_feedback(
            evaluation_data=request.evaluation_data,
            historical_evaluations=request.historical_evaluations
        )
        
        if not extraction_result['success']:
            raise HTTPException(
                status_code=500, 
                detail=f"记忆提取失败: {extraction_result.get('error', 'Unknown error')}"
            )
        
        # 保存提取的记忆到数据库
        saved_memories = []
        for memory_data in extraction_result['memories']:
            memory_id = str(uuid.uuid4())
            
            await db_service.execute_insert("""
                INSERT INTO enterprise_memory (
                    id, tenant_id, memory_type, memory_category,
                    memory_title, memory_description, memory_content,
                    source_type, source_reference_id, confidence_score,
                    created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """, [
                memory_id,
                current_user['tenant_id'],
                memory_data['memory_type'],
                memory_data.get('memory_category'),
                memory_data['memory_title'],
                memory_data.get('memory_description'),
                memory_data['memory_content'],
                memory_data['source_type'],
                memory_data.get('source_reference_id'),
                memory_data['confidence_score'],
                current_user['user_id']
            ])
            
            # 构建返回的记忆信息
            memory_info = MemoryInfo(
                id=memory_id,
                memory_type=memory_data['memory_type'],
                memory_category=memory_data.get('memory_category'),
                memory_title=memory_data['memory_title'],
                memory_description=memory_data.get('memory_description'),
                memory_content=memory_data['memory_content'],
                source_type=memory_data['source_type'],
                source_reference_id=memory_data.get('source_reference_id'),
                confidence_score=memory_data['confidence_score'],
                success_rate=None,
                applied_count=0,
                created_at=datetime.now().isoformat(),
                last_applied_at=None,
                is_active=True
            )
            
            saved_memories.append(memory_info)
        
        return MemoryExtractionResult(
            success=True,
            memories=saved_memories,
            memory_count=len(saved_memories),
            message=f"成功提取 {len(saved_memories)} 条企业记忆"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"记忆提取失败: {str(e)}")

@router.post("/search", response_model=MemorySearchResult)
async def search_memories(
    request: MemorySearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """搜索相关企业记忆"""
    try:
        # 检查缓存
        cache_key = f"memory_search:{hash(str(request.dict()))}"
        cached_result = await cache_service.get("memory", cache_key)
        
        if cached_result:
            return MemorySearchResult(**cached_result)
        
        # 从数据库获取现有记忆
        query = """
            SELECT * FROM enterprise_memory 
            WHERE tenant_id = $1 AND is_active = true
        """
        params = [current_user['tenant_id']]
        
        if request.memory_type:
            query += " AND memory_type = $2"
            params.append(request.memory_type)
        
        query += " ORDER BY confidence_score DESC, created_at DESC"
        
        existing_memories = await db_service.execute_query(query, params)
        
        # 执行记忆检索
        relevant_memories = await memory_service.retrieve_relevant_memories(
            current_context=request.context,
            existing_memories=existing_memories,
            min_confidence=request.min_confidence,
            min_relevance=request.min_relevance
        )
        
        # 限制返回数量
        limited_memories = relevant_memories[:request.limit]
        
        # 构建返回结果
        memory_infos = []
        for memory_data in limited_memories:
            memory_info = MemoryInfo(
                id=memory_data['id'],
                memory_type=memory_data['memory_type'],
                memory_category=memory_data.get('memory_category'),
                memory_title=memory_data['memory_title'],
                memory_description=memory_data.get('memory_description'),
                memory_content=memory_data['memory_content'],
                source_type=memory_data['source_type'],
                source_reference_id=memory_data.get('source_reference_id'),
                confidence_score=memory_data['confidence_score'],
                success_rate=memory_data.get('success_rate'),
                applied_count=memory_data.get('applied_count', 0),
                created_at=memory_data['created_at'],
                last_applied_at=memory_data.get('last_applied_at'),
                is_active=memory_data['is_active']
            )
            memory_infos.append(memory_info)
        
        result = MemorySearchResult(
            memories=memory_infos,
            total_count=len(relevant_memories),
            search_context=request.context
        )
        
        # 缓存结果
        await cache_service.set("memory", result.dict(), cache_key, ttl=1800)
        
        return result
        
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        raise HTTPException(status_code=500, detail=f"记忆搜索失败: {str(e)}")

@router.post("/apply")
async def apply_memory_to_prediction(
    request: MemoryApplicationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """将企业记忆应用到预测结果"""
    try:
        # 获取记忆数据
        memories = []
        for memory_id in request.memory_ids:
            memory_data = await db_service.execute_one("""
                SELECT * FROM enterprise_memory 
                WHERE id = $1 AND tenant_id = $2 AND is_active = true
            """, [memory_id, current_user['tenant_id']])
            
            if memory_data:
                memories.append(memory_data)
        
        if not memories:
            raise HTTPException(status_code=404, detail="未找到有效的记忆")
        
        # 应用记忆到预测
        adjusted_prediction = await memory_service.apply_memory_to_prediction(
            base_prediction=request.base_prediction,
            memories=memories
        )
        
        return {
            "success": True,
            "original_prediction": request.base_prediction,
            "adjusted_prediction": adjusted_prediction,
            "applied_memories": len(memories),
            "adjustment_summary": _generate_adjustment_summary(
                request.base_prediction,
                adjusted_prediction
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory application failed: {e}")
        raise HTTPException(status_code=500, detail=f"记忆应用失败: {str(e)}")

@router.post("/track")
async def track_memory_effectiveness(
    request: MemoryTrackingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: EnterpriseMemoryService = Depends(get_memory_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """追踪记忆应用效果"""
    try:
        # 验证记忆是否存在
        memory_data = await db_service.execute_one("""
            SELECT * FROM enterprise_memory 
            WHERE id = $1 AND tenant_id = $2
        """, [request.memory_id, current_user['tenant_id']])
        
        if not memory_data:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        # 追踪记忆效果
        tracking_result = await memory_service.track_memory_effectiveness(
            memory_id=request.memory_id,
            application_result=request.application_result,
            supabase_client=db_service
        )
        
        if not tracking_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"记忆追踪失败: {tracking_result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "memory_id": request.memory_id,
            "tracking_result": tracking_result,
            "message": "记忆应用效果已记录"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory tracking failed: {e}")
        raise HTTPException(status_code=500, detail=f"记忆追踪失败: {str(e)}")

@router.get("/{memory_id}", response_model=MemoryInfo)
async def get_memory_info(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取记忆详细信息"""
    try:
        memory_data = await db_service.execute_one("""
            SELECT * FROM enterprise_memory 
            WHERE id = $1 AND tenant_id = $2
        """, [memory_id, current_user['tenant_id']])
        
        if not memory_data:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        return MemoryInfo(**memory_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memory info failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆信息失败: {str(e)}")

@router.get("/", response_model=List[MemoryInfo])
async def list_memories(
    memory_type: Optional[str] = None,
    memory_category: Optional[str] = None,
    min_confidence: Optional[float] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """列出企业记忆"""
    try:
        query = """
            SELECT * FROM enterprise_memory 
            WHERE tenant_id = $1 AND is_active = true
        """
        params = [current_user['tenant_id']]
        
        if memory_type:
            query += f" AND memory_type = ${len(params) + 1}"
            params.append(memory_type)
        
        if memory_category:
            query += f" AND memory_category = ${len(params) + 1}"
            params.append(memory_category)
        
        if min_confidence:
            query += f" AND confidence_score >= ${len(params) + 1}"
            params.append(min_confidence)
        
        query += " ORDER BY confidence_score DESC, created_at DESC"
        
        memories = await db_service.execute_query(query, params)
        
        return [MemoryInfo(**memory) for memory in memories]
        
    except Exception as e:
        logger.error(f"List memories failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆列表失败: {str(e)}")

@router.delete("/{memory_id}")
async def deactivate_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """停用记忆"""
    try:
        # 验证记忆是否存在
        memory_data = await db_service.execute_one("""
            SELECT * FROM enterprise_memory 
            WHERE id = $1 AND tenant_id = $2
        """, [memory_id, current_user['tenant_id']])
        
        if not memory_data:
            raise HTTPException(status_code=404, detail="记忆不存在")
        
        # 停用记忆
        await db_service.execute_update("""
            UPDATE enterprise_memory 
            SET is_active = false, deprecated_at = $1
            WHERE id = $2
        """, [datetime.now(), memory_id])
        
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆已停用"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate memory failed: {e}")
        raise HTTPException(status_code=500, detail=f"停用记忆失败: {str(e)}")

@router.get("/stats/summary")
async def get_memory_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """获取记忆统计信息"""
    try:
        # 总体统计
        total_stats = await db_service.execute_one("""
            SELECT 
                COUNT(*) as total_memories,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_memories,
                AVG(confidence_score) as avg_confidence,
                AVG(success_rate) as avg_success_rate,
                SUM(applied_count) as total_applications
            FROM enterprise_memory 
            WHERE tenant_id = $1
        """, [current_user['tenant_id']])
        
        # 按类型统计
        type_stats = await db_service.execute_query("""
            SELECT 
                memory_type,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence,
                AVG(success_rate) as avg_success_rate
            FROM enterprise_memory 
            WHERE tenant_id = $1 AND is_active = true
            GROUP BY memory_type
            ORDER BY count DESC
        """, [current_user['tenant_id']])
        
        return {
            "summary": total_stats,
            "by_type": type_stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get memory stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"获取记忆统计失败: {str(e)}")

def _generate_adjustment_summary(original: Dict[str, Any], adjusted: Dict[str, Any]) -> Dict[str, Any]:
    """生成调整摘要"""
    summary = {}
    
    for key, original_value in original.items():
        if key in adjusted and adjusted[key] != original_value:
            summary[key] = {
                "original": original_value,
                "adjusted": adjusted[key],
                "change": adjusted[key] - original_value if isinstance(original_value, (int, float)) else "modified"
            }
    
    return summary

