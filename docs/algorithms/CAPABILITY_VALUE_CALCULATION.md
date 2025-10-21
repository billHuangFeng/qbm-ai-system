# 能力价值计算公式设计

## 📋 算法概述

基于用户澄清，能力价值评估由**人工把握灵活性**，系统提供计算功能。算法实现"稳定成果+收益百分比"的能力价值量化，支持连续6个月稳定性判定。

## 🎯 用户说明指引

### 什么是能力价值计算？
能力价值计算是评估企业核心能力价值的方法。它通过分析能力带来的稳定成果和收益贡献，量化能力的真实价值。

### 为什么需要能力价值计算？
- **能力价值量化**：将抽象的企业能力转化为具体的货币价值
- **能力投资决策**：帮助判断能力建设投资是否值得
- **能力优化指导**：为能力提升提供数据支持

### 计算步骤说明
1. **确定稳定成果**：识别能力带来的可量化成果（如质量合格率、上市周期等）
2. **计算贡献百分比**：(当前成果 - 基准成果) ÷ 当前成果 × 100%
3. **确定年度收益**：计算能力带来的年度收益（如成本节省、收入增量等）
4. **计算月度价值**：年度收益 × 贡献百分比 ÷ 12
5. **稳定性检查**：验证是否连续6个月达到标准

### 数据来源说明
- **稳定成果**：来自MES质检模块、研发管理系统、营销系统等
- **基准成果**：历史无该能力时的平均成果水平
- **年度收益**：来自财务部成本报表、CRM收入数据等
- **贡献百分比**：基于成果提升幅度计算

### 使用场景
- **能力投资评估**：评估能力建设投资价值
- **能力价值监控**：定期评估能力价值变化
- **能力优化指导**：识别需要优化的能力类型

## 🎯 核心公式

### 1. 能力价值计算
```
△能力价值 = 稳定成果对应的年度收益 × 贡献百分比 ÷ 12
```

### 2. 贡献百分比计算
```
贡献百分比 = (当前成果 - 基准成果) ÷ 当前成果 × 100%
```

### 3. 稳定性判定
```
稳定性 = 连续6个月达到标准成果
```

## 🔧 算法实现

### 1. TypeScript实现

```typescript
// 能力价值计算接口
interface CapabilityValueCalculation {
  capabilityId: string;
  capabilityType: 'production' | 'rd' | 'marketing' | 'delivery' | 'channel';
  stableOutcome: StableOutcome;
  annualRevenue: number;
  contributionPercentage: number;
  monthlyValue: number;
  stabilityStatus: 'stable' | 'unstable' | 'pending';
  calculationDate: Date;
}

// 稳定成果定义
interface StableOutcome {
  metric: string;
  currentValue: number;
  baselineValue: number;
  targetValue: number;
  unit: string;
  measurementPeriod: number; // 连续月数
}

// 能力价值计算器
class CapabilityValueCalculator {
  private readonly STABILITY_MONTHS = 6;
  private readonly CONTRIBUTION_THRESHOLD = 0.05; // 5%最小贡献

  /**
   * 计算能力价值
   * @param capabilityId 能力ID
   * @param stableOutcome 稳定成果
   * @param annualRevenue 年度收益
   * @returns 能力价值计算结果
   */
  async calculateCapabilityValue(
    capabilityId: string,
    stableOutcome: StableOutcome,
    annualRevenue: number
  ): Promise<CapabilityValueCalculation> {
    // 1. 验证输入数据
    this.validateInputs(stableOutcome, annualRevenue);
    
    // 2. 计算贡献百分比
    const contributionPercentage = this.calculateContributionPercentage(stableOutcome);
    
    // 3. 计算月度价值
    const monthlyValue = this.calculateMonthlyValue(annualRevenue, contributionPercentage);
    
    // 4. 检查稳定性状态
    const stabilityStatus = await this.checkStabilityStatus(capabilityId, stableOutcome);
    
    return {
      capabilityId,
      capabilityType: this.getCapabilityType(capabilityId),
      stableOutcome,
      annualRevenue,
      contributionPercentage,
      monthlyValue,
      stabilityStatus,
      calculationDate: new Date()
    };
  }

  /**
   * 计算贡献百分比
   */
  private calculateContributionPercentage(stableOutcome: StableOutcome): number {
    const { currentValue, baselineValue } = stableOutcome;
    
    if (currentValue <= baselineValue) {
      return 0; // 无贡献
    }
    
    const contribution = (currentValue - baselineValue) / currentValue;
    return Math.max(contribution, this.CONTRIBUTION_THRESHOLD);
  }

  /**
   * 计算月度价值
   */
  private calculateMonthlyValue(annualRevenue: number, contributionPercentage: number): number {
    return (annualRevenue * contributionPercentage) / 12;
  }

  /**
   * 检查稳定性状态
   */
  private async checkStabilityStatus(
    capabilityId: string,
    stableOutcome: StableOutcome
  ): Promise<'stable' | 'unstable' | 'pending'> {
    // 查询最近6个月的数据
    const recentData = await this.getRecentCapabilityData(capabilityId, this.STABILITY_MONTHS);
    
    if (recentData.length < this.STABILITY_MONTHS) {
      return 'pending'; // 数据不足
    }
    
    // 检查是否连续6个月达到标准
    const isStable = recentData.every(data => 
      data.metricValue >= stableOutcome.targetValue
    );
    
    return isStable ? 'stable' : 'unstable';
  }

  /**
   * 获取能力类型
   */
  private getCapabilityType(capabilityId: string): string {
    // 根据能力ID或名称判断类型
    const capabilityTypes = {
      'production': ['生产', '制造', '加工'],
      'rd': ['研发', '创新', '技术'],
      'marketing': ['营销', '推广', '传播'],
      'delivery': ['交付', '物流', '配送'],
      'channel': ['渠道', '销售', '分销']
    };
    
    for (const [type, keywords] of Object.entries(capabilityTypes)) {
      if (keywords.some(keyword => capabilityId.includes(keyword))) {
        return type;
      }
    }
    
    return 'unknown';
  }

  /**
   * 验证输入数据
   */
  private validateInputs(stableOutcome: StableOutcome, annualRevenue: number): void {
    if (stableOutcome.currentValue <= 0) {
      throw new Error('当前成果值必须大于0');
    }
    
    if (stableOutcome.baselineValue < 0) {
      throw new Error('基准成果值不能为负数');
    }
    
    if (stableOutcome.targetValue <= stableOutcome.baselineValue) {
      throw new Error('目标成果值必须大于基准成果值');
    }
    
    if (annualRevenue <= 0) {
      throw new Error('年度收益必须大于0');
    }
  }
}
```

### 2. 数据库存储

```sql
-- 能力价值计算函数
CREATE OR REPLACE FUNCTION calculate_capability_value(
  p_capability_id UUID,
  p_current_value DECIMAL(10,4),
  p_baseline_value DECIMAL(10,4),
  p_target_value DECIMAL(10,4),
  p_annual_revenue DECIMAL(15,2)
) RETURNS TABLE(
  contribution_percentage DECIMAL(5,4),
  monthly_value DECIMAL(15,2),
  stability_status TEXT
) AS $$
DECLARE
  v_contribution_percentage DECIMAL(5,4);
  v_monthly_value DECIMAL(15,2);
  v_stability_status TEXT;
  v_recent_data_count INTEGER;
BEGIN
  -- 计算贡献百分比
  IF p_current_value <= p_baseline_value THEN
    v_contribution_percentage := 0;
  ELSE
    v_contribution_percentage := (p_current_value - p_baseline_value) / p_current_value;
    -- 最小贡献5%
    IF v_contribution_percentage < 0.05 THEN
      v_contribution_percentage := 0.05;
    END IF;
  END IF;
  
  -- 计算月度价值
  v_monthly_value := (p_annual_revenue * v_contribution_percentage) / 12;
  
  -- 检查稳定性状态
  SELECT COUNT(*) INTO v_recent_data_count
  FROM capability_value_assessment
  WHERE capability_id = p_capability_id
    AND month_date >= CURRENT_DATE - INTERVAL '6 months'
    AND metric_value >= p_target_value;
  
  IF v_recent_data_count < 6 THEN
    v_stability_status := 'pending';
  ELSIF v_recent_data_count = 6 THEN
    v_stability_status := 'stable';
  ELSE
    v_stability_status := 'unstable';
  END IF;
  
  RETURN QUERY SELECT v_contribution_percentage, v_monthly_value, v_stability_status;
END;
$$ LANGUAGE plpgsql;
```

## 📊 具体能力类型计算

### 1. 生产能力计算

```typescript
// 生产能力价值计算
class ProductionCapabilityCalculator extends CapabilityValueCalculator {
  /**
   * 计算生产能力价值
   */
  async calculateProductionValue(
    capabilityId: string,
    qualityRate: number, // 质量合格率
    baselineQualityRate: number, // 基准合格率
    annualRevenue: number
  ): Promise<CapabilityValueCalculation> {
    const stableOutcome: StableOutcome = {
      metric: '质量合格率',
      currentValue: qualityRate,
      baselineValue: baselineQualityRate,
      targetValue: 0.96, // 96%目标
      unit: '%',
      measurementPeriod: 6
    };
    
    return await this.calculateCapabilityValue(capabilityId, stableOutcome, annualRevenue);
  }
  
  /**
   * 计算返工成本节省
   */
  private calculateReworkCostSaving(qualityRate: number, baselineRate: number, totalCost: number): number {
    const improvement = qualityRate - baselineRate;
    return totalCost * improvement; // 返工成本节省
  }
  
  /**
   * 计算复购增量
   */
  private calculateRepurchaseIncrement(qualityRate: number, baselineRate: number, customerBase: number, avgOrderValue: number): number {
    const improvement = qualityRate - baselineRate;
    const repurchaseRate = improvement * 0.1; // 假设质量提升10%带来1%复购率提升
    return customerBase * repurchaseRate * avgOrderValue;
  }
}
```

### 2. 研发能力计算

```typescript
// 研发能力价值计算
class RDCapabilityCalculator extends CapabilityValueCalculator {
  /**
   * 计算研发能力价值
   */
  async calculateRDValue(
    capabilityId: string,
    timeToMarket: number, // 上市周期（月）
    baselineTimeToMarket: number, // 基准上市周期
    annualRevenue: number
  ): Promise<CapabilityValueCalculation> {
    const stableOutcome: StableOutcome = {
      metric: '上市周期',
      currentValue: timeToMarket,
      baselineValue: baselineTimeToMarket,
      targetValue: 12, // 12个月目标
      unit: '月',
      measurementPeriod: 6
    };
    
    return await this.calculateCapabilityValue(capabilityId, stableOutcome, annualRevenue);
  }
  
  /**
   * 计算提前上市收益
   */
  private calculateEarlyMarketRevenue(
    timeToMarket: number,
    baselineTimeToMarket: number,
    monthlyRevenue: number
  ): number {
    const monthsSaved = baselineTimeToMarket - timeToMarket;
    return monthsSaved * monthlyRevenue;
  }
  
  /**
   * 计算专利授权费
   */
  private calculatePatentLicenseFee(patentCount: number, avgLicenseFee: number): number {
    return patentCount * avgLicenseFee;
  }
}
```

### 3. 播传能力计算

```typescript
// 播传能力价值计算
class MarketingCapabilityCalculator extends CapabilityValueCalculator {
  /**
   * 计算播传能力价值
   */
  async calculateMarketingValue(
    capabilityId: string,
    conversionRate: number, // 转化率
    baselineConversionRate: number, // 基准转化率
    annualRevenue: number
  ): Promise<CapabilityValueCalculation> {
    const stableOutcome: StableOutcome = {
      metric: '转化率',
      currentValue: conversionRate,
      baselineValue: baselineConversionRate,
      targetValue: 0.28, // 28%目标
      unit: '%',
      measurementPeriod: 6
    };
    
    return await this.calculateCapabilityValue(capabilityId, stableOutcome, annualRevenue);
  }
  
  /**
   * 计算获客成本节省
   */
  private calculateCustomerAcquisitionCostSaving(
    conversionRate: number,
    baselineRate: number,
    marketingBudget: number
  ): number {
    const improvement = conversionRate - baselineRate;
    return marketingBudget * improvement; // 转化率提升带来的成本节省
  }
  
  /**
   * 计算转化增量
   */
  private calculateConversionIncrement(
    conversionRate: number,
    baselineRate: number,
    traffic: number,
    avgOrderValue: number
  ): number {
    const improvement = conversionRate - baselineRate;
    return traffic * improvement * avgOrderValue;
  }
}
```

## 🔄 稳定性判定算法

### 1. 连续稳定性检查

```typescript
// 稳定性判定器
class StabilityChecker {
  private readonly STABILITY_MONTHS = 6;
  private readonly STABILITY_THRESHOLD = 0.95; // 95%稳定性阈值

  /**
   * 检查能力稳定性
   */
  async checkCapabilityStability(
    capabilityId: string,
    metricType: string,
    targetValue: number
  ): Promise<StabilityResult> {
    // 1. 获取最近6个月数据
    const recentData = await this.getRecentCapabilityData(capabilityId, this.STABILITY_MONTHS);
    
    // 2. 计算稳定性指标
    const stabilityMetrics = this.calculateStabilityMetrics(recentData, targetValue);
    
    // 3. 判定稳定性状态
    const stabilityStatus = this.determineStabilityStatus(stabilityMetrics);
    
    return {
      capabilityId,
      metricType,
      targetValue,
      stabilityStatus,
      stabilityMetrics,
      recommendation: this.generateRecommendation(stabilityStatus, stabilityMetrics)
    };
  }

  /**
   * 计算稳定性指标
   */
  private calculateStabilityMetrics(data: CapabilityData[], targetValue: number): StabilityMetrics {
    const totalMonths = data.length;
    const达标Months = data.filter(d => d.metricValue >= targetValue).length;
    const达标率 = 达标Months / totalMonths;
    
    const values = data.map(d => d.metricValue);
    const平均值 = values.reduce((sum, val) => sum + val, 0) / values.length;
    const标准差 = this.calculateStandardDeviation(values);
    const变异系数 = 标准差 / 平均值;
    
    return {
      totalMonths,
      达标Months,
      达标率,
      平均值,
      标准差,
      变异系数,
      isStable: 达标率 >= this.STABILITY_THRESHOLD
    };
  }

  /**
   * 判定稳定性状态
   */
  private determineStabilityStatus(metrics: StabilityMetrics): 'stable' | 'unstable' | 'pending' {
    if (metrics.totalMonths < this.STABILITY_MONTHS) {
      return 'pending';
    }
    
    if (metrics.isStable && metrics.变异系数 < 0.1) {
      return 'stable';
    }
    
    return 'unstable';
  }
}
```

### 2. 数据库稳定性检查

```sql
-- 能力稳定性检查函数
CREATE OR REPLACE FUNCTION check_capability_stability(
  p_capability_id UUID,
  p_metric_type TEXT,
  p_target_value DECIMAL(10,4)
) RETURNS TABLE(
  stability_status TEXT,
 达标率 DECIMAL(5,4),
 平均值 DECIMAL(10,4),
 标准差 DECIMAL(10,4),
 变异系数 DECIMAL(10,4)
) AS $$
DECLARE
  v_total_months INTEGER;
  v_达标_months INTEGER;
  v_达标率 DECIMAL(5,4);
  v_平均值 DECIMAL(10,4);
  v_标准差 DECIMAL(10,4);
  v_变异系数 DECIMAL(10,4);
  v_stability_status TEXT;
BEGIN
  -- 获取最近6个月数据
  SELECT COUNT(*), COUNT(CASE WHEN metric_value >= p_target_value THEN 1 END)
  INTO v_total_months, v_达标_months
  FROM capability_value_assessment
  WHERE capability_id = p_capability_id
    AND month_date >= CURRENT_DATE - INTERVAL '6 months';
  
  -- 计算达标率
  IF v_total_months > 0 THEN
    v_达标率 := v_达标_months::DECIMAL / v_total_months;
  ELSE
    v_达标率 := 0;
  END IF;
  
  -- 计算平均值
  SELECT AVG(metric_value) INTO v_平均值
  FROM capability_value_assessment
  WHERE capability_id = p_capability_id
    AND month_date >= CURRENT_DATE - INTERVAL '6 months';
  
  -- 计算标准差
  SELECT STDDEV(metric_value) INTO v_标准差
  FROM capability_value_assessment
  WHERE capability_id = p_capability_id
    AND month_date >= CURRENT_DATE - INTERVAL '6 months';
  
  -- 计算变异系数
  IF v_平均值 > 0 THEN
    v_变异系数 := v_标准差 / v_平均值;
  ELSE
    v_变异系数 := 0;
  END IF;
  
  -- 判定稳定性状态
  IF v_total_months < 6 THEN
    v_stability_status := 'pending';
  ELSIF v_达标率 >= 0.95 AND v_变异系数 < 0.1 THEN
    v_stability_status := 'stable';
  ELSE
    v_stability_status := 'unstable';
  END IF;
  
  RETURN QUERY SELECT v_stability_status, v_达标率, v_平均值, v_标准差, v_变异系数;
END;
$$ LANGUAGE plpgsql;
```

## 📈 性能优化

### 1. 批量计算

```typescript
// 批量能力价值计算
class BatchCapabilityCalculator {
  private batchSize = 5;
  private batchTimeout = 500; // 0.5秒

  /**
   * 批量计算多个能力价值
   */
  async batchCalculateCapabilityValues(
    capabilities: CapabilityValueInput[]
  ): Promise<CapabilityValueCalculation[]> {
    const results: CapabilityValueCalculation[] = [];
    
    for (let i = 0; i < capabilities.length; i += this.batchSize) {
      const batch = capabilities.slice(i, i + this.batchSize);
      const batchResults = await Promise.all(
        batch.map(capability => this.calculateSingleCapabilityValue(capability))
      );
      results.push(...batchResults);
      
      // 避免阻塞，让出控制权
      if (i + this.batchSize < capabilities.length) {
        await this.delay(this.batchTimeout);
      }
    }
    
    return results;
  }
}
```

### 2. 缓存策略

```typescript
// 能力价值计算缓存
class CapabilityValueCache {
  private cache = new Map<string, any>();
  private ttl = 1800000; // 30分钟

  /**
   * 获取缓存的能力价值计算结果
   */
  get(capabilityId: string, inputs: any): CapabilityValueCalculation | null {
    const key = this.generateCacheKey(capabilityId, inputs);
    const item = this.cache.get(key);
    
    if (!item || Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }

  /**
   * 缓存能力价值计算结果
   */
  set(capabilityId: string, inputs: any, result: CapabilityValueCalculation): void {
    const key = this.generateCacheKey(capabilityId, inputs);
    this.cache.set(key, {
      value: result,
      expires: Date.now() + this.ttl
    });
  }
}
```

## 🚀 实施计划

### 阶段1：基础算法实现（Week 1）
1. **TypeScript计算器**：实现CapabilityValueCalculator类
2. **数据库函数**：实现calculate_capability_value函数
3. **稳定性检查**：实现稳定性判定算法

### 阶段2：具体能力类型（Week 2）
1. **生产能力**：实现生产质量合格率计算
2. **研发能力**：实现上市周期计算
3. **播传能力**：实现转化率计算

### 阶段3：性能优化（Week 3）
1. **批量计算**：实现批量能力价值计算
2. **缓存策略**：实现计算结果缓存
3. **性能测试**：验证性能指标

---

**本算法设计确保能力价值计算的准确性和灵活性，支持多种能力类型和稳定性判定，满足100家企业的计算需求。**
