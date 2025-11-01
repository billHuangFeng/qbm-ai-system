# AI增强战略层服务

本模块提供AI增强的战略层管理服务，集成多种AI算法实现智能化的战略目标、指标、OKR和需求管理。

## 📁 服务列表

### 1. AIStrategicObjectivesService
**功能**: AI增强战略目标管理服务
- **集成算法**: SynergyAnalysis（协同效应分析）、ThresholdAnalysis（阈值识别）
- **主要功能**:
  - 创建战略目标并自动进行协同效应分析
  - 识别关键阈值指标
  - 批量分析目标协同效应
  - 更新目标并重新分析

**示例用法**:
```python
from src.services.ai_strategic_layer import AIStrategicObjectivesService

service = AIStrategicObjectivesService(db_service, memory_service)

# 创建战略目标
result = await service.create_strategic_objective(
    objective_name="用户增长战略",
    objective_type="strategic_goal",
    objective_content="在未来3年内实现1000万用户，年增长率30%",
    parent_objective_id=parent_id
)

# 分析协同效应
synergy = result["synergy_analysis"]
print(f"协同效应得分: {synergy['synergy_score']}")
```

### 2. AINorthStarService
**功能**: AI驱动北极星指标推荐服务
- **集成算法**: DynamicWeights（动态权重优化）、ARIMAModel（时间序列预测）
- **主要功能**:
  - 创建北极星指标并自动计算AI权重
  - AI预测指标趋势（ARIMA模型）
  - 推荐相关指标（基于企业记忆系统）
  - 计算指标健康度评分
  - 批量更新指标值
  - 指标对比分析

**示例用法**:
```python
from src.services.ai_strategic_layer import AINorthStarService

service = AINorthStarService(db_service, memory_service)

# 创建北极星指标
result = await service.create_north_star_metric(
    metric_name="月活跃用户数",
    metric_description="每月活跃用户数量",
    strategic_objective_id=objective_id,
    metric_type="growth",
    target_value=1000000.0
)

# 获取指标健康度
health = await service.calculate_metric_health_score(metric_id)
print(f"健康度得分: {health['health_score']}, 状态: {health['status']}")

# 更新指标值
await service.update_metric_value(
    metric_id=metric_id,
    metric_value=850000.0
)
```

### 3. AIOKRService
**功能**: AI增强OKR管理服务
- **集成算法**: XGBoost（达成概率预测）、企业记忆系统（最佳实践推荐）
- **主要功能**:
  - 创建OKR并自动预测达成概率
  - 创建关键结果（KR）
  - 更新KR进度并重新预测
  - 推荐最佳实践
  - 识别风险因素

**示例用法**:
```python
from src.services.ai_strategic_layer import AIOKRService

service = AIOKRService(db_service, memory_service)

# 创建OKR
result = await service.create_okr(
    okr_name="Q1用户增长",
    objective_statement="在第一季度实现30%的用户增长",
    strategic_objective_id=objective_id,
    period_type="quarterly",
    period_start="2025-01-01",
    period_end="2025-03-31"
)

print(f"达成概率: {result['achievement_prediction']['probability']}")
print(f"最佳实践: {result['best_practices']}")

# 创建关键结果
kr_result = await service.create_key_result(
    okr_id=result["okr_id"],
    kr_name="新用户获取",
    kr_statement="在第一季度获取10000新用户",
    kr_type="metric",
    target_value=10000.0
)

# 更新进度
await service.update_key_result_progress(
    kr_id=kr_result["kr_id"],
    current_value=8500.0,
    current_progress=85.0
)
```

### 4. AIDecisionRequirementsService
**功能**: AI需求分析服务
- **集成算法**: MLPModel（优先级预测）、企业记忆系统（相似需求分析）
- **主要功能**:
  - 创建决策需求并自动分析优先级
  - 查找相似的历史需求
  - 推荐最佳实践
  - 风险评估

**示例用法**:
```python
from src.services.ai_strategic_layer import AIDecisionRequirementsService

service = AIDecisionRequirementsService(db_service, memory_service)

# 创建需求
result = await service.create_requirement(
    requirement_title="增加营销预算",
    requirement_description="需要增加Q1营销预算以支持用户增长目标",
    requirement_type="strategic",
    parent_decision_id=decision_id,
    strategic_objective_id=objective_id,
    requester_id="user_123",
    requester_name="张三",
    required_by_date="2025-06-30"
)

print(f"优先级得分: {result['priority_analysis']['priority_score']}")
print(f"优先级等级: {result['priority_analysis']['priority_level']}")
print(f"相似需求: {result['similar_requirements']}")
```

## 🔌 API端点

所有服务都通过REST API暴露，端点前缀：`/ai-strategic`

### AI分析端点

1. **协同效应分析**
   - `POST /ai-strategic/analyze-synergy`
   - 请求体: `{ "objective_id": "...", "related_objective_ids": [...] }`

2. **指标推荐**
   - `POST /ai-strategic/recommend-metrics`
   - 请求体: `{ "strategic_objective_id": "...", "context": {...} }`

3. **冲突预测**
   - `POST /ai-strategic/predict-conflicts`
   - 请求体: `{ "decision_ids": [...], "check_type": "full_alignment" }`

4. **基线生成**
   - `POST /ai-strategic/generate-baseline`
   - 请求体: `{ "decision_id": "...", "baseline_name": "...", "include_predictions": true }`

### CRUD端点

#### OKR管理
- `POST /ai-strategic/okr/create` - 创建OKR
- `POST /ai-strategic/okr/{okr_id}/key-result/create` - 创建关键结果
- `POST /ai-strategic/okr/{okr_id}/key-result/{kr_id}/update-progress` - 更新KR进度
- `GET /ai-strategic/okr/{okr_id}` - 获取OKR详情
- `GET /ai-strategic/okr/{okr_id}/prediction` - 获取OKR达成概率预测
- `GET /ai-strategic/okr/by-objective/{strategic_objective_id}` - 获取指定目标下的所有OKR

#### 需求管理
- `POST /ai-strategic/requirement/create` - 创建决策需求
- `GET /ai-strategic/requirement/{requirement_id}` - 获取需求详情
- `GET /ai-strategic/requirement/{requirement_id}/priority` - 获取需求优先级分析

#### 指标管理
- `POST /ai-strategic/metric/create` - 创建北极星指标
- `GET /ai-strategic/metric/{metric_id}` - 获取指标详情
- `GET /ai-strategic/metric/{metric_id}/health` - 获取指标健康度评分

### 完整API文档

访问 `/docs` 查看完整的Swagger API文档，包含所有端点的详细说明和请求/响应示例。

## 🤖 AI算法集成详情

### SynergyAnalysis（协同效应分析）
- **用途**: 分析战略目标之间的协同效应
- **输入**: 目标特征数据（优先级、内容长度、数值指标等）
- **输出**: 协同效应得分、详细分析结果
- **应用**: `AIStrategicObjectivesService._analyze_synergy()`

### ThresholdAnalysis（阈值识别）
- **用途**: 识别目标中的关键阈值指标
- **输入**: 目标内容中的数值数据
- **输出**: 阈值指标列表，包含阈值值和置信度
- **应用**: `AIStrategicObjectivesService._identify_threshold_indicators()`

### DynamicWeights（动态权重）
- **用途**: 优化北极星指标的权重分配
- **输入**: 历史指标数据和目标值
- **输出**: 优化的权重值、权重详细信息
- **应用**: `AINorthStarService._calculate_ai_weight()`

### ARIMAModel（时间序列预测）
- **用途**: 预测指标的未来趋势
- **输入**: 指标历史值（至少10个数据点）
- **输出**: 预测值、置信区间、模型质量评估
- **应用**: `AINorthStarService._predict_trend()`

### XGBoost（达成概率预测）
- **用途**: 预测OKR的达成概率
- **输入**: OKR特征（KR数量、进度、历史成功率等）
- **输出**: 达成概率、影响因素分析
- **应用**: `AIOKRService._predict_achievement_probability()`

### MLPModel（优先级预测）
- **用途**: 预测决策需求的优先级
- **输入**: 需求特征（类型、时间紧急度、战略关联度等）
- **输出**: 优先级得分、优先级等级（1-10）
- **应用**: `AIDecisionRequirementsService._analyze_priority()`

## 📊 数据流

```
用户请求
    ↓
API端点 (ai_strategic_layer.py)
    ↓
服务层 (ai_*_service.py)
    ↓
AI算法层 (algorithms/*.py)
    ↓
数据库/企业记忆系统
    ↓
返回AI增强的结果
```

## 🔄 服务依赖

所有服务依赖以下基础服务：
- `DatabaseService`: 数据库操作
- `EnterpriseMemoryService`: 企业记忆系统（推荐最佳实践、查找相似模式）

## ⚙️ 初始化

```python
from src.services.database_service import DatabaseService
from src.services.enhanced_enterprise_memory import EnterpriseMemoryService
from src.services.ai_strategic_layer import (
    AIStrategicObjectivesService,
    AINorthStarService,
    AIOKRService,
    AIDecisionRequirementsService
)

# 初始化基础服务
db_service = DatabaseService()
memory_service = EnterpriseMemoryService()

# 初始化AI战略层服务
strategic_service = AIStrategicObjectivesService(db_service, memory_service)
north_star_service = AINorthStarService(db_service, memory_service)
okr_service = AIOKRService(db_service, memory_service)
requirements_service = AIDecisionRequirementsService(db_service, memory_service)
```

## 📈 性能优化建议

1. **缓存AI分析结果**: 对于不常变化的目标和指标，可以缓存AI分析结果
2. **批量处理**: 使用批量更新接口减少数据库查询次数
3. **异步处理**: 长时间运行的AI分析可以使用后台任务
4. **历史数据预加载**: 预加载常用历史数据以加速模型训练

## 🧪 测试

运行测试：
```bash
pytest tests/test_ai_strategic_layer.py -v
```

测试覆盖：
- 服务功能测试
- AI算法集成测试
- API端点测试
- 端到端工作流测试

## 📝 注意事项

1. **数据要求**: 
   - ARIMA预测需要至少10个历史数据点
   - XGBoost预测需要至少10条历史OKR记录
   - MLP优先级预测需要至少20条历史需求记录

2. **错误处理**: 
   - 所有服务都有完善的错误处理和回退机制
   - 当AI算法失败时，会自动回退到基于规则的方法

3. **性能**: 
   - AI模型训练可能需要几秒到几十秒
   - 建议对耗时操作使用异步处理和缓存

## 🔗 相关文档

- [数据库表结构](../database/postgresql/15_ai_strategic_layer.sql)
- [API文档](../../api/endpoints/ai_strategic_layer.py)
- [测试用例](../../../tests/test_ai_strategic_layer.py)

