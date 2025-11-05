"""
BMOS系统 - API测试套件
作用: 提供API端到端测试
状态: ✅ 实施中
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import json
from datetime import datetime

# 导入应用
from main import app
from services.model_training_service import ModelTrainingService
from services.enterprise_memory_service import EnterpriseMemoryService
from services.database_service import DatabaseService
from services.cache_service import CacheService
from src.api.dependencies import (
    get_model_training_service,
    get_database_service,
    get_current_user,
    get_memory_service,
    get_cache_service,
)

# 测试客户端
client = TestClient(app)

# Mock数据
MOCK_USER = {
    "user_id": "test_user_123",
    "tenant_id": "test_tenant_456",
    "role": "admin",
}

MOCK_MODEL_INFO = {
    "id": "model_123",
    "model_type": "marginal_analysis",
    "model_version": "v1.0.0",
    "model_name": "Test Model",
    "accuracy_score": 0.85,
    "r_squared": 0.82,
    "mae": 0.05,
    "rmse": 0.08,
    "training_data_size": 1000,
    "last_training_date": "2024-01-01T00:00:00",
    "model_status": "active",
    "is_production": True,
}

MOCK_PREDICTION_RESULT = {
    "success": True,
    "prediction": {
        "value": 1500000,
        "confidence": 0.85,
        "features_importance": {"asset_investment": 0.6, "capability_improvement": 0.4},
    },
}

MOCK_MEMORY_DATA = {
    "id": "memory_123",
    "memory_type": "pattern",
    "memory_category": "business_rule",
    "memory_title": "市场环境调整规则",
    "memory_description": "当市场环境变化时，需要调整预测模型",
    "memory_content": {
        "condition": "market_condition == 'volatile'",
        "adjustment": "multiply_prediction_by(0.9)",
    },
    "source_type": "manager_evaluation",
    "source_reference_id": "eval_123",
    "confidence_score": 0.9,
    "success_rate": 0.85,
    "applied_count": 5,
    "created_at": "2024-01-01T00:00:00",
    "last_applied_at": "2024-01-15T00:00:00",
    "is_active": True,
}


class TestModelTrainingAPI:
    """模型训练API测试"""

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_train_model_success(self):
        """测试模型训练成功"""
        training_request = {
            "model_type": "marginal_analysis",
            "target_variable": "revenue",
            "features": ["asset_investment", "capability_improvement"],
            "hyperparameters": {"rf_n_estimators": 100, "rf_max_depth": 10},
            "training_data_period": "2024-01-01 to 2024-12-31",
        }

        # Mock依赖
        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post("/api/v1/models/train", json=training_request)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            assert "task_id" in data

    def test_train_model_invalid_type(self):
        """测试无效模型类型"""
        training_request = {
            "model_type": "invalid_type",
            "target_variable": "revenue",
            "features": ["asset_investment"],
        }

        response = client.post("/api/v1/models/train", json=training_request)
        assert response.status_code == 400
        assert "不支持的模型类型" in response.json()["detail"]

    def test_get_model_info(self):
        """测试获取模型信息"""
        model_id = "model_123"

        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.get(f"/api/v1/models/{model_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == model_id

    def test_list_models(self):
        """测试列出模型"""
        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.get("/api/v1/models/")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestEnterpriseMemoryAPI:
    """企业记忆API测试"""

    def test_extract_memory_success(self):
        """测试记忆提取成功"""
        extraction_request = {
            "evaluation_data": {
                "evaluationType": "adjust",
                "metricAdjustments": [
                    {"metricName": "revenue", "adjustmentReason": "市场环境变化"}
                ],
                "evaluationContent": "需要根据市场环境调整预测模型",
            },
            "historical_evaluations": [],
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_memory_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post("/api/v1/memories/extract", json=extraction_request)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "memories" in data

    def test_search_memories(self):
        """测试记忆搜索"""
        search_request = {
            "context": {
                "scenario": "revenue_prediction",
                "department": "sales",
                "time_period": "2024-Q1",
            },
            "memory_type": "pattern",
            "min_confidence": 0.7,
            "min_relevance": 0.6,
            "limit": 10,
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_memory_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_cache_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post("/api/v1/memories/search", json=search_request)
            assert response.status_code == 200
            data = response.json()
            assert "memories" in data
            assert "total_count" in data

    def test_apply_memory(self):
        """测试记忆应用"""
        application_request = {
            "base_prediction": {"value": 1500000, "confidence": 0.85},
            "memory_ids": ["memory_123"],
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_memory_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post("/api/v1/memories/apply", json=application_request)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "adjusted_prediction" in data


class TestPredictionAPI:
    """预测API测试"""

    def test_single_prediction(self):
        """测试单次预测"""
        prediction_request = {
            "model_id": "model_123",
            "input_data": {
                "asset_investment": 1000000,
                "capability_improvement": 0.15,
                "market_condition": "good",
            },
            "prediction_type": "single",
            "include_confidence": True,
            "apply_memory": True,
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_memory_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_cache_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post(
                "/api/v1/predictions/predict", json=prediction_request
            )
            assert response.status_code == 200
            data = response.json()
            assert "prediction_id" in data
            assert "prediction_result" in data

    def test_batch_prediction(self):
        """测试批量预测"""
        batch_request = {
            "model_id": "model_123",
            "input_batch": [
                {"asset_investment": 1000000, "capability_improvement": 0.15},
                {"asset_investment": 2000000, "capability_improvement": 0.20},
            ],
            "include_confidence": True,
            "apply_memory": True,
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_memory_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post(
                "/api/v1/predictions/predict/batch", json=batch_request
            )
            assert response.status_code == 200
            data = response.json()
            assert "batch_id" in data
            assert data["total_count"] == 2

    def test_timeseries_prediction(self):
        """测试时间序列预测"""
        timeseries_request = {
            "model_id": "timeseries_model_123",
            "historical_data": [
                {"date": "2024-01-01", "value": 1000000},
                {"date": "2024-02-01", "value": 1100000},
                {"date": "2024-03-01", "value": 1200000},
            ],
            "forecast_periods": 12,
            "include_confidence_intervals": True,
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post(
                "/api/v1/predictions/predict/timeseries", json=timeseries_request
            )
            assert response.status_code == 200
            data = response.json()
            assert "forecast_data" in data
            assert len(data["forecast_data"]) == 12

    def test_prediction_history(self):
        """测试预测历史"""
        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.get("/api/v1/predictions/history")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_model_accuracy(self):
        """测试模型准确度"""
        model_id = "model_123"

        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.get(f"/api/v1/predictions/accuracy/{model_id}")
            assert response.status_code == 200
            data = response.json()
            assert "accuracy_rate" in data
            assert "total_predictions" in data

    def test_prediction_feedback(self):
        """测试预测反馈"""
        feedback_data = {
            "prediction_id": "pred_123",
            "actual_value": 1600000,
            "feedback_notes": "实际结果比预测高",
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post("/api/v1/predictions/feedback", json=feedback_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True


class TestIntegration:
    """集成测试"""

    def test_full_prediction_workflow(self):
        """测试完整预测工作流"""
        # 1. 训练模型
        training_request = {
            "model_type": "marginal_analysis",
            "target_variable": "revenue",
            "features": ["asset_investment", "capability_improvement"],
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            # 训练模型
            train_response = client.post("/api/v1/models/train", json=training_request)
            assert train_response.status_code == 200
            task_id = train_response.json()["task_id"]

            # 2. 提取记忆
            extraction_request = {
                "evaluation_data": {
                    "evaluationType": "adjust",
                    "evaluationContent": "需要调整预测模型",
                }
            }

            overrides[get_memory_service] = lambda: Mock()
            memory_response = client.post(
                "/api/v1/memories/extract", json=extraction_request
            )
            assert memory_response.status_code == 200

            # 3. 执行预测
            prediction_request = {
                "model_id": "model_123",
                "input_data": {
                    "asset_investment": 1000000,
                    "capability_improvement": 0.15,
                },
                "apply_memory": True,
            }

            overrides[get_cache_service] = lambda: Mock()
            pred_response = client.post(
                "/api/v1/predictions/predict", json=prediction_request
            )
            assert pred_response.status_code == 200

            # 4. 提交反馈
            feedback_data = {
                "prediction_id": pred_response.json()["prediction_id"],
                "actual_value": 1500000,
            }

            feedback_response = client.post(
                "/api/v1/predictions/feedback", json=feedback_data
            )
            assert feedback_response.status_code == 200


class TestErrorHandling:
    """错误处理测试"""

    def test_model_not_found(self):
        """测试模型不存在"""
        prediction_request = {
            "model_id": "nonexistent_model",
            "input_data": {"test": 1},
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.post(
                "/api/v1/predictions/predict", json=prediction_request
            )
            assert response.status_code == 404
            assert "模型不存在" in response.json()["detail"]

    def test_invalid_input_data(self):
        """测试无效输入数据"""
        prediction_request = {"model_id": "model_123", "input_data": {}}  # 空输入数据

        response = client.post("/api/v1/predictions/predict", json=prediction_request)
        assert response.status_code == 422  # Validation error

    def test_database_connection_error(self):
        """测试数据库连接错误"""
        # Mock数据库服务抛出异常
        mock_db = Mock()
        mock_db.execute_one.side_effect = Exception("Database connection failed")

        with client.app.dependency_overrides as overrides:
            overrides[get_database_service] = lambda: mock_db
            overrides[get_current_user] = lambda: MOCK_USER

            response = client.get("/api/v1/models/model_123")
            assert response.status_code == 500
            assert "Database error" in response.json()["detail"]


# 性能测试
class TestPerformance:
    """性能测试"""

    def test_prediction_response_time(self):
        """测试预测响应时间"""
        prediction_request = {
            "model_id": "model_123",
            "input_data": {"asset_investment": 1000000, "capability_improvement": 0.15},
        }

        with client.app.dependency_overrides as overrides:
            overrides[get_model_training_service] = lambda: Mock()
            overrides[get_database_service] = lambda: Mock()
            overrides[get_cache_service] = lambda: Mock()
            overrides[get_current_user] = lambda: MOCK_USER

            import time

            start_time = time.time()
            response = client.post(
                "/api/v1/predictions/predict", json=prediction_request
            )
            end_time = time.time()

            assert response.status_code == 200
            assert (end_time - start_time) < 2.0  # 响应时间应小于2秒

    def test_concurrent_predictions(self):
        """测试并发预测"""
        import threading
        import time

        prediction_request = {
            "model_id": "model_123",
            "input_data": {"asset_investment": 1000000, "capability_improvement": 0.15},
        }

        results = []

        def make_prediction():
            with client.app.dependency_overrides as overrides:
                overrides[get_model_training_service] = lambda: Mock()
                overrides[get_database_service] = lambda: Mock()
                overrides[get_cache_service] = lambda: Mock()
                overrides[get_current_user] = lambda: MOCK_USER

                response = client.post(
                    "/api/v1/predictions/predict", json=prediction_request
                )
                results.append(response.status_code)

        # 创建10个并发线程
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_prediction)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有请求都成功
        assert len(results) == 10
        assert all(status == 200 for status in results)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
