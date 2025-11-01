"""
API集成测试
"""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.src.main import app

class TestAPIIntegration:
    """API集成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.client = TestClient(app)
        
        # 创建测试数据
        np.random.seed(42)
        n_samples = 100
        self.test_data = {
            "features": {
                "feature1": np.random.normal(0, 1, n_samples).tolist(),
                "feature2": np.random.normal(0, 1, n_samples).tolist(),
                "feature3": np.random.normal(0, 1, n_samples).tolist()
            },
            "target": (np.random.normal(0, 1, n_samples) * 2).tolist()
        }
        
        self.test_weights = {
            "feature1": 0.5,
            "feature2": 0.3,
            "feature3": 0.2
        }
    
    def test_analyze_data_relationships_api(self):
        """测试数据关系分析API"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": self.test_data,
                    "analysis_types": ["synergy", "threshold", "lag", "advanced"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis_results" in data
            assert "status" in data
            assert data["status"] == "completed"
    
    def test_optimize_weights_api(self):
        """测试权重优化API"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/optimize-weights",
                json={
                    "data": self.test_data,
                    "optimization_method": "comprehensive",
                    "validation_methods": ["cross_validation", "bootstrap"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "optimization_results" in data
            assert "status" in data
            assert data["status"] == "completed"
    
    def test_predict_with_optimized_weights_api(self):
        """测试使用优化权重进行预测API"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            # 创建测试数据
            test_data_with_test = {
                "features": self.test_data["features"],
                "target": self.test_data["target"],
                "test_features": {
                    "feature1": np.random.normal(0, 1, 20).tolist(),
                    "feature2": np.random.normal(0, 1, 20).tolist(),
                    "feature3": np.random.normal(0, 1, 20).tolist()
                }
            }
            
            response = self.client.post(
                "/api/v1/models/predict",
                json={
                    "data": test_data_with_test,
                    "weights": self.test_weights
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "predictions" in data
            assert "status" in data
            assert data["status"] == "completed"
    
    def test_get_algorithm_insights_api(self):
        """测试获取算法洞察API"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.get("/api/v1/models/insights")
            
            assert response.status_code == 200
            data = response.json()
            assert "insights" in data
            assert "status" in data
            assert data["status"] == "completed"
    
    def test_analyze_data_relationships_empty_data(self):
        """测试空数据处理"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": {"features": {}, "target": []},
                    "analysis_types": ["synergy"]
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "数据不能为空" in data["detail"]
    
    def test_optimize_weights_empty_data(self):
        """测试空数据权重优化"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/optimize-weights",
                json={
                    "data": {"features": {}, "target": []},
                    "optimization_method": "comprehensive"
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "数据不能为空" in data["detail"]
    
    def test_predict_empty_data(self):
        """测试空数据预测"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/predict",
                json={
                    "data": {"features": {}, "target": [], "test_features": {}},
                    "weights": {}
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "数据不能为空" in data["detail"]
    
    def test_analyze_data_relationships_different_types(self):
        """测试不同分析类型"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            analysis_types_list = [
                ["synergy"],
                ["threshold"],
                ["lag"],
                ["advanced"],
                ["synergy", "threshold"],
                ["synergy", "lag", "advanced"]
            ]
            
            for analysis_types in analysis_types_list:
                response = self.client.post(
                    "/api/v1/models/analyze",
                    json={
                        "data": self.test_data,
                        "analysis_types": analysis_types
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "analysis_results" in data
                assert "status" in data
    
    def test_optimize_weights_different_methods(self):
        """测试不同优化方法"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            optimization_methods = [
                "gradient_descent",
                "genetic_algorithm",
                "simulated_annealing",
                "particle_swarm",
                "bayesian",
                "comprehensive"
            ]
            
            for method in optimization_methods:
                response = self.client.post(
                    "/api/v1/models/optimize-weights",
                    json={
                        "data": self.test_data,
                        "optimization_method": method
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "optimization_results" in data
                assert "status" in data
    
    def test_optimize_weights_different_validation_methods(self):
        """测试不同验证方法"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            validation_methods_list = [
                ["cross_validation"],
                ["bootstrap"],
                ["time_series"],
                ["stability"],
                ["cross_validation", "bootstrap"],
                ["cross_validation", "bootstrap", "stability"]
            ]
            
            for validation_methods in validation_methods_list:
                response = self.client.post(
                    "/api/v1/models/optimize-weights",
                    json={
                        "data": self.test_data,
                        "optimization_method": "comprehensive",
                        "validation_methods": validation_methods
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "optimization_results" in data
                assert "status" in data
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            # 测试无效数据格式
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": "invalid_data",
                    "analysis_types": ["synergy"]
                }
            )
            
            # 应该返回500错误，因为数据格式无效
            assert response.status_code == 500
    
    def test_api_performance(self):
        """测试API性能"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            # 创建较大的数据集
            large_data = {
                "features": {
                    f"feature_{i}": np.random.normal(0, 1, 500).tolist()
                    for i in range(10)
                },
                "target": np.random.normal(0, 1, 500).tolist()
            }
            
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": large_data,
                    "analysis_types": ["synergy", "threshold"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis_results" in data
            assert "status" in data
    
    def test_api_workflow(self):
        """测试完整API工作流"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            # 1. 数据关系分析
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": self.test_data,
                    "analysis_types": ["synergy", "threshold", "lag", "advanced"]
                }
            )
            assert response.status_code == 200
            analysis_data = response.json()
            assert "analysis_results" in analysis_data
            
            # 2. 权重优化
            response = self.client.post(
                "/api/v1/models/optimize-weights",
                json={
                    "data": self.test_data,
                    "optimization_method": "comprehensive",
                    "validation_methods": ["cross_validation", "bootstrap"]
                }
            )
            assert response.status_code == 200
            optimization_data = response.json()
            assert "optimization_results" in optimization_data
            
            # 3. 使用优化后的权重进行预测
            test_data_with_test = {
                "features": self.test_data["features"],
                "target": self.test_data["target"],
                "test_features": {
                    "feature1": np.random.normal(0, 1, 20).tolist(),
                    "feature2": np.random.normal(0, 1, 20).tolist(),
                    "feature3": np.random.normal(0, 1, 20).tolist()
                }
            }
            
            response = self.client.post(
                "/api/v1/models/predict",
                json={
                    "data": test_data_with_test,
                    "weights": self.test_weights
                }
            )
            assert response.status_code == 200
            prediction_data = response.json()
            assert "predictions" in prediction_data
            
            # 4. 获取算法洞察
            response = self.client.get("/api/v1/models/insights")
            assert response.status_code == 200
            insights_data = response.json()
            assert "insights" in insights_data
            
            # 验证整个工作流的完整性
            assert analysis_data is not None
            assert optimization_data is not None
            assert prediction_data is not None
            assert insights_data is not None
    
    def test_api_authentication(self):
        """测试API认证"""
        # 测试未认证的请求
        response = self.client.post(
            "/api/v1/models/analyze",
            json={
                "data": self.test_data,
                "analysis_types": ["synergy"]
            }
        )
        
        # 应该返回401或403错误
        assert response.status_code in [401, 403, 500]
    
    def test_api_cors(self):
        """测试API CORS"""
        response = self.client.options("/api/v1/models/analyze")
        # CORS预检请求应该成功
        assert response.status_code in [200, 204]
    
    def test_api_content_type(self):
        """测试API内容类型"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": self.test_data,
                    "analysis_types": ["synergy"]
                }
            )
            
            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]
    
    def test_api_response_format(self):
        """测试API响应格式"""
        with patch('backend.src.api.endpoints.models.require_permission') as mock_auth:
            mock_auth.return_value = Mock()
            
            response = self.client.post(
                "/api/v1/models/analyze",
                json={
                    "data": self.test_data,
                    "analysis_types": ["synergy"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 检查响应格式
            assert isinstance(data, dict)
            assert "analysis_results" in data
            assert "status" in data
            assert data["status"] == "completed"
            
            # 检查分析结果格式
            analysis_results = data["analysis_results"]
            assert isinstance(analysis_results, dict)
            assert "synergy" in analysis_results
            assert "overall_score" in analysis_results


