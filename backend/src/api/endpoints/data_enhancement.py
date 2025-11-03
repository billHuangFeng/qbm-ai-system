"""
数据增强API端点
提供数据导入完善系统第3阶段的5个核心服务API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from backend.src.security.auth import get_current_user
from backend.src.security.database import SecureDatabaseService
from backend.src.services.data_enhancement import (
    MasterDataMatcher,
    CalculationConflictDetector,
    SmartValueImputer,
    DataQualityAssessor,
    StagingTableManager
)
from backend.src.error_handling.unified import handle_errors, BusinessError

# 获取数据库服务的依赖
async def get_db_service() -> SecureDatabaseService:
    """获取数据库服务实例"""
    from backend.src.security.database import db_service
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库服务未初始化"
        )
    return db_service

router = APIRouter(prefix="/data-enhancement", tags=["data-enhancement"])
logger = logging.getLogger(__name__)


# ==================== 请求模型 ====================

class MasterDataMatchRequest(BaseModel):
    """主数据匹配请求"""
    data_type: str = Field(..., description="数据类型（order/production/expense）")
    records: List[Dict[str, Any]] = Field(..., description="待匹配记录列表")
    master_data_table: str = Field(..., description="主数据表名")
    confidence_threshold: float = Field(0.8, description="置信度阈值（默认0.8）")


class ConflictDetectionRequest(BaseModel):
    """计算冲突检测请求"""
    data_type: str = Field(..., description="数据类型（order/production/expense）")
    records: List[Dict[str, Any]] = Field(..., description="数据记录列表")
    calculation_rules: List[Dict[str, Any]] = Field(..., description="计算规则定义")
    tolerance: Optional[float] = Field(0.01, description="容差阈值（默认0.01）")


class ImputationRequest(BaseModel):
    """智能补值请求"""
    data_type: str = Field(..., description="数据类型（order/production/expense）")
    records: List[Dict[str, Any]] = Field(..., description="数据记录列表")
    field_configs: Dict[str, Dict[str, Any]] = Field(..., description="字段配置（类型、默认值、业务规则）")
    strategy: str = Field("auto", description="补值策略（auto/knn/iterative/random_forest/rule_based）")


class QualityAssessmentRequest(BaseModel):
    """数据质量评估请求"""
    data_type: str = Field(..., description="数据类型（order/production/expense）")
    records: List[Dict[str, Any]] = Field(..., description="数据记录列表")
    validation_rules: Dict[str, Any] = Field(..., description="验证规则配置")


class StagingTableRequest(BaseModel):
    """暂存表管理请求"""
    data_type: str = Field(..., description="数据类型（order/production/expense）")
    operation: str = Field(..., description="操作类型（create/migrate/cleanup）")
    target_table: Optional[str] = Field(None, description="目标表名（create和migrate时需要）")
    staging_table_name: Optional[str] = Field(None, description="暂存表名（migrate时需要）")
    records: Optional[List[Dict[str, Any]]] = Field(None, description="数据记录（create时需要）")
    retention_days: Optional[int] = Field(None, description="保留天数（cleanup时需要）")


# ==================== 响应模型 ====================

class MasterDataMatchResponse(BaseModel):
    """主数据匹配响应"""
    matched_records: List[Dict[str, Any]]
    unmatched_records: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    success: bool = True
    message: str = "主数据匹配完成"


class ConflictDetectionResponse(BaseModel):
    """计算冲突检测响应"""
    conflicts: List[Dict[str, Any]]
    cascade_conflicts: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    success: bool = True
    message: str = "计算冲突检测完成"


class ImputationResponse(BaseModel):
    """智能补值响应"""
    imputed_records: List[Dict[str, Any]]
    imputation_log: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    success: bool = True
    message: str = "智能补值完成"


class QualityAssessmentResponse(BaseModel):
    """数据质量评估响应"""
    overall_score: float
    importability: str  # excellent/good/fixable/rejected
    dimensions: Dict[str, Any]
    blocking_issues: List[Dict[str, Any]]
    fixable_issues: List[Dict[str, Any]]
    recommendations: List[str]
    success: bool = True
    message: str = "数据质量评估完成"


class StagingTableResponse(BaseModel):
    """暂存表管理响应"""
    staging_table_name: Optional[str] = None
    status: str
    row_count: Optional[int] = None
    created_at: Optional[str] = None
    success: bool = True
    message: str = "暂存表操作完成"


# ==================== API端点 ====================

@router.post("/match-master-data", response_model=MasterDataMatchResponse)
@handle_errors
async def match_master_data(
    request: MasterDataMatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """
    主数据匹配API
    
    根据辅助信息（名称、统一社会信用代码等）匹配主数据ID
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少租户ID"
            )
        
        # 初始化匹配服务
        matcher = MasterDataMatcher(db_service)
        
        # 执行匹配
        result = await matcher.match_master_data(
            data_type=request.data_type,
            records=request.records,
            master_data_table=request.master_data_table,
            tenant_id=tenant_id,
            confidence_threshold=request.confidence_threshold
        )
        
        return MasterDataMatchResponse(
            matched_records=result["matched_records"],
            unmatched_records=result["unmatched_records"],
            statistics=result["statistics"],
            success=True,
            message="主数据匹配完成"
        )
        
    except Exception as e:
        logger.error(f"主数据匹配失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"主数据匹配失败: {str(e)}"
        )


@router.post("/detect-conflicts", response_model=ConflictDetectionResponse)
@handle_errors
async def detect_conflicts(
    request: ConflictDetectionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """
    计算冲突检测API
    
    检测存在计算逻辑关系的字段之间的冲突
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        # 初始化冲突检测服务
        detector = CalculationConflictDetector(db_service)
        
        # 执行冲突检测
        result = await detector.detect_conflicts(
            data_type=request.data_type,
            records=request.records,
            calculation_rules=request.calculation_rules,
            tolerance=request.tolerance,
            tenant_id=tenant_id
        )
        
        return ConflictDetectionResponse(
            conflicts=result["conflicts"],
            cascade_conflicts=result.get("cascade_conflicts", []),
            statistics=result["statistics"],
            success=True,
            message="计算冲突检测完成"
        )
        
    except Exception as e:
        logger.error(f"计算冲突检测失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算冲突检测失败: {str(e)}"
        )


@router.post("/impute-values", response_model=ImputationResponse)
@handle_errors
async def impute_values(
    request: ImputationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """
    智能补值API
    
    智能填充缺失值
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        # 初始化补值服务
        imputer = SmartValueImputer(db_service)
        
        # 执行补值
        result = await imputer.impute_values(
            data_type=request.data_type,
            records=request.records,
            field_configs=request.field_configs,
            strategy=request.strategy,
            tenant_id=tenant_id
        )
        
        return ImputationResponse(
            imputed_records=result["imputed_records"],
            imputation_log=result["imputation_log"],
            statistics=result["statistics"],
            success=True,
            message="智能补值完成"
        )
        
    except Exception as e:
        logger.error(f"智能补值失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能补值失败: {str(e)}"
        )


@router.post("/assess-quality", response_model=QualityAssessmentResponse)
@handle_errors
async def assess_quality(
    request: QualityAssessmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """
    数据质量评估API
    
    7维度质量检查 + 质量评分 + 可导入性判定
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少租户ID"
            )
        
        # 初始化质量评估服务
        assessor = DataQualityAssessor(db_service)
        
        # 执行质量评估
        result = await assessor.assess_quality(
            data_type=request.data_type,
            records=request.records,
            validation_rules=request.validation_rules,
            tenant_id=tenant_id
        )
        
        return QualityAssessmentResponse(
            overall_score=result["overall_score"],
            importability=result["importability"],
            dimensions=result["dimensions"],
            blocking_issues=result["blocking_issues"],
            fixable_issues=result["fixable_issues"],
            recommendations=result["recommendations"],
            success=True,
            message="数据质量评估完成"
        )
        
    except Exception as e:
        logger.error(f"数据质量评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据质量评估失败: {str(e)}"
        )


@router.post("/manage-staging", response_model=StagingTableResponse)
@handle_errors
async def manage_staging(
    request: StagingTableRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """
    暂存表管理API
    
    动态创建和管理暂存表
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少租户ID"
            )
        
        # 初始化暂存表管理服务
        manager = StagingTableManager(db_service)
        
        # 执行暂存表操作
        result = await manager.manage_staging(
            data_type=request.data_type,
            tenant_id=tenant_id,
            operation=request.operation,
            target_table=request.target_table,
            staging_table_name=request.staging_table_name,
            records=request.records,
            retention_days=request.retention_days
        )
        
        return StagingTableResponse(
            staging_table_name=result.get("staging_table_name"),
            status=result.get("status", "success"),
            row_count=result.get("row_count"),
            created_at=result.get("created_at"),
            success=True,
            message="暂存表操作完成"
        )
        
    except Exception as e:
        logger.error(f"暂存表管理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"暂存表管理失败: {str(e)}"
        )

