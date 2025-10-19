#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本 - QBM AI System
不依赖数据库，直接测试核心功能
"""
import sys
import os
import json
from datetime import datetime

# 添加backend路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from fastapi import FastAPI
        print("[OK] FastAPI 导入成功")
    except ImportError as e:
        print(f"[FAIL] FastAPI 导入失败: {e}")
        return False
    
    try:
        import uvicorn
        print("[OK] Uvicorn 导入成功")
    except ImportError as e:
        print(f"[FAIL] Uvicorn 导入失败: {e}")
        return False
    
    try:
        from sqlalchemy import create_engine
        print("[OK] SQLAlchemy 导入成功")
    except ImportError as e:
        print(f"[FAIL] SQLAlchemy 导入失败: {e}")
        return False
    
    try:
        import pymysql
        print("[OK] PyMySQL 导入成功")
    except ImportError as e:
        print(f"[FAIL] PyMySQL 导入失败: {e}")
        return False
    
    return True

def test_fastapi_app():
    """测试FastAPI应用创建"""
    print("\n测试FastAPI应用创建...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="QBM AI System",
            description="AI增强的商业模式量化分析系统",
            version="1.0.0"
        )
        
        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {"message": "QBM AI System API", "status": "running"}
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        
        print("[OK] FastAPI应用创建成功")
        return app
        
    except Exception as e:
        print(f"[FAIL] FastAPI应用创建失败: {e}")
        return None

def test_ai_engine():
    """测试AI引擎模块"""
    print("\n测试AI引擎模块...")
    
    try:
        # 测试数据处理器
        from ai_engine.utils.data_processor import DataProcessor
        processor = DataProcessor()
        print("[OK] 数据处理器创建成功")
        
        # 测试客户分析器
        from ai_engine.analyzers.customer_analyzer import CustomerAnalyzer
        analyzer = CustomerAnalyzer()
        print("[OK] 客户分析器创建成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] AI引擎模块测试失败: {e}")
        return False

def test_data_models():
    """测试数据模型"""
    print("\n测试数据模型...")
    
    try:
        # 测试用户模型
        from backend.app.models.user import User
        print("[OK] 用户模型导入成功")
        
        # 测试客户模型
        from backend.app.models.customer import Customer
        print("[OK] 客户模型导入成功")
        
        # 测试产品模型
        from backend.app.models.product import Product
        print("[OK] 产品模型导入成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 数据模型测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    try:
        # 测试认证端点
        from backend.app.api.v1.endpoints.auth import router as auth_router
        print("[OK] 认证端点导入成功")
        
        # 测试客户端点
        from backend.app.api.v1.endpoints.customers import router as customers_router
        print("[OK] 客户端点导入成功")
        
        # 测试产品端点
        from backend.app.api.v1.endpoints.products import router as products_router
        print("[OK] 产品端点导入成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] API端点测试失败: {e}")
        return False

def test_crud_operations():
    """测试CRUD操作"""
    print("\n测试CRUD操作...")
    
    try:
        # 测试基础CRUD
        from backend.app.crud.base import CRUDBase
        print("[OK] 基础CRUD导入成功")
        
        # 测试用户CRUD
        from backend.app.crud.user import user
        print("[OK] 用户CRUD导入成功")
        
        # 测试客户CRUD
        from backend.app.crud.customer import customer
        print("[OK] 客户CRUD导入成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] CRUD操作测试失败: {e}")
        return False

def test_schemas():
    """测试数据模式"""
    print("\n测试数据模式...")
    
    try:
        # 测试用户模式
        from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse
        print("[OK] 用户模式导入成功")
        
        # 测试客户模式
        from backend.app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
        print("[OK] 客户模式导入成功")
        
        # 测试产品模式
        from backend.app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
        print("[OK] 产品模式导入成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 数据模式测试失败: {e}")
        return False

def test_security():
    """测试安全模块"""
    print("\n测试安全模块...")
    
    try:
        from backend.app.core.security import get_password_hash, verify_password, create_access_token
        print("[OK] 安全模块导入成功")
        
        # 测试密码哈希
        password = "test123"
        hashed = get_password_hash(password)
        print("[OK] 密码哈希功能正常")
        
        # 测试密码验证
        is_valid = verify_password(password, hashed)
        if is_valid:
            print("[OK] 密码验证功能正常")
        else:
            print("[FAIL] 密码验证功能异常")
            return False
        
        # 测试JWT令牌
        token = create_access_token(data={"sub": "test_user"})
        if token:
            print("[OK] JWT令牌创建功能正常")
        else:
            print("[FAIL] JWT令牌创建功能异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 安全模块测试失败: {e}")
        return False

def run_simple_server():
    """运行简单服务器"""
    print("\n启动简单测试服务器...")
    
    app = test_fastapi_app()
    if app:
        print("[OK] 服务器启动成功")
        print("访问地址:")
        print("  - 主页: http://localhost:8000/")
        print("  - 健康检查: http://localhost:8000/health")
        print("  - API文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止服务器")
        
        try:
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("\n服务器已停止")
        except Exception as e:
            print(f"[FAIL] 服务器启动失败: {e}")
    else:
        print("[FAIL] 无法启动服务器")

def main():
    """主函数"""
    print("QBM AI System 简化测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("模块导入", test_imports),
        ("FastAPI应用", test_fastapi_app),
        ("AI引擎", test_ai_engine),
        ("数据模型", test_data_models),
        ("API端点", test_api_endpoints),
        ("CRUD操作", test_crud_operations),
        ("数据模式", test_schemas),
        ("安全模块", test_security),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n执行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"[PASS] {test_name} 测试通过")
            else:
                print(f"[FAIL] {test_name} 测试失败")
        except Exception as e:
            print(f"[ERROR] {test_name} 测试异常: {e}")
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n所有测试通过！系统核心功能正常。")
        
        # 询问是否启动服务器
        choice = input("\n是否启动测试服务器？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            run_simple_server()
    else:
        print(f"\n有 {total - passed} 个测试失败，请检查系统配置。")
    
    print("\n提示:")
    print("1. 这是一个简化测试，不包含数据库连接")
    print("2. 如需完整测试，请配置数据库后运行完整测试套件")
    print("3. 测试服务器仅用于验证核心功能")

if __name__ == "__main__":
    main()