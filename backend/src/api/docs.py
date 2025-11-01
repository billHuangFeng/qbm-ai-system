"""
BMOS系统 - API文档配置
作用: 配置API文档和OpenAPI规范
状态: ✅ 实施中
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
import os

def create_openapi_schema(app: FastAPI) -> dict:
    """创建OpenAPI规范"""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="BMOS API",
            version="1.0.0",
            description="""
            ## BMOS边际分析系统API文档
            
            ### 系统概述
            BMOS (Business Model Optimization System) 是一个基于AI的边际分析系统，
            通过机器学习模型和企业记忆机制，实现"越用越聪明"的智能决策支持。
            
            ### 核心功能
            
            #### 1. 模型训练服务
            - **边际分析模型**: 分析资产投资和能力提升的边际效应
            - **时间序列模型**: 预测业务指标的未来趋势
            - **NPV计算模型**: 评估资产投资的净现值
            - **能力价值模型**: 量化核心能力的价值贡献
            
            #### 2. 企业记忆系统
            - **记忆提取**: 从管理者评价中自动提取业务规则和模式
            - **记忆检索**: 基于上下文智能搜索相关记忆
            - **记忆应用**: 将历史经验应用到当前预测中
            - **效果追踪**: 监控记忆应用的效果和准确度
            
            #### 3. 预测服务
            - **单次预测**: 基于输入数据生成预测结果
            - **批量预测**: 支持大量数据的批量预测处理
            - **时间序列预测**: 提供未来趋势预测和置信区间
            - **预测反馈**: 收集实际结果用于模型优化
            
            ### 技术特性
            
            #### 智能学习机制
            - **动态权重优化**: 基于历史数据自动调整模型权重
            - **反馈闭环**: 管理者评价 → 模型更新 → 预测改进
            - **企业记忆**: 积累和复用业务经验和规则
            - **持续优化**: 模型性能随使用时间不断提升
            
            #### 多租户架构
            - **数据隔离**: 每个租户的数据完全隔离
            - **权限控制**: 基于角色的访问控制
            - **个性化**: 每个租户拥有独立的模型和记忆
            
            ### API使用指南
            
            #### 认证方式
            所有API请求都需要在Header中包含有效的JWT Token:
            ```
            Authorization: Bearer <your_jwt_token>
            ```
            
            #### 响应格式
            所有API响应都遵循统一格式:
            ```json
            {
                "success": true,
                "data": {...},
                "message": "操作成功",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            ```
            
            #### 错误处理
            错误响应包含详细的错误信息:
            ```json
            {
                "success": false,
                "error": {
                    "code": "MODEL_NOT_FOUND",
                    "message": "模型不存在",
                    "details": {...}
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
            ```
            
            ### 快速开始
            
            #### 1. 训练模型
            ```bash
            POST /api/v1/models/train
            {
                "model_type": "marginal_analysis",
                "target_variable": "revenue",
                "features": ["asset_investment", "capability_improvement"]
            }
            ```
            
            #### 2. 执行预测
            ```bash
            POST /api/v1/predictions/predict
            {
                "model_id": "model_123",
                "input_data": {
                    "asset_investment": 1000000,
                    "capability_improvement": 0.15
                }
            }
            ```
            
            #### 3. 提取企业记忆
            ```bash
            POST /api/v1/memories/extract
            {
                "evaluation_data": {
                    "evaluationType": "adjust",
                    "evaluationContent": "需要调整预测模型"
                }
            }
            ```
            
            ### 最佳实践
            
            #### 模型训练
            - 使用足够的历史数据（建议至少1000条记录）
            - 定期重训练模型以保持准确性
            - 监控模型性能指标（准确度、R²、MAE等）
            
            #### 预测使用
            - 确保输入数据的质量和完整性
            - 利用企业记忆提高预测准确性
            - 及时提交预测反馈以改进模型
            
            #### 企业记忆
            - 定期提取和整理业务规则
            - 维护记忆的准确性和时效性
            - 监控记忆应用的效果
            
            ### 支持与联系
            
            如有问题或建议，请联系技术支持团队。
            
            - **邮箱**: support@bmos.ai
            - **文档**: https://docs.bmos.ai
            - **GitHub**: https://github.com/bmos/bmos-ai-system
            """,
            routes=app.routes,
        )
        
        # 添加自定义标签
        openapi_schema["tags"] = [
            {
                "name": "模型训练",
                "description": "机器学习模型的训练、重训练和管理"
            },
            {
                "name": "企业记忆",
                "description": "企业记忆的提取、搜索、应用和追踪"
            },
            {
                "name": "预测服务",
                "description": "基于训练模型的预测和反馈"
            },
            {
                "name": "系统管理",
                "description": "系统健康检查、配置和监控"
            }
        ]
        
        # 添加服务器信息
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "开发环境"
            },
            {
                "url": "https://api.bmos.ai",
                "description": "生产环境"
            }
        ]
        
        # 添加安全方案
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Token认证"
            }
        }
        
        # 添加全局安全要求
        openapi_schema["security"] = [{"BearerAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    return custom_openapi

def configure_api_docs(app: FastAPI):
    """配置API文档"""
    
    # 设置自定义OpenAPI
    app.openapi = create_openapi_schema(app)
    
    # 配置Swagger UI
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    
    # 添加CORS支持文档访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

# API文档元数据
API_METADATA = {
    "title": "BMOS API",
    "version": "1.0.0",
    "description": "BMOS边际分析系统API",
    "contact": {
        "name": "BMOS技术支持",
        "email": "support@bmos.ai",
        "url": "https://docs.bmos.ai"
    },
    "license": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    "termsOfService": "https://bmos.ai/terms",
    "externalDocs": {
        "description": "BMOS系统文档",
        "url": "https://docs.bmos.ai"
    }
}

# API端点分组
API_TAGS = [
    {
        "name": "模型训练",
        "description": "机器学习模型的训练、重训练和管理功能",
        "externalDocs": {
            "description": "模型训练指南",
            "url": "https://docs.bmos.ai/models"
        }
    },
    {
        "name": "企业记忆",
        "description": "企业记忆的提取、搜索、应用和追踪功能",
        "externalDocs": {
            "description": "企业记忆指南",
            "url": "https://docs.bmos.ai/memories"
        }
    },
    {
        "name": "预测服务",
        "description": "基于训练模型的预测和反馈功能",
        "externalDocs": {
            "description": "预测服务指南",
            "url": "https://docs.bmos.ai/predictions"
        }
    },
    {
        "name": "系统管理",
        "description": "系统健康检查、配置和监控功能",
        "externalDocs": {
            "description": "系统管理指南",
            "url": "https://docs.bmos.ai/admin"
        }
    }
]

# 示例请求和响应
EXAMPLE_REQUESTS = {
    "train_model": {
        "summary": "训练边际分析模型",
        "value": {
            "model_type": "marginal_analysis",
            "target_variable": "revenue",
            "features": ["asset_investment", "capability_improvement"],
            "hyperparameters": {
                "rf_n_estimators": 100,
                "rf_max_depth": 10
            },
            "training_data_period": "2024-01-01 to 2024-12-31"
        }
    },
    "make_prediction": {
        "summary": "执行预测",
        "value": {
            "model_id": "model_123",
            "input_data": {
                "asset_investment": 1000000,
                "capability_improvement": 0.15,
                "market_condition": "good"
            },
            "prediction_type": "single",
            "include_confidence": True,
            "apply_memory": True
        }
    },
    "extract_memory": {
        "summary": "提取企业记忆",
        "value": {
            "evaluation_data": {
                "evaluationType": "adjust",
                "metricAdjustments": [
                    {
                        "metricName": "revenue",
                        "adjustmentReason": "市场环境变化"
                    }
                ],
                "evaluationContent": "需要根据市场环境调整预测模型"
            },
            "historical_evaluations": []
        }
    }
}

EXAMPLE_RESPONSES = {
    "training_success": {
        "summary": "训练任务提交成功",
        "value": {
            "task_id": "task_123",
            "status": "queued",
            "estimated_time": "10-15分钟",
            "message": "模型训练任务已提交"
        }
    },
    "prediction_success": {
        "summary": "预测成功",
        "value": {
            "prediction_id": "pred_123",
            "model_id": "model_123",
            "prediction_result": {
                "value": 1500000,
                "confidence": 0.85,
                "features_importance": {
                    "asset_investment": 0.6,
                    "capability_improvement": 0.4
                }
            },
            "confidence_score": 0.85,
            "applied_memories": ["memory_123"],
            "prediction_time": "2024-01-01T00:00:00",
            "processing_time_ms": 150
        }
    },
    "memory_extraction_success": {
        "summary": "记忆提取成功",
        "value": {
            "success": True,
            "memories": [
                {
                    "id": "memory_123",
                    "memory_type": "pattern",
                    "memory_title": "市场环境调整规则",
                    "memory_description": "当市场环境变化时，需要调整预测模型",
                    "confidence_score": 0.9
                }
            ],
            "memory_count": 1,
            "message": "成功提取 1 条企业记忆"
        }
    }
}


