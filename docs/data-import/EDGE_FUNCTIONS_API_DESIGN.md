# Edge Functions API 设计文档

**项目**: 数据导入功能迁移到 Supabase Edge Functions  
**创建日期**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

---

## 📋 概述

本文档定义所有 Supabase Edge Functions API 的接口规范，包括输入、输出、错误码和伪代码。

---

## 1. data-import-upload

### Function: data-import-upload

**Path**: `/functions/v1/data-import-upload`  
**Method**: POST  
**Runtime**: Deno  
**Timeout**: 60s

### Input

**Body**: FormData
- `file`: File (CSV, Excel, JSON, Parquet)
  - **支持格式**: `.csv`, `.xlsx`, `.xls`, `.json`, `.parquet`
  - **最大大小**: 50MB
- `source_system`: string (可选) - 数据源系统标识
- `document_type`: string (可选) - 单据类型（purchase_order, sales_order, etc.）
- `tenant_id`: string (必需) - 租户ID
- `user_id`: string (可选) - 用户ID

### Output

**成功响应** (200):
```json
{
  "success": true,
  "file_id": "uuid-v4",
  "file_name": "example.xlsx",
  "file_size": 1024000,
  "row_count": 1500,
  "column_count": 20,
  "format_detection": {
    "format_type": "repeated_header",
    "confidence": 0.95,
    "details": {
      "unique_docs": 100,
      "total_rows": 1500,
      "duplicate_ratio": 0.93
    }
  },
  "storage_path": "data-import/tenant-123/uuid-v4/example.xlsx",
  "uploaded_at": "2025-01-23T10:00:00Z"
}
```

**错误响应** (400):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式，仅支持 CSV, Excel, JSON, Parquet",
    "details": {}
  }
}
```

**错误响应** (413):
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "文件大小超过限制（最大50MB）",
    "details": {
      "file_size": 52428800,
      "max_size": 52428800
    }
  }
}
```

**错误响应** (500):
```json
{
  "success": false,
  "error": {
    "code": "SERVER_ERROR",
    "message": "服务器内部错误",
    "details": {
      "error": "具体错误信息"
    }
  }
}
```

### Error Codes

| 错误码 | HTTP状态 | 说明 |
|--------|---------|------|
| `INVALID_FILE_FORMAT` | 400 | 文件格式不支持 |
| `FILE_TOO_LARGE` | 413 | 文件大小超过限制 |
| `UPLOAD_FAILED` | 500 | 文件上传失败 |
| `PARSING_ERROR` | 500 | 文件解析失败 |
| `SERVER_ERROR` | 500 | 服务器内部错误 |

### Pseudocode

```typescript
// supabase/functions/data-import-upload/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  try {
    // 1. 验证请求方法
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ success: false, error: { code: 'METHOD_NOT_ALLOWED', message: '仅支持POST方法' } }),
        { status: 405, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // 2. 解析FormData
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return new Response(
        JSON.stringify({ success: false, error: { code: 'MISSING_FILE', message: '未提供文件' } }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // 3. 验证文件格式
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      return new Response(
        JSON.stringify({ success: false, error: { code: 'INVALID_FILE_FORMAT', message: '不支持的文件格式' } }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // 4. 验证文件大小（最大50MB）
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return new Response(
        JSON.stringify({ success: false, error: { code: 'FILE_TOO_LARGE', message: '文件大小超过限制' } }),
        { status: 413, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // 5. 初始化Supabase客户端
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    // 6. 获取租户ID和用户ID
    const tenantId = formData.get('tenant_id') as string;
    const userId = formData.get('user_id') as string;
    const sourceSystem = formData.get('source_system') as string || 'unknown';
    const documentType = formData.get('document_type') as string || null;
    
    // 7. 生成文件ID
    const fileId = crypto.randomUUID();
    const storagePath = `data-import/${tenantId}/${fileId}/${file.name}`;
    
    // 8. 上传文件到Supabase Storage
    const fileBuffer = await file.arrayBuffer();
    const { error: uploadError } = await supabase.storage
      .from('data-import')
      .upload(storagePath, fileBuffer, {
        contentType: file.type,
        upsert: false
      });
    
    if (uploadError) {
      throw new Error(`文件上传失败: ${uploadError.message}`);
    }
    
    // 9. 解析文件内容
    const fileContent = await parseFile(file, fileExtension);
    
    // 10. 调用格式识别算法
    const formatDetection = await detectFormat(fileContent.data);
    
    // 11. 保存上传记录到数据库
    const { error: dbError } = await supabase
      .from('data_import_uploads')
      .insert({
        id: fileId,
        tenant_id: tenantId,
        user_id: userId,
        file_name: file.name,
        file_size: file.size,
        row_count: fileContent.data.length,
        column_count: fileContent.columns.length,
        format_type: formatDetection.formatType,
        format_confidence: formatDetection.confidence,
        storage_path: storagePath,
        source_system: sourceSystem,
        document_type: documentType,
        status: 'uploaded',
        uploaded_at: new Date().toISOString()
      });
    
    if (dbError) {
      throw new Error(`数据库保存失败: ${dbError.message}`);
    }
    
    // 12. 返回结果
    return new Response(
      JSON.stringify({
        success: true,
        file_id: fileId,
        file_name: file.name,
        file_size: file.size,
        row_count: fileContent.data.length,
        column_count: fileContent.columns.length,
        format_detection: {
          format_type: formatDetection.formatType,
          confidence: formatDetection.confidence,
          details: formatDetection.details
        },
        storage_path: storagePath,
        uploaded_at: new Date().toISOString()
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
    
  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: error.message || '服务器内部错误',
          details: { error: error.toString() }
        }
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
});
```

---

## 2. data-import-analyze

### Function: data-import-analyze

**Path**: `/functions/v1/data-import-analyze`  
**Method**: POST  
**Runtime**: Deno  
**Timeout**: 30s

### Input

**Body**: JSON
```json
{
  "file_id": "uuid-v4",
  "target_table": "doc_purchase_order_header",
  "source_system": "erp_system_1",
  "document_type": "purchase_order",
  "user_id": "user-123"
}
```

### Output

**成功响应** (200):
```json
{
  "success": true,
  "file_id": "uuid-v4",
  "field_mappings": [
    {
      "source_field": "采购单号",
      "candidates": [
        {
          "target_field": "document_number",
          "confidence": 0.95,
          "method": "history",
          "source": "历史映射 (使用10次)"
        },
        {
          "target_field": "order_number",
          "confidence": 0.75,
          "method": "similarity",
          "source": "字符串相似度匹配"
        }
      ],
      "recommended_target": "document_number",
      "recommended_confidence": 0.95
    }
  ],
  "format_detection": {
    "format_type": "repeated_header",
    "confidence": 0.95
  },
  "data_preview": {
    "total_rows": 1500,
    "sample_rows": [
      { "采购单号": "PO001", "客户名称": "客户A", ... }
    ]
  }
}
```

### Pseudocode

```typescript
serve(async (req) => {
  const { file_id, target_table, source_system, document_type, user_id } = await req.json();
  
  // 1. 从Storage获取文件
  const fileData = await supabase.storage.from('data-import').download(filePath);
  
  // 2. 解析文件
  const parsedData = await parseFile(fileData);
  
  // 3. 调用字段映射推荐算法
  const fieldMappings = await recommendMappings(
    parsedData.columns,
    source_system,
    target_table,
    document_type,
    user_id,
    supabase
  );
  
  // 4. 调用格式识别算法
  const formatDetection = await detectFormat(parsedData.data);
  
  // 5. 返回分析结果
  return new Response(JSON.stringify({
    success: true,
    file_id,
    field_mappings,
    format_detection,
    data_preview: {
      total_rows: parsedData.data.length,
      sample_rows: parsedData.data.slice(0, 5)
    }
  }));
});
```

---

## 3. data-import-validate

### Function: data-import-validate

**Path**: `/functions/v1/data-import-validate`  
**Method**: POST  
**Timeout**: 60s

### Input

```json
{
  "file_id": "uuid-v4",
  "field_mappings": {
    "采购单号": "document_number",
    "客户名称": "customer_name",
    ...
  },
  "validation_rules": [
    {
      "field": "document_number",
      "type": "required",
      "message": "单据号是必填字段"
    },
    {
      "field": "total_amount_with_tax",
      "type": "business",
      "message": "价税合计 = 不含税金额 + 税额"
    }
  ]
}
```

### Output

```json
{
  "success": true,
  "file_id": "uuid-v4",
  "validation_report": {
    "total_rows": 1500,
    "valid_rows": 1450,
    "invalid_rows": 50,
    "errors": [
      {
        "row_index": 10,
        "field": "document_number",
        "message": "单据号是必填字段",
        "value": null
      }
    ],
    "warnings": [],
    "quality_score": 0.967
  }
}
```

---

## 4. data-import-match-master

### Function: data-import-match-master

**Path**: `/functions/v1/data-import-match-master`  
**Method**: POST  
**Timeout**: 60s

### Input

```json
{
  "file_id": "uuid-v4",
  "records": [
    {
      "row_index": 0,
      "master_data_type": "counterparty",
      "source_values": {
        "name": "北京科技有限公司",
        "code": "91110000..."
      }
    }
  ],
  "confidence_threshold": 0.8
}
```

### Output

```json
{
  "success": true,
  "file_id": "uuid-v4",
  "matches": [
    {
      "row_index": 0,
      "master_data_type": "counterparty",
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
  ],
  "statistics": {
    "total_records": 100,
    "matched_records": 95,
    "unmatched_records": 5,
    "multiple_match_records": 3
  }
}
```

---

## 5. data-import-match-headers

### Function: data-import-match-headers

**Path**: `/functions/v1/data-import-match-headers`  
**Method**: POST  
**Timeout**: 30s

### Input

```json
{
  "document_numbers": ["PO001", "PO002", "PO003"],
  "document_type": "purchase_order",
  "table_name": "doc_purchase_order_header"
}
```

### Output

```json
{
  "success": true,
  "matches": [
    {
      "document_number": "PO001",
      "header_id": "uuid-123",
      "confidence": 1.0,
      "found": true,
      "header_info": {
        "id": "uuid-123",
        "document_number": "PO001",
        "document_date": "2025-01-01",
        "customer_name": "客户A"
      }
    },
    {
      "document_number": "PO999",
      "header_id": null,
      "confidence": 0.0,
      "found": false,
      "message": "系统中未找到单据号PO999的单据头记录"
    }
  ],
  "unmatched_count": 1
}
```

---

## 6. data-import-history

### Function: data-import-history

**Path**: `/functions/v1/data-import-history`  
**Method**: GET  
**Timeout**: 10s

### Input

**Query Parameters**:
- `tenant_id`: string (必需)
- `limit`: number (可选, 默认50)
- `offset`: number (可选, 默认0)
- `status`: string (可选, uploaded/processing/completed/failed)

### Output

```json
{
  "success": true,
  "history": [
    {
      "file_id": "uuid-v4",
      "file_name": "example.xlsx",
      "file_size": 1024000,
      "row_count": 1500,
      "status": "completed",
      "uploaded_at": "2025-01-23T10:00:00Z",
      "completed_at": "2025-01-23T10:05:00Z",
      "quality_score": 0.95
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

---

## 7. data-import-cleanup

### Function: data-import-cleanup

**Path**: `/functions/v1/data-import-cleanup`  
**Method**: POST  
**Timeout**: 30s

### Input

```json
{
  "file_ids": ["uuid-1", "uuid-2"],
  "delete_storage": true,
  "delete_database": true
}
```

### Output

```json
{
  "success": true,
  "deleted_files": 2,
  "deleted_storage_files": 2,
  "deleted_database_records": 2
}
```

---

## 📦 依赖项

### Deno 标准库
- `https://deno.land/std@0.168.0/http/server.ts` - HTTP服务器
- `https://deno.land/std@0.168.0/streams/` - 流处理

### 外部库
- `@supabase/supabase-js@2` - Supabase客户端
- `xlsx` 或 `exceljs` - Excel解析
- `csv-parse` - CSV解析

---

## 🔐 认证和授权

所有 Edge Functions 需要：
1. **认证**: 通过 Supabase Auth JWT Token
2. **授权**: 验证 `tenant_id` 和 `user_id` 权限
3. **RLS**: 数据库层面行级安全策略

---

## 📊 性能要求

| Function | 最大执行时间 | 最大内存 | 最大文件大小 |
|----------|------------|---------|-------------|
| data-import-upload | 60s | 512MB | 50MB |
| data-import-analyze | 30s | 256MB | N/A |
| data-import-validate | 60s | 512MB | N/A |
| data-import-match-master | 60s | 256MB | N/A |
| data-import-match-headers | 30s | 128MB | N/A |
| data-import-history | 10s | 64MB | N/A |
| data-import-cleanup | 30s | 128MB | N/A |

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

