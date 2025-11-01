"""
BMOS系统 - 基础pytest测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """测试基本导入"""
    from fastapi import FastAPI
    import asyncio
    from unittest.mock import Mock
    
    assert FastAPI is not None
    assert asyncio is not None
    assert Mock is not None

def test_fastapi_app():
    """测试FastAPI应用创建"""
    from fastapi import FastAPI
    
    app = FastAPI(title="BMOS Test")
    assert app.title == "BMOS Test"

def test_mock_creation():
    """测试Mock对象创建"""
    from unittest.mock import Mock
    
    mock_user = Mock()
    mock_user.tenant_id = "test_tenant"
    mock_user.username = "testuser"
    
    assert mock_user.tenant_id == "test_tenant"
    assert mock_user.username == "testuser"

def test_async_function():
    """测试异步函数"""
    import asyncio
    
    async def test_async():
        return "async test result"
    
    result = asyncio.run(test_async())
    assert result == "async test result"

@pytest.mark.asyncio
async def test_async_with_pytest():
    """使用pytest-asyncio测试异步函数"""
    async def async_task():
        return "pytest async test"
    
    result = await async_task()
    assert result == "pytest async test"

def test_project_files_exist():
    """测试项目文件存在"""
    test_files = [
        "tests/test_api_endpoints.py",
        "tests/test_performance.py", 
        "tests/test_security.py"
    ]
    
    for file_path in test_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"文件不存在: {file_path}"

def test_project_dirs_exist():
    """测试项目目录存在"""
    test_dirs = [
        "src",
        "tests",
        "src/api",
        "src/api/endpoints"
    ]
    
    for dir_path in test_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"目录不存在: {dir_path}"
