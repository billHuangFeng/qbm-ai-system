# 模块1: 全链条价值传递 - 需求规格说明书

## 1. 功能概述

### 1.1 功能描述
全链条价值传递模块是商业模式动态优化系统的核心模块，负责分析和管理从"核心资源+能力→产品特性→价值主张→客户感知→体验价值→客户买单"的完整价值链，通过量化分析各环节效率，识别优化机会，提供精准的归因分析和优化建议。

### 1.2 业务价值
- **量化价值链效率**: 将抽象的价值链转化为可量化的指标，实现精准管理
- **识别优化机会**: 通过数据分析发现价值链中的瓶颈和低效环节
- **精准归因分析**: 使用Shapley算法计算各渠道/活动的真实贡献度
- **数据驱动决策**: 为商业模式优化提供科学的数据支撑

### 1.3 用户角色
- **业务分析师**: 分析价值链效率，识别优化机会
- **营销经理**: 了解各渠道的真实贡献度，优化营销投入
- **产品经理**: 分析产品特性对客户价值的影响
- **决策者**: 基于数据做出商业模式优化决策

## 2. 功能需求

### 2.1 功能列表
- [ ] **价值链分析引擎**: 分析价值链各环节的效率和转化率
- [ ] **归因分析引擎**: 使用Shapley算法计算各渠道/活动的贡献度
- [ ] **优化建议生成**: 基于分析结果生成具体的优化建议
- [ ] **价值链可视化**: 提供直观的价值链分析图表
- [ ] **历史趋势分析**: 分析价值链效率的历史变化趋势
- [ ] **实时监控**: 实时监控价值链各环节的关键指标

### 2.2 输入输出

#### 输入
- **订单数据**: 客户订单信息，包含产品、渠道、时间等
- **客户数据**: 客户基本信息、行为数据、反馈数据
- **产品数据**: 产品特性、价格、库存等信息
- **渠道数据**: 营销渠道、转化渠道、成本数据
- **活动数据**: 营销活动、促销活动、推广活动数据

#### 输出
- **价值链分析报告**: 各环节效率分析、瓶颈识别
- **归因分析结果**: 各渠道/活动的贡献度排名
- **优化建议**: 具体的优化措施和预期效果
- **可视化图表**: 价值链流程图、效率对比图、趋势图
- **实时监控面板**: 关键指标的实时监控界面

### 2.3 业务规则
- **数据完整性**: 所有输入数据必须完整，缺失数据需要标记处理
- **时间一致性**: 分析时间窗口内的数据必须保持时间一致性
- **归因公平性**: 使用Shapley算法确保归因分析的公平性
- **优化可行性**: 生成的优化建议必须具有可操作性
- **结果可追溯**: 所有分析结果必须可以追溯到原始数据

## 3. 技术需求

### 3.1 API接口

#### 3.1.1 价值链分析接口
- **接口**: POST /api/v1/value-chain/analyze
- **描述**: 分析价值链各环节效率
- **参数**:
```json
{
  "time_range": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "analysis_type": "comprehensive",
  "include_trends": true
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "chain_analysis": {
      "core_resources": {
        "efficiency": 0.85,
        "conversion_rate": 0.78,
        "bottleneck": "supplier_delivery"
      },
      "product_features": {
        "efficiency": 0.92,
        "conversion_rate": 0.88,
        "bottleneck": "feature_development"
      },
      "value_proposition": {
        "efficiency": 0.76,
        "conversion_rate": 0.82,
        "bottleneck": "communication"
      },
      "customer_perception": {
        "efficiency": 0.89,
        "conversion_rate": 0.91,
        "bottleneck": "experience_design"
      },
      "experience_value": {
        "efficiency": 0.94,
        "conversion_rate": 0.87,
        "bottleneck": "service_quality"
      },
      "customer_purchase": {
        "efficiency": 0.88,
        "conversion_rate": 0.93,
        "bottleneck": "payment_process"
      }
    },
    "overall_efficiency": 0.87,
    "bottlenecks": [
      {
        "segment": "value_proposition",
        "issue": "communication",
        "impact": 0.15,
        "priority": "high"
      }
    ],
    "trends": {
      "efficiency_trend": "improving",
      "conversion_trend": "stable",
      "bottleneck_trend": "reducing"
    }
  }
}
```

#### 3.1.2 归因分析接口
- **接口**: POST /api/v1/attribution/analyze
- **描述**: 使用Shapley算法进行归因分析
- **参数**:
```json
{
  "time_range": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "attribution_type": "shapley",
  "channels": ["social_media", "search_engine", "email", "direct"],
  "metrics": ["conversions", "revenue", "engagement"]
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "attribution_results": {
      "social_media": {
        "conversions": 0.32,
        "revenue": 0.28,
        "engagement": 0.45,
        "shapley_value": 0.35
      },
      "search_engine": {
        "conversions": 0.28,
        "revenue": 0.35,
        "engagement": 0.22,
        "shapley_value": 0.28
      },
      "email": {
        "conversions": 0.25,
        "revenue": 0.22,
        "engagement": 0.18,
        "shapley_value": 0.22
      },
      "direct": {
        "conversions": 0.15,
        "revenue": 0.15,
        "engagement": 0.15,
        "shapley_value": 0.15
      }
    },
    "total_attribution": 1.0,
    "confidence_score": 0.89,
    "analysis_metadata": {
      "sample_size": 10000,
      "analysis_time": "2025-01-19T10:00:00Z",
      "algorithm_version": "shapley_v2.1"
    }
  }
}
```

#### 3.1.3 优化建议接口
- **接口**: POST /api/v1/optimization/suggestions
- **描述**: 基于分析结果生成优化建议
- **参数**:
```json
{
  "analysis_results": {
    "chain_analysis": {...},
    "attribution_results": {...}
  },
  "optimization_goals": ["efficiency", "conversion", "revenue"],
  "constraints": {
    "budget_limit": 100000,
    "time_limit": "30_days"
  }
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggestions": [
      {
        "id": "opt_001",
        "title": "优化价值主张沟通",
        "description": "改进价值主张的沟通方式，提升客户理解度",
        "target_segment": "value_proposition",
        "priority": "high",
        "expected_impact": {
          "efficiency_improvement": 0.15,
          "conversion_improvement": 0.12,
          "revenue_improvement": 0.08
        },
        "implementation": {
          "effort": "medium",
          "cost": 15000,
          "timeline": "2_weeks",
          "resources": ["marketing_team", "design_team"]
        },
        "success_metrics": [
          "communication_efficiency",
          "customer_understanding_rate",
          "conversion_rate"
        ]
      }
    ],
    "total_suggestions": 5,
    "estimated_roi": 2.3,
    "implementation_priority": [
      "opt_001",
      "opt_003",
      "opt_002"
    ]
  }
}
```

### 3.2 数据模型

#### 3.2.1 价值链分析数据模型 (ClickHouse)
```sql
-- 价值链分析结果表
CREATE TABLE fact_value_chain_analysis (
    analysis_id String,
    time_period String,
    segment_name String,
    efficiency_score Decimal(5,4),
    conversion_rate Decimal(5,4),
    bottleneck_type String,
    bottleneck_impact Decimal(5,4),
    analysis_date DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (analysis_id, time_period, segment_name);

-- 归因分析结果表
CREATE TABLE fact_attribution_analysis (
    analysis_id String,
    channel_name String,
    metric_name String,
    attribution_value Decimal(5,4),
    shapley_value Decimal(5,4),
    confidence_score Decimal(5,4),
    analysis_date DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (analysis_id, channel_name, metric_name);

-- 优化建议表
CREATE TABLE fact_optimization_suggestions (
    suggestion_id String,
    analysis_id String,
    title String,
    description String,
    target_segment String,
    priority String,
    expected_impact Map(String, Decimal(5,4)),
    implementation Map(String, String),
    success_metrics Array(String),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (suggestion_id, analysis_id);
```

#### 3.2.2 前端数据接口 (React + TypeScript)
```typescript
// 价值链分析数据类型
interface ValueChainAnalysis {
  analysisId: string;
  timePeriod: string;
  segmentName: string;
  efficiencyScore: number;
  conversionRate: number;
  bottleneckType: string;
  bottleneckImpact: number;
  analysisDate: string;
}

// 归因分析数据类型
interface AttributionAnalysis {
  analysisId: string;
  channelName: string;
  metricName: string;
  attributionValue: number;
  shapleyValue: number;
  confidenceScore: number;
  analysisDate: string;
}

// 优化建议数据类型
interface OptimizationSuggestion {
  suggestionId: string;
  analysisId: string;
  title: string;
  description: string;
  targetSegment: string;
  priority: 'high' | 'medium' | 'low';
  expectedImpact: {
    efficiencyImprovement: number;
    conversionImprovement: number;
    revenueImprovement: number;
  };
  implementation: {
    effort: string;
    cost: number;
    timeline: string;
    resources: string[];
  };
  successMetrics: string[];
}
```

### 3.3 算法逻辑

#### 3.3.1 价值链效率计算算法
```python
def calculate_chain_efficiency(segment_data):
    """
    计算价值链各环节效率
    
    Args:
        segment_data: 环节数据，包含投入和产出信息
    
    Returns:
        efficiency_score: 效率分数 (0-1)
        conversion_rate: 转化率 (0-1)
        bottleneck_type: 瓶颈类型
        bottleneck_impact: 瓶颈影响程度 (0-1)
    """
    # 1. 计算基础效率指标
    input_volume = segment_data['input_volume']
    output_volume = segment_data['output_volume']
    processing_time = segment_data['processing_time']
    
    # 2. 计算效率分数
    efficiency_score = output_volume / (input_volume * processing_time)
    
    # 3. 计算转化率
    conversion_rate = output_volume / input_volume
    
    # 4. 识别瓶颈
    bottleneck_type = identify_bottleneck(segment_data)
    bottleneck_impact = calculate_bottleneck_impact(segment_data, bottleneck_type)
    
    return {
        'efficiency_score': efficiency_score,
        'conversion_rate': conversion_rate,
        'bottleneck_type': bottleneck_type,
        'bottleneck_impact': bottleneck_impact
    }
```

#### 3.3.2 Shapley归因算法
```python
def calculate_shapley_attribution(channels, outcomes):
    """
    使用Shapley算法计算各渠道的归因贡献
    
    Args:
        channels: 渠道列表
        outcomes: 结果数据
    
    Returns:
        shapley_values: 各渠道的Shapley值
    """
    n = len(channels)
    shapley_values = {}
    
    for channel in channels:
        shapley_value = 0
        
        # 计算所有可能的渠道组合
        for subset in get_all_subsets(channels):
            if channel in subset:
                # 计算包含该渠道的贡献
                with_channel = calculate_contribution(subset, outcomes)
                without_channel = calculate_contribution(subset - {channel}, outcomes)
                
                # 计算权重
                weight = 1 / (n * math.comb(n-1, len(subset)-1))
                
                # 累加Shapley值
                shapley_value += weight * (with_channel - without_channel)
        
        shapley_values[channel] = shapley_value
    
    return shapley_values
```

## 4. 验收标准

### 4.1 功能验收
- [ ] **价值链分析准确性**: 分析结果与实际情况的准确率 > 90%
- [ ] **归因分析公平性**: Shapley值总和 = 1.0，误差 < 0.01
- [ ] **优化建议可操作性**: 生成的建议中可操作的比例 > 80%
- [ ] **实时监控响应性**: 数据更新延迟 < 5秒
- [ ] **可视化展示完整性**: 所有关键指标都有对应的可视化展示

### 4.2 性能验收
- **响应时间**: API接口响应时间 < 2秒
- **并发用户**: 支持100个并发用户同时使用
- **数据量**: 支持处理100万条订单数据
- **计算精度**: 数值计算精度保持小数点后4位
- **内存使用**: 单次分析内存使用 < 1GB

### 4.3 质量验收
- **代码覆盖率**: 单元测试覆盖率 > 90%
- **测试通过率**: 所有测试用例通过率 = 100%
- **文档完整性**: API文档、用户手册完整性 = 100%
- **错误处理**: 异常情况处理覆盖率 = 100%
- **数据一致性**: 数据一致性检查通过率 = 100%

---

**这个需求规格说明书为模块1的开发和测试提供了完整的指导！** 🎉
