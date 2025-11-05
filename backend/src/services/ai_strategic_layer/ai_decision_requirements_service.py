"""
AI需求分析服务
集成MLPModel预测需求优先级
集成企业记忆系统分析历史需求模式
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

from ...algorithms.neural_networks import MLPModel
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIDecisionRequirementsService:
    """AI需求分析服务"""

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        memory_service: Optional[EnterpriseMemoryService] = None,
    ):
        self.db_service = db_service
        self.memory_service = memory_service

        # 初始化AI算法
        self.mlp_model = MLPModel(hidden_layer_sizes=(100, 50), max_iter=1000)

        logger.info("AI需求分析服务初始化完成")

    async def create_requirement(
        self,
        requirement_title: str,
        requirement_description: str,
        requirement_type: str,
        parent_decision_id: str,
        strategic_objective_id: Optional[str] = None,
        requester_id: str = "",
        requester_name: str = "",
        requester_department: Optional[str] = None,
        requirement_category: Optional[str] = None,
        required_by_date: Optional[str] = None,
        priority_level: int = 5,
        **kwargs,
    ) -> Dict[str, Any]:
        """创建决策需求"""
        try:
            # 1. 生成需求编码
            requirement_code = await self._generate_requirement_code()

            # 2. 插入基础数据
            if self.db_service:
                requirement_id = await self.db_service.execute_insert(
                    """
                    INSERT INTO decision_requirements
                    (requirement_code, requirement_title, requirement_description,
                     requirement_type, requirement_category, parent_decision_id,
                     strategic_objective_id, requester_id, requester_name,
                     requester_department, required_by_date, priority_level, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    RETURNING requirement_id
                    """,
                    [
                        requirement_code,
                        requirement_title,
                        requirement_description,
                        requirement_type,
                        requirement_category,
                        parent_decision_id,
                        strategic_objective_id,
                        requester_id,
                        requester_name,
                        requester_department,
                        required_by_date,
                        priority_level,
                        "draft",
                    ],
                )
            else:
                requirement_id = "mock_requirement_id"

            # 3. AI分析优先级
            priority_analysis = await self._analyze_priority(
                requirement_id,
                requirement_title,
                requirement_description,
                requirement_type,
                strategic_objective_id,
                required_by_date,
            )

            # 4. AI分析相似需求（使用企业记忆系统）
            similar_requirements = await self._find_similar_requirements(
                requirement_description, requirement_type
            )

            # 5. AI推荐最佳实践
            best_practices = await self._recommend_best_practices(
                requirement_description, requirement_type
            )

            # 6. AI风险评估
            risk_assessment = await self._assess_risks(
                requirement_id, priority_analysis, similar_requirements
            )

            # 7. 更新AI分析结果
            if self.db_service and requirement_id:
                await self.db_service.execute_update(
                    """
                    UPDATE decision_requirements
                    SET ai_priority_score = $1,
                        ai_priority_analysis = $2,
                        ai_similar_requirements = $3,
                        ai_best_practices = $4,
                        ai_risk_assessment = $5
                    WHERE requirement_id = $6
                    """,
                    [
                        priority_analysis.get("priority_score", 0.5),
                        json.dumps(priority_analysis),
                        json.dumps(similar_requirements),
                        json.dumps(best_practices),
                        json.dumps(risk_assessment),
                        requirement_id,
                    ],
                )

            return {
                "success": True,
                "requirement_id": requirement_id,
                "requirement_code": requirement_code,
                "priority_analysis": priority_analysis,
                "similar_requirements": similar_requirements,
                "best_practices": best_practices,
                "risk_assessment": risk_assessment,
            }

        except Exception as e:
            logger.error(f"创建决策需求失败: {e}")
            raise

    async def _analyze_priority(
        self,
        requirement_id: str,
        requirement_title: str,
        requirement_description: str,
        requirement_type: str,
        strategic_objective_id: Optional[str],
        required_by_date: Optional[str],
    ) -> Dict[str, Any]:
        """AI分析需求优先级（使用MLPModel）"""
        try:
            # 1. 准备特征数据
            feature_data = await self._prepare_priority_features(
                requirement_title,
                requirement_description,
                requirement_type,
                strategic_objective_id,
                required_by_date,
            )

            if not feature_data:
                return {
                    "priority_score": 0.5,
                    "method": "default",
                    "confidence": 0.3,
                    "factors": {},
                }

            # 2. 尝试使用历史数据训练模型
            historical_data = await self._get_historical_requirement_data()

            if historical_data and len(historical_data) >= 20:
                try:
                    # 训练MLP模型
                    X_train = pd.DataFrame(historical_data["features"])
                    y_train = pd.Series(historical_data["targets"])

                    self.mlp_model.fit(X_train, y_train)

                    # 评估模型
                    evaluation = self.mlp_model.evaluate(X_train, y_train)

                    # 使用模型预测优先级
                    X_pred = pd.DataFrame([feature_data])
                    priority_score = self.mlp_model.predict(X_pred)[0]

                    # 确保分数在0-1范围内
                    priority_score = max(0.0, min(1.0, float(priority_score)))

                    # 获取特征重要性
                    feature_importance = self.mlp_model.get_feature_importance()

                    # 转换为优先级等级（1-10）
                    priority_level = int(priority_score * 9) + 1

                    return {
                        "priority_score": priority_score,
                        "priority_level": priority_level,
                        "method": "mlp",
                        "confidence": min(0.9, evaluation.get("r2", 0.5) + 0.3),
                        "model_evaluation": evaluation,
                        "feature_importance": feature_importance,
                        "factors": self._analyze_priority_factors(feature_data),
                    }
                except Exception as e:
                    logger.warning(f"MLP模型预测优先级失败: {e}，使用规则方法")

            # 3. 回退到基于规则的优先级分析
            return await self._rule_based_priority_analysis(
                feature_data, requirement_type
            )

        except Exception as e:
            logger.error(f"分析需求优先级失败: {e}")
            return {
                "priority_score": 0.5,
                "priority_level": 5,
                "method": "error",
                "confidence": 0.3,
                "error": str(e),
            }

    async def _prepare_priority_features(
        self,
        requirement_title: str,
        requirement_description: str,
        requirement_type: str,
        strategic_objective_id: Optional[str],
        required_by_date: Optional[str],
    ) -> Dict[str, float]:
        """准备优先级分析特征"""
        try:
            features = {}

            # 1. 需求类型特征（one-hot编码）
            type_mapping = {
                "strategic": 0.9,
                "tactical": 0.6,
                "operational": 0.3,
                "emergency": 1.0,
            }
            features["type_urgency"] = type_mapping.get(requirement_type, 0.5)

            # 2. 文本特征（长度、关键词）
            description_length = len(requirement_description)
            title_length = len(requirement_title)

            # 归一化文本长度
            features["description_length_norm"] = min(1.0, description_length / 1000.0)
            features["title_length_norm"] = min(1.0, title_length / 200.0)

            # 关键紧急词权重
            urgent_keywords = ["紧急", "urgent", "critical", "重要", "必须", "立即"]
            urgent_count = sum(
                1
                for keyword in urgent_keywords
                if keyword.lower() in requirement_description.lower()
                or keyword.lower() in requirement_title.lower()
            )
            features["urgent_keyword_score"] = min(1.0, urgent_count / 3.0)

            # 3. 时间紧急度
            if required_by_date:
                try:
                    required_date = pd.to_datetime(required_by_date)
                    days_until_due = (required_date - datetime.now()).days

                    # 归一化：距离截止日期越近，紧急度越高
                    if days_until_due <= 0:
                        features["time_urgency"] = 1.0
                    elif days_until_due <= 7:
                        features["time_urgency"] = 0.9
                    elif days_until_due <= 30:
                        features["time_urgency"] = 0.6
                    elif days_until_due <= 90:
                        features["time_urgency"] = 0.3
                    else:
                        features["time_urgency"] = 0.1
                except:
                    features["time_urgency"] = 0.5
            else:
                features["time_urgency"] = 0.3  # 没有截止日期，默认不太紧急

            # 4. 战略关联度
            if strategic_objective_id:
                features["strategic_alignment"] = 0.8  # 有战略目标关联，优先级较高

                # 如果有数据库服务，可以进一步分析战略目标的重要性
                if self.db_service:
                    try:
                        objective = await self.db_service.execute_one(
                            """
                            SELECT priority_level, status
                            FROM strategic_objectives
                            WHERE objective_id = $1
                            """,
                            [strategic_objective_id],
                        )

                        if objective:
                            priority_level = objective.get("priority_level", 5)
                            features["strategic_alignment"] = priority_level / 10.0
                    except:
                        pass
            else:
                features["strategic_alignment"] = 0.4  # 无战略关联，优先级较低

            return features

        except Exception as e:
            logger.error(f"准备优先级特征失败: {e}")
            return {}

    async def _get_historical_requirement_data(self) -> Optional[Dict[str, Any]]:
        """获取历史需求数据用于训练"""
        try:
            if not self.db_service:
                return None

            # 获取历史需求数据（已处理的需求）
            historical_requirements = await self.db_service.execute_query(
                """
                SELECT 
                    requirement_title,
                    requirement_description,
                    requirement_type,
                    strategic_objective_id,
                    required_by_date,
                    priority_level,
                    status,
                    approved_date,
                    rejected_date
                FROM decision_requirements
                WHERE status IN ('approved', 'rejected')
                AND ai_priority_score IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 100
                """
            )

            if not historical_requirements or len(historical_requirements) < 20:
                return None

            # 准备训练数据
            features_list = []
            targets = []

            for req in historical_requirements:
                # 准备特征
                feature_data = await self._prepare_priority_features(
                    req.get("requirement_title", ""),
                    req.get("requirement_description", ""),
                    req.get("requirement_type", ""),
                    req.get("strategic_objective_id"),
                    req.get("required_by_date"),
                )

                if feature_data:
                    features_list.append(feature_data)

                    # 目标变量：归一化的优先级
                    priority_level = req.get("priority_level", 5)
                    target = priority_level / 10.0  # 归一化到0-1

                    # 如果被批准，可能优先级更准确
                    if req.get("status") == "approved":
                        # 基于批准时间和优先级判断
                        targets.append(target)
                    else:
                        # 被拒绝的，可能优先级较低，但保持原值
                        targets.append(max(0.1, target - 0.1))

            if len(features_list) >= 20 and len(features_list) == len(targets):
                return {"features": features_list, "targets": targets}

            return None

        except Exception as e:
            logger.warning(f"获取历史需求数据失败: {e}")
            return None

    async def _rule_based_priority_analysis(
        self, feature_data: Dict[str, float], requirement_type: str
    ) -> Dict[str, Any]:
        """基于规则的优先级分析（回退方法）"""
        try:
            # 计算优先级得分
            priority_score = 0.5  # 基础分数

            # 类型紧急度
            type_urgency = feature_data.get("type_urgency", 0.5)
            priority_score += (type_urgency - 0.5) * 0.3

            # 时间紧急度
            time_urgency = feature_data.get("time_urgency", 0.5)
            priority_score += (time_urgency - 0.5) * 0.3

            # 战略关联度
            strategic_alignment = feature_data.get("strategic_alignment", 0.5)
            priority_score += (strategic_alignment - 0.5) * 0.2

            # 紧急关键词
            urgent_keyword_score = feature_data.get("urgent_keyword_score", 0.0)
            priority_score += urgent_keyword_score * 0.2

            # 确保分数在0-1范围内
            priority_score = max(0.0, min(1.0, priority_score))

            # 转换为优先级等级（1-10）
            priority_level = int(priority_score * 9) + 1

            return {
                "priority_score": priority_score,
                "priority_level": priority_level,
                "method": "rule_based",
                "confidence": 0.6,
                "factors": self._analyze_priority_factors(feature_data),
            }

        except Exception as e:
            logger.error(f"基于规则的优先级分析失败: {e}")
            return {
                "priority_score": 0.5,
                "priority_level": 5,
                "method": "rule_based_error",
                "confidence": 0.3,
            }

    def _analyze_priority_factors(
        self, feature_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """分析优先级因素"""
        factors = {"high_priority_factors": [], "low_priority_factors": []}

        # 高优先级因素
        if feature_data.get("type_urgency", 0) > 0.8:
            factors["high_priority_factors"].append("需求类型紧急度高")

        if feature_data.get("time_urgency", 0) > 0.8:
            factors["high_priority_factors"].append("时间紧急度高")

        if feature_data.get("strategic_alignment", 0) > 0.7:
            factors["high_priority_factors"].append("战略关联度高")

        if feature_data.get("urgent_keyword_score", 0) > 0.5:
            factors["high_priority_factors"].append("包含紧急关键词")

        # 低优先级因素
        if feature_data.get("type_urgency", 0) < 0.3:
            factors["low_priority_factors"].append("需求类型紧急度低")

        if feature_data.get("time_urgency", 0) < 0.3:
            factors["low_priority_factors"].append("时间紧急度低")

        if feature_data.get("strategic_alignment", 0) < 0.4:
            factors["low_priority_factors"].append("战略关联度低或无战略关联")

        return factors

    async def _find_similar_requirements(
        self, requirement_description: str, requirement_type: str
    ) -> List[Dict[str, Any]]:
        """查找相似的历史需求（使用企业记忆系统）"""
        try:
            similar_requirements = []

            # 1. 使用企业记忆系统搜索相似模式
            if self.memory_service:
                try:
                    query = f"{requirement_type} requirement {requirement_description[:200]}"
                    patterns = await self.memory_service.search_similar_patterns(
                        query=query, limit=10
                    )

                    for pattern in patterns:
                        pattern_dict = (
                            pattern.dict() if hasattr(pattern, "dict") else pattern
                        )
                        similar_requirements.append(
                            {
                                "pattern_id": pattern_dict.get("id", ""),
                                "description": pattern_dict.get("description", ""),
                                "pattern_type": pattern_dict.get("pattern_type", ""),
                                "confidence": pattern_dict.get("confidence", 0.6),
                                "source": "enterprise_memory",
                                "similarity": pattern_dict.get("confidence", 0.6),
                            }
                        )
                except Exception as e:
                    logger.warning(f"从企业记忆系统查找相似需求失败: {e}")

            # 2. 从数据库查找相似需求
            if self.db_service:
                try:
                    # 使用相似度查询（简化版：关键词匹配）
                    description_keywords = requirement_description.split()[:10]
                    if description_keywords:
                        keyword_pattern = "%" + "%".join(description_keywords[:3]) + "%"

                        similar_db_reqs = await self.db_service.execute_query(
                            """
                            SELECT 
                                requirement_id,
                                requirement_code,
                                requirement_title,
                                requirement_description,
                                requirement_type,
                                status,
                                priority_level,
                                ai_priority_score
                            FROM decision_requirements
                            WHERE requirement_type = $1
                            AND requirement_description ILIKE $2
                            AND status IN ('approved', 'rejected')
                            ORDER BY created_at DESC
                            LIMIT 5
                            """,
                            [requirement_type, keyword_pattern],
                        )

                        for req in similar_db_reqs:
                            similar_requirements.append(
                                {
                                    "requirement_id": req.get("requirement_id"),
                                    "requirement_code": req.get("requirement_code"),
                                    "title": req.get("requirement_title"),
                                    "description": req.get(
                                        "requirement_description", ""
                                    )[:200],
                                    "type": req.get("requirement_type"),
                                    "status": req.get("status"),
                                    "priority_level": req.get("priority_level"),
                                    "ai_priority_score": req.get("ai_priority_score"),
                                    "source": "database",
                                    "similarity": 0.7,  # 简化相似度
                                }
                            )
                except Exception as e:
                    logger.warning(f"从数据库查找相似需求失败: {e}")

            # 按相似度排序
            similar_requirements.sort(
                key=lambda x: x.get("similarity", 0), reverse=True
            )

            return similar_requirements[:5]  # 返回Top 5

        except Exception as e:
            logger.error(f"查找相似需求失败: {e}")
            return []

    async def _recommend_best_practices(
        self, requirement_description: str, requirement_type: str
    ) -> List[Dict[str, Any]]:
        """推荐最佳实践（使用企业记忆系统+专家知识）"""
        try:
            recommendations = []

            # 1. 搜索专家知识（理论框架）
            try:
                from ...services.expert_knowledge import (
                    ExpertKnowledgeService,
                    KnowledgeSearchService,
                )

                # 获取服务实例（如果可用）
                # 注意：这里需要从依赖注入获取，暂时使用简化方式
                tenant_id = getattr(self, "_tenant_id", "default_tenant")

                # 尝试获取知识集成服务（如果有）
                if hasattr(self, "knowledge_integration_service"):
                    integration_service = self.knowledge_integration_service

                    # 搜索专家知识
                    expert_knowledge = (
                        await integration_service.search_relevant_knowledge(
                            tenant_id=tenant_id,
                            context={
                                "domain_category": "resource_allocation",
                                "problem_type": "decision_problem",
                                "description": requirement_description,
                            },
                            limit=3,
                        )
                    )

                    for knowledge in expert_knowledge:
                        recommendations.append(
                            {
                                "practice": knowledge.get(
                                    "summary", knowledge.get("title", "")
                                ),
                                "pattern_type": knowledge.get(
                                    "knowledge_type", "best_practice"
                                ),
                                "confidence": (
                                    0.8
                                    if knowledge.get("verification_status")
                                    == "verified"
                                    else 0.6
                                ),
                                "source": "expert_knowledge",
                                "rationale": f"基于专家知识「{knowledge.get('title')}」推荐",
                                "expert_knowledge_id": knowledge.get("id"),
                            }
                        )
            except ImportError:
                logger.warning("专家知识服务未导入，跳过专家知识推荐")
            except Exception as e:
                logger.warning(f"从专家知识系统获取推荐失败: {e}")

            # 2. 搜索企业记忆（实践经验）
            if self.memory_service:
                try:
                    # 搜索相关最佳实践
                    query = f"{requirement_type} requirement best practices {requirement_description[:200]}"
                    patterns = await self.memory_service.search_similar_patterns(
                        query=query, limit=10
                    )

                    for pattern in patterns:
                        pattern_dict = (
                            pattern.dict() if hasattr(pattern, "dict") else pattern
                        )
                        recommendations.append(
                            {
                                "practice": pattern_dict.get("description", ""),
                                "pattern_type": pattern_dict.get("pattern_type", ""),
                                "confidence": pattern_dict.get("confidence", 0.6),
                                "source": "enterprise_memory",
                                "rationale": "基于历史成功模式推荐",
                            }
                        )
                except Exception as e:
                    logger.warning(f"从企业记忆系统获取推荐失败: {e}")

            # 如果没有从企业记忆系统获取到推荐，添加一些默认最佳实践
            if not recommendations:
                type_practices = {
                    "strategic": [
                        "确保需求与长期战略目标对齐",
                        "进行充分的影响范围分析",
                        "获得高层管理层的支持",
                    ],
                    "tactical": [
                        "明确需求的执行路径和里程碑",
                        "识别关键依赖和资源需求",
                        "建立清晰的验收标准",
                    ],
                    "operational": [
                        "定义明确的执行步骤",
                        "分配清晰的负责人和时间表",
                        "建立定期检查机制",
                    ],
                    "emergency": [
                        "快速评估和决策",
                        "最小化影响范围",
                        "制定应急响应计划",
                    ],
                }

                default_practices = type_practices.get(
                    requirement_type, type_practices["operational"]
                )

                for practice in default_practices[:3]:
                    recommendations.append(
                        {
                            "practice": practice,
                            "pattern_type": "best_practice",
                            "confidence": 0.8,
                            "source": "standard_template",
                            "rationale": f"基于{requirement_type}类型需求的标准最佳实践",
                        }
                    )

            return recommendations[:5]  # 返回Top 5

        except Exception as e:
            logger.error(f"推荐最佳实践失败: {e}")
            return []

    async def _assess_risks(
        self,
        requirement_id: str,
        priority_analysis: Dict[str, Any],
        similar_requirements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """评估需求风险"""
        try:
            risks = []

            priority_score = priority_analysis.get("priority_score", 0.5)

            # 基于优先级分析的风险
            if priority_score < 0.3:
                risks.append(
                    {
                        "risk_type": "low_priority",
                        "severity": "low",
                        "description": "需求优先级较低，可能被延迟或取消",
                        "recommendation": "建议加强需求的价值论证",
                    }
                )

            # 基于相似历史需求的风险
            if similar_requirements:
                rejected_count = sum(
                    1 for req in similar_requirements if req.get("status") == "rejected"
                )
                total_count = len(similar_requirements)

                if total_count > 0 and rejected_count / total_count > 0.5:
                    risks.append(
                        {
                            "risk_type": "high_rejection_rate",
                            "severity": "medium",
                            "description": f"相似需求的历史拒绝率较高（{rejected_count}/{total_count}）",
                            "recommendation": "建议分析拒绝原因并优化需求方案",
                        }
                    )

            # 基于特征因素的风险
            factors = priority_analysis.get("factors", {})
            low_priority_factors = factors.get("low_priority_factors", [])

            if len(low_priority_factors) > 2:
                risks.append(
                    {
                        "risk_type": "multiple_low_priority_factors",
                        "severity": "medium",
                        "description": "存在多个低优先级因素",
                        "recommendation": "建议重新评估需求的必要性和紧迫性",
                    }
                )

            return {
                "risk_count": len(risks),
                "risks": risks,
                "overall_risk_level": (
                    "low"
                    if len(risks) == 0
                    else "medium" if len(risks) <= 2 else "high"
                ),
            }

        except Exception as e:
            logger.error(f"评估需求风险失败: {e}")
            return {
                "risk_count": 0,
                "risks": [],
                "overall_risk_level": "unknown",
                "error": str(e),
            }

    async def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """获取需求详情"""
        try:
            if not self.db_service:
                return None

            result = await self.db_service.execute_one(
                """
                SELECT * FROM decision_requirements
                WHERE requirement_id = $1
                """,
                [requirement_id],
            )

            return result

        except Exception as e:
            logger.error(f"获取需求详情失败: {e}")
            return None

    async def get_requirements_by_decision(
        self, parent_decision_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取指定决策下的所有需求"""
        try:
            if not self.db_service:
                return []

            query = """
                SELECT * FROM decision_requirements
                WHERE parent_decision_id = $1
            """
            params = [parent_decision_id]

            if status:
                query += " AND status = $2"
                params.append(status)

            query += " ORDER BY ai_priority_score DESC NULLS LAST, created_at DESC"

            results = await self.db_service.execute_query(query, params)

            return results

        except Exception as e:
            logger.error(f"获取需求列表失败: {e}")
            return []

    async def _generate_requirement_code(self) -> str:
        """生成需求编码"""
        try:
            if self.db_service:
                try:
                    year = datetime.now().year
                    result = await self.db_service.execute_one(
                        """
                        SELECT COUNT(*) as count
                        FROM decision_requirements
                        WHERE requirement_code LIKE $1
                        """,
                        [f"REQ_{year}_%"],
                    )

                    count = result.get("count", 0) if result else 0
                    return f"REQ_{year}_{count + 1:04d}"

                except Exception:
                    pass

            # 默认编码
            return f"REQ_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        except Exception as e:
            logger.warning(f"生成需求编码失败: {e}")
            return f"REQ_{datetime.now().strftime('%Y%m%d%H%M%S')}"
