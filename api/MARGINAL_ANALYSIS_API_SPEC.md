# 边际分析API契约规范

## 概述

本文档定义了边际影响分析系统的11个核心API端点，包括清单管理、计算引擎、边际分析和动态反馈功能。

## API基础信息

- **Base URL**: `https://your-domain.com/api`
- **认证方式**: Bearer Token (Supabase JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2024-01-25T10:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  },
  "timestamp": "2024-01-25T10:30:00Z"
}
```

## 1. 清单管理API (3个端点)

### 1.1 资产清单管理

#### GET /api/assets
获取资产清单列表

**请求参数:**
```json
{
  "page": 1,
  "limit": 20,
  "asset_type": "tangible",
  "status": "active",
  "sort_by": "asset_name",
  "sort_order": "asc"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "assets": [
      {
        "id": "uuid",
        "asset_code": "ASSET-001",
        "asset_name": "生产设备A",
        "asset_type": "tangible",
        "acquisition_date": "2024-01-01",
        "acquisition_cost": 1000000.00,
        "current_book_value": 800000.00,
        "calculated_npv": 1200000.00,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

#### POST /api/assets
创建新资产

**请求体:**
```json
{
  "asset_code": "ASSET-002",
  "asset_name": "生产设备B",
  "asset_type": "tangible",
  "acquisition_date": "2024-01-15",
  "acquisition_cost": 1500000.00,
  "useful_life_years": 10,
  "residual_value": 150000.00,
  "depreciation_method": "straight_line",
  "discount_rate": 0.10,
  "annual_cash_flow": [180000, 190000, 200000, 210000, 220000]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "new-asset-uuid",
    "asset_code": "ASSET-002",
    "calculated_npv": 1350000.00,
    "created_at": "2024-01-25T10:30:00Z"
  }
}
```

#### PUT /api/assets/{id}
更新资产信息

#### DELETE /api/assets/{id}
删除资产

### 1.2 能力清单管理

#### GET /api/capabilities
获取能力清单列表

**请求参数:**
```json
{
  "page": 1,
  "limit": 20,
  "capability_type": "technical",
  "capability_level": "advanced",
  "sort_by": "capability_name",
  "sort_order": "asc"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "capabilities": [
      {
        "id": "uuid",
        "capability_code": "CAP-001",
        "capability_name": "数据分析能力",
        "capability_type": "technical",
        "capability_level": "advanced",
        "contribution_percentage": 0.25,
        "annual_benefit": 500000.00,
        "calculated_value": 125000.00,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

#### POST /api/capabilities
创建新能力

**请求体:**
```json
{
  "capability_code": "CAP-002",
  "capability_name": "项目管理能力",
  "capability_type": "management",
  "capability_level": "expert",
  "description": "高级项目管理能力",
  "contribution_percentage": 0.30,
  "annual_benefit": 600000.00,
  "benefit_measurement_period": 12
}
```

#### PUT /api/capabilities/{id}
更新能力信息

#### DELETE /api/capabilities/{id}
删除能力

### 1.3 价值评估项管理

#### GET /api/value-items
获取价值评估项列表

**请求参数:**
```json
{
  "product_id": "product-uuid",
  "value_category": "intrinsic",
  "page": 1,
  "limit": 20
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "value_items": [
      {
        "id": "uuid",
        "product_id": "product-uuid",
        "value_category": "intrinsic",
        "value_item_name": "产品质量",
        "weight": 0.30,
        "current_score": 8.5,
        "target_score": 9.0,
        "max_score": 10.0,
        "last_evaluation_date": "2024-01-20"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 30,
      "total_pages": 2
    }
  }
}
```

#### POST /api/value-items
创建价值评估项

**请求体:**
```json
{
  "product_id": "product-uuid",
  "value_category": "cognitive",
  "value_item_name": "品牌认知度",
  "weight": 0.25,
  "max_score": 10.0,
  "evaluation_criteria": "基于市场调研的认知度评分",
  "evaluation_method": "survey"
}
```

#### PUT /api/value-items/{id}
更新价值评估项

#### DELETE /api/value-items/{id}
删除价值评估项

## 2. 计算引擎API (4个端点)

### 2.1 资产NPV计算

#### POST /api/calculate/asset-npv
计算资产净现值

**请求体:**
```json
{
  "asset_id": "asset-uuid",
  "discount_rate": 0.10,
  "cash_flow_years": 5,
  "annual_cash_flow": [120000, 130000, 140000, 150000, 160000],
  "recalculate": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "asset_id": "asset-uuid",
    "npv": 1350000.00,
    "discount_rate": 0.10,
    "cash_flow_years": 5,
    "annual_cash_flow": [120000, 130000, 140000, 150000, 160000],
    "calculation_details": {
      "year_1_pv": 109090.91,
      "year_2_pv": 107438.02,
      "year_3_pv": 105155.29,
      "year_4_pv": 102450.00,
      "year_5_pv": 99347.11,
      "total_pv": 1350000.00
    },
    "calculation_date": "2024-01-25T10:30:00Z"
  }
}
```

### 2.2 能力价值计算

#### POST /api/calculate/capability-value
计算能力价值

**请求体:**
```json
{
  "capability_id": "capability-uuid",
  "calculation_method": "stable_output",
  "stable_output_metrics": {
    "revenue_impact": 500000.00,
    "cost_savings": 100000.00,
    "efficiency_gains": 0.15
  },
  "contribution_percentage": 0.25
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "capability_id": "capability-uuid",
    "calculated_value": 150000.00,
    "calculation_method": "stable_output",
    "calculation_details": {
      "annual_benefit": 600000.00,
      "contribution_percentage": 0.25,
      "stable_output_value": 150000.00
    },
    "calculation_date": "2024-01-25T10:30:00Z"
  }
}
```

### 2.3 产品价值评估

#### POST /api/calculate/product-value
计算产品价值评估

**请求体:**
```json
{
  "product_id": "product-uuid",
  "evaluation_items": [
    {
      "value_item_id": "item-uuid-1",
      "score": 8.5
    },
    {
      "value_item_id": "item-uuid-2",
      "score": 7.8
    }
  ],
  "evaluation_date": "2024-01-25"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "product_id": "product-uuid",
    "total_score": 8.15,
    "category_scores": {
      "intrinsic": 8.2,
      "cognitive": 7.8,
      "experiential": 8.5
    },
    "evaluation_details": [
      {
        "value_item_id": "item-uuid-1",
        "value_category": "intrinsic",
        "score": 8.5,
        "weight": 0.30,
        "weighted_score": 2.55
      }
    ],
    "evaluation_date": "2024-01-25T10:30:00Z"
  }
}
```

### 2.4 全链路增量计算

#### POST /api/calculate/full-chain-delta
计算全链路增量指标

**请求体:**
```json
{
  "calculation_period": "2024-01",
  "metrics": [
    "revenue_delta",
    "cost_delta",
    "efficiency_delta",
    "quality_delta"
  ],
  "include_predictions": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "calculation_period": "2024-01",
    "metrics": {
      "revenue_delta": {
        "current_value": 1200000.00,
        "previous_value": 1100000.00,
        "delta_value": 100000.00,
        "delta_percentage": 9.09,
        "trend_direction": "up"
      },
      "cost_delta": {
        "current_value": 800000.00,
        "previous_value": 850000.00,
        "delta_value": -50000.00,
        "delta_percentage": -5.88,
        "trend_direction": "down"
      }
    },
    "predictions": {
      "next_month_revenue": 1250000.00,
      "next_month_cost": 780000.00,
      "confidence_level": 0.85
    },
    "calculation_date": "2024-01-25T10:30:00Z"
  }
}
```

## 3. 边际分析API (2个端点)

### 3.1 Shapley简化版分析

#### POST /api/analysis/shapley-simplified
执行Shapley简化版边际贡献分析

**请求体:**
```json
{
  "analysis_id": "analysis-uuid",
  "target_metric": "revenue",
  "factors": [
    {
      "factor_id": "asset-uuid-1",
      "factor_type": "asset",
      "factor_name": "生产设备A"
    },
    {
      "factor_id": "capability-uuid-1",
      "factor_type": "capability",
      "factor_name": "数据分析能力"
    }
  ],
  "time_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "calculation_method": "linear_regression"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis-uuid",
    "target_metric": "revenue",
    "total_contribution": 1000000.00,
    "factor_contributions": [
      {
        "factor_id": "asset-uuid-1",
        "factor_name": "生产设备A",
        "marginal_contribution": 600000.00,
        "contribution_percentage": 60.0,
        "shapley_value": 0.6,
        "significance": true,
        "p_value": 0.02
      },
      {
        "factor_id": "capability-uuid-1",
        "factor_name": "数据分析能力",
        "marginal_contribution": 400000.00,
        "contribution_percentage": 40.0,
        "shapley_value": 0.4,
        "significance": true,
        "p_value": 0.01
      }
    ],
    "model_metrics": {
      "r_squared": 0.85,
      "mae": 50000.00,
      "rmse": 75000.00
    },
    "calculation_date": "2024-01-25T10:30:00Z"
  }
}
```

### 3.2 时间序列简化版分析

#### POST /api/analysis/timeseries-simplified
执行时间序列简化版趋势分析

**请求体:**
```json
{
  "metric_code": "revenue",
  "time_period": {
    "start_date": "2023-01-01",
    "end_date": "2024-01-31"
  },
  "prediction_months": 3,
  "seasonality": true,
  "trend_analysis": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "metric_code": "revenue",
    "historical_data": [
      {
        "date": "2023-01-01",
        "value": 1000000.00
      },
      {
        "date": "2023-02-01",
        "value": 1050000.00
      }
    ],
    "trend_analysis": {
      "trend_direction": "up",
      "trend_strength": 0.75,
      "volatility_index": 0.15,
      "seasonality_detected": true
    },
    "predictions": [
      {
        "date": "2024-02-01",
        "predicted_value": 1300000.00,
        "confidence_interval": {
          "lower": 1200000.00,
          "upper": 1400000.00
        }
      }
    ],
    "model_metrics": {
      "mape": 8.5,
      "rmse": 75000.00,
      "r_squared": 0.82
    },
    "calculation_date": "2024-01-25T10:30:00Z"
  }
}
```

## 4. 动态反馈API (2个端点)

### 4.1 触发动态反馈

#### POST /api/feedback/trigger
触发动态反馈机制

**请求体:**
```json
{
  "trigger_type": "profit_reinvestment",
  "trigger_conditions": {
    "profit_threshold": 1000000.00,
    "growth_rate_threshold": 0.15
  },
  "feedback_actions": [
    {
      "action_type": "resource_allocation",
      "target_assets": ["asset-uuid-1", "asset-uuid-2"],
      "allocation_amount": 200000.00
    }
  ],
  "execution_delay_days": 0
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "feedback_id": "feedback-uuid",
    "trigger_type": "profit_reinvestment",
    "trigger_conditions_met": true,
    "scheduled_actions": [
      {
        "action_id": "action-uuid-1",
        "action_type": "resource_allocation",
        "scheduled_date": "2024-01-25T10:30:00Z",
        "status": "scheduled"
      }
    ],
    "execution_timeline": {
      "immediate": [],
      "delayed": ["action-uuid-1"]
    },
    "feedback_created_at": "2024-01-25T10:30:00Z"
  }
}
```

### 4.2 获取反馈状态

#### GET /api/feedback/status
获取动态反馈状态

**请求参数:**
```json
{
  "feedback_id": "feedback-uuid",
  "include_actions": true,
  "status_filter": "active"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "feedback_id": "feedback-uuid",
    "trigger_type": "profit_reinvestment",
    "status": "active",
    "trigger_conditions": {
      "profit_threshold": 1000000.00,
      "current_profit": 1200000.00,
      "conditions_met": true
    },
    "actions": [
      {
        "action_id": "action-uuid-1",
        "action_type": "resource_allocation",
        "status": "completed",
        "executed_at": "2024-01-25T10:30:00Z",
        "result": {
          "allocated_amount": 200000.00,
          "target_assets": ["asset-uuid-1", "asset-uuid-2"]
        }
      }
    ],
    "next_evaluation_date": "2024-02-25T10:30:00Z",
    "last_updated": "2024-01-25T10:30:00Z"
  }
}
```

## 错误代码定义

| 错误代码 | HTTP状态码 | 描述 |
|---------|------------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未授权访问 |
| `FORBIDDEN` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 422 | 数据验证失败 |
| `CALCULATION_ERROR` | 500 | 计算过程错误 |
| `MODEL_ERROR` | 500 | 模型执行错误 |
| `DATABASE_ERROR` | 500 | 数据库操作错误 |

## 限流和配额

- **请求频率**: 1000 requests/hour per user
- **计算配额**: 100 calculations/day per user
- **数据大小**: 最大10MB per request
- **超时设置**: 30 seconds per request

## 版本控制

- **当前版本**: v1.0
- **版本策略**: 向后兼容
- **弃用通知**: 提前30天通知

## 测试端点

### 健康检查
```
GET /api/health
```

### 版本信息
```
GET /api/version
```

### API文档
```
GET /api/docs
```


