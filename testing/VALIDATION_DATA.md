# 边际分析验证数据文档

## 概述

本文档提供了边际分析系统的验证数据，包括测试数据集、基准数据、预期结果和验证标准。

## 验证数据分类

### 1. 基准数据集
### 2. 边界条件数据
### 3. 异常情况数据
### 4. 性能测试数据
### 5. 集成测试数据

## 1. 基准数据集

### 1.1 资产基准数据

#### 标准资产数据集
```json
{
  "assets": [
    {
      "id": "asset_001",
      "asset_code": "ASSET-001",
      "asset_name": "生产设备A",
      "asset_type": "tangible",
      "acquisition_date": "2024-01-01",
      "acquisition_cost": 1000000.00,
      "useful_life_years": 10,
      "residual_value": 100000.00,
      "depreciation_method": "straight_line",
      "discount_rate": 0.10,
      "cash_flow_years": 5,
      "annual_cash_flow": [120000, 130000, 140000, 150000, 160000],
      "expected_npv": 1350000.00,
      "expected_roi": 0.35
    },
    {
      "id": "asset_002",
      "asset_code": "ASSET-002",
      "asset_name": "办公设备",
      "asset_type": "intangible",
      "acquisition_date": "2024-01-15",
      "acquisition_cost": 500000.00,
      "useful_life_years": 5,
      "residual_value": 50000.00,
      "depreciation_method": "straight_line",
      "discount_rate": 0.10,
      "cash_flow_years": 5,
      "annual_cash_flow": [100000, 110000, 120000, 130000, 140000],
      "expected_npv": 650000.00,
      "expected_roi": 0.30
    }
  ]
}
```

#### 预期计算结果
```json
{
  "asset_001": {
    "npv": 1350000.00,
    "roi": 0.35,
    "payback_period": 7.5,
    "irr": 0.12,
    "calculation_details": {
      "year_1_pv": 109090.91,
      "year_2_pv": 107438.02,
      "year_3_pv": 105155.29,
      "year_4_pv": 102450.00,
      "year_5_pv": 99347.11,
      "total_pv": 1350000.00
    }
  },
  "asset_002": {
    "npv": 650000.00,
    "roi": 0.30,
    "payback_period": 4.2,
    "irr": 0.15,
    "calculation_details": {
      "year_1_pv": 90909.09,
      "year_2_pv": 90909.09,
      "year_3_pv": 90090.09,
      "year_4_pv": 88888.89,
      "year_5_pv": 86956.52,
      "total_pv": 650000.00
    }
  }
}
```

### 1.2 能力基准数据

#### 标准能力数据集
```json
{
  "capabilities": [
    {
      "id": "cap_001",
      "capability_code": "CAP-001",
      "capability_name": "数据分析能力",
      "capability_type": "technical",
      "capability_level": "advanced",
      "description": "高级数据分析能力",
      "contribution_percentage": 0.25,
      "annual_benefit": 500000.00,
      "benefit_measurement_period": 12,
      "expected_value": 125000.00
    },
    {
      "id": "cap_002",
      "capability_code": "CAP-002",
      "capability_name": "项目管理能力",
      "capability_type": "management",
      "capability_level": "expert",
      "description": "专家级项目管理能力",
      "contribution_percentage": 0.30,
      "annual_benefit": 600000.00,
      "benefit_measurement_period": 12,
      "expected_value": 180000.00
    }
  ]
}
```

### 1.3 产品价值基准数据

#### 标准产品价值数据集
```json
{
  "products": [
    {
      "id": "prod_001",
      "product_name": "产品A",
      "value_items": [
        {
          "value_category": "intrinsic",
          "value_item_name": "产品质量",
          "weight": 0.30,
          "current_score": 8.5,
          "target_score": 9.0,
          "max_score": 10.0
        },
        {
          "value_category": "cognitive",
          "value_item_name": "品牌认知度",
          "weight": 0.25,
          "current_score": 7.8,
          "target_score": 8.5,
          "max_score": 10.0
        },
        {
          "value_category": "experiential",
          "value_item_name": "用户体验",
          "weight": 0.45,
          "current_score": 8.5,
          "target_score": 9.0,
          "max_score": 10.0
        }
      ],
      "expected_total_score": 8.15,
      "expected_category_scores": {
        "intrinsic": 8.2,
        "cognitive": 7.8,
        "experiential": 8.5
      }
    }
  ]
}
```

## 2. 边界条件数据

### 2.1 极值数据

#### 最大/最小值数据
```json
{
  "boundary_conditions": {
    "max_values": {
      "acquisition_cost": 999999999.99,
      "useful_life_years": 50,
      "discount_rate": 0.99,
      "contribution_percentage": 1.0,
      "annual_benefit": 999999999.99
    },
    "min_values": {
      "acquisition_cost": 0.01,
      "useful_life_years": 1,
      "discount_rate": 0.001,
      "contribution_percentage": 0.001,
      "annual_benefit": 0.01
    },
    "zero_values": {
      "acquisition_cost": 0,
      "annual_benefit": 0,
      "contribution_percentage": 0
    }
  }
}
```

### 2.2 边界测试用例
```json
{
  "boundary_test_cases": [
    {
      "name": "最大购置成本",
      "data": {
        "acquisition_cost": 999999999.99,
        "expected_behavior": "正常处理"
      }
    },
    {
      "name": "最小购置成本",
      "data": {
        "acquisition_cost": 0.01,
        "expected_behavior": "正常处理"
      }
    },
    {
      "name": "零购置成本",
      "data": {
        "acquisition_cost": 0,
        "expected_behavior": "抛出验证错误"
      }
    },
    {
      "name": "负购置成本",
      "data": {
        "acquisition_cost": -1000,
        "expected_behavior": "抛出验证错误"
      }
    }
  ]
}
```

## 3. 异常情况数据

### 3.1 数据格式异常

#### 无效数据格式
```json
{
  "invalid_formats": {
    "invalid_dates": [
      "2024-13-01",
      "2024-02-30",
      "invalid-date",
      "2024/01/01",
      "01-01-2024"
    ],
    "invalid_numbers": [
      "not-a-number",
      "1,000,000",
      "1.000.000",
      "1e6",
      "∞"
    ],
    "invalid_emails": [
      "invalid-email",
      "@example.com",
      "user@",
      "user@domain",
      "user@domain."
    ]
  }
}
```

### 3.2 业务逻辑异常

#### 业务规则违反数据
```json
{
  "business_rule_violations": {
    "duplicate_asset_codes": [
      {
        "asset_code": "ASSET-001",
        "asset_name": "设备A"
      },
      {
        "asset_code": "ASSET-001",
        "asset_name": "设备B"
      }
    ],
    "invalid_asset_types": [
      {
        "asset_type": "invalid_type",
        "expected_behavior": "抛出验证错误"
      }
    ],
    "invalid_capability_levels": [
      {
        "capability_level": "invalid_level",
        "expected_behavior": "抛出验证错误"
      }
    ]
  }
}
```

## 4. 性能测试数据

### 4.1 大数据集

#### 大规模资产数据
```json
{
  "large_dataset": {
    "asset_count": 10000,
    "capability_count": 5000,
    "value_item_count": 15000,
    "metric_count": 100000,
    "expected_processing_time": "< 30 seconds",
    "expected_memory_usage": "< 500MB"
  }
}
```

#### 性能基准数据
```json
{
  "performance_benchmarks": {
    "npv_calculation": {
      "small_dataset": {
        "record_count": 100,
        "expected_time": "< 1 second",
        "expected_memory": "< 10MB"
      },
      "medium_dataset": {
        "record_count": 1000,
        "expected_time": "< 5 seconds",
        "expected_memory": "< 50MB"
      },
      "large_dataset": {
        "record_count": 10000,
        "expected_time": "< 30 seconds",
        "expected_memory": "< 200MB"
      }
    },
    "shapley_calculation": {
      "factors_5": {
        "factor_count": 5,
        "expected_time": "< 2 seconds"
      },
      "factors_10": {
        "factor_count": 10,
        "expected_time": "< 10 seconds"
      },
      "factors_20": {
        "factor_count": 20,
        "expected_time": "< 60 seconds"
      }
    }
  }
}
```

### 4.2 并发测试数据

#### 并发用户数据
```json
{
  "concurrent_users": {
    "light_load": {
      "user_count": 10,
      "requests_per_second": 5,
      "expected_response_time": "< 1 second"
    },
    "medium_load": {
      "user_count": 50,
      "requests_per_second": 25,
      "expected_response_time": "< 2 seconds"
    },
    "heavy_load": {
      "user_count": 100,
      "requests_per_second": 50,
      "expected_response_time": "< 5 seconds"
    }
  }
}
```

## 5. 集成测试数据

### 5.1 端到端测试数据

#### 完整业务流程数据
```json
{
  "e2e_test_data": {
    "user_workflow": {
      "step_1": {
        "action": "login",
        "data": {
          "email": "test@example.com",
          "password": "password123"
        },
        "expected_result": "登录成功"
      },
      "step_2": {
        "action": "upload_asset_data",
        "data": {
          "file": "asset_data.xlsx",
          "record_count": 100
        },
        "expected_result": "数据导入成功"
      },
      "step_3": {
        "action": "run_marginal_analysis",
        "data": {
          "target_metric": "revenue",
          "factors": ["asset_001", "cap_001"],
          "time_period": "2024-01-01 to 2024-12-31"
        },
        "expected_result": "分析完成"
      },
      "step_4": {
        "action": "manager_evaluation",
        "data": {
          "evaluation_type": "confirm",
          "evaluation_content": "分析结果准确"
        },
        "expected_result": "评价提交成功"
      }
    }
  }
}
```

### 5.2 数据一致性测试

#### 跨表关联数据
```json
{
  "consistency_test_data": {
    "asset_capability_relations": [
      {
        "asset_id": "asset_001",
        "capability_id": "cap_001",
        "relation_type": "contribution",
        "contribution_value": 0.6
      },
      {
        "asset_id": "asset_002",
        "capability_id": "cap_002",
        "relation_type": "dependency",
        "dependency_value": 0.4
      }
    ],
    "expected_consistency": {
      "total_relations": 2,
      "valid_relations": 2,
      "invalid_relations": 0
    }
  }
}
```

## 6. 验证标准

### 6.1 数值精度标准

#### 计算精度要求
```json
{
  "precision_standards": {
    "npv_calculation": {
      "decimal_places": 2,
      "tolerance": 0.01,
      "rounding_method": "round_half_up"
    },
    "shapley_values": {
      "decimal_places": 4,
      "tolerance": 0.0001,
      "rounding_method": "round_half_up"
    },
    "percentage_calculations": {
      "decimal_places": 2,
      "tolerance": 0.01,
      "rounding_method": "round_half_up"
    }
  }
}
```

### 6.2 性能标准

#### 响应时间要求
```json
{
  "performance_standards": {
    "api_response_times": {
      "simple_queries": "< 500ms",
      "complex_calculations": "< 5 seconds",
      "large_dataset_processing": "< 30 seconds"
    },
    "ui_response_times": {
      "page_load": "< 3 seconds",
      "chart_rendering": "< 2 seconds",
      "data_export": "< 10 seconds"
    },
    "database_operations": {
      "simple_insert": "< 100ms",
      "complex_query": "< 1 second",
      "bulk_operations": "< 10 seconds"
    }
  }
}
```

## 7. 数据生成工具

### 7.1 测试数据生成器

#### 数据生成脚本
```typescript
class ValidationDataGenerator {
  generateAssetData(count: number): AssetData[] {
    return Array.from({ length: count }, (_, i) => ({
      id: `asset_${i.toString().padStart(3, '0')}`,
      asset_code: `ASSET-${i.toString().padStart(3, '0')}`,
      asset_name: `测试设备${i}`,
      asset_type: this.randomChoice(['tangible', 'intangible', 'financial']),
      acquisition_date: this.randomDate('2020-01-01', '2024-12-31'),
      acquisition_cost: this.randomNumber(10000, 10000000),
      useful_life_years: this.randomNumber(1, 20),
      residual_value: this.randomNumber(0, 100000),
      depreciation_method: this.randomChoice(['straight_line', 'declining_balance']),
      discount_rate: this.randomNumber(0.05, 0.20),
      cash_flow_years: this.randomNumber(3, 10),
      annual_cash_flow: this.generateCashFlow(this.randomNumber(3, 10))
    }));
  }

  generateCapabilityData(count: number): CapabilityData[] {
    return Array.from({ length: count }, (_, i) => ({
      id: `cap_${i.toString().padStart(3, '0')}`,
      capability_code: `CAP-${i.toString().padStart(3, '0')}`,
      capability_name: `测试能力${i}`,
      capability_type: this.randomChoice(['technical', 'business', 'management', 'operational']),
      capability_level: this.randomChoice(['beginner', 'intermediate', 'advanced', 'expert']),
      contribution_percentage: this.randomNumber(0.1, 1.0),
      annual_benefit: this.randomNumber(100000, 1000000)
    }));
  }

  private randomChoice<T>(choices: T[]): T {
    return choices[Math.floor(Math.random() * choices.length)];
  }

  private randomNumber(min: number, max: number): number {
    return Math.random() * (max - min) + min;
  }

  private randomDate(start: string, end: string): string {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const randomTime = startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime());
    return new Date(randomTime).toISOString().split('T')[0];
  }

  private generateCashFlow(years: number): number[] {
    const baseAmount = this.randomNumber(100000, 500000);
    return Array.from({ length: years }, (_, i) => 
      baseAmount * (1 + this.randomNumber(-0.1, 0.2) * i)
    );
  }
}
```

### 7.2 数据验证工具

#### 验证函数
```typescript
class DataValidator {
  validateAssetData(data: AssetData): ValidationResult {
    const errors: string[] = [];
    
    if (!data.asset_code || data.asset_code.trim() === '') {
      errors.push('资产编码不能为空');
    }
    
    if (!data.asset_name || data.asset_name.trim() === '') {
      errors.push('资产名称不能为空');
    }
    
    if (!['tangible', 'intangible', 'financial'].includes(data.asset_type)) {
      errors.push('无效的资产类型');
    }
    
    if (data.acquisition_cost <= 0) {
      errors.push('购置成本必须大于0');
    }
    
    if (data.useful_life_years <= 0) {
      errors.push('使用年限必须大于0');
    }
    
    if (data.discount_rate < 0 || data.discount_rate > 1) {
      errors.push('折现率必须在0-1之间');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  validateCalculationResult(result: CalculationResult, expected: ExpectedResult): ValidationResult {
    const errors: string[] = [];
    
    if (Math.abs(result.npv - expected.npv) > expected.tolerance) {
      errors.push(`NPV计算误差过大: 实际${result.npv}, 预期${expected.npv}`);
    }
    
    if (Math.abs(result.roi - expected.roi) > expected.tolerance) {
      errors.push(`ROI计算误差过大: 实际${result.roi}, 预期${expected.roi}`);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
}
```

## 8. 测试数据管理

### 8.1 数据版本控制

#### 数据版本管理
```json
{
  "data_versions": {
    "v1.0": {
      "description": "初始验证数据集",
      "created_date": "2024-01-01",
      "asset_count": 100,
      "capability_count": 50,
      "test_cases": 200
    },
    "v1.1": {
      "description": "增加边界条件测试数据",
      "created_date": "2024-01-15",
      "asset_count": 150,
      "capability_count": 75,
      "test_cases": 300
    },
    "v2.0": {
      "description": "增加性能测试数据",
      "created_date": "2024-02-01",
      "asset_count": 1000,
      "capability_count": 500,
      "test_cases": 500
    }
  }
}
```

### 8.2 数据清理策略

#### 数据清理规则
```typescript
class DataCleanupManager {
  async cleanupTestData(): Promise<void> {
    // 清理测试数据库
    await this.truncateTables([
      'core_asset_master',
      'core_capability_master',
      'product_value_item_master',
      'monthly_delta_metrics'
    ]);
    
    // 清理测试文件
    await this.removeTestFiles();
    
    // 重置序列号
    await this.resetSequences();
  }

  async resetTestEnvironment(): Promise<void> {
    await this.cleanupTestData();
    await this.seedBaseData();
    await this.setupTestUsers();
  }
}
```

## 9. 验证报告模板

### 9.1 验证结果报告

#### 报告结构
```json
{
  "validation_report": {
    "summary": {
      "total_tests": 1000,
      "passed": 950,
      "failed": 50,
      "success_rate": 0.95
    },
    "categories": {
      "unit_tests": {
        "total": 600,
        "passed": 580,
        "failed": 20,
        "success_rate": 0.967
      },
      "integration_tests": {
        "total": 300,
        "passed": 280,
        "failed": 20,
        "success_rate": 0.933
      },
      "e2e_tests": {
        "total": 100,
        "passed": 90,
        "failed": 10,
        "success_rate": 0.90
      }
    },
    "performance_metrics": {
      "average_response_time": "1.2s",
      "memory_usage": "250MB",
      "cpu_usage": "45%"
    },
    "recommendations": [
      "优化慢查询性能",
      "增加错误处理覆盖",
      "改进用户体验"
    ]
  }
}
```

## 10. 持续验证

### 10.1 自动化验证

#### 验证流水线
```yaml
# .github/workflows/validation.yml
name: Data Validation

on: [push, pull_request]

jobs:
  validate-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run validate:data
      - run: npm run validate:calculations
      - run: npm run validate:performance
```

### 10.2 数据质量监控

#### 质量指标
```typescript
interface DataQualityMetrics {
  completeness: number;      // 数据完整性
  accuracy: number;          // 数据准确性
  consistency: number;       // 数据一致性
  validity: number;          // 数据有效性
  timeliness: number;        // 数据及时性
  overall: number;           // 总体质量
}

class DataQualityMonitor {
  async monitorDataQuality(): Promise<DataQualityMetrics> {
    return {
      completeness: await this.calculateCompleteness(),
      accuracy: await this.calculateAccuracy(),
      consistency: await this.calculateConsistency(),
      validity: await this.calculateValidity(),
      timeliness: await this.calculateTimeliness(),
      overall: await this.calculateOverallQuality()
    };
  }
}
```
