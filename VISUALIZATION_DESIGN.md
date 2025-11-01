# BMOS 可视化界面设计方案

## 🎨 设计理念

基于用户提供的商业模式图和OGSM目标管理图，设计具象化的企业商业模式状态和优化机会展示界面。

## 📊 核心可视化组件

### 一、价值分配网络图（Value Network Graph）

**目标**：展示客户、员工、合作伙伴、企业之间的增量价值分配网络

**推荐图形**：力导向图（Force-Directed Graph）

**技术实现**：
- 库选择：D3.js 或 React Flow
- 文件位置：`src/components/Visualization/ValueNetworkGraph.tsx`

**设计要点**：
```typescript
// 节点设计
interface NetworkNode {
  id: string;
  type: 'customer' | 'employee' | 'partner' | 'enterprise';
  name: string;
  valueReceived: number;  // 接收的价值量
  valueGiven: number;     // 贡献的价值量
  netValue: number;       // 增量价值
}

// 连线设计
interface NetworkLink {
  source: string;
  target: string;
  value: number;          // 价值流动量
  type: string;           // 价值类型（金钱、服务、产品等）
}

// 可视化特性
- 节点大小：根据价值量动态调整
- 连线粗细：根据流动量动态调整
- 颜色编码：
  * 客户：蓝色
  * 员工：绿色
  * 合作伙伴：橙色
  * 企业：紫色
- 交互功能：
  * 点击节点：查看详细价值分配
  * 悬停连线：显示价值流动详情
  * 拖拽节点：重新布局
```

---

### 二、价值链路桑基图（Value Chain Sankey）

**目标**：展示从投入资源到商业成果的完整价值流动

**推荐图形**：桑基图（Sankey Diagram）

**技术实现**：
- 库选择：Recharts Sankey 或 Plotly
- 文件位置：`src/components/Visualization/ValueChainSankey.tsx`

**数据流设计**：
```
投入资源 → 生产 → 产品特性 → 产品价值 → 客户预期价值 → 销售 → 销售收入
                ↓           ↓           ↓           ↓          ↓          ↓
              成本 ←────────────────────────────────────────────────── 现金流
```

**设计要点**：
```typescript
interface SankeyData {
  nodes: Array<{
    name: string;
    category: 'input' | 'process' | 'output' | 'cost';
  }>;
  links: Array<{
    source: number;
    target: number;
    value: number;
    efficiency: number;  // 转化效率
  }>;
}

// 关键指标标注
- 生产效率：85%
- 价值特性系数：0.92
- 播传效率：78%
- 交付效率：88%
- 兴趣转化成交率：65%
- 服务转化成交率：72%
```

---

### 三、价值创造链路与瓶颈识别（Value Chain Flow）

**目标**：展示各环节关键指标，突出瓶颈（优化机会点）

**推荐图形**：增强型流程图 + 热力图

**技术实现**：
- 自定义React组件
- 文件位置：`src/components/Visualization/ValueChainFlow.tsx`

**设计要点**：
```typescript
interface ChainNode {
  id: string;
  name: string;
  metricName: string;
  metricValue: number;
  target: number;
  efficiency: number;
  isBottleneck: boolean;
  severity: 'critical' | 'warning' | 'normal';
  improvementPotential: number;
}

// 视觉设计
- 正常环节：绿色边框
- 警告环节：黄色边框
- 瓶颈环节：红色边框 + 脉动动画 + ⚠️ 图标
- 效率显示：大字号百分比
- 趋势指示：↑上升 ↓下降 → 持平
```

**布局示例**：
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   生产      │ →  │  产品特性   │ →  │  产品价值   │ →  │  客户预期   │
│   85%       │    │   92%       │    │   78% ⚠️    │    │   88%       │
│   生产效率  │    │价值特性系数 │    │  播传效率   │    │  交付效率   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     ↓                  ↓                  ↓                  ↓
  [生产资源]        [研发能力]         [播传资源]         [交付能力]
  [生产能力]        [研发资源]         [播传能力]         [交付资源]
```

---

### 四、层级决策树状图（Decision Tree View）

**目标**：展示企业决策层级关系（纵向对齐 + 横向拉通）

**推荐图形**：可折叠树状图 + OGSM卡片

**技术实现**：
- 库选择：React Organizational Chart 或自定义
- 文件位置：`src/components/Visualization/DecisionTreeView.tsx`

**设计要点**：

#### 4.1 纵向层级对齐

```typescript
interface DecisionNode {
  id: string;
  level: 'board' | 'executive' | 'department' | 'team';
  name: string;
  
  // OGSM 结构
  objective: string;           // 目标 O
  strategies: string[];        // 关键举措 S
  kpi: {
    name: string;
    target: number;
    actual: number;
  };
  
  // 执行状态
  status: 'completed' | 'in_progress' | 'paused' | 'not_started' | 'overdue';
  
  // 执行闭环
  executionLoop: {
    decision: boolean;         // 决策完成
    decomposition: boolean;    // 分解完成
    execution: boolean;        // 执行中
    facts: boolean;            // 业务事实收集
    metrics: boolean;          // 指标计算
    evaluation: boolean;       // 管理者评价
    optimization: boolean;     // 优化建议
  };
  
  // 子节点
  children: DecisionNode[];
}
```

#### 4.2 状态图标设计

```
✅ 已完成（绿色圆圈）
🔄 进行中（蓝色旋转图标）
⏸️ 暂停（黄色暂停图标）
❌ 未开始/逾期（红色叉号）
📊 数据驱动指示器（图表图标）
🎯 关键目标标记（靶心图标）
⚡ 高优先级（闪电图标）
```

#### 4.3 OGSM卡片设计

```typescript
function DecisionCard({ node }) {
  return (
    <Card className={`
      w-64 p-4 border-2
      ${levelColors[node.level]}
    `}>
      {/* 头部：名称 + 状态 */}
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-bold">{node.name}</h4>
        <span className="text-xl">{statusIcons[node.status]}</span>
      </div>

      {/* OGSM 信息 */}
      <div className="text-xs space-y-1">
        <div><strong>O:</strong> {node.objective}</div>
        <div><strong>S:</strong> {node.strategies.join(', ')}</div>
        <div className="flex items-center justify-between">
          <span><strong>KPI:</strong> {node.kpi.name}</span>
          <ProgressBadge 
            actual={node.kpi.actual} 
            target={node.kpi.target} 
          />
        </div>
      </div>

      {/* 执行闭环指示器 */}
      <div className="mt-2 flex items-center gap-1">
        <StatusDot active={node.executionLoop.decision} tooltip="决策" />
        <StatusDot active={node.executionLoop.execution} tooltip="执行" />
        <StatusDot active={node.executionLoop.facts} tooltip="业务事实" />
        <StatusDot active={node.executionLoop.metrics} tooltip="指标" />
        <StatusDot active={node.executionLoop.evaluation} tooltip="评价" />
        <StatusDot active={node.executionLoop.optimization} tooltip="优化" />
      </div>
    </Card>
  );
}

// 层级颜色配置
const levelColors = {
  board: 'bg-purple-100 border-purple-500',      // 董事会层：紫色
  executive: 'bg-blue-100 border-blue-500',      // 高管层：蓝色
  department: 'bg-green-100 border-green-500',   // 部门层：绿色
  team: 'bg-yellow-100 border-yellow-500'        // 团队层：黄色
};
```

#### 4.4 横向拉通连线

```typescript
interface CrossLink {
  id: string;
  sourceId: string;      // 源决策ID
  targetId: string;      // 目标决策ID
  type: 'dependency' | 'shared_kpi' | 'collaboration';
  description: string;
}

// 视觉设计
- 依赖关系：橙色虚线箭头
- 共享KPI：绿色虚线双向箭头
- 协同关系：蓝色虚线
```

---

### 五、流程详情与核心资源/能力状态（Process Detail View）

**目标**：详细展示流程关键指标、优化机会、核心资源和能力状态

**技术实现**：
- 自定义React组件
- 文件位置：`src/components/Visualization/ProcessDetailView.tsx`

**设计要点**：

#### 5.1 关键指标卡片

```typescript
interface ProcessMetric {
  id: string;
  name: string;
  value: number;
  target: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  changeRate: number;
}

function MetricCard({ metric }) {
  const isHealthy = metric.value >= metric.target;
  const trendIcon = {
    up: '↑',
    down: '↓',
    stable: '→'
  };

  return (
    <Card className={`
      p-4 border-l-4
      ${isHealthy ? 'border-green-500' : 'border-red-500'}
    `}>
      <div className="text-sm text-gray-500">{metric.name}</div>
      <div className="text-2xl font-bold mt-1">
        {metric.value}{metric.unit}
      </div>
      <div className="flex items-center justify-between mt-2 text-xs">
        <span>目标: {metric.target}{metric.unit}</span>
        <span className={`
          flex items-center gap-1
          ${metric.trend === 'up' ? 'text-green-600' : 
            metric.trend === 'down' ? 'text-red-600' : 'text-gray-600'}
        `}>
          {trendIcon[metric.trend]} {metric.changeRate}%
        </span>
      </div>
    </Card>
  );
}
```

#### 5.2 优化机会点卡片

```typescript
interface OpportunityCard {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  expectedImprovement: string;
  estimatedCost: number;
  estimatedTimeframe: string;
  implementationDifficulty: number;  // 1-5
}

function OpportunityCard({ opportunity }) {
  const priorityStyles = {
    high: 'border-red-500 bg-red-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50'
  };

  return (
    <Card className={`
      p-4 border-l-4 ${priorityStyles[opportunity.priority]}
    `}>
      <div className="flex items-center justify-between">
        <h4 className="font-semibold">{opportunity.title}</h4>
        <Badge>{opportunity.priority}</Badge>
      </div>
      <p className="text-sm mt-2 text-gray-700">{opportunity.description}</p>
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div>
          <span className="text-gray-500">预期提升:</span>
          <span className="font-semibold ml-1">{opportunity.expectedImprovement}</span>
        </div>
        <div>
          <span className="text-gray-500">预计投入:</span>
          <span className="font-semibold ml-1">¥{opportunity.estimatedCost}</span>
        </div>
        <div>
          <span className="text-gray-500">实施难度:</span>
          <DifficultyStars level={opportunity.implementationDifficulty} />
        </div>
      </div>
    </Card>
  );
}
```

#### 5.3 核心资源状态卡片

```typescript
interface CoreResource {
  id: string;
  name: string;
  category: string;
  type: string;
  controlLevel: number;        // 0-1，控制程度
  competitiveness: number;     // 0-1，竞争力
  rarity: 'common' | 'rare' | 'unique';
  status: 'active' | 'developing' | 'depleting';
}

function ResourceCard({ resource }) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold">{resource.name}</h4>
        <Badge>{resource.category}</Badge>
      </div>

      {/* 控制程度进度条 */}
      <div className="mb-2">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">控制程度</span>
          <span className="font-semibold">{(resource.controlLevel * 100).toFixed(0)}%</span>
        </div>
        <ProgressBar 
          value={resource.controlLevel * 100} 
          color={resource.controlLevel > 0.7 ? 'green' : 'yellow'}
        />
      </div>

      {/* 竞争力进度条 */}
      <div className="mb-2">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">竞争力</span>
          <span className="font-semibold">{(resource.competitiveness * 100).toFixed(0)}%</span>
        </div>
        <ProgressBar 
          value={resource.competitiveness * 100} 
          color={resource.competitiveness > 0.7 ? 'green' : 'yellow'}
        />
      </div>

      {/* 稀缺性和状态标签 */}
      <div className="flex items-center gap-2 mt-3">
        <Badge variant={rarityVariant[resource.rarity]}>
          {rarityLabel[resource.rarity]}
        </Badge>
        <Badge variant={statusVariant[resource.status]}>
          {statusLabel[resource.status]}
        </Badge>
      </div>
    </Card>
  );
}
```

#### 5.4 核心能力状态卡片

```typescript
interface CoreCapability {
  id: string;
  name: string;
  category: string;
  maturityLevel: number;           // 0-1，成熟度
  competitiveAdvantage: number;    // 0-1，竞争优势
  transferability: number;         // 0-1，可转移性
  developmentCost: number;
  status: 'emerging' | 'developing' | 'mature' | 'declining';
}

function CapabilityCard({ capability }) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold">{capability.name}</h4>
        <Badge>{capability.category}</Badge>
      </div>

      {/* 成熟度水平 */}
      <div className="mb-2">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">成熟度</span>
          <span className="font-semibold">{(capability.maturityLevel * 100).toFixed(0)}%</span>
        </div>
        <ProgressBar 
          value={capability.maturityLevel * 100} 
          color={capability.maturityLevel > 0.7 ? 'green' : 'yellow'}
        />
      </div>

      {/* 竞争优势 */}
      <div className="mb-2">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-500">竞争优势</span>
          <span className="font-semibold">{(capability.competitiveAdvantage * 100).toFixed(0)}%</span>
        </div>
        <ProgressBar 
          value={capability.competitiveAdvantage * 100} 
          color={capability.competitiveAdvantage > 0.7 ? 'green' : 'yellow'}
        />
      </div>

      {/* 状态和开发成本 */}
      <div className="flex items-center justify-between mt-3">
        <Badge variant={statusVariant[capability.status]}>
          {statusLabel[capability.status]}
        </Badge>
        <span className="text-xs text-gray-500">
          开发成本: ¥{capability.developmentCost}
        </span>
      </div>
    </Card>
  );
}
```

---

## 🎨 主仪表盘布局

### Dashboard 页面结构

```typescript
// src/pages/Dashboard.tsx

export default function Dashboard() {
  const [activeView, setActiveView] = useState<'network' | 'chain' | 'decision' | 'process'>('network');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">BMOS 商业模式优化系统</h1>
          <nav className="flex gap-2">
            <Button 
              variant={activeView === 'network' ? 'default' : 'outline'}
              onClick={() => setActiveView('network')}
            >
              价值网络
            </Button>
            <Button 
              variant={activeView === 'chain' ? 'default' : 'outline'}
              onClick={() => setActiveView('chain')}
            >
              价值链路
            </Button>
            <Button 
              variant={activeView === 'decision' ? 'default' : 'outline'}
              onClick={() => setActiveView('decision')}
            >
              决策管理
            </Button>
            <Button 
              variant={activeView === 'process' ? 'default' : 'outline'}
              onClick={() => setActiveView('process')}
            >
              流程详情
            </Button>
          </nav>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto p-8 space-y-8">
        {/* 视图1：价值分配网络 */}
        {activeView === 'network' && (
          <section>
            <h2 className="text-2xl font-semibold mb-4">价值分配网络</h2>
            <Card className="p-6">
              <ValueNetworkGraph data={networkData} />
            </Card>
          </section>
        )}

        {/* 视图2：价值创造链路 */}
        {activeView === 'chain' && (
          <section>
            <h2 className="text-2xl font-semibold mb-4">价值创造链路分析</h2>
            <ValueChainSankey data={sankeyData} />
            <div className="mt-8">
              <ValueChainFlow chainData={chainData} />
            </div>
          </section>
        )}

        {/* 视图3：层级决策管理 */}
        {activeView === 'decision' && (
          <section>
            <h2 className="text-2xl font-semibold mb-4">层级决策管理</h2>
            <Card className="p-6 overflow-auto">
              <DecisionTreeView decisionsData={decisionsData} />
            </Card>
          </section>
        )}

        {/* 视图4：流程详情 */}
        {activeView === 'process' && (
          <section>
            <h2 className="text-2xl font-semibold mb-4">流程详细分析</h2>
            <Tabs defaultValue="production">
              <TabsList>
                <TabsTrigger value="production">生产流程</TabsTrigger>
                <TabsTrigger value="rd">研发流程</TabsTrigger>
                <TabsTrigger value="marketing">营销流程</TabsTrigger>
                <TabsTrigger value="sales">销售流程</TabsTrigger>
              </TabsList>
              {['production', 'rd', 'marketing', 'sales'].map(process => (
                <TabsContent key={process} value={process}>
                  <ProcessDetailView processData={processesData[process]} />
                </TabsContent>
              ))}
            </Tabs>
          </section>
        )}
      </main>
    </div>
  );
}
```

---

## 📦 依赖包清单

```json
{
  "dependencies": {
    "d3": "^7.8.5",
    "react-flow-renderer": "^10.3.17",
    "recharts": "^2.12.0",
    "react-organizational-chart": "^2.2.1",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-badge": "^1.0.4"
  }
}
```

---

## 🎯 实施优先级

### 第1周：核心可视化组件
1. ValueNetworkGraph（价值分配网络图）
2. ValueChainFlow（价值链路与瓶颈识别）

### 第2周：决策管理与流程详情
1. DecisionTreeView（层级决策树状图）
2. ProcessDetailView（流程详情与资源/能力状态）

### 第3周：数据集成与优化
1. 连接Supabase数据源
2. 实时数据更新
3. 性能优化

### 第4周：交互优化与测试
1. 用户交互优化
2. 动画效果
3. 响应式布局
4. 完整测试

---

## ✨ 特色功能

1. **实时瓶颈预警**：当某个环节效率低于阈值时，自动脉动提醒
2. **智能优化建议**：基于瓶颈识别，自动生成优化建议
3. **决策执行闭环可视化**：6个点的执行闭环状态一目了然
4. **横向拉通连线**：清晰展示跨部门协同关系
5. **资源/能力健康度监控**：实时监控核心资源和能力状态

---

**这套可视化方案将企业商业模式状态具象化，让管理者一目了然地发现优化机会！** 🎉




