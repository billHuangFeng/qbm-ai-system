# BMOS API 使用示例文档

## 📚 目录
1. [认证和授权](#认证和授权)
2. [数据导入](#数据导入)
3. [AI Copilot](#ai-copilot)
4. [模型训练](#模型训练)
5. [数据分析](#数据分析)
6. [企业记忆](#企业记忆)
7. [预测服务](#预测服务)
8. [任务调度](#任务调度)
9. [监控和告警](#监控和告警)

---

## 认证和授权

### 1. 用户注册

**请求示例：**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "role": "analyst",
    "tenant_id": "tenant001"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "注册成功",
  "user": {
    "id": "user_123",
    "username": "testuser",
    "email": "test@example.com",
    "role": "analyst",
    "tenant_id": "tenant001",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

### 2. 用户登录

**请求示例：**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!",
    "tenant_id": "tenant001"
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": "user_123",
    "username": "testuser",
    "email": "test@example.com",
    "role": "analyst",
    "tenant_id": "tenant001"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

### 3. 刷新令牌

**请求示例：**
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "refresh_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## 数据导入

### 1. 上传并分析文件

**请求示例：**
```bash
curl -X POST http://localhost:8000/data-import/upload \
  -F "file=@sales_data.xlsx" \
  -F "source_type=excel"
```

**响应示例：**
```json
{
  "success": true,
  "file_info": {
    "filename": "sales_data.xlsx",
    "size": 245760,
    "source_type": "excel",
    "upload_time": "2024-01-15T10:30:00"
  },
  "detected_format": "single_header_multi_rows",
  "data_preview": [
    {
      "sheet": "Sheet1",
      "row": 1,
      "data": {
        "date": "2024-01-01",
        "product": "产品A",
        "sales": 10000,
        "quantity": 100
      }
    }
  ],
  "suggested_mappings": [
    {
      "source_field": "date",
      "target_field": "date",
      "data_type": "date",
      "is_required": true
    },
    {
      "source_field": "sales",
      "target_field": "amount",
      "data_type": "float",
      "is_required": true
    }
  ],
  "quality_assessment": {
    "overall_score": 0.92,
    "quality_level": "good",
    "issues": [],
    "warnings": ["第5行数据可能异常"]
  }
}
```

### 2. 执行数据导入

**请求示例：**
```bash
curl -X POST http://localhost:8000/data-import/import \
  -F "file=@sales_data.xlsx" \
  -F "source_type=excel" \
  -F "document_format=single_header_multi_rows" \
  -F 'field_mappings=[{"source_field":"date","target_field":"date","data_type":"date"}]' \
  -F "target_table=fact_sales" \
  -F 'import_config={"load_mode":"insert","batch_size":1000}'
```

### 3. 查询导入状态

**请求示例：**
```bash
curl -X GET http://localhost:8000/data-import/status/import_20240115_103000
```

---

## AI Copilot

### 1. 与AI对话

**请求示例：**
```bash
curl -X POST http://localhost:8000/ai-copilot/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "message": "帮我分析一下上个月销售额下降的原因",
    "user_id": "user_123",
    "session_id": "session_001"
  }'
```

**响应示例：**
```json
{
  "status": "success",
  "user_input": "帮我分析一下上个月销售额下降的原因",
  "analysis_results": [
    {
      "analysis_type": "marginal_analysis",
      "scenario": "sales_decline_analysis",
      "marginal_effects": {
        "product_A": -0.15,
        "product_B": -0.20,
        "marketing_impact": -0.10
      },
      "recommendations": ["优化产品A定价策略", "加强产品B营销"]
    }
  ],
  "synthesis": "根据分析结果，上个月销售额下降15%，主要原因包括：1. 产品A销量下降20%；2. 产品B需求减少；3. 营销投入效果不佳。建议调整产品定价和营销策略。",
  "insights": [
    "产品A价格敏感度上升",
    "产品B市场竞争力下降",
    "营销ROI下降"
  ],
  "recommendations": [
    "优化产品A定价策略",
    "加强产品B营销",
    "重新评估营销渠道"
  ],
  "next_actions": [
    "深入分析产品A的价格弹性",
    "研究产品B的市场竞争格局",
    "评估营销预算分配"
  ]
}
```

### 2. 直接执行工具

**请求示例：**
```bash
curl -X POST http://localhost:8000/ai-copilot/execute-tool \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "tool_id": "marginal_analysis",
    "parameters": {
      "business_scenario": "sales_optimization",
      "decision_variables": ["price", "marketing_budget"],
      "time_horizon": 12
    },
    "user_id": "user_123",
    "session_id": "session_001"
  }'
```

### 3. 获取可用工具列表

**请求示例：**
```bash
curl -X GET http://localhost:8000/ai-copilot/tools
```

---

## 模型训练

### 1. 训练新模型

**请求示例：**
```bash
curl -X POST http://localhost:8000/model-training/train \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "model_type": "marginal_analysis",
    "training_data": "historical_sales",
    "features": ["price", "marketing", "seasonality"],
    "target": "sales_volume",
    "hyperparameters": {
      "n_estimators": 100,
      "max_depth": 10,
      "learning_rate": 0.1
    }
  }'
```

**响应示例：**
```json
{
  "success": true,
  "training_id": "training_123",
  "model_id": "model_456",
  "status": "training",
  "progress": 0.25,
  "estimated_completion": "2024-01-15T11:00:00"
}
```

### 2. 查询训练状态

**请求示例：**
```bash
curl -X GET http://localhost:8000/model-training/status/training_123
```

### 3. 获取模型列表

**请求示例：**
```bash
curl -X GET http://localhost:8000/model-training/models
```

---

## 数据分析

### 1. 边际影响分析

**请求示例：**
```bash
curl -X POST http://localhost:8000/analysis/marginal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "business_scenario": "product_pricing",
    "decision_variables": ["price", "quality"],
    "time_horizon": 12,
    "target_metric": "profit"
  }'
```

### 2. 协同效应分析

**请求示例：**
```bash
curl -X POST http://localhost:8000/analysis/synergy \
  -H "Content-Type: application/json" \
  -d '{
    "feature_data": {
      "features": [[100, 10, 5], [110, 12, 6]],
      "target": [1000, 1150]
    },
    "target_metric": "sales",
    "analysis_depth": "deep"
  }'
```

---

## 企业记忆

### 1. 提取企业记忆

**请求示例：**
```bash
curl -X POST http://localhost:8000/enterprise-memory/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "event_type": "decision_success",
    "context": {
      "decision": "pricing_strategy",
      "outcome": "positive",
      "metrics": {"revenue_increase": 0.15}
    },
    "insights": ["定价策略调整成功提升收入15%"]
  }'
```

### 2. 检索相关知识

**请求示例：**
```bash
curl -X GET "http://localhost:8000/enterprise-memory/search?query=pricing&limit=10"
```

### 3. 应用学习经验

**请求示例：**
```bash
curl -X POST http://localhost:8000/enterprise-memory/apply \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "new_product_pricing",
    "similar_past_cases": ["case_001", "case_002"],
    "adaptation_strategy": "conservative_increase"
  }'
```

---

## 预测服务

### 1. 生成预测

**请求示例：**
```bash
curl -X POST http://localhost:8000/predictions/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "model_id": "model_456",
    "input_data": {
      "price": 100,
      "marketing": 50,
      "seasonality": 1.2
    },
    "forecast_horizon": 12,
    "confidence_level": 0.95
  }'
```

**响应示例：**
```json
{
  "prediction_id": "pred_789",
  "model_id": "model_456",
  "predictions": [
    {"period": 1, "value": 1100, "confidence": 0.95},
    {"period": 2, "value": 1150, "confidence": 0.93}
  ],
  "metrics": {
    "mae": 50,
    "rmse": 75,
    "r2_score": 0.85
  }
}
```

### 2. 批量预测

**请求示例：**
```bash
curl -X POST http://localhost:8000/predictions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_456",
    "input_data": [
      {"price": 100, "marketing": 50},
      {"price": 110, "marketing": 60}
    ]
  }'
```

---

## 任务调度

### 1. 创建定时任务

**请求示例：**
```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "每日数据质量检查",
    "description": "每天凌晨检查数据质量",
    "function_name": "data_quality_check",
    "parameters": {
      "dataset_id": "dataset_001",
      "dataset_name": "销售数据"
    },
    "schedule_type": "daily",
    "schedule_config": {
      "time": "02:00"
    },
    "priority": 2,
    "max_retries": 3
  }'
```

### 2. 立即执行任务

**请求示例：**
```bash
curl -X POST http://localhost:8000/scheduler/tasks/task_123/execute
```

### 3. 获取调度器统计

**请求示例：**
```bash
curl -X GET http://localhost:8000/scheduler/stats
```

---

## 监控和告警

### 1. 获取系统指标

**请求示例：**
```bash
curl -X GET http://localhost:8000/monitoring/metrics
```

**响应示例：**
```json
{
  "cpu": {
    "percent": 35.5,
    "cores": 8
  },
  "memory": {
    "total": 17179869184,
    "available": 8589934592,
    "percent": 50.0,
    "used": 8589934592
  },
  "disk": {
    "total": 500107862016,
    "used": 250053931008,
    "free": 250053931008,
    "percent": 50.0
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. 创建告警规则

**请求示例：**
```bash
curl -X POST http://localhost:8000/monitoring/alerts/rules \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "CPU使用率过高",
    "metric_name": "cpu.percent",
    "condition": "gt",
    "threshold": 80.0,
    "severity": "high",
    "notification_channels": ["email", "slack"]
  }'
```

### 3. 获取活跃告警

**请求示例：**
```bash
curl -X GET "http://localhost:8000/monitoring/alerts?status=active&severity=high"
```

---

## 错误处理

所有API都返回统一的错误格式：

```json
{
  "success": false,
  "error_code": 400,
  "message": "请求参数无效",
  "details": {
    "field": "email",
    "issue": "邮箱格式不正确"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## 常见HTTP状态码

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 权限不足
- `404 Not Found` - 资源不存在
- `422 Unprocessable Entity` - 数据验证失败
- `500 Internal Server Error` - 服务器错误

## 完整代码示例

### Python示例

```python
import httpx
import asyncio

class BMOSClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def chat_with_copilot(self, message: str):
        """与AI Copilot聊天"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ai-copilot/chat",
                headers=self.headers,
                json={
                    "message": message,
                    "user_id": "user_123",
                    "session_id": "session_001"
                }
            )
            return response.json()
    
    async def import_data(self, file_path: str):
        """导入数据"""
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = await client.post(
                    f"{self.base_url}/data-import/upload",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data={"source_type": "excel"}
                )
                return response.json()

# 使用示例
async def main():
    client = BMOSClient("http://localhost:8000", "your_token_here")
    
    # 与AI聊天
    result = await client.chat_with_copilot("分析销售趋势")
    print(result)
    
    # 导入数据
    import_result = await client.import_data("sales_data.xlsx")
    print(import_result)

asyncio.run(main())
```

### JavaScript/TypeScript示例

```typescript
class BMOSClient {
  constructor(private baseUrl: string, private token: string) {}
  
  async chatWithCopilot(message: string) {
    const response = await fetch(`${this.baseUrl}/ai-copilot/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        user_id: 'user_123',
        session_id: 'session_001'
      })
    });
    return await response.json();
  }
  
  async importData(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', 'excel');
    
    const response = await fetch(`${this.baseUrl}/data-import/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    return await response.json();
  }
}

// 使用示例
const client = new BMOSClient('http://localhost:8000', 'your_token_here');

// 与AI聊天
const result = await client.chatWithCopilot('分析销售趋势');
console.log(result);

// 导入数据
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const importResult = await client.importData(file);
console.log(importResult);
```

## 最佳实践

1. **使用连接池** - 复用HTTP连接以提高性能
2. **错误重试** - 实现指数退避重试机制
3. **超时设置** - 为所有请求设置合理的超时时间
4. **认证管理** - 定期刷新访问令牌
5. **日志记录** - 记录所有API调用以便调试
6. **数据验证** - 客户端也要验证数据格式
7. **缓存策略** - 对GET请求实现适当的缓存

