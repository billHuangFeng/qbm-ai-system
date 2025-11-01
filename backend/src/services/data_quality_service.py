"""
数据质量检查工具
提供全面的数据质量评估、监控和报告功能
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class QualityMetric(Enum):
    """质量指标枚举"""
    COMPLETENESS = "completeness"      # 完整性
    ACCURACY = "accuracy"              # 准确性
    CONSISTENCY = "consistency"        # 一致性
    VALIDITY = "validity"              # 有效性
    UNIQUENESS = "uniqueness"          # 唯一性
    TIMELINESS = "timeliness"          # 及时性
    RELEVANCE = "relevance"            # 相关性

class QualityLevel(Enum):
    """质量等级枚举"""
    EXCELLENT = "excellent"    # 95%+
    GOOD = "good"            # 85-95%
    FAIR = "fair"            # 70-85%
    POOR = "poor"            # <70%

class IssueSeverity(Enum):
    """问题严重程度枚举"""
    CRITICAL = "critical"    # 严重
    HIGH = "high"           # 高
    MEDIUM = "medium"       # 中等
    LOW = "low"             # 低
    INFO = "info"           # 信息

@dataclass
class QualityIssue:
    """质量问题"""
    id: str
    metric: QualityMetric
    severity: IssueSeverity
    description: str
    affected_records: int
    affected_fields: List[str]
    suggested_fix: Optional[str] = None
    detected_at: datetime = None

@dataclass
class QualityReport:
    """质量报告"""
    dataset_id: str
    dataset_name: str
    total_records: int
    total_fields: int
    overall_score: float
    quality_level: QualityLevel
    metrics_scores: Dict[QualityMetric, float]
    issues: List[QualityIssue]
    recommendations: List[str]
    generated_at: datetime
    processing_time: float

@dataclass
class QualityRule:
    """质量规则"""
    id: str
    name: str
    description: str
    metric: QualityMetric
    rule_type: str  # 'threshold', 'pattern', 'statistical', 'custom'
    rule_config: Dict[str, Any]
    severity: IssueSeverity
    is_active: bool = True

class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service
        
        # 质量规则
        self.quality_rules = self._load_quality_rules()
        
        # 统计信息
        self.stats_cache = {}
    
    async def check_data_quality(
        self,
        dataset_id: str,
        dataset_name: str,
        data: Union[pd.DataFrame, Dict[str, Any]],
        custom_rules: Optional[List[QualityRule]] = None
    ) -> QualityReport:
        """检查数据质量"""
        start_time = datetime.now()
        
        try:
            # 转换数据格式
            if isinstance(data, dict):
                df = self._convert_dict_to_dataframe(data)
            else:
                df = data.copy()
            
            # 基本统计信息
            total_records = len(df)
            total_fields = len(df.columns)
            
            # 计算各项质量指标
            metrics_scores = {}
            all_issues = []
            
            # 完整性检查
            completeness_score, completeness_issues = await self._check_completeness(df)
            metrics_scores[QualityMetric.COMPLETENESS] = completeness_score
            all_issues.extend(completeness_issues)
            
            # 准确性检查
            accuracy_score, accuracy_issues = await self._check_accuracy(df)
            metrics_scores[QualityMetric.ACCURACY] = accuracy_score
            all_issues.extend(accuracy_issues)
            
            # 一致性检查
            consistency_score, consistency_issues = await self._check_consistency(df)
            metrics_scores[QualityMetric.CONSISTENCY] = consistency_score
            all_issues.extend(consistency_issues)
            
            # 有效性检查
            validity_score, validity_issues = await self._check_validity(df)
            metrics_scores[QualityMetric.VALIDITY] = validity_score
            all_issues.extend(validity_issues)
            
            # 唯一性检查
            uniqueness_score, uniqueness_issues = await self._check_uniqueness(df)
            metrics_scores[QualityMetric.UNIQUENESS] = uniqueness_score
            all_issues.extend(uniqueness_issues)
            
            # 及时性检查
            timeliness_score, timeliness_issues = await self._check_timeliness(df)
            metrics_scores[QualityMetric.TIMELINESS] = timeliness_score
            all_issues.extend(timeliness_issues)
            
            # 相关性检查
            relevance_score, relevance_issues = await self._check_relevance(df)
            metrics_scores[QualityMetric.RELEVANCE] = relevance_score
            all_issues.extend(relevance_issues)
            
            # 应用自定义规则
            if custom_rules:
                custom_issues = await self._apply_custom_rules(df, custom_rules)
                all_issues.extend(custom_issues)
            
            # 计算总体质量分数
            overall_score = np.mean(list(metrics_scores.values()))
            
            # 确定质量等级
            if overall_score >= 0.95:
                quality_level = QualityLevel.EXCELLENT
            elif overall_score >= 0.85:
                quality_level = QualityLevel.GOOD
            elif overall_score >= 0.70:
                quality_level = QualityLevel.FAIR
            else:
                quality_level = QualityLevel.POOR
            
            # 生成建议
            recommendations = await self._generate_recommendations(metrics_scores, all_issues)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QualityReport(
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                total_records=total_records,
                total_fields=total_fields,
                overall_score=overall_score,
                quality_level=quality_level,
                metrics_scores=metrics_scores,
                issues=all_issues,
                recommendations=recommendations,
                generated_at=datetime.now(),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Data quality check failed: {str(e)}")
            raise
    
    def _convert_dict_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """将字典转换为DataFrame"""
        try:
            if "sheets" in data:
                # Excel数据
                all_data = []
                for sheet_name, sheet_data in data["sheets"].items():
                    headers = sheet_data.get("headers", [])
                    rows = sheet_data.get("rows", [])
                    
                    for row in rows:
                        row_dict = {}
                        for i, cell in enumerate(row):
                            if i < len(headers):
                                row_dict[headers[i]] = cell
                        all_data.append(row_dict)
                
                return pd.DataFrame(all_data)
            
            elif "rows" in data:
                # CSV或JSON数据
                headers = data.get("headers", [])
                rows = data.get("rows", [])
                
                data_list = []
                for row in rows:
                    row_dict = {}
                    for i, cell in enumerate(row):
                        if i < len(headers):
                            row_dict[headers[i]] = cell
                    data_list.append(row_dict)
                
                return pd.DataFrame(data_list)
            
            else:
                raise ValueError("不支持的数据格式")
                
        except Exception as e:
            logger.error(f"Failed to convert dict to DataFrame: {str(e)}")
            raise
    
    async def _check_completeness(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据完整性"""
        try:
            issues = []
            total_cells = df.size
            missing_cells = df.isnull().sum().sum()
            
            # 计算完整性分数
            completeness_score = 1 - (missing_cells / total_cells) if total_cells > 0 else 1.0
            
            # 检查每个字段的缺失情况
            for column in df.columns:
                missing_count = df[column].isnull().sum()
                missing_percentage = missing_count / len(df) if len(df) > 0 else 0
                
                if missing_percentage > 0.1:  # 缺失率超过10%
                    severity = IssueSeverity.CRITICAL if missing_percentage > 0.5 else IssueSeverity.HIGH
                    
                    issue = QualityIssue(
                        id=f"completeness_{column}_{datetime.now().timestamp()}",
                        metric=QualityMetric.COMPLETENESS,
                        severity=severity,
                        description=f"字段 {column} 缺失 {missing_count} 个值 ({missing_percentage:.1%})",
                        affected_records=missing_count,
                        affected_fields=[column],
                        suggested_fix=f"检查数据源，补充缺失的 {column} 值",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
            
            return completeness_score, issues
            
        except Exception as e:
            logger.error(f"Completeness check failed: {str(e)}")
            return 0.0, []
    
    async def _check_accuracy(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据准确性"""
        try:
            issues = []
            accuracy_scores = []
            
            for column in df.columns:
                column_data = df[column].dropna()
                
                if len(column_data) == 0:
                    accuracy_scores.append(0.0)
                    continue
                
                # 根据数据类型检查准确性
                if pd.api.types.is_numeric_dtype(column_data):
                    # 数值类型：检查异常值
                    score, column_issues = await self._check_numeric_accuracy(column_data, column)
                    accuracy_scores.append(score)
                    issues.extend(column_issues)
                
                elif pd.api.types.is_datetime64_any_dtype(column_data):
                    # 日期类型：检查日期格式和合理性
                    score, column_issues = await self._check_datetime_accuracy(column_data, column)
                    accuracy_scores.append(score)
                    issues.extend(column_issues)
                
                elif pd.api.types.is_string_dtype(column_data):
                    # 字符串类型：检查格式和内容
                    score, column_issues = await self._check_string_accuracy(column_data, column)
                    accuracy_scores.append(score)
                    issues.extend(column_issues)
                
                else:
                    # 其他类型
                    accuracy_scores.append(1.0)
            
            overall_accuracy = np.mean(accuracy_scores) if accuracy_scores else 1.0
            return overall_accuracy, issues
            
        except Exception as e:
            logger.error(f"Accuracy check failed: {str(e)}")
            return 0.0, []
    
    async def _check_numeric_accuracy(self, data: pd.Series, column: str) -> Tuple[float, List[QualityIssue]]:
        """检查数值类型准确性"""
        try:
            issues = []
            
            # 使用IQR方法检测异常值
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_percentage = len(outliers) / len(data) if len(data) > 0 else 0
            
            if outlier_percentage > 0.05:  # 异常值超过5%
                severity = IssueSeverity.HIGH if outlier_percentage > 0.2 else IssueSeverity.MEDIUM
                
                issue = QualityIssue(
                    id=f"accuracy_outlier_{column}_{datetime.now().timestamp()}",
                    metric=QualityMetric.ACCURACY,
                    severity=severity,
                    description=f"字段 {column} 发现 {len(outliers)} 个异常值 ({outlier_percentage:.1%})",
                    affected_records=len(outliers),
                    affected_fields=[column],
                    suggested_fix=f"检查 {column} 字段的异常值，确认是否为数据错误",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 计算准确性分数
            accuracy_score = 1 - outlier_percentage
            
            return accuracy_score, issues
            
        except Exception as e:
            logger.error(f"Numeric accuracy check failed: {str(e)}")
            return 0.0, []
    
    async def _check_datetime_accuracy(self, data: pd.Series, column: str) -> Tuple[float, List[QualityIssue]]:
        """检查日期类型准确性"""
        try:
            issues = []
            
            # 检查未来日期
            now = datetime.now()
            future_dates = data[data > now]
            future_percentage = len(future_dates) / len(data) if len(data) > 0 else 0
            
            if future_percentage > 0.1:  # 未来日期超过10%
                issue = QualityIssue(
                    id=f"accuracy_future_date_{column}_{datetime.now().timestamp()}",
                    metric=QualityMetric.ACCURACY,
                    severity=IssueSeverity.MEDIUM,
                    description=f"字段 {column} 发现 {len(future_dates)} 个未来日期 ({future_percentage:.1%})",
                    affected_records=len(future_dates),
                    affected_fields=[column],
                    suggested_fix=f"检查 {column} 字段的未来日期是否合理",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 检查过于久远的日期
            old_date = datetime(1900, 1, 1)
            old_dates = data[data < old_date]
            old_percentage = len(old_dates) / len(data) if len(data) > 0 else 0
            
            if old_percentage > 0.05:  # 过于久远的日期超过5%
                issue = QualityIssue(
                    id=f"accuracy_old_date_{column}_{datetime.now().timestamp()}",
                    metric=QualityMetric.ACCURACY,
                    severity=IssueSeverity.MEDIUM,
                    description=f"字段 {column} 发现 {len(old_dates)} 个过于久远的日期 ({old_percentage:.1%})",
                    affected_records=len(old_dates),
                    affected_fields=[column],
                    suggested_fix=f"检查 {column} 字段的日期是否合理",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 计算准确性分数
            accuracy_score = 1 - (future_percentage + old_percentage)
            
            return accuracy_score, issues
            
        except Exception as e:
            logger.error(f"Datetime accuracy check failed: {str(e)}")
            return 0.0, []
    
    async def _check_string_accuracy(self, data: pd.Series, column: str) -> Tuple[float, List[QualityIssue]]:
        """检查字符串类型准确性"""
        try:
            issues = []
            
            # 检查空字符串
            empty_strings = data[data.str.strip() == ""]
            empty_percentage = len(empty_strings) / len(data) if len(data) > 0 else 0
            
            if empty_percentage > 0.1:  # 空字符串超过10%
                issue = QualityIssue(
                    id=f"accuracy_empty_string_{column}_{datetime.now().timestamp()}",
                    metric=QualityMetric.ACCURACY,
                    severity=IssueSeverity.MEDIUM,
                    description=f"字段 {column} 发现 {len(empty_strings)} 个空字符串 ({empty_percentage:.1%})",
                    affected_records=len(empty_strings),
                    affected_fields=[column],
                    suggested_fix=f"检查 {column} 字段的空字符串是否合理",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 检查特殊字符
            special_chars = data[data.str.contains(r'[^\w\s\u4e00-\u9fff]', regex=True, na=False)]
            special_percentage = len(special_chars) / len(data) if len(data) > 0 else 0
            
            if special_percentage > 0.2:  # 特殊字符超过20%
                issue = QualityIssue(
                    id=f"accuracy_special_chars_{column}_{datetime.now().timestamp()}",
                    metric=QualityMetric.ACCURACY,
                    severity=IssueSeverity.LOW,
                    description=f"字段 {column} 发现 {len(special_chars)} 个包含特殊字符的值 ({special_percentage:.1%})",
                    affected_records=len(special_chars),
                    affected_fields=[column],
                    suggested_fix=f"检查 {column} 字段的特殊字符是否合理",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 计算准确性分数
            accuracy_score = 1 - (empty_percentage + special_percentage * 0.5)
            
            return accuracy_score, issues
            
        except Exception as e:
            logger.error(f"String accuracy check failed: {str(e)}")
            return 0.0, []
    
    async def _check_consistency(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据一致性"""
        try:
            issues = []
            consistency_scores = []
            
            # 检查字段间的一致性
            for i, col1 in enumerate(df.columns):
                for j, col2 in enumerate(df.columns):
                    if i >= j:
                        continue
                    
                    # 检查数值字段的一致性
                    if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                        score, column_issues = await self._check_numeric_consistency(df[col1], df[col2], col1, col2)
                        consistency_scores.append(score)
                        issues.extend(column_issues)
                    
                    # 检查分类字段的一致性
                    elif pd.api.types.is_string_dtype(df[col1]) and pd.api.types.is_string_dtype(df[col2]):
                        score, column_issues = await self._check_categorical_consistency(df[col1], df[col2], col1, col2)
                        consistency_scores.append(score)
                        issues.extend(column_issues)
            
            # 检查重复记录
            duplicate_count = df.duplicated().sum()
            duplicate_percentage = duplicate_count / len(df) if len(df) > 0 else 0
            
            if duplicate_percentage > 0.05:  # 重复记录超过5%
                issue = QualityIssue(
                    id=f"consistency_duplicates_{datetime.now().timestamp()}",
                    metric=QualityMetric.CONSISTENCY,
                    severity=IssueSeverity.HIGH if duplicate_percentage > 0.2 else IssueSeverity.MEDIUM,
                    description=f"发现 {duplicate_count} 条重复记录 ({duplicate_percentage:.1%})",
                    affected_records=duplicate_count,
                    affected_fields=list(df.columns),
                    suggested_fix="检查并处理重复记录",
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            # 计算一致性分数
            consistency_score = 1 - duplicate_percentage
            if consistency_scores:
                consistency_score = np.mean([consistency_score] + consistency_scores)
            
            return consistency_score, issues
            
        except Exception as e:
            logger.error(f"Consistency check failed: {str(e)}")
            return 0.0, []
    
    async def _check_numeric_consistency(
        self, 
        col1: pd.Series, 
        col2: pd.Series, 
        col1_name: str, 
        col2_name: str
    ) -> Tuple[float, List[QualityIssue]]:
        """检查数值字段一致性"""
        try:
            issues = []
            
            # 计算相关系数
            correlation = col1.corr(col2)
            
            if pd.notna(correlation) and abs(correlation) > 0.8:
                # 高相关字段，检查逻辑一致性
                if col1_name.lower() in ['price', 'amount'] and col2_name.lower() in ['quantity', 'count']:
                    # 价格和数量应该成正比
                    ratio = col1 / col2
                    ratio_std = ratio.std()
                    
                    if ratio_std > ratio.mean() * 0.5:  # 标准差过大
                        issue = QualityIssue(
                            id=f"consistency_ratio_{col1_name}_{col2_name}_{datetime.now().timestamp()}",
                            metric=QualityMetric.CONSISTENCY,
                            severity=IssueSeverity.MEDIUM,
                            description=f"字段 {col1_name} 和 {col2_name} 的比例关系不一致",
                            affected_records=len(col1),
                            affected_fields=[col1_name, col2_name],
                            suggested_fix=f"检查 {col1_name} 和 {col2_name} 的逻辑关系",
                            detected_at=datetime.now()
                        )
                        issues.append(issue)
            
            return 1.0, issues
            
        except Exception as e:
            logger.error(f"Numeric consistency check failed: {str(e)}")
            return 0.0, []
    
    async def _check_categorical_consistency(
        self, 
        col1: pd.Series, 
        col2: pd.Series, 
        col1_name: str, 
        col2_name: str
    ) -> Tuple[float, List[QualityIssue]]:
        """检查分类字段一致性"""
        try:
            issues = []
            
            # 检查分类组合的合理性
            if col1_name.lower() in ['status', 'state'] and col2_name.lower() in ['category', 'type']:
                # 状态和类别的组合检查
                cross_tab = pd.crosstab(col1, col2)
                
                # 检查是否有不合理的组合
                for status in cross_tab.index:
                    for category in cross_tab.columns:
                        count = cross_tab.loc[status, category]
                        if count > 0:
                            # 这里可以添加具体的业务逻辑检查
                            pass
            
            return 1.0, issues
            
        except Exception as e:
            logger.error(f"Categorical consistency check failed: {str(e)}")
            return 0.0, []
    
    async def _check_validity(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据有效性"""
        try:
            issues = []
            validity_scores = []
            
            for column in df.columns:
                column_data = df[column].dropna()
                
                if len(column_data) == 0:
                    validity_scores.append(0.0)
                    continue
                
                # 根据字段名推断验证规则
                validation_rules = self._get_validation_rules(column)
                
                invalid_count = 0
                for rule in validation_rules:
                    invalid_records = await self._apply_validation_rule(column_data, rule)
                    invalid_count += len(invalid_records)
                    
                    if len(invalid_records) > 0:
                        issue = QualityIssue(
                            id=f"validity_{rule['type']}_{column}_{datetime.now().timestamp()}",
                            metric=QualityMetric.VALIDITY,
                            severity=rule['severity'],
                            description=f"字段 {column} 有 {len(invalid_records)} 个值不符合 {rule['description']}",
                            affected_records=len(invalid_records),
                            affected_fields=[column],
                            suggested_fix=f"修正 {column} 字段中不符合 {rule['description']} 的值",
                            detected_at=datetime.now()
                        )
                        issues.append(issue)
                
                # 计算有效性分数
                validity_score = 1 - (invalid_count / len(column_data)) if len(column_data) > 0 else 1.0
                validity_scores.append(validity_score)
            
            overall_validity = np.mean(validity_scores) if validity_scores else 1.0
            return overall_validity, issues
            
        except Exception as e:
            logger.error(f"Validity check failed: {str(e)}")
            return 0.0, []
    
    def _get_validation_rules(self, column_name: str) -> List[Dict[str, Any]]:
        """获取字段验证规则"""
        rules = []
        column_lower = column_name.lower()
        
        # 邮箱验证
        if 'email' in column_lower or 'mail' in column_lower:
            rules.append({
                'type': 'email',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'description': '邮箱格式',
                'severity': IssueSeverity.HIGH
            })
        
        # 手机号验证
        elif 'phone' in column_lower or 'mobile' in column_lower:
            rules.append({
                'type': 'phone',
                'pattern': r'^1[3-9]\d{9}$',
                'description': '手机号格式',
                'severity': IssueSeverity.HIGH
            })
        
        # 身份证验证
        elif 'id_card' in column_lower or 'idcard' in column_lower:
            rules.append({
                'type': 'id_card',
                'pattern': r'^\d{17}[\dXx]$',
                'description': '身份证格式',
                'severity': IssueSeverity.HIGH
            })
        
        # 金额验证
        elif 'amount' in column_lower or 'price' in column_lower or 'money' in column_lower:
            rules.append({
                'type': 'amount',
                'min_value': 0,
                'max_value': 999999999,
                'description': '金额范围',
                'severity': IssueSeverity.MEDIUM
            })
        
        # 状态验证
        elif 'status' in column_lower or 'state' in column_lower:
            rules.append({
                'type': 'enum',
                'allowed_values': ['active', 'inactive', 'pending', 'completed', 'cancelled'],
                'description': '状态值',
                'severity': IssueSeverity.MEDIUM
            })
        
        return rules
    
    async def _apply_validation_rule(self, data: pd.Series, rule: Dict[str, Any]) -> List[int]:
        """应用验证规则"""
        try:
            invalid_indices = []
            
            if rule['type'] == 'email' or rule['type'] == 'phone' or rule['type'] == 'id_card':
                # 正则表达式验证
                pattern = rule['pattern']
                for idx, value in data.items():
                    if pd.notna(value) and not re.match(pattern, str(value)):
                        invalid_indices.append(idx)
            
            elif rule['type'] == 'amount':
                # 数值范围验证
                min_value = rule.get('min_value', float('-inf'))
                max_value = rule.get('max_value', float('inf'))
                for idx, value in data.items():
                    if pd.notna(value):
                        try:
                            num_value = float(value)
                            if not (min_value <= num_value <= max_value):
                                invalid_indices.append(idx)
                        except (ValueError, TypeError):
                            invalid_indices.append(idx)
            
            elif rule['type'] == 'enum':
                # 枚举值验证
                allowed_values = rule['allowed_values']
                for idx, value in data.items():
                    if pd.notna(value) and str(value).lower() not in [v.lower() for v in allowed_values]:
                        invalid_indices.append(idx)
            
            return invalid_indices
            
        except Exception as e:
            logger.error(f"Validation rule application failed: {str(e)}")
            return []
    
    async def _check_uniqueness(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据唯一性"""
        try:
            issues = []
            
            # 检查主键唯一性
            primary_key_candidates = []
            for column in df.columns:
                column_lower = column.lower()
                if any(keyword in column_lower for keyword in ['id', 'key', 'code', 'number']):
                    primary_key_candidates.append(column)
            
            uniqueness_scores = []
            for column in primary_key_candidates:
                unique_count = df[column].nunique()
                total_count = len(df)
                uniqueness_ratio = unique_count / total_count if total_count > 0 else 1.0
                
                uniqueness_scores.append(uniqueness_ratio)
                
                if uniqueness_ratio < 0.95:  # 唯一性低于95%
                    duplicate_count = total_count - unique_count
                    issue = QualityIssue(
                        id=f"uniqueness_{column}_{datetime.now().timestamp()}",
                        metric=QualityMetric.UNIQUENESS,
                        severity=IssueSeverity.HIGH if uniqueness_ratio < 0.8 else IssueSeverity.MEDIUM,
                        description=f"字段 {column} 有 {duplicate_count} 个重复值 (唯一性: {uniqueness_ratio:.1%})",
                        affected_records=duplicate_count,
                        affected_fields=[column],
                        suggested_fix=f"检查并修正 {column} 字段的重复值",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
            
            # 计算总体唯一性分数
            overall_uniqueness = np.mean(uniqueness_scores) if uniqueness_scores else 1.0
            
            return overall_uniqueness, issues
            
        except Exception as e:
            logger.error(f"Uniqueness check failed: {str(e)}")
            return 0.0, []
    
    async def _check_timeliness(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据及时性"""
        try:
            issues = []
            
            # 查找时间相关字段
            time_columns = []
            for column in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[column]):
                    time_columns.append(column)
                elif any(keyword in column.lower() for keyword in ['date', 'time', 'created', 'updated']):
                    time_columns.append(column)
            
            timeliness_scores = []
            for column in time_columns:
                try:
                    # 转换为日期时间
                    if not pd.api.types.is_datetime64_any_dtype(df[column]):
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    
                    # 检查数据的新鲜度
                    now = datetime.now()
                    recent_data = df[column].dropna()
                    
                    if len(recent_data) > 0:
                        # 计算数据年龄
                        data_age = (now - recent_data.max()).days
                        
                        # 根据字段类型确定合理的年龄阈值
                        if 'created' in column.lower() or 'updated' in column.lower():
                            threshold = 30  # 创建/更新时间应该在30天内
                        elif 'date' in column.lower():
                            threshold = 365  # 日期数据应该在1年内
                        else:
                            threshold = 90  # 其他时间字段默认90天
                        
                        if data_age > threshold:
                            issue = QualityIssue(
                                id=f"timeliness_{column}_{datetime.now().timestamp()}",
                                metric=QualityMetric.TIMELINESS,
                                severity=IssueSeverity.MEDIUM if data_age > threshold * 2 else IssueSeverity.LOW,
                                description=f"字段 {column} 的数据已过期 {data_age} 天",
                                affected_records=len(recent_data),
                                affected_fields=[column],
                                suggested_fix=f"更新 {column} 字段的数据",
                                detected_at=datetime.now()
                            )
                            issues.append(issue)
                        
                        # 计算及时性分数
                        timeliness_score = max(0, 1 - (data_age / threshold))
                        timeliness_scores.append(timeliness_score)
                
                except Exception as e:
                    logger.error(f"Timeliness check failed for column {column}: {str(e)}")
                    timeliness_scores.append(0.0)
            
            # 计算总体及时性分数
            overall_timeliness = np.mean(timeliness_scores) if timeliness_scores else 1.0
            
            return overall_timeliness, issues
            
        except Exception as e:
            logger.error(f"Timeliness check failed: {str(e)}")
            return 0.0, []
    
    async def _check_relevance(self, df: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """检查数据相关性"""
        try:
            issues = []
            
            # 检查字段间的相关性
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) > 1:
                correlation_matrix = df[numeric_columns].corr()
                
                # 查找高相关性的字段对
                high_correlations = []
                for i in range(len(numeric_columns)):
                    for j in range(i+1, len(numeric_columns)):
                        corr_value = correlation_matrix.iloc[i, j]
                        if abs(corr_value) > 0.9:  # 高相关性
                            high_correlations.append({
                                'col1': numeric_columns[i],
                                'col2': numeric_columns[j],
                                'correlation': corr_value
                            })
                
                # 检查是否有冗余字段
                if len(high_correlations) > len(numeric_columns) * 0.3:  # 高相关性字段对过多
                    issue = QualityIssue(
                        id=f"relevance_high_correlation_{datetime.now().timestamp()}",
                        metric=QualityMetric.RELEVANCE,
                        severity=IssueSeverity.LOW,
                        description=f"发现 {len(high_correlations)} 对高相关性字段，可能存在冗余",
                        affected_records=len(df),
                        affected_fields=list(numeric_columns),
                        suggested_fix="检查并移除冗余字段",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
            
            # 检查字段的变异系数
            relevance_scores = []
            for column in numeric_columns:
                column_data = df[column].dropna()
                if len(column_data) > 1:
                    cv = column_data.std() / column_data.mean() if column_data.mean() != 0 else 0
                    
                    if cv < 0.01:  # 变异系数过小，数据变化不大
                        issue = QualityIssue(
                            id=f"relevance_low_variance_{column}_{datetime.now().timestamp()}",
                            metric=QualityMetric.RELEVANCE,
                            severity=IssueSeverity.LOW,
                            description=f"字段 {column} 的变异系数过小 ({cv:.4f})，数据变化不大",
                            affected_records=len(column_data),
                            affected_fields=[column],
                            suggested_fix=f"检查 {column} 字段是否必要",
                            detected_at=datetime.now()
                        )
                        issues.append(issue)
                    
                    # 计算相关性分数
                    relevance_score = min(1.0, cv * 100)  # 变异系数越大，相关性越高
                    relevance_scores.append(relevance_score)
            
            # 计算总体相关性分数
            overall_relevance = np.mean(relevance_scores) if relevance_scores else 1.0
            
            return overall_relevance, issues
            
        except Exception as e:
            logger.error(f"Relevance check failed: {str(e)}")
            return 0.0, []
    
    async def _apply_custom_rules(self, df: pd.DataFrame, custom_rules: List[QualityRule]) -> List[QualityIssue]:
        """应用自定义规则"""
        try:
            issues = []
            
            for rule in custom_rules:
                if not rule.is_active:
                    continue
                
                # 根据规则类型应用不同的检查逻辑
                if rule.rule_type == 'threshold':
                    issues.extend(await self._apply_threshold_rule(df, rule))
                elif rule.rule_type == 'pattern':
                    issues.extend(await self._apply_pattern_rule(df, rule))
                elif rule.rule_type == 'statistical':
                    issues.extend(await self._apply_statistical_rule(df, rule))
                elif rule.rule_type == 'custom':
                    issues.extend(await self._apply_custom_rule(df, rule))
            
            return issues
            
        except Exception as e:
            logger.error(f"Custom rules application failed: {str(e)}")
            return []
    
    async def _apply_threshold_rule(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """应用阈值规则"""
        try:
            issues = []
            config = rule.rule_config
            
            field_name = config.get('field')
            if field_name not in df.columns:
                return issues
            
            threshold = config.get('threshold')
            operator = config.get('operator', '>')
            
            field_data = df[field_name].dropna()
            if len(field_data) == 0:
                return issues
            
            # 根据操作符检查阈值
            if operator == '>':
                violations = field_data[field_data > threshold]
            elif operator == '<':
                violations = field_data[field_data < threshold]
            elif operator == '>=':
                violations = field_data[field_data >= threshold]
            elif operator == '<=':
                violations = field_data[field_data <= threshold]
            elif operator == '==':
                violations = field_data[field_data == threshold]
            elif operator == '!=':
                violations = field_data[field_data != threshold]
            else:
                return issues
            
            if len(violations) > 0:
                violation_percentage = len(violations) / len(field_data)
                
                issue = QualityIssue(
                    id=f"custom_threshold_{rule.id}_{datetime.now().timestamp()}",
                    metric=rule.metric,
                    severity=rule.severity,
                    description=f"字段 {field_name} 有 {len(violations)} 个值违反规则: {field_name} {operator} {threshold}",
                    affected_records=len(violations),
                    affected_fields=[field_name],
                    suggested_fix=rule.description,
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Threshold rule application failed: {str(e)}")
            return []
    
    async def _apply_pattern_rule(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """应用模式规则"""
        try:
            issues = []
            config = rule.rule_config
            
            field_name = config.get('field')
            if field_name not in df.columns:
                return issues
            
            pattern = config.get('pattern')
            if not pattern:
                return issues
            
            field_data = df[field_name].dropna()
            if len(field_data) == 0:
                return issues
            
            # 应用正则表达式模式
            violations = field_data[~field_data.astype(str).str.match(pattern, na=False)]
            
            if len(violations) > 0:
                issue = QualityIssue(
                    id=f"custom_pattern_{rule.id}_{datetime.now().timestamp()}",
                    metric=rule.metric,
                    severity=rule.severity,
                    description=f"字段 {field_name} 有 {len(violations)} 个值不符合模式: {pattern}",
                    affected_records=len(violations),
                    affected_fields=[field_name],
                    suggested_fix=rule.description,
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Pattern rule application failed: {str(e)}")
            return []
    
    async def _apply_statistical_rule(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """应用统计规则"""
        try:
            issues = []
            config = rule.rule_config
            
            field_name = config.get('field')
            if field_name not in df.columns:
                return issues
            
            field_data = df[field_name].dropna()
            if len(field_data) == 0:
                return issues
            
            # 计算统计指标
            mean_val = field_data.mean()
            std_val = field_data.std()
            z_scores = np.abs((field_data - mean_val) / std_val) if std_val > 0 else np.zeros(len(field_data))
            
            # 检查异常值
            threshold = config.get('z_score_threshold', 3)
            outliers = field_data[z_scores > threshold]
            
            if len(outliers) > 0:
                issue = QualityIssue(
                    id=f"custom_statistical_{rule.id}_{datetime.now().timestamp()}",
                    metric=rule.metric,
                    severity=rule.severity,
                    description=f"字段 {field_name} 有 {len(outliers)} 个统计异常值 (Z-score > {threshold})",
                    affected_records=len(outliers),
                    affected_fields=[field_name],
                    suggested_fix=rule.description,
                    detected_at=datetime.now()
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Statistical rule application failed: {str(e)}")
            return []
    
    async def _apply_custom_rule(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """应用自定义规则"""
        try:
            issues = []
            config = rule.rule_config
            
            # 这里可以实现更复杂的自定义规则逻辑
            # 例如：跨字段验证、业务逻辑检查等
            
            return issues
            
        except Exception as e:
            logger.error(f"Custom rule application failed: {str(e)}")
            return []
    
    async def _generate_recommendations(
        self, 
        metrics_scores: Dict[QualityMetric, float], 
        issues: List[QualityIssue]
    ) -> List[str]:
        """生成改进建议"""
        try:
            recommendations = []
            
            # 基于质量指标生成建议
            for metric, score in metrics_scores.items():
                if score < 0.8:  # 分数低于80%
                    if metric == QualityMetric.COMPLETENESS:
                        recommendations.append("建议检查数据源，补充缺失的数据")
                    elif metric == QualityMetric.ACCURACY:
                        recommendations.append("建议检查数据录入过程，提高数据准确性")
                    elif metric == QualityMetric.CONSISTENCY:
                        recommendations.append("建议统一数据格式和标准")
                    elif metric == QualityMetric.VALIDITY:
                        recommendations.append("建议加强数据验证规则")
                    elif metric == QualityMetric.UNIQUENESS:
                        recommendations.append("建议检查并处理重复数据")
                    elif metric == QualityMetric.TIMELINESS:
                        recommendations.append("建议更新过期的数据")
                    elif metric == QualityMetric.RELEVANCE:
                        recommendations.append("建议检查数据字段的相关性")
            
            # 基于问题严重程度生成建议
            critical_issues = [issue for issue in issues if issue.severity == IssueSeverity.CRITICAL]
            high_issues = [issue for issue in issues if issue.severity == IssueSeverity.HIGH]
            
            if critical_issues:
                recommendations.append(f"优先处理 {len(critical_issues)} 个严重问题")
            
            if high_issues:
                recommendations.append(f"及时处理 {len(high_issues)} 个高优先级问题")
            
            # 基于问题类型生成建议
            issue_types = {}
            for issue in issues:
                issue_type = issue.metric.value
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in issue_types.items():
                if count > 5:  # 某种类型的问题过多
                    recommendations.append(f"重点关注 {issue_type} 相关问题，共 {count} 个")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return []
    
    def _load_quality_rules(self) -> List[QualityRule]:
        """加载质量规则"""
        # 这里可以从数据库或配置文件加载规则
        # 暂时返回默认规则
        return [
            QualityRule(
                id="rule_001",
                name="数值范围检查",
                description="检查数值字段是否在合理范围内",
                metric=QualityMetric.VALIDITY,
                rule_type="threshold",
                rule_config={
                    "field": "amount",
                    "operator": ">=",
                    "threshold": 0
                },
                severity=IssueSeverity.HIGH
            ),
            QualityRule(
                id="rule_002",
                name="邮箱格式检查",
                description="检查邮箱字段格式是否正确",
                metric=QualityMetric.VALIDITY,
                rule_type="pattern",
                rule_config={
                    "field": "email",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                severity=IssueSeverity.HIGH
            )
        ]

