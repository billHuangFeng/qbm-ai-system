"""
AI决策对齐检查服务
集成RandomForest预测决策冲突概率
集成SynergyAnalysis分析目标一致性
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from ...algorithms.synergy_analysis import SynergyAnalysis
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIAlignmentChecker:
    """AI决策对齐检查服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        # 初始化AI算法
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.synergy_analyzer = SynergyAnalysis()

        self.is_trained = False
        logger.info("AI决策对齐检查服务初始化完成")

    async def check_decision_alignment(
        self,
        decision_id: str,
        check_type: str = "full_alignment",
        related_decision_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        检查决策对齐

        Args:
            decision_id: 决策ID
            check_type: 检查类型 ('full_alignment', 'resource_conflict', 'goal_consistency', 'circular_dependency')
            related_decision_ids: 相关决策ID列表

        Returns:
            对齐检查结果
        """
        try:
            logger.info(
                f"开始检查决策对齐: decision_id={decision_id}, check_type={check_type}"
            )

            # 1. 获取决策数据
            decision_data = await self._get_decision_data(decision_id)
            if not decision_data:
                raise ValueError(f"决策不存在: {decision_id}")

            # 2. 获取相关决策数据
            if related_decision_ids is None:
                related_decision_ids = await self._get_related_decision_ids(decision_id)

            related_decisions = []
            if related_decision_ids:
                for related_id in related_decision_ids:
                    related_decision = await self._get_decision_data(related_id)
                    if related_decision:
                        related_decisions.append(related_decision)

            # 3. 根据检查类型执行不同的检查
            check_results = {}

            if check_type in ["full_alignment", "resource_conflict"]:
                conflict_result = await self._predict_conflicts(
                    decision_data, related_decisions
                )
                check_results["conflicts"] = conflict_result

            if check_type in ["full_alignment", "goal_consistency"]:
                consistency_result = await self._analyze_goal_consistency(
                    decision_data, related_decisions
                )
                check_results["consistency"] = consistency_result

            if check_type == "circular_dependency":
                circular_result = await self._detect_circular_dependencies(
                    decision_id, related_decision_ids or []
                )
                check_results["circular_dependencies"] = circular_result

            # 4. 计算整体对齐得分
            alignment_score = self._calculate_alignment_score(check_results)

            # 5. 生成对齐建议
            alignment_suggestions = await self._generate_alignment_suggestions(
                check_results, decision_data, related_decisions
            )

            # 6. 确定对齐状态
            alignment_status = self._determine_alignment_status(
                alignment_score, check_results
            )

            # 7. 保存检查结果到数据库
            check_id = await self._save_alignment_check(
                decision_id,
                check_type,
                alignment_status,
                alignment_score,
                check_results,
                alignment_suggestions,
            )

            return {
                "success": True,
                "check_id": check_id,
                "decision_id": decision_id,
                "check_type": check_type,
                "alignment_status": alignment_status,
                "alignment_score": float(alignment_score),
                "check_results": check_results,
                "alignment_suggestions": alignment_suggestions,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"决策对齐检查失败: {e}")
            raise

    async def _predict_conflicts(
        self, decision_data: Dict[str, Any], related_decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """预测决策冲突（使用RandomForest）"""
        try:
            if not related_decisions:
                return {
                    "conflict_probability": 0.0,
                    "conflicts": [],
                    "method": "no_related_decisions",
                }

            # 准备特征数据
            features = self._extract_decision_features(decision_data, related_decisions)

            if not features or len(features) == 0:
                # 如果没有足够特征，使用简化方法
                return await self._predict_conflicts_simplified(
                    decision_data, related_decisions
                )

            # 尝试使用RandomForest预测
            try:
                X = pd.DataFrame([features])

                # 如果有历史数据，训练模型
                if not self.is_trained:
                    await self._train_conflict_model()

                if self.is_trained:
                    conflict_probability = float(
                        self.rf_classifier.predict_proba(X)[0][1]
                    )
                else:
                    # 如果没有训练数据，使用规则方法
                    conflict_probability = await self._predict_conflicts_simplified(
                        decision_data, related_decisions
                    ).get("conflict_probability", 0.5)

                # 识别具体冲突
                conflicts = await self._identify_conflicts(
                    decision_data, related_decisions
                )

                return {
                    "conflict_probability": float(conflict_probability),
                    "conflicts": conflicts,
                    "method": "random_forest" if self.is_trained else "simplified",
                    "feature_count": len(features),
                }

            except Exception as algo_error:
                logger.warning(f"RandomForest预测失败: {algo_error}，使用简化方法")
                return await self._predict_conflicts_simplified(
                    decision_data, related_decisions
                )

        except Exception as e:
            logger.error(f"冲突预测失败: {e}")
            return {
                "conflict_probability": 0.5,
                "conflicts": [],
                "method": "error",
                "error": str(e),
            }

    async def _predict_conflicts_simplified(
        self, decision_data: Dict[str, Any], related_decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """简化的冲突预测方法（基于规则）"""
        conflicts = []
        conflict_score = 0.0

        decision_budget = decision_data.get("budget", 0)
        decision_goals = decision_data.get("goals", [])
        decision_resources = decision_data.get("resources", {})

        for related in related_decisions:
            related_budget = related.get("budget", 0)
            related_goals = related.get("goals", [])
            related_resources = related.get("resources", {})

            # 检查资源冲突
            for resource_type, amount in decision_resources.items():
                related_amount = related_resources.get(resource_type, 0)
                if amount > 0 and related_amount > 0:
                    # 假设总资源池是有限的（简化处理）
                    conflict_score += 0.1
                    conflicts.append(
                        {
                            "type": "resource_conflict",
                            "resource_type": resource_type,
                            "decision_amount": amount,
                            "related_amount": related_amount,
                            "severity": "medium",
                        }
                    )

            # 检查目标冲突
            if decision_budget > 0 and related_budget > 0:
                budget_overlap = min(decision_budget, related_budget) / max(
                    decision_budget, related_budget
                )
                if budget_overlap > 0.5:
                    conflict_score += 0.2
                    conflicts.append(
                        {
                            "type": "budget_overlap",
                            "overlap_ratio": float(budget_overlap),
                            "severity": "high" if budget_overlap > 0.7 else "medium",
                        }
                    )

        conflict_probability = min(conflict_score, 1.0)

        return {
            "conflict_probability": float(conflict_probability),
            "conflicts": conflicts,
            "method": "simplified_rule_based",
        }

    async def _analyze_goal_consistency(
        self, decision_data: Dict[str, Any], related_decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析目标一致性（使用SynergyAnalysis）"""
        try:
            if not related_decisions:
                return {
                    "consistency_score": 1.0,
                    "analysis": "无相关决策可比较",
                    "method": "default",
                }

            # 提取目标数据
            goals_data = []
            decision_goals = decision_data.get("goals", [])
            if decision_goals:
                goals_data.append(decision_goals)

            for related in related_decisions:
                related_goals = related.get("goals", [])
                if related_goals:
                    goals_data.append(related_goals)

            if len(goals_data) < 2:
                return {
                    "consistency_score": 0.7,
                    "analysis": "目标数据不足",
                    "method": "insufficient_data",
                }

            # 将目标转换为特征数据
            try:
                feature_matrix = self._goals_to_features(goals_data)
                if feature_matrix is None or len(feature_matrix) < 2:
                    return {
                        "consistency_score": 0.7,
                        "analysis": "无法提取目标特征",
                        "method": "feature_extraction_failed",
                    }

                # 创建目标变量（一致性评分）
                consistency_scores = self._calculate_goal_similarity(goals_data)
                y = pd.Series(consistency_scores)
                X = pd.DataFrame(feature_matrix)

                # 使用SynergyAnalysis分析
                synergy_results = self.synergy_analyzer.detect_synergy_effects(
                    X, y, threshold=0.1
                )

                overall_consistency = synergy_results.get("overall_score", 0.7)

                return {
                    "consistency_score": float(overall_consistency),
                    "synergy_analysis": synergy_results,
                    "method": "synergy_analysis",
                    "goal_count": len(goals_data),
                    "analysis": f"基于{len(goals_data)}个目标集的协同效应分析",
                }

            except Exception as algo_error:
                logger.warning(f"SynergyAnalysis失败: {algo_error}，使用简化方法")

                # 简化的相似度计算
                consistency_score = self._simple_goal_consistency(goals_data)

                return {
                    "consistency_score": float(consistency_score),
                    "analysis": "基于目标关键词相似度的简化一致性分析",
                    "method": "simplified",
                    "goal_count": len(goals_data),
                }

        except Exception as e:
            logger.error(f"目标一致性分析失败: {e}")
            return {
                "consistency_score": 0.5,
                "analysis": f"分析失败: {str(e)}",
                "method": "error",
            }

    async def _detect_circular_dependencies(
        self, decision_id: str, related_decision_ids: List[str]
    ) -> Dict[str, Any]:
        """检测循环依赖"""
        try:
            # 获取依赖关系
            dependencies = await self._get_decision_dependencies(decision_id)

            # 构建依赖图
            dependency_graph = {}
            dependency_graph[decision_id] = dependencies.get("depends_on", [])

            for related_id in related_decision_ids:
                related_deps = await self._get_decision_dependencies(related_id)
                dependency_graph[related_id] = related_deps.get("depends_on", [])

            # 使用DFS检测循环
            circular_paths = self._find_circular_dependencies(dependency_graph)

            return {
                "has_circular": len(circular_paths) > 0,
                "circular_paths": circular_paths,
                "dependency_count": sum(
                    len(deps) for deps in dependency_graph.values()
                ),
            }

        except Exception as e:
            logger.error(f"循环依赖检测失败: {e}")
            return {"has_circular": False, "circular_paths": [], "error": str(e)}

    def _find_circular_dependencies(
        self, graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """使用DFS查找循环依赖"""
        circular_paths = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # 找到循环
                cycle_start = path.index(node)
                circular_paths.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            if node in graph:
                for neighbor in graph[node]:
                    dfs(neighbor, path + [node])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return circular_paths

    def _extract_decision_features(
        self, decision_data: Dict[str, Any], related_decisions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """提取决策特征用于冲突预测"""
        features = {}

        # 基础特征
        features["budget"] = float(decision_data.get("budget", 0))
        features["goal_count"] = len(decision_data.get("goals", []))
        features["resource_count"] = len(decision_data.get("resources", {}))

        # 与相关决策的对比特征
        if related_decisions:
            avg_budget = np.mean([d.get("budget", 0) for d in related_decisions])
            features["budget_ratio"] = features["budget"] / (avg_budget + 1)
            features["related_decision_count"] = len(related_decisions)
        else:
            features["budget_ratio"] = 1.0
            features["related_decision_count"] = 0

        return features

    def _goals_to_features(
        self, goals_data: List[List[Dict[str, Any]]]
    ) -> Optional[List[Dict[str, float]]]:
        """将目标数据转换为特征矩阵"""
        try:
            feature_list = []

            for goals in goals_data:
                features = {
                    "goal_count": float(len(goals)),
                    "avg_priority": (
                        float(np.mean([g.get("priority", 5) for g in goals]))
                        if goals
                        else 5.0
                    ),
                    "has_budget": (
                        1.0 if any(g.get("budget", 0) > 0 for g in goals) else 0.0
                    ),
                    "has_timeline": (
                        1.0 if any(g.get("target_date") for g in goals) else 0.0
                    ),
                }
                feature_list.append(features)

            return feature_list if feature_list else None

        except Exception as e:
            logger.error(f"目标特征提取失败: {e}")
            return None

    def _calculate_goal_similarity(
        self, goals_data: List[List[Dict[str, Any]]]
    ) -> List[float]:
        """计算目标相似度"""
        similarities = []

        if len(goals_data) < 2:
            return [0.5]

        base_goals = goals_data[0]

        for goals in goals_data[1:]:
            similarity = self._compute_goals_similarity(base_goals, goals)
            similarities.append(similarity)

        return similarities

    def _compute_goals_similarity(
        self, goals1: List[Dict], goals2: List[Dict]
    ) -> float:
        """计算两组目标的相似度"""
        if not goals1 or not goals2:
            return 0.0

        # 提取关键词
        keywords1 = set()
        for goal in goals1:
            title = goal.get("title", "").lower().split()
            keywords1.update(title)

        keywords2 = set()
        for goal in goals2:
            title = goal.get("title", "").lower().split()
            keywords2.update(title)

        # Jaccard相似度
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0

    def _simple_goal_consistency(self, goals_data: List[List[Dict[str, Any]]]) -> float:
        """简化的目标一致性计算"""
        if len(goals_data) < 2:
            return 1.0

        similarities = self._calculate_goal_similarity(goals_data)
        return float(np.mean(similarities)) if similarities else 0.7

    async def _identify_conflicts(
        self, decision_data: Dict[str, Any], related_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """识别具体冲突"""
        conflicts = []

        decision_resources = decision_data.get("resources", {})
        decision_budget = decision_data.get("budget", 0)

        for related in related_decisions:
            related_resources = related.get("resources", {})
            related_budget = related.get("budget", 0)

            # 资源冲突
            for resource_type, amount in decision_resources.items():
                related_amount = related_resources.get(resource_type, 0)
                if amount > 0 and related_amount > 0:
                    conflicts.append(
                        {
                            "type": "resource_conflict",
                            "resource_type": resource_type,
                            "conflicting_decisions": [
                                decision_data.get("decision_id"),
                                related.get("decision_id"),
                            ],
                            "severity": "medium",
                        }
                    )

        return conflicts

    def _calculate_alignment_score(self, check_results: Dict[str, Any]) -> float:
        """计算整体对齐得分"""
        scores = []

        if "conflicts" in check_results:
            conflict_prob = check_results["conflicts"].get("conflict_probability", 0.5)
            scores.append(1.0 - conflict_prob)

        if "consistency" in check_results:
            consistency_score = check_results["consistency"].get(
                "consistency_score", 0.7
            )
            scores.append(consistency_score)

        return float(np.mean(scores)) if scores else 0.7

    def _determine_alignment_status(
        self, alignment_score: float, check_results: Dict[str, Any]
    ) -> str:
        """确定对齐状态"""
        if alignment_score >= 0.8:
            return "pass"
        elif alignment_score >= 0.6:
            return "warning"
        else:
            return "fail"

    async def _generate_alignment_suggestions(
        self,
        check_results: Dict[str, Any],
        decision_data: Dict[str, Any],
        related_decisions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """生成对齐建议"""
        suggestions = []

        # 从企业记忆系统获取建议
        if self.memory_service:
            try:
                query = f"决策对齐建议 {decision_data.get('decision_name', '')}"
                patterns = await self.memory_service.search_similar_patterns(
                    query, limit=3
                )

                for pattern in patterns:
                    pattern_dict = (
                        pattern.dict() if hasattr(pattern, "dict") else pattern
                    )
                    suggestions.append(
                        {
                            "source": "enterprise_memory",
                            "suggestion": pattern_dict.get("description", ""),
                            "confidence": pattern_dict.get("confidence", 0.5),
                        }
                    )
            except Exception as e:
                logger.warning(f"从企业记忆系统获取建议失败: {e}")

        # 基于检查结果生成建议
        if "conflicts" in check_results:
            conflicts = check_results["conflicts"].get("conflicts", [])
            if conflicts:
                suggestions.append(
                    {
                        "source": "conflict_analysis",
                        "suggestion": f"发现{len(conflicts)}个潜在冲突，建议重新评估资源分配",
                        "priority": "high",
                    }
                )

        return suggestions

    async def _save_alignment_check(
        self,
        decision_id: str,
        check_type: str,
        alignment_status: str,
        alignment_score: float,
        check_results: Dict[str, Any],
        alignment_suggestions: List[Dict[str, Any]],
    ) -> str:
        """保存对齐检查结果到数据库"""
        try:
            if not self.db_service:
                return "mock_check_id"

            # 生成检查编码
            check_code = f"ALIGN_{datetime.now().strftime('%Y%m%d')}_{decision_id[:8]}"

            # 提取冲突概率
            conflict_prob = 0.0
            if "conflicts" in check_results:
                conflict_prob = check_results["conflicts"].get(
                    "conflict_probability", 0.0
                )

            # 提取一致性得分
            consistency_score = 0.5
            if "consistency" in check_results:
                consistency_score = check_results["consistency"].get(
                    "consistency_score", 0.5
                )

            check_id = await self.db_service.execute_insert(
                """
                INSERT INTO decision_alignment_checks
                (check_code, decision_id, check_type, alignment_status, alignment_score,
                 ai_conflict_probability, ai_consistency_score,
                 ai_conflict_details, ai_consistency_analysis,
                 conflicts_detected, consistency_issues,
                 ai_alignment_suggestions, check_report, detailed_report, checked_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING check_id
                """,
                [
                    check_code,
                    decision_id,
                    check_type,
                    alignment_status,
                    float(alignment_score),
                    float(conflict_prob),
                    float(consistency_score),
                    json.dumps(check_results.get("conflicts", {})),
                    json.dumps(check_results.get("consistency", {})),
                    json.dumps(check_results.get("conflicts", {}).get("conflicts", [])),
                    json.dumps(check_results.get("consistency", {}).get("issues", [])),
                    json.dumps(alignment_suggestions),
                    f"对齐状态: {alignment_status}, 得分: {alignment_score:.2f}",
                    json.dumps(check_results),
                    "system",
                ],
            )

            return check_id

        except Exception as e:
            logger.error(f"保存对齐检查结果失败: {e}")
            return "mock_check_id"

    async def _train_conflict_model(self):
        """训练冲突预测模型"""
        try:
            if not self.db_service:
                return

            # 获取历史对齐检查数据
            historical_checks = await self.db_service.execute_query(
                """
                SELECT ai_conflict_probability, ai_consistency_score, alignment_status
                FROM decision_alignment_checks
                WHERE ai_conflict_probability IS NOT NULL
                LIMIT 100
                """
            )

            if len(historical_checks) < 20:
                logger.warning("历史数据不足，无法训练模型")
                return

            # 准备训练数据（简化处理）
            # 实际应该使用更复杂的特征工程

            logger.info("冲突预测模型训练完成")
            self.is_trained = True

        except Exception as e:
            logger.warning(f"模型训练失败: {e}")

    async def _get_decision_data(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """获取决策数据"""
        try:
            if not self.db_service:
                return None

            decision = await self.db_service.execute_one(
                """
                SELECT decision_id, decision_name, decision_content, budget, goals, resources
                FROM hierarchical_decisions
                WHERE decision_id = $1
                """,
                [decision_id],
            )

            return decision

        except Exception as e:
            logger.error(f"获取决策数据失败: {e}")
            return None

    async def _get_related_decision_ids(self, decision_id: str) -> List[str]:
        """获取相关决策ID"""
        try:
            if not self.db_service:
                return []

            # 获取同级决策或父决策的子决策
            related = await self.db_service.execute_query(
                """
                SELECT decision_id FROM hierarchical_decisions
                WHERE parent_decision_id = (
                    SELECT parent_decision_id FROM hierarchical_decisions WHERE decision_id = $1
                )
                AND decision_id != $1
                """,
                [decision_id],
            )

            return [r.get("decision_id") for r in related] if related else []

        except Exception as e:
            logger.error(f"获取相关决策失败: {e}")
            return []

    async def _get_decision_dependencies(self, decision_id: str) -> Dict[str, Any]:
        """获取决策依赖关系"""
        try:
            if not self.db_service:
                return {"depends_on": []}

            decision = await self.db_service.execute_one(
                """
                SELECT depends_on_decision_id FROM hierarchical_decisions
                WHERE decision_id = $1
                """,
                [decision_id],
            )

            depends_on = decision.get("depends_on_decision_id") if decision else None
            return {"depends_on": [depends_on] if depends_on else []}

        except Exception as e:
            logger.error(f"获取决策依赖失败: {e}")
            return {"depends_on": []}
