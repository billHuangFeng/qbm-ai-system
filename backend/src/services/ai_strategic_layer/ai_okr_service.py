"""
AI增强OKR管理服务
集成XGBoost预测OKR达成概率
集成企业记忆系统推荐最佳实践
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

from ...algorithms.ensemble_models import XGBoostModel
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIOKRService:
    """AI增强OKR管理服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None, 
                 memory_service: Optional[EnterpriseMemoryService] = None):
        self.db_service = db_service
        self.memory_service = memory_service
        
        # 初始化AI算法
        self.xgb_model = XGBoostModel(n_estimators=100, max_depth=6, learning_rate=0.1)
        
        logger.info("AI增强OKR服务初始化完成")
    
    async def create_okr(
        self,
        okr_name: str,
        objective_statement: str,
        strategic_objective_id: str,
        period_type: str,
        period_start: str,
        period_end: str,
        owner_id: Optional[str] = None,
        owner_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建OKR"""
        try:
            # 1. 生成OKR编码
            okr_code = await self._generate_okr_code(period_type, period_start)
            
            # 2. 插入基础数据
            if self.db_service:
                okr_id = await self.db_service.execute_insert(
                    """
                    INSERT INTO okr_objectives
                    (okr_name, okr_description, okr_code, strategic_objective_id,
                     period_type, period_start, period_end, objective_statement,
                     owner_id, owner_name, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    RETURNING okr_id
                    """,
                    [
                        okr_name,
                        kwargs.get("okr_description", ""),
                        okr_code,
                        strategic_objective_id,
                        period_type,
                        period_start,
                        period_end,
                        objective_statement,
                        owner_id,
                        owner_name,
                        "draft"
                    ]
                )
            else:
                okr_id = "mock_okr_id"
            
            # 3. AI预测达成概率
            achievement_prediction = await self._predict_achievement_probability(okr_id)
            
            # 4. AI推荐最佳实践
            best_practices = await self._recommend_best_practices(
                objective_statement, strategic_objective_id
            )
            
            # 5. AI识别风险因素
            risk_factors = await self._identify_risk_factors(okr_id, achievement_prediction)
            
            # 6. 更新AI分析结果
            if self.db_service and okr_id:
                await self.db_service.execute_update(
                    """
                    UPDATE okr_objectives
                    SET ai_achievement_probability = $1,
                        ai_achievement_prediction = $2,
                        ai_best_practices = $3,
                        ai_risk_factors = $4,
                        ai_recommendations = $5
                    WHERE okr_id = $6
                    """,
                    [
                        achievement_prediction.get("probability", 0.5),
                        json.dumps(achievement_prediction),
                        json.dumps(best_practices),
                        json.dumps(risk_factors),
                        json.dumps({"recommendations": []}),
                        okr_id
                    ]
                )
            
            return {
                "success": True,
                "okr_id": okr_id,
                "okr_code": okr_code,
                "achievement_prediction": achievement_prediction,
                "best_practices": best_practices,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"创建OKR失败: {e}")
            raise
    
    async def create_key_result(
        self,
        okr_id: str,
        kr_name: str,
        kr_statement: str,
        kr_type: str,
        target_value: Optional[float] = None,
        current_value: Optional[float] = None,
        unit: Optional[str] = None,
        weight: float = 1.0,
        owner_id: Optional[str] = None,
        owner_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建关键结果(KR)"""
        try:
            # 1. 插入基础数据
            if self.db_service:
                kr_id = await self.db_service.execute_insert(
                    """
                    INSERT INTO okr_key_results
                    (kr_name, kr_description, okr_id, kr_statement, kr_type,
                     target_value, current_value, baseline_value, unit,
                     weight, priority, owner_id, owner_name, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    RETURNING kr_id
                    """,
                    [
                        kr_name,
                        kwargs.get("kr_description", ""),
                        okr_id,
                        kr_statement,
                        kr_type,
                        target_value,
                        current_value,
                        kwargs.get("baseline_value"),
                        unit,
                        weight,
                        kwargs.get("priority", 5),
                        owner_id,
                        owner_name,
                        "not_started"
                    ]
                )
            else:
                kr_id = "mock_kr_id"
            
            # 2. 更新OKR进度
            await self._update_okr_progress(okr_id)
            
            # 3. 重新预测OKR达成概率
            achievement_prediction = await self._predict_achievement_probability(okr_id)
            
            if self.db_service and okr_id:
                await self.db_service.execute_update(
                    """
                    UPDATE okr_objectives
                    SET ai_achievement_probability = $1,
                        ai_achievement_prediction = $2
                    WHERE okr_id = $3
                    """,
                    [
                        achievement_prediction.get("probability", 0.5),
                        json.dumps(achievement_prediction),
                        okr_id
                    ]
                )
            
            return {
                "success": True,
                "kr_id": kr_id,
                "achievement_prediction": achievement_prediction
            }
            
        except Exception as e:
            logger.error(f"创建关键结果失败: {e}")
            raise
    
    async def _predict_achievement_probability(
        self,
        okr_id: str
    ) -> Dict[str, Any]:
        """AI预测OKR达成概率（使用XGBoost）"""
        try:
            # 1. 获取OKR信息
            if self.db_service:
                okr = await self.db_service.execute_one(
                    """
                    SELECT * FROM okr_objectives
                    WHERE okr_id = $1
                    """,
                    [okr_id]
                )
                
                # 获取相关的KRs
                krs = await self.db_service.execute_query(
                    """
                    SELECT * FROM okr_key_results
                    WHERE okr_id = $1
                    """,
                    [okr_id]
                )
            else:
                okr = None
                krs = []
            
            if not okr:
                return {
                    "probability": 0.5,
                    "method": "default",
                    "confidence": 0.3,
                    "factors": {}
                }
            
            # 2. 准备特征数据用于XGBoost预测
            feature_data = await self._prepare_prediction_features(okr, krs)
            
            if not feature_data or len(feature_data) == 0:
                return {
                    "probability": 0.5,
                    "method": "insufficient_data",
                    "confidence": 0.3,
                    "factors": {}
                }
            
            # 3. 尝试使用历史数据训练模型
            historical_data = await self._get_historical_okr_data(okr.get("strategic_objective_id"))
            
            if historical_data and len(historical_data) >= 10:
                try:
                    # 训练XGBoost模型
                    X_train = pd.DataFrame(historical_data["features"])
                    y_train = pd.Series(historical_data["targets"])
                    
                    self.xgb_model.fit(X_train, y_train)
                    
                    # 评估模型
                    evaluation = self.xgb_model.evaluate(X_train, y_train)
                    
                    # 使用模型预测
                    X_pred = pd.DataFrame([feature_data])
                    prediction_prob = self.xgb_model.predict(X_pred)[0]
                    
                    # 确保概率在0-1范围内
                    prediction_prob = max(0.0, min(1.0, float(prediction_prob)))
                    
                    # 获取特征重要性
                    feature_importance = self.xgb_model.get_feature_importance()
                    
                    return {
                        "probability": prediction_prob,
                        "method": "xgboost",
                        "confidence": min(0.9, evaluation.get("r2", 0.5) + 0.3),
                        "model_evaluation": evaluation,
                        "feature_importance": feature_importance,
                        "factors": self._analyze_achievement_factors(feature_data, okr, krs)
                    }
                except Exception as e:
                    logger.warning(f"XGBoost模型预测失败: {e}，使用简化方法")
            
            # 4. 回退到基于规则的预测
            return await self._rule_based_prediction(okr, krs, feature_data)
            
        except Exception as e:
            logger.error(f"预测OKR达成概率失败: {e}")
            return {
                "probability": 0.5,
                "method": "error",
                "confidence": 0.3,
                "error": str(e)
            }
    
    async def _prepare_prediction_features(
        self,
        okr: Dict[str, Any],
        krs: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """准备预测特征"""
        try:
            features = {}
            
            # 1. OKR基本信息特征
            # 周期长度（天数）
            if okr.get("period_start") and okr.get("period_end"):
                try:
                    start_date = pd.to_datetime(okr.get("period_start"))
                    end_date = pd.to_datetime(okr.get("period_end"))
                    period_days = (end_date - start_date).days
                    features["period_days"] = float(period_days) / 365.0  # 归一化到年
                except:
                    features["period_days"] = 0.25  # 默认3个月
            
            # 2. KR特征
            if krs:
                features["kr_count"] = len(krs)
                
                # KR进度相关特征
                total_progress = sum(kr.get("current_progress", 0) for kr in krs)
                avg_progress = total_progress / len(krs) if len(krs) > 0 else 0
                features["avg_kr_progress"] = avg_progress / 100.0
                
                # KR完成度
                completed_krs = sum(1 for kr in krs if kr.get("status") == "completed")
                features["kr_completion_rate"] = completed_krs / len(krs) if len(krs) > 0 else 0
                
                # KR风险数量
                at_risk_krs = sum(1 for kr in krs if kr.get("status") == "at_risk")
                features["kr_risk_ratio"] = at_risk_krs / len(krs) if len(krs) > 0 else 0
                
                # KR目标完成度（如果有目标值）
                kr_target_ratios = []
                for kr in krs:
                    target_val = kr.get("target_value")
                    current_val = kr.get("current_value")
                    if target_val and current_val and target_val != 0:
                        ratio = abs(current_val / target_val) if target_val > 0 else 0
                        kr_target_ratios.append(min(1.0, ratio))
                
                if kr_target_ratios:
                    features["avg_kr_target_ratio"] = np.mean(kr_target_ratios)
                else:
                    features["avg_kr_target_ratio"] = 0.5
            else:
                features["kr_count"] = 0
                features["avg_kr_progress"] = 0.0
                features["kr_completion_rate"] = 0.0
                features["kr_risk_ratio"] = 0.0
                features["avg_kr_target_ratio"] = 0.5
            
            # 3. OKR当前状态特征
            current_progress = okr.get("current_progress", 0)
            features["okr_progress"] = current_progress / 100.0
            
            expected_progress = okr.get("expected_progress")
            if expected_progress:
                progress_variance = abs(current_progress - expected_progress) / 100.0
                features["progress_variance"] = progress_variance
            else:
                features["progress_variance"] = 0.0
            
            # 4. 历史成功率（如果有）
            if self.db_service:
                strategic_obj_id = okr.get("strategic_objective_id")
                if strategic_obj_id:
                    historical_okrs = await self.db_service.execute_query(
                        """
                        SELECT status, current_progress
                        FROM okr_objectives
                        WHERE strategic_objective_id = $1
                        AND okr_id != $2
                        AND status IN ('completed', 'failed')
                        """,
                        [strategic_obj_id, okr.get("okr_id")]
                    )
                    
                    if historical_okrs:
                        success_count = sum(1 for h in historical_okrs if h.get("status") == "completed")
                        features["historical_success_rate"] = success_count / len(historical_okrs)
                    else:
                        features["historical_success_rate"] = 0.5
                else:
                    features["historical_success_rate"] = 0.5
            else:
                features["historical_success_rate"] = 0.5
            
            return features
            
        except Exception as e:
            logger.error(f"准备预测特征失败: {e}")
            return {}
    
    async def _get_historical_okr_data(
        self,
        strategic_objective_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """获取历史OKR数据用于训练"""
        try:
            if not self.db_service or not strategic_objective_id:
                return None
            
            # 获取历史OKR数据
            historical_okrs = await self.db_service.execute_query(
                """
                SELECT o.*, 
                       COUNT(kr.kr_id) as kr_count,
                       AVG(kr.current_progress) as avg_kr_progress,
                       SUM(CASE WHEN kr.status = 'completed' THEN 1 ELSE 0 END) as completed_krs,
                       SUM(CASE WHEN kr.status = 'at_risk' THEN 1 ELSE 0 END) as at_risk_krs
                FROM okr_objectives o
                LEFT JOIN okr_key_results kr ON o.okr_id = kr.okr_id
                WHERE o.strategic_objective_id = $1
                AND o.status IN ('completed', 'failed')
                GROUP BY o.okr_id
                HAVING COUNT(DISTINCT kr.kr_id) > 0
                ORDER BY o.created_at DESC
                LIMIT 50
                """,
                [strategic_objective_id]
            )
            
            if not historical_okrs or len(historical_okrs) < 10:
                return None
            
            # 准备训练数据
            features_list = []
            targets = []
            
            for okr in historical_okrs:
                # 获取该OKR的所有KRs
                krs = await self.db_service.execute_query(
                    """
                    SELECT * FROM okr_key_results
                    WHERE okr_id = $1
                    """,
                    [okr.get("okr_id")]
                )
                
                # 准备特征
                feature_data = await self._prepare_prediction_features(okr, krs)
                
                if feature_data:
                    features_list.append(feature_data)
                    
                    # 目标变量：是否完成（1表示完成，0表示失败）
                    target = 1.0 if okr.get("status") == "completed" else 0.0
                    targets.append(target)
            
            if len(features_list) >= 10 and len(features_list) == len(targets):
                return {
                    "features": features_list,
                    "targets": targets
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"获取历史OKR数据失败: {e}")
            return None
    
    async def _rule_based_prediction(
        self,
        okr: Dict[str, Any],
        krs: List[Dict[str, Any]],
        feature_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """基于规则的预测（回退方法）"""
        try:
            # 基于多个因素计算概率
            probability = 0.5  # 基础概率
            
            # 1. 基于当前进度
            current_progress = feature_data.get("okr_progress", 0.0)
            if current_progress > 0.8:
                probability += 0.2
            elif current_progress > 0.5:
                probability += 0.1
            elif current_progress < 0.2:
                probability -= 0.2
            
            # 2. 基于KR完成率
            kr_completion = feature_data.get("kr_completion_rate", 0.0)
            probability += (kr_completion - 0.5) * 0.2
            
            # 3. 基于KR风险
            kr_risk = feature_data.get("kr_risk_ratio", 0.0)
            probability -= kr_risk * 0.3
            
            # 4. 基于历史成功率
            historical_success = feature_data.get("historical_success_rate", 0.5)
            probability += (historical_success - 0.5) * 0.2
            
            # 确保概率在0-1范围内
            probability = max(0.0, min(1.0, probability))
            
            return {
                "probability": probability,
                "method": "rule_based",
                "confidence": 0.6,
                "factors": self._analyze_achievement_factors(feature_data, okr, krs)
            }
            
        except Exception as e:
            logger.error(f"基于规则的预测失败: {e}")
            return {
                "probability": 0.5,
                "method": "rule_based_error",
                "confidence": 0.3
            }
    
    def _analyze_achievement_factors(
        self,
        feature_data: Dict[str, float],
        okr: Dict[str, Any],
        krs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析达成因素"""
        factors = {
            "positive_factors": [],
            "risk_factors": []
        }
        
        # 积极因素
        if feature_data.get("okr_progress", 0) > 0.7:
            factors["positive_factors"].append("OKR进度良好")
        
        if feature_data.get("kr_completion_rate", 0) > 0.7:
            factors["positive_factors"].append("大部分KR已完成")
        
        if feature_data.get("historical_success_rate", 0) > 0.6:
            factors["positive_factors"].append("历史成功率较高")
        
        # 风险因素
        if feature_data.get("kr_risk_ratio", 0) > 0.3:
            factors["risk_factors"].append("存在多个处于风险状态的KR")
        
        if feature_data.get("progress_variance", 0) > 0.3:
            factors["risk_factors"].append("进度与预期存在较大偏差")
        
        if len(krs) == 0:
            factors["risk_factors"].append("缺少关键结果定义")
        
        return factors
    
    async def _recommend_best_practices(
        self,
        objective_statement: str,
        strategic_objective_id: str
    ) -> List[Dict[str, Any]]:
        """AI推荐最佳实践（使用企业记忆系统）"""
        try:
            recommendations = []
            
            if self.memory_service:
                try:
                    # 搜索相似的成功模式
                    query = f"OKR best practices {objective_statement}"
                    patterns = await self.memory_service.search_similar_patterns(
                        query=query,
                        limit=10
                    )
                    
                    for pattern in patterns:
                        pattern_dict = pattern.dict() if hasattr(pattern, 'dict') else pattern
                        recommendations.append({
                            "practice": pattern_dict.get("description", ""),
                            "pattern_type": pattern_dict.get("pattern_type", ""),
                            "confidence": pattern_dict.get("confidence", 0.6),
                            "source": "enterprise_memory",
                            "rationale": "基于历史成功模式推荐"
                        })
                except Exception as e:
                    logger.warning(f"从企业记忆系统获取推荐失败: {e}")
            
            # 如果没有从企业记忆系统获取到推荐，添加一些默认最佳实践
            if not recommendations:
                recommendations = [
                    {
                        "practice": "确保每个OKR有2-5个可衡量的关键结果",
                        "pattern_type": "structure",
                        "confidence": 0.9,
                        "source": "standard_template",
                        "rationale": "行业标准最佳实践"
                    },
                    {
                        "practice": "定期（每周或每两周）更新KR进度",
                        "pattern_type": "process",
                        "confidence": 0.8,
                        "source": "standard_template",
                        "rationale": "行业标准最佳实践"
                    },
                    {
                        "practice": "目标应该具有挑战性但可实现（通常达成概率在70-80%）",
                        "pattern_type": "strategy",
                        "confidence": 0.85,
                        "source": "standard_template",
                        "rationale": "行业标准最佳实践"
                    }
                ]
            
            return recommendations[:5]  # 返回Top 5
            
        except Exception as e:
            logger.error(f"推荐最佳实践失败: {e}")
            return []
    
    async def _identify_risk_factors(
        self,
        okr_id: str,
        achievement_prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别风险因素"""
        try:
            risk_factors = []
            
            probability = achievement_prediction.get("probability", 0.5)
            
            # 基于预测概率的风险
            if probability < 0.4:
                risk_factors.append({
                    "risk_type": "low_achievement_probability",
                    "severity": "high",
                    "description": "AI预测达成概率较低",
                    "probability": probability,
                    "recommendation": "建议重新评估OKR目标或调整资源分配"
                })
            elif probability < 0.6:
                risk_factors.append({
                    "risk_type": "moderate_achievement_probability",
                    "severity": "medium",
                    "description": "AI预测达成概率中等",
                    "probability": probability,
                    "recommendation": "建议加强监控和资源支持"
                })
            
            # 从达成因素中提取风险
            factors = achievement_prediction.get("factors", {})
            risk_items = factors.get("risk_factors", [])
            
            for risk_item in risk_items:
                risk_factors.append({
                    "risk_type": "factor_based_risk",
                    "severity": "medium",
                    "description": risk_item,
                    "recommendation": f"建议关注并处理：{risk_item}"
                })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"识别风险因素失败: {e}")
            return []
    
    async def _update_okr_progress(self, okr_id: str) -> None:
        """更新OKR进度"""
        try:
            if not self.db_service:
                return
            
            # 获取所有KRs
            krs = await self.db_service.execute_query(
                """
                SELECT weight, current_progress, status
                FROM okr_key_results
                WHERE okr_id = $1
                """,
                [okr_id]
            )
            
            if not krs:
                return
            
            # 计算加权平均进度
            total_weight = sum(kr.get("weight", 1.0) for kr in krs)
            weighted_progress = sum(
                kr.get("current_progress", 0) * kr.get("weight", 1.0)
                for kr in krs
            )
            
            if total_weight > 0:
                avg_progress = weighted_progress / total_weight
            else:
                avg_progress = 0.0
            
            # 更新OKR进度
            await self.db_service.execute_update(
                """
                UPDATE okr_objectives
                SET current_progress = $1,
                    updated_at = NOW()
                WHERE okr_id = $2
                """,
                [float(avg_progress), okr_id]
            )
            
        except Exception as e:
            logger.error(f"更新OKR进度失败: {e}")
    
    async def update_key_result_progress(
        self,
        kr_id: str,
        current_value: Optional[float] = None,
        current_progress: Optional[float] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新关键结果进度"""
        try:
            if not self.db_service:
                return {"success": False, "error": "数据库服务未初始化"}
            
            # 获取KR信息
            kr = await self.db_service.execute_one(
                """
                SELECT * FROM okr_key_results
                WHERE kr_id = $1
                """,
                [kr_id]
            )
            
            if not kr:
                return {"success": False, "error": "关键结果不存在"}
            
            okr_id = kr.get("okr_id")
            
            # 更新KR
            update_fields = []
            params = []
            param_index = 1
            
            if current_value is not None:
                update_fields.append(f"current_value = ${param_index}")
                params.append(current_value)
                param_index += 1
                
                # 如果有目标值，自动计算进度
                target_value = kr.get("target_value")
                if target_value and target_value != 0:
                    calculated_progress = min(100.0, max(0.0, (current_value / target_value) * 100))
                    if current_progress is None:
                        current_progress = calculated_progress
            
            if current_progress is not None:
                update_fields.append(f"current_progress = ${param_index}")
                params.append(current_progress)
                param_index += 1
            
            if status:
                update_fields.append(f"status = ${param_index}")
                params.append(status)
                param_index += 1
            
            if update_fields:
                update_fields.append("updated_at = NOW()")
                params.append(kr_id)
                
                query = f"""
                    UPDATE okr_key_results
                    SET {', '.join(update_fields)}
                    WHERE kr_id = ${param_index}
                """
                
                await self.db_service.execute_update(query, params)
                
                # 记录进度跟踪历史
                await self.db_service.execute_insert(
                    """
                    INSERT INTO okr_progress_tracking
                    (kr_id, tracking_date, progress_value, actual_value, target_value)
                    VALUES ($1, CURRENT_DATE, $2, $3, $4)
                    """,
                    [
                        kr_id,
                        current_progress or kr.get("current_progress", 0),
                        current_value or kr.get("current_value"),
                        kr.get("target_value")
                    ]
                )
            
            # 更新OKR进度
            await self._update_okr_progress(okr_id)
            
            # 重新预测OKR达成概率
            achievement_prediction = await self._predict_achievement_probability(okr_id)
            
            if self.db_service:
                await self.db_service.execute_update(
                    """
                    UPDATE okr_objectives
                    SET ai_achievement_probability = $1,
                        ai_achievement_prediction = $2
                    WHERE okr_id = $3
                    """,
                    [
                        achievement_prediction.get("probability", 0.5),
                        json.dumps(achievement_prediction),
                        okr_id
                    ]
                )
            
            return {
                "success": True,
                "kr_id": kr_id,
                "updated_progress": current_progress,
                "achievement_prediction": achievement_prediction
            }
            
        except Exception as e:
            logger.error(f"更新关键结果进度失败: {e}")
            raise
    
    async def get_okr(self, okr_id: str) -> Optional[Dict[str, Any]]:
        """获取OKR详情"""
        try:
            if not self.db_service:
                return None
            
            okr = await self.db_service.execute_one(
                """
                SELECT * FROM okr_objectives
                WHERE okr_id = $1
                """,
                [okr_id]
            )
            
            if okr:
                # 获取所有KRs
                krs = await self.db_service.execute_query(
                    """
                    SELECT * FROM okr_key_results
                    WHERE okr_id = $1
                    ORDER BY priority DESC, weight DESC
                    """,
                    [okr_id]
                )
                okr["key_results"] = krs
            
            return okr
            
        except Exception as e:
            logger.error(f"获取OKR详情失败: {e}")
            return None
    
    async def get_okrs_by_objective(
        self,
        strategic_objective_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取指定战略目标下的所有OKR"""
        try:
            if not self.db_service:
                return []
            
            query = """
                SELECT * FROM okr_objectives
                WHERE strategic_objective_id = $1
            """
            params = [strategic_objective_id]
            
            if status:
                query += " AND status = $2"
                params.append(status)
            
            query += " ORDER BY period_start DESC, created_at DESC"
            
            results = await self.db_service.execute_query(query, params)
            
            return results
            
        except Exception as e:
            logger.error(f"获取OKR列表失败: {e}")
            return []
    
    async def _generate_okr_code(self, period_type: str, period_start: str) -> str:
        """生成OKR编码"""
        try:
            if self.db_service:
                try:
                    # 解析周期起始日期
                    start_date = pd.to_datetime(period_start)
                    period_prefix = start_date.strftime('%Y')
                    
                    if period_type == "quarterly":
                        quarter = (start_date.month - 1) // 3 + 1
                        period_prefix += f"Q{quarter}"
                    elif period_type == "annual":
                        period_prefix += "ANNUAL"
                    else:
                        period_prefix += start_date.strftime('%m')
                    
                    # 统计该周期已有的OKR数量
                    result = await self.db_service.execute_one(
                        """
                        SELECT COUNT(*) as count
                        FROM okr_objectives
                        WHERE okr_code LIKE $1
                        """,
                        [f"OKR_{period_prefix}_%"]
                    )
                    
                    count = result.get("count", 0) if result else 0
                    return f"OKR_{period_prefix}_{count + 1:03d}"
                    
                except Exception:
                    pass
            
            # 默认编码
            return f"OKR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        except Exception as e:
            logger.warning(f"生成OKR编码失败: {e}")
            return f"OKR_{datetime.now().strftime('%Y%m%d%H%M%S')}"


