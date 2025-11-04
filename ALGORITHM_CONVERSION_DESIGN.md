# BMOS AI 算法转换设计文档

## 📋 概述

本文档描述如何将 FastAPI Python 算法转换为 Supabase Edge Functions (Deno/TypeScript) 实现。

## 🎯 核心算法清单

### Algorithm 1: 文档格式识别 ✅ 
**状态**: 已实现  
**位置**: `supabase/functions/_shared/format-detector.ts`

#### 算法描述
自动识别6种单据格式类型:
1. **格式1**: 多行明细对应重复单据头
2. **格式2**: 多行明细但只有第一行有单据头
3. **格式3**: 单据头和明细分离
4. **格式4**: 只有单据头记录
5. **格式5**: 只有明细记录
6. **格式6**: 纯单据头记录

#### 实现要点
```typescript
// 1. 字段查找 - 支持多种别名
function findColumn(data: Record<string, any>[], possibleNames: string[]): string | null

// 2. 格式检测函数
function detectRepeatedHeader(data): [confidence, details]
function detectFirstRowHeader(data): [confidence, details]
function detectSeparateHeaderBody(data): [confidence, details]
function detectHeaderOnly(data): [confidence, details]
function detectDetailOnly(data): [confidence, details]
function detectPureHeader(data): [confidence, details]

// 3. 主检测逻辑
export async function detectFormat(data, metadata?): Promise<FormatDetectionResult>
```

#### 转换要点
- ✅ Python dict → TypeScript Record<string, any>
- ✅ Python tuple → TypeScript array [number, object]
- ✅ Python set → TypeScript Set
- ✅ Python list comprehension → TypeScript map/filter
- ✅ Python f-string → TypeScript template literals

---

### Algorithm 2: 数据质量检测
**状态**: 待实现  
**位置**: `supabase/functions/_shared/data-validator.ts`

#### 算法描述
检测数据质量问题，包括:
1. **完整性检测**: 空值比例、必填字段缺失
2. **准确性检测**: 数据类型验证、格式验证
3. **一致性检测**: 重复记录、数据关联性
4. **异常值检测**: 统计离群点、业务规则违反

#### Python 原型
```python
def validate_data_quality(df: pd.DataFrame, rules: dict) -> QualityReport:
    """
    数据质量检测
    
    Args:
        df: pandas DataFrame
        rules: 验证规则字典
        
    Returns:
        QualityReport 包含质量分数和问题列表
    """
    report = QualityReport()
    
    # 1. 完整性检测
    null_ratio = df.isnull().sum() / len(df)
    report.completeness_score = 1.0 - null_ratio.mean()
    
    for field in rules.get('required_fields', []):
        if field not in df.columns:
            report.add_issue('MISSING_FIELD', field, severity='error')
        elif df[field].isnull().any():
            null_count = df[field].isnull().sum()
            report.add_issue('NULL_VALUE', field, 
                           affected_rows=null_count,
                           severity='error' if null_count/len(df) > 0.1 else 'warning')
    
    # 2. 准确性检测
    for field, dtype in rules.get('field_types', {}).items():
        if field in df.columns:
            try:
                df[field].astype(dtype)
            except:
                report.add_issue('TYPE_MISMATCH', field, severity='error')
    
    # 3. 一致性检测
    if rules.get('check_duplicates'):
        duplicates = df.duplicated()
        if duplicates.any():
            report.add_issue('DUPLICATE_ROWS', 
                           affected_rows=duplicates.sum(),
                           severity='warning')
    
    # 4. 异常值检测（针对数值字段）
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)).sum()
        if outliers > 0:
            report.add_issue('OUTLIERS', col, 
                           affected_rows=outliers,
                           severity='info')
    
    # 计算总体质量分数
    report.calculate_overall_score()
    
    return report
```

#### TypeScript 转换
```typescript
// supabase/functions/_shared/data-validator.ts

export interface ValidationRule {
  required_fields?: string[];
  field_types?: Record<string, string>;
  max_null_ratio?: number;
  check_duplicates?: boolean;
  outlier_detection?: boolean;
}

export interface QualityIssue {
  type: string;
  severity: 'error' | 'warning' | 'info';
  field?: string;
  description: string;
  affected_rows: number;
}

export interface QualityReport {
  overall_quality_score: number;
  completeness_score: number;
  accuracy_score: number;
  consistency_score: number;
  issues: QualityIssue[];
}

export async function validateDataQuality(
  data: Array<Record<string, any>>,
  rules: ValidationRule
): Promise<QualityReport> {
  const report: QualityReport = {
    overall_quality_score: 0,
    completeness_score: 0,
    accuracy_score: 0,
    consistency_score: 0,
    issues: []
  };
  
  if (data.length === 0) {
    return report;
  }
  
  const columns = Object.keys(data[0]);
  
  // 1. 完整性检测
  report.completeness_score = calculateCompleteness(data, columns);
  checkRequiredFields(data, rules.required_fields || [], report);
  
  // 2. 准确性检测
  report.accuracy_score = checkFieldTypes(data, rules.field_types || {}, report);
  
  // 3. 一致性检测
  report.consistency_score = 1.0;
  if (rules.check_duplicates) {
    checkDuplicates(data, report);
  }
  
  // 4. 异常值检测
  if (rules.outlier_detection) {
    detectOutliers(data, report);
  }
  
  // 计算总体分数
  report.overall_quality_score = (
    report.completeness_score +
    report.accuracy_score +
    report.consistency_score
  ) / 3;
  
  return report;
}

// 辅助函数
function calculateCompleteness(
  data: Array<Record<string, any>>,
  columns: string[]
): number {
  let totalFields = data.length * columns.length;
  let nullFields = 0;
  
  for (const row of data) {
    for (const col of columns) {
      if (row[col] === null || row[col] === undefined || row[col] === '') {
        nullFields++;
      }
    }
  }
  
  return 1.0 - (nullFields / totalFields);
}

function checkRequiredFields(
  data: Array<Record<string, any>>,
  requiredFields: string[],
  report: QualityReport
): void {
  const columns = Object.keys(data[0]);
  
  for (const field of requiredFields) {
    if (!columns.includes(field)) {
      report.issues.push({
        type: 'MISSING_FIELD',
        severity: 'error',
        field,
        description: `必填字段 "${field}" 不存在`,
        affected_rows: 0
      });
      continue;
    }
    
    let nullCount = 0;
    for (const row of data) {
      if (row[field] === null || row[field] === undefined || row[field] === '') {
        nullCount++;
      }
    }
    
    if (nullCount > 0) {
      const nullRatio = nullCount / data.length;
      report.issues.push({
        type: 'NULL_VALUE',
        severity: nullRatio > 0.1 ? 'error' : 'warning',
        field,
        description: `字段 "${field}" 包含 ${nullCount} 个空值 (${(nullRatio * 100).toFixed(1)}%)`,
        affected_rows: nullCount
      });
    }
  }
}

function checkFieldTypes(
  data: Array<Record<string, any>>,
  fieldTypes: Record<string, string>,
  report: QualityReport
): number {
  let correctTypeFields = 0;
  let totalChecked = 0;
  
  for (const [field, expectedType] of Object.entries(fieldTypes)) {
    if (!data[0].hasOwnProperty(field)) {
      continue;
    }
    
    let typeErrors = 0;
    for (const row of data) {
      const value = row[field];
      if (value === null || value === undefined || value === '') {
        continue;
      }
      
      totalChecked++;
      const actualType = typeof value;
      
      // 简化的类型检查
      if (expectedType === 'number' && actualType !== 'number') {
        if (isNaN(Number(value))) {
          typeErrors++;
        }
      } else if (expectedType === 'string' && actualType !== 'string') {
        typeErrors++;
      } else if (expectedType === 'boolean' && actualType !== 'boolean') {
        typeErrors++;
      } else {
        correctTypeFields++;
      }
    }
    
    if (typeErrors > 0) {
      report.issues.push({
        type: 'TYPE_MISMATCH',
        severity: 'error',
        field,
        description: `字段 "${field}" 类型不匹配，期望 ${expectedType}`,
        affected_rows: typeErrors
      });
    }
  }
  
  return totalChecked > 0 ? correctTypeFields / totalChecked : 1.0;
}

function checkDuplicates(
  data: Array<Record<string, any>>,
  report: QualityReport
): void {
  const seen = new Set<string>();
  let duplicates = 0;
  
  for (const row of data) {
    const key = JSON.stringify(row);
    if (seen.has(key)) {
      duplicates++;
    }
    seen.add(key);
  }
  
  if (duplicates > 0) {
    report.issues.push({
      type: 'DUPLICATE_ROWS',
      severity: 'warning',
      description: `检测到 ${duplicates} 行重复数据`,
      affected_rows: duplicates
    });
    report.consistency_score *= (1 - duplicates / data.length);
  }
}

function detectOutliers(
  data: Array<Record<string, any>>,
  report: QualityReport
): void {
  const columns = Object.keys(data[0]);
  
  for (const col of columns) {
    // 检查是否为数值列
    const values = data
      .map(row => row[col])
      .filter(v => v !== null && v !== undefined && typeof v === 'number' || !isNaN(Number(v)))
      .map(v => Number(v));
    
    if (values.length < 4) continue; // 数据太少，不进行异常值检测
    
    // 计算四分位数
    values.sort((a, b) => a - b);
    const q1 = quantile(values, 0.25);
    const q3 = quantile(values, 0.75);
    const iqr = q3 - q1;
    
    // 检测离群点
    let outlierCount = 0;
    for (const v of values) {
      if (v < q1 - 1.5 * iqr || v > q3 + 1.5 * iqr) {
        outlierCount++;
      }
    }
    
    if (outlierCount > 0) {
      report.issues.push({
        type: 'OUTLIERS',
        severity: 'info',
        field: col,
        description: `字段 "${col}" 检测到 ${outlierCount} 个异常值`,
        affected_rows: outlierCount
      });
    }
  }
}

function quantile(arr: number[], q: number): number {
  const sorted = [...arr].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  } else {
    return sorted[base];
  }
}
```

---

### Algorithm 3: 主数据匹配
**状态**: 待实现  
**位置**: `supabase/functions/_shared/master-data-matcher.ts`

#### 算法描述
使用模糊匹配算法将导入数据与主数据表匹配:
1. **精确匹配**: 完全相同的名称/代码
2. **模糊匹配**: Levenshtein距离、相似度评分
3. **多候选推荐**: 返回相似度最高的N个候选项
4. **缓存优化**: 缓存匹配结果提高性能

#### Python 原型
```python
from difflib import SequenceMatcher
import re

def calculate_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度 (0-1)"""
    # 标准化
    s1 = normalize_string(str1)
    s2 = normalize_string(str2)
    
    # 精确匹配
    if s1 == s2:
        return 1.0
    
    # 使用 SequenceMatcher
    return SequenceMatcher(None, s1, s2).ratio()

def normalize_string(s: str) -> str:
    """字符串标准化"""
    s = s.strip().lower()
    # 移除常见后缀
    suffixes = ['有限公司', '股份有限公司', '集团', '科技', '网络', 'ltd', 'inc', 'corp']
    for suffix in suffixes:
        s = s.replace(suffix, '')
    # 移除特殊字符
    s = re.sub(r'[^\w\s]', '', s)
    return s.strip()

def match_master_data(
    source_values: List[str],
    master_data: List[Dict],
    match_field: str,
    threshold: float = 0.8
) -> List[MatchResult]:
    """
    主数据匹配
    
    Args:
        source_values: 待匹配的值列表
        master_data: 主数据列表
        match_field: 匹配字段名
        threshold: 相似度阈值
        
    Returns:
        匹配结果列表
    """
    results = []
    
    for source_value in source_values:
        # 精确匹配
        exact_match = next(
            (item for item in master_data if item[match_field] == source_value),
            None
        )
        
        if exact_match:
            results.append({
                'source_value': source_value,
                'matched': True,
                'master_id': exact_match['id'],
                'master_name': exact_match[match_field],
                'confidence': 1.0
            })
            continue
        
        # 模糊匹配
        candidates = []
        for item in master_data:
            similarity = calculate_similarity(source_value, item[match_field])
            if similarity >= threshold:
                candidates.append({
                    'id': item['id'],
                    'name': item[match_field],
                    'similarity': similarity
                })
        
        # 按相似度排序
        candidates.sort(key=lambda x: x['similarity'], reverse=True)
        
        if candidates:
            best_match = candidates[0]
            results.append({
                'source_value': source_value,
                'matched': True,
                'master_id': best_match['id'],
                'master_name': best_match['name'],
                'confidence': best_match['similarity'],
                'candidates': candidates[:5]  # 返回top 5候选
            })
        else:
            results.append({
                'source_value': source_value,
                'matched': False,
                'confidence': 0.0,
                'candidates': []
            })
    
    return results
```

#### TypeScript 转换
```typescript
// supabase/functions/_shared/master-data-matcher.ts

export interface MatchCandidate {
  id: string;
  name: string;
  similarity: number;
}

export interface MatchResult {
  source_value: string;
  matched: boolean;
  master_id?: string;
  master_name?: string;
  confidence: number;
  candidates?: MatchCandidate[];
}

// Levenshtein 距离算法
function levenshteinDistance(str1: string, str2: string): number {
  const len1 = str1.length;
  const len2 = str2.length;
  const matrix: number[][] = [];
  
  for (let i = 0; i <= len1; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= len2; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,      // deletion
        matrix[i][j - 1] + 1,      // insertion
        matrix[i - 1][j - 1] + cost // substitution
      );
    }
  }
  
  return matrix[len1][len2];
}

// 计算相似度
export function calculateSimilarity(str1: string, str2: string): number {
  const s1 = normalizeString(str1);
  const s2 = normalizeString(str2);
  
  // 精确匹配
  if (s1 === s2) {
    return 1.0;
  }
  
  // 使用 Levenshtein 距离计算相似度
  const maxLen = Math.max(s1.length, s2.length);
  if (maxLen === 0) return 1.0;
  
  const distance = levenshteinDistance(s1, s2);
  return 1.0 - (distance / maxLen);
}

// 字符串标准化
export function normalizeString(s: string): string {
  let normalized = s.trim().toLowerCase();
  
  // 移除常见后缀
  const suffixes = [
    '有限公司', '股份有限公司', '集团', '科技', '网络', 
    'ltd', 'inc', 'corp', 'co.', 'limited'
  ];
  
  for (const suffix of suffixes) {
    normalized = normalized.replace(new RegExp(suffix + '$', 'i'), '');
  }
  
  // 移除特殊字符，保留中文、英文、数字
  normalized = normalized.replace(/[^\u4e00-\u9fa5a-z0-9\s]/gi, '');
  
  return normalized.trim();
}

// 主数据匹配
export async function matchMasterData(
  sourceValues: string[],
  masterData: Array<Record<string, any>>,
  matchField: string,
  threshold: number = 0.8
): Promise<MatchResult[]> {
  const results: MatchResult[] = [];
  
  for (const sourceValue of sourceValues) {
    // 1. 精确匹配
    const exactMatch = masterData.find(
      item => item[matchField] === sourceValue
    );
    
    if (exactMatch) {
      results.push({
        source_value: sourceValue,
        matched: true,
        master_id: exactMatch.id,
        master_name: exactMatch[matchField],
        confidence: 1.0
      });
      continue;
    }
    
    // 2. 模糊匹配
    const candidates: MatchCandidate[] = [];
    
    for (const item of masterData) {
      const similarity = calculateSimilarity(
        sourceValue,
        item[matchField]
      );
      
      if (similarity >= threshold) {
        candidates.push({
          id: item.id,
          name: item[matchField],
          similarity
        });
      }
    }
    
    // 按相似度排序
    candidates.sort((a, b) => b.similarity - a.similarity);
    
    if (candidates.length > 0) {
      const bestMatch = candidates[0];
      results.push({
        source_value: sourceValue,
        matched: true,
        master_id: bestMatch.id,
        master_name: bestMatch.name,
        confidence: bestMatch.similarity,
        candidates: candidates.slice(0, 5) // Top 5 候选
      });
    } else {
      results.push({
        source_value: sourceValue,
        matched: false,
        confidence: 0.0,
        candidates: []
      });
    }
  }
  
  return results;
}
```

---

### Algorithm 4: 单据头提取
**状态**: 待实现  
**位置**: `supabase/functions/_shared/header-extractor.ts`

#### 算法描述
根据识别的格式类型，从数据中提取单据头信息:
1. **格式1处理**: 去重复的单据头
2. **格式2处理**: 提取第一行单据头
3. **格式3处理**: 分离单据头和明细
4. **明细关联**: 建立单据头与明细行的关联关系

#### Python 原型
```python
def extract_headers(df: pd.DataFrame, format_type: str) -> List[DocumentHeader]:
    """
    提取单据头
    
    Args:
        df: 数据DataFrame
        format_type: 格式类型
        
    Returns:
        单据头列表
    """
    headers = []
    
    if format_type == 'repeated_header':
        # 格式1: 按单据号分组，每组取第一行作为单据头
        doc_col = find_column(df, ['单据号', 'document_number'])
        if doc_col:
            grouped = df.groupby(doc_col)
            for doc_num, group in grouped:
                header_row = group.iloc[0]
                headers.append({
                    'document_number': doc_num,
                    'document_date': header_row.get('单据日期'),
                    'customer_name': header_row.get('客户名称'),
                    'total_amount': group['金额'].sum() if '金额' in group.columns else None,
                    'detail_row_indices': group.index.tolist()
                })
    
    elif format_type == 'first_row_header':
        # 格式2: 第一行是单据头
        header_row = df.iloc[0]
        headers.append({
            'document_number': header_row.get('单据号'),
            'document_date': header_row.get('单据日期'),
            'customer_name': header_row.get('客户名称'),
            'total_amount': df['金额'].sum() if '金额' in df.columns else None,
            'detail_row_indices': list(range(len(df)))
        })
    
    elif format_type == 'separate_header_body':
        # 格式3: 单据头和明细分离
        # 假设第一行是单据头，后续是明细
        header_row = df.iloc[0]
        headers.append({
            'document_number': header_row.get('单据号'),
            'document_date': header_row.get('单据日期'),
            'customer_name': header_row.get('客户名称'),
            'total_amount': header_row.get('不含税金额'),
            'detail_row_indices': list(range(1, len(df)))
        })
    
    return headers
```

#### TypeScript 转换
```typescript
// supabase/functions/_shared/header-extractor.ts

export interface DocumentHeader {
  document_number: string;
  document_date?: string;
  customer_name?: string;
  total_amount?: number;
  detail_row_indices: number[];
  metadata?: Record<string, any>;
}

export async function extractHeaders(
  data: Array<Record<string, any>>,
  formatType: string
): Promise<DocumentHeader[]> {
  const headers: DocumentHeader[] = [];
  
  if (formatType === 'repeated_header') {
    // 格式1: 重复单据头，按单据号分组
    const docNumberCol = findColumn(data, ['单据号', 'document_number', '订单号']);
    
    if (!docNumberCol) {
      throw new Error('未找到单据号字段');
    }
    
    // 按单据号分组
    const grouped = new Map<string, number[]>();
    data.forEach((row, index) => {
      const docNum = row[docNumberCol];
      if (!grouped.has(docNum)) {
        grouped.set(docNum, []);
      }
      grouped.get(docNum)!.push(index);
    });
    
    // 提取每个单据的头信息
    for (const [docNum, indices] of grouped.entries()) {
      const firstRow = data[indices[0]];
      
      // 计算总金额
      let totalAmount = 0;
      const amountCol = findColumn(data, ['金额', 'amount', '不含税金额']);
      if (amountCol) {
        for (const idx of indices) {
          const amt = Number(data[idx][amountCol]) || 0;
          totalAmount += amt;
        }
      }
      
      headers.push({
        document_number: docNum,
        document_date: firstRow['单据日期'] || firstRow['document_date'],
        customer_name: firstRow['客户名称'] || firstRow['customer_name'],
        total_amount: totalAmount,
        detail_row_indices: indices
      });
    }
  } else if (formatType === 'first_row_header') {
    // 格式2: 只有第一行有单据头
    const firstRow = data[0];
    
    let totalAmount = 0;
    const amountCol = findColumn(data, ['金额', 'amount']);
    if (amountCol) {
      totalAmount = data.reduce((sum, row) => sum + (Number(row[amountCol]) || 0), 0);
    }
    
    headers.push({
      document_number: firstRow['单据号'] || firstRow['document_number'] || 'UNKNOWN',
      document_date: firstRow['单据日期'] || firstRow['document_date'],
      customer_name: firstRow['客户名称'] || firstRow['customer_name'],
      total_amount: totalAmount,
      detail_row_indices: Array.from({ length: data.length }, (_, i) => i)
    });
  } else if (formatType === 'separate_header_body') {
    // 格式3: 单据头和明细分离
    const headerRow = data[0];
    
    headers.push({
      document_number: headerRow['单据号'] || headerRow['document_number'] || 'UNKNOWN',
      document_date: headerRow['单据日期'] || headerRow['document_date'],
      customer_name: headerRow['客户名称'] || headerRow['customer_name'],
      total_amount: Number(headerRow['不含税金额'] || headerRow['total_amount']) || 0,
      detail_row_indices: Array.from({ length: data.length - 1 }, (_, i) => i + 1)
    });
  } else if (formatType === 'header_only') {
    // 格式4: 只有单据头，每行一个单据
    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      headers.push({
        document_number: row['单据号'] || row['document_number'] || `DOC-${i + 1}`,
        document_date: row['单据日期'] || row['document_date'],
        customer_name: row['客户名称'] || row['customer_name'],
        total_amount: Number(row['金额'] || row['amount']) || 0,
        detail_row_indices: [i]
      });
    }
  }
  
  return headers;
}

// 辅助函数：查找列名
function findColumn(data: Array<Record<string, any>>, possibleNames: string[]): string | null {
  if (data.length === 0) return null;
  
  const columns = Object.keys(data[0]);
  
  for (const colName of columns) {
    const normalized = colName.toLowerCase().trim();
    for (const possible of possibleNames) {
      if (normalized.includes(possible.toLowerCase()) || 
          possible.toLowerCase().includes(normalized)) {
        return colName;
      }
    }
  }
  
  return null;
}
```

---

## 🔄 通用转换模式

### Pandas → 原生TypeScript

#### 1. DataFrame操作
```python
# Python
df.groupby('column')['amount'].sum()
df['field'].isnull().sum()
df.drop_duplicates()
```

```typescript
// TypeScript
// 分组求和
const grouped = new Map<string, number>();
data.forEach(row => {
  const key = row['column'];
  grouped.set(key, (grouped.get(key) || 0) + row['amount']);
});

// 计算空值
const nullCount = data.filter(row => 
  row['field'] === null || row['field'] === undefined || row['field'] === ''
).length;

// 去重
const unique = Array.from(
  new Map(data.map(row => [JSON.stringify(row), row])).values()
);
```

#### 2. 数值计算
```python
# Python
import numpy as np
np.mean(df['column'])
np.quantile(df['column'], 0.75)
```

```typescript
// TypeScript
const mean = arr.reduce((sum, val) => sum + val, 0) / arr.length;

function quantile(arr: number[], q: number): number {
  const sorted = [...arr].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  return sorted[base] + rest * (sorted[base + 1] - sorted[base] || 0);
}
```

#### 3. 字符串处理
```python
# Python
text.lower().strip()
re.sub(r'[^\w\s]', '', text)
```

```typescript
// TypeScript
text.toLowerCase().trim()
text.replace(/[^\w\s]/g, '')
```

---

## 🧪 测试策略

### 1. 单元测试
每个算法模块独立测试，使用模拟数据。

### 2. 集成测试
在 Edge Functions 中调用算法，验证端到端流程。

### 3. 性能测试
测试大数据量下的性能表现（10万行+）。

---

## 📚 参考资源

- [Deno标准库](https://deno.land/std)
- [TypeScript文档](https://www.typescriptlang.org/docs/)
- [Levenshtein距离算法](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [数据质量检测最佳实践](https://www.talend.com/resources/what-is-data-quality/)
