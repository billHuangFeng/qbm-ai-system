"""
数据导入API端点
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import json

from ....database import get_db
from .auth import get_current_active_user
from ....services.data_import_service import DataImportService

router = APIRouter()
data_import_service = DataImportService()

@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    分析上传的文件
    """
    try:
        result = await data_import_service.analyze_file(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    table_type: str = Form(...),
    mapping_config: str = Form(...),
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    导入数据
    """
    try:
        # 解析映射配置
        mapping_config_dict = json.loads(mapping_config)
        
        result = await data_import_service.import_data(file, table_type, mapping_config_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
def get_supported_formats(
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    获取支持的文件格式
    """
    return {
        "supported_formats": data_import_service.supported_formats,
        "table_mappings": list(data_import_service.table_mappings.keys())
    }

@router.get("/table-schema/{table_type}")
def get_table_schema(
    table_type: str,
    current_user = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    获取表结构信息
    """
    if table_type not in data_import_service.table_mappings:
        raise HTTPException(status_code=404, detail="不支持的表类型")
    
    return data_import_service.table_mappings[table_type]

@router.get("/")
def read_import_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    获取数据导入日志列表
    """
    return {"message": "数据导入功能已实现，请使用 /analyze 和 /import 端点"}
