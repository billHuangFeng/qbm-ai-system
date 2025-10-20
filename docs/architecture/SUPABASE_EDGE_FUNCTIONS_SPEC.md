# Supabase Edge Functions - 契约与伪代码

本规范定义 5 个核心函数的输入/输出、错误码与伪代码，供 Lovable 在 Supabase Edge Functions 上实现。

通用规范
- 请求与响应均为 JSON
- Header 需包含 Authorization(可选)；写入操作使用 service role 或 RLS 允许的策略
- 统一错误结构：`{ success: false, error: string }`

## 1) 数据导入 data-import
- 路径：`/functions/v1/data-import`
- 方法：POST
- 输入：
```json
{
  "sourceSystem": "erp|crm|oa|manual",
  "sourceType": "expense|asset|order|feedback",
  "rows": [ { "...": "原始字段" } ],
  "fileName": "optional.csv"
}
```
- 输出：
```json
{ "success": true, "batchId": "uuid", "inserted": 120, "failed": 3 }
```
- 伪代码：
```
validate input
create import_batch log
for row in rows:
  upsert into raw_data_staging(source_system, source_type, raw_data, import_method='api')
run quality checks -> write data_quality_check
route by sourceType -> transform to fact tables
update batch log with counts
return {success, batchId, inserted, failed}
```

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

## 4) Shapley 归因 shapley-attribution
- 路径：`/functions/v1/shapley-attribution`
- 方法：POST
- 输入：`{ "orderId": "uuid" }`
- 输出：`{ "success": true, "shapleyValues": {"touchpointId": number} }`
- 伪代码（与前端一致，后续可替换为更优解）：
```
fetch touchpoints by orderId from customer_journey
if empty -> 404
values = calculateShapleyValues(touchpoints)
for tp in touchpoints:
  insert into bridge_attribution(order_id, touchpoint_type, touchpoint_id, attribution_value)
return {success, values}
```

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
