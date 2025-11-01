# AI增强制定闭环服务

本模块提供AI增强的制定闭环管理服务，集成多种AI算法实现智能化的决策对齐检查、基线生成和需求分析。

## 📁 服务列表

### 1. AIAlignmentChecker
**功能**: AI决策对齐检查服务
- **集成算法**: RandomForest（冲突预测）、SynergyAnalysis（目标一致性分析）
- **主要功能**:
  - 检查决策对齐（完整对齐、资源冲突、目标一致性、循环依赖）
  - 预测决策冲突概率
  - 分析目标一致性
  - 检测循环依赖
  - 生成对齐建议

**示例用法**:
```python
from src.services.ai_planning_loop import AIAlignmentChecker

service = AIAlignmentChecker(db_service, memory_service)

# 检查决策对齐
result = await service.check_decision_alignment(
    decision_id="decision_123",
    check_type="full_alignment"
)

print(f"对齐状态: {result['alignment_status']}")
print(f"对齐得分: {result['alignment_score']}")
```

### 2. AIBaselineGenerator
**功能**: AI基线生成服务
- **集成算法**: VARModel（多变量时间序列预测）、LightGBM（参数优化）
- **主要功能**:
  - 生成决策基线快照
  - AI预测基线结果（支持多周期预测）
  - 优化基线参数
  - 风险评估

**示例用法**:
```python
from src.services.ai_planning_loop import AIBaselineGenerator

service = AIBaselineGenerator(db_service, memory_service)

# 生成基线
result = await service.generate_baseline(
    decision_id="decision_123",
    baseline_name="Q1基线",
    include_predictions=True,
    prediction_periods=4
)

print(f"基线ID: {result['baseline_id']}")
print(f"AI置信度: {result['ai_confidence']}")
print(f"预测结果: {result['ai_predictions']}")
```

### 3. AIRequirementAnalyzer
**功能**: AI需求深度分析服务
- **集成算法**: ThresholdAnalysis（关键需求识别）、企业记忆系统（相似需求查找）
- **主要功能**:
  - 深度分析需求（相似度、阈值、优化建议）
  - 查找相似历史需求
  - 识别关键需求阈值
  - 推荐需求优化建议
  - 风险评估和价值评估

**示例用法**:
```python
from src.services.ai_planning_loop import AIRequirementAnalyzer

service = AIRequirementAnalyzer(db_service, memory_service)

# 深度分析需求
result = await service.analyze_requirement_depth(
    requirement_id="req_123",
    analysis_type="full"
)

print(f"相似需求: {result['analysis_results']['similar_requirements']}")
print(f"关键阈值: {result['analysis_results']['threshold_indicators']}")
print(f"优化建议: {result['analysis_results']['optimization_suggestions']}")
```

## 🔌 API端点

所有服务都通过REST API暴露，端点前缀：`/ai-planning`

### 核心端点

1. **决策对齐检查**
   - `POST /ai-planning/check-alignment`
   - 请求体: `{ "decision_id": "...", "check_type": "full_alignment", "related_decision_ids": [...] }`

2. **冲突预测**
   - `POST /ai-planning/predict-conflicts`
   - 请求体: `{ "decision_id": "...", "related_decision_ids": [...] }`

3. **基线生成**
   - `POST /ai-planning/generate-baseline`
   - 请求体: `{ "decision_id": "...", "baseline_name": "...", "include_predictions": true, "prediction_periods": 4 }`

4. **需求深度分析**
   - `POST /ai-planning/analyze-requirement`
   - 请求体: `{ "requirement_id": "...", "analysis_type": "full" }`

### 辅助端点

- `GET /ai-planning/baseline/{baseline_id}` - 获取基线详情
- `GET /ai-planning/requirement/{requirement_id}/similar` - 获取相似需求
- `GET /ai-planning/alignment-report/{decision_id}` - 获取对齐检查报告
- `POST /ai-planning/optimize-baseline` - 优化基线参数

## 🤖 AI算法集成详情

### RandomForest（冲突预测）
- **用途**: 预测决策之间的冲突概率
- **输入**: 决策特征（预算、目标、资源等）
- **输出**: 冲突概率、具体冲突列表
- **应用**: `AIAlignmentChecker._predict_conflicts()`

### SynergyAnalysis（目标一致性）
- **用途**: 分析多个决策目标的协同效应和一致性
- **输入**: 目标特征矩阵
- **输出**: 一致性得分、协同效应分析
- **应用**: `AIAlignmentChecker._analyze_goal_consistency()`

### VARModel（基线预测）
- **用途**: 多变量时间序列预测基线结果
- **输入**: 历史基线数据（至少3个变量，10+条记录）
- **输出**: 未来多个周期的预测值
- **应用**: `AIBaselineGenerator._predict_baseline_outcomes()`

### LightGBM（参数优化和预测）
- **用途**: 优化基线参数或单变量预测
- **输入**: 特征数据和目标变量
- **输出**: 优化建议或预测值
- **应用**: `AIBaselineGenerator._optimize_baseline_parameters()`, `_predict_with_lightgbm()`

### ThresholdAnalysis（关键需求识别）
- **用途**: 识别需求中的关键阈值指标
- **输入**: 需求描述中的数值数据
- **输出**: 阈值指标列表
- **应用**: `AIRequirementAnalyzer._identify_critical_requirements()`

## 📊 数据流

```
用户请求
    ↓
API端点 (ai_planning_loop.py)
    ↓
服务层 (ai_planning_loop/*.py)
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
from src.services.ai_planning_loop import (
    AIAlignmentChecker,
    AIBaselineGenerator,
    AIRequirementAnalyzer
)

# 初始化基础服务
db_service = DatabaseService()
memory_service = EnterpriseMemoryService()

# 初始化AI制定闭环服务
alignment_checker = AIAlignmentChecker(db_service, memory_service)
baseline_generator = AIBaselineGenerator(db_service, memory_service)
requirement_analyzer = AIRequirementAnalyzer(db_service, memory_service)
```

## 📈 性能优化建议

1. **缓存对齐检查结果**: 对齐检查结果可以缓存，因为决策对齐关系不会频繁变化
2. **异步基线生成**: 基线生成可能耗时较长，建议使用后台任务
3. **批量需求分析**: 可以批量分析多个需求以提高效率
4. **历史数据预加载**: 预加载常用历史数据以加速模型训练

## 🧪 测试

运行测试：
```bash
pytest tests/test_ai_planning_loop.py -v
```

测试覆盖：
- 服务功能测试
- AI算法集成测试
- API端点测试
- 端到端工作流测试

## 📝 注意事项

1. **数据要求**: 
   - VARModel预测需要至少10条历史记录和3个变量
   - 对齐检查需要至少2个相关决策
   - 需求分析需要历史需求数据以提高准确性

2. **错误处理**: 
   - 所有服务都有完善的错误处理和回退机制
   - 当AI算法失败时，会自动回退到基于规则的方法

3. **性能**: 
   - 对齐检查可能需要几秒时间
   - 基线生成和预测可能需要10-30秒
   - 建议对耗时操作使用异步处理

## 🔗 相关文档

- [数据库表结构](../../../database/postgresql/16_ai_planning_loop.sql)
- [API文档](../../api/endpoints/ai_planning_loop.py)
- [测试用例](../../../tests/test_ai_planning_loop.py)

