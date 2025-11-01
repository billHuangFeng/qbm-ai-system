"""
BMOS系统 - 机器学习库测试
验证机器学习库是否可以正常导入和使用
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_sklearn_import():
    """测试scikit-learn导入"""
    try:
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.neural_network import MLPClassifier
        from sklearn.impute import SimpleImputer, KNNImputer
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer
        print("[OK] scikit-learn导入成功")
        return True
    except ImportError as e:
        print(f"[ERROR] scikit-learn导入失败: {e}")
        return False

def test_xgboost_import():
    """测试XGBoost导入"""
    try:
        import xgboost as xgb
        from xgboost import XGBClassifier, XGBRegressor
        print("[OK] XGBoost导入成功")
        return True
    except ImportError as e:
        print(f"✗ XGBoost导入失败: {e}")
        return False

def test_lightgbm_import():
    """测试LightGBM导入"""
    try:
        import lightgbm as lgb
        from lightgbm import LGBMClassifier, LGBMRegressor
        print("✓ LightGBM导入成功")
        return True
    except ImportError as e:
        print(f"✗ LightGBM导入失败: {e}")
        return False

def test_pandas_import():
    """测试Pandas导入"""
    try:
        import pandas as pd
        import numpy as np
        print("✓ Pandas和NumPy导入成功")
        return True
    except ImportError as e:
        print(f"✗ Pandas导入失败: {e}")
        return False

def test_matplotlib_import():
    """测试Matplotlib导入"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ Matplotlib和Seaborn导入成功")
        return True
    except ImportError as e:
        print(f"✗ Matplotlib导入失败: {e}")
        return False

def test_basic_ml_functionality():
    """测试基本机器学习功能"""
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
        
        # 生成测试数据
        X, y = make_classification(n_samples=100, n_features=4, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # 预测
        predictions = model.predict(X_test)
        accuracy = model.score(X_test, y_test)
        
        assert len(predictions) == len(y_test)
        assert 0 <= accuracy <= 1
        print(f"✓ 基本机器学习功能测试成功，准确率: {accuracy:.3f}")
        return True
        
    except Exception as e:
        print(f"✗ 基本机器学习功能测试失败: {e}")
        return False

def test_xgboost_functionality():
    """测试XGBoost功能"""
    try:
        import numpy as np
        import xgboost as xgb
        from sklearn.datasets import make_regression
        
        # 生成测试数据
        X, y = make_regression(n_samples=100, n_features=4, random_state=42)
        
        # 训练XGBoost模型
        model = xgb.XGBRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # 预测
        predictions = model.predict(X)
        
        assert len(predictions) == len(y)
        print("✓ XGBoost功能测试成功")
        return True
        
    except Exception as e:
        print(f"✗ XGBoost功能测试失败: {e}")
        return False

def test_lightgbm_functionality():
    """测试LightGBM功能"""
    try:
        import numpy as np
        import lightgbm as lgb
        from sklearn.datasets import make_classification
        
        # 生成测试数据
        X, y = make_classification(n_samples=100, n_features=4, random_state=42)
        
        # 训练LightGBM模型
        model = lgb.LGBMClassifier(n_estimators=10, random_state=42, verbose=-1)
        model.fit(X, y)
        
        # 预测
        predictions = model.predict(X)
        
        assert len(predictions) == len(y)
        print("✓ LightGBM功能测试成功")
        return True
        
    except Exception as e:
        print(f"✗ LightGBM功能测试失败: {e}")
        return False

def test_bmos_algorithm_imports():
    """测试BMOS算法模块导入"""
    try:
        # 测试算法模块导入
        from src.algorithms.ensemble_models import RandomForestModel, XGBoostModel, LightGBMModel
        print("✓ BMOS算法模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ BMOS算法模块导入失败: {e}")
        return False

def test_bmos_services_imports():
    """测试BMOS服务模块导入"""
    try:
        # 测试服务模块导入
        from src.services.model_training_service import ModelTrainingService
        print("✓ BMOS服务模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ BMOS服务模块导入失败: {e}")
        return False

def run_ml_tests():
    """运行机器学习测试"""
    print("BMOS系统 - 机器学习库测试")
    print("=" * 50)
    
    tests = [
        ("scikit-learn导入", test_sklearn_import),
        ("XGBoost导入", test_xgboost_import),
        ("LightGBM导入", test_lightgbm_import),
        ("Pandas导入", test_pandas_import),
        ("Matplotlib导入", test_matplotlib_import),
        ("基本ML功能", test_basic_ml_functionality),
        ("XGBoost功能", test_xgboost_functionality),
        ("LightGBM功能", test_lightgbm_functionality),
        ("BMOS算法模块", test_bmos_algorithm_imports),
        ("BMOS服务模块", test_bmos_services_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}执行失败: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("机器学习库测试结果:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有机器学习库测试通过！")
        return True
    else:
        print("⚠️ 部分机器学习库测试失败")
        return False

if __name__ == "__main__":
    success = run_ml_tests()
    sys.exit(0 if success else 1)
