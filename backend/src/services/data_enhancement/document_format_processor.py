"""
BMOS系统 - 文档格式处理器
作用: 处理6种复杂单据格式，包括前向填充、数据合并、虚拟记录生成
状态: ✅ 实施中
"""

from typing import Dict, Optional, Any, List
import logging
import pandas as pd
import numpy as np

from ...database_service import DatabaseService
from ...base import BaseService
from .document_format_detector import DocumentFormatType

logger = logging.getLogger(__name__)


class DocumentFormatProcessor(BaseService):
    """文档格式处理器"""

    def __init__(self, db_service: Optional[DatabaseService] = None):
        super().__init__(db_service)

    async def process_format(
        self,
        data: pd.DataFrame,
        format_type: DocumentFormatType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """处理指定格式的数据

        Args:
            data: 原始数据DataFrame
            format_type: 格式类型
            metadata: 元数据（可选）

        Returns:
            处理后的DataFrame
        """
        if data is None or len(data) == 0:
            raise ValueError("数据为空，无法处理格式")

        if format_type == DocumentFormatType.REPEATED_HEADER:
            # 格式1：直接使用，无需处理
            return data
        elif format_type == DocumentFormatType.FIRST_ROW_HEADER:
            # 格式2：前向填充单据头字段
            return await self._process_first_row_header(data, metadata)
        elif format_type == DocumentFormatType.SEPARATE_HEADER_BODY:
            # 格式3：可忽略，或通过分两次导入实现
            return data
        elif format_type == DocumentFormatType.HEADER_ONLY:
            # 格式4：创建虚拟明细记录
            return await self._process_header_only(data, metadata)
        elif format_type == DocumentFormatType.DETAIL_ONLY:
            # 格式5：需要匹配单据头ID（由调用方处理）
            return data
        elif format_type == DocumentFormatType.PURE_HEADER:
            # 格式6：直接使用，无需处理
            return data
        else:
            logger.warning(f"未知的格式类型: {format_type}")
            return data

    async def _process_first_row_header(
        self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """处理格式2：前向填充单据头字段

        特点：第一行包含单据头信息，后续明细行的单据头字段为空，需要通过前向填充补全。
        """
        if len(data) <= 1:
            return data

        processed_data = data.copy()

        # 查找单据头字段
        header_fields = self._find_header_fields(processed_data)

        if not header_fields:
            logger.warning("未找到单据头字段，无法进行前向填充")
            return processed_data

        # 查找单据号字段（用于判断是否切换到新的单据）
        doc_number_fields = self._find_columns(
            processed_data, ["单据号", "document_number", "document_id", "单号"]
        )

        # 前向填充单据头字段
        for idx in range(1, len(processed_data)):
            row = processed_data.iloc[idx]

            # 检查是否是新单据（单据号字段有值）
            is_new_document = False
            if doc_number_fields:
                doc_number_col = doc_number_fields[0]
                if (
                    not pd.isna(row[doc_number_col])
                    and str(row[doc_number_col]).strip()
                ):
                    is_new_document = True

            # 如果单据号字段有值，说明是新单据，不需要填充
            # 否则，从前一行复制单据头字段的值
            if not is_new_document:
                prev_row = processed_data.iloc[idx - 1]
                for field in header_fields:
                    # 如果当前行的字段为空，从前一行复制
                    if pd.isna(row[field]) or str(row[field]).strip() == "":
                        processed_data.at[idx, field] = prev_row[field]

        return processed_data

    async def _process_header_only(
        self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """处理格式4：创建虚拟明细记录

        特点：只有单据头信息，没有明细。为每条单据头记录创建一条虚拟明细记录。
        """
        if len(data) == 0:
            return data

        processed_data = data.copy()

        # 查找明细字段
        detail_fields = self._find_detail_fields(processed_data)

        # 为每条单据头记录创建虚拟明细记录
        expanded_rows = []

        for idx, row in processed_data.iterrows():
            new_row = row.copy()

            # 为明细字段填充默认值
            for field in detail_fields:
                if field not in new_row or pd.isna(new_row[field]):
                    # 使用默认值（可以是空值或特定标记）
                    new_row[field] = None  # 或使用特定标记如 'VIRTUAL'

            expanded_rows.append(new_row)

        # 如果创建了虚拟明细记录，返回新的DataFrame
        if expanded_rows:
            result_df = pd.DataFrame(expanded_rows)
            return result_df

        return processed_data

    def _find_header_fields(self, data: pd.DataFrame) -> List[str]:
        """查找单据头字段"""
        header_fields = [
            "单据号",
            "document_number",
            "document_id",
            "单号",
            "单据日期",
            "document_date",
            "date",
            "日期",
            "客户名称",
            "customer_name",
            "supplier_name",
            "供应商名称",
            "往来单位名称",
            "counterparty_name",
            "不含税金额",
            "ex_tax_amount",
            "amount_excluding_tax",
            "税额",
            "tax_amount",
            "tax",
            "价税合计",
            "total_amount_with_tax",
            "amount_including_tax",
        ]

        return self._find_columns(data, header_fields)

    def _find_detail_fields(self, data: pd.DataFrame) -> List[str]:
        """查找明细字段"""
        detail_fields = [
            "产品名称",
            "product_name",
            "item_name",
            "物料名称",
            "数量",
            "quantity",
            "qty",
            "单价",
            "unit_price",
            "price",
            "计量单位",
            "unit",
            "unit_name",
            "不含税金额",
            "ex_tax_amount",
            "amount_excluding_tax",
            "税额",
            "tax_amount",
            "tax",
            "价税合计",
            "total_amount_with_tax",
            "amount_including_tax",
        ]

        return self._find_columns(data, detail_fields)

    def _find_columns(
        self, data: pd.DataFrame, field_names: list, case_sensitive: bool = False
    ) -> list:
        """查找匹配的列名"""
        if data is None or len(data.columns) == 0:
            return []

        matched_cols = []
        data_cols = data.columns.tolist()

        for field_name in field_names:
            if case_sensitive:
                if field_name in data_cols:
                    matched_cols.append(field_name)
            else:
                field_lower = field_name.lower()
                for col in data_cols:
                    if (
                        col.lower() == field_lower
                        or field_lower in col.lower()
                        or col.lower() in field_lower
                    ):
                        if col not in matched_cols:
                            matched_cols.append(col)

        return matched_cols
