# BMOS AI 数据导入系统 - Lovable 实施就绪文档

## 📋 实施概览

本文档描述使用 Lovable Cloud 和 Supabase Edge Functions 实现 BMOS AI 数据导入系统的实施计划。

## 🎯 实施目标

### 核心功能
1. **智能文件上传** - 支持 CSV, Excel, JSON 格式
2. **格式自动识别** - 识别6种单据格式
3. **数据质量检测** - 自动验证数据质量
4. **主数据匹配** - 智能匹配主数据
5. **导入历史追踪** - 完整的导入审计日志

### 技术架构
- **前端**: React + TypeScript + Vite
- **后端**: Supabase Edge Functions (Deno)
- **数据库**: PostgreSQL (Supabase)
- **存储**: Supabase Storage
- **认证**: Supabase Auth

## 📦 已完成功能

### ✅ Phase 1: 基础设施 (已完成)

#### 1.1 数据库表结构
- ✅ `data_import_uploads` - 上传记录表
- ✅ `field_mapping_history` - 字段映射历史
- ✅ `data_import_log` - 导入日志
- ✅ `data_quality_report` - 质量报告
- ✅ RLS 策略配置完成

#### 1.2 存储桶
- ✅ `data-import` 存储桶已创建
- ✅ RLS 策略已配置

#### 1.3 共享模块
- ✅ `cors.ts` - CORS 配置
- ✅ `file-parser.ts` - 文件解析（CSV, Excel, JSON）
- ✅ `format-detector.ts` - 格式识别算法

#### 1.4 Edge Functions
- ✅ `data-import-upload` - 文件上传和格式识别

## 🚀 待实施功能

### Phase 2: 核心算法实现

#### 2.1 数据验证 Edge Function
**功能**: `data-import-validate`
- 文件格式验证
- 数据完整性检查
- 字段类型验证
- 空值比例检测
- 异常值识别
- 重复数据检测

**输入**:
```typescript
{
  file_id: string;
  validation_rules?: {
    required_fields?: string[];
    max_null_ratio?: number;
    check_duplicates?: boolean;
  };
}
```

**输出**:
```typescript
{
  success: boolean;
  quality_report: {
    overall_quality_score: number;
    completeness_score: number;
    accuracy_score: number;
    consistency_score: number;
    issues: Array<{
      type: string;
      severity: string;
      field?: string;
      description: string;
      affected_rows: number;
    }>;
  };
}
```

#### 2.2 主数据匹配 Edge Function
**功能**: `data-import-match-master`
- 自动匹配主数据（客户、SKU、供应商等）
- 模糊匹配算法
- 相似度评分
- 多候选项推荐

**输入**:
```typescript
{
  file_id: string;
  match_config: {
    entity_type: 'customer' | 'sku' | 'supplier' | 'channel';
    match_fields: string[];
    threshold?: number;
  };
}
```

**输出**:
```typescript
{
  success: boolean;
  match_results: Array<{
    source_value: string;
    matched: boolean;
    master_id?: string;
    master_name?: string;
    confidence: number;
    candidates?: Array<{
      id: string;
      name: string;
      similarity: number;
    }>;
  }>;
}
```

#### 2.3 文档头提取 Edge Function  
**功能**: `data-import-extract-headers`
- 根据格式类型提取单据头
- 去重和标准化
- 关联明细行

**输入**:
```typescript
{
  file_id: string;
  format_type: string;
}
```

**输出**:
```typescript
{
  success: boolean;
  headers: Array<{
    document_number: string;
    document_date?: string;
    customer_name?: string;
    total_amount?: number;
    detail_row_indices: number[];
  }>;
}
```

#### 2.4 数据导入执行 Edge Function
**功能**: `data-import-execute`
- 将验证通过的数据导入到目标表
- 支持批量导入
- 事务处理
- 错误回滚

**输入**:
```typescript
{
  file_id: string;
  target_table: string;
  field_mapping: Record<string, string>;
  import_mode: 'insert' | 'upsert' | 'update';
}
```

**输出**:
```typescript
{
  success: boolean;
  import_id: string;
  stats: {
    total_rows: number;
    success_rows: number;
    failed_rows: number;
    skipped_rows: number;
    duration_ms: number;
  };
  errors?: Array<{
    row_index: number;
    error_message: string;
  }>;
}
```

### Phase 3: 高级功能

#### 3.1 导入历史查询 Edge Function
**功能**: `data-import-history`
- 查询导入历史
- 分页支持
- 过滤和排序

#### 3.2 导入统计分析 Edge Function
**功能**: `data-import-stats`
- 导入成功率统计
- 文件格式分布
- 质量趋势分析
- 性能指标

#### 3.3 文件清理 Edge Function
**功能**: `data-import-cleanup`
- 定时清理过期文件
- 删除失败的上传
- 存储空间管理

## 🔧 实施步骤

### Step 1: 实现数据验证 (优先级: 高)
```bash
# 创建 Edge Function
supabase/functions/data-import-validate/index.ts

# 实现验证算法
supabase/functions/_shared/data-validator.ts
```

### Step 2: 实现主数据匹配 (优先级: 高)
```bash
# 创建 Edge Function
supabase/functions/data-import-match-master/index.ts

# 实现匹配算法
supabase/functions/_shared/master-data-matcher.ts
```

### Step 3: 实现文档头提取 (优先级: 中)
```bash
# 创建 Edge Function
supabase/functions/data-import-extract-headers/index.ts

# 实现提取算法
supabase/functions/_shared/header-extractor.ts
```

### Step 4: 实现数据导入执行 (优先级: 高)
```bash
# 创建 Edge Function
supabase/functions/data-import-execute/index.ts

# 实现导入逻辑
supabase/functions/_shared/data-importer.ts
```

### Step 5: 前端集成测试 (优先级: 高)
- 更新 `src/services/dataImportApi.ts`
- 测试完整导入流程
- 错误处理优化

### Step 6: 实现高级功能 (优先级: 低)
- 导入历史查询
- 统计分析
- 文件清理

## 📊 数据流程图

```
用户上传文件
    ↓
data-import-upload (格式识别)
    ↓
data-import-validate (质量检测)
    ↓
data-import-match-master (主数据匹配)
    ↓
data-import-extract-headers (提取单据头)
    ↓
data-import-execute (执行导入)
    ↓
data-import-log (记录日志)
```

## 🧪 测试策略

### 单元测试
- 每个共享模块独立测试
- 模拟数据覆盖边界情况

### 集成测试
- Edge Function 端到端测试
- 数据库操作验证
- 存储操作验证

### 性能测试
- 大文件上传测试 (50MB)
- 并发上传测试
- 批量导入性能测试

## 📝 配置文件更新

### supabase/config.toml
```toml
project_id = "fmpnelntcmvjvhsavkmv"

[functions.data-import-upload]
verify_jwt = true

[functions.data-import-validate]
verify_jwt = true

[functions.data-import-match-master]
verify_jwt = true

[functions.data-import-extract-headers]
verify_jwt = true

[functions.data-import-execute]
verify_jwt = true

[functions.data-import-history]
verify_jwt = true

[functions.data-import-stats]
verify_jwt = true

[functions.data-import-cleanup]
verify_jwt = false  # 定时任务，无需JWT
```

## 🔒 安全考虑

1. **认证**: 所有 Edge Functions 都需要 JWT 认证
2. **授权**: 使用 RLS 策略确保租户隔离
3. **文件验证**: 严格的文件类型和大小限制
4. **SQL注入防护**: 使用参数化查询
5. **存储安全**: 私有存储桶，按租户隔离

## 📈 性能优化

1. **文件解析**: 流式处理大文件
2. **批量操作**: 使用批量插入减少数据库往返
3. **缓存**: 缓存主数据查询结果
4. **异步处理**: 大文件导入使用后台任务

## 🐛 错误处理

1. **详细错误日志**: 记录所有错误到 `data_import_log`
2. **友好错误消息**: 返回用户可理解的错误信息
3. **事务回滚**: 导入失败时回滚所有更改
4. **重试机制**: 网络错误自动重试

## 📚 参考文档

- [Supabase Edge Functions 文档](https://supabase.com/docs/guides/functions)
- [Deno 标准库](https://deno.land/std)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

## ✅ 实施检查清单

- [ ] Phase 2: 核心算法实现
  - [ ] 数据验证 Edge Function
  - [ ] 主数据匹配 Edge Function
  - [ ] 文档头提取 Edge Function
  - [ ] 数据导入执行 Edge Function
- [ ] Phase 3: 高级功能
  - [ ] 导入历史查询
  - [ ] 统计分析
  - [ ] 文件清理
- [ ] 前端集成
  - [ ] API 客户端更新
  - [ ] UI 组件集成
  - [ ] 错误处理
- [ ] 测试
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] 性能测试
- [ ] 文档
  - [ ] API 文档
  - [ ] 用户手册
  - [ ] 运维手册

## 🎉 下一步行动

1. **立即开始**: 实现 `data-import-validate` Edge Function
2. **参考**: 查看 `EDGE_FUNCTIONS_TEST_CASES.md` 了解测试用例
3. **协作**: 与团队讨论实施优先级和时间表
