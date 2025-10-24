# 复杂单据格式处理 - ETL扩展设计

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (算法设计与技术架构)
- **实施方**: Lovable (前端集成与UI实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 复杂单据格式问题分析

### 1.1 单据格式类型识别

根据您描述的情况，我们需要处理以下5种复杂的单据格式：

#### **格式1: 多行明细对应重复单据头**
```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 金额
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 1000
DOC001 | 2024-01-01 | 客户A | 产品2 | 5  | 500
DOC002 | 2024-01-02 | 客户B | 产品3 | 8  | 800
```

#### **格式2: 多行明细但只有第一行有单据头**
```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 金额
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 1000
       |           |        | 产品2 | 5  | 500
       |           |        | 产品3 | 3  | 300
DOC002 | 2024-01-02 | 客户B | 产品4 | 8  | 800
```

#### **格式3: 单据头和明细分离在不同表**
```
单据头表:
单据号 | 单据日期 | 客户名称 | 总金额
DOC001 | 2024-01-01 | 客户A | 1800

明细表:
单据号 | 产品名称 | 数量 | 金额
DOC001 | 产品1 | 10 | 1000
DOC001 | 产品2 | 5  | 500
DOC001 | 产品3 | 3  | 300
```

#### **格式4: 只有单据头记录**
```
单据号 | 单据日期 | 客户名称 | 总金额 | 备注
DOC001 | 2024-01-01 | 客户A | 1800 | 汇总单据
```

#### **格式5: 只有明细记录**
```
产品名称 | 数量 | 金额 | 部门
产品1 | 10 | 1000 | 销售部
产品2 | 5  | 500  | 销售部
产品3 | 3  | 300  | 销售部
```

---

## 2. 智能单据格式识别算法

### 2.1 格式识别器设计

```python
class DocumentFormatDetector:
    """单据格式识别器"""
    
    def __init__(self):
        self.format_patterns = {
            'repeated_header': self.detect_repeated_header,
            'first_row_header': self.detect_first_row_header,
            'separated_tables': self.detect_separated_tables,
            'header_only': self.detect_header_only,
            'detail_only': self.detect_detail_only
        }
    
    def detect_format(self, data: pd.DataFrame, metadata: dict = None) -> str:
        """检测单据格式"""
        scores = {}
        
        for format_name, detector in self.format_patterns.items():
            score = detector(data, metadata)
            scores[format_name] = score
        
        # 返回得分最高的格式
        return max(scores, key=scores.get)
    
    def detect_repeated_header(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测重复单据头格式"""
        score = 0.0
        
        # 检查是否有重复的单据号
        if '单据号' in data.columns or 'document_id' in data.columns:
            doc_id_col = '单据号' if '单据号' in data.columns else 'document_id'
            unique_docs = data[doc_id_col].nunique()
            total_rows = len(data)
            
            # 如果重复单据号较多，可能是重复头格式
            if unique_docs < total_rows * 0.8:
                score += 0.6
        
        # 检查是否有客户名称等头信息重复
        header_cols = ['客户名称', 'customer_name', '单据日期', 'document_date']
        for col in header_cols:
            if col in data.columns:
                if data[col].nunique() < len(data) * 0.8:
                    score += 0.2
        
        return min(score, 1.0)
    
    def detect_first_row_header(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测第一行单据头格式"""
        score = 0.0
        
        # 检查是否有空值模式
        if len(data) > 1:
            # 检查第二行开始是否有空值
            second_row = data.iloc[1]
            empty_count = second_row.isna().sum()
            total_cols = len(second_row)
            
            if empty_count > total_cols * 0.3:
                score += 0.7
        
        # 检查是否有单据号列且第一行有值，后续行为空
        doc_cols = ['单据号', 'document_id', '单号']
        for col in doc_cols:
            if col in data.columns:
                first_value = data[col].iloc[0]
                if pd.notna(first_value):
                    # 检查后续行是否为空
                    subsequent_empty = data[col].iloc[1:].isna().sum()
                    if subsequent_empty > len(data) * 0.5:
                        score += 0.3
        
        return min(score, 1.0)
    
    def detect_separated_tables(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测分离表格式"""
        score = 0.0
        
        # 如果有元数据信息，检查是否提到分离表
        if metadata and 'table_type' in metadata:
            if metadata['table_type'] in ['header', 'detail']:
                score += 0.8
        
        # 检查数据特征
        if '单据号' in data.columns:
            # 如果单据号唯一且行数较少，可能是头表
            if data['单据号'].nunique() == len(data) and len(data) < 100:
                score += 0.6
        
        return min(score, 1.0)
    
    def detect_header_only(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测只有单据头格式"""
        score = 0.0
        
        # 检查是否有汇总字段
        summary_cols = ['总金额', 'total_amount', '汇总', 'summary']
        for col in summary_cols:
            if col in data.columns:
                score += 0.4
        
        # 检查行数是否较少
        if len(data) < 50:
            score += 0.3
        
        # 检查是否有明细相关字段
        detail_cols = ['产品名称', 'product_name', '数量', 'quantity']
        detail_count = sum(1 for col in detail_cols if col in data.columns)
        if detail_count == 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def detect_detail_only(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测只有明细格式"""
        score = 0.0
        
        # 检查是否有明细字段
        detail_cols = ['产品名称', 'product_name', '数量', 'quantity', '金额', 'amount']
        detail_count = sum(1 for col in detail_cols if col in data.columns)
        if detail_count >= 3:
            score += 0.5
        
        # 检查是否没有单据头字段
        header_cols = ['单据号', 'document_id', '客户名称', 'customer_name']
        header_count = sum(1 for col in header_cols if col in data.columns)
        if header_count == 0:
            score += 0.3
        
        # 检查是否有部门等分类字段
        if '部门' in data.columns or 'department' in data.columns:
            score += 0.2
        
        return min(score, 1.0)
```

### 2.2 智能数据处理器

```python
class IntelligentDocumentProcessor:
    """智能单据处理器"""
    
    def __init__(self):
        self.format_detector = DocumentFormatDetector()
        self.processors = {
            'repeated_header': self.process_repeated_header,
            'first_row_header': self.process_first_row_header,
            'separated_tables': self.process_separated_tables,
            'header_only': self.process_header_only,
            'detail_only': self.process_detail_only
        }
    
    def process_document(self, data: pd.DataFrame, metadata: dict = None) -> ProcessResult:
        """处理单据数据"""
        # 1. 检测格式
        format_type = self.format_detector.detect_format(data, metadata)
        
        # 2. 选择处理器
        processor = self.processors.get(format_type)
        if not processor:
            raise ValueError(f"不支持的格式类型: {format_type}")
        
        # 3. 处理数据
        result = processor(data, metadata)
        
        return ProcessResult(
            format_type=format_type,
            processed_data=result,
            success=True
        )
    
    def process_repeated_header(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理重复单据头格式"""
        # 直接使用原始数据，因为每行都是完整的记录
        return data.copy()
    
    def process_first_row_header(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理第一行单据头格式"""
        processed_data = data.copy()
        
        # 识别头字段和明细字段
        header_fields = self.identify_header_fields(data)
        detail_fields = self.identify_detail_fields(data)
        
        # 填充空值
        for field in header_fields:
            if field in processed_data.columns:
                processed_data[field] = processed_data[field].fillna(method='ffill')
        
        return processed_data
    
    def process_separated_tables(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理分离表格式"""
        # 需要额外的头表数据
        if not metadata or 'header_data' not in metadata:
            raise ValueError("分离表格式需要提供头表数据")
        
        header_data = metadata['header_data']
        
        # 合并头表和明细表
        merged_data = self.merge_header_and_detail(header_data, data)
        
        return merged_data
    
    def process_header_only(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理只有单据头格式"""
        # 为汇总数据创建虚拟明细记录
        processed_data = self.create_virtual_details(data)
        
        return processed_data
    
    def process_detail_only(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理只有明细格式"""
        # 为明细数据创建虚拟单据头
        processed_data = self.create_virtual_header(data)
        
        return processed_data
    
    def identify_header_fields(self, data: pd.DataFrame) -> list:
        """识别单据头字段"""
        header_patterns = [
            '单据号', 'document_id', '单号',
            '单据日期', 'document_date', '日期',
            '客户名称', 'customer_name', '客户',
            '总金额', 'total_amount', '金额'
        ]
        
        return [col for col in data.columns if any(pattern in col for pattern in header_patterns)]
    
    def identify_detail_fields(self, data: pd.DataFrame) -> list:
        """识别明细字段"""
        detail_patterns = [
            '产品名称', 'product_name', '产品',
            '数量', 'quantity', 'qty',
            '单价', 'unit_price', '价格',
            '金额', 'amount', '小计'
        ]
        
        return [col for col in data.columns if any(pattern in col for pattern in detail_patterns)]
    
    def merge_header_and_detail(self, header_data: pd.DataFrame, detail_data: pd.DataFrame) -> pd.DataFrame:
        """合并头表和明细表"""
        # 找到关联字段
        header_key = self.find_join_key(header_data)
        detail_key = self.find_join_key(detail_data)
        
        if not header_key or not detail_key:
            raise ValueError("无法找到关联字段")
        
        # 执行合并
        merged = detail_data.merge(
            header_data,
            left_on=detail_key,
            right_on=header_key,
            how='left'
        )
        
        return merged
    
    def create_virtual_details(self, header_data: pd.DataFrame) -> pd.DataFrame:
        """为头表创建虚拟明细"""
        virtual_details = []
        
        for _, row in header_data.iterrows():
            # 创建一条虚拟明细记录
            virtual_detail = {
                '单据号': row.get('单据号', ''),
                '产品名称': '汇总项目',
                '数量': 1,
                '金额': row.get('总金额', 0),
                '备注': '汇总记录'
            }
            virtual_details.append(virtual_detail)
        
        return pd.DataFrame(virtual_details)
    
    def create_virtual_header(self, detail_data: pd.DataFrame) -> pd.DataFrame:
        """为明细表创建虚拟单据头"""
        # 按部门或其他分组字段创建虚拟单据头
        if '部门' in detail_data.columns:
            grouped = detail_data.groupby('部门')
        else:
            # 如果没有分组字段，创建单个虚拟头
            grouped = [(None, detail_data)]
        
        virtual_headers = []
        
        for group_name, group_data in grouped:
            virtual_header = {
                '单据号': f"VIRTUAL_{group_name or 'DEFAULT'}_{len(virtual_headers) + 1}",
                '单据日期': pd.Timestamp.now().strftime('%Y-%m-%d'),
                '客户名称': f"虚拟客户_{group_name or 'DEFAULT'}",
                '总金额': group_data['金额'].sum() if '金额' in group_data.columns else 0,
                '备注': f"虚拟单据头_{group_name or 'DEFAULT'}"
            }
            virtual_headers.append(virtual_header)
        
        return pd.DataFrame(virtual_headers)
    
    def find_join_key(self, data: pd.DataFrame) -> str:
        """查找关联字段"""
        key_patterns = ['单据号', 'document_id', '单号', 'id']
        
        for pattern in key_patterns:
            for col in data.columns:
                if pattern in col.lower():
                    return col
        
        return None
```

---

## 3. 配置驱动的处理策略

### 3.1 处理配置定义

```python
@dataclass
class DocumentProcessingConfig:
    """单据处理配置"""
    
    # 格式识别配置
    auto_detect_format: bool = True
    preferred_format: str = None
    
    # 字段映射配置
    field_mappings: Dict[str, str] = None
    
    # 数据验证配置
    validation_rules: Dict[str, Dict] = None
    
    # 处理策略配置
    processing_strategy: str = 'standard'  # standard, aggressive, conservative
    
    # 错误处理配置
    error_handling: str = 'strict'  # strict, lenient, ignore
    
    def __post_init__(self):
        if self.field_mappings is None:
            self.field_mappings = {
                '单据号': 'document_id',
                '单据日期': 'document_date',
                '客户名称': 'customer_name',
                '产品名称': 'product_name',
                '数量': 'quantity',
                '金额': 'amount'
            }
        
        if self.validation_rules is None:
            self.validation_rules = {
                'document_id': {'required': True, 'unique': True},
                'document_date': {'required': True, 'format': 'date'},
                'amount': {'required': True, 'min': 0}
            }
```

### 3.2 处理策略实现

```python
class DocumentProcessingStrategy:
    """单据处理策略"""
    
    def __init__(self, config: DocumentProcessingConfig):
        self.config = config
        self.processor = IntelligentDocumentProcessor()
    
    def process(self, data: pd.DataFrame, metadata: dict = None) -> ProcessResult:
        """执行处理策略"""
        
        # 1. 预处理数据
        preprocessed_data = self.preprocess_data(data)
        
        # 2. 格式识别和处理
        if self.config.auto_detect_format:
            result = self.processor.process_document(preprocessed_data, metadata)
        else:
            result = self.process_with_preferred_format(preprocessed_data, metadata)
        
        # 3. 后处理
        final_result = self.postprocess_data(result.processed_data)
        
        # 4. 数据验证
        validation_result = self.validate_processed_data(final_result)
        
        return ProcessResult(
            format_type=result.format_type,
            processed_data=final_result,
            validation_result=validation_result,
            success=validation_result.success
        )
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理"""
        processed = data.copy()
        
        # 清理空白行
        processed = processed.dropna(how='all')
        
        # 清理空白列
        processed = processed.dropna(axis=1, how='all')
        
        # 标准化列名
        processed.columns = processed.columns.str.strip()
        
        return processed
    
    def process_with_preferred_format(self, data: pd.DataFrame, metadata: dict = None) -> ProcessResult:
        """使用指定格式处理"""
        format_type = self.config.preferred_format
        processor = self.processor.processors.get(format_type)
        
        if not processor:
            raise ValueError(f"不支持的指定格式: {format_type}")
        
        processed_data = processor(data, metadata)
        
        return ProcessResult(
            format_type=format_type,
            processed_data=processed_data,
            success=True
        )
    
    def postprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据后处理"""
        processed = data.copy()
        
        # 字段映射
        if self.config.field_mappings:
            processed = processed.rename(columns=self.config.field_mappings)
        
        # 数据类型转换
        processed = self.convert_data_types(processed)
        
        # 数据标准化
        processed = self.standardize_data(processed)
        
        return processed
    
    def convert_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据类型转换"""
        processed = data.copy()
        
        # 日期字段转换
        date_columns = ['document_date', '单据日期', '日期']
        for col in date_columns:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col], errors='coerce')
        
        # 数值字段转换
        numeric_columns = ['amount', '金额', 'quantity', '数量']
        for col in numeric_columns:
            if col in processed.columns:
                processed[col] = pd.to_numeric(processed[col], errors='coerce')
        
        return processed
    
    def standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据标准化"""
        processed = data.copy()
        
        # 字符串字段标准化
        string_columns = processed.select_dtypes(include=['object']).columns
        for col in string_columns:
            processed[col] = processed[col].astype(str).str.strip()
        
        return processed
    
    def validate_processed_data(self, data: pd.DataFrame) -> ValidationResult:
        """验证处理后的数据"""
        errors = []
        
        if self.config.validation_rules:
            for field, rules in self.config.validation_rules.items():
                if field in data.columns:
                    # 必填字段检查
                    if rules.get('required', False):
                        if data[field].isna().any():
                            errors.append(f"{field} 字段存在空值")
                    
                    # 唯一性检查
                    if rules.get('unique', False):
                        if data[field].duplicated().any():
                            errors.append(f"{field} 字段存在重复值")
                    
                    # 数值范围检查
                    if 'min' in rules:
                        if (data[field] < rules['min']).any():
                            errors.append(f"{field} 字段存在小于 {rules['min']} 的值")
                    
                    if 'max' in rules:
                        if (data[field] > rules['max']).any():
                            errors.append(f"{field} 字段存在大于 {rules['max']} 的值")
        
        return ValidationResult(
            success=len(errors) == 0,
            errors=errors
        )
```

---

## 4. 使用示例和最佳实践

### 4.1 基本使用示例

```python
# 示例1: 自动格式识别
def process_unknown_format():
    """处理未知格式的数据"""
    
    # 加载数据
    data = pd.read_excel('unknown_format.xlsx')
    
    # 创建配置
    config = DocumentProcessingConfig(
        auto_detect_format=True,
        processing_strategy='standard',
        error_handling='lenient'
    )
    
    # 创建处理器
    strategy = DocumentProcessingStrategy(config)
    
    # 处理数据
    result = strategy.process(data)
    
    if result.success:
        print(f"检测到格式: {result.format_type}")
        print(f"处理成功，共 {len(result.processed_data)} 条记录")
        return result.processed_data
    else:
        print(f"处理失败: {result.validation_result.errors}")
        return None

# 示例2: 指定格式处理
def process_specific_format():
    """处理指定格式的数据"""
    
    # 加载数据
    data = pd.read_excel('first_row_header_format.xlsx')
    
    # 创建配置
    config = DocumentProcessingConfig(
        auto_detect_format=False,
        preferred_format='first_row_header',
        processing_strategy='aggressive'
    )
    
    # 创建处理器
    strategy = DocumentProcessingStrategy(config)
    
    # 处理数据
    result = strategy.process(data)
    
    return result.processed_data

# 示例3: 分离表格式处理
def process_separated_tables():
    """处理分离表格式数据"""
    
    # 加载头表和明细表
    header_data = pd.read_excel('header_table.xlsx')
    detail_data = pd.read_excel('detail_table.xlsx')
    
    # 创建元数据
    metadata = {
        'table_type': 'detail',
        'header_data': header_data
    }
    
    # 创建配置
    config = DocumentProcessingConfig(
        auto_detect_format=True,
        processing_strategy='standard'
    )
    
    # 创建处理器
    strategy = DocumentProcessingStrategy(config)
    
    # 处理数据
    result = strategy.process(detail_data, metadata)
    
    return result.processed_data
```

### 4.2 错误处理和恢复

```python
class DocumentProcessingErrorHandler:
    """单据处理错误处理器"""
    
    def __init__(self, config: DocumentProcessingConfig):
        self.config = config
    
    def handle_processing_error(self, error: Exception, data: pd.DataFrame) -> ProcessResult:
        """处理处理错误"""
        
        if self.config.error_handling == 'strict':
            # 严格模式：直接抛出错误
            raise error
        
        elif self.config.error_handling == 'lenient':
            # 宽松模式：尝试修复错误
            return self.attempt_error_recovery(error, data)
        
        elif self.config.error_handling == 'ignore':
            # 忽略模式：返回原始数据
            return ProcessResult(
                format_type='unknown',
                processed_data=data,
                success=False,
                error_message=str(error)
            )
    
    def attempt_error_recovery(self, error: Exception, data: pd.DataFrame) -> ProcessResult:
        """尝试错误恢复"""
        
        # 尝试不同的处理策略
        recovery_strategies = [
            self.try_simple_format,
            self.try_manual_mapping,
            self.try_partial_processing
        ]
        
        for strategy in recovery_strategies:
            try:
                result = strategy(data)
                if result.success:
                    return result
            except Exception:
                continue
        
        # 如果所有策略都失败，返回错误
        return ProcessResult(
            format_type='unknown',
            processed_data=data,
            success=False,
            error_message=f"无法恢复处理错误: {str(error)}"
        )
    
    def try_simple_format(self, data: pd.DataFrame) -> ProcessResult:
        """尝试简单格式处理"""
        # 假设所有数据都是完整记录
        return ProcessResult(
            format_type='repeated_header',
            processed_data=data,
            success=True
        )
    
    def try_manual_mapping(self, data: pd.DataFrame) -> ProcessResult:
        """尝试手动映射"""
        # 使用默认字段映射
        mapped_data = data.copy()
        if self.config.field_mappings:
            mapped_data = mapped_data.rename(columns=self.config.field_mappings)
        
        return ProcessResult(
            format_type='manual_mapping',
            processed_data=mapped_data,
            success=True
        )
    
    def try_partial_processing(self, data: pd.DataFrame) -> ProcessResult:
        """尝试部分处理"""
        # 只处理能识别的字段
        processed_data = data.copy()
        
        # 移除无法处理的列
        processed_data = processed_data.dropna(axis=1, how='all')
        
        return ProcessResult(
            format_type='partial',
            processed_data=processed_data,
            success=True
        )
```

---

## 5. 集成到现有ETL系统

### 5.1 扩展现有ETL处理器

```python
class EnhancedETLProcessor(ETLProcessor):
    """增强的ETL处理器"""
    
    def __init__(self, config: ETLConfig):
        super().__init__(config)
        self.document_processor = IntelligentDocumentProcessor()
        self.document_strategy = DocumentProcessingStrategy(
            DocumentProcessingConfig()
        )
    
    def process_document_data(self, file_path: str, metadata: dict = None) -> ProcessingResult:
        """处理单据数据"""
        try:
            # 1. 提取数据
            raw_data = self.extract_data(file_path)
            
            # 2. 智能格式处理
            document_result = self.document_strategy.process(raw_data, metadata)
            
            if not document_result.success:
                return ProcessingResult(
                    success=False,
                    file_path=file_path,
                    errors=[f"单据格式处理失败: {document_result.error_message}"]
                )
            
            # 3. 标准ETL处理
            cleaned_data = self.clean_data(document_result.processed_data)
            validated_data = self.validate_data(cleaned_data)
            transformed_data = self.transform_data(validated_data)
            
            # 4. 加载数据
            load_result = self.load_data(transformed_data, 'processed_documents')
            
            return ProcessingResult(
                success=True,
                file_path=file_path,
                data=transformed_data,
                row_count=len(transformed_data),
                format_type=document_result.format_type
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                file_path=file_path,
                errors=[str(e)]
            )
```

### 5.2 配置管理

```python
# 配置文件示例: document_processing_config.yaml
document_processing:
  auto_detect_format: true
  preferred_format: null
  processing_strategy: standard
  error_handling: lenient
  
  field_mappings:
    单据号: document_id
    单据日期: document_date
    客户名称: customer_name
    产品名称: product_name
    数量: quantity
    金额: amount
  
  validation_rules:
    document_id:
      required: true
      unique: true
    document_date:
      required: true
      format: date
    amount:
      required: true
      min: 0
  
  format_specific_rules:
    first_row_header:
      fill_method: forward
      header_fields: [单据号, 单据日期, 客户名称]
    separated_tables:
      join_key: 单据号
      header_required: true
    detail_only:
      create_virtual_header: true
      group_by: 部门
```

---

## 6. 总结

### 6.1 核心特性

✅ **智能格式识别**: 自动检测5种复杂单据格式
✅ **灵活处理策略**: 支持多种处理模式和错误恢复
✅ **配置驱动**: 通过配置文件灵活调整处理行为
✅ **错误处理**: 完善的错误处理和恢复机制
✅ **扩展性**: 易于扩展新的格式和处理策略

### 6.2 技术亮点

- **模式识别算法**: 基于数据特征自动识别单据格式
- **智能数据填充**: 自动填充空值和关联数据
- **虚拟记录生成**: 为不完整数据创建虚拟记录
- **多策略处理**: 支持不同的处理策略和错误恢复

### 6.3 下一步行动

**Cursor的交付物** ✅:
- [x] 复杂单据格式处理算法设计（本文档）

**Lovable的实施任务** ⏳:
1. 实现智能格式识别器
2. 实现各种格式的处理器
3. 集成到现有ETL系统
4. 添加配置管理界面
5. 实现错误处理和恢复机制

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 1-2周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com
