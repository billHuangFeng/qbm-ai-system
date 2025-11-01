/**
 * 边际影响分析核心算法实现
 * 基于ΔV-CL信号检测的瓶颈识别算法
 */

export interface MarginalAnalysisData {
  period: string;
  efficiency: number;
  cost: number;
  revenue: number;
  quantity: number;
}

export interface BottleneckSignal {
  signalId: string;
  signalType: 'bottleneck' | 'efficiency_drop' | 'cost_spike' | 'revenue_decline';
  severity: 'low' | 'medium' | 'high' | 'critical';
  process: string;
  businessUnit: string;
  detectedAt: string;
  description: string;
  impactScore: number;
  recommendations: string[];
  relatedMetrics: {
    efficiencyScore: number;
    marginalCost: number;
    marginalRevenue: number;
  };
}

export interface MarginalAnalysisResult {
  success: boolean;
  signals: BottleneckSignal[];
  analysisSummary: {
    totalSignals: number;
    highSeverity: number;
    mediumSeverity: number;
    lowSeverity: number;
    analysisConfidence: number;
  };
  marginalMetrics: {
    marginalCost: number;
    marginalRevenue: number;
    marginalProfit: number;
    optimalQuantity: number;
  };
}

/**
 * ΔV-CL信号检测算法
 * 基于边际分析检测瓶颈信号
 */
export class DeltaVCLSignalAlgorithm {
  private sensitivity: number = 0.8;
  private threshold: number = 0.7;
  private minDataPoints: number = 10;

  constructor(config?: {
    sensitivity?: number;
    threshold?: number;
    minDataPoints?: number;
  }) {
    if (config) {
      this.sensitivity = config.sensitivity || this.sensitivity;
      this.threshold = config.threshold || this.threshold;
      this.minDataPoints = config.minDataPoints || this.minDataPoints;
    }
  }

  /**
   * 检测瓶颈信号
   */
  async detectBottleneckSignals(
    data: MarginalAnalysisData[],
    analysisScope?: {
      businessUnits?: string[];
      processTypes?: string[];
    }
  ): Promise<MarginalAnalysisResult> {
    try {
      // 数据验证
      if (data.length < this.minDataPoints) {
        throw new Error(`数据点不足，需要至少${this.minDataPoints}个数据点`);
      }

      // 计算边际分析指标
      const marginalMetrics = this.calculateMarginalMetrics(data);
      
      // 检测瓶颈信号
      const signals = await this.detectSignals(data, marginalMetrics);
      
      // 计算分析摘要
      const analysisSummary = this.calculateAnalysisSummary(signals);
      
      return {
        success: true,
        signals,
        analysisSummary,
        marginalMetrics
      };
      
    } catch (error) {
      return {
        success: false,
        signals: [],
        analysisSummary: {
          totalSignals: 0,
          highSeverity: 0,
          mediumSeverity: 0,
          lowSeverity: 0,
          analysisConfidence: 0
        },
        marginalMetrics: {
          marginalCost: 0,
          marginalRevenue: 0,
          marginalProfit: 0,
          optimalQuantity: 0
        }
      };
    }
  }

  /**
   * 计算边际分析指标
   */
  private calculateMarginalMetrics(data: MarginalAnalysisData[]): {
    marginalCost: number;
    marginalRevenue: number;
    marginalProfit: number;
    optimalQuantity: number;
  } {
    if (data.length < 2) {
      return {
        marginalCost: 0,
        marginalRevenue: 0,
        marginalProfit: 0,
        optimalQuantity: 0
      };
    }

    // 按数量排序
    const sortedData = [...data].sort((a, b) => a.quantity - b.quantity);
    
    // 计算边际成本
    const marginalCost = this.calculateMarginalCost(sortedData);
    
    // 计算边际收入
    const marginalRevenue = this.calculateMarginalRevenue(sortedData);
    
    // 计算边际利润
    const marginalProfit = marginalRevenue - marginalCost;
    
    // 计算最优数量（边际利润为0的点）
    const optimalQuantity = this.calculateOptimalQuantity(sortedData, marginalCost, marginalRevenue);
    
    return {
      marginalCost,
      marginalRevenue,
      marginalProfit,
      optimalQuantity
    };
  }

  /**
   * 计算边际成本
   */
  private calculateMarginalCost(data: MarginalAnalysisData[]): number {
    if (data.length < 2) return 0;
    
    const totalCosts = data.map(d => d.cost);
    const quantities = data.map(d => d.quantity);
    
    // 使用线性回归计算边际成本
    const slope = this.calculateSlope(quantities, totalCosts);
    return slope;
  }

  /**
   * 计算边际收入
   */
  private calculateMarginalRevenue(data: MarginalAnalysisData[]): number {
    if (data.length < 2) return 0;
    
    const totalRevenues = data.map(d => d.revenue);
    const quantities = data.map(d => d.quantity);
    
    // 使用线性回归计算边际收入
    const slope = this.calculateSlope(quantities, totalRevenues);
    return slope;
  }

  /**
   * 计算最优数量
   */
  private calculateOptimalQuantity(
    data: MarginalAnalysisData[],
    marginalCost: number,
    marginalRevenue: number
  ): number {
    if (Math.abs(marginalCost - marginalRevenue) < 0.01) {
      // 边际成本等于边际收入，返回最大数量
      return Math.max(...data.map(d => d.quantity));
    }
    
    // 使用插值法找到边际利润为0的点
    const quantities = data.map(d => d.quantity);
    const costs = data.map(d => d.cost);
    const revenues = data.map(d => d.revenue);
    
    // 寻找边际利润最接近0的数量点
    let optimalQuantity = quantities[0];
    let minProfitDiff = Infinity;
    
    for (let i = 0; i < quantities.length - 1; i++) {
      const q1 = quantities[i];
      const q2 = quantities[i + 1];
      const c1 = costs[i];
      const c2 = costs[i + 1];
      const r1 = revenues[i];
      const r2 = revenues[i + 1];
      
      const marginalCostAtQ1 = (c2 - c1) / (q2 - q1);
      const marginalRevenueAtQ1 = (r2 - r1) / (q2 - q1);
      const marginalProfitAtQ1 = marginalRevenueAtQ1 - marginalCostAtQ1;
      
      if (Math.abs(marginalProfitAtQ1) < minProfitDiff) {
        minProfitDiff = Math.abs(marginalProfitAtQ1);
        optimalQuantity = q1;
      }
    }
    
    return optimalQuantity;
  }

  /**
   * 检测信号
   */
  private async detectSignals(
    data: MarginalAnalysisData[],
    marginalMetrics: any
  ): Promise<BottleneckSignal[]> {
    const signals: BottleneckSignal[] = [];
    
    // 检测效率瓶颈
    const efficiencySignals = this.detectEfficiencyBottlenecks(data);
    signals.push(...efficiencySignals);
    
    // 检测成本瓶颈
    const costSignals = this.detectCostBottlenecks(data, marginalMetrics);
    signals.push(...costSignals);
    
    // 检测收入瓶颈
    const revenueSignals = this.detectRevenueBottlenecks(data, marginalMetrics);
    signals.push(...revenueSignals);
    
    return signals;
  }

  /**
   * 检测效率瓶颈
   */
  private detectEfficiencyBottlenecks(data: MarginalAnalysisData[]): BottleneckSignal[] {
    const signals: BottleneckSignal[] = [];
    
    // 计算效率趋势
    const efficiencyTrend = this.calculateTrend(data.map(d => d.efficiency));
    
    // 检测效率下降
    if (efficiencyTrend < -0.1) { // 效率下降超过10%
      const severity = this.calculateSeverity(Math.abs(efficiencyTrend));
      
      signals.push({
        signalId: `efficiency_${Date.now()}`,
        signalType: 'efficiency_drop',
        severity,
        process: '生产流程',
        businessUnit: '生产部',
        detectedAt: new Date().toISOString(),
        description: `生产效率下降${(Math.abs(efficiencyTrend) * 100).toFixed(1)}%，存在瓶颈`,
        impactScore: Math.abs(efficiencyTrend),
        recommendations: [
          '检查生产设备状态',
          '优化生产流程',
          '增加人员培训',
          '检查原材料质量'
        ],
        relatedMetrics: {
          efficiencyScore: data[data.length - 1].efficiency,
          marginalCost: 0,
          marginalRevenue: 0
        }
      });
    }
    
    return signals;
  }

  /**
   * 检测成本瓶颈
   */
  private detectCostBottlenecks(
    data: MarginalAnalysisData[],
    marginalMetrics: any
  ): BottleneckSignal[] {
    const signals: BottleneckSignal[] = [];
    
    // 检测边际成本异常
    if (marginalMetrics.marginalCost > this.threshold) {
      const severity = this.calculateSeverity(marginalMetrics.marginalCost);
      
      signals.push({
        signalId: `cost_${Date.now()}`,
        signalType: 'cost_spike',
        severity,
        process: '成本控制',
        businessUnit: '财务部',
        detectedAt: new Date().toISOString(),
        description: `边际成本过高，存在成本瓶颈`,
        impactScore: marginalMetrics.marginalCost,
        recommendations: [
          '优化供应链管理',
          '降低原材料成本',
          '提高生产效率',
          '重新评估定价策略'
        ],
        relatedMetrics: {
          efficiencyScore: 0,
          marginalCost: marginalMetrics.marginalCost,
          marginalRevenue: marginalMetrics.marginalRevenue
        }
      });
    }
    
    return signals;
  }

  /**
   * 检测收入瓶颈
   */
  private detectRevenueBottlenecks(
    data: MarginalAnalysisData[],
    marginalMetrics: any
  ): BottleneckSignal[] {
    const signals: BottleneckSignal[] = [];
    
    // 检测边际收入下降
    if (marginalMetrics.marginalRevenue < 0) {
      const severity = this.calculateSeverity(Math.abs(marginalMetrics.marginalRevenue));
      
      signals.push({
        signalId: `revenue_${Date.now()}`,
        signalType: 'revenue_decline',
        severity,
        process: '销售流程',
        businessUnit: '销售部',
        detectedAt: new Date().toISOString(),
        description: `边际收入为负，存在收入瓶颈`,
        impactScore: Math.abs(marginalMetrics.marginalRevenue),
        recommendations: [
          '优化产品定价',
          '提高产品价值',
          '加强市场推广',
          '改善客户体验'
        ],
        relatedMetrics: {
          efficiencyScore: 0,
          marginalCost: marginalMetrics.marginalCost,
          marginalRevenue: marginalMetrics.marginalRevenue
        }
      });
    }
    
    return signals;
  }

  /**
   * 计算趋势
   */
  private calculateTrend(values: number[]): number {
    if (values.length < 2) return 0;
    
    const n = values.length;
    const x = Array.from({ length: n }, (_, i) => i);
    const y = values;
    
    // 计算线性回归斜率
    const slope = this.calculateSlope(x, y);
    return slope;
  }

  /**
   * 计算斜率（线性回归）
   */
  private calculateSlope(x: number[], y: number[]): number {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);
    
    return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  }

  /**
   * 计算严重程度
   */
  private calculateSeverity(value: number): 'low' | 'medium' | 'high' | 'critical' {
    if (value < 0.3) return 'low';
    if (value < 0.6) return 'medium';
    if (value < 0.8) return 'high';
    return 'critical';
  }

  /**
   * 计算分析摘要
   */
  private calculateAnalysisSummary(signals: BottleneckSignal[]): {
    totalSignals: number;
    highSeverity: number;
    mediumSeverity: number;
    lowSeverity: number;
    analysisConfidence: number;
  } {
    const severityCounts = signals.reduce((acc, signal) => {
      acc[signal.severity]++;
      return acc;
    }, { low: 0, medium: 0, high: 0, critical: 0 });
    
    // 计算分析置信度
    const confidence = Math.min(1, Math.max(0, 1 - (signals.length * 0.1)));
    
    return {
      totalSignals: signals.length,
      highSeverity: severityCounts.high + severityCounts.critical,
      mediumSeverity: severityCounts.medium,
      lowSeverity: severityCounts.low,
      analysisConfidence: confidence
    };
  }
}

/**
 * 边际分析计算器
 */
export class MarginalAnalysisCalculator {
  /**
   * 计算边际分析
   */
  static calculateMarginalAnalysis(data: MarginalAnalysisData[]): {
    marginalCost: number;
    marginalRevenue: number;
    marginalProfit: number;
    optimalQuantity: number;
    profitMaximizationPoint: {
      quantity: number;
      totalProfit: number;
      marginalProfit: number;
    };
  } {
    if (data.length < 2) {
      return {
        marginalCost: 0,
        marginalRevenue: 0,
        marginalProfit: 0,
        optimalQuantity: 0,
        profitMaximizationPoint: {
          quantity: 0,
          totalProfit: 0,
          marginalProfit: 0
        }
      };
    }

    // 按数量排序
    const sortedData = [...data].sort((a, b) => a.quantity - b.quantity);
    
    // 计算边际成本
    const marginalCost = this.calculateMarginalCost(sortedData);
    
    // 计算边际收入
    const marginalRevenue = this.calculateMarginalRevenue(sortedData);
    
    // 计算边际利润
    const marginalProfit = marginalRevenue - marginalCost;
    
    // 计算最优数量
    const optimalQuantity = this.calculateOptimalQuantity(sortedData, marginalCost, marginalRevenue);
    
    // 计算利润最大化点
    const profitMaximizationPoint = this.calculateProfitMaximizationPoint(
      sortedData, 
      marginalCost, 
      marginalRevenue
    );
    
    return {
      marginalCost,
      marginalRevenue,
      marginalProfit,
      optimalQuantity,
      profitMaximizationPoint
    };
  }

  private static calculateMarginalCost(data: MarginalAnalysisData[]): number {
    if (data.length < 2) return 0;
    
    const totalCosts = data.map(d => d.cost);
    const quantities = data.map(d => d.quantity);
    
    return this.calculateSlope(quantities, totalCosts);
  }

  private static calculateMarginalRevenue(data: MarginalAnalysisData[]): number {
    if (data.length < 2) return 0;
    
    const totalRevenues = data.map(d => d.revenue);
    const quantities = data.map(d => d.quantity);
    
    return this.calculateSlope(quantities, totalRevenues);
  }

  private static calculateOptimalQuantity(
    data: MarginalAnalysisData[],
    marginalCost: number,
    marginalRevenue: number
  ): number {
    if (Math.abs(marginalCost - marginalRevenue) < 0.01) {
      return Math.max(...data.map(d => d.quantity));
    }
    
    // 寻找边际利润最接近0的点
    let optimalQuantity = data[0].quantity;
    let minProfitDiff = Infinity;
    
    for (let i = 0; i < data.length - 1; i++) {
      const q1 = data[i].quantity;
      const q2 = data[i + 1].quantity;
      const c1 = data[i].cost;
      const c2 = data[i + 1].cost;
      const r1 = data[i].revenue;
      const r2 = data[i + 1].revenue;
      
      const marginalCostAtQ1 = (c2 - c1) / (q2 - q1);
      const marginalRevenueAtQ1 = (r2 - r1) / (q2 - q1);
      const marginalProfitAtQ1 = marginalRevenueAtQ1 - marginalCostAtQ1;
      
      if (Math.abs(marginalProfitAtQ1) < minProfitDiff) {
        minProfitDiff = Math.abs(marginalProfitAtQ1);
        optimalQuantity = q1;
      }
    }
    
    return optimalQuantity;
  }

  private static calculateProfitMaximizationPoint(
    data: MarginalAnalysisData[],
    marginalCost: number,
    marginalRevenue: number
  ): { quantity: number; totalProfit: number; marginalProfit: number } {
    const optimalQuantity = this.calculateOptimalQuantity(data, marginalCost, marginalRevenue);
    
    // 找到对应的数据点
    const optimalDataPoint = data.find(d => d.quantity === optimalQuantity) || data[0];
    
    return {
      quantity: optimalQuantity,
      totalProfit: optimalDataPoint.revenue - optimalDataPoint.cost,
      marginalProfit: marginalRevenue - marginalCost
    };
  }

  private static calculateSlope(x: number[], y: number[]): number {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);
    
    return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  }
}

