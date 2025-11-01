# Data-Import 路由决策指南

**创建时间**: 2025-10-31  
**版本**: 1.0

---

## 📋 目的

本指南帮助前端和系统自动判断应该使用 **Edge Functions** 还是 **FastAPI** 来处理数据导入请求。

---

## 🎯 决策流程

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
快速响应         深度处理
    ↓              ↓
返回结果         返回结果
```

---

## 📐 决策标准

### 使用 Edge Functions 的条件（必须全部满足）✅

1. **文件格式**: CSV 或 JSON
   - ✅ `.csv` 文件
   - ✅ `.json` 文件
   - ❌ `.xlsx`, `.xls` → 使用 FastAPI
   - ❌ `.xml` → 使用 FastAPI

2. **文件大小**: < 1MB
   - ✅ 文件大小 < 1,048,576 字节
   - ❌ ≥ 1MB → 使用 FastAPI

3. **数据行数**: < 10,000行
   - ✅ 预估行数 < 10,000
   - ❌ ≥ 10,000行 → 使用 FastAPI

4. **字段映射**: 简单映射
   - ✅ 字段名相同或预定义映射
   - ✅ 无需智能映射算法
   - ❌ 需要智能映射 → 使用 FastAPI

5. **数据转换**: 无需复杂转换
   - ✅ 基础类型转换
   - ✅ 简单清洗
   - ❌ 复杂ETL转换 → 使用 FastAPI

6. **质量检查**: 基础验证即可
   - ✅ 必填字段检查
   - ✅ 基本类型验证
   - ❌ 需要深度质量分析 → 使用 FastAPI

---

### 使用 FastAPI 的条件（满足任一即可）✅

1. **文件格式**: 复杂格式
   - ✅ Excel (`.xlsx`, `.xls`)
   - ✅ XML (`.xml`)
   - ✅ 其他复杂格式

2. **文件大小**: ≥ 1MB
   - ✅ 文件大小 ≥ 1,048,576 字节

3. **数据行数**: ≥ 10,000行
   - ✅ 预估行数 ≥ 10,000

4. **字段映射**: 需要智能映射
   - ✅ 需要自动识别字段
   - ✅ 需要复杂映射规则
   - ✅ 需要机器学习映射

5. **数据转换**: 需要复杂转换
   - ✅ 复杂ETL流程
   - ✅ 数据清洗规则
   - ✅ 数据计算和衍生字段

6. **质量检查**: 需要深度分析
   - ✅ 7项质量指标评估
   - ✅ 完整性、准确性、一致性等
   - ✅ 质量报告和建议

---

## 🔍 自动判断逻辑

### 前端判断逻辑（TypeScript）

```typescript
interface FileInfo {
  name: string;
  size: number;
  type: string;
}

function shouldUseEdgeFunctions(file: FileInfo, options?: {
  estimatedRows?: number;
  needComplexMapping?: boolean;
  needComplexETL?: boolean;
  needDeepQualityCheck?: boolean;
}): boolean {
  // 1. 检查文件格式
  const ext = file.name.split('.').pop()?.toLowerCase();
  if (ext !== 'csv' && ext !== 'json') {
    return false; // 使用 FastAPI
  }
  
  // 2. 检查文件大小
  if (file.size >= 1_048_576) { // 1MB
    return false; // 使用 FastAPI
  }
  
  // 3. 检查数据行数（如果提供）
  if (options?.estimatedRows && options.estimatedRows >= 10_000) {
    return false; // 使用 FastAPI
  }
  
  // 4. 检查是否需要复杂映射
  if (options?.needComplexMapping) {
    return false; // 使用 FastAPI
  }
  
  // 5. 检查是否需要复杂ETL
  if (options?.needComplexETL) {
    return false; // 使用 FastAPI
  }
  
  // 6. 检查是否需要深度质量检查
  if (options?.needDeepQualityCheck) {
    return false; // 使用 FastAPI
  }
  
  // 所有条件都满足，使用 Edge Functions
  return true;
}
```

### 后端判断逻辑（FastAPI，用于回退）

```python
def should_use_edge_functions(
    file_name: str,
    file_size: int,
    file_format: str,
    estimated_rows: Optional[int] = None,
    need_complex_mapping: bool = False,
    need_complex_etl: bool = False,
    need_deep_quality_check: bool = False
) -> bool:
    """判断是否应该使用Edge Functions"""
    
    # 1. 检查文件格式
    ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
    if ext not in ['csv', 'json']:
        return False
    
    # 2. 检查文件大小
    if file_size >= 1_048_576:  # 1MB
        return False
    
    # 3. 检查数据行数
    if estimated_rows and estimated_rows >= 10_000:
        return False
    
    # 4. 检查是否需要复杂功能
    if need_complex_mapping or need_complex_etl or need_deep_quality_check:
        return False
    
    # 所有条件都满足
    return True
```

---

## 📊 决策矩阵

| 场景 | 文件格式 | 文件大小 | 行数 | 映射 | ETL | 质量检查 | 使用 |
|------|---------|---------|------|------|-----|---------|------|
| **场景1** | CSV | 500KB | 5,000 | 简单 | 无 | 基础 | ✅ Edge Functions |
| **场景2** | JSON | 800KB | 8,000 | 简单 | 无 | 基础 | ✅ Edge Functions |
| **场景3** | Excel | 500KB | 5,000 | 简单 | 无 | 基础 | ❌ FastAPI |
| **场景4** | CSV | 2MB | 5,000 | 简单 | 无 | 基础 | ❌ FastAPI |
| **场景5** | CSV | 500KB | 20,000 | 简单 | 无 | 基础 | ❌ FastAPI |
| **场景6** | CSV | 500KB | 5,000 | 复杂 | 无 | 基础 | ❌ FastAPI |
| **场景7** | CSV | 500KB | 5,000 | 简单 | 复杂 | 基础 | ❌ FastAPI |
| **场景8** | CSV | 500KB | 5,000 | 简单 | 无 | 深度 | ❌ FastAPI |

---

## 🔄 实施建议

### 前端实现

1. **预检查**: 上传前检查文件特性
2. **自动路由**: 根据检查结果选择API端点
3. **用户提示**: 如果文件太大或复杂，提示用户可能需要更长时间处理
4. **回退机制**: 如果Edge Functions失败，自动回退到FastAPI

### 后端实现

1. **Edge Functions**: 实现简单的导入逻辑
2. **FastAPI**: 实现完整的ETL流程
3. **统一响应格式**: 两者返回格式一致，便于前端处理

---

## 📝 API端点对比

### Edge Functions: 简单导入

**端点**: `POST /functions/v1/data-import`

**特点**:
- ✅ 快速响应（< 10秒）
- ✅ 简单验证和写入
- ✅ 基础质量检查
- ❌ 不支持复杂格式
- ❌ 不支持复杂ETL

### FastAPI: 复杂ETL

**端点**: `POST /api/v1/data-import/import`

**特点**:
- ✅ 支持所有格式
- ✅ 复杂ETL处理
- ✅ 深度质量分析
- ⚠️ 可能需要较长时间（> 10秒）
- ✅ 支持大文件处理

---

## 🚀 使用示例

### 前端自动路由示例

```typescript
async function importData(file: File, options: ImportOptions) {
  const fileInfo = {
    name: file.name,
    size: file.size,
    type: file.type
  };
  
  // 自动判断使用哪个端点
  const useEdgeFunctions = shouldUseEdgeFunctions(fileInfo, {
    estimatedRows: options.estimatedRows,
    needComplexMapping: options.needComplexMapping,
    needComplexETL: options.needComplexETL,
    needDeepQualityCheck: options.needDeepQualityCheck
  });
  
  if (useEdgeFunctions) {
    // 使用 Edge Functions（快速）
    return await importViaEdgeFunctions(file, options);
  } else {
    // 使用 FastAPI（复杂ETL）
    return await importViaFastAPI(file, options);
  }
}
```

### 回退机制示例

```typescript
async function importWithFallback(file: File, options: ImportOptions) {
  try {
    // 先尝试 Edge Functions
    if (shouldUseEdgeFunctions(fileInfo, options)) {
      try {
        return await importViaEdgeFunctions(file, options);
      } catch (error) {
        // Edge Functions失败，回退到FastAPI
        console.warn('Edge Functions failed, falling back to FastAPI', error);
        return await importViaFastAPI(file, options);
      }
    } else {
      // 直接使用 FastAPI
      return await importViaFastAPI(file, options);
    }
  } catch (error) {
    throw new Error(`Data import failed: ${error.message}`);
  }
}
```

---

## ✅ 最佳实践

1. **预检查优先**: 上传前先检查文件特性，减少不必要的请求
2. **默认快速**: 如果可能，默认使用Edge Functions（更快）
3. **自动回退**: Edge Functions失败时自动回退到FastAPI
4. **用户提示**: 明确告知用户处理时间和方式
5. **进度跟踪**: FastAPI处理时显示进度（如果支持）

---

## 📚 相关文档

- [分工方案文档](./DATA_IMPORT_DIVISION_PLAN.md)
- [决策指南文档](./FASTAPI_EDGE_FUNCTIONS_DECISION_GUIDE.md)
- [Edge Functions规范](../architecture/SUPABASE_EDGE_FUNCTIONS_SPEC.md)
- [FastAPI ETL服务](../backend/src/services/data_import_etl.py)

---

**文档版本**: 1.0  
**最后更新**: 2025-10-31

