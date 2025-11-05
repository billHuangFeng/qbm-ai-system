"""
数据导入相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

from backend.src.security.auth import get_current_user
from backend.src.services.data_import_etl import DataImportETL
from backend.src.error_handling.unified import handle_errors, BusinessError
from backend.src.logging_config import get_logger

router = APIRouter(prefix="/data", tags=["data"])
logger = get_logger("data_import_api")


# 请求模型
class DataImportRequest(BaseModel):
    source_type: str = Field(..., description="数据源类型")
    document_format: str = Field(..., description="文档格式")
    field_mappings: List[Dict[str, str]] = Field(..., description="字段映射")
    target_table: str = Field(..., description="目标表")
    import_config: Dict[str, Any] = Field(default={}, description="导入配置")


class DataValidationRequest(BaseModel):
    table_name: str = Field(..., description="表名")
    validation_rules: List[Dict[str, Any]] = Field(..., description="验证规则")


# 响应模型
class DataImportResponse(BaseModel):
    import_id: str
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    errors: List[str]
    created_at: str

    class Config:
        from_attributes = True


class DataValidationResponse(BaseModel):
    validation_id: str
    table_name: str
    validation_results: Dict[str, Any]
    overall_score: float
    recommendations: List[str]
    created_at: str

    class Config:
        from_attributes = True


# 数据导入
@router.post("/import", response_model=DataImportResponse)
@handle_errors
async def import_data(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    document_format: str = Form(...),
    field_mappings: str = Form(...),
    target_table: str = Form(...),
    import_config: str = Form(default="{}"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """导入数据文件"""
    try:
        import_id = str(uuid.uuid4())

        # 解析表单数据
        field_mappings_list = json.loads(field_mappings)
        import_config_dict = json.loads(import_config)

        # 处理文件上传
        file_content = await file.read()

        # 执行数据导入
        import_result = await etl_service.process_data_import(
            file_content=file_content,
            filename=file.filename,
            source_type=source_type,
            document_format=document_format,
            field_mappings=field_mappings_list,
            target_table=target_table,
            import_config=import_config_dict,
            tenant_id=current_user["tenant_id"],
        )

        return DataImportResponse(
            import_id=import_id,
            status=import_result.get("status", "completed"),
            total_records=import_result.get("total_records", 0),
            successful_records=import_result.get("successful_records", 0),
            failed_records=import_result.get("failed_records", 0),
            errors=import_result.get("errors", []),
            created_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"数据导入失败: {e}")
        raise BusinessError(
            code="DATA_IMPORT_FAILED", message=f"数据导入失败: {str(e)}"
        )


# 数据验证
@router.post("/validate", response_model=DataValidationResponse)
@handle_errors
async def validate_data(
    request: DataValidationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """验证数据质量"""
    try:
        validation_id = str(uuid.uuid4())

        # 执行数据验证
        validation_result = await etl_service.validate_data_quality(
            table_name=request.table_name,
            validation_rules=request.validation_rules,
            tenant_id=current_user["tenant_id"],
        )

        return DataValidationResponse(
            validation_id=validation_id,
            table_name=request.table_name,
            validation_results=validation_result.get("results", {}),
            overall_score=validation_result.get("overall_score", 0.0),
            recommendations=validation_result.get("recommendations", []),
            created_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"数据验证失败: {e}")
        raise BusinessError(
            code="DATA_VALIDATION_FAILED", message=f"数据验证失败: {str(e)}"
        )


# 获取导入历史
@router.get("/import/history", response_model=List[DataImportResponse])
@handle_errors
async def get_import_history(
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """获取数据导入历史"""
    try:
        history = await etl_service.get_import_history(
            tenant_id=current_user["tenant_id"], limit=limit, offset=offset
        )

        return [
            DataImportResponse(
                import_id=record["import_id"],
                status=record["status"],
                total_records=record["total_records"],
                successful_records=record["successful_records"],
                failed_records=record["failed_records"],
                errors=record["errors"],
                created_at=record["created_at"],
            )
            for record in history
        ]

    except Exception as e:
        logger.error(f"获取导入历史失败: {e}")
        raise BusinessError(
            code="IMPORT_HISTORY_FAILED", message=f"获取导入历史失败: {str(e)}"
        )


# 获取导入状态
@router.get("/import/{import_id}/status", response_model=DataImportResponse)
@handle_errors
async def get_import_status(
    import_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """获取数据导入状态"""
    try:
        status = await etl_service.get_import_status(
            import_id=import_id, tenant_id=current_user["tenant_id"]
        )

        if not status:
            raise BusinessError(code="IMPORT_NOT_FOUND", message="导入记录不存在")

        return DataImportResponse(
            import_id=status["import_id"],
            status=status["status"],
            total_records=status["total_records"],
            successful_records=status["successful_records"],
            failed_records=status["failed_records"],
            errors=status["errors"],
            created_at=status["created_at"],
        )

    except BusinessError:
        raise
    except Exception as e:
        logger.error(f"获取导入状态失败: {e}")
        raise BusinessError(
            code="IMPORT_STATUS_FAILED", message=f"获取导入状态失败: {str(e)}"
        )


# 取消导入
@router.post("/import/{import_id}/cancel")
@handle_errors
async def cancel_import(
    import_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """取消数据导入"""
    try:
        # 取消导入
        result = await etl_service.cancel_import(
            import_id=import_id, tenant_id=current_user["tenant_id"]
        )

        return {"success": True, "message": "导入已取消"}

    except Exception as e:
        logger.error(f"取消导入失败: {e}")
        raise BusinessError(
            code="IMPORT_CANCEL_FAILED", message=f"取消导入失败: {str(e)}"
        )


# 获取支持的文件格式
@router.get("/formats", response_model=Dict[str, Any])
@handle_errors
async def get_supported_formats(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """获取支持的文件格式"""
    try:
        supported_formats = {
            "document_formats": ["excel", "csv", "json", "xml", "pdf"],
            "source_types": [
                "file_upload",
                "database_connection",
                "api_endpoint",
                "cloud_storage",
            ],
            "target_tables": [
                "fact_order",
                "fact_voice",
                "fact_cost",
                "fact_supplier",
                "fact_produce",
                "dim_vpt",
                "dim_pft",
                "dim_activity",
                "dim_media_channel",
                "dim_conv_channel",
                "dim_sku",
                "dim_customer",
                "dim_date",
                "dim_supplier",
            ],
        }

        return {
            "success": True,
            "supported_formats": supported_formats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取支持格式失败: {e}")
        raise BusinessError(
            code="FORMATS_FAILED", message=f"获取支持格式失败: {str(e)}"
        )


# 获取数据预览
@router.post("/preview", response_model=Dict[str, Any])
@handle_errors
async def preview_data(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    document_format: str = Form(...),
    preview_rows: int = Form(default=10),
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """预览数据文件"""
    try:
        # 处理文件上传
        file_content = await file.read()

        # 获取数据预览
        preview_result = await etl_service.preview_data(
            file_content=file_content,
            filename=file.filename,
            source_type=source_type,
            document_format=document_format,
            preview_rows=preview_rows,
        )

        return {
            "success": True,
            "preview_data": preview_result.get("data", []),
            "columns": preview_result.get("columns", []),
            "total_rows": preview_result.get("total_rows", 0),
            "sample_rows": preview_result.get("sample_rows", 0),
        }

    except Exception as e:
        logger.error(f"数据预览失败: {e}")
        raise BusinessError(
            code="DATA_PREVIEW_FAILED", message=f"数据预览失败: {str(e)}"
        )


# 获取数据统计
@router.get("/stats", response_model=Dict[str, Any])
@handle_errors
async def get_data_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    etl_service: DataImportETL = Depends(lambda: DataImportETL()),
):
    """获取数据统计"""
    try:
        stats = await etl_service.get_data_stats(tenant_id=current_user["tenant_id"])

        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取数据统计失败: {e}")
        raise BusinessError(
            code="DATA_STATS_FAILED", message=f"获取数据统计失败: {str(e)}"
        )
