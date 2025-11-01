# FastAPI 数据导入ETL规范

**创建时间**: 2025-10-31  
**版本**: 1.0

---

## 📋 目的

本规范定义FastAPI负责的复杂数据导入ETL功能，包括复杂文档解析、智能字段映射、深度质量检查和复杂数据转换。

---

## 🎯 适用范围

FastAPI数据导入ETL适用于以下场景：

1. **复杂文件格式**
   - ✅ Excel (`.xlsx`, `.xls`)
   - ✅ XML (`.xml`)
   - ✅ 其他复杂格式

2. **大文件处理**
   - ✅ 文件大小 ≥ 1MB
   - ✅ 数据行数 ≥ 10,000行

3. **复杂处理需求**
   - ✅ 需要智能字段映射
   - ✅ 需要复杂ETL转换
   - ✅ 需要深度质量分析（7项指标）

---

## 🔌 API端点

### 1. 上传并导入数据

**端点**: `POST /api/v1/data-import/import`

**请求**:
- `file`: 文件上传（multipart/form-data）
- `source_type`: 数据源类型（`expense|asset|order|feedback`）
- `document_format`: 文档格式（`auto|excel|csv|json|xml`）
- `field_mappings`: 字段映射配置（JSON字符串）
- `target_table`: 目标表名
- `import_config`: 导入配置（JSON字符串）

**响应**:
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

### 2. 分析文件结构

**端点**: `POST /api/v1/data-import/analyze`

**功能**: 分析文件结构，推荐字段映射和导入配置

**响应**:
```json
{
  "documentFormat": "excel",
  "detectedStructure": {
    "headers": ["field1", "field2", ...],
    "rowCount": 1000,
    "dataTypes": {...}
  },
  "suggestedMappings": [...],
  "estimatedQuality": 0.85
}
```

---

### 3. 验证数据

**端点**: `POST /api/v1/data-import/validate`

**功能**: 深度数据验证，不实际导入

**响应**:
```json
{
  "isValid": true,
  "qualityScore": 0.92,
  "errors": [...],
  "warnings": [...],
  "recommendations": [...]
}
```

---

## 🔧 处理流程

### 完整ETL流程

```
1. 文件上传
   ↓
2. 格式检测（自动或指定）
   ↓
3. 文档解析（智能识别表头、多格式支持）
   ↓
4. 深度质量检查（7项指标）
   ├── 完整性检查
   ├── 准确性检查
   ├── 一致性检查
   ├── 及时性检查
   ├── 有效性检查
   ├── 唯一性检查
   └── 完整性检查
   ↓
5. 智能字段映射
   ├── 自动识别相似字段
   ├── 应用映射规则
   └── 处理缺失字段
   ↓
6. 复杂数据转换
   ├── 类型转换
   ├── 数据计算
   ├── 衍生字段生成
   └── 数据清洗
   ↓
7. 数据验证（深度验证）
   ↓
8. 数据加载到目标表
   ↓
9. 生成导入报告
```

---

## 📊 功能特性

### 1. 复杂文档解析 ✅

**支持格式**:
- Excel（`.xlsx`, `.xls`）- 使用 `openpyxl`
- XML（`.xml`）- 使用 `xml.etree.ElementTree`
- CSV（`.csv`）- 使用 `pandas`
- JSON（`.json`）- 使用 `json`

**智能识别**:
- 自动识别表头位置
- 支持多行表头
- 识别数据区域
- 处理合并单元格（Excel）

### 2. 智能字段映射 ✅

**功能**:
- 自动识别相似字段名
- 模糊匹配（编辑距离算法）
- 基于上下文的映射
- 用户自定义映射规则

**算法**:
- 字符串相似度（Levenshtein距离）
- 语义相似度（如果可用）
- 历史映射记录学习

### 3. 深度质量检查 ✅

**7项质量指标**:
1. **完整性** (Completeness) - 必填字段填充率
2. **准确性** (Accuracy) - 数据准确性
3. **一致性** (Consistency) - 数据一致性
4. **及时性** (Timeliness) - 数据时效性
5. **有效性** (Validity) - 数据有效性
6. **唯一性** (Uniqueness) - 数据唯一性
7. **完整性** (Integrity) - 数据完整性

**质量等级**:
- **优秀** (Excellent): ≥ 95%
- **良好** (Good): 85-95%
- **一般** (Fair): 70-85%
- **较差** (Poor): < 70%

### 4. 复杂数据转换 ✅

**转换类型**:
- 数据类型转换
- 数据格式转换（日期、货币等）
- 数据计算（公式、聚合）
- 衍生字段生成
- 数据清洗规则

### 5. 数据加载 ✅

**加载方式**:
- 批量插入（PostgreSQL）
- 事务管理
- 错误回滚
- 进度跟踪

---

## 🚀 性能优化

### 1. 大文件处理

- **分块处理**: 大文件分块读取和处理
- **流式处理**: 边读边处理，不全部加载到内存
- **进度跟踪**: 实时反馈处理进度

### 2. 异步处理

- **后台任务**: 长时间任务使用异步后台任务
- **任务队列**: 使用任务队列管理批量导入
- **状态查询**: 支持查询任务状态

### 3. 缓存优化

- **映射规则缓存**: 缓存常用字段映射规则
- **质量检查结果缓存**: 缓存质量检查结果
- **模板缓存**: 缓存常用导入模板

---

## 📝 错误处理

### 错误类型

1. **文件格式错误** (400)
   - 不支持的文件格式
   - 文件损坏
   - 文件读取失败

2. **数据验证错误** (400)
   - 必填字段缺失
   - 数据类型错误
   - 数据范围错误

3. **处理错误** (500)
   - ETL转换失败
   - 数据库写入失败
   - 系统错误

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "DATA_IMPORT_FAILED",
    "message": "数据导入失败",
    "details": {
      "errorType": "validation_error",
      "rowIndex": 5,
      "field": "amount",
      "reason": "数据类型错误"
    }
  }
}
```

---

## ✅ 与Edge Functions对比

| 特性 | Edge Functions | FastAPI |
|------|---------------|---------|
| **文件格式** | CSV/JSON | Excel/XML/CSV/JSON |
| **文件大小** | < 1MB | 无限制 |
| **数据行数** | < 10,000 | 无限制 |
| **字段映射** | 简单映射 | 智能映射 |
| **质量检查** | 基础验证 | 深度分析（7项指标） |
| **数据转换** | 基础转换 | 复杂ETL |
| **执行时间** | < 10秒 | 可能 > 10秒 |
| **异步处理** | ❌ | ✅ |

---

## 📚 相关文档

- [分工方案文档](./DATA_IMPORT_DIVISION_PLAN.md)
- [路由决策指南](./DATA_IMPORT_ROUTING_GUIDE.md)
- [决策指南文档](./FASTAPI_EDGE_FUNCTIONS_DECISION_GUIDE.md)
- [ETL服务代码](../backend/src/services/data_import_etl.py)

---

## 🔗 API端点清单

1. `POST /api/v1/data-import/import` - 上传并导入数据
2. `POST /api/v1/data-import/analyze` - 分析文件结构
3. `POST /api/v1/data-import/validate` - 验证数据
4. `GET /api/v1/data-import/history` - 获取导入历史
5. `GET /api/v1/data-import/{importId}` - 获取导入详情

---

**文档版本**: 1.0  
**最后更新**: 2025-10-31


