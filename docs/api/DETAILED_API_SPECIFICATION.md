# 边际影响分析系统 - 详细API规范文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (API设计)
- **实施方**: Lovable (API实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. API概览

### 1.1 基础信息
- **Base URL**: `https://api.qbm-system.com/v1`
- **认证方式**: Bearer Token (JWT)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 通用响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2025-01-23T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 1.3 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": {
      "field": "document_id",
      "reason": "单据号不能为空"
    }
  },
  "timestamp": "2025-01-23T10:30:00Z",
  "request_id": "req_123456789"
}
```

---

## 2. 数据导入API

### 2.1 文件上传接口

#### POST /api/data-import/upload
**功能**: 上传原始数据文件

**请求参数**:
```json
{
  "source_system": "erp",
  "source_type": "expense",
  "file_data": "base64_encoded_file_content",
  "file_name": "expense_data_2024.xlsx",
  "import_method": "manual",
  "processing_options": {
    "auto_detect_format": true,
    "supplement_missing_data": true,
    "validation_level": "strict"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_123456789",
    "file_id": "file_987654321",
    "processing_status": "pending",
    "estimated_records": 1500,
    "detected_format": "repeated_header",
    "processing_time_estimate": "2-3分钟"
  }
}
```

### 2.2 处理状态查询

#### GET /api/data-import/status/{batch_id}
**功能**: 查询数据处理状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_123456789",
    "status": "processing",
    "progress": 65,
    "processed_records": 975,
    "total_records": 1500,
    "success_count": 950,
    "error_count": 25,
    "current_stage": "data_validation",
    "estimated_completion": "2025-01-23T10:35:00Z"
  }
}
```

### 2.3 处理结果获取

#### GET /api/data-import/result/{batch_id}
**功能**: 获取处理结果

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_123456789",
    "processing_summary": {
      "total_records": 1500,
      "success_count": 1450,
      "error_count": 50,
      "processing_time": "2分30秒",
      "data_quality_score": 0.92
    },
    "processed_data": [
      {
        "document_id": "DOC001",
        "document_date": "2024-01-01",
        "customer_name": "客户A",
        "amount": 1000.00,
        "record_type": "header"
      }
    ],
    "quality_report": {
      "completeness": 0.95,
      "accuracy": 0.92,
      "consistency": 0.88,
      "recommendations": [
        "建议检查客户名称的一致性",
        "部分日期格式需要标准化"
      ]
    }
  }
}
```

---

## 3. 边际分析API

### 3.1 ΔV-CL信号检测

#### POST /api/marginal-analysis/delta-vcl-signals
**功能**: 检测ΔV-CL瓶颈信号

**请求参数**:
```json
{
  "analysis_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "analysis_scope": {
    "business_units": ["销售部", "生产部"],
    "process_types": ["生产流程", "传播流程", "交付流程"]
  },
  "signal_config": {
    "sensitivity": "medium",
    "threshold": 0.8,
    "min_data_points": 10
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_123456789",
    "signals": [
      {
        "signal_id": "signal_001",
        "signal_type": "bottleneck",
        "severity": "high",
        "process": "生产流程",
        "business_unit": "生产部",
        "detected_at": "2024-06-15",
        "description": "生产效率瓶颈，边际收益递减",
        "impact_score": 0.85,
        "recommendations": [
          "优化生产资源配置",
          "检查设备维护计划"
        ],
        "related_metrics": {
          "efficiency_score": 0.65,
          "marginal_cost": 1200.00,
          "marginal_revenue": 800.00
        }
      }
    ],
    "analysis_summary": {
      "total_signals": 3,
      "high_severity": 1,
      "medium_severity": 2,
      "low_severity": 0,
      "analysis_confidence": 0.88
    }
  }
}
```

### 3.2 边际分析计算

#### POST /api/marginal-analysis/calculate
**功能**: 计算边际分析指标

**请求参数**:
```json
{
  "calculation_type": "marginal_analysis",
  "input_data": {
    "cost_data": [
      {
        "period": "2024-01",
        "total_cost": 100000,
        "variable_cost": 60000,
        "fixed_cost": 40000
      }
    ],
    "revenue_data": [
      {
        "period": "2024-01",
        "total_revenue": 150000,
        "unit_price": 100,
        "quantity": 1500
      }
    ]
  },
  "analysis_parameters": {
    "time_horizon": 12,
    "discount_rate": 0.08,
    "optimization_target": "profit_maximization"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "calculation_id": "calc_123456789",
    "marginal_analysis": {
      "marginal_cost": 40.00,
      "marginal_revenue": 100.00,
      "marginal_profit": 60.00,
      "optimal_quantity": 2000,
      "profit_maximization_point": {
        "quantity": 2000,
        "total_profit": 120000,
        "marginal_profit": 0
      }
    },
    "efficiency_metrics": {
      "cost_efficiency": 0.75,
      "revenue_efficiency": 0.85,
      "overall_efficiency": 0.80
    },
    "recommendations": [
      "建议增加产量至2000单位",
      "优化成本结构，降低边际成本"
    ]
  }
}
```

---

## 4. 四要素协同分析API

### 4.1 协同效应分析

#### POST /api/synergy-analysis/calculate
**功能**: 计算四要素协同效应

**请求参数**:
```json
{
  "analysis_period": "2024-01-01",
  "core_resources": [
    {
      "resource_id": "resource_001",
      "resource_name": "技术团队",
      "resource_type": "human",
      "quantity": 10,
      "quality_score": 0.85
    }
  ],
  "core_capabilities": [
    {
      "capability_id": "capability_001",
      "capability_name": "产品开发",
      "maturity_level": 0.80,
      "development_investment": 50000
    }
  ],
  "synergy_config": {
    "interaction_degree": 2,
    "optimization_method": "genetic_algorithm",
    "convergence_threshold": 0.001
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "synergy_analysis_id": "synergy_123456789",
    "synergy_effects": [
      {
        "resource_capability_pair": {
          "resource": "技术团队",
          "capability": "产品开发"
        },
        "synergy_coefficient": 0.75,
        "interaction_strength": 0.85,
        "synergy_contribution": 0.80,
        "optimization_potential": 0.15
      }
    ],
    "overall_synergy_score": 0.78,
    "synergy_recommendations": [
      "加强技术团队与产品开发的协作",
      "增加跨部门沟通机制"
    ]
  }
}
```

---

## 5. 三大流程管理API

### 5.1 流程效能监控

#### GET /api/process-monitoring/efficiency
**功能**: 获取三大流程效能数据

**查询参数**:
- `process_type`: 流程类型 (production|propagation|delivery)
- `time_range`: 时间范围 (last_30d|last_90d|last_year)
- `business_unit`: 业务单元 (可选)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "process_type": "production",
    "time_range": "last_30d",
    "efficiency_metrics": {
      "overall_efficiency": 0.82,
      "production_efficiency": 0.85,
      "quality_efficiency": 0.78,
      "cost_efficiency": 0.80
    },
    "trend_analysis": {
      "trend_direction": "improving",
      "trend_strength": 0.15,
      "forecast_next_month": 0.84
    },
    "bottleneck_analysis": {
      "primary_bottleneck": "设备维护",
      "bottleneck_impact": 0.25,
      "resolution_priority": "high"
    }
  }
}
```

### 5.2 流程优化建议

#### POST /api/process-optimization/recommendations
**功能**: 生成流程优化建议

**请求参数**:
```json
{
  "process_type": "production",
  "optimization_goals": [
    "提高生产效率",
    "降低运营成本",
    "提升产品质量"
  ],
  "constraints": {
    "budget_limit": 100000,
    "time_limit": 90,
    "resource_availability": ["设备", "人员", "技术"]
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "optimization_id": "opt_123456789",
    "recommendations": [
      {
        "recommendation_id": "rec_001",
        "title": "优化生产排程",
        "description": "通过智能排程算法优化生产计划",
        "expected_impact": {
          "efficiency_improvement": 0.15,
          "cost_reduction": 20000,
          "time_saving": 10
        },
        "implementation_plan": {
          "duration": 30,
          "resources_required": ["生产经理", "IT支持"],
          "budget_required": 15000
        },
        "priority": "high",
        "feasibility": 0.85
      }
    ],
    "overall_impact": {
      "total_efficiency_gain": 0.25,
      "total_cost_saving": 50000,
      "roi": 2.5
    }
  }
}
```

---

## 6. 映射匹配度分析API

### 6.1 产品特性-客户价值映射

#### POST /api/mapping-analysis/product-customer-mapping
**功能**: 分析产品特性与客户价值的映射关系

**请求参数**:
```json
{
  "product_characteristics": [
    {
      "characteristic_id": "char_001",
      "characteristic_name": "产品质量",
      "characteristic_value": 0.85,
      "characteristic_type": "performance"
    }
  ],
  "customer_values": [
    {
      "value_id": "value_001",
      "value_name": "可靠性",
      "value_importance": 0.90,
      "value_type": "must_have"
    }
  ],
  "mapping_config": {
    "analysis_method": "kano_model",
    "correlation_threshold": 0.7,
    "significance_level": 0.05
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "mapping_analysis_id": "mapping_123456789",
    "mapping_results": [
      {
        "product_characteristic": "产品质量",
        "customer_value": "可靠性",
        "mapping_strength": 0.88,
        "correlation_coefficient": 0.85,
        "significance": true,
        "kano_category": "must_have",
        "optimization_potential": 0.12
      }
    ],
    "overall_mapping_score": 0.82,
    "mapping_recommendations": [
      "加强产品质量与可靠性的关联",
      "优化产品特性配置"
    ]
  }
}
```

---

## 7. 决策管理API

### 7.1 决策循环执行

#### POST /api/decision-management/execute-cycle
**功能**: 执行决策循环分析

**请求参数**:
```json
{
  "trigger_type": "manual",
  "analysis_scope": {
    "business_units": ["销售部", "生产部"],
    "time_period": "2024-01-01 to 2024-12-31"
  },
  "analysis_config": {
    "include_marginal_analysis": true,
    "include_synergy_analysis": true,
    "include_process_optimization": true
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_123456789",
    "execution_status": "completed",
    "analysis_results": {
      "marginal_analysis": {
        "bottleneck_signals": 3,
        "optimization_opportunities": 5
      },
      "synergy_analysis": {
        "synergy_score": 0.78,
        "improvement_potential": 0.15
      },
      "process_optimization": {
        "efficiency_gains": 0.20,
        "cost_savings": 50000
      }
    },
    "recommendations": [
      {
        "category": "immediate_action",
        "priority": "high",
        "description": "立即优化生产排程",
        "expected_impact": "效率提升15%"
      }
    ],
    "next_review_date": "2024-02-15"
  }
}
```

### 7.2 管理者评价确认

#### POST /api/decision-management/manager-evaluation
**功能**: 提交管理者评价和确认

**请求参数**:
```json
{
  "analysis_id": "analysis_123456789",
  "evaluation_type": "confirm",
  "evaluation_content": "同意系统分析结果，建议立即实施优化方案",
  "metric_adjustments": [
    {
      "metric_id": "metric_001",
      "metric_name": "生产效率",
      "current_value": 0.85,
      "adjusted_value": 0.90,
      "adjustment_reason": "基于实际运营情况调整"
    }
  ],
  "implementation_plan": {
    "start_date": "2024-02-01",
    "duration": 60,
    "responsible_person": "生产经理",
    "budget_required": 30000
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "evaluation_id": "eval_123456789",
    "evaluation_status": "confirmed",
    "adjusted_analysis": {
      "updated_metrics": [
        {
          "metric_name": "生产效率",
          "original_value": 0.85,
          "adjusted_value": 0.90,
          "impact_assessment": "预期效率提升5%"
        }
      ]
    },
    "implementation_tracking": {
      "tracking_id": "track_123456789",
      "milestones": [
        {
          "milestone": "方案设计完成",
          "due_date": "2024-02-15",
          "status": "pending"
        }
      ]
    }
  }
}
```

---

## 8. 数据查询API

### 8.1 业务事实查询

#### GET /api/business-facts/query
**功能**: 查询业务事实数据

**查询参数**:
- `fact_type`: 事实类型 (expense|asset|order|feedback)
- `date_range`: 日期范围
- `business_unit`: 业务单元
- `page`: 页码
- `limit`: 每页数量

**响应示例**:
```json
{
  "success": true,
  "data": {
    "facts": [
      {
        "fact_id": "fact_001",
        "fact_type": "expense",
        "amount": 1000.00,
        "date": "2024-01-15",
        "department": "销售部",
        "description": "市场推广费用"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_records": 1000,
      "records_per_page": 100
    },
    "summary": {
      "total_amount": 1000000.00,
      "average_amount": 1000.00,
      "fact_count": 1000
    }
  }
}
```

### 8.2 分析结果查询

#### GET /api/analysis-results/query
**功能**: 查询分析结果

**查询参数**:
- `analysis_type`: 分析类型 (marginal|synergy|process|mapping)
- `time_range`: 时间范围
- `status`: 状态 (completed|processing|failed)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "analysis_results": [
      {
        "analysis_id": "analysis_123456789",
        "analysis_type": "marginal",
        "analysis_date": "2024-01-15",
        "status": "completed",
        "summary": {
          "signals_detected": 3,
          "efficiency_score": 0.82,
          "optimization_potential": 0.15
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_records": 500
    }
  }
}
```

---

## 9. 系统管理API

### 9.1 健康检查

#### GET /api/system/health
**功能**: 系统健康状态检查

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-23T10:30:00Z",
    "components": {
      "database": {
        "status": "healthy",
        "response_time": "50ms"
      },
      "cache": {
        "status": "healthy",
        "hit_rate": 0.85
      },
      "algorithms": {
        "status": "healthy",
        "processing_time": "2.5s"
      }
    },
    "performance_metrics": {
      "cpu_usage": 0.45,
      "memory_usage": 0.60,
      "disk_usage": 0.30
    }
  }
}
```

### 9.2 系统配置

#### GET /api/system/config
**功能**: 获取系统配置

**响应示例**:
```json
{
  "success": true,
  "data": {
    "system_config": {
      "analysis_settings": {
        "default_time_horizon": 12,
        "default_discount_rate": 0.08,
        "signal_sensitivity": "medium"
      },
      "processing_settings": {
        "batch_size": 1000,
        "max_processing_time": 300,
        "retry_attempts": 3
      },
      "notification_settings": {
        "email_notifications": true,
        "sms_notifications": false,
        "notification_frequency": "daily"
      }
    }
  }
}
```

---

## 10. 错误码定义

### 10.1 通用错误码
- `VALIDATION_ERROR`: 数据验证失败
- `AUTHENTICATION_ERROR`: 认证失败
- `AUTHORIZATION_ERROR`: 权限不足
- `NOT_FOUND`: 资源不存在
- `INTERNAL_ERROR`: 内部服务器错误

### 10.2 业务错误码
- `DATA_FORMAT_ERROR`: 数据格式错误
- `PROCESSING_ERROR`: 数据处理失败
- `ANALYSIS_ERROR`: 分析计算失败
- `OPTIMIZATION_ERROR`: 优化计算失败

### 10.3 HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 11. 总结

本API规范文档提供了完整的边际影响分析系统API接口定义，包括：

1. **数据导入API**: 文件上传、处理状态查询、结果获取
2. **边际分析API**: ΔV-CL信号检测、边际分析计算
3. **协同分析API**: 四要素协同效应分析
4. **流程管理API**: 三大流程效能监控和优化
5. **映射分析API**: 产品特性-客户价值映射
6. **决策管理API**: 决策循环执行和管理者评价
7. **数据查询API**: 业务事实和分析结果查询
8. **系统管理API**: 健康检查和配置管理

所有API都具备完整的请求/响应格式、错误处理、认证授权等机制，能够满足系统的所有业务需求。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 2-3周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com


