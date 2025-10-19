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

def test_get_products(auth_headers):
    """测试获取产品列表"""
    response = client.get("/api/v1/products/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data

def test_create_product(auth_headers):
    """测试创建产品"""
    product_data = {
        "name": "测试产品",
        "description": "这是一个测试产品",
        "price": 99.99,
        "category": "软件",
        "stock_quantity": 100
    }
    
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]

def test_get_product(auth_headers):
    """测试获取单个产品"""
    # 先创建一个产品
    product_data = {
        "name": "测试产品2",
        "description": "这是第二个测试产品",
        "price": 199.99,
        "category": "硬件",
        "stock_quantity": 50
    }
    
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers
    )
    product_id = create_response.json()["id"]
    
    # 获取产品信息
    response = client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]

def test_update_product(auth_headers):
    """测试更新产品"""
    # 先创建一个产品
    product_data = {
        "name": "测试产品3",
        "description": "这是第三个测试产品",
        "price": 299.99,
        "category": "服务",
        "stock_quantity": 25
    }
    
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers
    )
    product_id = create_response.json()["id"]
    
    # 更新产品信息
    update_data = {
        "name": "更新后的产品名称",
        "description": "更新后的产品描述",
        "price": 399.99,
        "category": "服务",
        "stock_quantity": 30
    }
    
    response = client.put(
        f"/api/v1/products/{product_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]

def test_delete_product(auth_headers):
    """测试删除产品"""
    # 先创建一个产品
    product_data = {
        "name": "测试产品4",
        "description": "这是第四个测试产品",
        "price": 499.99,
        "category": "软件",
        "stock_quantity": 75
    }
    
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers
    )
    product_id = create_response.json()["id"]
    
    # 删除产品
    response = client.delete(f"/api/v1/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # 验证产品已被删除
    get_response = client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_get_product_stats(auth_headers):
    """测试获取产品统计信息"""
    response = client.get("/api/v1/products/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "total_categories" in data

def test_get_featured_products(auth_headers):
    """测试获取推荐产品列表"""
    response = client.get("/api/v1/products/featured", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)



