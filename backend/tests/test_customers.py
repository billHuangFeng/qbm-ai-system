import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """创建认证头"""
    token = create_access_token(data={"sub": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_get_customers(auth_headers):
    """测试获取客户列表"""
    response = client.get("/api/v1/customers/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data

def test_create_customer(auth_headers):
    """测试创建客户"""
    customer_data = {
        "name": "测试客户",
        "contact_person": "张三",
        "contact_email": "zhangsan@example.com",
        "contact_phone": "13800138001",
        "industry": "科技",
        "region": "北京",
        "address": "北京市朝阳区",
        "description": "测试客户描述"
    }
    
    response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["contact_person"] == customer_data["contact_person"]

def test_get_customer(auth_headers):
    """测试获取单个客户"""
    # 先创建一个客户
    customer_data = {
        "name": "测试客户2",
        "contact_person": "李四",
        "contact_email": "lisi@example.com",
        "contact_phone": "13800138002",
        "industry": "金融",
        "region": "上海"
    }
    
    create_response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers=auth_headers
    )
    customer_id = create_response.json()["id"]
    
    # 获取客户信息
    response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]

def test_update_customer(auth_headers):
    """测试更新客户"""
    # 先创建一个客户
    customer_data = {
        "name": "测试客户3",
        "contact_person": "王五",
        "contact_email": "wangwu@example.com",
        "contact_phone": "13800138003",
        "industry": "教育",
        "region": "广州"
    }
    
    create_response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers=auth_headers
    )
    customer_id = create_response.json()["id"]
    
    # 更新客户信息
    update_data = {
        "name": "更新后的客户名称",
        "contact_person": "王五",
        "contact_email": "wangwu@example.com",
        "contact_phone": "13800138003",
        "industry": "教育",
        "region": "广州"
    }
    
    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]

def test_delete_customer(auth_headers):
    """测试删除客户"""
    # 先创建一个客户
    customer_data = {
        "name": "测试客户4",
        "contact_person": "赵六",
        "contact_email": "zhaoliu@example.com",
        "contact_phone": "13800138004",
        "industry": "医疗",
        "region": "深圳"
    }
    
    create_response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers=auth_headers
    )
    customer_id = create_response.json()["id"]
    
    # 删除客户
    response = client.delete(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # 验证客户已被删除
    get_response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_get_customer_stats(auth_headers):
    """测试获取客户统计信息"""
    response = client.get("/api/v1/customers/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert "vip_customers" in data

def test_get_vip_customers(auth_headers):
    """测试获取VIP客户列表"""
    response = client.get("/api/v1/customers/vip", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)



