# 三类价值评估方法设计

## 📋 算法概述

基于用户澄清，三类价值评估通过**嵌入式调研页面**收集数据，系统提供计算功能。算法实现内在价值、认知价值、体验价值的量化评估，支持加权得分和评估项明细。

## 🎯 用户说明指引

### 什么是三类价值评估？
三类价值评估是评估产品价值的综合方法，包括：
- **内在价值**：产品本身的功能、性能、质量等价值
- **认知价值**：客户对产品价值的认知和感知
- **体验价值**：客户使用产品时的体验和感受

### 为什么需要三类价值评估？
- **全面价值评估**：从多个维度评估产品价值
- **客户价值理解**：了解客户对产品价值的真实感受
- **产品优化指导**：为产品改进提供数据支持

### 评估方法说明
1. **内在价值评估**：通过产品测试、功能分析等方式评估
2. **认知价值评估**：通过客户调研、市场研究等方式评估
3. **体验价值评估**：通过用户体验测试、满意度调研等方式评估

### 数据收集方式
- **嵌入式调研页面**：可嵌入到其他系统或独立使用
- **实时数据同步**：调研数据立即同步到主系统
- **多维度评估**：支持覆盖率、满意度、回忆率等多个维度

### 使用场景
- **产品价值评估**：全面评估产品价值
- **客户价值分析**：了解客户对产品的真实感受
- **产品优化指导**：为产品改进提供数据支持

## 🎯 核心公式

### 1. 产品内在价值评估（基于特性单独估值）
```
内在价值总得分 = Σ(特性单独估值 × 特性权重) ÷ 产品总价值

特性单独估值 = (含该特性版本售价 - 基础版售价) - 该特性的边际成本增量

特性分类估值：
- 功能型特性：基于参数提升幅度的溢价
- 体验型特性：基于体验改善可感知度的溢价  
- 稀缺型特性：基于稀缺性与独家性的溢价
- 服务型特性：基于服务必要性与便捷性的溢价

估值修正：
- 协同效应修正：多特性叠加的协同效应系数
- 生命周期修正：特性价值随时间变化的修正系数
```

### 2. 客户认知价值评估（主观感知数据）
```
认知价值总得分 = 功能认知覆盖率 × 50% + 支付意愿偏差 × 30% + 认知偏差率 × 20%

功能认知覆盖率 = (客户准确回忆项数 ÷ 产品核心功能总项数) × 100%
支付意愿偏差 = (客户平均WTP ÷ 产品实际定价) × 100%
认知偏差率 = 1 - |(客户认知值 - 产品实际值) ÷ 产品实际值| × 100%
```

### 3. 客户体验价值评估（使用后行为/反馈数据）
```
体验价值总得分 = 体验-认知偏差 × 40% + 场景满意度 × 30% + 行为转化总分 × 30%

体验-认知偏差 = 1 - |(实际使用值 - 认知值) ÷ 认知值| × 100%
场景满意度 = (某场景中选择"满意/非常满意"的客户数 ÷ 该场景调研总客户数) × 100%
行为转化总分 = 复购意愿率 × 60% + (NPS ÷ 100) × 40% × 100
```

## 🔧 算法实现

### 1. TypeScript实现

```typescript
// 价值评估接口
interface ValueAssessment {
  assessmentId: string;
  valueType: 'intrinsic' | 'cognitive' | 'experiential';
  overallScore: number;
  assessmentDetails: AssessmentDetails;
  assessmentDate: Date;
  tenantId: string;
  productId: string;
}

// 产品特性单独估值数据
interface ProductFeatureValuationData {
  features: ProductFeature[];
  totalProductValue: number; // 产品总价值
}

// 产品特性
interface ProductFeature {
  featureId: string;
  featureName: string;
  featureType: 'functional' | 'experiential' | 'scarce' | 'service';
  valuationMethod: 'internal_price_diff' | 'external_competitor' | 'customer_wtp';
  
  // 内部价差法数据
  baseVersionPrice: number; // 基础版售价
  featureVersionPrice: number; // 含特性版售价
  baseVersionCost: number; // 基础版成本
  featureVersionCost: number; // 含特性版成本
  
  // 外部竞品法数据
  competitorFeaturePrice: number; // 竞品特性价格
  competitorFeatureCost: number; // 竞品特性成本
  brandPowerDifference: number; // 品牌力差异（%）
  
  // 客户支付意愿法数据
  customerWTP: number; // 客户平均支付意愿
  customerWTPDistribution: WTPDistribution[]; // WTP分布
  
  // 修正系数
  synergyCoefficient: number; // 协同效应修正系数
  lifecycleCoefficient: number; // 生命周期修正系数
  
  // 验证数据
  salesRatio: number; // 升级版销量占比
  customerFeedback: number; // 客户反馈评分
}

// WTP分布
interface WTPDistribution {
  priceRange: string; // 价格区间
  customerRatio: number; // 客户占比
  weightedWTP: number; // 加权WTP
}

// 特性估值结果
interface FeatureValuationResult {
  featureId: string;
  featureName: string;
  preliminaryValuation: number; // 初步估值
  finalValuation: number; // 最终估值
  synergyCoefficient: number; // 协同效应修正系数
  lifecycleCoefficient: number; // 生命周期修正系数
  salesRatio: number; // 销量占比
  customerFeedback: number; // 客户反馈评分
}

// 客户认知价值数据
interface CognitiveValueData {
  totalCoreFunctions: number; // 产品核心功能总项数
  recalledFunctions: number; // 客户准确回忆项数
  customerWTP: number; // 客户平均WTP
  productPrice: number; // 产品实际定价
  customerCognition: number; // 客户认知的功能值
  productActualValue: number; // 产品实际功能值
}

// 客户体验价值数据
interface ExperientialValueData {
  actualUsageValue: number; // 实际使用功能值
  customerCognitionValue: number; // 客户认知功能值
  satisfiedCustomers: number; // 场景中满意客户数
  totalSurveyCustomers: number; // 场景调研总客户数
  repurchaseWillingCustomers: number; // 复购意愿客户数
  totalRepurchaseSurvey: number; // 复购调研总客户数
  npsScore: number; // NPS值
}

// 评估详情
interface AssessmentDetails {
  coverage: number; // 覆盖率
  satisfaction: number; // 满足深度
  recallRate: number; // 回忆率
  wtpDeviation: number; // WTP偏差
  cognitiveDeviation: number; // 认知偏差
  experienceDeviation: number; // 体验偏差
  scenarioSatisfaction: number; // 场景满意度
  behaviorConversion: number; // 行为转化
}

// 价值评估计算器
class ValueAssessmentCalculator {
  private readonly WEIGHTS = {
    intrinsic: { coverage: 0.4, satisfaction: 0.6 },
    cognitive: { recallRate: 0.3, wtpDeviation: 0.4, cognitiveDeviation: 0.3 },
    experiential: { experienceDeviation: 0.4, scenarioSatisfaction: 0.4, behaviorConversion: 0.2 }
  };

  /**
   * 计算产品内在价值（基于特性单独估值）
   */
  async calculateIntrinsicValue(
    assessmentId: string,
    valuationData: ProductFeatureValuationData,
    tenantId: string,
    productId: string
  ): Promise<ValueAssessment> {
    // 1. 验证输入数据
    this.validateValuationInputs(valuationData);
    
    // 2. 计算各特性单独估值
    const featureValuations = await this.calculateFeatureValuations(valuationData.features);
    
    // 3. 计算内在价值总得分
    const totalFeatureValue = featureValuations.reduce((sum, feature) => sum + feature.finalValuation, 0);
    const overallScore = (totalFeatureValue / valuationData.totalProductValue) * 100;
    
    // 4. 构建评估详情
    const assessmentDetails: AssessmentDetails = {
      coverage: this.calculateFeatureCoverage(featureValuations),
      satisfaction: this.calculateFeatureSatisfaction(featureValuations),
      recallRate: 0,
      wtpDeviation: 0,
      cognitiveDeviation: 0,
      experienceDeviation: 0,
      scenarioSatisfaction: 0,
      behaviorConversion: 0
    };
    
    return {
      assessmentId,
      valueType: 'intrinsic',
      overallScore,
      assessmentDetails,
      assessmentDate: new Date(),
      tenantId,
      productId
    };
  }

  /**
   * 计算客户认知价值
   */
  async calculateCognitiveValue(
    assessmentId: string,
    cognitiveData: CognitiveValueData,
    tenantId: string,
    productId: string
  ): Promise<ValueAssessment> {
    // 1. 验证输入数据
    this.validateCognitiveInputs(cognitiveData);
    
    // 2. 计算功能认知覆盖率
    const cognitiveCoverage = (cognitiveData.recalledFunctions / cognitiveData.totalCoreFunctions) * 100;
    
    // 3. 计算支付意愿偏差
    const wtpDeviation = (cognitiveData.customerWTP / cognitiveData.productPrice) * 100;
    
    // 4. 计算认知偏差率
    const cognitiveDeviation = (1 - Math.abs((cognitiveData.customerCognition - cognitiveData.productActualValue) / cognitiveData.productActualValue)) * 100;
    
    // 5. 计算认知价值总得分
    const overallScore = cognitiveCoverage * 0.5 + wtpDeviation * 0.3 + cognitiveDeviation * 0.2;
    
    // 6. 构建评估详情
    const assessmentDetails: AssessmentDetails = {
      coverage: 0,
      satisfaction: 0,
      recallRate: cognitiveCoverage,
      wtpDeviation,
      cognitiveDeviation,
      experienceDeviation: 0,
      scenarioSatisfaction: 0,
      behaviorConversion: 0
    };
    
    return {
      assessmentId,
      valueType: 'cognitive',
      overallScore,
      assessmentDetails,
      assessmentDate: new Date(),
      tenantId,
      productId
    };
  }

  /**
   * 计算客户体验价值
   */
  async calculateExperientialValue(
    assessmentId: string,
    experientialData: ExperientialValueData,
    tenantId: string,
    productId: string
  ): Promise<ValueAssessment> {
    // 1. 验证输入数据
    this.validateExperientialInputs(experientialData);
    
    // 2. 计算体验-认知偏差
    const experienceCognitionDeviation = (1 - Math.abs((experientialData.actualUsageValue - experientialData.customerCognitionValue) / experientialData.customerCognitionValue)) * 100;
    
    // 3. 计算场景满意度
    const scenarioSatisfaction = (experientialData.satisfiedCustomers / experientialData.totalSurveyCustomers) * 100;
    
    // 4. 计算行为转化总分
    const repurchaseRate = (experientialData.repurchaseWillingCustomers / experientialData.totalRepurchaseSurvey) * 100;
    const behaviorConversion = repurchaseRate * 0.6 + (experientialData.npsScore / 100) * 0.4 * 100;
    
    // 5. 计算体验价值总得分
    const overallScore = experienceCognitionDeviation * 0.4 + scenarioSatisfaction * 0.3 + behaviorConversion * 0.3;
    
    // 6. 构建评估详情
    const assessmentDetails: AssessmentDetails = {
      coverage: 0,
      satisfaction: 0,
      recallRate: 0,
      wtpDeviation: 0,
      cognitiveDeviation: 0,
      experienceDeviation: experienceCognitionDeviation,
      scenarioSatisfaction,
      behaviorConversion
    };
    
    return {
      assessmentId,
      valueType: 'experiential',
      overallScore,
      assessmentDetails,
      assessmentDate: new Date(),
      tenantId,
      productId
    };
  }

  /**
   * 计算特性单独估值
   */
  private async calculateFeatureValuations(features: ProductFeature[]): Promise<FeatureValuationResult[]> {
    const results: FeatureValuationResult[] = [];
    
    for (const feature of features) {
      let preliminaryValuation = 0;
      
      // 根据估值方法计算初步估值
      switch (feature.valuationMethod) {
        case 'internal_price_diff':
          preliminaryValuation = this.calculateInternalPriceDiffValuation(feature);
          break;
        case 'external_competitor':
          preliminaryValuation = this.calculateExternalCompetitorValuation(feature);
          break;
        case 'customer_wtp':
          preliminaryValuation = this.calculateCustomerWTPValuation(feature);
          break;
      }
      
      // 应用修正系数
      const finalValuation = preliminaryValuation * feature.synergyCoefficient * feature.lifecycleCoefficient;
      
      results.push({
        featureId: feature.featureId,
        featureName: feature.featureName,
        preliminaryValuation,
        finalValuation,
        synergyCoefficient: feature.synergyCoefficient,
        lifecycleCoefficient: feature.lifecycleCoefficient,
        salesRatio: feature.salesRatio,
        customerFeedback: feature.customerFeedback
      });
    }
    
    return results;
  }

  /**
   * 内部价差法估值
   */
  private calculateInternalPriceDiffValuation(feature: ProductFeature): number {
    const priceDiff = feature.featureVersionPrice - feature.baseVersionPrice;
    const costDiff = feature.featureVersionCost - feature.baseVersionCost;
    return priceDiff - costDiff;
  }

  /**
   * 外部竞品法估值
   */
  private calculateExternalCompetitorValuation(feature: ProductFeature): number {
    const competitorPremium = feature.competitorFeaturePrice - feature.competitorFeatureCost;
    const brandAdjustment = 1 - (feature.brandPowerDifference / 100);
    const costAdvantage = feature.competitorFeatureCost - (feature.featureVersionCost - feature.baseVersionCost);
    return (competitorPremium * brandAdjustment) + costAdvantage;
  }

  /**
   * 客户支付意愿法估值
   */
  private calculateCustomerWTPValuation(feature: ProductFeature): number {
    const marginalCost = feature.featureVersionCost - feature.baseVersionCost;
    return feature.customerWTP - marginalCost;
  }

  /**
   * 计算特性覆盖率
   */
  private calculateFeatureCoverage(valuations: FeatureValuationResult[]): number {
    const totalFeatures = valuations.length;
    const valuableFeatures = valuations.filter(v => v.finalValuation > 0).length;
    return (valuableFeatures / totalFeatures) * 100;
  }

  /**
   * 计算特性满意度
   */
  private calculateFeatureSatisfaction(valuations: FeatureValuationResult[]): number {
    const totalFeedback = valuations.reduce((sum, v) => sum + v.customerFeedback, 0);
    return totalFeedback / valuations.length;
  }

  /**
   * 计算认知价值得分
   */
  private calculateCognitiveScore(recallRate: number, wtpDeviation: number, cognitiveDeviation: number): number {
    const { recallRate: recallWeight, wtpDeviation: wtpWeight, cognitiveDeviation: cognitiveWeight } = this.WEIGHTS.cognitive;
    return (recallRate * recallWeight) + (wtpDeviation * wtpWeight) + (cognitiveDeviation * cognitiveWeight);
  }

  /**
   * 计算体验价值得分
   */
  private calculateExperientialScore(experienceDeviation: number, scenarioSatisfaction: number, behaviorConversion: number): number {
    const { experienceDeviation: expWeight, scenarioSatisfaction: scenarioWeight, behaviorConversion: behaviorWeight } = this.WEIGHTS.experiential;
    return (experienceDeviation * expWeight) + (scenarioSatisfaction * scenarioWeight) + (behaviorConversion * behaviorWeight);
  }

  /**
   * 验证内在价值输入
   */
  private validateIntrinsicInputs(coverage: number, satisfaction: number): void {
    if (coverage < 0 || coverage > 100) {
      throw new Error('覆盖率必须在0-100之间');
    }
    
    if (satisfaction < 0 || satisfaction > 100) {
      throw new Error('满足深度必须在0-100之间');
    }
  }

  /**
   * 验证认知价值输入
   */
  private validateCognitiveInputs(recallRate: number, wtpDeviation: number, cognitiveDeviation: number): void {
    if (recallRate < 0 || recallRate > 100) {
      throw new Error('回忆率必须在0-100之间');
    }
    
    if (wtpDeviation < 0 || wtpDeviation > 100) {
      throw new Error('WTP偏差必须在0-100之间');
    }
    
    if (cognitiveDeviation < 0 || cognitiveDeviation > 100) {
      throw new Error('认知偏差必须在0-100之间');
    }
  }

  /**
   * 验证体验价值输入
   */
  private validateExperientialInputs(experienceDeviation: number, scenarioSatisfaction: number, behaviorConversion: number): void {
    if (experienceDeviation < 0 || experienceDeviation > 100) {
      throw new Error('体验偏差必须在0-100之间');
    }
    
    if (scenarioSatisfaction < 0 || scenarioSatisfaction > 100) {
      throw new Error('场景满意度必须在0-100之间');
    }
    
    if (behaviorConversion < 0 || behaviorConversion > 100) {
      throw new Error('行为转化必须在0-100之间');
    }
  }
}
```

### 2. 数据库存储

```sql
-- 内在价值评估计算函数
CREATE OR REPLACE FUNCTION calculate_intrinsic_value(
  p_coverage DECIMAL(5,2),
  p_satisfaction DECIMAL(5,2)
) RETURNS DECIMAL(5,2) AS $$
DECLARE
  v_overall_score DECIMAL(5,2);
BEGIN
  -- 内在价值得分 = 覆盖率 × 0.4 + 满足深度 × 0.6
  v_overall_score := (p_coverage * 0.4) + (p_satisfaction * 0.6);
  
  RETURN v_overall_score;
END;
$$ LANGUAGE plpgsql;

-- 认知价值评估计算函数
CREATE OR REPLACE FUNCTION calculate_cognitive_value(
  p_recall_rate DECIMAL(5,2),
  p_wtp_deviation DECIMAL(5,2),
  p_cognitive_deviation DECIMAL(5,2)
) RETURNS DECIMAL(5,2) AS $$
DECLARE
  v_overall_score DECIMAL(5,2);
BEGIN
  -- 认知价值得分 = 回忆率 × 0.3 + WTP偏差 × 0.4 + 认知偏差 × 0.3
  v_overall_score := (p_recall_rate * 0.3) + (p_wtp_deviation * 0.4) + (p_cognitive_deviation * 0.3);
  
  RETURN v_overall_score;
END;
$$ LANGUAGE plpgsql;

-- 体验价值评估计算函数
CREATE OR REPLACE FUNCTION calculate_experiential_value(
  p_experience_deviation DECIMAL(5,2),
  p_scenario_satisfaction DECIMAL(5,2),
  p_behavior_conversion DECIMAL(5,2)
) RETURNS DECIMAL(5,2) AS $$
DECLARE
  v_overall_score DECIMAL(5,2);
BEGIN
  -- 体验价值得分 = 体验偏差 × 0.4 + 场景满意度 × 0.4 + 行为转化 × 0.2
  v_overall_score := (p_experience_deviation * 0.4) + (p_scenario_satisfaction * 0.4) + (p_behavior_conversion * 0.2);
  
  RETURN v_overall_score;
END;
$$ LANGUAGE plpgsql;
```

## 📊 数据采集表模板

### 产品特性单独估值数据采集表

| 特性名称 | 特性类型 | 估值方法 | 基础数据 | 裸价差/竞品溢价/平均WTP | 边际成本增量 | 初步估值 | 修正系数 | 最终估值 | 验证数据 |
|----------|----------|----------|----------|------------------------|-------------|----------|----------|----------|----------|
| **手机67W快充** | 功能型 | 内部价差法 | 基础版2999元(成本1800)，升级版3299元(成本1880) | 300元 | 80元 | 220元 | 成长期1.0 | 220元 | 升级版销量占比60% |
| **冰箱除菌功能** | 功能型 | 外部竞品法 | 竞品选装包499元(成本150)，自身成本140元 | 349元(竞品溢价) | 140元 | 341.55元 | 导入期1.2 | 409.86元 | 调研80%客户愿多付400+元 |
| **AI语音助手** | 体验型 | 支付意愿法 | 调研1000人，平均WTP80元，自身成本25元 | 80元(平均WTP) | 25元 | 55元 | 导入期1.2 | 66元 | 新品测试中，意向占比75% |

### 特性分类与估值方法说明

| 特性类型 | 定义 | 单独售卖场景示例 | 核心溢价驱动因素 | 估值方法 |
|----------|------|------------------|------------------|----------|
| **功能型特性** | 解决客户具体功能需求，参数可量化 | 基础款手机(续航4000mAh) + 续航升级包(+2000mAh) | 功能参数提升幅度 | 内部价差法/外部竞品法 |
| **体验型特性** | 优化使用感受，非参数化但可感知 | 基础款耳机(普通降噪) + 深度降噪升级包 | 体验改善的可感知度 | 客户支付意愿法 |
| **稀缺型特性** | 独家或限量供应，具备差异化壁垒 | 基础款汽车(标准版车漆) + 独家定制车漆选装包 | 稀缺性与独家性 | 外部竞品法/客户支付意愿法 |
| **服务型特性** | 配套服务支持，延伸特性价值 | 基础款家电(1年质保) + 延保2年服务包 | 服务的必要性与便捷性 | 客户支付意愿法 |

### 估值方法详细说明

#### 1. 内部价差法
```
特性单独估值 = (含该特性版本售价 - 基础版售价) - 该特性的边际成本增量
适用场景：自有产品有清晰的"基础-升级"版本划分
```

#### 2. 外部竞品法
```
自有特性估值 = (竞品溢价 × (1 - 品牌力差异)) + (竞品边际成本 - 自身边际成本)
适用场景：自有产品无多版本，但竞品有明确的特性单独售卖定价
```

#### 3. 客户支付意愿法
```
特性单独估值 = 客户平均WTP - 边际成本增量
适用场景：全新特性(无竞品参考)或niche市场产品
```

### 修正系数说明

| 修正类型 | 修正系数 | 说明 | 示例 |
|----------|----------|------|------|
| **协同效应修正** | 1.0-1.5 | 多特性叠加的协同效应 | 高分辨率屏幕+高刷新率的视觉体验协同 |
| **生命周期修正** | 0.7-1.2 | 特性价值随时间变化 | 导入期1.2，成长期1.0，成熟期0.7 |
| **二、客户认知价值（总分）** | | | | | 100% | =功能认知覆盖率×50% + 支付意愿偏差×30% + 认知偏差率×20% |
| | 1. 功能认知覆盖率 | | | | 50% | =客户回忆项数/产品功能总项数×100% |
| | | 1.1 产品核心功能总项数 | 产品功能清单 | ______ 项 | - | - |
| | | 1.2 客户准确回忆项数 | 认知调研问卷 | ______ 项 | - | - |
| | 2. 支付意愿偏差 | | | | 30% | =客户WTP/产品定价×100% |
| | | 2.1 客户平均WTP | 支付意愿调研 | ______ 元 | - | - |
| | | 2.2 产品实际定价 | 产品定价表 | ______ 元 | - | - |
| | 3. 认知偏差率 | | | | 20% | =(1-ABS((客户认知值-实际值)/实际值))×100% |
| | | 3.1 客户认知功能值 | 认知调研 | ______ | - | - |
| | | 3.2 产品实际功能值 | 产品测试报告 | ______ | - | - |
| **三、客户体验价值（总分）** | | | | | 100% | =体验-认知偏差×40% + 场景满意度×30% + 行为转化×30% |
| | 1. 体验-认知偏差 | | | | 40% | =(1-ABS((实际使用值-认知值)/认知值))×100% |
| | | 1.1 实际使用功能值 | 产品使用日志/体验调研 | ______ | - | - |
| | | 1.2 客户认知功能值 | 认知调研 | ______ | - | - |
| | 2. 场景满意度 | | | | 30% | =满意客户数/调研总客户数×100% |
| | | 2.1 核心场景名称 | 体验调研 | ______ | - | - |
| | | 2.2 场景中满意客户数 | 场景化调研问卷 | ______ 人 | - | - |
| | | 2.3 场景调研总客户数 | 场景化调研问卷 | ______ 人 | - | - |
| | 3. 行为转化 | | | | 30% | =复购意愿率×60% + (NPS/100)×40%×100 |
| | | 3.1 复购意愿客户数 | 体验后调研 | ______ 人 | - | - |
| | | 3.2 复购调研总客户数 | 体验后调研 | ______ 人 | - | - |
| | | 3.3 复购意愿率 | - | =复购意愿数/调研总数×100% → ______% | 60% | - |
| | | 3.4 NPS值 | NPS调研问卷 | ______ 分 | 40% | - |

### 数据采集说明

1. **填写逻辑**：先填"△"项（手动录入数据），再通过公式计算"★"项
2. **数据来源规范**：
   - 内在价值：需求调研需≥300份样本，产品测试建议第三方执行
   - 认知价值：调研对象为"未使用但了解产品的潜在客户"
   - 体验价值：使用日志需自动采集，减少主观隐瞒
3. **得分解读**：≥80分为高价值，60-80分为中等，<60分为待优化

## 📊 具体评估项明细

### 1. 内在价值评估项

```typescript
// 内在价值评估项
interface IntrinsicValueAssessmentItems {
  // 覆盖率评估
  coverage: {
    productFeatures: number; // 产品功能覆盖率
    userNeeds: number; // 用户需求覆盖率
    marketSegments: number; // 市场细分覆盖率
    useCases: number; // 使用场景覆盖率
  };
  
  // 满足深度评估
  satisfaction: {
    functionalSatisfaction: number; // 功能满足度
    performanceSatisfaction: number; // 性能满足度
    qualitySatisfaction: number; // 质量满足度
    reliabilitySatisfaction: number; // 可靠性满足度
  };
}

// 内在价值评估计算器
class IntrinsicValueAssessmentCalculator {
  /**
   * 计算覆盖率得分
   */
  calculateCoverageScore(items: IntrinsicValueAssessmentItems['coverage']): number {
    const weights = {
      productFeatures: 0.3,
      userNeeds: 0.3,
      marketSegments: 0.2,
      useCases: 0.2
    };
    
    return (
      items.productFeatures * weights.productFeatures +
      items.userNeeds * weights.userNeeds +
      items.marketSegments * weights.marketSegments +
      items.useCases * weights.useCases
    );
  }
  
  /**
   * 计算满足深度得分
   */
  calculateSatisfactionScore(items: IntrinsicValueAssessmentItems['satisfaction']): number {
    const weights = {
      functionalSatisfaction: 0.3,
      performanceSatisfaction: 0.3,
      qualitySatisfaction: 0.2,
      reliabilitySatisfaction: 0.2
    };
    
    return (
      items.functionalSatisfaction * weights.functionalSatisfaction +
      items.performanceSatisfaction * weights.performanceSatisfaction +
      items.qualitySatisfaction * weights.qualitySatisfaction +
      items.reliabilitySatisfaction * weights.reliabilitySatisfaction
    );
  }
}
```

### 2. 认知价值评估项

```typescript
// 认知价值评估项
interface CognitiveValueAssessmentItems {
  // 回忆率评估
  recallRate: {
    brandRecall: number; // 品牌回忆率
    productRecall: number; // 产品回忆率
    featureRecall: number; // 功能回忆率
    benefitRecall: number; // 利益回忆率
  };
  
  // WTP偏差评估
  wtpDeviation: {
    pricePerception: number; // 价格感知
    valuePerception: number; // 价值感知
    willingnessToPay: number; // 支付意愿
    priceSensitivity: number; // 价格敏感性
  };
  
  // 认知偏差评估
  cognitiveDeviation: {
    brandAwareness: number; // 品牌认知
    productAwareness: number; // 产品认知
    featureAwareness: number; // 功能认知
    benefitAwareness: number; // 利益认知
  };
}

// 认知价值评估计算器
class CognitiveValueAssessmentCalculator {
  /**
   * 计算回忆率得分
   */
  calculateRecallRateScore(items: CognitiveValueAssessmentItems['recallRate']): number {
    const weights = {
      brandRecall: 0.3,
      productRecall: 0.3,
      featureRecall: 0.2,
      benefitRecall: 0.2
    };
    
    return (
      items.brandRecall * weights.brandRecall +
      items.productRecall * weights.productRecall +
      items.featureRecall * weights.featureRecall +
      items.benefitRecall * weights.benefitRecall
    );
  }
  
  /**
   * 计算WTP偏差得分
   */
  calculateWTPDeviationScore(items: CognitiveValueAssessmentItems['wtpDeviation']): number {
    const weights = {
      pricePerception: 0.3,
      valuePerception: 0.3,
      willingnessToPay: 0.2,
      priceSensitivity: 0.2
    };
    
    return (
      items.pricePerception * weights.pricePerception +
      items.valuePerception * weights.valuePerception +
      items.willingnessToPay * weights.willingnessToPay +
      items.priceSensitivity * weights.priceSensitivity
    );
  }
  
  /**
   * 计算认知偏差得分
   */
  calculateCognitiveDeviationScore(items: CognitiveValueAssessmentItems['cognitiveDeviation']): number {
    const weights = {
      brandAwareness: 0.3,
      productAwareness: 0.3,
      featureAwareness: 0.2,
      benefitAwareness: 0.2
    };
    
    return (
      items.brandAwareness * weights.brandAwareness +
      items.productAwareness * weights.productAwareness +
      items.featureAwareness * weights.featureAwareness +
      items.benefitAwareness * weights.benefitAwareness
    );
  }
}
```

### 3. 体验价值评估项

```typescript
// 体验价值评估项
interface ExperientialValueAssessmentItems {
  // 体验偏差评估
  experienceDeviation: {
    usability: number; // 易用性
    accessibility: number; // 可访问性
    efficiency: number; // 效率
    satisfaction: number; // 满意度
  };
  
  // 场景满意度评估
  scenarioSatisfaction: {
    primaryScenario: number; // 主要场景满意度
    secondaryScenario: number; // 次要场景满意度
    edgeCaseScenario: number; // 边缘场景满意度
    errorScenario: number; // 错误场景满意度
  };
  
  // 行为转化评估
  behaviorConversion: {
    purchaseIntent: number; // 购买意图
    recommendationIntent: number; // 推荐意图
    repurchaseIntent: number; // 复购意图
    loyaltyIntent: number; // 忠诚度意图
  };
}

// 体验价值评估计算器
class ExperientialValueAssessmentCalculator {
  /**
   * 计算体验偏差得分
   */
  calculateExperienceDeviationScore(items: ExperientialValueAssessmentItems['experienceDeviation']): number {
    const weights = {
      usability: 0.3,
      accessibility: 0.2,
      efficiency: 0.3,
      satisfaction: 0.2
    };
    
    return (
      items.usability * weights.usability +
      items.accessibility * weights.accessibility +
      items.efficiency * weights.efficiency +
      items.satisfaction * weights.satisfaction
    );
  }
  
  /**
   * 计算场景满意度得分
   */
  calculateScenarioSatisfactionScore(items: ExperientialValueAssessmentItems['scenarioSatisfaction']): number {
    const weights = {
      primaryScenario: 0.4,
      secondaryScenario: 0.3,
      edgeCaseScenario: 0.2,
      errorScenario: 0.1
    };
    
    return (
      items.primaryScenario * weights.primaryScenario +
      items.secondaryScenario * weights.secondaryScenario +
      items.edgeCaseScenario * weights.edgeCaseScenario +
      items.errorScenario * weights.errorScenario
    );
  }
  
  /**
   * 计算行为转化得分
   */
  calculateBehaviorConversionScore(items: ExperientialValueAssessmentItems['behaviorConversion']): number {
    const weights = {
      purchaseIntent: 0.3,
      recommendationIntent: 0.3,
      repurchaseIntent: 0.2,
      loyaltyIntent: 0.2
    };
    
    return (
      items.purchaseIntent * weights.purchaseIntent +
      items.recommendationIntent * weights.recommendationIntent +
      items.repurchaseIntent * weights.repurchaseIntent +
      items.loyaltyIntent * weights.loyaltyIntent
    );
  }
}
```

## 🔄 嵌入式调研页面集成

### 1. 调研页面数据收集

```typescript
// 调研页面数据收集器
class SurveyDataCollector {
  private surveyId: string;
  private tenantId: string;
  private productId: string;
  
  constructor(surveyId: string, tenantId: string, productId: string) {
    this.surveyId = surveyId;
    this.tenantId = tenantId;
    this.productId = productId;
  }
  
  /**
   * 收集内在价值数据
   */
  async collectIntrinsicValueData(surveyData: any): Promise<ValueAssessment> {
    const calculator = new ValueAssessmentCalculator();
    
    // 提取覆盖率数据
    const coverage = this.extractCoverageData(surveyData);
    
    // 提取满足深度数据
    const satisfaction = this.extractSatisfactionData(surveyData);
    
    // 计算内在价值
    return await calculator.calculateIntrinsicValue(
      this.surveyId,
      coverage,
      satisfaction,
      this.tenantId,
      this.productId
    );
  }
  
  /**
   * 收集认知价值数据
   */
  async collectCognitiveValueData(surveyData: any): Promise<ValueAssessment> {
    const calculator = new ValueAssessmentCalculator();
    
    // 提取回忆率数据
    const recallRate = this.extractRecallRateData(surveyData);
    
    // 提取WTP偏差数据
    const wtpDeviation = this.extractWTPDeviationData(surveyData);
    
    // 提取认知偏差数据
    const cognitiveDeviation = this.extractCognitiveDeviationData(surveyData);
    
    // 计算认知价值
    return await calculator.calculateCognitiveValue(
      this.surveyId,
      recallRate,
      wtpDeviation,
      cognitiveDeviation,
      this.tenantId,
      this.productId
    );
  }
  
  /**
   * 收集体验价值数据
   */
  async collectExperientialValueData(surveyData: any): Promise<ValueAssessment> {
    const calculator = new ValueAssessmentCalculator();
    
    // 提取体验偏差数据
    const experienceDeviation = this.extractExperienceDeviationData(surveyData);
    
    // 提取场景满意度数据
    const scenarioSatisfaction = this.extractScenarioSatisfactionData(surveyData);
    
    // 提取行为转化数据
    const behaviorConversion = this.extractBehaviorConversionData(surveyData);
    
    // 计算体验价值
    return await calculator.calculateExperientialValue(
      this.surveyId,
      experienceDeviation,
      scenarioSatisfaction,
      behaviorConversion,
      this.tenantId,
      this.productId
    );
  }
  
  /**
   * 提取覆盖率数据
   */
  private extractCoverageData(surveyData: any): number {
    // 根据调研数据结构提取覆盖率
    const productFeatures = surveyData.coverage?.productFeatures || 0;
    const userNeeds = surveyData.coverage?.userNeeds || 0;
    const marketSegments = surveyData.coverage?.marketSegments || 0;
    const useCases = surveyData.coverage?.useCases || 0;
    
    const calculator = new IntrinsicValueAssessmentCalculator();
    return calculator.calculateCoverageScore({
      productFeatures,
      userNeeds,
      marketSegments,
      useCases
    });
  }
  
  /**
   * 提取满足深度数据
   */
  private extractSatisfactionData(surveyData: any): number {
    // 根据调研数据结构提取满足深度
    const functionalSatisfaction = surveyData.satisfaction?.functional || 0;
    const performanceSatisfaction = surveyData.satisfaction?.performance || 0;
    const qualitySatisfaction = surveyData.satisfaction?.quality || 0;
    const reliabilitySatisfaction = surveyData.satisfaction?.reliability || 0;
    
    const calculator = new IntrinsicValueAssessmentCalculator();
    return calculator.calculateSatisfactionScore({
      functionalSatisfaction,
      performanceSatisfaction,
      qualitySatisfaction,
      reliabilitySatisfaction
    });
  }
}
```

### 2. 实时数据同步

```typescript
// 实时数据同步器
class RealTimeValueAssessmentSync {
  private wsClient: WebSocketClient;
  
  constructor(wsClient: WebSocketClient) {
    this.wsClient = wsClient;
  }
  
  /**
   * 同步价值评估数据
   */
  async syncValueAssessment(assessment: ValueAssessment): Promise<void> {
    try {
      // 1. 保存到数据库
      await this.saveValueAssessment(assessment);
      
      // 2. 触发实时计算
      await this.triggerRealTimeCalculation(assessment);
      
      // 3. 通知相关用户
      await this.notifyRelevantUsers(assessment);
      
      // 4. 发送WebSocket消息
      this.wsClient.send({
        type: 'value_assessment_updated',
        data: assessment
      });
      
    } catch (error) {
      console.error('价值评估数据同步失败:', error);
      throw error;
    }
  }
  
  /**
   * 触发实时计算
   */
  private async triggerRealTimeCalculation(assessment: ValueAssessment): Promise<void> {
    // 根据价值类型触发不同的计算
    switch (assessment.valueType) {
      case 'intrinsic':
        await this.triggerIntrinsicValueCalculation(assessment);
        break;
      case 'cognitive':
        await this.triggerCognitiveValueCalculation(assessment);
        break;
      case 'experiential':
        await this.triggerExperientialValueCalculation(assessment);
        break;
    }
  }
}
```

## 📈 性能优化

### 1. 批量计算

```typescript
// 批量价值评估计算
class BatchValueAssessmentCalculator {
  private batchSize = 10;
  private batchTimeout = 1000; // 1秒

  /**
   * 批量计算多个价值评估
   */
  async batchCalculateValueAssessments(
    assessments: ValueAssessmentInput[]
  ): Promise<ValueAssessment[]> {
    const results: ValueAssessment[] = [];
    
    for (let i = 0; i < assessments.length; i += this.batchSize) {
      const batch = assessments.slice(i, i + this.batchSize);
      const batchResults = await Promise.all(
        batch.map(assessment => this.calculateSingleValueAssessment(assessment))
      );
      results.push(...batchResults);
      
      // 避免阻塞，让出控制权
      if (i + this.batchSize < assessments.length) {
        await this.delay(this.batchTimeout);
      }
    }
    
    return results;
  }
}
```

### 2. 缓存策略

```typescript
// 价值评估计算缓存
class ValueAssessmentCache {
  private cache = new Map<string, any>();
  private ttl = 3600000; // 1小时

  /**
   * 获取缓存的价值评估计算结果
   */
  get(assessmentId: string, inputs: any): ValueAssessment | null {
    const key = this.generateCacheKey(assessmentId, inputs);
    const item = this.cache.get(key);
    
    if (!item || Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }

  /**
   * 缓存价值评估计算结果
   */
  set(assessmentId: string, inputs: any, result: ValueAssessment): void {
    const key = this.generateCacheKey(assessmentId, inputs);
    this.cache.set(key, {
      value: result,
      expires: Date.now() + this.ttl
    });
  }
}
```

## 🚀 实施计划

### 阶段1：基础算法实现（Week 1）
1. **TypeScript计算器**：实现ValueAssessmentCalculator类
2. **数据库函数**：实现三类价值评估计算函数
3. **评估项明细**：实现具体评估项计算

### 阶段2：嵌入式调研集成（Week 2）
1. **数据收集器**：实现SurveyDataCollector类
2. **实时同步**：实现RealTimeValueAssessmentSync类
3. **WebSocket集成**：实现实时数据同步

### 阶段3：性能优化（Week 3）
1. **批量计算**：实现批量价值评估计算
2. **缓存策略**：实现计算结果缓存
3. **性能测试**：验证性能指标

---

**本算法设计确保三类价值评估的准确性和实时性，支持嵌入式调研页面数据收集，满足100家企业的评估需求。**
