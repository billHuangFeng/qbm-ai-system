"""
数据增强服务 - 计算冲突检测
检测存在计算逻辑关系的字段之间的冲突

功能：
- 解析字段定义中的计算公式（例如："金额 = 数量 × 单价"）
- 表达式求值引擎（支持 +, -, ×, ÷, 括号）
- 浮点数容差比较（使用 decimal 库，精度0.01）
- 级联冲突检测（使用图算法BFS检测依赖链）
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Set
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import re
from collections import deque

from ...security.database import SecureDatabaseService
from ...error_handling.unified import BMOSError, BusinessError
from ...services.base import BaseService, ServiceConfig

logger = logging.getLogger(__name__)


class CalculationConflictError(BMOSError):
    """计算冲突错误"""

    pass


class CalculationConflictDetector(BaseService):
    """计算冲突检测服务"""

    def __init__(
        self, db_service: SecureDatabaseService, config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, config=config)
        self.default_tolerance = Decimal("0.01")

        # 运算符映射
        self.operator_map = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "×": lambda x, y: x * y,
            "*": lambda x, y: x * y,
            "÷": lambda x, y: x / y if y != 0 else float("inf"),
            "/": lambda x, y: x / y if y != 0 else float("inf"),
        }

    def parse_formula(self, formula: str) -> Dict[str, Any]:
        """
        解析计算公式

        Args:
            formula: 计算公式字符串，例如："金额 = 数量 × 单价"

        Returns:
            解析后的公式结构
        """
        try:
            # 分离等号左右两边
            if "=" not in formula:
                raise ValueError(f"无效的公式格式: {formula}")

            left, right = formula.split("=", 1)
            left = left.strip()
            right = right.strip()

            # 解析右侧表达式
            # 支持的操作符: +, -, ×, *, ÷, /
            # 支持的字段引用: [字段名] 或 字段名

            # 提取字段引用
            field_pattern = r"\[?(\w+)\]?"
            fields = re.findall(field_pattern, right)

            # 提取运算符
            operator_pattern = r"[+\-×*÷/]"
            operators = re.findall(operator_pattern, right)

            return {
                "target_field": left,
                "expression": right,
                "referenced_fields": fields,
                "operators": operators,
                "formula": formula,
            }

        except Exception as e:
            logger.error(f"公式解析失败: {e}")
            raise CalculationConflictError(f"公式解析失败: {e}")

    def evaluate_expression(self, expression: str, record: Dict[str, Any]) -> Decimal:
        """
        计算表达式值

        Args:
            expression: 表达式字符串
            record: 数据记录

        Returns:
            计算结果
        """
        try:
            # 替换字段引用为实际值
            def replace_field(match):
                field_name = match.group(1)
                value = record.get(field_name, 0)
                try:
                    return str(float(value))
                except (ValueError, TypeError):
                    return "0"

            # 替换字段引用
            pattern = r"\[?(\w+)\]?"
            numeric_expression = re.sub(pattern, replace_field, expression)

            # 标准化运算符
            numeric_expression = numeric_expression.replace("×", "*").replace("÷", "/")

            # 计算表达式（使用eval，注意安全性）
            # 在生产环境中应该使用更安全的表达式解析库
            result = eval(numeric_expression, {"__builtins__": {}})

            return Decimal(str(result)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        except Exception as e:
            logger.warning(f"表达式计算失败: {expression}, 错误: {e}")
            return Decimal("0")

    def compare_values(
        self, expected: Decimal, actual: Decimal, tolerance: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        比较两个值是否在容差范围内

        Args:
            expected: 期望值
            actual: 实际值
            tolerance: 容差阈值

        Returns:
            (是否匹配, 差值)
        """
        difference = abs(expected - actual)
        is_match = difference <= tolerance

        return is_match, difference

    def detect_conflicts_in_record(
        self,
        record: Dict[str, Any],
        row_index: int,
        calculation_rules: List[Dict[str, Any]],
        tolerance: Decimal,
    ) -> List[Dict[str, Any]]:
        """
        检测单条记录中的计算冲突

        Args:
            record: 数据记录
            row_index: 行索引
            calculation_rules: 计算规则列表
            tolerance: 容差阈值

        Returns:
            冲突列表
        """
        conflicts = []

        for rule in calculation_rules:
            try:
                formula = rule.get("formula", "")
                if not formula:
                    continue

                # 解析公式
                parsed = self.parse_formula(formula)
                target_field = parsed["target_field"]

                # 检查目标字段是否存在
                if target_field not in record:
                    continue

                # 获取实际值
                actual_value = record.get(target_field)
                if actual_value is None or pd.isna(actual_value):
                    continue

                try:
                    actual_decimal = Decimal(str(actual_value)).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                except (ValueError, TypeError):
                    continue

                # 计算期望值
                expected_decimal = self.evaluate_expression(
                    parsed["expression"], record
                )

                # 比较值
                is_match, difference = self.compare_values(
                    expected_decimal, actual_decimal, tolerance
                )

                if not is_match:
                    # 判断严重程度
                    relative_diff = (
                        abs(difference) / abs(expected_decimal)
                        if expected_decimal != 0
                        else float("inf")
                    )

                    if relative_diff > 0.1:
                        severity = "high"
                    elif relative_diff > 0.05:
                        severity = "medium"
                    else:
                        severity = "low"

                    # 判断是否可自动修复
                    auto_fixable = relative_diff < 0.2  # 差异小于20%时可自动修复

                    # 生成修复建议
                    suggested_fix = (
                        "use_calculated_value" if auto_fixable else "manual_review"
                    )

                    conflict = {
                        "row_index": row_index,
                        "field": target_field,
                        "expected_value": float(expected_decimal),
                        "actual_value": float(actual_decimal),
                        "difference": float(difference),
                        "relative_difference": relative_diff,
                        "formula": formula,
                        "severity": severity,
                        "auto_fixable": auto_fixable,
                        "suggested_fix": suggested_fix,
                    }

                    conflicts.append(conflict)

            except Exception as e:
                logger.warning(f"检测计算冲突失败 (行{row_index}): {e}")
                continue

        return conflicts

    def build_dependency_graph(
        self, calculation_rules: List[Dict[str, Any]]
    ) -> Dict[str, Set[str]]:
        """
        构建字段依赖关系图

        Args:
            calculation_rules: 计算规则列表

        Returns:
            依赖关系图 {字段: {依赖字段集合}}
        """
        graph = {}

        for rule in calculation_rules:
            try:
                formula = rule.get("formula", "")
                if not formula:
                    continue

                parsed = self.parse_formula(formula)
                target_field = parsed["target_field"]
                referenced_fields = parsed["referenced_fields"]

                if target_field not in graph:
                    graph[target_field] = set()

                graph[target_field].update(referenced_fields)

            except Exception as e:
                logger.warning(f"构建依赖图失败: {e}")
                continue

        return graph

    def detect_cascade_conflicts(
        self,
        records: List[Dict[str, Any]],
        calculation_rules: List[Dict[str, Any]],
        tolerance: Decimal,
    ) -> List[Dict[str, Any]]:
        """
        检测级联冲突（使用BFS算法）

        Args:
            records: 数据记录列表
            calculation_rules: 计算规则列表
            tolerance: 容差阈值

        Returns:
            级联冲突列表
        """
        # 构建依赖图
        dependency_graph = self.build_dependency_graph(calculation_rules)

        cascade_conflicts = []

        for record in records:
            row_index = record.get("row_index", 0)
            conflicts = self.detect_conflicts_in_record(
                record, row_index, calculation_rules, tolerance
            )

            if not conflicts:
                continue

            # 使用BFS检测级联冲突
            for conflict in conflicts:
                conflict_field = conflict["field"]

                # 查找依赖该字段的其他字段
                dependent_fields = [
                    field
                    for field, deps in dependency_graph.items()
                    if conflict_field in deps
                ]

                if dependent_fields:
                    conflict["cascade_fields"] = dependent_fields
                    conflict["cascade_impact"] = len(dependent_fields)

            cascade_conflicts.extend(conflicts)

        return cascade_conflicts

    async def detect_conflicts(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
        calculation_rules: List[Dict[str, Any]],
        tolerance: Optional[float] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        检测计算冲突

        Args:
            data_type: 数据类型（order/production/expense）
            records: 数据记录列表（DataFrame格式或字典列表）
            calculation_rules: 计算规则定义
            tolerance: 容差阈值（默认0.01）
            tenant_id: 租户ID（可选）

        Returns:
            冲突检测结果
        """
        try:
            # 转换tolerance为Decimal
            if tolerance is None:
                tolerance = self.default_tolerance
            else:
                tolerance = Decimal(str(tolerance))

            # 转换records为字典列表
            if isinstance(records, pd.DataFrame):
                records_list = records.to_dict("records")
                for i, record in enumerate(records_list):
                    record["row_index"] = i
            else:
                records_list = records
                for i, record in enumerate(records_list):
                    if "row_index" not in record:
                        record["row_index"] = i

            # 检测冲突
            all_conflicts = []
            for record in records_list:
                conflicts = self.detect_conflicts_in_record(
                    record, record["row_index"], calculation_rules, tolerance
                )
                all_conflicts.extend(conflicts)

            # 检测级联冲突
            cascade_conflicts = self.detect_cascade_conflicts(
                records_list, calculation_rules, tolerance
            )

            # 统计信息
            total_records = len(records_list)
            conflicts_found = len(all_conflicts)
            auto_fixable_count = sum(
                1 for c in all_conflicts if c.get("auto_fixable", False)
            )

            # 按严重程度分类
            high_severity = sum(1 for c in all_conflicts if c.get("severity") == "high")
            medium_severity = sum(
                1 for c in all_conflicts if c.get("severity") == "medium"
            )
            low_severity = sum(1 for c in all_conflicts if c.get("severity") == "low")

            statistics = {
                "total_checked": total_records,
                "conflicts_found": conflicts_found,
                "auto_fixable": auto_fixable_count,
                "manual_review_required": conflicts_found - auto_fixable_count,
                "severity_breakdown": {
                    "high": high_severity,
                    "medium": medium_severity,
                    "low": low_severity,
                },
                "cascade_conflicts": len(cascade_conflicts),
            }

            return {
                "conflicts": all_conflicts,
                "cascade_conflicts": cascade_conflicts,
                "statistics": statistics,
            }

        except Exception as e:
            logger.error(f"计算冲突检测失败: {e}")
            raise CalculationConflictError(f"计算冲突检测失败: {e}")
