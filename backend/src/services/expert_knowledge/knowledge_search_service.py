"""
知识搜索服务
提供语义搜索、相关性排序、知识推荐等功能
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService

logger = logging.getLogger(__name__)

# 尝试导入语义搜索库（可选依赖）
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers 未安装，语义搜索功能将降级为关键词搜索")


class KnowledgeSearchService:
    """知识搜索服务"""
    
    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        cache_service: Optional[CacheService] = None
    ):
        self.db_service = db_service
        self.cache_service = cache_service
        
        # TF-IDF向量化器（用于关键词搜索）
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # 语义搜索模型（可选）
        self.semantic_model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # 使用轻量级中文模型
                self.semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("语义搜索模型加载成功")
            except Exception as e:
                logger.warning(f"语义搜索模型加载失败，将使用关键词搜索: {e}")
                self.semantic_model = None
    
    async def semantic_search(
        self,
        query: str,
        tenant_id: str,
        domain_category: Optional[str] = None,
        problem_type: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """语义搜索（基于向量嵌入）"""
        try:
            # 先获取候选知识
            candidates = await self._get_candidate_knowledge(
                tenant_id=tenant_id,
                domain_category=domain_category,
                problem_type=problem_type,
                limit=100  # 获取更多候选以便排序
            )
            
            if not candidates:
                return []
            
            # 生成查询向量
            if self.semantic_model:
                query_embedding = self.semantic_model.encode([query])[0]
            else:
                # 降级为关键词搜索
                return await self.keyword_search(query, tenant_id, domain_category, problem_type, limit)
            
            # 计算相似度
            results_with_scores = []
            
            for candidate in candidates:
                # 生成知识向量
                knowledge_text = f"{candidate.get('title', '')} {candidate.get('summary', '')} {candidate.get('content', '')[:500]}"
                knowledge_embedding = self.semantic_model.encode([knowledge_text])[0]
                
                # 计算余弦相似度
                similarity = float(np.dot(query_embedding, knowledge_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(knowledge_embedding)
                ))
                
                if similarity >= min_similarity:
                    candidate['similarity_score'] = similarity
                    results_with_scores.append(candidate)
            
            # 按相似度排序
            results_with_scores.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            return results_with_scores[:limit]
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            # 降级为关键词搜索
            return await self.keyword_search(query, tenant_id, domain_category, problem_type, limit)
    
    async def keyword_search(
        self,
        query: str,
        tenant_id: str,
        domain_category: Optional[str] = None,
        problem_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """关键词搜索（使用PostgreSQL全文搜索）"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，返回空结果")
                return []
            
            # 构建查询条件
            conditions = [
                "tenant_id = :tenant_id",
                "is_active = true",
                "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, '')) @@ plainto_tsquery('english', :query)"
            ]
            params = {'tenant_id': tenant_id, 'query': query}
            
            if domain_category:
                conditions.append("domain_category = :domain_category")
                params['domain_category'] = domain_category
            
            if problem_type:
                conditions.append("problem_type = :problem_type")
                params['problem_type'] = problem_type
            
            where_clause = " AND ".join(conditions)
            
            # 查询（按相关性排序）
            query_sql = f"""
                SELECT *,
                    ts_rank(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, '')), 
                           plainto_tsquery('english', :query)) as rank
                FROM expert_knowledge
                WHERE {where_clause}
                ORDER BY rank DESC, applied_count DESC, created_at DESC
                LIMIT :limit
            """
            params['limit'] = limit
            
            results = await self.db_service.fetch_all(query_sql, params)
            
            return results or []
            
        except Exception as e:
            logger.error(f"关键词搜索失败: {e}")
            return []
    
    async def category_filter(
        self,
        tenant_id: str,
        domain_category: Optional[str] = None,
        problem_type: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """分类过滤"""
        try:
            if not self.db_service:
                return []
            
            conditions = ["tenant_id = :tenant_id", "is_active = true"]
            params = {'tenant_id': tenant_id}
            
            if domain_category:
                conditions.append("domain_category = :domain_category")
                params['domain_category'] = domain_category
            
            if problem_type:
                conditions.append("problem_type = :problem_type")
                params['problem_type'] = problem_type
            
            if knowledge_type:
                conditions.append("knowledge_type = :knowledge_type")
                params['knowledge_type'] = knowledge_type
            
            if verification_status:
                conditions.append("verification_status = :verification_status")
                params['verification_status'] = verification_status
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT * FROM expert_knowledge
                WHERE {where_clause}
                ORDER BY 
                    CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END DESC,
                    relevance_score DESC,
                    applied_count DESC
                LIMIT :limit
            """
            params['limit'] = limit
            
            results = await self.db_service.fetch_all(query, params)
            
            return results or []
            
        except Exception as e:
            logger.error(f"分类过滤失败: {e}")
            return []
    
    async def relevance_ranking(
        self,
        knowledge_list: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """相关性排序"""
        try:
            # 计算相关性得分
            for knowledge in knowledge_list:
                relevance = 0.0
                
                # 基础得分：验证状态
                if knowledge.get('verification_status') == 'verified':
                    relevance += 0.3
                
                # 应用统计得分
                applied_count = knowledge.get('applied_count', 0)
                if applied_count > 0:
                    success_rate = knowledge.get('success_rate', 0.5) or 0.5
                    relevance += min(0.3, success_rate * 0.3)
                
                # 已有相关性得分
                existing_score = knowledge.get('relevance_score', 0.5) or 0.5
                relevance += existing_score * 0.2
                
                # 上下文相关性（如果有）
                if context:
                    context_relevance = self._calculate_context_relevance(knowledge, context)
                    relevance += context_relevance * 0.2
                
                knowledge['calculated_relevance'] = min(1.0, relevance)
            
            # 按相关性排序
            knowledge_list.sort(key=lambda x: x.get('calculated_relevance', 0), reverse=True)
            
            return knowledge_list
            
        except Exception as e:
            logger.error(f"相关性排序失败: {e}")
            return knowledge_list
    
    async def recommend_knowledge(
        self,
        tenant_id: str,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """推荐相关知识"""
        try:
            # 从上下文中提取搜索关键词
            query_parts = []
            
            if context.get('domain_category'):
                query_parts.append(context['domain_category'])
            
            if context.get('problem_type'):
                query_parts.append(context['problem_type'])
            
            if context.get('description'):
                query_parts.append(context['description'][:100])
            
            query = ' '.join(query_parts) if query_parts else None
            
            # 执行搜索
            if query:
                results = await self.semantic_search(
                    query=query,
                    tenant_id=tenant_id,
                    domain_category=context.get('domain_category'),
                    problem_type=context.get('problem_type'),
                    limit=limit * 2  # 获取更多候选
                )
            else:
                results = await self.category_filter(
                    tenant_id=tenant_id,
                    domain_category=context.get('domain_category'),
                    problem_type=context.get('problem_type'),
                    limit=limit * 2
                )
            
            # 相关性排序
            ranked_results = await self.relevance_ranking(results, context)
            
            # 过滤：优先推荐已验证的知识
            verified_results = [r for r in ranked_results if r.get('verification_status') == 'verified']
            other_results = [r for r in ranked_results if r.get('verification_status') != 'verified']
            
            final_results = verified_results[:limit] + other_results[:max(0, limit - len(verified_results))]
            
            return final_results[:limit]
            
        except Exception as e:
            logger.error(f"推荐知识失败: {e}")
            return []
    
    # ========== 私有辅助方法 ==========
    
    async def _get_candidate_knowledge(
        self,
        tenant_id: str,
        domain_category: Optional[str] = None,
        problem_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取候选知识（用于排序）"""
        try:
            if not self.db_service:
                return []
            
            conditions = ["tenant_id = :tenant_id", "is_active = true"]
            params = {'tenant_id': tenant_id}
            
            if domain_category:
                conditions.append("domain_category = :domain_category")
                params['domain_category'] = domain_category
            
            if problem_type:
                conditions.append("problem_type = :problem_type")
                params['problem_type'] = problem_type
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT id, title, summary, content, domain_category, problem_type, 
                       knowledge_type, verification_status, applied_count, success_rate, relevance_score
                FROM expert_knowledge
                WHERE {where_clause}
                LIMIT :limit
            """
            params['limit'] = limit
            
            results = await self.db_service.fetch_all(query, params)
            
            return results or []
            
        except Exception as e:
            logger.error(f"获取候选知识失败: {e}")
            return []
    
    def _calculate_context_relevance(
        self,
        knowledge: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """计算上下文相关性"""
        relevance = 0.0
        
        # 领域匹配
        if knowledge.get('domain_category') == context.get('domain_category'):
            relevance += 0.4
        
        # 问题类型匹配
        if knowledge.get('problem_type') == context.get('problem_type'):
            relevance += 0.4
        
        # 知识类型匹配（如果有）
        if context.get('knowledge_type') and knowledge.get('knowledge_type') == context.get('knowledge_type'):
            relevance += 0.2
        
        return min(1.0, relevance)

