"""
BMOS数据导入服务 - 增强版
实现文件上传、数据解析、验证和质量检查
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
import logging
from datetime import datetime
import asyncio
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)


class DataImportResult(BaseModel):
    """数据导入结果模型"""

    success: bool
    message: str
    file_name: str
    file_size: int
    rows_imported: int
    columns_detected: List[str]
    data_types: Dict[str, str]
    quality_score: float
    warnings: List[str] = []
    errors: List[str] = []
    import_timestamp: datetime


class DataQualityReport(BaseModel):
    """数据质量报告模型"""

    total_rows: int
    total_columns: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    data_types: Dict[str, str]
    quality_score: float
    recommendations: List[str]


class DataImportService:
    """数据导入服务"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.supported_formats = [".csv", ".xlsx", ".xls", ".json", ".parquet"]

    async def upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """上传文件到服务器"""
        try:
            # 验证文件格式
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in self.supported_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件格式: {file_extension}。支持的格式: {', '.join(self.supported_formats)}",
                )

            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = self.upload_dir / safe_filename

            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            logger.info(f"文件上传成功: {safe_filename}, 大小: {len(content)} bytes")

            return {
                "success": True,
                "message": "文件上传成功",
                "file_name": safe_filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "upload_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    async def parse_file(self, file_path: str) -> pd.DataFrame:
        """解析文件为DataFrame"""
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()

            if file_extension == ".csv":
                df = pd.read_csv(file_path, encoding="utf-8")
            elif file_extension in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            elif file_extension == ".json":
                df = pd.read_json(file_path)
            elif file_extension == ".parquet":
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")

            logger.info(
                f"文件解析成功: {file_path.name}, 行数: {len(df)}, 列数: {len(df.columns)}"
            )
            return df

        except Exception as e:
            logger.error(f"文件解析失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")

    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据质量"""
        try:
            validation_result = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_rows": df.duplicated().sum(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "quality_score": 0.0,
                "warnings": [],
                "errors": [],
            }

            # 计算质量分数
            quality_score = 100.0

            # 检查缺失值
            missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            if missing_ratio > 0.1:
                validation_result["warnings"].append(
                    f"缺失值比例较高: {missing_ratio:.2%}"
                )
                quality_score -= missing_ratio * 50

            # 检查重复行
            duplicate_ratio = validation_result["duplicate_rows"] / len(df)
            if duplicate_ratio > 0.05:
                validation_result["warnings"].append(
                    f"重复行比例较高: {duplicate_ratio:.2%}"
                )
                quality_score -= duplicate_ratio * 30

            # 检查数据类型一致性
            for col in df.columns:
                if df[col].dtype == "object":
                    # 检查是否可以转换为数值
                    try:
                        pd.to_numeric(df[col], errors="raise")
                        validation_result["warnings"].append(
                            f"列 '{col}' 可能应该是数值类型"
                        )
                    except:
                        pass

            validation_result["quality_score"] = max(0, quality_score)

            logger.info(
                f"数据验证完成, 质量分数: {validation_result['quality_score']:.1f}"
            )
            return validation_result

        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")

    def generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """生成数据改进建议"""
        recommendations = []

        # 基于缺失值的建议
        missing_values = validation_result["missing_values"]
        for col, missing_count in missing_values.items():
            if missing_count > 0:
                missing_ratio = missing_count / validation_result["total_rows"]
                if missing_ratio > 0.5:
                    recommendations.append(
                        f"列 '{col}' 缺失值过多({missing_ratio:.1%})，建议删除该列"
                    )
                elif missing_ratio > 0.1:
                    recommendations.append(
                        f"列 '{col}' 有缺失值({missing_count}个)，建议填充或插值"
                    )

        # 基于重复行的建议
        if validation_result["duplicate_rows"] > 0:
            recommendations.append(
                f"发现 {validation_result['duplicate_rows']} 个重复行，建议去重"
            )

        # 基于数据类型的建议
        data_types = validation_result["data_types"]
        for col, dtype in data_types.items():
            if dtype == "object":
                recommendations.append(f"列 '{col}' 是文本类型，检查是否需要数值转换")

        return recommendations

    async def import_data(self, file: UploadFile) -> DataImportResult:
        """完整的数据导入流程"""
        try:
            # 1. 上传文件
            upload_result = await self.upload_file(file)

            # 2. 解析文件
            df = await self.parse_file(upload_result["file_path"])

            # 3. 验证数据
            validation_result = self.validate_data(df)

            # 4. 生成建议
            recommendations = self.generate_recommendations(validation_result)

            # 5. 创建导入结果
            result = DataImportResult(
                success=True,
                message="数据导入成功",
                file_name=upload_result["file_name"],
                file_size=upload_result["file_size"],
                rows_imported=validation_result["total_rows"],
                columns_detected=list(df.columns),
                data_types=validation_result["data_types"],
                quality_score=validation_result["quality_score"],
                warnings=validation_result["warnings"],
                errors=validation_result["errors"],
                import_timestamp=datetime.now(),
            )

            logger.info(
                f"数据导入完成: {result.file_name}, 质量分数: {result.quality_score:.1f}"
            )
            return result

        except Exception as e:
            logger.error(f"数据导入失败: {str(e)}")
            return DataImportResult(
                success=False,
                message=f"数据导入失败: {str(e)}",
                file_name=file.filename or "unknown",
                file_size=0,
                rows_imported=0,
                columns_detected=[],
                data_types={},
                quality_score=0.0,
                errors=[str(e)],
                import_timestamp=datetime.now(),
            )

    def get_import_history(self) -> List[Dict[str, Any]]:
        """获取导入历史"""
        try:
            history = []
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    history.append(
                        {
                            "file_name": file_path.name,
                            "file_size": stat.st_size,
                            "created_time": datetime.fromtimestamp(
                                stat.st_ctime
                            ).isoformat(),
                            "modified_time": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )

            # 按创建时间排序
            history.sort(key=lambda x: x["created_time"], reverse=True)
            return history

        except Exception as e:
            logger.error(f"获取导入历史失败: {str(e)}")
            return []

    def cleanup_old_files(self, days: int = 7) -> int:
        """清理旧文件"""
        try:
            import time

            cutoff_time = time.time() - (days * 24 * 60 * 60)
            cleaned_count = 0

            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1

            logger.info(f"清理了 {cleaned_count} 个旧文件")
            return cleaned_count

        except Exception as e:
            logger.error(f"清理旧文件失败: {str(e)}")
            return 0


# 创建全局实例
data_import_service = DataImportService()


# 示例使用函数
async def demo_data_import():
    """演示数据导入功能"""
    print("BMOS数据导入服务演示")
    print("=" * 50)

    # 创建示例数据
    sample_data = pd.DataFrame(
        {
            "id": range(1, 101),
            "name": [f"User_{i}" for i in range(1, 101)],
            "age": np.random.randint(18, 65, 100),
            "salary": np.random.normal(50000, 15000, 100),
            "department": np.random.choice(["IT", "HR", "Finance", "Marketing"], 100),
        }
    )

    # 添加一些缺失值
    sample_data.loc[5:10, "age"] = np.nan
    sample_data.loc[15:20, "salary"] = np.nan

    # 保存示例数据
    sample_file = data_import_service.upload_dir / "sample_data.csv"
    sample_data.to_csv(sample_file, index=False)

    print(f"创建示例数据文件: {sample_file}")
    print(f"数据形状: {sample_data.shape}")
    print(f"列名: {list(sample_data.columns)}")

    # 验证数据
    validation_result = data_import_service.validate_data(sample_data)
    print(f"\n数据质量报告:")
    print(f"总行数: {validation_result['total_rows']}")
    print(f"总列数: {validation_result['total_columns']}")
    print(f"质量分数: {validation_result['quality_score']:.1f}")
    print(f"缺失值: {validation_result['missing_values']}")
    print(f"重复行: {validation_result['duplicate_rows']}")

    if validation_result["warnings"]:
        print(f"\n警告:")
        for warning in validation_result["warnings"]:
            print(f"  - {warning}")

    # 生成建议
    recommendations = data_import_service.generate_recommendations(validation_result)
    if recommendations:
        print(f"\n改进建议:")
        for rec in recommendations:
            print(f"  - {rec}")

    print("\n数据导入服务演示完成!")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_data_import())
