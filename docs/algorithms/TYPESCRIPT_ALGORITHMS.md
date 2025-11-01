# TypeScript算法实现指南

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **可用**

---

## 📋 概述

本文档提供所有算法的**TypeScript实现版本**，可直接用于Supabase Edge Functions。

**重要约束**:
- ✅ 执行时间 ≤ 10秒
- ✅ 计算复杂度 O(n) 或更低
- ✅ 仅使用TypeScript原生功能和Deno标准库
- ✅ 不使用外部依赖（除Supabase SDK）

---

## 🔧 基础工具函数

### 数组统计函数

```typescript
/**
 * 计算数组和
 */
export function sum(values: number[]): number {
  return values.reduce((acc, val) => acc + val, 0);
}

/**
 * 计算数组平均值
 */
export function average(values: number[]): number {
  if (values.length === 0) return 0;
  return sum(values) / values.length;
}

/**
 * 计算数组最大值
 */
export function max(values: number[]): number {
  return Math.max(...values);
}

/**
 * 计算数组最小值
 */
export function min(values: number[]): number {
  return Math.min(...values);
}

/**
 * 计算标准差
 */
export function standardDeviation(values: number[]): number {
  if (values.length === 0) return 0;
  const avg = average(values);
  const variance = average(values.map(v => Math.pow(v - avg, 2)));
  return Math.sqrt(variance);
}
```

---

## 📊 简单算法实现

### 1. ThresholdAnalysis（阈值识别）

**用途**: 识别超出阈值的数据点

```typescript
interface ThresholdConfig {
  field: string;
  threshold: number;
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq';
}

interface ThresholdResult {
  matched: any[];
  count: number;
  threshold: number;
}

/**
 * 阈值分析
 * 复杂度: O(n)
 */
export function thresholdAnalysis(
  data: any[],
  config: ThresholdConfig
): ThresholdResult {
  const matched = data.filter(item => {
    const value = item[config.field];
    
    switch (config.operator) {
      case 'gt':
        return value > config.threshold;
      case 'lt':
        return value < config.threshold;
      case 'gte':
        return value >= config.threshold;
      case 'lte':
        return value <= config.threshold;
      case 'eq':
        return value === config.threshold;
      default:
        return false;
    }
  });

  return {
    matched,
    count: matched.length,
    threshold: config.threshold
  };
}
```

### 2. DynamicWeightCalculator（动态权重计算 - 简化版）

**用途**: 计算动态权重

```typescript
interface WeightConfig {
  initialWeights: number[];
  adjustmentFactors: number[];
  decayRate?: number;
}

/**
 * 动态权重计算（简化版）
 * 复杂度: O(n)
 */
export function calculateDynamicWeights(
  config: WeightConfig,
  iterations: number = 1
): number[] {
  let weights = [...config.initialWeights];
  const decayRate = config.decayRate || 0.9;

  for (let i = 0; i < iterations; i++) {
    // 应用调整因子
    weights = weights.map((w, idx) => {
      const adjustment = config.adjustmentFactors[idx] || 1;
      return w * adjustment * Math.pow(decayRate, i);
    });

    // 归一化
    const total = sum(weights);
    if (total > 0) {
      weights = weights.map(w => w / total);
    }
  }

  return weights;
}
```

---

## 🤖 机器学习算法简化版

### 3. LinearRegression（线性回归 - 替代XGBoost）

**用途**: 预测OKR达成概率、需求优先级等

```typescript
interface FeatureVector {
  [key: string]: number;
}

interface LinearRegressionModel {
  weights: number[];
  bias: number;
  featureNames: string[];
}

/**
 * 训练线性回归模型（简化版）
 * 复杂度: O(n*m)，n=样本数，m=特征数（通常m很小，所以接近O(n)）
 */
export function trainLinearRegression(
  features: FeatureVector[],
  labels: number[],
  learningRate: number = 0.01,
  iterations: number = 100
): LinearRegressionModel {
  if (features.length !== labels.length || features.length === 0) {
    throw new Error('Invalid training data');
  }

  const featureNames = Object.keys(features[0]);
  const numFeatures = featureNames.length;
  
  // 初始化权重和偏置
  let weights = new Array(numFeatures).fill(0);
  let bias = 0;

  // 特征归一化（防止数值溢出）
  const normalizedFeatures = features.map(f => {
    const normalized: FeatureVector = {};
    featureNames.forEach(name => {
      normalized[name] = (f[name] || 0) / 100; // 简单归一化
    });
    return normalized;
  });

  // 梯度下降训练
  for (let iter = 0; iter < iterations; iter++) {
    let totalError = 0;
    const weightGradients = new Array(numFeatures).fill(0);
    let biasGradient = 0;

    for (let i = 0; i < normalizedFeatures.length; i++) {
      // 预测
      let prediction = bias;
      featureNames.forEach((name, idx) => {
        prediction += weights[idx] * normalizedFeatures[i][name];
      });

      // 误差
      const error = prediction - labels[i];
      totalError += error * error;

      // 梯度
      biasGradient += error;
      featureNames.forEach((name, idx) => {
        weightGradients[idx] += error * normalizedFeatures[i][name];
      });
    }

    // 更新权重和偏置
    const avgError = totalError / normalizedFeatures.length;
    const avgBiasGradient = biasGradient / normalizedFeatures.length;
    
    bias -= learningRate * avgBiasGradient;
    weights = weights.map((w, idx) => {
      const avgGradient = weightGradients[idx] / normalizedFeatures.length;
      return w - learningRate * avgGradient;
    });

    // 早停（如果误差足够小）
    if (avgError < 0.001) break;
  }

  return {
    weights,
    bias,
    featureNames
  };
}

/**
 * 使用线性回归模型预测
 * 复杂度: O(m)，m=特征数（通常很小，所以是O(1)）
 */
export function predictLinearRegression(
  model: LinearRegressionModel,
  features: FeatureVector
): number {
  let prediction = model.bias;
  
  model.featureNames.forEach((name, idx) => {
    const value = (features[name] || 0) / 100; // 归一化
    prediction += model.weights[idx] * value;
  });

  // 归一化到[0, 1]
  return Math.max(0, Math.min(1, prediction));
}
```

### 4. MovingAverage（移动平均 - 替代ARIMA）

**用途**: 时间序列预测、趋势分析

```typescript
/**
 * 简单移动平均
 * 复杂度: O(n)
 */
export function simpleMovingAverage(
  values: number[],
  windowSize: number
): number[] {
  if (windowSize <= 0 || windowSize > values.length) {
    throw new Error('Invalid window size');
  }

  const result: number[] = [];
  
  for (let i = windowSize - 1; i < values.length; i++) {
    const window = values.slice(i - windowSize + 1, i + 1);
    result.push(average(window));
  }

  return result;
}

/**
 * 指数移动平均
 * 复杂度: O(n)
 */
export function exponentialMovingAverage(
  values: number[],
  alpha: number = 0.3
): number[] {
  if (alpha < 0 || alpha > 1) {
    throw new Error('Alpha must be between 0 and 1');
  }

  const result: number[] = [values[0]]; // 第一个值作为初始值

  for (let i = 1; i < values.length; i++) {
    const ema = alpha * values[i] + (1 - alpha) * result[i - 1];
    result.push(ema);
  }

  return result;
}

/**
 * 线性趋势预测
 * 复杂度: O(n)
 */
export function linearTrend(
  values: number[],
  periods: number = 1
): number {
  if (values.length < 2) return values[0] || 0;

  // 计算线性回归系数（简化为两点）
  const n = values.length;
  const x = Array.from({ length: n }, (_, i) => i);
  const y = values;

  const sumX = sum(x);
  const sumY = sum(y);
  const sumXY = x.reduce((acc, val, idx) => acc + val * y[idx], 0);
  const sumX2 = x.reduce((acc, val) => acc + val * val, 0);

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  // 预测未来值
  return slope * (n - 1 + periods) + intercept;
}
```

### 5. WeightedScoring（加权评分 - 替代MLP）

**用途**: 需求优先级分析、评分排序

```typescript
interface WeightedScoreConfig {
  fields: string[];
  weights: number[];
  normalization?: 'min-max' | 'z-score' | 'none';
}

/**
 * 加权评分
 * 复杂度: O(n*m)，n=记录数，m=字段数
 */
export function weightedScoring(
  data: any[],
  config: WeightedScoreConfig
): { item: any; score: number }[] {
  if (config.fields.length !== config.weights.length) {
    throw new Error('Fields and weights must have same length');
  }

  // 归一化权重
  const totalWeight = sum(config.weights);
  const normalizedWeights = config.weights.map(w => w / totalWeight);

  // 计算每个记录的分数
  return data.map(item => {
    let score = 0;

    config.fields.forEach((field, idx) => {
      const value = item[field] || 0;
      const normalizedValue = normalizeValue(value, data, field, config.normalization);
      score += normalizedWeights[idx] * normalizedValue;
    });

    return {
      item,
      score
    };
  }).sort((a, b) => b.score - a.score); // 降序排序
}

/**
 * 值归一化
 */
function normalizeValue(
  value: number,
  allData: any[],
  field: string,
  method?: 'min-max' | 'z-score' | 'none'
): number {
  if (!method || method === 'none') return value;

  const values = allData.map(d => d[field] || 0);

  if (method === 'min-max') {
    const minVal = min(values);
    const maxVal = max(values);
    const range = maxVal - minVal;
    return range === 0 ? 0 : (value - minVal) / range;
  }

  if (method === 'z-score') {
    const avg = average(values);
    const std = standardDeviation(values);
    return std === 0 ? 0 : (value - avg) / std;
  }

  return value;
}
```

### 6. PearsonCorrelation（Pearson相关系数 - 用于协同效应分析）

**用途**: 分析变量间相关性（替代复杂的协同效应分析）

```typescript
/**
 * 计算Pearson相关系数
 * 复杂度: O(n)
 */
export function pearsonCorrelation(x: number[], y: number[]): number {
  if (x.length !== y.length || x.length === 0) {
    throw new Error('Arrays must have same length and non-empty');
  }

  const n = x.length;
  const sumX = sum(x);
  const sumY = sum(y);
  const sumXY = x.reduce((acc, val, idx) => acc + val * y[idx], 0);
  const sumX2 = x.reduce((acc, val) => acc + val * val, 0);
  const sumY2 = y.reduce((acc, val) => acc + val * val, 0);

  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

  return denominator === 0 ? 0 : numerator / denominator;
}

/**
 * 批量计算相关系数矩阵（限制变量数量）
 * 复杂度: O(m²*n)，m=变量数，n=样本数
 * 限制: m < 20（否则可能超时）
 */
export function correlationMatrix(
  data: Record<string, number[]>
): Record<string, Record<string, number>> {
  const variables = Object.keys(data);
  
  if (variables.length > 20) {
    throw new Error('Too many variables. Limit is 20 for performance.');
  }

  const matrix: Record<string, Record<string, number>> = {};

  for (let i = 0; i < variables.length; i++) {
    matrix[variables[i]] = {};
    
    for (let j = 0; j < variables.length; j++) {
      if (i === j) {
        matrix[variables[i]][variables[j]] = 1;
      } else {
        matrix[variables[i]][variables[j]] = pearsonCorrelation(
          data[variables[i]],
          data[variables[j]]
        );
      }
    }
  }

  return matrix;
}
```

---

## 📊 使用示例

### 示例1: 使用线性回归预测OKR达成概率

```typescript
// 训练数据
const trainingData = [
  { historicalSuccessRate: 0.8, timeSpan: 90, complexity: 0.5 },
  { historicalSuccessRate: 0.6, timeSpan: 120, complexity: 0.7 },
  // ... 更多数据
];

const labels = [0.85, 0.65, /* ... */];

// 训练模型
const model = trainLinearRegression(trainingData, labels);

// 预测新OKR
const newOKR = {
  historicalSuccessRate: 0.7,
  timeSpan: 100,
  complexity: 0.6
};

const prediction = predictLinearRegression(model, newOKR);
console.log(`OKR达成概率: ${(prediction * 100).toFixed(2)}%`);
```

### 示例2: 使用移动平均预测趋势

```typescript
// 历史数据
const monthlyMetrics = [100, 105, 110, 108, 115, 120, 118];

// 计算移动平均
const ma7 = simpleMovingAverage(monthlyMetrics, 7);
console.log('移动平均:', ma7);

// 预测下一个月
const nextMonth = linearTrend(monthlyMetrics, 1);
console.log('下月预测:', nextMonth);
```

### 示例3: 使用加权评分分析需求优先级

```typescript
const requirements = [
  { importance: 0.8, urgency: 0.6, impact: 0.7 },
  { importance: 0.6, urgency: 0.8, impact: 0.5 },
  // ... 更多需求
];

const config: WeightedScoreConfig = {
  fields: ['importance', 'urgency', 'impact'],
  weights: [0.4, 0.3, 0.3],
  normalization: 'min-max'
};

const scored = weightedScoring(requirements, config);
console.log('优先级排序:', scored);
```

---

## ⚠️ 性能优化建议

### 1. 大数据集分批处理

```typescript
async function processLargeDataset<T>(
  data: T[],
  processor: (batch: T[]) => Promise<any>,
  batchSize: number = 1000
): Promise<any[]> {
  const results: any[] = [];
  
  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize);
    const batchResult = await processor(batch);
    results.push(...batchResult);
    
    // 检查执行时间
    if (Date.now() - startTime > 9000) {
      throw new Error('Execution timeout');
    }
  }
  
  return results;
}
```

### 2. 限制变量数量

```typescript
// 相关系数矩阵计算（限制变量数量）
if (variables.length > 20) {
  throw new Error('Too many variables. Please reduce to 20 or less.');
}
```

### 3. 缓存计算结果

```typescript
// 使用Map缓存
const cache = new Map<string, number>();

function cachedCalculation(key: string, calculator: () => number): number {
  if (cache.has(key)) {
    return cache.get(key)!;
  }
  
  const result = calculator();
  cache.set(key, result);
  return result;
}
```

---

## 📚 相关文档

- [Python到TypeScript迁移计划](../PYTHON_TO_TYPESCRIPT_MIGRATION_PLAN.md)
- [Edge Functions设计规范](../../COLLABORATIVE_DEVELOPMENT_FRAMEWORK.md)
- [API端点设计模板](../api/EDGE_FUNCTIONS_API_TEMPLATE.md)（待创建）

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23

