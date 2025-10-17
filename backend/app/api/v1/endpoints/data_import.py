"""
数据导入API端点
"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....database import get_db
from .auth import get_current_active_user

router = APIRouter()

@router.get("/")
def read_import_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    获取数据导入日志列表
    """
    return {"message": "数据导入功能开发中..."}
