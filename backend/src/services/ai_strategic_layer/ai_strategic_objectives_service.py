"""
AI增强战略目标管理服务
集成SynergyAnalysis分析战略目标协同效应
集成ThresholdAnalysis识别关键阈值指标
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ...algorithms.synergy_analysis import SynergyAnalysis
from ...algorithms.threshold_analysis import ThresholdAnalysis
from ..database_service import DatabaseService
from ..enhanced_enterprise_memory import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class AIStrategicObjectivesService:
    """AI增强战略目标管理服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None, 
                 memory_service: Optional[EnterpriseMemoryService] = None):
        self.db_service = db_service
        self.memory_service = memory_service
        
        # 初始化AI算法
        self.synergy_analyzer = SynergyAnalysis()
        self.threshold_analyzer = ThresholdAnalysis()
        
        logger.info("AI增强战略目标服务初始化完成")
    
    async def create_strategic_objective(
        self,
        objective_name: str,
        objective_type: str,
        objective_content: str,
        parent_objective_id: Optional[str] = None,
        target_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """创建战略目标"""
        try:
            # 1. 插入基础数据
            objective_data = {
                "objective_name": objective_name,
                "objective_type": objective_type,
                "objective_content": objective_content,
                "parent_objective_id": parent_objective_id,
                "target_date": target_date,
                "status": "active",
                **kwargs
            }
            
            if self.db_service:
                objective_id = await self.db_service.execute_insert(
                    """
                    INSERT INTO strategic_objectives 
                    (objective_name, objective_type, objective_content, parent_objective_id, target_date, status)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING objective_id
                    """,
                    [objective_name, objective_type, objective_content, parent_objective_id, target_date, "active"]
                )
            else:
                # 如果没有数据库服务，返回模拟ID
                objective_id = "mock_objective_id"
            
            # 2. AI分析协同效应
            synergy_analysis = await self._analyze_synergy(objective_id, parent_objective_id)
            
            # 3. AI识别阈值指标
            threshold_indicators = await self._identify_threshold_indicators(objective_content)
            
            # 4. 更新AI分析结果
            if self.db_service and objective_id:
                await self.db_service.execute_update(
                    """
                    UPDATE strategic_objectives
                    SET synergy_score = $1,
                        synergy_analysis = $2,
                        threshold_indicators = $3,
                        ai_recommendations = $4
                    WHERE objective_id = $5
                    """,
                    [
                        synergy_analysis.get("synergy_score", 0.0),
                        json.dumps(synergy_analysis),
                        json.dumps(threshold_indicators),
                        json.dumps({"recommendations": []}),
                        objective_id
                    ]
                )
            
            return {
                "success": True,
                "objective_id": objective_id,
                "synergy_analysis": synergy_analysis,
                "threshold_indicators": threshold_indicators
            }
            
        except Exception as e:
            logger.error(f"创建战略目标失败: {e}")
            raise
    
    async def _analyze_synergy(
        self, 
        objective_id: str, 
        parent_objective_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析战略目标协同效应（使用SynergyAnalysis算法）"""
        try:
            # 1. 获取所有相关目标
            related_objectives = []
            if self.db_service:
                if parent_objective_id:
                    # 获取同级目标
                    siblings = await self.db_service.execute_query(
                        """
                        SELECT objective_id, objective_name, objective_content, 
                               priority_level, synergy_score
                        FROM strategic_objectives
                        WHERE parent_objective_id = $1 OR objective_id = $1
                        """,
                        [parent_objective_id]
                    )
                    related_objectives = siblings if siblings else []
            
            if not related_objectives or len(related_objectives) < 2:
                return {
                    "synergy_score": 0.5,
                    "analysis": "无相关目标可分析或目标数量不足",
                    "related_objectives": [],
                    "method": "default"
                }
            
            # 2. 尝试使用SynergyAnalysis进行真正的协同效应分析
            try:
                # 准备数值特征数据
                feature_data = []
                for obj in related_objectives:
                    features = {
                        "priority_level": float(obj.get("priority_level", 5)) / 10.0,
                        "existing_synergy": float(obj.get("synergy_score", 0.5)),
                        "content_length": len(obj.get("objective_content", "")) / 1000.0,
                        "has_numeric": 1.0 if any(c.isdigit() for c in obj.get("objective_content", "")) else 0.0
                    }
                    
                    # 提取数值关键词
                    import re
                    numbers = re.findall(r'\d+\.?\d*', obj.get("objective_content", ""))
                    features["numeric_count"] = min(len(numbers) / 5.0, 1.0)
                    if numbers:
                        features["max_number"] = min(float(max(numbers, key=float)) / 100.0, 1.0) if numbers else 0.0
                    else:
                        features["max_number"] = 0.0
                    
                    feature_data.append(features)
                
                # 创建特征矩阵
                import pandas as pd
                feature_names = list(feature_data[0].keys())
                X = pd.DataFrame(feature_data, columns=feature_names)
                
                # 创建目标变量（基于协同效应的综合评分）
                # 这里使用现有协同分数和目标相似度的组合
                y_values = []
                base_obj = related_objectives[0]
                for obj in related_objectives:
                    similarity = await self._calculate_objective_similarity(
                        base_obj.get("objective_content", ""),
                        obj.get("objective_content", "")
                    )
                    priority_weight = float(obj.get("priority_level", 5)) / 10.0
                    combined_score = similarity * 0.6 + priority_weight * 0.4
                    y_values.append(combined_score)
                
                y = pd.Series(y_values)
                
                # 使用SynergyAnalysis进行协同效应检测
                synergy_results = self.synergy_analyzer.detect_synergy_effects(
                    X, y, threshold=0.1
                )
                
                overall_synergy = synergy_results.get("overall_score", 0.5)
                
                # 构建协同效应详情
                synergy_details = []
                pairwise_synergy = synergy_results.get("pairwise", {})
                
                for obj in related_objectives[1:]:  # 跳过第一个（自己）
                    # 尝试从pairwise结果中找到对应的协同分数
                    synergy_score = 0.5
                    
                    # 如果有pairwise结果，尝试匹配
                    if pairwise_synergy:
                        # 使用目标相似度作为默认协同分数
                        similarity = await self._calculate_objective_similarity(
                            base_obj.get("objective_content", ""),
                            obj.get("objective_content", "")
                        )
                        synergy_score = similarity
                    
                    synergy_details.append({
                        "target_objective_id": obj.get("objective_id"),
                        "target_objective_name": obj.get("objective_name"),
                        "synergy_score": synergy_score
                    })
                
                return {
                    "synergy_score": float(overall_synergy),
                    "analysis": "基于SynergyAnalysis算法的协同效应分析",
                    "method": "synergy_analysis",
                    "synergy_details": synergy_results,
                    "related_objectives": synergy_details,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as algo_error:
                logger.warning(f"使用SynergyAnalysis算法失败: {algo_error}，回退到简化方法")
                
                # 回退到简化的相似度计算方法
                synergy_scores = []
                synergy_details = []
                base_obj = related_objectives[0]
                
                for obj in related_objectives[1:]:  # 跳过第一个
                    similarity = await self._calculate_objective_similarity(
                        base_obj.get("objective_content", ""),
                        obj.get("objective_content", "")
                    )
                    
                    synergy_scores.append(similarity)
                    synergy_details.append({
                        "target_objective_id": obj.get("objective_id"),
                        "target_objective_name": obj.get("objective_name"),
                        "synergy_score": similarity
                    })
                
                overall_synergy = sum(synergy_scores) / len(synergy_scores) if synergy_scores else 0.5
                
                return {
                    "synergy_score": float(overall_synergy),
                    "analysis": "基于目标相似度和关联性计算的协同效应",
                    "method": "simplified",
                    "related_objectives": synergy_details,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"协同效应分析失败: {e}")
            return {
                "synergy_score": 0.5,
                "analysis": f"分析失败: {str(e)}",
                "method": "error",
                "related_objectives": []
            }
    
    async def _identify_threshold_indicators(self, objective_content: str) -> List[Dict[str, Any]]:
        """识别关键阈值指标（使用ThresholdAnalysis算法）"""
        try:
            threshold_indicators = []
            
            # 1. 从目标内容中提取数值
            import re
            numbers = re.findall(r'\d+\.?\d*%?', objective_content)
            numeric_values = []
            
            for num_str in numbers:
                try:
                    # 移除百分号并转换为浮点数
                    clean_num = num_str.replace('%', '')
                    numeric_values.append(float(clean_num))
                except:
                    continue
            
            # 2. 如果有足够的数值数据，尝试使用ThresholdAnalysis
            if len(numeric_values) >= 3 and self.db_service:
                try:
                    # 尝试获取相关的历史指标数据用于阈值分析
                    # 这里简化处理：直接使用提取的数值创建特征数据
                    import pandas as pd
                    import numpy as np
                    
                    # 创建模拟特征数据（实际应用中应从历史数据获取）
                    feature_data = {
                        "value": numeric_values[:10],  # 取前10个值
                        "index": list(range(len(numeric_values[:10])))
                    }
                    
                    # 创建目标变量（基于数值的重要性）
                    X = pd.DataFrame(feature_data)
                    # 使用数值本身作为目标变量（简化处理）
                    y = pd.Series(numeric_values[:10])
                    
                    if len(X) >= 3:
                        # 使用ThresholdAnalysis检测阈值效应
                        threshold_results = self.threshold_analyzer.detect_threshold_effects(
                            X[["value"]], y, min_samples=2
                        )
                        
                        # 从结果中提取阈值
                        tree_thresholds = threshold_results.get("decision_tree", {})
                        if tree_thresholds:
                            for feature, thresholds in tree_thresholds.items():
                                if isinstance(thresholds, dict):
                                    threshold_value = thresholds.get("threshold", None)
                                    if threshold_value:
                                        threshold_indicators.append({
                                            "indicator_name": f"阈值指标_{len(threshold_indicators) + 1}",
                                            "threshold_value": float(threshold_value),
                                            "indicator_type": "threshold_analysis",
                                            "confidence": thresholds.get("significance", 0.7),
                                            "source": "threshold_analysis_algorithm",
                                            "method": "decision_tree"
                                        })
                
                except Exception as algo_error:
                    logger.warning(f"使用ThresholdAnalysis算法失败: {algo_error}")
            
            # 3. 基础数值提取（如果算法分析失败或数据不足）
            if not threshold_indicators:
                for i, num_str in enumerate(numbers[:5]):
                    threshold_indicators.append({
                        "indicator_name": f"数值指标_{i + 1}",
                        "threshold_value": num_str,
                        "indicator_type": "numeric",
                        "confidence": 0.7,
                        "source": "text_extraction",
                        "method": "regex"
                    })
            
            # 4. 从企业记忆系统获取历史阈值模式
            if self.memory_service:
                try:
                    patterns = await self.memory_service.search_similar_patterns(
                        query=f"threshold {objective_content[:200]}",
                        limit=5
                    )
                    if patterns:
                        for pattern in patterns[:3]:
                            pattern_dict = pattern.dict() if hasattr(pattern, 'dict') else pattern
                            
                            # 尝试从模式中提取阈值
                            threshold_value = None
                            outcomes = pattern_dict.get("outcomes")
                            if isinstance(outcomes, dict):
                                threshold_value = outcomes.get("threshold")
                            elif isinstance(pattern_dict.get("description"), str):
                                # 从描述中提取数值
                                desc_numbers = re.findall(r'\d+\.?\d*', pattern_dict.get("description", ""))
                                if desc_numbers:
                                    threshold_value = desc_numbers[0]
                            
                            if threshold_value:
                                threshold_indicators.append({
                                    "indicator_name": pattern_dict.get("description", "历史模式指标")[:100],
                                    "threshold_value": threshold_value,
                                    "indicator_type": "historical_pattern",
                                    "confidence": pattern_dict.get("confidence", 0.5),
                                    "source": "enterprise_memory",
                                    "pattern_id": pattern_dict.get("id", "")
                                })
                except Exception as e:
                    logger.warning(f"从企业记忆系统提取阈值指标失败: {e}")
            
            return threshold_indicators[:10]  # 最多返回10个
            
        except Exception as e:
            logger.error(f"识别阈值指标失败: {e}")
            # 回退到基本的数值提取
            import re
            numbers = re.findall(r'\d+\.?\d*%?', objective_content)
            return [
                {
                    "indicator_name": f"指标_{i+1}",
                    "threshold_value": num_str,
                    "indicator_type": "numeric",
                    "confidence": 0.5,
                    "source": "fallback"
                }
                for i, num_str in enumerate(numbers[:5])
            ]
    
    async def _calculate_objective_similarity(self, content1: str, content2: str) -> float:
        """计算目标相似度"""
        try:
            # 使用简单的文本相似度计算
            # 实际实现中可以使用TF-IDF、余弦相似度等
            
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            similarity = intersection / union if union > 0 else 0.0
            return min(similarity, 1.0)
            
        except Exception as e:
            logger.error(f"计算目标相似度失败: {e}")
            return 0.0
    
    async def analyze_all_objectives_synergy(self) -> Dict[str, Any]:
        """分析所有战略目标的协同效应"""
        try:
            if not self.db_service:
                return {"error": "数据库服务未配置"}
            
            # 获取所有活跃的战略目标
            objectives = await self.db_service.execute_query(
                """
                SELECT objective_id, objective_name, objective_content, parent_objective_id
                FROM strategic_objectives
                WHERE status = 'active'
                ORDER BY hierarchy_level, priority_level DESC
                """
            )
            
            if not objectives:
                return {"objectives": [], "overall_synergy": 0.0}
            
            # 使用SynergyAnalysis进行批量分析
            # 准备数据矩阵
            objective_texts = [obj.get("objective_content", "") for obj in objectives]
            
            # 简化的协同效应分析
            synergy_matrix = []
            for i, obj1 in enumerate(objectives):
                row = []
                for j, obj2 in enumerate(objectives):
                    if i == j:
                        row.append(1.0)
                    else:
                        similarity = await self._calculate_objective_similarity(
                            obj1.get("objective_content", ""),
                            obj2.get("objective_content", "")
                        )
                        row.append(similarity)
                synergy_matrix.append(row)
            
            # 计算整体协同效应
            overall_synergy = sum(sum(row) for row in synergy_matrix) / (len(objectives) ** 2)
            
            return {
                "objectives": objectives,
                "synergy_matrix": synergy_matrix,
                "overall_synergy": overall_synergy,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"批量协同效应分析失败: {e}")
            raise
    
    async def get_strategic_objective(self, objective_id: str) -> Optional[Dict[str, Any]]:
        """获取战略目标详情"""
        try:
            if not self.db_service:
                return None
            
            result = await self.db_service.execute_one(
                """
                SELECT * FROM strategic_objectives
                WHERE objective_id = $1
                """,
                [objective_id]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"获取战略目标失败: {e}")
            return None
    
    async def update_strategic_objective(
        self,
        objective_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新战略目标"""
        try:
            if not self.db_service:
                return {"error": "数据库服务未配置"}
            
            # 构建更新SQL
            set_clauses = []
            values = []
            param_index = 1
            
            for key, value in updates.items():
                if key != "objective_id":
                    set_clauses.append(f"{key} = ${param_index}")
                    values.append(value)
                    param_index += 1
            
            if not set_clauses:
                return {"error": "没有要更新的字段"}
            
            set_clauses.append("updated_at = NOW()")
            values.append(objective_id)
            
            sql = f"""
                UPDATE strategic_objectives
                SET {', '.join(set_clauses)}
                WHERE objective_id = ${param_index}
                RETURNING objective_id
            """
            
            result = await self.db_service.execute_one(sql, values)
            
            # 如果更新了内容，重新进行AI分析
            if "objective_content" in updates:
                await self._analyze_synergy(objective_id, updates.get("parent_objective_id"))
                threshold_indicators = await self._identify_threshold_indicators(updates["objective_content"])
                
                await self.db_service.execute_update(
                    """
                    UPDATE strategic_objectives
                    SET threshold_indicators = $1
                    WHERE objective_id = $2
                    """,
                    [json.dumps(threshold_indicators), objective_id]
                )
            
            return {
                "success": True,
                "objective_id": result.get("objective_id") if result else objective_id
            }
            
        except Exception as e:
            logger.error(f"更新战略目标失败: {e}")
            raise
