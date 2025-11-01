# 边际分析图表要求规范

## 概述

本文档定义了边际影响分析系统所需的7个核心图表组件，包括数据可视化、趋势分析、关系网络和价值评估图表。

## 技术栈

- **图表库**: Recharts + D3.js
- **React组件**: 自定义图表组件
- **数据处理**: 实时数据转换
- **交互性**: 支持钻取、筛选、缩放

## 图表规范

### 1. 价值链流程图 (Sankey图)

#### 用途
展示价值在价值链中的流动和转化过程

#### 技术要求
```typescript
interface SankeyChartProps {
  data: {
    nodes: Array<{
      id: string;
      name: string;
      category: 'input' | 'process' | 'output';
      value: number;
    }>;
    links: Array<{
      source: string;
      target: string;
      value: number;
      color?: string;
    }>;
  };
  width?: number;
  height?: number;
  showValues?: boolean;
  interactive?: boolean;
}
```

#### 视觉规范
- **节点颜色**: 
  - 输入节点: #3B82F6 (蓝色)
  - 处理节点: #10B981 (绿色)
  - 输出节点: #F59E0B (橙色)
- **连接线**: 根据流量大小调整粗细
- **标签**: 显示节点名称和数值
- **交互**: 悬停显示详细信息

#### 数据示例
```json
{
  "nodes": [
    { "id": "raw_materials", "name": "原材料", "category": "input", "value": 1000000 },
    { "id": "production", "name": "生产加工", "category": "process", "value": 1200000 },
    { "id": "finished_goods", "name": "成品", "category": "output", "value": 1500000 }
  ],
  "links": [
    { "source": "raw_materials", "target": "production", "value": 1000000 },
    { "source": "production", "target": "finished_goods", "value": 1200000 }
  ]
}
```

### 2. 价值网络图 (Network图)

#### 用途
展示资源、能力和价值之间的复杂关系网络

#### 技术要求
```typescript
interface NetworkChartProps {
  data: {
    nodes: Array<{
      id: string;
      label: string;
      group: 'asset' | 'capability' | 'value';
      size: number;
      color: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
      weight: number;
      type: 'contribution' | 'dependency' | 'synergy';
    }>;
  };
  layout: 'force' | 'hierarchical' | 'circular';
  showLabels?: boolean;
  interactive?: boolean;
}
```

#### 视觉规范
- **节点大小**: 根据重要性调整
- **节点颜色**: 
  - 资产: #8B5CF6 (紫色)
  - 能力: #06B6D4 (青色)
  - 价值: #EF4444 (红色)
- **连接线**: 根据关系强度调整粗细
- **布局**: 力导向布局，自动调整位置

#### 数据示例
```json
{
  "nodes": [
    { "id": "asset_1", "label": "生产设备A", "group": "asset", "size": 100, "color": "#8B5CF6" },
    { "id": "capability_1", "label": "数据分析", "group": "capability", "size": 80, "color": "#06B6D4" },
    { "id": "value_1", "label": "收入增长", "group": "value", "size": 120, "color": "#EF4444" }
  ],
  "edges": [
    { "source": "asset_1", "target": "value_1", "weight": 0.6, "type": "contribution" },
    { "source": "capability_1", "target": "value_1", "weight": 0.4, "type": "contribution" }
  ]
}
```

### 3. 边际贡献图 (Shapley值可视化)

#### 用途
展示各因素对目标指标的边际贡献度

#### 技术要求
```typescript
interface ShapleyChartProps {
  data: Array<{
    factor: string;
    shapleyValue: number;
    contribution: number;
    significance: boolean;
    pValue: number;
  }>;
  targetMetric: string;
  totalValue: number;
  showSignificance?: boolean;
  sortBy?: 'shapley' | 'contribution';
}
```

#### 视觉规范
- **柱状图**: 水平柱状图展示贡献度
- **颜色编码**: 
  - 显著贡献: #10B981 (绿色)
  - 一般贡献: #F59E0B (橙色)
  - 不显著: #6B7280 (灰色)
- **标签**: 显示因子名称、Shapley值、贡献百分比
- **排序**: 按贡献度降序排列

#### 数据示例
```json
{
  "targetMetric": "收入",
  "totalValue": 10000000,
  "data": [
    {
      "factor": "生产设备A",
      "shapleyValue": 0.6,
      "contribution": 6000000,
      "significance": true,
      "pValue": 0.02
    },
    {
      "factor": "数据分析能力",
      "shapleyValue": 0.4,
      "contribution": 4000000,
      "significance": true,
      "pValue": 0.01
    }
  ]
}
```

### 4. 时间序列预测图

#### 用途
展示历史趋势和未来预测

#### 技术要求
```typescript
interface TimeSeriesChartProps {
  data: Array<{
    date: string;
    actual: number;
    predicted?: number;
    confidenceInterval?: {
      lower: number;
      upper: number;
    };
  }>;
  xAxis: {
    type: 'time';
    format: string;
  };
  yAxis: {
    label: string;
    format: 'currency' | 'number' | 'percentage';
  };
  showConfidence?: boolean;
  showTrend?: boolean;
}
```

#### 视觉规范
- **历史数据**: 实线，蓝色 (#3B82F6)
- **预测数据**: 虚线，橙色 (#F59E0B)
- **置信区间**: 半透明填充区域
- **趋势线**: 平滑曲线
- **交互**: 悬停显示具体数值

#### 数据示例
```json
{
  "data": [
    { "date": "2024-01-01", "actual": 1000000, "predicted": null },
    { "date": "2024-02-01", "actual": 1050000, "predicted": null },
    { "date": "2024-03-01", "actual": null, "predicted": 1100000, "confidenceInterval": { "lower": 1000000, "upper": 1200000 } }
  ],
  "xAxis": { "type": "time", "format": "YYYY-MM" },
  "yAxis": { "label": "收入", "format": "currency" }
}
```

### 5. 资产NPV趋势图

#### 用途
展示资产净现值的时间变化趋势

#### 技术要求
```typescript
interface NPVTrendChartProps {
  data: Array<{
    assetId: string;
    assetName: string;
    timeline: Array<{
      date: string;
      npv: number;
      cashFlow: number;
      discountRate: number;
    }>;
  }>;
  showMultipleAssets?: boolean;
  showCashFlow?: boolean;
  showDiscountRate?: boolean;
}
```

#### 视觉规范
- **NPV线**: 粗线，不同颜色区分资产
- **现金流**: 柱状图，半透明
- **折现率**: 虚线，灰色
- **图例**: 清晰标识各线条含义
- **交互**: 点击切换显示/隐藏

#### 数据示例
```json
{
  "data": [
    {
      "assetId": "asset_1",
      "assetName": "生产设备A",
      "timeline": [
        { "date": "2024-01-01", "npv": 1200000, "cashFlow": 120000, "discountRate": 0.10 },
        { "date": "2024-02-01", "npv": 1250000, "cashFlow": 130000, "discountRate": 0.10 }
      ]
    }
  ]
}
```

### 6. 能力价值热力图

#### 用途
展示能力在不同维度的价值分布

#### 技术要求
```typescript
interface CapabilityHeatmapProps {
  data: Array<{
    capability: string;
    dimension: string;
    value: number;
    level: 'low' | 'medium' | 'high';
  }>;
  dimensions: string[];
  capabilities: string[];
  colorScale: 'viridis' | 'plasma' | 'inferno' | 'magma';
  showValues?: boolean;
  interactive?: boolean;
}
```

#### 视觉规范
- **颜色映射**: 从低到高，蓝色到红色
- **数值显示**: 单元格内显示具体数值
- **悬停效果**: 显示详细信息
- **排序**: 支持按行或列排序

#### 数据示例
```json
{
  "dimensions": ["技术能力", "管理能力", "创新能力"],
  "capabilities": ["数据分析", "项目管理", "团队协作"],
  "data": [
    { "capability": "数据分析", "dimension": "技术能力", "value": 0.8, "level": "high" },
    { "capability": "项目管理", "dimension": "管理能力", "value": 0.6, "level": "medium" }
  ]
}
```

### 7. 产品价值雷达图

#### 用途
展示产品在多个价值维度的综合评估

#### 技术要求
```typescript
interface RadarChartProps {
  data: Array<{
    product: string;
    dimensions: Array<{
      name: string;
      value: number;
      maxValue: number;
    }>;
  }>;
  dimensions: string[];
  maxValue: number;
  showMultipleProducts?: boolean;
  showTargetValues?: boolean;
  interactive?: boolean;
}
```

#### 视觉规范
- **雷达形状**: 多边形，填充半透明
- **网格线**: 同心圆，表示不同等级
- **数据点**: 圆点，不同颜色区分产品
- **标签**: 维度名称和数值
- **图例**: 产品标识

#### 数据示例
```json
{
  "dimensions": ["内在价值", "认知价值", "体验价值"],
  "maxValue": 10,
  "data": [
    {
      "product": "产品A",
      "dimensions": [
        { "name": "内在价值", "value": 8.2, "maxValue": 10 },
        { "name": "认知价值", "value": 7.8, "maxValue": 10 },
        { "name": "体验价值", "value": 8.5, "maxValue": 10 }
      ]
    }
  ]
}
```

## 通用图表组件

### 基础图表组件
```typescript
interface BaseChartProps {
  data: any[];
  width?: number;
  height?: number;
  title?: string;
  subtitle?: string;
  loading?: boolean;
  error?: string;
  onDataClick?: (data: any) => void;
  onDataHover?: (data: any) => void;
}

const BaseChart: React.FC<BaseChartProps> = ({
  data,
  width = 800,
  height = 400,
  title,
  subtitle,
  loading,
  error,
  onDataClick,
  onDataHover
}) => {
  if (loading) return <ChartSkeleton />;
  if (error) return <ChartError message={error} />;
  
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold">{title}</h3>}
      {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
      <div className="mt-4">
        {/* 图表内容 */}
      </div>
    </div>
  );
};
```

### 图表容器组件
```typescript
interface ChartContainerProps {
  children: React.ReactNode;
  title: string;
  actions?: React.ReactNode;
  filters?: React.ReactNode;
  exportable?: boolean;
  onExport?: () => void;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  children,
  title,
  actions,
  filters,
  exportable = false,
  onExport
}) => {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="flex items-center gap-2">
          {actions}
          {exportable && (
            <Button variant="outline" size="sm" onClick={onExport}>
              <Download className="w-4 h-4 mr-2" />
              导出
            </Button>
          )}
        </div>
      </div>
      {filters && <div className="mb-4">{filters}</div>}
      <div className="w-full">{children}</div>
    </Card>
  );
};
```

## 响应式设计

### 断点适配
```typescript
const useResponsiveChart = () => {
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 });
  
  useEffect(() => {
    const updateDimensions = () => {
      const container = document.getElementById('chart-container');
      if (container) {
        setDimensions({
          width: container.offsetWidth,
          height: Math.max(300, container.offsetWidth * 0.5)
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);
  
  return dimensions;
};
```

### 移动端优化
- **触摸交互**: 支持触摸缩放和拖拽
- **简化显示**: 移动端隐藏部分细节
- **垂直布局**: 移动端采用垂直布局

## 性能优化

### 数据虚拟化
```typescript
const useVirtualizedData = (data: any[], maxItems: number = 1000) => {
  const [visibleData, setVisibleData] = useState(data.slice(0, maxItems));
  
  useEffect(() => {
    if (data.length > maxItems) {
      // 实现数据虚拟化逻辑
      setVisibleData(data.slice(0, maxItems));
    } else {
      setVisibleData(data);
    }
  }, [data, maxItems]);
  
  return visibleData;
};
```

### 渲染优化
- **防抖**: 数据更新防抖
- **节流**: 滚动事件节流
- **Memo**: React.memo优化
- **懒加载**: 图表组件懒加载

## 交互功能

### 钻取功能
```typescript
interface DrillDownProps {
  onDrillDown: (data: any) => void;
  onDrillUp: () => void;
  currentLevel: number;
  maxLevel: number;
}

const DrillDown: React.FC<DrillDownProps> = ({
  onDrillDown,
  onDrillUp,
  currentLevel,
  maxLevel
}) => {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={onDrillUp}
        disabled={currentLevel === 0}
      >
        <ChevronUp className="w-4 h-4" />
        上钻
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={onDrillDown}
        disabled={currentLevel === maxLevel}
      >
        <ChevronDown className="w-4 h-4" />
        下钻
      </Button>
    </div>
  );
};
```

### 筛选功能
```typescript
interface ChartFilterProps {
  filters: Array<{
    key: string;
    label: string;
    type: 'select' | 'date' | 'number';
    options?: Array<{ value: any; label: string }>;
  }>;
  values: Record<string, any>;
  onChange: (key: string, value: any) => void;
}

const ChartFilter: React.FC<ChartFilterProps> = ({
  filters,
  values,
  onChange
}) => {
  return (
    <div className="flex flex-wrap gap-4">
      {filters.map(filter => (
        <div key={filter.key} className="flex flex-col">
          <label className="text-sm font-medium mb-1">{filter.label}</label>
          {filter.type === 'select' && (
            <Select
              value={values[filter.key]}
              onValueChange={(value) => onChange(filter.key, value)}
            >
              {filter.options?.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </Select>
          )}
        </div>
      ))}
    </div>
  );
};
```

## 测试策略

### 单元测试
```typescript
describe('SankeyChart', () => {
  it('renders nodes and links correctly', () => {
    const mockData = {
      nodes: [{ id: '1', name: 'Node 1', category: 'input', value: 100 }],
      links: [{ source: '1', target: '2', value: 100 }]
    };
    
    render(<SankeyChart data={mockData} />);
    expect(screen.getByText('Node 1')).toBeInTheDocument();
  });
  
  it('handles empty data gracefully', () => {
    render(<SankeyChart data={{ nodes: [], links: [] }} />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });
});
```

### 集成测试
```typescript
describe('Chart Integration', () => {
  it('updates chart when data changes', async () => {
    const { rerender } = render(<SankeyChart data={initialData} />);
    
    rerender(<SankeyChart data={updatedData} />);
    
    await waitFor(() => {
      expect(screen.getByText('Updated Node')).toBeInTheDocument();
    });
  });
});
```

### 性能测试
```typescript
describe('Chart Performance', () => {
  it('renders large datasets efficiently', () => {
    const largeDataset = generateLargeDataset(10000);
    const startTime = performance.now();
    
    render(<SankeyChart data={largeDataset} />);
    
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(1000); // 1秒内完成
  });
});
```

