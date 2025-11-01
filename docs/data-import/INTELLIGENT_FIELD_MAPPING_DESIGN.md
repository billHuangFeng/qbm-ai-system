# 智能字段映射设计文档

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **设计完成，待实现**

---

## 📋 核心需求

在数据导入时，用户提供的源文件格式、字段名称会出现变化，但有一定稳定性。因此需要：

1. ✅ **智能映射**：自动推荐字段映射关系，降低用户操作难度
2. ✅ **历史记忆**：记录历史映射记录，作为下次智能映射的参考
3. ✅ **持续学习**：用户确认的映射会被记录下来，提高后续推荐的准确性
4. ✅ **上下文感知**：考虑数据源类型、单据类型等上下文信息

---

## 🎯 系统架构

### 数据流程

```
1. 用户上传文件
   ↓
2. 系统解析文件字段
   ↓
3. 查询历史映射记录（基于：数据源类型、单据类型、用户ID）
   ↓
4. 智能映射算法
   ├── 历史映射匹配（优先使用）
   ├── 相似度计算（字符串相似度、语义相似度）
   └── 上下文规则（数据源特定的映射规则）
   ↓
5. 生成映射推荐列表
   ├── 高置信度映射（自动应用）
   ├── 中置信度映射（推荐给用户确认）
   └── 低置信度映射（提示用户）
   ↓
6. 用户确认或调整映射
   ↓
7. 记录确认后的映射到历史记录
   ↓
8. 应用映射，继续处理
```

---

## 📊 数据库设计

### 1. 字段映射历史表

```sql
-- 字段映射历史记录表
CREATE TABLE field_mapping_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 上下文信息
    source_system VARCHAR(50) NOT NULL,        -- 数据源系统（如：erp_system_a, manual, ...）
    document_type VARCHAR(50),                  -- 单据类型（如：purchase_order, sales_order, ...）
    user_id UUID,                               -- 用户ID（可选，个人化映射）
    
    -- 源字段信息
    source_field_name VARCHAR(255) NOT NULL,    -- 源文件字段名
    source_field_type VARCHAR(50),              -- 源字段类型（string, number, date, ...）
    source_field_position INTEGER,              -- 字段位置（如果没有列名，使用位置）
    
    -- 目标字段信息
    target_field_name VARCHAR(255) NOT NULL,    -- 目标标准字段名
    target_field_category VARCHAR(50),          -- 字段类别（header, detail, amount, ...）
    
    -- 匹配信息
    match_confidence DECIMAL(5,2),             -- 匹配置信度（0-100）
    match_method VARCHAR(50),                   -- 匹配方法（history, similarity, rule, manual）
    
    -- 使用统计
    usage_count INTEGER DEFAULT 1,              -- 使用次数
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 最后使用时间
    first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 首次使用时间
    
    -- 用户反馈
    is_confirmed BOOLEAN DEFAULT TRUE,         -- 是否被用户确认
    is_rejected BOOLEAN DEFAULT FALSE,          -- 是否被用户拒绝
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    CONSTRAINT unique_mapping UNIQUE (source_system, document_type, source_field_name, target_field_name, user_id)
);

-- 索引优化
CREATE INDEX idx_field_mapping_context ON field_mapping_history(source_system, document_type, user_id);
CREATE INDEX idx_field_mapping_source ON field_mapping_history(source_field_name);
CREATE INDEX idx_field_mapping_target ON field_mapping_history(target_field_name);
CREATE INDEX idx_field_mapping_usage ON field_mapping_history(usage_count DESC, last_used_at DESC);
```

### 2. 字段映射规则表（可选）

```sql
-- 字段映射规则表（系统级规则，不需要用户确认）
CREATE TABLE field_mapping_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 规则条件
    source_system VARCHAR(50),                  -- 适用数据源（NULL表示所有）
    document_type VARCHAR(50),                  -- 适用单据类型（NULL表示所有）
    
    -- 匹配模式
    source_pattern VARCHAR(255) NOT NULL,      -- 源字段模式（支持正则表达式）
    match_type VARCHAR(50) DEFAULT 'exact',     -- 匹配类型：exact, prefix, suffix, regex, contains
    
    -- 目标字段
    target_field_name VARCHAR(255) NOT NULL,    -- 目标标准字段名
    
    -- 优先级
    priority INTEGER DEFAULT 100,               -- 优先级（数字越小优先级越高）
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,            -- 是否启用
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    CREATE INDEX idx_field_mapping_rules_pattern ON field_mapping_rules(source_pattern);
);
```

---

## 🧠 智能映射算法

### 1. 映射推荐算法

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import sqlalchemy as sa
from sqlalchemy.orm import Session

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

class IntelligentFieldMapper:
    """智能字段映射器"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def recommend_mappings(
        self,
        source_fields: List[str],
        source_system: str,
        document_type: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> List[FieldMappingRecommendation]:
        """推荐字段映射
        
        Args:
            source_fields: 源文件字段列表
            source_system: 数据源系统
            document_type: 单据类型
            user_id: 用户ID（可选，用于个人化推荐）
            context: 额外上下文信息
        
        Returns:
            映射推荐列表
        """
        recommendations = []
        
        for source_field in source_fields:
            candidates = []
            
            # 1. 查询历史映射（优先）
            history_candidates = self._get_history_mappings(
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
                    source_field, document_type
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
    
    def _get_history_mappings(
        self,
        source_field: str,
        source_system: str,
        document_type: Optional[str],
        user_id: Optional[str]
    ) -> List[MappingCandidate]:
        """查询历史映射"""
        # 构建查询（优先匹配用户、系统、单据类型）
        query = self.db.query(FieldMappingHistory).filter(
            FieldMappingHistory.source_field_name == source_field,
            FieldMappingHistory.source_system == source_system,
            FieldMappingHistory.is_confirmed == True,
            FieldMappingHistory.is_rejected == False
        )
        
        if document_type:
            # 先查询匹配单据类型的
            query_type = query.filter(
                FieldMappingHistory.document_type == document_type
            ).order_by(
                FieldMappingHistory.usage_count.desc(),
                FieldMappingHistory.last_used_at.desc()
            ).limit(5).all()
            
            if query_type:
                return [
                    MappingCandidate(
                        target_field=m.target_field_name,
                        confidence=min(0.95 + m.usage_count * 0.01, 1.0),  # 使用次数越多，置信度越高
                        method='history',
                        source=f'历史映射（{m.usage_count}次使用）'
                    )
                    for m in query_type
                ]
        
        # 查询不限制单据类型的通用映射
        query_general = query.filter(
            FieldMappingHistory.document_type.is_(None)
        ).order_by(
            FieldMappingHistory.usage_count.desc(),
            FieldMappingHistory.last_used_at.desc()
        ).limit(3).all()
        
        return [
            MappingCandidate(
                target_field=m.target_field_name,
                confidence=min(0.85 + m.usage_count * 0.01, 0.95),
                method='history',
                source=f'历史映射（通用，{m.usage_count}次使用）'
            )
            for m in query_general
        ]
    
    def _apply_mapping_rules(
        self,
        source_field: str,
        source_system: str,
        document_type: Optional[str]
    ) -> List[MappingCandidate]:
        """应用映射规则"""
        candidates = []
        
        # 查询匹配的规则
        rules = self.db.query(FieldMappingRule).filter(
            FieldMappingRule.is_active == True
        ).all()
        
        for rule in rules:
            # 检查是否匹配数据源和单据类型
            if rule.source_system and rule.source_system != source_system:
                continue
            if rule.document_type and rule.document_type != document_type:
                continue
            
            # 检查字段名是否匹配规则
            if self._match_pattern(source_field, rule.source_pattern, rule.match_type):
                candidates.append(MappingCandidate(
                    target_field=rule.target_field_name,
                    confidence=0.9,  # 规则匹配置信度较高
                    method='rule',
                    source=f'系统规则：{rule.source_pattern}'
                ))
        
        return candidates
    
    def _calculate_similarity_mappings(
        self,
        source_field: str,
        document_type: Optional[str]
    ) -> List[MappingCandidate]:
        """计算相似度匹配"""
        candidates = []
        
        # 获取标准字段列表（根据单据类型）
        standard_fields = self._get_standard_fields(document_type)
        
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
        # 方法1：SequenceMatcher（编辑距离）
        similarity_1 = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
        
        # 方法2：包含关系
        similarity_2 = 0.0
        if str1.lower() in str2.lower() or str2.lower() in str1.lower():
            similarity_2 = 0.7
        
        # 方法3：字符交集比例
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        if len(set1) > 0 and len(set2) > 0:
            similarity_3 = len(set1 & set2) / len(set1 | set2)
        else:
            similarity_3 = 0.0
        
        # 取最大值
        return max(similarity_1, similarity_2, similarity_3)
    
    def _match_pattern(self, field_name: str, pattern: str, match_type: str) -> bool:
        """匹配字段模式"""
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
            import re
            return bool(re.match(pattern, field_name, re.IGNORECASE))
        else:
            return False
    
    def _get_standard_fields(self, document_type: Optional[str]) -> List[str]:
        """获取标准字段列表"""
        # 标准字段列表（根据单据类型）
        base_fields = [
            # 单据头字段
            '单据号', 'document_id', 'document_number',
            '单据日期', 'document_date', 'date',
            '客户名称', 'customer_name', 'supplier_name',
            '经营主体名称', 'business_entity_name',
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax',
            '税额', 'tax_amount', 'tax',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax',
            # 明细字段
            '产品名称', 'product_name', 'item_name',
            '数量', 'quantity', 'qty',
            '单价', 'unit_price', 'price',
            '计量单位', 'unit', 'unit_name',
        ]
        
        # 可以根据单据类型扩展
        if document_type == 'purchase_order':
            base_fields.extend(['供应商名称', 'supplier_name'])
        elif document_type == 'sales_order':
            base_fields.extend(['客户名称', 'customer_name'])
        
        return base_fields
    
    def _deduplicate_and_sort_candidates(
        self,
        candidates: List[MappingCandidate]
    ) -> List[MappingCandidate]:
        """去重并排序候选"""
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
```

### 2. 映射记录和更新

```python
def save_mapping_history(
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
    # 检查是否已存在
    existing = self.db.query(FieldMappingHistory).filter(
        FieldMappingHistory.source_system == source_system,
        FieldMappingHistory.document_type == document_type,
        FieldMappingHistory.source_field_name == source_field,
        FieldMappingHistory.target_field_name == target_field,
        FieldMappingHistory.user_id == user_id
    ).first()
    
    if existing:
        # 更新使用统计
        existing.usage_count += 1
        existing.last_used_at = sa.func.now()
        existing.is_confirmed = is_confirmed
        existing.is_rejected = False
        existing.match_confidence = confidence
        existing.match_method = match_method
    else:
        # 创建新记录
        new_mapping = FieldMappingHistory(
            source_system=source_system,
            document_type=document_type,
            user_id=user_id,
            source_field_name=source_field,
            target_field_name=target_field,
            match_confidence=confidence,
            match_method=match_method,
            usage_count=1,
            is_confirmed=is_confirmed,
            is_rejected=False
        )
        self.db.add(new_mapping)
    
    self.db.commit()
```

---

## 🔌 API端点设计

### 1. 获取映射推荐

```http
POST /api/v1/data-import/recommend-mappings
Content-Type: application/json

{
  "source_fields": ["采购订单号", "订单日期", "供应商", "物料名称", "数量", "单价", "金额"],
  "source_system": "erp_system_a",
  "document_type": "purchase_order",
  "user_id": "uuid"  // 可选
}
```

**响应**:
```json
{
  "recommendations": [
    {
      "source_field": "采购订单号",
      "recommended_target": "单据号",
      "recommended_confidence": 0.98,
      "method": "history",
      "candidates": [
        {
          "target_field": "单据号",
          "confidence": 0.98,
          "method": "history",
          "source": "历史映射（15次使用）"
        },
        {
          "target_field": "document_id",
          "confidence": 0.75,
          "method": "similarity",
          "source": "相似度匹配（0.75）"
        }
      ]
    },
    {
      "source_field": "订单日期",
      "recommended_target": "单据日期",
      "recommended_confidence": 0.95,
      "method": "history",
      "candidates": [...]
    },
    {
      "source_field": "物料名称",
      "recommended_target": "产品名称",
      "recommended_confidence": 0.82,
      "method": "similarity",
      "candidates": [...]
    }
  ],
  "summary": {
    "total_fields": 7,
    "high_confidence_count": 5,  // 置信度 >= 0.9
    "medium_confidence_count": 2,  // 0.7 <= 置信度 < 0.9
    "low_confidence_count": 0  // 置信度 < 0.7
  }
}
```

### 2. 确认映射（记录历史）

```http
POST /api/v1/data-import/confirm-mappings
Content-Type: application/json

{
  "source_system": "erp_system_a",
  "document_type": "purchase_order",
  "user_id": "uuid",  // 可选
  "mappings": [
    {
      "source_field": "采购订单号",
      "target_field": "单据号",
      "confidence": 0.98,
      "method": "history",
      "is_confirmed": true
    },
    {
      "source_field": "订单日期",
      "target_field": "单据日期",
      "confidence": 0.95,
      "method": "history",
      "is_confirmed": true
    },
    {
      "source_field": "物料名称",
      "target_field": "产品名称",
      "confidence": 0.82,
      "method": "similarity",
      "is_confirmed": true
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "saved_count": 3,
  "updated_count": 2,
  "new_count": 1
}
```

### 3. 拒绝映射（记录拒绝历史）

```http
POST /api/v1/data-import/reject-mapping
Content-Type: application/json

{
  "source_system": "erp_system_a",
  "document_type": "purchase_order",
  "source_field": "物料名称",
  "target_field": "产品名称",
  "reason": "用户手动调整"
}
```

### 4. 查询历史映射

```http
GET /api/v1/data-import/mapping-history
Query Parameters:
  - source_system: erp_system_a
  - document_type: purchase_order (可选)
  - user_id: uuid (可选)
  - limit: 50
```

**响应**:
```json
{
  "mappings": [
    {
      "id": "uuid",
      "source_field": "采购订单号",
      "target_field": "单据号",
      "usage_count": 15,
      "last_used_at": "2025-01-20T10:30:00Z",
      "match_method": "history",
      "confidence": 0.98
    },
    ...
  ],
  "total": 25
}
```

---

## 📝 使用流程示例

### 完整导入流程（带智能映射）

```python
# 1. 用户上传文件
file_path = "purchase_order.xlsx"

# 2. 系统解析文件字段
source_fields = extract_fields(file_path)  # ["采购订单号", "订单日期", "供应商", ...]

# 3. 获取映射推荐
mapper = IntelligentFieldMapper(db_session)
recommendations = mapper.recommend_mappings(
    source_fields=source_fields,
    source_system="erp_system_a",
    document_type="purchase_order",
    user_id="user_123"
)

# 4. 前端展示推荐，用户确认或调整
# 用户确认后的映射：
confirmed_mappings = {
    "采购订单号": "单据号",  # 高置信度，自动应用
    "订单日期": "单据日期",   # 高置信度，自动应用
    "供应商": "客户名称",     # 用户手动调整
    "物料名称": "产品名称",   # 中置信度，用户确认
    "数量": "数量",          # 完全匹配，自动应用
    "单价": "单价",          # 完全匹配，自动应用
    "金额": "不含税金额"     # 用户手动调整
}

# 5. 保存映射历史
for source_field, target_field in confirmed_mappings.items():
    rec = next(r for r in recommendations if r.source_field == source_field)
    mapper.save_mapping_history(
        source_field=source_field,
        target_field=target_field,
        source_system="erp_system_a",
        document_type="purchase_order",
        user_id="user_123",
        match_method=rec.method,
        confidence=rec.recommended_confidence,
        is_confirmed=True
    )

# 6. 应用映射，继续处理
processed_data = apply_field_mappings(raw_data, confirmed_mappings)
```

---

## ✅ 特性总结

### 核心功能

1. ✅ **历史映射优先**：优先使用历史映射记录，置信度更高
2. ✅ **相似度计算**：字符串相似度匹配，支持多种算法
3. ✅ **规则匹配**：系统级映射规则，支持正则表达式
4. ✅ **上下文感知**：考虑数据源、单据类型、用户ID
5. ✅ **持续学习**：记录用户确认，提高后续准确性
6. ✅ **使用统计**：跟踪使用次数，优先推荐常用映射

### 优势

- 🎯 **降低操作难度**：自动推荐，减少90%的手动映射工作
- 🧠 **持续学习**：系统越用越准确
- 👤 **个人化**：支持用户级别的个人化映射
- 📊 **统计分析**：跟踪映射使用情况
- 🔧 **灵活配置**：支持系统级规则和用户级映射

---

## 📚 相关文档

- [复杂单据格式处理](./COMPLEX_DOCUMENT_FORMAT_HANDLING.md)
- [分工策略文档](./COMPLEX_IMPORT_DIVISION_STRATEGY.md)

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23

