# BMOS API参考文档

## 数据导入

### POST /api/data-import/upload

上传原始数据到暂存表。

**请求体**:
```json
{
  "sourceSystem": "erp|crm|oa|manual",
  "sourceType": "expense|asset|order|feedback",
  "rawData": {},
  "importMethod": "manual|api|file"
}
```

**响应**:
```json
{
  "success": true,
  "rawId": "uuid"
}
```

### POST /api/data-import/transform

将原始数据转化为业务事实表数据。

**请求体**:
```json
{
  "rawId": "uuid"
}
```

**响应**:
```json
{
  "success": true
}
```

## 决策循环

### POST /api/decision-cycle/execute

执行决策循环分析。

**请求体**:
```json
{
  "triggerId": "uuid|manual"
}
```

**响应**:
```json
{
  "success": true,
  "executionId": "uuid",
  "evaluationTaskId": "uuid"
}
```

### GET /api/decision-cycle/status

获取决策循环执行状态。

**响应**:
```json
{
  "executions": [],
  "triggers": []
}
```

## 管理者评价

### POST /api/manager-evaluation/submit

提交管理者评价和确认。

**请求体**:
```json
{
  "analysisId": "uuid",
  "evaluationType": "confirm|clarify|adjust",
  "evaluationContent": "string",
  "metricAdjustments": [
    {
      "metricId": "uuid",
      "newValue": 0.85,
      "confidence": 0.9
    }
  ]
}
```

**响应**:
```json
{
  "success": true
}
```

### GET /api/manager-evaluation/tasks

获取待评价任务列表。

**响应**:
```json
{
  "tasks": []
}
```

## 分析引擎

### POST /api/analysis/shapley-attribution

执行Shapley归因分析。

**请求体**:
```json
{
  "orderId": "uuid"
}
```

**响应**:
```json
{
  "success": true,
  "shapleyValues": {
    "touchpoint1": 0.3,
    "touchpoint2": 0.7
  }
}
```

### POST /api/analysis/marginal-impact

分析边际影响。

**请求体**:
```json
{
  "decisionId": "uuid",
  "businessFactType": "expense|asset|order"
}
```

**响应**:
```json
{
  "success": true,
  "marginalImpact": {
    "revenue": 10000,
    "cost": 5000,
    "profit": 5000,
    "roi": 1.0
  }
}
```

### POST /api/analysis/value-increment

计算价值增量。

**请求体**:
```json
{
  "decisionId": "uuid"
}
```

**响应**:
```json
{
  "success": true,
  "valueIncrement": {
    "totalValueIncrement": 15000,
    "breakdown": {
      "directImpact": 10000,
      "indirectImpact": 3000,
      "timeSeriesImpact": 2000
    }
  }
}
```

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 405 | 方法不允许 |
| 500 | 服务器内部错误 |

## 认证

所有API请求需要在请求头中包含用户认证信息：

```
Authorization: Bearer <token>
```

或者通过请求头传递用户ID：

```
user-id: <user-uuid>
```
