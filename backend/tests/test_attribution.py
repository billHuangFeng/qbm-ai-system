"""
Shapley归因API端点测试
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, List
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)


class TestShapleyAttribution:
    """Shapley归因端点测试"""
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/attribution/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "attribution"
    
    def test_shapley_attribution_single_touchpoint(self):
        """测试单触点归因"""
        request_data = {
            "order_id": "order-001",
            "touchpoints": [
                {
                    "id": "tp-001",
                    "type": "media",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "cost": 100.0
                }
            ],
            "conversion_value": 1000.0,
            "method": "exact"
        }
        
        response = client.post("/attribution/shapley", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_id"] == "order-001"
        assert "attribution" in data
        assert "tp-001" in data["attribution"]
        assert data["attribution"]["tp-001"] == 1.0  # 单触点应该是100%
        assert data["touchpoint_count"] == 1
        assert data["method"] == "exact"
    
    def test_shapley_attribution_multiple_touchpoints(self):
        """测试多触点归因（使用蒙特卡洛方法）"""
        request_data = {
            "order_id": "order-002",
            "touchpoints": [
                {
                    "id": "tp-001",
                    "type": "media",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "cost": 100.0
                },
                {
                    "id": "tp-002",
                    "type": "channel",
                    "timestamp": "2024-01-02T14:00:00Z",
                    "cost": 50.0
                },
                {
                    "id": "tp-003",
                    "type": "campaign",
                    "timestamp": "2024-01-03T16:00:00Z",
                    "cost": 200.0
                }
            ],
            "conversion_value": 1000.0,
            "method": "monte_carlo"
        }
        
        response = client.post("/attribution/shapley", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_id"] == "order-002"
        assert "attribution" in data
        assert len(data["attribution"]) == 3
        
        # 验证归因权重总和接近1.0
        total_weight = sum(data["attribution"].values())
        assert abs(total_weight - 1.0) < 0.01  # 允许小的浮点误差
        
        # 验证所有触点都有权重
        assert "tp-001" in data["attribution"]
        assert "tp-002" in data["attribution"]
        assert "tp-003" in data["attribution"]
        
        # 验证权重都是正数
        for weight in data["attribution"].values():
            assert weight >= 0
            assert weight <= 1
    
    def test_shapley_attribution_small_exact(self):
        """测试小规模完全枚举方法（n <= 10）"""
        request_data = {
            "order_id": "order-003",
            "touchpoints": [
                {
                    "id": f"tp-{i:03d}",
                    "type": "media",
                    "timestamp": f"2024-01-{i:02d}T10:00:00Z",
                    "cost": float(i * 10)
                }
                for i in range(1, 6)  # 5个触点
            ],
            "conversion_value": 1000.0,
            "method": "exact"
        }
        
        response = client.post("/attribution/shapley", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_id"] == "order-003"
        assert len(data["attribution"]) == 5
        
        # 验证归因权重总和接近1.0
        total_weight = sum(data["attribution"].values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_shapley_attribution_large_monte_carlo(self):
        """测试大规模蒙特卡洛方法（n > 10）"""
        request_data = {
            "order_id": "order-004",
            "touchpoints": [
                {
                    "id": f"tp-{i:03d}",
                    "type": "media",
                    "timestamp": f"2024-01-{i%28+1:02d}T10:00:00Z",
                    "cost": float(i * 10)
                }
                for i in range(1, 16)  # 15个触点，使用蒙特卡洛
            ],
            "conversion_value": 5000.0,
            "method": "monte_carlo"
        }
        
        response = client.post("/attribution/shapley", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_id"] == "order-004"
        assert len(data["attribution"]) == 15
        
        # 验证归因权重总和接近1.0
        total_weight = sum(data["attribution"].values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_shapley_attribution_empty_touchpoints(self):
        """测试空触点列表"""
        request_data = {
            "order_id": "order-005",
            "touchpoints": [],
            "conversion_value": 1000.0
        }
        
        response = client.post("/attribution/shapley", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_id"] == "order-005"
        assert data["attribution"] == {}
        assert data["touchpoint_count"] == 0
    
    def test_batch_shapley_attribution(self):
        """测试批量归因"""
        request_data = {
            "orders": [
                {
                    "order_id": "order-batch-001",
                    "customer_id": "cust-001",
                    "amount": 1000.0
                },
                {
                    "order_id": "order-batch-002",
                    "customer_id": "cust-002",
                    "amount": 2000.0
                }
            ],
            "touchpoint_journey": {
                "order-batch-001": [
                    {
                        "id": "tp-batch-001-1",
                        "type": "media",
                        "timestamp": "2024-01-01T10:00:00Z",
                        "cost": 100.0
                    },
                    {
                        "id": "tp-batch-001-2",
                        "type": "channel",
                        "timestamp": "2024-01-02T14:00:00Z",
                        "cost": 50.0
                    }
                ],
                "order-batch-002": [
                    {
                        "id": "tp-batch-002-1",
                        "type": "media",
                        "timestamp": "2024-01-01T10:00:00Z",
                        "cost": 200.0
                    }
                ]
            }
        }
        
        response = client.post("/attribution/shapley/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "order-batch-001" in data["results"]
        assert "order-batch-002" in data["results"]
        
        # 验证第一个订单的归因
        order1_attribution = data["results"]["order-batch-001"]
        assert len(order1_attribution) == 2
        total_weight = sum(order1_attribution.values())
        assert abs(total_weight - 1.0) < 0.01
        
        # 验证第二个订单的归因（单触点）
        order2_attribution = data["results"]["order-batch-002"]
        assert len(order2_attribution) == 1
        assert sum(order2_attribution.values()) == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

