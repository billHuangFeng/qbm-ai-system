# 数据导入API文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **已完成**

**文档目的**: 记录数据导入功能的所有API端点，供前端和Edge Functions调用

---

## 📋 目录

1. [API端点列表](#1-api端点列表)
2. [字段映射推荐API](#2-字段映射推荐api)
3. [获取表结构API](#3-获取表结构api)
4. [获取可用表列表API](#4-获取可用表列表api)
5. [保存映射历史API](#5-保存映射历史api)
6. [错误处理](#6-错误处理)

---

## 1. API端点列表

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/data-enhancement/recommend-field-mappings` | POST | 字段映射推荐 | ✅ |
| `/api/v1/data-enhancement/table-schema/{table_name}` | GET | 获取表结构 | ✅ |
| `/api/v1/data-enhancement/available-tables` | GET | 获取可用表列表 | ✅ |
| `/api/v1/data-enhancement/save-mapping-history` | POST | 保存映射历史 | ✅ |

**Base URL**: `http://localhost:8000` (开发环境)  
**认证**: 所有API都需要JWT Token认证

---

## 2. 字段映射推荐API

### 端点

```
POST /api/v1/data-enhancement/recommend-field-mappings
```

### 功能

根据源字段列表和目标表，智能推荐字段映射关系。支持：
- 历史映射（优先）
- 规则匹配
- 相似度计算

### 请求

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```json
{
  "source_fields": ["订单号", "客户名称", "订单日期", "产品代码", "数量", "单价"],
  "target_table": "sales_order_header",
  "source_system": "upload",
  "document_type": "SO",
  "user_id": "optional-user-id"
}
```

**参数说明**:
- `source_fields` (必需): 源文件字段列表
- `target_table` (必需): 目标表名（如 `sales_order_header`）
- `source_system` (可选): 数据源系统标识（默认 `"upload"`）
- `document_type` (可选): 单据类型（SO/SH/SI/PO/RC/PI）
- `user_id` (可选): 用户ID（用于个人化推荐）

### 响应

**成功响应** (200):
```json
{
  "recommendations": [
    {
      "source_field": "订单号",
      "recommended_target": "order_number",
      "recommended_confidence": 0.95,
      "candidates": [
        {
          "target_field": "order_number",
          "confidence": 0.95,
          "method": "history",
          "source": "历史映射（15次使用）"
        },
        {
          "target_field": "document_number",
          "confidence": 0.75,
          "method": "similarity",
          "source": "相似度匹配（85%）"
        }
      ]
    },
    {
      "source_field": "客户名称",
      "recommended_target": "customer_name",
      "recommended_confidence": 0.88,
      "candidates": [
        {
          "target_field": "customer_name",
          "confidence": 0.88,
          "method": "similarity",
          "source": "相似度匹配（88%）"
        }
      ]
    }
  ],
  "success": true,
  "message": "字段映射推荐完成"
}
```

**错误响应** (400):
```json
{
  "detail": "target_table 是必需的，必须提供目标表名以从数据库获取字段"
}
```

**错误响应** (500):
```json
{
  "detail": "字段映射推荐失败: <error_message>"
}
```

### 使用示例

```typescript
// TypeScript调用示例
const response = await fetch('http://localhost:8000/api/v1/data-enhancement/recommend-field-mappings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source_fields: ['订单号', '客户名称', '订单日期'],
    target_table: 'sales_order_header',
    source_system: 'ERP_SYSTEM_A',
    document_type: 'SO'
  })
});

const result = await response.json();
console.log(result.recommendations);
```

---

## 3. 获取表结构API

### 端点

```
GET /api/v1/data-enhancement/table-schema/{table_name}?document_type={doc_type}
```

### 功能

返回目标表的字段定义和主数据匹配字段

### 请求

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
- `table_name` (必需): 目标表名（如 `sales_order_header`）

**Query Parameters**:
- `document_type` (可选): 单据类型（用于获取主数据匹配字段）

### 响应

**成功响应** (200):
```json
{
  "table_name": "sales_order_header",
  "fields": [
    {
      "name": "id",
      "type": "uuid",
      "nullable": false,
      "default": "gen_random_uuid()"
    },
    {
      "name": "tenant_id",
      "type": "uuid",
      "nullable": false,
      "default": null
    },
    {
      "name": "order_number",
      "type": "character varying",
      "nullable": false,
      "default": null
    },
    {
      "name": "order_date",
      "type": "date",
      "nullable": false,
      "default": null
    },
    {
      "name": "customer_id",
      "type": "uuid",
      "nullable": true,
      "default": null
    },
    {
      "name": "customer_name",
      "type": "character varying",
      "nullable": true,
      "default": null
    }
  ],
  "master_data_fields": [
    "customer_name",
    "customer_code"
  ],
  "field_types": {
    "id": {
      "data_type": "uuid",
      "max_length": null,
      "nullable": false,
      "default": "gen_random_uuid()"
    },
    "order_number": {
      "data_type": "character varying",
      "max_length": 50,
      "nullable": false,
      "default": null
    }
  },
  "success": true,
  "message": "获取表结构成功"
}
```

### 使用示例

```typescript
// TypeScript调用示例
const response = await fetch(
  'http://localhost:8000/api/v1/data-enhancement/table-schema/sales_order_header?document_type=SO',
  {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const result = await response.json();
console.log(result.fields);  // 表字段列表
console.log(result.master_data_fields);  // 主数据匹配字段
```

---

## 4. 获取可用表列表API

### 端点

```
GET /api/v1/data-enhancement/available-tables?document_type={doc_type}
```

### 功能

返回所有可用的导入目标表列表，按业务场景分组

### 请求

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
- `document_type` (可选): 单据类型（用于过滤表列表）

### 响应

**成功响应** (200):
```json
{
  "tables": [
    {
      "table_name": "sales_order_header",
      "display_name": "销售订单头表",
      "category": "销售流程",
      "document_type": "SO",
      "has_lines": true,
      "line_table": "sales_order_line"
    },
    {
      "table_name": "shipment_header",
      "display_name": "发货单头表",
      "category": "销售流程",
      "document_type": "SH",
      "has_lines": true,
      "line_table": "shipment_line"
    },
    {
      "table_name": "dim_customer",
      "display_name": "客户主数据",
      "category": "主数据",
      "document_type": null,
      "has_lines": false
    }
  ],
  "categories": {
    "销售流程": ["sales_order_header", "shipment_header", "sales_invoice_header"],
    "采购流程": ["purchase_order_header", "receipt_header", "purchase_invoice_header"],
    "主数据": ["dim_customer", "dim_supplier", "dim_sku", "dim_channel"]
  },
  "success": true,
  "message": "获取可用表列表成功"
}
```

### 使用示例

```typescript
// TypeScript调用示例
const response = await fetch(
  'http://localhost:8000/api/v1/data-enhancement/available-tables?document_type=SO',
  {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const result = await response.json();
console.log(result.tables);  // 可用表列表
console.log(result.categories);  // 按类别分组
```

---

## 5. 保存映射历史API

### 端点

```
POST /api/v1/data-enhancement/save-mapping-history
```

### 功能

将用户确认的字段映射保存到`field_mapping_history`表，用于未来的智能推荐学习

### 请求

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```json
{
  "source_system": "ERP_SYSTEM_A",
  "target_table": "sales_order_header",
  "source_field": "订单号",
  "target_field": "order_number",
  "document_type": "SO",
  "mapping_method": "manual",
  "confidence_score": 1.0
}
```

**参数说明**:
- `source_system` (必需): 数据源系统标识
- `target_table` (必需): 目标表名
- `source_field` (必需): 源字段名
- `target_field` (必需): 目标字段名
- `document_type` (可选): 单据类型
- `mapping_method` (可选): 映射方法（`manual`/`rule`/`similarity`，默认 `manual`）
- `confidence_score` (可选): 置信度分数（0-1）

### 响应

**成功响应** (200):
```json
{
  "mapping_id": "uuid-v4",
  "success": true,
  "message": "映射历史保存成功"
}
```

**错误响应** (400):
```json
{
  "detail": "缺少租户ID"
}
```

### 使用示例

```typescript
// TypeScript调用示例
const response = await fetch('http://localhost:8000/api/v1/data-enhancement/save-mapping-history', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source_system: 'ERP_SYSTEM_A',
    target_table: 'sales_order_header',
    source_field: '订单号',
    target_field: 'order_number',
    document_type: 'SO',
    mapping_method: 'manual',
    confidence_score: 1.0
  })
});

const result = await response.json();
console.log(result.mapping_id);
```

---

## 6. 错误处理

### 标准错误响应格式

```json
{
  "detail": "错误消息"
}
```

### 错误码

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 400 | Bad Request | 请求参数错误（如缺少必需参数） |
| 401 | Unauthorized | 认证失败（JWT Token无效或过期） |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在（如表不存在） |
| 500 | Internal Server Error | 服务器内部错误 |

### 常见错误

**错误1**: `target_table 是必需的`
- **原因**: 请求中缺少`target_table`参数
- **解决**: 在请求体中提供`target_table`参数

**错误2**: `缺少租户ID`
- **原因**: JWT Token中缺少`tenant_id`或用户未关联租户
- **解决**: 检查用户认证信息

**错误3**: `目标表 {table_name} 不存在或没有字段`
- **原因**: 指定的目标表不存在
- **解决**: 使用`/available-tables`端点获取可用表列表

---

## 7. 调用流程说明

### 完整字段映射流程

```typescript
// 1. 获取可用表列表
const tablesResponse = await fetch('/api/v1/data-enhancement/available-tables?document_type=SO');
const { tables } = await tablesResponse.json();

// 2. 用户选择目标表
const targetTable = 'sales_order_header';

// 3. 获取表结构
const schemaResponse = await fetch(`/api/v1/data-enhancement/table-schema/${targetTable}?document_type=SO`);
const { fields, master_data_fields } = await schemaResponse.json();

// 4. 获取源字段（从上传的文件中解析）
const sourceFields = ['订单号', '客户名称', '订单日期', '产品代码', '数量', '单价'];

// 5. 获取字段映射推荐
const mappingResponse = await fetch('/api/v1/data-enhancement/recommend-field-mappings', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source_fields: sourceFields,
    target_table: targetTable,
    source_system: 'ERP_SYSTEM_A',
    document_type: 'SO'
  })
});

const { recommendations } = await mappingResponse.json();

// 6. 用户确认映射关系
const confirmedMappings = {
  '订单号': 'order_number',
  '客户名称': 'customer_name',
  '订单日期': 'order_date'
};

// 7. 保存映射历史（批量保存）
for (const [sourceField, targetField] of Object.entries(confirmedMappings)) {
  await fetch('/api/v1/data-enhancement/save-mapping-history', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      source_system: 'ERP_SYSTEM_A',
      target_table: targetTable,
      source_field: sourceField,
      target_field: targetField,
      document_type: 'SO',
      mapping_method: 'manual',
      confidence_score: 1.0
    })
  });
}
```

---

## 8. 性能要求

### 响应时间基准

| API端点 | 首次查询 | 缓存命中 |
|---------|---------|---------|
| `/recommend-field-mappings` | < 500ms | < 50ms |
| `/table-schema/{table_name}` | < 200ms | < 20ms |
| `/available-tables` | < 100ms | < 10ms |
| `/save-mapping-history` | < 100ms | - |

### 缓存策略

- **表结构缓存**: 24小时（表结构变化不频繁）
- **字段映射推荐**: 使用历史映射缓存，提升推荐速度
- **可用表列表**: 内存缓存（配置信息，无需数据库查询）

---

## 9. 测试建议

### 单元测试

- 测试各个API端点的参数验证
- 测试错误处理逻辑
- 测试缓存机制

### 集成测试

- 测试完整的字段映射流程
- 测试映射历史学习效果（保存后再次推荐）

### 性能测试

- 测试响应时间是否满足要求
- 测试并发请求处理能力

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

