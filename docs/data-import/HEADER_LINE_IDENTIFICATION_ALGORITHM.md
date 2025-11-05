# 头行识别算法文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P0 - 必需文档**

**文档目的**: 提供可转换为TypeScript的头行识别算法，供Lovable在Edge Functions中实现

---

## 📋 目录

1. [算法概述](#1-算法概述)
2. [Python实现代码](#2-python实现代码)
3. [算法说明](#3-算法说明)
4. [测试用例](#4-测试用例)
5. [TypeScript转换建议](#5-typescript转换建议)

---

## 1. 算法概述

### 1.1 核心功能

头行识别算法的目标是从Excel/CSV数据中自动识别：
- **Header行**: 单据头记录（包含单据号、客户/供应商、日期等信息）
- **Line行**: 单据明细记录（包含SKU、数量、单价等信息）
- **关联关系**: Line行与Header行的归属关系

### 1.2 输入输出

**输入**:
- `df`: pandas DataFrame，原始数据
- `doc_type`: 单据类型 (SO/SH/SI/PO/RC/PI)
- `field_mappings`: 字段映射字典（源字段 → 目标字段）

**输出**:
```python
{
    "headers": [
        {
            "row_index": 0,
            "data": {...},
            "line_start": 1,
            "line_end": 3
        }
    ],
    "lines": [
        {
            "row_index": 1,
            "header_index": 0,
            "data": {...}
        }
    ]
}
```

---

## 2. Python实现代码

### 2.1 完整实现

```python
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from enum import Enum

class HeaderLineIdentifier:
    """
    单据头行识别器
    
    功能:
    1. 识别Header行和Line行
    2. 建立Header和Line的关联关系
    3. 处理格式1（重复Header）和格式2（前向填充）
    """
    
    def __init__(self, doc_type: str):
        """
        Args:
            doc_type: 单据类型 (SO/SH/SI/PO/RC/PI)
        """
        self.doc_type = doc_type
        
        # Header字段定义（根据单据类型）
        self.header_fields = self._get_header_fields(doc_type)
        
        # Line字段定义
        self.line_fields = [
            'sku_code', 'sku_name', 'product_code', 'product_name',
            'quantity', 'unit_price', 'line_amount', 'line_no'
        ]
        
        # 单据号字段（用于关联）
        self.document_number_fields = {
            'SO': 'order_number',
            'SH': 'shipment_number',
            'SI': 'invoice_number',
            'PO': 'po_number',
            'RC': 'receipt_number',
            'PI': 'invoice_number'
        }
    
    def identify(self, df: pd.DataFrame, field_mappings: Dict[str, str] = None) -> Dict[str, List[Dict]]:
        """
        识别DataFrame中的头行结构
        
        Args:
            df: 原始数据
            field_mappings: 字段映射字典（源字段 → 目标字段）
        
        Returns:
            {
                "headers": [
                    {
                        "row_index": 0,
                        "data": {...},
                        "line_start": 1,
                        "line_end": 3
                    }
                ],
                "lines": [
                    {
                        "row_index": 1,
                        "header_index": 0,
                        "data": {...}
                    }
                ]
            }
        """
        # 应用字段映射
        if field_mappings:
            df = self._apply_field_mappings(df, field_mappings)
        
        # 检测格式类型
        format_type = self._detect_format_type(df)
        
        # 根据格式类型识别头行
        if format_type == 'repeated_header':
            return self._identify_repeated_header_format(df)
        elif format_type == 'first_row_header':
            return self._identify_first_row_header_format(df)
        else:
            # 默认使用重复Header格式
            return self._identify_repeated_header_format(df)
    
    def _get_header_fields(self, doc_type: str) -> List[str]:
        """获取Header字段列表"""
        base_fields = ['document_number', 'document_date', 'remark']
        
        if doc_type in ['SO', 'SH', 'SI']:
            # 销售流程：客户相关
            return base_fields + ['customer_id', 'customer_name', 'customer_code', 'channel_id']
        elif doc_type in ['PO', 'RC', 'PI']:
            # 采购流程：供应商相关
            return base_fields + ['supplier_id', 'supplier_name', 'supplier_code']
        else:
            return base_fields
    
    def _apply_field_mappings(self, df: pd.DataFrame, mappings: Dict[str, str]) -> pd.DataFrame:
        """应用字段映射"""
        df_mapped = df.copy()
        
        for source_field, target_field in mappings.items():
            if source_field in df_mapped.columns:
                df_mapped[target_field] = df_mapped[source_field]
        
        return df_mapped
    
    def _detect_format_type(self, df: pd.DataFrame) -> str:
        """
        检测格式类型
        
        返回:
            'repeated_header': 格式1，每行重复Header
            'first_row_header': 格式2，第一行Header，后续行前向填充
        """
        if len(df) <= 1:
            return 'repeated_header'
        
        # 获取单据号字段
        doc_number_field = self.document_number_fields.get(self.doc_type, 'document_number')
        
        if doc_number_field not in df.columns:
            return 'repeated_header'
        
        # 检查第二行及以后的行，单据号字段是否为空
        second_row_onwards = df.iloc[1:]
        null_rate = second_row_onwards[doc_number_field].isna().sum() / len(second_row_onwards)
        
        # 如果超过50%的行单据号为空，判断为格式2（前向填充）
        if null_rate > 0.5:
            return 'first_row_header'
        else:
            return 'repeated_header'
    
    def _identify_repeated_header_format(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        识别格式1：重复Header格式
        
        特点：每行都包含完整的Header信息和Line信息
        """
        headers = []
        lines = []
        
        # 获取单据号字段
        doc_number_field = self.document_number_fields.get(self.doc_type, 'document_number')
        
        # 按单据号分组
        if doc_number_field in df.columns:
            # 获取所有非空的单据号
            df_with_doc = df[df[doc_number_field].notna()].copy()
            
            if len(df_with_doc) == 0:
                # 如果没有单据号，每行都作为独立的Header
                for idx, row in df.iterrows():
                    if self._is_header_row(row):
                        headers.append({
                            'row_index': idx,
                            'data': row.to_dict(),
                            'line_start': idx,
                            'line_end': idx
                        })
                        lines.append({
                            'row_index': idx,
                            'header_index': len(headers) - 1,
                            'data': row.to_dict()
                        })
            else:
                # 按单据号分组
                grouped = df_with_doc.groupby(doc_number_field)
                
                for doc_number, group in grouped:
                    # 每组的第一行作为Header
                    first_row = group.iloc[0]
                    header_idx = first_row.name
                    
                    headers.append({
                        'row_index': header_idx,
                        'data': first_row.to_dict(),
                        'line_start': group.index.min(),
                        'line_end': group.index.max()
                    })
                    
                    # 该组的所有行都作为Line
                    for idx, row in group.iterrows():
                        lines.append({
                            'row_index': idx,
                            'header_index': len(headers) - 1,
                            'data': row.to_dict()
                        })
        else:
            # 没有单据号字段，每行都作为独立的Header+Line
            for idx, row in df.iterrows():
                if self._is_header_row(row):
                    headers.append({
                        'row_index': idx,
                        'data': row.to_dict(),
                        'line_start': idx,
                        'line_end': idx
                    })
                    lines.append({
                        'row_index': idx,
                        'header_index': len(headers) - 1,
                        'data': row.to_dict()
                    })
        
        return {
            'headers': headers,
            'lines': lines
        }
    
    def _identify_first_row_header_format(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        识别格式2：第一行Header格式
        
        特点：第一行包含Header信息，后续行的Header字段为空，需要前向填充
        """
        headers = []
        lines = []
        
        # 获取单据号字段
        doc_number_field = self.document_number_fields.get(self.doc_type, 'document_number')
        
        # 前向填充Header字段
        df_filled = df.copy()
        for field in self.header_fields:
            if field in df_filled.columns:
                df_filled[field] = df_filled[field].fillna(method='ffill')
        
        # 按单据号分组（前向填充后）
        if doc_number_field in df_filled.columns:
            # 识别Header行（单据号变化的行）
            df_filled['is_new_header'] = df_filled[doc_number_field] != df_filled[doc_number_field].shift(1)
            header_rows = df_filled[df_filled['is_new_header'] == True]
            
            for idx, header_row in header_rows.iterrows():
                # 获取该Header对应的所有Line行
                doc_number = header_row[doc_number_field]
                line_rows = df_filled[df_filled[doc_number_field] == doc_number]
                
                headers.append({
                    'row_index': idx,
                    'data': header_row[self.header_fields].to_dict(),
                    'line_start': line_rows.index.min(),
                    'line_end': line_rows.index.max()
                })
                
                # 添加Line行
                for line_idx, line_row in line_rows.iterrows():
                    lines.append({
                        'row_index': line_idx,
                        'header_index': len(headers) - 1,
                        'data': line_row[self.line_fields].to_dict()
                    })
        else:
            # 没有单据号字段，第一行作为Header，其余行作为Line
            if len(df_filled) > 0:
                first_row = df_filled.iloc[0]
                headers.append({
                    'row_index': 0,
                    'data': first_row[self.header_fields].to_dict(),
                    'line_start': 0,
                    'line_end': len(df_filled) - 1
                })
                
                for idx, row in df_filled.iterrows():
                    lines.append({
                        'row_index': idx,
                        'header_index': 0,
                        'data': row[self.line_fields].to_dict()
                    })
        
        return {
            'headers': headers,
            'lines': lines
        }
    
    def _is_header_row(self, row: pd.Series) -> bool:
        """
        判断是否为Header行
        
        判断依据:
        1. 包含单据号字段且不为空
        2. 包含客户/供应商字段且不为空
        3. 包含日期字段且不为空
        4. 不包含SKU相关字段（或SKU字段为空）
        """
        # 检查必需的Header字段
        required_fields = []
        if self.doc_type in ['SO', 'SH', 'SI']:
            required_fields = ['customer_name', 'customer_code']
        elif self.doc_type in ['PO', 'RC', 'PI']:
            required_fields = ['supplier_name', 'supplier_code']
        
        has_required_fields = any(
            field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
            for field in required_fields
        )
        
        # 检查日期字段
        date_fields = ['document_date', 'order_date', 'shipment_date', 'invoice_date', 'po_date', 'receipt_date']
        has_date_field = any(
            field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
            for field in date_fields
        )
        
        # 检查是否包含SKU字段（Line特征）
        line_indicators = ['sku_code', 'sku_name', 'product_code', 'product_name']
        has_line_fields = any(
            field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
            for field in line_indicators
        )
        
        # Header行：有必需字段 且 有日期字段 且 没有Line字段
        return has_required_fields and has_date_field and not has_line_fields
    
    def _is_line_row(self, row: pd.Series) -> bool:
        """
        判断是否为Line行
        
        判断依据:
        1. 包含SKU相关字段且不为空
        2. 包含数量字段且不为空
        3. 包含单价字段（可选，可能为空）
        """
        # 检查SKU字段
        line_indicators = ['sku_code', 'sku_name', 'product_code', 'product_name']
        has_sku_field = any(
            field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
            for field in line_indicators
        )
        
        # 检查数量字段
        has_quantity = (
            'quantity' in row.index and 
            pd.notna(row.get('quantity')) and 
            str(row.get('quantity')).strip() != ''
        )
        
        # Line行：有SKU字段 且 有数量字段
        return has_sku_field and has_quantity
    
    def _find_parent_header(self, line_index: int, headers: List[Dict], format_type: str) -> Optional[int]:
        """
        查找Line行对应的Header
        
        Args:
            line_index: Line行的索引
            headers: Header行列表（已按索引排序）
            format_type: 格式类型
        
        Returns:
            Header行的索引，如果未找到返回None
        """
        if format_type == 'repeated_header':
            # 格式1：直接通过单据号匹配（已在识别时确定）
            for header in headers:
                if header['line_start'] <= line_index <= header['line_end']:
                    return headers.index(header)
        elif format_type == 'first_row_header':
            # 格式2：向上查找最近的Header
            for header in reversed(headers):
                if header['row_index'] < line_index:
                    return headers.index(header)
        
        return None
```

---

## 3. 算法说明

### 3.1 算法核心思路

1. **格式检测**: 通过分析单据号字段的空值率，判断是格式1（重复Header）还是格式2（前向填充）

2. **Header识别**: 
   - 检查是否包含必需的Header字段（客户/供应商、日期等）
   - 检查是否不包含Line字段（SKU、数量等）

3. **Line识别**:
   - 检查是否包含SKU字段和数量字段
   - 通过单据号或位置关系关联到Header

4. **关联建立**:
   - 格式1：通过单据号分组，每组的第一行作为Header，其余行作为Line
   - 格式2：前向填充Header字段，然后按填充后的单据号分组

### 3.2 关键特征

**Header行特征**:
- 包含单据号字段（如`order_number`、`shipment_number`等）
- 包含客户/供应商字段（`customer_name`、`supplier_name`等）
- 包含日期字段（`order_date`、`shipment_date`等）
- 通常不包含SKU相关字段（或SKU字段为空）

**Line行特征**:
- 包含SKU相关字段（`sku_code`、`sku_name`等）
- 包含数量字段（`quantity`）
- 包含单价字段（`unit_price`，可能为空）
- 单据号字段可能为空（格式2：前向填充）

### 3.3 性能考虑

- **时间复杂度**: O(n)，其中n是数据行数
  - 格式检测: O(n)
  - Header识别: O(n)
  - Line识别: O(n)
  - 关联建立: O(n log n)（如果使用分组）

- **空间复杂度**: O(n)
  - 存储Header和Line数据结构

- **适用数据规模**: 
  - 建议 < 10,000行（单次处理）
  - 超过10,000行建议分批处理

---

## 4. 测试用例

### 4.1 测试用例1: 标准格式（格式1）

```python
import pandas as pd

# 测试数据：格式1（重复Header）
test_data_1 = pd.DataFrame([
    {
        'order_number': 'SO001',
        'customer_name': '客户A',
        'order_date': '2025-01-20',
        'sku_code': 'P001',
        'sku_name': '产品1',
        'quantity': 10,
        'unit_price': 100
    },
    {
        'order_number': 'SO001',
        'customer_name': '客户A',
        'order_date': '2025-01-20',
        'sku_code': 'P002',
        'sku_name': '产品2',
        'quantity': 5,
        'unit_price': 200
    },
    {
        'order_number': 'SO002',
        'customer_name': '客户B',
        'order_date': '2025-01-21',
        'sku_code': 'P003',
        'sku_name': '产品3',
        'quantity': 20,
        'unit_price': 50
    }
])

identifier = HeaderLineIdentifier('SO')
result = identifier.identify(test_data_1)

# 预期结果
expected_result = {
    'headers': [
        {
            'row_index': 0,
            'data': {...},
            'line_start': 0,
            'line_end': 1
        },
        {
            'row_index': 2,
            'data': {...},
            'line_start': 2,
            'line_end': 2
        }
    ],
    'lines': [
        {'row_index': 0, 'header_index': 0, 'data': {...}},
        {'row_index': 1, 'header_index': 0, 'data': {...}},
        {'row_index': 2, 'header_index': 1, 'data': {...}}
    ]
}

assert len(result['headers']) == 2
assert len(result['lines']) == 3
assert result['headers'][0]['line_start'] == 0
assert result['headers'][0]['line_end'] == 1
```

### 4.2 测试用例2: 复杂格式（格式2）

```python
# 测试数据：格式2（前向填充）
test_data_2 = pd.DataFrame([
    {
        'order_number': 'SO001',
        'customer_name': '客户A',
        'order_date': '2025-01-20',
        'sku_code': 'P001',
        'sku_name': '产品1',
        'quantity': 10,
        'unit_price': 100
    },
    {
        'order_number': None,  # 空值，需要前向填充
        'customer_name': None,
        'order_date': None,
        'sku_code': 'P002',
        'sku_name': '产品2',
        'quantity': 5,
        'unit_price': 200
    },
    {
        'order_number': 'SO002',  # 新单据
        'customer_name': '客户B',
        'order_date': '2025-01-21',
        'sku_code': 'P003',
        'sku_name': '产品3',
        'quantity': 20,
        'unit_price': 50
    }
])

result = identifier.identify(test_data_2)

# 预期结果
assert len(result['headers']) == 2
assert len(result['lines']) == 3
assert result['lines'][1]['header_index'] == 0  # 第二行应该关联到第一个Header
```

### 4.3 测试用例3: 边界情况

```python
# 测试用例3: 空数据
test_data_3 = pd.DataFrame()
result = identifier.identify(test_data_3)
assert len(result['headers']) == 0
assert len(result['lines']) == 0

# 测试用例4: 只有一行
test_data_4 = pd.DataFrame([{
    'order_number': 'SO001',
    'customer_name': '客户A',
    'order_date': '2025-01-20',
    'sku_code': 'P001',
    'quantity': 10
}])
result = identifier.identify(test_data_4)
assert len(result['headers']) == 1
assert len(result['lines']) == 1
```

---

## 5. TypeScript转换建议

### 5.1 推荐库

**pandas替代**:
- 使用原生`Array<Record<string, any>>`表示数据
- 使用`Array.map()`、`Array.filter()`、`Array.reduce()`等原生方法

**numpy替代**:
- 使用原生`Math`操作
- 使用`Array.reduce()`计算统计值

### 5.2 关键函数映射

| Python | TypeScript |
|--------|-----------|
| `df.iloc[i]` | `data[i]` |
| `df[column].isna()` | `value === null \|\| value === undefined \|\| value === ''` |
| `pd.Series.apply()` | `array.map()` |
| `df.groupby()` | `Array.reduce()` 或使用 `Map` |
| `df.fillna(method='ffill')` | 手动实现前向填充循环 |

### 5.3 TypeScript实现示例

```typescript
interface HeaderRow {
  rowIndex: number;
  data: Record<string, any>;
  lineStart: number;
  lineEnd: number;
}

interface LineRow {
  rowIndex: number;
  headerIndex: number;
  data: Record<string, any>;
}

interface IdentificationResult {
  headers: HeaderRow[];
  lines: LineRow[];
}

class HeaderLineIdentifier {
  private docType: string;
  private headerFields: string[];
  private lineFields: string[];
  
  constructor(docType: string) {
    this.docType = docType;
    this.headerFields = this.getHeaderFields(docType);
    this.lineFields = [
      'sku_code', 'sku_name', 'product_code', 'product_name',
      'quantity', 'unit_price', 'line_amount', 'line_no'
    ];
  }
  
  identify(
    data: Array<Record<string, any>>,
    fieldMappings?: Record<string, string>
  ): IdentificationResult {
    // 应用字段映射
    let processedData = data;
    if (fieldMappings) {
      processedData = this.applyFieldMappings(data, fieldMappings);
    }
    
    // 检测格式类型
    const formatType = this.detectFormatType(processedData);
    
    // 根据格式类型识别头行
    if (formatType === 'repeated_header') {
      return this.identifyRepeatedHeaderFormat(processedData);
    } else {
      return this.identifyFirstRowHeaderFormat(processedData);
    }
  }
  
  private detectFormatType(data: Array<Record<string, any>>): string {
    if (data.length <= 1) {
      return 'repeated_header';
    }
    
    const docNumberField = this.getDocumentNumberField();
    if (!docNumberField) {
      return 'repeated_header';
    }
    
    // 检查第二行及以后的行，单据号字段是否为空
    const secondRowOnwards = data.slice(1);
    const nullCount = secondRowOnwards.filter(row => 
      !row[docNumberField] || row[docNumberField] === ''
    ).length;
    
    const nullRate = nullCount / secondRowOnwards.length;
    
    // 如果超过50%的行单据号为空，判断为格式2
    return nullRate > 0.5 ? 'first_row_header' : 'repeated_header';
  }
  
  private identifyRepeatedHeaderFormat(
    data: Array<Record<string, any>>
  ): IdentificationResult {
    const headers: HeaderRow[] = [];
    const lines: LineRow[] = [];
    
    const docNumberField = this.getDocumentNumberField();
    
    if (docNumberField) {
      // 按单据号分组
      const grouped = new Map<string, number[]>();
      
      data.forEach((row, index) => {
        const docNumber = row[docNumberField];
        if (docNumber) {
          if (!grouped.has(docNumber)) {
            grouped.set(docNumber, []);
          }
          grouped.get(docNumber)!.push(index);
        }
      });
      
      // 每组的第一行作为Header
      let headerIndex = 0;
      grouped.forEach((indices, docNumber) => {
        const firstIndex = indices[0];
        const headerRow = data[firstIndex];
        
        headers.push({
          rowIndex: firstIndex,
          data: headerRow,
          lineStart: Math.min(...indices),
          lineEnd: Math.max(...indices)
        });
        
        // 该组的所有行都作为Line
        indices.forEach(lineIndex => {
          lines.push({
            rowIndex: lineIndex,
            headerIndex: headerIndex,
            data: data[lineIndex]
          });
        });
        
        headerIndex++;
      });
    } else {
      // 没有单据号字段，每行都作为独立的Header+Line
      data.forEach((row, index) => {
        if (this.isHeaderRow(row)) {
          headers.push({
            rowIndex: index,
            data: row,
            lineStart: index,
            lineEnd: index
          });
          
          lines.push({
            rowIndex: index,
            headerIndex: headers.length - 1,
            data: row
          });
        }
      });
    }
    
    return { headers, lines };
  }
  
  private identifyFirstRowHeaderFormat(
    data: Array<Record<string, any>>
  ): IdentificationResult {
    const headers: HeaderRow[] = [];
    const lines: LineRow[] = [];
    
    // 前向填充Header字段
    const filledData = this.forwardFill(data, this.headerFields);
    
    const docNumberField = this.getDocumentNumberField();
    
    if (docNumberField) {
      // 识别Header行（单据号变化的行）
      const headerIndices: number[] = [];
      filledData.forEach((row, index) => {
        if (index === 0 || row[docNumberField] !== filledData[index - 1][docNumberField]) {
          headerIndices.push(index);
        }
      });
      
      // 为每个Header创建记录
      headerIndices.forEach((headerIndex, idx) => {
        const docNumber = filledData[headerIndex][docNumberField];
        const headerRow = filledData[headerIndex];
        
        // 找到该Header对应的所有Line行
        const lineIndices: number[] = [];
        const nextHeaderIndex = headerIndices[idx + 1] || filledData.length;
        
        for (let i = headerIndex; i < nextHeaderIndex; i++) {
          if (filledData[i][docNumberField] === docNumber) {
            lineIndices.push(i);
          }
        }
        
        headers.push({
          rowIndex: headerIndex,
          data: this.extractHeaderData(headerRow),
          lineStart: Math.min(...lineIndices),
          lineEnd: Math.max(...lineIndices)
        });
        
        // 添加Line行
        lineIndices.forEach(lineIndex => {
          lines.push({
            rowIndex: lineIndex,
            headerIndex: idx,
            data: this.extractLineData(filledData[lineIndex])
          });
        });
      });
    }
    
    return { headers, lines };
  }
  
  private forwardFill(
    data: Array<Record<string, any>>,
    fields: string[]
  ): Array<Record<string, any>> {
    const filled = data.map(row => ({ ...row }));
    
    fields.forEach(field => {
      let lastValue: any = null;
      
      filled.forEach((row, index) => {
        if (row[field] && row[field] !== '') {
          lastValue = row[field];
        } else if (lastValue !== null) {
          row[field] = lastValue;
        }
      });
    });
    
    return filled;
  }
  
  private isHeaderRow(row: Record<string, any>): boolean {
    // 检查必需的Header字段
    const requiredFields = this.getRequiredHeaderFields();
    const hasRequiredFields = requiredFields.some(field => 
      row[field] && row[field] !== ''
    );
    
    // 检查日期字段
    const dateFields = ['document_date', 'order_date', 'shipment_date', 
                        'invoice_date', 'po_date', 'receipt_date'];
    const hasDateField = dateFields.some(field => 
      row[field] && row[field] !== ''
    );
    
    // 检查是否包含SKU字段（Line特征）
    const lineIndicators = ['sku_code', 'sku_name', 'product_code', 'product_name'];
    const hasLineFields = lineIndicators.some(field => 
      row[field] && row[field] !== ''
    );
    
    return hasRequiredFields && hasDateField && !hasLineFields;
  }
  
  private getHeaderFields(docType: string): string[] {
    const baseFields = ['document_number', 'document_date', 'remark'];
    
    if (['SO', 'SH', 'SI'].includes(docType)) {
      return [...baseFields, 'customer_id', 'customer_name', 'customer_code', 'channel_id'];
    } else if (['PO', 'RC', 'PI'].includes(docType)) {
      return [...baseFields, 'supplier_id', 'supplier_name', 'supplier_code'];
    }
    
    return baseFields;
  }
  
  private getDocumentNumberField(): string | null {
    const fieldMap: Record<string, string> = {
      'SO': 'order_number',
      'SH': 'shipment_number',
      'SI': 'invoice_number',
      'PO': 'po_number',
      'RC': 'receipt_number',
      'PI': 'invoice_number'
    };
    
    return fieldMap[this.docType] || null;
  }
  
  private getRequiredHeaderFields(): string[] {
    if (['SO', 'SH', 'SI'].includes(this.docType)) {
      return ['customer_name', 'customer_code'];
    } else if (['PO', 'RC', 'PI'].includes(this.docType)) {
      return ['supplier_name', 'supplier_code'];
    }
    
    return [];
  }
  
  private extractHeaderData(row: Record<string, any>): Record<string, any> {
    const headerData: Record<string, any> = {};
    this.headerFields.forEach(field => {
      if (row[field] !== undefined) {
        headerData[field] = row[field];
      }
    });
    return headerData;
  }
  
  private extractLineData(row: Record<string, any>): Record<string, any> {
    const lineData: Record<string, any> = {};
    this.lineFields.forEach(field => {
      if (row[field] !== undefined) {
        lineData[field] = row[field];
      }
    });
    return lineData;
  }
  
  private applyFieldMappings(
    data: Array<Record<string, any>>,
    mappings: Record<string, string>
  ): Array<Record<string, any>> {
    return data.map(row => {
      const mapped: Record<string, any> = { ...row };
      Object.entries(mappings).forEach(([source, target]) => {
        if (source in mapped) {
          mapped[target] = mapped[source];
        }
      });
      return mapped;
    });
  }
}
```

### 5.4 注意事项

1. **空值处理**: TypeScript中需要明确检查 `null`、`undefined` 和空字符串
2. **分组操作**: 使用 `Map` 或 `Array.reduce()` 替代 pandas 的 `groupby`
3. **前向填充**: 手动实现循环，不能依赖 pandas 的 `fillna(method='ffill')`
4. **性能优化**: 对于大数据集（>1000行），考虑分批处理
5. **类型安全**: 使用 TypeScript 接口定义数据结构，提高类型安全性

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

