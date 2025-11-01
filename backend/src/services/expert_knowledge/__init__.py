"""
专家知识库服务模块
提供专家知识管理、文档处理、知识搜索、学习服务和AI集成功能
"""

from .expert_knowledge_service import ExpertKnowledgeService
from .document_processing_service import DocumentProcessingService
from .knowledge_search_service import KnowledgeSearchService
from .learning_service import LearningService
from .knowledge_integration_service import KnowledgeIntegrationService

__all__ = [
    "ExpertKnowledgeService",
    "DocumentProcessingService",
    "KnowledgeSearchService",
    "LearningService",
    "KnowledgeIntegrationService",
]

