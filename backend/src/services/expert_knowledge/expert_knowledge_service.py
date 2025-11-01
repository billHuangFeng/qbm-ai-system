"""
专家知识服务
提供专家知识的CRUD、搜索、分类管理等功能
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from ...services.database_service import DatabaseService
from ...services.cache_service import CacheService

logger = logging.getLogger(__name__)


class ExpertKnowledgeService:
    """专家知识服务"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None, cache_service: Optional[CacheService] = None):
        self.db_service = db_service
        self.cache_service = cache_service
        
        # 知识类型枚举
        self.knowledge_types = [
            'theory',           # 理论框架
            'methodology',      # 方法论
            'case_study',       # 案例研究
            'tool_template',    # 工具模板
            'best_practice',    # 最佳实践
            'warning'           # 警示教训
        ]
        
        # 领域分类
        self.domain_categories = [
            'business_model',      # 商业模式
            'cost_optimization',    # 成本优化
            'resource_allocation',  # 资源分配
            'capability_enhancement', # 能力增强
            'market_strategy',      # 市场策略
            'product_design',       # 产品设计
            'risk_management',      # 风险管理
            'performance_measurement' # 绩效测量
        ]
        
        # 问题类型
        self.problem_types = [
            'decision_problem',     # 决策问题
            'optimization_problem', # 优化问题
            'risk_problem',         # 风险问题
            'innovation_problem',   # 创新问题
            'retrospective_problem' # 复盘问题
        ]
    
    async def create_knowledge(
        self,
        tenant_id: str,
        title: str,
        content: str,
        knowledge_type: str,
        domain_category: str,
        problem_type: str,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_type: str = 'manual_entry',
        source_reference: Optional[str] = None,
        is_public: bool = False,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建知识条目"""
        try:
            knowledge_id = str(uuid.uuid4())
            
            # 验证分类
            if knowledge_type not in self.knowledge_types:
                raise ValueError(f"无效的知识类型: {knowledge_type}")
            if domain_category not in self.domain_categories:
                raise ValueError(f"无效的领域分类: {domain_category}")
            if problem_type not in self.problem_types:
                raise ValueError(f"无效的问题类型: {problem_type}")
            
            knowledge_data = {
                'id': knowledge_id,
                'tenant_id': tenant_id,
                'title': title,
                'summary': summary or self._generate_summary(content),
                'content': content,
                'knowledge_type': knowledge_type,
                'domain_category': domain_category,
                'problem_type': problem_type,
                'tags': tags or [],
                'source_type': source_type,
                'source_reference': source_reference,
                'verification_status': 'pending',
                'applied_count': 0,
                'relevance_score': 0.5,
                'is_active': True,
                'is_public': is_public,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # 保存到数据库
            if self.db_service:
                await self.db_service.insert('expert_knowledge', knowledge_data)
            else:
                logger.warning("数据库服务未初始化，知识条目仅存储在内存中")
            
            logger.info(f"创建知识条目成功: {knowledge_id}, 标题: {title}")
            
            return {
                'success': True,
                'knowledge_id': knowledge_id,
                'knowledge': knowledge_data
            }
            
        except Exception as e:
            logger.error(f"创建知识条目失败: {e}")
            raise
    
    async def get_knowledge_by_id(self, knowledge_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取知识详情"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，无法获取知识详情")
                return None
            
            query = "SELECT * FROM expert_knowledge WHERE id = :id"
            params = {'id': knowledge_id}
            
            if tenant_id:
                query += " AND tenant_id = :tenant_id"
                params['tenant_id'] = tenant_id
            
            knowledge = await self.db_service.fetch_one(query, params)
            
            if knowledge:
                # 获取关联的附件
                attachments = await self._get_attachments(knowledge_id)
                knowledge['attachments'] = attachments
                
                return knowledge
            
            return None
            
        except Exception as e:
            logger.error(f"获取知识详情失败: {e}")
            return None
    
    async def update_knowledge(
        self,
        knowledge_id: str,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新知识"""
        try:
            # 验证更新字段
            allowed_fields = [
                'title', 'summary', 'content', 'knowledge_type',
                'domain_category', 'problem_type', 'tags',
                'source_reference', 'is_active', 'is_public'
            ]
            
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            filtered_updates['updated_at'] = datetime.now()
            
            if not self.db_service:
                logger.warning("数据库服务未初始化，无法更新知识")
                return {'success': False, 'message': '数据库服务未初始化'}
            
            # 执行更新
            result = await self.db_service.update(
                'expert_knowledge',
                {'id': knowledge_id, 'tenant_id': tenant_id},
                filtered_updates
            )
            
            logger.info(f"更新知识成功: {knowledge_id}")
            
            return {
                'success': True,
                'knowledge_id': knowledge_id,
                'updated_fields': list(filtered_updates.keys())
            }
            
        except Exception as e:
            logger.error(f"更新知识失败: {e}")
            raise
    
    async def delete_knowledge(self, knowledge_id: str, tenant_id: str) -> Dict[str, Any]:
        """删除知识（软删除，标记为不活跃）"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，无法删除知识")
                return {'success': False, 'message': '数据库服务未初始化'}
            
            # 软删除：标记为不活跃
            await self.db_service.update(
                'expert_knowledge',
                {'id': knowledge_id, 'tenant_id': tenant_id},
                {
                    'is_active': False,
                    'updated_at': datetime.now()
                }
            )
            
            logger.info(f"删除知识成功: {knowledge_id}")
            
            return {
                'success': True,
                'knowledge_id': knowledge_id
            }
            
        except Exception as e:
            logger.error(f"删除知识失败: {e}")
            raise
    
    async def search_knowledge(
        self,
        tenant_id: str,
        query: Optional[str] = None,
        domain_category: Optional[str] = None,
        problem_type: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verification_status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """多维度搜索知识"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，返回空结果")
                return {'total': 0, 'knowledge_list': []}
            
            # 构建查询
            conditions = ["tenant_id = :tenant_id", "is_active = true"]
            params = {'tenant_id': tenant_id}
            
            if query:
                # 全文搜索
                conditions.append(
                    "(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(content, '')) @@ plainto_tsquery('english', :query))"
                )
                params['query'] = query
            
            if domain_category:
                conditions.append("domain_category = :domain_category")
                params['domain_category'] = domain_category
            
            if problem_type:
                conditions.append("problem_type = :problem_type")
                params['problem_type'] = problem_type
            
            if knowledge_type:
                conditions.append("knowledge_type = :knowledge_type")
                params['knowledge_type'] = knowledge_type
            
            if tags:
                conditions.append("tags && :tags")
                params['tags'] = tags
            
            if verification_status:
                conditions.append("verification_status = :verification_status")
                params['verification_status'] = verification_status
            
            where_clause = " AND ".join(conditions)
            
            # 查询总数
            count_query = f"SELECT COUNT(*) as total FROM expert_knowledge WHERE {where_clause}"
            total_result = await self.db_service.fetch_one(count_query, params)
            total = total_result.get('total', 0) if total_result else 0
            
            # 查询数据
            search_query = f"""
                SELECT * FROM expert_knowledge
                WHERE {where_clause}
                ORDER BY 
                    CASE WHEN relevance_score IS NOT NULL THEN relevance_score ELSE 0 END DESC,
                    applied_count DESC,
                    created_at DESC
                LIMIT :limit OFFSET :offset
            """
            params['limit'] = limit
            params['offset'] = offset
            
            results = await self.db_service.fetch_all(search_query, params)
            
            return {
                'total': total,
                'limit': limit,
                'offset': offset,
                'knowledge_list': results or []
            }
            
        except Exception as e:
            logger.error(f"搜索知识失败: {e}")
            return {'total': 0, 'knowledge_list': []}
    
    async def get_related_knowledge(
        self,
        knowledge_id: str,
        tenant_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取相关知识（基于分类和标签）"""
        try:
            # 先获取当前知识
            knowledge = await self.get_knowledge_by_id(knowledge_id, tenant_id)
            if not knowledge:
                return []
            
            # 基于分类和标签搜索相关知识
            related = await self.search_knowledge(
                tenant_id=tenant_id,
                domain_category=knowledge.get('domain_category'),
                problem_type=knowledge.get('problem_type'),
                tags=knowledge.get('tags', []),
                limit=limit + 1  # +1 排除自己
            )
            
            # 过滤掉当前知识
            related_list = [
                k for k in related.get('knowledge_list', [])
                if k.get('id') != knowledge_id
            ][:limit]
            
            return related_list
            
        except Exception as e:
            logger.error(f"获取相关知识失败: {e}")
            return []
    
    async def apply_knowledge(
        self,
        knowledge_id: str,
        tenant_id: str,
        user_id: str,
        application_context: str,
        application_type: str,
        applied_content: str,
        decision_id: Optional[str] = None,
        related_service: Optional[str] = None,
        reasoning_excerpt: Optional[str] = None
    ) -> Dict[str, Any]:
        """记录知识应用"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，无法记录知识应用")
                return {'success': False}
            
            application_data = {
                'id': str(uuid.uuid4()),
                'knowledge_id': knowledge_id,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'application_context': application_context,
                'application_type': application_type,
                'applied_content': applied_content,
                'decision_id': decision_id,
                'related_service': related_service,
                'reasoning_excerpt': reasoning_excerpt,
                'applied_at': datetime.now()
            }
            
            await self.db_service.insert('knowledge_application_history', application_data)
            
            # 更新知识应用统计
            await self._update_application_stats(knowledge_id)
            
            logger.info(f"记录知识应用成功: knowledge_id={knowledge_id}, context={application_context}")
            
            return {
                'success': True,
                'application_id': application_data['id']
            }
            
        except Exception as e:
            logger.error(f"记录知识应用失败: {e}")
            return {'success': False}
    
    async def verify_knowledge(
        self,
        knowledge_id: str,
        tenant_id: str,
        verified_by: str,
        verification_status: str,
        verification_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证知识（严谨性检查）"""
        try:
            if not self.db_service:
                logger.warning("数据库服务未初始化，无法验证知识")
                return {'success': False}
            
            if verification_status not in ['pending', 'verified', 'rejected']:
                raise ValueError(f"无效的验证状态: {verification_status}")
            
            update_data = {
                'verification_status': verification_status,
                'verified_by': verified_by,
                'verification_notes': verification_notes,
                'verified_at': datetime.now() if verification_status != 'pending' else None,
                'updated_at': datetime.now()
            }
            
            await self.db_service.update(
                'expert_knowledge',
                {'id': knowledge_id, 'tenant_id': tenant_id},
                update_data
            )
            
            logger.info(f"验证知识成功: knowledge_id={knowledge_id}, status={verification_status}")
            
            return {
                'success': True,
                'knowledge_id': knowledge_id,
                'verification_status': verification_status
            }
            
        except Exception as e:
            logger.error(f"验证知识失败: {e}")
            raise
    
    async def import_knowledge_from_document(
        self,
        tenant_id: str,
        title: str,
        file_path: str,
        file_type: str,
        domain_category: str,
        problem_type: str,
        knowledge_type: str = 'methodology',
        source_reference: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """从文档导入知识（需要配合DocumentProcessingService使用）"""
        try:
            # 这里应该调用 DocumentProcessingService 提取文本
            # 暂时返回占位符
            logger.info(f"准备从文档导入知识: {file_path}")
            
            # 实际实现时需要：
            # 1. 使用 DocumentProcessingService 提取文本
            # 2. 解析文档结构
            # 3. 创建知识条目
            # 4. 保存附件信息
            
            return {
                'success': False,
                'message': '文档导入功能待实现，需要配合 DocumentProcessingService'
            }
            
        except Exception as e:
            logger.error(f"从文档导入知识失败: {e}")
            raise
    
    # 私有辅助方法
    
    async def _get_attachments(self, knowledge_id: str) -> List[Dict[str, Any]]:
        """获取知识附件"""
        try:
            if not self.db_service:
                return []
            
            query = "SELECT * FROM knowledge_attachments WHERE knowledge_id = :knowledge_id ORDER BY created_at"
            attachments = await self.db_service.fetch_all(query, {'knowledge_id': knowledge_id})
            
            return attachments or []
            
        except Exception as e:
            logger.error(f"获取附件失败: {e}")
            return []
    
    async def _update_application_stats(self, knowledge_id: str):
        """更新知识应用统计"""
        try:
            if not self.db_service:
                return
            
            # 查询应用历史
            query = """
                SELECT 
                    COUNT(*) as applied_count,
                    COUNT(*) FILTER (WHERE was_helpful = true) as successful_count,
                    AVG(impact_score) as avg_impact_score
                FROM knowledge_application_history
                WHERE knowledge_id = :knowledge_id
            """
            stats = await self.db_service.fetch_one(query, {'knowledge_id': knowledge_id})
            
            if stats:
                applied_count = stats.get('applied_count', 0) or 0
                successful_count = stats.get('successful_count', 0) or 0
                success_rate = (successful_count / applied_count) if applied_count > 0 else None
                
                await self.db_service.update(
                    'expert_knowledge',
                    {'id': knowledge_id},
                    {
                        'applied_count': applied_count,
                        'successful_application_count': successful_count,
                        'success_rate': success_rate,
                        'updated_at': datetime.now()
                    }
                )
                
        except Exception as e:
            logger.error(f"更新应用统计失败: {e}")
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成摘要"""
        if len(content) <= max_length:
            return content
        
        # 简单截取前max_length个字符
        summary = content[:max_length]
        # 尝试在句号处截断
        last_period = summary.rfind('。')
        if last_period > max_length * 0.7:  # 如果句号位置不太靠前
            summary = summary[:last_period + 1]
        else:
            summary = summary + "..."
        
        return summary


