# 边际影响分析系统UI/UX设计文档

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2024-01-01
- **负责人**: Cursor AI
- **状态**: ⏳ 待提交 → ✅ 已完成

## 1. 设计概述

### 1.1 设计原则
- **用户中心**: 以用户需求为中心的设计
- **简洁明了**: 界面简洁，操作直观
- **数据驱动**: 突出数据可视化和分析结果
- **响应式**: 支持多设备访问
- **可访问性**: 符合无障碍设计标准

### 1.2 技术栈
- **前端框架**: React 18 + TypeScript
- **UI组件库**: Ant Design + Tailwind CSS
- **图表库**: ECharts + D3.js
- **状态管理**: Redux Toolkit
- **路由**: React Router v6

### 1.3 设计系统
- **色彩系统**: 基于企业品牌色彩
- **字体系统**: 支持中英文混排
- **图标系统**: 统一的图标风格
- **组件系统**: 可复用的组件库

## 2. 页面结构设计

### 2.1 整体布局

#### 2.1.1 主布局结构
```
┌─────────────────────────────────────────────────────────┐
│                    顶部导航栏                            │
├─────────────────────────────────────────────────────────┤
│ 侧边栏 │                   主内容区                      │
│       │                                               │
│       │                                               │
│       │                                               │
│       │                                               │
└─────────────────────────────────────────────────────────┘
```

#### 2.1.2 响应式布局
- **桌面端**: 侧边栏 + 主内容区
- **平板端**: 可折叠侧边栏
- **移动端**: 抽屉式侧边栏

### 2.2 导航设计

#### 2.2.1 顶部导航栏
```typescript
interface TopNavigation {
  logo: string;
  title: string;
  userMenu: {
    avatar: string;
    name: string;
    tenant: string;
    settings: string;
    logout: string;
  };
  notifications: {
    count: number;
    items: Notification[];
  };
}
```

#### 2.2.2 侧边栏导航
```typescript
interface SidebarNavigation {
  items: NavigationItem[];
  collapsed: boolean;
  activeKey: string;
}

interface NavigationItem {
  key: string;
  title: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
}
```

## 3. 核心页面设计

### 3.1 仪表板页面

#### 3.1.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 边际影响分析仪表板                              │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────┐ │
│ │ 关键指标卡片 │ │ 关键指标卡片 │ │ 关键指标卡片 │ │ 卡片 │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └───────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │                趋势图表区域                           │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────────────────────┐ │
│ │   分析结果列表   │ │        实时监控面板             │ │
│ └─────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.1.2 关键指标卡片
```typescript
interface MetricCard {
  title: string;
  value: number;
  unit: string;
  trend: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    period: string;
  };
  status: 'good' | 'warning' | 'danger';
  chart?: ChartData;
}
```

#### 3.1.3 趋势图表
```typescript
interface TrendChart {
  type: 'line' | 'bar' | 'area';
  data: ChartData[];
  xAxis: string[];
  yAxis: {
    label: string;
    unit: string;
  };
  series: {
    name: string;
    data: number[];
    color: string;
  }[];
}
```

### 3.2 资产管理页面

#### 3.2.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 核心资产管理                                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 搜索和筛选区域                                       │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 资产列表表格                                         │ │
│ │ ┌─────┬─────────┬─────────┬─────────┬─────────┬───┐ │ │
│ │ │选择 │资产名称 │资产类型 │当前价值 │状态    │操作│ │ │
│ │ ├─────┼─────────┼─────────┼─────────┼─────────┼───┤ │ │
│ │ │ ☐   │设备A    │研发资产 │100万    │正常    │...│ │ │
│ │ └─────┴─────────┴─────────┴─────────┴─────────┴───┘ │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 分页和操作按钮                                       │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.2.2 资产列表表格
```typescript
interface AssetTable {
  columns: TableColumn[];
  data: Asset[];
  pagination: {
    current: number;
    pageSize: number;
    total: number;
  };
  selection: {
    selectedRowKeys: string[];
    onChange: (keys: string[]) => void;
  };
  actions: {
    create: () => void;
    edit: (id: string) => void;
    delete: (id: string) => void;
    export: () => void;
  };
}
```

#### 3.2.3 资产详情模态框
```typescript
interface AssetDetailModal {
  visible: boolean;
  asset: Asset;
  tabs: {
    basic: AssetBasicInfo;
    cashflow: CashFlowChart;
    analysis: AnalysisResults;
    history: HistoryRecords;
  };
}
```

### 3.3 能力管理页面

#### 3.3.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 核心能力管理                                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 能力概览卡片区域                                     │ │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │ │
│ │ │研发能力 │ │设计能力 │ │生产能力 │ │传播能力 │     │ │
│ │ │ 85%    │ │ 78%    │ │ 92%    │ │ 67%    │     │ │
│ │ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 能力雷达图                                         │ │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 能力绩效趋势图                                       │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.3.2 能力概览卡片
```typescript
interface CapabilityCard {
  name: string;
  type: string;
  currentScore: number;
  targetScore: number;
  trend: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
  };
  status: 'excellent' | 'good' | 'warning' | 'danger';
  metrics: {
    label: string;
    value: number;
    unit: string;
  }[];
}
```

#### 3.3.3 能力雷达图
```typescript
interface CapabilityRadarChart {
  dimensions: string[];
  data: {
    name: string;
    value: number[];
  }[];
  max: number;
  min: number;
  colors: string[];
}
```

### 3.4 价值评估页面

#### 3.4.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 产品价值评估                                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 价值评估概览                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │ │
│ │ │内在价值     │ │认知价值     │ │体验价值     │     │ │
│ │ │ 0.85       │ │ 0.78       │ │ 0.92       │     │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘     │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 价值评估详细分析                                     │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────┐ │ │
│ │ │ 产品特性列表    │ │       价值分析图表           │ │ │
│ │ │                │ │                             │ │ │
│ │ │                │ │                             │ │ │
│ │ └─────────────────┘ └─────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.4.2 价值评估概览
```typescript
interface ValueAssessmentOverview {
  intrinsicValue: {
    score: number;
    trend: TrendData;
    factors: ValueFactor[];
  };
  cognitiveValue: {
    score: number;
    trend: TrendData;
    factors: ValueFactor[];
  };
  experientialValue: {
    score: number;
    trend: TrendData;
    factors: ValueFactor[];
  };
}
```

#### 3.4.3 价值分析图表
```typescript
interface ValueAnalysisChart {
  type: 'radar' | 'bar' | 'line';
  data: {
    categories: string[];
    series: {
      name: string;
      data: number[];
      color: string;
    }[];
  };
  options: ChartOptions;
}
```

### 3.5 边际影响分析页面

#### 3.5.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 边际影响分析                                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 分析配置区域                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │ │
│ │ │分析周期     │ │分析范围     │ │分析选项     │     │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘     │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 分析结果展示区域                                     │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────┐ │ │
│ │ │ 影响系数矩阵    │ │       影响趋势图            │ │ │
│ │ │                │ │                             │ │ │
│ │ │                │ │                             │ │ │
│ │ └─────────────────┘ └─────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘
```

#### 3.5.2 分析配置
```typescript
interface AnalysisConfig {
  period: {
    startDate: string;
    endDate: string;
    type: 'monthly' | 'quarterly' | 'yearly';
  };
  scope: {
    assetTypes: string[];
    capabilityTypes: string[];
    valueTypes: string[];
  };
  options: {
    includeSynergy: boolean;
    includeThreshold: boolean;
    includeLag: boolean;
    optimizationMethod: string;
  };
}
```

#### 3.5.3 影响系数矩阵
```typescript
interface ImpactMatrix {
  rows: string[];
  columns: string[];
  data: number[][];
  colors: {
    min: string;
    max: string;
    neutral: string;
  };
  tooltip: {
    formatter: (value: number, row: string, col: string) => string;
  };
}
```

### 3.6 权重优化页面

#### 3.6.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 动态权重优化                                    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 优化配置区域                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │ │
│ │ │优化方法     │ │目标指标     │ │约束条件     │     │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘     │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 优化结果展示区域                                     │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────┐ │ │
│ │ │ 权重对比图      │ │       优化过程图            │ │ │
│ │ │                │ │                             │ │ │
│ │ │                │ │                             │ │ │
│ │ └─────────────────┘ └─────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.6.2 优化配置
```typescript
interface OptimizationConfig {
  method: 'gradient_descent' | 'genetic_algorithm' | 'simulated_annealing' | 'particle_swarm' | 'bayesian';
  objective: 'r2_score' | 'mse' | 'mae';
  constraints: {
    weightBounds: {
      min: number;
      max: number;
    };
    sumConstraint: number;
  };
  validationMethods: string[];
}
```

#### 3.6.3 权重对比图
```typescript
interface WeightComparisonChart {
  type: 'bar' | 'radar' | 'pie';
  data: {
    categories: string[];
    series: {
      name: string;
      data: number[];
      color: string;
    }[];
  };
  comparison: {
    before: number[];
    after: number[];
  };
}
```

### 3.7 预测分析页面

#### 3.7.1 页面布局
```
┌─────────────────────────────────────────────────────────┐
│ 页面标题: 预测分析                                        │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 预测配置区域                                         │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │ │
│ │ │预测类型     │ │预测时间     │ │模型选择     │     │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘     │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 预测结果展示区域                                     │ │
│ │ ┌─────────────────┐ ┌─────────────────────────────┐ │ │
│ │ │ 预测趋势图      │ │       预测置信区间          │ │ │
│ │ │                │ │                             │ │ │
│ │ │                │ │                             │ │ │
│ │ └─────────────────┘ └─────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### 3.7.2 预测配置
```typescript
interface PredictionConfig {
  type: 'asset_value' | 'capability_performance' | 'value_assessment';
  horizon: number; // 预测时间范围（月）
  model: {
    type: 'ensemble' | 'linear' | 'tree' | 'neural';
    parameters: Record<string, any>;
  };
  inputData: {
    assetIds: string[];
    historicalPeriods: number;
    externalFactors: Record<string, number>;
  };
}
```

#### 3.7.3 预测趋势图
```typescript
interface PredictionTrendChart {
  type: 'line';
  data: {
    historical: {
      x: string[];
      y: number[];
    };
    predicted: {
      x: string[];
      y: number[];
      confidence: {
        upper: number[];
        lower: number[];
      };
    };
  };
  options: {
    showConfidence: boolean;
    showHistorical: boolean;
    colors: {
      historical: string;
      predicted: string;
      confidence: string;
    };
  };
}
```

## 4. 组件设计

### 4.1 基础组件

#### 4.1.1 按钮组件
```typescript
interface ButtonProps {
  type: 'primary' | 'secondary' | 'danger' | 'ghost';
  size: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: string;
  children: React.ReactNode;
  onClick: () => void;
}
```

#### 4.1.2 输入框组件
```typescript
interface InputProps {
  type: 'text' | 'number' | 'email' | 'password';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
}
```

#### 4.1.3 选择器组件
```typescript
interface SelectProps {
  options: {
    label: string;
    value: string;
    disabled?: boolean;
  }[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  disabled?: boolean;
}
```

### 4.2 数据展示组件

#### 4.2.1 表格组件
```typescript
interface TableProps {
  columns: TableColumn[];
  data: any[];
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, size: number) => void;
  };
  selection?: {
    selectedRowKeys: string[];
    onChange: (keys: string[]) => void;
  };
  loading?: boolean;
  rowKey: string;
}
```

#### 4.2.2 图表组件
```typescript
interface ChartProps {
  type: 'line' | 'bar' | 'pie' | 'radar' | 'scatter';
  data: ChartData;
  options?: ChartOptions;
  loading?: boolean;
  height?: number;
  width?: number;
}
```

#### 4.2.3 指标卡片组件
```typescript
interface MetricCardProps {
  title: string;
  value: number;
  unit: string;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    period: string;
  };
  status?: 'good' | 'warning' | 'danger';
  chart?: ChartData;
  loading?: boolean;
}
```

### 4.3 业务组件

#### 4.3.1 资产卡片组件
```typescript
interface AssetCardProps {
  asset: Asset;
  onEdit: (asset: Asset) => void;
  onDelete: (asset: Asset) => void;
  onView: (asset: Asset) => void;
  selected?: boolean;
  onSelect: (asset: Asset, selected: boolean) => void;
}
```

#### 4.3.2 能力雷达图组件
```typescript
interface CapabilityRadarProps {
  data: {
    name: string;
    value: number[];
  }[];
  dimensions: string[];
  max: number;
  min: number;
  colors: string[];
  loading?: boolean;
}
```

#### 4.3.3 价值评估组件
```typescript
interface ValueAssessmentProps {
  assessment: ValueAssessment;
  onUpdate: (assessment: ValueAssessment) => void;
  onAnalyze: (assessment: ValueAssessment) => void;
  loading?: boolean;
}
```

## 5. 交互设计

### 5.1 用户操作流程

#### 5.1.1 资产创建流程
```
1. 点击"创建资产"按钮
2. 填写资产基本信息
3. 设置资产参数
4. 上传相关文档
5. 确认创建
6. 返回资产列表
```

#### 5.1.2 分析执行流程
```
1. 选择分析类型
2. 配置分析参数
3. 选择数据范围
4. 执行分析
5. 查看分析结果
6. 导出分析报告
```

#### 5.1.3 权重优化流程
```
1. 选择优化方法
2. 设置目标指标
3. 配置约束条件
4. 执行优化
5. 查看优化结果
6. 应用优化权重
```

### 5.2 反馈机制

#### 5.2.1 加载状态
```typescript
interface LoadingState {
  global: boolean;
  page: boolean;
  component: boolean;
  message?: string;
}
```

#### 5.2.2 错误处理
```typescript
interface ErrorState {
  hasError: boolean;
  message: string;
  code?: string;
  details?: any;
  retry?: () => void;
}
```

#### 5.2.3 成功提示
```typescript
interface SuccessState {
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

### 5.3 数据验证

#### 5.3.1 表单验证
```typescript
interface FormValidation {
  rules: {
    required?: boolean;
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => boolean;
  };
  message: string;
}
```

#### 5.3.2 数据格式验证
```typescript
interface DataValidation {
  type: 'number' | 'string' | 'date' | 'email' | 'url';
  format?: string;
  range?: {
    min: number;
    max: number;
  };
  required: boolean;
}
```

## 6. 响应式设计

### 6.1 断点设置
```typescript
interface Breakpoints {
  xs: 0;
  sm: 576;
  md: 768;
  lg: 992;
  xl: 1200;
  xxl: 1600;
}
```

### 6.2 布局适配
```typescript
interface ResponsiveLayout {
  mobile: {
    layout: 'stack';
    navigation: 'drawer';
    sidebar: 'hidden';
  };
  tablet: {
    layout: 'grid';
    navigation: 'tabs';
    sidebar: 'collapsible';
  };
  desktop: {
    layout: 'flex';
    navigation: 'sidebar';
    sidebar: 'visible';
  };
}
```

### 6.3 组件适配
```typescript
interface ResponsiveComponent {
  mobile: ComponentProps;
  tablet: ComponentProps;
  desktop: ComponentProps;
}
```

## 7. 可访问性设计

### 7.1 键盘导航
```typescript
interface KeyboardNavigation {
  tabIndex: number;
  onKeyDown: (event: KeyboardEvent) => void;
  onKeyUp: (event: KeyboardEvent) => void;
  onEnter: () => void;
  onEscape: () => void;
}
```

### 7.2 屏幕阅读器支持
```typescript
interface ScreenReaderSupport {
  ariaLabel: string;
  ariaDescription: string;
  ariaExpanded: boolean;
  ariaSelected: boolean;
  role: string;
}
```

### 7.3 颜色对比度
```typescript
interface ColorContrast {
  normal: number; // 4.5:1
  large: number; // 3:1
  enhanced: number; // 7:1
}
```

## 8. 性能优化

### 8.1 懒加载
```typescript
interface LazyLoading {
  components: string[];
  images: string[];
  charts: string[];
  threshold: number;
}
```

### 8.2 虚拟滚动
```typescript
interface VirtualScroll {
  itemHeight: number;
  containerHeight: number;
  overscan: number;
  onScroll: (scrollTop: number) => void;
}
```

### 8.3 缓存策略
```typescript
interface CacheStrategy {
  data: {
    ttl: number;
    maxSize: number;
    strategy: 'lru' | 'fifo' | 'lfu';
  };
  components: {
    memo: boolean;
    pure: boolean;
  };
}
```

## 9. 主题系统

### 9.1 色彩主题
```typescript
interface ColorTheme {
  primary: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };
  secondary: ColorPalette;
  neutral: ColorPalette;
  semantic: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
}
```

### 9.2 字体主题
```typescript
interface FontTheme {
  family: {
    primary: string;
    secondary: string;
    mono: string;
  };
  size: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
  };
  weight: {
    light: number;
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
}
```

### 9.3 间距主题
```typescript
interface SpacingTheme {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
}
```

## 10. 国际化支持

### 10.1 多语言支持
```typescript
interface I18nConfig {
  locales: string[];
  defaultLocale: string;
  messages: Record<string, Record<string, string>>;
  fallback: string;
}
```

### 10.2 本地化格式
```typescript
interface LocaleFormat {
  date: string;
  time: string;
  number: string;
  currency: string;
  percentage: string;
}
```

## 11. 总结

本UI/UX设计文档提供了完整的边际影响分析系统界面设计，包括：

1. **完整的页面设计**: 7个核心页面的详细设计
2. **组件系统**: 基础组件、数据展示组件、业务组件
3. **交互设计**: 用户操作流程、反馈机制、数据验证
4. **响应式设计**: 多设备适配、断点设置、布局适配
5. **可访问性设计**: 键盘导航、屏幕阅读器支持、颜色对比度
6. **性能优化**: 懒加载、虚拟滚动、缓存策略
7. **主题系统**: 色彩、字体、间距主题
8. **国际化支持**: 多语言、本地化格式

该设计系统支持多设备访问，具备良好的用户体验和可访问性，能够满足边际影响分析系统的所有界面需求。


