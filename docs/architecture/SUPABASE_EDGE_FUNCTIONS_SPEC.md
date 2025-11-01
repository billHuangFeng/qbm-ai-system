# Supabase Edge Functions - 契约与伪代码

本规范定义 5 个核心函数的输入/输出、错误码与伪代码，供 Lovable 在 Supabase Edge Functions 上实现。

通用规范
- 请求与响应均为 JSON
- Header 需包含 Authorization(可选)；写入操作使用 service role 或 RLS 允许的策略
- 统一错误结构：`{ success: false, error: string }`

## 1) 数据导入 data-import ⚠️ 分工调整

**⚠️ 重要说明**: `data-import` 功能现在分为两部分：
- **Edge Functions**: 处理简单导入（CSV/JSON，< 1MB，< 10,000行）
- **FastAPI**: 处理复杂ETL（Excel/XML，复杂转换，深度质量检查）

### Edge Functions: 简单导入

**适用范围**:
- ✅ CSV或JSON格式
- ✅ 文件大小 < 1MB
- ✅ 数据行数 < 10,000行
- ✅ 简单字段映射
- ✅ 基础质量检查

**路径**: `/functions/v1/data-import`  
**方法**: POST

**输入**:
```json
{
  "sourceSystem": "erp|crm|oa|manual",
  "sourceType": "expense|asset|order|feedback",
  "rows": [ 
    { "field1": "value1", "field2": "value2", ... }
  ],
  "fileName": "optional.csv",
  "fieldMappings": {
    "field1": "target_field1"
  }
}
```

**输出**:
```json
{
  "success": true,
  "batchId": "uuid",
  "inserted": 120,
  "failed": 3,
  "issues": [
    {
      "rowIndex": 5,
      "issueType": "missing_required_field",
      "field": "amount",
      "suggestedFix": "default_value"
    }
  ]
}
```

**伪代码（Edge Functions）**:
```
validate input (sourceSystem, sourceType, rows非空)
create import_batch log (status='processing')
for each row:
  validate basic fields (必填、类型)
  apply field mappings (如果有)
  upsert into raw_data_staging(source_system, source_type, raw_data, import_method='api')
run basic quality checks -> write data_quality_check (必填、类型、范围)
update batch log with counts
return {success, batchId, inserted, failed, issues}
```

**限制**: 
- ❌ 不支持Excel/XML等复杂格式
- ❌ 不支持复杂ETL转换
- ❌ 不支持深度质量分析

**如果超出范围**: 应调用FastAPI `/api/v1/data-import/import` 端点

### FastAPI: 复杂ETL

**路径**: `POST /api/v1/data-import/import`  
**适用范围**: 
- Excel、XML等复杂格式
- 文件大小 ≥ 1MB
- 数据行数 ≥ 10,000行
- 需要复杂转换或深度质量检查

**详细信息**: 参见FastAPI API文档和 `docs/DATA_IMPORT_DIVISION_PLAN.md`

## 2) 管理者评价 manager-evaluation
- 路径：`/functions/v1/manager-evaluation`
- 方法：POST
- 输入：
```json
{
  "analysisId": "uuid",
  "evaluationType": "confirm|clarify|adjust",
  "evaluationContent": "string",
  "metricAdjustments": [ { "metricId": "uuid", "newValue": 0.85, "confidence": 0.9 } ]
}
```
- 输出：`{ "success": true }`
- 伪代码：
```
insert into manager_evaluation(...)
for each adjustment:
  insert into metric_confirmation(...)
call decision-cycle if follow-up needed
```

## 3) 决策循环 decision-cycle
- 路径：`/functions/v1/decision-cycle`
- 方法：POST
- 输入：
```json
{ "triggerId": "uuid|manual" }
```
- 输出：
```json
{ "success": true, "executionId": "uuid", "evaluationTaskId": "uuid" }
```
- 伪代码：
```
create execution record (running)
collect business facts (select from fact_* tables)
calculate metrics (simple placeholders)
create evaluation task (write to decision_cycle_execution.log)
update execution (waiting_evaluation)
```

## 4) Shapley 归因 shapley-attribution ⚠️ 已迁移到 FastAPI

**⚠️ 重要变更**: Shapley归因功能已从Edge Functions迁移到FastAPI后端。

**原因**:
- Shapley算法时间复杂度为O(n!)，不适合Edge Functions的执行时间限制
- 需要使用Python生态库（numpy）进行复杂计算
- 蒙特卡洛采样需要大量计算资源

**新的API端点**:
- FastAPI: `POST /attribution/shapley`
- 文档: 参见FastAPI API文档 (`/docs`)

**如果Edge Functions需要调用**:
可以使用Edge Functions作为代理路由，调用FastAPI服务：
```typescript
// Edge Functions 代理实现（可选）
const response = await fetch(`${FASTAPI_URL}/attribution/shapley`, {
  method: 'POST',
  body: JSON.stringify({ orderId, touchpoints, conversionValue })
});
return response;
```

**原Edge Functions实现**: 已移除，不再维护

## 5) TOC 瓶颈识别 toc-bottleneck
- 路径：`/functions/v1/toc-bottleneck`
- 方法：POST
- 输入：
```json
{
  "valueChain": [ { "id": "prod", "outputRate": 0.85 }, ... ]
}
```
- 输出：`{ "success": true, "bottleneckId": "prod" }`
- 伪代码：
```
if valueChain empty -> 400
bottleneck = reduce to min by outputRate
return {success, bottleneckId}
```

## 错误码约定
- 200：成功 `{ success: true }`
- 400：参数错误 `{ success: false, error: 'bad_request' }`
- 404：无数据 `{ success: false, error: 'not_found' }`
- 500：内部错误 `{ success: false, error: 'internal_error' }`

## 安全与 RLS
- 函数使用 SERVICE_ROLE_KEY 写入（或在表上配置合适的 RLS 策略）
- 建议对导入与执行记录表按 org_id 做行级隔离




