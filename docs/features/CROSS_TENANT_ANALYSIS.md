# 跨租户分析功能设计

## 📋 功能概述

为分析师提供跨租户分析功能，支持不同企业的资产ROI对比、行业基准分析和趋势分析。

## 🎯 三大分析功能

### 1. 对比分析：不同企业的资产ROI对比

#### 功能描述
- **资产ROI对比**：对比不同企业的同类资产ROI表现
- **能力价值对比**：对比不同企业的同类能力价值
- **效率指标对比**：对比不同企业的效率指标

#### 数据模型
```sql
-- 跨租户资产ROI对比视图
CREATE VIEW vw_cross_tenant_asset_roi AS
SELECT 
    t.tenant_name,
    am.asset_category,
    am.asset_name,
    aa.accumulated_value,
    aa.monthly_delta,
    cvh.capability_value,
    cvh.roi,
    aa.month_date
FROM asset_accumulation aa
JOIN core_asset_master am ON aa.asset_id = am.asset_id
JOIN tenants t ON am.tenant_id = t.tenant_id
LEFT JOIN capability_value_history cvh ON am.asset_id = cvh.asset_id
WHERE aa.month_date >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY t.tenant_name, am.asset_category, aa.month_date;

-- 跨租户能力价值对比视图
CREATE VIEW vw_cross_tenant_capability_value AS
SELECT 
    t.tenant_name,
    cm.capability_category,
    cm.capability_name,
    cvh.capability_value,
    cvh.roi,
    cvh.month_date
FROM capability_value_history cvh
JOIN core_capability_master cm ON cvh.capability_id = cm.capability_id
JOIN tenants t ON cm.tenant_id = t.tenant_id
WHERE cvh.month_date >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY t.tenant_name, cm.capability_category, cvh.month_date;
```

#### API接口
```typescript
// 资产ROI对比分析
interface AssetROIComparison {
  tenantId: string;
  tenantName: string;
  assetCategory: string;
  assetName: string;
  currentROI: number;
  averageROI: number;
  rank: number;
  percentile: number;
}

// 能力价值对比分析
interface CapabilityValueComparison {
  tenantId: string;
  tenantName: string;
  capabilityCategory: string;
  capabilityName: string;
  currentValue: number;
  averageValue: number;
  rank: number;
  percentile: number;
}

// 对比分析API
async function getAssetROIComparison(
  assetCategory: string,
  month: string
): Promise<AssetROIComparison[]> {
  return await db.query(`
    SELECT 
      t.tenant_id,
      t.tenant_name,
      am.asset_category,
      am.asset_name,
      cvh.roi as current_roi,
      AVG(cvh.roi) OVER (PARTITION BY am.asset_category) as average_roi,
      RANK() OVER (PARTITION BY am.asset_category ORDER BY cvh.roi DESC) as rank,
      PERCENT_RANK() OVER (PARTITION BY am.asset_category ORDER BY cvh.roi) as percentile
    FROM capability_value_history cvh
    JOIN core_capability_master cm ON cvh.capability_id = cm.capability_id
    JOIN tenants t ON cm.tenant_id = t.tenant_id
    WHERE am.asset_category = $1 AND cvh.month_date = $2
    ORDER BY cvh.roi DESC
  `, [assetCategory, month]);
}
```

### 2. 行业基准：基于多企业数据的行业基准分析

#### 功能描述
- **行业基准计算**：基于多企业数据计算行业基准值
- **基准对比**：企业指标与行业基准的对比
- **基准趋势**：行业基准的变化趋势

#### 数据模型
```sql
-- 行业基准计算表
CREATE TABLE industry_benchmarks (
    benchmark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL, -- asset_roi/capability_value/efficiency
    metric_category VARCHAR(50) NOT NULL, -- production/rd/dissemination/delivery/channel
    benchmark_value DECIMAL(10,4) NOT NULL,
    benchmark_percentile DECIMAL(5,4), -- 基准百分位
    sample_size INT NOT NULL, -- 样本数量
    calculation_month DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 行业基准历史表
CREATE TABLE industry_benchmark_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    benchmark_id UUID REFERENCES industry_benchmarks(benchmark_id),
    metric_type VARCHAR(50) NOT NULL,
    metric_category VARCHAR(50) NOT NULL,
    benchmark_value DECIMAL(10,4) NOT NULL,
    benchmark_percentile DECIMAL(5,4),
    sample_size INT NOT NULL,
    calculation_month DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 基准计算逻辑
```typescript
// 行业基准计算
async function calculateIndustryBenchmark(
  metricType: string,
  metricCategory: string,
  month: string
): Promise<IndustryBenchmark> {
  // 1. 获取所有企业的相关数据
  const data = await getCrossTenantData(metricType, metricCategory, month);
  
  // 2. 计算基准值
  const benchmark = {
    metricType,
    metricCategory,
    benchmarkValue: calculatePercentile(data, 0.5), // 中位数
    benchmarkPercentile: 0.5,
    sampleSize: data.length,
    calculationMonth: month
  };
  
  // 3. 保存基准值
  await saveIndustryBenchmark(benchmark);
  
  return benchmark;
}

// 企业基准对比
async function compareWithBenchmark(
  tenantId: string,
  metricType: string,
  metricCategory: string,
  month: string
): Promise<BenchmarkComparison> {
  const benchmark = await getIndustryBenchmark(metricType, metricCategory, month);
  const tenantData = await getTenantData(tenantId, metricType, metricCategory, month);
  
  return {
    tenantId,
    metricType,
    metricCategory,
    tenantValue: tenantData.value,
    benchmarkValue: benchmark.benchmarkValue,
    deviation: tenantData.value - benchmark.benchmarkValue,
    deviationPercent: ((tenantData.value - benchmark.benchmarkValue) / benchmark.benchmarkValue) * 100,
    percentile: calculatePercentileRank(tenantData.value, benchmark.sampleSize),
    performance: tenantData.value > benchmark.benchmarkValue ? 'above' : 'below'
  };
}
```

### 3. 趋势分析：跨企业的趋势分析

#### 功能描述
- **跨企业趋势**：分析多个企业的共同趋势
- **行业趋势**：基于多企业数据的行业趋势
- **趋势预测**：基于历史数据的趋势预测

#### 数据模型
```sql
-- 跨企业趋势分析表
CREATE TABLE cross_tenant_trends (
    trend_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trend_type VARCHAR(50) NOT NULL, -- asset_roi/capability_value/efficiency
    trend_category VARCHAR(50) NOT NULL,
    trend_direction VARCHAR(20) NOT NULL, -- increasing/decreasing/stable
    trend_strength DECIMAL(5,4) NOT NULL, -- 趋势强度
    trend_period VARCHAR(20) NOT NULL, -- 1m/3m/6m/12m
    sample_size INT NOT NULL,
    calculation_month DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 趋势分析结果表
CREATE TABLE trend_analysis_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trend_id UUID REFERENCES cross_tenant_trends(trend_id),
    tenant_id UUID NOT NULL,
    tenant_name VARCHAR(200) NOT NULL,
    current_value DECIMAL(15,4) NOT NULL,
    trend_value DECIMAL(15,4) NOT NULL,
    deviation DECIMAL(15,4) NOT NULL,
    rank INT NOT NULL,
    percentile DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 趋势分析逻辑
```typescript
// 跨企业趋势分析
async function analyzeCrossTenantTrends(
  trendType: string,
  trendCategory: string,
  period: string
): Promise<CrossTenantTrend> {
  // 1. 获取跨企业数据
  const crossTenantData = await getCrossTenantData(trendType, trendCategory, period);
  
  // 2. 计算趋势
  const trend = {
    trendType,
    trendCategory,
    trendDirection: calculateTrendDirection(crossTenantData),
    trendStrength: calculateTrendStrength(crossTenantData),
    trendPeriod: period,
    sampleSize: crossTenantData.length,
    calculationMonth: new Date()
  };
  
  // 3. 保存趋势分析
  await saveCrossTenantTrend(trend);
  
  return trend;
}

// 趋势预测
async function predictTrend(
  trendType: string,
  trendCategory: string,
  forecastMonths: number
): Promise<TrendForecast> {
  // 1. 获取历史趋势数据
  const historicalData = await getHistoricalTrendData(trendType, trendCategory);
  
  // 2. 使用时间序列模型预测
  const forecast = await timeSeriesForecast(historicalData, forecastMonths);
  
  // 3. 计算预测置信度
  const confidence = calculateForecastConfidence(historicalData, forecast);
  
  return {
    trendType,
    trendCategory,
    forecast,
    confidence,
    forecastMonths
  };
}
```

## 🔐 权限控制设计

### 1. 分析师权限配置

#### 权限矩阵
```typescript
// 分析师权限配置
interface AnalystPermissions {
  tenantId: string;
  authorizedTenants: string[]; // 授权访问的租户列表
  analysisTypes: string[]; // 允许的分析类型
  dataAccess: {
    crossTenant: boolean; // 跨租户分析权限
    benchmark: boolean; // 行业基准分析权限
    trend: boolean; // 趋势分析权限
  };
  restrictions: {
    maxTenants: number; // 最大租户数量
    dataRetention: number; // 数据保留期限（月）
    exportLimit: number; // 导出限制
  };
}
```

#### 权限验证
```typescript
// 权限验证中间件
async function validateAnalystPermissions(
  analystId: string,
  requestedTenants: string[],
  analysisType: string
): Promise<boolean> {
  const permissions = await getAnalystPermissions(analystId);
  
  // 1. 检查租户授权
  const unauthorizedTenants = requestedTenants.filter(
    tenant => !permissions.authorizedTenants.includes(tenant)
  );
  
  if (unauthorizedTenants.length > 0) {
    throw new Error(`未授权访问租户: ${unauthorizedTenants.join(', ')}`);
  }
  
  // 2. 检查分析类型权限
  if (!permissions.analysisTypes.includes(analysisType)) {
    throw new Error(`未授权分析类型: ${analysisType}`);
  }
  
  // 3. 检查数据访问权限
  if (analysisType === 'cross_tenant' && !permissions.dataAccess.crossTenant) {
    throw new Error('未授权跨租户分析');
  }
  
  return true;
}
```

### 2. 数据脱敏策略

#### 敏感数据脱敏
```typescript
// 数据脱敏处理
function anonymizeTenantData(data: any[]): any[] {
  return data.map(item => ({
    ...item,
    tenantName: `企业${item.tenantId.slice(-4)}`, // 脱敏企业名称
    assetName: item.assetName.replace(/\d+/g, '***'), // 脱敏资产名称
    capabilityName: item.capabilityName.replace(/\d+/g, '***'), // 脱敏能力名称
    // 保留数值用于分析，但脱敏标识信息
  }));
}
```

## 📊 分析结果展示

### 1. 对比分析结果

#### 资产ROI对比图表
```typescript
// 资产ROI对比图表数据
interface AssetROIComparisonChart {
  categories: string[]; // 资产类别
  series: {
    name: string; // 企业名称
    data: number[]; // ROI数据
  }[];
  benchmarks: {
    name: string; // 基准名称
    data: number[]; // 基准数据
  }[];
}
```

#### 能力价值对比图表
```typescript
// 能力价值对比图表数据
interface CapabilityValueComparisonChart {
  categories: string[]; // 能力类别
  series: {
    name: string; // 企业名称
    data: number[]; // 能力价值数据
  }[];
  benchmarks: {
    name: string; // 基准名称
    data: number[]; // 基准数据
  }[];
}
```

### 2. 行业基准结果

#### 基准对比仪表盘
```typescript
// 基准对比仪表盘数据
interface BenchmarkDashboard {
  tenantId: string;
  tenantName: string;
  metrics: {
    assetROI: {
      current: number;
      benchmark: number;
      deviation: number;
      percentile: number;
    };
    capabilityValue: {
      current: number;
      benchmark: number;
      deviation: number;
      percentile: number;
    };
    efficiency: {
      current: number;
      benchmark: number;
      deviation: number;
      percentile: number;
    };
  };
  overallPerformance: 'above' | 'below' | 'average';
  recommendations: string[];
}
```

### 3. 趋势分析结果

#### 趋势分析图表
```typescript
// 趋势分析图表数据
interface TrendAnalysisChart {
  timeSeries: string[]; // 时间序列
  trends: {
    name: string; // 趋势名称
    data: number[]; // 趋势数据
  }[];
  forecasts: {
    name: string; // 预测名称
    data: number[]; // 预测数据
    confidence: number; // 预测置信度
  }[];
}
```

## 🚀 实施计划

### 阶段1：跨租户数据查询（Week 1-2）
1. **权限控制**：实现分析师跨租户权限验证
2. **数据查询**：实现跨租户数据查询API
3. **数据脱敏**：实现敏感数据脱敏处理

### 阶段2：对比分析功能（Week 3-4）
1. **资产ROI对比**：实现资产ROI对比分析
2. **能力价值对比**：实现能力价值对比分析
3. **对比图表**：实现对比分析结果可视化

### 阶段3：行业基准分析（Week 5-6）
1. **基准计算**：实现行业基准计算逻辑
2. **基准对比**：实现企业基准对比分析
3. **基准仪表盘**：实现基准对比结果展示

### 阶段4：趋势分析功能（Week 7-8）
1. **趋势计算**：实现跨企业趋势分析
2. **趋势预测**：实现趋势预测功能
3. **趋势图表**：实现趋势分析结果可视化

---

**本设计确保分析师能够进行跨租户的对比分析、行业基准分析和趋势分析，同时保证数据安全和权限控制。**





