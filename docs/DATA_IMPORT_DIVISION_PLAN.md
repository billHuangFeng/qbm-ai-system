# Data-Import 分工细化方案

**创建时间**: 2025-10-31  
**状态**: 🚀 **实施中**

---

## 📋 目标

明确 `data-import` 功能在 Edge Functions 和 FastAPI 之间的分工，将简单逻辑放在 Edge Functions，复杂 ETL 逻辑放在 FastAPI。

---

## 🔍 当前状态分析

### 现有实现

1. **Edge Functions 规范** (`SUPABASE_EDGE_FUNCTIONS_SPEC.md`)
   - 定义了简单的数据导入流程
   - 伪代码包含：验证、批量日志、写入原始表、质量检查、路由转换

2. **FastAPI Mock实现** (`backend/src/api/endpoints/ingestion.py`)
   - Mock端点，返回模拟数据
   - 包含批次管理、问题管理、规则管理等

3. **FastAPI 完整实现** (`backend/src/services/data_import_etl.py`)
   - 复杂的ETL逻辑
   - 支持多种文档格式（Excel、CSV、JSON、XML等）
   - 数据质量检查、字段映射、数据转换等

---

## 🎯 分工方案

### Edge Functions：简单导入流程 ✅

**职责**:
1. **输入验证** - 简单格式验证
2. **批次创建** - 创建导入批次记录
3. **数据写入** - 直接写入原始数据表（raw_data_staging）
4. **简单质量检查** - 基础验证（必填字段、数据类型）
5. **状态更新** - 更新批次状态和统计

**适用场景**:
- ✅ 简单CSV/JSON数据导入
- ✅ 数据格式标准，无需复杂转换
- ✅ 快速验证和写入
- ✅ 执行时间 < 10秒

**限制**:
- ❌ 不支持复杂文档格式解析（Excel、XML等）
- ❌ 不支持复杂ETL转换
- ❌ 不支持复杂字段映射
- ❌ 不支持机器学习质量检查

---

### FastAPI：复杂ETL流程 ✅

**职责**:
1. **复杂文档解析** - Excel、XML、多格式解析
2. **智能格式检测** - 自动识别文档结构
3. **复杂字段映射** - 智能字段映射和转换
4. **数据质量分析** - 7项质量指标评估
5. **数据清洗** - 复杂清洗规则
6. **数据转换** - 复杂转换逻辑
7. **数据加载** - 写入目标表（经过转换）

**适用场景**:
- ✅ 复杂文档格式（Excel、XML等）
- ✅ 需要复杂ETL转换
- ✅ 需要智能字段映射
- ✅ 需要深度质量检查
- ✅ 执行时间可能 > 10秒

**特点**:
- ✅ 使用Python生态库（pandas、openpyxl等）
- ✅ 支持复杂算法和质量检查
- ✅ 支持长时间运行任务

---

## 📊 功能对比表

| 功能 | Edge Functions | FastAPI | 说明 |
|------|---------------|---------|------|
| **简单CSV导入** | ✅ | ⚠️ | Edge Functions快速处理 |
| **简单JSON导入** | ✅ | ⚠️ | Edge Functions快速处理 |
| **Excel解析** | ❌ | ✅ | 需要openpyxl库 |
| **XML解析** | ❌ | ✅ | 需要xml解析库 |
| **智能格式检测** | ❌ | ✅ | 需要复杂逻辑 |
| **简单验证** | ✅ | ✅ | 两者都支持 |
| **复杂验证** | ❌ | ✅ | 需要Python库 |
| **简单字段映射** | ✅ | ✅ | Edge Functions支持基础映射 |
| **复杂字段映射** | ❌ | ✅ | 需要智能映射算法 |
| **基础质量检查** | ✅ | ✅ | 两者都支持 |
| **深度质量分析** | ❌ | ✅ | 7项质量指标 |
| **简单清洗** | ✅ | ✅ | 两者都支持 |
| **复杂清洗** | ❌ | ✅ | 需要复杂规则 |
| **直接写入原始表** | ✅ | ✅ | Edge Functions快速写入 |
| **写入目标表（转换后）** | ❌ | ✅ | 需要ETL转换 |

---

## 🔧 实施步骤

### Phase 2.1: 定义Edge Functions简单导入规范 ✅

1. ✅ 明确Edge Functions支持的场景
2. ✅ 定义输入/输出格式
3. ✅ 定义简单的验证规则
4. ✅ 定义错误处理

### Phase 2.2: 更新FastAPI复杂ETL实现 ⏳

1. ⏳ 明确FastAPI负责的复杂逻辑
2. ⏳ 优化ETL流程
3. ⏳ 添加API端点
4. ⏳ 添加文档

### Phase 2.3: 创建路由决策逻辑 ⏳

1. ⏳ 前端如何选择Edge Functions还是FastAPI
2. ⏳ 自动路由决策逻辑
3. ⏳ 回退机制

---

## 📐 决策标准

### 使用 Edge Functions 的条件（必须全部满足）✅

1. **文件格式**: CSV 或 JSON
2. **文件大小**: < 1MB
3. **数据行数**: < 10,000行
4. **字段映射**: 简单映射（字段名相同或预定义映射）
5. **数据转换**: 无需复杂转换
6. **质量检查**: 仅需基础验证

### 使用 FastAPI 的条件（满足任一即可）✅

1. **文件格式**: Excel、XML等复杂格式
2. **文件大小**: ≥ 1MB
3. **数据行数**: ≥ 10,000行
4. **字段映射**: 需要智能映射或复杂映射
5. **数据转换**: 需要复杂转换逻辑
6. **质量检查**: 需要深度质量分析（7项指标）

---

## 📝 Edge Functions 简单导入规范

### 输入格式

```json
{
  "sourceSystem": "erp|crm|oa|manual",
  "sourceType": "expense|asset|order|feedback",
  "rows": [
    {
      "field1": "value1",
      "field2": "value2",
      ...
    }
  ],
  "fileName": "optional.csv",
  "fieldMappings": {
    "field1": "target_field1",
    "field2": "target_field2"
  }
}
```

### 处理流程

```typescript
1. 验证输入（sourceSystem, sourceType, rows非空）
2. 创建import_batch记录（status='processing'）
3. 对每一行：
   a. 简单验证（必填字段、基本类型）
   b. 应用字段映射（如果有）
   c. 写入raw_data_staging表
4. 运行基础质量检查（必填、类型、范围）
5. 更新批次状态和统计
6. 返回结果
```

### 输出格式

```json
{
  "success": true,
  "batchId": "uuid",
  "inserted": 120,
  "failed": 3,
  "issues": [
    {
      "rowIndex": 5,
      "issueType": "missing_required_field",
      "field": "amount",
      "suggestedFix": "default_value"
    }
  ]
}
```

---

## 📝 FastAPI 复杂ETL规范

### 输入格式

```json
{
  "file": "<file upload>",
  "sourceType": "expense|asset|order|feedback",
  "documentFormat": "auto|excel|csv|json|xml",
  "fieldMappings": [
    {
      "sourceField": "field1",
      "targetField": "target_field1",
      "transformation": "optional"
    }
  ],
  "targetTable": "fact_expense|fact_asset|...",
  "importConfig": {
    "qualityCheck": true,
    "deepAnalysis": true,
    "autoClean": true
  }
}
```

### 处理流程

```python
1. 上传文件（支持大文件）
2. 检测文档格式（自动或指定）
3. 解析文档结构（智能识别表头、多格式）
4. 深度质量检查（7项指标）
5. 智能字段映射（自动映射或使用配置）
6. 复杂数据转换（类型转换、计算、清洗）
7. 数据验证（深度验证）
8. 数据清洗（复杂清洗规则）
9. 写入目标表（转换后的数据）
10. 生成导入报告
```

### 输出格式

```json
{
  "importId": "uuid",
  "status": "completed|failed|partial",
  "totalRecords": 1000,
  "successfulRecords": 995,
  "failedRecords": 5,
  "qualityScore": 0.92,
  "qualityLevel": "good",
  "errors": [...],
  "warnings": [...],
  "processingTime": 12.5
}
```

---

## 🔄 工作流程

### 前端选择逻辑

```
用户上传文件
    ↓
检查文件特性
    ↓
┌───────────────────────┐
│ 符合 Edge Functions   │
│     条件？            │
└───────────────────────┘
    ↓ Yes          ↓ No
Edge Functions    FastAPI
简单导入         复杂ETL
    ↓              ↓
返回结果         返回结果
```

### 自动路由建议

1. **文件扩展名**: `.csv`, `.json` → Edge Functions（默认）
2. **文件大小**: < 1MB → Edge Functions
3. **用户选择**: 可以手动选择使用FastAPI

---

## 📊 实施进度

- [x] Phase 2.1: 定义Edge Functions简单导入规范
- [ ] Phase 2.2: 更新FastAPI复杂ETL实现
- [ ] Phase 2.3: 创建路由决策逻辑
- [ ] Phase 2.4: 更新文档

---

## 📚 相关文档

- [优化计划文档](./FASTAPI_EDGE_FUNCTIONS_OPTIMIZATION_PLAN.md)
- [决策指南文档](./FASTAPI_EDGE_FUNCTIONS_DECISION_GUIDE.md)
- [Edge Functions规范](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)
- [数据导入ETL服务](../backend/src/services/data_import_etl.py)

---

**下一步**: 更新Edge Functions规范，明确简单导入的详细实现


