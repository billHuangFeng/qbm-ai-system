# Lovable + Cursor 协同开发实施计划

> **创建时间**: 2025-10-20  
> **协同模式**: Lovable 全栈开发 + Cursor 需求分析和算法设计  
> **目标**: 在6-8周内完成商业模式动态优化与决策管理综合系统的MVP版本

---

## 🎯 核心架构决策

### **技术栈统一**
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **后端**: Supabase (PostgreSQL + Edge Functions + Authentication + Storage)
- **部署**: Lovable Cloud (前端) + Supabase Cloud (后端)
- **开发工具**: Lovable (前端开发) + Cursor (需求分析)

### **分工明确**
| 角色 | 职责 | 工具 |
|-----|------|------|
| **Lovable** | 前端UI开发、数据库设计、Edge Functions实现、简单业务逻辑、部署运维 | Lovable编辑器 |
| **Cursor** | 需求分析、复杂算法设计、API文档编写、代码审查、测试用例设计 | Cursor + Git |

---

## 📋 迁移步骤（5个阶段）

### **阶段1：清理不兼容代码 + 创建基础文件** 🚨 [当前阶段]

#### 问题描述
- ✅ 已修复: 创建 `src/lib/utils.ts` (shadcn/ui 依赖)
- ✅ 已修复: 前端组件错误处理优化 (`RawDataUploader.tsx`, `CycleMonitor.tsx`, `EvaluationPanel.tsx`)
- ✅ 已修复: API 路由类型安全 (`shapley-attribution.ts`, `decision-cycle/execute.ts`)
- ⚠️ 待删除: `src/pages/api/` 目录 (Next.js API Routes 与 Vite 不兼容)
- ⚠️ 待删除: `next.config.js` (不需要)

#### 操作清单
- [x] 创建 `src/lib/utils.ts`
- [x] 修复前端组件错误处理
- [x] 修复 API 路由类型安全
- [ ] 删除 `src/pages/api/` 目录
- [ ] 删除 `next.config.js`
- [ ] 清理 `package.json` 中的 Next.js 依赖

#### 验收标准
- ✅ 所有 TypeScript 编译错误消失
- ⏳ 项目可以正常构建 (`npm run build`)
- ⏳ 开发服务器正常运行 (`npm run dev`)

---

### **阶段2：集成 Supabase + 数据库设计** 📊 [下一阶段]

#### Cursor 的工作
1. **输出数据库设计文档** (基于 `BUSINESS_DATA_PIPELINE.md`)
   - 27张核心表 + 4个视图的完整设计
   - 表关系图 (ER Diagram)
   - 字段说明和数据类型
   - 索引策略和性能优化建议
   - RLS (Row Level Security) 策略设计

2. **设计数据库表分类**
   - **维度表 (9张)**: `dim_vpt`, `dim_pft`, `dim_customer`, `dim_channel`, `dim_sku`, `dim_employee`, `dim_supplier`, `dim_campaign`, `dim_time`
   - **事实表 (5张)**: `fact_order`, `fact_voice`, `fact_expense`, `fact_supplier`, `fact_production`
   - **桥接表 (5张)**: `bridge_media_vpt`, `bridge_attribution`, `bridge_conversion_vpt`, `bridge_sku_pft`, `bridge_employee_kpi`
   - **决策管理表 (4张)**: `decision_hierarchy`, `decision_decomposition`, `decision_kpi`, `decision_execution_link`
   - **分析结果表 (4张)**: `analysis_shapley`, `analysis_toc`, `analysis_margin`, `analysis_value_increment`

#### Lovable 的工作
1. **启用 Lovable Cloud** (Supabase 集成)
2. **创建数据库表** (在 Supabase SQL Editor 中执行 DDL)
3. **配置 RLS 策略** (基于 Cursor 的设计)
4. **创建必要的索引和视图**
5. **设置 Supabase 客户端** (`src/lib/supabase.ts`)

#### 数据库表设计示例

##### 维度表：价值主张 (Value Proposition Table)
```sql
CREATE TABLE dim_vpt (
  vpt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vpt_name TEXT NOT NULL,
  vpt_category TEXT CHECK (vpt_category IN ('功能型', '情感型', '社会型')),
  vpt_description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_dim_vpt_category ON dim_vpt(vpt_category);

-- RLS 策略
ALTER TABLE dim_vpt ENABLE ROW LEVEL SECURITY;
CREATE POLICY "允许所有认证用户读取" ON dim_vpt FOR SELECT TO authenticated USING (true);
```

##### 事实表：订单
```sql
CREATE TABLE fact_order (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES dim_customer(customer_id) ON DELETE CASCADE,
  sku_id UUID REFERENCES dim_sku(sku_id) ON DELETE SET NULL,
  channel_id UUID REFERENCES dim_channel(channel_id) ON DELETE SET NULL,
  order_amount DECIMAL(15,2) NOT NULL CHECK (order_amount >= 0),
  order_cost DECIMAL(15,2),
  order_date TIMESTAMPTZ NOT NULL,
  order_status TEXT DEFAULT 'pending' CHECK (order_status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_fact_order_customer ON fact_order(customer_id);
CREATE INDEX idx_fact_order_date ON fact_order(order_date DESC);
CREATE INDEX idx_fact_order_status ON fact_order(order_status);
```

##### 桥接表：归因分析
```sql
CREATE TABLE bridge_attribution (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID REFERENCES fact_order(order_id) ON DELETE CASCADE,
  touchpoint_type TEXT NOT NULL CHECK (touchpoint_type IN ('媒体', '渠道', '活动', '员工')),
  touchpoint_id UUID NOT NULL,
  attribution_value DECIMAL(10,6) CHECK (attribution_value BETWEEN 0 AND 1),
  attribution_method TEXT DEFAULT 'shapley',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_bridge_attribution_order ON bridge_attribution(order_id);
CREATE INDEX idx_bridge_attribution_type ON bridge_attribution(touchpoint_type, touchpoint_id);
```

#### 验收标准
- [ ] Supabase 项目创建完成
- [ ] 所有27张表创建成功
- [ ] RLS 策略配置完成
- [ ] 索引创建完成
- [ ] Supabase 客户端集成到前端

---

### **阶段3：实现 Supabase Edge Functions** 🔧

#### Edge Functions 列表

##### 3.1 简单业务逻辑 (Lovable 独立完成)

**函数1: 数据导入**
```typescript
// supabase/functions/data-import/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { tableName, data } = await req.json();
  
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // 批量插入数据
  const { data: inserted, error } = await supabase
    .from(tableName)
    .insert(data);

  if (error) {
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify({ success: true, insertedCount: data.length }), {
    headers: { 'Content-Type': 'application/json' }
  });
});
```

**函数2: 管理者评价**
```typescript
// supabase/functions/manager-evaluation/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { decisionId, evaluationContent, adjustments } = await req.json();
  
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // 保存评价
  const { error } = await supabase.from('manager_evaluation').insert({
    decision_id: decisionId,
    evaluation_content: evaluationContent,
    adjustments: adjustments,
    evaluated_at: new Date().toISOString()
  });

  if (error) {
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 更新决策状态
  await supabase.from('decision_hierarchy')
    .update({ decision_status: 'evaluated' })
    .eq('decision_id', decisionId);

  return new Response(JSON.stringify({ success: true }), {
    headers: { 'Content-Type': 'application/json' }
  });
});
```

**函数3: 决策循环触发**
```typescript
// supabase/functions/decision-cycle/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { triggerType } = await req.json(); // 'scheduled' | 'threshold' | 'manual'
  
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // 创建执行记录
  const { data: execution } = await supabase.from('decision_cycle_execution').insert({
    trigger_type: triggerType,
    execution_start: new Date().toISOString(),
    execution_status: 'running'
  }).select().single();

  try {
    // 1. 数据提取
    await extractData(supabase);
    
    // 2. 数据转换
    await transformData(supabase);
    
    // 3. 调用分析函数
    await analyzeData(supabase);
    
    // 4. 生成决策建议
    await generateDecisions(supabase);

    // 更新执行状态
    await supabase.from('decision_cycle_execution')
      .update({ 
        execution_end: new Date().toISOString(),
        execution_status: 'completed' 
      })
      .eq('execution_id', execution.execution_id);

    return new Response(JSON.stringify({ success: true, executionId: execution.execution_id }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    await supabase.from('decision_cycle_execution')
      .update({ 
        execution_end: new Date().toISOString(),
        execution_status: 'failed',
        execution_log: { error: String(error) }
      })
      .eq('execution_id', execution.execution_id);

    throw error;
  }
});

// 辅助函数（简化版本）
async function extractData(supabase: any) {
  // 从原始数据表提取数据
}
async function transformData(supabase: any) {
  // ETL 转换逻辑
}
async function analyzeData(supabase: any) {
  // 调用分析算法
}
async function generateDecisions(supabase: any) {
  // 生成决策建议
}
```

##### 3.2 复杂算法 (Cursor 设计 → Lovable 实现)

#### Cursor 提供的算法文档

**算法1: Shapley 归因**

> **Cursor 输出**: `docs/algorithms/SHAPLEY_ATTRIBUTION.md`

```markdown
# Shapley 归因算法设计

## 算法目标
计算每个营销触点对最终转化的贡献度，解决多触点归因问题。

## 输入
- `orderId`: 订单ID
- `touchpoints[]`: 订单关联的所有触点
  - `touchpoint_id`: 触点ID
  - `touchpoint_type`: 触点类型 (媒体/渠道/活动)
  - `timestamp`: 触点发生时间
  - `cost`: 触点成本

## 输出
- `shapleyValues`: Map<touchpoint_id, contribution_value>
  - `contribution_value`: 0-1之间的贡献度，所有触点总和为1

## 算法伪代码

```
function calculateShapley(touchpoints):
  n = touchpoints.length
  shapleyValues = {}
  
  for each touchpoint i in touchpoints:
    marginalContribution = 0
    permutationCount = 0
    
    # 枚举所有可能的触点排列
    for each permutation P of touchpoints:
      # 找到当前触点在排列中的位置
      position = P.indexOf(i)
      
      # 计算包含该触点前的子集
      coalitionBefore = P.slice(0, position)
      
      # 计算包含该触点后的子集
      coalitionAfter = P.slice(0, position + 1)
      
      # 计算边际贡献
      valueBefore = evaluateCoalition(coalitionBefore)
      valueAfter = evaluateCoalition(coalitionAfter)
      marginalContribution += (valueAfter - valueBefore)
      permutationCount += 1
    
    # 计算平均边际贡献
    shapleyValues[i.id] = marginalContribution / permutationCount
  
  # 归一化（确保总和为1）
  totalValue = sum(shapleyValues.values())
  for key in shapleyValues:
    shapleyValues[key] = shapleyValues[key] / totalValue
  
  return shapleyValues

function evaluateCoalition(coalition):
  # 评估触点联盟的转化概率
  # 简化模型：每个触点独立贡献10%，有递减效应
  baseRate = 0.05
  diminishingFactor = 0.9
  
  probability = 0
  for i, touchpoint in enumerate(coalition):
    contribution = baseRate * (diminishingFactor ** i)
    probability += contribution
  
  return min(probability, 1.0)  # 最大概率为1
```

## 性能优化建议

### 方案1: 蒙特卡洛采样（推荐用于生产环境）
当触点数量 > 10 时，完全枚举所有排列的计算量过大（10! = 3,628,800）。
建议使用蒙特卡洛采样，随机生成1000-10000个排列来估算Shapley值。

```
function calculateShapleyMonteCarlo(touchpoints, sampleCount = 5000):
  n = touchpoints.length
  marginalContributions = {} # 每个触点的边际贡献累加
  
  for sample in 1..sampleCount:
    # 随机打乱触点顺序
    permutation = shuffle(touchpoints)
    
    for i, touchpoint in enumerate(permutation):
      coalitionBefore = permutation[0..i-1]
      coalitionAfter = permutation[0..i]
      
      valueBefore = evaluateCoalition(coalitionBefore)
      valueAfter = evaluateCoalition(coalitionAfter)
      
      marginalContributions[touchpoint.id] += (valueAfter - valueBefore)
  
  # 计算平均值并归一化
  shapleyValues = {}
  for id, contribution in marginalContributions:
    shapleyValues[id] = contribution / sampleCount
  
  # 归一化
  totalValue = sum(shapleyValues.values())
  for key in shapleyValues:
    shapleyValues[key] = shapleyValues[key] / totalValue
  
  return shapleyValues
```

### 方案2: 缓存中间结果
使用动态规划缓存 `evaluateCoalition` 的结果，避免重复计算。

## 测试用例

### 测试用例1: 简单场景
**输入**:
```json
{
  "orderId": "order-001",
  "touchpoints": [
    {"id": "media-a", "type": "媒体", "timestamp": "2024-01-01T10:00:00Z", "cost": 100},
    {"id": "channel-b", "type": "渠道", "timestamp": "2024-01-02T14:00:00Z", "cost": 50},
    {"id": "campaign-c", "type": "活动", "timestamp": "2024-01-03T16:00:00Z", "cost": 200}
  ]
}
```

**预期输出**:
```json
{
  "media-a": 0.42,
  "channel-b": 0.28,
  "campaign-c": 0.30
}
```

### 测试用例2: 边界情况
- **单个触点**: Shapley值应为1.0
- **所有触点成本相同**: Shapley值应接近均等分配
- **触点数量 > 10**: 应自动切换到蒙特卡洛采样

## 算法复杂度分析
- **时间复杂度**: O(n! * n) (完全枚举) 或 O(k * n) (蒙特卡洛，k为采样次数)
- **空间复杂度**: O(n)
```

#### Lovable 的实现

**文件**: `supabase/functions/shapley-attribution/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { orderId } = await req.json();
  
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // 1. 获取订单的所有触点
  const { data: touchpoints, error } = await supabase
    .from('customer_journey')
    .select('*')
    .eq('order_id', orderId)
    .order('timestamp', { ascending: true });

  if (error || !touchpoints || touchpoints.length === 0) {
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'No touchpoints found for this order' 
    }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 2. 计算 Shapley 值
  const shapleyValues = touchpoints.length <= 10
    ? calculateShapleyExact(touchpoints)
    : calculateShapleyMonteCarlo(touchpoints, 5000);

  // 3. 保存结果到数据库
  const insertData = touchpoints.map(tp => ({
    order_id: orderId,
    touchpoint_type: tp.type,
    touchpoint_id: tp.id,
    attribution_value: shapleyValues[tp.id],
    attribution_method: touchpoints.length <= 10 ? 'exact' : 'monte_carlo'
  }));

  await supabase.from('bridge_attribution').insert(insertData);

  // 4. 保存到分析结果表
  await supabase.from('analysis_shapley').insert({
    order_id: orderId,
    shapley_values: shapleyValues,
    touchpoint_count: touchpoints.length,
    calculated_at: new Date().toISOString()
  });

  return new Response(JSON.stringify({ 
    success: true, 
    shapleyValues,
    method: touchpoints.length <= 10 ? 'exact' : 'monte_carlo'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
});

// 精确计算 Shapley 值（适用于触点数 <= 10）
function calculateShapleyExact(touchpoints: any[]): Record<string, number> {
  const n = touchpoints.length;
  const marginalContributions: Record<string, number[]> = {};
  
  // 初始化
  touchpoints.forEach(tp => {
    marginalContributions[tp.id] = [];
  });

  // 生成所有排列
  const permutations = generatePermutations(touchpoints);

  // 对每个排列计算边际贡献
  for (const perm of permutations) {
    for (let i = 0; i < n; i++) {
      const touchpoint = perm[i];
      const coalitionBefore = perm.slice(0, i);
      const coalitionAfter = perm.slice(0, i + 1);
      
      const valueBefore = evaluateCoalition(coalitionBefore);
      const valueAfter = evaluateCoalition(coalitionAfter);
      
      marginalContributions[touchpoint.id].push(valueAfter - valueBefore);
    }
  }

  // 计算平均值
  const shapleyValues: Record<string, number> = {};
  for (const id in marginalContributions) {
    const contributions = marginalContributions[id];
    shapleyValues[id] = contributions.reduce((a, b) => a + b, 0) / contributions.length;
  }

  // 归一化
  return normalizeShapleyValues(shapleyValues);
}

// 蒙特卡洛采样计算 Shapley 值（适用于触点数 > 10）
function calculateShapleyMonteCarlo(touchpoints: any[], sampleCount: number): Record<string, number> {
  const n = touchpoints.length;
  const marginalContributions: Record<string, number> = {};
  
  // 初始化
  touchpoints.forEach(tp => {
    marginalContributions[tp.id] = 0;
  });

  // 蒙特卡洛采样
  for (let sample = 0; sample < sampleCount; sample++) {
    // 随机打乱触点顺序
    const permutation = shuffle([...touchpoints]);
    
    for (let i = 0; i < n; i++) {
      const touchpoint = permutation[i];
      const coalitionBefore = permutation.slice(0, i);
      const coalitionAfter = permutation.slice(0, i + 1);
      
      const valueBefore = evaluateCoalition(coalitionBefore);
      const valueAfter = evaluateCoalition(coalitionAfter);
      
      marginalContributions[touchpoint.id] += (valueAfter - valueBefore);
    }
  }

  // 计算平均值
  const shapleyValues: Record<string, number> = {};
  for (const id in marginalContributions) {
    shapleyValues[id] = marginalContributions[id] / sampleCount;
  }

  // 归一化
  return normalizeShapleyValues(shapleyValues);
}

// 评估触点联盟的转化概率
function evaluateCoalition(coalition: any[]): number {
  if (coalition.length === 0) return 0;
  
  const baseRate = 0.05;
  const diminishingFactor = 0.9;
  
  let probability = 0;
  for (let i = 0; i < coalition.length; i++) {
    const contribution = baseRate * Math.pow(diminishingFactor, i);
    probability += contribution;
  }
  
  return Math.min(probability, 1.0);
}

// 归一化 Shapley 值（确保总和为1）
function normalizeShapleyValues(values: Record<string, number>): Record<string, number> {
  const totalValue = Object.values(values).reduce((a, b) => a + b, 0);
  
  if (totalValue === 0) return values;
  
  const normalized: Record<string, number> = {};
  for (const key in values) {
    normalized[key] = values[key] / totalValue;
  }
  
  return normalized;
}

// 生成所有排列（用于精确计算）
function generatePermutations<T>(arr: T[]): T[][] {
  if (arr.length <= 1) return [arr];
  
  const result: T[][] = [];
  for (let i = 0; i < arr.length; i++) {
    const rest = [...arr.slice(0, i), ...arr.slice(i + 1)];
    const restPerms = generatePermutations(rest);
    
    for (const perm of restPerms) {
      result.push([arr[i], ...perm]);
    }
  }
  
  return result;
}

// Fisher-Yates 洗牌算法（用于蒙特卡洛采样）
function shuffle<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
```

#### 验收标准
- [ ] 至少实现5个核心 Edge Functions
- [ ] Shapley 归因算法通过所有测试用例
- [ ] Edge Functions 响应时间 < 3s
- [ ] 错误处理完善（异常日志记录）

---

### **阶段4：构建 React 前端界面** 🎨

#### 核心页面列表

##### 4.1 数据导入页面 (`src/pages/DataImport.tsx`)
**功能**:
- 上传 CSV/Excel 文件
- 预览数据（前10行）
- 映射字段到数据库表
- 批量导入数据

**UI 组件**:
- 文件上传组件 (`FileUploader`)
- 数据预览表格 (`DataPreviewTable`)
- 字段映射表单 (`FieldMapper`)
- 导入进度条 (`ImportProgress`)

##### 4.2 价值链分析页面 (`src/pages/ValueChainAnalysis.tsx`)
**功能**:
- 可视化价值链流程图
- 显示每个环节的效率指标
- Shapley 归因分析结果展示
- TOC 瓶颈识别和优化建议

**UI 组件**:
- 价值链流程图 (`ValueChainFlow`) - 已存在
- 价值网络图 (`ValueNetworkGraph`) - 已存在
- 归因分析卡片 (`AttributionCard`)
- 瓶颈分析面板 (`BottleneckPanel`)

##### 4.3 决策管理页面 (`src/pages/DecisionManagement.tsx`)
**功能**:
- 层级决策树状图（战略/战术/执行）
- 决策创建/审批/执行
- 决策效果追踪
- KPI 监控面板

**UI 组件**:
- 决策树组件 (`DecisionTree`)
- 决策表单 (`DecisionForm`)
- 决策审批流程 (`ApprovalFlow`)
- KPI 卡片 (`KPICard`)

##### 4.4 管理者评价页面 (`src/pages/ManagerEvaluation.tsx`)
**功能**:
- 查看系统初步分析结果
- 提交评价意见
- 调整指标权重
- 确认/驳回决策建议

**UI 组件**:
- 评价面板 (`EvaluationPanel`) - 已存在
- 权重调整滑块 (`WeightAdjuster`)
- 决策对比表 (`DecisionComparison`)

##### 4.5 数据看板页面 (`src/pages/Dashboard.tsx`)
**功能**:
- 关键指标卡片（营收、利润、转化率、满意度）
- 趋势图表（时间序列）
- 实时数据更新（Supabase Realtime）

**UI 组件**:
- 指标卡片 (`MetricCard`)
- 趋势图表 (`TrendChart` - 使用 recharts)
- 实时数据流 (`RealtimeDataStream`)

#### Lovable 的工作
1. **创建所有页面和组件**
2. **集成 Supabase 客户端** (`src/lib/supabase.ts`)
3. **实现实时数据订阅**
4. **优化响应式布局**（移动端适配）
5. **添加 Loading 状态和错误处理**

#### Cursor 的工作
1. **审查页面布局和交互逻辑**
2. **提供 UI/UX 设计建议**
3. **提供数据可视化方案**（图表类型、颜色方案）

#### 验收标准
- [ ] 所有5个核心页面完成
- [ ] 响应式布局适配（桌面端 + 移动端）
- [ ] 实时数据更新正常工作
- [ ] 页面加载时间 < 2s

---

### **阶段5：测试 + 优化 + 部署** 🚀

#### 测试清单

##### 功能测试
- [ ] 数据导入功能（CSV → Supabase）
- [ ] Shapley 归因计算正确性
- [ ] 决策循环自动触发
- [ ] 管理者评价提交和状态更新
- [ ] 实时数据更新（Supabase Realtime）

##### 性能测试
- [ ] 页面响应速度 < 2s
- [ ] Edge Functions 响应时间 < 3s
- [ ] 数据库查询优化（索引效果验证）
- [ ] 并发用户支持（100+ 用户）

##### 安全测试
- [ ] RLS 策略验证（数据访问权限）
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] CSRF 防护

#### Cursor 的测试工作
1. **编写集成测试脚本** (Python)
   - 验证 Shapley 算法正确性
   - 验证 TOC 瓶颈识别准确性
   - 验证决策循环完整性

2. **提供测试用例**
   ```python
   # tests/test_shapley.py
   def test_shapley_simple_case():
       touchpoints = [
           {"id": "a", "type": "媒体", "timestamp": "2024-01-01T10:00:00Z"},
           {"id": "b", "type": "渠道", "timestamp": "2024-01-02T14:00:00Z"},
           {"id": "c", "type": "活动", "timestamp": "2024-01-03T16:00:00Z"}
       ]
       
       result = call_edge_function('shapley-attribution', {
           'orderId': 'test-order-001',
           'touchpoints': touchpoints
       })
       
       assert result['success'] == True
       assert sum(result['shapleyValues'].values()) == pytest.approx(1.0, abs=0.01)
       assert all(0 <= v <= 1 for v in result['shapleyValues'].values())
   ```

#### Lovable 的优化工作
1. **数据库索引优化**
   - 为高频查询字段添加索引
   - 创建复合索引
   - 分析查询计划（EXPLAIN ANALYZE）

2. **前端性能优化**
   - 代码分割（React.lazy）
   - 图片懒加载
   - 缓存策略（React Query）

3. **部署优化**
   - 配置 CDN
   - 启用 Gzip 压缩
   - 配置缓存策略

#### 部署流程
1. **Lovable 部署前端** (一键部署到 Lovable Cloud)
2. **配置环境变量** (Supabase URL, Anon Key)
3. **部署 Edge Functions** (通过 Supabase CLI)
4. **配置自定义域名** (可选)

#### 验收标准
- [ ] 所有功能测试通过
- [ ] 性能测试达标
- [ ] 安全测试通过
- [ ] 生产环境部署成功

---

## 🔄 协同工作流程示例

### **功能实现流程：Shapley 归因**

#### 第1步：Cursor 提供需求文档
- 输出文件: `docs/algorithms/SHAPLEY_ATTRIBUTION.md`
- 内容: 算法目标、输入输出、伪代码、测试用例

#### 第2步：Lovable 实现 Edge Function
- 创建文件: `supabase/functions/shapley-attribution/index.ts`
- 内容: 基于 Cursor 伪代码的 TypeScript 实现

#### 第3步：Cursor 审查代码
- 检查算法实现是否符合需求
- 提供优化建议（如：蒙特卡洛采样）
- 验证测试用例是否通过

#### 第4步：Lovable 调优部署
- 根据 Cursor 建议优化代码
- 部署到 Supabase
- 在前端页面中调用该 Edge Function

#### 第5步：集成测试
- Cursor 运行集成测试脚本
- 验证算法正确性和性能
- 确认与前端的集成正常

---

## 📊 关键成功指标

### 技术指标
| 指标 | 目标值 | 当前状态 |
|-----|-------|---------|
| TypeScript 编译错误 | 0 | ✅ 0 |
| 数据库表创建 | 27张表 + 4个视图 | ⏳ 待完成 |
| Edge Functions 部署 | 至少5个核心函数 | ⏳ 待完成 |
| 页面响应速度 | < 2s | ⏳ 待测试 |
| Shapley 算法准确率 | > 90% | ⏳ 待验证 |

### 协同效率指标
| 指标 | 目标值 | 说明 |
|-----|-------|-----|
| Cursor 需求文档产出 | < 4小时/功能 | 包括算法设计、API文档 |
| Lovable 功能实现 | < 1天/功能 | 包括前端+后端+测试 |
| 代码审查周期 | < 1天 | Cursor 审查 Lovable 代码 |
| 每周功能交付 | 2-3个核心功能 | 持续迭代 |

---

## 📅 项目里程碑

### 第1周（当前周）
- [x] 清理不兼容代码
- [x] 创建 `src/lib/utils.ts`
- [x] 修复 TypeScript 编译错误
- [ ] 删除 `src/pages/api/` 和 `next.config.js`
- [ ] 启用 Lovable Cloud (Supabase)

### 第2周
- [ ] Cursor 完成数据库设计文档
- [ ] Lovable 创建所有数据库表
- [ ] 配置 RLS 策略
- [ ] 创建第一个 Edge Function (数据导入)

### 第3-4周
- [ ] Cursor 提供 Shapley 算法设计
- [ ] Lovable 实现 Shapley Edge Function
- [ ] 完成价值链分析页面
- [ ] 集成测试

### 第5-6周
- [ ] 完成决策管理页面
- [ ] 完成管理者评价页面
- [ ] 完成数据看板页面
- [ ] 性能优化

### 第7-8周
- [ ] 全面测试（功能+性能+安全）
- [ ] 部署到生产环境
- [ ] 用户验收测试
- [ ] 发布 MVP 版本

---

## 🎯 立即行动项

### 第一优先级（本周）
1. ✅ **Lovable**: 创建 `src/lib/utils.ts`
2. ✅ **Lovable**: 修复 TypeScript 编译错误
3. ⏳ **Lovable**: 删除 `src/pages/api/` 和 `next.config.js`
4. ⏳ **Lovable**: 启用 Lovable Cloud
5. ⏳ **Cursor**: 开始数据库设计文档编写

### 第二优先级（下周）
1. **Cursor**: 完成数据库设计文档（27张表）
2. **Lovable**: 在 Supabase 中创建所有表
3. **Lovable**: 实现第一个 Edge Function（数据导入）
4. **Cursor**: 提供 Shapley 算法伪代码

### 第三优先级（两周后）
1. **Lovable**: 完成价值链分析页面
2. **Cursor**: 审查算法实现
3. **共同**: 进行集成测试

---

## 📞 沟通机制

### 日常沟通
- **Cursor → Lovable**: 通过 GitHub Issues 提交需求文档
- **Lovable → Cursor**: 通过 GitHub Pull Requests 提交代码
- **代码审查**: Cursor 审查 Lovable 的 PR，提供反馈

### 文档同步
- **Cursor 输出目录**: `docs/algorithms/`, `docs/api/`, `docs/testing/`
- **Lovable 拉取**: 从 Git 仓库拉取最新文档
- **更新频率**: 每天同步一次

### 进度跟踪
- **工具**: GitHub Projects
- **看板**: To Do / In Progress / In Review / Done
- **每周同步**: 周五下午进行进度回顾

---

## 🔗 相关文档

- [协同开发框架](./COLLABORATIVE_DEVELOPMENT_FRAMEWORK.md)
- [需求梳理工作计划](./REQUIREMENTS_WORK_PLAN.md)
- [模块1需求规格](./MODULE1_VALUE_CHAIN_ANALYSIS.md)
- [数据管道设计](../BUSINESS_DATA_PIPELINE.md)
- [统一架构设计](../UNIFIED_ARCHITECTURE.md)

---

**最后更新**: 2025-10-20  
**协同模式**: Lovable 全栈开发 + Cursor 需求分析和算法设计  
**预计完成**: 2025-12-15 (8周后)
