# Edge Functions集成方案文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P1 - 重要文档**

**文档目的**: 提供Edge Functions调用FastAPI的集成方案，供Lovable在Edge Functions中实现

---

## 📋 目录

1. [调用流程](#1-调用流程)
2. [错误重试机制](#2-错误重试机制)
3. [环境变量配置](#3-环境变量配置)
4. [最佳实践](#4-最佳实践)

---

## 1. 调用流程

### 1.1 标准调用模式

```typescript
// Edge Function调用FastAPI的标准模式

import { createClient } from '@supabase/supabase-js';
import { corsHeaders, handleCors } from '../_shared/cors.ts';

/**
 * 调用FastAPI的标准函数
 * 
 * @param endpoint FastAPI端点路径（如 '/api/v1/document/recognize-format'）
 * @param payload 请求体数据
 * @param authHeader Supabase JWT token（从请求Header中获取）
 * @returns FastAPI响应数据
 */
async function callFastAPI(
  endpoint: string,
  payload: any,
  authHeader: string
): Promise<any> {
  // 1. 获取FastAPI URL（从环境变量）
  const fastApiUrl = Deno.env.get('FASTAPI_URL');
  
  if (!fastApiUrl) {
    throw new Error('FASTAPI_URL环境变量未配置');
  }
  
  // 2. 构建完整URL
  const url = `${fastApiUrl}${endpoint}`;
  
  // 3. 发送请求
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authHeader}`,  // 传递Supabase JWT
    },
    body: JSON.stringify(payload),
  });
  
  // 4. 检查响应状态
  if (!response.ok) {
    // 尝试解析错误响应
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error_message: response.statusText };
    }
    
    throw new Error(
      `FastAPI error (${response.status}): ${errorData.error_message || errorData.message || 'Unknown error'}`
    );
  }
  
  // 5. 解析响应数据
  const data = await response.json();
  return data;
}
```

### 1.2 使用示例：格式识别

```typescript
// supabase/functions/data-import-recognize-format/index.ts

import { createClient } from '@supabase/supabase-js';
import { corsHeaders, handleCors } from '../_shared/cors.ts';

Deno.serve(async (req) => {
  // 1. 处理CORS
  if (handleCors(req)) return handleCors(req);
  
  try {
    // 2. 获取请求参数
    const { file_id } = await req.json();
    
    // 3. 验证用户（获取Supabase client）
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: '缺少Authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: authHeader } } }
    );
    
    // 4. 获取文件
    const { data: upload } = await supabase
      .from('data_import_uploads')
      .select('*')
      .eq('id', file_id)
      .single();
    
    if (!upload) {
      return new Response(
        JSON.stringify({ error: '文件不存在' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    // 5. 下载文件
    const { data: fileData } = await supabase.storage
      .from('data-import')
      .download(upload.storage_path);
    
    if (!fileData) {
      return new Response(
        JSON.stringify({ error: '文件下载失败' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    // 6. 转换为Base64（如果需要）
    const arrayBuffer = await fileData.arrayBuffer();
    const base64Content = btoa(
      String.fromCharCode(...new Uint8Array(arrayBuffer))
    );
    
    // 7. 调用FastAPI
    const fastApiUrl = Deno.env.get('FASTAPI_URL');
    const response = await fetch(`${fastApiUrl}/api/v1/document/recognize-format`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify({
        file_content: base64Content,
        file_name: upload.file_name,
        tenant_id: upload.tenant_id,
        source_system: upload.source_system,
        document_type: upload.document_type,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`FastAPI error: ${error.error_message || error.message}`);
    }
    
    const result = await response.json();
    
    // 8. 保存结果到数据库
    await supabase
      .from('data_import_uploads')
      .update({
        detected_document_type: result.document_type,
        recognition_confidence: result.confidence,
        format_type: result.format_type,
        format_confidence: result.format_confidence,
      })
      .eq('id', file_id);
    
    // 9. 返回结果
    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
    
  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
```

---

## 2. 错误重试机制

### 2.1 带重试的调用函数

```typescript
/**
 * 带重试机制的FastAPI调用函数
 * 
 * @param endpoint FastAPI端点路径
 * @param payload 请求体数据
 * @param authHeader Supabase JWT token
 * @param maxRetries 最大重试次数（默认3次）
 * @param retryDelay 重试延迟（毫秒，默认1000ms）
 * @returns FastAPI响应数据
 */
async function callFastAPIWithRetry(
  endpoint: string,
  payload: any,
  authHeader: string,
  maxRetries: number = 3,
  retryDelay: number = 1000
): Promise<any> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      // 尝试调用FastAPI
      return await callFastAPI(endpoint, payload, authHeader);
      
    } catch (error) {
      lastError = error as Error;
      
      // 如果是最后一次尝试，直接抛出错误
      if (attempt === maxRetries - 1) {
        throw error;
      }
      
      // 判断是否应该重试
      const shouldRetry = shouldRetryError(error as Error);
      
      if (!shouldRetry) {
        // 不应该重试的错误（如400 Bad Request），直接抛出
        throw error;
      }
      
      // 指数退避：延迟时间 = retryDelay * 2^attempt
      const delay = retryDelay * Math.pow(2, attempt);
      console.log(`FastAPI调用失败，${delay}ms后重试 (${attempt + 1}/${maxRetries})`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // 理论上不会执行到这里
  throw lastError || new Error('FastAPI调用失败');
}

/**
 * 判断错误是否应该重试
 * 
 * @param error 错误对象
 * @returns 是否应该重试
 */
function shouldRetryError(error: Error): boolean {
  const message = error.message.toLowerCase();
  
  // 不应该重试的错误
  const nonRetryableErrors = [
    '400',
    '401',
    '403',
    '404',
    'invalid',
    'missing',
    'unauthorized',
    'forbidden',
    'not found'
  ];
  
  // 检查是否包含不应该重试的错误关键词
  for (const keyword of nonRetryableErrors) {
    if (message.includes(keyword)) {
      return false;
    }
  }
  
  // 其他错误（如500、502、503、504、timeout、network）应该重试
  return true;
}
```

### 2.2 重试策略说明

**重试策略**:
- **最大重试次数**: 3次（可配置）
- **重试延迟**: 指数退避（1s, 2s, 4s）
- **不应重试的错误**: 400, 401, 403, 404（客户端错误）
- **应该重试的错误**: 500, 502, 503, 504, timeout, network error（服务器错误或网络错误）

**使用示例**:
```typescript
try {
  const result = await callFastAPIWithRetry(
    '/api/v1/document/match-master-data',
    {
      entity_type: 'customer',
      input_values: [...],
      tenant_id: 'tenant-123',
      threshold: 0.8
    },
    authHeader,
    3,  // 最大重试3次
    1000  // 初始延迟1秒
  );
  
  return result;
} catch (error) {
  // 处理最终失败
  console.error('FastAPI调用最终失败:', error);
  throw error;
}
```

---

## 3. 环境变量配置

### 3.1 必需的环境变量

**FastAPI URL配置**:
```bash
# .env.local（本地开发）
FASTAPI_URL=http://localhost:8000

# Supabase Edge Functions环境变量（生产环境）
# 在Supabase Dashboard中配置：
# Settings > Edge Functions > Secrets
# FASTAPI_URL=https://your-fastapi-domain.com
```

**配置获取**:
```typescript
// 在Edge Function中获取环境变量
const fastApiUrl = Deno.env.get('FASTAPI_URL');

if (!fastApiUrl) {
  throw new Error('FASTAPI_URL环境变量未配置');
}
```

### 3.2 是否需要额外的API Key验证？

**建议**: 不需要额外的API Key验证，原因：
1. **JWT Token已足够**: Supabase生成的JWT token已经包含了用户身份和租户信息
2. **简化调用**: 不需要额外的API Key管理
3. **安全性**: JWT token验证已经提供了足够的安全性

**如果确实需要API Key**:
```typescript
// 在请求头中添加API Key
const response = await fetch(`${fastApiUrl}${endpoint}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authHeader}`,
    'X-API-Key': Deno.env.get('FASTAPI_API_KEY'),  // 可选
  },
  body: JSON.stringify(payload),
});
```

### 3.3 超时时间建议

**建议的超时时间**:
- **格式识别**: 30秒（文件解析可能较慢）
- **头行识别**: 20秒（数据处理可能较慢）
- **主数据匹配**: 60秒（批量匹配可能较慢）
- **单据头匹配**: 10秒（简单查询）

**实现**:
```typescript
async function callFastAPIWithTimeout(
  endpoint: string,
  payload: any,
  authHeader: string,
  timeoutMs: number = 30000
): Promise<any> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(`${fastApiUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authHeader}`,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,  // 添加AbortSignal
    });
    
    clearTimeout(timeoutId);
    return await response.json();
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error(`FastAPI调用超时（${timeoutMs}ms）`);
    }
    throw error;
  }
}
```

---

## 4. 最佳实践

### 4.1 共享工具函数

**创建共享工具函数** (`supabase/functions/_shared/fastapi-client.ts`):
```typescript
/**
 * FastAPI客户端工具函数
 */

export interface FastAPICallOptions {
  endpoint: string;
  payload: any;
  authHeader: string;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
}

/**
 * 调用FastAPI（带重试和超时）
 */
export async function callFastAPI(options: FastAPICallOptions): Promise<any> {
  const {
    endpoint,
    payload,
    authHeader,
    maxRetries = 3,
    retryDelay = 1000,
    timeout = 30000
  } = options;
  
  const fastApiUrl = Deno.env.get('FASTAPI_URL');
  if (!fastApiUrl) {
    throw new Error('FASTAPI_URL环境变量未配置');
  }
  
  const url = `${fastApiUrl}${endpoint}`;
  
  // 实现带重试和超时的调用逻辑
  // ...（参考上面的代码）
}

/**
 * 格式识别
 */
export async function recognizeFormat(
  fileContent: string,
  fileName: string,
  tenantId: string,
  authHeader: string,
  options?: { sourceSystem?: string; documentType?: string }
): Promise<any> {
  return await callFastAPI({
    endpoint: '/api/v1/document/recognize-format',
    payload: {
      file_content: fileContent,
      file_name: fileName,
      tenant_id: tenantId,
      ...options
    },
    authHeader,
    timeout: 30000  // 30秒超时
  });
}

/**
 * 头行识别
 */
export async function identifyHeaders(
  data: any[],
  documentType: string,
  tenantId: string,
  authHeader: string,
  options?: { formatType?: string; fieldMappings?: Record<string, string> }
): Promise<any> {
  return await callFastAPI({
    endpoint: '/api/v1/document/identify-headers',
    payload: {
      data,
      document_type: documentType,
      tenant_id: tenantId,
      ...options
    },
    authHeader,
    timeout: 20000  // 20秒超时
  });
}

/**
 * 主数据匹配
 */
export async function matchMasterData(
  entityType: string,
  inputValues: any[],
  tenantId: string,
  authHeader: string,
  options?: { threshold?: number; returnTop?: number }
): Promise<any> {
  return await callFastAPI({
    endpoint: '/api/v1/document/match-master-data',
    payload: {
      entity_type: entityType,
      input_values: inputValues,
      tenant_id: tenantId,
      threshold: options?.threshold || 0.8,
      return_top: options?.returnTop || 3
    },
    authHeader,
    timeout: 60000  // 60秒超时（批量匹配可能较慢）
  });
}
```

### 4.2 使用共享工具函数

```typescript
// 在Edge Function中使用共享工具函数
import { recognizeFormat, identifyHeaders, matchMasterData } from '../_shared/fastapi-client.ts';

Deno.serve(async (req) => {
  const authHeader = req.headers.get('Authorization')!;
  const { file_id } = await req.json();
  
  // 使用共享工具函数
  const result = await recognizeFormat(
    fileContent,
    fileName,
    tenantId,
    authHeader,
    { sourceSystem: 'ERP', documentType: 'SO' }
  );
  
  return new Response(JSON.stringify(result), {
    headers: { 'Content-Type': 'application/json' }
  });
});
```

### 4.3 错误处理最佳实践

```typescript
/**
 * 统一的错误处理函数
 */
function handleFastAPIError(error: Error): Response {
  const message = error.message.toLowerCase();
  
  // 客户端错误（400-499）
  if (message.includes('400') || message.includes('bad request')) {
    return new Response(
      JSON.stringify({ error: '请求参数错误', details: error.message }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }
  
  if (message.includes('401') || message.includes('unauthorized')) {
    return new Response(
      JSON.stringify({ error: '认证失败', details: error.message }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }
  
  if (message.includes('404') || message.includes('not found')) {
    return new Response(
      JSON.stringify({ error: '资源不存在', details: error.message }),
      { status: 404, headers: { 'Content-Type': 'application/json' } }
    );
  }
  
  // 服务器错误（500-599）
  if (message.includes('500') || message.includes('timeout')) {
    return new Response(
      JSON.stringify({ error: 'FastAPI服务暂时不可用，请稍后重试', details: error.message }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
  
  // 其他错误
  return new Response(
    JSON.stringify({ error: 'FastAPI调用失败', details: error.message }),
    { status: 500, headers: { 'Content-Type': 'application/json' } }
  );
}
```

---

## 5. 性能优化建议

### 5.1 并发调用

```typescript
/**
 * 并发调用多个FastAPI端点
 */
async function callMultipleFastAPIEndpoints(
  calls: Array<{ endpoint: string; payload: any }>,
  authHeader: string
): Promise<any[]> {
  const fastApiUrl = Deno.env.get('FASTAPI_URL')!;
  
  // 并发发送所有请求
  const promises = calls.map(({ endpoint, payload }) =>
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

### 5.2 批量处理

```typescript
/**
 * 批量处理数据（分批调用FastAPI）
 */
async function batchProcess(
  data: any[],
  batchSize: number,
  processFn: (batch: any[]) => Promise<any>
): Promise<any[]> {
  const results: any[] = [];
  
  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize);
    const batchResult = await processFn(batch);
    results.push(...batchResult);
  }
  
  return results;
}
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

