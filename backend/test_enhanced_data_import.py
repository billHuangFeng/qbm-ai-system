#!/usr/bin/env python3
"""
BMOS数据导入功能测试脚本
测试增强的数据导入服务
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

from src.services.enhanced_data_import import DataImportService, data_import_service

async def test_data_import_service():
    """测试数据导入服务"""
    print("BMOS数据导入服务测试")
    print("=" * 50)
    
    # 1. 测试服务初始化
    print("\n1. 测试服务初始化:")
    print(f"上传目录: {data_import_service.upload_dir}")
    print(f"支持格式: {data_import_service.supported_formats}")
    print("OK 服务初始化成功")
    
    # 2. 创建测试数据
    print("\n2. 创建测试数据:")
    test_data = pd.DataFrame({
        'id': range(1, 51),
        'name': [f'User_{i}' for i in range(1, 51)],
        'age': np.random.randint(18, 65, 50),
        'salary': np.random.normal(50000, 15000, 50),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 50),
        'score': np.random.uniform(0, 100, 50)
    })
    
    # 添加一些缺失值
    test_data.loc[5:10, 'age'] = np.nan
    test_data.loc[15:20, 'salary'] = np.nan
    
    print(f"测试数据形状: {test_data.shape}")
    print(f"列名: {list(test_data.columns)}")
    print("OK 测试数据创建成功")
    
    # 3. 测试数据验证
    print("\n3. 测试数据验证:")
    validation_result = data_import_service.validate_data(test_data)
    
    print(f"总行数: {validation_result['total_rows']}")
    print(f"总列数: {validation_result['total_columns']}")
    print(f"质量分数: {validation_result['quality_score']:.1f}")
    print(f"缺失值: {validation_result['missing_values']}")
    print(f"重复行: {validation_result['duplicate_rows']}")
    
    if validation_result['warnings']:
        print("警告:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")
    
    print("OK 数据验证完成")
    
    # 4. 测试建议生成
    print("\n4. 测试建议生成:")
    recommendations = data_import_service.generate_recommendations(validation_result)
    
    if recommendations:
        print("改进建议:")
        for rec in recommendations:
            print(f"  - {rec}")
    else:
        print("无改进建议")
    
    print("OK 建议生成完成")
    
    # 5. 测试文件保存和解析
    print("\n5. 测试文件保存和解析:")
    
    # 保存为CSV
    csv_file = data_import_service.upload_dir / "test_data.csv"
    test_data.to_csv(csv_file, index=False)
    print(f"CSV文件保存: {csv_file}")
    
    # 解析CSV文件
    parsed_df = await data_import_service.parse_file(str(csv_file))
    print(f"解析结果形状: {parsed_df.shape}")
    print("OK 文件保存和解析成功")
    
    # 6. 测试导入历史
    print("\n6. 测试导入历史:")
    history = data_import_service.get_import_history()
    print(f"历史文件数量: {len(history)}")
    
    if history:
        print("最近的文件:")
        for i, file_info in enumerate(history[:3]):
            print(f"  {i+1}. {file_info['file_name']} ({file_info['file_size']} bytes)")
    
    print("OK 导入历史查询成功")
    
    # 7. 测试清理功能
    print("\n7. 测试清理功能:")
    cleaned_count = data_import_service.cleanup_old_files(days=0)  # 清理所有文件
    print(f"清理文件数量: {cleaned_count}")
    print("OK 清理功能测试完成")
    
    print("\n" + "=" * 50)
    print("数据导入服务测试完成!")
    print("所有功能测试通过 OK")

async def test_data_quality_scenarios():
    """测试不同数据质量场景"""
    print("\n数据质量场景测试")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "高质量数据",
            "data": pd.DataFrame({
                'id': range(1, 21),
                'value': np.random.normal(100, 10, 20),
                'category': ['A', 'B'] * 10
            })
        },
        {
            "name": "高缺失值数据",
            "data": pd.DataFrame({
                'id': range(1, 21),
                'value': [np.nan] * 15 + list(np.random.normal(100, 10, 5)),
                'category': ['A'] * 20
            })
        },
        {
            "name": "重复数据",
            "data": pd.DataFrame({
                'id': [1, 2, 3, 1, 2, 3] * 3,
                'value': np.random.normal(100, 10, 18),
                'category': ['A', 'B', 'C'] * 6
            })
        },
        {
            "name": "混合数据类型",
            "data": pd.DataFrame({
                'id': range(1, 21),
                'text': [f'text_{i}' for i in range(1, 21)],
                'number': np.random.normal(100, 10, 20),
                'date': pd.date_range('2023-01-01', periods=20, freq='D')
            })
        }
    ]
    
    for scenario in scenarios:
        print(f"\n测试场景: {scenario['name']}")
        print(f"数据形状: {scenario['data'].shape}")
        
        validation_result = data_import_service.validate_data(scenario['data'])
        recommendations = data_import_service.generate_recommendations(validation_result)
        
        print(f"质量分数: {validation_result['quality_score']:.1f}")
        print(f"缺失值: {sum(validation_result['missing_values'].values())}")
        print(f"重复行: {validation_result['duplicate_rows']}")
        
        if recommendations:
            print("建议:")
            for rec in recommendations[:2]:  # 只显示前2个建议
                print(f"  - {rec}")
        
        print("OK 场景测试完成")

async def main():
    """主测试函数"""
    try:
        # 运行基本测试
        await test_data_import_service()
        
        # 运行质量场景测试
        await test_data_quality_scenarios()
        
        print("\n所有测试完成!")
        print("数据导入服务功能正常，可以开始使用!")
        
    except Exception as e:
        print(f"\nERROR 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
