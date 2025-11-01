# QBM AI System - 用户培训指南

## 🎯 系统概述

QBM AI System是一个智能化的企业决策管理系统，通过AI技术帮助企业进行战略规划、目标管理和决策制定。

### 核心功能
- **智能战略管理** - 协同分析、权重优化、趋势预测
- **智能制定闭环** - 对齐检查、冲突预测、基线生成
- **智能推荐系统** - 最佳实践、相似模式、优化建议
- **企业记忆系统** - "越用越聪明"的知识积累

---

## 🚀 快速开始

### 1. 系统访问
- **API文档**: http://localhost:8000/docs
- **管理界面**: http://localhost:8000/admin (待开发)
- **健康检查**: http://localhost:8000/health

### 2. 认证方式
系统使用JWT Token进行身份认证：
```bash
# 获取Token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 使用Token
curl -X GET "http://localhost:8000/ai-strategic/metrics/primary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 功能模块详解

### 1. AI战略层管理

#### 1.1 战略目标管理
**功能**: 创建和管理企业战略目标

**API端点**:
```bash
# 创建战略目标
POST /ai-strategic/objectives/create

# 获取目标列表
GET /ai-strategic/objectives

# 更新目标
PUT /ai-strategic/objectives/{objective_id}

# 删除目标
DELETE /ai-strategic/objectives/{objective_id}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/ai-strategic/objectives/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_name": "市场扩张",
    "description": "在未来2年内将市场份额提升至30%",
    "priority": "high",
    "target_date": "2025-12-31",
    "success_metrics": ["市场份额", "收入增长", "客户数量"]
  }'
```

#### 1.2 北极星指标管理
**功能**: 管理和优化关键业务指标

**核心API**:
```bash
# 创建北极星指标
POST /ai-strategic/metric/create

# 获取指标健康度
GET /ai-strategic/metric/{metric_id}/health

# 更新指标值
POST /ai-strategic/metric/{metric_id}/update-values

# 获取主要指标
GET /ai-strategic/metrics/primary
```

**使用示例**:
```bash
# 创建指标
curl -X POST "http://localhost:8000/ai-strategic/metric/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "月活跃用户数",
    "metric_type": "user_engagement",
    "target_value": 1000000,
    "current_value": 750000,
    "unit": "users",
    "frequency": "monthly"
  }'

# 查看健康度
curl -X GET "http://localhost:8000/ai-strategic/metric/1/health" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 1.3 OKR管理
**功能**: 创建和管理目标与关键结果

**核心API**:
```bash
# 创建OKR
POST /ai-strategic/okr/create

# 创建关键结果
POST /ai-strategic/okr/{okr_id}/key-result/create

# 更新KR进度
POST /ai-strategic/okr/{okr_id}/key-result/{kr_id}/update-progress

# 获取OKR预测
GET /ai-strategic/okr/{okr_id}/prediction
```

**使用示例**:
```bash
# 创建OKR
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

# 添加关键结果
curl -X POST "http://localhost:8000/ai-strategic/okr/1/key-result/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kr_name": "新增用户数达到10万",
    "target_value": 100000,
    "current_value": 25000,
    "unit": "users"
  }'
```

### 2. AI制定闭环管理

#### 2.1 决策对齐检查
**功能**: 检查决策间的一致性和对齐度

**核心API**:
```bash
# 检查决策对齐
POST /ai-planning/check-alignment

# 预测决策冲突
POST /ai-planning/predict-conflicts

# 获取对齐报告
GET /ai-planning/alignment-report/{decision_id}
```

**使用示例**:
```bash
# 检查对齐
curl -X POST "http://localhost:8000/ai-planning/check-alignment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision_123",
    "check_type": "full_alignment",
    "related_decisions": ["decision_456", "decision_789"]
  }'
```

#### 2.2 基线生成
**功能**: 生成决策执行基线并预测结果

**核心API**:
```bash
# 生成基线
POST /ai-planning/generate-baseline

# 获取基线详情
GET /ai-planning/baseline/{baseline_id}

# 优化基线参数
POST /ai-planning/optimize-baseline
```

**使用示例**:
```bash
# 生成基线
curl -X POST "http://localhost:8000/ai-planning/generate-baseline" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "decision_123",
    "baseline_name": "Q1营销基线",
    "include_predictions": true,
    "prediction_periods": 4
  }'
```

#### 2.3 需求深度分析
**功能**: 深度分析决策需求并推荐最佳实践

**核心API**:
```bash
# 深度分析需求
POST /ai-planning/analyze-requirement

# 获取相似需求
GET /ai-planning/requirement/{requirement_id}/similar
```

**使用示例**:
```bash
# 分析需求
curl -X POST "http://localhost:8000/ai-planning/analyze-requirement" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement_id": "req_123",
    "analysis_type": "full"
  }'
```

---

## 🤖 AI功能使用指南

### 1. 协同效应分析
**用途**: 分析多个目标或决策间的协同效应

**使用场景**:
- 制定年度战略计划时
- 评估新项目对现有目标的影响
- 优化资源配置

**API调用**:
```bash
curl -X POST "http://localhost:8000/ai-strategic/analyze-synergy" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "objectives": ["objective_1", "objective_2", "objective_3"],
    "analysis_type": "comprehensive"
  }'
```

### 2. 指标推荐
**用途**: 基于历史数据和业务目标推荐关键指标

**使用场景**:
- 新业务线指标设计
- 现有指标体系优化
- 对标分析

**API调用**:
```bash
curl -X POST "http://localhost:8000/ai-strategic/recommend-metrics" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_domain": "ecommerce",
    "target_objectives": ["revenue_growth", "customer_satisfaction"],
    "time_horizon": "quarterly"
  }'
```

### 3. 冲突预测
**用途**: 预测决策间可能产生的冲突

**使用场景**:
- 多部门协调决策
- 资源分配冲突预警
- 时间线冲突检测

**API调用**:
```bash
curl -X POST "http://localhost:8000/ai-strategic/predict-conflicts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": ["decision_1", "decision_2"],
    "time_range": "2025-01-01 to 2025-12-31"
  }'
```

---

## 📈 最佳实践

### 1. 数据质量
- **定期更新数据**: 确保指标和目标的实时性
- **数据验证**: 使用系统内置的数据质量检查
- **历史数据积累**: 系统"越用越聪明"需要足够的历史数据

### 2. 目标设定
- **SMART原则**: 确保目标具体、可衡量、可达成、相关、有时限
- **层次化设计**: 战略目标 → OKR → 关键结果
- **定期回顾**: 建议每月回顾一次OKR进度

### 3. 决策流程
- **对齐检查**: 重大决策前先进行对齐检查
- **基线生成**: 为重要决策生成执行基线
- **持续监控**: 定期检查决策执行情况

### 4. 团队协作
- **权限管理**: 合理分配用户权限
- **沟通机制**: 利用系统推荐的最佳实践
- **知识共享**: 充分利用企业记忆功能

---

## 🔧 常见问题解答

### Q1: 如何提高AI预测的准确性？
**A**: 
1. 提供更多历史数据
2. 确保数据质量
3. 定期更新模型
4. 使用系统推荐的指标

### Q2: 系统推荐的最佳实践可信吗？
**A**: 
1. 基于企业历史数据
2. 结合行业最佳实践
3. 持续学习和优化
4. 建议结合实际情况判断

### Q3: 如何处理决策冲突？
**A**: 
1. 使用冲突预测功能
2. 分析冲突原因
3. 调整决策优先级
4. 重新分配资源

### Q4: 系统性能如何优化？
**A**: 
1. 定期清理历史数据
2. 使用缓存功能
3. 合理设置预测参数
4. 监控系统资源使用

---

## 📚 进阶使用

### 1. 自定义AI模型
系统支持自定义AI模型训练，可以针对特定业务场景优化预测准确性。

### 2. 集成外部系统
通过API接口，可以与其他企业系统集成，实现数据自动同步。

### 3. 高级分析
利用系统的高级分析功能，进行更深入的业务洞察。

---

## 🆘 技术支持

### 获取帮助
1. **API文档**: http://localhost:8000/docs
2. **系统日志**: 查看 `logs/app.log`
3. **健康检查**: http://localhost:8000/health
4. **技术支持**: 联系系统管理员

### 反馈建议
欢迎提供使用反馈和改进建议，帮助系统持续优化！

---

**开始使用QBM AI System，让AI助力您的企业决策！** 🚀

