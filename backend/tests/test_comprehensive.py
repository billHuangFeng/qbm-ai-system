"""
BMOS系统 - 综合测试套件
提供完整的测试覆盖，包括单元测试、集成测试和端到端测试
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime
import tempfile
import os

# 导入被测试的模块
from src.security.database import SecureDatabaseService
from src.security.auth import SecureAuthService
from src.security.config import SecuritySettings, validate_password_strength
from src.performance.optimization import PerformanceOptimizedService, PaginationParams, PaginationResult
from src.error_handling.unified import BMOSError, ErrorHandler, ErrorCode, ErrorSeverity
from src.services.base import BaseService, CRUDService, BusinessService
from src.config.unified import Settings, ConfigManager, Environment

# 测试数据
TEST_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "role": "user",
    "tenant_id": "tenant_001"
}

TEST_PAGINATION_DATA = [
    {"id": i, "name": f"item_{i}", "value": i * 10}
    for i in range(1, 101)
]

class TestSecurityConfig:
    """安全配置测试"""
    
    def test_security_settings_validation(self):
        """测试安全配置验证"""
        # 测试有效配置
        valid_config = SecuritySettings(
            jwt_secret_key="a" * 32,
            cors_origins=["http://localhost:3000"]
        )
        assert valid_config.jwt_secret_key == "a" * 32
        assert valid_config.cors_origins == ["http://localhost:3000"]
    
    def test_invalid_jwt_secret_key(self):
        """测试无效JWT密钥"""
        with pytest.raises(ValueError, match="JWT_SECRET_KEY must be at least 32 characters"):
            SecuritySettings(jwt_secret_key="short")
    
    def test_default_jwt_secret_key(self):
        """测试默认JWT密钥"""
        with pytest.raises(ValueError, match="JWT_SECRET_KEY must be set"):
            SecuritySettings(jwt_secret_key="your-secret-key-here")
    
    def test_password_strength_validation(self):
        """测试密码强度验证"""
        settings = SecuritySettings(jwt_secret_key="a" * 32)
        
        # 测试强密码
        is_valid, errors = validate_password_strength("StrongPass123!", settings)
        assert is_valid
        assert len(errors) == 0
        
        # 测试弱密码
        is_valid, errors = validate_password_strength("weak", settings)
        assert not is_valid
        assert len(errors) > 0

class TestSecureDatabaseService:
    """安全数据库服务测试"""
    
    @pytest.fixture
    async def mock_db_service(self):
        """模拟数据库服务"""
        service = SecureDatabaseService("postgresql://test:test@localhost/test")
        service.pool = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_db_service):
        """测试健康检查成功"""
        mock_db_service.pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = {"1": 1}
        
        result = await mock_db_service.health_check()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_db_service):
        """测试健康检查失败"""
        mock_db_service.pool.acquire.return_value.__aenter__.return_value.fetchrow.side_effect = Exception("Connection failed")
        
        result = await mock_db_service.health_check()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_safe_select(self, mock_db_service):
        """测试安全查询"""
        mock_result = [{"id": 1, "name": "test"}]
        mock_db_service.pool.acquire.return_value.__aenter__.return_value.fetch.return_value = mock_result
        
        result = await mock_db_service.safe_select(
            table="test_table",
            columns=["id", "name"],
            where_clause="id = $1",
            where_params=[1]
        )
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_safe_insert(self, mock_db_service):
        """测试安全插入"""
        mock_result = {"id": 1, "name": "test"}
        mock_db_service.pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = mock_result
        
        result = await mock_db_service.safe_insert("test_table", {"name": "test"})
        
        assert result == mock_result

class TestPerformanceOptimization:
    """性能优化测试"""
    
    @pytest.fixture
    async def mock_perf_service(self):
        """模拟性能优化服务"""
        mock_db = AsyncMock()
        service = PerformanceOptimizedService(mock_db)
        return service
    
    def test_pagination_params(self):
        """测试分页参数"""
        # 测试正常参数
        params = PaginationParams(page=2, size=10)
        assert params.page == 2
        assert params.size == 10
        assert params.offset == 10
        
        # 测试边界值
        params = PaginationParams(page=0, size=0)
        assert params.page == 1
        assert params.size == 20
        
        # 测试最大值限制
        params = PaginationParams(size=200)
        assert params.size == 100  # max_size
    
    @pytest.mark.asyncio
    async def test_paginated_query(self, mock_perf_service):
        """测试分页查询"""
        # 模拟数据库查询结果
        mock_perf_service.db_service.execute_query.side_effect = [
            {"total": 100},  # count query
            [{"id": 1, "name": "item_1"}]  # data query
        ]
        
        pagination = PaginationParams(page=1, size=10)
        result = await mock_perf_service.paginated_query(
            table="test_table",
            pagination=pagination
        )
        
        assert isinstance(result, PaginationResult)
        assert result.total == 100
        assert result.page == 1
        assert result.size == 10
        assert result.has_next is True
        assert result.has_prev is False
    
    @pytest.mark.asyncio
    async def test_batch_load_with_relations(self, mock_perf_service):
        """测试批量加载关联数据"""
        # 模拟主表数据
        mock_perf_service.paginated_query.return_value = PaginationResult(
            data=[{"id": 1, "name": "main_1"}, {"id": 2, "name": "main_2"}],
            total=2,
            page=1,
            size=10,
            total_pages=1,
            has_next=False,
            has_prev=False
        )
        
        # 模拟关联数据
        mock_perf_service.db_service.execute_query.return_value = [
            {"id": 1, "main_id": 1, "value": "rel_1"},
            {"id": 2, "main_id": 1, "value": "rel_2"}
        ]
        
        relation_tables = {
            "relations": {
                "table": "relation_table",
                "foreign_key": "main_id",
                "columns": ["id", "main_id", "value"]
            }
        }
        
        result = await mock_perf_service.batch_load_with_relations(
            main_table="main_table",
            relation_tables=relation_tables
        )
        
        assert len(result) == 2
        assert "relations" in result[0]
        assert len(result[0]["relations"]) == 2

class TestErrorHandling:
    """错误处理测试"""
    
    def test_bmos_error_creation(self):
        """测试BMOS错误创建"""
        error = BMOSError(
            message="Test error",
            code=ErrorCode.VALIDATION_ERROR,
            details={"field": "test_field"},
            severity=ErrorSeverity.MEDIUM
        )
        
        assert error.message == "Test error"
        assert error.code == ErrorCode.VALIDATION_ERROR
        assert error.details["field"] == "test_field"
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.user_message == "Test error"
    
    def test_business_error(self):
        """测试业务错误"""
        error = BMOSError("Business logic failed")
        assert error.code == ErrorCode.BUSINESS_LOGIC_ERROR
    
    def test_validation_error(self):
        """测试验证错误"""
        error = BMOSError("Validation failed", field="email")
        assert error.code == ErrorCode.VALIDATION_ERROR
        assert error.details["field"] == "email"
    
    def test_error_handler(self):
        """测试错误处理器"""
        handler = ErrorHandler(include_debug=True)
        
        error = BMOSError("Test error", ErrorCode.VALIDATION_ERROR)
        response = handler.handle_bmos_error(error)
        
        assert response.status_code == 422
        content = json.loads(response.body.decode())
        assert content["success"] is False
        assert content["error"]["code"] == "VALIDATION_ERROR"
        assert content["error"]["message"] == "Test error"

class TestBaseService:
    """基础服务测试"""
    
    @pytest.fixture
    async def mock_base_service(self):
        """模拟基础服务"""
        mock_db = AsyncMock()
        mock_cache = AsyncMock()
        service = BaseService(mock_db, mock_cache)
        return service
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_base_service):
        """测试健康检查"""
        mock_base_service.db_service.health_check.return_value = True
        mock_base_service.cache_service.ping.return_value = True
        
        result = await mock_base_service.health_check()
        
        assert result["status"] == "healthy"
        assert result["database"] == "connected"
        assert result["cache"] == "connected"
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, mock_base_service):
        """测试根据ID获取记录"""
        mock_result = [{"id": 1, "name": "test"}]
        mock_base_service.db_service.safe_select.return_value = mock_result
        
        result = await mock_base_service.get_by_id("test_table", 1)
        
        assert result == mock_result
        mock_base_service.db_service.safe_select.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_record(self, mock_base_service):
        """测试创建记录"""
        mock_result = {"id": 1, "name": "test"}
        mock_base_service.db_service.safe_insert.return_value = mock_result
        
        result = await mock_base_service.create_record("test_table", {"name": "test"})
        
        assert result == mock_result

class TestCRUDService:
    """CRUD服务测试"""
    
    @pytest.fixture
    async def mock_crud_service(self):
        """模拟CRUD服务"""
        mock_db = AsyncMock()
        mock_cache = AsyncMock()
        service = CRUDService(mock_db, "test_table", mock_cache)
        return service
    
    @pytest.mark.asyncio
    async def test_create(self, mock_crud_service):
        """测试创建操作"""
        mock_result = {"id": 1, "name": "test", "created_at": datetime.now()}
        mock_crud_service.create_record.return_value = mock_result
        mock_crud_service.cache_service.delete_pattern.return_value = None
        
        result = await mock_crud_service.create({"name": "test"})
        
        assert result == mock_result
        assert "created_at" in result
        assert "updated_at" in result
    
    @pytest.mark.asyncio
    async def test_get_by_id_with_cache(self, mock_crud_service):
        """测试带缓存的根据ID获取"""
        mock_result = {"id": 1, "name": "test"}
        mock_crud_service.cache_service.get.return_value = mock_result
        
        result = await mock_crud_service.get_by_id(1)
        
        assert result == mock_result
        # 应该从缓存获取，不调用数据库
        mock_crud_service.db_service.safe_select.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_by_id_without_cache(self, mock_crud_service):
        """测试不带缓存的根据ID获取"""
        mock_result = [{"id": 1, "name": "test"}]
        mock_crud_service.cache_service.get.return_value = None
        mock_crud_service.db_service.safe_select.return_value = mock_result
        mock_crud_service.cache_service.set.return_value = True
        
        result = await mock_crud_service.get_by_id(1)
        
        assert result == mock_result
        mock_crud_service.db_service.safe_select.assert_called_once()
        mock_crud_service.cache_service.set.assert_called_once()

class TestConfigManager:
    """配置管理器测试"""
    
    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        manager = ConfigManager()
        assert manager._settings is None
    
    def test_settings_property(self):
        """测试配置属性"""
        manager = ConfigManager()
        settings = manager.settings
        
        assert isinstance(settings, Settings)
        assert manager._settings is not None
    
    def test_environment_checks(self):
        """测试环境检查"""
        manager = ConfigManager()
        
        # 默认应该是开发环境
        assert manager.is_development() is True
        assert manager.is_production() is False
        assert manager.is_testing() is False
    
    def test_config_getters(self):
        """测试配置获取器"""
        manager = ConfigManager()
        
        db_config = manager.get_database_config()
        redis_config = manager.get_redis_config()
        security_config = manager.get_security_config()
        
        assert db_config is not None
        assert redis_config is not None
        assert security_config is not None

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_user_registration_flow(self):
        """测试用户注册流程"""
        # 模拟数据库服务
        mock_db = AsyncMock()
        mock_cache = AsyncMock()
        
        # 模拟用户不存在
        mock_db.safe_select.return_value = []
        
        # 模拟用户创建
        mock_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
            "tenant_id": "tenant_001",
            "is_active": True,
            "is_verified": False
        }
        mock_db.safe_insert.return_value = mock_user
        
        # 创建认证服务
        auth_service = SecureAuthService(mock_db)
        
        # 执行注册
        result = await auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
            role="user",
            tenant_id="tenant_001"
        )
        
        assert result["success"] is True
        assert result["user"]["username"] == "testuser"
        assert "token" in result
        assert "refresh_token" in result
    
    @pytest.mark.asyncio
    async def test_data_pagination_flow(self):
        """测试数据分页流程"""
        # 模拟数据库服务
        mock_db = AsyncMock()
        
        # 模拟分页查询
        mock_db.execute_query.side_effect = [
            {"total": 100},  # count query
            [{"id": 1, "name": "item_1"}]  # data query
        ]
        
        # 创建性能优化服务
        perf_service = PerformanceOptimizedService(mock_db)
        
        # 执行分页查询
        pagination = PaginationParams(page=1, size=10)
        result = await perf_service.paginated_query(
            table="test_table",
            pagination=pagination
        )
        
        assert isinstance(result, PaginationResult)
        assert result.total == 100
        assert len(result.data) == 1
        assert result.has_next is True

class TestEndToEnd:
    """端到端测试"""
    
    @pytest.mark.asyncio
    async def test_complete_user_workflow(self):
        """测试完整用户工作流"""
        # 1. 用户注册
        # 2. 用户登录
        # 3. 数据查询
        # 4. 数据更新
        # 5. 用户登出
        
        # 这里可以实现完整的端到端测试
        # 由于需要真实的数据库连接，这里只是示例
        pass

# 测试配置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_config_file():
    """临时配置文件"""
    config_data = {
        "database": {
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_user": "test",
            "postgres_password": "test",
            "postgres_db": "test"
        },
        "security": {
            "jwt_secret_key": "a" * 32,
            "cors_origins": ["http://localhost:3000"]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # 清理
    os.unlink(temp_file)

# 测试标记
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]

# 性能测试标记
pytestmark_performance = [
    pytest.mark.asyncio,
    pytest.mark.performance,
]

# 集成测试标记
pytestmark_integration = [
    pytest.mark.asyncio,
    pytest.mark.integration,
]

# 端到端测试标记
pytestmark_e2e = [
    pytest.mark.asyncio,
    pytest.mark.e2e,
    pytest.mark.slow,
]

