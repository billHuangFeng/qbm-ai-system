# 算法转换设计文档

**项目**: 数据导入功能迁移到 Supabase Edge Functions  
**创建日期**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

---

## 📋 概述

本文档描述将 Python FastAPI 后端算法转换为 TypeScript Supabase Edge Functions 的设计方案。所有算法已在 FastAPI 中实现，本文档提供 TypeScript 转换指南。

---

## 1. 格式识别算法 (Algorithm 1)

### 1.1 当前 Python 实现

**文件位置**: `backend/src/services/data_enhancement/document_format_detector.py`

**核心功能**:
- 自动识别 6 种单据格式
- 计算每种格式的置信度（0-1）
- 返回最佳匹配格式

**支持的格式类型**:
```python
class DocumentFormatType(Enum):
    REPEATED_HEADER = "repeated_header"  # 格式1: 多行明细对应重复单据头
    FIRST_ROW_HEADER = "first_row_header"  # 格式2: 多行明细但只有第一行有单据头
    SEPARATE_HEADER_BODY = "separate_header_body"  # 格式3: 单据头和明细分离
    HEADER_ONLY = "header_only"  # 格式4: 只有单据头记录
    DETAIL_ONLY = "detail_only"  # 格式5: 只有明细记录（补充明细时）
    PURE_HEADER = "pure_header"  # 格式6: 纯单据头记录（无明细）
```

### 1.2 TypeScript 转换方案

#### 核心逻辑描述

1. **格式检测策略**:
   - 并行检测所有格式类型
   - 为每种格式计算置信度分数
   - 返回置信度最高的格式

2. **使用的 Deno/npm 库**:
   - `xlsx` 或 `exceljs`: Excel 文件解析
   - `csv-parse`: CSV 文件解析
   - 无需额外外部库（纯逻辑计算）

3. **伪代码**:

```typescript
interface FormatDetectionResult {
  formatType: DocumentFormatType;
  confidence: number; // 0-1
  details: Record<string, any>;
}

enum DocumentFormatType {
  REPEATED_HEADER = "repeated_header",
  FIRST_ROW_HEADER = "first_row_header",
  SEPARATE_HEADER_BODY = "separate_header_body",
  HEADER_ONLY = "header_only",
  DETAIL_ONLY = "detail_only",
  PURE_HEADER = "pure_header"
}

async function detectFormat(
  data: Array<Record<string, any>>,
  metadata?: Record<string, any>
): Promise<FormatDetectionResult> {
  // 1. 检测所有格式类型
  const scores: Record<DocumentFormatType, number> = {};
  const details: Record<string, any> = {};
  
  for (const formatType of Object.values(DocumentFormatType)) {
    const [score, detail] = await detectFormatType(data, formatType, metadata);
    scores[formatType] = score;
    details[formatType] = detail;
  }
  
  // 2. 选择得分最高的格式
  const bestFormat = Object.entries(scores)
    .sort(([, a], [, b]) => b - a)[0][0] as DocumentFormatType;
  const bestScore = scores[bestFormat];
  
  return {
    formatType: bestFormat,
    confidence: bestScore,
    details
  };
}

// 格式1: 重复单据头检测
function detectRepeatedHeader(data: Array<Record<string, any>>): [number, any] {
  // 查找单据号字段
  const docNumberCol = findColumn(data, ['单据号', 'document_number', 'document_id', '单号']);
  if (!docNumberCol) return [0.0, { reason: '未找到单据号字段' }];
  
  // 统计唯一单据数
  const uniqueDocs = new Set(data.map(row => row[docNumberCol])).size;
  const totalRows = data.length;
  
  if (totalRows === 0) return [0.0, { reason: '数据为空' }];
  
  // 计算重复率
  const duplicateRatio = 1.0 - (uniqueDocs / totalRows);
  
  if (duplicateRatio > 0.2) {
    const confidence = Math.min(0.9, 0.7 + duplicateRatio * 0.5);
    return [confidence, {
      uniqueDocs,
      totalRows,
      duplicateRatio,
      reason: `检测到重复单据头，唯一单据数: ${uniqueDocs}, 总行数: ${totalRows}`
    }];
  }
  
  return [0.3, { reason: '单据号重复率较低' }];
}

// 格式2: 第一行单据头检测
function detectFirstRowHeader(data: Array<Record<string, any>>): [number, any] {
  if (data.length < 2) return [0.0, { reason: '数据行数不足' }];
  
  // 检查第二行及之后的行是否有大量空值（单据头字段）
  const headerFields = ['单据号', 'document_number', '单据日期', 'document_date', 
                         '客户名称', 'customer_name', '不含税金额', 'ex_tax_amount'];
  const headerCols = findColumns(data, headerFields);
  
  if (headerCols.length === 0) return [0.0, { reason: '未找到单据头字段' }];
  
  // 检查第二行之后的空值比例
  let emptyCount = 0;
  let totalFields = 0;
  
  for (let i = 1; i < data.length; i++) {
    for (const col of headerCols) {
      totalFields++;
      if (!data[i][col] || data[i][col] === '') {
        emptyCount++;
      }
    }
  }
  
  const emptyRatio = emptyCount / totalFields;
  
  if (emptyRatio > 0.3) {
    const confidence = Math.min(0.95, 0.7 + emptyRatio * 0.5);
    return [confidence, {
      emptyRatio,
      reason: `第二行及之后单据头字段空值比例: ${(emptyRatio * 100).toFixed(1)}%`
    }];
  }
  
  return [0.2, { reason: '单据头字段空值比例较低' }];
}
```

### 1.3 复杂度分析

- **时间复杂度**: O(n × m)，其中 n 是数据行数，m 是字段数
- **空间复杂度**: O(n)，需要存储检测结果

### 1.4 测试用例

#### 测试用例 1: 格式1（重复单据头）
```typescript
const testData1 = [
  { 单据号: 'PO001', 产品名称: '产品A', 数量: 10 },
  { 单据号: 'PO001', 产品名称: '产品B', 数量: 20 },
  { 单据号: 'PO002', 产品名称: '产品C', 数量: 30 },
  { 单据号: 'PO002', 产品名称: '产品D', 数量: 40 }
];
// 期望: formatType = REPEATED_HEADER, confidence > 0.7
```

#### 测试用例 2: 格式2（第一行单据头）
```typescript
const testData2 = [
  { 单据号: 'PO001', 客户名称: '客户A', 产品名称: '产品A', 数量: 10 },
  { 单据号: null, 客户名称: null, 产品名称: '产品B', 数量: 20 },
  { 单据号: null, 客户名称: null, 产品名称: '产品C', 数量: 30 }
];
// 期望: formatType = FIRST_ROW_HEADER, confidence > 0.7
```

#### 测试用例 3: 格式4（只有单据头）
```typescript
const testData3 = [
  { 单据号: 'PO001', 客户名称: '客户A', 不含税金额: 1000 },
  { 单据号: 'PO002', 客户名称: '客户B', 不含税金额: 2000 }
];
// 期望: formatType = HEADER_ONLY, confidence > 0.8
```

---

## 2. 字段映射算法 (Algorithm 2)

### 2.1 当前 Python 实现

**文件位置**: `backend/src/services/data_enhancement/intelligent_field_mapper.py`

**核心功能**:
- 历史映射查询（最高优先级）
- 规则匹配
- 字符串相似度计算（Levenshtein 距离）
- 动态从数据库获取目标字段

### 2.2 TypeScript 转换方案

#### 使用的 Deno/npm 库

- **`fastest-levenshtein`**: Levenshtein 距离计算（推荐，性能最好）
- **`fuse.js`**: 模糊搜索（可选，用于更复杂的匹配）
- **`@supabase/supabase-js`**: PostgreSQL 数据库查询

#### 核心逻辑

```typescript
interface MappingCandidate {
  targetField: string;
  confidence: number; // 0-1
  method: 'history' | 'similarity' | 'rule' | 'manual';
  source: string; // 推荐来源描述
}

interface FieldMappingRecommendation {
  sourceField: string;
  candidates: MappingCandidate[];
  recommendedTarget?: string;
  recommendedConfidence: number;
}

// Levenshtein 距离实现（使用 fastest-levenshtein）
import { distance } from 'https://deno.land/x/fastest_levenshtein/mod.ts';

function calculateSimilarity(str1: string, str2: string): number {
  const maxLen = Math.max(str1.length, str2.length);
  if (maxLen === 0) return 1.0;
  
  const levenshteinDist = distance(str1.toLowerCase(), str2.toLowerCase());
  return 1.0 - (levenshteinDist / maxLen);
}

// 历史映射查询逻辑
async function getHistoryMappings(
  sourceField: string,
  sourceSystem: string,
  documentType: string | null,
  userId: string | null,
  supabaseClient: SupabaseClient
): Promise<MappingCandidate[]> {
  let query = supabaseClient
    .from('field_mapping_history')
    .select('target_field, usage_count, last_used_at')
    .eq('source_field', sourceField)
    .eq('source_system', sourceSystem);
  
  if (documentType) {
    query = query.eq('document_type', documentType);
  }
  
  if (userId) {
    query = query.eq('user_id', userId);
  }
  
  query = query.order('usage_count', { ascending: false })
    .order('last_used_at', { ascending: false })
    .limit(10);
  
  const { data, error } = await query;
  
  if (error || !data) return [];
  
  return data.map(record => ({
    targetField: record.target_field,
    confidence: Math.min(0.95, 0.85 + (record.usage_count / 100) * 0.1),
    method: 'history' as const,
    source: `历史映射 (使用${record.usage_count}次)`
  }));
}

// 权重计算公式
function calculateWeightedScore(
  historyScore: number,
  similarityScore: number,
  ruleScore: number
): number {
  // 历史映射权重: 60%
  // 相似度权重: 30%
  // 规则权重: 10%
  return (historyScore * 0.6) + (similarityScore * 0.3) + (ruleScore * 0.1);
}

// 字段映射推荐主函数
async function recommendMappings(
  sourceFields: string[],
  sourceSystem: string,
  targetTable: string,
  documentType: string | null,
  userId: string | null,
  supabaseClient: SupabaseClient
): Promise<FieldMappingRecommendation[]> {
  // 1. 从数据库获取目标字段列表
  const targetFields = await getTargetFieldsFromDB(targetTable, supabaseClient);
  
  const recommendations: FieldMappingRecommendation[] = [];
  
  for (const sourceField of sourceFields) {
    const candidates: MappingCandidate[] = [];
    
    // 2. 查询历史映射（优先）
    const historyCandidates = await getHistoryMappings(
      sourceField, sourceSystem, documentType, userId, supabaseClient
    );
    candidates.push(...historyCandidates);
    
    // 3. 应用映射规则
    const ruleCandidates = applyMappingRules(sourceField, sourceSystem, documentType);
    candidates.push(...ruleCandidates);
    
    // 4. 计算相似度匹配
    if (candidates.length === 0 || Math.max(...candidates.map(c => c.confidence)) < 0.8) {
      const similarityCandidates = calculateSimilarityMappings(sourceField, targetFields);
      candidates.push(...similarityCandidates);
    }
    
    // 5. 去重和排序
    const uniqueCandidates = deduplicateAndSort(candidates);
    
    recommendations.push({
      sourceField,
      candidates: uniqueCandidates,
      recommendedTarget: uniqueCandidates[0]?.targetField,
      recommendedConfidence: uniqueCandidates[0]?.confidence || 0.0
    });
  }
  
  return recommendations;
}
```

### 2.3 复杂度分析

- **时间复杂度**: O(n × m × k)，其中 n 是源字段数，m 是目标字段数，k 是历史映射记录数
- **空间复杂度**: O(n × m)，存储推荐结果

### 2.4 测试用例

#### 测试用例 1: 历史映射优先
```typescript
// 场景: 源字段 "采购单号" 在历史中有映射到 "document_number" 的记录
// 期望: 推荐 "document_number"，置信度 > 0.85
```

#### 测试用例 2: 相似度匹配
```typescript
// 场景: 源字段 "客户名" 与目标字段 "customer_name" 相似
// 期望: 推荐 "customer_name"，置信度 > 0.7
```

---

## 3. 主数据匹配算法 (Algorithm 3)

### 3.1 当前 Python 实现

**文件位置**: `backend/src/services/data_enhancement/master_data_matcher.py`

**核心功能**:
- 模糊字符串匹配（fuzzywuzzy + Levenshtein 距离）
- 中文拼音匹配（pypinyin）
- 企业名称标准化
- 统一社会信用代码校验和匹配
- 7 种主数据类型匹配

### 3.2 TypeScript 转换方案

#### 使用的 Deno/npm 库

- **`fuzzysort`**: 模糊字符串搜索（推荐，性能好）
- **`fuse.js`**: 模糊搜索（备选）
- **PostgreSQL `similarity()` 函数**: 使用 pg_trgm 扩展（推荐用于数据库查询）
- **`pinyin-pro`**: 中文拼音转换（Deno 兼容）

#### 核心逻辑

```typescript
// 使用 fuzzysort 进行模糊匹配
import fuzzysort from 'https://deno.land/x/fuzzysort@v2.0.0/mod.ts';

interface MasterDataMatchResult {
  recordIndex: number;
  masterDataType: string;
  candidates: Array<{
    id: number;
    name: string;
    confidence: number;
    matchFields: string[];
  }>;
  noMatch: boolean;
  multipleMatches: boolean;
}

// 7 张主数据表查询策略
const MASTER_DATA_TABLES = {
  business_entity: 'mst_business_entity',
  counterparty: 'mst_counterparty',
  product: 'mst_product',
  unit: 'mst_unit',
  tax_rate: 'mst_tax_rate',
  employee: 'mst_employee',
  exchange_rate: 'mst_exchange_rate'
};

// 并发查询方案（使用 Promise.all）
async function matchMasterData(
  records: Array<Record<string, any>>,
  masterDataType: string,
  tenantId: string,
  supabaseClient: SupabaseClient,
  confidenceThreshold: number = 0.8
): Promise<MasterDataMatchResult[]> {
  const tableName = MASTER_DATA_TABLES[masterDataType];
  if (!tableName) {
    throw new Error(`未知的主数据类型: ${masterDataType}`);
  }
  
  // 1. 批量查询主数据（使用并发）
  const masterDataPromises = records.map(async (record) => {
    const query = supabaseClient
      .from(tableName)
      .select('id, name, code, standardized_name')
      .eq('tenant_id', tenantId)
      .eq('is_deleted', false)
      .limit(1000); // 限制查询数量
    
    const { data, error } = await query;
    return { record, masterData: data || [], error };
  });
  
  const masterDataResults = await Promise.all(masterDataPromises);
  
  // 2. 对每条记录进行匹配
  const matchResults: MasterDataMatchResult[] = [];
  
  for (const { record, masterData } of masterDataResults) {
    const candidates = [];
    
    // 3. 使用 fuzzysort 进行模糊匹配
    const searchTerm = record.name || record.entity_name || '';
    const fuzzyResults = fuzzysort.go(searchTerm, masterData, {
      key: 'name',
      threshold: -10000 // 不设置阈值，返回所有结果
    });
    
    // 4. 计算置信度并筛选
    for (const result of fuzzyResults) {
      const confidence = calculateConfidence(searchTerm, result.obj.name, record.code, result.obj.code);
      
      if (confidence >= confidenceThreshold) {
        candidates.push({
          id: result.obj.id,
          name: result.obj.name,
          confidence,
          matchFields: ['name']
        });
      }
    }
    
    // 5. 代码精确匹配（如果提供）
    if (record.code) {
      const exactCodeMatch = masterData.find(m => m.code === record.code);
      if (exactCodeMatch) {
        const nameSimilarity = calculateNameSimilarity(record.name, exactCodeMatch.name);
        const codeConfidence = nameSimilarity > 0.7 ? 1.0 : 0.75;
        
        // 更新或添加候选
        const existingIndex = candidates.findIndex(c => c.id === exactCodeMatch.id);
        if (existingIndex >= 0) {
          candidates[existingIndex].confidence = Math.max(candidates[existingIndex].confidence, codeConfidence);
        } else {
          candidates.push({
            id: exactCodeMatch.id,
            name: exactCodeMatch.name,
            confidence: codeConfidence,
            matchFields: ['code', 'name']
          });
        }
      }
    }
    
    // 6. 排序和去重
    candidates.sort((a, b) => b.confidence - a.confidence);
    const uniqueCandidates = deduplicateCandidates(candidates);
    
    matchResults.push({
      recordIndex: record.index || 0,
      masterDataType,
      candidates: uniqueCandidates.slice(0, 5), // 返回前5个候选
      noMatch: uniqueCandidates.length === 0,
      multipleMatches: uniqueCandidates.length > 1
    });
  }
  
  return matchResults;
}

// 置信度计算函数
function calculateConfidence(
  sourceName: string,
  targetName: string,
  sourceCode?: string,
  targetCode?: string
): number {
  let confidence = 0.0;
  
  // 1. 代码完全一致 + 名称大致类似（>0.7）= 100%置信度
  if (sourceCode && targetCode && sourceCode === targetCode) {
    const nameSimilarity = calculateNameSimilarity(sourceName, targetName);
    if (nameSimilarity > 0.7) {
      return 1.0;
    } else {
      // 代码一致但名称不匹配 = 高置信度（75-100%）
      return Math.max(0.75, 0.75 + nameSimilarity * 0.25);
    }
  }
  
  // 2. 代码细微差异（1-2字符）+ 名称大致类似 = 置信度大打折扣（30-60%）
  if (sourceCode && targetCode) {
    const codeDistance = levenshteinDistance(sourceCode, targetCode);
    if (codeDistance <= 2 && codeDistance > 0) {
      const nameSimilarity = calculateNameSimilarity(sourceName, targetName);
      if (nameSimilarity > 0.7) {
        return 0.3 + (nameSimilarity - 0.7) * 1.0; // 30-60%
      }
    }
  }
  
  // 3. 仅依赖名称匹配
  const nameSimilarity = calculateNameSimilarity(sourceName, targetName);
  confidence = nameSimilarity * 0.9; // 名称匹配最高90%
  
  return confidence;
}

// 企业名称标准化
function standardizeCompanyName(name: string): string {
  let standardized = name.trim();
  
  // 去除括号内容
  standardized = standardized.replace(/\([^)]*\)/g, '');
  standardized = standardized.replace(/（[^）]*）/g, '');
  
  // 去除公司后缀
  const suffixes = ['有限公司', '股份有限公司', '有限责任公司', '集团', '集团有限公司'];
  for (const suffix of suffixes) {
    if (standardized.endsWith(suffix)) {
      standardized = standardized.slice(0, -suffix.length);
    }
  }
  
  return standardized.trim();
}
```

### 3.3 复杂度分析

- **时间复杂度**: O(n × m × log m)，其中 n 是记录数，m 是主数据记录数
- **空间复杂度**: O(n × k)，其中 k 是候选匹配数（通常 k <= 5）

### 3.4 测试用例

#### 测试用例 1: 代码完全一致 + 名称大致类似
```typescript
// 场景: 源记录 { name: "北京科技有限公司", code: "91110000..." }
//       主数据 { name: "北京科技有限公司", code: "91110000..." }
// 期望: confidence = 1.0
```

#### 测试用例 2: 代码细微差异 + 名称大致类似
```typescript
// 场景: 源记录 { name: "北京科技", code: "91110000..." }
//       主数据 { name: "北京科技有限公司", code: "91110001..." }
// 期望: confidence = 0.3-0.6
```

---

## 4. 单据头匹配算法 (Algorithm 4)

### 4.1 当前 Python 实现

**文件位置**: `backend/src/services/data_enhancement/document_header_matcher.py`

**核心功能**:
- 通过单据号匹配系统中已存在的单据头记录ID
- 匹配结果验证

### 4.2 TypeScript 转换方案

#### 使用的 Deno/npm 库

- **PostgreSQL `similarity()` 函数**: 使用 pg_trgm 扩展（推荐）
- **`@supabase/supabase-js`**: PostgreSQL 数据库查询

#### 核心逻辑

```typescript
interface DocumentHeaderMatchResult {
  documentNumber: string;
  headerId: string | null;
  confidence: number;
  found: boolean;
  headerInfo: Record<string, any> | null;
  message?: string;
}

// 使用 PostgreSQL similarity() 函数进行模糊匹配
async function matchDocumentHeaders(
  documentNumbers: string[],
  documentType: string | null,
  tableName: string,
  supabaseClient: SupabaseClient
): Promise<DocumentHeaderMatchResult[]> {
  if (documentNumbers.length === 0) return [];
  
  // 1. 构建查询（使用 PostgreSQL similarity 函数）
  // 注意: 需要启用 pg_trgm 扩展
  const query = `
    SELECT 
      id,
      document_number,
      document_date,
      customer_name,
      supplier_name,
      counterparty_name,
      total_amount_with_tax,
      created_at,
      similarity(document_number, $1) as sim_score
    FROM ${tableName}
    WHERE document_number = ANY($2)
      AND is_deleted = false
    ORDER BY sim_score DESC
  `;
  
  const { data, error } = await supabaseClient.rpc('match_document_headers', {
    document_numbers: documentNumbers,
    table_name: tableName
  });
  
  if (error) {
    // 降级方案: 使用精确匹配
    return await matchDocumentHeadersExact(documentNumbers, tableName, supabaseClient);
  }
  
  // 2. 构建匹配字典
  const matchDict = new Map<string, any>();
  for (const record of data || []) {
    const docNum = record.document_number;
    if (!matchDict.has(docNum) || matchDict.get(docNum).sim_score < record.sim_score) {
      matchDict.set(docNum, record);
    }
  }
  
  // 3. 构建结果
  const results: DocumentHeaderMatchResult[] = [];
  for (const docNum of documentNumbers) {
    const matched = matchDict.get(docNum);
    
    if (matched && matched.sim_score >= 0.8) {
      results.push({
        documentNumber: docNum,
        headerId: matched.id,
        confidence: matched.sim_score,
        found: true,
        headerInfo: {
          id: matched.id,
          documentNumber: matched.document_number,
          documentDate: matched.document_date,
          customerName: matched.customer_name
        }
      });
    } else {
      results.push({
        documentNumber: docNum,
        headerId: null,
        confidence: 0.0,
        found: false,
        headerInfo: null,
        message: `系统中未找到单据号 ${docNum} 的单据头记录`
      });
    }
  }
  
  return results;
}

// 精确匹配降级方案
async function matchDocumentHeadersExact(
  documentNumbers: string[],
  tableName: string,
  supabaseClient: SupabaseClient
): Promise<DocumentHeaderMatchResult[]> {
  const { data, error } = await supabaseClient
    .from(tableName)
    .select('id, document_number, document_date, customer_name')
    .in('document_number', documentNumbers)
    .eq('is_deleted', false);
  
  if (error) {
    throw new Error(`查询失败: ${error.message}`);
  }
  
  const matchDict = new Map<string, any>();
  for (const record of data || []) {
    matchDict.set(record.document_number, record);
  }
  
  return documentNumbers.map(docNum => {
    const matched = matchDict.get(docNum);
    return {
      documentNumber: docNum,
      headerId: matched?.id || null,
      confidence: matched ? 1.0 : 0.0,
      found: !!matched,
      headerInfo: matched || null,
      message: matched ? undefined : `未找到单据号 ${docNum}`
    };
  });
}
```

### 4.3 复杂度分析

- **时间复杂度**: O(n × log m)，其中 n 是单据号数量，m 是数据库记录数
- **空间复杂度**: O(n)，存储匹配结果

### 4.4 测试用例

#### 测试用例 1: 精确匹配
```typescript
// 场景: 单据号 "PO001" 在数据库中存在
// 期望: found = true, confidence = 1.0, headerId 不为 null
```

#### 测试用例 2: 模糊匹配
```typescript
// 场景: 单据号 "PO001" 与数据库中的 "PO-001" 相似
// 期望: found = true, confidence >= 0.8
```

---

## 5. 数据验证算法 (Algorithm 5)

### 5.1 当前 Python 实现

**文件位置**: `backend/src/services/data_enhancement/data_quality_assessor.py`

**核心功能**:
- 必填字段验证
- 数据类型验证
- 业务规则验证
- 金额字段一致性验证（价税合计 = 不含税金额 + 税额）

### 5.2 TypeScript 转换方案

#### 核心逻辑

```typescript
interface ValidationRule {
  field: string;
  type: 'required' | 'type' | 'range' | 'format' | 'business';
  value?: any;
  message?: string;
}

interface ValidationResult {
  field: string;
  valid: boolean;
  message?: string;
  value?: any;
}

interface DataValidationReport {
  totalRows: number;
  validRows: number;
  invalidRows: number;
  errors: Array<{
    rowIndex: number;
    field: string;
    message: string;
    value?: any;
  }>;
  warnings: Array<{
    rowIndex: number;
    field: string;
    message: string;
  }>;
}

// 业务规则验证逻辑
function validateBusinessRules(
  data: Array<Record<string, any>>,
  rules: ValidationRule[]
): DataValidationReport {
  const errors: Array<{ rowIndex: number; field: string; message: string; value?: any }> = [];
  const warnings: Array<{ rowIndex: number; field: string; message: string }> = [];
  
  for (let i = 0; i < data.length; i++) {
    const row = data[i];
    
    // 1. 必填字段验证
    for (const rule of rules.filter(r => r.type === 'required')) {
      if (!row[rule.field] || row[rule.field] === '') {
        errors.push({
          rowIndex: i,
          field: rule.field,
          message: rule.message || `${rule.field} 是必填字段`,
          value: row[rule.field]
        });
      }
    }
    
    // 2. 数据类型验证
    for (const rule of rules.filter(r => r.type === 'type')) {
      const value = row[rule.field];
      if (value !== null && value !== undefined && value !== '') {
        const expectedType = rule.value; // 'number', 'string', 'date', etc.
        if (!validateType(value, expectedType)) {
          errors.push({
            rowIndex: i,
            field: rule.field,
            message: `${rule.field} 类型不正确，期望 ${expectedType}`,
            value
          });
        }
      }
    }
    
    // 3. 金额字段一致性验证
    const exTaxAmount = parseFloat(row['不含税金额'] || row['ex_tax_amount'] || '0');
    const taxAmount = parseFloat(row['税额'] || row['tax_amount'] || '0');
    const totalAmount = parseFloat(row['价税合计'] || row['total_amount_with_tax'] || '0');
    
    const calculatedTotal = exTaxAmount + taxAmount;
    const difference = Math.abs(totalAmount - calculatedTotal);
    
    if (difference > 0.01) { // 允许0.01的误差
      errors.push({
        rowIndex: i,
        field: '价税合计',
        message: `价税合计不一致: 计算值 ${calculatedTotal.toFixed(2)} ≠ 实际值 ${totalAmount.toFixed(2)}`,
        value: totalAmount
      });
    }
    
    // 4. 业务规则验证（自定义规则）
    for (const rule of rules.filter(r => r.type === 'business')) {
      const isValid = validateBusinessRule(row, rule);
      if (!isValid) {
        warnings.push({
          rowIndex: i,
          field: rule.field,
          message: rule.message || `业务规则验证失败: ${rule.field}`
        });
      }
    }
  }
  
  const validRows = data.length - errors.length;
  
  return {
    totalRows: data.length,
    validRows,
    invalidRows: errors.length,
    errors,
    warnings
  };
}

// 类型验证辅助函数
function validateType(value: any, expectedType: string): boolean {
  switch (expectedType) {
    case 'number':
      return typeof value === 'number' || !isNaN(parseFloat(value));
    case 'string':
      return typeof value === 'string';
    case 'date':
      return !isNaN(Date.parse(value));
    case 'integer':
      return Number.isInteger(value) || Number.isInteger(parseInt(value));
    default:
      return true;
  }
}
```

### 5.3 复杂度分析

- **时间复杂度**: O(n × r)，其中 n 是数据行数，r 是验证规则数
- **空间复杂度**: O(n)，存储验证结果

### 5.4 测试用例

#### 测试用例 1: 必填字段验证
```typescript
// 场景: 数据行缺少必填字段 "单据号"
// 期望: errors 包含该字段的错误信息
```

#### 测试用例 2: 金额一致性验证
```typescript
// 场景: 不含税金额=100, 税额=13, 价税合计=120
// 期望: errors 包含金额不一致的错误信息
```

---

## 📦 依赖库清单

### Deno 标准库
- 无需额外依赖（使用 Deno 内置功能）

### npm 包（通过 `deno.land/x/` 或 `npm:` 导入）

1. **文件解析**:
   - `xlsx` 或 `exceljs`: Excel 文件解析
   - `csv-parse`: CSV 文件解析

2. **字符串匹配**:
   - `fastest-levenshtein`: Levenshtein 距离计算
   - `fuzzysort`: 模糊字符串搜索
   - `fuse.js`: 模糊搜索（备选）

3. **中文处理**:
   - `pinyin-pro`: 中文拼音转换

4. **数据库**:
   - `@supabase/supabase-js`: Supabase 客户端

---

## ✅ 转换完成检查清单

- [x] 格式识别算法转换方案
- [x] 字段映射算法转换方案
- [x] 主数据匹配算法转换方案
- [x] 单据头匹配算法转换方案
- [x] 数据验证算法转换方案
- [x] 依赖库清单
- [x] 复杂度分析
- [x] 测试用例（每个算法至少3个）

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23  
**状态**: ✅ Cursor 准备完成，待 Lovable 实施

