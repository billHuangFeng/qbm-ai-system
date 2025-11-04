# Edge Functions 测试用例文档

**项目**: 数据导入功能迁移到 Supabase Edge Functions  
**创建日期**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

---

## 📋 测试用例概述

本文档包含所有 Edge Functions 的测试用例，用于验证功能正确性。

---

## 1. data-import-upload 测试用例

### 测试用例 1.1: 成功上传 CSV 文件

**输入**:
- `file`: `test_data.csv` (1MB, 1000行)
- `tenant_id`: `tenant-123`
- `user_id`: `user-456`

**期望输出**:
```json
{
  "success": true,
  "file_id": "uuid-v4",
  "file_name": "test_data.csv",
  "file_size": 1048576,
  "row_count": 1000,
  "column_count": 15,
  "format_detection": {
    "format_type": "repeated_header",
    "confidence": 0.95
  }
}
```

**验证点**:
- ✅ HTTP状态码 = 200
- ✅ `success` = true
- ✅ `file_id` 是有效的UUID
- ✅ `row_count` = 1000
- ✅ 文件已上传到Supabase Storage
- ✅ 数据库记录已创建

---

### 测试用例 1.2: 文件格式不支持

**输入**:
- `file`: `test_data.pdf` (PDF文件)

**期望输出**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式，仅支持 CSV, Excel, JSON, Parquet"
  }
}
```

**验证点**:
- ✅ HTTP状态码 = 400
- ✅ `success` = false
- ✅ 错误码 = `INVALID_FILE_FORMAT`

---

### 测试用例 1.3: 文件过大

**输入**:
- `file`: `large_file.xlsx` (60MB)

**期望输出**:
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "文件大小超过限制（最大50MB）",
    "details": {
      "file_size": 62914560,
      "max_size": 52428800
    }
  }
}
```

**验证点**:
- ✅ HTTP状态码 = 413
- ✅ 错误码 = `FILE_TOO_LARGE`

---

## 2. data-import-analyze 测试用例

### 测试用例 2.1: 字段映射推荐（历史映射优先）

**前置条件**:
- 数据库中已有历史映射记录:
  - `source_field`: "采购单号"
  - `target_field`: "document_number"
  - `usage_count`: 10

**输入**:
```json
{
  "file_id": "uuid-v4",
  "target_table": "doc_purchase_order_header",
  "source_system": "erp_system_1",
  "document_type": "purchase_order"
}
```

**期望输出**:
```json
{
  "success": true,
  "field_mappings": [
    {
      "source_field": "采购单号",
      "candidates": [
        {
          "target_field": "document_number",
          "confidence": 0.95,
          "method": "history",
          "source": "历史映射 (使用10次)"
        }
      ],
      "recommended_target": "document_number",
      "recommended_confidence": 0.95
    }
  ]
}
```

**验证点**:
- ✅ 历史映射被优先推荐
- ✅ 置信度 >= 0.85

---

### 测试用例 2.2: 字段映射推荐（相似度匹配）

**前置条件**:
- 数据库中没有历史映射记录

**输入**:
```json
{
  "file_id": "uuid-v4",
  "target_table": "doc_purchase_order_header",
  "source_system": "new_system",
  "source_fields": ["客户名", "订单日期"]
}
```

**期望输出**:
```json
{
  "success": true,
  "field_mappings": [
    {
      "source_field": "客户名",
      "candidates": [
        {
          "target_field": "customer_name",
          "confidence": 0.75,
          "method": "similarity",
          "source": "字符串相似度匹配"
        }
      ],
      "recommended_target": "customer_name",
      "recommended_confidence": 0.75
    }
  ]
}
```

**验证点**:
- ✅ 使用相似度匹配
- ✅ 置信度 0.6-0.9

---

## 3. data-import-validate 测试用例

### 测试用例 3.1: 必填字段验证失败

**输入**:
```json
{
  "file_id": "uuid-v4",
  "field_mappings": {
    "采购单号": "document_number",
    "客户名称": "customer_name"
  },
  "validation_rules": [
    {
      "field": "document_number",
      "type": "required",
      "message": "单据号是必填字段"
    }
  ]
}
```

**测试数据**:
```json
[
  { "采购单号": "PO001", "客户名称": "客户A" },
  { "采购单号": null, "客户名称": "客户B" }  // 缺少单据号
]
```

**期望输出**:
```json
{
  "success": true,
  "validation_report": {
    "total_rows": 2,
    "valid_rows": 1,
    "invalid_rows": 1,
    "errors": [
      {
        "row_index": 1,
        "field": "document_number",
        "message": "单据号是必填字段",
        "value": null
      }
    ],
    "quality_score": 0.5
  }
}
```

**验证点**:
- ✅ 检测到必填字段缺失
- ✅ 错误信息准确

---

### 测试用例 3.2: 金额一致性验证

**输入**:
```json
{
  "validation_rules": [
    {
      "field": "total_amount_with_tax",
      "type": "business",
      "message": "价税合计 = 不含税金额 + 税额"
    }
  ]
}
```

**测试数据**:
```json
[
  {
    "不含税金额": 100,
    "税额": 13,
    "价税合计": 113  // 正确
  },
  {
    "不含税金额": 200,
    "税额": 26,
    "价税合计": 250  // 错误: 应该是226
  }
]
```

**期望输出**:
```json
{
  "validation_report": {
    "errors": [
      {
        "row_index": 1,
        "field": "价税合计",
        "message": "价税合计不一致: 计算值 226.00 ≠ 实际值 250.00",
        "value": 250
      }
    ]
  }
}
```

**验证点**:
- ✅ 检测到金额不一致
- ✅ 计算值正确

---

## 4. data-import-match-master 测试用例

### 测试用例 4.1: 代码完全一致 + 名称大致类似

**前置条件**:
- 主数据表中有记录:
  - `code`: "91110000..."
  - `name`: "北京科技有限公司"

**输入**:
```json
{
  "records": [
    {
      "row_index": 0,
      "master_data_type": "business_entity",
      "source_values": {
        "name": "北京科技有限公司",
        "code": "91110000..."
      }
    }
  ]
}
```

**期望输出**:
```json
{
  "matches": [
    {
      "row_index": 0,
      "candidates": [
        {
          "id": 123,
          "name": "北京科技有限公司",
          "confidence": 1.0,
          "match_fields": ["name", "code"]
        }
      ],
      "no_match": false,
      "multiple_matches": false
    }
  ]
}
```

**验证点**:
- ✅ `confidence` = 1.0
- ✅ `match_fields` 包含 "code" 和 "name"

---

### 测试用例 4.2: 代码细微差异 + 名称大致类似

**输入**:
```json
{
  "records": [
    {
      "row_index": 0,
      "master_data_type": "business_entity",
      "source_values": {
        "name": "北京科技有限公司",
        "code": "91110001..."  // 与主数据中的 "91110000..." 差1个字符
      }
    }
  ]
}
```

**期望输出**:
```json
{
  "matches": [
    {
      "row_index": 0,
      "candidates": [
        {
          "id": 123,
          "name": "北京科技有限公司",
          "confidence": 0.45,  // 30-60% 置信度
          "match_fields": ["name"]
        }
      ]
    }
  ]
}
```

**验证点**:
- ✅ `confidence` 在 0.3-0.6 之间
- ✅ 置信度被显著降低

---

### 测试用例 4.3: 总公司和分公司匹配（低置信度）

**输入**:
```json
{
  "records": [
    {
      "row_index": 0,
      "master_data_type": "business_entity",
      "source_values": {
        "name": "北京科技有限公司",  // 记录是总公司
        "code": "91110000..."
      }
    }
  ]
}
```

**前置条件**:
- 主数据表中有记录:
  - `name`: "北京科技有限公司上海分公司"
  - `code`: "91110000..."

**期望输出**:
```json
{
  "matches": [
    {
      "row_index": 0,
      "candidates": [
        {
          "id": 456,
          "name": "北京科技有限公司上海分公司",
          "confidence": 0.60,  // 低置信度
          "match_fields": ["name"],
          "match_type": "headquarter_branch"
        }
      ]
    }
  ]
}
```

**验证点**:
- ✅ `confidence` = 0.60（低置信度）
- ✅ 匹配类型 = "headquarter_branch"

---

## 5. data-import-match-headers 测试用例

### 测试用例 5.1: 精确匹配成功

**前置条件**:
- 数据库中有单据头记录:
  - `document_number`: "PO001"
  - `id`: "uuid-123"

**输入**:
```json
{
  "document_numbers": ["PO001", "PO002"],
  "document_type": "purchase_order",
  "table_name": "doc_purchase_order_header"
}
```

**期望输出**:
```json
{
  "matches": [
    {
      "document_number": "PO001",
      "header_id": "uuid-123",
      "confidence": 1.0,
      "found": true,
      "header_info": {
        "id": "uuid-123",
        "document_number": "PO001"
      }
    },
    {
      "document_number": "PO002",
      "header_id": null,
      "confidence": 0.0,
      "found": false,
      "message": "系统中未找到单据号PO002的单据头记录"
    }
  ]
}
```

**验证点**:
- ✅ 找到的记录 `found` = true
- ✅ `confidence` = 1.0
- ✅ 未找到的记录 `found` = false

---

## 6. 集成测试用例

### 测试用例 6.1: 完整导入流程

**步骤**:
1. 上传文件 (`data-import-upload`)
2. 分析文件结构 (`data-import-analyze`)
3. 验证数据 (`data-import-validate`)
4. 匹配主数据 (`data-import-match-master`)
5. 匹配单据头 (`data-import-match-headers`)

**期望结果**:
- ✅ 所有步骤成功执行
- ✅ 数据质量评分 >= 0.8
- ✅ 主数据匹配率 >= 80%
- ✅ 单据头匹配率 >= 90%

---

## 7. 性能测试用例

### 测试用例 7.1: 大文件处理

**输入**:
- `file`: `large_file.xlsx` (10MB, 10000行)

**期望**:
- ✅ 上传时间 < 30s
- ✅ 分析时间 < 60s
- ✅ 内存使用 < 512MB

---

### 测试用例 7.2: 并发上传

**输入**:
- 同时上传 10 个文件

**期望**:
- ✅ 所有文件成功上传
- ✅ 无数据冲突
- ✅ 总处理时间 < 300s

---

## 8. 边界测试用例

### 测试用例 8.1: 空文件

**输入**:
- `file`: `empty.csv` (0行)

**期望输出**:
```json
{
  "success": false,
  "error": {
    "code": "EMPTY_FILE",
    "message": "文件为空，无法处理"
  }
}
```

---

### 测试用例 8.2: 单行数据

**输入**:
- `file`: `single_row.csv` (1行)

**期望**:
- ✅ 成功处理
- ✅ 格式识别正确

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

