# 复杂单据格式处理实施计划（更新版）

## 核心流程调整

### 正确的处理顺序

1. **解析源文件**
   - 读取Excel/CSV数据
   - 检测是否有列名（表头）
   - 如果没有列名，使用列索引（col_0, col_1, ...）或自动识别

2. **字段映射**（关键步骤，必须在识别之前完成）
   - 将源文件字段（可能是任意名称）映射到标准字段名
   - 支持用户手动配置映射
   - 支持自动智能映射（基于相似度匹配）
   - 如果源文件没有列名，使用位置索引映射

3. **应用字段映射**
   - 将数据列的列名改为标准字段名
   - 确保所有数据都使用标准字段名

4. **格式识别**
   - 基于标准字段名识别单据格式（格式1/2/3/4/5/6）

5. **单据头/明细字段识别**
   - 基于标准字段名识别单据头字段和明细字段

6. **数据处理**
   - 根据识别出的格式进行相应处理（前向填充、合并等）

## 需要更新的文档部分

### 1. 流程说明部分（新增）

在文档开头增加完整的处理流程说明，明确字段映射的位置。

### 2. 智能数据处理器更新

更新 `IntelligentDocumentProcessor.process_document()` 方法，增加字段映射步骤：

```python
def process_document(self, data: pd.DataFrame, field_mappings: Dict[str, str] = None, metadata: dict = None) -> ProcessResult:
    """处理单据数据"""
    # 1. 字段映射（必须在格式识别之前）
    if field_mappings:
        data = self.apply_field_mappings(data, field_mappings)
    elif metadata and 'field_mappings' in metadata:
        data = self.apply_field_mappings(data, metadata['field_mappings'])
    
    # 2. 检测格式（基于映射后的标准字段名）
    format_type = self.format_detector.detect_format(data, metadata)
    
    # 3. 选择处理器
    processor = self.processors.get(format_type)
    if not processor:
        raise ValueError(f"不支持的格式类型: {format_type}")
    
    # 4. 处理数据
    result = processor(data, metadata)
    
    return ProcessResult(...)

def apply_field_mappings(self, data: pd.DataFrame, field_mappings: Dict[str, str]) -> pd.DataFrame:
    """应用字段映射"""
    # 将源字段名映射到标准字段名
    mapped_data = data.rename(columns=field_mappings)
    return mapped_data
```

### 3. 字段识别方法更新

更新 `identify_header_fields()` 和 `identify_detail_fields()` 方法：
- 这些方法现在基于**已经映射后的标准字段名**工作
- 增加税务相关字段的模式匹配

### 4. 税务字段支持

在所有涉及金额字段的地方，增加：
- 不含税金额 (ex_tax_amount / amount_excluding_tax / 不含税)
- 税额 (tax_amount / tax)
- 价税合计 (total_amount_with_tax / amount_including_tax / 含税金额)
- 税率 (tax_rate / tax_rate_percent)

### 5. 无列名处理

增加处理无列名文件的逻辑：
- 使用列索引（col_0, col_1, ...）作为临时字段名
- 提供位置映射配置（第1列 → 单据号，第2列 → 单据日期等）
- 或通过数据内容自动推断列名

### 6. 字段映射示例

增加字段映射的详细示例：
- 源文件字段名 → 标准字段名
- 位置索引 → 标准字段名
- 自动映射建议

## 实施步骤

1. ✅ 更新文档流程说明
2. ✅ 更新智能数据处理器，增加字段映射步骤
3. ✅ 更新字段识别模式，增加税务字段
4. ✅ 更新格式示例，增加税务字段
5. ✅ 增加无列名文件处理说明
6. ✅ 增加字段映射示例和配置说明

## 文件路径

- `docs/data-import/COMPLEX_DOCUMENT_FORMAT_HANDLING.md`

