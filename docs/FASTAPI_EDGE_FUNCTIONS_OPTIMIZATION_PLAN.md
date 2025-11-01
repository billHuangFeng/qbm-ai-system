# FastAPI 与 Edge Functions 分工优化计划

**创建时间**: 2025-10-31  
**状态**: 🚀 **实施中**

---

## 📋 优化目标

明确 FastAPI 与 Edge Functions 的分工边界，优化架构合理性，提高系统性能和可维护性。

---

## 🎯 核心改进点

### 1. 立即调整：`shapley-attribution` 移到 FastAPI ✅

**原因**: 
- 时间复杂度 O(n!)，不适合 Edge Functions 的执行时间限制
- 需要复杂算法计算，应该使用 Python 生态库

**实施方案**:
- 在 FastAPI 中创建 `/api/attribution/shapley` 端点
- Edge Functions 中移除 `shapley-attribution`（或改为代理路由）
- 使用 Python 的算法库实现完整功能

---

### 2. 细化 `data-import` 分工 ⚠️

**当前问题**: 
- 简单导入和复杂 ETL 混在一起
- 需要明确边界

**实施方案**:
- **Edge Functions**: 简单验证和写入
- **FastAPI**: 复杂 ETL、数据转换、质量检查

---

### 3. 建立决策标准文档 ✅

**实施方案**:
- 创建明确的分工决策流程
- 定义判断标准（执行时间、复杂度、依赖库等）
- 更新架构文档

---

## 📊 改进前后对比

### 改进前 ❌

| 功能 | 计划位置 | 问题 |
|------|---------|------|
| `shapley-attribution` | Edge Functions | ❌ O(n!) 复杂算法，不适合边缘 |
| `data-import` | Edge Functions | ⚠️ 简单和复杂逻辑未分离 |
| `decision-cycle` | Edge Functions | ⚠️ 可能后续变复杂 |

### 改进后 ✅

| 功能 | 位置 | 理由 |
|------|------|------|
| `shapley-attribution` | **FastAPI** | ✅ 复杂算法，需要 Python 库 |
| `data-import` (简单) | **Edge Functions** | ✅ 快速验证和写入 |
| `data-import` (复杂) | **FastAPI** | ✅ ETL、转换、质量检查 |
| `decision-cycle` | **Edge Functions** | ✅ 当前简单，后续可迁移 |

---

## 🔧 实施步骤

### Phase 1: 立即调整（1-2天）

1. ✅ 创建 FastAPI 的 `shapley-attribution` 端点
2. ✅ 实现 Shapley 值计算算法（使用 Python）
3. ✅ 更新 Edge Functions 规范文档
4. ✅ 更新架构文档

### Phase 2: 细化分工（2-3天）

1. ✅ 分析 `data-import` 的具体需求
2. ✅ 分离简单和复杂逻辑
3. ✅ 定义 Edge Functions 简单导入规范
4. ✅ 定义 FastAPI 复杂 ETL 规范
5. ✅ 创建路由决策指南
6. ⏳ 实现 Edge Functions 简单导入（Lovable）
7. ⏳ 优化 FastAPI 复杂 ETL（如需要）

### Phase 3: 建立标准（1天）

1. ⏳ 创建分工决策标准文档
2. ⏳ 更新架构设计文档
3. ⏳ 创建决策流程图

---

## 📐 分工决策标准

### Edge Functions 适合 ✅

1. **执行时间**: < 10秒
2. **计算复杂度**: O(n) 或更低
3. **依赖**: 仅 Supabase SDK，无需外部库
4. **数据量**: 单次处理 < 1MB
5. **功能类型**: 
   - 简单 CRUD
   - 轻量级数据验证
   - 数据库查询封装
   - 实时数据同步

### FastAPI 适合 ✅

1. **执行时间**: 无限制（支持异步任务）
2. **计算复杂度**: O(n²) 或更高
3. **依赖**: 需要 Python 生态库（pandas、numpy、scikit-learn 等）
4. **数据量**: 支持大文件处理
5. **功能类型**:
   - 复杂算法计算
   - 机器学习模型训练
   - 长时间运行任务
   - 大量数据处理
   - 文档处理（OCR、Word/PPT）

---

## 🚀 实施进度

- [x] Phase 1: 创建优化计划文档 ✅
- [x] Phase 1: 实现 FastAPI shapley-attribution 端点 ✅
- [x] Phase 1: 创建 ShapleyAttributionService 服务 ✅
- [x] Phase 1: 更新 Edge Functions 规范文档 ✅
- [x] Phase 1: 创建决策指南文档 ✅
- [x] Phase 1: 创建测试文件 ✅
- [ ] Phase 1: 运行测试验证功能
- [x] Phase 2: 细化 data-import 分工 ✅
  - [x] Phase 2.1: 定义Edge Functions简单导入规范 ✅
  - [x] Phase 2.2: 定义FastAPI复杂ETL规范 ✅
  - [x] Phase 2.3: 创建路由决策指南 ✅
- [x] Phase 3: 建立决策标准 ✅

---

## 📚 相关文档

- [架构设计文档](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)
- [FastAPI 后端设计](../CURSOR_COMPLETED_MODULES.md)
- [系统状态报告](../SYSTEM_STATUS_REPORT.md)

---

**下一步**: 开始实施 Phase 1 - 创建 FastAPI shapley-attribution 端点

