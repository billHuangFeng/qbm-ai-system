"""
BMOS数据导入API端点 - 增强版
提供完整的数据导入、解析、验证和质量检查功能
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime
import asyncio

from ..services.enhanced_data_import import (
    DataImportService, 
    DataImportResult, 
    DataQualityReport,
    data_import_service
)
from ..api.dependencies import get_current_user
from ..models.base import User

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/data-import", tags=["数据导入"])

@router.post("/upload", response_model=DataImportResult)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传数据文件
    
    - **file**: 要上传的数据文件 (支持 CSV, Excel, JSON, Parquet)
    - **current_user**: 当前用户
    
    返回数据导入结果，包括质量分数和建议
    """
    try:
        logger.info(f"用户 {current_user.username} 上传文件: {file.filename}")
        
        # 执行数据导入
        result = await data_import_service.import_data(file)
        
        if result.success:
            logger.info(f"文件上传成功: {result.file_name}, 质量分数: {result.quality_score:.1f}")
        else:
            logger.warning(f"文件上传失败: {result.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"文件上传异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.post("/upload-batch")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    批量上传多个数据文件
    
    - **files**: 要上传的数据文件列表
    - **current_user**: 当前用户
    
    返回批量导入结果
    """
    try:
        logger.info(f"用户 {current_user.username} 批量上传 {len(files)} 个文件")
        
        results = []
        for file in files:
            try:
                result = await data_import_service.import_data(file)
                results.append(result)
            except Exception as e:
                logger.error(f"文件 {file.filename} 上传失败: {str(e)}")
                results.append(DataImportResult(
                    success=False,
                    message=f"上传失败: {str(e)}",
                    file_name=file.filename or "unknown",
                    file_size=0,
                    rows_imported=0,
                    columns_detected=[],
                    data_types={},
                    quality_score=0.0,
                    errors=[str(e)],
                    import_timestamp=datetime.now()
                ))
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量上传完成: {success_count}/{len(files)} 个文件成功")
        
        return {
            "total_files": len(files),
            "successful_uploads": success_count,
            "failed_uploads": len(files) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量上传异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量上传失败: {str(e)}")

@router.get("/history")
async def get_import_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取数据导入历史
    
    - **limit**: 返回记录数量限制
    - **current_user**: 当前用户
    
    返回导入历史记录
    """
    try:
        logger.info(f"用户 {current_user.username} 查询导入历史")
        
        history = data_import_service.get_import_history()
        
        # 限制返回数量
        if limit > 0:
            history = history[:limit]
        
        return {
            "total_records": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"获取导入历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取导入历史失败: {str(e)}")

@router.post("/validate/{file_name}")
async def validate_uploaded_file(
    file_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    验证已上传的文件
    
    - **file_name**: 文件名
    - **current_user**: 当前用户
    
    返回数据质量报告
    """
    try:
        logger.info(f"用户 {current_user.username} 验证文件: {file_name}")
        
        file_path = data_import_service.upload_dir / file_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 解析文件
        df = await data_import_service.parse_file(str(file_path))
        
        # 验证数据
        validation_result = data_import_service.validate_data(df)
        
        # 生成建议
        recommendations = data_import_service.generate_recommendations(validation_result)
        
        quality_report = DataQualityReport(
            total_rows=validation_result["total_rows"],
            total_columns=validation_result["total_columns"],
            missing_values=validation_result["missing_values"],
            duplicate_rows=validation_result["duplicate_rows"],
            data_types=validation_result["data_types"],
            quality_score=validation_result["quality_score"],
            recommendations=recommendations
        )
        
        logger.info(f"文件验证完成: {file_name}, 质量分数: {quality_report.quality_score:.1f}")
        
        return quality_report
        
    except Exception as e:
        logger.error(f"文件验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件验证失败: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_files(
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """
    清理旧文件
    
    - **days**: 保留天数
    - **current_user**: 当前用户
    
    返回清理结果
    """
    try:
        logger.info(f"用户 {current_user.username} 清理 {days} 天前的文件")
        
        cleaned_count = data_import_service.cleanup_old_files(days)
        
        logger.info(f"清理完成: {cleaned_count} 个文件")
        
        return {
            "message": f"清理完成",
            "cleaned_files": cleaned_count,
            "retention_days": days
        }
        
    except Exception as e:
        logger.error(f"清理文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理文件失败: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """
    获取支持的文件格式
    
    返回支持的文件格式列表
    """
    return {
        "supported_formats": data_import_service.supported_formats,
        "format_descriptions": {
            ".csv": "逗号分隔值文件",
            ".xlsx": "Excel 2007+ 文件",
            ".xls": "Excel 97-2003 文件",
            ".json": "JSON 数据文件",
            ".parquet": "Parquet 列式存储文件"
        }
    }

@router.post("/demo")
async def create_demo_data(
    rows: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    创建演示数据
    
    - **rows**: 数据行数
    - **current_user**: 当前用户
    
    返回演示数据信息
    """
    try:
        logger.info(f"用户 {current_user.username} 创建演示数据: {rows} 行")
        
        import pandas as pd
        import numpy as np
        
        # 创建演示数据
        demo_data = pd.DataFrame({
            'id': range(1, rows + 1),
            'name': [f'User_{i}' for i in range(1, rows + 1)],
            'age': np.random.randint(18, 65, rows),
            'salary': np.random.normal(50000, 15000, rows),
            'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], rows),
            'join_date': pd.date_range('2020-01-01', periods=rows, freq='D')
        })
        
        # 添加一些缺失值
        missing_indices = np.random.choice(rows, size=int(rows * 0.05), replace=False)
        demo_data.loc[missing_indices, 'age'] = np.nan
        
        # 保存演示数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        demo_file = data_import_service.upload_dir / f"demo_data_{timestamp}.csv"
        demo_data.to_csv(demo_file, index=False)
        
        # 验证数据
        validation_result = data_import_service.validate_data(demo_data)
        
        logger.info(f"演示数据创建完成: {demo_file.name}")
        
        return {
            "message": "演示数据创建成功",
            "file_name": demo_file.name,
            "file_path": str(demo_file),
            "rows": rows,
            "columns": list(demo_data.columns),
            "quality_score": validation_result["quality_score"],
            "warnings": validation_result["warnings"]
        }
        
    except Exception as e:
        logger.error(f"创建演示数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建演示数据失败: {str(e)}")

@router.get("/stats")
async def get_import_stats(
    current_user: User = Depends(get_current_user)
):
    """
    获取数据导入统计信息
    
    - **current_user**: 当前用户
    
    返回导入统计信息
    """
    try:
        logger.info(f"用户 {current_user.username} 查询导入统计")
        
        history = data_import_service.get_import_history()
        
        # 计算统计信息
        total_files = len(history)
        total_size = sum(h["file_size"] for h in history)
        
        # 按文件类型分组
        file_types = {}
        for h in history:
            ext = h["file_name"].split('.')[-1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # 最近7天的导入
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_imports = [
            h for h in history 
            if datetime.fromisoformat(h["created_time"]) > week_ago
        ]
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "recent_imports_7days": len(recent_imports),
            "upload_directory": str(data_import_service.upload_dir),
            "supported_formats": data_import_service.supported_formats
        }
        
    except Exception as e:
        logger.error(f"获取导入统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取导入统计失败: {str(e)}")

# 健康检查端点
@router.get("/health")
async def health_check():
    """数据导入服务健康检查"""
    try:
        # 检查上传目录
        upload_dir_exists = data_import_service.upload_dir.exists()
        
        # 检查权限
        can_write = os.access(data_import_service.upload_dir, os.W_OK)
        
        return {
            "status": "healthy" if upload_dir_exists and can_write else "unhealthy",
            "upload_directory": str(data_import_service.upload_dir),
            "directory_exists": upload_dir_exists,
            "can_write": can_write,
            "supported_formats": data_import_service.supported_formats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


