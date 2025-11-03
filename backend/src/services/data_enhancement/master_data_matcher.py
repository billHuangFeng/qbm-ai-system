"""
数据增强服务 - 主数据匹配
根据辅助信息（名称、统一社会信用代码等）匹配主数据ID

功能：
- 模糊字符串匹配（fuzzywuzzy + Levenshtein距离）
- 中文拼音匹配（pypinyin）
- 企业名称标准化（去除括号、"有限公司"等）
- 统一社会信用代码校验和匹配
- 多维度加权评分（名称相似度60% + 信用代码40%）
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import re

# 依赖库导入
try:
    from fuzzywuzzy import fuzz, process
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    raise ImportError("请安装依赖: pip install fuzzywuzzy python-Levenshtein")

try:
    from pypinyin import lazy_pinyin
except ImportError:
    raise ImportError("请安装依赖: pip install pypinyin")

from ...security.database import SecureDatabaseService
from ...error_handling.unified import BMOSError, BusinessError
from ...services.base import BaseService, ServiceConfig

logger = logging.getLogger(__name__)


class MasterDataMatchError(BMOSError):
    """主数据匹配错误"""
    pass


class MasterDataMatcher(BaseService):
    """主数据匹配服务"""
    
    def __init__(
        self,
        db_service: SecureDatabaseService,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, config=config)
        self.confidence_threshold = 0.8
        
        # 匹配规则说明：
        # 1. 代码完全一致 + 名称大致类似（>0.7）= 100%置信度
        # 2. 代码完全一致但名称不匹配 = 高置信度（75-100%），代码是唯一标识
        # 3. 代码细微差异（1-2字符）+ 名称大致类似 = 置信度大打折扣（30-60%）
        # 4. 代码较大差异（3+字符）= 低置信度（0-30%），即使名称匹配
        # 5. 无代码时，仅依赖名称匹配
        
        # 企业名称标准化规则
        self.company_suffixes = [
            "有限公司", "股份有限公司", "有限责任公司",
            "集团", "集团有限公司", "股份公司",
            "企业", "实业", "贸易", "科技", "信息技术"
        ]
        self.standardization_patterns = [
            (r'\([^)]*\)', ''),  # 去除括号内容
            (r'（[^）]*）', ''),   # 去除中文括号内容
            (r'[A-Za-z]+', ''),  # 去除英文
        ]
    
    def standardize_company_name(self, name: str) -> str:
        """
        企业名称标准化
        
        Args:
            name: 原始企业名称
            
        Returns:
            标准化后的企业名称
        """
        if not name or pd.isna(name):
            return ""
        
        name = str(name).strip()
        
        # 去除括号内容
        for pattern, replacement in self.standardization_patterns:
            name = re.sub(pattern, replacement, name)
        
        # 去除后缀
        for suffix in self.company_suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # 去除多余空格
        name = re.sub(r'\s+', '', name)
        
        return name
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        计算企业名称相似度
        
        Args:
            name1: 名称1
            name2: 名称2
            
        Returns:
            相似度分数 (0-1)
        """
        if not name1 or not name2:
            return 0.0
        
        # 标准化名称
        std_name1 = self.standardize_company_name(name1)
        std_name2 = self.standardize_company_name(name2)
        
        # 完全匹配
        if std_name1 == std_name2:
            return 1.0
        
        # 使用fuzzywuzzy计算相似度
        ratio = fuzz.ratio(std_name1, std_name2) / 100.0
        
        # 使用部分匹配（考虑子串匹配）
        partial_ratio = fuzz.partial_ratio(std_name1, std_name2) / 100.0
        
        # 使用token排序匹配（考虑词序）
        token_sort_ratio = fuzz.token_sort_ratio(std_name1, std_name2) / 100.0
        
        # 拼音匹配（中文名称）
        pinyin_similarity = self._calculate_pinyin_similarity(std_name1, std_name2)
        
        # 综合评分
        final_score = max(ratio, partial_ratio, token_sort_ratio, pinyin_similarity)
        
        return final_score
    
    def _calculate_pinyin_similarity(self, name1: str, name2: str) -> float:
        """计算拼音相似度"""
        try:
            pinyin1 = ''.join(lazy_pinyin(name1))
            pinyin2 = ''.join(lazy_pinyin(name2))
            
            if not pinyin1 or not pinyin2:
                return 0.0
            
            return fuzz.ratio(pinyin1, pinyin2) / 100.0
        except Exception as e:
            logger.warning(f"拼音匹配失败: {e}")
            return 0.0
    
    def validate_credit_code(self, code: str) -> bool:
        """
        验证统一社会信用代码格式
        
        Args:
            code: 统一社会信用代码
            
        Returns:
            是否为有效格式
        """
        if not code or pd.isna(code):
            return False
        
        code = str(code).strip()
        
        # 统一社会信用代码为18位
        if len(code) != 18:
            return False
        
        # 格式检查：字母+数字
        if not re.match(r'^[0-9A-HJ-NPQRTUWXY]{18}$', code):
            return False
        
        return True
    
    def calculate_code_similarity(self, code1: str, code2: str) -> float:
        """
        计算代码相似度（支持统一社会信用代码、身份证号码、产品代码等）
        
        逻辑：
        - 完全匹配 = 1.0（最高置信度）
        - 细微差异（1-2个字符差异）= 0.3-0.5（可能是输入错误，但风险较高）
        - 较大差异（3+个字符差异）= 0.0-0.2（很可能不匹配）
        
        Args:
            code1: 代码1
            code2: 代码2
            
        Returns:
            相似度分数 (0-1)
        """
        if not code1 or not code2 or pd.isna(code1) or pd.isna(code2):
            return 0.0
        
        code1 = str(code1).strip().upper()
        code2 = str(code2).strip().upper()
        
        # 完全匹配 = 1.0（最高置信度）
        if code1 == code2:
            return 1.0
        
        # 计算编辑距离（Levenshtein距离）
        edit_distance = levenshtein_distance(code1, code2)
        max_length = max(len(code1), len(code2))
        
        if max_length == 0:
            return 0.0
        
        # 基于编辑距离计算相似度
        # 相似度 = 1 - (编辑距离 / 最大长度)
        base_similarity = 1.0 - (edit_distance / max_length)
        
        # 根据差异程度调整置信度
        # 细微差异（1-2个字符）：置信度0.3-0.5（可能是输入错误，风险较高）
        if edit_distance <= 2:
            # 细微差异时，置信度大幅降低
            # 1个字符差异：0.5
            # 2个字符差异：0.3
            similarity = max(0.3, 0.5 - (edit_distance - 1) * 0.2)
        # 较大差异（3-4个字符）：置信度0.1-0.2（很可能不匹配）
        elif edit_distance <= 4:
            similarity = max(0.1, 0.2 - (edit_distance - 3) * 0.05)
        # 很大差异（5+个字符）：置信度0.0（几乎肯定不匹配）
        else:
            similarity = 0.0
        
        # 考虑长度差异的影响
        length_diff = abs(len(code1) - len(code2))
        if length_diff > 0:
            # 长度不同进一步降低置信度
            similarity *= (1.0 - length_diff * 0.1)
        
        return max(0.0, min(1.0, similarity))
    
    async def fetch_master_data(
        self,
        data_type: str,
        master_data_table: str,
        tenant_id: str
    ) -> pd.DataFrame:
        """
        从数据库获取主数据
        
        Args:
            data_type: 数据类型（order/production/expense）
            master_data_table: 主数据表名
            tenant_id: 租户ID
            
        Returns:
            主数据DataFrame
        """
        try:
            # 构建查询语句
            query = f"""
                SELECT 
                    id,
                    name,
                    credit_code,
                    alias_name,
                    tenant_id
                FROM {master_data_table}
                WHERE tenant_id = $1
            """
            
            results = await self.db_service.execute_query(
                query,
                params=[tenant_id],
                fetch_all=True
            )
            
            if not results:
                logger.warning(f"未找到主数据: {master_data_table}")
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            return df
            
        except Exception as e:
            logger.error(f"获取主数据失败: {e}")
            raise MasterDataMatchError(f"获取主数据失败: {e}")
    
    def match_single_record(
        self,
        record: Dict[str, Any],
        master_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        匹配单条记录
        
        Args:
            record: 待匹配记录
            master_data: 主数据DataFrame
            
        Returns:
            匹配结果
        """
        record_name = record.get("name", "")
        record_code = record.get("credit_code", "")
        row_index = record.get("row_index", 0)
        
        if master_data.empty:
            return {
                "row_index": row_index,
                "suggested_master_id": None,
                "confidence": 0.0,
                "match_reason": "无主数据可匹配",
                "alternatives": []
            }
        
        best_match = None
        best_score = 0.0
        alternatives = []
        
        # 遍历所有主数据记录
        for _, master_row in master_data.iterrows():
            master_id = master_row.get("id")
            master_name = master_row.get("name", "")
            master_code = master_row.get("credit_code", "")
            master_alias = master_row.get("alias_name", "")
            
            # 计算名称相似度
            name_sim = self.calculate_name_similarity(record_name, master_name)
            if master_alias:
                alias_sim = self.calculate_name_similarity(record_name, master_alias)
                name_sim = max(name_sim, alias_sim)
            
            # 计算代码相似度
            code_sim = 0.0
            code_fully_matched = False
            if record_code and master_code:
                code_sim = self.calculate_code_similarity(record_code, master_code)
                code_fully_matched = (code_sim >= 1.0)
            
            # 综合评分（改进逻辑）
            # 规则1：代码完全一致 + 名称大致类似（>0.7）= 100%置信度
            if code_fully_matched and name_sim >= 0.7:
                final_score = 1.0
            # 规则2：代码完全一致但名称不匹配 = 高置信度（可能是输入错误，但代码是唯一标识）
            elif code_fully_matched and name_sim >= 0.5:
                # 代码完全一致时，即使名称不完全匹配，也给予高置信度
                # 但名称匹配度仍然会影响最终分数
                final_score = 0.85 + name_sim * 0.15  # 85-100%之间
            # 规则3：代码有细微差异（0.3-1.0）+ 名称大致类似 = 置信度大打折扣
            elif code_sim >= 0.3 and name_sim >= 0.7:
                # 代码有细微差异时，即使名称匹配，也大幅降低置信度
                # 可能是输入错误，但也可能是不匹配
                final_score = code_sim * 0.6 + name_sim * 0.4
                # 进一步降低：代码细微差异的风险惩罚
                if code_sim < 1.0:
                    final_score *= 0.7  # 代码有差异时，再打7折
            # 规则4：代码有较大差异（<0.3）+ 名称匹配 = 低置信度
            elif code_sim < 0.3 and name_sim >= 0.7:
                # 代码差异较大时，即使名称匹配，也认为可能不匹配
                final_score = name_sim * 0.6  # 仅基于名称，且降低权重
            # 规则5：有代码但差异大 + 名称也不匹配 = 低置信度
            elif code_sim > 0 and code_sim < 0.3 and name_sim < 0.7:
                final_score = code_sim * 0.3 + name_sim * 0.7
            # 规则6：有代码且完全匹配，但名称完全不匹配（<0.5）= 中等置信度（代码优先）
            elif code_fully_matched and name_sim < 0.5:
                final_score = 0.75  # 代码完全匹配时，即使名称不匹配，仍给予中等置信度
            # 规则7：无代码，仅依赖名称匹配
            elif code_sim == 0:
                final_score = name_sim
            # 规则8：其他情况
            else:
                # 有代码但匹配度低，名称匹配度也低
                final_score = code_sim * 0.4 + name_sim * 0.6
            
            # 确保最终分数在0-1范围内
            final_score = max(0.0, min(1.0, final_score))
            
            # 记录候选匹配
            if final_score >= 0.6:
                alternatives.append({
                    "master_id": master_id,
                    "master_name": master_name,
                    "confidence": final_score,
                    "name_similarity": name_sim,
                    "code_similarity": code_sim
                })
            
            # 更新最佳匹配
            if final_score > best_score:
                best_score = final_score
                best_match = {
                    "master_id": master_id,
                    "master_name": master_name,
                    "confidence": final_score,
                    "name_similarity": name_sim,
                    "code_similarity": code_sim
                }
        
        # 排序候选匹配（按置信度降序）
        alternatives.sort(key=lambda x: x["confidence"], reverse=True)
        alternatives = alternatives[:5]  # 只保留前5个候选
        
        # 生成匹配原因
        match_reason = self._generate_match_reason(best_match, record_name, record_code)
        
        return {
            "row_index": row_index,
            "suggested_master_id": best_match["master_id"] if best_match and best_score >= self.confidence_threshold else None,
            "confidence": best_score,
            "match_reason": match_reason,
            "alternatives": alternatives
        }
    
    def _generate_match_reason(
        self,
        match: Optional[Dict[str, Any]],
        record_name: str,
        record_code: str
    ) -> str:
        """生成匹配原因描述"""
        if not match:
            return "未找到匹配的主数据"
        
        name_sim = match.get("name_similarity", 0.0)
        code_sim = match.get("code_similarity", 0.0)
        confidence = match.get("confidence", 0.0)
        code_fully_matched = (code_sim >= 1.0)
        
        reasons = []
        
        # 代码匹配情况
        if code_fully_matched:
            reasons.append("代码完全匹配（100%）")
        elif code_sim >= 0.3:
            # 计算编辑距离用于描述
            edit_distance = int((1.0 - code_sim) * max(len(record_code), 10))
            reasons.append(f"代码存在细微差异（约{edit_distance}个字符，相似度{code_sim*100:.0f}%）")
        elif code_sim > 0:
            reasons.append(f"代码存在较大差异（相似度{code_sim*100:.0f}%）")
        
        # 名称匹配情况
        if name_sim >= 0.9:
            reasons.append(f"名称相似度{name_sim*100:.0f}%（高度匹配）")
        elif name_sim >= 0.7:
            reasons.append(f"名称相似度{name_sim*100:.0f}%（大致相似）")
        elif name_sim >= 0.5:
            reasons.append(f"名称相似度{name_sim*100:.0f}%（部分相似）")
        elif name_sim > 0:
            reasons.append(f"名称相似度{name_sim*100:.0f}%（低相似度）")
        
        # 特殊情况说明
        if code_fully_matched and name_sim >= 0.7:
            reasons.append("【完全匹配】代码完全一致且名称相似")
        elif code_fully_matched and name_sim < 0.5:
            reasons.append("【注意】代码完全一致但名称差异较大，可能是输入错误")
        elif code_sim >= 0.3 and code_sim < 1.0 and name_sim >= 0.7:
            reasons.append("【警告】代码存在细微差异，可能是输入错误，也可能是不匹配")
        
        if not reasons:
            reasons.append(f"综合相似度{confidence*100:.0f}%")
        
        return " | ".join(reasons) if reasons else "低相似度匹配"
    
    async def match_master_data(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
        master_data_table: str,
        tenant_id: str,
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        匹配主数据
        
        Args:
            data_type: 数据类型（order/production/expense）
            records: 待匹配记录列表
            master_data_table: 主数据表名
            tenant_id: 租户ID
            confidence_threshold: 置信度阈值（默认0.8）
            
        Returns:
            匹配结果
        """
        self.confidence_threshold = confidence_threshold
        
        try:
            # 获取主数据
            master_data = await self.fetch_master_data(
                data_type,
                master_data_table,
                tenant_id
            )
            
            # 匹配每条记录
            matched_records = []
            unmatched_records = []
            
            for record in records:
                match_result = self.match_single_record(record, master_data)
                
                if match_result["suggested_master_id"]:
                    matched_records.append(match_result)
                else:
                    unmatched_records.append(match_result)
            
            # 统计信息
            total_records = len(records)
            matched_count = len(matched_records)
            unmatched_count = len(unmatched_records)
            match_rate = matched_count / total_records if total_records > 0 else 0.0
            
            # 平均置信度
            avg_confidence = (
                np.mean([r["confidence"] for r in matched_records])
                if matched_records else 0.0
            )
            
            statistics = {
                "total_records": total_records,
                "matched_count": matched_count,
                "unmatched_count": unmatched_count,
                "match_rate": match_rate,
                "average_confidence": avg_confidence,
                "confidence_threshold": confidence_threshold
            }
            
            return {
                "matched_records": matched_records,
                "unmatched_records": unmatched_records,
                "statistics": statistics
            }
            
        except Exception as e:
            logger.error(f"主数据匹配失败: {e}")
            raise MasterDataMatchError(f"主数据匹配失败: {e}")

