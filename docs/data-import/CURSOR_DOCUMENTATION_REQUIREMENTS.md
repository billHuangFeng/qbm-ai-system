# Cursor 文档准备要求清单

**项目**: 数据导入功能迁移到 Supabase Edge Functions  
**日期**: 2025-11-04  
**状态**: 📝 待 Cursor 准备

---

## 📋 必需文档清单

### 1. 算法转换设计文档

**文件路径**: `docs/data-import/ALGORITHM_CONVERSION_DESIGN.md`

**必需内容**:

#### 1.1 格式识别算法 (Algorithm 1)
- **当前 Python 实现**：简要描述
- **TypeScript 转换方案**：
  - 核心逻辑描述
  - 使用的 Deno/npm 库
  - 伪代码或关键代码片段
- **复杂度分析**：时间复杂度和空间复杂度
- **测试用例**：至少 3 个测试场景

#### 1.2 字段映射算法 (Algorithm 2)
- **当前 Python 实现**：简要描述
- **TypeScript 转换方案**：
  - Levenshtein 距离实现（推荐库：`fastest-levenshtein`）
  - 历史映射查询逻辑
  - 权重计算公式
- **复杂度分析**
- **测试用例**

#### 1.3 主数据匹配算法 (Algorithm 3)
- **当前 Python 实现**：简要描述（rapidfuzz）
- **TypeScript 转换方案**：
  - 推荐库：`fuzzysort`、`fuse.js` 或 PostgreSQL `similarity()`
  - 7 张主数据表的查询策略
  - 并发查询方案（Promise.all）
- **复杂度分析**
- **测试用例**

#### 1.4 单据头匹配算法 (Algorithm 4)
- **当前 Python 实现**：简要描述
- **TypeScript 转换方案**：
  - 使用 PostgreSQL `similarity()` 函数
  - 模糊匹配阈值建议
- **复杂度分析**
- **测试用例**

#### 1.5 数据验证算法 (Algorithm 5)
- **当前 Python 实现**：简要描述
- **TypeScript 转换方案**：
  - 业务规则验证逻辑
  - 金额计算验证
  - 完整性检查
- **复杂度分析**
- **测试用例**

---

### 2. Edge Functions API 设计文档

**文件路径**: `docs/data-import/EDGE_FUNCTIONS_API_DESIGN.md`

**必需内容**（参考 `docs/api/EDGE_FUNCTIONS_API_TEMPLATE.md` 格式）:

#### 2.1 data-import-upload
```markdown
### Function: data-import-upload
**Path**: `/functions/v1/data-import-upload`
**Method**: POST

#### Input
- **Body**: FormData
  - `file`: File (CSV, Excel, JSON)

#### Output
```json
{
  "success": true,
  "file_id": "uuid",
  "file_name": "example.xlsx",
  "row_count": 1500,
  "format_detection": {
    "format_type": "FORMAT_1_REPEATING_HEADER",
    "confidence": 0.95
  }
}
```

#### Error Codes
- 400: 文件格式不支持
- 413: 文件过大
- 500: 服务器错误

#### Pseudocode
```typescript
// 1. 接收文件
// 2. 上传到 Supabase Storage
// 3. 解析文件内容
// 4. 调用格式识别算法
// 5. 返回结果
```
```

**为以下 Edge Functions 创建类似文档**:
- `data-import-analyze`
- `data-import-validate`
- `data-import-match-master`
- `data-import-match-headers`
- `data-import-history`
- `data-import-cleanup`

---

### 3. 数据库设计文档

**文件路径**: `docs/data-import/DATABASE_OPTIMIZATION_DESIGN.md`

**必需内容**:

#### 3.1 PostgreSQL 扩展
```sql
-- 启用 pg_trgm（三元组相似度）
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

#### 3.2 模糊匹配函数设计
```sql
-- 函数签名
CREATE OR REPLACE FUNCTION fuzzy_match_master_data(
  search_text TEXT,
  table_name TEXT,
  threshold FLOAT DEFAULT 0.6
) RETURNS TABLE (...);

-- 函数说明
-- 参数说明
-- 返回值说明
-- 使用示例
```

#### 3.3 索引设计
```sql
-- 为 7 张主数据表添加 GIN 索引
CREATE INDEX idx_customer_name_trgm ON dim_customer USING gin(name gin_trgm_ops);
-- ... 其他索引
```

**理由**: 提升模糊匹配性能

#### 3.4 新增表设计
```sql
-- import_logs 表
CREATE TABLE import_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  file_name TEXT NOT NULL,
  -- ... 其他字段
);
```

**字段说明**:
- `id`: 主键
- `tenant_id`: 租户 ID
- `file_name`: 文件名
- ...

---

### 4. 迁移测试计划

**文件路径**: `docs/data-import/MIGRATION_TEST_PLAN.md`

**必需内容**:

#### 4.1 单元测试计划
| 测试模块 | 测试场景 | 预期结果 | 测试数据 |
|---------|---------|---------|---------|
| 格式识别 | 格式1：重复表头 | `format_type: "FORMAT_1_REPEATING_HEADER"` | `test_data/format1.xlsx` |
| 格式识别 | 格式2：单表头 | `format_type: "FORMAT_2_SINGLE_HEADER"` | `test_data/format2.csv` |
| 字段映射 | 完全匹配 | 映射置信度 > 0.9 | ... |
| 主数据匹配 | 客户名模糊匹配 | 返回前 5 个匹配结果 | ... |

#### 4.2 集成测试计划
| 测试流程 | 步骤 | 验证点 |
|---------|-----|-------|
| 完整导入流程 | 1. 上传文件 | 返回 file_id |
|  | 2. 格式识别 | 识别正确格式 |
|  | 3. 主数据匹配 | 匹配率 > 80% |
|  | 4. 数据验证 | 质量评分 > 0.7 |

#### 4.3 性能测试计划
| 测试项 | 测试数据量 | 目标性能 | 测试工具 |
|-------|-----------|---------|---------|
| 文件上传 | 10MB Excel | < 5 秒 | 手动测试 |
| 格式识别 | 5000 行 | < 3 秒 | Deno.bench |
| 主数据匹配 | 1000 条记录 | < 10 秒 | Deno.bench |

#### 4.4 测试数据准备
- 格式1 测试文件：`test_data/format1.xlsx`（100 行）
- 格式2 测试文件：`test_data/format2.csv`（500 行）
- 大文件测试：`test_data/large_file.xlsx`（10000 行）

---

### 5. 性能优化方案

**文件路径**: `docs/data-import/PERFORMANCE_OPTIMIZATION.md`

**必需内容**:

#### 5.1 大文件处理策略
- **问题**: Edge Functions 有请求大小限制（10MB）
- **解决方案**:
  1. 客户端上传到 Supabase Storage
  2. Edge Function 从 Storage 流式读取
  3. 分块处理（每次 1000 行）
- **伪代码**:
```typescript
async function processLargeFile(fileId: string) {
  const stream = await storage.from('import-files').download(fileId)
  for await (const chunk of parseCSVStream(stream)) {
    await processChunk(chunk)
  }
}
```

#### 5.2 并发优化
- **主数据匹配并发查询**:
```typescript
const results = await Promise.all([
  matchCustomer(data),
  matchSupplier(data),
  matchSKU(data),
  // ... 其他 4 张表
])
```

#### 5.3 缓存策略
- 主数据缓存（使用内存缓存，有效期 5 分钟）
- 字段映射历史缓存

#### 5.4 数据库查询优化
- 批量插入（使用 `COPY` 或 multi-row INSERT）
- 预编译语句
- 避免 N+1 查询

---

## 📝 文档格式要求

1. **Markdown 格式**
2. **包含代码示例**（伪代码或 TypeScript）
3. **清晰的章节结构**
4. **具体的技术方案**（不要模糊描述）
5. **测试用例和数据**

---

## ✅ 完成标准

Cursor 提供的文档应满足以下标准：
- [ ] 所有算法都有清晰的 TypeScript 转换方案
- [ ] 每个 Edge Function 都有完整的 API 设计
- [ ] 数据库优化方案具体可执行（SQL 语句）
- [ ] 测试计划覆盖单元、集成、性能测试
- [ ] 性能优化方案具体可实施

---

## 🔄 协作流程

### Checkpoint 1: 文档审查（Cursor → Lovable）
**时间**: Cursor 完成文档后
**内容**: Lovable 审查文档完整性和可行性
**输出**: 审查意见 + 修改建议

### Checkpoint 2: 算法实现验证（Lovable → Cursor）
**时间**: Lovable 实现算法后
**内容**: Cursor 验证算法准确性
**输出**: 验证报告 + 算法优化建议

### Checkpoint 3: 性能与准确性测试（共同）
**时间**: 迁移完成后
**内容**: 共同进行性能测试和准确性验证
**输出**: 测试报告 + 优化建议

---

## 📞 沟通机制

- **GitHub Issues**: 用于跟踪文档任务和问题
- **响应时间**: 24 小时内回复
- **紧急问题**: 通过项目 README 中的联系方式

---

**准备就绪后**: 请在此文档顶部更新状态为 "✅ 文档已完成"，并通知 Lovable 开始实施阶段。
