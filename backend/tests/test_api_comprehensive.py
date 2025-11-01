"""
Backend API测试用例
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from main import app
from src.services.database_service import DatabaseService
from src.services.cache_service import CacheService
from src.services.model_training_service import ModelTrainingService
from src.services.enterprise_memory_service import EnterpriseMemoryService
from src.algorithms.synergy_analysis import SynergyAnalysis
from src.algorithms.threshold_analysis import ThresholdAnalysis
from src.algorithms.dynamic_weights import DynamicWeights

# 测试数据库URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def mock_db_service():
    """模拟数据库服务"""
    mock_service = Mock(spec=DatabaseService)
    mock_service.get_connection.return_value = Mock()
    return mock_service

@pytest.fixture
def mock_cache_service():
    """模拟缓存服务"""
    mock_service = Mock(spec=CacheService)
    mock_service.get.return_value = None
    mock_service.set.return_value = True
    return mock_service

@pytest.fixture
def sample_data():
    """生成测试数据"""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'feature_1': np.random.normal(10, 2, n_samples),
        'feature_2': np.random.normal(5, 1, n_samples),
        'feature_3': np.random.normal(8, 1.5, n_samples),
        'target': np.random.normal(20, 3, n_samples)
    }
    
    return pd.DataFrame(data)

class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "timestamp": response.json()["timestamp"]}

class TestModelTrainingAPI:
    """模型训练API测试"""
    
    @patch('src.api.endpoints.model_training.ModelTrainingService')
    def test_train_marginal_analysis_model(self, mock_service_class, client, sample_data):
        """测试边际分析模型训练"""
        # 模拟服务
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.train_marginal_analysis_model.return_value = {
            "model_id": "test_model_1",
            "model_type": "marginal_analysis",
            "performance_metrics": {
                "r2_score": 0.85,
                "mse": 2.5,
                "mae": 1.2
            },
            "feature_importance": {
                "feature_1": 0.4,
                "feature_2": 0.35,
                "feature_3": 0.25
            }
        }
        
        # 准备请求数据
        request_data = {
            "model_name": "test_marginal_model",
            "model_type": "marginal_analysis",
            "training_data": sample_data.to_dict('records'),
            "target_column": "target",
            "feature_columns": ["feature_1", "feature_2", "feature_3"],
            "hyperparameters": {
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            }
        }
        
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == "test_model_1"
        assert data["model_type"] == "marginal_analysis"
        assert data["performance_metrics"]["r2_score"] == 0.85
    
    @patch('src.api.endpoints.model_training.ModelTrainingService')
    def test_train_time_series_model(self, mock_service_class, client):
        """测试时间序列模型训练"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.train_timeseries_model.return_value = {
            "model_id": "test_ts_model_1",
            "model_type": "time_series",
            "performance_metrics": {
                "r2_score": 0.78,
                "mse": 3.2,
                "mae": 1.5
            },
            "forecast_horizon": 12
        }
        
        request_data = {
            "model_name": "test_ts_model",
            "model_type": "time_series",
            "time_series_data": [
                {"date": "2024-01-01", "value": 100},
                {"date": "2024-01-02", "value": 105},
                {"date": "2024-01-03", "value": 110}
            ],
            "target_column": "value",
            "forecast_horizon": 12,
            "hyperparameters": {
                "n_estimators": 100,
                "learning_rate": 0.1
            }
        }
        
        response = client.post("/api/v1/models/train/time-series", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == "test_ts_model_1"
        assert data["model_type"] == "time_series"
    
    @patch('src.api.endpoints.model_training.ModelTrainingService')
    def test_predict(self, mock_service_class, client):
        """测试预测功能"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.predict.return_value = {
            "prediction_id": "pred_1",
            "predicted_value": 25.5,
            "confidence_interval": {
                "lower": 23.0,
                "upper": 28.0
            },
            "confidence_level": 0.95,
            "model_used": "test_model_1"
        }
        
        request_data = {
            "model_id": "test_model_1",
            "input_data": {
                "feature_1": 12.5,
                "feature_2": 6.0,
                "feature_3": 9.0
            }
        }
        
        response = client.post("/api/v1/models/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_value"] == 25.5
        assert data["confidence_interval"]["lower"] == 23.0
        assert data["confidence_interval"]["upper"] == 28.0

class TestEnterpriseMemoryAPI:
    """企业记忆API测试"""
    
    @patch('src.api.endpoints.enterprise_memory.EnterpriseMemoryService')
    def test_extract_memory_from_feedback(self, mock_service_class, client):
        """测试从反馈中提取记忆"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.extract_memory_from_feedback.return_value = {
            "memory_id": "mem_1",
            "memory_type": "pattern",
            "memory_category": "business_process",
            "memory_content": {
                "pattern": "High customer satisfaction leads to increased revenue",
                "confidence": 0.85,
                "evidence": ["case_1", "case_2", "case_3"]
            },
            "extraction_date": datetime.now().isoformat()
        }
        
        request_data = {
            "feedback_data": {
                "evaluation_id": "eval_1",
                "feedback_type": "confirmation",
                "feedback_content": "Customer satisfaction improved after implementing new process",
                "metrics": {
                    "satisfaction_score": 0.9,
                    "revenue_increase": 0.15
                }
            }
        }
        
        response = client.post("/api/v1/memory/extract/feedback", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["memory_id"] == "mem_1"
        assert data["memory_type"] == "pattern"
    
    @patch('src.api.endpoints.enterprise_memory.EnterpriseMemoryService')
    def test_retrieve_relevant_memories(self, mock_service_class, client):
        """测试检索相关记忆"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.retrieve_relevant_memories.return_value = {
            "query_context": "customer satisfaction analysis",
            "relevant_memories": [
                {
                    "memory_id": "mem_1",
                    "relevance_score": 0.92,
                    "memory_type": "pattern",
                    "memory_content": "High customer satisfaction leads to increased revenue"
                },
                {
                    "memory_id": "mem_2",
                    "relevance_score": 0.78,
                    "memory_type": "strategy",
                    "memory_content": "Focus on customer feedback to improve satisfaction"
                }
            ],
            "total_memories_found": 2
        }
        
        request_data = {
            "query_context": "customer satisfaction analysis",
            "context_type": "prediction",
            "max_results": 10,
            "min_relevance_score": 0.5
        }
        
        response = client.post("/api/v1/memory/retrieve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["relevant_memories"]) == 2
        assert data["relevant_memories"][0]["relevance_score"] == 0.92

class TestPredictionsAPI:
    """预测API测试"""
    
    @patch('src.api.endpoints.predictions.ModelTrainingService')
    def test_track_prediction_accuracy(self, mock_service_class, client):
        """测试预测准确性跟踪"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.track_prediction_accuracy.return_value = {
            "log_id": "log_1",
            "prediction_id": "pred_1",
            "actual_value": 24.8,
            "predicted_value": 25.5,
            "prediction_error": 0.7,
            "absolute_error": 0.7,
            "percentage_error": 2.8,
            "prediction_accuracy": 0.972,
            "is_outlier": False
        }
        
        request_data = {
            "prediction_id": "pred_1",
            "model_id": "test_model_1",
            "prediction_type": "marginal_analysis",
            "predicted_value": 25.5,
            "actual_value": 24.8,
            "prediction_date": datetime.now().isoformat(),
            "feature_values": {
                "feature_1": 12.5,
                "feature_2": 6.0,
                "feature_3": 9.0
            }
        }
        
        response = client.post("/api/v1/predictions/track-accuracy", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["prediction_accuracy"] == 0.972
        assert data["is_outlier"] == False

class TestAlgorithmServices:
    """算法服务测试"""
    
    def test_synergy_analysis(self, sample_data):
        """测试协同效应分析"""
        synergy_analysis = SynergyAnalysis()
        
        X = sample_data[['feature_1', 'feature_2', 'feature_3']]
        y = sample_data['target']
        
        results = synergy_analysis.detect_synergy_effects(X, y)
        
        assert 'overall_score' in results
        assert 'pairwise_interactions' in results
        assert 'polynomial_interactions' in results
        assert 'random_forest_interactions' in results
        assert isinstance(results['overall_score'], float)
        assert 0 <= results['overall_score'] <= 1
    
    def test_threshold_analysis(self, sample_data):
        """测试阈值分析"""
        threshold_analysis = ThresholdAnalysis()
        
        X = sample_data[['feature_1', 'feature_2', 'feature_3']]
        y = sample_data['target']
        
        results = threshold_analysis.detect_threshold_effects(X, y)
        
        assert 'overall_score' in results
        assert 'tree_thresholds' in results
        assert 'piecewise_regression' in results
        assert 'random_forest_thresholds' in results
        assert isinstance(results['overall_score'], float)
        assert 0 <= results['overall_score'] <= 1
    
    def test_dynamic_weights(self, sample_data):
        """测试动态权重计算"""
        dynamic_weights = DynamicWeights()
        
        X = sample_data[['feature_1', 'feature_2', 'feature_3']]
        y = sample_data['target']
        
        results = dynamic_weights.calculate_dynamic_weights(X, y)
        
        assert 'overall_score' in results
        assert 'correlation_weights' in results
        assert 'importance_weights' in results
        assert 'regression_weights' in results
        assert 'normalized' in results
        assert isinstance(results['overall_score'], float)
        assert 0 <= results['overall_score'] <= 1

class TestDataValidation:
    """数据验证测试"""
    
    def test_invalid_model_type(self, client):
        """测试无效的模型类型"""
        request_data = {
            "model_name": "test_model",
            "model_type": "invalid_type",
            "training_data": []
        }
        
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self, client):
        """测试缺失必需字段"""
        request_data = {
            "model_name": "test_model"
            # Missing model_type and training_data
        }
        
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_data_format(self, client):
        """测试无效的数据格式"""
        request_data = {
            "model_name": "test_model",
            "model_type": "marginal_analysis",
            "training_data": "invalid_data_format"
        }
        
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data)
        assert response.status_code == 422  # Validation error

class TestErrorHandling:
    """错误处理测试"""
    
    @patch('src.api.endpoints.model_training.ModelTrainingService')
    def test_model_training_error(self, mock_service_class, client):
        """测试模型训练错误处理"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.train_marginal_analysis_model.side_effect = Exception("Training failed")
        
        request_data = {
            "model_name": "test_model",
            "model_type": "marginal_analysis",
            "training_data": []
        }
        
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data)
        assert response.status_code == 500
        assert "error" in response.json()
    
    @patch('src.api.endpoints.predictions.ModelTrainingService')
    def test_prediction_error(self, mock_service_class, client):
        """测试预测错误处理"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.predict.side_effect = Exception("Prediction failed")
        
        request_data = {
            "model_id": "invalid_model",
            "input_data": {}
        }
        
        response = client.post("/api/v1/models/predict", json=request_data)
        assert response.status_code == 500
        assert "error" in response.json()

class TestPerformance:
    """性能测试"""
    
    def test_large_dataset_handling(self, client):
        """测试大数据集处理"""
        # 生成大数据集
        np.random.seed(42)
        n_samples = 10000
        large_data = {
            'feature_1': np.random.normal(10, 2, n_samples),
            'feature_2': np.random.normal(5, 1, n_samples),
            'feature_3': np.random.normal(8, 1.5, n_samples),
            'target': np.random.normal(20, 3, n_samples)
        }
        
        request_data = {
            "model_name": "large_dataset_model",
            "model_type": "marginal_analysis",
            "training_data": pd.DataFrame(large_data).to_dict('records'),
            "target_column": "target",
            "feature_columns": ["feature_1", "feature_2", "feature_3"]
        }
        
        # 测试请求不会超时
        response = client.post("/api/v1/models/train/marginal-analysis", json=request_data, timeout=30)
        assert response.status_code in [200, 422]  # 可能因为数据太大而验证失败，但不应该超时

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


