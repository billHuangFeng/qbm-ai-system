"""
知识集成服务
提供与AI决策系统的集成功能，包括知识搜索、应用和推理链生成
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .expert_knowledge_service import ExpertKnowledgeService
from .knowledge_search_service import KnowledgeSearchService
from ...services.enterprise_memory_service import EnterpriseMemoryService

logger = logging.getLogger(__name__)


class KnowledgeIntegrationService:
    """知识集成服务"""
    
    def __init__(
        self,
        knowledge_service: ExpertKnowledgeService,
        search_service: KnowledgeSearchService,
        memory_service: Optional[EnterpriseMemoryService] = None
    ):
        self.knowledge_service = knowledge_service
        self.search_service = search_service
        self.memory_service = memory_service
    
    async def search_relevant_knowledge(
        self,
        tenant_id: str,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """在AI决策时搜索相关知识"""
        try:
            # 从上下文中提取信息
            domain_category = context.get('domain_category')
            problem_type = context.get('problem_type')
            description = context.get('description') or context.get('requirement_description', '')
            
            # 使用语义搜索
            results = await self.search_service.recommend_knowledge(
                tenant_id=tenant_id,
                context={
                    'domain_category': domain_category,
                    'problem_type': problem_type,
                    'description': description
                },
                limit=limit
            )
            
            logger.info(f"搜索到 {len(results)} 条相关专家知识")
            
            return results
            
        except Exception as e:
            logger.error(f"搜索相关知识失败: {e}")
            return []
    
    async def apply_knowledge_to_decision(
        self,
        knowledge_id: str,
        tenant_id: str,
        user_id: str,
        decision_context: Dict[str, Any],
        application_type: str = 'reasoning',
        reasoning_excerpt: Optional[str] = None
    ) -> Dict[str, Any]:
        """将专家知识应用到决策过程"""
        try:
            # 获取知识详情
            knowledge = await self.knowledge_service.get_knowledge_by_id(knowledge_id, tenant_id)
            
            if not knowledge:
                raise ValueError("知识不存在")
            
            # 记录应用
            applied_content = f"{knowledge.get('title', '')}: {knowledge.get('summary', '')[:200]}"
            
            result = await self.knowledge_service.apply_knowledge(
                knowledge_id=knowledge_id,
                tenant_id=tenant_id,
                user_id=user_id,
                application_context=decision_context.get('context', 'decision_making'),
                application_type=application_type,
                applied_content=applied_content,
                decision_id=decision_context.get('decision_id'),
                related_service=decision_context.get('service_name'),
                reasoning_excerpt=reasoning_excerpt
            )
            
            logger.info(f"知识应用成功: knowledge_id={knowledge_id}, type={application_type}")
            
            return {
                'success': True,
                'knowledge': knowledge,
                'application_result': result
            }
            
        except Exception as e:
            logger.error(f"应用知识到决策失败: {e}")
            raise
    
    async def combine_with_enterprise_memory(
        self,
        tenant_id: str,
        context: Dict[str, Any],
        expert_knowledge_limit: int = 3,
        memory_limit: int = 3
    ) -> Dict[str, Any]:
        """与企业记忆系统结合"""
        try:
            combined_results = {
                'expert_knowledge': [],
                'enterprise_memory': [],
                'combined_recommendations': []
            }
            
            # 搜索专家知识
            expert_knowledge = await self.search_relevant_knowledge(
                tenant_id=tenant_id,
                context=context,
                limit=expert_knowledge_limit
            )
            combined_results['expert_knowledge'] = expert_knowledge
            
            # 搜索企业记忆（如果可用）
            if self.memory_service:
                try:
                    # 构建搜索查询
                    query = context.get('description', '') or context.get('requirement_description', '')
                    if not query:
                        query = f"{context.get('domain_category', '')} {context.get('problem_type', '')}"
                    
                    # 使用企业记忆服务的搜索功能
                    if hasattr(self.memory_service, 'search_similar_patterns'):
                        memory_results = await self.memory_service.search_similar_patterns(
                            query=query,
                            limit=memory_limit
                        )
                        
                        # 转换为字典格式
                        if memory_results:
                            memory_list = []
                            for mem in memory_results:
                                if hasattr(mem, 'dict'):
                                    memory_list.append(mem.dict())
                                else:
                                    memory_list.append(mem)
                            combined_results['enterprise_memory'] = memory_list
                            
                except Exception as e:
                    logger.warning(f"搜索企业记忆失败: {e}")
            
            # 生成综合推荐
            combined_recommendations = self._generate_combined_recommendations(
                expert_knowledge=expert_knowledge,
                enterprise_memory=combined_results.get('enterprise_memory', []),
                context=context
            )
            combined_results['combined_recommendations'] = combined_recommendations
            
            return combined_results
            
        except Exception as e:
            logger.error(f"结合企业记忆失败: {e}")
            return {
                'expert_knowledge': [],
                'enterprise_memory': [],
                'combined_recommendations': []
            }
    
    async def generate_reasoning_chain(
        self,
        tenant_id: str,
        decision_context: Dict[str, Any],
        include_data_evidence: bool = True
    ) -> Dict[str, Any]:
        """生成推理链（结合专家知识+企业记忆+数据）"""
        try:
            reasoning_chain = {
                'decision_context': decision_context,
                'expert_knowledge': [],
                'enterprise_memory': [],
                'data_evidence': {},
                'reasoning_steps': [],
                'conclusion': None
            }
            
            # 1. 搜索专家知识（理论框架）
            expert_knowledge = await self.search_relevant_knowledge(
                tenant_id=tenant_id,
                context=decision_context,
                limit=3
            )
            reasoning_chain['expert_knowledge'] = expert_knowledge
            
            # 2. 搜索企业记忆（实践经验）
            if self.memory_service:
                combined = await self.combine_with_enterprise_memory(
                    tenant_id=tenant_id,
                    context=decision_context,
                    expert_knowledge_limit=3,
                    memory_limit=3
                )
                reasoning_chain['enterprise_memory'] = combined.get('enterprise_memory', [])
            
            # 3. 生成推理步骤
            reasoning_steps = []
            
            # 步骤1: 理论依据（专家知识）
            if expert_knowledge:
                for knowledge in expert_knowledge[:2]:  # 取前2个
                    reasoning_steps.append({
                        'step_type': 'theory',
                        'source': 'expert_knowledge',
                        'title': knowledge.get('title'),
                        'summary': knowledge.get('summary'),
                        'reasoning': f"根据专家知识「{knowledge.get('title')}」，{knowledge.get('summary', '')[:100]}"
                    })
            
            # 步骤2: 实践证据（企业记忆）
            if reasoning_chain.get('enterprise_memory'):
                for memory in reasoning_chain['enterprise_memory'][:2]:  # 取前2个
                    memory_desc = memory.get('description', '') or memory.get('memory_description', '')
                    reasoning_steps.append({
                        'step_type': 'practice',
                        'source': 'enterprise_memory',
                        'title': memory.get('title') or memory.get('memory_title', ''),
                        'summary': memory_desc[:200] if memory_desc else '',
                        'reasoning': f"基于历史实践「{memory.get('title', '未知')}」，我们之前有过类似经验"
                    })
            
            # 步骤3: 数据支撑（如果有）
            if include_data_evidence and decision_context.get('data_evidence'):
                data_evidence = decision_context['data_evidence']
                reasoning_steps.append({
                    'step_type': 'data',
                    'source': 'data_analysis',
                    'title': '数据分析结果',
                    'summary': str(data_evidence),
                    'reasoning': f"数据分析表明：{data_evidence.get('summary', '数据支撑决策')}"
                })
                reasoning_chain['data_evidence'] = data_evidence
            
            reasoning_chain['reasoning_steps'] = reasoning_steps
            
            # 4. 生成综合结论
            conclusion = self._generate_conclusion(
                expert_knowledge=expert_knowledge,
                enterprise_memory=reasoning_chain.get('enterprise_memory', []),
                data_evidence=reasoning_chain.get('data_evidence'),
                context=decision_context
            )
            reasoning_chain['conclusion'] = conclusion
            
            return reasoning_chain
            
        except Exception as e:
            logger.error(f"生成推理链失败: {e}")
            raise
    
    # ========== 私有辅助方法 ==========
    
    def _generate_combined_recommendations(
        self,
        expert_knowledge: List[Dict[str, Any]],
        enterprise_memory: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成综合推荐"""
        recommendations = []
        
        # 专家知识推荐（理论框架）
        for knowledge in expert_knowledge:
            recommendations.append({
                'type': 'expert_knowledge',
                'source': '理论框架',
                'title': knowledge.get('title'),
                'summary': knowledge.get('summary'),
                'recommendation': f"建议参考：{knowledge.get('title')}",
                'rationale': knowledge.get('summary', '')[:200],
                'priority': 'high' if knowledge.get('verification_status') == 'verified' else 'medium'
            })
        
        # 企业记忆推荐（实践经验）
        for memory in enterprise_memory:
            memory_title = memory.get('title') or memory.get('memory_title', '未知')
            memory_desc = memory.get('description') or memory.get('memory_description', '')
            
            recommendations.append({
                'type': 'enterprise_memory',
                'source': '实践经验',
                'title': memory_title,
                'summary': memory_desc[:200] if memory_desc else '',
                'recommendation': f"历史案例：{memory_title}",
                'rationale': memory_desc[:200] if memory_desc else '',
                'priority': 'medium'
            })
        
        return recommendations
    
    def _generate_conclusion(
        self,
        expert_knowledge: List[Dict[str, Any]],
        enterprise_memory: List[Dict[str, Any]],
        data_evidence: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成综合结论"""
        conclusion = {
            'summary': '',
            'recommendations': [],
            'confidence': 0.5,
            'sources': []
        }
        
        # 生成结论摘要
        summary_parts = []
        
        if expert_knowledge:
            summary_parts.append(f"专家知识提供了 {len(expert_knowledge)} 个理论框架")
        
        if enterprise_memory:
            summary_parts.append(f"企业记忆提供了 {len(enterprise_memory)} 个实践经验")
        
        if data_evidence:
            summary_parts.append("数据分析提供了数据支撑")
        
        conclusion['summary'] = '；'.join(summary_parts) if summary_parts else "基于现有信息生成决策建议"
        
        # 推荐建议
        if expert_knowledge:
            top_knowledge = expert_knowledge[0]
            conclusion['recommendations'].append({
                'type': 'expert_knowledge',
                'title': top_knowledge.get('title'),
                'description': top_knowledge.get('summary', '')[:200]
            })
        
        # 置信度计算
        confidence = 0.5  # 基础置信度
        
        if expert_knowledge:
            # 有验证的专家知识提高置信度
            verified_count = sum(1 for k in expert_knowledge if k.get('verification_status') == 'verified')
            confidence += 0.2 * (verified_count / len(expert_knowledge))
        
        if enterprise_memory:
            # 有企业记忆提高置信度
            confidence += 0.2
        
        if data_evidence:
            # 有数据支撑提高置信度
            confidence += 0.1
        
        conclusion['confidence'] = min(1.0, confidence)
        
        # 来源
        conclusion['sources'] = [
            {'type': 'expert_knowledge', 'count': len(expert_knowledge)},
            {'type': 'enterprise_memory', 'count': len(enterprise_memory)},
            {'type': 'data_evidence', 'count': 1 if data_evidence else 0}
        ]
        
        return conclusion

