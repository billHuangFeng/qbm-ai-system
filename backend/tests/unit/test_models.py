"""
数据模型单元测试
"""

import pytest
from datetime import datetime
from src.models.historical_data import HistoricalData
from src.models.base import BaseModel


class TestBaseModel:
    """测试基础模型"""

    def test_base_model_creation(self):
        """测试基础模型创建"""
        # 这里需要实际的数据库连接，暂时跳过
        pass


class TestHistoricalData:
    """测试历史数据模型"""

    def test_historical_data_creation(self):
        """测试历史数据创建"""
        # 创建测试数据
        data = HistoricalData(
            tenant_id="test_tenant",
            data_type="asset",
            data_date=datetime.now(),
            period_type="monthly",
        )

        # 验证基础字段
        assert data.tenant_id == "test_tenant"
        assert data.data_type == "asset"
        assert data.period_type == "monthly"
        assert data.data_id is not None  # 应该自动生成UUID

    def test_data_quality_validation(self):
        """测试数据质量验证"""
        data = HistoricalData(
            tenant_id="test_tenant",
            data_type="asset",
            data_date=datetime.now(),
            period_type="monthly",
            rd_asset=1000.0,
            design_asset=2000.0,
        )

        score = data.validate_data_quality()
        assert 0.0 <= score <= 1.0
        assert data.data_quality_score == score

    def test_data_quality_with_negative_values(self):
        """测试负值数据质量验证"""
        data = HistoricalData(
            tenant_id="test_tenant",
            data_type="asset",
            data_date=datetime.now(),
            period_type="monthly",
            rd_asset=-100.0,  # 负值
            design_asset=2000.0,
        )

        score = data.validate_data_quality()
        assert score < 1.0  # 应该因为负值而降低分数

    def test_to_dict_method(self):
        """测试转换为字典方法"""
        data = HistoricalData(
            tenant_id="test_tenant",
            data_type="asset",
            data_date=datetime.now(),
            period_type="monthly",
        )

        data_dict = data.to_dict()
        assert isinstance(data_dict, dict)
        assert "tenant_id" in data_dict
        assert "data_type" in data_dict
        assert "created_at" in data_dict
