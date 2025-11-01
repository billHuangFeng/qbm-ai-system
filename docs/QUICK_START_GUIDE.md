# QBM AI System - 快速开始指南

## 🚀 快速启动

### 1. 环境准备

```bash
# 进入项目目录
cd qbm-ai-system/backend

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL="postgresql://user:password@localhost:5432/qbm_db"
export JWT_SECRET_KEY="your-secret-key-here"
```

### 2. 数据库初始化

```bash
# 运行数据库迁移
psql -U postgres -d qbm_db -f ../database/postgresql/15_ai_strategic_layer.sql
psql -U postgres -d qbm_db -f ../database/postgresql/16_ai_planning_loop.sql
```

### 3. 启动服务

```bash
# 启动FastAPI服务
python main.py

# 或者使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 API使用示例

### 示例1: 创建OKR并查看AI预测

```bash
# 1. 创建OKR
curl -X POST "http://localhost:8000/ai-strategic/okr/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "okr_name": "Q1用户增长",
    "objective_statement": "在第一季度实现30%的用户增长",
    "strategic_objective_id": "objective_123",
    "period_type": "quarterly",
    "period_start": "2025-01-01",
    "period_end": "2025-03-31"
  }'

# 响应示例：
# {
#   "success": true,
#   "okr_id": "okr_abc123",
#   "achievement_prediction": {
#     "probability": 0.75,
#     "confidence": 0.8
#   },
#   "best_practices": [...]
# }
```

### 示例2: 检查决策对齐

```bash
# 2. 检查决策对齐
curl -X POST "http://localhost:8000/ai-planning/check-alignment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision_123",
    "check_type": "full_alignment"
  }'

# 响应示例：
# {
#   "success": true,
#   "alignment_status": "pass",
#   "alignment_score": 0.85,
#   "check_results": {
#     "conflicts": {...},
#     "consistency": {...}
#   }
# }
```

### 示例3: 生成决策基线

```bash
# 3. 生成基线
curl -X POST "http://localhost:8000/ai-planning/generate-baseline" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision_123",
    "baseline_name": "Q1基线",
    "include_predictions": true,
    "prediction_periods": 4
  }'

# 响应示例：
# {
#   "success": true,
#   "baseline_id": "baseline_xyz789",
#   "ai_predictions": {
#     "predicted_outcomes": {...}
#   },
#   "ai_confidence": 0.75
# }
```

### 示例4: 深度分析需求

```bash
# 4. 深度分析需求
curl -X POST "http://localhost:8000/ai-planning/analyze-requirement" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_id": "req_123",
    "analysis_type": "full"
  }'

# 响应示例：
# {
#   "success": true,
#   "analysis_results": {
#     "similar_requirements": [...],
#     "threshold_indicators": [...],
#     "optimization_suggestions": [...]
#   }
# }
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行AI战略层测试
pytest tests/test_ai_strategic_layer.py -v

# 运行AI制定闭环测试
pytest tests/test_ai_planning_loop.py -v

# 运行特定测试
pytest tests/test_ai_strategic_layer.py::TestAINorthStarService::test_create_north_star_metric -v
```

---

## 📚 主要API端点速查

### AI战略层 (`/ai-strategic`)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/okr/create` | POST | 创建OKR |
| `/okr/{okr_id}` | GET | 获取OKR详情 |
| `/okr/{okr_id}/prediction` | GET | 获取达成概率预测 |
| `/metric/create` | POST | 创建北极星指标 |
| `/metric/{metric_id}/health` | GET | 获取指标健康度 |
| `/requirement/create` | POST | 创建决策需求 |

### AI制定闭环 (`/ai-planning`)

| 端点 | 方法 | 功能 |
|------|------|------|
| `/check-alignment` | POST | 检查决策对齐 |
| `/predict-conflicts` | POST | 预测决策冲突pattern |
| `/generate-baseline` | POST | 生成决策基线 |
| `/baseline/{baseline_id}` | GET | 获取基线详情 |
| `/analyze-requirement` | POST | 深度分析需求 |

---

## 🔧 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/qbm_db

# JWT配置
JWT_SECRET_KEY=your-secret-key-here

# 应用配置
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 数据库配置

确保PostgreSQL已启动并创建数据库：

```sql
CREATE DATABASE qbm_db;
\c qbm_db
平价
```

---

## 💡 常见问题

### Q1: 启动服务时提示数据库连接失败？

**A:** 检查：
1. PostgreSQL服务是否启动
2. DATABASE_URL环境变量是否正确
3. 数据库用户权限是否足够

### Q2: AI预测返回默认值？

**A:** 可能原因：
1. 历史数据不足（需要至少10条记录）
2. 数据质量不够（缺少必要字段）
3. 检查日志查看具体错误信息

### Q3: API返回401未授权？

**A:** 确保：
1. 请求头包含正确的Authorization token
2. Token未过期
3. 用户有相应权限

---

## 📖 更多文档

- [系统现状分析](./SYSTEM_STATUS_COMPREHENSIVE_ANALYSIS.md)
- [Phase 1完成总结](./PHASE1_FINAL_COMPLETION_REPORT.md)
- [API详细文档](../backend/src/api/endpoints/ai_strategic_layer.py)
- [服务使用指南](../backend/src/services/ai_strategic_layer/README.md)

---

## 🆘 获取帮助

如遇问题，请：
1. 查看日志：`logs/app.log`
2. 检查API文档：http://localhost:8000/docs
3. 查看测试用例了解用法

