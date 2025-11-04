"""
BMOS系统 - 智能字段映射器
作用: 实现智能字段映射推荐，支持历史映射、规则匹配和相似度计算
状态: ✅ 实施中
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from difflib import SequenceMatcher
import logging
import re
import asyncio
from datetime import datetime

import pandas as pd

from ...database_service import DatabaseService
from ...base import BaseService

logger = logging.getLogger(__name__)


@dataclass
class MappingCandidate:
    """映射候选"""
    target_field: str
    confidence: float  # 0-1
    method: str  # 'history', 'similarity', 'rule', 'manual'
    source: str  # 推荐来源描述


@dataclass
class FieldMappingRecommendation:
    """字段映射推荐结果"""
    source_field: str
    candidates: List[MappingCandidate]
    recommended_target: Optional[str] = None
    recommended_confidence: float = 0.0


class IntelligentFieldMapper(BaseService):
    """智能字段映射器"""
    
    # 内存缓存（进程内缓存，用于快速访问）
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    _cache_lock = {}
    
    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        cache_service: Optional[Any] = None
    ):
        super().__init__(db_service)
        self.cache_service = cache_service
        
        if not db_service:
            raise ValueError("数据库服务是必需的，无法使用硬编码降级方案")
        
        # 缓存配置
        self.cache_ttl = {
            'table_fields': 86400,  # 24小时 - 表结构变化不频繁
            'master_data_fields': 86400,  # 24小时
            'foreign_keys': 86400,  # 24小时
        }
        
        # 缓存键前缀
        self.cache_prefix = 'field_mapper'
    
    async def recommend_mappings(
        self,
        source_fields: List[str],
        source_system: str,
        target_table: str,
        document_type: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[FieldMappingRecommendation]:
        """推荐字段映射
        
        Args:
            source_fields: 源文件字段列表
            source_system: 数据源系统
            target_table: 目标表名（必需，用于动态获取字段）
            document_type: 单据类型
            user_id: 用户ID（可选，用于个人化推荐）
            context: 额外上下文信息
        
        Returns:
            映射推荐列表
        
        Raises:
            ValueError: 如果 target_table 未提供或数据库服务不可用
        """
        if not target_table:
            raise ValueError("target_table 是必需的，必须提供目标表名以从数据库获取字段")
        
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法进行字段映射推荐")
        
        recommendations = []
        
        # 从数据库动态获取标准字段列表（使用缓存）
        standard_fields = await self._get_standard_fields_from_db(
            target_table, document_type, use_cache=True
        )
        
        for source_field in source_fields:
            candidates = []
            
            # 1. 查询历史映射（优先）
            history_candidates = await self._get_history_mappings(
                source_field, source_system, document_type, user_id
            )
            candidates.extend(history_candidates)
            
            # 2. 应用映射规则
            rule_candidates = self._apply_mapping_rules(
                source_field, source_system, document_type
            )
            candidates.extend(rule_candidates)
            
            # 3. 计算相似度匹配（如果没有历史记录或规则）
            if not candidates or max(c.confidence for c in candidates) < 0.8:
                similarity_candidates = self._calculate_similarity_mappings(
                    source_field, standard_fields
                )
                candidates.extend(similarity_candidates)
            
            # 4. 排序和去重
            candidates = self._deduplicate_and_sort_candidates(candidates)
            
            # 5. 构建推荐结果
            recommended_target = candidates[0].target_field if candidates else None
            recommended_confidence = candidates[0].confidence if candidates else 0.0
            
            recommendations.append(FieldMappingRecommendation(
                source_field=source_field,
                candidates=candidates,
                recommended_target=recommended_target,
                recommended_confidence=recommended_confidence
            ))
        
        return recommendations
    
    async def _get_history_mappings(
        self,
        source_field: str,
        source_system: str,
        document_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MappingCandidate]:
        """查询历史映射"""
        if not self.db_service:
            return []
        
        candidates = []
        
        try:
            # 构建查询SQL
            query_sql = """
                SELECT 
                    target_field_name,
                    usage_count,
                    match_confidence,
                    match_method
                FROM field_mapping_history
                WHERE source_field_name = :source_field
                  AND source_system = :source_system
                  AND is_confirmed = TRUE
                  AND is_rejected = FALSE
            """
            params = {
                'source_field': source_field,
                'source_system': source_system
            }
            
            if document_type:
                # 先查询匹配单据类型的
                query_sql_type = query_sql + " AND document_type = :document_type"
                params_type = {**params, 'document_type': document_type}
                query_sql_type += " ORDER BY usage_count DESC, last_used_at DESC LIMIT 5"
                
                results = await self.db_service.fetch_all(query_sql_type, params_type)
                
                if results:
                    for row in results:
                        confidence = min(0.95 + row['usage_count'] * 0.01, 1.0)
                        candidates.append(MappingCandidate(
                            target_field=row['target_field_name'],
                            confidence=confidence,
                            method=row.get('match_method', 'history'),
                            source=f'历史映射（{row["usage_count"]}次使用）'
                        ))
                    return candidates
            
            # 查询不限制单据类型的通用映射
            query_sql_general = query_sql + " AND document_type IS NULL"
            query_sql_general += " ORDER BY usage_count DESC, last_used_at DESC LIMIT 3"
            
            results = await self.db_service.fetch_all(query_sql_general, params)
            
            for row in results:
                confidence = min(0.85 + row['usage_count'] * 0.01, 0.95)
                candidates.append(MappingCandidate(
                    target_field=row['target_field_name'],
                    confidence=confidence,
                    method=row.get('match_method', 'history'),
                    source=f'历史映射（通用，{row["usage_count"]}次使用）'
                ))
                
        except Exception as e:
            logger.warning(f"查询历史映射失败: {e}")
        
        return candidates
    
    def _apply_mapping_rules(
        self,
        source_field: str,
        source_system: str,
        document_type: Optional[str]
    ) -> List[MappingCandidate]:
        """应用映射规则"""
        candidates = []
        
        # 内置规则（可以先从数据库加载，这里先用内置规则）
        rules = [
            {
                'source_pattern': r'采购.*单号|订单号|PO.*号',
                'match_type': 'regex',
                'target_field': '单据号',
                'source_system': None,
                'document_type': None,
            },
            {
                'source_pattern': r'日期|date',
                'match_type': 'contains',
                'target_field': '单据日期',
                'source_system': None,
                'document_type': None,
            },
            {
                'source_pattern': r'客户|供应商',
                'match_type': 'contains',
                'target_field': '客户名称',
                'source_system': None,
                'document_type': None,
            },
            {
                'source_pattern': r'产品|物料|商品',
                'match_type': 'contains',
                'target_field': '产品名称',
                'source_system': None,
                'document_type': None,
            },
            {
                'source_pattern': r'数量|qty',
                'match_type': 'contains',
                'target_field': '数量',
                'source_system': None,
                'document_type': None,
            },
            {
                'source_pattern': r'单价|price',
                'match_type': 'contains',
                'target_field': '单价',
                'source_system': None,
                'document_type': None,
            },
        ]
        
        for rule in rules:
            # 检查是否匹配数据源和单据类型
            if rule.get('source_system') and rule['source_system'] != source_system:
                continue
            if rule.get('document_type') and rule['document_type'] != document_type:
                continue
            
            # 检查字段名是否匹配规则
            if self._match_pattern(source_field, rule['source_pattern'], rule['match_type']):
                candidates.append(MappingCandidate(
                    target_field=rule['target_field'],
                    confidence=0.9,  # 规则匹配置信度较高
                    method='rule',
                    source=f'系统规则：{rule["source_pattern"]}'
                ))
        
        return candidates
    
    def _calculate_similarity_mappings(
        self,
        source_field: str,
        standard_fields: List[str]
    ) -> List[MappingCandidate]:
        """计算相似度匹配
        
        Args:
            source_field: 源字段名
            standard_fields: 标准字段列表（从数据库动态获取或降级列表）
        """
        candidates = []
        
        for target_field in standard_fields:
            # 计算字符串相似度
            similarity = self._calculate_string_similarity(source_field, target_field)
            
            if similarity > 0.6:  # 相似度阈值
                candidates.append(MappingCandidate(
                    target_field=target_field,
                    confidence=similarity,
                    method='similarity',
                    source=f'相似度匹配（{similarity:.2f}）'
                ))
        
        return candidates
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0
        
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # 方法1：SequenceMatcher（编辑距离）
        similarity_1 = SequenceMatcher(None, str1_lower, str2_lower).ratio()
        
        # 方法2：包含关系
        similarity_2 = 0.0
        if str1_lower in str2_lower or str2_lower in str1_lower:
            similarity_2 = 0.7
        
        # 方法3：字符交集比例
        set1 = set(str1_lower)
        set2 = set(str2_lower)
        if len(set1) > 0 and len(set2) > 0:
            similarity_3 = len(set1 & set2) / len(set1 | set2)
        else:
            similarity_3 = 0.0
        
        # 取最大值
        return max(similarity_1, similarity_2, similarity_3)
    
    def _match_pattern(self, field_name: str, pattern: str, match_type: str) -> bool:
        """匹配字段模式"""
        if not field_name or not pattern:
            return False
        
        field_lower = field_name.lower()
        pattern_lower = pattern.lower()
        
        if match_type == 'exact':
            return field_lower == pattern_lower
        elif match_type == 'prefix':
            return field_lower.startswith(pattern_lower)
        elif match_type == 'suffix':
            return field_lower.endswith(pattern_lower)
        elif match_type == 'contains':
            return pattern_lower in field_lower
        elif match_type == 'regex':
            try:
                return bool(re.search(pattern, field_name, re.IGNORECASE))
            except re.error:
                return False
        else:
            return False
    
    async def _get_standard_fields_from_db(
        self,
        target_table: str,
        document_type: Optional[str] = None,
        use_cache: bool = True
    ) -> List[str]:
        """从数据库动态获取标准字段列表（带缓存和并发优化）
        
        1. 查询目标表的所有字段
        2. 识别主数据ID字段并获取对应的匹配字段
        3. 返回目标表字段 + 主数据匹配字段的列表
        
        Args:
            target_table: 目标表名
            document_type: 单据类型（可选）
            use_cache: 是否使用缓存（默认True）
        
        Returns:
            标准字段列表
        
        Raises:
            ValueError: 如果数据库服务不可用或查询失败
        """
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法获取标准字段列表")
        
        cache_key = f"{self.cache_prefix}:standard_fields:{target_table}"
        
        # 1. 检查内存缓存
        if use_cache and target_table in self._memory_cache:
            cached = self._memory_cache[target_table].get('standard_fields')
            if cached:
                logger.debug(f"从内存缓存获取标准字段: {target_table}")
                return cached
        
        # 2. 检查Redis缓存
        if use_cache and self.cache_service:
            try:
                cached_data = await self.cache_service.get('standard_fields', target_table)
                if cached_data:
                    logger.debug(f"从Redis缓存获取标准字段: {target_table}")
                    # 同时更新内存缓存
                    if target_table not in self._memory_cache:
                        self._memory_cache[target_table] = {}
                    self._memory_cache[target_table]['standard_fields'] = cached_data
                    return cached_data
            except Exception as e:
                logger.warning(f"从Redis获取缓存失败: {e}")
        
        standard_fields = []
        
        try:
            # 并发查询：同时获取表字段和主数据匹配字段
            table_fields_task = self._get_target_table_fields(target_table, use_cache)
            master_data_fields_task = self._get_master_data_match_fields(
                target_table, document_type, use_cache
            )
            
            # 等待两个任务完成
            table_fields, master_data_fields = await asyncio.gather(
                table_fields_task,
                master_data_fields_task,
                return_exceptions=True
            )
            
            # 处理表字段结果
            if isinstance(table_fields, Exception):
                logger.error(f"获取目标表字段失败: {table_fields}")
                raise table_fields
            
            if not table_fields:
                raise ValueError(f"目标表 {target_table} 不存在或没有字段")
            standard_fields.extend(table_fields)
            
            # 处理主数据匹配字段结果
            if isinstance(master_data_fields, Exception):
                logger.warning(f"获取主数据匹配字段失败: {master_data_fields}")
                # 主数据匹配字段是可选的，不抛出异常
            else:
                standard_fields.extend(master_data_fields)
            
        except Exception as e:
            logger.error(f"从数据库获取标准字段失败: {e}")
            raise ValueError(f"无法从数据库获取标准字段列表: {str(e)}") from e
        
        if not standard_fields:
            raise ValueError(f"无法获取目标表 {target_table} 的标准字段列表")
        
        result = list(set(standard_fields))  # 去重
        
        # 更新缓存
        if use_cache:
            # 更新内存缓存
            if target_table not in self._memory_cache:
                self._memory_cache[target_table] = {}
            self._memory_cache[target_table]['standard_fields'] = result
            
            # 更新Redis缓存
            if self.cache_service:
                try:
                    await self.cache_service.set(
                        'standard_fields',
                        result,
                        target_table,
                        ttl=self.cache_ttl['table_fields']  # 使用表字段的TTL
                    )
                except Exception as e:
                    logger.warning(f"更新Redis缓存失败: {e}")
        
        return result
    
    async def _get_target_table_fields(
        self,
        target_table: str,
        use_cache: bool = True
    ) -> List[str]:
        """获取目标表的所有字段名（带缓存）
        
        Args:
            target_table: 目标表名
            use_cache: 是否使用缓存（默认True）
        
        Returns:
            字段名列表
        
        Raises:
            ValueError: 如果数据库服务不可用或查询失败
        """
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法查询目标表字段")
        
        cache_key = f"{self.cache_prefix}:table_fields:{target_table}"
        
        # 1. 检查内存缓存
        if use_cache and target_table in self._memory_cache:
            cached = self._memory_cache[target_table].get('fields')
            if cached:
                logger.debug(f"从内存缓存获取表字段: {target_table}")
                return cached
        
        # 2. 检查Redis缓存
        if use_cache and self.cache_service:
            try:
                cached_data = await self.cache_service.get('table_fields', target_table)
                if cached_data:
                    logger.debug(f"从Redis缓存获取表字段: {target_table}")
                    # 同时更新内存缓存
                    if target_table not in self._memory_cache:
                        self._memory_cache[target_table] = {}
                    self._memory_cache[target_table]['fields'] = cached_data
                    return cached_data
            except Exception as e:
                logger.warning(f"从Redis获取缓存失败: {e}")
        
        # 3. 从数据库查询
        try:
            # 查询PostgreSQL系统表获取列信息
            query_sql = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :table_name
                  AND table_schema = 'public'
                ORDER BY ordinal_position
            """
            results = await self.db_service.fetch_all(query_sql, {
                'table_name': target_table
            })
            
            if not results:
                raise ValueError(f"目标表 {target_table} 不存在或没有字段")
            
            field_names = [row['column_name'] for row in results]
            
            # 4. 更新缓存
            if use_cache:
                # 更新内存缓存
                if target_table not in self._memory_cache:
                    self._memory_cache[target_table] = {}
                self._memory_cache[target_table]['fields'] = field_names
                
                # 更新Redis缓存
                if self.cache_service:
                    try:
                        await self.cache_service.set(
                            'table_fields',
                            field_names,
                            target_table,
                            ttl=self.cache_ttl['table_fields']
                        )
                    except Exception as e:
                        logger.warning(f"更新Redis缓存失败: {e}")
            
            return field_names
        except Exception as e:
            logger.error(f"查询目标表字段失败: {e}")
            raise ValueError(f"无法查询目标表 {target_table} 的字段: {str(e)}") from e
    
    async def _get_master_data_match_fields(
        self,
        target_table: str,
        document_type: Optional[str] = None,
        use_cache: bool = True
    ) -> List[str]:
        """获取主数据匹配字段（带缓存）
        
        1. 识别目标表中的主数据ID字段（如 business_entity_id）
        2. 通过外键约束找到对应的主数据表（如 dim_business_entity）
        3. 从主数据表中获取用于匹配的字段（如 entity_name, credit_code）
        
        Args:
            target_table: 目标表名
            document_type: 单据类型（可选）
            use_cache: 是否使用缓存（默认True）
        
        Returns:
            主数据匹配字段列表
        
        Raises:
            ValueError: 如果数据库服务不可用或查询失败
        """
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法获取主数据匹配字段")
        
        cache_key = f"{self.cache_prefix}:master_data_fields:{target_table}"
        
        # 1. 检查内存缓存
        if use_cache and target_table in self._memory_cache:
            cached = self._memory_cache[target_table].get('master_data_fields')
            if cached is not None:
                logger.debug(f"从内存缓存获取主数据匹配字段: {target_table}")
                return cached
        
        # 2. 检查Redis缓存
        if use_cache and self.cache_service:
            try:
                cached_data = await self.cache_service.get('master_data_fields', target_table)
                if cached_data is not None:
                    logger.debug(f"从Redis缓存获取主数据匹配字段: {target_table}")
                    # 同时更新内存缓存
                    if target_table not in self._memory_cache:
                        self._memory_cache[target_table] = {}
                    self._memory_cache[target_table]['master_data_fields'] = cached_data
                    return cached_data
            except Exception as e:
                logger.warning(f"从Redis获取缓存失败: {e}")
        
        match_fields = []
        
        try:
            # 查询外键约束，找到主数据ID字段对应的主数据表（带缓存）
            fk_results = await self._get_foreign_keys(target_table, use_cache)
            
            if not fk_results:
                # 如果没有找到外键约束，尝试通过字段名推断主数据表
                all_fields = await self._get_target_table_fields(target_table)
                id_fields = [f for f in all_fields if f.endswith('_id')]
                
                # 主数据ID字段到主数据表的映射
                id_to_table_mapping = {
                    'business_entity_id': 'dim_business_entity',
                    'counterparty_id': 'dim_counterparty',
                    'product_id': 'dim_product',
                    'unit_id': 'dim_unit',
                    'tax_rate_id': 'dim_tax_rate',
                    'employee_id': 'dim_employee',
                    'exchange_rate_id': 'dim_exchange_rate',
                }
                
                for id_field in id_fields:
                    if id_field in id_to_table_mapping:
                        master_table = id_to_table_mapping[id_field]
                        # 获取主数据表的匹配字段
                        master_fields = await self._get_master_table_match_fields(master_table)
                        match_fields.extend(master_fields)
                
                return list(set(match_fields))
            
            # 主数据表到匹配字段的映射（可以从配置表或元数据表获取）
            master_data_match_config = {
                'dim_business_entity': ['entity_name', 'credit_code', 'unified_social_credit_code', 'business_entity_name'],
                'dim_counterparty': ['counterparty_name', 'credit_code', 'unified_social_credit_code', 'counterparty_code'],
                'dim_product': ['product_name', 'specification', 'model', 'product_code'],
                'dim_unit': ['unit_name', 'unit_code'],
                'dim_tax_rate': ['tax_rate', 'tax_rate_name', 'rate_value'],
                'dim_employee': ['employee_name', 'employee_code', 'id_number'],
                'dim_exchange_rate': ['currency', 'exchange_rate', 'rate_date'],
            }
            
            # 从主数据表获取匹配字段
            for fk in fk_results:
                master_table = fk['referenced_table']
                if master_table in master_data_match_config:
                    # 直接使用配置的字段名
                    match_fields.extend(master_data_match_config[master_table])
                else:
                    # 或者动态查询主数据表的字段
                    master_fields = await self._get_master_table_match_fields(master_table, use_cache)
                    match_fields.extend(master_fields)
            
            # 更新缓存
            if use_cache:
                # 更新内存缓存
                if target_table not in self._memory_cache:
                    self._memory_cache[target_table] = {}
                self._memory_cache[target_table]['master_data_fields'] = match_fields
                
                # 更新Redis缓存
                if self.cache_service:
                    try:
                        await self.cache_service.set(
                            'master_data_fields',
                            match_fields,
                            target_table,
                            ttl=self.cache_ttl['master_data_fields']
                        )
                    except Exception as e:
                        logger.warning(f"更新Redis缓存失败: {e}")
                    
        except Exception as e:
            logger.error(f"查询主数据匹配字段失败: {e}")
            # 如果查询失败，不影响主流程，只返回已获取的字段
            # 但不抛出异常，因为主数据匹配字段是可选的
        
        return list(set(match_fields))  # 去重
    
    async def _get_foreign_keys(
        self,
        target_table: str,
        use_cache: bool = True
    ) -> List[Dict[str, str]]:
        """获取目标表的外键约束（带缓存）
        
        Args:
            target_table: 目标表名
            use_cache: 是否使用缓存
        
        Returns:
            外键约束列表，每个元素包含 id_field 和 referenced_table
        """
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法查询外键约束")
        
        cache_key = f"{self.cache_prefix}:foreign_keys:{target_table}"
        
        # 1. 检查内存缓存
        if use_cache and target_table in self._memory_cache:
            cached = self._memory_cache[target_table].get('foreign_keys')
            if cached is not None:
                logger.debug(f"从内存缓存获取外键约束: {target_table}")
                return cached
        
        # 2. 检查Redis缓存
        if use_cache and self.cache_service:
            try:
                cached_data = await self.cache_service.get('foreign_keys', target_table)
                if cached_data is not None:
                    logger.debug(f"从Redis缓存获取外键约束: {target_table}")
                    # 同时更新内存缓存
                    if target_table not in self._memory_cache:
                        self._memory_cache[target_table] = {}
                    self._memory_cache[target_table]['foreign_keys'] = cached_data
                    return cached_data
            except Exception as e:
                logger.warning(f"从Redis获取缓存失败: {e}")
        
        # 3. 从数据库查询
        try:
            fk_query = """
                SELECT
                    kcu.column_name AS id_field,
                    ccu.table_name AS referenced_table
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                WHERE tc.table_name = :table_name
                  AND tc.table_schema = 'public'
                  AND tc.constraint_type = 'FOREIGN KEY'
                  AND kcu.column_name LIKE '%_id'
                  AND ccu.table_name LIKE 'dim_%'
                ORDER BY kcu.ordinal_position
            """
            
            results = await self.db_service.fetch_all(fk_query, {
                'table_name': target_table
            })
            
            fk_results = [
                {
                    'id_field': row['id_field'],
                    'referenced_table': row['referenced_table']
                }
                for row in results
            ] if results else []
            
            # 4. 更新缓存
            if use_cache:
                # 更新内存缓存
                if target_table not in self._memory_cache:
                    self._memory_cache[target_table] = {}
                self._memory_cache[target_table]['foreign_keys'] = fk_results
                
                # 更新Redis缓存
                if self.cache_service:
                    try:
                        await self.cache_service.set(
                            'foreign_keys',
                            fk_results,
                            target_table,
                            ttl=self.cache_ttl['foreign_keys']
                        )
                    except Exception as e:
                        logger.warning(f"更新Redis缓存失败: {e}")
            
            return fk_results
        except Exception as e:
            logger.error(f"查询外键约束失败: {e}")
            # 外键查询失败不影响主流程，返回空列表
            return []
    
    async def _get_master_table_match_fields(
        self,
        master_table: str,
        use_cache: bool = True
    ) -> List[str]:
        """获取主数据表的匹配字段（带缓存）
        
        从主数据表中获取用于匹配的字段（排除系统字段）
        
        Args:
            master_table: 主数据表名
            use_cache: 是否使用缓存
        
        Returns:
            匹配字段列表
        
        Raises:
            ValueError: 如果数据库服务不可用或查询失败
        """
        if not self.db_service:
            raise ValueError("数据库服务不可用，无法获取主数据表匹配字段")
        
        # 使用已缓存的表字段查询方法
        try:
            # 获取主数据表的所有字段（带缓存）
            all_fields = await self._get_target_table_fields(master_table, use_cache)
            
            if not all_fields:
                raise ValueError(f"主数据表 {master_table} 不存在或没有字段")
            
            # 过滤掉ID、时间戳等系统字段
            system_fields = {
                'id', '_id', 'created_at', 'updated_at', 'deleted_at',
                'is_deleted', 'tenant_id', 'created_by', 'updated_by'
            }
            
            filtered_fields = [
                f for f in all_fields
                if f not in system_fields
                and not f.endswith('_id')
                and not f.endswith('_at')
                and not f.startswith('is_')
                and not f.startswith('has_')
            ]
            
            if not filtered_fields:
                logger.warning(f"主数据表 {master_table} 没有可用的匹配字段")
                return []
            
            return filtered_fields[:10]  # 最多返回10个字段
            
        except Exception as e:
            logger.error(f"获取主数据表匹配字段失败: {e}")
            raise ValueError(f"无法获取主数据表 {master_table} 的匹配字段: {str(e)}") from e
    
    async def invalidate_table_cache(self, target_table: str):
        """使指定表的缓存失效
        
        Args:
            target_table: 目标表名
        """
        # 清除内存缓存
        if target_table in self._memory_cache:
            del self._memory_cache[target_table]
        
        # 清除Redis缓存
        if self.cache_service:
            try:
                await self.cache_service.delete('table_fields', target_table)
                await self.cache_service.delete('master_data_fields', target_table)
                await self.cache_service.delete('foreign_keys', target_table)
                await self.cache_service.delete('standard_fields', target_table)
                logger.info(f"已清除表 {target_table} 的缓存")
            except Exception as e:
                logger.warning(f"清除Redis缓存失败: {e}")
    
    async def preload_table_cache(self, tables: List[str]):
        """预加载多个表的缓存
        
        Args:
            tables: 表名列表
        """
        if not tables:
            return
        
        logger.info(f"开始预加载 {len(tables)} 个表的缓存")
        
        # 并发预加载所有表
        tasks = [
            self._get_standard_fields_from_db(table, use_cache=True)
            for table in tables
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"预加载完成: {success_count}/{len(tables)} 个表成功")
        except Exception as e:
            logger.warning(f"预加载缓存失败: {e}")
    
    def _deduplicate_and_sort_candidates(
        self,
        candidates: List[MappingCandidate]
    ) -> List[MappingCandidate]:
        """去重并排序候选"""
        if not candidates:
            return []
        
        # 按目标字段去重（保留置信度最高的）
        unique_candidates = {}
        for candidate in candidates:
            key = candidate.target_field
            if key not in unique_candidates or candidate.confidence > unique_candidates[key].confidence:
                unique_candidates[key] = candidate
        
        # 按置信度排序
        return sorted(
            unique_candidates.values(),
            key=lambda x: x.confidence,
            reverse=True
        )
    
    async def save_mapping_history(
        self,
        source_field: str,
        target_field: str,
        source_system: str,
        document_type: Optional[str],
        user_id: Optional[str],
        match_method: str,
        confidence: float,
        is_confirmed: bool = True
    ):
        """保存映射历史记录"""
        if not self.db_service:
            return
        
        try:
            # 检查是否已存在
            check_sql = """
                SELECT id, usage_count
                FROM field_mapping_history
                WHERE source_system = :source_system
                  AND document_type = :document_type
                  AND source_field_name = :source_field
                  AND target_field_name = :target_field
                  AND (user_id = :user_id OR (:user_id IS NULL AND user_id IS NULL))
            """
            params = {
                'source_system': source_system,
                'document_type': document_type,
                'source_field': source_field,
                'target_field': target_field,
                'user_id': user_id
            }
            
            existing = await self.db_service.fetch_one(check_sql, params)
            
            if existing:
                # 更新使用统计
                update_sql = """
                    UPDATE field_mapping_history
                    SET usage_count = usage_count + 1,
                        last_used_at = CURRENT_TIMESTAMP,
                        is_confirmed = :is_confirmed,
                        is_rejected = FALSE,
                        match_confidence = :confidence,
                        match_method = :match_method,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """
                await self.db_service.execute_query(update_sql, {
                    'id': existing['id'],
                    'is_confirmed': is_confirmed,
                    'confidence': confidence,
                    'match_method': match_method
                })
            else:
                # 创建新记录
                insert_sql = """
                    INSERT INTO field_mapping_history (
                        source_system, document_type, user_id,
                        source_field_name, target_field_name,
                        match_confidence, match_method,
                        usage_count, is_confirmed, is_rejected,
                        created_at, updated_at
                    ) VALUES (
                        :source_system, :document_type, :user_id,
                        :source_field, :target_field,
                        :confidence, :match_method,
                        1, :is_confirmed, FALSE,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                await self.db_service.execute_query(insert_sql, {
                    'source_system': source_system,
                    'document_type': document_type,
                    'user_id': user_id,
                    'source_field': source_field,
                    'target_field': target_field,
                    'confidence': confidence,
                    'match_method': match_method,
                    'is_confirmed': is_confirmed
                })
                
        except Exception as e:
            logger.error(f"保存映射历史记录失败: {e}")
            raise

