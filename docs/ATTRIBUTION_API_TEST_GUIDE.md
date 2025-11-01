# Shapley归因API测试指南

**创建时间**: 2025-10-31  
**状态**: ✅ **API已实现**

---

## 📋 API端点

### 1. 健康检查

**端点**: `GET /attribution/health`

**响应**:
```json
{
  "status": "ok",
  "service": "attribution"
}
```

---

### 2. 单个订单归因

**端点**: `POST /attribution/shapley`

**请求体**:
```json
{
  "order_id": "order-001",
  "touchpoints": [
    {
      "id": "tp-001",
      "type": "media",
      "timestamp": "2024-01-01T10:00:00Z",
      "cost": 100.0,
      "quality_score": 0.8
    },
    {
      "id": "tp-002",
      "type": "channel",
      "timestamp": "2024-01-02T14:00:00Z",
      "cost": 50.0
    }
  ],
  "conversion_value": 1000.0,
  "method": "monte_carlo"
}
```

**响应**:
```json
{
  "order_id": "order-001",
  "attribution": {
    "tp-001": 0.65,
    "tp-002": 0.35
  },
  "method": "monte_carlo",
  "touchpoint_count": 2
}
```

---

### 3. 批量订单归因

**端点**: `POST /attribution/shapley/batch`

**请求体**:
```json
{
  "orders": [
    {
      "order_id": "order-001",
      "customer_id": "cust-001",
      "amount": 1000.0
    },
    {
      "order_id": "order-002",
      "customer_id": "cust-002",
      "amount": 2000.0
    }
  ],
  "touchpoint_journey": {
    "order-001": [
      {
        "id": "tp-001",
        "type": "media",
        "timestamp": "2024-01-01T10:00:00Z",
        "cost": 100.0
      }
    ],
    "order-002": [
      {
        "id": "tp-002",
        "type": "channel",
        "timestamp": "2024-01-02T14:00:00Z",
        "cost": 200.0
      }
    ]
  }
}
```

**响应**:
```json
{
  "results": {
    "order-001": {
      "tp-001": 1.0
    },
    "order-002": {
      "tp-002": 1.0
    }
  }
}
```

---

## 🧪 测试方法

### 1. 使用curl测试

```bash
# 健康检查
curl http://localhost:8081/attribution/health

# 单个订单归因
curl -X POST http://localhost:8081/attribution/shapley \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-001",
    "touchpoints": [
      {
        "id": "tp-001",
        "type": "media",
        "timestamp": "2024-01-01T10:00:00Z",
        "cost": 100.0
      },
      {
        "id": "tp-002",
        "type": "channel",
        "timestamp": "2024-01-02T14:00:00Z",
        "cost": 50.0
      }
    ],
    "conversion_value": 1000.0,
    "method": "monte_carlo"
  }'
```

### 2. 使用pytest测试

```bash
cd qbm-ai-system/backend
pytest tests/test_attribution.py -v
```

### 3. 使用Python测试

```python
import requests

url = "http://localhost:8081/attribution/shapley"
data = {
    "order_id": "order-001",
    "touchpoints": [
        {
            "id": "tp-001",
            "type": "media",
            "timestamp": "2024-01-01T10:00:00Z",
            "cost": 100.0
        }
    ],
    "conversion_value": 1000.0
}

response = requests.post(url, json=data)
print(response.json())
```

---

## 📊 测试用例

### 测试用例1: 单触点

- **输入**: 1个触点
- **预期**: 归因权重为1.0（100%）
- **方法**: 完全枚举

### 测试用例2: 多触点（小规模）

- **输入**: 3-10个触点
- **预期**: 归因权重总和为1.0
- **方法**: 完全枚举或蒙特卡洛

### 测试用例3: 多触点（大规模）

- **输入**: > 10个触点
- **预期**: 归因权重总和为1.0
- **方法**: 蒙特卡洛采样

### 测试用例4: 批量归因

- **输入**: 多个订单
- **预期**: 每个订单都有正确的归因结果
- **方法**: 批量处理

---

## ✅ 验证标准

1. **功能正确性**
   - ✅ 单触点归因权重为1.0
   - ✅ 多触点归因权重总和接近1.0（允许浮点误差）
   - ✅ 所有触点都有非负权重
   - ✅ 权重范围在[0, 1]之间

2. **性能要求**
   - ✅ 小规模（≤10触点）响应时间 < 1秒
   - ✅ 大规模（>10触点）响应时间 < 5秒
   - ✅ 批量处理（10个订单）响应时间 < 10秒

3. **错误处理**
   - ✅ 空触点列表返回空结果
   - ✅ 无效输入返回400错误
   - ✅ 服务器错误返回500错误

---

## 🔍 调试建议

1. **检查服务状态**
   ```bash
   curl http://localhost:8081/attribution/health
   ```

2. **查看API文档**
   ```
   http://localhost:8081/docs
   ```

3. **检查日志**
   - 查看服务日志中的错误信息
   - 检查numpy库是否正确安装

4. **验证输入格式**
   - 确保触点数据格式正确
   - 确保时间戳格式符合ISO 8601

---

## 📚 相关文档

- [优化计划文档](./FASTAPI_EDGE_FUNCTIONS_OPTIMIZATION_PLAN.md)
- [决策指南文档](./FASTAPI_EDGE_FUNCTIONS_DECISION_GUIDE.md)
- [Edge Functions规范](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)

---

**文档版本**: 1.0  
**最后更新**: 2025-10-31


