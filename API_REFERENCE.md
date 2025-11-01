# QBM AI系统 - API参考文档

## 📋 概述

QBM AI系统提供RESTful API接口，支持边际影响分析、模型训练、预测服务、企业记忆管理等功能。

**基础URL**: `http://localhost:8000/api/v1`

**认证**: JWT Bearer Token

## 🔐 认证

### 获取访问令牌
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 使用令牌
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🧠 模型训练API

### 训练边际分析模型
```http
POST /api/v1/models/train/marginal-analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_name": "sales_analysis_model",
  "model_type": "marginal_analysis",
  "training_data": [
    {
      "feature_1": 100.5,
      "feature_2": 50.0,
      "feature_3": 0.1,
      "target": 1500.0
    }
  ],
  "target_column": "target",
  "feature_columns": ["feature_1", "feature_2", "feature_3"],
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  }
}
```

**响应**:
```json
{
  "model_id": "model_12345",
  "model_type": "marginal_analysis",
  "model_name": "sales_analysis_model",
  "training_status": "completed",
  "performance_metrics": {
    "r2_score": 0.85,
    "mse": 2.5,
    "mae": 1.2,
    "cross_validation_score": 0.82
  },
  "feature_importance": {
    "feature_1": 0.4,
    "feature_2": 0.35,
    "feature_3": 0.25
  },
  "training_time_seconds": 45.2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 训练时间序列模型
```http
POST /api/v1/models/train/time-series
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_name": "revenue_forecast_model",
  "model_type": "time_series",
  "time_series_data": [
    {
      "date": "2024-01-01",
      "value": 1000.0,
      "feature_1": 100.5,
      "feature_2": 50.0
    }
  ],
  "target_column": "value",
  "forecast_horizon": 12,
  "hyperparameters": {
    "n_estimators": 100,
    "learning_rate": 0.1,
    "max_depth": 6
  }
}
```

**响应**:
```json
{
  "model_id": "model_67890",
  "model_type": "time_series",
  "model_name": "revenue_forecast_model",
  "training_status": "completed",
  "performance_metrics": {
    "r2_score": 0.78,
    "mse": 3.2,
    "mae": 1.5,
    "forecast_accuracy": 0.82
  },
  "forecast_horizon": 12,
  "training_time_seconds": 32.1,
  "created_at": "2024-01-15T10:35:00Z"
}
```

### 训练NPV模型
```http
POST /api/v1/models/train/npv
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_name": "asset_npv_model",
  "asset_data": [
    {
      "asset_id": "asset_001",
      "acquisition_cost": 100000,
      "useful_life": 10,
      "maintenance_cost": 5000,
      "utilization_rate": 0.8,
      "performance_score": 0.9
    }
  ],
  "discount_rate": 0.1,
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 8
  }
}
```

### 训练能力价值模型
```http
POST /api/v1/models/train/capability-value
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_name": "capability_value_model",
  "capability_data": [
    {
      "capability_id": "cap_001",
      "development_cost": 50000,
      "proficiency_score": 0.85,
      "utilization_rate": 0.7,
      "performance_impact": 0.8
    }
  ],
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 6
  }
}
```

## 🔮 预测API

### 生成预测
```http
POST /api/v1/models/predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_id": "model_12345",
  "input_data": {
    "feature_1": 120.0,
    "feature_2": 60.0,
    "feature_3": 0.15
  },
  "prediction_type": "marginal_analysis",
  "include_confidence": true
}
```

**响应**:
```json
{
  "prediction_id": "pred_12345",
  "model_id": "model_12345",
  "predicted_value": 1750.5,
  "confidence_interval": {
    "lower": 1650.0,
    "upper": 1850.0
  },
  "confidence_level": 0.95,
  "prediction_accuracy": 0.85,
  "feature_contributions": {
    "feature_1": 0.4,
    "feature_2": 0.35,
    "feature_3": 0.25
  },
  "prediction_date": "2024-01-15T11:00:00Z"
}
```

### 批量预测
```http
POST /api/v1/models/predict/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_id": "model_12345",
  "input_data": [
    {
      "feature_1": 120.0,
      "feature_2": 60.0,
      "feature_3": 0.15
    },
    {
      "feature_1": 130.0,
      "feature_2": 65.0,
      "feature_3": 0.20
    }
  ],
  "prediction_type": "marginal_analysis"
}
```

## 🧠 企业记忆API

### 从反馈中提取记忆
```http
POST /api/v1/memory/extract/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "feedback_data": {
    "evaluation_id": "eval_12345",
    "feedback_type": "confirmation",
    "feedback_content": "分析结果准确，建议采用此策略",
    "metrics": {
      "satisfaction_score": 0.9,
      "revenue_increase": 0.15,
      "cost_reduction": 0.08
    },
    "context": {
      "business_scenario": "sales_optimization",
      "time_period": "Q1_2024"
    }
  }
}
```

**响应**:
```json
{
  "memory_id": "mem_12345",
  "memory_type": "pattern",
  "memory_category": "business_process",
  "memory_content": {
    "pattern": "销售优化策略在Q1期间效果显著",
    "confidence": 0.85,
    "evidence": ["eval_12345"],
    "metrics": {
      "revenue_increase": 0.15,
      "cost_reduction": 0.08
    }
  },
  "extraction_date": "2024-01-15T11:30:00Z",
  "relevance_score": 0.92
}
```

### 从预测错误中提取记忆
```http
POST /api/v1/memory/extract/prediction-error
Authorization: Bearer <token>
Content-Type: application/json

{
  "error_data": {
    "prediction_id": "pred_12345",
    "model_id": "model_12345",
    "predicted_value": 1750.5,
    "actual_value": 1600.0,
    "prediction_error": 150.5,
    "error_context": {
      "feature_values": {
        "feature_1": 120.0,
        "feature_2": 60.0,
        "feature_3": 0.15
      },
      "business_context": "peak_season"
    }
  }
}
```

### 检索相关记忆
```http
POST /api/v1/memory/retrieve
Authorization: Bearer <token>
Content-Type: application/json

{
  "query_context": "销售优化策略分析",
  "context_type": "prediction",
  "max_results": 10,
  "min_relevance_score": 0.5,
  "memory_types": ["pattern", "strategy"],
  "business_context": {
    "scenario": "sales_optimization",
    "time_period": "Q1_2024"
  }
}
```

**响应**:
```json
{
  "query_context": "销售优化策略分析",
  "relevant_memories": [
    {
      "memory_id": "mem_12345",
      "relevance_score": 0.92,
      "memory_type": "pattern",
      "memory_content": "销售优化策略在Q1期间效果显著",
      "confidence": 0.85,
      "application_suggestions": [
        "在Q1期间重点实施销售优化策略",
        "预期收入增长15%，成本降低8%"
      ]
    }
  ],
  "total_memories_found": 1,
  "retrieval_time_ms": 45
}
```

### 应用记忆到预测
```http
POST /api/v1/memory/apply
Authorization: Bearer <token>
Content-Type: application/json

{
  "prediction_id": "pred_12345",
  "memory_ids": ["mem_12345", "mem_67890"],
  "application_method": "weighted_combination",
  "adjustment_parameters": {
    "confidence_threshold": 0.7,
    "max_adjustment": 0.2
  }
}
```

## 📊 预测准确性跟踪API

### 跟踪预测准确性
```http
POST /api/v1/predictions/track-accuracy
Authorization: Bearer <token>
Content-Type: application/json

{
  "prediction_id": "pred_12345",
  "model_id": "model_12345",
  "prediction_type": "marginal_analysis",
  "predicted_value": 1750.5,
  "actual_value": 1600.0,
  "prediction_date": "2024-01-15T11:00:00Z",
  "feature_values": {
    "feature_1": 120.0,
    "feature_2": 60.0,
    "feature_3": 0.15
  },
  "validation_method": "holdout"
}
```

**响应**:
```json
{
  "log_id": "log_12345",
  "prediction_id": "pred_12345",
  "actual_value": 1600.0,
  "predicted_value": 1750.5,
  "prediction_error": 150.5,
  "absolute_error": 150.5,
  "percentage_error": 9.4,
  "prediction_accuracy": 0.906,
  "is_outlier": false,
  "outlier_reason": null,
  "tracking_date": "2024-01-15T12:00:00Z"
}
```

### 获取预测准确性统计
```http
GET /api/v1/predictions/accuracy-stats?model_id=model_12345&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

**响应**:
```json
{
  "model_id": "model_12345",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "statistics": {
    "total_predictions": 150,
    "avg_accuracy": 0.85,
    "avg_absolute_error": 125.5,
    "avg_percentage_error": 7.8,
    "accuracy_std": 0.12,
    "outlier_rate": 0.05,
    "feedback_rate": 0.15
  },
  "trend_analysis": {
    "accuracy_trend": "improving",
    "trend_slope": 0.02,
    "trend_confidence": 0.78
  }
}
```

## 📈 算法分析API

### 协同效应分析
```http
POST /api/v1/algorithms/synergy-analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "analysis_data": [
    {
      "feature_1": 100.5,
      "feature_2": 50.0,
      "feature_3": 0.1,
      "target": 1500.0
    }
  ],
  "target_column": "target",
  "feature_columns": ["feature_1", "feature_2", "feature_3"],
  "analysis_options": {
    "max_lag": 12,
    "min_correlation": 0.1,
    "significance_level": 0.05
  }
}
```

**响应**:
```json
{
  "analysis_id": "analysis_12345",
  "overall_score": 0.75,
  "synergy_level": "high",
  "pairwise_interactions": [
    {
      "features": ["feature_1", "feature_2"],
      "synergy_score": 0.68,
      "significance": 0.95,
      "interaction_type": "multiplicative"
    }
  ],
  "polynomial_interactions": [
    {
      "features": ["feature_1", "feature_2"],
      "degree": 2,
      "synergy_score": 0.72,
      "significance": 0.88
    }
  ],
  "random_forest_interactions": [
    {
      "features": ["feature_1", "feature_2"],
      "importance_gain": 0.15,
      "synergy_score": 0.65
    }
  ],
  "shapley_values": {
    "feature_contributions": {
      "feature_1": 0.4,
      "feature_2": 0.35,
      "feature_3": 0.25
    },
    "interaction_contributions": {
      "feature_1_x_feature_2": 0.12
    }
  },
  "insights": [
    "feature_1和feature_2之间存在显著的协同效应",
    "建议在模型中包含交互特征"
  ],
  "recommendations": [
    "添加feature_1 × feature_2交互特征",
    "考虑使用非线性模型"
  ]
}
```

### 阈值分析
```http
POST /api/v1/algorithms/threshold-analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "analysis_data": [
    {
      "feature_1": 100.5,
      "feature_2": 50.0,
      "feature_3": 0.1,
      "target": 1500.0
    }
  ],
  "target_column": "target",
  "feature_columns": ["feature_1", "feature_2", "feature_3"],
  "analysis_options": {
    "max_thresholds": 5,
    "min_effect_size": 0.1,
    "significance_level": 0.05
  }
}
```

### 动态权重分析
```http
POST /api/v1/algorithms/dynamic-weights
Authorization: Bearer <token>
Content-Type: application/json

{
  "analysis_data": [
    {
      "feature_1": 100.5,
      "feature_2": 50.0,
      "feature_3": 0.1,
      "target": 1500.0
    }
  ],
  "target_column": "target",
  "feature_columns": ["feature_1", "feature_2", "feature_3"],
  "weight_methods": ["correlation", "importance", "regression"],
  "optimization_options": {
    "method": "gradient_descent",
    "max_iterations": 1000,
    "convergence_threshold": 1e-6
  }
}
```

## 📋 管理者评价API

### 提交评价
```http
POST /api/v1/evaluations
Authorization: Bearer <token>
Content-Type: application/json

{
  "evaluation_type": "confirmation",
  "evaluation_score": 0.85,
  "feedback": "分析结果准确，建议采用此策略",
  "analysis_id": "analysis_12345",
  "evaluation_context": {
    "business_scenario": "sales_optimization",
    "time_period": "Q1_2024",
    "stakeholders": ["sales_manager", "finance_manager"]
  },
  "suggested_improvements": [
    "增加季节性因素考虑",
    "优化特征选择算法"
  ]
}
```

**响应**:
```json
{
  "evaluation_id": "eval_12345",
  "evaluation_type": "confirmation",
  "evaluation_score": 0.85,
  "feedback": "分析结果准确，建议采用此策略",
  "status": "completed",
  "quality_assessment": {
    "completeness_score": 0.9,
    "accuracy_score": 0.85,
    "consistency_score": 0.88,
    "overall_quality": 0.88
  },
  "learning_insights": [
    "确认了销售优化策略的有效性",
    "识别了季节性因素的重要性"
  ],
  "created_at": "2024-01-15T13:00:00Z"
}
```

### 获取评价历史
```http
GET /api/v1/evaluations?evaluator_id=user_123&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

### 获取评价统计
```http
GET /api/v1/evaluations/statistics?period=monthly&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## 🔄 决策循环API

### 获取决策循环状态
```http
GET /api/v1/decision-cycle/status
Authorization: Bearer <token>
```

**响应**:
```json
{
  "cycle_id": "cycle_12345",
  "status": "running",
  "progress": 65,
  "current_phase": "model_training",
  "estimated_completion": "2024-01-15T15:00:00Z",
  "execution_history": [
    {
      "phase": "data_preprocessing",
      "status": "completed",
      "duration_seconds": 120,
      "completed_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 触发决策循环
```http
POST /api/v1/decision-cycle/trigger
Authorization: Bearer <token>
Content-Type: application/json

{
  "trigger_type": "scheduled",
  "trigger_context": {
    "business_scenario": "monthly_analysis",
    "data_sources": ["sales_data", "customer_data"]
  },
  "execution_parameters": {
    "analysis_types": ["synergy", "threshold", "lag"],
    "model_types": ["marginal_analysis", "time_series"]
  }
}
```

## 📊 数据导入API

### 上传数据文件
```http
POST /api/v1/data/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary_file_data>
file_type: "excel"
mapping_config: {
  "target_column": "revenue",
  "feature_columns": ["price", "quantity", "promotion"],
  "date_column": "date"
}
```

**响应**:
```json
{
  "upload_id": "upload_12345",
  "filename": "sales_data.xlsx",
  "file_size": 2048576,
  "records_total": 1500,
  "records_successful": 1480,
  "records_failed": 20,
  "upload_status": "completed",
  "quality_report": {
    "missing_values": 0.02,
    "duplicate_rows": 0.01,
    "outliers": 0.05,
    "data_quality_score": 0.92
  },
  "uploaded_at": "2024-01-15T14:00:00Z"
}
```

### 获取上传历史
```http
GET /api/v1/data/upload-history?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## 🔍 搜索和过滤

### 通用搜索
```http
GET /api/v1/search?query=sales&type=model&limit=10&offset=0
Authorization: Bearer <token>
```

### 高级过滤
```http
POST /api/v1/search/advanced
Authorization: Bearer <token>
Content-Type: application/json

{
  "filters": {
    "model_type": "marginal_analysis",
    "created_after": "2024-01-01",
    "performance_threshold": 0.8
  },
  "sort_by": "created_at",
  "sort_order": "desc",
  "limit": 20,
  "offset": 0
}
```

## 📈 监控和统计API

### 系统健康检查
```http
GET /api/v1/health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T15:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "models": "healthy"
  },
  "metrics": {
    "active_models": 15,
    "total_predictions": 1250,
    "avg_response_time_ms": 45
  }
}
```

### 获取系统统计
```http
GET /api/v1/statistics?period=daily&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## ❌ 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "model_name",
      "issue": "Model name is required"
    },
    "timestamp": "2024-01-15T15:30:00Z",
    "request_id": "req_12345"
  }
}
```

### 常见错误代码
- `VALIDATION_ERROR` (400): 输入数据验证失败
- `AUTHENTICATION_ERROR` (401): 认证失败
- `AUTHORIZATION_ERROR` (403): 权限不足
- `NOT_FOUND` (404): 资源不存在
- `CONFLICT` (409): 资源冲突
- `INTERNAL_ERROR` (500): 服务器内部错误
- `SERVICE_UNAVAILABLE` (503): 服务不可用

## 📝 请求限制

- **速率限制**: 1000 请求/小时/用户
- **文件上传**: 最大 10MB
- **批量操作**: 最大 1000 条记录
- **超时**: 30秒 (训练操作除外)

## 🔄 版本控制

API版本通过URL路径控制：
- `v1`: 当前稳定版本
- `v2`: 开发中版本 (预览)

## 📚 更多资源

- [完整实施指南](./IMPLEMENTATION_GUIDE.md)
- [算法详细说明](./docs/algorithms/)
- [部署指南](./docs/deployment/)
- [故障排除](./docs/troubleshooting/)

---

**API文档版本**: 1.0.0  
**最后更新**: 2024-01-15