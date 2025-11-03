# 单据导入算法详细技术方案

## 1. 系统架构概述

### 1.1 整体架构
```
用户上传文件 (Lovable前端)
    ↓
文件解析 (FastAPI)
    ↓
格式识别 (Algorithm 1)
    ↓
智能字段映射 (Algorithm 2)
    ↓
主数据匹配 (Algorithm 3)
    ↓
单据头ID匹配 (Algorithm 4)
    ↓
数据处理与验证 (Algorithm 5)
    ↓
暂存表写入
    ↓
用户确认
    ↓
正式表写入
```

### 1.2 技术栈
- **语言**: Python 3.11+
- **框架**: FastAPI
- **数据处理**: pandas 2.0+, numpy 1.24+
- **字符串匹配**: python-Levenshtein 0.21+, rapidfuzz 3.0+
- **数据库**: asyncpg (PostgreSQL异步驱动)
- **验证**: pydantic 2.0+
- **并发**: asyncio

---

## 2. 核心算法设计

### Algorithm 1: 单据格式识别算法

#### 2.1.1 目标
自动识别Excel/CSV文件中的6种单据格式

#### 2.1.2 支持的格式类型
```python
class DocumentFormat(str, Enum):
    FORMAT_1_REPEATING_HEADER = "格式1:每行重复单据头"
    FORMAT_2_FORWARD_FILL = "格式2:单据头前向填充"
    FORMAT_3_HEADER_ONLY = "格式3:仅单据头"
    FORMAT_4_LINE_ONLY = "格式4:仅单据体(需匹配)"
    FORMAT_5_MIXED = "格式5:混合格式"
    FORMAT_6_GROUPED = "格式6:分组格式"
```

#### 2.1.3 识别算法流程
```python
class DocumentFormatRecognizer:
    def __init__(self):
        # 单据头字段特征词库
        self.header_keywords = [
            'order_no', 'order_date', 'customer', 'tenant',
            'total_amount', 'status', '单据号', '日期', '客户'
        ]
        
        # 单据体字段特征词库
        self.line_keywords = [
            'line_no', 'product', 'sku', 'quantity', 'price',
            'amount', '行号', '产品', '数量', '单价', '金额'
        ]
    
    async def recognize_format(self, df: pd.DataFrame) -> DocumentFormatResult:
        """识别单据格式"""
        
        # Step 1: 分析列结构
        columns = df.columns.tolist()
        header_cols = self._identify_header_columns(columns)
        line_cols = self._identify_line_columns(columns)
        
        # Step 2: 分析数据模式
        patterns = await self._analyze_data_patterns(df, header_cols, line_cols)
        
        # Step 3: 确定格式类型
        format_type = self._determine_format_type(patterns)
        
        # Step 4: 生成识别结果
        return DocumentFormatResult(
            format_type=format_type,
            confidence=patterns['confidence'],
            header_columns=header_cols,
            line_columns=line_cols,
            statistics=patterns['stats'],
            suggestions=self._generate_suggestions(format_type, patterns)
        )
    
    def _analyze_data_patterns(self, df: pd.DataFrame, 
                               header_cols: List[str], 
                               line_cols: List[str]) -> Dict:
        """分析数据模式"""
        patterns = {
            'has_header_cols': len(header_cols) > 0,
            'has_line_cols': len(line_cols) > 0,
            'header_repetition_rate': 0.0,
            'header_null_rate': 0.0,
            'has_grouping': False,
            'confidence': 0.0,
            'stats': {}
        }
        
        if len(header_cols) > 0:
            # 计算单据头字段重复率
            repetition_counts = []
            for col in header_cols:
                if col in df.columns:
                    unique_count = df[col].nunique()
                    total_count = len(df)
                    repetition_counts.append(unique_count / total_count)
            
            patterns['header_repetition_rate'] = np.mean(repetition_counts) if repetition_counts else 0
            
            # 计算空值率
            null_rates = []
            for col in header_cols:
                if col in df.columns:
                    null_rate = df[col].isnull().sum() / len(df)
                    null_rates.append(null_rate)
            
            patterns['header_null_rate'] = np.mean(null_rates) if null_rates else 0
            
            # 检测是否有分组(连续相同值)
            for col in header_cols:
                if col in df.columns:
                    groups = df[col].ne(df[col].shift()).cumsum()
                    if groups.nunique() < len(df) * 0.8:  # 80%阈值
                        patterns['has_grouping'] = True
                        break
        
        patterns['stats'] = {
            'total_rows': len(df),
            'header_cols_count': len(header_cols),
            'line_cols_count': len(line_cols)
        }
        
        return patterns
    
    def _determine_format_type(self, patterns: Dict) -> DocumentFormat:
        """确定格式类型"""
        has_header = patterns['has_header_cols']
        has_line = patterns['has_line_cols']
        repetition_rate = patterns['header_repetition_rate']
        null_rate = patterns['header_null_rate']
        has_grouping = patterns['has_grouping']
        
        # 决策树
        if has_header and has_line:
            if repetition_rate > 0.8:  # 高重复率
                patterns['confidence'] = 0.95
                return DocumentFormat.FORMAT_1_REPEATING_HEADER
            elif null_rate > 0.3 and has_grouping:  # 有空值且有分组
                patterns['confidence'] = 0.85
                return DocumentFormat.FORMAT_2_FORWARD_FILL
            elif has_grouping:
                patterns['confidence'] = 0.75
                return DocumentFormat.FORMAT_6_GROUPED
            else:
                patterns['confidence'] = 0.65
                return DocumentFormat.FORMAT_5_MIXED
        elif has_header and not has_line:
            patterns['confidence'] = 0.90
            return DocumentFormat.FORMAT_3_HEADER_ONLY
        elif not has_header and has_line:
            patterns['confidence'] = 0.90
            return DocumentFormat.FORMAT_4_LINE_ONLY
        else:
            patterns['confidence'] = 0.50
            return DocumentFormat.FORMAT_5_MIXED
```

#### 2.1.4 数据模型
```python
class DocumentFormatResult(BaseModel):
    format_type: DocumentFormat
    confidence: float
    header_columns: List[str]
    line_columns: List[str]
    statistics: Dict[str, Any]
    suggestions: List[str]
```

---

### Algorithm 2: 智能字段映射算法

#### 2.2.1 映射策略
```python
class IntelligentFieldMapper:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.weights = {
            'exact_match': 1.0,
            'historical_match': 0.9,
            'levenshtein_similarity': 0.7,
            'semantic_similarity': 0.6,
            'position_similarity': 0.3
        }
    
    async def recommend_mappings(
        self, 
        source_fields: List[str],
        target_table: str,
        context: Dict[str, Any]
    ) -> List[FieldMappingRecommendation]:
        """推荐字段映射"""
        
        # Step 1: 获取目标字段
        target_fields = await self._get_target_fields(target_table)
        
        # Step 2: 并行计算多种匹配分数
        results = await asyncio.gather(
            self._get_historical_mappings(source_fields, target_table, context),
            self._calculate_string_similarity(source_fields, target_fields),
            self._calculate_semantic_similarity(source_fields, target_fields),
            self._calculate_position_similarity(source_fields, target_fields)
        )
        
        historical = results[0]
        string_sim = results[1]
        semantic_sim = results[2]
        position_sim = results[3]
        
        # Step 3: 综合评分
        recommendations = []
        for source_field in source_fields:
            candidates = []
            
            for target_field in target_fields:
                # 计算综合分数
                score = 0.0
                reasons = []
                
                # 精确匹配
                if source_field.lower() == target_field.lower():
                    score = self.weights['exact_match']
                    reasons.append("精确匹配")
                else:
                    # 历史记录匹配
                    if source_field in historical and target_field in historical[source_field]:
                        hist_score = historical[source_field][target_field]
                        score += hist_score * self.weights['historical_match']
                        reasons.append(f"历史匹配(使用{hist_score:.0%}次)")
                    
                    # 字符串相似度
                    str_score = string_sim.get((source_field, target_field), 0)
                    score += str_score * self.weights['levenshtein_similarity']
                    if str_score > 0.7:
                        reasons.append(f"字符串相似度{str_score:.1%}")
                    
                    # 语义相似度
                    sem_score = semantic_sim.get((source_field, target_field), 0)
                    score += sem_score * self.weights['semantic_similarity']
                    if sem_score > 0.6:
                        reasons.append(f"语义相似度{sem_score:.1%}")
                    
                    # 位置相似度
                    pos_score = position_sim.get((source_field, target_field), 0)
                    score += pos_score * self.weights['position_similarity']
                
                # 归一化分数
                total_weight = sum(self.weights.values())
                normalized_score = min(score / total_weight, 1.0)
                
                if normalized_score > 0.3:  # 阈值过滤
                    candidates.append(
                        MappingCandidate(
                            target_field=target_field,
                            confidence=normalized_score,
                            reasons=reasons
                        )
                    )
            
            # 排序候选
            candidates.sort(key=lambda x: x.confidence, reverse=True)
            
            recommendations.append(
                FieldMappingRecommendation(
                    source_field=source_field,
                    candidates=candidates[:5],  # 只返回前5个
                    auto_confirm=candidates[0].confidence > 0.85 if candidates else False
                )
            )
        
        return recommendations
    
    def _calculate_string_similarity(
        self, 
        source_fields: List[str], 
        target_fields: List[str]
    ) -> Dict[Tuple[str, str], float]:
        """计算字符串相似度 (Levenshtein距离)"""
        from Levenshtein import ratio
        
        similarities = {}
        for src in source_fields:
            for tgt in target_fields:
                sim = ratio(src.lower(), tgt.lower())
                similarities[(src, tgt)] = sim
        
        return similarities
    
    def _calculate_semantic_similarity(
        self, 
        source_fields: List[str], 
        target_fields: List[str]
    ) -> Dict[Tuple[str, str], float]:
        """计算语义相似度 (基于预定义词库)"""
        # 同义词词库
        synonyms = {
            'order_no': ['订单号', '单据号', 'order_number', 'doc_no'],
            'customer': ['客户', 'client', 'customer_name', '客户名称'],
            'product': ['产品', 'item', 'sku', 'product_name', '物料'],
            'quantity': ['数量', 'qty', 'amount', '数量'],
            'price': ['单价', 'unit_price', '价格'],
            'amount': ['金额', 'total', 'total_amount', '总额'],
        }
        
        similarities = {}
        for src in source_fields:
            for tgt in target_fields:
                # 检查是否在同义词组中
                for key, words in synonyms.items():
                    if src.lower() in words and tgt.lower() in words:
                        similarities[(src, tgt)] = 0.9
                        break
                else:
                    similarities[(src, tgt)] = 0.0
        
        return similarities
```

#### 2.2.2 数据模型
```python
class MappingCandidate(BaseModel):
    target_field: str
    confidence: float
    reasons: List[str]

class FieldMappingRecommendation(BaseModel):
    source_field: str
    candidates: List[MappingCandidate]
    auto_confirm: bool

class FieldMappingConfirmation(BaseModel):
    source_field: str
    target_field: str
    user_confirmed: bool
```

---

### Algorithm 3: 主数据匹配算法

#### 2.3.1 支持的主数据类型
```python
class MasterDataType(str, Enum):
    BUSINESS_ENTITY = "business_entity"    # 经营主体
    CUSTOMER = "customer"                  # 客户
    SUPPLIER = "supplier"                  # 供应商
    PRODUCT_SKU = "product_sku"           # 产品/SKU
    DEPARTMENT = "department"             # 部门
    EMPLOYEE = "employee"                 # 员工
    PROJECT = "project"                   # 项目
```

#### 2.3.2 匹配算法
```python
class MasterDataMatcher:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def match_master_data(
        self,
        data: pd.DataFrame,
        field_name: str,
        master_type: MasterDataType,
        tenant_id: str
    ) -> MasterDataMatchResult:
        """主数据匹配"""
        
        # Step 1: 获取主数据
        master_data = await self._get_master_data(master_type, tenant_id)
        
        # Step 2: 执行三级匹配
        unique_values = data[field_name].dropna().unique()
        match_results = []
        
        for value in unique_values:
            # 精确匹配
            exact_match = self._exact_match(value, master_data)
            if exact_match:
                match_results.append(
                    MatchResult(
                        source_value=value,
                        matched_id=exact_match['id'],
                        matched_name=exact_match['name'],
                        match_type=MatchType.EXACT,
                        confidence=1.0
                    )
                )
                continue
            
            # 组合匹配 (编码+名称)
            combined_match = self._combined_match(value, master_data)
            if combined_match:
                match_results.append(
                    MatchResult(
                        source_value=value,
                        matched_id=combined_match['id'],
                        matched_name=combined_match['name'],
                        match_type=MatchType.COMBINED,
                        confidence=0.95
                    )
                )
                continue
            
            # 模糊匹配
            fuzzy_matches = self._fuzzy_match(value, master_data, threshold=0.8)
            if fuzzy_matches:
                if len(fuzzy_matches) == 1:
                    match = fuzzy_matches[0]
                    match_results.append(
                        MatchResult(
                            source_value=value,
                            matched_id=match['id'],
                            matched_name=match['name'],
                            match_type=MatchType.FUZZY,
                            confidence=match['score']
                        )
                    )
                else:
                    # 多个匹配候选，需要用户决策
                    match_results.append(
                        MatchResult(
                            source_value=value,
                            matched_id=None,
                            matched_name=None,
                            match_type=MatchType.MULTIPLE_CANDIDATES,
                            confidence=0.0,
                            candidates=[
                                MatchCandidate(
                                    id=m['id'],
                                    name=m['name'],
                                    code=m.get('code'),
                                    confidence=m['score']
                                )
                                for m in fuzzy_matches[:5]
                            ]
                        )
                    )
            else:
                # 无匹配
                match_results.append(
                    MatchResult(
                        source_value=value,
                        matched_id=None,
                        matched_name=None,
                        match_type=MatchType.NO_MATCH,
                        confidence=0.0,
                        suggest_create=True
                    )
                )
        
        # Step 3: 统计匹配情况
        stats = self._calculate_match_statistics(match_results)
        
        return MasterDataMatchResult(
            field_name=field_name,
            master_type=master_type,
            total_values=len(unique_values),
            match_results=match_results,
            statistics=stats,
            requires_user_decision=stats['requires_decision_count'] > 0
        )
    
    def _fuzzy_match(
        self, 
        value: str, 
        master_data: List[Dict], 
        threshold: float = 0.8
    ) -> List[Dict]:
        """模糊匹配 (使用rapidfuzz)"""
        from rapidfuzz import fuzz, process
        
        # 准备搜索数据
        choices = {
            item['name']: item for item in master_data
        }
        
        # 执行模糊搜索
        results = process.extract(
            value, 
            choices.keys(), 
            scorer=fuzz.WRatio,
            limit=5
        )
        
        # 过滤并返回
        matches = []
        for match_name, score, _ in results:
            if score >= threshold * 100:  # rapidfuzz返回0-100分数
                item = choices[match_name]
                matches.append({
                    'id': item['id'],
                    'name': item['name'],
                    'code': item.get('code'),
                    'score': score / 100.0
                })
        
        return matches
```

#### 2.3.3 数据模型
```python
class MatchType(str, Enum):
    EXACT = "exact"
    COMBINED = "combined"
    FUZZY = "fuzzy"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    NO_MATCH = "no_match"

class MatchCandidate(BaseModel):
    id: str
    name: str
    code: Optional[str]
    confidence: float

class MatchResult(BaseModel):
    source_value: str
    matched_id: Optional[str]
    matched_name: Optional[str]
    match_type: MatchType
    confidence: float
    candidates: List[MatchCandidate] = []
    suggest_create: bool = False

class MasterDataMatchResult(BaseModel):
    field_name: str
    master_type: MasterDataType
    total_values: int
    match_results: List[MatchResult]
    statistics: Dict[str, int]
    requires_user_decision: bool
```

---

### Algorithm 4: 单据头ID匹配算法

#### 2.4.1 应用场景
仅单据体格式(格式4)，需要匹配已有单据头或创建新单据头

#### 2.4.2 匹配算法
```python
class DocumentHeaderMatcher:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def match_document_headers(
        self,
        line_items: pd.DataFrame,
        document_type: str,  # 'sales_order', 'shipment', etc.
        key_fields: List[str],  # ['order_no', 'order_date', 'customer_id']
        tenant_id: str
    ) -> DocumentHeaderMatchResult:
        """匹配单据头"""
        
        # Step 1: 提取唯一的单据头组合
        unique_headers = line_items[key_fields].drop_duplicates()
        
        # Step 2: 查询数据库中已有的单据头
        table_name = f"{document_type}_header"
        existing_headers = await self._query_existing_headers(
            table_name, key_fields, unique_headers, tenant_id
        )
        
        # Step 3: 执行匹配
        match_results = []
        for _, header_row in unique_headers.iterrows():
            # 构造匹配键
            match_key = {k: header_row[k] for k in key_fields}
            
            # 精确匹配
            matched = self._find_exact_match(match_key, existing_headers)
            if matched:
                match_results.append(
                    HeaderMatchResult(
                        source_key=match_key,
                        matched_header_id=matched['id'],
                        match_type=HeaderMatchType.EXACT,
                        confidence=1.0,
                        action=MatchAction.USE_EXISTING
                    )
                )
            else:
                # 模糊匹配 (单据号相似，日期接近)
                fuzzy_matches = self._fuzzy_match_headers(
                    match_key, existing_headers, threshold=0.85
                )
                
                if len(fuzzy_matches) == 1:
                    match = fuzzy_matches[0]
                    match_results.append(
                        HeaderMatchResult(
                            source_key=match_key,
                            matched_header_id=match['id'],
                            match_type=HeaderMatchType.FUZZY,
                            confidence=match['score'],
                            action=MatchAction.USE_EXISTING,
                            requires_confirmation=True
                        )
                    )
                elif len(fuzzy_matches) > 1:
                    match_results.append(
                        HeaderMatchResult(
                            source_key=match_key,
                            matched_header_id=None,
                            match_type=HeaderMatchType.MULTIPLE,
                            confidence=0.0,
                            action=MatchAction.USER_DECIDE,
                            candidates=fuzzy_matches,
                            requires_confirmation=True
                        )
                    )
                else:
                    # 无匹配，建议创建新单据头
                    match_results.append(
                        HeaderMatchResult(
                            source_key=match_key,
                            matched_header_id=None,
                            match_type=HeaderMatchType.NO_MATCH,
                            confidence=0.0,
                            action=MatchAction.CREATE_NEW,
                            requires_confirmation=False
                        )
                    )
        
        return DocumentHeaderMatchResult(
            document_type=document_type,
            total_headers=len(unique_headers),
            match_results=match_results,
            requires_user_decision=any(r.requires_confirmation for r in match_results)
        )
    
    def _fuzzy_match_headers(
        self,
        key: Dict[str, Any],
        existing: List[Dict],
        threshold: float = 0.85
    ) -> List[Dict]:
        """模糊匹配单据头"""
        from rapidfuzz import fuzz
        from datetime import timedelta
        
        matches = []
        
        for existing_header in existing:
            score = 0.0
            components = []
            
            # 单据号相似度 (权重0.6)
            if 'order_no' in key and 'order_no' in existing_header:
                order_sim = fuzz.ratio(
                    str(key['order_no']), 
                    str(existing_header['order_no'])
                ) / 100.0
                score += order_sim * 0.6
                components.append(order_sim * 0.6)
            
            # 日期接近度 (权重0.3)
            if 'order_date' in key and 'order_date' in existing_header:
                date_diff = abs((key['order_date'] - existing_header['order_date']).days)
                if date_diff <= 3:  # 3天内
                    date_score = 1.0 - (date_diff / 3.0)
                    score += date_score * 0.3
                    components.append(date_score * 0.3)
            
            # 客户匹配 (权重0.1)
            if 'customer_id' in key and 'customer_id' in existing_header:
                if key['customer_id'] == existing_header['customer_id']:
                    score += 0.1
                    components.append(0.1)
            
            if score >= threshold:
                matches.append({
                    'id': existing_header['id'],
                    'order_no': existing_header.get('order_no'),
                    'order_date': existing_header.get('order_date'),
                    'score': score,
                    'score_breakdown': components
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
```

---

### Algorithm 5: 数据处理与验证算法

#### 2.5.1 前向填充处理
```python
class DataProcessor:
    def forward_fill_headers(
        self, 
        df: pd.DataFrame, 
        header_cols: List[str]
    ) -> pd.DataFrame:
        """前向填充单据头字段"""
        df_filled = df.copy()
        
        for col in header_cols:
            if col in df_filled.columns:
                # 前向填充空值
                df_filled[col] = df_filled[col].fillna(method='ffill')
        
        return df_filled
```

#### 2.5.2 头-明细关联
```python
    def associate_header_lines(
        self,
        df: pd.DataFrame,
        header_key_cols: List[str],
        line_cols: List[str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """关联单据头和单据体"""
        
        # 提取单据头 (去重)
        header_df = df[header_key_cols].drop_duplicates().reset_index(drop=True)
        header_df['temp_header_id'] = range(len(header_df))
        
        # 合并获取header_id
        df_with_id = df.merge(
            header_df, 
            on=header_key_cols, 
            how='left'
        )
        
        # 分离单据体
        line_df = df_with_id[['temp_header_id'] + line_cols].copy()
        
        return header_df, line_df
```

#### 2.5.3 金额验证
```python
    def validate_amounts(
        self,
        df: pd.DataFrame,
        qty_col: str = 'quantity',
        price_col: str = 'unit_price',
        amount_col: str = 'amount',
        tax_rate_col: str = 'tax_rate',
        tax_amount_col: str = 'tax_amount',
        total_col: str = 'total_amount',
        tolerance: float = 0.01
    ) -> AmountValidationResult:
        """验证金额计算一致性"""
        
        issues = []
        
        for idx, row in df.iterrows():
            # 验证: 金额 = 数量 × 单价
            if all(col in df.columns for col in [qty_col, price_col, amount_col]):
                calculated = row[qty_col] * row[price_col]
                actual = row[amount_col]
                if abs(calculated - actual) > tolerance:
                    issues.append(
                        AmountIssue(
                            row_index=idx,
                            issue_type='amount_mismatch',
                            expected=calculated,
                            actual=actual,
                            difference=actual - calculated
                        )
                    )
            
            # 验证: 价税合计 = 金额 + 税额
            if all(col in df.columns for col in [amount_col, tax_amount_col, total_col]):
                calculated_total = row[amount_col] + row[tax_amount_col]
                actual_total = row[total_col]
                if abs(calculated_total - actual_total) > tolerance:
                    issues.append(
                        AmountIssue(
                            row_index=idx,
                            issue_type='total_mismatch',
                            expected=calculated_total,
                            actual=actual_total,
                            difference=actual_total - calculated_total
                        )
                    )
        
        return AmountValidationResult(
            total_rows=len(df),
            issues_found=len(issues),
            issues=issues,
            is_valid=len(issues) == 0
        )
```

---

## 3. API端点设计

### 3.1 文件分析端点
```python
@router.post("/api/v1/data-import/analyze")
async def analyze_import_file(
    file: UploadFile,
    document_type: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
) -> FileAnalysisResponse:
    """
    分析导入文件并推荐配置
    
    Returns:
        - 格式识别结果
        - 字段映射推荐
        - 数据质量评估
    """
    pass
```

### 3.2 格式处理端点
```python
@router.post("/api/v1/data-import/process")
async def process_import_file(
    file: UploadFile,
    config: ImportConfiguration,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
) -> ProcessingResponse:
    """
    处理导入文件
    
    Steps:
        1. 格式识别
        2. 字段映射应用
        3. 数据转换
        4. 写入暂存表
    
    Returns:
        - 处理状态
        - 暂存表ID
        - 记录数统计
    """
    pass
```

### 3.3 主数据匹配端点
```python
@router.post("/api/v1/data-import/match-master-data")
async def match_master_data(
    staging_table_id: str,
    field_name: str,
    master_type: MasterDataType,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
) -> MasterDataMatchResult:
    """
    主数据匹配
    
    Returns:
        - 匹配结果
        - 需要用户决策的项
        - 匹配统计
    """
    pass
```

### 3.4 单据头匹配端点
```python
@router.post("/api/v1/data-import/match-document-header")
async def match_document_header(
    staging_table_id: str,
    document_type: str,
    key_fields: List[str],
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
) -> DocumentHeaderMatchResult:
    """
    单据头匹配
    
    Returns:
        - 匹配结果
        - 需要创建的新单据头
        - 需要用户确认的项
    """
    pass
```

### 3.5 用户决策确认端点
```python
@router.post("/api/v1/data-import/confirm-decisions")
async def confirm_user_decisions(
    staging_table_id: str,
    decisions: List[UserDecision],
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user)
) -> ConfirmationResponse:
    """
    确认用户决策并完成导入
    
    Steps:
        1. 应用用户决策
        2. 创建新主数据/单据头 (如需要)
        3. 从暂存表写入正式表
        4. 更新映射历史
    
    Returns:
        - 导入结果
        - 成功/失败记录数
    """
    pass
```

---

## 4. 数据库设计

### 4.1 暂存表
```sql
CREATE TABLE import_staging (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255),
    row_data JSONB NOT NULL,  -- 原始行数据
    mapped_data JSONB,         -- 映射后数据
    validation_status VARCHAR(20),  -- 'pending', 'valid', 'invalid'
    validation_errors JSONB,
    match_status VARCHAR(20),  -- 'pending', 'matched', 'requires_decision'
    match_results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_staging_tenant ON import_staging(tenant_id);
CREATE INDEX idx_staging_status ON import_staging(validation_status, match_status);
```

### 4.2 字段映射历史表
```sql
CREATE TABLE field_mapping_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    document_type VARCHAR(50),
    source_field VARCHAR(100),
    target_field VARCHAR(100),
    confidence DECIMAL(3,2),
    usage_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mapping_lookup ON field_mapping_history(
    tenant_id, document_type, source_field
);
```

---

## 5. 实现优先级

### Phase 1: 核心算法 (Week 1-2)
- [ ] Algorithm 1: 格式识别算法
- [ ] Algorithm 2: 智能字段映射算法
- [ ] 数据库表创建
- [ ] `/analyze` 端点

### Phase 2: 匹配算法 (Week 3-4)
- [ ] Algorithm 3: 主数据匹配算法
- [ ] Algorithm 4: 单据头ID匹配算法
- [ ] `/match-master-data` 端点
- [ ] `/match-document-header` 端点

### Phase 3: 数据处理 (Week 5)
- [ ] Algorithm 5: 数据处理与验证
- [ ] `/process` 端点
- [ ] `/confirm-decisions` 端点

### Phase 4: 集成测试 (Week 6)
- [ ] 与Lovable前端集成
- [ ] 完整流程测试
- [ ] 性能优化

---

## 6. 性能优化建议

### 6.1 大文件处理
```python
async def process_large_file_in_chunks(
    file_path: str,
    chunk_size: int = 10000
) -> AsyncGenerator[pd.DataFrame, None]:
    """分块处理大文件"""
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        yield chunk
```

### 6.2 并行处理
```python
async def parallel_master_data_matching(
    df: pd.DataFrame,
    fields_to_match: List[Tuple[str, MasterDataType]]
) -> Dict[str, MasterDataMatchResult]:
    """并行执行多个字段的主数据匹配"""
    tasks = [
        match_master_data(df, field, master_type)
        for field, master_type in fields_to_match
    ]
    results = await asyncio.gather(*tasks)
    return dict(zip([f[0] for f in fields_to_match], results))
```

### 6.3 缓存策略
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_master_data(
    master_type: MasterDataType,
    tenant_id: str
) -> List[Dict]:
    """缓存主数据查询"""
    return await db.fetch_master_data(master_type, tenant_id)
```

---

## 7. 错误处理

### 7.1 异常定义
```python
class ImportError(Exception):
    """导入基础异常"""
    pass

class FormatRecognitionError(ImportError):
    """格式识别失败"""
    pass

class FieldMappingError(ImportError):
    """字段映射错误"""
    pass

class MasterDataMatchError(ImportError):
    """主数据匹配失败"""
    pass

class ValidationError(ImportError):
    """数据验证失败"""
    pass
```

### 7.2 错误响应
```python
class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime
```

---

## 8. 测试策略

### 8.1 单元测试
```python
# tests/test_format_recognizer.py
async def test_format_1_recognition():
    df = pd.DataFrame({
        'order_no': ['SO001', 'SO001', 'SO002'],
        'product': ['P1', 'P2', 'P3']
    })
    result = await recognizer.recognize_format(df)
    assert result.format_type == DocumentFormat.FORMAT_1_REPEATING_HEADER
```

### 8.2 集成测试
```python
# tests/test_import_flow.py
async def test_complete_import_flow():
    # 上传文件
    analysis = await analyze_import_file(test_file)
    
    # 处理文件
    processing = await process_import_file(test_file, analysis.config)
    
    # 主数据匹配
    match_result = await match_master_data(processing.staging_id, 'customer')
    
    # 确认导入
    final = await confirm_user_decisions(processing.staging_id, decisions)
    
    assert final.success_count > 0
```

---

## 9. 部署配置

### 9.1 依赖项
```txt
# requirements.txt
fastapi==0.104.0
pandas==2.1.0
numpy==1.25.0
python-Levenshtein==0.21.0
rapidfuzz==3.2.0
asyncpg==0.28.0
pydantic==2.4.0
openpyxl==3.1.2  # Excel支持
```

### 9.2 环境变量
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/bmos
REDIS_URL=redis://localhost:6379
MAX_FILE_SIZE_MB=100
CHUNK_SIZE=10000
```

---

## 10. 文档要求

### 10.1 API文档
- 使用FastAPI自动生成OpenAPI文档
- 访问 `/docs` 查看交互式API文档

### 10.2 算法文档
- 每个算法类添加详细的docstring
- 包含参数说明、返回值、示例代码

### 10.3 用户手册
- 创建 `docs/user-guide/DATA_IMPORT_GUIDE.md`
- 包含操作流程、常见问题、故障排查

---

**本技术方案需在Cursor中的FastAPI后端实现**
