# Supabase Edge Functions API设计模板

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **可用**

---

## 📋 重要说明

**⚠️ 技术栈约束**: Lovable只能使用Supabase Edge Functions，不能使用FastAPI Python后端。

所有API设计必须：
- ✅ 使用TypeScript编写
- ✅ 符合Deno Runtime规范
- ✅ 执行时间 ≤ 10秒
- ✅ 计算复杂度 O(n) 或更低
- ✅ 仅使用Supabase SDK和Deno标准库

---

## 🔧 Edge Function标准模板

### 模板1: 基础CRUD操作

```typescript
// supabase/functions/[resource-name]/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// 类型定义
interface CreateRequest {
  table: string;
  data: Record<string, any>;
}

interface ReadRequest {
  table: string;
  id?: string;
  filters?: Record<string, any>;
  limit?: number;
  offset?: number;
}

interface UpdateRequest {
  table: string;
  id: string;
  data: Record<string, any>;
}

interface DeleteRequest {
  table: string;
  id: string;
}

// CORS处理
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  // 处理CORS预检请求
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // 创建Supabase客户端
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    );

    const { action, ...body } = await req.json();

    switch (action) {
      case 'create': {
        const { table, data }: CreateRequest = body;
        
        if (!table || !data) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing table or data' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }

        const { data: result, error } = await supabaseClient
          .from(table)
          .insert(data)
          .select();

        if (error) throw error;

        return new Response(
          JSON.stringify({ success: true, data: result }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      case 'read': {
        const { table, id, filters, limit, offset }: ReadRequest = body;
        
        if (!table) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing table' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }

        let query = supabaseClient.from(table).select('*');

        if (id) {
          query = query.eq('id', id);
        } else if (filters) {
          Object.entries(filters).forEach(([key, value]) => {
            query = query.eq(key, value);
          });
        }

        if (limit) query = query.limit(limit);
        if (offset) query = query.range(offset, offset + (limit || 10) - 1);

        const { data: result, error } = await query;

        if (error) throw error;

        return new Response(
          JSON.stringify({ success: true, data: result }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      case 'update': {
        const { table, id, data }: UpdateRequest = body;
        
        if (!table || !id || !data) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing table, id, or data' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }

        const { data: result, error } = await supabaseClient
          .from(table)
          .update(data)
          .eq('id', id)
          .select();

        if (error) throw error;

        return new Response(
          JSON.stringify({ success: true, data: result }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      case 'delete': {
        const { table, id }: DeleteRequest = body;
        
        if (!table || !id) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing table or id' }),
            { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        }

        const { error } = await supabaseClient
          .from(table)
          .delete()
          .eq('id', id);

        if (error) throw error;

        return new Response(
          JSON.stringify({ success: true, message: 'Deleted successfully' }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      default:
        return new Response(
          JSON.stringify({ success: false, error: 'Invalid action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }

  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message || 'Internal server error' 
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});
```

---

### 模板2: 算法计算端点

```typescript
// supabase/functions/[algorithm-name]/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { 
  linearRegression,
  movingAverage,
  weightedScoring,
  // ... 其他算法函数
} from '../../utils/algorithms.ts'; // 假设算法函数在utils目录

interface AlgorithmRequest {
  algorithm: string;
  input: any;
  config?: any;
}

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { algorithm, input, config }: AlgorithmRequest = await req.json();

    if (!algorithm || !input) {
      return new Response(
        JSON.stringify({ success: false, error: 'Missing algorithm or input' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    let result: any;

    // 执行算法
    switch (algorithm) {
      case 'linear-regression':
        result = await linearRegression(input, config);
        break;

      case 'moving-average':
        result = await movingAverage(input, config);
        break;

      case 'weighted-scoring':
        result = await weightedScoring(input, config);
        break;

      // ... 其他算法

      default:
        return new Response(
          JSON.stringify({ success: false, error: 'Unknown algorithm' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }

    return new Response(
      JSON.stringify({ success: true, result }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message || 'Internal server error' 
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});
```

---

## 📝 API文档格式

### 标准API文档模板

```markdown
# [功能名称] Edge Functions API

## 函数路径
`supabase/functions/[function-name]/index.ts`

## 调用方式

### 前端调用
```typescript
const { data, error } = await supabase.functions.invoke('[function-name]', {
  body: {
    // 请求参数
  }
});
```

### HTTP调用
```bash
curl -X POST https://[project].supabase.co/functions/v1/[function-name] \
  -H "Authorization: Bearer [anon-key]" \
  -H "Content-Type: application/json" \
  -d '{
    // 请求参数
  }'
```

## 输入参数 (JSON Body)

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `param1` | string | 是 | 参数说明 |
| `param2` | number | 否 | 参数说明 |

## 输出格式

### 成功响应 (200)
```json
{
  "success": true,
  "data": {
    // 响应数据
  }
}
```

### 错误响应 (400/500)
```json
{
  "success": false,
  "error": "错误描述"
}
```

## 错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 成功 |
| 400 | 输入参数错误 |
| 500 | 内部服务器错误 |

## 限制

- **执行时间**: ≤ 10秒
- **数据量**: < 1MB
- **计算复杂度**: O(n) 或更低

## 示例

### 请求示例
```typescript
const result = await supabase.functions.invoke('okr-create', {
  body: {
    title: 'Q1销售目标',
    objectiveId: '123',
    targetValue: 1000000
  }
});
```

### 响应示例
```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "title": "Q1销售目标",
    "status": "active"
  }
}
```
```

---

## 🎯 API端点设计清单

### Cursor必须提供的文档

对于每个API端点，Cursor必须提供：

1. ✅ **函数路径**: `supabase/functions/[name]/index.ts`
2. ✅ **TypeScript类型定义**: 请求和响应的接口
3. ✅ **输入输出契约**: 详细的参数说明
4. ✅ **算法实现**: TypeScript代码（如果需要）
5. ✅ **错误处理**: 错误码和错误消息
6. ✅ **性能限制**: 执行时间、数据量、复杂度限制
7. ✅ **前端调用示例**: TypeScript代码示例

### Lovable必须实现的内容

1. ✅ **Edge Function代码**: 基于Cursor提供的模板实现
2. ✅ **错误处理**: 统一的错误响应格式
3. ✅ **测试**: 单元测试和集成测试
4. ✅ **部署**: 使用Supabase CLI部署

---

## 📚 相关文档

- [Python到TypeScript迁移计划](../PYTHON_TO_TYPESCRIPT_MIGRATION_PLAN.md)
- [TypeScript算法实现指南](../algorithms/TYPESCRIPT_ALGORITHMS.md)
- [Edge Functions设计规范](../../COLLABORATIVE_DEVELOPMENT_FRAMEWORK.md)

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23

