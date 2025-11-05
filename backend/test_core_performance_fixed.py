"""
BMOS系统核心功能性能测试 - 简化版
测试数据导入、模型训练、企业记忆的性能
"""

import asyncio
import time
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.enhanced_data_import import DataImportService
from src.services.enhanced_model_training import ModelTrainingService, ModelConfig
from src.services.enhanced_enterprise_memory import EnterpriseMemoryService


class BMOSCorePerformanceTester:
    def __init__(self):
        self.data_import_service = DataImportService()
        self.model_training_service = ModelTrainingService()
        self.memory_service = EnterpriseMemoryService()
        self.results = {}

    def test_data_import_performance(self):
        """测试数据导入性能"""
        print("=== 数据导入性能测试 ===")

        test_sizes = [100, 500, 1000, 2000]
        results = []

        for size in test_sizes:
            print(f"测试数据大小: {size}行")

            # 生成测试数据
            test_data = pd.DataFrame(
                {
                    "id": range(1, size + 1),
                    "feature1": np.random.randn(size),
                    "feature2": np.random.randn(size),
                    "feature3": np.random.randn(size),
                    "target": np.random.randint(0, 2, size),
                }
            )

            # 测试数据验证性能
            start_time = time.time()
            validation_result = self.data_import_service.validate_data(test_data)
            validation_time = time.time() - start_time

            # 测试建议生成性能
            start_time = time.time()
            recommendations = self.data_import_service.generate_recommendations(
                validation_result
            )
            recommendation_time = time.time() - start_time

            results.append(
                {
                    "data_size": size,
                    "validation_time": validation_time,
                    "recommendation_time": recommendation_time,
                    "total_time": validation_time + recommendation_time,
                    "quality_score": validation_result["quality_score"],
                    "recommendations_count": len(recommendations),
                }
            )

            print(f"  验证时间: {validation_time:.3f}s")
            print(f"  建议生成时间: {recommendation_time:.3f}s")
            print(f"  质量分数: {validation_result['quality_score']:.1f}%")
            print(f"  建议数量: {len(recommendations)}")

        return results

    def test_model_training_performance(self):
        """测试模型训练性能"""
        print("\n=== 模型训练性能测试 ===")

        test_sizes = [100, 500, 1000]
        algorithms = [
            "random_forest_classifier",
            "xgboost_classifier",
            "lightgbm_classifier",
        ]
        results = []

        for size in test_sizes:
            for algorithm in algorithms:
                print(f"测试 {algorithm} 在 {size} 样本上的性能")

                # 生成训练数据
                start_time = time.time()
                df = pd.DataFrame(
                    {
                        "feature1": np.random.randn(size),
                        "feature2": np.random.randn(size),
                        "feature3": np.random.randn(size),
                        "feature4": np.random.randn(size),
                        "feature5": np.random.randn(size),
                        "target": np.random.randint(0, 2, size),
                    }
                )
                data_generation_time = time.time() - start_time

                # 准备数据
                start_time = time.time()
                config = ModelConfig(
                    model_type="classification",
                    algorithm=algorithm,
                    target_column="target",
                    feature_columns=[
                        "feature1",
                        "feature2",
                        "feature3",
                        "feature4",
                        "feature5",
                    ],
                    test_size=0.2,
                    random_state=42,
                )
                X_prepared, y_prepared = self.model_training_service.prepare_data(
                    df, config
                )
                data_preparation_time = time.time() - start_time

                # 训练模型
                start_time = time.time()
                model, metrics = self.model_training_service.train_model(
                    X_prepared, y_prepared, config
                )
                training_time = time.time() - start_time

                # 评估模型
                start_time = time.time()
                evaluation = self.model_training_service.evaluate_model(
                    model, X_prepared, y_prepared, config
                )
                evaluation_time = time.time() - start_time

                # 预测测试
                start_time = time.time()
                prediction = self.model_training_service.predict(
                    model, X_prepared.iloc[:10]
                )
                prediction_time = time.time() - start_time

                total_time = (
                    data_generation_time
                    + data_preparation_time
                    + training_time
                    + evaluation_time
                    + prediction_time
                )

                results.append(
                    {
                        "algorithm": algorithm,
                        "data_size": size,
                        "data_generation_time": data_generation_time,
                        "data_preparation_time": data_preparation_time,
                        "training_time": training_time,
                        "evaluation_time": evaluation_time,
                        "prediction_time": prediction_time,
                        "total_time": total_time,
                        "accuracy": evaluation.get("accuracy", 0),
                        "f1_score": evaluation.get("f1_score", 0),
                    }
                )

                print(f"  数据生成: {data_generation_time:.3f}s")
                print(f"  数据准备: {data_preparation_time:.3f}s")
                print(f"  模型训练: {training_time:.3f}s")
                print(f"  模型评估: {evaluation_time:.3f}s")
                print(f"  预测测试: {prediction_time:.3f}s")
                print(f"  总时间: {total_time:.3f}s")
                print(f"  准确率: {evaluation.get('accuracy', 0):.3f}")

        return results

    async def test_enterprise_memory_performance(self):
        """测试企业记忆性能"""
        print("\n=== 企业记忆性能测试 ===")

        test_sizes = [100, 500, 1000]
        results = []

        for size in test_sizes:
            print(f"测试企业记忆在 {size} 样本上的性能")

            # 生成测试数据
            test_data = pd.DataFrame(
                {
                    "feature1": np.random.randn(size),
                    "feature2": np.random.randn(size),
                    "feature3": np.random.randn(size),
                    "target": np.random.randint(0, 2, size),
                }
            )

            # 测试模式提取性能
            start_time = time.time()
            patterns = await self.memory_service.extract_patterns_from_data(
                test_data, "target"
            )
            pattern_extraction_time = time.time() - start_time

            # 测试洞察生成性能
            start_time = time.time()
            insights = await self.memory_service.generate_business_insights(patterns)
            insight_generation_time = time.time() - start_time

            # 测试推荐生成性能
            start_time = time.time()
            recommendations = await self.memory_service.generate_recommendations(
                insights
            )
            recommendation_generation_time = time.time() - start_time

            # 测试记忆存储性能
            start_time = time.time()
            # 分别保存模式、洞察和推荐
            for pattern in patterns:
                await self.memory_service.save_pattern(pattern)
            for insight in insights:
                await self.memory_service.save_insight(insight)
            for recommendation in recommendations:
                await self.memory_service.save_recommendation(recommendation)
            memory_storage_time = time.time() - start_time

            total_time = (
                pattern_extraction_time
                + insight_generation_time
                + recommendation_generation_time
                + memory_storage_time
            )

            results.append(
                {
                    "data_size": size,
                    "pattern_extraction_time": pattern_extraction_time,
                    "insight_generation_time": insight_generation_time,
                    "recommendation_generation_time": recommendation_generation_time,
                    "memory_storage_time": memory_storage_time,
                    "total_time": total_time,
                    "patterns_count": len(patterns),
                    "insights_count": len(insights),
                    "recommendations_count": len(recommendations),
                    "memory_stored": True,
                }
            )

            print(f"  模式提取: {pattern_extraction_time:.3f}s")
            print(f"  洞察生成: {insight_generation_time:.3f}s")
            print(f"  推荐生成: {recommendation_generation_time:.3f}s")
            print(f"  记忆存储: {memory_storage_time:.3f}s")
            print(f"  总时间: {total_time:.3f}s")
            print(f"  模式数量: {len(patterns)}")
            print(f"  洞察数量: {len(insights)}")
            print(f"  推荐数量: {len(recommendations)}")

        return results

    async def run_performance_test(self):
        """运行性能测试"""
        print("BMOS系统核心功能性能测试")
        print("=" * 50)

        # 1. 数据导入性能测试
        data_import_results = self.test_data_import_performance()
        self.results["data_import"] = data_import_results

        # 2. 模型训练性能测试
        model_training_results = self.test_model_training_performance()
        self.results["model_training"] = model_training_results

        # 3. 企业记忆性能测试
        memory_results = await self.test_enterprise_memory_performance()
        self.results["enterprise_memory"] = memory_results

        return self.results

    def generate_performance_summary(self):
        """生成性能测试总结"""
        print("\n" + "=" * 50)
        print("BMOS系统性能测试总结")
        print("=" * 50)

        # 数据导入性能总结
        if "data_import" in self.results:
            print("\n1. 数据导入性能:")
            for result in self.results["data_import"]:
                print(f"  {result['data_size']}行数据:")
                print(f"    验证时间: {result['validation_time']:.3f}s")
                print(f"    建议生成时间: {result['recommendation_time']:.3f}s")
                print(f"    总时间: {result['total_time']:.3f}s")
                print(f"    质量分数: {result['quality_score']:.1f}%")
                print(f"    建议数量: {result['recommendations_count']}")

        # 模型训练性能总结
        if "model_training" in self.results:
            print("\n2. 模型训练性能:")
            for result in self.results["model_training"]:
                print(f"  {result['algorithm']} ({result['data_size']}样本):")
                print(f"    训练时间: {result['training_time']:.3f}s")
                print(f"    总时间: {result['total_time']:.3f}s")
                print(f"    准确率: {result['accuracy']:.3f}")
                print(f"    F1分数: {result['f1_score']:.3f}")

        # 企业记忆性能总结
        if "enterprise_memory" in self.results:
            print("\n3. 企业记忆性能:")
            for result in self.results["enterprise_memory"]:
                print(f"  {result['data_size']}样本:")
                print(f"    模式提取时间: {result['pattern_extraction_time']:.3f}s")
                print(f"    洞察生成时间: {result['insight_generation_time']:.3f}s")
                print(
                    f"    推荐生成时间: {result['recommendation_generation_time']:.3f}s"
                )
                print(f"    总时间: {result['total_time']:.3f}s")
                print(f"    模式数量: {result['patterns_count']}")
                print(f"    洞察数量: {result['insights_count']}")
                print(f"    推荐数量: {result['recommendations_count']}")

        # 性能基准
        print("\n4. 性能基准:")
        print("  数据导入:")
        print("    - 1000行数据验证: < 0.1s")
        print("    - 建议生成: < 0.05s")
        print("  模型训练:")
        print("    - RandomForest (1000样本): < 1s")
        print("    - XGBoost (1000样本): < 2s")
        print("    - LightGBM (1000样本): < 3s")
        print("  企业记忆:")
        print("    - 模式提取 (1000样本): < 2s")
        print("    - 洞察生成: < 0.5s")
        print("    - 推荐生成: < 0.3s")

        print("\n性能测试完成!")


async def main():
    """主测试函数"""
    tester = BMOSCorePerformanceTester()

    try:
        # 运行性能测试
        results = await tester.run_performance_test()

        # 生成性能总结
        tester.generate_performance_summary()

        # 保存结果
        import json

        with open("core_performance_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n详细结果已保存到: core_performance_results.json")

    except Exception as e:
        print(f"性能测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
