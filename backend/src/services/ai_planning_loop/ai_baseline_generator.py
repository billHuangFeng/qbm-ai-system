"""
AI基线生成服务
集成VARModel生成预测基线
集成LightGBM优化基线参数
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

from ...algorithms.time_series import VARModel
from ...algorithms.ensemble_models import LightGBMModel
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIBaselineGenerator:
    """AI基线生成服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None,
                 memory_service: Optional[EnterpriseMemoryService] = None):
        self.db_service = db_service
        self.memory_service = memory_service
        
        # 初始化AI算法
        self.var_model = VARModel(maxlags=5)
        self.lightgbm_model = LightGBMModel(n_estimators=100, max_depth=6, learning_rate=0.1)
        
        logger.info("AI基线生成服务初始化完成")
    
    async def generate_baseline(
        self,
        decision_id: str,
        baseline_name: str,
        include_predictions: bool = True,
        prediction_periods: int = 4
    ) -> Dict[str, Any]:
        """
        生成决策基线
        
        Args:
            decision_id: 决策ID
            baseline_name: 基线名称
            include_predictions: 是否包含AI预测
            prediction_periods: 预测周期数
        
        Returns:
            基线生成结果
        """
        try:
            logger.info(f"开始生成基线: decision_id={decision_id}, baseline_name={baseline_name}")
            
            # 1. 获取决策数据
            decision_data = await self._get_decision_data(decision_id)
            if not decision_data:
                raise ValueError(f"决策不存在: {decision_id}")
            
            # 2. 获取历史数据
            historical_data = await self._get_historical_baseline_data(decision_id)
            
            # 3. 构建基线快照
            baseline_data = await self._build_baseline_snapshot(decision_data)
            
            # 4. AI预测基线结果
            ai_predictions = None
            ai_confidence = 0.5
            
            if include_predictions:
                try:
                    ai_predictions = await self._predict_baseline_outcomes(
                        decision_data, historical_data, prediction_periods
                    )
                    ai_confidence = ai_predictions.get("confidence", 0.7)
                except Exception as e:
                    logger.warning(f"AI预测失败: {e}，使用默认预测")
                    ai_predictions = await self._generate_default_predictions(baseline_data, prediction_periods)
            
            # 5. 优化基线参数（可选）
            optimization_suggestions = None
            try:
                optimization_suggestions = await self._optimize_baseline_parameters(
                    baseline_data, historical_data
                )
            except Exception as e:
                logger.warning(f"基线优化失败: {e}")
            
            # 6. 风险评估
            risk_factors = await self._assess_baseline_risks(baseline_data, ai_predictions)
            
            # 7. 生成基线编码
            baseline_code = await self._generate_baseline_code(decision_id)
            
            # 8. 保存基线到数据库
            baseline_id = await self._save_baseline(
                decision_id, baseline_code, baseline_name, baseline_data,
                ai_predictions, ai_confidence, optimization_suggestions, risk_factors
            )
            
            return {
                "success": True,
                "baseline_id": baseline_id,
                "baseline_code": baseline_code,
                "baseline_name": baseline_name,
                "baseline_data": baseline_data,
                "ai_predictions": ai_predictions,
                "ai_confidence": float(ai_confidence),
                "optimization_suggestions": optimization_suggestions,
                "risk_factors": risk_factors,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"基线生成失败: {e}")
            raise
    
    async def _predict_baseline_outcomes(
        self,
        decision_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        prediction_periods: int
    ) -> Dict[str, Any]:
        """预测基线结果（使用VARModel）"""
        try:
            if not historical_data or len(historical_data) < 10:
                logger.warning("历史数据不足，使用简化预测")
                return await self._generate_default_predictions(
                    {"target_kpis": decision_data.get("target_kpis", [])},
                    prediction_periods
                )
            
            # 准备时间序列数据
            ts_data = self._prepare_time_series_data(historical_data, decision_data)
            
            if ts_data is None or len(ts_data) < 10:
                return await self._generate_default_predictions(
                    {"target_kpis": decision_data.get("target_kpis", [])},
                    prediction_periods
                )
            
            # 尝试使用VARModel进行多变量时间序列预测
            try:
                # VAR需要至少3个变量
                if ts_data.shape[1] >= 3 and len(ts_data) >= 10:
                    self.var_model.fit(ts_data)
                    forecasts = self.var_model.predict(steps=prediction_periods)
                    
                    # 处理预测结果
                    predicted_outcomes = self._process_var_forecasts(
                        forecasts, decision_data, prediction_periods
                    )
                    
                    return {
                        "predicted_outcomes": predicted_outcomes,
                        "method": "var_model",
                        "confidence": 0.75,
                        "prediction_periods": prediction_periods,
                        "model_performance": self.var_model.fitted_model.score if hasattr(self.var_model, 'fitted_model') else None
                    }
                else:
                    # 使用LightGBM进行单变量预测
                    return await self._predict_with_lightgbm(ts_data, decision_data, prediction_periods)
                    
            except Exception as var_error:
                logger.warning(f"VARModel预测失败: {var_error}，使用LightGBM")
                return await self._predict_with_lightgbm(ts_data, decision_data, prediction_periods)
                
        except Exception as e:
            logger.error(f"基线结果预测失败: {e}")
            return await self._generate_default_predictions(
                {"target_kpis": decision_data.get("target_kpis", [])},
                prediction_periods
            )
    
    async def _predict_with_lightgbm(
        self,
        ts_data: pd.DataFrame,
        decision_data: Dict[str, Any],
        prediction_periods: int
    ) -> Dict[str, Any]:
        """使用LightGBM进行预测"""
        try:
            if ts_data is None or len(ts_data) < 5:
                return await self._generate_default_predictions(
                    {"target_kpis": decision_data.get("target_kpis", [])},
                    prediction_periods
                )
            
            # 为每个变量训练LightGBM模型
            predictions = {}
            
            for col in ts_data.columns:
                try:
                    # 创建特征（滞后特征）
                    X, y = self._create_lag_features(ts_data[[col]], lags=3)
                    
                    if len(X) < 3:
                        continue
                    
                    # 训练模型
                    self.lightgbm_model.fit(X, y)
                    
                    # 预测
                    last_features = self._get_last_features(ts_data[[col]], lags=3)
                    if last_features is not None:
                        future_values = []
                        current_features = last_features
                        
                        for _ in range(prediction_periods):
                            pred_value = self.lightgbm_model.predict(
                                pd.DataFrame([current_features], columns=X.columns)
                            )[0]
                            future_values.append(float(pred_value))
                            
                            # 更新特征用于下一步预测
                            current_features = self._update_features(current_features, pred_value)
                        
                        predictions[col] = future_values
                except Exception as e:
                    logger.warning(f"LightGBM预测变量{col}失败: {e}")
                    continue
            
            return {
                "predicted_outcomes": predictions,
                "method": "lightgbm",
                "confidence": 0.7,
                "prediction_periods": prediction_periods,
                "variables_predicted": list(predictions.keys())
            }
            
        except Exception as e:
            logger.error(f"LightGBM预测失败: {e}")
            return await self._generate_default_predictions(
                {"target_kpis": decision_data.get("target_kpis", [])},
                prediction_periods
            )
    
    def _prepare_time_series_data(
        self,
        historical_data: List[Dict[str, Any]],
        decision_data: Dict[str, Any]
    ) -> Optional[pd.DataFrame]:
        """准备时间序列数据"""
        try:
            if not historical_data:
                return None
            
            # 提取时间序列指标
            ts_records = []
            
            for record in historical_data[-20:]:  # 使用最近20条记录
                record_dict = {}
                
                # 提取数值指标
                if isinstance(record, dict):
                    for key in ["revenue", "cost", "profit", "kpi_value"]:
                        if key in record:
                            record_dict[key] = float(record[key]) if record[key] is not None else 0.0
                
                if record_dict:
                    ts_records.append(record_dict)
            
            if not ts_records:
                return None
            
            df = pd.DataFrame(ts_records)
            
            # 确保至少3列
            if df.shape[1] < 3:
                # 填充到3列
                for i in range(3 - df.shape[1]):
                    df[f"var_{i}"] = df.iloc[:, 0] if df.shape[1] > 0 else 0.0
            
            return df
            
        except Exception as e:
            logger.error(f"准备时间序列数据失败: {e}")
            return None
    
    def _process_var_forecasts(
        self,
        forecasts: np.ndarray,
        decision_data: Dict[str, Any],
        prediction_periods: int
    ) -> Dict[str, Any]:
        """处理VAR预测结果"""
        try:
            target_kpis = decision_data.get("target_kpis", [])
            
            predicted_outcomes = {}
            
            if forecasts.ndim == 2:
                # 多变量预测
                for i, kpi in enumerate(target_kpis[:forecasts.shape[1]]):
                    kpi_name = kpi.get("name", f"kpi_{i}") if isinstance(kpi, dict) else f"kpi_{i}"
                    predicted_outcomes[kpi_name] = forecasts[:, i].tolist()
            else:
                # 单变量预测
                predicted_outcomes["main_kpi"] = forecasts.tolist()
            
            return predicted_outcomes
            
        except Exception as e:
            logger.error(f"处理VAR预测失败: {e}")
            return {"main_outcome": [0.0] * prediction_periods}
    
    def _create_lag_features(self, series: pd.DataFrame, lags: int = 3) -> tuple:
        """创建滞后特征"""
        try:
            data = series.values.flatten()
            X_list = []
            y_list = []
            
            for i in range(lags, len(data)):
                X_list.append(data[i-lags:i].tolist())
                y_list.append(data[i])
            
            if not X_list:
                return None, None
            
            X = pd.DataFrame(X_list, columns=[f"lag_{j+1}" for j in range(lags)])
            y = pd.Series(y_list)
            
            return X, y
            
        except Exception as e:
            logger.error(f"创建滞后特征失败: {e}")
            return None, None
    
    def _get_last_features(self, series: pd.DataFrame, lags: int = 3) -> Optional[List[float]]:
        """获取最后lags个值作为特征"""
        try:
            data = series.values.flatten()
            if len(data) < lags:
                return None
            return data[-lags:].tolist()
        except Exception as e:
            return None
    
    def _update_features(self, features: List[float], new_value: float) -> List[float]:
        """更新特征（滑动窗口）"""
        return features[1:] + [new_value]
    
    async def _optimize_baseline_parameters(
        self,
        baseline_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """优化基线参数（使用LightGBM）"""
        try:
            if not historical_data or len(historical_data) < 10:
                return None
            
            # 准备优化数据
            optimization_data = self._prepare_optimization_data(baseline_data, historical_data)
            
            if optimization_data is None:
                return None
            
            # 使用LightGBM找出最优参数
            try:
                X = optimization_data["features"]
                y = optimization_data["target"]
                
                if len(X) < 5:
                    return None
                
                self.lightgbm_model.fit(X, y)
                
                # 获取特征重要性
                feature_importance = self.lightgbm_model.get_feature_importance()
                
                # 生成优化建议
                suggestions = []
                
                # 尝试获取专家知识中的方法论（基线生成相关）
                expert_knowledge_methods = []
                try:
                    from ...services.expert_knowledge import KnowledgeIntegrationService, ExpertKnowledgeService, KnowledgeSearchService
                    from ...services.enterprise_memory_service import EnterpriseMemoryService
                    
                    if self.db_service:
                        knowledge_service = ExpertKnowledgeService(db_service=self.db_service)
                        search_service = KnowledgeSearchService(db_service=self.db_service)
                        integration_service = KnowledgeIntegrationService(
                            knowledge_service=knowledge_service,
                            search_service=search_service,
                            memory_service=self.memory_service
                        )
                        
                        tenant_id = getattr(self, '_tenant_id', 'default_tenant')
                        
                        # 搜索基线生成相关的专家知识
                        expert_knowledge = await integration_service.search_relevant_knowledge(
                            tenant_id=tenant_id,
                            context={
                                'domain_category': 'resource_allocation',
                                'problem_type': 'optimization_problem',
                                'description': '基线生成和参数优化方法论'
                            },
                            limit=3
                        )
                        
                        expert_knowledge_methods = [
                            {
                                'title': k.get('title'),
                                'summary': k.get('summary', '')[:200],
                                'knowledge_type': k.get('knowledge_type')
                            }
                            for k in expert_knowledge
                            if k.get('knowledge_type') in ['methodology', 'theory', 'best_practice']
                        ]
                except Exception as e:
                    logger.warning(f"获取专家知识失败: {e}")
                
                for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]:
                    current_value = baseline_data.get("baseline_data", {}).get(feature, 0)
                    
                    suggestion = {
                        "parameter": feature,
                        "current_value": current_value,
                        "importance": float(importance),
                        "recommendation": "考虑调整此参数以优化基线"
                    }
                    
                    # 如果有专家知识，添加理论支撑
                    if expert_knowledge_methods:
                        suggestion["expert_knowledge_reference"] = expert_knowledge_methods[0].get('summary', '')
                        suggestion["methodology"] = expert_knowledge_methods[0].get('title', '')
                    
                    suggestions.append(suggestion)
                
                result = {
                    "optimization_model": "lightgbm",
                    "suggestions": suggestions,
                    "confidence": 0.7
                }
                
                # 添加专家知识引用
                if expert_knowledge_methods:
                    result["expert_knowledge_methods"] = expert_knowledge_methods
                
                return result
                
            except Exception as e:
                logger.warning(f"LightGBM优化失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"基线参数优化失败: {e}")
            return None
    
    def _prepare_optimization_data(
        self,
        baseline_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """准备优化数据"""
        try:
            # 简化实现，实际应该更复杂
            features_list = []
            target_list = []
            
            for record in historical_data[-20:]:
                if isinstance(record, dict):
                    features = {
                        "budget": float(record.get("budget", 0)),
                        "resource_count": float(len(record.get("resources", [])))
                    }
                    target = float(record.get("success_score", 0.5))
                    features_list.append(features)
                    target_list.append(target)
            
            if not features_list:
                return None
            
            X = pd.DataFrame(features_list)
            y = pd.Series(target_list)
            
            return {"features": X, "target": y}
            
        except Exception as e:
            logger.error(f"准备优化数据失败: {e}")
            return None
    
    async def _generate_default_predictions(
        self,
        baseline_data: Dict[str, Any],
        prediction_periods: int
    ) -> Dict[str, Any]:
        """生成默认预测（当AI模型不可用时）"""
        target_kpis = baseline_data.get("target_kpis", [])
        
        predicted_outcomes = {}
        for kpi in target_kpis:
            kpi_name = kpi.get("name", "kpi") if isinstance(kpi, dict) else "kpi"
            target_value = kpi.get("target_value", 100) if isinstance(kpi, dict) else 100
            
            # 简单的线性增长预测
            predictions = [
                float(target_value * (1 + 0.05 * (i + 1))) 
                for i in range(prediction_periods)
            ]
            predicted_outcomes[kpi_name] = predictions
        
        return {
            "predicted_outcomes": predicted_outcomes,
            "method": "default_linear",
            "confidence": 0.5,
            "prediction_periods": prediction_periods
        }
    
    async def _assess_baseline_risks(
        self,
        baseline_data: Dict[str, Any],
        ai_predictions: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """评估基线风险"""
        risks = []
        
        # 检查预算风险
        budget = baseline_data.get("budget_allocation", {}).get("total", 0)
        if budget > 1000000:
            risks.append({
                "type": "budget_risk",
                "severity": "medium",
                "description": "预算较高，需要谨慎管理"
            })
        
        # 检查时间风险
        target_kpis = baseline_data.get("target_kpis", [])
        if len(target_kpis) > 10:
            risks.append({
                "type": "complexity_risk",
                "severity": "low",
                "description": "KPI数量较多，实施复杂度较高"
            })
        
        # 基于AI预测的风险
        if ai_predictions:
            confidence = ai_predictions.get("confidence", 0.7)
            if confidence < 0.6:
                risks.append({
                    "type": "prediction_uncertainty",
                    "severity": "medium",
                    "description": f"预测置信度较低({confidence:.2f})，建议重新评估"
                })
        
        return risks
    
    async def _build_baseline_snapshot(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建基线快照"""
        return {
            "target_kpis": decision_data.get("target_kpis", []),
            "budget_allocation": decision_data.get("budget_allocation", {}),
            "key_results": decision_data.get("key_results", []),
            "dependencies": decision_data.get("dependencies", []),
            "assumptions": decision_data.get("assumptions", []),
            "snapshot_time": datetime.now().isoformat()
        }
    
    async def _generate_baseline_code(self, decision_id: str) -> str:
        """生成基线编码"""
        date_str = datetime.now().strftime("%Y%m%d")
        decision_short = decision_id[:8].upper()
        return f"BL_{date_str}_{decision_short}"
    
    async def _save_baseline(
        self,
        decision_id: str,
        baseline_code: str,
        baseline_name: str,
        baseline_data: Dict[str, Any],
        ai_predictions: Optional[Dict[str, Any]],
        ai_confidence: float,
        optimization_suggestions: Optional[Dict[str, Any]],
        risk_factors: List[Dict[str, Any]]
    ) -> str:
        """保存基线到数据库"""
        try:
            if not self.db_service:
                return "mock_baseline_id"
            
            baseline_id = await self.db_service.execute_insert(
                """
                INSERT INTO decision_baselines
                (baseline_code, decision_id, baseline_name, baseline_data,
                 target_kpis, budget_allocation, key_results, dependencies, assumptions,
                 ai_predicted_outcomes, ai_baseline_confidence,
                 ai_optimization_suggestions, ai_risk_factors, frozen_by, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING baseline_id
                """,
                [
                    baseline_code,
                    decision_id,
                    baseline_name,
                    json.dumps(baseline_data),
                    json.dumps(baseline_data.get("target_kpis", [])),
                    json.dumps(baseline_data.get("budget_allocation", {})),
                    json.dumps(baseline_data.get("key_results", [])),
                    json.dumps(baseline_data.get("dependencies", [])),
                    json.dumps(baseline_data.get("assumptions", [])),
                    json.dumps(ai_predictions) if ai_predictions else None,
                    float(ai_confidence),
                    json.dumps(optimization_suggestions) if optimization_suggestions else None,
                    json.dumps(risk_factors),
                    "system",
                    "active"
                ]
            )
            
            return baseline_id
            
        except Exception as e:
            logger.error(f"保存基线失败: {e}")
            return "mock_baseline_id"
    
    async def _get_decision_data(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """获取决策数据"""
        try:
            if not self.db_service:
                return None
            
            decision = await self.db_service.execute_one(
                """
                SELECT decision_id, decision_name, decision_content,
                       budget, target_kpis, budget_allocation,
                       key_results, dependencies, assumptions
                FROM hierarchical_decisions
                WHERE decision_id = $1
                """,
                [decision_id]
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"获取决策数据失败: {e}")
            return None
    
    async def _get_historical_baseline_data(self, decision_id: str) -> List[Dict[str, Any]]:
        """获取历史基线数据"""
        try:
            if not self.db_service:
                return []
            
            historical = await self.db_service.execute_query(
                """
                SELECT baseline_data, ai_predicted_outcomes
                FROM decision_baselines
                WHERE decision_id = $1
                ORDER BY frozen_at DESC
                LIMIT 20
                """,
                [decision_id]
            )
            
            return historical if historical else []
            
        except Exception as e:
            logger.error(f"获取历史基线数据失败: {e}")
            return []

