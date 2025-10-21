# 资产NPV折现算法设计

## 📋 算法概述

基于用户澄清，资产现金流预测由**人工保证准确性**，系统提供NPV计算功能。算法实现未来5年现金流增量现值的计算，并分摊至月度增量。

## 🎯 用户说明指引

### 什么是资产NPV计算？
资产NPV（净现值）计算是评估资产价值的重要方法。它通过计算资产未来5年带来的现金流增量，并折现到当前时点，得出资产的真实价值。

### 为什么需要NPV计算？
- **资产价值量化**：将抽象的资产转化为具体的货币价值
- **投资决策支持**：帮助判断资产投资是否值得
- **资源优化配置**：为资产配置提供数据支持

### 计算步骤说明
1. **收集历史数据**：获取无该资产时的历史平均现金流（基准现金流）
2. **预测未来现金流**：预测有该资产后未来5年的现金流
3. **计算现金流增量**：未来现金流 - 基准现金流
4. **折现计算**：将未来现金流按8%折现率折现到当前
5. **月度分摊**：将5年NPV分摊到60个月

### 数据来源说明
- **基准现金流**：来自ERP财务模块，2022-2024年无该资产时的平均现金流
- **未来现金流**：由财务部门预测，基于资产投入后的预期收益
- **折现率**：使用企业WACC（加权平均资本成本），默认8%

### 使用场景
- **新资产投资评估**：评估新设备、技术、品牌等投资价值
- **资产价值监控**：定期评估现有资产价值变化
- **投资组合优化**：比较不同资产的投资价值

## 🎯 核心公式

### 1. 现金流增量计算
```
第n年现金流增量 = 当年有资产现金流 - 历史基准现金流
```

### 2. NPV现值计算
```
NPV = Σ(第n年现金流增量 × 折现系数)
其中：折现系数 = 1/(1+r)^n
r = 企业WACC（加权平均资本成本）= 8%
n = 1,2,3,4,5年
```

### 3. 月度资产增量计算
```
月度资产增量 = NPV ÷ 60
（5年 = 60个月，分摊至月度）
```

## 🔧 算法实现

### 1. TypeScript实现

```typescript
// 资产NPV计算接口
interface AssetNPVCalculation {
  assetId: string;
  baselineYear: number;
  baselineCashflow: number;
  year1to5Cashflows: number[];
  discountRate: number;
  npvTotal: number;
  monthlyAssetDelta: number;
  calculationDate: Date;
}

// 资产NPV计算器
class AssetNPVCalculator {
  private readonly MONTHS_PER_YEAR = 12;
  private readonly PROJECTION_YEARS = 5;
  private readonly DEFAULT_DISCOUNT_RATE = 0.08;

  /**
   * 计算资产NPV和月度增量
   * @param assetId 资产ID
   * @param baselineCashflow 基准现金流（无该资产时）
   * @param year1to5Cashflows 未来5年现金流预测
   * @param discountRate 折现率（默认8%）
   * @returns NPV计算结果
   */
  async calculateAssetNPV(
    assetId: string,
    baselineCashflow: number,
    year1to5Cashflows: number[],
    discountRate: number = this.DEFAULT_DISCOUNT_RATE
  ): Promise<AssetNPVCalculation> {
    // 1. 验证输入数据
    this.validateInputs(baselineCashflow, year1to5Cashflows, discountRate);
    
    // 2. 计算现金流增量
    const cashflowIncrements = this.calculateCashflowIncrements(
      baselineCashflow, 
      year1to5Cashflows
    );
    
    // 3. 计算NPV现值
    const npvTotal = this.calculateNPV(cashflowIncrements, discountRate);
    
    // 4. 计算月度资产增量
    const monthlyAssetDelta = this.calculateMonthlyDelta(npvTotal);
    
    return {
      assetId,
      baselineYear: new Date().getFullYear(),
      baselineCashflow,
      year1to5Cashflows,
      discountRate,
      npvTotal,
      monthlyAssetDelta,
      calculationDate: new Date()
    };
  }

  /**
   * 计算现金流增量
   */
  private calculateCashflowIncrements(
    baselineCashflow: number,
    year1to5Cashflows: number[]
  ): number[] {
    return year1to5Cashflows.map(cashflow => 
      cashflow - baselineCashflow
    );
  }

  /**
   * 计算NPV现值
   */
  private calculateNPV(
    cashflowIncrements: number[],
    discountRate: number
  ): number {
    let npv = 0;
    
    for (let year = 1; year <= this.PROJECTION_YEARS; year++) {
      const discountFactor = 1 / Math.pow(1 + discountRate, year);
      const presentValue = cashflowIncrements[year - 1] * discountFactor;
      npv += presentValue;
    }
    
    return npv;
  }

  /**
   * 计算月度资产增量
   */
  private calculateMonthlyDelta(npvTotal: number): number {
    return npvTotal / (this.PROJECTION_YEARS * this.MONTHS_PER_YEAR);
  }

  /**
   * 验证输入数据
   */
  private validateInputs(
    baselineCashflow: number,
    year1to5Cashflows: number[],
    discountRate: number
  ): void {
    if (baselineCashflow < 0) {
      throw new Error('基准现金流不能为负数');
    }
    
    if (year1to5Cashflows.length !== this.PROJECTION_YEARS) {
      throw new Error(`现金流预测必须包含${this.PROJECTION_YEARS}年数据`);
    }
    
    if (year1to5Cashflows.some(cashflow => cashflow < 0)) {
      throw new Error('现金流预测不能为负数');
    }
    
    if (discountRate <= 0 || discountRate >= 1) {
      throw new Error('折现率必须在0-1之间');
    }
  }
}
```

### 2. 数据库存储

```sql
-- 资产NPV计算结果存储
CREATE OR REPLACE FUNCTION calculate_asset_npv(
  p_asset_id UUID,
  p_baseline_cashflow DECIMAL(15,2),
  p_year1_cashflow DECIMAL(15,2),
  p_year2_cashflow DECIMAL(15,2),
  p_year3_cashflow DECIMAL(15,2),
  p_year4_cashflow DECIMAL(15,2),
  p_year5_cashflow DECIMAL(15,2),
  p_discount_rate DECIMAL(5,4) DEFAULT 0.08
) RETURNS TABLE(
  npv_total DECIMAL(15,2),
  monthly_delta DECIMAL(15,2)
) AS $$
DECLARE
  v_npv_total DECIMAL(15,2) := 0;
  v_monthly_delta DECIMAL(15,2);
  v_discount_factor DECIMAL(10,6);
  v_present_value DECIMAL(15,2);
  v_cashflow_increment DECIMAL(15,2);
BEGIN
  -- 计算第1年NPV
  v_cashflow_increment := p_year1_cashflow - p_baseline_cashflow;
  v_discount_factor := 1 / POWER(1 + p_discount_rate, 1);
  v_present_value := v_cashflow_increment * v_discount_factor;
  v_npv_total := v_npv_total + v_present_value;
  
  -- 计算第2年NPV
  v_cashflow_increment := p_year2_cashflow - p_baseline_cashflow;
  v_discount_factor := 1 / POWER(1 + p_discount_rate, 2);
  v_present_value := v_cashflow_increment * v_discount_factor;
  v_npv_total := v_npv_total + v_present_value;
  
  -- 计算第3年NPV
  v_cashflow_increment := p_year3_cashflow - p_baseline_cashflow;
  v_discount_factor := 1 / POWER(1 + p_discount_rate, 3);
  v_present_value := v_cashflow_increment * v_discount_factor;
  v_npv_total := v_npv_total + v_present_value;
  
  -- 计算第4年NPV
  v_cashflow_increment := p_year4_cashflow - p_baseline_cashflow;
  v_discount_factor := 1 / POWER(1 + p_discount_rate, 4);
  v_present_value := v_cashflow_increment * v_discount_factor;
  v_npv_total := v_npv_total + v_present_value;
  
  -- 计算第5年NPV
  v_cashflow_increment := p_year5_cashflow - p_baseline_cashflow;
  v_discount_factor := 1 / POWER(1 + p_discount_rate, 5);
  v_present_value := v_cashflow_increment * v_discount_factor;
  v_npv_total := v_npv_total + v_present_value;
  
  -- 计算月度增量
  v_monthly_delta := v_npv_total / 60; -- 5年 = 60个月
  
  RETURN QUERY SELECT v_npv_total, v_monthly_delta;
END;
$$ LANGUAGE plpgsql;
```

## 📊 Excel示例计算

### 示例数据
| 项目 | 数值 | 说明 |
|------|------|------|
| 基准现金流 | 1,000,000 | 无该资产时的历史平均现金流 |
| 第1年现金流 | 1,800,000 | 有该资产后的预测现金流 |
| 第2年现金流 | 1,900,000 | 有该资产后的预测现金流 |
| 第3年现金流 | 1,950,000 | 有该资产后的预测现金流 |
| 第4年现金流 | 1,850,000 | 有该资产后的预测现金流 |
| 第5年现金流 | 1,750,000 | 有该资产后的预测现金流 |
| 折现率 | 8% | 企业WACC |

### 手工计算过程

#### 第1年计算
```
现金流增量 = 1,800,000 - 1,000,000 = 800,000
折现系数 = 1/(1+0.08)^1 = 0.926
现值 = 800,000 × 0.926 = 740,800
```

#### 第2年计算
```
现金流增量 = 1,900,000 - 1,000,000 = 900,000
折现系数 = 1/(1+0.08)^2 = 0.857
现值 = 900,000 × 0.857 = 771,300
```

#### 第3年计算
```
现金流增量 = 1,950,000 - 1,000,000 = 950,000
折现系数 = 1/(1+0.08)^3 = 0.794
现值 = 950,000 × 0.794 = 754,300
```

#### 第4年计算
```
现金流增量 = 1,850,000 - 1,000,000 = 850,000
折现系数 = 1/(1+0.08)^4 = 0.735
现值 = 850,000 × 0.735 = 624,750
```

#### 第5年计算
```
现金流增量 = 1,750,000 - 1,000,000 = 750,000
折现系数 = 1/(1+0.08)^5 = 0.681
现值 = 750,000 × 0.681 = 510,750
```

#### 总NPV计算
```
NPV = 740,800 + 771,300 + 754,300 + 624,750 + 510,750 = 3,401,900
```

#### 月度资产增量
```
月度资产增量 = 3,401,900 ÷ 60 = 56,698.33
```

## 🔄 版本控制集成

### 1. 版本创建逻辑

```typescript
// 资产NPV版本管理
class AssetNPVVersionManager {
  /**
   * 创建新版本
   */
  async createNewVersion(
    assetId: string,
    npvData: AssetNPVCalculation,
    versionType: 'annual' | 'major_change' | 'manual',
    reason: string,
    userId: string
  ): Promise<string> {
    // 1. 获取当前版本号
    const currentVersion = await this.getCurrentVersion(assetId);
    const newVersionNumber = currentVersion + 1;
    
    // 2. 将当前版本标记为归档
    await this.archiveCurrentVersion(assetId);
    
    // 3. 创建新版本
    const versionId = await this.createVersion({
      assetId,
      versionNumber: newVersionNumber,
      versionType,
      versionReason: reason,
      ...npvData,
      isCurrent: true,
      createdBy: userId
    });
    
    // 4. 记录版本历史
    await this.recordVersionHistory(assetId, versionId, 'created', reason, null, npvData, userId);
    
    return versionId;
  }
  
  /**
   * 获取版本历史
   */
  async getVersionHistory(assetId: string): Promise<VersionHistory[]> {
    return await db.query(`
      SELECT 
        v.version_number,
        v.version_type,
        v.version_reason,
        v.npv_total,
        v.monthly_asset_delta,
        v.is_current,
        v.created_at,
        u.user_name as created_by_name
      FROM asset_cashflow_projection_versions v
      LEFT JOIN users u ON v.created_by = u.user_id
      WHERE v.asset_id = $1
      ORDER BY v.version_number DESC
    `, [assetId]);
  }
}
```

### 2. 版本对比分析

```typescript
// 版本对比分析
class AssetNPVVersionComparison {
  /**
   * 对比两个版本
   */
  async compareVersions(
    assetId: string,
    version1: number,
    version2: number
  ): Promise<VersionComparison> {
    const v1 = await this.getVersion(assetId, version1);
    const v2 = await this.getVersion(assetId, version2);
    
    return {
      assetId,
      version1: v1.version_number,
      version2: v2.version_number,
      differences: {
        npvChange: v2.npv_total - v1.npv_total,
        npvChangePercent: ((v2.npv_total - v1.npv_total) / v1.npv_total) * 100,
        monthlyDeltaChange: v2.monthly_asset_delta - v1.monthly_asset_delta,
        cashflowChanges: this.compareCashflows(v1, v2)
      },
      impact: this.calculateImpact(v1, v2)
    };
  }
  
  /**
   * 计算影响
   */
  private calculateImpact(v1: any, v2: any): ImpactAnalysis {
    const npvChange = v2.npv_total - v1.npv_total;
    const monthlyChange = v2.monthly_asset_delta - v1.monthly_asset_delta;
    
    return {
      npvImpact: {
        absolute: npvChange,
        relative: (npvChange / v1.npv_total) * 100,
        significance: Math.abs(npvChange) > v1.npv_total * 0.1 ? 'high' : 'low'
      },
      monthlyImpact: {
        absolute: monthlyChange,
        relative: (monthlyChange / v1.monthly_asset_delta) * 100,
        significance: Math.abs(monthlyChange) > v1.monthly_asset_delta * 0.1 ? 'high' : 'low'
      },
      recommendations: this.generateRecommendations(npvChange, monthlyChange)
    };
  }
}
```

## 📈 性能优化

### 1. 批量计算

```typescript
// 批量NPV计算
class BatchNPVCalculator {
  private batchSize = 10;
  private batchTimeout = 1000; // 1秒
  
  /**
   * 批量计算多个资产的NPV
   */
  async batchCalculateNPV(assets: AssetNPVInput[]): Promise<AssetNPVCalculation[]> {
    const results: AssetNPVCalculation[] = [];
    
    for (let i = 0; i < assets.length; i += this.batchSize) {
      const batch = assets.slice(i, i + this.batchSize);
      const batchResults = await Promise.all(
        batch.map(asset => this.calculateSingleNPV(asset))
      );
      results.push(...batchResults);
      
      // 避免阻塞，让出控制权
      if (i + this.batchSize < assets.length) {
        await this.delay(10);
      }
    }
    
    return results;
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 2. 缓存策略

```typescript
// NPV计算缓存
class NPVCalculationCache {
  private cache = new Map<string, any>();
  private ttl = 3600000; // 1小时
  
  /**
   * 获取缓存的NPV计算结果
   */
  get(assetId: string, inputs: any): AssetNPVCalculation | null {
    const key = this.generateCacheKey(assetId, inputs);
    const item = this.cache.get(key);
    
    if (!item || Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  /**
   * 缓存NPV计算结果
   */
  set(assetId: string, inputs: any, result: AssetNPVCalculation): void {
    const key = this.generateCacheKey(assetId, inputs);
    this.cache.set(key, {
      value: result,
      expires: Date.now() + this.ttl
    });
  }
  
  private generateCacheKey(assetId: string, inputs: any): string {
    const inputsHash = this.hashInputs(inputs);
    return `${assetId}_${inputsHash}`;
  }
}
```

## 🚀 实施计划

### 阶段1：基础算法实现（Week 1）
1. **TypeScript计算器**：实现AssetNPVCalculator类
2. **数据库函数**：实现calculate_asset_npv函数
3. **单元测试**：验证算法正确性

### 阶段2：版本控制集成（Week 2）
1. **版本管理**：实现版本创建和历史查询
2. **版本对比**：实现版本差异分析
3. **影响分析**：实现影响评估和推荐

### 阶段3：性能优化（Week 3）
1. **批量计算**：实现批量NPV计算
2. **缓存策略**：实现计算结果缓存
3. **性能测试**：验证性能指标

---

**本算法设计确保资产NPV计算的准确性和效率，支持版本控制和性能优化，满足100家企业的计算需求。**
