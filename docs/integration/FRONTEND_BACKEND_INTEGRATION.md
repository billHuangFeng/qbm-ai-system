# 前后端集成说明文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **已完成**

**文档目的**: 说明前端如何调用后端字段映射推荐API，包括缓存策略和错误处理

---

## 📋 目录

1. [前端调用后端API](#1-前端调用后端api)
2. [缓存策略说明](#2-缓存策略说明)
3. [错误处理指南](#3-错误处理指南)
4. [最佳实践](#4-最佳实践)

---

## 1. 前端调用后端API

### 1.1 创建API客户端

```typescript
// src/lib/api/data-import.ts

import { supabase } from '@/lib/supabase';

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';

/**
 * 获取JWT Token（从Supabase获取）
 */
async function getAuthToken(): Promise<string> {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error('未登录或Token无效');
  }
  return session.access_token;
}

/**
 * 调用FastAPI的标准函数
 */
async function callFastAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();
  
  const response = await fetch(`${FASTAPI_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `API调用失败: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * 字段映射推荐API
 */
export async function recommendFieldMappings(params: {
  sourceFields: string[];
  targetTable: string;
  sourceSystem?: string;
  documentType?: string;
}): Promise<any> {
  return callFastAPI('/api/v1/data-enhancement/recommend-field-mappings', {
    method: 'POST',
    body: JSON.stringify({
      source_fields: params.sourceFields,
      target_table: params.targetTable,
      source_system: params.sourceSystem || 'upload',
      document_type: params.documentType
    })
  });
}

/**
 * 获取表结构API
 */
export async function getTableSchema(
  tableName: string,
  documentType?: string
): Promise<any> {
  const queryParams = documentType ? `?document_type=${documentType}` : '';
  return callFastAPI(`/api/v1/data-enhancement/table-schema/${tableName}${queryParams}`);
}

/**
 * 获取可用表列表API
 */
export async function getAvailableTables(documentType?: string): Promise<any> {
  const queryParams = documentType ? `?document_type=${documentType}` : '';
  return callFastAPI(`/api/v1/data-enhancement/available-tables${queryParams}`);
}

/**
 * 保存映射历史API
 */
export async function saveMappingHistory(params: {
  sourceSystem: string;
  targetTable: string;
  sourceField: string;
  targetField: string;
  documentType?: string;
  mappingMethod?: string;
  confidenceScore?: number;
}): Promise<any> {
  return callFastAPI('/api/v1/data-enhancement/save-mapping-history', {
    method: 'POST',
    body: JSON.stringify({
      source_system: params.sourceSystem,
      target_table: params.targetTable,
      source_field: params.sourceField,
      target_field: params.targetField,
      document_type: params.documentType,
      mapping_method: params.mappingMethod || 'manual',
      confidence_score: params.confidenceScore
    })
  });
}
```

### 1.2 使用示例

```typescript
// src/components/data-import/FieldMappingEditor.tsx

import { useState, useEffect } from 'react';
import { 
  recommendFieldMappings, 
  getTableSchema, 
  getAvailableTables,
  saveMappingHistory 
} from '@/lib/api/data-import';

export function FieldMappingEditor({ 
  sourceFields, 
  documentType 
}: FieldMappingEditorProps) {
  const [targetTable, setTargetTable] = useState<string>('');
  const [targetFields, setTargetFields] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 1. 获取可用表列表
  useEffect(() => {
    async function loadAvailableTables() {
      try {
        const result = await getAvailableTables(documentType);
        // 显示表列表供用户选择
        console.log(result.tables);
      } catch (error) {
        console.error('获取可用表列表失败:', error);
      }
    }
    
    if (documentType) {
      loadAvailableTables();
    }
  }, [documentType]);
  
  // 2. 获取表结构（当用户选择目标表时）
  useEffect(() => {
    async function loadTableSchema() {
      if (!targetTable) return;
      
      setLoading(true);
      try {
        const result = await getTableSchema(targetTable, documentType);
        setTargetFields(result.fields);
        console.log('表字段:', result.fields);
        console.log('主数据匹配字段:', result.master_data_fields);
      } catch (error) {
        console.error('获取表结构失败:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadTableSchema();
  }, [targetTable, documentType]);
  
  // 3. 获取字段映射推荐（当用户选择目标表后）
  useEffect(() => {
    async function loadRecommendations() {
      if (!targetTable || !sourceFields.length) return;
      
      setLoading(true);
      try {
        const result = await recommendFieldMappings({
          sourceFields,
          targetTable,
          documentType
        });
        setRecommendations(result.recommendations);
        console.log('映射推荐:', result.recommendations);
      } catch (error) {
        console.error('获取映射推荐失败:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadRecommendations();
  }, [targetTable, sourceFields, documentType]);
  
  // 4. 保存映射历史（用户确认映射后）
  const handleSaveMapping = async (
    sourceField: string, 
    targetField: string
  ) => {
    try {
      await saveMappingHistory({
        sourceSystem: 'upload',
        targetTable,
        sourceField,
        targetField,
        documentType,
        mappingMethod: 'manual',
        confidenceScore: 1.0
      });
      console.log('映射历史保存成功');
    } catch (error) {
      console.error('保存映射历史失败:', error);
    }
  };
  
  return (
    <div>
      {/* UI组件 */}
    </div>
  );
}
```

---

## 2. 缓存策略说明

### 2.1 后端缓存策略

**表结构缓存**:
- **缓存层级**: 内存缓存 + Redis缓存
- **TTL**: 24小时（表结构变化不频繁）
- **缓存键**: `field_mapper:table_fields:{table_name}`

**字段映射推荐缓存**:
- **缓存层级**: 历史映射查询结果缓存
- **TTL**: 永久（直到用户更新映射）
- **缓存键**: 基于`tenant_id`、`source_system`、`target_table`、`source_field`

### 2.2 前端缓存策略

**建议实现**:
```typescript
// src/lib/cache/table-schema-cache.ts

const schemaCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 24 * 60 * 60 * 1000;  // 24小时

export async function getTableSchemaCached(
  tableName: string,
  documentType?: string
): Promise<any> {
  const cacheKey = `${tableName}:${documentType || ''}`;
  const cached = schemaCache.get(cacheKey);
  
  // 检查缓存是否有效
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  
  // 从API获取
  const data = await getTableSchema(tableName, documentType);
  
  // 更新缓存
  schemaCache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  
  return data;
}
```

### 2.3 缓存失效策略

**自动失效**:
- 表结构缓存：24小时后自动失效
- 映射历史缓存：保存新映射后，相关缓存自动失效

**手动清除**:
```typescript
// 清除特定表的缓存
export function clearTableSchemaCache(tableName: string) {
  const keys = Array.from(schemaCache.keys()).filter(key => 
    key.startsWith(`${tableName}:`)
  );
  keys.forEach(key => schemaCache.delete(key));
}
```

---

## 3. 错误处理指南

### 3.1 错误类型

**网络错误**:
```typescript
try {
  const result = await recommendFieldMappings({...});
} catch (error) {
  if (error.message.includes('Failed to fetch')) {
    // 网络错误
    showError('网络连接失败，请检查网络');
  }
}
```

**认证错误**:
```typescript
try {
  const result = await recommendFieldMappings({...});
} catch (error) {
  if (error.message.includes('401') || error.message.includes('未登录')) {
    // 认证失败
    showError('登录已过期，请重新登录');
    // 跳转到登录页面
    router.push('/login');
  }
}
```

**参数错误**:
```typescript
try {
  const result = await recommendFieldMappings({...});
} catch (error) {
  if (error.message.includes('target_table 是必需的')) {
    // 参数错误
    showError('请选择目标表');
  }
}
```

**服务器错误**:
```typescript
try {
  const result = await recommendFieldMappings({...});
} catch (error) {
  if (error.message.includes('500')) {
    // 服务器错误
    showError('服务器错误，请稍后重试');
    // 记录错误日志
    console.error('API错误:', error);
  }
}
```

### 3.2 统一错误处理Hook

```typescript
// src/hooks/useApiError.ts

import { useState, useCallback } from 'react';

export function useApiError() {
  const [error, setError] = useState<string | null>(null);
  
  const handleError = useCallback((error: Error) => {
    let errorMessage = '操作失败';
    
    if (error.message.includes('401')) {
      errorMessage = '登录已过期，请重新登录';
    } else if (error.message.includes('400')) {
      errorMessage = '请求参数错误';
    } else if (error.message.includes('404')) {
      errorMessage = '资源不存在';
    } else if (error.message.includes('500')) {
      errorMessage = '服务器错误，请稍后重试';
    } else {
      errorMessage = error.message;
    }
    
    setError(errorMessage);
    
    // 3秒后自动清除错误
    setTimeout(() => setError(null), 3000);
  }, []);
  
  return { error, handleError, clearError: () => setError(null) };
}
```

### 3.3 重试机制

```typescript
// src/lib/api/retry.ts

/**
 * 带重试的API调用
 */
export async function callFastAPIWithRetry<T>(
  endpoint: string,
  options: RequestInit = {},
  maxRetries: number = 3
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await callFastAPI<T>(endpoint, options);
    } catch (error) {
      lastError = error as Error;
      
      // 如果是客户端错误（400-499），不重试
      if (error instanceof Error && error.message.includes('40')) {
        throw error;
      }
      
      // 如果是最后一次尝试，抛出错误
      if (attempt === maxRetries - 1) {
        throw error;
      }
      
      // 指数退避
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError || new Error('API调用失败');
}
```

---

## 4. 最佳实践

### 4.1 性能优化

**批量保存映射历史**:
```typescript
// 批量保存映射历史，减少API调用次数
async function saveMappingHistoryBatch(
  mappings: Array<{
    sourceField: string;
    targetField: string;
  }>
) {
  const promises = mappings.map(mapping =>
    saveMappingHistory({
      sourceSystem: 'upload',
      targetTable,
      sourceField: mapping.sourceField,
      targetField: mapping.targetField,
      documentType
    })
  );
  
  await Promise.all(promises);
}
```

**预加载表结构**:
```typescript
// 在用户选择单据类型时，预加载相关表的结构
useEffect(() => {
  if (documentType) {
    // 预加载常用表的结构
    const commonTables = ['sales_order_header', 'purchase_order_header'];
    commonTables.forEach(table => {
      getTableSchemaCached(table, documentType).catch(() => {
        // 静默失败，不影响用户体验
      });
    });
  }
}, [documentType]);
```

### 4.2 用户体验优化

**加载状态提示**:
```typescript
const [loading, setLoading] = useState(false);
const [loadingMessage, setLoadingMessage] = useState('');

async function loadRecommendations() {
  setLoading(true);
  setLoadingMessage('正在获取映射推荐...');
  
  try {
    const result = await recommendFieldMappings({...});
    setRecommendations(result.recommendations);
  } finally {
    setLoading(false);
    setLoadingMessage('');
  }
}
```

**乐观更新**:
```typescript
// 保存映射历史时，先更新UI，再调用API
const handleSaveMapping = async (sourceField: string, targetField: string) => {
  // 乐观更新：立即更新UI
  setMappings(prev => ({
    ...prev,
    [sourceField]: targetField
  }));
  
  try {
    await saveMappingHistory({...});
  } catch (error) {
    // 如果失败，回滚UI
    setMappings(prev => {
      const next = { ...prev };
      delete next[sourceField];
      return next;
    });
    showError('保存失败，请重试');
  }
};
```

---

## 5. 完整集成示例

### 5.1 React Hook示例

```typescript
// src/hooks/useFieldMapping.ts

import { useState, useEffect, useCallback } from 'react';
import {
  recommendFieldMappings,
  getTableSchema,
  getAvailableTables,
  saveMappingHistory
} from '@/lib/api/data-import';

export function useFieldMapping(
  sourceFields: string[],
  documentType?: string
) {
  const [targetTable, setTargetTable] = useState<string>('');
  const [targetFields, setTargetFields] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [availableTables, setAvailableTables] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 加载可用表列表
  useEffect(() => {
    async function loadTables() {
      try {
        const result = await getAvailableTables(documentType);
        setAvailableTables(result.tables);
      } catch (err) {
        setError('获取可用表列表失败');
      }
    }
    
    if (documentType) {
      loadTables();
    }
  }, [documentType]);
  
  // 加载表结构
  useEffect(() => {
    async function loadSchema() {
      if (!targetTable) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const result = await getTableSchema(targetTable, documentType);
        setTargetFields(result.fields);
      } catch (err) {
        setError('获取表结构失败');
      } finally {
        setLoading(false);
      }
    }
    
    loadSchema();
  }, [targetTable, documentType]);
  
  // 加载映射推荐
  useEffect(() => {
    async function loadRecommendations() {
      if (!targetTable || !sourceFields.length) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const result = await recommendFieldMappings({
          sourceFields,
          targetTable,
          documentType
        });
        setRecommendations(result.recommendations);
      } catch (err) {
        setError('获取映射推荐失败');
      } finally {
        setLoading(false);
      }
    }
    
    loadRecommendations();
  }, [targetTable, sourceFields, documentType]);
  
  // 保存映射历史
  const saveMapping = useCallback(async (
    sourceField: string,
    targetField: string
  ) => {
    try {
      await saveMappingHistory({
        sourceSystem: 'upload',
        targetTable,
        sourceField,
        targetField,
        documentType
      });
      return true;
    } catch (err) {
      setError('保存映射历史失败');
      return false;
    }
  }, [targetTable, documentType]);
  
  return {
    targetTable,
    setTargetTable,
    targetFields,
    recommendations,
    availableTables,
    loading,
    error,
    saveMapping
  };
}
```

### 5.2 组件使用示例

```typescript
// src/components/data-import/FieldMappingEditor.tsx

import { useFieldMapping } from '@/hooks/useFieldMapping';

export function FieldMappingEditor({ 
  sourceFields, 
  documentType 
}: FieldMappingEditorProps) {
  const {
    targetTable,
    setTargetTable,
    targetFields,
    recommendations,
    availableTables,
    loading,
    error,
    saveMapping
  } = useFieldMapping(sourceFields, documentType);
  
  return (
    <div>
      {/* 表选择器 */}
      <select value={targetTable} onChange={e => setTargetTable(e.target.value)}>
        <option value="">请选择目标表</option>
        {availableTables.map(table => (
          <option key={table.table_name} value={table.table_name}>
            {table.display_name}
          </option>
        ))}
      </select>
      
      {/* 映射推荐列表 */}
      {loading && <div>加载中...</div>}
      {error && <div className="error">{error}</div>}
      
      {recommendations.map(rec => (
        <div key={rec.source_field}>
          <span>{rec.source_field}</span>
          <select
            value={rec.recommended_target || ''}
            onChange={e => saveMapping(rec.source_field, e.target.value)}
          >
            {rec.candidates.map(candidate => (
              <option key={candidate.target_field} value={candidate.target_field}>
                {candidate.target_field} ({candidate.confidence * 100}%)
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
}
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

