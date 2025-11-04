"""
BMOS系统 - 文档格式识别器
作用: 自动识别6种复杂单据格式，支持格式检测和置信度计算
状态: ✅ 实施中
"""

from typing import Dict, Optional, Any, Tuple
from enum import Enum
import logging
import pandas as pd

from ...database_service import DatabaseService
from ...base import BaseService

logger = logging.getLogger(__name__)


class DocumentFormatType(Enum):
    """单据格式类型"""
    REPEATED_HEADER = "repeated_header"  # 格式1: 多行明细对应重复单据头
    FIRST_ROW_HEADER = "first_row_header"  # 格式2: 多行明细但只有第一行有单据头
    SEPARATE_HEADER_BODY = "separate_header_body"  # 格式3: 单据头和明细分离（可忽略）
    HEADER_ONLY = "header_only"  # 格式4: 只有单据头记录
    DETAIL_ONLY = "detail_only"  # 格式5: 只有明细记录（补充明细时）
    PURE_HEADER = "pure_header"  # 格式6: 纯单据头记录（无明细）


class DocumentFormatDetector(BaseService):
    """文档格式识别器"""
    
    # 单据头字段（用于识别格式）
    HEADER_FIELDS = [
        '单据号', 'document_number', 'document_id', '单号',
        '单据日期', 'document_date', 'date', '日期',
        '客户名称', 'customer_name', 'supplier_name', '供应商名称',
        '往来单位名称', 'counterparty_name',
        '不含税金额', 'ex_tax_amount', 'amount_excluding_tax',
        '税额', 'tax_amount', 'tax',
        '价税合计', 'total_amount_with_tax', 'amount_including_tax',
    ]
    
    # 明细字段（用于识别格式）
    DETAIL_FIELDS = [
        '产品名称', 'product_name', 'item_name', '物料名称',
        '数量', 'quantity', 'qty',
        '单价', 'unit_price', 'price',
        '计量单位', 'unit', 'unit_name',
    ]
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        super().__init__(db_service)
    
    async def detect_format(
        self,
        data: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[DocumentFormatType, float, Dict[str, Any]]:
        """检测单据格式
        
        Args:
            data: 数据DataFrame
            metadata: 元数据（可选）
        
        Returns:
            (格式类型, 置信度, 检测详情)
        """
        if data is None or len(data) == 0:
            raise ValueError("数据为空，无法检测格式")
        
        scores = {}
        details = {}
        
        # 检测每种格式
        for format_type in DocumentFormatType:
            score, detail = await self._detect_format_type(data, format_type, metadata)
            scores[format_type] = score
            details[format_type.value] = detail
        
        # 返回得分最高的格式
        best_format = max(scores, key=scores.get)
        best_score = scores[best_format]
        
        return best_format, best_score, details
    
    async def _detect_format_type(
        self,
        data: pd.DataFrame,
        format_type: DocumentFormatType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """检测特定格式类型"""
        
        if format_type == DocumentFormatType.REPEATED_HEADER:
            return self._detect_repeated_header(data)
        elif format_type == DocumentFormatType.FIRST_ROW_HEADER:
            return self._detect_first_row_header(data)
        elif format_type == DocumentFormatType.SEPARATE_HEADER_BODY:
            return self._detect_separate_header_body(data)
        elif format_type == DocumentFormatType.HEADER_ONLY:
            return self._detect_header_only(data)
        elif format_type == DocumentFormatType.DETAIL_ONLY:
            return self._detect_detail_only(data)
        elif format_type == DocumentFormatType.PURE_HEADER:
            return self._detect_pure_header(data)
        else:
            return 0.0, {}
    
    def _detect_repeated_header(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测重复单据头格式（格式1）"""
        # 检查是否有单据号字段
        doc_number_cols = self._find_columns(data, ['单据号', 'document_number', 'document_id', '单号'])
        
        if not doc_number_cols:
            return 0.0, {'reason': '未找到单据号字段'}
        
        doc_number_col = doc_number_cols[0]
        
        # 检查是否有重复的单据号
        unique_docs = data[doc_number_col].nunique()
        total_rows = len(data)
        
        if total_rows == 0:
            return 0.0, {'reason': '数据为空'}
        
        # 如果唯一单据数少于总行数的80%，说明有重复单据头
        duplicate_ratio = 1.0 - (unique_docs / total_rows)
        
        if duplicate_ratio > 0.2:  # 至少有20%的重复
            confidence = min(0.9, 0.7 + duplicate_ratio * 0.5)
            return confidence, {
                'unique_docs': int(unique_docs),
                'total_rows': int(total_rows),
                'duplicate_ratio': duplicate_ratio,
                'reason': f'检测到重复单据头，唯一单据数: {unique_docs}, 总行数: {total_rows}'
            }
        
        return 0.3, {'reason': '单据号重复率较低，可能是格式1但不是最佳匹配'}
    
    def _detect_first_row_header(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测第一行单据头格式（格式2）"""
        if len(data) < 2:
            return 0.0, {'reason': '数据行数不足'}
        
        # 检查第二行及之后的行是否有大量空值（单据头字段）
        header_cols = self._find_columns(
            data,
            self.HEADER_FIELDS
        )
        
        if not header_cols:
            return 0.0, {'reason': '未找到单据头字段'}
        
        # 检查第二行
        second_row = data.iloc[1]
        empty_count = 0
        total_header_cols = len(header_cols)
        
        for col in header_cols:
            if pd.isna(second_row[col]) or str(second_row[col]).strip() == '':
                empty_count += 1
        
        if total_header_cols == 0:
            return 0.0, {'reason': '未找到有效的单据头字段'}
        
        empty_ratio = empty_count / total_header_cols
        
        # 如果第二行的单据头字段有超过30%为空，可能是格式2
        if empty_ratio > 0.3:
            confidence = min(0.8, 0.5 + empty_ratio * 0.6)
            return confidence, {
                'empty_count': empty_count,
                'total_header_cols': total_header_cols,
                'empty_ratio': empty_ratio,
                'reason': f'第二行单据头字段空值比例: {empty_ratio:.2%}'
            }
        
        return 0.2, {'reason': '第二行单据头字段空值比例较低'}
    
    def _detect_separate_header_body(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测单据头和明细分离格式（格式3）"""
        # 格式3在实际业务中较少出现，可以返回较低置信度
        return 0.1, {'reason': '格式3在实际业务中较少出现，建议通过分两次导入实现'}
    
    def _detect_header_only(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测只有单据头记录格式（格式4）"""
        # 检查是否有明细字段
        detail_cols = self._find_columns(data, self.DETAIL_FIELDS)
        header_cols = self._find_columns(data, self.HEADER_FIELDS)
        
        if not header_cols:
            return 0.0, {'reason': '未找到单据头字段'}
        
        # 如果没有明细字段或明细字段全部为空，可能是格式4
        if not detail_cols:
            return 0.7, {
                'reason': '未找到明细字段，可能是格式4（只有单据头记录）',
                'header_cols_count': len(header_cols)
            }
        
        # 检查明细字段是否全部为空
        detail_empty_ratio = 0.0
        for col in detail_cols:
            empty_count = data[col].isna().sum()
            total = len(data)
            detail_empty_ratio += (empty_count / total) if total > 0 else 0
        
        detail_empty_ratio /= len(detail_cols) if detail_cols else 1
        
        if detail_empty_ratio > 0.8:  # 80%以上的明细字段为空
            return 0.6, {
                'reason': f'明细字段空值比例: {detail_empty_ratio:.2%}, 可能是格式4',
                'detail_empty_ratio': detail_empty_ratio
            }
        
        return 0.2, {'reason': '明细字段存在数据，不太可能是格式4'}
    
    def _detect_detail_only(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测只有明细记录格式（格式5）"""
        # 检查是否有单据号字段（用于关联已存在的单据头）
        doc_number_cols = self._find_columns(data, ['单据号', 'document_number', 'document_id', '单号'])
        detail_cols = self._find_columns(data, self.DETAIL_FIELDS)
        header_cols = self._find_columns(data, self.HEADER_FIELDS)
        
        if not detail_cols:
            return 0.0, {'reason': '未找到明细字段'}
        
        if not doc_number_cols:
            return 0.3, {
                'reason': '未找到单据号字段，但存在明细字段',
                'detail_cols_count': len(detail_cols)
            }
        
        # 检查单据头字段（除单据号外）是否为空
        other_header_cols = [col for col in header_cols if col not in doc_number_cols]
        if other_header_cols:
            empty_ratio = 0.0
            for col in other_header_cols:
                empty_count = data[col].isna().sum()
                total = len(data)
                empty_ratio += (empty_count / total) if total > 0 else 0
            empty_ratio /= len(other_header_cols)
            
            if empty_ratio > 0.7:  # 70%以上的其他单据头字段为空
                return 0.7, {
                    'reason': f'其他单据头字段空值比例: {empty_ratio:.2%}, 可能是格式5',
                    'empty_ratio': empty_ratio,
                    'has_document_number': True
                }
        
        # 如果有单据号字段但其他单据头字段大部分为空，可能是格式5
        if doc_number_cols and len(other_header_cols) == 0:
            return 0.5, {
                'reason': '有单据号字段，但其他单据头字段较少，可能是格式5',
                'has_document_number': True
            }
        
        return 0.3, {'reason': '格式5特征不明显'}
    
    def _detect_pure_header(self, data: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """检测纯单据头记录格式（格式6）"""
        # 检查是否有明细字段
        detail_cols = self._find_columns(data, self.DETAIL_FIELDS)
        header_cols = self._find_columns(data, self.HEADER_FIELDS)
        
        if not header_cols:
            return 0.0, {'reason': '未找到单据头字段'}
        
        # 如果没有明细字段，可能是格式6
        if not detail_cols:
            return 0.8, {
                'reason': '未找到明细字段，可能是格式6（纯单据头记录）',
                'header_cols_count': len(header_cols),
                'rows_count': len(data)
            }
        
        # 检查明细字段是否全部为空
        detail_empty_count = 0
        for col in detail_cols:
            if data[col].isna().all() or (data[col].astype(str).str.strip() == '').all():
                detail_empty_count += 1
        
        if detail_empty_count == len(detail_cols):
            return 0.75, {
                'reason': '所有明细字段为空，可能是格式6',
                'detail_cols_count': len(detail_cols),
                'detail_empty_count': detail_empty_count
            }
        
        return 0.2, {'reason': '明细字段存在数据，不太可能是格式6'}
    
    def _find_columns(
        self,
        data: pd.DataFrame,
        field_names: list,
        case_sensitive: bool = False
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
                    if col.lower() == field_lower or field_lower in col.lower() or col.lower() in field_lower:
                        if col not in matched_cols:
                            matched_cols.append(col)
        
        return matched_cols

