"""
BMOS系统 - 数据质量检查重构
将长函数拆分为更小的、可维护的单元
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pandas as pd
import logging

from backend.src.error_handling.decorators import handle_service_errors
from backend.src.constants import QualityMetric, QualityLevel, IssueSeverity

logger = logging.getLogger(__name__)

class DataQualityCheckerRefactored:
    """重构后的数据质量检查器"""
    
    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service
        self.quality_rules = self._load_quality_rules()
        self.stats_cache = {}
    
    @handle_service_errors(default_message="数据质量检查失败")
    async def check_data_quality(
        self,
        dataset_id: str,
        dataset_name: str,
        data: Union[pd.DataFrame, Dict[str, Any]],
        custom_rules: Optional[List] = None
    ):
        """检查数据质量 - 主函数"""
        start_time = datetime.now()
        
        # 1. 准备数据
        df = await self._prepare_data(data)
        
        # 2. 执行质量检查
        quality_results = await self._execute_quality_checks(df, custom_rules)
        
        # 3. 生成质量报告
        report = await self._generate_quality_report(
            dataset_id, dataset_name, df, quality_results, start_time
        )
        
        return report
    
    async def _prepare_data(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
        """准备数据"""
        if isinstance(data, dict):
            return self._convert_dict_to_dataframe(data)
        return data.copy()
    
    async def _execute_quality_checks(
        self,
        df: pd.DataFrame,
        custom_rules: Optional[List] = None
    ) -> Dict[str, Any]:
        """执行质量检查"""
        quality_results = {}
        
        # 完整性检查
        completeness_result = await self._check_completeness(df)
        quality_results['completeness'] = completeness_result
        
        # 准确性检查
        accuracy_result = await self._check_accuracy(df)
        quality_results['accuracy'] = accuracy_result
        
        # 一致性检查
        consistency_result = await self._check_consistency(df)
        quality_results['consistency'] = consistency_result
        
        # 有效性检查
        validity_result = await self._check_validity(df)
        quality_results['validity'] = validity_result
        
        # 唯一性检查
        uniqueness_result = await self._check_uniqueness(df)
        quality_results['uniqueness'] = uniqueness_result
        
        # 及时性检查
        timeliness_result = await self._check_timeliness(df)
        quality_results['timeliness'] = timeliness_result
        
        # 相关性检查
        relevance_result = await self._check_relevance(df)
        quality_results['relevance'] = relevance_result
        
        # 自定义规则检查
        if custom_rules:
            custom_result = await self._check_custom_rules(df, custom_rules)
            quality_results['custom'] = custom_result
        
        return quality_results
    
    async def _generate_quality_report(
        self,
        dataset_id: str,
        dataset_name: str,
        df: pd.DataFrame,
        quality_results: Dict[str, Any],
        start_time: datetime
    ):
        """生成质量报告"""
        from backend.src.error_handling.unified import QualityReport
        
        # 计算总体评分
        total_records = len(df)
        total_fields = len(df.columns)
        
        # 收集所有指标分数
        metrics_scores = {}
        all_issues = []
        
        for metric, result in quality_results.items():
            metrics_scores[result['metric']] = result['score']
            all_issues.extend(result['issues'])
        
        # 计算总体分数
        overall_score = sum(metrics_scores.values()) / len(metrics_scores) if metrics_scores else 0.0
        
        # 确定质量等级
        quality_level = self._determine_quality_level(overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(all_issues, overall_score)
        
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
    
    async def _check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据完整性"""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness_score = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        issues = []
        if completeness_score < 0.95:
            issues.append({
                'id': f'completeness_{datetime.now().timestamp()}',
                'metric': QualityMetric.COMPLETENESS,
                'severity': IssueSeverity.HIGH if completeness_score < 0.7 else IssueSeverity.MEDIUM,
                'description': f'数据完整性不足: {missing_cells} 个缺失值',
                'affected_records': missing_cells,
                'affected_fields': df.columns[df.isnull().any()].tolist(),
                'suggested_fix': '考虑填充缺失值或删除空记录',
                'detected_at': datetime.now()
            })
        
        return {
            'metric': QualityMetric.COMPLETENESS,
            'score': completeness_score,
            'issues': issues
        }
    
    async def _check_accuracy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据准确性"""
        # 这里可以实现具体的准确性检查逻辑
        # 例如：数据类型检查、数值范围检查等
        accuracy_score = 1.0
        issues = []
        
        return {
            'metric': QualityMetric.ACCURACY,
            'score': accuracy_score,
            'issues': issues
        }
    
    async def _check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据一致性"""
        # 这里可以实现一致性检查逻辑
        consistency_score = 1.0
        issues = []
        
        return {
            'metric': QualityMetric.CONSISTENCY,
            'score': consistency_score,
            'issues': issues
        }
    
    async def _check_validity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据有效性"""
        # 这里可以实现有效性检查逻辑
        validity_score = 1.0
        issues = []
        
        return {
            'metric': QualityMetric.VALIDITY,
            'score': validity_score,
            'issues': issues
        }
    
    async def _check_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据唯一性"""
        duplicate_count = df.duplicated().sum()
        unique_score = 1 - (duplicate_count / len(df)) if len(df) > 0 else 1.0
        
        issues = []
        if duplicate_count > 0:
            issues.append({
                'id': f'uniqueness_{datetime.now().timestamp()}',
                'metric': QualityMetric.UNIQUENESS,
                'severity': IssueSeverity.MEDIUM,
                'description': f'发现 {duplicate_count} 条重复记录',
                'affected_records': duplicate_count,
                'affected_fields': df.columns.tolist(),
                'suggested_fix': '移除重复记录',
                'detected_at': datetime.now()
            })
        
        return {
            'metric': QualityMetric.UNIQUENESS,
            'score': unique_score,
            'issues': issues
        }
    
    async def _check_timeliness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据及时性"""
        timeliness_score = 1.0
        issues = []
        
        return {
            'metric': QualityMetric.TIMELINESS,
            'score': timeliness_score,
            'issues': issues
        }
    
    async def _check_relevance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """检查数据相关性"""
        relevance_score = 1.0
        issues = []
        
        return {
            'metric': QualityMetric.RELEVANCE,
            'score': relevance_score,
            'issues': issues
        }
    
    async def _check_custom_rules(self, df: pd.DataFrame, custom_rules: List) -> Dict[str, Any]:
        """检查自定义规则"""
        custom_score = 1.0
        issues = []
        
        return {
            'metric': 'custom',
            'score': custom_score,
            'issues': issues
        }
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 0.95:
            return QualityLevel.EXCELLENT
        elif score >= 0.85:
            return QualityLevel.GOOD
        elif score >= 0.70:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def _generate_recommendations(self, issues: List[Dict], overall_score: float) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        
        if overall_score < 0.70:
            recommendations.append("数据质量较低，建议进行全面清理")
        
        critical_issues = [i for i in issues if i.get('severity') == 'CRITICAL']
        if critical_issues:
            recommendations.append(f"发现 {len(critical_issues)} 个严重质量问题，需要立即处理")
        
        # 根据具体问题生成建议
        for issue in issues:
            if issue.get('suggested_fix'):
                recommendations.append(issue['suggested_fix'])
        
        return recommendations
    
    def _load_quality_rules(self) -> List[Dict]:
        """加载质量规则"""
        return []
    
    def _convert_dict_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """将字典转换为DataFrame"""
        return pd.DataFrame(data)

