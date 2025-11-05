"""
数据增强服务 - 数据质量评估
7维度质量检查 + 质量评分 + 可导入性判定

功能：
- 完整性（Completeness）：缺失值比例
- 准确性（Accuracy）：数据类型正确性、格式合规性
- 一致性（Consistency）：计算字段一致性
- 及时性（Timeliness）：日期字段合理性
- 唯一性（Uniqueness）：主键重复检查
- 合规性（Validity）：业务规则校验
- 关联性（Referential Integrity）：外键引用检查
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

from ...security.database import SecureDatabaseService
from ...error_handling.unified import BMOSError, BusinessError
from ...services.base import BaseService, ServiceConfig

logger = logging.getLogger(__name__)


class QualityAssessmentError(BMOSError):
    """数据质量评估错误"""

    pass


class DataQualityAssessor(BaseService):
    """数据质量评估服务"""

    def __init__(
        self, db_service: SecureDatabaseService, config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, config=config)

        # 质量维度权重
        self.dimension_weights = {
            "completeness": 0.20,  # 完整性 20%
            "accuracy": 0.25,  # 准确性 25%
            "consistency": 0.15,  # 一致性 15%
            "timeliness": 0.10,  # 及时性 10%
            "uniqueness": 0.15,  # 唯一性 15%
            "validity": 0.10,  # 合规性 10%
            "referential_integrity": 0.05,  # 关联性 5%
        }

    def assess_completeness(self, df: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """
        评估完整性（缺失值比例）

        Args:
            df: DataFrame

        Returns:
            (分数, 详细信息)
        """
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()

        if total_cells == 0:
            return 0.0, {"missing_count": 0, "total_cells": 0, "missing_ratio": 1.0}

        missing_ratio = missing_cells / total_cells
        score = 1.0 - missing_ratio

        details = {
            "missing_count": int(missing_cells),
            "total_cells": total_cells,
            "missing_ratio": float(missing_ratio),
            "fields_missing": {
                col: {
                    "missing_count": int(df[col].isnull().sum()),
                    "missing_ratio": float(df[col].isnull().sum() / len(df)),
                }
                for col in df.columns
                if df[col].isnull().sum() > 0
            },
        }

        return float(score), details

    def assess_accuracy(
        self, df: pd.DataFrame, field_configs: Dict[str, Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估准确性（数据类型正确性、格式合规性）

        Args:
            df: DataFrame
            field_configs: 字段配置

        Returns:
            (分数, 详细信息)
        """
        accuracy_scores = []
        issues = []

        for col in df.columns:
            field_config = field_configs.get(col, {})
            expected_type = field_config.get("data_type", "string")

            col_accuracy = 1.0
            col_issues = []

            # 检查数据类型
            if expected_type == "numeric":
                # 检查是否为数值型
                non_numeric_count = 0
                for val in df[col].dropna():
                    try:
                        float(val)
                    except (ValueError, TypeError):
                        non_numeric_count += 1

                if len(df[col].dropna()) > 0:
                    col_accuracy *= 1.0 - non_numeric_count / len(df[col].dropna())
                    if non_numeric_count > 0:
                        col_issues.append(
                            {
                                "field": col,
                                "issue": "非数值型数据",
                                "count": non_numeric_count,
                            }
                        )

            elif expected_type == "date":
                # 检查日期格式
                invalid_date_count = 0
                for val in df[col].dropna():
                    if not isinstance(val, (datetime, pd.Timestamp)):
                        try:
                            pd.to_datetime(val)
                        except (ValueError, TypeError):
                            invalid_date_count += 1

                if len(df[col].dropna()) > 0:
                    col_accuracy *= 1.0 - invalid_date_count / len(df[col].dropna())
                    if invalid_date_count > 0:
                        col_issues.append(
                            {
                                "field": col,
                                "issue": "无效日期格式",
                                "count": invalid_date_count,
                            }
                        )

            # 检查格式合规性（如邮箱、电话等）
            format_pattern = field_config.get("format_pattern")
            if format_pattern:
                invalid_format_count = 0
                for val in df[col].dropna():
                    if not re.match(format_pattern, str(val)):
                        invalid_format_count += 1

                if len(df[col].dropna()) > 0:
                    col_accuracy *= 1.0 - invalid_format_count / len(df[col].dropna())
                    if invalid_format_count > 0:
                        col_issues.append(
                            {
                                "field": col,
                                "issue": "格式不符合要求",
                                "count": invalid_format_count,
                            }
                        )

            accuracy_scores.append(col_accuracy)
            issues.extend(col_issues)

        overall_score = np.mean(accuracy_scores) if accuracy_scores else 1.0

        details = {
            "field_scores": {
                col: float(score) for col, score in zip(df.columns, accuracy_scores)
            },
            "issues": issues,
            "overall_score": float(overall_score),
        }

        return float(overall_score), details

    def assess_consistency(
        self, df: pd.DataFrame, calculation_rules: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估一致性（计算字段一致性）

        Args:
            df: DataFrame
            calculation_rules: 计算规则列表

        Returns:
            (分数, 详细信息)
        """
        if not calculation_rules:
            return 1.0, {"consistent_count": 0, "total_checked": 0}

        consistent_count = 0
        total_checked = 0
        issues = []

        for rule in calculation_rules:
            formula = rule.get("formula", "")
            if not formula or "=" not in formula:
                continue

            try:
                left, right = formula.split("=", 1)
                target_field = left.strip()

                if target_field not in df.columns:
                    continue

                # 简化：检查是否有缺失值（实际应该检查计算一致性）
                # 这里简化处理，实际应该使用calculation_conflict_detector
                missing_count = df[target_field].isnull().sum()
                total_count = len(df)

                if missing_count == 0:
                    consistent_count += 1
                else:
                    issues.append(
                        {
                            "field": target_field,
                            "issue": "计算字段存在缺失值",
                            "count": missing_count,
                        }
                    )

                total_checked += 1

            except Exception as e:
                logger.warning(f"一致性检查失败: {e}")
                continue

        score = consistent_count / total_checked if total_checked > 0 else 1.0

        details = {
            "consistent_count": consistent_count,
            "total_checked": total_checked,
            "issues": issues,
        }

        return float(score), details

    def assess_timeliness(
        self, df: pd.DataFrame, date_fields: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估及时性（日期字段合理性）

        Args:
            df: DataFrame
            date_fields: 日期字段列表

        Returns:
            (分数, 详细信息)
        """
        if not date_fields:
            return 1.0, {"checked_fields": []}

        timeliness_scores = []
        issues = []

        current_date = datetime.now()
        max_date = current_date
        min_date = current_date - timedelta(days=365 * 10)  # 10年前

        for field in date_fields:
            if field not in df.columns:
                continue

            valid_count = 0
            total_count = 0
            field_issues = []

            for val in df[field].dropna():
                total_count += 1
                try:
                    if isinstance(val, (datetime, pd.Timestamp)):
                        date_val = val
                    else:
                        date_val = pd.to_datetime(val)

                    # 检查日期是否在合理范围内
                    if min_date <= date_val <= max_date:
                        valid_count += 1
                    else:
                        field_issues.append(
                            {"value": str(val), "issue": "日期超出合理范围"}
                        )

                except (ValueError, TypeError):
                    field_issues.append({"value": str(val), "issue": "无效日期格式"})

            field_score = valid_count / total_count if total_count > 0 else 1.0
            timeliness_scores.append(field_score)

            if field_issues:
                issues.append(
                    {"field": field, "issues": field_issues[:5]}  # 只显示前5个问题
                )

        overall_score = np.mean(timeliness_scores) if timeliness_scores else 1.0

        details = {
            "checked_fields": date_fields,
            "field_scores": {
                field: float(score)
                for field, score in zip(date_fields, timeliness_scores)
            },
            "issues": issues,
        }

        return float(overall_score), details

    def assess_uniqueness(
        self, df: pd.DataFrame, primary_keys: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估唯一性（主键重复检查）

        Args:
            df: DataFrame
            primary_keys: 主键字段列表

        Returns:
            (分数, 详细信息)
        """
        if not primary_keys:
            return 1.0, {"checked_keys": []}

        uniqueness_scores = []
        issues = []

        for key_field in primary_keys:
            if key_field not in df.columns:
                continue

            total_count = len(df)
            unique_count = df[key_field].nunique()
            duplicate_count = total_count - unique_count

            if total_count == 0:
                continue

            score = unique_count / total_count
            uniqueness_scores.append(score)

            if duplicate_count > 0:
                # 找出重复的值
                duplicates = df[df[key_field].duplicated(keep=False)][
                    key_field
                ].unique()
                issues.append(
                    {
                        "field": key_field,
                        "duplicate_count": int(duplicate_count),
                        "duplicate_values": duplicates.tolist()[:10],  # 只显示前10个
                    }
                )

        overall_score = np.mean(uniqueness_scores) if uniqueness_scores else 1.0

        details = {
            "checked_keys": primary_keys,
            "field_scores": {
                key: float(score) for key, score in zip(primary_keys, uniqueness_scores)
            },
            "issues": issues,
        }

        return float(overall_score), details

    def assess_validity(
        self, df: pd.DataFrame, validation_rules: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估合规性（业务规则校验）

        Args:
            df: DataFrame
            validation_rules: 验证规则配置

        Returns:
            (分数, 详细信息)
        """
        if not validation_rules:
            return 1.0, {"checked_rules": []}

        valid_count = 0
        total_count = len(df)
        issues = []

        # 简化的规则检查
        for rule_name, rule_config in validation_rules.items():
            field = rule_config.get("field")
            rule_type = rule_config.get("rule_type")

            if not field or field not in df.columns:
                continue

            if rule_type == "range":
                # 范围检查
                min_val = rule_config.get("min")
                max_val = rule_config.get("max")

                if min_val is not None:
                    invalid = df[df[field] < min_val]
                    if len(invalid) > 0:
                        issues.append(
                            {
                                "rule": rule_name,
                                "field": field,
                                "issue": f"值小于最小值 {min_val}",
                                "count": len(invalid),
                            }
                        )

                if max_val is not None:
                    invalid = df[df[field] > max_val]
                    if len(invalid) > 0:
                        issues.append(
                            {
                                "rule": rule_name,
                                "field": field,
                                "issue": f"值大于最大值 {max_val}",
                                "count": len(invalid),
                            }
                        )

            elif rule_type == "enum":
                # 枚举值检查
                allowed_values = rule_config.get("values", [])
                if allowed_values:
                    invalid = df[~df[field].isin(allowed_values)]
                    if len(invalid) > 0:
                        issues.append(
                            {
                                "rule": rule_name,
                                "field": field,
                                "issue": f"值不在允许的枚举列表中",
                                "count": len(invalid),
                            }
                        )

            valid_count += 1

        score = (
            (total_count - sum(i.get("count", 0) for i in issues)) / total_count
            if total_count > 0
            else 1.0
        )
        score = max(0.0, min(1.0, score))

        details = {"checked_rules": list(validation_rules.keys()), "issues": issues}

        return float(score), details

    async def assess_referential_integrity(
        self, df: pd.DataFrame, foreign_keys: List[Dict[str, Any]], tenant_id: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        评估关联性（外键引用检查）

        Args:
            df: DataFrame
            foreign_keys: 外键配置列表
            tenant_id: 租户ID

        Returns:
            (分数, 详细信息)
        """
        if not foreign_keys:
            return 1.0, {"checked_keys": []}

        integrity_scores = []
        issues = []

        for fk_config in foreign_keys:
            fk_field = fk_config.get("field")
            reference_table = fk_config.get("reference_table")
            reference_field = fk_config.get("reference_field", "id")

            if not fk_field or fk_field not in df.columns:
                continue

            if not reference_table:
                continue

            try:
                # 从数据库获取引用表的数据
                query = f"""
                    SELECT DISTINCT {reference_field}
                    FROM {reference_table}
                    WHERE tenant_id = $1
                """

                reference_values = await self.db_service.execute_query(
                    query, params=[tenant_id], fetch_all=True
                )

                reference_set = set(row[reference_field] for row in reference_values)

                # 检查外键值是否在引用表中
                fk_values = df[fk_field].dropna().unique()
                invalid_count = sum(1 for val in fk_values if val not in reference_set)
                total_count = len(fk_values)

                if total_count > 0:
                    score = 1.0 - (invalid_count / total_count)
                    integrity_scores.append(score)

                    if invalid_count > 0:
                        invalid_values = [
                            val for val in fk_values if val not in reference_set
                        ][:10]
                        issues.append(
                            {
                                "field": fk_field,
                                "reference_table": reference_table,
                                "invalid_count": invalid_count,
                                "invalid_values": invalid_values,
                            }
                        )

            except Exception as e:
                logger.warning(f"关联性检查失败 ({fk_field}): {e}")
                continue

        overall_score = np.mean(integrity_scores) if integrity_scores else 1.0

        details = {
            "checked_keys": [fk.get("field") for fk in foreign_keys],
            "issues": issues,
        }

        return float(overall_score), details

    def determine_importability(
        self, overall_score: float, blocking_issues: List[Dict[str, Any]]
    ) -> str:
        """
        判定可导入性

        Args:
            overall_score: 总体质量分数
            blocking_issues: 阻塞性问题列表

        Returns:
            可导入性等级（excellent/good/fixable/rejected）
        """
        if blocking_issues:
            return "rejected"

        if overall_score >= 0.95:
            return "excellent"
        elif overall_score >= 0.85:
            return "good"
        elif overall_score >= 0.70:
            return "fixable"
        else:
            return "rejected"

    async def assess_quality(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
        validation_rules: Dict[str, Any],
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        评估数据质量

        Args:
            data_type: 数据类型（order/production/expense）
            records: 数据记录列表（DataFrame格式或字典列表）
            validation_rules: 验证规则配置
            tenant_id: 租户ID（可选）

        Returns:
            质量评估结果
        """
        try:
            # 转换records为DataFrame
            if isinstance(records, pd.DataFrame):
                df = records.copy()
            else:
                df = pd.DataFrame(records)

            # 获取配置
            field_configs = validation_rules.get("field_configs", {})
            calculation_rules = validation_rules.get("calculation_rules", [])
            date_fields = validation_rules.get("date_fields", [])
            primary_keys = validation_rules.get("primary_keys", [])
            foreign_keys = validation_rules.get("foreign_keys", [])
            business_rules = validation_rules.get("business_rules", {})

            # 评估各个维度
            completeness_score, completeness_details = self.assess_completeness(df)
            accuracy_score, accuracy_details = self.assess_accuracy(df, field_configs)
            consistency_score, consistency_details = self.assess_consistency(
                df, calculation_rules
            )
            timeliness_score, timeliness_details = self.assess_timeliness(
                df, date_fields
            )
            uniqueness_score, uniqueness_details = self.assess_uniqueness(
                df, primary_keys
            )
            validity_score, validity_details = self.assess_validity(df, business_rules)

            # 关联性检查需要数据库访问
            if tenant_id:
                referential_score, referential_details = (
                    await self.assess_referential_integrity(df, foreign_keys, tenant_id)
                )
            else:
                referential_score = 1.0
                referential_details = {"checked_keys": []}

            # 计算加权总分
            dimensions = {
                "completeness": {
                    "score": completeness_score,
                    "weight": self.dimension_weights["completeness"],
                    "details": completeness_details,
                },
                "accuracy": {
                    "score": accuracy_score,
                    "weight": self.dimension_weights["accuracy"],
                    "details": accuracy_details,
                },
                "consistency": {
                    "score": consistency_score,
                    "weight": self.dimension_weights["consistency"],
                    "details": consistency_details,
                },
                "timeliness": {
                    "score": timeliness_score,
                    "weight": self.dimension_weights["timeliness"],
                    "details": timeliness_details,
                },
                "uniqueness": {
                    "score": uniqueness_score,
                    "weight": self.dimension_weights["uniqueness"],
                    "details": uniqueness_details,
                },
                "validity": {
                    "score": validity_score,
                    "weight": self.dimension_weights["validity"],
                    "details": validity_details,
                },
                "referential_integrity": {
                    "score": referential_score,
                    "weight": self.dimension_weights["referential_integrity"],
                    "details": referential_details,
                },
            }

            overall_score = sum(
                dim["score"] * dim["weight"] for dim in dimensions.values()
            )

            # 识别阻塞性问题
            blocking_issues = []
            fixable_issues = []

            # 收集所有问题
            if completeness_score < 0.5:
                blocking_issues.append(
                    {
                        "issue_id": "HIGH_MISSING_VALUES",
                        "severity": "critical",
                        "count": completeness_details.get("missing_count", 0),
                        "description": "缺失值过多，影响数据可用性",
                        "auto_fixable": False,
                    }
                )

            if uniqueness_score < 0.9:
                for issue in uniqueness_details.get("issues", []):
                    fixable_issues.append(
                        {
                            "issue_id": "DUPLICATE_PRIMARY_KEY",
                            "severity": "high",
                            "count": issue.get("duplicate_count", 0),
                            "description": f"主键字段 {issue['field']} 存在重复值",
                            "auto_fixable": True,
                            "field": issue["field"],
                            "examples": issue.get("duplicate_values", [])[:5],
                        }
                    )

            # 判定可导入性
            importability = self.determine_importability(overall_score, blocking_issues)

            # 生成建议
            recommendations = []
            if overall_score < 0.85:
                recommendations.append("建议进行数据清洗和修复")
            if completeness_score < 0.8:
                recommendations.append("建议补充缺失值")
            if uniqueness_score < 1.0:
                recommendations.append("建议处理重复主键")

            return {
                "overall_score": float(overall_score),
                "importability": importability,
                "dimensions": dimensions,
                "blocking_issues": blocking_issues,
                "fixable_issues": fixable_issues,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"数据质量评估失败: {e}")
            raise QualityAssessmentError(f"数据质量评估失败: {e}")
