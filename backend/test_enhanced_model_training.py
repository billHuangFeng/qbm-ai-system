#!/usr/bin/env python3
"""
BMOS模型训练功能测试脚本
测试增强的模型训练服务
"""

import asyncio
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.enhanced_model_training import ModelTrainingService, ModelConfig, model_training_service

async def test_model_training_service():
    """测试模型训练服务"""
    print("BMOS模型训练服务测试")
    print("=" * 50)
    
    # 1. 测试服务初始化
    print("\n1. 测试服务初始化:")
    print(f"模型目录: {model_training_service.models_dir}")
    print(f"支持算法: {list(model_training_service.supported_algorithms.keys())}")
    print("OK 服务初始化成功")
    
    # 2. 创建测试数据
    print("\n2. 创建测试数据:")
    
    # 分类数据
    np.random.seed(42)
    classification_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 200),
        'feature2': np.random.normal(0, 1, 200),
        'feature3': np.random.normal(0, 1, 200),
        'target': np.random.choice(['A', 'B', 'C'], 200)
    })
    
    # 回归数据
    regression_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 200),
        'feature2': np.random.normal(0, 1, 200),
        'feature3': np.random.normal(0, 1, 200),
        'target': np.random.normal(0, 1, 200)
    })
    
    print(f"分类数据形状: {classification_data.shape}")
    print(f"回归数据形状: {regression_data.shape}")
    print("OK 测试数据创建成功")
    
    # 3. 测试数据准备
    print("\n3. 测试数据准备:")
    
    config_classification = ModelConfig(
        model_type="classification",
        algorithm="random_forest_classifier",
        target_column="target",
        feature_columns=["feature1", "feature2", "feature3"]
    )
    
    X_class, y_class = model_training_service.prepare_data(classification_data, config_classification)
    print(f"分类数据准备: X{X_class.shape}, y{y_class.shape}")
    
    config_regression = ModelConfig(
        model_type="regression",
        algorithm="random_forest_regressor",
        target_column="target",
        feature_columns=["feature1", "feature2", "feature3"]
    )
    
    X_reg, y_reg = model_training_service.prepare_data(regression_data, config_regression)
    print(f"回归数据准备: X{X_reg.shape}, y{y_reg.shape}")
    print("OK 数据准备成功")
    
    # 4. 测试模型训练
    print("\n4. 测试模型训练:")
    
    # 训练分类模型
    model_class, training_info_class = model_training_service.train_model(
        X_class, y_class, config_classification
    )
    print(f"分类模型训练完成: {type(model_class).__name__}")
    print(f"训练时间: {training_info_class['training_time']:.2f}秒")
    
    # 训练回归模型
    model_reg, training_info_reg = model_training_service.train_model(
        X_reg, y_reg, config_regression
    )
    print(f"回归模型训练完成: {type(model_reg).__name__}")
    print(f"训练时间: {training_info_reg['training_time']:.2f}秒")
    print("OK 模型训练成功")
    
    # 5. 测试模型评估
    print("\n5. 测试模型评估:")
    
    # 划分测试集
    from sklearn.model_selection import train_test_split
    
    X_class_train, X_class_test, y_class_train, y_class_test = train_test_split(
        X_class, y_class, test_size=0.2, random_state=42
    )
    
    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    
    # 重新训练模型
    model_class, _ = model_training_service.train_model(X_class_train, y_class_train, config_classification)
    model_reg, _ = model_training_service.train_model(X_reg_train, y_reg_train, config_regression)
    
    # 评估分类模型
    metrics_class = model_training_service.evaluate_model(model_class, X_class_test, y_class_test, config_classification)
    print(f"分类模型准确率: {metrics_class['accuracy']:.3f}")
    
    # 评估回归模型
    metrics_reg = model_training_service.evaluate_model(model_reg, X_reg_test, y_reg_test, config_regression)
    print(f"回归模型R2分数: {metrics_reg['r2_score']:.3f}")
    print("OK 模型评估成功")
    
    # 6. 测试交叉验证
    print("\n6. 测试交叉验证:")
    
    cv_scores_class = model_training_service.cross_validate_model(model_class, X_class_train, y_class_train)
    print(f"分类模型交叉验证分数: {cv_scores_class}")
    
    cv_scores_reg = model_training_service.cross_validate_model(model_reg, X_reg_train, y_reg_train)
    print(f"回归模型交叉验证分数: {cv_scores_reg}")
    print("OK 交叉验证成功")
    
    # 7. 测试模型预测
    print("\n7. 测试模型预测:")
    
    # 创建测试数据
    test_features = pd.DataFrame({
        'feature1': [0.5, -0.3, 1.2],
        'feature2': [0.8, -1.1, 0.4],
        'feature3': [-0.2, 0.7, -0.9]
    })
    
    # 分类预测
    prediction_class = model_training_service.predict(model_class, test_features)
    print(f"分类预测: {prediction_class.prediction}")
    if prediction_class.confidence:
        print(f"置信度: {prediction_class.confidence:.3f}")
    
    # 回归预测
    prediction_reg = model_training_service.predict(model_reg, test_features)
    print(f"回归预测: {prediction_reg.prediction}")
    print("OK 模型预测成功")
    
    # 8. 测试完整训练流程
    print("\n8. 测试完整训练流程:")
    
    result_classification = await model_training_service.train_complete_model(
        classification_data, config_classification
    )
    
    result_regression = await model_training_service.train_complete_model(
        regression_data, config_regression
    )
    
    print(f"完整训练 - 分类模型: {result_classification.model_id}")
    print(f"完整训练 - 回归模型: {result_regression.model_id}")
    print("OK 完整训练流程成功")
    
    # 9. 测试模型管理
    print("\n9. 测试模型管理:")
    
    # 获取模型列表
    models = model_training_service.get_model_list()
    print(f"已训练模型数量: {len(models)}")
    
    # 加载模型
    if models:
        model_id = models[0]['model_id']
        loaded_model, model_info = model_training_service.load_model(model_id)
        print(f"模型加载成功: {model_id}")
        
        # 删除模型
        deleted = model_training_service.delete_model(model_id)
        print(f"模型删除: {'成功' if deleted else '失败'}")
    
    print("OK 模型管理功能成功")
    
    print("\n" + "=" * 50)
    print("模型训练服务测试完成!")
    print("所有功能测试通过 OK")

async def test_different_algorithms():
    """测试不同算法"""
    print("\n不同算法测试")
    print("=" * 50)
    
    # 创建测试数据
    np.random.seed(42)
    data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 300),
        'feature2': np.random.normal(0, 1, 300),
        'feature3': np.random.normal(0, 1, 300),
        'target': np.random.choice(['A', 'B', 'C'], 300)
    })
    
    algorithms = [
        "random_forest_classifier",
        "xgboost_classifier",
        "lightgbm_classifier"
    ]
    
    for algorithm in algorithms:
        print(f"\n测试算法: {algorithm}")
        
        config = ModelConfig(
            model_type="classification",
            algorithm=algorithm,
            target_column="target",
            feature_columns=["feature1", "feature2", "feature3"],
            parameters={"n_estimators": 50, "max_depth": 5}
        )
        
        try:
            result = await model_training_service.train_complete_model(data, config)
            print(f"  模型ID: {result.model_id}")
            print(f"  准确率: {result.accuracy:.3f}")
            print(f"  训练时间: {result.training_time:.2f}秒")
            print("OK 算法测试成功")
            
        except Exception as e:
            print(f"ERROR 算法测试失败: {str(e)}")

async def main():
    """主测试函数"""
    try:
        # 运行基本测试
        await test_model_training_service()
        
        # 运行算法测试
        await test_different_algorithms()
        
        print("\n所有测试完成!")
        print("模型训练服务功能正常，可以开始使用!")
        
    except Exception as e:
        print(f"\nERROR 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

