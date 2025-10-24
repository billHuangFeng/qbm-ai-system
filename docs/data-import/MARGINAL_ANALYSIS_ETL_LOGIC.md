# 边际影响分析系统 - ETL数据处理逻辑文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-10-23
- **负责人**: Cursor (算法设计与技术架构)
- **实施方**: Lovable (前端集成与UI实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 系统概述

### 1.1 目标
为边际影响分析系统设计完整的数据处理管道（ETL），确保从Excel模板导入的数据能够准确、高效地转换为系统可用的分析数据，支持：

- **数据清洗**: 处理缺失值、异常值、格式不一致等问题
- **数据验证**: 确保数据完整性和业务规则符合性
- **数据转换**: 将原始数据转换为分析所需的标准化格式
- **数据加载**: 安全、高效地存储到数据库
- **数据质量监控**: 实时监控数据质量，提供质量报告

### 1.2 核心价值
1. **数据质量保证**: 通过多层验证确保数据准确性
2. **处理效率**: 支持大批量数据快速处理
3. **错误处理**: 智能识别和修复常见数据问题
4. **可追溯性**: 完整的数据处理日志和审计轨迹
5. **扩展性**: 支持新的数据源和业务规则

### 1.3 技术特点
- **多格式支持**: Excel、CSV、JSON等格式
- **增量处理**: 支持增量数据更新
- **并行处理**: 多线程/多进程提升处理速度
- **容错机制**: 单条记录错误不影响整体处理
- **实时监控**: 处理进度和质量指标实时展示

---

## 2. ETL架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        数据源层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Excel    │  │ CSV     │  │ JSON     │  │ API      │   │
│  │ 模板     │  │ 文件    │  │ 数据     │  │ 接口     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │        数据提取层 (Extract)          │
        │  - 文件解析器 (Excel/CSV/JSON)      │
        │  - 数据格式检测                     │
        │  - 编码处理                        │
        │  - 分块读取                        │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │        数据转换层 (Transform)       │
        │  ┌────────────────────────────┐    │
        │  │ 1. 数据清洗 (Data Cleaning) │    │
        │  │    - 缺失值处理             │    │
        │  │    - 异常值检测             │    │
        │  │    - 格式标准化             │    │
        │  └──────────┬─────────────────┘    │
        │             ▼                       │
        │  ┌────────────────────────────┐    │
        │  │ 2. 数据验证 (Data Validation) │    │
        │  │    - 业务规则验证           │    │
        │  │    - 数据类型检查           │    │
        │  │    - 范围检查              │    │
        │  └──────────┬─────────────────┘    │
        │             ▼                       │
        │  ┌────────────────────────────┐    │
        │  │ 3. 数据转换 (Data Transform) │    │
        │  │    - 字段映射              │    │
        │  │    - 计算字段生成           │    │
        │  │    - 数据聚合              │    │
        │  └──────────┬─────────────────┘    │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │        数据加载层 (Load)           │
        │  - 批量插入优化                   │
        │  - 事务管理                       │
        │  - 冲突处理                       │
        │  - 索引更新                       │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │        数据质量监控层               │
        │  - 质量指标计算                    │
        │  - 异常报告生成                    │
        │  - 处理日志记录                    │
        │  - 性能监控                       │
        └────────────────────────────────────┘
```

### 2.2 数据流处理

#### 2.2.1 数据提取（Extract）

**支持的数据源**:
- Excel文件（.xlsx, .xls）
- CSV文件（UTF-8, GBK编码）
- JSON数据
- API接口数据
- 数据库查询结果

**提取策略**:
```python
class DataExtractor:
    """数据提取器"""
    
    def __init__(self, source_type: str):
        self.source_type = source_type
        self.parsers = {
            'excel': ExcelParser(),
            'csv': CSVParser(),
            'json': JSONParser(),
            'api': APIParser()
        }
    
    def extract(self, source: str, config: dict) -> pd.DataFrame:
        """提取数据"""
        parser = self.parsers[self.source_type]
        return parser.parse(source, config)
    
    def validate_format(self, data: pd.DataFrame) -> ValidationResult:
        """验证数据格式"""
        # 检查必需列
        required_columns = config.get('required_columns', [])
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            return ValidationResult(
                success=False,
                errors=[f"缺少必需列: {missing_columns}"]
            )
        
        return ValidationResult(success=True)
```

#### 2.2.2 数据转换（Transform）

**清洗规则**:
```python
class DataCleaner:
    """数据清洗器"""
    
    def clean_missing_values(self, data: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """处理缺失值"""
        if strategy == 'drop':
            return data.dropna()
        elif strategy == 'fill_mean':
            return data.fillna(data.mean())
        elif strategy == 'fill_median':
            return data.fillna(data.median())
        elif strategy == 'fill_forward':
            return data.fillna(method='ffill')
        else:
            return data
    
    def detect_outliers(self, data: pd.DataFrame, column: str) -> List[int]:
        """检测异常值（使用IQR方法）"""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
        return outliers.index.tolist()
    
    def standardize_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化格式"""
        # 统一日期格式
        date_columns = ['created_at', 'updated_at', 'analysis_month']
        for col in date_columns:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], errors='coerce')
        
        # 统一数值格式
        numeric_columns = ['npv_value', 'cash_flow', 'roi_score']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data
```

**验证规则**:
```python
class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.business_rules = {
            'asset_npv': {'min': 0, 'max': 10000000},
            'capability_score': {'min': 0, 'max': 100},
            'roi_score': {'min': 0, 'max': 10},
            'analysis_month': {'format': 'YYYY-MM'}
        }
    
    def validate_business_rules(self, data: pd.DataFrame) -> ValidationResult:
        """验证业务规则"""
        errors = []
        
        for column, rules in self.business_rules.items():
            if column in data.columns:
                # 范围检查
                if 'min' in rules:
                    invalid_min = data[data[column] < rules['min']]
                    if not invalid_min.empty:
                        errors.append(f"{column} 存在小于 {rules['min']} 的值")
                
                if 'max' in rules:
                    invalid_max = data[data[column] > rules['max']]
                    if not invalid_max.empty:
                        errors.append(f"{column} 存在大于 {rules['max']} 的值")
                
                # 格式检查
                if 'format' in rules:
                    if rules['format'] == 'YYYY-MM':
                        invalid_format = data[~data[column].str.match(r'^\d{4}-\d{2}$')]
                        if not invalid_format.empty:
                            errors.append(f"{column} 格式不正确，应为 YYYY-MM")
        
        return ValidationResult(
            success=len(errors) == 0,
            errors=errors
        )
    
    def validate_data_types(self, data: pd.DataFrame) -> ValidationResult:
        """验证数据类型"""
        errors = []
        
        # 检查数值列
        numeric_columns = ['npv_value', 'cash_flow', 'roi_score']
        for col in numeric_columns:
            if col in data.columns:
                non_numeric = data[~pd.to_numeric(data[col], errors='coerce').notna()]
                if not non_numeric.empty:
                    errors.append(f"{col} 包含非数值数据")
        
        return ValidationResult(
            success=len(errors) == 0,
            errors=errors
        )
```

**转换规则**:
```python
class DataTransformer:
    """数据转换器"""
    
    def map_columns(self, data: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        """字段映射"""
        return data.rename(columns=mapping)
    
    def calculate_derived_fields(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算衍生字段"""
        # 计算ROI
        if 'npv_value' in data.columns and 'investment' in data.columns:
            data['roi_score'] = data['npv_value'] / data['investment']
        
        # 计算效能指标
        if 'output_value' in data.columns and 'input_cost' in data.columns:
            data['efficiency_score'] = data['output_value'] / data['input_cost']
        
        return data
    
    def aggregate_data(self, data: pd.DataFrame, group_by: list, agg_functions: dict) -> pd.DataFrame:
        """数据聚合"""
        return data.groupby(group_by).agg(agg_functions).reset_index()
```

#### 2.2.3 数据加载（Load）

**批量插入策略**:
```python
class DataLoader:
    """数据加载器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.batch_size = 1000
    
    def load_in_batches(self, data: pd.DataFrame, table_name: str) -> LoadResult:
        """批量加载数据"""
        try:
            # 分批处理
            total_rows = len(data)
            success_count = 0
            error_count = 0
            errors = []
            
            for i in range(0, total_rows, self.batch_size):
                batch = data.iloc[i:i + self.batch_size]
                
                try:
                    # 插入数据
                    batch.to_sql(
                        table_name,
                        self.db,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                    success_count += len(batch)
                    
                except Exception as e:
                    error_count += len(batch)
                    errors.append(f"批次 {i//self.batch_size + 1}: {str(e)}")
            
            return LoadResult(
                success=error_count == 0,
                total_rows=total_rows,
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            return LoadResult(
                success=False,
                total_rows=len(data),
                success_count=0,
                error_count=len(data),
                errors=[str(e)]
            )
    
    def handle_conflicts(self, data: pd.DataFrame, table_name: str, conflict_resolution: str) -> LoadResult:
        """处理数据冲突"""
        if conflict_resolution == 'replace':
            # 先删除冲突数据，再插入新数据
            pass
        elif conflict_resolution == 'ignore':
            # 忽略冲突数据
            pass
        elif conflict_resolution == 'update':
            # 更新冲突数据
            pass
        
        return self.load_in_batches(data, table_name)
```

---

## 3. 数据质量监控

### 3.1 质量指标定义

```python
class DataQualityMetrics:
    """数据质量指标"""
    
    def __init__(self):
        self.metrics = {
            'completeness': 0.0,  # 完整性
            'accuracy': 0.0,      # 准确性
            'consistency': 0.0,   # 一致性
            'validity': 0.0,      # 有效性
            'timeliness': 0.0     # 及时性
        }
    
    def calculate_completeness(self, data: pd.DataFrame) -> float:
        """计算完整性指标"""
        total_cells = data.size
        non_null_cells = data.count().sum()
        return non_null_cells / total_cells if total_cells > 0 else 0.0
    
    def calculate_accuracy(self, data: pd.DataFrame, reference_data: pd.DataFrame = None) -> float:
        """计算准确性指标"""
        if reference_data is None:
            # 基于业务规则验证
            validator = DataValidator()
            validation_result = validator.validate_business_rules(data)
            return 1.0 if validation_result.success else 0.8
        
        # 与参考数据对比
        common_columns = set(data.columns) & set(reference_data.columns)
        if not common_columns:
            return 0.0
        
        accuracy_scores = []
        for col in common_columns:
            if data[col].dtype == reference_data[col].dtype:
                matches = (data[col] == reference_data[col]).sum()
                accuracy_scores.append(matches / len(data))
        
        return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
    
    def calculate_consistency(self, data: pd.DataFrame) -> float:
        """计算一致性指标"""
        # 检查数据格式一致性
        consistency_score = 1.0
        
        # 检查日期格式一致性
        date_columns = ['created_at', 'updated_at', 'analysis_month']
        for col in date_columns:
            if col in data.columns:
                try:
                    pd.to_datetime(data[col])
                except:
                    consistency_score -= 0.1
        
        # 检查数值格式一致性
        numeric_columns = ['npv_value', 'cash_flow', 'roi_score']
        for col in numeric_columns:
            if col in data.columns:
                try:
                    pd.to_numeric(data[col])
                except:
                    consistency_score -= 0.1
        
        return max(0.0, consistency_score)
    
    def generate_quality_report(self, data: pd.DataFrame) -> QualityReport:
        """生成质量报告"""
        self.metrics['completeness'] = self.calculate_completeness(data)
        self.metrics['accuracy'] = self.calculate_accuracy(data)
        self.metrics['consistency'] = self.calculate_consistency(data)
        
        # 计算总体质量分数
        overall_score = sum(self.metrics.values()) / len(self.metrics)
        
        # 生成建议
        recommendations = []
        if self.metrics['completeness'] < 0.9:
            recommendations.append("数据完整性不足，建议检查缺失值")
        if self.metrics['accuracy'] < 0.9:
            recommendations.append("数据准确性不足，建议验证业务规则")
        if self.metrics['consistency'] < 0.9:
            recommendations.append("数据一致性不足，建议统一格式")
        
        return QualityReport(
            overall_score=overall_score,
            metrics=self.metrics,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
```

### 3.2 异常检测和报告

```python
class AnomalyDetector:
    """异常检测器"""
    
    def detect_anomalies(self, data: pd.DataFrame) -> List[Anomaly]:
        """检测数据异常"""
        anomalies = []
        
        # 检测缺失值异常
        missing_anomalies = self.detect_missing_anomalies(data)
        anomalies.extend(missing_anomalies)
        
        # 检测数值异常
        numeric_anomalies = self.detect_numeric_anomalies(data)
        anomalies.extend(numeric_anomalies)
        
        # 检测格式异常
        format_anomalies = self.detect_format_anomalies(data)
        anomalies.extend(format_anomalies)
        
        return anomalies
    
    def detect_missing_anomalies(self, data: pd.DataFrame) -> List[Anomaly]:
        """检测缺失值异常"""
        anomalies = []
        
        for column in data.columns:
            missing_count = data[column].isna().sum()
            missing_rate = missing_count / len(data)
            
            if missing_rate > 0.1:  # 缺失率超过10%
                anomalies.append(Anomaly(
                    type='missing_data',
                    column=column,
                    severity='high' if missing_rate > 0.5 else 'medium',
                    description=f"列 {column} 缺失率 {missing_rate:.2%}",
                    affected_rows=missing_count
                ))
        
        return anomalies
    
    def detect_numeric_anomalies(self, data: pd.DataFrame) -> List[Anomaly]:
        """检测数值异常"""
        anomalies = []
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            # 检测异常值
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
            
            if len(outliers) > 0:
                anomalies.append(Anomaly(
                    type='outlier',
                    column=column,
                    severity='medium',
                    description=f"列 {column} 发现 {len(outliers)} 个异常值",
                    affected_rows=len(outliers)
                ))
        
        return anomalies
```

---

## 4. 性能优化

### 4.1 并行处理

```python
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ParallelETLProcessor:
    """并行ETL处理器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def process_files_parallel(self, file_paths: List[str]) -> List[ProcessingResult]:
        """并行处理多个文件"""
        with self.thread_pool as executor:
            futures = [executor.submit(self.process_single_file, path) for path in file_paths]
            results = [future.result() for future in futures]
        
        return results
    
    def process_single_file(self, file_path: str) -> ProcessingResult:
        """处理单个文件"""
        try:
            # 提取数据
            extractor = DataExtractor(self.get_file_type(file_path))
            data = extractor.extract(file_path)
            
            # 清洗数据
            cleaner = DataCleaner()
            cleaned_data = cleaner.clean_missing_values(data, strategy='fill_median')
            cleaned_data = cleaner.standardize_format(cleaned_data)
            
            # 验证数据
            validator = DataValidator()
            validation_result = validator.validate_business_rules(cleaned_data)
            
            if not validation_result.success:
                return ProcessingResult(
                    success=False,
                    file_path=file_path,
                    errors=validation_result.errors
                )
            
            # 转换数据
            transformer = DataTransformer()
            transformed_data = transformer.calculate_derived_fields(cleaned_data)
            
            return ProcessingResult(
                success=True,
                file_path=file_path,
                data=transformed_data,
                row_count=len(transformed_data)
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                file_path=file_path,
                errors=[str(e)]
            )
```

### 4.2 内存优化

```python
class MemoryOptimizedETL:
    """内存优化的ETL处理器"""
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
    
    def process_large_file(self, file_path: str) -> Generator[pd.DataFrame, None, None]:
        """分块处理大文件"""
        for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
            # 处理每个数据块
            processed_chunk = self.process_chunk(chunk)
            yield processed_chunk
    
    def process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """处理数据块"""
        # 清洗
        chunk = self.clean_chunk(chunk)
        
        # 验证
        chunk = self.validate_chunk(chunk)
        
        # 转换
        chunk = self.transform_chunk(chunk)
        
        return chunk
    
    def stream_to_database(self, file_path: str, table_name: str):
        """流式处理并直接写入数据库"""
        for chunk in self.process_large_file(file_path):
            # 直接写入数据库，不保存在内存中
            chunk.to_sql(
                table_name,
                self.db_connection,
                if_exists='append',
                index=False,
                method='multi'
            )
```

### 4.3 缓存策略

```python
import redis
import pickle
import hashlib

class ETLCache:
    """ETL缓存管理器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1小时
    
    def get_cache_key(self, file_path: str, config: dict) -> str:
        """生成缓存键"""
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        config_hash = hashlib.md5(str(config).encode()).hexdigest()
        return f"etl_cache:{file_hash}:{config_hash}"
    
    def get_cached_result(self, file_path: str, config: dict) -> Optional[ProcessingResult]:
        """获取缓存结果"""
        cache_key = self.get_cache_key(file_path, config)
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return pickle.loads(cached_data)
        return None
    
    def cache_result(self, file_path: str, config: dict, result: ProcessingResult):
        """缓存处理结果"""
        cache_key = self.get_cache_key(file_path, config)
        serialized_result = pickle.dumps(result)
        self.redis.setex(cache_key, self.cache_ttl, serialized_result)
```

---

## 5. 错误处理和恢复

### 5.1 错误分类和处理

```python
class ETLErrorHandler:
    """ETL错误处理器"""
    
    def __init__(self):
        self.error_handlers = {
            'file_not_found': self.handle_file_not_found,
            'format_error': self.handle_format_error,
            'validation_error': self.handle_validation_error,
            'database_error': self.handle_database_error,
            'memory_error': self.handle_memory_error
        }
    
    def handle_error(self, error: Exception, context: dict) -> ErrorHandlingResult:
        """处理错误"""
        error_type = self.classify_error(error)
        handler = self.error_handlers.get(error_type, self.handle_unknown_error)
        return handler(error, context)
    
    def classify_error(self, error: Exception) -> str:
        """分类错误类型"""
        if isinstance(error, FileNotFoundError):
            return 'file_not_found'
        elif isinstance(error, (ValueError, TypeError)):
            return 'format_error'
        elif isinstance(error, ValidationError):
            return 'validation_error'
        elif isinstance(error, (ConnectionError, IntegrityError)):
            return 'database_error'
        elif isinstance(error, MemoryError):
            return 'memory_error'
        else:
            return 'unknown'
    
    def handle_file_not_found(self, error: Exception, context: dict) -> ErrorHandlingResult:
        """处理文件未找到错误"""
        return ErrorHandlingResult(
            success=False,
            action='retry',
            retry_after=60,  # 60秒后重试
            message=f"文件未找到: {error.filename}",
            suggestions=["检查文件路径", "确认文件存在", "检查文件权限"]
        )
    
    def handle_format_error(self, error: Exception, context: dict) -> ErrorHandlingResult:
        """处理格式错误"""
        return ErrorHandlingResult(
            success=False,
            action='skip',
            message=f"数据格式错误: {str(error)}",
            suggestions=["检查数据格式", "使用数据清洗功能", "联系数据提供方"]
        )
    
    def handle_validation_error(self, error: Exception, context: dict) -> ErrorHandlingResult:
        """处理验证错误"""
        return ErrorHandlingResult(
            success=False,
            action='fix',
            message=f"数据验证失败: {str(error)}",
            suggestions=["检查业务规则", "修正数据值", "联系业务专家"]
        )
```

### 5.2 重试机制

```python
import time
from functools import wraps

class RetryMechanism:
    """重试机制"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def retry_on_failure(self, func):
        """重试装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < self.max_retries:
                        wait_time = self.backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        break
            
            raise last_exception
        
        return wrapper
    
    def retry_with_exponential_backoff(self, func, *args, **kwargs):
        """指数退避重试"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.backoff_factor ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
```

---

## 6. 监控和日志

### 6.1 处理监控

```python
class ETLMonitor:
    """ETL监控器"""
    
    def __init__(self):
        self.metrics = {
            'files_processed': 0,
            'rows_processed': 0,
            'errors_count': 0,
            'processing_time': 0.0,
            'success_rate': 0.0
        }
        self.start_time = None
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
    
    def update_metrics(self, files_processed: int = 0, rows_processed: int = 0, 
                       errors: int = 0):
        """更新指标"""
        self.metrics['files_processed'] += files_processed
        self.metrics['rows_processed'] += rows_processed
        self.metrics['errors_count'] += errors
        
        if self.start_time:
            self.metrics['processing_time'] = time.time() - self.start_time
        
        # 计算成功率
        total_operations = self.metrics['files_processed'] + self.metrics['errors_count']
        if total_operations > 0:
            self.metrics['success_rate'] = self.metrics['files_processed'] / total_operations
    
    def generate_report(self) -> MonitoringReport:
        """生成监控报告"""
        return MonitoringReport(
            metrics=self.metrics,
            timestamp=datetime.now(),
            status='completed' if self.metrics['errors_count'] == 0 else 'completed_with_errors'
        )
```

### 6.2 日志记录

```python
import logging
from logging.handlers import RotatingFileHandler

class ETLLogger:
    """ETL日志记录器"""
    
    def __init__(self, log_file: str = 'etl.log'):
        self.logger = logging.getLogger('ETL')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_file_processing(self, file_path: str, status: str, details: dict = None):
        """记录文件处理日志"""
        self.logger.info(f"处理文件: {file_path}, 状态: {status}")
        if details:
            self.logger.info(f"详细信息: {details}")
    
    def log_error(self, error: Exception, context: dict):
        """记录错误日志"""
        self.logger.error(f"ETL错误: {str(error)}")
        self.logger.error(f"上下文: {context}")
    
    def log_performance(self, operation: str, duration: float, records: int):
        """记录性能日志"""
        self.logger.info(f"操作: {operation}, 耗时: {duration:.2f}s, 记录数: {records}")
```

---

## 7. 配置管理

### 7.1 ETL配置

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ETLConfig:
    """ETL配置"""
    
    # 数据源配置
    source_type: str = 'excel'
    source_path: str = ''
    encoding: str = 'utf-8'
    
    # 处理配置
    chunk_size: int = 10000
    max_workers: int = 4
    batch_size: int = 1000
    
    # 清洗配置
    missing_value_strategy: str = 'fill_median'
    outlier_detection: bool = True
    outlier_threshold: float = 1.5
    
    # 验证配置
    validation_rules: Dict[str, Dict] = None
    strict_validation: bool = True
    
    # 输出配置
    target_table: str = ''
    conflict_resolution: str = 'replace'
    
    # 缓存配置
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    # 监控配置
    enable_monitoring: bool = True
    log_level: str = 'INFO'
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {
                'asset_npv': {'min': 0, 'max': 10000000},
                'capability_score': {'min': 0, 'max': 100},
                'roi_score': {'min': 0, 'max': 10}
            }
```

### 7.2 配置加载

```python
import yaml
import json

class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_from_yaml(file_path: str) -> ETLConfig:
        """从YAML文件加载配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return ETLConfig(**config_data)
    
    @staticmethod
    def load_from_json(file_path: str) -> ETLConfig:
        """从JSON文件加载配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return ETLConfig(**config_data)
    
    @staticmethod
    def load_from_env() -> ETLConfig:
        """从环境变量加载配置"""
        import os
        
        return ETLConfig(
            source_type=os.getenv('ETL_SOURCE_TYPE', 'excel'),
            source_path=os.getenv('ETL_SOURCE_PATH', ''),
            encoding=os.getenv('ETL_ENCODING', 'utf-8'),
            chunk_size=int(os.getenv('ETL_CHUNK_SIZE', '10000')),
            max_workers=int(os.getenv('ETL_MAX_WORKERS', '4')),
            batch_size=int(os.getenv('ETL_BATCH_SIZE', '1000'))
        )
```

---

## 8. 使用示例

### 8.1 基本使用

```python
# 基本ETL处理示例
def basic_etl_example():
    """基本ETL处理示例"""
    
    # 1. 加载配置
    config = ConfigLoader.load_from_yaml('etl_config.yaml')
    
    # 2. 创建ETL处理器
    etl_processor = ETLProcessor(config)
    
    # 3. 处理文件
    result = etl_processor.process_file('data/asset_data.xlsx')
    
    # 4. 检查结果
    if result.success:
        print(f"处理成功: {result.row_count} 行数据")
    else:
        print(f"处理失败: {result.errors}")
    
    return result

# 批量处理示例
def batch_etl_example():
    """批量ETL处理示例"""
    
    # 文件列表
    file_paths = [
        'data/assets_2024_01.xlsx',
        'data/assets_2024_02.xlsx',
        'data/assets_2024_03.xlsx'
    ]
    
    # 并行处理
    parallel_processor = ParallelETLProcessor(max_workers=4)
    results = parallel_processor.process_files_parallel(file_paths)
    
    # 汇总结果
    total_rows = sum(r.row_count for r in results if r.success)
    total_errors = sum(1 for r in results if not r.success)
    
    print(f"处理完成: {total_rows} 行数据, {total_errors} 个错误")
    
    return results
```

### 8.2 高级使用

```python
# 自定义ETL流程
def custom_etl_pipeline():
    """自定义ETL流程"""
    
    # 1. 数据提取
    extractor = DataExtractor('excel')
    raw_data = extractor.extract('data/raw_data.xlsx')
    
    # 2. 数据清洗
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_missing_values(raw_data, strategy='fill_forward')
    cleaned_data = cleaner.standardize_format(cleaned_data)
    
    # 3. 数据验证
    validator = DataValidator()
    validation_result = validator.validate_business_rules(cleaned_data)
    
    if not validation_result.success:
        print(f"验证失败: {validation_result.errors}")
        return
    
    # 4. 数据转换
    transformer = DataTransformer()
    transformed_data = transformer.calculate_derived_fields(cleaned_data)
    
    # 5. 数据加载
    loader = DataLoader(db_connection)
    load_result = loader.load_in_batches(transformed_data, 'asset_data')
    
    # 6. 质量监控
    quality_metrics = DataQualityMetrics()
    quality_report = quality_metrics.generate_quality_report(transformed_data)
    
    print(f"数据质量报告: {quality_report.overall_score:.2f}")
    
    return {
        'data': transformed_data,
        'quality_report': quality_report,
        'load_result': load_result
    }
```

---

## 9. 部署和运维

### 9.1 Docker部署

```dockerfile
# Dockerfile for ETL Service
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 设置环境变量
ENV ETL_CONFIG_PATH=/app/config/etl_config.yaml
ENV LOG_LEVEL=INFO

# 启动命令
CMD ["python", "-m", "etl.main"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  etl-service:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/qbm
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=qbm
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 9.2 监控配置

```python
# 监控配置
MONITORING_CONFIG = {
    'prometheus': {
        'enabled': True,
        'port': 9090,
        'metrics_path': '/metrics'
    },
    'grafana': {
        'enabled': True,
        'port': 3000,
        'dashboards': [
            'etl_performance.json',
            'data_quality.json',
            'error_rates.json'
        ]
    },
    'alerts': {
        'error_rate_threshold': 0.05,  # 5%错误率
        'processing_time_threshold': 3600,  # 1小时
        'quality_score_threshold': 0.8  # 80%质量分数
    }
}
```

---

## 10. 总结

### 10.1 核心特性

✅ **完整ETL流程**: 提取→转换→加载的完整数据处理管道
✅ **数据质量保证**: 多层验证确保数据准确性
✅ **性能优化**: 并行处理、内存优化、缓存策略
✅ **错误处理**: 智能错误分类和恢复机制
✅ **监控运维**: 完整的监控和日志系统
✅ **配置管理**: 灵活的配置系统支持不同环境

### 10.2 技术亮点

- **多格式支持**: Excel、CSV、JSON等格式统一处理
- **并行处理**: 多线程/多进程提升处理速度
- **内存优化**: 分块处理大文件，避免内存溢出
- **智能缓存**: Redis缓存提升重复处理效率
- **质量监控**: 实时数据质量指标和异常检测
- **容错机制**: 单条记录错误不影响整体处理

### 10.3 下一步行动

**Cursor的交付物** ✅:
- [x] ETL逻辑文档（本文档）

**Lovable的实施任务** ⏳:
1. 实现ETL处理服务（FastAPI）
2. 集成数据清洗和验证逻辑
3. 实现文件上传和批量处理UI
4. 添加数据质量监控仪表板
5. 实现错误处理和用户反馈机制

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 2-3周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com

