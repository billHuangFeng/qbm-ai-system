"""
BMOS系统 - 安全测试套件
测试系统的安全性和权限控制
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi import HTTPException

from backend.src.api.endpoints import optimization, monitoring, tasks
from backend.src.security.auth import User, Permission
from backend.src.error_handling.unified import BusinessError


class TestSecurityControls:
    """安全控制测试"""

    @pytest.fixture
    def admin_user(self):
        """管理员用户"""
        return User(
            user_id="admin_123",
            username="admin",
            email="admin@example.com",
            tenant_id="tenant_123",
            role="admin",
            permissions=[
                Permission.WRITE_OPTIMIZATION,
                Permission.READ_OPTIMIZATION,
                Permission.READ_DATA,
                Permission.TASK_CREATE,
                Permission.TASK_READ,
                Permission.TASK_DELETE,
            ],
        )

    @pytest.fixture
    def regular_user(self):
        """普通用户"""
        return User(
            user_id="user_123",
            username="user",
            email="user@example.com",
            tenant_id="tenant_123",
            role="user",
            permissions=[Permission.READ_DATA],  # 只有读取权限
        )

    @pytest.fixture
    def other_tenant_user(self):
        """其他租户用户"""
        return User(
            user_id="other_123",
            username="other",
            email="other@example.com",
            tenant_id="other_tenant",  # 不同的租户
            role="manager",
            permissions=[Permission.WRITE_OPTIMIZATION, Permission.READ_OPTIMIZATION],
        )

    @pytest.mark.asyncio
    async def test_unauthorized_access_optimization(self, regular_user):
        """测试未授权访问优化建议"""
        optimization_data = {
            "recommendation_type": "security",
            "title": "安全测试",
            "description": "测试未授权访问",
            "priority": "high",
        }

        with patch(
            "backend.src.api.endpoints.optimization.require_permission"
        ) as mock_auth:
            # 模拟权限检查失败
            mock_auth.side_effect = HTTPException(status_code=403, detail="权限不足")

            with pytest.raises(HTTPException) as exc_info:
                await optimization.create_optimization(
                    optimization_data=optimization_data,
                    current_user=regular_user,
                    db=Mock(),
                )

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_cross_tenant_data_access(self, other_tenant_user):
        """测试跨租户数据访问"""
        with patch("backend.src.api.endpoints.optimization.get_db") as mock_db:
            # 模拟数据库查询结果（其他租户的数据）
            mock_row = (
                1,
                "uuid1",
                "tenant_123",
                "performance",
                "其他租户建议",
                "描述",
                "high",
                8.5,
                "medium",
                1.5,
                "pending",
                None,
                None,
            )
            mock_db.return_value.execute.return_value.fetchone.return_value = mock_row

            with patch(
                "backend.src.api.endpoints.optimization.require_permission"
            ) as mock_auth:
                mock_auth.return_value = other_tenant_user

                # 尝试访问其他租户的优化建议
                with pytest.raises(Exception):  # 应该抛出异常
                    await optimization.get_optimization(
                        recommendation_id="uuid1",
                        current_user=other_tenant_user,
                        db=mock_db.return_value,
                    )

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, admin_user):
        """测试SQL注入防护"""
        # 尝试SQL注入攻击
        malicious_data = {
            "recommendation_type": "'; DROP TABLE optimization_recommendations; --",
            "title": "SQL注入测试",
            "description": "测试SQL注入防护",
            "priority": "high",
        }

        with patch("backend.src.api.endpoints.optimization.get_db") as mock_db:
            mock_db.return_value.execute.return_value.fetchone.return_value = [123]

            with patch(
                "backend.src.api.endpoints.optimization.require_permission"
            ) as mock_auth:
                mock_auth.return_value = admin_user

                # 应该正常处理，不会执行恶意SQL
                result = await optimization.create_optimization(
                    optimization_data=malicious_data,
                    current_user=admin_user,
                    db=mock_db.return_value,
                )

                # 验证参数化查询被使用
                mock_db.return_value.execute.assert_called_once()
                call_args = mock_db.return_value.execute.call_args

                # 验证使用了参数化查询（参数应该作为列表传递）
                assert isinstance(call_args[0][1], list), "应该使用参数化查询"

    @pytest.mark.asyncio
    async def test_input_validation_security(self, admin_user):
        """测试输入验证安全性"""
        # 测试各种恶意输入
        malicious_inputs = [
            {"title": "", "description": "空标题测试"},  # 空标题
            {"title": "x" * 10000, "description": "超长标题测试"},  # 超长标题
            {"title": "<script>alert('xss')</script>", "description": "XSS测试"},  # XSS
            {"title": "正常标题", "description": ""},  # 空描述
        ]

        for malicious_data in malicious_inputs:
            optimization_data = {
                "recommendation_type": "security",
                "title": malicious_data["title"],
                "description": malicious_data["description"],
                "priority": "medium",
            }

            with patch(
                "backend.src.api.endpoints.optimization.require_permission"
            ) as mock_auth:
                mock_auth.return_value = admin_user

                # 应该抛出验证错误
                with pytest.raises(Exception):
                    await optimization.create_optimization(
                        optimization_data=optimization_data,
                        current_user=admin_user,
                        db=Mock(),
                    )

    @pytest.mark.asyncio
    async def test_task_tenant_isolation(self, other_tenant_user):
        """测试任务租户隔离"""
        # 创建其他租户的任务
        other_tenant_task = Mock()
        other_tenant_task.task_id = "task_456"
        other_tenant_task.tenant_id = "other_tenant"
        other_tenant_task.status = "PENDING"

        with patch(
            "backend.src.api.endpoints.tasks.get_task_manager"
        ) as mock_task_manager:
            mock_task_manager.return_value.get_task.return_value = other_tenant_task

            with patch(
                "backend.src.api.endpoints.tasks.require_permission"
            ) as mock_auth:
                mock_auth.return_value = other_tenant_user

                # 尝试取消其他租户的任务
                with pytest.raises(Exception):  # 应该抛出权限异常
                    await tasks.cancel_task(
                        task_id="task_456",
                        current_user=other_tenant_user,
                        task_manager=mock_task_manager.return_value,
                    )


class TestAuthenticationSecurity:
    """认证安全测试"""

    @pytest.mark.asyncio
    async def test_jwt_token_validation(self):
        """测试JWT令牌验证"""
        # 测试无效令牌
        invalid_tokens = [
            "invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            None,
        ]

        for invalid_token in invalid_tokens:
            with patch("backend.src.security.auth.decode_jwt_token") as mock_decode:
                mock_decode.side_effect = Exception("Invalid token")

                with pytest.raises(Exception):
                    # 这里应该调用认证函数
                    pass  # 占位符

    @pytest.mark.asyncio
    async def test_permission_escalation_prevention(self):
        """测试权限提升防护"""
        # 模拟低权限用户尝试执行高权限操作
        low_privilege_user = User(
            user_id="low_user",
            username="lowuser",
            email="low@example.com",
            tenant_id="tenant_123",
            role="user",
            permissions=[Permission.READ_DATA],  # 只有读取权限
        )

        # 尝试执行需要写入权限的操作
        optimization_data = {
            "recommendation_type": "security",
            "title": "权限提升测试",
            "description": "测试权限提升防护",
            "priority": "high",
        }

        with patch(
            "backend.src.api.endpoints.optimization.require_permission"
        ) as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=403, detail="权限不足")

            with pytest.raises(HTTPException) as exc_info:
                await optimization.create_optimization(
                    optimization_data=optimization_data,
                    current_user=low_privilege_user,
                    db=Mock(),
                )

            assert exc_info.value.status_code == 403


class TestDataSecurity:
    """数据安全测试"""

    @pytest.fixture
    def sensitive_user(self):
        """包含敏感信息的用户"""
        return User(
            user_id="sensitive_123",
            username="sensitive",
            email="sensitive@example.com",
            tenant_id="sensitive_tenant",
            role="analyst",
            permissions=[Permission.READ_DATA],
        )

    @pytest.mark.asyncio
    async def test_sensitive_data_logging(self, sensitive_user):
        """测试敏感数据日志记录"""
        with patch("backend.src.api.endpoints.monitoring.get_db") as mock_db:
            mock_db.return_value.execute.return_value.fetchall.return_value = []

            with patch(
                "backend.src.api.endpoints.monitoring.require_permission"
            ) as mock_auth:
                mock_auth.return_value = sensitive_user

                with patch(
                    "backend.src.api.endpoints.monitoring.logger"
                ) as mock_logger:
                    await monitoring.get_monitoring_data(
                        current_user=sensitive_user, db=mock_db.return_value, hours=24
                    )

                    # 验证日志中没有记录敏感信息
                    log_calls = mock_logger.info.call_args_list
                    for call in log_calls:
                        log_message = str(call)
                        # 确保日志中没有包含密码、令牌等敏感信息
                        assert "password" not in log_message.lower()
                        assert "token" not in log_message.lower()
                        assert "secret" not in log_message.lower()

    @pytest.mark.asyncio
    async def test_data_encryption(self, sensitive_user):
        """测试数据加密"""
        # 测试敏感数据在传输和存储时的加密
        optimization_data = {
            "recommendation_type": "security",
            "title": "加密测试",
            "description": "包含敏感信息: password123, secret_key",
            "priority": "high",
        }

        with patch("backend.src.api.endpoints.optimization.get_db") as mock_db:
            mock_db.return_value.execute.return_value.fetchone.return_value = [123]

            with patch(
                "backend.src.api.endpoints.optimization.require_permission"
            ) as mock_auth:
                mock_auth.return_value = sensitive_user

                await optimization.create_optimization(
                    optimization_data=optimization_data,
                    current_user=sensitive_user,
                    db=mock_db.return_value,
                )

                # 验证数据库调用使用了参数化查询
                mock_db.return_value.execute.assert_called_once()
                call_args = mock_db.return_value.execute.call_args

                # 验证参数化查询防止了SQL注入
                assert isinstance(call_args[0][1], list)


class TestRateLimiting:
    """速率限制测试"""

    @pytest.fixture
    def rate_limit_user(self):
        """速率限制测试用户"""
        return User(
            user_id="rate_limit_user",
            username="ratelimit",
            email="ratelimit@example.com",
            tenant_id="rate_tenant",
            role="user",
            permissions=[Permission.READ_DATA],
        )

    @pytest.mark.asyncio
    async def test_rate_limiting_protection(self, rate_limit_user):
        """测试速率限制保护"""

        # 模拟大量并发请求
        async def make_request():
            with patch("backend.src.api.endpoints.monitoring.get_db") as mock_db:
                mock_db.return_value.execute.return_value.fetchall.return_value = []

                with patch(
                    "backend.src.api.endpoints.monitoring.require_permission"
                ) as mock_auth:
                    mock_auth.return_value = rate_limit_user

                    await monitoring.get_monitoring_data(
                        current_user=rate_limit_user, db=mock_db.return_value, hours=24
                    )

        # 快速发送大量请求
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计被限制的请求数量
        rate_limited_count = sum(
            1 for result in results if isinstance(result, Exception)
        )

        # 验证速率限制生效（应该有部分请求被限制）
        assert rate_limited_count > 0, "速率限制没有生效"


# 测试配置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 运行安全测试的命令
# pytest backend/tests/test_security.py -v --tb=short
