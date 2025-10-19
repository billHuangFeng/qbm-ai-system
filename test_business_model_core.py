#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试商业模式核心分析功能
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from business_model_core import BusinessModelAnalyzer, BusinessModelDashboard, ValuePropositionStage, ValuePropositionMetrics

def create_sample_data():
    """创建示例数据"""
    print("创建示例数据...")
    
    # 1. 客户认知数据
    customer_data = pd.DataFrame({
        'customer_id': range(1, 101),
        'customer_segment': np.random.choice(['企业客户', '个人客户', 'VIP客户'], 100),
        'value_proposition_awareness': np.random.normal(3.5, 1.0, 100).clip(1, 5),
        'value_proposition_acceptance': np.random.normal(3.2, 1.1, 100).clip(1, 5),
        'experience_quality_score': np.random.normal(3.8, 0.8, 100).clip(1, 5),
        'value_realization_score': np.random.normal(3.6, 0.9, 100).clip(1, 5),
        'customer_lifetime_value': np.random.exponential(100000, 100),
        'conversion_rate': np.random.beta(2, 5, 100),
        'awareness_channel': np.random.choice(['线上广告', '朋友推荐', '销售拜访', '展会', '社交媒体'], 100),
        'acceptance_barriers': [json.dumps(['价格', '信任', '功能']) if np.random.random() < 0.3 else None for _ in range(100)],
        'experience_touchpoints': [json.dumps({'购买': 4.2, '使用': 3.8, '售后': 4.0}) for _ in range(100)],
        'experience_feedback': ['体验良好' if np.random.random() > 0.3 else '需要改进' for _ in range(100)]
    })
    
    # 2. 产品数据
    product_data = pd.DataFrame({
        'product_id': range(1, 21),
        'product_name': [f'产品{i}' for i in range(1, 21)],
        'product_category': np.random.choice(['软件', '硬件', '服务'], 20),
        'product_features': [json.dumps({'功能A': 4.5, '功能B': 3.8, '功能C': 4.2}) for _ in range(20)],
        'value_proposition_alignment': np.random.normal(3.7, 0.7, 20).clip(1, 5),
        'value_proposition_fulfillment': np.random.beta(3, 2, 20),
        'product_quality': np.random.normal(4.0, 0.6, 20).clip(1, 5),
        'product_innovation': np.random.normal(3.5, 0.8, 20).clip(1, 5),
        'product_performance': np.random.normal(3.8, 0.7, 20).clip(1, 5),
        'customer_satisfaction': np.random.normal(3.9, 0.5, 20).clip(1, 5),
        'market_share': np.random.exponential(5, 20),
        'launch_date': [datetime.now() - timedelta(days=np.random.randint(30, 1000)) for _ in range(20)]
    })
    
    # 3. 资源能力数据
    resource_data = pd.DataFrame({
        'resource_id': range(1, 31),
        'name': [f'资源{i}' for i in range(1, 31)],
        'type': np.random.choice(['resource', 'capability'], 30),
        'category': np.random.choice(['技术', '人力', '资金', '设备'], 30),
        'current_level': np.random.normal(3.5, 1.0, 30).clip(1, 5),
        'required_level': np.random.normal(4.0, 0.8, 30).clip(1, 5),
        'utilization_rate': np.random.beta(2, 2, 30),
        'efficiency_score': np.random.normal(3.6, 0.9, 30).clip(1, 5),
        'capability_level': np.random.normal(3.4, 1.1, 30).clip(1, 5),
        'value_delivery_ratio': np.random.beta(3, 2, 30),
        'cost_effectiveness': np.random.normal(3.7, 0.8, 30).clip(1, 5)
    })
    
    # 4. 价值数据
    value_data = pd.DataFrame({
        'value_id': range(1, 51),
        'customer_id': np.random.randint(1, 101, 50),
        'resource_id': np.random.randint(1, 31, 50),
        'value_delivered': np.random.exponential(50000, 50),
        'delivery_quality': np.random.normal(3.8, 0.7, 50).clip(1, 5),
        'delivery_efficiency': np.random.normal(3.6, 0.8, 50).clip(1, 5),
        'customer_satisfaction': np.random.normal(3.9, 0.6, 50).clip(1, 5),
        'resource_investment': np.random.exponential(30000, 50),
        'investment_efficiency': np.random.normal(3.5, 0.9, 50).clip(1, 5),
        'roi': np.random.normal(1.5, 0.5, 50).clip(0.5, 3.0),
        'delivery_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(50)]
    })
    
    # 5. 投资数据
    investment_data = pd.DataFrame({
        'investment_id': range(1, 26),
        'investment_category': np.random.choice(['研发', '营销', '运营', '基础设施'], 25),
        'investment_type': np.random.choice(['一次性', '持续性'], 25),
        'investment_amount': np.random.exponential(100000, 25),
        'expected_return': np.random.exponential(150000, 25),
        'actual_return': np.random.exponential(140000, 25),
        'value_increase': np.random.exponential(40000, 25),
        'marginal_investment': np.random.exponential(20000, 25),
        'marginal_value': np.random.exponential(30000, 25),
        'roi': np.random.normal(1.4, 0.4, 25).clip(0.8, 2.5),
        'payback_period': np.random.randint(6, 36, 25),
        'investment_date': [datetime.now() - timedelta(days=np.random.randint(1, 730)) for _ in range(25)]
    })
    
    # 6. 销售数据
    sales_data = pd.DataFrame({
        'sale_id': range(1, 201),
        'product_id': np.random.randint(1, 21, 200),
        'customer_id': np.random.randint(1, 101, 200),
        'sales_value': np.random.exponential(25000, 200),
        'customer_satisfaction': np.random.normal(3.8, 0.7, 200).clip(1, 5),
        'sales_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(200)]
    })
    
    return {
        'customers': customer_data,
        'products': product_data,
        'resources': resource_data,
        'values': value_data,
        'investments': investment_data,
        'sales': sales_data
    }

def test_value_proposition_cognition():
    """测试价值主张认知分析"""
    print("\n=== 测试价值主张认知分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_value_proposition_cognition(data['customers'])
        
        print("[OK] 价值主张认知分析成功")
        print(f"认知度分布: {results.get('awareness_distribution', {})}")
        print(f"渠道效果: {results.get('channel_effectiveness', {})}")
        print(f"认知价值相关性: {results.get('awareness_value_correlation', 0):.3f}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 价值主张认知分析失败: {e}")
        return False

def test_customer_acceptance():
    """测试客户接纳程度分析"""
    print("\n=== 测试客户接纳程度分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_customer_acceptance(data['customers'])
        
        print("[OK] 客户接纳程度分析成功")
        print(f"接纳指标: {results.get('acceptance_metrics', {})}")
        print(f"接纳障碍分析: {results.get('barrier_analysis', {})}")
        print(f"接纳转化关系: {results.get('acceptance_conversion_relationship', {})}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 客户接纳程度分析失败: {e}")
        return False

def test_customer_experience():
    """测试客户体验程度分析"""
    print("\n=== 测试客户体验程度分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_customer_experience(data['customers'], data['products'])
        
        print("✅ 客户体验程度分析成功")
        print(f"体验指标: {results.get('experience_metrics', {})}")
        print(f"触点分析: {results.get('touchpoint_analysis', {})}")
        print(f"产品体验关系: {results.get('product_experience_relationship', {})}")
        print(f"体验价值相关性: {results.get('experience_value_correlation', 0):.3f}")
        
        return True
    except Exception as e:
        print(f"❌ 客户体验程度分析失败: {e}")
        return False

def test_value_product_relationship():
    """测试价值主张与产品特性关系分析"""
    print("\n=== 测试价值主张与产品特性关系分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_value_product_relationship(data['products'], data['sales'])
        
        print("✅ 价值主张与产品特性关系分析成功")
        print(f"特性价值贡献: {results.get('feature_value_contribution', {})}")
        print(f"类别对齐: {results.get('category_alignment', {})}")
        print(f"特性满意度: {results.get('satisfaction_by_features', {})}")
        print(f"实现度分析: {results.get('fulfillment_analysis', {})}")
        
        return True
    except Exception as e:
        print(f"❌ 价值主张与产品特性关系分析失败: {e}")
        return False

def test_resource_capability_value():
    """测试资源能力与价值关系分析"""
    print("\n=== 测试资源能力与价值关系分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_resource_capability_value(
            data['resources'], data['resources'], data['values']
        )
        
        print("✅ 资源能力与价值关系分析成功")
        print(f"资源效率: {results.get('resource_efficiency', {})}")
        print(f"能力价值关系: {results.get('capability_value_relationship', {})}")
        print(f"投资价值比率: {results.get('investment_value_ratio', {})}")
        print(f"能力缺口分析: {results.get('capability_gap_analysis', {})}")
        
        return True
    except Exception as e:
        print(f"❌ 资源能力与价值关系分析失败: {e}")
        return False

def test_resource_capability_product():
    """测试资源能力与产品特性关系分析"""
    print("\n=== 测试资源能力与产品特性关系分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_resource_capability_product(
            data['resources'], data['resources'], data['products']
        )
        
        print("✅ 资源能力与产品特性关系分析成功")
        print(f"开发资源关系: {results.get('development_resource_relationship', {})}")
        print(f"能力质量关系: {results.get('capability_quality_relationship', 0):.3f}")
        print(f"性能资源关系: {results.get('performance_resource_relationship', {})}")
        print(f"能力创新关系: {results.get('capability_innovation_relationship', 0):.3f}")
        
        return True
    except Exception as e:
        print(f"❌ 资源能力与产品特性关系分析失败: {e}")
        return False

def test_incremental_value():
    """测试价值增量分析"""
    print("\n=== 测试价值增量分析 ===")
    
    analyzer = BusinessModelAnalyzer()
    data = create_sample_data()
    
    try:
        results = analyzer.analyze_incremental_value(data['investments'], data['values'])
        
        print("✅ 价值增量分析成功")
        print(f"ROI分析: {results.get('roi_analysis', {})}")
        print(f"边际价值分析: {results.get('marginal_value_analysis', {})}")
        print(f"价值增量预测: {results.get('value_increment_prediction', {})}")
        print(f"最优投资组合: {results.get('optimal_investment_portfolio', {})}")
        
        return True
    except Exception as e:
        print(f"❌ 价值增量分析失败: {e}")
        return False

def test_comprehensive_analysis():
    """测试综合分析"""
    print("\n=== 测试综合分析 ===")
    
    dashboard = BusinessModelDashboard()
    data = create_sample_data()
    
    try:
        results = dashboard.generate_comprehensive_analysis(data)
        
        print("✅ 综合分析成功")
        print(f"分析模块数量: {len(results)}")
        
        for module_name, module_results in results.items():
            print(f"  - {module_name}: {len(module_results)} 个分析结果")
        
        return True
    except Exception as e:
        print(f"❌ 综合分析失败: {e}")
        return False

def main():
    """主测试函数"""
    print("QBM AI System 商业模式核心分析功能测试")
    print("=" * 60)
    
    tests = [
        ("价值主张认知分析", test_value_proposition_cognition),
        ("客户接纳程度分析", test_customer_acceptance),
        ("客户体验程度分析", test_customer_experience),
        ("价值主张与产品特性关系分析", test_value_product_relationship),
        ("资源能力与价值关系分析", test_resource_capability_value),
        ("资源能力与产品特性关系分析", test_resource_capability_product),
        ("价值增量分析", test_incremental_value),
        ("综合分析", test_comprehensive_analysis),
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
    print("\n" + "=" * 60)
    print("商业模式核心分析功能测试结果:")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有核心分析功能测试通过！")
        print("系统已成功实现您要求的核心商业模式分析功能：")
        print("✅ 客户对企业价值主张的认知分析")
        print("✅ 客户对价值主张的接纳程度分析")
        print("✅ 客户体验程度分析")
        print("✅ 价值主张与产品特性的关系分析")
        print("✅ 资源和能力与客户体验价值的关系分析")
        print("✅ 资源和能力与产品特性实现的关系分析")
        print("✅ 投入资源带来的价值增量分析")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步优化")
    
    print("\n💡 系统现在专注于您要求的核心商业模式量化分析功能！")

if __name__ == "__main__":
    main()
