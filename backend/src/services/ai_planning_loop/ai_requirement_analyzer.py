"""
AI需求深度分析服务
集成企业记忆系统查找相似需求和推荐最佳实践
集成ThresholdAnalysis识别关键需求阈值
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import pandas as pd
import numpy as np

from ...algorithms.threshold_analysis import ThresholdAnalysis
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIRequirementAnalyzer:
    """AI需求深度分析服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None,
                 memory_service: Optional[EnterpriseMemoryService] = None):
        self.db_service = db_service
        self.memory_service = memory_service
        
        # 初始化AI算法
        self.threshold_analyzer = ThresholdAnalysis()
        
        logger.info("AI需求深度分析服务初始化完成")
    
    async def analyze_requirement_depth(
        self,
        requirement_id: str,
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """
        深度分析需求
        
        Args:
            requirement_id: 需求ID
            analysis_type: 分析类型 ('full', 'similarity', 'threshold', 'optimization')
        
        Returns:
            深度分析结果
        """
        try:
            logger.info(f"开始深度分析需求: requirement_id={requirement_id}, analysis_type={analysis_type}")
            
            # 1. 获取需求数据
            requirement_data = await self._get_requirement_data(requirement_id)
            if not requirement_data:
                raise ValueError(f"需求不存在: {requirement_id}")
            
            analysis_results = {}
            
            # 2. 相似需求分析
            if analysis_type in ["full", "similarity"]:
                similar_requirements = await self._find_similar_requirements(
                    requirement_data
                )
                analysis_results["similar_requirements"] = similar_requirements
            
            # 3. 关键需求阈值识别
            if analysis_type in ["full", "threshold"]:
                threshold_indicators = await self._identify_critical_requirements(
                    requirement_data
                )
                analysis_results["threshold_indicators"] = threshold_indicators
            
            # 4. 需求优化建议
            if analysis_type in ["full", "optimization"]:
                optimization_suggestions = await self._recommend_requirement_optimization(
                    requirement_data, similar_requirements if "similar_requirements" in analysis_results else []
                )
                analysis_results["optimization_suggestions"] = optimization_suggestions
            
            # 5. 需求风险评估
            risk_assessment = await self._assess_requirement_risks(
                requirement_data, analysis_results
            )
            analysis_results["risk_assessment"] = risk_assessment
            
            # 6. 需求价值评估
            value_assessment = await self._assess_requirement_value(
                requirement_data, analysis_results
            )
            analysis_results["value_assessment"] = value_assessment
            
            return {
                "success": True,
                "requirement_id": requirement_id,
                "analysis_type": analysis_type,
                "analysis_results": analysis_results,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"需求深度分析失败: {e}")
            raise
    
    async def _find_similar_requirements(
        self,
        requirement_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """查找相似需求（使用企业记忆系统）"""
        try:
            similar_reqs = []
            
            # 1. 从数据库查找历史相似需求
            if self.db_service:
                historical_reqs = await self.db_service.execute_query(
                    """
                    SELECT requirement_id, requirement_title, requirement_description,
                           requirement_type, status, ai_priority_score
                    FROM decision_requirements
                    WHERE requirement_type = $1
                      AND status IN ('approved', 'completed')
                      AND requirement_id != $2
                    ORDER BY ai_priority_score DESC
                    LIMIT 10
                    """,
                    [
                        requirement_data.get("requirement_type"),
                        requirement_data.get("requirement_id")
                    ]
                )
                
                for req in historical_reqs or []:
                    similarity = await self._calculate_requirement_similarity(
                        requirement_data, req
                    )
                    if similarity > 0.3:  # 相似度阈值
                        similar_reqs.append({
                            "requirement_id": req.get("requirement_id"),
                            "requirement_title": req.get("requirement_title"),
                            "similarity_score": float(similarity),
                            "source": "database"
                        })
            
            # 2. 从企业记忆系统查找相似模式
            if self.memory_service:
                try:
                    query = f"{requirement_data.get('requirement_title', '')} {requirement_data.get('requirement_description', '')[:200]}"
                    patterns = await self.memory_service.search_similar_patterns(
                        query=query,
                        limit=5
                    )
                    
                    for pattern in patterns:
                        pattern_dict = pattern.dict() if hasattr(pattern, 'dict') else pattern
                        
                        # 尝试从模式中提取需求信息
                        pattern_text = pattern_dict.get("description", "")
                        similarity = self._text_similarity(
                            requirement_data.get("requirement_description", ""),
                            pattern_text
                        )
                        
                        if similarity > 0.3:
                            similar_reqs.append({
                                "pattern_id": pattern_dict.get("id"),
                                "pattern_description": pattern_text[:200],
                                "similarity_score": float(similarity),
                                "confidence": pattern_dict.get("confidence", 0.5),
                                "source": "enterprise_memory"
                            })
                except Exception as e:
                    logger.warning(f"企业记忆系统查询失败: {e}")
            
            # 按相似度排序
            similar_reqs.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
            
            return similar_reqs[:5]  # 返回最相似的5个
            
        except Exception as e:
            logger.error(f"查找相似需求失败: {e}")
            return []
    
    async def _identify_critical_requirements(
        self,
        requirement_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别关键需求阈值（使用ThresholdAnalysis）"""
        try:
            threshold_indicators = []
            
            # 1. 从需求描述中提取数值
            requirement_text = f"{requirement_data.get('requirement_title', '')} {requirement_data.get('requirement_description', '')}"
            
            import re
            numbers = re.findall(r'\d+\.?\d*%?', requirement_text)
            numeric_values = []
            
            for num_str in numbers:
                try:
                    clean_num = num_str.replace('%', '')
                    numeric_values.append(float(clean_num))
                except:
                    continue
            
            # 2. 如果有足够数值，使用ThresholdAnalysis
            if len(numeric_values) >= 3:
                try:
                    # 准备数据
                    feature_data = {
                        "value": numeric_values[:10],
                        "index": list(range(len(numeric_values[:10])))
                    }
                    
                    X = pd.DataFrame(feature_data)
                    y = pd.Series(numeric_values[:10])
                    
                    if len(X) >= 3:
                        # 使用ThresholdAnalysis检测阈值
                        threshold_results = self.threshold_analyzer.detect_threshold_effects(
                            X[["value"]], y, min_samples=2
                        )
                        
                        # 提取阈值
                        tree_thresholds = threshold_results.get("decision_tree", {})
                        if tree_thresholds:
                            for feature, thresholds in tree_thresholds.items():
                                if isinstance(thresholds, dict):
                                    threshold_value = thresholds.get("threshold", None)
                                    if threshold_value:
                                        threshold_indicators.append({
                                            "indicator_name": f"关键阈值_{len(threshold_indicators) + 1}",
                                            "threshold_value": float(threshold_value),
                                            "indicator_type": "threshold_analysis",
                                            "significance": thresholds.get("significance", 0.7),
                                            "method": "decision_tree"
                                        })
                except Exception as algo_error:
                    logger.warning(f"ThresholdAnalysis失败: {algo_error}")
            
            # 3. 从需求优先级和时间紧急度识别关键需求
            priority_level = requirement_data.get("priority_level", 5)
            required_by_date = requirement_data.get("required_by_date")
            
            if priority_level >= 8:
                threshold_indicators.append({
                    "indicator_name": "高优先级需求",
                    "threshold_value": priority_level,
                    "indicator_type": "priority",
                    "significance": 0.9,
                    "method": "priority_analysis"
                })
            
            if required_by_date:
                days_until_due = (datetime.fromisoformat(required_by_date) - datetime.now()).days
                if days_until_due <= 30:
                    threshold_indicators.append({
                        "indicator_name": "紧急时间要求",
                        "threshold_value": days_until_due,
                        "indicator_type": "time_urgency",
                        "significance": 0.8 if days_until_due <= 7 else 0.6,
                        "method": "time_analysis"
                    })
            
            return threshold_indicators
            
        except Exception as e:
            logger.error(f"识别关键需求失败: {e}")
            return []
    
    async def _recommend_requirement_optimization(
        self,
        requirement_data: Dict[str, Any],
        similar_requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """推荐需求优化建议"""
        try:
            suggestions = []
            
            # 1. 基于相似需求的成功经验
            successful_similar = [
                req for req in similar_requirements
                if req.get("source") == "database"
            ][:3]
            
            if successful_similar:
                suggestions.append({
                    "type": "best_practice",
                    "suggestion": f"参考{len(successful_similar)}个相似成功需求，建议：",
                    "details": [
                        f"- 需求'{req.get('requirement_title', '')}'的成功经验可作为参考"
                        for req in successful_similar
                    ],
                    "priority": "medium"
                })
            
            # 2. 基于企业记忆系统的最佳实践
            if self.memory_service:
                try:
                    query = f"需求优化最佳实践 {requirement_data.get('requirement_type', '')}"
                    patterns = await self.memory_service.search_similar_patterns(
                        query=query,
                        limit=3
                    )
                    
                    for pattern in patterns:
                        pattern_dict = pattern.dict() if hasattr(pattern, 'dict') else pattern
                        suggestions.append({
                            "type": "enterprise_memory",
                            "suggestion": pattern_dict.get("description", "")[:200],
                            "confidence": pattern_dict.get("confidence", 0.5),
                            "priority": "medium"
                        })
                except Exception as e:
                    logger.warning(f"获取企业记忆建议失败: {e}")
            
            # 3. 基于需求特征的优化建议
            requirement_desc = requirement_data.get("requirement_description", "")
            
            if len(requirement_desc) < 100:
                suggestions.append({
                    "type": "content_improvement",
                    "suggestion": "需求描述较短，建议补充更详细的说明",
                    "priority": "low"
                })
            
            if requirement_data.get("required_by_date") is None:
                suggestions.append({
                    "type": "time_management",
                    "suggestion": "建议设置需求截止日期，便于优先级管理",
                    "priority": "medium"
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return []
    
    async def _assess_requirement_risks(
        self,
        requirement_data: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估需求风险"""
        try:
            risks = []
            risk_score = 0.0
            
            # 1. 检查时间风险
            required_by_date = requirement_data.get("required_by_date")
            if required_by_date:
                days_until_due = (datetime.fromisoformat(required_by_date) - datetime.now()).days
                if days_until_due < 7:
                    risk_score += 0.3
                    risks.append({
                        "type": "time_risk",
                        "severity": "high",
                        "description": f"截止日期紧迫（{days_until_due}天）"
                    })
            
            # 2. 检查相似需求失败风险
            similar_reqs = analysis_results.get("similar_requirements", [])
            failed_similar = [req for req in similar_reqs if req.get("status") == "rejected"]
            if len(failed_similar) > 2:
                risk_score += 0.2
                risks.append({
                    "type": "similarity_risk",
                    "severity": "medium",
                    "description": f"发现{len(failed_similar)}个类似需求被拒绝"
                })
            
            # 3. 检查优先级风险
            priority_level = requirement_data.get("priority_level", 5)
            ai_priority = requirement_data.get("ai_priority_score", 0.5)
            
            if priority_level >= 9 and ai_priority < 0.6:
                risk_score += 0.2
                risks.append({
                    "type": "priority_mismatch",
                    "severity": "medium",
                    "description": "人工优先级与AI评估存在较大差异"
                })
            
            return {
                "risk_score": float(min(risk_score, 1.0)),
                "risks": risks,
                "risk_level": "high" if risk_score > 0.5 else "medium" if risk_score > 0.3 else "low"
            }
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return {
                "risk_score": 0.5,
                "risks": [],
                "risk_level": "unknown"
            }
    
    async def _assess_requirement_value(
        self,
        requirement_data: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估需求价值"""
        try:
            value_score = 0.5
            
            # 基于多个因素评估
            factors = {}
            
            # 1. 优先级因素
            priority_level = requirement_data.get("priority_level", 5)
            factors["priority"] = priority_level / 10.0
            value_score += factors["priority"] * 0.3
            
            # 2. AI优先级因素
            ai_priority = requirement_data.get("ai_priority_score", 0.5)
            factors["ai_priority"] = ai_priority
            value_score += factors["ai_priority"] * 0.3
            
            # 3. 战略关联因素
            strategic_obj_id = requirement_data.get("strategic_objective_id")
            factors["strategic_alignment"] = 0.8 if strategic_obj_id else 0.5
            value_score += factors["strategic_alignment"] * 0.2
            
            # 4. 相似需求成功率
            similar_reqs = analysis_results.get("similar_requirements", [])
            if similar_reqs:
                successful_count = sum(1 for req in similar_reqs if req.get("status") == "completed")
                success_rate = successful_count / len(similar_reqs)
                factors["similar_success_rate"] = success_rate
                value_score += success_rate * 0.2
            
            value_score = min(value_score, 1.0)
            
            return {
                "value_score": float(value_score),
                "factors": factors,
                "value_level": "high" if value_score > 0.7 else "medium" if value_score > 0.5 else "low"
            }
            
        except Exception as e:
            logger.error(f"价值评估失败: {e}")
            return {
                "value_score": 0.5,
                "factors": {},
                "value_level": "unknown"
            }
    
    async def _calculate_requirement_similarity(
        self,
        req1: Dict[str, Any],
        req2: Dict[str, Any]
    ) -> float:
        """计算需求相似度"""
        try:
            # 文本相似度
            text1 = f"{req1.get('requirement_title', '')} {req1.get('requirement_description', '')}"
            text2 = f"{req2.get('requirement_title', '')} {req2.get('requirement_description', '')}"
            
            similarity = self._text_similarity(text1, text2)
            
            # 类型相似度
            type_similarity = 1.0 if req1.get("requirement_type") == req2.get("requirement_type") else 0.5
            
            # 综合相似度
            return (similarity * 0.7 + type_similarity * 0.3)
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（Jaccard相似度）"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    async def _get_requirement_data(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """获取需求数据"""
        try:
            if not self.db_service:
                return None
            
            requirement = await self.db_service.execute_one(
                """
                SELECT requirement_id, requirement_code, requirement_title,
                       requirement_description, requirement_type, requirement_category,
                       parent_decision_id, strategic_objective_id,
                       requester_id, requester_name, requester_department,
                       priority_level, ai_priority_score, status,
                       required_by_date, approved_date, rejected_date
                FROM decision_requirements
                WHERE requirement_id = $1
                """,
                [requirement_id]
            )
            
            return requirement
            
        except Exception as e:
            logger.error(f"获取需求数据失败: {e}")
            return None


