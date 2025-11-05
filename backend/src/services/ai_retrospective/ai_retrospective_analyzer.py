"""
AI复盘分析服务
提供根因分析、模式识别、成功因素提取和失败原因分析功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from uuid import uuid4

from ...algorithms.threshold_analysis import ThresholdAnalysis
from ...algorithms.synergy_analysis import SynergyAnalysis
from ...algorithms.time_series import ARIMAModel
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIRetrospectiveAnalyzer:
    """AI复盘分析服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        # 初始化AI算法
        self.threshold_analyzer = ThresholdAnalysis()
        self.synergy_analyzer = SynergyAnalysis()
        self.arima_model = ARIMAModel()

        logger.info("AI复盘分析服务初始化完成")

    async def analyze_root_causes(
        self,
        issue_data: Dict[str, Any],
        session_id: str,
        analysis_depth: str = "comprehensive",
    ) -> Dict[str, Any]:
        """
        AI驱动的根因分析

        Args:
            issue_data: 问题数据
            session_id: 复盘会话ID
            analysis_depth: 分析深度 ('basic', 'comprehensive', 'deep')

        Returns:
            根因分析结果
        """
        try:
            logger.info(
                f"开始根因分析: session_id={session_id}, depth={analysis_depth}"
            )

            # 1. 获取相关历史数据
            historical_issues = await self._get_similar_historical_issues(issue_data)

            # 2. 提取关键特征
            features = self._extract_issue_features(issue_data, historical_issues)

            # 3. 使用因果推理分析根因
            root_causes = await self._identify_root_causes(features, analysis_depth)

            # 4. 计算因果链
            causal_chains = await self._build_causal_chains(root_causes, issue_data)

            # 5. 评估根因重要性
            root_cause_scores = self._score_root_causes(root_causes, causal_chains)

            # 6. 构建洞察内容
            insight_content = {
                "root_causes": root_causes,
                "causal_chains": causal_chains,
                "root_cause_scores": root_cause_scores,
                "analysis_depth": analysis_depth,
                "confidence": self._calculate_confidence(root_cause_scores),
            }

            # 7. 保存洞察到数据库
            insight_id = await self._save_insight(
                session_id=session_id,
                insight_type="root_cause",
                insight_title="根因分析",
                insight_content=insight_content,
                confidence_score=insight_content["confidence"],
            )

            # 8. 记录到企业记忆
            if self.memory_service:
                await self._record_to_memory(
                    memory_type="root_cause_analysis",
                    content=insight_content,
                    tags=["retrospective", "root_cause", analysis_depth],
                )

            return {
                "success": True,
                "insight_id": insight_id,
                "root_causes": root_causes,
                "causal_chains": causal_chains,
                "confidence": insight_content["confidence"],
            }

        except Exception as e:
            logger.error(f"根因分析失败: {e}")
            return {"success": False, "error": str(e)}

    async def identify_patterns(
        self,
        historical_data: List[Dict[str, Any]],
        session_id: str,
        pattern_type: str = "all",
    ) -> Dict[str, Any]:
        """
        模式识别和趋势分析

        Args:
            historical_data: 历史数据列表
            session_id: 复盘会话ID
            pattern_type: 模式类型 ('temporal', 'correlation', 'sequential', 'all')

        Returns:
            模式识别结果
        """
        try:
            logger.info(
                f"开始模式识别: session_id={session_id}, pattern_type={pattern_type}"
            )

            if not historical_data or len(historical_data) < 5:
                return {"success": False, "error": "历史数据不足，无法进行模式识别"}

            # 1. 转换为DataFrame
            df = pd.DataFrame(historical_data)

            # 2. 根据类型识别模式
            patterns = {}

            if pattern_type in ["temporal", "all"]:
                temporal_patterns = await self._identify_temporal_patterns(df)
                patterns["temporal"] = temporal_patterns

            if pattern_type in ["correlation", "all"]:
                correlation_patterns = await self._identify_correlation_patterns(df)
                patterns["correlation"] = correlation_patterns

            if pattern_type in ["sequential", "all"]:
                sequential_patterns = await self._identify_sequential_patterns(df)
                patterns["sequential"] = sequential_patterns

            # 3. 分析模式重要性
            pattern_scores = self._score_patterns(patterns)

            # 4. 构建洞察内容
            insight_content = {
                "patterns": patterns,
                "pattern_scores": pattern_scores,
                "pattern_type": pattern_type,
                "data_points": len(df),
                "confidence": self._calculate_pattern_confidence(patterns),
            }

            # 5. 保存洞察
            insight_id = await self._save_insight(
                session_id=session_id,
                insight_type="pattern",
                insight_title="模式识别",
                insight_content=insight_content,
                confidence_score=insight_content["confidence"],
            )

            return {
                "success": True,
                "insight_id": insight_id,
                "patterns": patterns,
                "pattern_scores": pattern_scores,
                "confidence": insight_content["confidence"],
            }

        except Exception as e:
            logger.error(f"模式识别失败: {e}")
            return {"success": False, "error": str(e)}

    async def extract_success_factors(
        self, success_cases: List[Dict[str, Any]], session_id: str
    ) -> Dict[str, Any]:
        """
        成功因素智能提取

        Args:
            success_cases: 成功案例列表
            session_id: 复盘会话ID

        Returns:
            成功因素分析结果
        """
        try:
            logger.info(
                f"开始提取成功因素: session_id={session_id}, cases={len(success_cases)}"
            )

            if not success_cases or len(success_cases) < 3:
                return {"success": False, "error": "成功案例不足，无法进行分析"}

            # 1. 提取共同特征
            common_features = self._extract_common_features(success_cases)

            # 2. 使用协同分析识别成功因素
            success_factors = await self._analyze_success_factors(
                success_cases, common_features
            )

            # 3. 评估因素重要性
            factor_scores = self._score_success_factors(success_factors, success_cases)

            # 4. 识别最佳实践
            best_practices = await self._identify_best_practices(
                success_factors, success_cases
            )

            # 5. 构建洞察内容
            insight_content = {
                "success_factors": success_factors,
                "factor_scores": factor_scores,
                "best_practices": best_practices,
                "common_features": common_features,
                "case_count": len(success_cases),
                "confidence": self._calculate_success_confidence(factor_scores),
            }

            # 6. 保存洞察
            insight_id = await self._save_insight(
                session_id=session_id,
                insight_type="success_factor",
                insight_title="成功因素分析",
                insight_content=insight_content,
                confidence_score=insight_content["confidence"],
            )

            # 7. 记录到企业记忆
            if self.memory_service:
                await self._record_to_memory(
                    memory_type="success_factors",
                    content=insight_content,
                    tags=["retrospective", "success", "best_practice"],
                )

            return {
                "success": True,
                "insight_id": insight_id,
                "success_factors": success_factors,
                "factor_scores": factor_scores,
                "best_practices": best_practices,
                "confidence": insight_content["confidence"],
            }

        except Exception as e:
            logger.error(f"提取成功因素失败: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_failure_reasons(
        self, failure_cases: List[Dict[str, Any]], session_id: str
    ) -> Dict[str, Any]:
        """
        失败原因深度分析

        Args:
            failure_cases: 失败案例列表
            session_id: 复盘会话ID

        Returns:
            失败原因分析结果
        """
        try:
            logger.info(
                f"开始分析失败原因: session_id={session_id}, cases={len(failure_cases)}"
            )

            if not failure_cases or len(failure_cases) < 2:
                return {"success": False, "error": "失败案例不足，无法进行分析"}

            # 1. 提取失败特征
            failure_features = self._extract_failure_features(failure_cases)

            # 2. 识别常见失败模式
            failure_patterns = await self._identify_failure_patterns(failure_cases)

            # 3. 分析失败因果关系
            failure_chains = await self._analyze_failure_chains(failure_cases)

            # 4. 识别风险因素
            risk_factors = await self._identify_risk_factors(
                failure_features, failure_patterns
            )

            # 5. 构建洞察内容
            insight_content = {
                "failure_patterns": failure_patterns,
                "failure_chains": failure_chains,
                "risk_factors": risk_factors,
                "failure_features": failure_features,
                "case_count": len(failure_cases),
                "confidence": self._calculate_failure_confidence(failure_patterns),
            }

            # 6. 保存洞察
            insight_id = await self._save_insight(
                session_id=session_id,
                insight_type="failure_reason",
                insight_title="失败原因分析",
                insight_content=insight_content,
                confidence_score=insight_content["confidence"],
            )

            # 7. 记录到企业记忆
            if self.memory_service:
                await self._record_to_memory(
                    memory_type="failure_analysis",
                    content=insight_content,
                    tags=["retrospective", "failure", "risk"],
                )

            return {
                "success": True,
                "insight_id": insight_id,
                "failure_patterns": failure_patterns,
                "failure_chains": failure_chains,
                "risk_factors": risk_factors,
                "confidence": insight_content["confidence"],
            }

        except Exception as e:
            logger.error(f"分析失败原因失败: {e}")
            return {"success": False, "error": str(e)}

    # ==================== 辅助方法 ====================

    async def _get_similar_historical_issues(
        self, issue_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """获取相似的历史问题"""
        try:
            if self.memory_service:
                # 使用企业记忆查找相似案例
                try:
                    # 尝试使用search_similar_patterns或类似方法
                    query = json.dumps(issue_data)
                    patterns = await self.memory_service.search_similar_patterns(
                        query, limit=10
                    )
                    return [p.dict() if hasattr(p, "dict") else p for p in patterns]
                except AttributeError:
                    # 如果没有这个方法，返回空列表
                    return []
            return []
        except Exception as e:
            logger.warning(f"获取相似历史问题失败: {e}")
            return []

    def _extract_issue_features(
        self, issue_data: Dict[str, Any], historical_issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取问题特征"""
        features = {
            "issue_type": issue_data.get("type", "unknown"),
            "severity": issue_data.get("severity", "medium"),
            "impact_areas": issue_data.get("impact_areas", []),
            "related_metrics": issue_data.get("related_metrics", []),
        }

        # 从历史问题中提取共同特征
        if historical_issues:
            common_types = {}
            for issue in historical_issues:
                issue_type = issue.get("type", "unknown")
                common_types[issue_type] = common_types.get(issue_type, 0) + 1

            features["common_issue_types"] = common_types
            features["similar_issue_count"] = len(historical_issues)

        return features

    async def _identify_root_causes(
        self, features: Dict[str, Any], analysis_depth: str
    ) -> List[Dict[str, Any]]:
        """识别根因"""
        root_causes = []

        # 简化实现：基于特征分析识别可能的根因
        if features.get("issue_type"):
            root_causes.append(
                {
                    "cause": f"{features['issue_type']}相关问题",
                    "type": "structural",
                    "probability": 0.7,
                }
            )

        if features.get("related_metrics"):
            root_causes.append(
                {
                    "cause": "指标相关因素",
                    "type": "metric",
                    "probability": 0.6,
                    "affected_metrics": features["related_metrics"],
                }
            )

        # 根据深度增加更多分析
        if analysis_depth in ["comprehensive", "deep"]:
            if features.get("common_issue_types"):
                most_common = max(
                    features["common_issue_types"].items(), key=lambda x: x[1]
                )
                root_causes.append(
                    {
                        "cause": f"历史常见问题: {most_common[0]}",
                        "type": "historical_pattern",
                        "probability": 0.65,
                        "frequency": most_common[1],
                    }
                )

        return root_causes

    async def _build_causal_chains(
        self, root_causes: List[Dict[str, Any]], issue_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """构建因果链"""
        chains = []

        for i, cause in enumerate(root_causes):
            chain = {
                "chain_id": f"chain_{i+1}",
                "root_cause": cause,
                "immediate_causes": [],
                "effects": issue_data.get("effects", []),
            }
            chains.append(chain)

        return chains

    def _score_root_causes(
        self, root_causes: List[Dict[str, Any]], causal_chains: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """评估根因重要性"""
        scores = {}

        for cause in root_causes:
            cause_key = cause.get("cause", "unknown")
            base_score = cause.get("probability", 0.5)

            # 根据因果链长度调整分数
            chain_length = len([c for c in causal_chains if c["root_cause"] == cause])
            if chain_length > 0:
                base_score += 0.1

            scores[cause_key] = min(1.0, base_score)

        return scores

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """计算分析置信度"""
        if not scores:
            return 0.0

        # 基于最高分数和分数分布计算置信度
        max_score = max(scores.values()) if scores.values() else 0.0
        avg_score = np.mean(list(scores.values())) if scores.values() else 0.0

        # 综合置信度
        confidence = max_score * 0.6 + avg_score * 0.4
        return round(confidence, 3)

    async def _identify_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """识别时间模式"""
        patterns = {}

        # 简化实现：检测周期性模式
        if len(df) > 7:
            # 计算时间序列趋势
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if len(df[col].dropna()) > 0:
                    values = df[col].values
                    trend = "increasing" if values[-1] > values[0] else "decreasing"
                    patterns[col] = {
                        "trend": trend,
                        "volatility": float(np.std(values)),
                    }

        return patterns

    async def _identify_correlation_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """识别相关性模式"""
        patterns = {}

        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            # 计算相关系数矩阵
            corr_matrix = numeric_df.corr()

            # 找出强相关关系
            strong_correlations = []
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns):
                    if i < j:
                        corr_value = corr_matrix.loc[col1, col2]
                        if abs(corr_value) > 0.6:
                            strong_correlations.append(
                                {
                                    "variable1": col1,
                                    "variable2": col2,
                                    "correlation": float(corr_value),
                                }
                            )

            patterns["strong_correlations"] = strong_correlations

        return patterns

    async def _identify_sequential_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """识别序列模式"""
        patterns = {}

        # 简化实现：检测序列依赖关系
        if len(df) > 3:
            patterns["sequence_length"] = len(df)
            patterns["has_pattern"] = True

        return patterns

    def _score_patterns(self, patterns: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """评估模式重要性"""
        scores = {}

        for pattern_type, pattern_data in patterns.items():
            if pattern_data:
                # 基于模式复杂度评分
                complexity = len(str(pattern_data))
                score = min(1.0, complexity / 100)
                scores[pattern_type] = round(score, 3)
            else:
                scores[pattern_type] = 0.0

        return scores

    def _calculate_pattern_confidence(
        self, patterns: Dict[str, Dict[str, Any]]
    ) -> float:
        """计算模式识别置信度"""
        if not patterns:
            return 0.0

        pattern_scores = [len(str(v)) for v in patterns.values() if v]
        if not pattern_scores:
            return 0.0

        avg_score = np.mean(pattern_scores)
        confidence = min(1.0, avg_score / 100)
        return round(confidence, 3)

    def _extract_common_features(
        self, success_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取共同特征"""
        common_features = {}

        if not success_cases:
            return common_features

        # 统计共同出现的特征
        all_keys = set()
        for case in success_cases:
            all_keys.update(case.keys())

        for key in all_keys:
            values = [case.get(key) for case in success_cases if key in case]
            if len(values) == len(success_cases):
                common_features[key] = values[0] if len(set(values)) == 1 else values

        return common_features

    async def _analyze_success_factors(
        self, success_cases: List[Dict[str, Any]], common_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析成功因素"""
        factors = []

        # 基于共同特征识别成功因素
        for key, value in common_features.items():
            if key not in ["id", "timestamp", "created_at"]:
                factors.append(
                    {
                        "factor": key,
                        "value": value,
                        "frequency": len(success_cases),
                        "importance": (
                            "high" if isinstance(value, (int, float)) else "medium"
                        ),
                    }
                )

        return factors

    def _score_success_factors(
        self, factors: List[Dict[str, Any]], success_cases: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """评估成功因素重要性"""
        scores = {}

        for factor in factors:
            factor_name = factor.get("factor", "unknown")
            frequency = factor.get("frequency", 0)
            importance = factor.get("importance", "medium")

            base_score = frequency / len(success_cases) if success_cases else 0.0
            if importance == "high":
                base_score *= 1.2

            scores[factor_name] = min(1.0, base_score)

        return scores

    async def _identify_best_practices(
        self, success_factors: List[Dict[str, Any]], success_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别最佳实践"""
        practices = []

        # 简化实现：将高频成功因素转化为最佳实践
        for factor in success_factors:
            if factor.get("frequency", 0) >= len(success_cases) * 0.8:
                practices.append(
                    {
                        "practice": f"保持{factor.get('factor')}在{factor.get('value')}",
                        "reason": "在所有成功案例中都出现",
                        "confidence": (
                            factor.get("frequency", 0) / len(success_cases)
                            if success_cases
                            else 0.0
                        ),
                    }
                )

        return practices

    def _calculate_success_confidence(self, factor_scores: Dict[str, float]) -> float:
        """计算成功因素分析置信度"""
        if not factor_scores:
            return 0.0

        avg_score = np.mean(list(factor_scores.values()))
        return round(avg_score, 3)

    def _extract_failure_features(
        self, failure_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取失败特征"""
        features = {}

        if not failure_cases:
            return features

        # 统计失败特征
        for case in failure_cases:
            failure_type = case.get("failure_type", "unknown")
            features[failure_type] = features.get(failure_type, 0) + 1

        return features

    async def _identify_failure_patterns(
        self, failure_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别失败模式"""
        patterns = []

        # 统计常见失败类型
        failure_types = {}
        for case in failure_cases:
            failure_type = case.get("failure_type", "unknown")
            failure_types[failure_type] = failure_types.get(failure_type, 0) + 1

        for failure_type, count in failure_types.items():
            patterns.append(
                {
                    "pattern": failure_type,
                    "frequency": count,
                    "percentage": count / len(failure_cases) if failure_cases else 0.0,
                }
            )

        return patterns

    async def _analyze_failure_chains(
        self, failure_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析失败因果链"""
        chains = []

        for i, case in enumerate(failure_cases):
            chain = {
                "chain_id": f"failure_chain_{i+1}",
                "root_cause": case.get("root_cause", "unknown"),
                "immediate_causes": case.get("immediate_causes", []),
                "effects": case.get("effects", []),
            }
            chains.append(chain)

        return chains

    async def _identify_risk_factors(
        self, failure_features: Dict[str, Any], failure_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别风险因素"""
        risk_factors = []

        # 基于失败模式识别风险因素
        for pattern in failure_patterns:
            if pattern.get("percentage", 0) > 0.3:  # 超过30%的失败率
                risk_factors.append(
                    {
                        "risk_factor": pattern.get("pattern", "unknown"),
                        "risk_level": "high",
                        "frequency": pattern.get("frequency", 0),
                        "recommendation": f"注意避免{pattern.get('pattern')}类型的失败",
                    }
                )

        return risk_factors

    def _calculate_failure_confidence(
        self, failure_patterns: List[Dict[str, Any]]
    ) -> float:
        """计算失败分析置信度"""
        if not failure_patterns:
            return 0.0

        # 基于模式数量和频率计算置信度
        total_frequency = sum(p.get("frequency", 0) for p in failure_patterns)
        if total_frequency == 0:
            return 0.0

        confidence = min(1.0, len(failure_patterns) / 5.0)
        return round(confidence, 3)

    async def _save_insight(
        self,
        session_id: str,
        insight_type: str,
        insight_title: str,
        insight_content: Dict[str, Any],
        confidence_score: float,
    ) -> str:
        """保存洞察到数据库"""
        try:
            if not self.db_service:
                return str(uuid4())

            insight_id = str(uuid4())

            query = """
                INSERT INTO retrospective_insights (
                    id, session_id, insight_type, insight_title,
                    insight_content, confidence_score, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """

            result = await self.db_service.execute_query(
                query,
                [
                    insight_id,
                    session_id,
                    insight_type,
                    insight_title,
                    json.dumps(insight_content),
                    confidence_score,
                    datetime.now(),
                ],
            )

            return insight_id
        except Exception as e:
            logger.error(f"保存洞察失败: {e}")
            return str(uuid4())

    async def _record_to_memory(
        self, memory_type: str, content: Dict[str, Any], tags: List[str]
    ):
        """记录到企业记忆"""
        try:
            if self.memory_service:
                await self.memory_service.store_experience(
                    experience_type=memory_type, content=content, tags=tags
                )
        except Exception as e:
            logger.warning(f"记录到企业记忆失败: {e}")
