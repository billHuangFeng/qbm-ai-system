# Cursor与Lovable协同开发框架

## 🎯 协同开发目标

建立Cursor与Lovable的协同开发环境，实现高效分工合作：

- **Lovable负责**: 前端开发、数据库设计、UI/UX实现、Supabase Edge Functions（轻量级逻辑）
- **Cursor负责**: 需求梳理、Python后端（复杂算法）、业务分析、系统架构设计

## 📋 分工职责

### Lovable职责范围
- ✅ **前端开发**: React 19 + Vite + TypeScript + Tailwind CSS + shadcn/ui
- ✅ **UI/UX实现**: 用户界面、交互设计、响应式布局
- ✅ **前端组件**: 图表组件、表单组件、导航组件
- ✅ **前端路由**: 页面路由、状态管理
- ✅ **后端开发**: **Supabase Edge Functions (Deno Runtime)** - 轻量级业务逻辑
  - ✅ **技术栈**: Deno Runtime + TypeScript + Supabase SDK
  - ✅ **适用范围**: 简单CRUD、简单查询、O(n)算法、数据验证
  - ✅ **限制**: 执行时间≤10秒，计算复杂度O(n)或更低
  - ⚠️ **复杂算法**: 通过API调用Cursor的FastAPI后端
- ✅ **前端测试**: 组件测试、集成测试
- ✅ **后端测试**: Edge Function单元测试
- ✅ **数据库设计**: Supabase PostgreSQL + Row Level Security + Real-time
- ✅ **Supabase集成**: 数据库配置、实时订阅、认证、Edge Functions部署
- ✅ **数据库迁移**: 使用Supabase CLI（非Alembic）

### Cursor职责范围
- 🎯 **需求梳理**: 业务需求分析、功能规格定义
- 🎯 **系统架构**: 整体架构设计、模块划分
- 🎯 **业务分析**: 商业模式分析、算法设计
- 🎯 **API设计**: **FastAPI后端API设计** + Edge Functions API设计
  - FastAPI端点设计（复杂算法）
  - Edge Function代码模板（简单逻辑）
  - TypeScript和Python类型定义
  - 输入输出契约
- 🎯 **算法实现**: **Python复杂算法实现**
  - 机器学习算法（XGBoost, ARIMA, MLP等）
  - 复杂数据处理（Shapley归因等）
  - 文档处理和OCR
  - FastAPI服务维护
- 🎯 **技术指导**: 提供算法实现指导和技术支持
- 🎯 **文档编写**: 技术文档、**Edge Functions API文档**、算法文档（TypeScript）
- 🎯 **质量保证**: 代码审查、架构审查、性能优化建议

## 🔄 协同工作流

### 1. 需求梳理阶段 (Cursor主导)
```
Cursor工作:
├── 业务需求分析
├── 功能规格定义
├── API接口设计
├── 数据模型设计
└── 技术架构规划

输出文档:
├── 需求规格说明书
├── API接口文档
├── 数据库设计文档
└── 系统架构文档
```

### 2. 开发实现阶段 (Lovable主导)
```
Lovable工作:
├── 前端界面实现 (React + Vite)
├── 后端API实现 (Supabase Edge Functions - 全部后端逻辑)
├── 数据库表创建 (Supabase PostgreSQL)
├── 数据库迁移 (Supabase CLI)
├── UI组件开发
├── 业务逻辑开发 (全部在Edge Functions实现)
└── 前后端功能集成

Cursor协助:
├── 提供TypeScript算法实现代码
├── 提供Edge Functions代码模板
├── 技术架构审查
├── 代码质量审查
└── 性能优化建议（确保符合Edge Functions限制）
```

### 3. 集成测试阶段 (共同协作)
```
共同工作:
├── 前后端集成测试
├── 功能验证
├── 性能测试
└── 问题修复
```

## 📁 项目结构分工

### Lovable负责的目录
```
src/                          # React前端源码 (Vite)
├── components/               # React组件
├── pages/                    # 页面组件
│   └── [页面组件]
├── hooks/                    # 自定义Hooks
├── lib/                      # 工具库
└── types/                    # TypeScript类型定义

supabase/
├── functions/                # Supabase Edge Functions
│   ├── value-chain/         # 价值链分析API (轻量级)
│   ├── attribution/         # 归因分析API (简单查询)
│   ├── optimization/        # 优化建议API (CRUD)
│   └── decision/            # 决策管理API (状态管理)
└── migrations/              # 数据库迁移文件

public/                       # 静态资源
├── favicon.ico
├── placeholder.svg
└── robots.txt

# Lovable配置文件
package.json                 # 项目依赖配置
vite.config.ts               # Vite构建配置
tailwind.config.ts           # Tailwind CSS配置
tsconfig.json                # TypeScript配置
```

### Cursor负责的目录
```
docs/                       # 文档
├── requirements/           # 需求文档
├── api/                   # API文档
├── architecture/          # 架构文档
├── business/              # 业务文档
└── algorithms/            # 算法文档

algorithms/                 # 算法实现指导
├── shapley/               # Shapley归因算法
├── optimization/          # 优化算法
├── prediction/            # 预测算法
└── decision/              # 决策算法

research/                   # 研究资料
├── papers/                # 相关论文
├── benchmarks/            # 性能基准
└── experiments/           # 实验数据

scripts/                    # 工具脚本
├── analysis/              # 分析脚本
├── testing/               # 测试脚本
└── deployment/            # 部署脚本

# 部署配置
docker-compose.yml          # Docker编排
.github/workflows/          # CI/CD配置
```

## 🎯 Cursor需求梳理工作重点

### 1. 商业模式动态优化需求分析
- **价值链分析需求**: 如何量化价值链各环节效率
- **归因分析需求**: 如何计算各渠道/活动的贡献度
- **决策管理需求**: 如何实现层级决策管理
- **效果评估需求**: 如何量化决策效果

### 2. 技术架构需求设计
- **API接口设计**: **Supabase Edge Functions API设计**（非FastAPI）
  - Edge Function路径和HTTP方法
  - TypeScript类型定义
  - 输入输出契约
  - 错误处理规范
- **数据模型设计**: Supabase PostgreSQL表结构、关系设计、RLS策略
- **业务逻辑设计**: **TypeScript算法实现**（可直接用于Edge Functions）
- **集成需求设计**: 前后端集成（Edge Functions调用方式）、第三方集成

### 3. 功能模块需求定义
- **模块1: 全链条价值传递**
  - 价值链分析引擎需求
  - 归因分析算法需求
  - 优化建议生成需求

- **模块2: 动态管理脉络**
  - 数据采集需求
  - 指标计算需求
  - 分析报告需求

- **模块3: 利益协同与风险管控**
  - 价值贡献计算需求
  - 利益分配算法需求
  - 风险监控需求

- **模块4: 现金流健康管理**
  - 现金流分析需求
  - NPV计算需求
  - 健康评估需求

- **模块5: 关键量化方法应用**
  - TOC瓶颈定位需求
  - 边际分析需求
  - 价值增量计算需求

- **模块6: 决策管理支撑系统**
  - 层级决策管理需求
  - 决策追溯需求
  - 定期报告需求

## 📝 需求梳理输出模板

### 功能需求文档模板
```markdown
# [功能名称] 需求规格说明书

## 1. 功能概述
- 功能描述
- 业务价值
- 用户角色

## 2. 功能需求
- 功能列表
- 输入输出
- 业务规则

## 3. 技术需求
- API接口
- 数据模型
- 算法逻辑

## 4. 验收标准
- 功能验收
- 性能验收
- 质量验收
```

### Supabase Edge Functions API文档模板
```markdown
# [模块名称] Edge Functions API文档

## 函数路径
`supabase/functions/[function-name]/index.ts`

## 调用方式
```typescript
// 前端调用
const { data, error } = await supabase.functions.invoke('[function-name]', {
  body: { param1, param2 }
});
```

## 输入参数 (JSON Body)
- `param1`: string - 参数说明
- `param2`: number - 参数说明

## 输出格式 (JSON Response)
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

## 错误处理
- HTTP 400: 输入参数错误
- HTTP 500: 内部服务器错误

## Edge Function代码模板
参见下面的Edge Function示例模板
```

## 🔧 开发环境配置

### Cursor开发环境
```bash
# 后端开发环境
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 文档生成
cd docs
mkdocs serve
```

### Lovable开发环境
```bash
# 前端开发环境
npm install
npm run dev

# Supabase本地开发环境
supabase start
supabase functions serve

# Edge Functions部署
supabase functions deploy [function-name]

# 数据库迁移
supabase migration new [migration-name]
supabase db push
```

## 📊 协同开发检查清单

### Cursor工作检查清单
- [ ] 需求规格说明书完成
- [ ] API接口文档完成
- [ ] 数据模型设计完成
- [ ] 业务逻辑实现完成
- [ ] 后端测试完成
- [ ] 技术文档更新完成

### Lovable工作检查清单
- [ ] 前端界面实现完成
- [ ] 数据库表创建完成
- [ ] UI组件开发完成
- [ ] 前端功能集成完成
- [ ] 前端测试完成
- [ ] 用户界面优化完成

## 🚀 下一步行动

### 立即开始的工作
1. **Cursor**: 开始详细的需求梳理工作
2. **Lovable**: 等待Cursor的需求输出，准备前端开发
3. **共同**: 建立沟通机制，确保信息同步

### 沟通机制
- **需求变更**: 通过GitHub Issues进行沟通
- **技术讨论**: 通过GitHub Discussions进行讨论
- **进度同步**: 通过GitHub Projects进行跟踪

---

## 📘 Supabase Edge Functions API设计范式

### ⚠️ 重要技术栈约束

**Lovable只能使用Supabase Edge Functions，不能使用FastAPI Python后端。**

所有Cursor提供的API设计必须：
- ✅ 使用TypeScript编写
- ✅ 符合Deno Runtime规范
- ✅ 仅使用Supabase SDK和Deno标准库
- ✅ 执行时间≤10秒
- ✅ 计算复杂度O(n)或更低

---

## 🔧 Edge Function示例模板

### 模板1: 基础CRUD操作

```typescript
// supabase/functions/basic-crud/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// 类型定义
interface RequestBody {
  action: 'create' | 'read' | 'update' | 'delete';
  table: string;
  data?: Record<string, any>;
  id?: string;
  filters?: Record<string, any>;
}

serve(async (req) => {
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

    // 解析请求体
    const body: RequestBody = await req.json();

    // 验证输入参数
    if (!body.action || !body.table) {
      return new Response(
        JSON.stringify({ success: false, error: 'Missing required fields: action, table' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    let result;

    // 执行CRUD操作
    switch (body.action) {
      case 'create':
        if (!body.data) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing data for create operation' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }
        const { data: createData, error: createError } = await supabaseClient
          .from(body.table)
          .insert(body.data)
          .select();
        
        if (createError) throw createError;
        result = createData;
        break;

      case 'read':
        let query = supabaseClient.from(body.table).select('*');
        
        if (body.id) {
          query = query.eq('id', body.id);
        } else if (body.filters) {
          Object.entries(body.filters).forEach(([key, value]) => {
            query = query.eq(key, value);
          });
        }
        
        const { data: readData, error: readError } = await query;
        if (readError) throw readError;
        result = readData;
        break;

      case 'update':
        if (!body.id || !body.data) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing id or data for update operation' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }
        const { data: updateData, error: updateError } = await supabaseClient
          .from(body.table)
          .update(body.data)
          .eq('id', body.id)
          .select();
        
        if (updateError) throw updateError;
        result = updateData;
        break;

      case 'delete':
        if (!body.id) {
          return new Response(
            JSON.stringify({ success: false, error: 'Missing id for delete operation' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }
        const { error: deleteError } = await supabaseClient
          .from(body.table)
          .delete()
          .eq('id', body.id);
        
        if (deleteError) throw deleteError;
        result = { message: 'Deleted successfully' };
        break;

      default:
        return new Response(
          JSON.stringify({ success: false, error: 'Invalid action' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
    }

    // 返回成功响应
    return new Response(
      JSON.stringify({ success: true, data: result }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );

  } catch (error) {
    // 错误处理
    console.error('Error:', error);
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message || 'Internal server error' 
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
});
```

### 模板2: 简单算法计算（O(n)复杂度）

```typescript
// supabase/functions/simple-calculation/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

interface RequestBody {
  values: number[];
  operation: 'sum' | 'average' | 'max' | 'min';
}

serve(async (req) => {
  try {
    const body: RequestBody = await req.json();

    // 验证输入
    if (!body.values || !Array.isArray(body.values) || body.values.length === 0) {
      return new Response(
        JSON.stringify({ success: false, error: 'Invalid values array' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    let result: number;

    // 执行计算（O(n)复杂度）
    switch (body.operation) {
      case 'sum':
        result = body.values.reduce((acc, val) => acc + val, 0);
        break;

      case 'average':
        result = body.values.reduce((acc, val) => acc + val, 0) / body.values.length;
        break;

      case 'max':
        result = Math.max(...body.values);
        break;

      case 'min':
        result = Math.min(...body.values);
        break;

      default:
        return new Response(
          JSON.stringify({ success: false, error: 'Invalid operation' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
    }

    return new Response(
      JSON.stringify({ success: true, result }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
});
```

### 模板3: 数据库查询 + 简单处理

```typescript
// supabase/functions/data-query/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

interface RequestBody {
  table: string;
  filters?: Record<string, any>;
  limit?: number;
  offset?: number;
}

serve(async (req) => {
  try {
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

    const body: RequestBody = await req.json();

    // 构建查询
    let query = supabaseClient.from(body.table).select('*');

    // 应用过滤器
    if (body.filters) {
      Object.entries(body.filters).forEach(([key, value]) => {
        query = query.eq(key, value);
      });
    }

    // 应用分页
    if (body.limit) {
      query = query.limit(body.limit);
    }
    if (body.offset) {
      query = query.range(body.offset, body.offset + (body.limit || 10) - 1);
    }

    // 执行查询
    const { data, error } = await query;

    if (error) throw error;

    // 简单数据处理（O(n)复杂度）
    const processedData = data.map((item: any) => ({
      ...item,
      processedAt: new Date().toISOString()
    }));

    return new Response(
      JSON.stringify({ 
        success: true, 
        data: processedData,
        count: processedData.length
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
});
```

### 模板4: 前端调用示例

```typescript
// 前端调用Edge Function

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

// 调用CRUD操作
async function createRecord(table: string, data: Record<string, any>) {
  const { data: result, error } = await supabase.functions.invoke('basic-crud', {
    body: {
      action: 'create',
      table,
      data
    }
  });

  if (error) {
    console.error('Error:', error);
    return null;
  }

  return result.data;
}

// 调用算法计算
async function calculateSum(values: number[]) {
  const { data: result, error } = await supabase.functions.invoke('simple-calculation', {
    body: {
      values,
      operation: 'sum'
    }
  });

  if (error) {
    console.error('Error:', error);
    return null;
  }

  return result.result;
}
```

---

## 📋 Edge Functions设计规范

### 必须遵守的规范

1. **执行时间限制**: ≤10秒
   - 如果计算可能超过10秒，必须简化算法或分批处理

2. **计算复杂度**: O(n)或更低
   - 不允许O(n²)、O(n!)等复杂算法
   - 如果需要复杂算法，必须提供简化版本

3. **依赖库限制**:
   - ✅ 允许: Supabase SDK (`@supabase/supabase-js`)
   - ✅ 允许: Deno标准库 (`https://deno.land/std@...`)
   - ❌ 禁止: npm包（除非有Deno兼容版本）
   - ❌ 禁止: Python库、系统级库

4. **数据量限制**: 单次处理 < 1MB
   - 大文件处理必须分批或使用Supabase Storage

5. **错误处理**: 统一的错误响应格式
   ```typescript
   {
     success: false,
     error: "错误描述"
   }
   ```

6. **成功响应**: 统一的成功响应格式
   ```typescript
   {
     success: true,
     data: { ... }
   }
   ```

---

**这个协同开发框架确保Cursor专注于需求梳理和TypeScript算法设计，Lovable专注于Edge Functions实现和前端开发，实现高效分工合作！** 🎉

