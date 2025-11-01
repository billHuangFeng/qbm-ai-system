/**
 * 三大流程管理算法实现
 * 生产流程、传播流程、交付流程的效能监控和优化
 */

export interface ProcessMetrics {
  processType: 'production' | 'propagation' | 'delivery';
  period: string;
  efficiency: number;
  quality: number;
  cost: number;
  time: number;
  throughput: number;
}

export interface ProcessBottleneck {
  process: string;
  bottleneckLevel: number;
  impactScore: number;
  description: string;
  recommendations: string[];
}

export interface ProcessOptimizationResult {
  success: boolean;
  currentEfficiency: number;
  targetEfficiency: number;
  improvementPotential: number;
  bottlenecks: ProcessBottleneck[];
  optimizationRecommendations: {
    title: string;
    description: string;
    expectedImpact: {
      efficiencyImprovement: number;
      costReduction: number;
      timeSaving: number;
    };
    implementationPlan: {
      duration: number;
      resourcesRequired: string[];
      budgetRequired: number;
    };
    priority: 'high' | 'medium' | 'low';
    feasibility: number;
  }[];
}

/**
 * 生产流程监控器
 */
export class ProductionProcessMonitor {
  /**
   * 计算生产效能指标
   */
  calculateEfficiencyMetrics(data: ProcessMetrics[]): {
    productionEfficiency: number;
    qualityEfficiency: number;
    costEfficiency: number;
    overallEfficiency: number;
    trendAnalysis: {
      trendDirection: 'improving' | 'stable' | 'declining';
      trendStrength: number;
      forecastNextMonth: number;
    };
  } {
    if (data.length === 0) {
      return {
        productionEfficiency: 0,
        qualityEfficiency: 0,
        costEfficiency: 0,
        overallEfficiency: 0,
        trendAnalysis: {
          trendDirection: 'stable',
          trendStrength: 0,
          forecastNextMonth: 0
        }
      };
    }

    // 计算各项效率指标
    const productionEfficiency = this.calculateProductionEfficiency(data);
    const qualityEfficiency = this.calculateQualityEfficiency(data);
    const costEfficiency = this.calculateCostEfficiency(data);
    
    // 计算整体效率
    const overallEfficiency = (productionEfficiency + qualityEfficiency + costEfficiency) / 3;
    
    // 趋势分析
    const trendAnalysis = this.analyzeTrend(data);
    
    return {
      productionEfficiency,
      qualityEfficiency,
      costEfficiency,
      overallEfficiency,
      trendAnalysis
    };
  }

  /**
   * 检测生产瓶颈
   */
  detectBottlenecks(data: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测效率瓶颈
    const efficiencyBottlenecks = this.detectEfficiencyBottlenecks(data);
    bottlenecks.push(...efficiencyBottlenecks);
    
    // 检测质量瓶颈
    const qualityBottlenecks = this.detectQualityBottlenecks(data);
    bottlenecks.push(...qualityBottlenecks);
    
    // 检测成本瓶颈
    const costBottlenecks = this.detectCostBottlenecks(data);
    bottlenecks.push(...costBottlenecks);
    
    return bottlenecks;
  }

  private calculateProductionEfficiency(data: ProcessMetrics[]): number {
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    const avgThroughput = data.reduce((sum, d) => sum + d.throughput, 0) / data.length;
    
    // 生产效率 = 效率 × 吞吐量权重
    return avgEfficiency * (avgThroughput / 100); // 假设100为基准吞吐量
  }

  private calculateQualityEfficiency(data: ProcessMetrics[]): number {
    const avgQuality = data.reduce((sum, d) => sum + d.quality, 0) / data.length;
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    
    // 质量效率 = 质量 × 效率
    return avgQuality * avgEfficiency;
  }

  private calculateCostEfficiency(data: ProcessMetrics[]): number {
    const avgCost = data.reduce((sum, d) => sum + d.cost, 0) / data.length;
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    
    // 成本效率 = 效率 / 成本（成本越低，效率越高）
    return avgEfficiency / (avgCost / 1000); // 假设1000为基准成本
  }

  private analyzeTrend(data: ProcessMetrics[]): {
    trendDirection: 'improving' | 'stable' | 'declining';
    trendStrength: number;
    forecastNextMonth: number;
  } {
    if (data.length < 2) {
      return {
        trendDirection: 'stable',
        trendStrength: 0,
        forecastNextMonth: data[0]?.efficiency || 0
      };
    }

    // 计算效率趋势
    const efficiencies = data.map(d => d.efficiency);
    const trend = this.calculateTrend(efficiencies);
    
    let trendDirection: 'improving' | 'stable' | 'declining';
    if (trend > 0.05) trendDirection = 'improving';
    else if (trend < -0.05) trendDirection = 'declining';
    else trendDirection = 'stable';
    
    // 预测下个月
    const lastEfficiency = efficiencies[efficiencies.length - 1];
    const forecastNextMonth = Math.max(0, Math.min(1, lastEfficiency + trend));
    
    return {
      trendDirection,
      trendStrength: Math.abs(trend),
      forecastNextMonth
    };
  }

  private detectEfficiencyBottlenecks(data: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测效率下降
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    if (avgEfficiency < 0.7) { // 效率低于70%
      bottlenecks.push({
        process: '生产流程',
        bottleneckLevel: 1 - avgEfficiency,
        impactScore: 1 - avgEfficiency,
        description: `生产效率为${(avgEfficiency * 100).toFixed(1)}%，存在效率瓶颈`,
        recommendations: [
          '优化生产排程',
          '提高设备利用率',
          '加强人员培训',
          '改进工艺流程'
        ]
      });
    }
    
    return bottlenecks;
  }

  private detectQualityBottlenecks(data: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测质量下降
    const avgQuality = data.reduce((sum, d) => sum + d.quality, 0) / data.length;
    if (avgQuality < 0.8) { // 质量低于80%
      bottlenecks.push({
        process: '质量控制',
        bottleneckLevel: 1 - avgQuality,
        impactScore: 1 - avgQuality,
        description: `产品质量为${(avgQuality * 100).toFixed(1)}%，存在质量瓶颈`,
        recommendations: [
          '加强质量检测',
          '改进原材料质量',
          '优化生产工艺',
          '提高员工质量意识'
        ]
      });
    }
    
    return bottlenecks;
  }

  private detectCostBottlenecks(data: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测成本上升
    const avgCost = data.reduce((sum, d) => sum + d.cost, 0) / data.length;
    const costTrend = this.calculateTrend(data.map(d => d.cost));
    
    if (costTrend > 0.1) { // 成本上升超过10%
      bottlenecks.push({
        process: '成本控制',
        bottleneckLevel: costTrend,
        impactScore: costTrend,
        description: `成本上升${(costTrend * 100).toFixed(1)}%，存在成本瓶颈`,
        recommendations: [
          '优化供应链管理',
          '降低原材料成本',
          '提高生产效率',
          '减少浪费'
        ]
      });
    }
    
    return bottlenecks;
  }

  private calculateTrend(values: number[]): number {
    if (values.length < 2) return 0;
    
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    const y = values;
    
    // 计算线性回归斜率
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);
    
    return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  }
}

/**
 * 传播流程监控器
 */
export class PropagationProcessMonitor {
  /**
   * 计算传播效能指标
   */
  calculatePropagationMetrics(data: ProcessMetrics[]): {
    reachEfficiency: number;
    conversionEfficiency: number;
    engagementEfficiency: number;
    overallEfficiency: number;
    channelPerformance: {
      channel: string;
      efficiency: number;
      reach: number;
      conversion: number;
    }[];
  } {
    if (data.length === 0) {
      return {
        reachEfficiency: 0,
        conversionEfficiency: 0,
        engagementEfficiency: 0,
        overallEfficiency: 0,
        channelPerformance: []
      };
    }

    // 计算传播效率
    const reachEfficiency = this.calculateReachEfficiency(data);
    const conversionEfficiency = this.calculateConversionEfficiency(data);
    const engagementEfficiency = this.calculateEngagementEfficiency(data);
    
    // 计算整体效率
    const overallEfficiency = (reachEfficiency + conversionEfficiency + engagementEfficiency) / 3;
    
    // 渠道性能分析
    const channelPerformance = this.analyzeChannelPerformance(data);
    
    return {
      reachEfficiency,
      conversionEfficiency,
      engagementEfficiency,
      overallEfficiency,
      channelPerformance
    };
  }

  private calculateReachEfficiency(data: ProcessMetrics[]): number {
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    const avgThroughput = data.reduce((sum, d) => sum + d.throughput, 0) / data.length;
    
    return avgEfficiency * (avgThroughput / 100);
  }

  private calculateConversionEfficiency(data: ProcessMetrics[]): number {
    const avgQuality = data.reduce((sum, d) => sum + d.quality, 0) / data.length;
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    
    return avgQuality * avgEfficiency;
  }

  private calculateEngagementEfficiency(data: ProcessMetrics[]): number {
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    const avgTime = data.reduce((sum, d) => sum + d.time, 0) / data.length;
    
    // 参与效率 = 效率 / 时间（时间越短，效率越高）
    return avgEfficiency / (avgTime / 100); // 假设100为基准时间
  }

  private analyzeChannelPerformance(data: ProcessMetrics[]): {
    channel: string;
    efficiency: number;
    reach: number;
    conversion: number;
  }[] {
    // 这里简化处理，实际应该按渠道分组分析
    return [
      {
        channel: '线上渠道',
        efficiency: 0.85,
        reach: 0.90,
        conversion: 0.75
      },
      {
        channel: '线下渠道',
        efficiency: 0.80,
        reach: 0.85,
        conversion: 0.80
      }
    ];
  }
}

/**
 * 交付流程监控器
 */
export class DeliveryProcessMonitor {
  /**
   * 计算交付效能指标
   */
  calculateDeliveryMetrics(data: ProcessMetrics[]): {
    deliveryEfficiency: number;
    customerSatisfaction: number;
    onTimeDelivery: number;
    overallEfficiency: number;
    deliveryBottlenecks: ProcessBottleneck[];
  } {
    if (data.length === 0) {
      return {
        deliveryEfficiency: 0,
        customerSatisfaction: 0,
        onTimeDelivery: 0,
        overallEfficiency: 0,
        deliveryBottlenecks: []
      };
    }

    // 计算交付效率
    const deliveryEfficiency = this.calculateDeliveryEfficiency(data);
    const customerSatisfaction = this.calculateCustomerSatisfaction(data);
    const onTimeDelivery = this.calculateOnTimeDelivery(data);
    
    // 计算整体效率
    const overallEfficiency = (deliveryEfficiency + customerSatisfaction + onTimeDelivery) / 3;
    
    // 检测交付瓶颈
    const deliveryBottlenecks = this.detectDeliveryBottlenecks(data);
    
    return {
      deliveryEfficiency,
      customerSatisfaction,
      onTimeDelivery,
      overallEfficiency,
      deliveryBottlenecks
    };
  }

  private calculateDeliveryEfficiency(data: ProcessMetrics[]): number {
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    const avgTime = data.reduce((sum, d) => sum + d.time, 0) / data.length;
    
    // 交付效率 = 效率 / 时间
    return avgEfficiency / (avgTime / 100);
  }

  private calculateCustomerSatisfaction(data: ProcessMetrics[]): number {
    const avgQuality = data.reduce((sum, d) => sum + d.quality, 0) / data.length;
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    
    return avgQuality * avgEfficiency;
  }

  private calculateOnTimeDelivery(data: ProcessMetrics[]): number {
    const avgEfficiency = data.reduce((sum, d) => sum + d.efficiency, 0) / data.length;
    const avgTime = data.reduce((sum, d) => sum + d.time, 0) / data.length;
    
    // 准时交付率 = 效率 × (1 - 时间延迟)
    const timeDelay = Math.max(0, (avgTime - 100) / 100); // 假设100为基准时间
    return avgEfficiency * (1 - timeDelay);
  }

  private detectDeliveryBottlenecks(data: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测交付时间瓶颈
    const avgTime = data.reduce((sum, d) => sum + d.time, 0) / data.length;
    if (avgTime > 120) { // 交付时间超过120
      bottlenecks.push({
        process: '交付流程',
        bottleneckLevel: (avgTime - 100) / 100,
        impactScore: (avgTime - 100) / 100,
        description: `平均交付时间为${avgTime.toFixed(1)}，存在时间瓶颈`,
        recommendations: [
          '优化物流配送',
          '提高库存管理',
          '加强供应链协调',
          '改进交付流程'
        ]
      });
    }
    
    return bottlenecks;
  }
}

/**
 * 流程优化器
 */
export class ProcessOptimizer {
  /**
   * 生成流程优化建议
   */
  generateOptimizationRecommendations(
    processType: 'production' | 'propagation' | 'delivery',
    currentMetrics: ProcessMetrics[],
    optimizationGoals: string[],
    constraints: {
      budgetLimit?: number;
      timeLimit?: number;
      resourceAvailability?: string[];
    } = {}
  ): ProcessOptimizationResult {
    // 计算当前效率
    const currentEfficiency = this.calculateCurrentEfficiency(currentMetrics);
    
    // 计算目标效率
    const targetEfficiency = this.calculateTargetEfficiency(currentMetrics, optimizationGoals);
    
    // 计算改进潜力
    const improvementPotential = targetEfficiency - currentEfficiency;
    
    // 检测瓶颈
    const bottlenecks = this.detectBottlenecks(currentMetrics);
    
    // 生成优化建议
    const optimizationRecommendations = this.generateRecommendations(
      processType,
      currentMetrics,
      optimizationGoals,
      constraints
    );
    
    return {
      success: true,
      currentEfficiency,
      targetEfficiency,
      improvementPotential,
      bottlenecks,
      optimizationRecommendations
    };
  }

  private calculateCurrentEfficiency(metrics: ProcessMetrics[]): number {
    if (metrics.length === 0) return 0;
    
    return metrics.reduce((sum, m) => sum + m.efficiency, 0) / metrics.length;
  }

  private calculateTargetEfficiency(metrics: ProcessMetrics[], goals: string[]): number {
    const currentEfficiency = this.calculateCurrentEfficiency(metrics);
    
    // 基于目标计算目标效率
    let targetEfficiency = currentEfficiency;
    
    if (goals.includes('提高生产效率')) {
      targetEfficiency += 0.1;
    }
    if (goals.includes('降低运营成本')) {
      targetEfficiency += 0.05;
    }
    if (goals.includes('提升产品质量')) {
      targetEfficiency += 0.08;
    }
    
    return Math.min(1, targetEfficiency);
  }

  private detectBottlenecks(metrics: ProcessMetrics[]): ProcessBottleneck[] {
    const bottlenecks: ProcessBottleneck[] = [];
    
    // 检测效率瓶颈
    const avgEfficiency = metrics.reduce((sum, m) => sum + m.efficiency, 0) / metrics.length;
    if (avgEfficiency < 0.8) {
      bottlenecks.push({
        process: '效率瓶颈',
        bottleneckLevel: 1 - avgEfficiency,
        impactScore: 1 - avgEfficiency,
        description: `当前效率为${(avgEfficiency * 100).toFixed(1)}%，存在效率瓶颈`,
        recommendations: [
          '优化流程设计',
          '提高资源利用率',
          '加强人员培训',
          '改进技术设备'
        ]
      });
    }
    
    return bottlenecks;
  }

  private generateRecommendations(
    processType: string,
    metrics: ProcessMetrics[],
    goals: string[],
    constraints: any
  ): ProcessOptimizationResult['optimizationRecommendations'] {
    const recommendations: ProcessOptimizationResult['optimizationRecommendations'] = [];
    
    // 基于流程类型生成建议
    if (processType === 'production') {
      recommendations.push({
        title: '优化生产排程',
        description: '通过智能排程算法优化生产计划，提高设备利用率',
        expectedImpact: {
          efficiencyImprovement: 0.15,
          costReduction: 20000,
          timeSaving: 10
        },
        implementationPlan: {
          duration: 30,
          resourcesRequired: ['生产经理', 'IT支持'],
          budgetRequired: 15000
        },
        priority: 'high',
        feasibility: 0.85
      });
    }
    
    if (processType === 'propagation') {
      recommendations.push({
        title: '优化传播渠道',
        description: '通过多渠道整合和精准投放提高传播效率',
        expectedImpact: {
          efficiencyImprovement: 0.20,
          costReduction: 30000,
          timeSaving: 15
        },
        implementationPlan: {
          duration: 45,
          resourcesRequired: ['营销经理', '数据分析师'],
          budgetRequired: 25000
        },
        priority: 'high',
        feasibility: 0.80
      });
    }
    
    if (processType === 'delivery') {
      recommendations.push({
        title: '优化交付流程',
        description: '通过物流优化和供应链协调提高交付效率',
        expectedImpact: {
          efficiencyImprovement: 0.18,
          costReduction: 25000,
          timeSaving: 12
        },
        implementationPlan: {
          duration: 60,
          resourcesRequired: ['物流经理', '供应链专员'],
          budgetRequired: 20000
        },
        priority: 'medium',
        feasibility: 0.75
      });
    }
    
    return recommendations;
  }
}

