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
    StagingTableManager,
)
from backend.src.services.data_enhancement.intelligent_field_mapper import (
    IntelligentFieldMapper,
)
from backend.src.error_handling.unified import handle_errors, BusinessError


# 获取数据库服务的依赖
async def get_db_service() -> SecureDatabaseService:
    """获取数据库服务实例"""
    from backend.src.security.database import db_service

    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库服务未初始化",
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
    field_configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="字段配置（类型、默认值、业务规则）"
    )
    strategy: str = Field(
        "auto", description="补值策略（auto/knn/iterative/random_forest/rule_based）"
    )


class QualityAssessmentRequest(BaseModel):
    """数据质量评估请求"""

    data_type: str = Field(..., description="数据类型（order/production/expense）")
    records: List[Dict[str, Any]] = Field(..., description="数据记录列表")
    validation_rules: Dict[str, Any] = Field(..., description="验证规则配置")


class StagingTableRequest(BaseModel):
    """暂存表管理请求"""

    data_type: str = Field(..., description="数据类型（order/production/expense）")
    operation: str = Field(..., description="操作类型（create/migrate/cleanup）")
    target_table: Optional[str] = Field(
        None, description="目标表名（create和migrate时需要）"
    )
    staging_table_name: Optional[str] = Field(
        None, description="暂存表名（migrate时需要）"
    )
    records: Optional[List[Dict[str, Any]]] = Field(
        None, description="数据记录（create时需要）"
    )
    retention_days: Optional[int] = Field(None, description="保留天数（cleanup时需要）")


class FieldMappingRequest(BaseModel):
    """字段映射推荐请求"""

    source_fields: List[str] = Field(..., description="源文件字段列表")
    target_table: str = Field(..., description="目标表名（必需）")
    source_system: str = Field("upload", description="数据源系统标识（默认'upload'）")
    document_type: Optional[str] = Field(
        None, description="单据类型（SO/SH/SI/PO/RC/PI）"
    )
    user_id: Optional[str] = Field(None, description="用户ID（可选，用于个人化推荐）")


class MappingHistoryRequest(BaseModel):
    """保存映射历史请求"""

    source_system: str = Field(..., description="数据源系统")
    target_table: str = Field(..., description="目标表名")
    source_field: str = Field(..., description="源字段名")
    target_field: str = Field(..., description="目标字段名")
    document_type: Optional[str] = Field(None, description="单据类型")
    mapping_method: str = Field(
        "manual", description="映射方法（manual/rule/similarity）"
    )
    confidence_score: Optional[float] = Field(None, description="置信度分数（0-1）")


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


class FieldMappingResponse(BaseModel):
    """字段映射推荐响应"""

    recommendations: List[Dict[str, Any]]
    success: bool = True
    message: str = "字段映射推荐完成"


class TableSchemaResponse(BaseModel):
    """表结构响应"""

    table_name: str
    fields: List[Dict[str, Any]]
    master_data_fields: List[str]
    field_types: Dict[str, str]
    success: bool = True
    message: str = "获取表结构成功"


class AvailableTablesResponse(BaseModel):
    """可用表列表响应"""

    tables: List[Dict[str, Any]]
    categories: Dict[str, List[str]]
    success: bool = True
    message: str = "获取可用表列表成功"


class MappingHistoryResponse(BaseModel):
    """保存映射历史响应"""

    mapping_id: str
    success: bool = True
    message: str = "映射历史保存成功"


# ==================== API端点 ====================


@router.post("/match-master-data", response_model=MasterDataMatchResponse)
@handle_errors
async def match_master_data(
    request: MasterDataMatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    主数据匹配API

    根据辅助信息（名称、统一社会信用代码等）匹配主数据ID
    """
    try:
        tenant_id = current_user.get("tenant_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 初始化匹配服务
        matcher = MasterDataMatcher(db_service)

        # 执行匹配
        result = await matcher.match_master_data(
            data_type=request.data_type,
            records=request.records,
            master_data_table=request.master_data_table,
            tenant_id=tenant_id,
            confidence_threshold=request.confidence_threshold,
        )

        return MasterDataMatchResponse(
            matched_records=result["matched_records"],
            unmatched_records=result["unmatched_records"],
            statistics=result["statistics"],
            success=True,
            message="主数据匹配完成",
        )

    except Exception as e:
        logger.error(f"主数据匹配失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"主数据匹配失败: {str(e)}",
        )


@router.post("/detect-conflicts", response_model=ConflictDetectionResponse)
@handle_errors
async def detect_conflicts(
    request: ConflictDetectionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
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
            tenant_id=tenant_id,
        )

        return ConflictDetectionResponse(
            conflicts=result["conflicts"],
            cascade_conflicts=result.get("cascade_conflicts", []),
            statistics=result["statistics"],
            success=True,
            message="计算冲突检测完成",
        )

    except Exception as e:
        logger.error(f"计算冲突检测失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算冲突检测失败: {str(e)}",
        )


@router.post("/impute-values", response_model=ImputationResponse)
@handle_errors
async def impute_values(
    request: ImputationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
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
            tenant_id=tenant_id,
        )

        return ImputationResponse(
            imputed_records=result["imputed_records"],
            imputation_log=result["imputation_log"],
            statistics=result["statistics"],
            success=True,
            message="智能补值完成",
        )

    except Exception as e:
        logger.error(f"智能补值失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能补值失败: {str(e)}",
        )


@router.post("/assess-quality", response_model=QualityAssessmentResponse)
@handle_errors
async def assess_quality(
    request: QualityAssessmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    数据质量评估API

    7维度质量检查 + 质量评分 + 可导入性判定
    """
    try:
        tenant_id = current_user.get("tenant_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 初始化质量评估服务
        assessor = DataQualityAssessor(db_service)

        # 执行质量评估
        result = await assessor.assess_quality(
            data_type=request.data_type,
            records=request.records,
            validation_rules=request.validation_rules,
            tenant_id=tenant_id,
        )

        return QualityAssessmentResponse(
            overall_score=result["overall_score"],
            importability=result["importability"],
            dimensions=result["dimensions"],
            blocking_issues=result["blocking_issues"],
            fixable_issues=result["fixable_issues"],
            recommendations=result["recommendations"],
            success=True,
            message="数据质量评估完成",
        )

    except Exception as e:
        logger.error(f"数据质量评估失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据质量评估失败: {str(e)}",
        )


@router.post("/manage-staging", response_model=StagingTableResponse)
@handle_errors
async def manage_staging(
    request: StagingTableRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    暂存表管理API

    动态创建和管理暂存表
    """
    try:
        tenant_id = current_user.get("tenant_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
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
            retention_days=request.retention_days,
        )

        return StagingTableResponse(
            staging_table_name=result.get("staging_table_name"),
            status=result.get("status", "success"),
            row_count=result.get("row_count"),
            created_at=result.get("created_at"),
            success=True,
            message="暂存表操作完成",
        )

    except Exception as e:
        logger.error(f"暂存表管理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"暂存表管理失败: {str(e)}",
        )


# ==================== 字段映射相关API ====================


@router.post("/recommend-field-mappings", response_model=FieldMappingResponse)
@handle_errors
async def recommend_field_mappings(
    request: FieldMappingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    字段映射推荐API

    根据源字段列表和目标表，智能推荐字段映射关系
    支持历史映射、规则匹配和相似度计算
    """
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("user_id") or request.user_id

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 初始化字段映射器
        mapper = IntelligentFieldMapper(db_service)

        # 执行字段映射推荐
        recommendations = await mapper.recommend_mappings(
            source_fields=request.source_fields,
            source_system=request.source_system,
            target_table=request.target_table,
            document_type=request.document_type,
            user_id=user_id,
        )

        # 转换为字典格式
        recommendations_dict = []
        for rec in recommendations:
            recommendations_dict.append(
                {
                    "source_field": rec.source_field,
                    "recommended_target": rec.recommended_target,
                    "recommended_confidence": rec.recommended_confidence,
                    "candidates": [
                        {
                            "target_field": c.target_field,
                            "confidence": c.confidence,
                            "method": c.method,
                            "source": c.source,
                        }
                        for c in rec.candidates
                    ],
                }
            )

        return FieldMappingResponse(
            recommendations=recommendations_dict,
            success=True,
            message="字段映射推荐完成",
        )

    except ValueError as e:
        logger.error(f"字段映射推荐失败（参数错误）: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"字段映射推荐失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"字段映射推荐失败: {str(e)}",
        )


@router.get("/table-schema/{table_name}", response_model=TableSchemaResponse)
@handle_errors
async def get_table_schema(
    table_name: str,
    document_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    获取表结构API

    返回目标表的字段定义和主数据匹配字段
    """
    try:
        tenant_id = current_user.get("tenant_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 初始化字段映射器
        mapper = IntelligentFieldMapper(db_service)

        # 获取表字段
        table_fields = await mapper._get_target_table_fields(table_name, use_cache=True)

        # 获取主数据匹配字段
        master_data_fields = await mapper._get_master_data_match_fields(
            table_name, document_type, use_cache=True
        )

        # 获取字段类型信息
        field_types = {}
        try:
            # 查询字段类型
            query_sql = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = :table_name
                  AND table_schema = 'public'
                ORDER BY ordinal_position
            """
            results = await db_service.fetch_all(query_sql, {"table_name": table_name})

            for row in results:
                field_name = row["column_name"]
                field_types[field_name] = {
                    "data_type": row["data_type"],
                    "max_length": row.get("character_maximum_length"),
                    "nullable": row["is_nullable"] == "YES",
                    "default": row.get("column_default"),
                }
        except Exception as e:
            logger.warning(f"获取字段类型信息失败: {e}")
            # 如果获取类型失败，使用默认值
            for field in table_fields:
                field_types[field] = {"data_type": "unknown"}

        # 构建字段详细信息
        fields_info = []
        for field in table_fields:
            field_info = {
                "name": field,
                "type": field_types.get(field, {}).get("data_type", "unknown"),
                "nullable": field_types.get(field, {}).get("nullable", True),
                "default": field_types.get(field, {}).get("default"),
            }
            fields_info.append(field_info)

        return TableSchemaResponse(
            table_name=table_name,
            fields=fields_info,
            master_data_fields=master_data_fields,
            field_types=field_types,
            success=True,
            message="获取表结构成功",
        )

    except ValueError as e:
        logger.error(f"获取表结构失败（参数错误）: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"获取表结构失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表结构失败: {str(e)}",
        )


@router.get("/available-tables", response_model=AvailableTablesResponse)
@handle_errors
async def get_available_tables(
    document_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    获取可用目标表列表API

    返回所有可用的导入目标表列表，按业务场景分组
    """
    try:
        tenant_id = current_user.get("tenant_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 定义可用表列表（根据document_type过滤）
        all_tables = [
            # 销售流程表
            {
                "table_name": "sales_order_header",
                "display_name": "销售订单头表",
                "category": "销售流程",
                "document_type": "SO",
                "has_lines": True,
                "line_table": "sales_order_line",
            },
            {
                "table_name": "shipment_header",
                "display_name": "发货单头表",
                "category": "销售流程",
                "document_type": "SH",
                "has_lines": True,
                "line_table": "shipment_line",
            },
            {
                "table_name": "sales_invoice_header",
                "display_name": "销售发票头表",
                "category": "销售流程",
                "document_type": "SI",
                "has_lines": True,
                "line_table": "sales_invoice_line",
            },
            # 采购流程表
            {
                "table_name": "purchase_order_header",
                "display_name": "采购订单头表",
                "category": "采购流程",
                "document_type": "PO",
                "has_lines": True,
                "line_table": "purchase_order_line",
            },
            {
                "table_name": "receipt_header",
                "display_name": "收货单头表",
                "category": "采购流程",
                "document_type": "RC",
                "has_lines": True,
                "line_table": "receipt_line",
            },
            {
                "table_name": "purchase_invoice_header",
                "display_name": "采购发票头表",
                "category": "采购流程",
                "document_type": "PI",
                "has_lines": True,
                "line_table": "purchase_invoice_line",
            },
            # 主数据表
            {
                "table_name": "dim_customer",
                "display_name": "客户主数据",
                "category": "主数据",
                "document_type": None,
                "has_lines": False,
            },
            {
                "table_name": "dim_supplier",
                "display_name": "供应商主数据",
                "category": "主数据",
                "document_type": None,
                "has_lines": False,
            },
            {
                "table_name": "dim_sku",
                "display_name": "SKU主数据",
                "category": "主数据",
                "document_type": None,
                "has_lines": False,
            },
            {
                "table_name": "dim_channel",
                "display_name": "渠道主数据",
                "category": "主数据",
                "document_type": None,
                "has_lines": False,
            },
        ]

        # 根据document_type过滤
        if document_type:
            filtered_tables = [
                t for t in all_tables if t.get("document_type") == document_type
            ]
        else:
            filtered_tables = all_tables

        # 按category分组
        categories = {}
        for table in filtered_tables:
            category = table["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(table["table_name"])

        return AvailableTablesResponse(
            tables=filtered_tables,
            categories=categories,
            success=True,
            message="获取可用表列表成功",
        )

    except Exception as e:
        logger.error(f"获取可用表列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可用表列表失败: {str(e)}",
        )


@router.post("/save-mapping-history", response_model=MappingHistoryResponse)
@handle_errors
async def save_mapping_history(
    request: MappingHistoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service),
):
    """
    保存映射历史API

    将用户确认的字段映射保存到field_mapping_history表
    用于未来的智能推荐学习
    """
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("user_id")

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="缺少租户ID"
            )

        # 使用UPSERT（INSERT ... ON CONFLICT）处理映射历史
        # 如果记录已存在，则更新使用次数；如果不存在，则插入新记录
        upsert_sql = """
            INSERT INTO field_mapping_history (
                tenant_id,
                source_system,
                target_table,
                source_field,
                target_field,
                document_type,
                mapping_method,
                confidence_score,
                created_by,
                usage_count,
                last_used_at,
                created_at
            ) VALUES (
                :tenant_id,
                :source_system,
                :target_table,
                :source_field,
                :target_field,
                :document_type,
                :mapping_method,
                :confidence_score,
                :created_by,
                1,
                NOW(),
                NOW()
            )
            ON CONFLICT (tenant_id, source_system, target_table, source_field, target_field)
            DO UPDATE SET
                usage_count = field_mapping_history.usage_count + 1,
                last_used_at = NOW(),
                updated_at = NOW()
            RETURNING id
        """

        result = await db_service.fetch_one(
            upsert_sql,
            {
                "tenant_id": tenant_id,
                "source_system": request.source_system,
                "target_table": request.target_table,
                "source_field": request.source_field,
                "target_field": request.target_field,
                "document_type": request.document_type,
                "mapping_method": request.mapping_method,
                "confidence_score": request.confidence_score,
                "created_by": user_id,
            },
        )

        mapping_id = str(result["id"]) if result else None

        return MappingHistoryResponse(
            mapping_id=mapping_id or "unknown", success=True, message="映射历史保存成功"
        )

    except Exception as e:
        logger.error(f"保存映射历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存映射历史失败: {str(e)}",
        )
