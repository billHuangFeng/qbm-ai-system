# 边际影响分析系统API契约规范

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2024-01-01
- **负责人**: Cursor AI
- **状态**: ⏳ 待提交 → ✅ 已完成

## 1. API概述

### 1.1 基础信息
- **Base URL**: `https://api.qbm-system.com/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API版本**: v1

### 1.2 通用规范
- 所有时间格式使用ISO 8601标准
- 所有金额使用DECIMAL类型，保留2位小数
- 所有API响应包含统一的错误处理
- 支持分页查询，默认每页20条记录
- 支持字段过滤和排序

## 2. 认证与授权

### 2.1 认证流程
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123",
  "tenant_id": "tenant-uuid"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh-token-string",
  "tenant_id": "tenant-uuid"
}
```

### 2.2 请求头
```http
Authorization: Bearer <access_token>
Content-Type: application/json
X-Tenant-ID: <tenant-uuid>
```

## 3. 核心资产API

### 3.1 资产管理

#### 3.1.1 获取资产列表
```http
GET /assets
Query Parameters:
- page: int (default: 1)
- size: int (default: 20, max: 100)
- asset_type: string (optional)
- status: string (optional)
- sort_by: string (default: created_at)
- sort_order: string (default: desc)

Response:
{
  "data": [
    {
      "id": "asset-uuid",
      "asset_name": "研发设备A",
      "asset_type": "研发资产",
      "asset_category": "设备",
      "current_value": 1000000.00,
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### 3.1.2 创建资产
```http
POST /assets
Content-Type: application/json

{
  "asset_name": "新研发设备",
  "asset_type": "研发资产",
  "asset_category": "设备",
  "asset_description": "高性能计算设备",
  "initial_value": 500000.00,
  "depreciation_rate": 0.1,
  "useful_life_years": 5,
  "acquisition_date": "2024-01-01",
  "metadata": {
    "brand": "Dell",
    "model": "PowerEdge R750"
  }
}

Response:
{
  "id": "asset-uuid",
  "asset_name": "新研发设备",
  "asset_type": "研发资产",
  "asset_category": "设备",
  "current_value": 500000.00,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 3.1.3 更新资产
```http
PUT /assets/{asset_id}
Content-Type: application/json

{
  "asset_name": "更新后的设备名称",
  "current_value": 450000.00,
  "status": "active"
}

Response:
{
  "id": "asset-uuid",
  "asset_name": "更新后的设备名称",
  "current_value": 450000.00,
  "status": "active",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 3.1.4 删除资产
```http
DELETE /assets/{asset_id}

Response:
{
  "message": "资产删除成功",
  "deleted_at": "2024-01-01T00:00:00Z"
}
```

### 3.2 资产现金流管理

#### 3.2.1 获取资产现金流
```http
GET /assets/{asset_id}/cash-flows
Query Parameters:
- start_date: string (ISO 8601)
- end_date: string (ISO 8601)
- cash_flow_type: string (optional)

Response:
{
  "data": [
    {
      "id": "cash-flow-uuid",
      "period_date": "2024-01-01",
      "cash_flow_amount": 50000.00,
      "cash_flow_type": "revenue",
      "description": "设备产生的收入"
    }
  ]
}
```

#### 3.2.2 创建现金流记录
```http
POST /assets/{asset_id}/cash-flows
Content-Type: application/json

{
  "period_date": "2024-01-01",
  "cash_flow_amount": 50000.00,
  "cash_flow_type": "revenue",
  "description": "设备产生的收入"
}

Response:
{
  "id": "cash-flow-uuid",
  "period_date": "2024-01-01",
  "cash_flow_amount": 50000.00,
  "cash_flow_type": "revenue",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 4. 核心能力API

### 4.1 能力管理

#### 4.1.1 获取能力列表
```http
GET /capabilities
Query Parameters:
- page: int (default: 1)
- size: int (default: 20)
- capability_type: string (optional)
- status: string (optional)

Response:
{
  "data": [
    {
      "id": "capability-uuid",
      "capability_name": "产品设计能力",
      "capability_type": "设计能力",
      "capability_level": "advanced",
      "current_performance": 0.85,
      "target_performance": 0.90,
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 50,
    "pages": 3
  }
}
```

#### 4.1.2 创建能力
```http
POST /capabilities
Content-Type: application/json

{
  "capability_name": "新设计能力",
  "capability_type": "设计能力",
  "capability_level": "intermediate",
  "description": "产品外观设计能力",
  "measurement_metrics": {
    "design_speed": "days_per_project",
    "quality_score": "customer_rating"
  },
  "target_outcomes": {
    "design_speed_target": 7,
    "quality_score_target": 4.5
  },
  "target_performance": 0.80
}

Response:
{
  "id": "capability-uuid",
  "capability_name": "新设计能力",
  "capability_type": "设计能力",
  "capability_level": "intermediate",
  "current_performance": 0.00,
  "target_performance": 0.80,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 4.1.3 更新能力绩效
```http
PUT /capabilities/{capability_id}/performance
Content-Type: application/json

{
  "performance_date": "2024-01-01",
  "performance_score": 0.85,
  "performance_metrics": {
    "design_speed": 6.5,
    "quality_score": 4.3
  },
  "evaluation_method": "peer_review",
  "evaluator": "设计主管"
}

Response:
{
  "id": "performance-uuid",
  "performance_score": 0.85,
  "performance_date": "2024-01-01",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 5. 产品价值评估API

### 5.1 产品特性管理

#### 5.1.1 获取产品特性列表
```http
GET /product-features
Query Parameters:
- page: int (default: 1)
- size: int (default: 20)
- feature_category: string (optional)
- development_status: string (optional)

Response:
{
  "data": [
    {
      "id": "feature-uuid",
      "feature_name": "智能推荐功能",
      "feature_category": "功能特性",
      "feature_priority": "high",
      "development_status": "completed",
      "target_customers": ["企业用户", "个人用户"]
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 30,
    "pages": 2
  }
}
```

#### 5.1.2 创建产品特性
```http
POST /product-features
Content-Type: application/json

{
  "feature_name": "新功能特性",
  "feature_category": "功能特性",
  "feature_description": "产品的新功能描述",
  "feature_priority": "high",
  "development_status": "planned",
  "target_customers": ["企业用户"],
  "competitive_advantage": "独特的竞争优势"
}

Response:
{
  "id": "feature-uuid",
  "feature_name": "新功能特性",
  "feature_category": "功能特性",
  "feature_priority": "high",
  "development_status": "planned",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5.2 价值评估管理

#### 5.2.1 创建价值评估
```http
POST /value-assessments
Content-Type: application/json

{
  "assessment_type": "intrinsic_value",
  "feature_id": "feature-uuid",
  "assessment_date": "2024-01-01",
  "customer_segment": "企业用户",
  "assessment_method": "survey",
  "intrinsic_value_score": 0.85,
  "willingness_to_pay": 1000.00,
  "market_price": 800.00,
  "premium_price": 200.00,
  "assessment_data": {
    "survey_responses": 150,
    "response_rate": 0.75,
    "confidence_level": 0.95
  }
}

Response:
{
  "id": "assessment-uuid",
  "assessment_type": "intrinsic_value",
  "intrinsic_value_score": 0.85,
  "willingness_to_pay": 1000.00,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 5.2.2 获取价值评估报告
```http
GET /value-assessments/report
Query Parameters:
- start_date: string (ISO 8601)
- end_date: string (ISO 8601)
- assessment_type: string (optional)
- customer_segment: string (optional)

Response:
{
  "summary": {
    "total_assessments": 100,
    "average_intrinsic_score": 0.82,
    "average_cognitive_score": 0.78,
    "average_experiential_score": 0.85,
    "total_willingness_to_pay": 500000.00
  },
  "trends": {
    "intrinsic_value_trend": [0.80, 0.82, 0.85],
    "cognitive_value_trend": [0.75, 0.78, 0.80],
    "experiential_value_trend": [0.82, 0.84, 0.85]
  },
  "insights": [
    {
      "type": "trend",
      "title": "内在价值持续提升",
      "description": "产品内在价值在过去3个月中持续提升",
      "impact_score": 0.85
    }
  ]
}
```

## 6. 边际影响分析API

### 6.1 分析执行

#### 6.1.1 执行边际影响分析
```http
POST /marginal-analysis/execute
Content-Type: application/json

{
  "analysis_period": "2024-01-01",
  "analysis_type": "monthly",
  "analysis_scope": {
    "asset_types": ["研发资产", "设计资产"],
    "capability_types": ["研发能力", "设计能力"],
    "value_types": ["intrinsic_value", "cognitive_value"]
  },
  "analysis_options": {
    "include_synergy": true,
    "include_threshold": true,
    "include_lag": true,
    "optimization_method": "comprehensive"
  }
}

Response:
{
  "analysis_id": "analysis-uuid",
  "status": "running",
  "estimated_completion": "2024-01-01T00:05:00Z",
  "progress": 0.0
}
```

#### 6.1.2 获取分析结果
```http
GET /marginal-analysis/{analysis_id}

Response:
{
  "id": "analysis-uuid",
  "analysis_period": "2024-01-01",
  "analysis_type": "monthly",
  "status": "completed",
  "results": {
    "asset_impact": 150000.00,
    "capability_impact": 120000.00,
    "value_impact": 180000.00,
    "efficiency_metrics": {
      "product_efficiency": 0.85,
      "production_efficiency": 0.78,
      "rd_efficiency": 0.82,
      "dissemination_efficiency": 0.75,
      "delivery_efficiency": 0.80,
      "channel_efficiency": 0.77
    },
    "synergy_effects": {
      "asset_capability_synergy": 0.15,
      "capability_value_synergy": 0.12,
      "asset_value_synergy": 0.18
    },
    "threshold_effects": {
      "critical_thresholds": [
        {
          "variable": "研发投入",
          "threshold": 1000000.00,
          "impact_multiplier": 1.5
        }
      ]
    },
    "lag_effects": {
      "capability_to_value_lag": 3,
      "asset_to_capability_lag": 2
    }
  },
  "confidence_level": 0.92,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z"
}
```

### 6.2 增量计算

#### 6.2.1 计算增量值
```http
POST /delta-calculations
Content-Type: application/json

{
  "calculation_type": "asset_delta",
  "base_period": "2023-12-01",
  "comparison_period": "2024-01-01",
  "calculation_method": "weighted_average",
  "input_data": {
    "asset_ids": ["asset-uuid-1", "asset-uuid-2"],
    "weight_factors": {
      "asset-uuid-1": 0.6,
      "asset-uuid-2": 0.4
    }
  }
}

Response:
{
  "id": "delta-uuid",
  "calculation_type": "asset_delta",
  "delta_value": 50000.00,
  "delta_percentage": 0.05,
  "calculation_method": "weighted_average",
  "validation_status": "validated",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 7. 权重优化API

### 7.1 权重优化

#### 7.1.1 执行权重优化
```http
POST /weight-optimization
Content-Type: application/json

{
  "optimization_method": "comprehensive",
  "target_metric": "r2_score",
  "optimization_scope": {
    "asset_types": ["研发资产", "设计资产"],
    "capability_types": ["研发能力", "设计能力"],
    "value_types": ["intrinsic_value"]
  },
  "constraints": {
    "weight_bounds": {
      "min": 0.01,
      "max": 0.5
    },
    "sum_constraint": 1.0
  },
  "validation_methods": ["cross_validation", "bootstrap"]
}

Response:
{
  "optimization_id": "optimization-uuid",
  "status": "running",
  "estimated_completion": "2024-01-01T00:10:00Z",
  "progress": 0.0
}
```

#### 7.1.2 获取优化结果
```http
GET /weight-optimization/{optimization_id}

Response:
{
  "id": "optimization-uuid",
  "optimization_method": "comprehensive",
  "status": "completed",
  "results": {
    "initial_weights": {
      "研发资产": 0.3,
      "设计资产": 0.2,
      "研发能力": 0.25,
      "设计能力": 0.25
    },
    "optimized_weights": {
      "研发资产": 0.35,
      "设计资产": 0.15,
      "研发能力": 0.3,
      "设计能力": 0.2
    },
    "performance_metrics": {
      "r2_score": 0.92,
      "mse": 0.08,
      "mae": 0.12
    },
    "validation_results": {
      "cross_validation_score": 0.89,
      "bootstrap_confidence": 0.95
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:10:00Z"
}
```

### 7.2 权重监控

#### 7.2.1 获取权重监控数据
```http
GET /weight-monitoring
Query Parameters:
- start_date: string (ISO 8601)
- end_date: string (ISO 8601)
- monitoring_type: string (optional)

Response:
{
  "data": [
    {
      "id": "monitoring-uuid",
      "monitoring_date": "2024-01-01T00:00:00Z",
      "monitoring_type": "performance",
      "current_weights": {
        "研发资产": 0.35,
        "设计资产": 0.15
      },
      "weight_drift": 0.02,
      "performance_score": 0.92,
      "stability_score": 0.88,
      "quality_score": 0.95,
      "anomalies": [],
      "alerts": [],
      "recommendations": [
        "权重稳定性良好，建议继续监控"
      ]
    }
  ]
}
```

## 8. 预测API

### 8.1 预测执行

#### 8.1.1 执行预测
```http
POST /predictions
Content-Type: application/json

{
  "prediction_type": "asset_value",
  "prediction_horizon": 12,
  "input_data": {
    "asset_ids": ["asset-uuid-1", "asset-uuid-2"],
    "historical_periods": 24,
    "external_factors": {
      "market_trend": 0.05,
      "inflation_rate": 0.03
    }
  },
  "model_options": {
    "model_type": "ensemble",
    "include_uncertainty": true,
    "confidence_level": 0.95
  }
}

Response:
{
  "prediction_id": "prediction-uuid",
  "status": "running",
  "estimated_completion": "2024-01-01T00:03:00Z",
  "progress": 0.0
}
```

#### 8.1.2 获取预测结果
```http
GET /predictions/{prediction_id}

Response:
{
  "id": "prediction-uuid",
  "prediction_type": "asset_value",
  "prediction_horizon": 12,
  "status": "completed",
  "results": {
    "predictions": [
      {
        "period": "2024-02-01",
        "predicted_value": 1050000.00,
        "confidence_interval": {
          "lower": 950000.00,
          "upper": 1150000.00
        }
      }
    ],
    "accuracy_metrics": {
      "mape": 0.08,
      "rmse": 50000.00,
      "r2_score": 0.89
    }
  },
  "model_used": "ensemble",
  "weights_used": {
    "研发资产": 0.35,
    "设计资产": 0.15
  },
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:03:00Z"
}
```

## 9. 分析洞察API

### 9.1 洞察获取

#### 9.1.1 获取分析洞察
```http
GET /insights
Query Parameters:
- start_date: string (ISO 8601)
- end_date: string (ISO 8601)
- insight_type: string (optional)
- insight_category: string (optional)

Response:
{
  "data": [
    {
      "id": "insight-uuid",
      "insight_date": "2024-01-01",
      "insight_type": "trend",
      "insight_category": "asset",
      "insight_title": "资产价值持续增长",
      "insight_description": "过去6个月中，研发资产价值持续增长，增长率达到15%",
      "impact_score": 0.85,
      "confidence_level": 0.92,
      "action_required": true,
      "action_items": [
        "增加研发资产投入",
        "优化资产配置结构"
      ]
    }
  ],
  "summary": {
    "total_insights": 25,
    "high_impact_insights": 5,
    "action_required_insights": 8
  }
}
```

#### 9.1.2 创建自定义洞察
```http
POST /insights
Content-Type: application/json

{
  "insight_type": "recommendation",
  "insight_category": "optimization",
  "insight_title": "权重优化建议",
  "insight_description": "基于最新分析结果，建议调整研发资产权重至0.4",
  "impact_score": 0.75,
  "confidence_level": 0.88,
  "action_required": true,
  "action_items": [
    "调整研发资产权重",
    "重新评估资产配置"
  ]
}

Response:
{
  "id": "insight-uuid",
  "insight_type": "recommendation",
  "insight_title": "权重优化建议",
  "impact_score": 0.75,
  "action_required": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 10. 数据导入API

### 10.1 批量数据导入

#### 10.1.1 导入资产数据
```http
POST /import/assets
Content-Type: multipart/form-data

Form Data:
- file: Excel文件
- import_type: "bulk_assets"
- mapping_config: JSON配置

Response:
{
  "import_id": "import-uuid",
  "status": "processing",
  "total_records": 100,
  "processed_records": 0,
  "error_records": 0,
  "estimated_completion": "2024-01-01T00:02:00Z"
}
```

#### 10.1.2 获取导入状态
```http
GET /import/{import_id}

Response:
{
  "id": "import-uuid",
  "status": "completed",
  "total_records": 100,
  "processed_records": 95,
  "error_records": 5,
  "errors": [
    {
      "row": 10,
      "error": "资产名称不能为空",
      "data": {"asset_name": ""}
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:02:00Z"
}
```

## 11. 错误处理

### 11.1 错误响应格式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "asset_name",
        "message": "资产名称不能为空"
      }
    ],
    "request_id": "req-uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 11.2 错误代码
- `400 BAD_REQUEST`: 请求参数错误
- `401 UNAUTHORIZED`: 认证失败
- `403 FORBIDDEN`: 权限不足
- `404 NOT_FOUND`: 资源不存在
- `409 CONFLICT`: 资源冲突
- `422 VALIDATION_ERROR`: 数据验证失败
- `429 TOO_MANY_REQUESTS`: 请求频率过高
- `500 INTERNAL_ERROR`: 服务器内部错误
- `503 SERVICE_UNAVAILABLE`: 服务不可用

## 12. 限流和配额

### 12.1 请求限制
- 认证用户: 1000请求/小时
- 匿名用户: 100请求/小时
- 批量操作: 10请求/小时

### 12.2 数据限制
- 单次查询最大记录数: 1000
- 文件上传最大大小: 100MB
- 批量导入最大记录数: 10000

## 13. 版本控制

### 13.1 API版本
- 当前版本: v1
- 版本策略: 向后兼容
- 废弃通知: 提前6个月通知

### 13.2 数据版本
- 所有数据记录包含版本号
- 支持数据回滚
- 版本历史查询

## 14. 监控和日志

### 14.1 请求日志
- 所有API请求记录日志
- 包含请求ID、用户ID、租户ID
- 响应时间和状态码

### 14.2 性能监控
- API响应时间监控
- 错误率监控
- 资源使用监控

## 15. 总结

本API契约规范提供了完整的边际影响分析系统API接口定义，包括：

1. **11个核心API端点**: 覆盖资产、能力、价值评估、分析、优化、预测、洞察等所有功能
2. **完整的请求/响应格式**: 标准化的JSON格式
3. **认证和授权**: JWT Token认证和租户隔离
4. **错误处理**: 统一的错误响应格式
5. **限流和配额**: 合理的API使用限制
6. **版本控制**: 向后兼容的版本管理
7. **监控和日志**: 完整的API监控体系

该API设计支持多租户架构，具备高性能、高可用性和强安全性，能够满足边际影响分析系统的所有业务需求。



