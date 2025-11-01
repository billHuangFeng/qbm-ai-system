"""
优化建议相关API端点
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ...auth import get_current_user, require_permission, Permission, User
from ..dependencies import get_database_service
from ...services.database_service import DatabaseService
from ...error_handling.decorators import handle_api_errors
from ...logging_config import get_logger

router = APIRouter()
logger = get_logger("optimization_endpoints")

# 请求模型
class OptimizationRequest(BaseModel):
    recommendation_type: str
    title: str
    description: str
    priority: str = "medium"
    impact_score: Optional[float] = None
    implementation_effort: Optional[str] = None
    expected_roi: Optional[float] = None

class OptimizationResponse(BaseModel):
    id: int
    tenant_id: str
    recommendation_id: str
    recommendation_type: str
    title: str
    description: str
    priority: str
    impact_score: Optional[float]
    implementation_effort: Optional[str]
    expected_roi: Optional[float]
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# 创建优化建议
@router.post("/", response_model=OptimizationResponse)
@handle_api_errors
async def create_optimization(
    optimization_data: OptimizationRequest,
    current_user: User = Depends(require_permission(Permission.WRITE_OPTIMIZATION)),
    db: DatabaseService = Depends(get_database_service)
):
    """创建优化建议"""
    try:
        # 生成唯一ID
        recommendation_id = str(uuid.uuid4())
        
        # 验证输入数据
        if not optimization_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="优化建议标题不能为空"
            )
        
        if not optimization_data.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="优化建议描述不能为空"
            )
        
        # 计算影响分数（如果未提供）
        if optimization_data.impact_score is None:
            impact_score = _calculate_impact_score(optimization_data)
        else:
            impact_score = optimization_data.impact_score
        
        # 插入数据库
        query = """
            INSERT INTO optimization_recommendations 
            (recommendation_id, tenant_id, recommendation_type, title, description, 
             priority, impact_score, implementation_effort, expected_roi, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
        """
        
        now = datetime.now()
        params = [
            recommendation_id,
            current_user.tenant_id,
            optimization_data.recommendation_type,
            optimization_data.title,
            optimization_data.description,
            optimization_data.priority,
            impact_score,
            optimization_data.implementation_effort,
            optimization_data.expected_roi,
            "pending",
            now,
            now
        ]
        
        result = await db.execute(query, params)
        optimization_id = result.fetchone()[0]
        
        logger.info(f"优化建议已创建: {recommendation_id}")
        
        return OptimizationResponse(
            id=optimization_id,
            tenant_id=current_user.tenant_id,
            recommendation_id=recommendation_id,
            recommendation_type=optimization_data.recommendation_type,
            title=optimization_data.title,
            description=optimization_data.description,
            priority=optimization_data.priority,
            impact_score=impact_score,
            implementation_effort=optimization_data.implementation_effort,
            expected_roi=optimization_data.expected_roi,
            status="pending",
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建优化建议失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建优化建议失败: {str(e)}"
        )

# 获取优化建议列表
@router.get("/", response_model=List[OptimizationResponse])
@handle_api_errors
async def get_optimizations(
    current_user: User = Depends(require_permission(Permission.READ_OPTIMIZATION)),
    db: DatabaseService = Depends(get_database_service),
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None
):
    """获取优化建议列表"""
    try:
        # 构建查询
        query = """
            SELECT id, recommendation_id, tenant_id, recommendation_type, title, description,
                   priority, impact_score, implementation_effort, expected_roi, status,
                   created_at, updated_at
            FROM optimization_recommendations
            WHERE tenant_id = $1
        """
        params = [current_user.tenant_id]
        
        # 添加过滤条件
        if status_filter:
            query += " AND status = $" + str(len(params) + 1)
            params.append(status_filter)
        
        if priority_filter:
            query += " AND priority = $" + str(len(params) + 1)
            params.append(priority_filter)
        
        # 添加排序和分页
        query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
        params.extend([limit, offset])
        
        # 执行查询
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        # 构建响应
        optimizations = []
        for row in rows:
            optimizations.append(OptimizationResponse(
                id=row[0],
                tenant_id=row[2],
                recommendation_id=row[1],
                recommendation_type=row[3],
                title=row[4],
                description=row[5],
                priority=row[6],
                impact_score=row[7],
                implementation_effort=row[8],
                expected_roi=row[9],
                status=row[10],
                created_at=row[11].isoformat() if row[11] else None,
                updated_at=row[12].isoformat() if row[12] else None
            ))
        
        logger.info(f"获取优化建议列表: {len(optimizations)} 条记录")
        return optimizations
        
    except Exception as e:
        logger.error(f"获取优化建议列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取优化建议列表失败: {str(e)}"
        )

# 获取单个优化建议
@router.get("/{recommendation_id}", response_model=OptimizationResponse)
@handle_api_errors
async def get_optimization(
    recommendation_id: str,
    current_user: User = Depends(require_permission(Permission.READ_OPTIMIZATION)),
    db: DatabaseService = Depends(get_database_service)
):
    """获取单个优化建议"""
    try:
        # 查询单个优化建议
        query = """
            SELECT id, recommendation_id, tenant_id, recommendation_type, title, description,
                   priority, impact_score, implementation_effort, expected_roi, status,
                   created_at, updated_at
            FROM optimization_recommendations
            WHERE recommendation_id = $1 AND tenant_id = $2
        """
        
        result = await db.execute(query, [recommendation_id, current_user.tenant_id])
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="优化建议不存在"
            )
        
        # 构建响应
        optimization = OptimizationResponse(
            id=row[0],
            tenant_id=row[2],
            recommendation_id=row[1],
            recommendation_type=row[3],
            title=row[4],
            description=row[5],
            priority=row[6],
            impact_score=row[7],
            implementation_effort=row[8],
            expected_roi=row[9],
            status=row[10],
            created_at=row[11].isoformat() if row[11] else None,
            updated_at=row[12].isoformat() if row[12] else None
        )
        
        logger.info(f"获取优化建议: {recommendation_id}")
        return optimization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取优化建议失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取优化建议失败: {str(e)}"
        )

# 辅助函数
def _calculate_impact_score(optimization_data: OptimizationRequest) -> float:
    """计算影响分数"""
    base_score = 5.0  # 基础分数
    
    # 根据优先级调整
    priority_multiplier = {
        "low": 0.5,
        "medium": 1.0,
        "high": 1.5,
        "critical": 2.0
    }
    
    multiplier = priority_multiplier.get(optimization_data.priority, 1.0)
    
    # 根据类型调整
    type_multiplier = {
        "performance": 1.2,
        "security": 1.5,
        "cost": 1.0,
        "user_experience": 1.1,
        "maintenance": 0.8
    }
    
    type_mult = type_multiplier.get(optimization_data.recommendation_type, 1.0)
    
    # 计算最终分数
    final_score = base_score * multiplier * type_mult
    
    # 限制在1-10范围内
    return max(1.0, min(10.0, final_score))


