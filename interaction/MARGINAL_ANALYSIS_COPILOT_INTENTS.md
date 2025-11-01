# 边际分析AI Copilot意图文档

## 概述

本文档定义了边际分析系统的15个核心AI Copilot意图，包括自然语言交互、智能建议、自动化操作和决策支持功能。

## AI Copilot架构

### 意图识别流程
```
用户输入 → 意图识别 → 参数提取 → 业务逻辑 → 结果生成 → 响应输出
```

### 技术栈
- **NLP引擎**: OpenAI GPT-4 / Claude
- **意图识别**: 基于规则 + 机器学习
- **参数提取**: 命名实体识别 (NER)
- **响应生成**: 模板 + 动态内容

## 核心意图定义

### 1. 资产价值分析意图

#### 意图标识
`ANALYZE_ASSET_VALUE`

#### 触发关键词
- "分析资产价值"
- "计算资产NPV"
- "资产投资回报"
- "资产价值评估"

#### 参数提取
```typescript
interface AssetValueAnalysisParams {
  assetId?: string;
  assetName?: string;
  timeRange?: {
    start: string;
    end: string;
  };
  analysisType: 'npv' | 'roi' | 'trend' | 'comparison';
  includePredictions?: boolean;
}
```

#### 响应模板
```
基于您的要求，我已经分析了{assetName}的价值情况：

📊 **当前价值指标**
- NPV: ¥{npv} (折现率: {discountRate}%)
- ROI: {roi}%
- 投资回收期: {paybackPeriod}年

📈 **价值趋势**
{trendChart}

💡 **优化建议**
1. {suggestion1}
2. {suggestion2}
3. {suggestion3}

需要我进一步分析其他方面吗？
```

### 2. 能力价值评估意图

#### 意图标识
`EVALUATE_CAPABILITY_VALUE`

#### 触发关键词
- "评估能力价值"
- "能力贡献分析"
- "能力投资回报"
- "能力价值量化"

#### 参数提取
```typescript
interface CapabilityValueParams {
  capabilityId?: string;
  capabilityName?: string;
  evaluationPeriod?: string;
  includeComparison?: boolean;
  benchmarkCapabilities?: string[];
}
```

#### 响应模板
```
我已经完成了{capabilityName}的价值评估：

🎯 **能力价值指标**
- 年度贡献: ¥{annualContribution}
- 贡献百分比: {contributionPercentage}%
- 价值评分: {valueScore}/10

📊 **能力分析**
- 能力级别: {capabilityLevel}
- 稳定成果: {stableOutputs}
- 提升潜力: {improvementPotential}%

🔍 **对比分析**
{comparisonTable}

💡 **提升建议**
1. {improvement1}
2. {improvement2}
```

### 3. 产品价值雷达图意图

#### 意图标识
`GENERATE_PRODUCT_RADAR`

#### 触发关键词
- "产品价值雷达图"
- "产品价值分析"
- "产品竞争力评估"
- "产品价值对比"

#### 参数提取
```typescript
interface ProductRadarParams {
  productIds: string[];
  comparisonProducts?: string[];
  valueCategories: ('intrinsic' | 'cognitive' | 'experiential')[];
  includeTrends?: boolean;
  timeRange?: string;
}
```

#### 响应模板
```
我为您生成了产品价值雷达图分析：

🎯 **产品价值总览**
{productRadarChart}

📊 **三类价值得分**
- 内在价值: {intrinsicScore}/10
- 认知价值: {cognitiveScore}/10  
- 体验价值: {experientialScore}/10

📈 **价值趋势**
{valueTrendChart}

💡 **优化建议**
1. 提升{weakestCategory}价值
2. 加强{strongestCategory}优势
3. 平衡三类价值发展
```

### 4. 边际贡献分析意图

#### 意图标识
`ANALYZE_MARGINAL_CONTRIBUTION`

#### 触发关键词
- "边际贡献分析"
- "Shapley值分析"
- "因素贡献度"
- "边际影响分析"

#### 参数提取
```typescript
interface MarginalContributionParams {
  targetMetric: string;
  factors: string[];
  timePeriod: {
    start: string;
    end: string;
  };
  analysisMethod: 'shapley' | 'regression' | 'correlation';
  includeSignificance?: boolean;
}
```

#### 响应模板
```
我已经完成了边际贡献分析：

🎯 **目标指标**: {targetMetric} (¥{totalValue})

📊 **边际贡献排名**
1. {factor1}: {contribution1}% (¥{value1})
2. {factor2}: {contribution2}% (¥{value2})
3. {factor3}: {contribution3}% (¥{value3})

📈 **贡献分析图表**
{contributionChart}

🔍 **显著性分析**
- 显著因素: {significantFactors}
- 不显著因素: {insignificantFactors}

💡 **优化建议**
1. 重点投入{topFactor}
2. 优化{lowFactor}效率
3. 考虑因素协同效应
```

### 5. 时间序列预测意图

#### 意图标识
`FORECAST_TIME_SERIES`

#### 触发关键词
- "时间序列预测"
- "趋势分析"
- "未来预测"
- "预测分析"

#### 参数提取
```typescript
interface TimeSeriesForecastParams {
  metric: string;
  timeRange: {
    start: string;
    end: string;
  };
  forecastPeriod: number; // 月数
  confidenceLevel: number; // 0-1
  includeSeasonality?: boolean;
  includeTrend?: boolean;
}
```

#### 响应模板
```
我已经完成了{metric}的时间序列预测：

📈 **历史趋势**
{historicalTrendChart}

🔮 **未来预测**
- 下月预测: ¥{nextMonthPrediction}
- 3个月预测: ¥{threeMonthPrediction}
- 6个月预测: ¥{sixMonthPrediction}

📊 **预测置信度**
- 整体置信度: {confidenceLevel}%
- 趋势强度: {trendStrength}
- 季节性: {seasonalityDetected}

⚠️ **风险提示**
{riskWarnings}

💡 **建议**
1. {suggestion1}
2. {suggestion2}
```

### 6. 决策循环触发意图

#### 意图标识
`TRIGGER_DECISION_CYCLE`

#### 触发关键词
- "触发决策循环"
- "执行决策分析"
- "启动决策流程"
- "决策循环分析"

#### 参数提取
```typescript
interface DecisionCycleParams {
  triggerType: 'manual' | 'scheduled' | 'event_driven';
  analysisScope: {
    businessUnits: string[];
    timePeriod: string;
  };
  analysisConfig: {
    includeMarginalAnalysis: boolean;
    includeSynergyAnalysis: boolean;
    includeProcessOptimization: boolean;
  };
  priority: 'high' | 'medium' | 'low';
}
```

#### 响应模板
```
我已经触发了决策循环分析：

🔄 **决策循环状态**
- 执行ID: {executionId}
- 状态: {status}
- 预计完成时间: {estimatedCompletion}

📊 **分析范围**
- 业务单元: {businessUnits}
- 时间周期: {timePeriod}
- 分析类型: {analysisTypes}

⏱️ **执行进度**
{progressBar}

📋 **下一步操作**
1. 等待分析完成
2. 查看分析结果
3. 进行管理者评价
```

### 7. 管理者评价意图

#### 意图标识
`MANAGER_EVALUATION`

#### 触发关键词
- "管理者评价"
- "评价分析结果"
- "确认分析"
- "调整指标"

#### 参数提取
```typescript
interface ManagerEvaluationParams {
  analysisId: string;
  evaluationType: 'confirm' | 'adjust' | 'reject';
  evaluationContent: string;
  metricAdjustments: Array<{
    metricId: string;
    adjustedValue: number;
    adjustmentReason: string;
  }>;
  implementationPlan?: {
    startDate: string;
    duration: number;
    responsiblePerson: string;
  };
}
```

#### 响应模板
```
我已经记录了您的管理者评价：

📝 **评价详情**
- 分析ID: {analysisId}
- 评价类型: {evaluationType}
- 评价内容: {evaluationContent}

📊 **指标调整**
{metricAdjustmentsTable}

📋 **实施计划**
- 开始日期: {startDate}
- 执行周期: {duration}天
- 负责人: {responsiblePerson}

✅ **确认信息**
您的评价已保存，系统将根据您的反馈调整后续分析。
```

### 8. 数据导入指导意图

#### 意图标识
`GUIDE_DATA_IMPORT`

#### 触发关键词
- "数据导入"
- "上传数据"
- "导入指导"
- "数据模板"

#### 参数提取
```typescript
interface DataImportGuideParams {
  dataType: 'asset' | 'capability' | 'value_item' | 'metric' | 'feedback' | 'model' | 'business_fact';
  importMethod: 'excel' | 'csv' | 'api';
  userExperience: 'beginner' | 'intermediate' | 'advanced';
  specificQuestions?: string[];
}
```

#### 响应模板
```
我来指导您完成{dataType}数据导入：

📋 **导入步骤**
1. 下载模板: {templateLink}
2. 填写数据: {dataGuidance}
3. 上传文件: {uploadInstructions}
4. 验证数据: {validationSteps}

📊 **数据要求**
{dataRequirements}

⚠️ **注意事项**
{warnings}

❓ **常见问题**
{faq}

需要我详细解释某个步骤吗？
```

### 9. 系统诊断意图

#### 意图标识
`SYSTEM_DIAGNOSTICS`

#### 触发关键词
- "系统诊断"
- "检查系统状态"
- "性能分析"
- "问题排查"

#### 参数提取
```typescript
interface SystemDiagnosticsParams {
  diagnosticType: 'performance' | 'data_quality' | 'model_accuracy' | 'user_activity';
  timeRange?: string;
  includeRecommendations?: boolean;
  alertLevel?: 'info' | 'warning' | 'error' | 'critical';
}
```

#### 响应模板
```
我已经完成了系统诊断：

🔍 **诊断结果**
- 系统状态: {systemStatus}
- 性能评分: {performanceScore}/100
- 数据质量: {dataQualityScore}/100
- 模型准确率: {modelAccuracy}%

📊 **详细指标**
{diagnosticMetrics}

⚠️ **发现的问题**
{issuesList}

💡 **优化建议**
{recommendations}

🔧 **自动修复**
{autoFixActions}
```

### 10. 成本优化建议意图

#### 意图标识
`COST_OPTIMIZATION_ADVICE`

#### 触发关键词
- "成本优化"
- "节省成本"
- "优化建议"
- "成本分析"

#### 参数提取
```typescript
interface CostOptimizationParams {
  optimizationArea: 'infrastructure' | 'operations' | 'data_processing' | 'model_training';
  currentCost: number;
  targetReduction: number;
  timeHorizon: number; // 月数
  constraints?: string[];
}
```

#### 响应模板
```
我为您分析了成本优化方案：

💰 **当前成本分析**
- 月度成本: ¥{currentCost}
- 主要成本项: {costBreakdown}

🎯 **优化目标**
- 目标降幅: {targetReduction}%
- 预期节省: ¥{expectedSavings}/月

📊 **优化方案**
{optimizationPlans}

⏱️ **实施时间线**
{implementationTimeline}

💡 **具体建议**
1. {suggestion1}
2. {suggestion2}
3. {suggestion3}
```

### 11. 报告生成意图

#### 意图标识
`GENERATE_REPORT`

#### 触发关键词
- "生成报告"
- "创建报告"
- "导出报告"
- "分析报告"

#### 参数提取
```typescript
interface ReportGenerationParams {
  reportType: 'executive' | 'technical' | 'operational' | 'financial';
  timeRange: {
    start: string;
    end: string;
  };
  includeCharts: boolean;
  includeRecommendations: boolean;
  format: 'pdf' | 'excel' | 'html';
  recipients?: string[];
}
```

#### 响应模板
```
我已经为您生成了{reportType}报告：

📋 **报告信息**
- 报告类型: {reportType}
- 时间范围: {timeRange}
- 生成时间: {generationTime}

📊 **报告内容**
{reportSections}

📈 **包含图表**
{chartList}

💡 **关键发现**
{keyFindings}

📤 **导出选项**
- PDF: {pdfLink}
- Excel: {excelLink}
- HTML: {htmlLink}
```

### 12. 异常检测意图

#### 意图标识
`DETECT_ANOMALIES`

#### 触发关键词
- "异常检测"
- "发现异常"
- "异常分析"
- "异常监控"

#### 参数提取
```typescript
interface AnomalyDetectionParams {
  dataSource: string;
  timeRange: {
    start: string;
    end: string;
  };
  sensitivity: 'low' | 'medium' | 'high';
  anomalyTypes: ('statistical' | 'pattern' | 'trend' | 'seasonal')[];
  includeExplanation?: boolean;
}
```

#### 响应模板
```
我已经完成了异常检测分析：

🚨 **检测结果**
- 异常数量: {anomalyCount}
- 严重程度: {severityLevel}
- 影响范围: {impactScope}

📊 **异常详情**
{anomalyDetails}

🔍 **异常分析**
{anomalyAnalysis}

💡 **处理建议**
1. {action1}
2. {action2}
3. {action3}

⚠️ **紧急处理**
{urgentActions}
```

### 13. 协同效应分析意图

#### 意图标识
`ANALYZE_SYNERGY_EFFECTS`

#### 触发关键词
- "协同效应分析"
- "协同作用"
- "协同优化"
- "协同价值"

#### 参数提取
```typescript
interface SynergyAnalysisParams {
  factors: string[];
  targetMetric: string;
  timePeriod: {
    start: string;
    end: string;
  };
  synergyType: 'resource_capability' | 'process_optimization' | 'value_creation';
  includeInteractionEffects?: boolean;
}
```

#### 响应模板
```
我已经完成了协同效应分析：

🤝 **协同效应总览**
- 协同系数: {synergyCoefficient}
- 协同价值: ¥{synergyValue}
- 优化潜力: {optimizationPotential}%

📊 **因素协同矩阵**
{synergyMatrix}

🔍 **协同分析**
- 最强协同: {strongestSynergy}
- 协同机会: {synergyOpportunities}
- 协同风险: {synergyRisks}

💡 **协同优化建议**
1. {synergySuggestion1}
2. {synergySuggestion2}
```

### 14. 流程优化意图

#### 意图标识
`OPTIMIZE_PROCESSES`

#### 触发关键词
- "流程优化"
- "流程分析"
- "效率提升"
- "流程改进"

#### 参数提取
```typescript
interface ProcessOptimizationParams {
  processType: 'production' | 'propagation' | 'delivery';
  optimizationGoal: 'efficiency' | 'cost' | 'quality' | 'speed';
  timeRange: {
    start: string;
    end: string;
  };
  includeBottleneckAnalysis?: boolean;
  includeResourceAllocation?: boolean;
}
```

#### 响应模板
```
我已经完成了{processType}流程优化分析：

⚡ **优化结果**
- 效率提升: {efficiencyGain}%
- 成本节省: ¥{costSaving}
- 质量改善: {qualityImprovement}%

📊 **流程分析**
{processAnalysis}

🔍 **瓶颈识别**
{bottleneckAnalysis}

💡 **优化方案**
{optimizationPlans}

📋 **实施建议**
{implementationRecommendations}
```

### 15. 智能推荐意图

#### 意图标识
`INTELLIGENT_RECOMMENDATIONS`

#### 触发关键词
- "智能推荐"
- "建议分析"
- "推荐方案"
- "优化建议"

#### 参数提取
```typescript
interface IntelligentRecommendationParams {
  recommendationType: 'investment' | 'resource_allocation' | 'process_improvement' | 'strategic_planning';
  userContext: {
    role: string;
    department: string;
    currentFocus: string[];
  };
  priority: 'high' | 'medium' | 'low';
  timeHorizon: 'short' | 'medium' | 'long';
}
```

#### 响应模板
```
我为您生成了个性化智能推荐：

🎯 **推荐概览**
- 推荐类型: {recommendationType}
- 优先级: {priority}
- 时间范围: {timeHorizon}

📊 **推荐方案**
{recommendationPlans}

💡 **具体建议**
1. {recommendation1}
2. {recommendation2}
3. {recommendation3}

📈 **预期效果**
{expectedOutcomes}

🎯 **下一步行动**
{nextActions}
```

## 意图识别引擎

### 1. 自然语言处理
```typescript
class IntentRecognizer {
  async recognizeIntent(userInput: string): Promise<IntentResult> {
    // 1. 预处理
    const processedInput = this.preprocessInput(userInput);
    
    // 2. 意图分类
    const intent = await this.classifyIntent(processedInput);
    
    // 3. 参数提取
    const parameters = await this.extractParameters(processedInput, intent);
    
    // 4. 置信度评估
    const confidence = await this.calculateConfidence(intent, parameters);
    
    return {
      intent,
      parameters,
      confidence,
      alternatives: await this.getAlternatives(intent, confidence)
    };
  }
}
```

### 2. 参数提取
```typescript
class ParameterExtractor {
  async extractParameters(input: string, intent: string): Promise<any> {
    const entities = await this.extractEntities(input);
    const parameters = {};
    
    switch (intent) {
      case 'ANALYZE_ASSET_VALUE':
        parameters.assetId = entities.assetId;
        parameters.assetName = entities.assetName;
        parameters.timeRange = entities.timeRange;
        break;
      // ... 其他意图
    }
    
    return parameters;
  }
}
```

### 3. 响应生成
```typescript
class ResponseGenerator {
  async generateResponse(intent: string, parameters: any, context: any): Promise<string> {
    const template = await this.getTemplate(intent);
    const data = await this.fetchData(parameters, context);
    const response = await this.renderTemplate(template, data);
    
    return response;
  }
}
```

## 上下文管理

### 1. 对话上下文
```typescript
interface ConversationContext {
  sessionId: string;
  userId: string;
  currentIntent?: string;
  previousIntents: string[];
  userPreferences: UserPreferences;
  systemState: SystemState;
  conversationHistory: ConversationTurn[];
}
```

### 2. 用户偏好
```typescript
interface UserPreferences {
  language: string;
  timezone: string;
  dataFormat: 'currency' | 'percentage' | 'number';
  chartPreferences: ChartPreferences;
  notificationSettings: NotificationSettings;
}
```

### 3. 系统状态
```typescript
interface SystemState {
  availableData: string[];
  activeAnalyses: string[];
  userPermissions: string[];
  systemLoad: number;
  lastUpdate: Date;
}
```

## 错误处理

### 1. 意图识别错误
```typescript
class IntentErrorHandler {
  handleRecognitionError(error: Error, userInput: string): string {
    if (error.name === 'IntentNotFound') {
      return this.suggestSimilarIntents(userInput);
    } else if (error.name === 'ParameterExtractionError') {
      return this.requestClarification(error.missingParameters);
    } else {
      return this.genericErrorResponse();
    }
  }
}
```

### 2. 业务逻辑错误
```typescript
class BusinessLogicErrorHandler {
  handleBusinessError(error: Error, context: any): string {
    switch (error.name) {
      case 'DataNotFound':
        return this.suggestDataAlternatives(context);
      case 'PermissionDenied':
        return this.explainPermissions(context);
      case 'ValidationError':
        return this.explainValidationErrors(error.details);
      default:
        return this.genericBusinessErrorResponse();
    }
  }
}
```

## 性能优化

### 1. 意图缓存
```typescript
class IntentCache {
  private cache = new Map<string, IntentResult>();
  
  async getCachedIntent(userInput: string): Promise<IntentResult | null> {
    const key = this.generateCacheKey(userInput);
    return this.cache.get(key) || null;
  }
  
  setCachedIntent(userInput: string, result: IntentResult): void {
    const key = this.generateCacheKey(userInput);
    this.cache.set(key, result);
  }
}
```

### 2. 响应缓存
```typescript
class ResponseCache {
  private cache = new Map<string, string>();
  
  async getCachedResponse(intent: string, parameters: any): Promise<string | null> {
    const key = this.generateResponseKey(intent, parameters);
    return this.cache.get(key) || null;
  }
}
```

## 监控和分析

### 1. 意图使用统计
```typescript
interface IntentUsageStats {
  intent: string;
  usageCount: number;
  successRate: number;
  averageResponseTime: number;
  userSatisfaction: number;
  commonErrors: string[];
}
```

### 2. 用户行为分析
```typescript
interface UserBehaviorAnalysis {
  userId: string;
  mostUsedIntents: string[];
  intentSequences: string[][];
  averageSessionLength: number;
  satisfactionScore: number;
  improvementSuggestions: string[];
}
```

## 测试策略

### 1. 意图识别测试
```typescript
describe('Intent Recognition', () => {
  it('should recognize asset value analysis intent', async () => {
    const input = '分析生产设备A的价值';
    const result = await intentRecognizer.recognizeIntent(input);
    
    expect(result.intent).toBe('ANALYZE_ASSET_VALUE');
    expect(result.parameters.assetName).toBe('生产设备A');
    expect(result.confidence).toBeGreaterThan(0.8);
  });
});
```

### 2. 参数提取测试
```typescript
describe('Parameter Extraction', () => {
  it('should extract time range from input', async () => {
    const input = '分析2024年1月到3月的数据';
    const parameters = await parameterExtractor.extractParameters(input, 'ANALYZE_ASSET_VALUE');
    
    expect(parameters.timeRange).toEqual({
      start: '2024-01-01',
      end: '2024-03-31'
    });
  });
});
```

### 3. 响应生成测试
```typescript
describe('Response Generation', () => {
  it('should generate appropriate response for asset analysis', async () => {
    const intent = 'ANALYZE_ASSET_VALUE';
    const parameters = { assetName: '生产设备A' };
    const response = await responseGenerator.generateResponse(intent, parameters, context);
    
    expect(response).toContain('生产设备A');
    expect(response).toContain('NPV');
    expect(response).toContain('ROI');
  });
});
```

