# 数据增强API设计文档

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **API端点设计完整**

---

## 📋 API概览

数据导入完善系统第3阶段提供5个核心API端点，用于数据增强和质量提升。

**基础路径**: `/api/v1/data-enhancement`

---

## 🔗 API端点列表

### 1. 主数据匹配 API

**端点**: `POST /api/v1/data-enhancement/match-master-data`

**功能**: 根据辅助信息（名称、统一社会信用代码等）匹配主数据ID

**请求体**:
```json
{
  "data_type": "order",
  "records": [
    {
      "row_index": 0,
      "name": "北京科技有限公司",
      "credit_code": "91110000123456789X"
    }
  ],
  "master_data_table": "customer_master",
  "confidence_threshold": 0.8
}
```

**响应体**:
```json
{
  "success": true,
  "message": "主数据匹配完成",
  "matched_records": [
    {
      "row_index": 0,
      "suggested_master_id": "uuid",
      "confidence": 0.92,
      "match_reason": "企业名称相似度95% + 信用代码完全匹配",
      "alternatives": [...]
    }
  ],
  "unmatched_records": [...],
  "statistics": {
    "total_records": 10,
    "matched_count": 8,
    "unmatched_count": 2,
    "match_rate": 0.8,
    "average_confidence": 0.88
  }
}
```

**错误码**:
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 2. 计算冲突检测 API

**端点**: `POST /api/v1/data-enhancement/detect-conflicts`

**功能**: 检测存在计算逻辑关系的字段之间的冲突

**请求体**:
```json
{
  "data_type": "order",
  "records": [
    {
      "row_index": 0,
      "数量": 10,
      "单价": 100,
      "订单金额": 1000
    }
  ],
  "calculation_rules": [
    {
      "formula": "订单金额 = 数量 × 单价"
    }
  ],
  "tolerance": 0.01
}
```

**响应体**:
```json
{
  "success": true,
  "message": "计算冲突检测完成",
  "conflicts": [
    {
      "row_index": 5,
      "field": "订单金额",
      "expected_value": 1500.00,
      "actual_value": 1450.00,
      "difference": -50.00,
      "formula": "数量 × 单价",
      "severity": "medium",
      "auto_fixable": true,
      "suggested_fix": "use_calculated_value"
    }
  ],
  "cascade_conflicts": [],
  "statistics": {
    "total_checked": 1000,
    "conflicts_found": 23,
    "auto_fixable": 18,
    "manual_review_required": 5,
    "severity_breakdown": {
      "high": 3,
      "medium": 10,
      "low": 10
    }
  }
}
```

**错误码**:
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 3. 智能补值 API

**端点**: `POST /api/v1/data-enhancement/impute-values`

**功能**: 智能填充缺失值

**请求体**:
```json
{
  "data_type": "order",
  "records": [
    {
      "单价": 100,
      "币种": "CNY"
    },
    {
      "单价": null,
      "币种": null
    }
  ],
  "field_configs": {
    "单价": {
      "field_type": "numeric",
      "default_value": null
    },
    "币种": {
      "field_type": "categorical",
      "rule_name": "currency"
    }
  },
  "strategy": "auto"
}
```

**响应体**:
```json
{
  "success": true,
  "message": "智能补值完成",
  "imputed_records": [...],
  "imputation_log": [
    {
      "row_index": 10,
      "field": "单价",
      "original_value": null,
      "imputed_value": 125.5,
      "method": "knn",
      "confidence": 0.85
    }
  ],
  "statistics": {
    "total_records": 100,
    "missing_count": 15,
    "imputed_count": 15,
    "imputation_rate": 1.0,
    "strategy_used": "auto",
    "fields_imputed": ["单价", "币种"]
  }
}
```

**错误码**:
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 4. 数据质量评估 API

**端点**: `POST /api/v1/data-enhancement/assess-quality`

**功能**: 7维度质量检查 + 质量评分 + 可导入性判定

**请求体**:
```json
{
  "data_type": "order",
  "records": [...],
  "validation_rules": {
    "field_configs": {
      "订单金额": {
        "data_type": "numeric"
      }
    },
    "calculation_rules": [
      {
        "formula": "订单金额 = 数量 × 单价"
      }
    ],
    "date_fields": ["订单日期"],
    "primary_keys": ["订单号"],
    "foreign_keys": [
      {
        "field": "customer_id",
        "reference_table": "customer_master",
        "reference_field": "id"
      }
    ],
    "business_rules": {
      "订单金额范围": {
        "rule_type": "range",
        "field": "订单金额",
        "min": 0,
        "max": 1000000
      }
    }
  }
}
```

**响应体**:
```json
{
  "success": true,
  "message": "数据质量评估完成",
  "overall_score": 87.5,
  "importability": "good",
  "dimensions": {
    "completeness": {
      "score": 0.90,
      "weight": 0.20,
      "details": {...}
    },
    "accuracy": {
      "score": 0.85,
      "weight": 0.25,
      "details": {...}
    },
    ...
  },
  "blocking_issues": [],
  "fixable_issues": [
    {
      "issue_id": "MISSING_MASTER_ID",
      "severity": "medium",
      "count": 15,
      "description": "15条记录缺失往来单位ID",
      "message": "检测到辅助信息可用于匹配",
      "auto_fixable": true,
      "field": "customer_id",
      "examples": [...]
    }
  ],
  "recommendations": [
    "建议进行数据清洗和修复",
    "建议补充缺失值"
  ]
}
```

**错误码**:
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 5. 暂存表管理 API

**端点**: `POST /api/v1/data-enhancement/manage-staging`

**功能**: 动态创建和管理暂存表

**请求体（创建）**:
```json
{
  "data_type": "order",
  "operation": "create",
  "target_table": "order_master",
  "records": [...]
}
```

**请求体（迁移）**:
```json
{
  "data_type": "order",
  "operation": "migrate",
  "target_table": "order_master",
  "staging_table_name": "staging_order_20250123_abc123"
}
```

**请求体（清理）**:
```json
{
  "data_type": "order",
  "operation": "cleanup",
  "retention_days": 7
}
```

**响应体（创建）**:
```json
{
  "success": true,
  "message": "暂存表操作完成",
  "staging_table_name": "staging_order_20250123_abc123",
  "status": "created",
  "row_count": 1234,
  "created_at": "2025-01-23T10:30:00Z"
}
```

**响应体（迁移）**:
```json
{
  "success": true,
  "message": "暂存表操作完成",
  "status": "success",
  "migrated_count": 1234
}
```

**响应体（清理）**:
```json
{
  "success": true,
  "message": "暂存表操作完成",
  "status": "success",
  "cleaned_count": 3,
  "cleaned_tables": ["staging_order_xxx", ...]
}
```

**错误码**:
- `400`: 请求参数错误（缺少必需参数）
- `500`: 服务器内部错误

---

## 🔐 认证要求

所有API端点都需要认证：

**请求头**:
```
Authorization: Bearer <token>
```

**认证失败响应**:
```json
{
  "detail": "Not authenticated"
}
```
状态码: `401`

---

## 📊 错误处理

### 通用错误响应格式

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-23T10:30:00Z"
}
```

### 错误码列表

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未认证 |
| `FORBIDDEN` | 403 | 无权限 |
| `NOT_FOUND` | 404 | 资源未找到 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `DATABASE_ERROR` | 500 | 数据库操作失败 |
| `VALIDATION_ERROR` | 400 | 数据验证失败 |

---

## 📈 性能要求

- **1000条数据处理时间**: < 10秒
- **主数据匹配准确率**: > 90%（置信度>0.8时）
- **计算冲突检测漏检率**: < 5%
- **智能补值合理性**: > 85%

---

## 📚 相关文档

- [数据导入完善系统第3阶段实施状态](../DATA_ENHANCEMENT_PHASE3_IMPLEMENTATION_STATUS.md)
- [数据导入完善系统第3阶段进度](../DATA_ENHANCEMENT_PHASE3_PROGRESS.md)
- [数据导入完善系统第3阶段快速开始](../DATA_ENHANCEMENT_PHASE3_QUICK_START.md)

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23  
**状态**: ✅ **API端点设计完整**

