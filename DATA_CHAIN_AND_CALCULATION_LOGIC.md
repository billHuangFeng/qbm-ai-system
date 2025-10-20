# BMOS系统数据链与计算逻辑梳理

## 🎯 系统概述

BMOS (Business Model Quantitative Optimization System) 基于《商业模式动态优化与决策管理综合方案》的6大模块，构建了完整的数据链和计算逻辑体系。

### 核心架构
- **数据层**: PostgreSQL (Supabase) + Next.js API Routes
- **计算层**: Shapley归因算法 + 价值链分析 + 决策管理
- **应用层**: React前端 + 实时可视化

---

## 📊 数据链架构

### 1. 数据流向图
```
原始数据源 → 数据采集 → 数据清洗 → 数据存储 → 计算分析 → 结果输出 → 决策应用
     ↓           ↓         ↓         ↓         ↓         ↓         ↓
  订单系统    数据连接器   数据验证   PostgreSQL  算法引擎   可视化    决策执行
  客户系统    数据同步     数据补全   Supabase    归因分析   报告生成   效果追踪
  财务系统    实时订阅     数据映射   数据仓库    优化建议   监控面板   反馈循环
```

### 2. 数据分层结构
```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                │
├─────────────────────────────────────────────────────────────┤
│  React前端界面  │  决策管理界面  │  可视化面板  │  监控仪表盘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    计算层 (Computation Layer)               │
├─────────────────────────────────────────────────────────────┤
│  Shapley归因算法 │  价值链分析引擎 │  优化建议生成 │  决策追踪引擎 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    数据层 (Data Layer)                      │
├─────────────────────────────────────────────────────────────┤
│  维度表 (9张)   │  事实表 (5张)   │  桥接表 (5张)  │  分析视图 (4张) │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    源数据层 (Source Layer)                  │
├─────────────────────────────────────────────────────────────┤
│  订单系统  │  客户系统  │  财务系统  │  营销系统  │  生产系统  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ 数据模型设计

### 1. 维度表 (11张)
```sql
-- 价值主张标签维度表
CREATE TABLE dim_vpt (
    vpt_id VARCHAR(50) PRIMARY KEY,
    vpt_name VARCHAR(100) NOT NULL,
    vpt_category VARCHAR(50),
    vpt_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品特性标签维度表
CREATE TABLE dim_pft (
    pft_id VARCHAR(50) PRIMARY KEY,
    pft_name VARCHAR(100) NOT NULL,
    pft_category VARCHAR(50),
    pft_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 核心资源标签维度表
CREATE TABLE dim_core_resource_tags (
    crt_id VARCHAR(50) PRIMARY KEY,
    crt_name VARCHAR(100) NOT NULL,
    crt_category VARCHAR(50) NOT NULL,
    crt_type VARCHAR(20) NOT NULL,
    crt_description TEXT,
    crt_value DECIMAL(15,2),
    crt_rarity VARCHAR(20),
    crt_control_level DECIMAL(3,2),
    crt_competitiveness DECIMAL(3,2),
    crt_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 核心能力标签维度表
CREATE TABLE dim_core_capability_tags (
    cct_id VARCHAR(50) PRIMARY KEY,
    cct_name VARCHAR(100) NOT NULL,
    cct_category VARCHAR(50) NOT NULL,
    cct_type VARCHAR(20) NOT NULL,
    cct_description TEXT,
    cct_maturity_level DECIMAL(3,2),
    cct_development_cost DECIMAL(15,2),
    cct_competitive_advantage DECIMAL(3,2),
    cct_transferability DECIMAL(3,2),
    cct_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 活动维度表
CREATE TABLE dim_activity (
    activity_id VARCHAR(50) PRIMARY KEY,
    activity_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50),
    activity_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 媒体渠道维度表
CREATE TABLE dim_media_channel (
    channel_id VARCHAR(50) PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50),
    channel_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 转化渠道维度表
CREATE TABLE dim_conv_channel (
    conv_channel_id VARCHAR(50) PRIMARY KEY,
    conv_channel_name VARCHAR(100) NOT NULL,
    conv_channel_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKU维度表
CREATE TABLE dim_sku (
    sku_id VARCHAR(50) PRIMARY KEY,
    sku_name VARCHAR(100) NOT NULL,
    sku_category VARCHAR(50),
    sku_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 客户维度表
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_segment VARCHAR(50),
    customer_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 日期维度表
CREATE TABLE dim_date (
    date_id VARCHAR(50) PRIMARY KEY,
    date_value DATE NOT NULL,
    year INT,
    month INT,
    quarter INT,
    week INT,
    day_of_week INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- 供应商维度表
CREATE TABLE dim_supplier (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    supplier_category VARCHAR(50),
    supplier_rating DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 事实表 (5张)
```sql
-- 订单事实表
CREATE TABLE fact_order (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    sku_id VARCHAR(50),
    order_date DATE,
    order_amount DECIMAL(10,2),
    order_quantity INT,
    channel_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (sku_id) REFERENCES dim_sku(sku_id),
    FOREIGN KEY (channel_id) REFERENCES dim_media_channel(channel_id)
);

-- 客户声音事实表
CREATE TABLE fact_voice (
    voice_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    vpt_id VARCHAR(50),
    voice_type VARCHAR(50),
    voice_content TEXT,
    sentiment_score DECIMAL(3,2),
    voice_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (vpt_id) REFERENCES dim_vpt(vpt_id)
);

-- 成本事实表
CREATE TABLE fact_cost (
    cost_id VARCHAR(50) PRIMARY KEY,
    activity_id VARCHAR(50),
    cost_type VARCHAR(50),
    cost_amount DECIMAL(10,2),
    cost_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES dim_activity(activity_id)
);

-- 供应商事实表
CREATE TABLE fact_supplier (
    supplier_record_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50),
    delivery_date DATE,
    delivery_quantity INT,
    delivery_quality_score DECIMAL(3,2),
    delivery_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES dim_supplier(supplier_id)
);

-- 生产事实表
CREATE TABLE fact_produce (
    produce_id VARCHAR(50) PRIMARY KEY,
    sku_id VARCHAR(50),
    production_date DATE,
    production_quantity INT,
    production_quality_score DECIMAL(3,2),
    production_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku_id) REFERENCES dim_sku(sku_id)
);
```

### 3. 桥接表 (7张)
```sql
-- 媒体渠道-价值主张桥接表
CREATE TABLE bridge_media_vpt (
    bridge_id VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50),
    vpt_id VARCHAR(50),
    association_strength DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES dim_media_channel(channel_id),
    FOREIGN KEY (vpt_id) REFERENCES dim_vpt(vpt_id)
);

-- 决策-核心资源关联表
CREATE TABLE bridge_decision_core_resources (
    bridge_id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) NOT NULL,
    crt_id VARCHAR(50) NOT NULL,
    resource_intent VARCHAR(100),
    control_target DECIMAL(3,2),
    current_control_level DECIMAL(3,2),
    investment_amount DECIMAL(15,2),
    expected_roi DECIMAL(5,4),
    priority_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES hierarchical_decisions(decision_id),
    FOREIGN KEY (crt_id) REFERENCES dim_core_resource_tags(crt_id)
);

-- 决策-核心能力关联表
CREATE TABLE bridge_decision_core_capabilities (
    bridge_id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) NOT NULL,
    cct_id VARCHAR(50) NOT NULL,
    capability_intent VARCHAR(100),
    development_target DECIMAL(3,2),
    current_maturity_level DECIMAL(3,2),
    development_investment DECIMAL(15,2),
    expected_advantage DECIMAL(3,2),
    priority_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES hierarchical_decisions(decision_id),
    FOREIGN KEY (cct_id) REFERENCES dim_core_capability_tags(cct_id)
);

-- 转化渠道-价值主张桥接表
CREATE TABLE bridge_conv_vpt (
    bridge_id VARCHAR(50) PRIMARY KEY,
    conv_channel_id VARCHAR(50),
    vpt_id VARCHAR(50),
    conversion_rate DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conv_channel_id) REFERENCES dim_conv_channel(conv_channel_id),
    FOREIGN KEY (vpt_id) REFERENCES dim_vpt(vpt_id)
);

-- SKU-产品特性桥接表
CREATE TABLE bridge_sku_pft (
    bridge_id VARCHAR(50) PRIMARY KEY,
    sku_id VARCHAR(50),
    pft_id VARCHAR(50),
    feature_strength DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku_id) REFERENCES dim_sku(sku_id),
    FOREIGN KEY (pft_id) REFERENCES dim_pft(pft_id)
);

-- 价值主张-产品特性桥接表
CREATE TABLE bridge_vpt_pft (
    bridge_id VARCHAR(50) PRIMARY KEY,
    vpt_id VARCHAR(50),
    pft_id VARCHAR(50),
    alignment_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vpt_id) REFERENCES dim_vpt(vpt_id),
    FOREIGN KEY (pft_id) REFERENCES dim_pft(pft_id)
);

-- 归因桥接表
CREATE TABLE bridge_attribution (
    attribution_id VARCHAR(50) PRIMARY KEY,
    channel_id VARCHAR(50),
    order_id VARCHAR(50),
    attribution_value DECIMAL(5,4),
    shapley_value DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES dim_media_channel(channel_id),
    FOREIGN KEY (order_id) REFERENCES fact_order(order_id)
);
```

---

## 🧮 核心计算逻辑

### 1. 价值链分析计算

#### 1.1 价值链效率计算
```typescript
// 价值链效率计算算法
interface ValueChainSegment {
  segmentName: string;
  inputVolume: number;
  outputVolume: number;
  processingTime: number;
  cost: number;
}

function calculateChainEfficiency(segment: ValueChainSegment): {
  efficiencyScore: number;
  conversionRate: number;
  bottleneckType: string;
  bottleneckImpact: number;
} {
  // 1. 计算效率分数
  const efficiencyScore = segment.outputVolume / (segment.inputVolume * segment.processingTime);
  
  // 2. 计算转化率
  const conversionRate = segment.outputVolume / segment.inputVolume;
  
  // 3. 识别瓶颈类型
  const bottleneckType = identifyBottleneck(segment);
  
  // 4. 计算瓶颈影响程度
  const bottleneckImpact = calculateBottleneckImpact(segment, bottleneckType);
  
  return {
    efficiencyScore: Math.min(efficiencyScore, 1.0), // 限制在0-1之间
    conversionRate: Math.min(conversionRate, 1.0),
    bottleneckType,
    bottleneckImpact
  };
}

function identifyBottleneck(segment: ValueChainSegment): string {
  const efficiencyThreshold = 0.8;
  const conversionThreshold = 0.85;
  
  if (segment.outputVolume / segment.inputVolume < conversionThreshold) {
    return 'conversion_bottleneck';
  } else if (segment.processingTime > segment.inputVolume * 0.1) {
    return 'processing_bottleneck';
  } else if (segment.cost / segment.outputVolume > 0.3) {
    return 'cost_bottleneck';
  } else {
    return 'no_bottleneck';
  }
}
```

#### 1.2 价值链各环节计算
```typescript
// 价值链各环节分析
class ValueChainAnalyzer {
  async analyzeValueChain(timeRange: { startDate: string; endDate: string }) {
    const segments = [
      'core_resources',      // 核心资源+能力
      'product_features',    // 产品特性
      'value_proposition',   // 价值主张
      'customer_perception', // 客户感知
      'experience_value',    // 体验价值
      'customer_purchase'    // 客户买单
    ];
    
    const analysisResults = {};
    
    for (const segment of segments) {
      const segmentData = await this.getSegmentData(segment, timeRange);
      const efficiency = calculateChainEfficiency(segmentData);
      
      analysisResults[segment] = {
        ...efficiency,
        metrics: await this.calculateSegmentMetrics(segment, timeRange)
      };
    }
    
    return {
      chainAnalysis: analysisResults,
      overallEfficiency: this.calculateOverallEfficiency(analysisResults),
      bottlenecks: this.identifyBottlenecks(analysisResults)
    };
  }
  
  private async getSegmentData(segment: string, timeRange: any) {
    // 根据环节类型获取相应数据
    switch (segment) {
      case 'core_resources':
        return await this.getSupplierAndProductionData(timeRange);
      case 'product_features':
        return await this.getProductFeatureData(timeRange);
      case 'value_proposition':
        return await this.getValuePropositionData(timeRange);
      case 'customer_perception':
        return await this.getCustomerPerceptionData(timeRange);
      case 'experience_value':
        return await this.getExperienceValueData(timeRange);
      case 'customer_purchase':
        return await this.getPurchaseData(timeRange);
    }
  }
}
```

### 2. Shapley归因算法

#### 2.1 Shapley值计算
```typescript
// Shapley归因算法实现
class ShapleyAttributionEngine {
  calculateShapleyAttribution(
    channels: string[],
    outcomes: Record<string, number>
  ): Record<string, number> {
    const n = channels.length;
    const shapleyValues: Record<string, number> = {};
    
    for (const channel of channels) {
      let shapleyValue = 0;
      
      // 计算所有可能的渠道组合
      const allSubsets = this.getAllSubsets(channels);
      
      for (const subset of allSubsets) {
        if (subset.includes(channel)) {
          // 计算包含该渠道的贡献
          const withChannel = this.calculateContribution(subset, outcomes);
          const withoutChannel = this.calculateContribution(
            subset.filter(c => c !== channel), 
            outcomes
          );
          
          // 计算权重
          const weight = 1 / (n * this.combination(n - 1, subset.length - 1));
          
          // 累加Shapley值
          shapleyValue += weight * (withChannel - withoutChannel);
        }
      }
      
      shapleyValues[channel] = shapleyValue;
    }
    
    return shapleyValues;
  }
  
  private getAllSubsets(channels: string[]): string[][] {
    const subsets: string[][] = [];
    const n = channels.length;
    
    // 生成所有可能的子集
    for (let i = 0; i < (1 << n); i++) {
      const subset: string[] = [];
      for (let j = 0; j < n; j++) {
        if (i & (1 << j)) {
          subset.push(channels[j]);
        }
      }
      if (subset.length > 0) {
        subsets.push(subset);
      }
    }
    
    return subsets;
  }
  
  private calculateContribution(subset: string[], outcomes: Record<string, number>): number {
    // 基于历史数据计算渠道组合的贡献
    let totalContribution = 0;
    
    for (const channel of subset) {
      totalContribution += outcomes[channel] || 0;
    }
    
    // 考虑渠道间的协同效应
    const synergyFactor = this.calculateSynergyFactor(subset);
    return totalContribution * synergyFactor;
  }
  
  private calculateSynergyFactor(subset: string[]): number {
    // 计算渠道间的协同效应
    if (subset.length <= 1) return 1.0;
    
    // 基于历史数据计算协同效应系数
    const synergyMatrix = this.getSynergyMatrix();
    let synergyFactor = 1.0;
    
    for (let i = 0; i < subset.length; i++) {
      for (let j = i + 1; j < subset.length; j++) {
        const synergy = synergyMatrix[subset[i]]?.[subset[j]] || 1.0;
        synergyFactor *= synergy;
      }
    }
    
    return synergyFactor;
  }
  
  private combination(n: number, k: number): number {
    if (k > n) return 0;
    if (k === 0 || k === n) return 1;
    
    let result = 1;
    for (let i = 0; i < k; i++) {
      result = result * (n - i) / (i + 1);
    }
    
    return result;
  }
}
```

#### 2.2 归因分析应用
```typescript
// 归因分析应用
class AttributionAnalyzer {
  async analyzeAttribution(request: {
    timeRange: { startDate: string; endDate: string };
    channels: string[];
    metrics: string[];
  }) {
    const { timeRange, channels, metrics } = request;
    
    // 1. 获取渠道数据
    const channelData = await this.getChannelData(channels, timeRange);
    
    // 2. 计算各指标的基础贡献
    const baseContributions = await this.calculateBaseContributions(channelData, metrics);
    
    // 3. 使用Shapley算法计算归因
    const shapleyEngine = new ShapleyAttributionEngine();
    const attributionResults = {};
    
    for (const metric of metrics) {
      const outcomes = baseContributions[metric];
      const shapleyValues = shapleyEngine.calculateShapleyAttribution(channels, outcomes);
      
      attributionResults[metric] = shapleyValues;
    }
    
    // 4. 计算置信度
    const confidenceScore = await this.calculateConfidenceScore(attributionResults);
    
    return {
      attributionResults,
      totalAttribution: 1.0,
      confidenceScore,
      analysisMetadata: {
        sampleSize: await this.getSampleSize(timeRange),
        analysisTime: new Date().toISOString(),
        algorithmVersion: 'shapley_v2.1'
      }
    };
  }
}
```

### 3. 优化建议生成

#### 3.1 优化建议算法
```typescript
// 优化建议生成引擎
class OptimizationSuggestionEngine {
  generateSuggestions(analysisResults: {
    chainAnalysis: any;
    attributionResults: any;
  }, optimizationGoals: string[], constraints: any) {
    const suggestions = [];
    
    // 1. 基于价值链分析的优化建议
    const chainSuggestions = this.generateChainOptimizationSuggestions(
      analysisResults.chainAnalysis
    );
    
    // 2. 基于归因分析的优化建议
    const attributionSuggestions = this.generateAttributionOptimizationSuggestions(
      analysisResults.attributionResults
    );
    
    // 3. 合并和排序建议
    const allSuggestions = [...chainSuggestions, ...attributionSuggestions];
    const prioritizedSuggestions = this.prioritizeSuggestions(
      allSuggestions, 
      optimizationGoals, 
      constraints
    );
    
    return {
      suggestions: prioritizedSuggestions,
      totalSuggestions: prioritizedSuggestions.length,
      estimatedROI: this.calculateEstimatedROI(prioritizedSuggestions),
      implementationPriority: prioritizedSuggestions.map(s => s.id)
    };
  }
  
  private generateChainOptimizationSuggestions(chainAnalysis: any) {
    const suggestions = [];
    
    for (const [segment, analysis] of Object.entries(chainAnalysis)) {
      if (analysis.efficiencyScore < 0.8) {
        suggestions.push({
          id: `opt_${segment}_001`,
          title: `优化${segment}效率`,
          description: `提升${segment}环节的效率，当前效率为${analysis.efficiencyScore}`,
          targetSegment: segment,
          priority: analysis.efficiencyScore < 0.6 ? 'high' : 'medium',
          expectedImpact: {
            efficiencyImprovement: 0.15,
            conversionImprovement: 0.12,
            revenueImprovement: 0.08
          },
          implementation: {
            effort: 'medium',
            cost: this.estimateCost(segment, 'efficiency'),
            timeline: '2_weeks',
            resources: this.getRequiredResources(segment)
          },
          successMetrics: [
            'efficiency_score',
            'conversion_rate',
            'bottleneck_impact'
          ]
        });
      }
    }
    
    return suggestions;
  }
  
  private prioritizeSuggestions(
    suggestions: any[], 
    goals: string[], 
    constraints: any
  ) {
    return suggestions
      .map(suggestion => ({
        ...suggestion,
        priorityScore: this.calculatePriorityScore(suggestion, goals, constraints)
      }))
      .sort((a, b) => b.priorityScore - a.priorityScore);
  }
  
  private calculatePriorityScore(suggestion: any, goals: string[], constraints: any): number {
    let score = 0;
    
    // 基于目标权重
    for (const goal of goals) {
      if (suggestion.expectedImpact[goal]) {
        score += suggestion.expectedImpact[goal] * this.getGoalWeight(goal);
      }
    }
    
    // 基于成本约束
    if (suggestion.implementation.cost <= constraints.budgetLimit) {
      score += 0.2;
    }
    
    // 基于时间约束
    if (this.isWithinTimeLimit(suggestion.implementation.timeline, constraints.timeLimit)) {
      score += 0.1;
    }
    
    return score;
  }
}
```

### 4. 决策管理计算

#### 4.1 层级决策管理
```typescript
// 层级决策管理系统
class HierarchicalDecisionManager {
  createDecision(decisionData: {
    level: 'strategic' | 'tactical' | 'operational';
    segment: string;
    intent: string;
    target: string;
    parentDecisionId?: string;
  }) {
    const decisionId = this.generateDecisionId(decisionData.level, decisionData.segment);
    
    const decision = {
      decisionId,
      decisionLevel: decisionData.level,
      parentDecisionId: decisionData.parentDecisionId,
      chainSegment: decisionData.segment,
      intent: decisionData.intent,
      quantitativeTarget: decisionData.target,
      relatedChain: this.getChainFlow(decisionData.segment),
      bmosTables: this.getBmosTables(decisionData.segment),
      decomposedDecisions: [],
      executionActions: [],
      createdAt: new Date(),
      status: 'active'
    };
    
    // 存储到数据库
    this.storeDecision(decision);
    
    return decisionId;
  }
  
  decomposeDecision(parentDecisionId: string, decompositionStrategy: string) {
    const parentDecision = this.getDecision(parentDecisionId);
    const decomposedDecisions = [];
    
    if (parentDecision.decisionLevel === 'strategic') {
      // 战略层分解为战术层
      decomposedDecisions.push(...this.decomposeToTactical(parentDecision, decompositionStrategy));
    } else if (parentDecision.decisionLevel === 'tactical') {
      // 战术层分解为执行层
      decomposedDecisions.push(...this.decomposeToOperational(parentDecision, decompositionStrategy));
    }
    
    return decomposedDecisions;
  }
  
  private decomposeToTactical(strategicDecision: any, strategy: string) {
    const tacticalDecisions = [];
    const departments = this.getDepartmentsBySegment(strategicDecision.chainSegment);
    
    for (const department of departments) {
      const tacticalDecision = {
        decisionId: this.generateDecisionId('tactical', department),
        decisionLevel: 'tactical',
        parentDecisionId: strategicDecision.decisionId,
        chainSegment: department,
        intent: `实现${strategicDecision.intent}的${department}策略`,
        quantitativeTarget: this.decomposeTarget(strategicDecision.quantitativeTarget, department),
        relatedChain: strategicDecision.relatedChain,
        bmosTables: this.getBmosTables(department),
        createdAt: new Date(),
        status: 'active'
      };
      
      tacticalDecisions.push(tacticalDecision);
      this.storeDecision(tacticalDecision);
    }
    
    return tacticalDecisions;
  }
}
```

#### 4.2 决策效果追踪
```typescript
// 决策效果追踪引擎
class DecisionTrackingEngine {
  async trackDecisionEffect(decisionId: string) {
    const decision = await this.getDecision(decisionId);
    const timeRange = this.getTrackingTimeRange(decision);
    
    // 1. 获取决策执行数据
    const executionData = await this.getExecutionData(decisionId, timeRange);
    
    // 2. 计算直接效果
    const directEffect = await this.calculateDirectEffect(decision, executionData);
    
    // 3. 计算间接效果
    const indirectEffect = await this.calculateIndirectEffect(decision, executionData);
    
    // 4. 计算总体效果
    const totalEffect = {
      direct: directEffect,
      indirect: indirectEffect,
      total: directEffect + indirectEffect
    };
    
    // 5. 生成追踪报告
    const trackingReport = {
      decisionId,
      timeRange,
      effects: totalEffect,
      metrics: await this.calculateTrackingMetrics(decision, executionData),
      recommendations: await this.generateTrackingRecommendations(decision, totalEffect)
    };
    
    return trackingReport;
  }
  
  private async calculateDirectEffect(decision: any, executionData: any) {
    // 计算决策的直接效果
    const targetMetric = decision.quantitativeTarget;
    const actualValue = executionData.actualValue;
    const expectedValue = executionData.expectedValue;
    
    const directEffect = (actualValue - expectedValue) / expectedValue;
    
    return directEffect;
  }
  
  private async calculateIndirectEffect(decision: any, executionData: any) {
    // 计算决策的间接效果
    const relatedDecisions = await this.getRelatedDecisions(decision.decisionId);
    let indirectEffect = 0;
    
    for (const relatedDecision of relatedDecisions) {
      const relatedEffect = await this.calculateDirectEffect(relatedDecision, executionData);
      indirectEffect += relatedEffect * this.getInfluenceWeight(decision, relatedDecision);
    }
    
    return indirectEffect;
  }
}
```

---

## 🔄 数据流转过程

### 1. 数据采集流程
```typescript
// 数据采集流程
class DataCollectionFlow {
  async collectData(timeRange: { startDate: string; endDate: string }) {
    // 1. 从各系统采集原始数据
    const rawData = await this.collectRawData(timeRange);
    
    // 2. 数据清洗和验证
    const cleanedData = await this.cleanData(rawData);
    
    // 3. 数据转换和映射
    const transformedData = await this.transformData(cleanedData);
    
    // 4. 存储到数据库
    await this.storeData(transformedData);
    
    // 5. 触发计算任务
    await this.triggerCalculationTasks(transformedData);
    
    return transformedData;
  }
  
  private async collectRawData(timeRange: any) {
    const dataSources = [
      'order_system',
      'customer_system', 
      'financial_system',
      'marketing_system',
      'production_system'
    ];
    
    const rawData = {};
    
    for (const source of dataSources) {
      rawData[source] = await this.collectFromSource(source, timeRange);
    }
    
    return rawData;
  }
}
```

### 2. 计算任务流程
```typescript
// 计算任务流程
class CalculationTaskFlow {
  async executeCalculationTasks(data: any) {
    const tasks = [
      'value_chain_analysis',
      'attribution_analysis',
      'optimization_suggestions',
      'decision_tracking'
    ];
    
    const results = {};
    
    for (const task of tasks) {
      try {
        results[task] = await this.executeTask(task, data);
      } catch (error) {
        console.error(`Task ${task} failed:`, error);
        results[task] = { error: error.message };
      }
    }
    
    return results;
  }
  
  private async executeTask(taskName: string, data: any) {
    switch (taskName) {
      case 'value_chain_analysis':
        const analyzer = new ValueChainAnalyzer();
        return await analyzer.analyzeValueChain(data.timeRange);
        
      case 'attribution_analysis':
        const attributionEngine = new AttributionAnalyzer();
        return await attributionEngine.analyzeAttribution(data.attributionRequest);
        
      case 'optimization_suggestions':
        const suggestionEngine = new OptimizationSuggestionEngine();
        return await suggestionEngine.generateSuggestions(
          data.analysisResults,
          data.optimizationGoals,
          data.constraints
        );
        
      case 'decision_tracking':
        const trackingEngine = new DecisionTrackingEngine();
        return await trackingEngine.trackDecisionEffect(data.decisionId);
    }
  }
}
```

---

## 📈 性能优化策略

### 1. 数据查询优化
```sql
-- 创建索引优化查询性能
CREATE INDEX idx_fact_order_date ON fact_order(order_date);
CREATE INDEX idx_fact_order_customer ON fact_order(customer_id);
CREATE INDEX idx_fact_order_sku ON fact_order(sku_id);
CREATE INDEX idx_bridge_attribution_channel ON bridge_attribution(channel_id);
CREATE INDEX idx_bridge_attribution_order ON bridge_attribution(order_id);

-- 创建复合索引
CREATE INDEX idx_fact_order_composite ON fact_order(order_date, customer_id, sku_id);
```

### 2. 计算缓存策略
```typescript
// 计算结果缓存
class CalculationCache {
  private cache = new Map();
  
  async getCachedResult(key: string, calculator: () => Promise<any>) {
    if (this.cache.has(key)) {
      const cached = this.cache.get(key);
      if (this.isCacheValid(cached)) {
        return cached.result;
      }
    }
    
    const result = await calculator();
    this.cache.set(key, {
      result,
      timestamp: Date.now(),
      ttl: 3600000 // 1小时
    });
    
    return result;
  }
  
  private isCacheValid(cached: any): boolean {
    return Date.now() - cached.timestamp < cached.ttl;
  }
}
```

### 3. 实时数据更新
```typescript
// 实时数据更新
class RealTimeDataUpdater {
  constructor() {
    this.setupSupabaseRealtime();
  }
  
  private setupSupabaseRealtime() {
    // 监听订单数据变化
    supabase
      .channel('order_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'fact_order' },
        (payload) => this.handleOrderChange(payload)
      )
      .subscribe();
    
    // 监听客户数据变化
    supabase
      .channel('customer_changes')
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'dim_customer' },
        (payload) => this.handleCustomerChange(payload)
      )
      .subscribe();
  }
  
  private async handleOrderChange(payload: any) {
    // 触发相关计算任务
    await this.triggerAttributionRecalculation(payload.new);
    await this.triggerValueChainRecalculation(payload.new);
  }
}
```

---

## 🎯 总结

### 数据链特点
1. **完整性**: 覆盖从数据采集到决策应用的全链路
2. **实时性**: 支持实时数据更新和计算
3. **可追溯性**: 每个计算结果都可以追溯到原始数据
4. **可扩展性**: 支持新数据源和计算逻辑的扩展

### 计算逻辑特点
1. **科学性**: 基于Shapley算法等科学方法
2. **准确性**: 高精度的数值计算和归因分析
3. **实用性**: 生成可操作的优化建议
4. **智能化**: 自动化的决策管理和效果追踪

### 系统优势
1. **理论指导**: 基于完整的商业模式理论框架
2. **技术先进**: 使用最新的数据分析和机器学习技术
3. **协同开发**: 支持Cursor和Lovable的协同开发
4. **部署简单**: Next.js全栈架构，Vercel一键部署

---

**这个数据链和计算逻辑体系为BMOS系统提供了完整的技术支撑，确保系统能够准确、高效地实现商业模式动态优化！** 🎉
