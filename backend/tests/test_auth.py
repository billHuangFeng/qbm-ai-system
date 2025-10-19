import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.models.user import User
from app.database import get_db
from sqlalchemy.orm import Session

client = TestClient(app)

def test_login_success():
    """测试成功登录"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """测试无效凭据登录"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_register_user():
    """测试用户注册"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_current_user():
    """测试获取当前用户信息"""
    # 创建测试token
    token = create_access_token(data={"sub": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data

def test_change_password():
    """测试修改密码"""
    token = create_access_token(data={"sub": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        "/api/v1/auth/change-password",
        json={
            "old_password": "admin123",
            "new_password": "newpassword123"
        },
        headers=headers
    )
    assert response.status_code == 200



