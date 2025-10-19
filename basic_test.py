#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试脚本 - QBM AI System
测试核心功能，避免复杂依赖
"""
import sys
import os
from datetime import datetime

def test_basic_imports():
    """测试基础模块导入"""
    print("测试基础模块导入...")
    
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
    
    try:
        import pandas
        print("[OK] Pandas 导入成功")
    except ImportError as e:
        print(f"[FAIL] Pandas 导入失败: {e}")
        return False
    
    try:
        import sklearn
        print("[OK] Scikit-learn 导入成功")
    except ImportError as e:
        print(f"[FAIL] Scikit-learn 导入失败: {e}")
        return False
    
    return True

def test_fastapi_basic():
    """测试FastAPI基础功能"""
    print("\n测试FastAPI基础功能...")
    
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
        
        @app.get("/test")
        async def test_endpoint():
            return {"test": "success", "data": {"value": 123}}
        
        print("[OK] FastAPI应用创建成功")
        print("[OK] 路由配置成功")
        return app
        
    except Exception as e:
        print(f"[FAIL] FastAPI基础功能测试失败: {e}")
        return None

def test_data_processing():
    """测试数据处理功能"""
    print("\n测试数据处理功能...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        data = {
            'customer_id': [1, 2, 3, 4, 5],
            'name': ['客户A', '客户B', '客户C', '客户D', '客户E'],
            'value': [1000, 2000, 1500, 3000, 2500],
            'date': pd.date_range('2024-01-01', periods=5)
        }
        
        df = pd.DataFrame(data)
        print("[OK] 测试数据创建成功")
        
        # 基本统计
        stats = df.describe()
        print("[OK] 数据统计计算成功")
        
        # 数据筛选
        filtered = df[df['value'] > 1500]
        print("[OK] 数据筛选功能正常")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 数据处理功能测试失败: {e}")
        return False

def test_ml_basic():
    """测试机器学习基础功能"""
    print("\n测试机器学习基础功能...")
    
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        import numpy as np
        
        # 创建测试数据
        X = np.random.rand(100, 2)
        y = X[:, 0] + 2 * X[:, 1] + np.random.rand(100) * 0.1
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        print("[OK] 数据分割成功")
        
        # 训练模型
        model = LinearRegression()
        model.fit(X_train, y_train)
        print("[OK] 模型训练成功")
        
        # 预测
        predictions = model.predict(X_test)
        print("[OK] 模型预测成功")
        
        # 计算R²分数
        score = model.score(X_test, y_test)
        print(f"[OK] 模型评分: {score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 机器学习基础功能测试失败: {e}")
        return False

def test_security_basic():
    """测试安全基础功能"""
    print("\n测试安全基础功能...")
    
    try:
        import hashlib
        import secrets
        
        # 测试基本哈希功能
        password = "test123"
        salt = secrets.token_hex(16)
        
        # 使用SHA256进行哈希
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        print("[OK] 密码哈希功能正常")
        
        # 测试哈希验证
        test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        if test_hash == hashed:
            print("[OK] 密码验证功能正常")
        else:
            print("[FAIL] 密码验证功能异常")
            return False
        
        # 测试随机数生成
        random_token = secrets.token_urlsafe(32)
        if len(random_token) > 0:
            print("[OK] 随机令牌生成功能正常")
        else:
            print("[FAIL] 随机令牌生成功能异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 安全基础功能测试失败: {e}")
        return False

def run_test_server():
    """运行测试服务器"""
    print("\n启动测试服务器...")
    
    app = test_fastapi_basic()
    if app:
        print("[OK] 服务器配置成功")
        print("访问地址:")
        print("  - 主页: http://localhost:8000/")
        print("  - 健康检查: http://localhost:8000/health")
        print("  - 测试端点: http://localhost:8000/test")
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
    print("QBM AI System 基础测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("基础模块导入", test_basic_imports),
        ("FastAPI基础功能", test_fastapi_basic),
        ("数据处理功能", test_data_processing),
        ("机器学习基础功能", test_ml_basic),
        ("安全基础功能", test_security_basic),
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
        print("\n所有基础测试通过！系统核心功能正常。")
        
        # 询问是否启动服务器
        choice = input("\n是否启动测试服务器？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            run_test_server()
    else:
        print(f"\n有 {total - passed} 个测试失败，请检查系统配置。")
    
    print("\n提示:")
    print("1. 这是基础功能测试，验证核心依赖和功能")
    print("2. 测试服务器提供基本的API端点")
    print("3. 可以通过浏览器访问 http://localhost:8000/docs 查看API文档")

if __name__ == "__main__":
    main()
