# FastAPI 与 Edge Functions 分工决策指南

**创建时间**: 2025-10-31  
**版本**: 2.0  
**重要更新**: 2025-01-23

---

## ⚠️ 重要技术栈约束

**Lovable只能使用Supabase Edge Functions，不能使用FastAPI Python后端。**

这意味着：
- ✅ **所有新功能**必须使用Edge Functions实现
- ✅ **所有算法**必须转换为TypeScript
- ✅ **所有API端点**必须设计为Edge Functions格式
- ❌ **不能使用**FastAPI Python后端（即使复杂算法也必须简化）

**注意**: 本文档保留FastAPI相关描述仅作为参考（历史文档或Cursor内部使用），但Lovable实施时**必须**使用Edge Functions。

---

## 📋 目的

本指南帮助开发团队明确判断新功能应该部署在 **Supabase Edge Functions**（Lovable实施），确保架构合理性和性能优化。

**注意**: 如果功能不符合Edge Functions标准，Cursor需要：
1. 简化算法使其符合Edge Functions限制
2. 或使用外部服务
3. 或移除该功能

---

## 🎯 决策流程（Lovable实施）

```
新功能需求
    ↓
评估功能特性
    ↓
┌───────────────────────┐
│ 是否符合 Edge Functions │
│     适用标准？          │
└───────────────────────┘
    ↓ Yes          ↓ No
Edge Functions   简化算法/外部服务/移除
    ↓              ↓
实施             重新评估
```

**关键**: 如果功能不符合Edge Functions标准，Cursor必须：
1. **简化算法**: 将复杂算法简化为Edge Functions可实现的版本
2. **使用外部服务**: 如果必须使用Python库（如OCR），使用外部API
3. **移除功能**: 如果无法简化且无替代方案，则移除该功能

**不能选择**: 保持在FastAPI（Lovable无法使用）

---

## ✅ Edge Functions 适用标准

### 必须满足以下所有条件：

1. **执行时间**: ≤ 10秒
   - ✅ 简单查询和处理
   - ✅ 轻量级验证
   - ✅ 快速响应需求

2. **计算复杂度**: O(n) 或更低
   - ✅ 线性时间算法
   - ✅ 简单循环和过滤
   - ❌ O(n²)、O(n!) 等复杂算法

3. **依赖库**: 仅 Supabase SDK
   - ✅ 只需 `@supabase/supabase-js`
   - ❌ 需要外部Python/Node库

4. **数据量**: 单次处理 < 1MB
   - ✅ 小批量数据处理
   - ❌ 大文件处理

5. **功能类型**:
   - ✅ 简单 CRUD 操作
   - ✅ 轻量级数据验证
   - ✅ 数据库查询封装
   - ✅ 实时数据同步
   - ✅ 身份认证和授权

---

## ❌ 不符合Edge Functions标准的处理方案

**⚠️ 重要**: 如果功能符合以下条件，**不能**保持在FastAPI（Lovable无法使用），必须：

### 方案A: 简化算法使其符合Edge Functions

**适用于**: 计算复杂度 O(n²) 或更高，但有简化可能性

**示例**:
- ❌ XGBoost → ✅ 线性回归 + 特征工程（TypeScript）
- ❌ ARIMA → ✅ 移动平均 + 线性趋势（TypeScript）
- ❌ MLP → ✅ 加权评分 + 规则引擎（TypeScript）

### 方案B: 使用外部服务

**适用于**: 必须使用Python特定库（如OCR、文档处理）

**示例**:
- ❌ pytesseract → ✅ Cloud Vision API / Tesseract.js API
- ❌ python-docx → ✅ CloudConvert API / 前端预处理
- ❌ sentence-transformers → ✅ Pinecone API / 关键词搜索

### 方案C: 移除功能或延迟实施

**适用于**: 无法简化且无替代方案

**示例**:
- ❌ Shapley归因（O(n!)） → ⚠️ 使用线性归因或首次/末次归因
- ❌ 复杂图神经网络 → ⚠️ 使用简化的图遍历算法

---

## 📊 决策矩阵（Lovable实施）

| 功能特性 | Edge Functions | 不符合标准的处理 | 示例 |
|---------|---------------|----------------|------|
| **执行时间** | < 10秒 | 分批处理/简化算法 | 大数据集分批处理 |
| **计算复杂度** | O(n) | 简化算法 | XGBoost → 线性回归 |
| **依赖库** | 仅Supabase SDK | 外部API或简化 | OCR → Cloud Vision API |
| **数据量** | < 1MB | 分批处理 | 大数据集分批导入 |
| **CRUD操作** | ✅ | - | 管理者评价 → Edge Functions |
| **复杂算法** | 简化版本 ✅ | 简化为O(n)版本 | XGBoost → 线性回归 |
| **实时同步** | ✅ | - | 数据同步 → Edge Functions |
| **模型训练** | ❌ | 预训练模型或外部服务 | 使用预训练权重 |
| **ML算法** | 简化版本 ✅ | 线性回归/规则引擎 | MLP → 加权评分 |

**关键**: 所有不符合Edge Functions标准的功能都必须：
1. ✅ 简化为Edge Functions可实现的版本，或
2. ✅ 使用外部服务，或
3. ✅ 移除功能

---

## 🔍 实际案例

### ✅ Edge Functions 案例

1. **管理者评价** (`manager-evaluation`)
   - ✅ 简单CRUD操作
   - ✅ 数据验证和保存
   - ✅ 执行时间 < 2秒
   - ✅ 仅需Supabase SDK

2. **预测误差追踪** (`prediction-error-tracker`)
   - ✅ 数据库查询和过滤
   - ✅ 简单统计分析
   - ✅ 执行时间 < 5秒

3. **TOC瓶颈识别** (`toc-bottleneck`)
   - ✅ 简单计算（找最小值）
   - ✅ O(n)复杂度
   - ✅ 执行时间 < 1秒

### ⚠️ 不符合Edge Functions标准的处理案例

1. **Shapley归因** (`shapley-attribution`)
   - ❌ 原: O(n!)复杂度，需要蒙特卡洛采样
   - ✅ 处理: 简化为线性归因或首次/末次归因（TypeScript）

2. **AI核心服务** (战略层、复盘等)
   - ❌ 原: 复杂机器学习算法（XGBoost, ARIMA等）
   - ✅ 处理: 简化为线性回归、移动平均等（TypeScript）
   - 📚 参见: [TypeScript算法实现指南](./algorithms/TYPESCRIPT_ALGORITHMS.md)

3. **文档处理** (Word/PPT/OCR)
   - ❌ 原: 需要python-docx, python-pptx, pytesseract
   - ✅ 处理: 使用外部API（CloudConvert, Cloud Vision）或前端预处理

4. **语义搜索**
   - ❌ 原: 需要sentence-transformers
   - ✅ 处理: 使用外部向量数据库API（Pinecone）或仅关键词搜索

### ✅ 复杂功能的简化案例

1. **数据导入** (`data-import`)
   - ✅ **Edge Functions**: 简单验证和写入（< 1MB, < 10,000行）
   - ✅ **分批处理**: 大数据集分批处理（Edge Functions）
   - ⚠️ **复杂ETL**: 简化为Edge Functions可实现的ETL逻辑

---

## 🚀 实施建议

### 1. 新功能开发流程（Lovable实施）

```
1. 评估功能特性
   ├── 检查执行时间需求
   ├── 检查计算复杂度
   ├── 检查依赖库需求
   └── 检查数据量

2. 应用决策标准
   ├── 符合Edge Functions标准 → 使用Edge Functions ✅
   ├── 不符合Edge Functions标准 → 简化算法/外部服务/移除 ⚠️
   └── 不能选择 → 保持在FastAPI ❌

3. 实施和测试
   ├── 实现功能（Edge Functions或简化版本）
   ├── 性能测试（确保≤10秒，O(n)复杂度）
   └── 验证决策正确性
```

**关键**: 所有功能最终必须在Edge Functions实现（简化版本）或使用外部服务。

### 2. 迁移指南

如果发现现有功能部署位置不合理：

1. **评估迁移成本**
   - 代码重写工作量
   - 测试成本
   - 用户体验影响

2. **制定迁移计划**
   - 分阶段迁移
   - 保持向后兼容
   - 更新文档

3. **执行迁移**
   - 实现新位置的功能
   - 测试验证
   - 更新调用方
   - 废弃旧实现

---

## 📚 相关文档

- [优化计划文档](./FASTAPI_EDGE_FUNCTIONS_OPTIMIZATION_PLAN.md)
- [Edge Functions规范](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)
- [FastAPI完成模块](./CURSOR_COMPLETED_MODULES.md)

---

## ✅ 总结

### ⚠️ 重要更新（2025-01-23）

**Lovable只能使用Edge Functions，不能使用FastAPI。**

**核心原则**:
- **Edge Functions**: Lovable实施的标准方式 ✅
- **不符合Edge Functions标准**: 必须简化、使用外部服务或移除 ⚠️
- **FastAPI**: 不能使用（Lovable无法访问）❌

**决策口诀**（Lovable实施）:
- 10秒内完成 → Edge Functions ✅
- 需要Python库 → 使用外部API或简化算法 ✅
- 复杂算法 → 简化为Edge Functions可实现的版本 ✅
- 简单CRUD → Edge Functions ✅
- 无法简化且无替代 → 移除功能或使用外部服务 ✅

**不能选择**:
- ❌ 保持在FastAPI（Lovable无法使用）

---

## 📚 相关文档

- [Python到TypeScript迁移计划](./PYTHON_TO_TYPESCRIPT_MIGRATION_PLAN.md) - 详细的迁移计划
- [TypeScript算法实现指南](./algorithms/TYPESCRIPT_ALGORITHMS.md) - 算法TypeScript实现
- [Edge Functions API设计模板](./api/EDGE_FUNCTIONS_API_TEMPLATE.md) - API设计模板
- [Edge Functions规范](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)
- [FastAPI完成模块](./CURSOR_COMPLETED_MODULES.md) - 参考（历史文档）

---

**文档版本**: 2.0  
**最后更新**: 2025-01-23  
**重要变更**: 明确Lovable只能使用Edge Functions，所有不符合标准的功能必须简化或使用外部服务


