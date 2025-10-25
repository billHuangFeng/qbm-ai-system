/**
 * 协同效应分析算法实现
 * 基于四要素协同的协同效应计算
 */

export interface CoreResource {
  resourceId: string;
  resourceName: string;
  resourceType: 'human' | 'equipment' | 'technology' | 'financial';
  quantity: number;
  qualityScore: number;
  cost: number;
  availability: number;
}

export interface CoreCapability {
  capabilityId: string;
  capabilityName: string;
  maturityLevel: number;
  developmentInvestment: number;
  performanceScore: number;
  strategicImportance: number;
}

export interface SynergyEffect {
  resourceCapabilityPair: {
    resource: string;
    capability: string;
  };
  synergyCoefficient: number;
  interactionStrength: number;
  synergyContribution: number;
  optimizationPotential: number;
  synergyType: 'complementary' | 'substitutive' | 'neutral' | 'synergistic';
}

export interface SynergyAnalysisResult {
  success: boolean;
  synergyEffects: SynergyEffect[];
  overallSynergyScore: number;
  synergyRecommendations: string[];
  resourceOptimization: {
    resourceId: string;
    currentUtilization: number;
    optimalUtilization: number;
    improvementPotential: number;
  }[];
  capabilityOptimization: {
    capabilityId: string;
    currentMaturity: number;
    targetMaturity: number;
    developmentGap: number;
  }[];
}

/**
 * 协同效应分析器
 */
export class SynergyAnalyzer {
  private interactionDegree: number = 2;
  private optimizationMethod: 'genetic_algorithm' | 'gradient_descent' | 'simulated_annealing' = 'genetic_algorithm';
  private convergenceThreshold: number = 0.001;

  constructor(config?: {
    interactionDegree?: number;
    optimizationMethod?: 'genetic_algorithm' | 'gradient_descent' | 'simulated_annealing';
    convergenceThreshold?: number;
  }) {
    if (config) {
      this.interactionDegree = config.interactionDegree || this.interactionDegree;
      this.optimizationMethod = config.optimizationMethod || this.optimizationMethod;
      this.convergenceThreshold = config.convergenceThreshold || this.convergenceThreshold;
    }
  }

  /**
   * 计算协同效应
   */
  async calculateSynergyEffects(
    resources: CoreResource[],
    capabilities: CoreCapability[]
  ): Promise<SynergyAnalysisResult> {
    try {
      // 验证输入数据
      this.validateInputData(resources, capabilities);
      
      // 计算资源-能力协同效应
      const synergyEffects = this.calculateResourceCapabilitySynergy(resources, capabilities);
      
      // 计算整体协同分数
      const overallSynergyScore = this.calculateOverallSynergyScore(synergyEffects);
      
      // 生成协同建议
      const synergyRecommendations = this.generateSynergyRecommendations(synergyEffects);
      
      // 计算资源优化建议
      const resourceOptimization = this.calculateResourceOptimization(resources, synergyEffects);
      
      // 计算能力优化建议
      const capabilityOptimization = this.calculateCapabilityOptimization(capabilities, synergyEffects);
      
      return {
        success: true,
        synergyEffects,
        overallSynergyScore,
        synergyRecommendations,
        resourceOptimization,
        capabilityOptimization
      };
      
    } catch (error) {
      return {
        success: false,
        synergyEffects: [],
        overallSynergyScore: 0,
        synergyRecommendations: [],
        resourceOptimization: [],
        capabilityOptimization: []
      };
    }
  }

  /**
   * 验证输入数据
   */
  private validateInputData(resources: CoreResource[], capabilities: CoreCapability[]): void {
    if (resources.length === 0) {
      throw new Error('资源数据不能为空');
    }
    
    if (capabilities.length === 0) {
      throw new Error('能力数据不能为空');
    }
    
    // 验证资源数据
    for (const resource of resources) {
      if (resource.quantity <= 0) {
        throw new Error(`资源 ${resource.resourceName} 的数量必须大于0`);
      }
      if (resource.qualityScore < 0 || resource.qualityScore > 1) {
        throw new Error(`资源 ${resource.resourceName} 的质量分数必须在0-1之间`);
      }
    }
    
    // 验证能力数据
    for (const capability of capabilities) {
      if (capability.maturityLevel < 0 || capability.maturityLevel > 1) {
        throw new Error(`能力 ${capability.capabilityName} 的成熟度必须在0-1之间`);
      }
    }
  }

  /**
   * 计算资源-能力协同效应
   */
  private calculateResourceCapabilitySynergy(
    resources: CoreResource[],
    capabilities: CoreCapability[]
  ): SynergyEffect[] {
    const synergyEffects: SynergyEffect[] = [];
    
    for (const resource of resources) {
      for (const capability of capabilities) {
        // 计算基础协同系数
        const synergyCoefficient = this.calculateSynergyCoefficient(resource, capability);
        
        // 计算交互强度
        const interactionStrength = this.calculateInteractionStrength(resource, capability);
        
        // 计算协同贡献
        const synergyContribution = this.calculateSynergyContribution(
          resource, 
          capability, 
          synergyCoefficient
        );
        
        // 计算优化潜力
        const optimizationPotential = this.calculateOptimizationPotential(
          resource,
          capability,
          synergyCoefficient
        );
        
        // 确定协同类型
        const synergyType = this.determineSynergyType(synergyCoefficient, interactionStrength);
        
        synergyEffects.push({
          resourceCapabilityPair: {
            resource: resource.resourceName,
            capability: capability.capabilityName
          },
          synergyCoefficient,
          interactionStrength,
          synergyContribution,
          optimizationPotential,
          synergyType
        });
      }
    }
    
    return synergyEffects;
  }

  /**
   * 计算协同系数
   */
  private calculateSynergyCoefficient(
    resource: CoreResource,
    capability: CoreCapability
  ): number {
    // 基础协同系数 = 资源质量 × 能力成熟度
    const baseSynergy = resource.qualityScore * capability.maturityLevel;
    
    // 资源可用性调整
    const availabilityAdjustment = resource.availability;
    
    // 能力性能调整
    const performanceAdjustment = capability.performanceScore;
    
    // 战略重要性调整
    const strategicAdjustment = capability.strategicImportance;
    
    // 计算最终协同系数
    const synergyCoefficient = baseSynergy * 
      (0.4 * availabilityAdjustment + 0.3 * performanceAdjustment + 0.3 * strategicAdjustment);
    
    return Math.min(1, Math.max(0, synergyCoefficient));
  }

  /**
   * 计算交互强度
   */
  private calculateInteractionStrength(
    resource: CoreResource,
    capability: CoreCapability
  ): number {
    // 基于资源类型和能力类型的匹配度
    const typeMatch = this.getTypeMatchScore(resource.resourceType, capability.capabilityName);
    
    // 基于数量的交互强度
    const quantityInteraction = Math.min(1, resource.quantity / 10); // 假设10为基准数量
    
    // 基于投资的交互强度
    const investmentInteraction = Math.min(1, capability.developmentInvestment / 100000); // 假设10万为基准投资
    
    return (typeMatch * 0.5 + quantityInteraction * 0.3 + investmentInteraction * 0.2);
  }

  /**
   * 获取类型匹配分数
   */
  private getTypeMatchScore(resourceType: string, capabilityName: string): number {
    const matchMatrix: Record<string, Record<string, number>> = {
      'human': {
        '产品开发': 0.9,
        '生产制造': 0.7,
        '销售推广': 0.8,
        '客户服务': 0.9
      },
      'equipment': {
        '产品开发': 0.6,
        '生产制造': 0.9,
        '销售推广': 0.4,
        '客户服务': 0.3
      },
      'technology': {
        '产品开发': 0.9,
        '生产制造': 0.8,
        '销售推广': 0.6,
        '客户服务': 0.7
      },
      'financial': {
        '产品开发': 0.8,
        '生产制造': 0.7,
        '销售推广': 0.9,
        '客户服务': 0.6
      }
    };
    
    return matchMatrix[resourceType]?.[capabilityName] || 0.5;
  }

  /**
   * 计算协同贡献
   */
  private calculateSynergyContribution(
    resource: CoreResource,
    capability: CoreCapability,
    synergyCoefficient: number
  ): number {
    // 协同贡献 = 协同系数 × 资源成本效率 × 能力投资效率
    const resourceCostEfficiency = resource.qualityScore / (resource.cost / resource.quantity);
    const capabilityInvestmentEfficiency = capability.performanceScore / (capability.developmentInvestment / 1000);
    
    return synergyCoefficient * resourceCostEfficiency * capabilityInvestmentEfficiency;
  }

  /**
   * 计算优化潜力
   */
  private calculateOptimizationPotential(
    resource: CoreResource,
    capability: CoreCapability,
    synergyCoefficient: number
  ): number {
    // 优化潜力 = (1 - 当前协同系数) × 资源质量提升空间 × 能力成熟度提升空间
    const resourceImprovementSpace = 1 - resource.qualityScore;
    const capabilityImprovementSpace = 1 - capability.maturityLevel;
    
    return (1 - synergyCoefficient) * resourceImprovementSpace * capabilityImprovementSpace;
  }

  /**
   * 确定协同类型
   */
  private determineSynergyType(
    synergyCoefficient: number,
    interactionStrength: number
  ): 'complementary' | 'substitutive' | 'neutral' | 'synergistic' {
    const combinedScore = (synergyCoefficient + interactionStrength) / 2;
    
    if (combinedScore >= 0.8) return 'synergistic';
    if (combinedScore >= 0.6) return 'complementary';
    if (combinedScore >= 0.4) return 'neutral';
    return 'substitutive';
  }

  /**
   * 计算整体协同分数
   */
  private calculateOverallSynergyScore(synergyEffects: SynergyEffect[]): number {
    if (synergyEffects.length === 0) return 0;
    
    // 计算加权平均协同分数
    const totalSynergyContribution = synergyEffects.reduce(
      (sum, effect) => sum + effect.synergyContribution, 
      0
    );
    
    const totalOptimizationPotential = synergyEffects.reduce(
      (sum, effect) => sum + effect.optimizationPotential, 
      0
    );
    
    // 整体协同分数 = 平均协同贡献 × (1 + 优化潜力)
    const averageSynergyContribution = totalSynergyContribution / synergyEffects.length;
    const averageOptimizationPotential = totalOptimizationPotential / synergyEffects.length;
    
    return averageSynergyContribution * (1 + averageOptimizationPotential);
  }

  /**
   * 生成协同建议
   */
  private generateSynergyRecommendations(synergyEffects: SynergyEffect[]): string[] {
    const recommendations: string[] = [];
    
    // 分析协同效应
    const synergisticEffects = synergyEffects.filter(e => e.synergyType === 'synergistic');
    const complementaryEffects = synergyEffects.filter(e => e.synergyType === 'complementary');
    const substitutiveEffects = synergyEffects.filter(e => e.synergyType === 'substitutive');
    
    if (synergisticEffects.length > 0) {
      recommendations.push('加强协同效应显著的资源-能力组合');
    }
    
    if (complementaryEffects.length > 0) {
      recommendations.push('优化互补性资源-能力组合的配置');
    }
    
    if (substitutiveEffects.length > 0) {
      recommendations.push('重新评估替代性资源-能力组合的必要性');
    }
    
    // 基于优化潜力生成建议
    const highPotentialEffects = synergyEffects.filter(e => e.optimizationPotential > 0.5);
    if (highPotentialEffects.length > 0) {
      recommendations.push('重点关注高优化潜力的资源-能力组合');
    }
    
    return recommendations;
  }

  /**
   * 计算资源优化建议
   */
  private calculateResourceOptimization(
    resources: CoreResource[],
    synergyEffects: SynergyEffect[]
  ): { resourceId: string; currentUtilization: number; optimalUtilization: number; improvementPotential: number }[] {
    return resources.map(resource => {
      // 计算当前利用率
      const currentUtilization = resource.qualityScore * resource.availability;
      
      // 计算最优利用率
      const resourceEffects = synergyEffects.filter(e => 
        e.resourceCapabilityPair.resource === resource.resourceName
      );
      
      const averageSynergyCoefficient = resourceEffects.length > 0 
        ? resourceEffects.reduce((sum, e) => sum + e.synergyCoefficient, 0) / resourceEffects.length
        : 0;
      
      const optimalUtilization = Math.min(1, currentUtilization + (1 - averageSynergyCoefficient) * 0.3);
      
      // 计算改进潜力
      const improvementPotential = optimalUtilization - currentUtilization;
      
      return {
        resourceId: resource.resourceId,
        currentUtilization,
        optimalUtilization,
        improvementPotential
      };
    });
  }

  /**
   * 计算能力优化建议
   */
  private calculateCapabilityOptimization(
    capabilities: CoreCapability[],
    synergyEffects: SynergyEffect[]
  ): { capabilityId: string; currentMaturity: number; targetMaturity: number; developmentGap: number }[] {
    return capabilities.map(capability => {
      const currentMaturity = capability.maturityLevel;
      
      // 计算目标成熟度
      const capabilityEffects = synergyEffects.filter(e => 
        e.resourceCapabilityPair.capability === capability.capabilityName
      );
      
      const averageOptimizationPotential = capabilityEffects.length > 0 
        ? capabilityEffects.reduce((sum, e) => sum + e.optimizationPotential, 0) / capabilityEffects.length
        : 0;
      
      const targetMaturity = Math.min(1, currentMaturity + averageOptimizationPotential);
      
      // 计算发展差距
      const developmentGap = targetMaturity - currentMaturity;
      
      return {
        capabilityId: capability.capabilityId,
        currentMaturity,
        targetMaturity,
        developmentGap
      };
    });
  }
}

/**
 * 协同效应优化器
 */
export class SynergyOptimizer {
  /**
   * 优化资源-能力配置
   */
  static optimizeResourceCapabilityConfiguration(
    resources: CoreResource[],
    capabilities: CoreCapability[],
    constraints: {
      maxBudget?: number;
      maxResources?: number;
      minCapabilityLevel?: number;
    } = {}
  ): {
    optimizedResources: CoreResource[];
    optimizedCapabilities: CoreCapability[];
    totalSynergyScore: number;
    optimizationRecommendations: string[];
  } {
    // 基于约束条件优化配置
    const optimizedResources = this.optimizeResources(resources, constraints);
    const optimizedCapabilities = this.optimizeCapabilities(capabilities, constraints);
    
    // 计算优化后的协同分数
    const analyzer = new SynergyAnalyzer();
    const synergyResult = analyzer.calculateSynergyEffects(optimizedResources, optimizedCapabilities);
    
    // 生成优化建议
    const optimizationRecommendations = this.generateOptimizationRecommendations(
      resources,
      capabilities,
      optimizedResources,
      optimizedCapabilities
    );
    
    return {
      optimizedResources,
      optimizedCapabilities,
      totalSynergyScore: synergyResult.overallSynergyScore,
      optimizationRecommendations
    };
  }

  private static optimizeResources(
    resources: CoreResource[],
    constraints: any
  ): CoreResource[] {
    return resources.map(resource => {
      // 基于约束条件优化资源
      let optimizedResource = { ...resource };
      
      // 预算约束
      if (constraints.maxBudget && resource.cost > constraints.maxBudget / resources.length) {
        optimizedResource.quantity = Math.floor((constraints.maxBudget / resources.length) / (resource.cost / resource.quantity));
      }
      
      // 资源数量约束
      if (constraints.maxResources && resource.quantity > constraints.maxResources) {
        optimizedResource.quantity = constraints.maxResources;
      }
      
      return optimizedResource;
    });
  }

  private static optimizeCapabilities(
    capabilities: CoreCapability[],
    constraints: any
  ): CoreCapability[] {
    return capabilities.map(capability => {
      // 基于约束条件优化能力
      let optimizedCapability = { ...capability };
      
      // 最小能力水平约束
      if (constraints.minCapabilityLevel && capability.maturityLevel < constraints.minCapabilityLevel) {
        optimizedCapability.maturityLevel = constraints.minCapabilityLevel;
      }
      
      return optimizedCapability;
    });
  }

  private static generateOptimizationRecommendations(
    originalResources: CoreResource[],
    originalCapabilities: CoreCapability[],
    optimizedResources: CoreResource[],
    optimizedCapabilities: CoreCapability[]
  ): string[] {
    const recommendations: string[] = [];
    
    // 分析资源变化
    for (let i = 0; i < originalResources.length; i++) {
      const original = originalResources[i];
      const optimized = optimizedResources[i];
      
      if (optimized.quantity !== original.quantity) {
        recommendations.push(`调整资源 ${original.resourceName} 的数量从 ${original.quantity} 到 ${optimized.quantity}`);
      }
    }
    
    // 分析能力变化
    for (let i = 0; i < originalCapabilities.length; i++) {
      const original = originalCapabilities[i];
      const optimized = optimizedCapabilities[i];
      
      if (optimized.maturityLevel !== original.maturityLevel) {
        recommendations.push(`提升能力 ${original.capabilityName} 的成熟度从 ${original.maturityLevel.toFixed(2)} 到 ${optimized.maturityLevel.toFixed(2)}`);
      }
    }
    
    return recommendations;
  }
}
