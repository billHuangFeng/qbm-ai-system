"""
BMOS企业记忆服务 - 增强版
实现知识提取、经验积累和智能推荐功能
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
import pickle
import hashlib
from collections import defaultdict, Counter
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)

class KnowledgePattern(BaseModel):
    """知识模式"""
    pattern_id: str
    pattern_type: str  # 'success', 'failure', 'trend', 'anomaly'
    description: str
    conditions: Dict[str, Any]
    outcomes: Dict[str, Any]
    confidence: float
    frequency: int
    last_seen: datetime
    created_at: datetime

class BusinessInsight(BaseModel):
    """业务洞察"""
    insight_id: str
    category: str  # 'performance', 'efficiency', 'risk', 'opportunity'
    title: str
    description: str
    evidence: List[Dict[str, Any]]
    impact_score: float
    confidence: float
    recommendations: List[str]
    created_at: datetime

class Experience(BaseModel):
    """经验记录"""
    experience_id: str
    scenario: str
    context: Dict[str, Any]
    actions_taken: List[str]
    results: Dict[str, Any]
    success: bool
    lessons_learned: List[str]
    tags: List[str]
    created_at: datetime

class Recommendation(BaseModel):
    """智能推荐"""
    recommendation_id: str
    type: str  # 'action', 'warning', 'optimization', 'opportunity'
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    rationale: str
    expected_impact: float
    confidence: float
    action_items: List[str]
    created_at: datetime

class EnterpriseMemoryService:
    """企业记忆服务"""
    
    def __init__(self, memory_dir: str = "enterprise_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.patterns_dir = self.memory_dir / "patterns"
        self.insights_dir = self.memory_dir / "insights"
        self.experiences_dir = self.memory_dir / "experiences"
        self.recommendations_dir = self.memory_dir / "recommendations"
        
        for dir_path in [self.patterns_dir, self.insights_dir, self.experiences_dir, self.recommendations_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 初始化向量化器
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # 内存缓存
        self.patterns_cache = {}
        self.insights_cache = {}
        self.experiences_cache = {}
        self.recommendations_cache = {}
        
        logger.info(f"企业记忆服务初始化完成: {self.memory_dir}")
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _save_to_file(self, data: Any, file_path: Path) -> None:
        """保存数据到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                else:
                    json.dump(data.dict(), f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise
    
    def _load_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从文件加载数据"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载文件失败: {str(e)}")
        return None
    
    async def extract_patterns_from_data(self, df: pd.DataFrame, 
                                       target_column: str = None,
                                       context: Dict[str, Any] = None) -> List[KnowledgePattern]:
        """从数据中提取知识模式"""
        try:
            logger.info(f"开始从数据中提取模式: {df.shape}")
            
            patterns = []
            
            # 1. 成功模式识别
            success_patterns = await self._identify_success_patterns(df, target_column)
            patterns.extend(success_patterns)
            
            # 2. 失败模式识别
            failure_patterns = await self._identify_failure_patterns(df, target_column)
            patterns.extend(failure_patterns)
            
            # 3. 趋势模式识别
            trend_patterns = await self._identify_trend_patterns(df)
            patterns.extend(trend_patterns)
            
            # 4. 异常模式识别
            anomaly_patterns = await self._identify_anomaly_patterns(df)
            patterns.extend(anomaly_patterns)
            
            # 保存模式
            for pattern in patterns:
                await self.save_pattern(pattern)
            
            logger.info(f"模式提取完成: {len(patterns)} 个模式")
            return patterns
            
        except Exception as e:
            logger.error(f"模式提取失败: {str(e)}")
            raise
    
    async def _identify_success_patterns(self, df: pd.DataFrame, target_column: str = None) -> List[KnowledgePattern]:
        """识别成功模式"""
        patterns = []
        
        try:
            if target_column and target_column in df.columns:
                # 基于目标列识别成功案例
                if df[target_column].dtype in ['int64', 'float64']:
                    # 数值型目标：高值表示成功
                    threshold = df[target_column].quantile(0.8)
                    success_data = df[df[target_column] >= threshold]
                else:
                    # 分类型目标：特定类别表示成功
                    success_data = df[df[target_column] == df[target_column].mode().iloc[0]]
                
                if len(success_data) > 0:
                    # 分析成功案例的特征
                    for col in df.columns:
                        if col != target_column and df[col].dtype in ['int64', 'float64']:
                            success_mean = success_data[col].mean()
                            overall_mean = df[col].mean()
                            
                            if success_mean > overall_mean * 1.2:  # 成功案例中该特征值明显更高
                                pattern = KnowledgePattern(
                                    pattern_id=self._generate_id(f"success_{col}_{success_mean}"),
                                    pattern_type="success",
                                    description=f"高{col}值通常与成功相关",
                                    conditions={col: {"min": success_mean * 0.8}},
                                    outcomes={"success_probability": 0.8},
                                    confidence=0.7,
                                    frequency=len(success_data),
                                    last_seen=datetime.now(),
                                    created_at=datetime.now()
                                )
                                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"成功模式识别失败: {str(e)}")
            return []
    
    async def _identify_failure_patterns(self, df: pd.DataFrame, target_column: str = None) -> List[KnowledgePattern]:
        """识别失败模式"""
        patterns = []
        
        try:
            if target_column and target_column in df.columns:
                # 基于目标列识别失败案例
                if df[target_column].dtype in ['int64', 'float64']:
                    # 数值型目标：低值表示失败
                    threshold = df[target_column].quantile(0.2)
                    failure_data = df[df[target_column] <= threshold]
                else:
                    # 分类型目标：特定类别表示失败
                    failure_data = df[df[target_column] == df[target_column].value_counts().index[-1]]
                
                if len(failure_data) > 0:
                    # 分析失败案例的特征
                    for col in df.columns:
                        if col != target_column and df[col].dtype in ['int64', 'float64']:
                            failure_mean = failure_data[col].mean()
                            overall_mean = df[col].mean()
                            
                            if failure_mean < overall_mean * 0.8:  # 失败案例中该特征值明显更低
                                pattern = KnowledgePattern(
                                    pattern_id=self._generate_id(f"failure_{col}_{failure_mean}"),
                                    pattern_type="failure",
                                    description=f"低{col}值通常与失败相关",
                                    conditions={col: {"max": failure_mean * 1.2}},
                                    outcomes={"failure_probability": 0.8},
                                    confidence=0.7,
                                    frequency=len(failure_data),
                                    last_seen=datetime.now(),
                                    created_at=datetime.now()
                                )
                                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"失败模式识别失败: {str(e)}")
            return []
    
    async def _identify_trend_patterns(self, df: pd.DataFrame) -> List[KnowledgePattern]:
        """识别趋势模式"""
        patterns = []
        
        try:
            # 寻找数值列之间的相关性
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) >= 2:
                correlation_matrix = df[numeric_cols].corr()
                
                for i, col1 in enumerate(numeric_cols):
                    for j, col2 in enumerate(numeric_cols):
                        if i < j:  # 避免重复
                            corr = correlation_matrix.loc[col1, col2]
                            
                            if abs(corr) > 0.7:  # 强相关
                                pattern = KnowledgePattern(
                                    pattern_id=self._generate_id(f"trend_{col1}_{col2}_{corr}"),
                                    pattern_type="trend",
                                    description=f"{col1}与{col2}呈{'正' if corr > 0 else '负'}相关",
                                    conditions={col1: {"correlation": corr}},
                                    outcomes={"prediction": f"当{col1}变化时，{col2}会{'同向' if corr > 0 else '反向'}变化"},
                                    confidence=abs(corr),
                                    frequency=len(df),
                                    last_seen=datetime.now(),
                                    created_at=datetime.now()
                                )
                                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"趋势模式识别失败: {str(e)}")
            return []
    
    async def _identify_anomaly_patterns(self, df: pd.DataFrame) -> List[KnowledgePattern]:
        """识别异常模式"""
        patterns = []
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                # 使用IQR方法检测异常值
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomalies = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                if len(anomalies) > 0 and len(anomalies) < len(df) * 0.1:  # 异常值不超过10%
                    pattern = KnowledgePattern(
                        pattern_id=self._generate_id(f"anomaly_{col}_{len(anomalies)}"),
                        pattern_type="anomaly",
                        description=f"{col}列存在{len(anomalies)}个异常值",
                        conditions={col: {"range": [lower_bound, upper_bound]}},
                        outcomes={"anomaly_count": len(anomalies), "anomaly_rate": len(anomalies) / len(df)},
                        confidence=0.8,
                        frequency=len(anomalies),
                        last_seen=datetime.now(),
                        created_at=datetime.now()
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"异常模式识别失败: {str(e)}")
            return []
    
    async def generate_business_insights(self, patterns: List[KnowledgePattern], 
                                      context: Dict[str, Any] = None) -> List[BusinessInsight]:
        """生成业务洞察"""
        try:
            logger.info(f"开始生成业务洞察: {len(patterns)} 个模式")
            
            insights = []
            
            # 1. 性能洞察
            performance_insights = await self._generate_performance_insights(patterns)
            insights.extend(performance_insights)
            
            # 2. 效率洞察
            efficiency_insights = await self._generate_efficiency_insights(patterns)
            insights.extend(efficiency_insights)
            
            # 3. 风险洞察
            risk_insights = await self._generate_risk_insights(patterns)
            insights.extend(risk_insights)
            
            # 4. 机会洞察
            opportunity_insights = await self._generate_opportunity_insights(patterns)
            insights.extend(opportunity_insights)
            
            # 保存洞察
            for insight in insights:
                await self.save_insight(insight)
            
            logger.info(f"业务洞察生成完成: {len(insights)} 个洞察")
            return insights
            
        except Exception as e:
            logger.error(f"业务洞察生成失败: {str(e)}")
            raise
    
    async def _generate_performance_insights(self, patterns: List[KnowledgePattern]) -> List[BusinessInsight]:
        """生成性能洞察"""
        insights = []
        
        try:
            success_patterns = [p for p in patterns if p.pattern_type == "success"]
            
            if success_patterns:
                # 分析成功模式的特征
                feature_importance = defaultdict(float)
                for pattern in success_patterns:
                    for condition, value in pattern.conditions.items():
                        feature_importance[condition] += pattern.confidence
                
                # 找出最重要的成功因素
                if feature_importance:
                    top_feature = max(feature_importance.items(), key=lambda x: x[1])
                    
                    insight = BusinessInsight(
                        insight_id=self._generate_id(f"performance_{top_feature[0]}"),
                        category="performance",
                        title=f"{top_feature[0]}是成功的关键因素",
                        description=f"分析发现{top_feature[0]}与成功高度相关，置信度为{top_feature[1]:.2f}",
                        evidence=[{"pattern_id": p.pattern_id, "confidence": p.confidence} for p in success_patterns],
                        impact_score=top_feature[1],
                        confidence=top_feature[1],
                        recommendations=[
                            f"重点关注{top_feature[0]}的优化",
                            f"建立{top_feature[0]}的监控机制",
                            f"制定{top_feature[0]}的改进计划"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"性能洞察生成失败: {str(e)}")
            return []
    
    async def _generate_efficiency_insights(self, patterns: List[KnowledgePattern]) -> List[BusinessInsight]:
        """生成效率洞察"""
        insights = []
        
        try:
            trend_patterns = [p for p in patterns if p.pattern_type == "trend"]
            
            if trend_patterns:
                # 分析趋势模式
                for pattern in trend_patterns:
                    insight = BusinessInsight(
                        insight_id=self._generate_id(f"efficiency_{pattern.pattern_id}"),
                        category="efficiency",
                        title=f"发现效率优化机会",
                        description=f"识别到{pattern.description}，可用于效率优化",
                        evidence=[{"pattern_id": pattern.pattern_id, "confidence": pattern.confidence}],
                        impact_score=pattern.confidence * 0.8,
                        confidence=pattern.confidence,
                        recommendations=[
                            f"利用{pattern.description}优化流程",
                            "建立相关指标的监控",
                            "制定效率提升计划"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"效率洞察生成失败: {str(e)}")
            return []
    
    async def _generate_risk_insights(self, patterns: List[KnowledgePattern]) -> List[BusinessInsight]:
        """生成风险洞察"""
        insights = []
        
        try:
            failure_patterns = [p for p in patterns if p.pattern_type == "failure"]
            anomaly_patterns = [p for p in patterns if p.pattern_type == "anomaly"]
            
            risk_patterns = failure_patterns + anomaly_patterns
            
            if risk_patterns:
                # 分析风险模式
                risk_factors = defaultdict(int)
                for pattern in risk_patterns:
                    for condition in pattern.conditions.keys():
                        risk_factors[condition] += pattern.frequency
                
                if risk_factors:
                    top_risk = max(risk_factors.items(), key=lambda x: x[1])
                    
                    insight = BusinessInsight(
                        insight_id=self._generate_id(f"risk_{top_risk[0]}"),
                        category="risk",
                        title=f"识别到{top_risk[0]}相关风险",
                        description=f"发现{top_risk[0]}与失败或异常相关，出现频率为{top_risk[1]}次",
                        evidence=[{"pattern_id": p.pattern_id, "frequency": p.frequency} for p in risk_patterns],
                        impact_score=top_risk[1] * 0.1,
                        confidence=0.8,
                        recommendations=[
                            f"加强对{top_risk[0]}的监控",
                            f"制定{top_risk[0]}的风险控制措施",
                            "建立早期预警机制"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"风险洞察生成失败: {str(e)}")
            return []
    
    async def _generate_opportunity_insights(self, patterns: List[KnowledgePattern]) -> List[BusinessInsight]:
        """生成机会洞察"""
        insights = []
        
        try:
            success_patterns = [p for p in patterns if p.pattern_type == "success"]
            
            if success_patterns:
                # 分析成功模式中的机会
                opportunity_score = sum(p.confidence * p.frequency for p in success_patterns)
                
                if opportunity_score > 0:
                    insight = BusinessInsight(
                        insight_id=self._generate_id(f"opportunity_{opportunity_score}"),
                        category="opportunity",
                        title="发现业务增长机会",
                        description=f"基于成功模式分析，发现{len(success_patterns)}个增长机会点",
                        evidence=[{"pattern_id": p.pattern_id, "confidence": p.confidence} for p in success_patterns],
                        impact_score=opportunity_score * 0.01,
                        confidence=0.7,
                        recommendations=[
                            "扩大成功模式的适用范围",
                            "复制成功案例的最佳实践",
                            "建立成功模式的标准化流程"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"机会洞察生成失败: {str(e)}")
            return []
    
    async def generate_recommendations(self, insights: List[BusinessInsight], 
                                    current_context: Dict[str, Any] = None) -> List[Recommendation]:
        """生成智能推荐"""
        try:
            logger.info(f"开始生成智能推荐: {len(insights)} 个洞察")
            
            recommendations = []
            
            for insight in insights:
                # 基于洞察生成推荐
                if insight.category == "performance":
                    rec = await self._generate_performance_recommendation(insight)
                    if rec:
                        recommendations.append(rec)
                
                elif insight.category == "efficiency":
                    rec = await self._generate_efficiency_recommendation(insight)
                    if rec:
                        recommendations.append(rec)
                
                elif insight.category == "risk":
                    rec = await self._generate_risk_recommendation(insight)
                    if rec:
                        recommendations.append(rec)
                
                elif insight.category == "opportunity":
                    rec = await self._generate_opportunity_recommendation(insight)
                    if rec:
                        recommendations.append(rec)
            
            # 保存推荐
            for rec in recommendations:
                await self.save_recommendation(rec)
            
            logger.info(f"智能推荐生成完成: {len(recommendations)} 个推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"智能推荐生成失败: {str(e)}")
            raise
    
    async def _generate_performance_recommendation(self, insight: BusinessInsight) -> Optional[Recommendation]:
        """生成性能推荐"""
        try:
            recommendation = Recommendation(
                recommendation_id=self._generate_id(f"perf_rec_{insight.insight_id}"),
                type="optimization",
                priority="high" if insight.impact_score > 0.7 else "medium",
                title=f"优化{insight.title}",
                description=f"基于洞察：{insight.description}",
                rationale=f"置信度：{insight.confidence:.2f}，影响分数：{insight.impact_score:.2f}",
                expected_impact=insight.impact_score,
                confidence=insight.confidence,
                action_items=insight.recommendations,
                created_at=datetime.now()
            )
            return recommendation
            
        except Exception as e:
            logger.error(f"性能推荐生成失败: {str(e)}")
            return None
    
    async def _generate_efficiency_recommendation(self, insight: BusinessInsight) -> Optional[Recommendation]:
        """生成效率推荐"""
        try:
            recommendation = Recommendation(
                recommendation_id=self._generate_id(f"eff_rec_{insight.insight_id}"),
                type="action",
                priority="medium",
                title=f"提升效率：{insight.title}",
                description=f"效率优化机会：{insight.description}",
                rationale=f"发现效率提升机会，置信度：{insight.confidence:.2f}",
                expected_impact=insight.impact_score,
                confidence=insight.confidence,
                action_items=insight.recommendations,
                created_at=datetime.now()
            )
            return recommendation
            
        except Exception as e:
            logger.error(f"效率推荐生成失败: {str(e)}")
            return None
    
    async def _generate_risk_recommendation(self, insight: BusinessInsight) -> Optional[Recommendation]:
        """生成风险推荐"""
        try:
            recommendation = Recommendation(
                recommendation_id=self._generate_id(f"risk_rec_{insight.insight_id}"),
                type="warning",
                priority="high",
                title=f"风险预警：{insight.title}",
                description=f"风险提示：{insight.description}",
                rationale=f"识别到潜在风险，置信度：{insight.confidence:.2f}",
                expected_impact=insight.impact_score,
                confidence=insight.confidence,
                action_items=insight.recommendations,
                created_at=datetime.now()
            )
            return recommendation
            
        except Exception as e:
            logger.error(f"风险推荐生成失败: {str(e)}")
            return None
    
    async def _generate_opportunity_recommendation(self, insight: BusinessInsight) -> Optional[Recommendation]:
        """生成机会推荐"""
        try:
            recommendation = Recommendation(
                recommendation_id=self._generate_id(f"opp_rec_{insight.insight_id}"),
                type="opportunity",
                priority="medium",
                title=f"增长机会：{insight.title}",
                description=f"业务机会：{insight.description}",
                rationale=f"发现增长机会，置信度：{insight.confidence:.2f}",
                expected_impact=insight.impact_score,
                confidence=insight.confidence,
                action_items=insight.recommendations,
                created_at=datetime.now()
            )
            return recommendation
            
        except Exception as e:
            logger.error(f"机会推荐生成失败: {str(e)}")
            return None
    
    async def save_pattern(self, pattern: KnowledgePattern) -> None:
        """保存知识模式"""
        try:
            file_path = self.patterns_dir / f"{pattern.pattern_id}.json"
            self._save_to_file(pattern, file_path)
            self.patterns_cache[pattern.pattern_id] = pattern
        except Exception as e:
            logger.error(f"保存模式失败: {str(e)}")
            raise
    
    async def save_insight(self, insight: BusinessInsight) -> None:
        """保存业务洞察"""
        try:
            file_path = self.insights_dir / f"{insight.insight_id}.json"
            self._save_to_file(insight, file_path)
            self.insights_cache[insight.insight_id] = insight
        except Exception as e:
            logger.error(f"保存洞察失败: {str(e)}")
            raise
    
    async def save_recommendation(self, recommendation: Recommendation) -> None:
        """保存智能推荐"""
        try:
            file_path = self.recommendations_dir / f"{recommendation.recommendation_id}.json"
            self._save_to_file(recommendation, file_path)
            self.recommendations_cache[recommendation.recommendation_id] = recommendation
        except Exception as e:
            logger.error(f"保存推荐失败: {str(e)}")
            raise
    
    async def get_patterns(self, pattern_type: str = None) -> List[KnowledgePattern]:
        """获取知识模式"""
        try:
            patterns = []
            
            for file_path in self.patterns_dir.glob("*.json"):
                data = self._load_from_file(file_path)
                if data:
                    pattern = KnowledgePattern(**data)
                    if pattern_type is None or pattern.pattern_type == pattern_type:
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"获取模式失败: {str(e)}")
            return []
    
    async def get_insights(self, category: str = None) -> List[BusinessInsight]:
        """获取业务洞察"""
        try:
            insights = []
            
            for file_path in self.insights_dir.glob("*.json"):
                data = self._load_from_file(file_path)
                if data:
                    insight = BusinessInsight(**data)
                    if category is None or insight.category == category:
                        insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"获取洞察失败: {str(e)}")
            return []
    
    async def get_recommendations(self, priority: str = None) -> List[Recommendation]:
        """获取智能推荐"""
        try:
            recommendations = []
            
            for file_path in self.recommendations_dir.glob("*.json"):
                data = self._load_from_file(file_path)
                if data:
                    recommendation = Recommendation(**data)
                    if priority is None or recommendation.priority == priority:
                        recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取推荐失败: {str(e)}")
            return []
    
    async def search_similar_patterns(self, query: str, limit: int = 5) -> List[KnowledgePattern]:
        """搜索相似模式"""
        try:
            patterns = await self.get_patterns()
            
            if not patterns:
                return []
            
            # 构建文本向量
            pattern_texts = [f"{p.description} {p.pattern_type}" for p in patterns]
            pattern_texts.append(query)
            
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(pattern_texts)
            
            # 计算相似度
            query_vector = tfidf_matrix[-1]
            pattern_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, pattern_vectors)[0]
            
            # 排序并返回最相似的
            similar_indices = np.argsort(similarities)[::-1][:limit]
            
            return [patterns[i] for i in similar_indices if similarities[i] > 0.1]
            
        except Exception as e:
            logger.error(f"搜索相似模式失败: {str(e)}")
            return []
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            patterns = await self.get_patterns()
            insights = await self.get_insights()
            recommendations = await self.get_recommendations()
            
            # 按类型统计
            pattern_types = Counter(p.pattern_type for p in patterns)
            insight_categories = Counter(i.category for i in insights)
            recommendation_types = Counter(r.type for r in recommendations)
            
            return {
                "total_patterns": len(patterns),
                "total_insights": len(insights),
                "total_recommendations": len(recommendations),
                "pattern_types": dict(pattern_types),
                "insight_categories": dict(insight_categories),
                "recommendation_types": dict(recommendation_types),
                "memory_directory": str(self.memory_dir),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取记忆统计失败: {str(e)}")
            return {}

# 创建全局实例
enterprise_memory_service = EnterpriseMemoryService()

# 示例使用函数
async def demo_enterprise_memory():
    """演示企业记忆功能"""
    print("BMOS企业记忆服务演示")
    print("=" * 50)
    
    # 创建示例数据
    np.random.seed(42)
    n_samples = 500
    
    # 模拟业务数据
    business_data = pd.DataFrame({
        'sales': np.random.normal(1000, 200, n_samples),
        'marketing_spend': np.random.normal(100, 30, n_samples),
        'customer_satisfaction': np.random.normal(4.0, 0.5, n_samples),
        'employee_count': np.random.randint(10, 100, n_samples),
        'profit_margin': np.random.normal(0.15, 0.05, n_samples),
        'success': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    })
    
    print(f"业务数据形状: {business_data.shape}")
    print(f"列名: {list(business_data.columns)}")
    
    # 1. 提取知识模式
    print("\n1. 提取知识模式:")
    patterns = await enterprise_memory_service.extract_patterns_from_data(
        business_data, target_column="success"
    )
    
    print(f"提取到 {len(patterns)} 个知识模式:")
    for pattern in patterns[:3]:  # 只显示前3个
        print(f"  - {pattern.pattern_type}: {pattern.description}")
    
    # 2. 生成业务洞察
    print("\n2. 生成业务洞察:")
    insights = await enterprise_memory_service.generate_business_insights(patterns)
    
    print(f"生成 {len(insights)} 个业务洞察:")
    for insight in insights[:3]:  # 只显示前3个
        print(f"  - {insight.category}: {insight.title}")
    
    # 3. 生成智能推荐
    print("\n3. 生成智能推荐:")
    recommendations = await enterprise_memory_service.generate_recommendations(insights)
    
    print(f"生成 {len(recommendations)} 个智能推荐:")
    for rec in recommendations[:3]:  # 只显示前3个
        print(f"  - {rec.type}: {rec.title}")
    
    # 4. 搜索相似模式
    print("\n4. 搜索相似模式:")
    similar_patterns = await enterprise_memory_service.search_similar_patterns("销售成功")
    
    print(f"找到 {len(similar_patterns)} 个相似模式:")
    for pattern in similar_patterns[:2]:  # 只显示前2个
        print(f"  - {pattern.description}")
    
    # 5. 获取记忆统计
    print("\n5. 获取记忆统计:")
    stats = await enterprise_memory_service.get_memory_stats()
    
    print(f"记忆统计:")
    print(f"  知识模式: {stats['total_patterns']}")
    print(f"  业务洞察: {stats['total_insights']}")
    print(f"  智能推荐: {stats['total_recommendations']}")
    print(f"  模式类型: {stats['pattern_types']}")
    print(f"  洞察类别: {stats['insight_categories']}")
    
    print("\n企业记忆服务演示完成!")

if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_enterprise_memory())

