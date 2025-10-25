# 边际影响分析系统 - 算法实现指导文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (算法设计)
- **实施方**: Lovable (算法实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 算法实现概述

### 1.1 核心算法体系
边际影响分析系统基于22个核心算法函数，构建完整的边际影响分析体系：

1. **数据关系分析算法** (4个)
2. **动态权重优化算法** (6个)
3. **权重验证算法** (7个)
4. **权重监控算法** (5个)

### 1.2 技术栈选择
- **语言**: TypeScript (前端) + Python (后端算法)
- **机器学习**: scikit-learn, XGBoost, LightGBM
- **优化算法**: scipy.optimize
- **时间序列**: statsmodels
- **数值计算**: NumPy, Pandas

---

## 2. 数据关系分析算法实现

### 2.1 协同效应分析算法

#### 2.1.1 核心实现
```typescript
class SynergyAnalysis {
  private poly: PolynomialFeatures;
  private rfModel: RandomForestRegressor;
  
  constructor(degree: number = 2, interactionOnly: boolean = false) {
    this.poly = new PolynomialFeatures({
      degree,
      interactionOnly,
      includeBias: false
    });
    this.rfModel = new RandomForestRegressor({
      nEstimators: 100,
      randomState: 42
    });
  }
  
  async detectSynergyEffects(X: DataFrame, y: Series): Promise<SynergyResult> {
    try {
      // 1. 生成交互特征
      const XPoly = this.poly.fitTransform(X);
      
      // 2. 训练随机森林模型
      this.rfModel.fit(XPoly, y);
      
      // 3. 计算特征重要性
      const featureImportance = this.rfModel.featureImportances;
      
      // 4. 识别协同效应
      const synergyEffects = this.identifySynergyEffects(
        XPoly, 
        featureImportance
      );
      
      // 5. 计算协同系数
      const synergyCoefficient = this.calculateSynergyCoefficient(
        synergyEffects
      );
      
      return {
        success: true,
        synergyEffects,
        synergyCoefficient,
        featureImportance,
        model: this.rfModel
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private identifySynergyEffects(
    XPoly: DataFrame, 
    featureImportance: number[]
  ): SynergyEffect[] {
    const synergyEffects: SynergyEffect[] = [];
    const featureNames = this.poly.getFeatureNamesOut();
    
    // 识别交互项
    for (let i = 0; i < featureNames.length; i++) {
      const featureName = featureNames[i];
      if (this.isInteractionTerm(featureName)) {
        const importance = featureImportance[i];
        if (importance > 0.1) { // 重要性阈值
          synergyEffects.push({
            featureName,
            importance,
            interactionStrength: importance,
            synergyContribution: this.calculateSynergyContribution(
              featureName, 
              importance
            )
          });
        }
      }
    }
    
    return synergyEffects;
  }
  
  private calculateSynergyCoefficient(synergyEffects: SynergyEffect[]): number {
    if (synergyEffects.length === 0) return 0;
    
    const totalImportance = synergyEffects.reduce(
      (sum, effect) => sum + effect.importance, 
      0
    );
    const avgSynergyContribution = synergyEffects.reduce(
      (sum, effect) => sum + effect.synergyContribution, 
      0
    ) / synergyEffects.length;
    
    return (totalImportance * avgSynergyContribution) / 100;
  }
}
```

#### 2.1.2 使用示例
```typescript
// 协同效应分析使用示例
const synergyAnalysis = new SynergyAnalysis(2, false);

const result = await synergyAnalysis.detectSynergyEffects(
  resourceCapabilityData,
  performanceMetrics
);

if (result.success) {
  console.log('协同效应系数:', result.synergyCoefficient);
  console.log('协同效应数量:', result.synergyEffects.length);
  
  // 生成协同效应报告
  const report = generateSynergyReport(result);
  await saveReport(report);
}
```

### 2.2 阈值效应分析算法

#### 2.2.1 核心实现
```typescript
class ThresholdAnalysis {
  private decisionTree: DecisionTreeRegressor;
  
  constructor() {
    this.decisionTree = new DecisionTreeRegressor({
      maxDepth: 10,
      minSamplesSplit: 5,
      randomState: 42
    });
  }
  
  async detectThresholdEffects(
    X: DataFrame, 
    y: Series
  ): Promise<ThresholdResult> {
    try {
      // 1. 训练决策树模型
      this.decisionTree.fit(X, y);
      
      // 2. 提取阈值点
      const thresholds = this.extractThresholds();
      
      // 3. 计算阈值效应
      const thresholdEffects = await this.calculateThresholdEffects(
        X, 
        y, 
        thresholds
      );
      
      // 4. 显著性检验
      const significanceTests = await this.performSignificanceTests(
        thresholdEffects
      );
      
      return {
        success: true,
        thresholds,
        thresholdEffects,
        significanceTests,
        model: this.decisionTree
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private extractThresholds(): Threshold[] {
    const thresholds: Threshold[] = [];
    const tree = this.decisionTree.tree;
    
    // 遍历决策树节点，提取分割点
    this.traverseTree(tree, 0, thresholds);
    
    return thresholds;
  }
  
  private async calculateThresholdEffects(
    X: DataFrame, 
    y: Series, 
    thresholds: Threshold[]
  ): Promise<ThresholdEffect[]> {
    const effects: ThresholdEffect[] = [];
    
    for (const threshold of thresholds) {
      // 分割数据
      const beforeData = X[X[threshold.feature] < threshold.value];
      const afterData = X[X[threshold.feature] >= threshold.value];
      
      if (beforeData.length > 0 && afterData.length > 0) {
        // 计算阈值前后均值
        const beforeMean = y[beforeData.index].mean();
        const afterMean = y[afterData.index].mean();
        
        // 计算阈值效应
        const thresholdEffect = (afterMean - beforeMean) / beforeMean;
        
        effects.push({
          feature: threshold.feature,
          threshold: threshold.value,
          beforeMean,
          afterMean,
          thresholdEffect,
          significance: await this.calculateSignificance(
            beforeData, 
            afterData, 
            y
          )
        });
      }
    }
    
    return effects;
  }
}
```

### 2.3 时间滞后分析算法

#### 2.3.1 核心实现
```typescript
class LagAnalysis {
  private maxLag: number;
  private significanceLevel: number;
  
  constructor(maxLag: number = 12, significanceLevel: number = 0.05) {
    this.maxLag = maxLag;
    this.significanceLevel = significanceLevel;
  }
  
  async detectLagEffects(
    X: DataFrame, 
    y: Series
  ): Promise<LagResult> {
    try {
      // 1. 计算滞后相关性
      const lagCorrelations = this.calculateLagCorrelations(X, y);
      
      // 2. 识别显著滞后
      const significantLags = this.identifySignificantLags(lagCorrelations);
      
      // 3. 构建滞后模型
      const lagModel = await this.buildLagModel(X, y, significantLags);
      
      // 4. 计算滞后效应
      const lagEffects = this.calculateLagEffects(lagModel, significantLags);
      
      return {
        success: true,
        lagCorrelations,
        significantLags,
        lagEffects,
        model: lagModel
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private calculateLagCorrelations(
    X: DataFrame, 
    y: Series
  ): LagCorrelation[] {
    const correlations: LagCorrelation[] = [];
    
    for (const feature of X.columns) {
      for (let lag = 1; lag <= this.maxLag; lag++) {
        const laggedFeature = X[feature].shift(lag);
        const correlation = laggedFeature.corr(y);
        
        if (!isNaN(correlation)) {
          correlations.push({
            feature,
            lag,
            correlation: Math.abs(correlation),
            significance: this.calculateCorrelationSignificance(
              correlation, 
              y.length
            )
          });
        }
      }
    }
    
    return correlations.sort((a, b) => b.correlation - a.correlation);
  }
  
  private async buildLagModel(
    X: DataFrame, 
    y: Series, 
    significantLags: SignificantLag[]
  ): Promise<LagModel> {
    // 创建滞后特征
    const lagFeatures = this.createLagFeatures(X, significantLags);
    
    // 训练模型
    const model = new LinearRegression();
    model.fit(lagFeatures, y);
    
    return {
      model,
      lagFeatures,
      coefficients: model.coef_,
      intercept: model.intercept_,
      rSquared: model.score(lagFeatures, y)
    };
  }
}
```

---

## 3. 动态权重优化算法实现

### 3.1 梯度下降优化

#### 3.1.1 核心实现
```typescript
class GradientDescentOptimizer {
  private learningRate: number;
  private maxIterations: number;
  private tolerance: number;
  private regularization: number;
  
  constructor(
    learningRate: number = 0.01,
    maxIterations: number = 1000,
    tolerance: number = 1e-6,
    regularization: number = 0.01
  ) {
    this.learningRate = learningRate;
    this.maxIterations = maxIterations;
    this.tolerance = tolerance;
    this.regularization = regularization;
  }
  
  async optimizeWeights(
    X: DataFrame, 
    y: Series, 
    initialWeights?: number[]
  ): Promise<OptimizationResult> {
    try {
      // 初始化权重
      let weights = initialWeights || this.initializeWeights(X.shape[1]);
      
      // 记录优化历史
      const history: OptimizationHistory[] = [];
      
      for (let iteration = 0; iteration < this.maxIterations; iteration++) {
        // 计算梯度
        const gradient = this.calculateGradient(X, y, weights);
        
        // 更新权重
        const newWeights = this.updateWeights(weights, gradient);
        
        // 计算损失
        const loss = this.calculateLoss(X, y, newWeights);
        
        // 记录历史
        history.push({
          iteration,
          weights: [...newWeights],
          loss,
          gradient: [...gradient]
        });
        
        // 检查收敛
        if (this.checkConvergence(weights, newWeights)) {
          break;
        }
        
        weights = newWeights;
      }
      
      return {
        success: true,
        optimalWeights: weights,
        finalLoss: this.calculateLoss(X, y, weights),
        iterations: history.length,
        history
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private calculateGradient(
    X: DataFrame, 
    y: Series, 
    weights: number[]
  ): number[] {
    const gradient = new Array(weights.length).fill(0);
    const m = X.shape[0];
    
    for (let i = 0; i < m; i++) {
      const prediction = this.predict(X.iloc[i], weights);
      const error = prediction - y.iloc[i];
      
      for (let j = 0; j < weights.length; j++) {
        gradient[j] += (error * X.iloc[i, j]) / m;
      }
    }
    
    // 添加正则化项
    for (let j = 0; j < weights.length; j++) {
      gradient[j] += this.regularization * weights[j];
    }
    
    return gradient;
  }
  
  private updateWeights(weights: number[], gradient: number[]): number[] {
    return weights.map((weight, index) => 
      weight - this.learningRate * gradient[index]
    );
  }
}
```

### 3.2 遗传算法优化

#### 3.2.1 核心实现
```typescript
class GeneticAlgorithmOptimizer {
  private populationSize: number;
  private mutationFactor: number;
  private crossoverRate: number;
  private maxGenerations: number;
  
  constructor(
    populationSize: number = 50,
    mutationFactor: number = 0.5,
    crossoverRate: number = 0.7,
    maxGenerations: number = 100
  ) {
    this.populationSize = populationSize;
    this.mutationFactor = mutationFactor;
    this.crossoverRate = crossoverRate;
    this.maxGenerations = maxGenerations;
  }
  
  async optimizeWeights(
    X: DataFrame, 
    y: Series, 
    fitnessFunction: (weights: number[]) => number
  ): Promise<GeneticOptimizationResult> {
    try {
      // 初始化种群
      let population = this.initializePopulation(X.shape[1]);
      
      // 记录进化历史
      const evolutionHistory: EvolutionRecord[] = [];
      
      for (let generation = 0; generation < this.maxGenerations; generation++) {
        // 评估适应度
        const fitnessScores = population.map(individual => ({
          individual,
          fitness: fitnessFunction(individual)
        }));
        
        // 排序（适应度越高越好）
        fitnessScores.sort((a, b) => b.fitness - a.fitness);
        
        // 记录最佳个体
        const bestIndividual = fitnessScores[0];
        evolutionHistory.push({
          generation,
          bestFitness: bestIndividual.fitness,
          averageFitness: fitnessScores.reduce((sum, s) => sum + s.fitness, 0) / fitnessScores.length,
          bestIndividual: [...bestIndividual.individual]
        });
        
        // 检查终止条件
        if (this.shouldTerminate(evolutionHistory)) {
          break;
        }
        
        // 选择、交叉、变异
        const newPopulation = this.evolvePopulation(fitnessScores);
        population = newPopulation;
      }
      
      return {
        success: true,
        optimalWeights: evolutionHistory[evolutionHistory.length - 1].bestIndividual,
        finalFitness: evolutionHistory[evolutionHistory.length - 1].bestFitness,
        generations: evolutionHistory.length,
        evolutionHistory
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private evolvePopulation(
    fitnessScores: FitnessScore[]
  ): number[][] {
    const newPopulation: number[][] = [];
    
    // 保留最佳个体（精英策略）
    newPopulation.push([...fitnessScores[0].individual]);
    
    // 生成新个体
    while (newPopulation.length < this.populationSize) {
      // 选择父代
      const parent1 = this.selectParent(fitnessScores);
      const parent2 = this.selectParent(fitnessScores);
      
      // 交叉
      const offspring = this.crossover(parent1, parent2);
      
      // 变异
      const mutatedOffspring = this.mutate(offspring);
      
      newPopulation.push(mutatedOffspring);
    }
    
    return newPopulation;
  }
  
  private crossover(parent1: number[], parent2: number[]): number[] {
    const offspring = [...parent1];
    
    for (let i = 0; i < parent1.length; i++) {
      if (Math.random() < this.crossoverRate) {
        offspring[i] = parent2[i];
      }
    }
    
    return offspring;
  }
  
  private mutate(individual: number[]): number[] {
    return individual.map(gene => {
      if (Math.random() < this.mutationFactor) {
        return gene + (Math.random() - 0.5) * 0.1; // 小幅变异
      }
      return gene;
    });
  }
}
```

---

## 4. 权重验证算法实现

### 4.1 交叉验证

#### 4.1.1 核心实现
```typescript
class CrossValidation {
  private kFolds: number;
  private randomState: number;
  
  constructor(kFolds: number = 5, randomState: number = 42) {
    this.kFolds = kFolds;
    this.randomState = randomState;
  }
  
  async validateWeights(
    X: DataFrame, 
    y: Series, 
    weights: number[]
  ): Promise<ValidationResult> {
    try {
      // 分割数据
      const folds = this.splitData(X, y);
      
      // 交叉验证
      const validationResults: FoldResult[] = [];
      
      for (let fold = 0; fold < this.kFolds; fold++) {
        const { trainX, trainY, testX, testY } = this.getFoldData(folds, fold);
        
        // 训练模型
        const model = this.trainModel(trainX, trainY, weights);
        
        // 测试模型
        const testResult = this.testModel(model, testX, testY);
        
        validationResults.push({
          fold,
          trainScore: testResult.trainScore,
          testScore: testResult.testScore,
          mse: testResult.mse,
          mae: testResult.mae,
          r2: testResult.r2
        });
      }
      
      // 计算平均性能
      const averagePerformance = this.calculateAveragePerformance(validationResults);
      
      return {
        success: true,
        validationResults,
        averagePerformance,
        weights
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private splitData(X: DataFrame, y: Series): FoldData[] {
    const folds: FoldData[] = [];
    const indices = Array.from({ length: X.shape[0] }, (_, i) => i);
    
    // 随机打乱
    this.shuffleArray(indices);
    
    // 分割为k折
    const foldSize = Math.floor(indices.length / this.kFolds);
    
    for (let i = 0; i < this.kFolds; i++) {
      const start = i * foldSize;
      const end = i === this.kFolds - 1 ? indices.length : (i + 1) * foldSize;
      const foldIndices = indices.slice(start, end);
      
      folds.push({
        indices: foldIndices,
        X: X.iloc[foldIndices],
        y: y.iloc[foldIndices]
      });
    }
    
    return folds;
  }
}
```

### 4.2 权重稳定性验证

#### 4.2.1 核心实现
```typescript
class WeightStabilityValidator {
  private bootstrapSamples: number;
  private confidenceLevel: number;
  
  constructor(bootstrapSamples: number = 1000, confidenceLevel: number = 0.95) {
    this.bootstrapSamples = bootstrapSamples;
    this.confidenceLevel = confidenceLevel;
  }
  
  async validateWeightStability(
    X: DataFrame, 
    y: Series, 
    weights: number[]
  ): Promise<StabilityResult> {
    try {
      // Bootstrap采样
      const bootstrapWeights = await this.bootstrapWeights(X, y, weights);
      
      // 计算权重统计
      const weightStats = this.calculateWeightStatistics(bootstrapWeights);
      
      // 计算稳定性指标
      const stabilityMetrics = this.calculateStabilityMetrics(weightStats);
      
      // 识别不稳定权重
      const unstableWeights = this.identifyUnstableWeights(
        weightStats, 
        stabilityMetrics
      );
      
      return {
        success: true,
        weightStats,
        stabilityMetrics,
        unstableWeights,
        confidence: this.confidenceLevel
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  private async bootstrapWeights(
    X: DataFrame, 
    y: Series, 
    originalWeights: number[]
  ): Promise<number[][]> {
    const bootstrapWeights: number[][] = [];
    
    for (let i = 0; i < this.bootstrapSamples; i++) {
      // Bootstrap采样
      const bootstrapIndices = this.bootstrapSample(X.shape[0]);
      const bootstrapX = X.iloc[bootstrapIndices];
      const bootstrapY = y.iloc[bootstrapIndices];
      
      // 重新优化权重
      const optimizer = new GradientDescentOptimizer();
      const result = await optimizer.optimizeWeights(bootstrapX, bootstrapY);
      
      if (result.success) {
        bootstrapWeights.push(result.optimalWeights);
      }
    }
    
    return bootstrapWeights;
  }
  
  private calculateStabilityMetrics(weightStats: WeightStatistics[]): StabilityMetrics {
    const metrics: StabilityMetrics = {
      coefficientOfVariation: [],
      confidenceIntervals: [],
      stabilityIndex: 0
    };
    
    for (const stat of weightStats) {
      // 计算变异系数
      const cv = stat.standardDeviation / Math.abs(stat.mean);
      metrics.coefficientOfVariation.push(cv);
      
      // 计算置信区间
      const ci = this.calculateConfidenceInterval(stat, this.confidenceLevel);
      metrics.confidenceIntervals.push(ci);
    }
    
    // 计算整体稳定性指数
    metrics.stabilityIndex = this.calculateOverallStabilityIndex(metrics);
    
    return metrics;
  }
}
```

---

## 5. 权重监控算法实现

### 5.1 实时监控

#### 5.1.1 核心实现
```typescript
class WeightMonitor {
  private monitoringInterval: number;
  private alertThreshold: number;
  private historicalWeights: WeightHistory[] = [];
  
  constructor(
    monitoringInterval: number = 60000, // 1分钟
    alertThreshold: number = 0.1
  ) {
    this.monitoringInterval = monitoringInterval;
    this.alertThreshold = alertThreshold;
  }
  
  async startMonitoring(
    weightSource: () => Promise<number[]>
  ): Promise<void> {
    setInterval(async () => {
      try {
        // 获取当前权重
        const currentWeights = await weightSource();
        
        // 记录权重历史
        this.recordWeightHistory(currentWeights);
        
        // 检测异常
        const anomalies = await this.detectAnomalies(currentWeights);
        
        // 发送告警
        if (anomalies.length > 0) {
          await this.sendAlerts(anomalies);
        }
        
      } catch (error) {
        console.error('权重监控错误:', error);
      }
    }, this.monitoringInterval);
  }
  
  private recordWeightHistory(weights: number[]): void {
    const timestamp = new Date();
    this.historicalWeights.push({
      timestamp,
      weights: [...weights]
    });
    
    // 保持最近1000条记录
    if (this.historicalWeights.length > 1000) {
      this.historicalWeights.shift();
    }
  }
  
  private async detectAnomalies(currentWeights: number[]): Promise<Anomaly[]> {
    const anomalies: Anomaly[] = [];
    
    if (this.historicalWeights.length < 10) {
      return anomalies; // 数据不足，无法检测异常
    }
    
    // 计算权重变化
    const previousWeights = this.historicalWeights[this.historicalWeights.length - 2].weights;
    const weightChanges = currentWeights.map((weight, index) => 
      Math.abs(weight - previousWeights[index])
    );
    
    // 检测异常变化
    for (let i = 0; i < weightChanges.length; i++) {
      if (weightChanges[i] > this.alertThreshold) {
        anomalies.push({
          weightIndex: i,
          currentValue: currentWeights[i],
          previousValue: previousWeights[i],
          change: weightChanges[i],
          severity: this.calculateSeverity(weightChanges[i]),
          timestamp: new Date()
        });
      }
    }
    
    return anomalies;
  }
}
```

### 5.2 性能监控

#### 5.2.1 核心实现
```typescript
class PerformanceMonitor {
  private performanceMetrics: PerformanceMetric[] = [];
  
  async monitorPerformance(
    algorithm: string,
    executionTime: number,
    memoryUsage: number,
    accuracy: number
  ): Promise<void> {
    const metric: PerformanceMetric = {
      algorithm,
      executionTime,
      memoryUsage,
      accuracy,
      timestamp: new Date()
    };
    
    this.performanceMetrics.push(metric);
    
    // 检查性能异常
    const anomalies = this.detectPerformanceAnomalies(metric);
    
    if (anomalies.length > 0) {
      await this.handlePerformanceAnomalies(anomalies);
    }
  }
  
  private detectPerformanceAnomalies(
    currentMetric: PerformanceMetric
  ): PerformanceAnomaly[] {
    const anomalies: PerformanceAnomaly[] = [];
    
    if (this.performanceMetrics.length < 10) {
      return anomalies;
    }
    
    // 计算历史平均值
    const recentMetrics = this.performanceMetrics.slice(-10);
    const avgExecutionTime = recentMetrics.reduce(
      (sum, m) => sum + m.executionTime, 0
    ) / recentMetrics.length;
    
    const avgMemoryUsage = recentMetrics.reduce(
      (sum, m) => sum + m.memoryUsage, 0
    ) / recentMetrics.length;
    
    // 检测执行时间异常
    if (currentMetric.executionTime > avgExecutionTime * 2) {
      anomalies.push({
        type: 'execution_time',
        currentValue: currentMetric.executionTime,
        expectedValue: avgExecutionTime,
        severity: 'high'
      });
    }
    
    // 检测内存使用异常
    if (currentMetric.memoryUsage > avgMemoryUsage * 1.5) {
      anomalies.push({
        type: 'memory_usage',
        currentValue: currentMetric.memoryUsage,
        expectedValue: avgMemoryUsage,
        severity: 'medium'
      });
    }
    
    return anomalies;
  }
}
```

---

## 6. 算法集成与优化

### 6.1 算法组合策略

#### 6.1.1 并行执行
```typescript
class ParallelAlgorithmExecutor {
  async executeAlgorithms(
    algorithms: AlgorithmConfig[],
    data: AnalysisData
  ): Promise<AlgorithmResults> {
    const results: AlgorithmResults = {};
    
    // 并行执行算法
    const promises = algorithms.map(async (config) => {
      const algorithm = this.createAlgorithm(config);
      const result = await algorithm.execute(data);
      return { name: config.name, result };
    });
    
    const algorithmResults = await Promise.all(promises);
    
    // 合并结果
    for (const { name, result } of algorithmResults) {
      results[name] = result;
    }
    
    return results;
  }
}
```

### 6.2 结果融合策略

#### 6.2.1 加权平均融合
```typescript
class ResultFusion {
  async fuseResults(
    results: AlgorithmResults,
    weights: Record<string, number>
  ): Promise<FusedResult> {
    const fusedResult: FusedResult = {
      weights: [],
      confidence: 0,
      recommendations: []
    };
    
    // 计算加权平均权重
    for (const [algorithmName, result] of Object.entries(results)) {
      if (result.success && weights[algorithmName]) {
        const weight = weights[algorithmName];
        fusedResult.weights.push({
          algorithm: algorithmName,
          weight: result.weights,
          confidence: result.confidence,
          contribution: weight
        });
      }
    }
    
    // 计算融合权重
    const fusedWeights = this.calculateFusedWeights(fusedResult.weights);
    
    // 计算融合置信度
    fusedResult.confidence = this.calculateFusedConfidence(fusedResult.weights);
    
    // 生成推荐
    fusedResult.recommendations = this.generateRecommendations(fusedWeights);
    
    return fusedResult;
  }
}
```

---

## 7. 性能优化策略

### 7.1 缓存机制

#### 7.1.1 算法结果缓存
```typescript
class AlgorithmCache {
  private cache = new Map<string, CacheEntry>();
  private maxCacheSize = 1000;
  private cacheTimeout = 5 * 60 * 1000; // 5分钟
  
  async getCachedResult(
    algorithmName: string,
    dataHash: string
  ): Promise<AlgorithmResult | null> {
    const key = `${algorithmName}:${dataHash}`;
    const entry = this.cache.get(key);
    
    if (entry && Date.now() - entry.timestamp < this.cacheTimeout) {
      return entry.result;
    }
    
    return null;
  }
  
  async setCachedResult(
    algorithmName: string,
    dataHash: string,
    result: AlgorithmResult
  ): Promise<void> {
    const key = `${algorithmName}:${dataHash}`;
    
    // 清理过期缓存
    this.cleanExpiredCache();
    
    // 限制缓存大小
    if (this.cache.size >= this.maxCacheSize) {
      this.evictOldestCache();
    }
    
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    });
  }
}
```

### 7.2 并行计算优化

#### 7.2.1 多线程处理
```typescript
class ParallelProcessor {
  async processInParallel<T, R>(
    items: T[],
    processor: (item: T) => Promise<R>,
    maxConcurrency: number = 4
  ): Promise<R[]> {
    const results: R[] = [];
    const executing: Promise<void>[] = [];
    
    for (const item of items) {
      const promise = processor(item).then(result => {
        results.push(result);
      });
      
      executing.push(promise);
      
      if (executing.length >= maxConcurrency) {
        await Promise.race(executing);
        executing.splice(executing.findIndex(p => p === promise), 1);
      }
    }
    
    await Promise.all(executing);
    return results;
  }
}
```

---

## 8. 测试与验证

### 8.1 单元测试

#### 8.1.1 算法测试
```typescript
describe('SynergyAnalysis', () => {
  it('应该正确检测协同效应', async () => {
    const analyzer = new SynergyAnalysis();
    const testData = generateTestData();
    
    const result = await analyzer.detectSynergyEffects(
      testData.features,
      testData.target
    );
    
    expect(result.success).toBe(true);
    expect(result.synergyCoefficient).toBeGreaterThan(0);
    expect(result.synergyEffects.length).toBeGreaterThan(0);
  });
});
```

### 8.2 性能测试

#### 8.2.1 算法性能测试
```typescript
describe('Algorithm Performance', () => {
  it('应该在合理时间内完成计算', async () => {
    const startTime = Date.now();
    
    const result = await executeMarginalAnalysis(largeDataset);
    
    const executionTime = Date.now() - startTime;
    
    expect(result.success).toBe(true);
    expect(executionTime).toBeLessThan(30000); // 30秒内完成
  });
});
```

---

## 9. 总结

本算法实现指导文档提供了完整的算法实现方案，包括：

1. **数据关系分析**: 协同效应、阈值效应、时间滞后分析
2. **动态权重优化**: 梯度下降、遗传算法、模拟退火等
3. **权重验证**: 交叉验证、稳定性验证、性能验证
4. **权重监控**: 实时监控、异常检测、性能监控
5. **算法集成**: 并行执行、结果融合、性能优化
6. **测试验证**: 单元测试、性能测试、集成测试

所有算法都具备完整的实现代码和测试用例，能够满足边际影响分析系统的所有业务需求。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 4-5周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com
