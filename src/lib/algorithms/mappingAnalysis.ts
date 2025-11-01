/**
 * 映射匹配度分析算法实现
 * 产品特性-客户价值映射分析
 */

export interface ProductCharacteristic {
  characteristicId: string;
  characteristicName: string;
  characteristicValue: number;
  characteristicType: 'performance' | 'quality' | 'price' | 'service' | 'innovation';
  importance: number;
  cost: number;
}

export interface CustomerValue {
  valueId: string;
  valueName: string;
  valueImportance: number;
  valueType: 'must_have' | 'one_dimensional' | 'attractive' | 'indifferent' | 'reverse';
  satisfaction: number;
  dissatisfaction: number;
}

export interface MappingResult {
  productCharacteristic: string;
  customerValue: string;
  mappingStrength: number;
  correlationCoefficient: number;
  significance: boolean;
  kanoCategory: string;
  optimizationPotential: number;
}

export interface MappingAnalysisResult {
  success: boolean;
  mappingResults: MappingResult[];
  overallMappingScore: number;
  mappingRecommendations: string[];
  kanoAnalysis: {
    categories: {
      must_have: string[];
      one_dimensional: string[];
      attractive: string[];
      indifferent: string[];
      reverse: string[];
    };
    optimizationPriorities: {
      characteristic: string;
      priority: number;
      reason: string;
    }[];
  };
}

/**
 * 产品特性-客户价值映射分析器
 */
export class ProductCustomerMappingAnalyzer {
  private correlationThreshold: number = 0.7;
  private significanceLevel: number = 0.05;

  constructor(config?: {
    correlationThreshold?: number;
    significanceLevel?: number;
  }) {
    if (config) {
      this.correlationThreshold = config.correlationThreshold || this.correlationThreshold;
      this.significanceLevel = config.significanceLevel || this.significanceLevel;
    }
  }

  /**
   * 计算映射强度
   */
  async calculateMappingStrength(
    productCharacteristics: ProductCharacteristic[],
    customerValues: CustomerValue[]
  ): Promise<MappingAnalysisResult> {
    try {
      // 验证输入数据
      this.validateInputData(productCharacteristics, customerValues);
      
      // 计算映射结果
      const mappingResults = this.calculateMappingResults(productCharacteristics, customerValues);
      
      // 计算整体映射分数
      const overallMappingScore = this.calculateOverallMappingScore(mappingResults);
      
      // 生成映射建议
      const mappingRecommendations = this.generateMappingRecommendations(mappingResults);
      
      // 进行卡诺模型分析
      const kanoAnalysis = this.performKanoAnalysis(mappingResults);
      
      return {
        success: true,
        mappingResults,
        overallMappingScore,
        mappingRecommendations,
        kanoAnalysis
      };
      
    } catch (error) {
      return {
        success: false,
        mappingResults: [],
        overallMappingScore: 0,
        mappingRecommendations: [],
        kanoAnalysis: {
          categories: {
            must_have: [],
            one_dimensional: [],
            attractive: [],
            indifferent: [],
            reverse: []
          },
          optimizationPriorities: []
        }
      };
    }
  }

  /**
   * 验证输入数据
   */
  private validateInputData(
    productCharacteristics: ProductCharacteristic[],
    customerValues: CustomerValue[]
  ): void {
    if (productCharacteristics.length === 0) {
      throw new Error('产品特性数据不能为空');
    }
    
    if (customerValues.length === 0) {
      throw new Error('客户价值数据不能为空');
    }
    
    // 验证产品特性数据
    for (const characteristic of productCharacteristics) {
      if (characteristic.characteristicValue < 0 || characteristic.characteristicValue > 1) {
        throw new Error(`产品特性 ${characteristic.characteristicName} 的值必须在0-1之间`);
      }
      if (characteristic.importance < 0 || characteristic.importance > 1) {
        throw new Error(`产品特性 ${characteristic.characteristicName} 的重要性必须在0-1之间`);
      }
    }
    
    // 验证客户价值数据
    for (const value of customerValues) {
      if (value.valueImportance < 0 || value.valueImportance > 1) {
        throw new Error(`客户价值 ${value.valueName} 的重要性必须在0-1之间`);
      }
      if (value.satisfaction < 0 || value.satisfaction > 1) {
        throw new Error(`客户价值 ${value.valueName} 的满意度必须在0-1之间`);
      }
    }
  }

  /**
   * 计算映射结果
   */
  private calculateMappingResults(
    productCharacteristics: ProductCharacteristic[],
    customerValues: CustomerValue[]
  ): MappingResult[] {
    const mappingResults: MappingResult[] = [];
    
    for (const characteristic of productCharacteristics) {
      for (const value of customerValues) {
        // 计算映射强度
        const mappingStrength = this.calculateMappingStrengthValue(characteristic, value);
        
        // 计算相关系数
        const correlationCoefficient = this.calculateCorrelationCoefficient(characteristic, value);
        
        // 计算显著性
        const significance = this.calculateSignificance(correlationCoefficient, productCharacteristics.length);
        
        // 确定卡诺类别
        const kanoCategory = this.determineKanoCategory(characteristic, value);
        
        // 计算优化潜力
        const optimizationPotential = this.calculateOptimizationPotential(characteristic, value, mappingStrength);
        
        mappingResults.push({
          productCharacteristic: characteristic.characteristicName,
          customerValue: value.valueName,
          mappingStrength,
          correlationCoefficient,
          significance,
          kanoCategory,
          optimizationPotential
        });
      }
    }
    
    return mappingResults;
  }

  /**
   * 计算映射强度值
   */
  private calculateMappingStrengthValue(
    characteristic: ProductCharacteristic,
    value: CustomerValue
  ): number {
    // 基础映射强度 = 特性值 × 价值重要性
    const baseMappingStrength = characteristic.characteristicValue * value.valueImportance;
    
    // 特性重要性调整
    const importanceAdjustment = characteristic.importance;
    
    // 价值类型调整
    const valueTypeAdjustment = this.getValueTypeAdjustment(value.valueType);
    
    // 计算最终映射强度
    const mappingStrength = baseMappingStrength * 
      (0.5 * importanceAdjustment + 0.3 * valueTypeAdjustment + 0.2);
    
    return Math.min(1, Math.max(0, mappingStrength));
  }

  /**
   * 获取价值类型调整系数
   */
  private getValueTypeAdjustment(valueType: string): number {
    const adjustments: Record<string, number> = {
      'must_have': 1.0,
      'one_dimensional': 0.8,
      'attractive': 0.6,
      'indifferent': 0.3,
      'reverse': 0.1
    };
    
    return adjustments[valueType] || 0.5;
  }

  /**
   * 计算相关系数
   */
  private calculateCorrelationCoefficient(
    characteristic: ProductCharacteristic,
    value: CustomerValue
  ): number {
    // 基于特性类型和价值类型的匹配度
    const typeMatch = this.getTypeMatchScore(characteristic.characteristicType, value.valueName);
    
    // 基于数值的相关系数
    const valueCorrelation = Math.abs(characteristic.characteristicValue - value.valueImportance);
    
    // 综合相关系数
    const correlationCoefficient = typeMatch * (1 - valueCorrelation);
    
    return Math.min(1, Math.max(0, correlationCoefficient));
  }

  /**
   * 获取类型匹配分数
   */
  private getTypeMatchScore(characteristicType: string, valueName: string): number {
    const matchMatrix: Record<string, Record<string, number>> = {
      'performance': {
        '性能': 0.9,
        '速度': 0.8,
        '效率': 0.9,
        '可靠性': 0.7
      },
      'quality': {
        '质量': 0.9,
        '可靠性': 0.8,
        '耐用性': 0.9,
        '稳定性': 0.8
      },
      'price': {
        '价格': 0.9,
        '性价比': 0.8,
        '成本': 0.9,
        '经济性': 0.8
      },
      'service': {
        '服务': 0.9,
        '支持': 0.8,
        '响应': 0.7,
        '帮助': 0.8
      },
      'innovation': {
        '创新': 0.9,
        '新颖': 0.8,
        '独特': 0.9,
        '先进': 0.8
      }
    };
    
    return matchMatrix[characteristicType]?.[valueName] || 0.5;
  }

  /**
   * 计算显著性
   */
  private calculateSignificance(correlationCoefficient: number, sampleSize: number): boolean {
    // 简化的显著性检验
    const criticalValue = 1.96 / Math.sqrt(sampleSize - 2);
    return Math.abs(correlationCoefficient) > criticalValue;
  }

  /**
   * 确定卡诺类别
   */
  private determineKanoCategory(
    characteristic: ProductCharacteristic,
    value: CustomerValue
  ): string {
    // 基于满意度和不满意度确定卡诺类别
    const satisfaction = value.satisfaction;
    const dissatisfaction = value.dissatisfaction;
    
    if (satisfaction > 0.8 && dissatisfaction > 0.8) {
      return 'one_dimensional';
    } else if (satisfaction > 0.8 && dissatisfaction < 0.3) {
      return 'attractive';
    } else if (satisfaction < 0.3 && dissatisfaction > 0.8) {
      return 'must_have';
    } else if (satisfaction < 0.3 && dissatisfaction < 0.3) {
      return 'indifferent';
    } else {
      return 'reverse';
    }
  }

  /**
   * 计算优化潜力
   */
  private calculateOptimizationPotential(
    characteristic: ProductCharacteristic,
    value: CustomerValue,
    mappingStrength: number
  ): number {
    // 优化潜力 = (1 - 当前映射强度) × 特性重要性 × 价值重要性
    const characteristicImportance = characteristic.importance;
    const valueImportance = value.valueImportance;
    
    return (1 - mappingStrength) * characteristicImportance * valueImportance;
  }

  /**
   * 计算整体映射分数
   */
  private calculateOverallMappingScore(mappingResults: MappingResult[]): number {
    if (mappingResults.length === 0) return 0;
    
    // 计算加权平均映射强度
    const totalMappingStrength = mappingResults.reduce(
      (sum, result) => sum + result.mappingStrength, 
      0
    );
    
    const averageMappingStrength = totalMappingStrength / mappingResults.length;
    
    // 计算显著性权重
    const significantResults = mappingResults.filter(result => result.significance);
    const significanceWeight = significantResults.length / mappingResults.length;
    
    // 整体映射分数 = 平均映射强度 × 显著性权重
    return averageMappingStrength * (0.7 + 0.3 * significanceWeight);
  }

  /**
   * 生成映射建议
   */
  private generateMappingRecommendations(mappingResults: MappingResult[]): string[] {
    const recommendations: string[] = [];
    
    // 分析映射强度
    const strongMappings = mappingResults.filter(r => r.mappingStrength > 0.8);
    const weakMappings = mappingResults.filter(r => r.mappingStrength < 0.3);
    
    if (strongMappings.length > 0) {
      recommendations.push('加强映射强度高的产品特性-客户价值组合');
    }
    
    if (weakMappings.length > 0) {
      recommendations.push('优化映射强度低的产品特性-客户价值组合');
    }
    
    // 基于优化潜力生成建议
    const highPotentialMappings = mappingResults.filter(r => r.optimizationPotential > 0.5);
    if (highPotentialMappings.length > 0) {
      recommendations.push('重点关注高优化潜力的产品特性-客户价值组合');
    }
    
    return recommendations;
  }

  /**
   * 进行卡诺模型分析
   */
  private performKanoAnalysis(mappingResults: MappingResult[]): {
    categories: {
      must_have: string[];
      one_dimensional: string[];
      attractive: string[];
      indifferent: string[];
      reverse: string[];
    };
    optimizationPriorities: {
      characteristic: string;
      priority: number;
      reason: string;
    }[];
  } {
    // 按卡诺类别分组
    const categories = {
      must_have: [] as string[],
      one_dimensional: [] as string[],
      attractive: [] as string[],
      indifferent: [] as string[],
      reverse: [] as string[]
    };
    
    for (const result of mappingResults) {
      categories[result.kanoCategory as keyof typeof categories].push(
        `${result.productCharacteristic} -> ${result.customerValue}`
      );
    }
    
    // 计算优化优先级
    const optimizationPriorities = mappingResults
      .filter(result => result.optimizationPotential > 0.3)
      .map(result => ({
        characteristic: result.productCharacteristic,
        priority: result.optimizationPotential,
        reason: this.getOptimizationReason(result)
      }))
      .sort((a, b) => b.priority - a.priority);
    
    return {
      categories,
      optimizationPriorities
    };
  }

  /**
   * 获取优化原因
   */
  private getOptimizationReason(result: MappingResult): string {
    if (result.kanoCategory === 'must_have') {
      return '必须满足的基本需求，优化优先级最高';
    } else if (result.kanoCategory === 'one_dimensional') {
      return '线性关系，投入越多满意度越高';
    } else if (result.kanoCategory === 'attractive') {
      return '惊喜因素，超出期望的附加价值';
    } else if (result.kanoCategory === 'indifferent') {
      return '客户不关心的特性，优化价值较低';
    } else {
      return '反向关系，需要避免的特性';
    }
  }
}

/**
 * 卡诺模型分析器
 */
export class KanoModelAnalyzer {
  /**
   * 卡诺模型分析
   */
  analyzeKanoModel(data: {
    characteristic: string;
    satisfaction: number;
    dissatisfaction: number;
  }[]): {
    categories: {
      must_have: string[];
      one_dimensional: string[];
      attractive: string[];
      indifferent: string[];
      reverse: string[];
    };
    optimizationPriorities: {
      characteristic: string;
      priority: number;
      reason: string;
    }[];
  } {
    const categories = {
      must_have: [] as string[],
      one_dimensional: [] as string[],
      attractive: [] as string[],
      indifferent: [] as string[],
      reverse: [] as string[]
    };
    
    const optimizationPriorities: {
      characteristic: string;
      priority: number;
      reason: string;
    }[] = [];
    
    for (const item of data) {
      const category = this.categorizeKanoItem(item);
      categories[category].push(item.characteristic);
      
      // 计算优化优先级
      const priority = this.calculateOptimizationPriority(item, category);
      optimizationPriorities.push({
        characteristic: item.characteristic,
        priority,
        reason: this.getPriorityReason(category, priority)
      });
    }
    
    // 按优先级排序
    optimizationPriorities.sort((a, b) => b.priority - a.priority);
    
    return {
      categories,
      optimizationPriorities
    };
  }

  /**
   * 分类卡诺项目
   */
  private categorizeKanoItem(item: {
    characteristic: string;
    satisfaction: number;
    dissatisfaction: number;
  }): 'must_have' | 'one_dimensional' | 'attractive' | 'indifferent' | 'reverse' {
    const { satisfaction, dissatisfaction } = item;
    
    if (satisfaction > 0.8 && dissatisfaction > 0.8) {
      return 'one_dimensional';
    } else if (satisfaction > 0.8 && dissatisfaction < 0.3) {
      return 'attractive';
    } else if (satisfaction < 0.3 && dissatisfaction > 0.8) {
      return 'must_have';
    } else if (satisfaction < 0.3 && dissatisfaction < 0.3) {
      return 'indifferent';
    } else {
      return 'reverse';
    }
  }

  /**
   * 计算优化优先级
   */
  private calculateOptimizationPriority(
    item: { characteristic: string; satisfaction: number; dissatisfaction: number },
    category: string
  ): number {
    const { satisfaction, dissatisfaction } = item;
    
    switch (category) {
      case 'must_have':
        return 1.0; // 最高优先级
      case 'one_dimensional':
        return 0.8; // 高优先级
      case 'attractive':
        return 0.6; // 中等优先级
      case 'indifferent':
        return 0.2; // 低优先级
      case 'reverse':
        return 0.1; // 最低优先级
      default:
        return 0.5;
    }
  }

  /**
   * 获取优先级原因
   */
  private getPriorityReason(category: string, priority: number): string {
    const reasons: Record<string, string> = {
      'must_have': '必须满足的基本需求，不满足会导致客户极度不满',
      'one_dimensional': '线性关系，投入越多满意度越高',
      'attractive': '惊喜因素，超出期望的附加价值',
      'indifferent': '客户不关心的特性，优化价值较低',
      'reverse': '反向关系，需要避免的特性'
    };
    
    return reasons[category] || '需要进一步分析';
  }
}

/**
 * 映射优化器
 */
export class MappingOptimizer {
  /**
   * 优化产品特性-客户价值映射
   */
  optimizeMapping(
    productCharacteristics: ProductCharacteristic[],
    customerValues: CustomerValue[],
    constraints: {
      maxBudget?: number;
      maxCharacteristics?: number;
      minMappingStrength?: number;
    } = {}
  ): {
    optimizedCharacteristics: ProductCharacteristic[];
    optimizedValues: CustomerValue[];
    totalMappingScore: number;
    optimizationRecommendations: string[];
  } {
    // 基于约束条件优化特性
    const optimizedCharacteristics = this.optimizeCharacteristics(productCharacteristics, constraints);
    
    // 基于约束条件优化价值
    const optimizedValues = this.optimizeValues(customerValues, constraints);
    
    // 计算优化后的映射分数
    const analyzer = new ProductCustomerMappingAnalyzer();
    const mappingResult = analyzer.calculateMappingStrength(optimizedCharacteristics, optimizedValues);
    
    // 生成优化建议
    const optimizationRecommendations = this.generateOptimizationRecommendations(
      productCharacteristics,
      customerValues,
      optimizedCharacteristics,
      optimizedValues
    );
    
    return {
      optimizedCharacteristics,
      optimizedValues,
      totalMappingScore: mappingResult.overallMappingScore,
      optimizationRecommendations
    };
  }

  private optimizeCharacteristics(
    characteristics: ProductCharacteristic[],
    constraints: any
  ): ProductCharacteristic[] {
    return characteristics.map(characteristic => {
      // 基于约束条件优化特性
      let optimizedCharacteristic = { ...characteristic };
      
      // 预算约束
      if (constraints.maxBudget && characteristic.cost > constraints.maxBudget / characteristics.length) {
        optimizedCharacteristic.characteristicValue = Math.min(
          optimizedCharacteristic.characteristicValue,
          (constraints.maxBudget / characteristics.length) / characteristic.cost
        );
      }
      
      // 特性数量约束
      if (constraints.maxCharacteristics && characteristics.length > constraints.maxCharacteristics) {
        // 选择重要性最高的特性
        if (characteristic.importance < 0.5) {
          optimizedCharacteristic.characteristicValue = 0;
        }
      }
      
      return optimizedCharacteristic;
    });
  }

  private optimizeValues(
    values: CustomerValue[],
    constraints: any
  ): CustomerValue[] {
    return values.map(value => {
      // 基于约束条件优化价值
      let optimizedValue = { ...value };
      
      // 最小映射强度约束
      if (constraints.minMappingStrength && value.valueImportance < constraints.minMappingStrength) {
        optimizedValue.valueImportance = constraints.minMappingStrength;
      }
      
      return optimizedValue;
    });
  }

  private generateOptimizationRecommendations(
    originalCharacteristics: ProductCharacteristic[],
    originalValues: CustomerValue[],
    optimizedCharacteristics: ProductCharacteristic[],
    optimizedValues: CustomerValue[]
  ): string[] {
    const recommendations: string[] = [];
    
    // 分析特性变化
    for (let i = 0; i < originalCharacteristics.length; i++) {
      const original = originalCharacteristics[i];
      const optimized = optimizedCharacteristics[i];
      
      if (optimized.characteristicValue !== original.characteristicValue) {
        recommendations.push(
          `调整产品特性 ${original.characteristicName} 的值从 ${original.characteristicValue.toFixed(2)} 到 ${optimized.characteristicValue.toFixed(2)}`
        );
      }
    }
    
    // 分析价值变化
    for (let i = 0; i < originalValues.length; i++) {
      const original = originalValues[i];
      const optimized = optimizedValues[i];
      
      if (optimized.valueImportance !== original.valueImportance) {
        recommendations.push(
          `调整客户价值 ${original.valueName} 的重要性从 ${original.valueImportance.toFixed(2)} 到 ${optimized.valueImportance.toFixed(2)}`
        );
      }
    }
    
    return recommendations;
  }
}


