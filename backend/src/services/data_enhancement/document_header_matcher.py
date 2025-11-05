"""
BMOS系统 - 单据头ID匹配器
作用: 通过单据号匹配系统中已存在的单据头记录ID（格式5补充明细时使用）
状态: ✅ 实施中
"""

from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
import logging
import pandas as pd

from ...database_service import DatabaseService
from ...base import BaseService

logger = logging.getLogger(__name__)


@dataclass
class DocumentHeaderMatchResult:
    """单据头匹配结果"""

    document_number: str
    header_id: Optional[str] = None
    confidence: float = 0.0
    found: bool = False
    header_info: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class DocumentHeaderMatcher(BaseService):
    """单据头ID匹配器"""

    def __init__(self, db_service: Optional[DatabaseService] = None):
        super().__init__(db_service)

    async def match_document_headers(
        self,
        document_numbers: List[str],
        document_type: Optional[str] = None,
        table_name: str = "doc_purchase_order_header",  # 默认表名，可根据单据类型调整
    ) -> List[DocumentHeaderMatchResult]:
        """批量匹配单据头ID

        Args:
            document_numbers: 单据号列表
            document_type: 单据类型（可选）
            table_name: 单据头表名（默认：doc_purchase_order_header）

        Returns:
            匹配结果列表
        """
        if not document_numbers:
            return []

        if not self.db_service:
            logger.warning("数据库服务未初始化，无法匹配单据头ID")
            return [
                DocumentHeaderMatchResult(
                    document_number=doc_num, found=False, message="数据库服务未初始化"
                )
                for doc_num in document_numbers
            ]

        results = []

        try:
            # 构建查询SQL
            # 根据单据类型选择不同的表
            table_name = self._get_table_name(document_type, table_name)

            # 查询匹配的单据头记录
            query_sql = f"""
                SELECT 
                    id,
                    document_number,
                    document_date,
                    customer_name,
                    supplier_name,
                    counterparty_name,
                    total_amount_with_tax,
                    created_at
                FROM {table_name}
                WHERE document_number = ANY(:document_numbers)
                  AND is_deleted = FALSE
            """

            params = {"document_numbers": document_numbers}

            matched_records = await self.db_service.fetch_all(query_sql, params)

            # 构建匹配字典
            match_dict = {}
            for record in matched_records:
                doc_num = record.get("document_number")
                if doc_num:
                    match_dict[doc_num] = record

            # 为每个单据号生成匹配结果
            for doc_num in document_numbers:
                if doc_num in match_dict:
                    record = match_dict[doc_num]
                    results.append(
                        DocumentHeaderMatchResult(
                            document_number=doc_num,
                            header_id=str(record["id"]),
                            confidence=1.0,  # 精确匹配，置信度为1.0
                            found=True,
                            header_info={
                                "id": str(record["id"]),
                                "document_number": record.get("document_number"),
                                "document_date": record.get("document_date"),
                                "customer_name": record.get("customer_name"),
                                "supplier_name": record.get("supplier_name"),
                                "counterparty_name": record.get("counterparty_name"),
                                "total_amount_with_tax": record.get(
                                    "total_amount_with_tax"
                                ),
                                "created_at": record.get("created_at"),
                            },
                            message=f"找到匹配的单据头记录（ID: {record['id']}）",
                        )
                    )
                else:
                    results.append(
                        DocumentHeaderMatchResult(
                            document_number=doc_num,
                            found=False,
                            confidence=0.0,
                            message=f"系统中未找到单据号 {doc_num} 的单据头记录",
                        )
                    )

        except Exception as e:
            logger.error(f"匹配单据头ID失败: {e}")
            # 返回所有失败的结果
            results = [
                DocumentHeaderMatchResult(
                    document_number=doc_num, found=False, message=f"匹配失败: {str(e)}"
                )
                for doc_num in document_numbers
            ]

        return results

    async def match_single_document_header(
        self,
        document_number: str,
        document_type: Optional[str] = None,
        table_name: str = "doc_purchase_order_header",
    ) -> DocumentHeaderMatchResult:
        """匹配单个单据头ID

        Args:
            document_number: 单据号
            document_type: 单据类型（可选）
            table_name: 单据头表名（默认：doc_purchase_order_header）

        Returns:
            匹配结果
        """
        results = await self.match_document_headers(
            [document_number], document_type, table_name
        )

        if results:
            return results[0]
        else:
            return DocumentHeaderMatchResult(
                document_number=document_number, found=False, message="未找到匹配结果"
            )

    def _get_table_name(self, document_type: Optional[str], default_table: str) -> str:
        """根据单据类型获取表名"""
        if not document_type:
            return default_table

        # 单据类型到表名的映射
        table_mapping = {
            "purchase_order": "doc_purchase_order_header",
            "sales_order": "doc_sales_order_header",
            "expense": "doc_expense_header",
            "asset": "doc_asset_header",
            "order": "doc_order_header",
            "feedback": "doc_feedback_header",
        }

        return table_mapping.get(document_type.lower(), default_table)

    async def create_document_header_if_not_exists(
        self,
        document_number: str,
        header_data: Dict[str, Any],
        document_type: Optional[str] = None,
        table_name: str = "doc_purchase_order_header",
    ) -> Tuple[Optional[str], bool]:
        """如果不存在则创建单据头记录

        Args:
            document_number: 单据号
            header_data: 单据头数据
            document_type: 单据类型（可选）
            table_name: 单据头表名（默认：doc_purchase_order_header）

        Returns:
            (header_id, is_created)
            - header_id: 单据头ID（如果创建成功或已存在）
            - is_created: 是否新创建（True=新创建，False=已存在）
        """
        if not self.db_service:
            raise ValueError("数据库服务未初始化")

        # 先尝试匹配
        match_result = await self.match_single_document_header(
            document_number, document_type, table_name
        )

        if match_result.found:
            # 已存在，返回现有ID
            return match_result.header_id, False

        # 不存在，创建新记录
        try:
            table_name = self._get_table_name(document_type, table_name)

            # 构建插入SQL（根据实际表结构调整）
            insert_sql = f"""
                INSERT INTO {table_name} (
                    document_number,
                    document_date,
                    customer_name,
                    supplier_name,
                    counterparty_name,
                    total_amount_with_tax,
                    created_at,
                    updated_at
                ) VALUES (
                    :document_number,
                    :document_date,
                    :customer_name,
                    :supplier_name,
                    :counterparty_name,
                    :total_amount_with_tax,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                ) RETURNING id
            """

            params = {
                "document_number": document_number,
                "document_date": header_data.get("document_date"),
                "customer_name": header_data.get("customer_name"),
                "supplier_name": header_data.get("supplier_name"),
                "counterparty_name": header_data.get("counterparty_name"),
                "total_amount_with_tax": header_data.get("total_amount_with_tax"),
            }

            result = await self.db_service.fetch_one(insert_sql, params)

            if result and "id" in result:
                return str(result["id"]), True
            else:
                raise ValueError("创建单据头记录失败：未返回ID")

        except Exception as e:
            logger.error(f"创建单据头记录失败: {e}")
            raise
