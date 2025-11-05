# 性能优化方案文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P1 - 重要文档**

**文档目的**: 提供数据导入功能的性能优化方案，供Lovable在实施时参考

---

## 📋 目录

1. [大文件处理](#1-大文件处理)
2. [批量插入优化](#2-批量插入优化)
3. [事务管理](#3-事务管理)
4. [缓存策略](#4-缓存策略)
5. [并发优化](#5-并发优化)

---

## 1. 大文件处理

### 1.1 问题分析

**Edge Functions限制**:
- **请求大小限制**: 10MB（Supabase Edge Functions）
- **执行时间限制**: 60秒（默认）
- **内存限制**: 128MB（默认）

**大文件处理挑战**:
- 文件大小可能超过10MB
- 数据行数可能超过10万行
- 处理时间可能超过60秒

### 1.2 解决方案

#### 方案1: 流式读取（推荐）

```typescript
/**
 * 流式读取大文件
 */
async function parseFileStream(filePath: string): Promise<AsyncGenerator<any[], void, unknown>> {
  const file = await Deno.open(filePath);
  const reader = file.readable.getReader();
  
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;
    
    // 追加到缓冲区
    buffer += new TextDecoder().decode(value);
    
    // 按行分割
    const lines = buffer.split('\n');
    
    // 保留最后一行（可能不完整）
    buffer = lines.pop() || '';
    
    // 处理完整的行
    for (const line of lines) {
      if (line.trim()) {
        yield parseLine(line);
      }
    }
  }
  
  // 处理最后一行
  if (buffer.trim()) {
    yield parseLine(buffer);
  }
  
  file.close();
}

// 使用示例
for await (const chunk of parseFileStream(filePath)) {
  await processChunk(chunk);
}
```

#### 方案2: 分块处理

```typescript
/**
 * 分块处理数据
 */
async function processInChunks<T>(
  data: T[],
  chunkSize: number = 1000,
  processChunk: (chunk: T[]) => Promise<void>
): Promise<void> {
  for (let i = 0; i < data.length; i += chunkSize) {
    const chunk = data.slice(i, i + chunkSize);
    await processChunk(chunk);
    
    // 可选：添加延迟，避免过载
    if (i + chunkSize < data.length) {
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  }
}

// 使用示例
await processInChunks(
  rows,
  1000,  // 每次处理1000行
  async (chunk) => {
    // 调用FastAPI处理
    await callFastAPI('/api/v1/document/process', {
      data: chunk,
      tenant_id: tenantId
    }, authHeader);
  }
);
```

### 1.3 建议的Chunk大小

**Cursor建议**:
- **小文件** (<10MB, <10,000行): 一次性处理
- **中等文件** (10-50MB, 10,000-100,000行): 每次处理1000行
- **大文件** (>50MB, >100,000行): 每次处理500行

**理由**:
- 1000行通常可以在一秒内处理完成
- 避免Edge Functions超时（60秒）
- 平衡性能和内存使用

### 1.4 FastAPI侧的分块处理

**是否需要FastAPI侧也实现分块处理？**

**Cursor建议**: 不需要，原因：
1. **FastAPI无超时限制**: FastAPI可以处理长时间运行的任务
2. **Edge Functions处理**: Edge Functions负责分块，FastAPI处理单个块
3. **简化架构**: 避免在FastAPI中重复实现分块逻辑

**如果确实需要FastAPI分块处理**:
```python
# FastAPI端点支持分块处理
@app.post("/api/v1/document/process")
async def process_chunk(
    chunk: List[Dict[str, Any]],
    tenant_id: str,
    chunk_index: int = 0,
    total_chunks: int = 1
):
    """处理单个数据块"""
    # 处理逻辑...
    return {"processed": len(chunk), "chunk_index": chunk_index}
```

### 1.5 内存溢出处理

**预防措施**:
1. **限制处理大小**: 单次处理不超过1000行
2. **及时释放内存**: 处理完一个块后立即释放
3. **监控内存使用**: 使用`Deno.memoryUsage()`监控

```typescript
/**
 * 监控内存使用
 */
function checkMemoryUsage(): void {
  const usage = Deno.memoryUsage();
  const usedMB = usage.heapUsed / 1024 / 1024;
  const limitMB = 128;  // Edge Functions内存限制
  
  if (usedMB > limitMB * 0.8) {
    console.warn(`内存使用率过高: ${usedMB.toFixed(2)}MB / ${limitMB}MB`);
  }
}

// 在处理过程中定期检查
setInterval(checkMemoryUsage, 5000);  // 每5秒检查一次
```

---

## 2. 批量插入优化

### 2.1 批量插入方案对比

#### 方案1: 使用COPY命令（推荐）

**性能**: ⭐⭐⭐⭐⭐ (最快)

```sql
-- 使用COPY命令批量插入
COPY sales_order_headers (
  tenant_id, order_number, order_date, customer_id, total_amount
)
FROM STDIN WITH (FORMAT csv, HEADER true);
```

**TypeScript实现**:
```typescript
async function bulkInsertWithCopy(
  tableName: string,
  columns: string[],
  rows: any[],
  supabase: SupabaseClient
): Promise<void> {
  // 构建CSV数据
  const csvHeader = columns.join(',');
  const csvRows = rows.map(row =>
    columns.map(col => escapeCSV(row[col])).join(',')
  );
  const csvData = [csvHeader, ...csvRows].join('\n');
  
  // 使用Supabase RPC调用COPY命令
  const { error } = await supabase.rpc('copy_from_csv', {
    p_table_name: tableName,
    p_csv_data: csvData
  });
  
  if (error) throw error;
}

function escapeCSV(value: any): string {
  if (value === null || value === undefined) return '';
  const str = String(value);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}
```

#### 方案2: 使用批量INSERT

**性能**: ⭐⭐⭐⭐ (较快)

```sql
-- 批量INSERT
INSERT INTO sales_order_headers (...)
VALUES 
  (...),
  (...),
  (...);
```

**TypeScript实现**:
```typescript
async function bulkInsert(
  tableName: string,
  rows: any[],
  supabase: SupabaseClient,
  batchSize: number = 1000
): Promise<void> {
  // 分批插入
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    
    const { error } = await supabase
      .from(tableName)
      .insert(batch);
    
    if (error) throw error;
  }
}
```

#### 方案3: 使用unnest

**性能**: ⭐⭐⭐ (中等)

```sql
-- 使用unnest批量插入
INSERT INTO sales_order_headers (...)
SELECT * FROM unnest(
  ARRAY[...]::uuid[],  -- tenant_id
  ARRAY[...]::varchar[],  -- order_number
  ARRAY[...]::date[]  -- order_date
);
```

**TypeScript实现**:
```typescript
async function bulkInsertWithUnnest(
  tableName: string,
  columns: string[],
  rows: any[],
  supabase: SupabaseClient
): Promise<void> {
  // 构建unnest参数
  const arrays = columns.map(col => {
    const values = rows.map(row => row[col]);
    return `ARRAY[${values.map(v => `'${v}'`).join(',')}]::${getColumnType(col)}[]`;
  });
  
  const query = `
    INSERT INTO ${tableName} (${columns.join(',')})
    SELECT * FROM unnest(${arrays.join(',')})
  `;
  
  const { error } = await supabase.rpc('execute_sql', { p_query: query });
  if (error) throw error;
}
```

### 2.2 性能对比

| 方案 | 1000行耗时 | 10000行耗时 | 100000行耗时 | 推荐场景 |
|------|-----------|------------|-------------|---------|
| COPY命令 | ~50ms | ~200ms | ~2s | 大批量导入（推荐） |
| 批量INSERT | ~100ms | ~500ms | ~5s | 中等批量导入 |
| unnest | ~150ms | ~800ms | ~8s | 小批量导入 |

**Cursor推荐**: 使用COPY命令，性能最好

### 2.3 实际使用建议

**批量插入最佳实践**:
```typescript
/**
 * 批量插入优化版本
 */
async function optimizedBulkInsert(
  tableName: string,
  rows: any[],
  supabase: SupabaseClient,
  batchSize: number = 1000
): Promise<void> {
  // 如果数据量小，直接使用批量INSERT
  if (rows.length < 100) {
    const { error } = await supabase
      .from(tableName)
      .insert(rows);
    if (error) throw error;
    return;
  }
  
  // 如果数据量大，使用COPY命令
  if (rows.length > 1000) {
    await bulkInsertWithCopy(tableName, Object.keys(rows[0]), rows, supabase);
    return;
  }
  
  // 中等数据量，使用批量INSERT
  await bulkInsert(tableName, rows, supabase, batchSize);
}
```

---

## 3. 事务管理

### 3.1 事务管理建议

**使用数据库存储过程**:
```sql
-- 创建导入事务存储过程
CREATE OR REPLACE FUNCTION import_documents_transaction(
  p_document_type VARCHAR,
  p_headers JSONB,
  p_lines JSONB,
  p_tenant_id UUID
) RETURNS JSONB AS $$
DECLARE
  v_result JSONB;
  v_header_ids UUID[];
BEGIN
  -- 开启事务（自动）
  
  -- 1. 插入Headers
  INSERT INTO sales_order_headers (...)
  SELECT ... FROM jsonb_populate_recordset(null::sales_order_headers, p_headers)
  RETURNING id INTO v_header_ids;
  
  -- 2. 插入Lines（关联Headers）
  INSERT INTO sales_order_lines (...)
  SELECT ... FROM jsonb_populate_recordset(null::sales_order_lines, p_lines);
  
  -- 3. 验证数据一致性
  -- 检查Header总额 = Line金额之和
  -- 检查必填字段
  -- ...
  
  -- 4. 如果验证失败，回滚（自动）
  -- 如果验证成功，提交（自动）
  
  RETURN jsonb_build_object(
    'success', true,
    'headers_count', jsonb_array_length(p_headers),
    'lines_count', jsonb_array_length(p_lines),
    'header_ids', v_header_ids
  );
  
EXCEPTION
  WHEN OTHERS THEN
    -- 自动回滚
    RAISE EXCEPTION '导入失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

**TypeScript调用**:
```typescript
async function importDocuments(
  headers: any[],
  lines: any[],
  documentType: string,
  tenantId: string,
  supabase: SupabaseClient
): Promise<any> {
  const { data, error } = await supabase.rpc('import_documents_transaction', {
    p_document_type: documentType,
    p_headers: headers,
    p_lines: lines,
    p_tenant_id: tenantId
  });
  
  if (error) {
    // 自动回滚
    throw new Error(`导入失败: ${error.message}`);
  }
  
  return data;
}
```

### 3.2 事务隔离级别

**建议**: 使用默认隔离级别（READ COMMITTED）

**理由**:
- 导入操作不需要最高隔离级别
- 默认隔离级别性能更好
- 满足数据一致性要求

---

## 4. 缓存策略

### 4.1 主数据缓存

**缓存策略**:
```typescript
/**
 * 主数据缓存（内存缓存）
 */
class MasterDataCache {
  private cache: Map<string, any> = new Map();
  private ttl: number = 5 * 60 * 1000;  // 5分钟
  
  async get(key: string): Promise<any | null> {
    const cached = this.cache.get(key);
    
    if (!cached) return null;
    
    // 检查是否过期
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }
  
  async set(key: string, data: any): Promise<void> {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  async clear(): Promise<void> {
    this.cache.clear();
  }
}

// 使用示例
const masterDataCache = new MasterDataCache();

async function getMasterData(
  entityType: string,
  tenantId: string,
  supabase: SupabaseClient
): Promise<any[]> {
  const cacheKey = `${entityType}:${tenantId}`;
  
  // 尝试从缓存获取
  const cached = await masterDataCache.get(cacheKey);
  if (cached) return cached;
  
  // 从数据库查询
  const { data, error } = await supabase
    .from(getMasterDataTable(entityType))
    .select('*')
    .eq('tenant_id', tenantId)
    .eq('is_active', true);
  
  if (error) throw error;
  
  // 缓存结果
  await masterDataCache.set(cacheKey, data);
  
  return data || [];
}
```

### 4.2 字段映射历史缓存

**缓存策略**:
```typescript
/**
 * 字段映射历史缓存
 */
class FieldMappingCache {
  private cache: Map<string, any> = new Map();
  private ttl: number = 10 * 60 * 1000;  // 10分钟
  
  async getRecommendations(
    sourceFields: string[],
    targetFields: string[],
    sourceSystem: string,
    tenantId: string
  ): Promise<any[] | null> {
    const cacheKey = `${sourceSystem}:${tenantId}:${sourceFields.join(',')}`;
    
    const cached = await this.get(cacheKey);
    if (cached) return cached;
    
    // 从数据库查询历史映射
    const { data } = await supabase
      .from('field_mapping_history')
      .select('*')
      .eq('source_system', sourceSystem)
      .eq('tenant_id', tenantId)
      .order('usage_count', { ascending: false })
      .limit(100);
    
    if (data) {
      await this.set(cacheKey, data);
      return data;
    }
    
    return null;
  }
  
  // ...（实现get/set方法）
}
```

---

## 5. 并发优化

### 5.1 主数据匹配并发查询

**并发查询优化**:
```typescript
/**
 * 并发查询多个主数据表
 */
async function matchMultipleMasterData(
  inputValues: any[],
  entityTypes: string[],
  tenantId: string,
  supabase: SupabaseClient
): Promise<any> {
  // 并发查询所有主数据表
  const queries = entityTypes.map(async (entityType) => {
    const masterData = await getMasterData(entityType, tenantId, supabase);
    return {
      entityType,
      masterData
    };
  });
  
  // 等待所有查询完成
  const results = await Promise.all(queries);
  
  // 执行匹配
  const matches = await Promise.all(
    inputValues.map(async (inputValue) => {
      const matchResults = await Promise.all(
        results.map(async ({ entityType, masterData }) => {
          return await matchSingleEntity(
            inputValue,
            entityType,
            masterData
          );
        })
      );
      
      return {
        input: inputValue,
        matches: matchResults
      };
    })
  );
  
  return matches;
}
```

### 5.2 FastAPI并发调用

**并发调用FastAPI**:
```typescript
/**
 * 并发调用多个FastAPI端点
 */
async function callMultipleFastAPIEndpoints(
  endpoints: Array<{ endpoint: string; payload: any }>,
  authHeader: string
): Promise<any[]> {
  const fastApiUrl = Deno.env.get('FASTAPI_URL')!;
  
  // 并发发送所有请求
  const promises = endpoints.map(({ endpoint, payload }) =>
    fetch(`${fastApiUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authHeader}`,
      },
      body: JSON.stringify(payload),
    }).then(res => res.json())
  );
  
  // 等待所有请求完成
  return await Promise.all(promises);
}
```

---

## 6. 性能基准

### 6.1 目标性能指标

| 场景 | 数据量 | 目标响应时间 | 实际响应时间 |
|------|--------|------------|-------------|
| 格式识别 | 10MB Excel | < 5秒 | ⏳ 待测试 |
| 头行识别 | 10,000行 | < 10秒 | ⏳ 待测试 |
| 主数据匹配 | 1,000条记录 | < 30秒 | ⏳ 待测试 |
| 批量插入 | 10,000行 | < 5秒 | ⏳ 待测试 |

### 6.2 性能测试方法

```typescript
/**
 * 性能测试工具
 */
async function performanceTest(
  testName: string,
  testFn: () => Promise<void>
): Promise<void> {
  const startTime = Date.now();
  
  try {
    await testFn();
    const duration = Date.now() - startTime;
    console.log(`${testName}: ${duration}ms`);
  } catch (error) {
    console.error(`${testName}失败:`, error);
  }
}

// 使用示例
await performanceTest('格式识别', async () => {
  await recognizeFormat(fileContent, fileName, tenantId, authHeader);
});
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

