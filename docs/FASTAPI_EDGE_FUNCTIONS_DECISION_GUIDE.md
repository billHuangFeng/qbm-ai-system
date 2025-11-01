# FastAPI 与 Edge Functions 分工决策指南

**创建时间**: 2025-10-31  
**版本**: 1.0

---

## 📋 目的

本指南帮助开发团队明确判断新功能应该部署在 **FastAPI 后端** 还是 **Supabase Edge Functions**，确保架构合理性和性能优化。

---

## 🎯 决策流程

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
Edge Functions    FastAPI
    ↓              ↓
实施             实施
```

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

## ✅ FastAPI 适用标准

### 满足以下任一条件即可：

1. **执行时间**: 无限制需求
   - ✅ 长时间运行任务
   - ✅ 异步处理需求
   - ✅ 后台任务

2. **计算复杂度**: O(n²) 或更高
   - ✅ 复杂算法计算
   - ✅ 机器学习推理
   - ✅ 图算法、优化算法

3. **依赖库**: 需要 Python 生态库
   - ✅ pandas, numpy, scikit-learn
   - ✅ 文档处理库（docx, pptx）
   - ✅ OCR库（pytesseract）
   - ✅ 语义搜索（sentence-transformers）

4. **数据量**: 大文件处理
   - ✅ 大量数据处理
   - ✅ 文件上传和处理
   - ✅ 批量导入导出

5. **功能类型**:
   - ✅ 复杂算法计算
   - ✅ 机器学习模型训练
   - ✅ 文档处理（Word/PPT/OCR）
   - ✅ 语义搜索
   - ✅ 长时间运行任务

---

## 📊 决策矩阵

| 功能特性 | Edge Functions | FastAPI | 示例 |
|---------|---------------|---------|------|
| **执行时间** | < 10秒 | 无限制 | - |
| **计算复杂度** | O(n) | O(n²)+ | Shapley归因 → FastAPI |
| **依赖库** | 仅Supabase SDK | Python库 | OCR → FastAPI |
| **数据量** | < 1MB | 大文件 | 数据导入 → 混合 |
| **CRUD操作** | ✅ | ⚠️ | 管理者评价 → Edge Functions |
| **复杂算法** | ❌ | ✅ | 协同效应分析 → FastAPI |
| **实时同步** | ✅ | ⚠️ | 数据同步 → Edge Functions |
| **模型训练** | ❌ | ✅ | 模型训练 → FastAPI |

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

### ✅ FastAPI 案例

1. **Shapley归因** (`shapley-attribution`)
   - ✅ O(n!)复杂度，需要蒙特卡洛采样
   - ✅ 需要numpy库
   - ✅ 执行时间可能 > 10秒
   - ✅ 已从Edge Functions迁移

2. **AI核心服务** (战略层、复盘等)
   - ✅ 复杂机器学习算法
   - ✅ 需要scikit-learn, XGBoost等
   - ✅ 长时间运行

3. **文档处理** (Word/PPT/OCR)
   - ✅ 需要python-docx, python-pptx
   - ✅ 需要pytesseract
   - ✅ 处理大文件

4. **语义搜索**
   - ✅ 需要sentence-transformers
   - ✅ 向量计算
   - ✅ 384维向量嵌入

### ⚠️ 混合模式案例

1. **数据导入** (`data-import`)
   - **Edge Functions**: 简单验证和写入
   - **FastAPI**: 复杂ETL、数据转换、质量检查

---

## 🚀 实施建议

### 1. 新功能开发流程

```
1. 评估功能特性
   ├── 检查执行时间需求
   ├── 检查计算复杂度
   ├── 检查依赖库需求
   └── 检查数据量

2. 应用决策标准
   ├── 符合Edge Functions标准 → 使用Edge Functions
   ├── 符合FastAPI标准 → 使用FastAPI
   └── 混合需求 → 分离简单和复杂逻辑

3. 实施和测试
   ├── 实现功能
   ├── 性能测试
   └── 验证决策正确性
```

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

**核心原则**:
- **Edge Functions**: 快速、简单、轻量级
- **FastAPI**: 复杂、计算密集、需要Python库

**决策口诀**:
- 10秒内完成 → Edge Functions
- 需要Python库 → FastAPI
- 复杂算法 → FastAPI
- 简单CRUD → Edge Functions

---

**文档版本**: 1.0  
**最后更新**: 2025-10-31


