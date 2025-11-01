# 复杂单据导入完整指南

**创建时间**: 2025-01-23  
**版本**: 2.0  
**状态**: ✅ **设计完成，待Lovable实施**

**文档说明**: 本文档整合了复杂单据导入的所有设计内容，包括智能字段映射、格式处理、主数据匹配、三阶段导入流程和分工策略。

---

## 📋 目录

1. [系统概述](#1-系统概述)
2. [智能字段映射](#2-智能字段映射)
3. [复杂单据格式处理](#3-复杂单据格式处理)
4. [主数据匹配和用户决策](#4-主数据匹配和用户决策)
5. [三阶段导入流程](#5-三阶段导入流程)
6. [技术分工策略](#6-技术分工策略)
7. [API接口设计](#7-api接口设计)
8. [数据库设计](#8-数据库设计)
9. [总结和实施建议](#9-总结和实施建议)

---

## 1. 系统概述

### 1.1 核心功能

复杂单据导入系统是一个智能化的数据导入解决方案，主要功能包括：

1. ✅ **智能字段映射**：自动推荐字段映射，记录历史映射，持续学习提高准确性
2. ✅ **格式识别**：自动识别6种复杂单据格式（常见格式优先）
3. ✅ **主数据匹配**：自动匹配7种主数据ID（经营主体、往来单位、产品、计量单位、税率、员工、汇率）
4. ✅ **用户决策机制**：在关键决策点支持用户选择（选择匹配、创建新、废弃）
5. ✅ **三阶段导入**：临时表隔离、问题修正、正式表导入

### 1.2 导入流程概览

```
用户上传文件
    ↓
【阶段1】字段映射（智能推荐 + 历史记忆）
    ↓
【阶段2】格式识别和处理（6种格式自动识别）
    ↓
【阶段3】主数据匹配（自动匹配 + 用户决策）
    ↓
【阶段4】导入临时表（staging_document_import）
    ↓
【阶段5】用户修正（批量/逐条处理问题）
    ↓
【阶段6】导入正式表（验证后导入）
```

---

## 2. 智能字段映射

### 2.1 核心需求

在数据导入时，用户提供的源文件格式、字段名称会出现变化，但有一定稳定性。因此需要：

1. ✅ **智能推荐**：自动推荐字段映射关系，降低用户操作难度
2. ✅ **历史记忆**：记录历史映射记录，作为下次智能映射的参考
3. ✅ **持续学习**：用户确认的映射会被记录下来，提高后续推荐的准确性
4. ✅ **上下文感知**：考虑数据源类型、单据类型、用户ID等上下文信息

### 2.2 映射优先级

1. **历史映射**（最高优先级）：同一数据源、同一单据类型的历史映射，置信度最高（0.85-1.0）
2. **系统规则**：系统级映射规则（如正则表达式匹配），置信度高（0.9）
3. **相似度匹配**：字符串相似度计算（SequenceMatcher、包含关系、字符交集），置信度中等（0.6-0.9）

### 2.3 映射推荐算法

```python
class IntelligentFieldMapper:
    """智能字段映射器"""
    
    def recommend_mappings(
        self,
        source_fields: List[str],
        source_system: str,
        document_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[FieldMappingRecommendation]:
        """推荐字段映射"""
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
            
            # 3. 计算相似度匹配
            if not candidates or max(c.confidence for c in candidates) < 0.8:
                similarity_candidates = self._calculate_similarity_mappings(
                    source_field, document_type
                )
                candidates.extend(similarity_candidates)
            
            # 4. 排序和去重
            candidates = self._deduplicate_and_sort_candidates(candidates)
            
            recommendations.append(FieldMappingRecommendation(
                source_field=source_field,
                candidates=candidates,
                recommended_target=candidates[0].target_field if candidates else None,
                recommended_confidence=candidates[0].confidence if candidates else 0.0
            ))
        
        return recommendations
```

### 2.4 数据库设计

```sql
-- 字段映射历史记录表
CREATE TABLE field_mapping_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 上下文信息
    source_system VARCHAR(50) NOT NULL,
    document_type VARCHAR(50),
    user_id UUID,
    
    -- 源字段信息
    source_field_name VARCHAR(255) NOT NULL,
    target_field_name VARCHAR(255) NOT NULL,
    
    -- 匹配信息
    match_confidence DECIMAL(5,2),
    match_method VARCHAR(50),  -- history, similarity, rule, manual
    
    -- 使用统计
    usage_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 用户反馈
    is_confirmed BOOLEAN DEFAULT TRUE,
    is_rejected BOOLEAN DEFAULT FALSE,
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_mapping UNIQUE (source_system, document_type, source_field_name, target_field_name, user_id)
);

-- 字段映射规则表（系统级规则）
CREATE TABLE field_mapping_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 规则条件
    source_system VARCHAR(50),
    document_type VARCHAR(50),
    
    -- 匹配模式
    source_pattern VARCHAR(255) NOT NULL,
    match_type VARCHAR(50) DEFAULT 'exact',  -- exact, prefix, suffix, regex, contains
    
    -- 目标字段
    target_field_name VARCHAR(255) NOT NULL,
    
    -- 优先级
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. 复杂单据格式处理

### 3.1 单据格式类型

根据实际业务场景，系统需要处理以下6种复杂的单据格式：

#### 格式1: 多行明细对应重复单据头 ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
DOC001 | 2024-01-01 | 客户A | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
DOC002 | 2024-01-02 | 客户B | 产品3 | 8  | 100.00 | 800.00  | 104.00 | 904.00
```
**特点**：每行都包含完整的单据头信息和明细信息。  
**场景**：最常见的单据格式，ERP系统导出标准格式。

#### 格式2: 多行明细但只有第一行有单据头 ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
       |           |        | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
       |           |        | 产品3 | 3  | 100.00 | 300.00  | 39.00  | 339.00
DOC002 | 2024-01-02 | 客户B | 产品4 | 8  | 100.00 | 800.00  | 104.00 | 904.00
```
**特点**：第一行包含单据头信息，后续明细行的单据头字段为空，需要通过前向填充补全。  
**场景**：Excel表格常见的紧凑格式，减少重复信息。

#### 格式3: 单据头和明细分离在不同表 ❌ **可忽略格式**

**说明**：该格式在实际业务场景中较少出现，可以忽略。如果确实需要支持，可以通过分两次导入（先导入单据头，再导入明细）来实现。

#### 格式4: 只有单据头记录 ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 不含税金额 | 税额 | 价税合计 | 备注
DOC001 | 2024-01-01 | 客户A | 1800.00 | 234.00 | 2034.00 | 汇总单据
```
**特点**：只有单据头信息，没有明细。允许用户选择导入，后续可补充明细记录。  
**场景**：汇总单据、服务类单据、或用户选择导入汇总数据后补充明细。

#### 格式5: 只有明细记录 ⚠️ **特殊场景格式**

```
单据号 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
DOC001 | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
DOC002 | 产品3 | 3  | 100.00 | 300.00  | 39.00  | 339.00
```
**特点**：只有明细信息，但包含单据号字段，用于关联系统中已存在的单据头记录。  
**场景**：主要用于**用户补充明细数据时**，当系统中已存在单据头记录（可能之前通过格式4导入），现在需要补充对应的明细行数据。

**关键处理逻辑**：
1. ✅ 系统通过明细记录中的**单据号**字段，在数据库中查找已存在的单据头记录ID
2. ✅ 如果找到匹配的单据头记录，将明细记录与单据头ID关联
3. ✅ 如果未找到匹配的单据头记录，需要用户决策：
   - **选择**：选择系统中某个相似的单据头（如果有）
   - **创建新**：创建新的单据头记录
   - **废弃**：跳过该明细记录，不导入

#### 格式6: 纯单据头记录（无明细） ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 不含税金额 | 税额 | 价税合计 | 单据类型 | 备注
DOC001 | 2024-01-01 | 客户A | 1800.00 | 234.00 | 2034.00 | 服务费 | 咨询服务
DOC002 | 2024-01-02 | 客户B | 500.00  | 65.00  | 565.00  | 服务费 | 技术支持
DOC003 | 2024-01-03 | 客户C | 1200.00 | 156.00 | 1356.00 | 服务费 | 培训服务
```
**特点**：纯单据头记录，无明细，直接使用。  
**场景**：服务费、咨询费、培训费等无明细的服务类单据。每条记录都是独立的单据，不需要明细信息。

### 3.2 格式识别算法

```python
class DocumentFormatDetector:
    """单据格式识别器"""
    
    def detect_format(self, data: pd.DataFrame, metadata: dict = None) -> str:
        """检测单据格式"""
        scores = {}
        
        for format_name, detector_func in self.format_patterns.items():
            score = detector_func(data, metadata)
            scores[format_name] = score
        
        # 返回得分最高的格式
        return max(scores, key=scores.get)
    
    def detect_repeated_header(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测重复单据头格式（格式1）"""
        # 检查是否有重复的单据号
        if '单据号' in data.columns:
            unique_docs = data['单据号'].nunique()
            total_rows = len(data)
            
            if unique_docs < total_rows * 0.8:
                return 0.9  # 高置信度
        return 0.0
    
    def detect_first_row_header(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测第一行单据头格式（格式2）"""
        if len(data) > 1:
            second_row = data.iloc[1]
            empty_count = second_row.isna().sum()
            total_cols = len(second_row)
            
            if empty_count > total_cols * 0.3:
                return 0.8  # 高置信度
        return 0.0
```

### 3.3 处理流程

```
1. 解析源文件
   ↓
2. 字段映射（将源字段映射到标准字段名）
   ↓
3. 格式识别（自动检测6种格式）
   ↓
4. 应用格式处理
   ├── 格式1：直接使用
   ├── 格式2：前向填充单据头字段
   ├── 格式4：创建虚拟明细记录
   ├── 格式5：匹配单据头ID
   └── 格式6：直接使用
   ↓
5. 数据验证和清洗
   ↓
6. 准备导入临时表
```

---

## 4. 主数据匹配和用户决策

### 4.1 主数据类型

系统支持以下7种主数据ID的自动匹配：

| 主数据类型 | 匹配字段 | 匹配表 | 匹配类型 |
|-----------|---------|--------|---------|
| 经营主体ID | 经营主体名称、统一社会信用代码 | dim_business_entity | 单字段匹配（优先代码） |
| 往来单位ID | 往来单位名称、统一社会信用代码 | dim_counterparty | 单字段匹配（优先代码） |
| 产品ID | 产品名称、规格型号 | dim_product | 组合匹配（名称+规格） |
| 计量单位ID | 计量单位名称 | dim_unit | 单字段匹配 |
| 税率ID | 税率值、税率名称 | dim_tax_rate | 单字段匹配 |
| 员工ID | 员工姓名、员工工号、身份证号 | dim_employee | 单字段匹配（优先工号） |
| 汇率ID | 币种、汇率日期、汇率值 | dim_exchange_rate | 组合匹配（币种+日期） |

### 4.2 匹配算法

```python
def match_master_data_ids(
    self,
    data: pd.DataFrame,
    master_data_config: Dict[str, Any],
    db_connection=None
) -> Dict[str, Any]:
    """匹配主数据ID"""
    
    for master_type, rule in master_data_rules.items():
        id_field = rule['id_field']
        match_fields = rule['match_fields']
        priority = rule.get('priority', [])
        match_type = rule.get('match_type', 'single')
        
        for idx, row in data.iterrows():
            match_results = []
            
            # 按优先级尝试匹配
            for priority_field in priority:
                # 执行匹配查询
                if match_type == 'combined':
                    match_result = self._match_combined_fields(row, match_fields, rule, db_connection)
                else:
                    match_result = self._match_single_field(source_value, match_field_config, db_connection)
                
                if match_result:
                    match_results.append({
                        **match_result,
                        'confidence': self._calculate_confidence(match_result, priority_field)
                    })
            
            # 处理匹配结果
            if len(match_results) == 0:
                # 未找到匹配，需要用户决策
                raise ValueError("需要用户决策：选择匹配、创建新记录、或废弃该记录")
            elif len(match_results) == 1:
                # 唯一匹配，检查置信度
                if match_result['confidence'] >= threshold:
                    data.at[idx, id_field] = match_result['id']
                else:
                    # 置信度低，需要用户确认
                    raise ValueError("需要用户确认匹配结果")
            else:
                # 多个匹配结果，需要用户选择
                raise ValueError("需要用户选择匹配项")
```

### 4.3 用户决策选项

**主数据匹配决策**：
1. **选择**：选择某个匹配项（从多个候选中选择）
2. **创建新**：创建新的主数据记录并自动匹配
3. **废弃**：跳过该记录，不导入

**单据头ID匹配决策**（格式5补充明细时）：
1. **选择**：选择系统中某个相似的单据头
2. **创建新**：创建新的单据头记录
3. **废弃**：跳过该明细记录，不导入

### 4.4 计算字段冲突纠正

**常见冲突**：
- 价税合计 ≠ 不含税金额 + 税额

**纠正策略**：
1. 优先信任：价税合计 = 不含税金额 + 税额（如果价税合计准确）
2. 用户选择：用户选择信任哪个字段
3. 自动修正：根据业务规则自动修正

---

## 5. 三阶段导入流程

### 5.1 为什么使用三阶段导入？

1. ✅ **数据安全**：临时表隔离错误数据，避免影响正式业务数据
2. ✅ **错误处理**：在临时表中批量修正问题，更灵活、更安全
3. ✅ **用户体验**：可以在临时表中预览和验证，提高数据质量
4. ✅ **业务流程**：适合需要审核、协作的业务场景
5. ✅ **系统性能**：减少正式表的写操作和锁竞争

### 5.2 阶段1：导入临时表

**目标**：
- 快速接收导入数据
- 保留原始数据
- 记录导入批次信息
- 标记问题数据

**流程**：
```
1. 数据去重和预处理
2. 导入临时表（staging_document_import）
3. 自动匹配主数据（高置信度自动匹配）
4. 标记问题数据：
   - 低置信度匹配
   - 匹配失败
   - 计算冲突（价税合计 ≠ 不含税金额 + 税额）
5. 状态标记：pending → matched/problem
```

**临时表结构**：
```sql
CREATE TABLE staging_document_import (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 导入批次信息
    batch_id UUID NOT NULL,
    import_user_id UUID,
    import_source VARCHAR(100),
    import_file_name VARCHAR(255),
    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 原始数据字段（保留所有原始字段）
    document_number VARCHAR(100),
    document_date DATE,
    customer_name VARCHAR(255),
    product_name VARCHAR(255),
    quantity DECIMAL(18,2),
    unit_price DECIMAL(18,2),
    amount_excluding_tax DECIMAL(18,2),
    tax_amount DECIMAL(18,2),
    total_amount_with_tax DECIMAL(18,2),
    
    -- 匹配后的字段
    business_entity_id UUID,
    counterparty_id UUID,
    product_id UUID,
    unit_id UUID,
    tax_rate_id UUID,
    employee_id UUID,
    exchange_rate_id UUID,
    document_header_id UUID,  -- 格式5补充明细时
    
    -- 问题标记和状态
    status VARCHAR(50) DEFAULT 'pending',  -- pending, matched, problem, confirmed, imported
    problem_type VARCHAR(50),  -- no_master_match, multiple_match, calculation_conflict
    problem_description TEXT,
    requires_user_action BOOLEAN DEFAULT FALSE,
    
    -- 用户决策信息
    user_action VARCHAR(50),  -- select, create_new, skip, fixed
    user_action_details JSONB,
    user_action_timestamp TIMESTAMP,
    handled_by_user_id UUID,
    
    -- 数据质量评分
    quality_score DECIMAL(5,2),
    validation_errors JSONB,
    
    -- 原始行数据（JSON格式）
    raw_data_json JSONB,
    row_number INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_staging_batch (batch_id),
    INDEX idx_staging_status (status),
    INDEX idx_staging_requires_action (requires_user_action)
);
```

### 5.3 阶段2：用户修正

**用户操作界面**：

1. **问题列表视图**
   - 显示所有需要处理的问题数据
   - 按问题类型分组（主数据匹配、计算冲突等）
   - 支持筛选和搜索

2. **批量处理功能**
   - 批量确认模糊匹配
   - 批量创建新的主数据记录
   - 批量废弃记录
   - 批量修正计算字段冲突

3. **逐条处理功能**
   - 显示原始数据和匹配结果
   - 用户选择、创建、废弃操作
   - 实时预览修正后的数据

**处理流程**：
```
1. 用户在临时表中处理问题：
   - 模糊匹配确认（选择、创建新、废弃）
   - 创建新的主数据记录并自动匹配
   - 废弃错误记录
   - 纠正计算字段冲突（价税合计 = 不含税金额 + 税额）
2. 批量或逐条处理
3. 状态更新：problem → confirmed
```

### 5.4 阶段3：导入正式表

**触发条件**：
- 所有问题已处理（status = 'confirmed'）
- 用户手动触发"确认导入"
- 定时批量导入（可选）

**导入逻辑**：
```sql
-- 1. 验证数据完整性
-- 2. 去重检查
-- 3. 导入正式表
INSERT INTO doc_purchase_order_header (...)
SELECT ... FROM staging_document_import
WHERE batch_id = ? AND status = 'confirmed';

INSERT INTO doc_purchase_order_detail (...)
SELECT ... FROM staging_document_import
WHERE batch_id = ? AND status = 'confirmed';

-- 4. 更新临时表状态
UPDATE staging_document_import
SET status = 'imported', imported_at = CURRENT_TIMESTAMP
WHERE batch_id = ? AND status = 'confirmed';
```

### 5.5 优化建议

1. **简化操作**：高置信度数据自动导入正式表，只将需要决策的数据导入临时表
2. **自动清理**：自动清理7天前的已导入数据，30天前的废弃数据
3. **性能优化**：使用批量操作、索引优化、异步处理

---

## 6. 技术分工策略

### 6.1 核心原则

复杂单据导入功能应采用 **"算法在后端，交互在前端"** 的混合模式：

- **Cursor (FastAPI)**: 实现核心算法和数据处理逻辑
- **Lovable (Edge Functions + Frontend)**: 实现用户交互界面和轻量级业务逻辑

### 6.2 Cursor 负责（FastAPI后端）

#### 核心算法实现

1. **格式识别算法**
   - 文档格式自动检测（6种格式识别）
   - 字段类型和结构分析
   - 模式匹配和特征提取

2. **字段映射算法**
   - 智能字段映射推荐
   - 字段相似度计算（Levenshtein距离、语义相似度）
   - 历史映射记录查询

3. **主数据匹配算法**
   - 主数据ID自动匹配（7种主数据类型）
   - 单字段和组合字段匹配
   - 模糊匹配和精确匹配
   - 置信度计算

4. **单据头ID匹配算法**
   - 通过单据号匹配系统中已存在的单据头记录ID
   - 匹配结果验证

5. **数据处理算法**
   - 前向填充（格式2）
   - 数据合并和关联
   - 虚拟记录生成

#### API端点

**核心处理端点**：
- `POST /api/v1/data-import/analyze` - 分析文件结构，推荐字段映射
- `POST /api/v1/data-import/process` - 处理复杂单据格式
- `POST /api/v1/data-import/validate` - 深度数据验证

**匹配和决策端点**：
- `POST /api/v1/data-import/match-master-data` - 主数据匹配（批量）
- `POST /api/v1/data-import/match-document-header` - 单据头ID匹配
- `POST /api/v1/data-import/match-status` - 获取匹配状态和待决策项

**用户决策端点**：
- `POST /api/v1/data-import/confirm-match` - 确认匹配决策
- `POST /api/v1/data-import/confirm-mappings` - 确认字段映射
- `POST /api/v1/data-import/reject-mapping` - 拒绝映射

**三阶段导入端点**：
- `POST /api/v1/data-import/stage1-import` - 阶段1：导入临时表
- `POST /api/v1/data-import/stage2-batch-fix` - 阶段2：批量修正
- `POST /api/v1/data-import/stage3-confirm-import` - 阶段3：确认导入正式表

### 6.3 Lovable 负责（Edge Functions + Frontend）

#### 用户交互界面

1. **字段映射界面**
   - 展示源字段和目标字段映射关系
   - 用户手动调整映射
   - 确认映射结果

2. **格式识别展示**
   - 显示检测到的格式类型
   - 格式置信度展示
   - 用户确认或手动选择格式

3. **匹配决策界面**
   - 主数据匹配结果展示（多个候选）
   - 单据头匹配结果展示
   - 用户选择操作：选择、创建新、废弃
   - 批量决策支持

4. **问题修正界面**
   - 临时表问题列表
   - 批量/逐条处理界面
   - 修正结果预览

#### 轻量级业务逻辑（Edge Functions）

- 简单验证
- 状态管理
- 数据写入（简单场景）

---

## 7. API接口设计

### 7.1 文件分析接口

```http
POST /api/v1/data-import/analyze
Content-Type: multipart/form-data

{
  "file": <file>,
  "source_type": "purchase_order|sales_order|...",
  "source_system": "erp_system_a",
  "document_type": "purchase_order"
}
```

**响应**:
```json
{
  "document_format": "excel",
  "detected_format_type": "repeated_header|first_row_header|...",
  "format_confidence": 0.95,
  "field_mappings": [
    {
      "source_field": "采购单号",
      "target_field": "单据号",
      "confidence": 0.98,
      "match_type": "history",
      "method": "历史映射（15次使用）"
    }
  ],
  "suggested_mappings": [...],
  "warnings": [...]
}
```

### 7.2 字段映射推荐接口

```http
POST /api/v1/data-import/recommend-mappings
Content-Type: application/json

{
  "source_fields": ["采购订单号", "订单日期", "供应商", ...],
  "source_system": "erp_system_a",
  "document_type": "purchase_order",
  "user_id": "uuid"
}
```

### 7.3 阶段1：导入临时表接口

```http
POST /api/v1/data-import/stage1-import
Content-Type: application/json

{
  "file_id": "uuid",
  "field_mappings": {...},
  "format_type": "repeated_header",
  "metadata": {...}
}
```

**响应**:
```json
{
  "batch_id": "uuid",
  "imported_count": 100,
  "problem_count": 15,
  "auto_matched_count": 85,
  "status": "completed",
  "problems": [
    {
      "row_index": 5,
      "problem_type": "no_master_match",
      "problem_description": "产品'XXX'未找到匹配记录",
      "requires_user_action": true
    }
  ]
}
```

### 7.4 阶段2：批量修正接口

```http
POST /api/v1/data-import/stage2-batch-fix
Content-Type: application/json

{
  "batch_id": "uuid",
  "actions": [
    {
      "row_id": "uuid",
      "action_type": "select|create_new|skip|fix_calculation",
      "action_details": {
        "selected_id": 123,
        "new_data": {...},
        "fixed_fields": {...}
      }
    }
  ]
}
```

### 7.5 阶段3：确认导入接口

```http
POST /api/v1/data-import/stage3-confirm-import
Content-Type: application/json

{
  "batch_id": "uuid",
  "validate_before_import": true
}
```

---

## 8. 数据库设计

### 8.1 核心表结构

**字段映射历史表**（见第2.4节）

**字段映射规则表**（见第2.4节）

**临时导入表**（见第5.2节）

### 8.2 索引优化

```sql
-- 字段映射历史表索引
CREATE INDEX idx_field_mapping_context ON field_mapping_history(source_system, document_type, user_id);
CREATE INDEX idx_field_mapping_source ON field_mapping_history(source_field_name);
CREATE INDEX idx_field_mapping_usage ON field_mapping_history(usage_count DESC, last_used_at DESC);

-- 临时导入表索引
CREATE INDEX idx_staging_batch ON staging_document_import(batch_id);
CREATE INDEX idx_staging_status ON staging_document_import(status);
CREATE INDEX idx_staging_requires_action ON staging_document_import(requires_user_action);
CREATE INDEX idx_staging_document_number ON staging_document_import(document_number);
```

---

## 9. 总结和实施建议

### 9.1 核心特性总结

✅ **智能字段映射**: 自动推荐字段映射，记录历史映射，持续学习提高准确性  
✅ **智能格式识别**: 自动检测6种复杂单据格式，优先支持常见格式（格式1/2/4/6）  
✅ **主数据自动匹配**: 支持7种主数据ID的自动匹配，支持精确和模糊匹配  
✅ **用户决策机制**: 在关键决策点支持用户选择（选择、创建新、废弃）  
✅ **三阶段导入**: 临时表隔离、问题修正、正式表导入，保证数据安全  
✅ **计算字段验证**: 验证价税合计 = 不含税金额 + 税额的一致性  
✅ **税务字段支持**: 完整支持不含税金额、税额、价税合计等税务字段  

### 9.2 实施优先级

**优先级1：核心功能（必须实现）**
1. ✅ 字段映射推荐和历史记录
2. ✅ 格式1、格式2、格式4、格式6处理器
3. ✅ 主数据匹配算法（7种主数据）
4. ✅ 临时表结构和导入逻辑
5. ✅ 用户修正界面（批量/逐条）

**优先级2：增强功能（推荐实现）**
6. ⏳ 格式5处理器（补充明细时）
7. ⏳ 计算字段冲突检测和纠正
8. ⏳ 自动清理机制
9. ⏳ 性能优化

**优先级3：可选功能**
10. ⏳ 格式3处理器（可忽略）
11. ⏳ 高级数据质量分析
12. ⏳ 协作处理功能

### 9.3 技术分工

**Cursor的交付物** ✅:
- [x] 算法设计和实现（字段映射、格式识别、主数据匹配）
- [x] API端点开发
- [x] 数据库设计
- [x] 完整设计文档（本文档）

**Lovable的实施任务** ⏳:
- [ ] 前端界面开发（字段映射、格式展示、匹配决策、问题修正）
- [ ] Edge Functions轻量级逻辑
- [ ] 用户交互流程实现
- [ ] UI/UX优化

### 9.4 预计实施时间

- **核心功能**: 2-3周
- **增强功能**: 1-2周
- **优化和测试**: 1周

**总计**: 4-6周

---

## 📚 附录

### A. 标准字段名清单

**单据头字段**：
- 单据号 (document_id)
- 单据日期 (document_date)
- 客户名称 (customer_name)
- 不含税金额 (ex_tax_amount)
- 税额 (tax_amount)
- 价税合计 (total_amount_with_tax)

**明细字段**：
- 产品名称 (product_name)
- 数量 (quantity)
- 单价 (unit_price)
- 不含税金额 (ex_tax_amount)
- 税额 (tax_amount)
- 价税合计 (total_amount_with_tax)
- 税率 (tax_rate)

### B. 问题类型枚举

- `no_master_match`: 主数据未找到匹配
- `multiple_master_match`: 主数据多个匹配候选
- `low_confidence_match`: 主数据匹配置信度低
- `no_document_header_match`: 单据头未找到匹配（格式5）
- `calculation_conflict`: 计算字段冲突
- `missing_required_field`: 必填字段缺失
- `invalid_data_type`: 数据类型错误
- `out_of_range`: 数据超出范围

### C. 状态枚举

**临时表状态**：
- `pending`: 待处理
- `matched`: 已匹配（高置信度自动匹配）
- `problem`: 有问题，需要用户处理
- `confirmed`: 已确认，准备导入正式表
- `imported`: 已导入正式表
- `rejected`: 已废弃

---

**文档版本**: 2.0  
**最后更新**: 2025-01-23  
**维护者**: Cursor (算法设计与技术架构)

