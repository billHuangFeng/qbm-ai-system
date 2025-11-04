# Edge Functions 测试用例

## 测试环境配置

### 前置条件
1. Supabase 项目已初始化
2. 数据库表已创建
3. 存储桶已配置
4. 用户已注册并获取 JWT Token

### 测试数据准备
```sql
-- 插入测试租户
INSERT INTO tenants (tenant_code, tenant_name, industry)
VALUES ('T001', 'Test Organization', 'Technology');

-- 插入测试用户配置
INSERT INTO user_profiles (user_id, tenant_id, email, full_name)
VALUES (
  'test-user-id',
  (SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'),
  'test@example.com',
  'Test User'
);

-- 插入测试主数据
INSERT INTO dim_customer (tenant_id, customer_code, customer_name, customer_segment, region)
VALUES 
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'C001', '阿里巴巴', 'A', '杭州'),
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'C002', '腾讯科技', 'A', '深圳'),
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'C003', '百度公司', 'B', '北京');

INSERT INTO dim_sku (tenant_id, sku_code, sku_name, category, unit_price)
VALUES
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'SKU001', 'iPhone 15 Pro', '手机', 7999),
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'SKU002', 'MacBook Pro', '电脑', 12999),
  ((SELECT tenant_id FROM tenants WHERE tenant_code = 'T001'), 'SKU003', 'AirPods Pro', '耳机', 1999);
```

## 1. data-import-upload 测试用例

### Test Case 1.1: CSV 文件上传 - 重复单据头格式
**目的**: 测试格式1识别（多行明细对应重复单据头）

**测试数据**: `test_data_format1.csv`
```csv
单据号,单据日期,客户名称,产品名称,数量,单价,金额
SO001,2024-01-15,阿里巴巴,iPhone 15 Pro,10,7999,79990
SO001,2024-01-15,阿里巴巴,MacBook Pro,5,12999,64995
SO001,2024-01-15,阿里巴巴,AirPods Pro,20,1999,39980
SO002,2024-01-16,腾讯科技,iPhone 15 Pro,15,7999,119985
SO002,2024-01-16,腾讯科技,AirPods Pro,30,1999,59970
```

**cURL 命令**:
```bash
curl -X POST 'https://fmpnelntcmvjvhsavkmv.supabase.co/functions/v1/data-import-upload' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'apikey: YOUR_SUPABASE_ANON_KEY' \
  -F 'file=@test_data_format1.csv' \
  -F 'source_system=erp' \
  -F 'document_type=sales_order'
```

**预期结果**:
```json
{
  "success": true,
  "file_id": "uuid",
  "file_name": "test_data_format1.csv",
  "file_size": 350,
  "row_count": 5,
  "column_count": 7,
  "format_detection": {
    "format_type": "repeated_header",
    "confidence": 0.85,
    "details": {
      "uniqueDocs": 2,
      "totalRows": 5,
      "duplicateRatio": 0.6
    }
  }
}
```

### Test Case 1.2: Excel 文件上传 - 第一行单据头格式
**目的**: 测试格式2识别（多行明细但只有第一行有单据头）

**测试数据**: `test_data_format2.xlsx`
| 单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 单价 |
|--------|----------|----------|----------|------|------|
| SO003 | 2024-01-17 | 百度公司 | iPhone 15 Pro | 8 | 7999 |
| | | | MacBook Pro | 3 | 12999 |
| | | | AirPods Pro | 15 | 1999 |

**cURL 命令**:
```bash
curl -X POST 'https://fmpnelntcmvjvhsavkmv.supabase.co/functions/v1/data-import-upload' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'apikey: YOUR_SUPABASE_ANON_KEY' \
  -F 'file=@test_data_format2.xlsx' \
  -F 'source_system=erp'
```

**预期结果**:
```json
{
  "success": true,
  "format_detection": {
    "format_type": "first_row_header",
    "confidence": 0.90
  }
}
```

### Test Case 1.3: 文件大小超限
**目的**: 测试文件大小验证

**测试数据**: 创建大于50MB的文件

**预期结果**:
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "文件大小超过限制（最大50MB）"
  }
}
```

### Test Case 1.4: 不支持的文件格式
**目的**: 测试文件格式验证

**测试数据**: `test_data.pdf`

**预期结果**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式，仅支持 CSV, Excel, JSON"
  }
}
```

### Test Case 1.5: 未提供认证
**目的**: 测试认证机制

**cURL 命令**:
```bash
curl -X POST 'https://fmpnelntcmvjvhsavkmv.supabase.co/functions/v1/data-import-upload' \
  -F 'file=@test_data_format1.csv'
```

**预期结果**:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "未提供认证信息"
  }
}
```

## 2. data-import-validate 测试用例 (待实现)

### Test Case 2.1: 完整数据验证
**输入**:
```json
{
  "file_id": "uploaded-file-uuid",
  "validation_rules": {
    "required_fields": ["单据号", "客户名称", "产品名称", "数量"],
    "max_null_ratio": 0.1,
    "check_duplicates": true
  }
}
```

**预期结果**:
```json
{
  "success": true,
  "quality_report": {
    "overall_quality_score": 0.95,
    "completeness_score": 1.0,
    "accuracy_score": 0.92,
    "consistency_score": 0.93,
    "issues": [
      {
        "type": "MISSING_VALUE",
        "severity": "warning",
        "field": "单价",
        "description": "检测到2个空值",
        "affected_rows": 2
      }
    ]
  }
}
```

### Test Case 2.2: 数据质量问题检测
**测试数据**: 包含空值、异常值的文件

**预期问题**:
- 必填字段缺失
- 数值字段包含非数字
- 日期格式不正确
- 重复记录
- 异常值（超出合理范围）

## 3. data-import-match-master 测试用例 (待实现)

### Test Case 3.1: 精确匹配
**输入**:
```json
{
  "file_id": "uploaded-file-uuid",
  "match_config": {
    "entity_type": "customer",
    "match_fields": ["客户名称"],
    "threshold": 0.8
  }
}
```

**预期结果**:
```json
{
  "success": true,
  "match_results": [
    {
      "source_value": "阿里巴巴",
      "matched": true,
      "master_id": "customer-uuid",
      "master_name": "阿里巴巴",
      "confidence": 1.0
    }
  ]
}
```

### Test Case 3.2: 模糊匹配
**输入**: 客户名称 "阿里巴巴网络技术有限公司"

**预期结果**:
```json
{
  "source_value": "阿里巴巴网络技术有限公司",
  "matched": true,
  "master_id": "customer-uuid",
  "master_name": "阿里巴巴",
  "confidence": 0.87,
  "candidates": [
    {
      "id": "customer-uuid",
      "name": "阿里巴巴",
      "similarity": 0.87
    }
  ]
}
```

### Test Case 3.3: 无匹配结果
**输入**: 客户名称 "不存在的公司"

**预期结果**:
```json
{
  "source_value": "不存在的公司",
  "matched": false,
  "confidence": 0.0,
  "candidates": []
}
```

## 4. data-import-extract-headers 测试用例 (待实现)

### Test Case 4.1: 格式1提取（重复单据头）
**输入**:
```json
{
  "file_id": "uploaded-file-uuid",
  "format_type": "repeated_header"
}
```

**预期结果**:
```json
{
  "success": true,
  "headers": [
    {
      "document_number": "SO001",
      "document_date": "2024-01-15",
      "customer_name": "阿里巴巴",
      "total_amount": 184965,
      "detail_row_indices": [0, 1, 2]
    },
    {
      "document_number": "SO002",
      "document_date": "2024-01-16",
      "customer_name": "腾讯科技",
      "total_amount": 179955,
      "detail_row_indices": [3, 4]
    }
  ]
}
```

### Test Case 4.2: 格式2提取（第一行单据头）
**预期结果**: 从第一行提取单据头信息，将后续行作为明细

## 5. data-import-execute 测试用例 (待实现)

### Test Case 5.1: 插入模式导入
**输入**:
```json
{
  "file_id": "uploaded-file-uuid",
  "target_table": "fact_order",
  "field_mapping": {
    "单据号": "order_id",
    "客户名称": "customer_id",
    "产品名称": "sku_id",
    "数量": "quantity",
    "金额": "order_amount",
    "单据日期": "order_date"
  },
  "import_mode": "insert"
}
```

**预期结果**:
```json
{
  "success": true,
  "import_id": "import-log-uuid",
  "stats": {
    "total_rows": 5,
    "success_rows": 5,
    "failed_rows": 0,
    "skipped_rows": 0,
    "duration_ms": 1250
  }
}
```

### Test Case 5.2: 更新模式导入
**输入**: 包含已存在记录的数据，使用 `upsert` 模式

**预期结果**: 已存在记录被更新，新记录被插入

### Test Case 5.3: 导入失败回滚
**输入**: 包含无效数据的文件

**预期结果**:
```json
{
  "success": false,
  "import_id": "import-log-uuid",
  "stats": {
    "total_rows": 5,
    "success_rows": 0,
    "failed_rows": 5,
    "skipped_rows": 0,
    "duration_ms": 500
  },
  "errors": [
    {
      "row_index": 2,
      "error_message": "客户ID不存在"
    },
    {
      "row_index": 4,
      "error_message": "数量字段必须为正数"
    }
  ]
}
```

## 6. 集成测试场景

### 场景1: 完整导入流程
```
1. 上传文件 (data-import-upload)
   ↓
2. 验证数据 (data-import-validate)
   ↓
3. 匹配主数据 (data-import-match-master)
   ↓
4. 提取单据头 (data-import-extract-headers)
   ↓
5. 执行导入 (data-import-execute)
   ↓
6. 查询导入结果
```

### 场景2: 错误处理流程
```
1. 上传包含错误的文件
   ↓
2. 验证失败，返回质量报告
   ↓
3. 用户修正数据后重新上传
   ↓
4. 验证通过，继续后续流程
```

### 场景3: 大文件导入
```
1. 上传50MB CSV文件（约50万行）
   ↓
2. 流式解析和验证
   ↓
3. 分批导入（每批10000行）
   ↓
4. 监控性能指标
```

## 7. 性能测试

### Test Case 7.1: 并发上传测试
- 同时上传10个文件
- 预期: 所有请求成功，平均响应时间 < 5秒

### Test Case 7.2: 大文件处理
- 文件大小: 50MB
- 行数: ~50万行
- 预期: 上传和解析成功，时间 < 30秒

### Test Case 7.3: 批量导入性能
- 数据量: 10万行
- 预期: 导入成功，速率 > 1000行/秒

## 8. 安全测试

### Test Case 8.1: 跨租户访问
- 用户A尝试访问用户B的文件
- 预期: 403 Forbidden

### Test Case 8.2: SQL注入防护
- 上传包含SQL注入代码的文件
- 预期: 安全处理，不执行恶意代码

### Test Case 8.3: 文件类型伪装
- 将可执行文件改为.csv扩展名
- 预期: 解析失败，返回错误

## 测试执行记录

### 执行日期: _________
### 执行人: _________
### 环境: Production / Staging / Development

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1.1 | ⬜ Pass ⬜ Fail | |
| 1.2 | ⬜ Pass ⬜ Fail | |
| 1.3 | ⬜ Pass ⬜ Fail | |
| 1.4 | ⬜ Pass ⬜ Fail | |
| 1.5 | ⬜ Pass ⬜ Fail | |
| 2.1 | ⬜ Pass ⬜ Fail | |
| 2.2 | ⬜ Pass ⬜ Fail | |
| 3.1 | ⬜ Pass ⬜ Fail | |
| 3.2 | ⬜ Pass ⬜ Fail | |
| 3.3 | ⬜ Pass ⬜ Fail | |
| 4.1 | ⬜ Pass ⬜ Fail | |
| 4.2 | ⬜ Pass ⬜ Fail | |
| 5.1 | ⬜ Pass ⬜ Fail | |
| 5.2 | ⬜ Pass ⬜ Fail | |
| 5.3 | ⬜ Pass ⬜ Fail | |
