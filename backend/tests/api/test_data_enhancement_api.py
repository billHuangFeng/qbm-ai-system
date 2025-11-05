"""
BMOS系统 - 数据增强API测试
测试字段映射推荐、表结构获取、可用表列表、映射历史保存等API端点
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import json


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.main_optimized import app

    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """获取认证Token（模拟）"""
    # 这里应该使用实际的认证逻辑获取Token
    # 为了测试，可以使用mock token
    return "mock_jwt_token"


@pytest.fixture
def headers(auth_token):
    """创建请求头"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestRecommendFieldMappings:
    """测试字段映射推荐API"""

    def test_recommend_field_mappings_success(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试字段映射推荐成功"""
        response = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": ["订单号", "客户名称", "订单日期"],
                "target_table": "sales_order_header",
                "source_system": "ERP_SYSTEM_A",
                "document_type": "SO",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

        # 验证推荐结果格式
        recommendation = data["recommendations"][0]
        assert "source_field" in recommendation
        assert "recommended_target" in recommendation
        assert "candidates" in recommendation

    def test_recommend_field_mappings_missing_target_table(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试缺少target_table参数"""
        response = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": ["订单号", "客户名称"],
                "source_system": "ERP_SYSTEM_A",
            },
        )

        assert response.status_code == 422  # 参数验证错误

    def test_recommend_field_mappings_invalid_table(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试无效的目标表"""
        response = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": ["订单号", "客户名称"],
                "target_table": "non_existent_table",
                "source_system": "ERP_SYSTEM_A",
            },
        )

        assert response.status_code in [400, 500]
        data = response.json()
        assert "detail" in data


class TestGetTableSchema:
    """测试获取表结构API"""

    def test_get_table_schema_success(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试获取表结构成功"""
        response = client.get(
            "/api/v1/data-enhancement/table-schema/sales_order_header?document_type=SO",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["table_name"] == "sales_order_header"
        assert "fields" in data
        assert len(data["fields"]) > 0
        assert "master_data_fields" in data
        assert "field_types" in data

        # 验证字段格式
        field = data["fields"][0]
        assert "name" in field
        assert "type" in field
        assert "nullable" in field

    def test_get_table_schema_not_found(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试表不存在"""
        response = client.get(
            "/api/v1/data-enhancement/table-schema/non_existent_table", headers=headers
        )

        assert response.status_code in [400, 404, 500]
        data = response.json()
        assert "detail" in data


class TestGetAvailableTables:
    """测试获取可用表列表API"""

    def test_get_available_tables_success(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试获取可用表列表成功"""
        response = client.get(
            "/api/v1/data-enhancement/available-tables", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tables" in data
        assert len(data["tables"]) > 0
        assert "categories" in data

        # 验证表格式
        table = data["tables"][0]
        assert "table_name" in table
        assert "display_name" in table
        assert "category" in table

    def test_get_available_tables_filtered_by_document_type(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试根据单据类型过滤表列表"""
        response = client.get(
            "/api/v1/data-enhancement/available-tables?document_type=SO",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 验证所有表都是SO类型
        for table in data["tables"]:
            if table.get("document_type"):
                assert table["document_type"] == "SO"


class TestSaveMappingHistory:
    """测试保存映射历史API"""

    def test_save_mapping_history_success(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试保存映射历史成功"""
        response = client.post(
            "/api/v1/data-enhancement/save-mapping-history",
            headers=headers,
            json={
                "source_system": "ERP_SYSTEM_A",
                "target_table": "sales_order_header",
                "source_field": "订单号",
                "target_field": "order_number",
                "document_type": "SO",
                "mapping_method": "manual",
                "confidence_score": 1.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mapping_id" in data

    def test_save_mapping_history_missing_required_fields(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试缺少必需字段"""
        response = client.post(
            "/api/v1/data-enhancement/save-mapping-history",
            headers=headers,
            json={
                "source_system": "ERP_SYSTEM_A",
                # 缺少target_table等必需字段
            },
        )

        assert response.status_code == 422  # 参数验证错误


class TestFieldMappingIntegration:
    """测试字段映射集成流程"""

    def test_complete_field_mapping_flow(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试完整的字段映射流程"""
        # 1. 获取可用表列表
        tables_response = client.get(
            "/api/v1/data-enhancement/available-tables?document_type=SO",
            headers=headers,
        )
        assert tables_response.status_code == 200
        tables = tables_response.json()["tables"]
        assert len(tables) > 0

        # 2. 选择目标表
        target_table = "sales_order_header"

        # 3. 获取表结构
        schema_response = client.get(
            f"/api/v1/data-enhancement/table-schema/{target_table}?document_type=SO",
            headers=headers,
        )
        assert schema_response.status_code == 200
        schema = schema_response.json()
        assert len(schema["fields"]) > 0

        # 4. 获取字段映射推荐
        mapping_response = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": ["订单号", "客户名称", "订单日期"],
                "target_table": target_table,
                "source_system": "ERP_SYSTEM_A",
                "document_type": "SO",
            },
        )
        assert mapping_response.status_code == 200
        recommendations = mapping_response.json()["recommendations"]
        assert len(recommendations) > 0

        # 5. 保存映射历史
        save_response = client.post(
            "/api/v1/data-enhancement/save-mapping-history",
            headers=headers,
            json={
                "source_system": "ERP_SYSTEM_A",
                "target_table": target_table,
                "source_field": "订单号",
                "target_field": "order_number",
                "document_type": "SO",
                "mapping_method": "manual",
                "confidence_score": 1.0,
            },
        )
        assert save_response.status_code == 200

        # 6. 再次获取推荐（验证历史学习效果）
        mapping_response2 = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": ["订单号", "客户名称"],
                "target_table": target_table,
                "source_system": "ERP_SYSTEM_A",
                "document_type": "SO",
            },
        )
        assert mapping_response2.status_code == 200
        recommendations2 = mapping_response2.json()["recommendations"]

        # 验证历史映射的置信度更高
        order_no_rec = next(
            (r for r in recommendations2 if r["source_field"] == "订单号"), None
        )
        if order_no_rec:
            # 历史映射应该有更高的置信度
            history_candidate = next(
                (c for c in order_no_rec["candidates"] if c["method"] == "history"),
                None,
            )
            if history_candidate:
                assert history_candidate["confidence"] >= 0.85


class TestPerformance:
    """测试性能要求"""

    def test_recommend_field_mappings_performance(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试字段映射推荐响应时间"""
        import time

        start_time = time.time()
        response = client.post(
            "/api/v1/data-enhancement/recommend-field-mappings",
            headers=headers,
            json={
                "source_fields": [
                    "订单号",
                    "客户名称",
                    "订单日期",
                    "产品代码",
                    "数量",
                    "单价",
                ],
                "target_table": "sales_order_header",
                "source_system": "ERP_SYSTEM_A",
                "document_type": "SO",
            },
        )
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # 转换为毫秒

        assert response.status_code == 200
        # 首次查询应该在500ms内
        assert duration < 500, f"响应时间过长: {duration}ms"

    def test_get_table_schema_performance(
        self, client: TestClient, headers: Dict[str, str]
    ):
        """测试获取表结构响应时间"""
        import time

        start_time = time.time()
        response = client.get(
            "/api/v1/data-enhancement/table-schema/sales_order_header", headers=headers
        )
        end_time = time.time()
        duration = (end_time - start_time) * 1000

        assert response.status_code == 200
        # 首次查询应该在200ms内
        assert duration < 200, f"响应时间过长: {duration}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
