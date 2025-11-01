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

根据实际业务场景，系统需要处理以下6种复杂的单据格式。**注意**：所有格式示例都使用**标准字段名**，实际导入时需要先将源文件字段映射到标准字段名。

**格式优先级说明**：
- ✅ **常见格式**：格式1、格式2、格式4、格式6 - 优先支持和实现
- ⚠️ **特殊场景**：格式5 - 主要用于用户补充明细数据时
- ❌ **可忽略格式**：格式3 - 单据头和明细分离在不同表，场景较少，可忽略

#### **格式1: 多行明细对应重复单据头** ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
DOC001 | 2024-01-01 | 客户A | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
DOC002 | 2024-01-02 | 客户B | 产品3 | 8  | 100.00 | 800.00  | 104.00 | 904.00
```
**特点**：每行都包含完整的单据头信息和明细信息。  
**场景**：最常见的单据格式，ERP系统导出标准格式。

#### **格式2: 多行明细但只有第一行有单据头** ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
       |           |        | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
       |           |        | 产品3 | 3  | 100.00 | 300.00  | 39.00  | 339.00
DOC002 | 2024-01-02 | 客户B | 产品4 | 8  | 100.00 | 800.00  | 104.00 | 904.00
```
**特点**：第一行包含单据头信息，后续明细行的单据头字段为空，需要通过前向填充补全。  
**场景**：Excel表格常见的紧凑格式，减少重复信息。

#### **格式3: 单据头和明细分离在不同表** ❌ **可忽略格式**

```
单据头表:
单据号 | 单据日期 | 客户名称 | 不含税金额 | 税额 | 价税合计
DOC001 | 2024-01-01 | 客户A | 1800.00 | 234.00 | 2034.00

明细表:
单据号 | 产品名称 | 数量 | 单价 | 不含税金额 | 税额 | 价税合计
DOC001 | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
DOC001 | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
DOC001 | 产品3 | 3  | 100.00 | 300.00  | 39.00  | 339.00
```
**特点**：单据头和明细信息分别存储在不同工作表或文件中，需要通过关联字段（单据号）合并。  
**说明**：该格式在实际业务场景中较少出现，可以忽略。如果确实需要支持，可以通过分两次导入（先导入单据头，再导入明细）来实现。

#### **格式4: 只有单据头记录** ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 不含税金额 | 税额 | 价税合计 | 备注
DOC001 | 2024-01-01 | 客户A | 1800.00 | 234.00 | 2034.00 | 汇总单据
```
**特点**：只有单据头信息，没有明细。允许用户选择导入，后续可补充明细记录。  
**场景**：汇总单据、服务类单据、或用户选择导入汇总数据后补充明细。

#### **格式5: 只有明细记录** ⚠️ **特殊场景格式**

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
4. ✅ 允许用户参与决策过程，选择匹配结果

#### **格式6: 纯单据头记录（无明细）** ✅ **常见格式**

```
单据号 | 单据日期 | 客户名称 | 不含税金额 | 税额 | 价税合计 | 单据类型 | 备注
DOC001 | 2024-01-01 | 客户A | 1800.00 | 234.00 | 2034.00 | 服务费 | 咨询服务
DOC002 | 2024-01-02 | 客户B | 500.00  | 65.00  | 565.00  | 服务费 | 技术支持
DOC003 | 2024-01-03 | 客户C | 1200.00 | 156.00 | 1356.00 | 服务费 | 培训服务
```
**特点**：纯单据头记录，无明细，直接使用。  
**场景**：服务费、咨询费、培训费等无明细的服务类单据。每条记录都是独立的单据，不需要明细信息。

### 1.2 处理流程说明

**重要**：由于源文件字段名称可能与标准字段名不一致，甚至没有列名，处理流程必须遵循以下顺序：

1. **解析源文件** - 读取Excel/CSV数据，检测是否有列名
2. **字段映射**（关键步骤） - 将源文件字段映射到标准字段名
   - 如果源文件有列名：支持用户手动配置或自动智能映射
   - 如果源文件没有列名：使用列索引（col_0, col_1, ...）或位置映射
3. **字段映射验证** - 检测字段映射后的完整性
   - 检查单据头字段是否完整
   - 检查明细字段是否完整
   - **如果明细字段缺失，提示用户决策**：
     - **选项1：继续导入** - 作为只有单据头的格式4导入，后续可补充明细
     - **选项2：放弃导入** - 提示用户补充明细字段后重新导入
4. **应用字段映射** - 将数据列名改为标准字段名
5. **必填字段验证** - 检查必填字段的完整性
   - **严格必填字段**：必须从源文件严格获取，缺失则终止导入
   - **可补充必填字段**：可以通过补充策略或人工补充
6. **主数据ID匹配** - 通过源文件中的信息匹配系统主数据ID
   - 经营主体ID：通过经营主体名称、统一社会信用代码匹配
   - 往来单位ID：通过往来单位名称、统一社会信用代码匹配
   - 产品ID：通过产品名称+规格型号匹配
   - 计量单位ID：通过计量单位名称匹配
   - 税率ID：通过税率值或税率名称匹配
   - **员工ID**：通过员工姓名、员工工号、身份证号匹配
   - **汇率ID**：通过币种+汇率日期、汇率值匹配
   - **匹配失败或多个匹配时，提示用户决策**
7. **格式识别** - 基于标准字段名识别单据格式（如果用户选择继续且明细缺失，则强制识别为格式4或格式6）
8. **单据头/明细字段识别** - 基于标准字段名识别单据头和明细字段
9. **数据处理** - 根据识别出的格式进行相应处理（前向填充、合并等）

---

## 2. 智能单据格式识别算法

### 2.1 格式识别器设计

```python
class DocumentFormatDetector:
    """单据格式识别器"""
    
    def __init__(self):
        self.format_patterns = {
            'repeated_header': self.detect_repeated_header,      # 格式1：常见
            'first_row_header': self.detect_first_row_header,    # 格式2：常见
            'separated_tables': self.detect_separated_tables,    # 格式3：可忽略
            'header_only': self.detect_header_only,              # 格式4：常见
            'detail_only': self.detect_detail_only,             # 格式5：特殊场景（补充明细时）
            'pure_header': self.detect_pure_header               # 格式6：常见
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
        """检测分离表格式
        
        注意：此格式在实际业务场景中较少出现，可以忽略。
        如果确实需要支持，可以通过分两次导入（先导入单据头，再导入明细）来实现。
        """
        # 由于格式3可忽略，返回较低分数，避免误识别
        return 0.0
    
    def detect_header_only(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测只有单据头格式"""
        score = 0.0
        
        # 检查是否有汇总字段（包括税务相关字段）
        summary_cols = [
            '总金额', 'total_amount', '汇总', 'summary',
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax',
            '税额', 'tax_amount', 'tax',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax'
        ]
        for col in summary_cols:
            if col in data.columns:
                score += 0.4
                break
        
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
        
        # 检查是否有明细字段（包括税务相关字段）
        detail_cols = [
            '产品名称', 'product_name', '数量', 'quantity', 
            '金额', 'amount', '不含税金额', 'ex_tax_amount', 
            '税额', 'tax_amount', '价税合计', 'total_amount_with_tax'
        ]
        detail_count = sum(1 for col in data.columns 
                          if any(pattern.lower() in col.lower() for pattern in detail_cols))
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
    
    def detect_pure_header(self, data: pd.DataFrame, metadata: dict = None) -> float:
        """检测纯单据头格式（无明细）"""
        score = 0.0
        
        # 检查是否有单据头字段（包括税务相关字段）
        header_cols = [
            '单据号', 'document_id', '客户名称', 'customer_name',
            '总金额', 'total_amount',
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax',
            '税额', 'tax_amount', 'tax',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax'
        ]
        header_count = sum(1 for col in header_cols if any(pattern.lower() in col.lower() for pattern in [p.split()[0] for p in header_cols if ' ' not in p]))
        # 简化匹配逻辑
        header_count = sum(1 for col in data.columns 
                          if any(pattern.lower() in col.lower() 
                                for pattern in ['单据号', 'document_id', '客户名称', 'customer_name', 
                                               '总金额', 'total_amount', '不含税', 'ex_tax', 
                                               '税额', 'tax', '价税', 'total_amount_with_tax']))
        if header_count >= 3:
            score += 0.4
        
        # 检查是否有服务类型等纯头字段
        service_cols = ['单据类型', 'document_type', '服务类型', 'service_type']
        if any(col in data.columns for col in service_cols):
            score += 0.3
        
        # 检查是否没有明细字段
        detail_cols = ['产品名称', 'product_name', '数量', 'quantity']
        detail_count = sum(1 for col in detail_cols if col in data.columns)
        if detail_count == 0:
            score += 0.3
        
        # 检查行数是否较少（纯头记录通常不多）
        if len(data) < 100:
            score += 0.2
        
        return min(score, 1.0)
```

### 2.2 智能数据处理器

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ProcessResult:
    """处理结果"""
    format_type: str
    processed_data: Optional[pd.DataFrame]
    success: bool
    requires_user_decision: bool = False
    decision_message: Optional[str] = None
    missing_detail_fields: Optional[List[str]] = None
    error_message: Optional[str] = None
    validation_warnings: Optional[List[str]] = None

class IntelligentDocumentProcessor:
    """智能单据处理器"""
    
    def __init__(self):
        self.format_detector = DocumentFormatDetector()
        self.processors = {
            'repeated_header': self.process_repeated_header,      # 格式1：常见
            'first_row_header': self.process_first_row_header,    # 格式2：常见
            'separated_tables': self.process_separated_tables,    # 格式3：可忽略（可选实现）
            'header_only': self.process_header_only,              # 格式4：常见
            'detail_only': self.process_detail_only,             # 格式5：特殊场景（补充明细时）
            'pure_header': self.process_pure_header               # 格式6：常见
        }
    
    def process_document(self, data: pd.DataFrame, field_mappings: Dict[str, str] = None, metadata: dict = None) -> ProcessResult:
        """处理单据数据
        
        Args:
            data: 源数据DataFrame（可能使用源文件字段名）
            field_mappings: 字段映射字典 {源字段名: 标准字段名}
            metadata: 元数据，可能包含field_mappings和用户决策
            
        Returns:
            ProcessResult: 处理结果
        """
        # 1. 字段映射（关键步骤，必须在格式识别之前）
        #    注意：格式识别和字段识别都基于标准字段名
        if field_mappings:
            data = self.apply_field_mappings(data, field_mappings)
        elif metadata and 'field_mappings' in metadata:
            data = self.apply_field_mappings(data, metadata['field_mappings'])
        
        # 2. 字段映射验证 - 检查字段完整性
        validation_result = self.validate_field_mapping_completeness(data)
        
        # 3. 如果明细字段缺失，检查用户决策
        if not validation_result['detail_fields_complete']:
            # 检查用户是否已做出决策
            user_decision = metadata.get('user_decision') if metadata else None
            
            if user_decision is None:
                # 需要用户决策，返回提示信息
                return ProcessResult(
                    format_type='pending_user_decision',
                    processed_data=None,
                    success=False,
                    requires_user_decision=True,
                    decision_message='明细字段缺失，请选择：1) 继续导入（作为只有单据头的格式） 2) 放弃导入（补充明细字段后重新导入）',
                    missing_detail_fields=validation_result['missing_detail_fields']
                )
            
            elif user_decision == 'continue_without_details':
                # 用户选择继续导入，强制识别为只有单据头的格式
                metadata['force_format'] = 'header_only' if validation_result['header_fields_complete'] else 'pure_header'
            elif user_decision == 'abort':
                # 用户选择放弃导入
                return ProcessResult(
                    format_type='aborted_by_user',
                    processed_data=None,
                    success=False,
                    error_message='用户选择放弃导入，请补充明细字段后重新导入'
                )
        
        # 4. 检测格式（基于映射后的标准字段名）
        #    如果用户选择继续且明细缺失，强制使用header_only或pure_header格式
        if metadata and 'force_format' in metadata:
            format_type = metadata['force_format']
        else:
        format_type = self.format_detector.detect_format(data, metadata)
        
        # 5. 选择处理器
        processor = self.processors.get(format_type)
        if not processor:
            raise ValueError(f"不支持的格式类型: {format_type}")
        
        # 6. 处理数据
        result = processor(data, metadata)
        
        # 7. 必填字段验证
        field_config = metadata.get('field_config', {}) if metadata else {}
        required_field_validation = self.validate_required_fields(result, field_config)
        
        # 如果严格必填字段缺失，直接返回错误
        if not required_field_validation['valid']:
            return ProcessResult(
                format_type=format_type,
                processed_data=None,
                success=False,
                error_message=f"严格必填字段缺失: {required_field_validation['strict_required_errors']}"
            )
        
        # 8. 主数据ID匹配
        master_data_config = metadata.get('master_data_config', {}) if metadata else {}
        db_connection = metadata.get('db_connection') if metadata else None
        
        master_data_match_result = self.match_master_data_ids(
            result, master_data_config, db_connection
        )
        
        # 如果主数据匹配需要用户决策
        if master_data_match_result['requires_user_decision']:
            return ProcessResult(
                format_type=format_type,
                processed_data=None,
                success=False,
                requires_user_decision=True,
                decision_message='主数据匹配需要用户决策',
                unmatched_records=master_data_match_result['unmatched_records'],
                multiple_matches=master_data_match_result['multiple_matches']
            )
        
        # 更新数据中的主数据ID
        if master_data_match_result['data'] is not None:
            result = master_data_match_result['data']
        
        # 9. 验证金额字段一致性（如果存在税务字段）
        if result is not None:
            amount_validation = self.validate_amount_fields(result)
            if not amount_validation['valid']:
                logger.warning(f"金额字段验证失败: {amount_validation['errors']}")
        
        return ProcessResult(
            format_type=format_type,
            processed_data=result,
            success=True,
            validation_warnings=validation_result.get('warnings', []),
            supplementable_missing_fields=required_field_validation.get('supplementable_missing', [])
        )
    
    def validate_field_mapping_completeness(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证字段映射后的完整性
        
        检查单据头字段和明细字段是否完整。
        
        Returns:
            验证结果字典，包含：
            - header_fields_complete: 单据头字段是否完整
            - detail_fields_complete: 明细字段是否完整
            - missing_header_fields: 缺失的单据头字段列表
            - missing_detail_fields: 缺失的明细字段列表
            - warnings: 警告信息列表
        """
        # 定义必需的单据头字段
        required_header_fields = [
            '单据号', 'document_id',  # 至少需要一个单据标识字段
        ]
        
        # 定义必需的明细字段（至少需要一个）
        required_detail_fields = [
            '产品名称', 'product_name',  # 产品或物料标识
            '数量', 'quantity',          # 数量
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax',  # 金额字段（至少一个）
            '金额', 'amount',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax'
        ]
        
        # 检查单据头字段
        header_fields = self.identify_header_fields(data)
        header_fields_complete = any(
            any(pattern.lower() in field.lower() for pattern in ['单据号', 'document_id', '单号'])
            for field in data.columns
        )
        
        missing_header_fields = []
        if not header_fields_complete:
            missing_header_fields = ['单据号']  # 单据号是必需的
        
        # 检查明细字段
        detail_fields = self.identify_detail_fields(data)
        # 至少需要一个明细字段
        detail_fields_complete = len(detail_fields) > 0
        
        missing_detail_fields = []
        if not detail_fields_complete:
            missing_detail_fields = ['产品名称', '数量', '不含税金额']  # 示例缺失字段
        
        warnings = []
        if not header_fields_complete:
            warnings.append('单据头字段不完整，缺少单据标识字段')
        if not detail_fields_complete:
            warnings.append('明细字段不完整，缺少产品、数量或金额字段')
        
        return {
            'header_fields_complete': header_fields_complete,
            'detail_fields_complete': detail_fields_complete,
            'missing_header_fields': missing_header_fields,
            'missing_detail_fields': missing_detail_fields,
            'warnings': warnings,
            'identified_header_fields': header_fields,
            'identified_detail_fields': detail_fields
        }
    
    def apply_field_mappings(self, data: pd.DataFrame, field_mappings: Dict[str, str]) -> pd.DataFrame:
        """应用字段映射
        
        将源文件字段名映射到标准字段名。
        如果源文件没有列名（使用col_0, col_1等），需要通过位置映射。
        
        Args:
            data: 源数据DataFrame
            field_mappings: 字段映射字典 {源字段名: 标准字段名}
            
        Returns:
            映射后的DataFrame（使用标准字段名）
        """
        mapped_data = data.copy()
        
        # 应用字段映射
        mapped_data = mapped_data.rename(columns=field_mappings)
        
        return mapped_data
    
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
        """处理分离表格式
        
        注意：格式3（分离表格式）在实际业务场景中较少出现，可以忽略。
        如果确实需要支持，可以通过分两次导入（先导入单据头，再导入明细）来实现。
        这里保留方法以保持接口完整性，但建议不实现或简单实现。
        """
        # 可选实现：如果需要支持，可以通过元数据中的header_data合并
        if not metadata or 'header_data' not in metadata:
            # 如果没有头表数据，建议用户分两次导入
            raise ValueError(
                "分离表格式需要提供头表数据。"
                "建议：先导入单据头数据（格式4），再导入明细数据（格式5）进行补充。"
            )
        
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
        """处理只有明细格式（格式5：补充明细场景）
        
        注意：格式5主要用于用户补充明细数据时。
        当系统中已存在单据头记录（可能之前通过格式4导入），现在需要补充对应的明细行数据。
        
        处理流程：
        1. 通过明细记录中的"单据号"字段，在数据库中查找已存在的单据头记录ID
        2. 如果找到匹配的单据头记录，将明细记录与单据头ID关联
        3. 如果未找到匹配或找到多个匹配，需要用户决策
        
        Args:
            data: 明细数据DataFrame，必须包含"单据号"字段
            metadata: 元数据，可包含：
                - db_connection: 数据库连接（用于查询单据头记录）
                - document_type: 单据类型（如"purchase_order"）
                - user_decisions: 用户决策结果（如果有）
        
        Returns:
            处理后的DataFrame，包含单据头ID字段（document_header_id）
        """
        processed_data = data.copy()
        
        # 检查是否包含单据号字段
        document_number_fields = ['单据号', 'document_number', 'document_id', '单号']
        document_number_field = None
        for field in document_number_fields:
            if field in data.columns:
                document_number_field = field
                break
        
        if not document_number_field:
            raise ValueError(
                "格式5（只有明细记录）必须包含单据号字段，"
                "用于匹配系统中已存在的单据头记录。"
                "请检查字段映射是否正确。"
            )
        
        # 提取所有唯一的单据号
        unique_document_numbers = data[document_number_field].dropna().unique()
        
        # 在数据库中查找单据头记录ID
        if metadata and metadata.get('db_connection'):
            db_connection = metadata['db_connection']
            document_type = metadata.get('document_type', 'purchase_order')
            
            # 查询单据头记录（通过单据号匹配）
            header_matches = self._match_document_headers(
                unique_document_numbers,
                document_type,
                db_connection
            )
            
            # 应用匹配结果
            processed_data['document_header_id'] = processed_data[document_number_field].map(
                lambda dn: header_matches.get(dn, {}).get('header_id') if pd.notna(dn) else None
            )
            
            # 记录匹配状态
            matched_count = processed_data['document_header_id'].notna().sum()
            unmatched_count = processed_data['document_header_id'].isna().sum()
            
            # 如果有未匹配的记录，需要用户决策
            if unmatched_count > 0:
                unmatched_document_numbers = processed_data[
                    processed_data['document_header_id'].isna()
                ][document_number_field].unique()
                
                # 返回需要用户决策的信息
                if 'user_decisions' not in metadata or not metadata['user_decisions']:
                    raise ValueError(
                        f"发现 {unmatched_count} 条明细记录无法匹配到单据头："
                        f"{unmatched_document_numbers.tolist()}。"
                        f"需要用户决策：选择匹配、创建新单据头、或废弃记录。"
                    )
            
            # 应用用户决策（如果有）
            if metadata.get('user_decisions'):
                processed_data = self._apply_user_decisions(
                    processed_data,
                    metadata['user_decisions'],
                    'document_header'
                )
        
        else:
            # 如果没有数据库连接，提示需要匹配
            raise ValueError(
                "格式5处理需要数据库连接来匹配单据头记录ID。"
                "请在metadata中提供db_connection。"
            )
        
        return processed_data
    
    def _match_document_headers(
        self,
        document_numbers: list,
        document_type: str,
        db_connection
    ) -> dict:
        """匹配单据头记录ID
        
        通过单据号在数据库中查找已存在的单据头记录ID。
        
        Args:
            document_numbers: 单据号列表
            document_type: 单据类型（如"purchase_order"）
            db_connection: 数据库连接
        
        Returns:
            匹配结果字典：{单据号: {'header_id': id, 'found': bool, 'confidence': float}}
        """
        matches = {}
        
        # 确定单据头表名（根据单据类型）
        header_table_map = {
            'purchase_order': 'doc_purchase_order_header',
            'sales_order': 'doc_sales_order_header',
            # 添加其他单据类型...
        }
        header_table = header_table_map.get(document_type)
        
        if not header_table:
            raise ValueError(f"不支持的单据类型: {document_type}")
        
        # 批量查询单据头记录
        # 实际实现应该使用SQL查询，这里为伪代码
        for doc_number in document_numbers:
            if pd.isna(doc_number):
                continue
            
            # SQL查询（示例）
            # SELECT id, document_number, document_date, customer_name
            # FROM {header_table}
            # WHERE document_number = %s
            # LIMIT 1
            
            # 这里假设查询返回结果
            query_result = self._query_document_header(db_connection, header_table, doc_number)
            
            if query_result:
                matches[doc_number] = {
                    'header_id': query_result['id'],
                    'header_info': query_result,
                    'found': True,
                    'confidence': 1.0  # 单据号精确匹配，置信度为1.0
                }
            else:
                matches[doc_number] = {
                    'header_id': None,
                    'header_info': None,
                    'found': False,
                    'confidence': 0.0,
                    'message': f"系统中未找到单据号 {doc_number} 的单据头记录"
                }
        
        return matches
    
    def _query_document_header(self, db_connection, table_name: str, document_number: str) -> dict:
        """查询单据头记录（需要实际实现）"""
        # 实际实现应该使用数据库查询
        # 这里返回None表示未找到，实际应该查询数据库
        return None
    
    def process_pure_header(self, data: pd.DataFrame, metadata: dict = None) -> pd.DataFrame:
        """处理纯单据头格式（无明细）"""
        # 纯单据头记录直接使用，不需要创建明细
        processed_data = data.copy()
        
        # 添加标记字段表示这是纯头记录
        processed_data['record_type'] = 'header_only'
        processed_data['has_details'] = False
        
        return processed_data
    
    def identify_header_fields(self, data: pd.DataFrame) -> list:
        """识别单据头字段
        
        注意：此方法基于已经映射后的标准字段名工作。
        在调用此方法之前，必须完成字段映射步骤。
        
        Returns:
            单据头字段列表
        """
        header_patterns = [
            # 单据基本信息
            '单据号', 'document_id', '单号',
            '单据日期', 'document_date', '日期',
            '客户名称', 'customer_name', '客户',
            # 金额字段（支持税务相关字段）
            '总金额', 'total_amount', '金额',
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax', '不含税',
            '税额', 'tax_amount', 'tax',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax', '含税金额'
        ]
        
        return [col for col in data.columns if any(pattern.lower() in col.lower() for pattern in header_patterns)]
    
    def identify_detail_fields(self, data: pd.DataFrame) -> list:
        """识别明细字段
        
        注意：此方法基于已经映射后的标准字段名工作。
        在调用此方法之前，必须完成字段映射步骤。
        
        Returns:
            明细字段列表
        """
        detail_patterns = [
            # 产品信息
            '产品名称', 'product_name', '产品',
            # 数量信息
            '数量', 'quantity', 'qty',
            # 价格信息
            '单价', 'unit_price', '价格',
            # 金额字段（支持税务相关字段）
            '金额', 'amount', '小计',
            '不含税金额', 'ex_tax_amount', 'amount_excluding_tax', '不含税',
            '税额', 'tax_amount', 'tax',
            '价税合计', 'total_amount_with_tax', 'amount_including_tax', '含税金额',
            # 税率信息
            '税率', 'tax_rate', 'tax_rate_percent'
        ]
        
        return [col for col in data.columns if any(pattern.lower() in col.lower() for pattern in detail_patterns)]
    
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
    
    def validate_amount_fields(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证金额字段的一致性
        
        检查价税合计 = 不含税金额 + 税额
        
        Returns:
            验证结果字典，包含valid、errors、warnings
        """
        errors = []
        warnings = []
        
        # 检查价税合计 = 不含税金额 + 税额
        # 支持多种字段名变体
        total_col = None
        ex_tax_col = None
        tax_col = None
        
        # 查找价税合计列
        for col in data.columns:
            if any(pattern in col.lower() for pattern in ['价税合计', 'total_amount_with_tax', 'amount_including_tax', '含税金额']):
                total_col = col
                break
        
        # 查找不含税金额列
        for col in data.columns:
            if any(pattern in col.lower() for pattern in ['不含税金额', 'ex_tax_amount', 'amount_excluding_tax', '不含税']):
                ex_tax_col = col
                break
        
        # 查找税额列
        for col in data.columns:
            if any(pattern in col.lower() for pattern in ['税额', 'tax_amount', 'tax']):
                tax_col = col
                break
        
        # 如果所有三个字段都存在，进行验证
        if total_col and ex_tax_col and tax_col:
            for idx, row in data.iterrows():
                calculated_total = (
                    (row.get(ex_tax_col, 0) or 0) + 
                    (row.get(tax_col, 0) or 0)
                )
                actual_total = row.get(total_col, 0) or 0
                
                # 允许0.01的误差（四舍五入误差）
                if abs(calculated_total - actual_total) > 0.01:
                    errors.append({
                        'row': idx,
                        'field': total_col,
                        'issue': f'价税合计({actual_total}) 不等于 不含税金额({row.get(ex_tax_col, 0)}) + 税额({row.get(tax_col, 0)})',
                        'calculated': calculated_total,
                        'actual': actual_total
                    })
        
        # 如果只有部分字段，给出警告
        if (total_col or ex_tax_col or tax_col) and not (total_col and ex_tax_col and tax_col):
            warnings.append('金额字段不完整，无法进行一致性验证')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def create_virtual_details(self, header_data: pd.DataFrame) -> pd.DataFrame:
        """为头表创建虚拟明细
        
        当只有单据头信息时，创建一条虚拟明细记录。
        优先使用价税合计，如果没有则使用总金额。
        """
        virtual_details = []
        
        for _, row in header_data.iterrows():
            # 优先使用价税合计，其次总金额，最后计算
            total_amount = (
                row.get('价税合计', None) or 
                row.get('total_amount_with_tax', None) or
                row.get('总金额', None) or
                row.get('total_amount', None) or
                0
            )
            
            # 如果不含税金额和税额都存在，使用它们；否则使用总金额作为不含税金额
            ex_tax_amount = (
                row.get('不含税金额', None) or
                row.get('ex_tax_amount', None) or
                row.get('amount_excluding_tax', None) or
                total_amount
            )
            
            tax_amount = (
                row.get('税额', None) or
                row.get('tax_amount', None) or
                0
            )
            
            # 创建一条虚拟明细记录
            virtual_detail = {
                '单据号': row.get('单据号', '') or row.get('document_id', ''),
                '产品名称': '汇总项目',
                '数量': 1,
                '金额': total_amount,
                '不含税金额': ex_tax_amount,
                '税额': tax_amount,
                '价税合计': total_amount,
                '备注': '汇总记录'
            }
            virtual_details.append(virtual_detail)
        
        return pd.DataFrame(virtual_details)
    
    def create_virtual_header(self, detail_data: pd.DataFrame) -> pd.DataFrame:
        """为明细表创建虚拟单据头
        
        当只有明细信息时，创建虚拟单据头。
        汇总明细的金额字段（优先价税合计，其次不含税金额+税额，最后金额）。
        """
        # 按部门或其他分组字段创建虚拟单据头
        if '部门' in detail_data.columns:
            grouped = detail_data.groupby('部门')
        else:
            # 如果没有分组字段，创建单个虚拟头
            grouped = [(None, detail_data)]
        
        virtual_headers = []
        
        for group_name, group_data in grouped:
            # 优先汇总价税合计
            if '价税合计' in group_data.columns:
                total_amount = group_data['价税合计'].sum()
            elif 'total_amount_with_tax' in group_data.columns:
                total_amount = group_data['total_amount_with_tax'].sum()
            # 其次汇总不含税金额+税额
            elif '不含税金额' in group_data.columns and '税额' in group_data.columns:
                total_amount = group_data['不含税金额'].sum() + group_data['税额'].sum()
            elif 'ex_tax_amount' in group_data.columns and 'tax_amount' in group_data.columns:
                total_amount = group_data['ex_tax_amount'].sum() + group_data['tax_amount'].sum()
            # 最后汇总金额
            elif '金额' in group_data.columns:
                total_amount = group_data['金额'].sum()
            elif 'amount' in group_data.columns:
                total_amount = group_data['amount'].sum()
            else:
                total_amount = 0
            
            # 汇总不含税金额和税额
            ex_tax_amount = (
                group_data['不含税金额'].sum() if '不含税金额' in group_data.columns else
                group_data['ex_tax_amount'].sum() if 'ex_tax_amount' in group_data.columns else
                total_amount
            )
            
            tax_amount = (
                group_data['税额'].sum() if '税额' in group_data.columns else
                group_data['tax_amount'].sum() if 'tax_amount' in group_data.columns else
                0
            )
            
            virtual_header = {
                '单据号': f"VIRTUAL_{group_name or 'DEFAULT'}_{len(virtual_headers) + 1}",
                '单据日期': pd.Timestamp.now().strftime('%Y-%m-%d'),
                '客户名称': f"虚拟客户_{group_name or 'DEFAULT'}",
                '不含税金额': ex_tax_amount,
                '税额': tax_amount,
                '价税合计': total_amount,
                '总金额': total_amount,  # 保持兼容性
                '备注': f"虚拟单据头_{group_name or 'DEFAULT'}"
            }
            virtual_headers.append(virtual_header)
        
        return pd.DataFrame(virtual_headers)
    
    def validate_required_fields(self, data: pd.DataFrame, field_config: Dict[str, Any]) -> Dict[str, Any]:
        """验证必填字段
        
        Args:
            data: 处理后的数据DataFrame
            field_config: 字段配置，包含必填字段定义
            
        Returns:
            验证结果字典，包含：
            - strict_required_errors: 严格必填字段缺失错误
            - supplementable_missing: 可补充必填字段缺失列表
            - requires_user_decision: 是否需要用户决策
        """
        strict_required_fields = field_config.get('strict_required_fields', [])
        supplementable_required_fields = field_config.get('supplementable_required_fields', [])
        
        strict_required_errors = []
        supplementable_missing = []
        
        # 检查严格必填字段
        for field in strict_required_fields:
            field_name = field.get('name')
            check_columns = field.get('columns', [field_name])
            
            # 检查是否至少有一个列存在且有值
            has_value = False
            for col in check_columns:
                if col in data.columns and data[col].notna().any():
                    has_value = True
                    break
            
            if not has_value:
                strict_required_errors.append({
                    'field': field_name,
                    'message': f'严格必填字段 {field_name} 缺失或为空，无法继续导入'
                })
        
        # 检查可补充必填字段
        for field in supplementable_required_fields:
            field_name = field.get('name')
            check_columns = field.get('columns', [field_name])
            supplement_strategy = field.get('supplement_strategy', 'manual')
            
            # 检查是否至少有一个列存在且有值
            has_value = False
            for col in check_columns:
                if col in data.columns and data[col].notna().any():
                    has_value = True
                    break
            
            if not has_value:
                supplementable_missing.append({
                    'field': field_name,
                    'supplement_strategy': supplement_strategy,
                    'columns': check_columns
                })
        
        return {
            'valid': len(strict_required_errors) == 0,
            'strict_required_errors': strict_required_errors,
            'supplementable_missing': supplementable_missing,
            'requires_user_decision': len(supplementable_missing) > 0
        }
    
    def match_master_data_ids(self, data: pd.DataFrame, master_data_config: Dict[str, Any], db_connection=None) -> Dict[str, Any]:
        """匹配主数据ID
        
        通过源文件中的信息（名称、代码等）匹配系统主数据ID。
        
        Args:
            data: 处理后的数据DataFrame
            master_data_config: 主数据匹配配置
            db_connection: 数据库连接（用于查询主数据）
            
        Returns:
            匹配结果字典，包含：
            - matched_ids: 成功匹配的主数据ID字典
            - unmatched_records: 未匹配的记录列表
            - multiple_matches: 多个匹配的记录列表（需要用户选择）
            - requires_user_decision: 是否需要用户决策
        """
        matched_ids = {}
        unmatched_records = []
        multiple_matches = []
        
        # 主数据匹配规则
        master_data_rules = master_data_config.get('matching_rules', {
            'business_entity': {
                'id_field': '经营主体id',
                'match_fields': [
                    {'field': '经营主体名称', 'table': 'dim_business_entity', 'column': 'entity_name'},
                    {'field': '统一社会信用代码', 'table': 'dim_business_entity', 'column': 'credit_code'}
                ],
                'priority': ['统一社会信用代码', '经营主体名称']
            },
            'counterparty': {
                'id_field': '往来单位id',
                'match_fields': [
                    {'field': '往来单位名称', 'table': 'dim_counterparty', 'column': 'counterparty_name'},
                    {'field': '统一社会信用代码', 'table': 'dim_counterparty', 'column': 'credit_code'}
                ],
                'priority': ['统一社会信用代码', '往来单位名称']
            },
            'product': {
                'id_field': '产品id',
                'match_fields': [
                    {'field': '产品名称', 'table': 'dim_product', 'column': 'product_name'},
                    {'field': '规格型号', 'table': 'dim_product', 'column': 'specification'}
                ],
                'match_type': 'combined',  # 需要同时匹配产品名称和规格型号
                'priority': ['产品名称', '规格型号']
            },
            'unit': {
                'id_field': '计量单位id',
                'match_fields': [
                    {'field': '计量单位名称', 'table': 'dim_unit', 'column': 'unit_name'}
                ],
                'priority': ['计量单位名称']
            },
            'tax_rate': {
                'id_field': '税率id',
                'match_fields': [
                    {'field': '税率', 'table': 'dim_tax_rate', 'column': 'tax_rate_value'},
                    {'field': '税率名称', 'table': 'dim_tax_rate', 'column': 'tax_rate_name'}
                ],
                'priority': ['税率', '税率名称']
            },
            'employee': {
                'id_field': '员工id',
                'match_fields': [
                    {'field': '员工姓名', 'table': 'dim_employee', 'column': 'employee_name'},
                    {'field': '员工工号', 'table': 'dim_employee', 'column': 'employee_code'},
                    {'field': '身份证号', 'table': 'dim_employee', 'column': 'id_card'}
                ],
                'priority': ['员工工号', '身份证号', '员工姓名']
            },
            'exchange_rate': {
                'id_field': '汇率id',
                'match_fields': [
                    {'field': '币种', 'table': 'dim_exchange_rate', 'column': 'currency_code'},
                    {'field': '汇率日期', 'table': 'dim_exchange_rate', 'column': 'rate_date'},
                    {'field': '汇率值', 'table': 'dim_exchange_rate', 'column': 'rate_value'}
                ],
                'match_type': 'combined',  # 需要同时匹配币种和日期
                'priority': ['币种', '汇率日期', '汇率值']
            }
        })
        
        # 为每个主数据类型进行匹配
        for master_type, rule in master_data_rules.items():
            id_field = rule['id_field']
            match_fields = rule['match_fields']
            priority = rule.get('priority', [])
            match_type = rule.get('match_type', 'single')  # single 或 combined
            
            # 在数据中添加ID列（初始为空）
            if id_field not in data.columns:
                data[id_field] = None
            
            # 遍历每一行数据进行匹配
            for idx, row in data.iterrows():
                match_results = []
                
                # 按优先级尝试匹配
                for priority_field in priority:
                    # 找到对应的匹配字段配置
                    match_field_config = next(
                        (mf for mf in match_fields if mf['field'] == priority_field),
                        None
                    )
                    
                    if not match_field_config:
                        continue
                    
                    # 检查源数据中是否有该字段
                    source_field = match_field_config['field']
                    if source_field not in data.columns:
                        continue
                    
                    source_value = row.get(source_field)
                    if pd.isna(source_value) or not source_value:
                        continue
                    
                    # 执行匹配查询
                    if match_type == 'combined':
                        # 组合匹配：需要同时匹配多个字段
                        match_result = self._match_combined_fields(
                            row, match_fields, rule, db_connection
                        )
                    else:
                        # 单字段匹配
                        match_result = self._match_single_field(
                            source_value,
                            match_field_config,
                            db_connection
                        )
                    
                    if match_result:
                        match_results.append({
                            **match_result,
                            'match_field': priority_field,
                            'confidence': self._calculate_confidence(match_result, priority_field)
                        })
                
                # 处理匹配结果
                if len(match_results) == 0:
                    # 未找到匹配，需要用户决策
                    if 'user_decisions' in metadata and metadata['user_decisions']:
                        decision = self._get_user_decision(
                            idx, master_type, row, metadata['user_decisions']
                        )
                        if decision and decision['action'] == 'select':
                            data.at[idx, id_field] = decision['selected_id']
                        elif decision and decision['action'] == 'create_new':
                            # 创建新记录的逻辑（需要实际实现）
                            new_id = self._create_new_master_data(master_type, row, db_connection)
                            data.at[idx, id_field] = new_id
                        elif decision and decision['action'] == 'skip':
                            # 跳过该记录
                            data.at[idx, id_field] = None
                            continue
                    else:
                        # 需要用户决策，但还没有决策结果
                        raise ValueError(
                            f"行 {idx} 的主数据 {master_type} 未找到匹配记录，需要用户决策："
                            f"选择匹配、创建新记录、或废弃该记录。"
                        )
                elif len(match_results) == 1:
                    # 唯一匹配，直接使用
                    match_result = match_results[0]
                    if match_result['confidence'] >= threshold:
                        data.at[idx, id_field] = match_result['id']
                    else:
                        # 置信度低，需要用户决策
                        if 'user_decisions' in metadata and metadata['user_decisions']:
                            decision = self._get_user_decision(
                                idx, master_type, row, metadata['user_decisions'],
                                candidates=[match_result]
                            )
                            if decision and decision['action'] == 'select':
                                data.at[idx, id_field] = decision['selected_id']
                            elif decision and decision['action'] == 'skip':
                                data.at[idx, id_field] = None
                                continue
                        else:
                            raise ValueError(
                                f"行 {idx} 的主数据 {master_type} 匹配置信度低 ({match_result['confidence']:.2f})，"
                                f"需要用户决策。"
                            )
                else:
                    # 多个匹配结果，需要用户选择
                    if 'user_decisions' in metadata and metadata['user_decisions']:
                        decision = self._get_user_decision(
                            idx, master_type, row, metadata['user_decisions'],
                            candidates=match_results
                        )
                        if decision and decision['action'] == 'select':
                            data.at[idx, id_field] = decision['selected_id']
                        elif decision and decision['action'] == 'create_new':
                            new_id = self._create_new_master_data(master_type, row, db_connection)
                            data.at[idx, id_field] = new_id
                        elif decision and decision['action'] == 'skip':
                            data.at[idx, id_field] = None
                            continue
                    else:
                        # 需要用户决策，但还没有决策结果
                        raise ValueError(
                            f"行 {idx} 的主数据 {master_type} 找到多个匹配候选，需要用户选择："
                            f"{[m['id'] for m in match_results]}。"
                        )
    
    def _match_combined_fields(
        self,
        row: pd.Series,
        match_fields: list,
        rule: dict,
        db_connection
                        )
                    else:
                        # 单字段匹配
                        match_result = self._match_single_field(
                            source_value, match_field_config, db_connection
                        )
                    
                    if match_result:
                        match_results.append({
                            'field': source_field,
                            'value': source_value,
                            'matches': match_result
                        })
                        
                        # 如果优先级字段匹配成功且唯一，直接使用
                        if len(match_result) == 1:
                            data.at[idx, id_field] = match_result[0]['id']
                            matched_ids[f"{master_type}_{idx}"] = match_result[0]['id']
                            break
                
                # 如果所有优先级字段都没有唯一匹配
                if data.at[idx, id_field] is None or pd.isna(data.at[idx, id_field]):
                    if match_results:
                        all_matches = []
                        for mr in match_results:
                            all_matches.extend(mr['matches'])
                        
                        # 去重
                        unique_matches = []
                        seen_ids = set()
                        for match in all_matches:
                            if match['id'] not in seen_ids:
                                unique_matches.append(match)
                                seen_ids.add(match['id'])
                        
                        if len(unique_matches) == 1:
                            # 只有一个匹配结果，直接使用
                            data.at[idx, id_field] = unique_matches[0]['id']
                            matched_ids[f"{master_type}_{idx}"] = unique_matches[0]['id']
                        elif len(unique_matches) > 1:
                            # 多个匹配结果，需要用户选择
                            multiple_matches.append({
                                'row_index': idx,
                                'master_type': master_type,
                                'id_field': id_field,
                                'source_values': {mr['field']: mr['value'] for mr in match_results},
                                'candidates': unique_matches
                            })
                        else:
                            # 没有匹配结果
                            unmatched_records.append({
                                'row_index': idx,
                                'master_type': master_type,
                                'id_field': id_field,
                                'source_values': {mr['field']: mr['value'] for mr in match_results},
                                'message': f'无法匹配 {master_type}，请检查数据或手动补充'
                            })
                    else:
                        # 没有匹配字段的值
                        unmatched_records.append({
                            'row_index': idx,
                            'master_type': master_type,
                            'id_field': id_field,
                            'source_values': {},
                            'message': f'{master_type} 匹配字段缺失或为空'
                        })
        
        return {
            'matched_ids': matched_ids,
            'unmatched_records': unmatched_records,
            'multiple_matches': multiple_matches,
            'requires_user_decision': len(multiple_matches) > 0 or len(unmatched_records) > 0,
            'data': data  # 返回更新后的数据
        }
    
    def _match_single_field(self, value: Any, match_config: Dict[str, Any], db_connection) -> List[Dict[str, Any]]:
        """单字段匹配
        
        Args:
            value: 要匹配的值
            match_config: 匹配配置
            db_connection: 数据库连接
            
        Returns:
            匹配结果列表 [{'id': ..., 'name': ..., 'confidence': ...}, ...]
        """
        if not db_connection:
            # 如果没有数据库连接，返回空列表
            return []
        
        table_name = match_config['table']
        column_name = match_config['column']
        
        # 执行数据库查询（示例SQL）
        # 实际实现时应该使用参数化查询防止SQL注入
        query = f"""
        SELECT id, {column_name} as name, 
               CASE 
                   WHEN {column_name} = %s THEN 1.0
                   WHEN {column_name} ILIKE %s THEN 0.9
                   WHEN {column_name} ILIKE %s THEN 0.8
                   ELSE 0.7
               END as confidence
        FROM {table_name}
        WHERE {column_name} ILIKE %s OR {column_name} = %s
        ORDER BY confidence DESC, {column_name}
        LIMIT 5
        """
        
        # 这里只是示例，实际应该使用ORM或参数化查询
        # results = db_connection.execute(query, [value, f"%{value}%", f"{value}%", f"%{value}%", value])
        
        # 模拟返回结果
        return []
    
    def _match_combined_fields(self, row: pd.Series, match_fields: List[Dict[str, Any]], rule: Dict[str, Any], db_connection) -> List[Dict[str, Any]]:
        """组合字段匹配
        
        例如：产品需要同时匹配产品名称和规格型号
        
        Args:
            row: 数据行
            match_fields: 匹配字段配置列表
            rule: 匹配规则
            db_connection: 数据库连接
            
        Returns:
            匹配结果列表
        """
        if not db_connection:
            return []
        
        # 构建组合查询条件
        conditions = []
        values = []
        
        for match_field in match_fields:
            source_field = match_field['field']
            if source_field in row.index:
                source_value = row.get(source_field)
                if pd.notna(source_value) and source_value:
                    table_column = f"{match_field['table']}.{match_field['column']}"
                    conditions.append(f"{match_field['table']}.{match_field['column']} = %s")
                    values.append(source_value)
        
        if not conditions:
            return []
        
        # 组合查询（示例）
        # query = f"""
        # SELECT p.id, p.product_name, p.specification,
        #        CASE WHEN p.product_name = %s AND p.specification = %s THEN 1.0 ELSE 0.8 END as confidence
        # FROM {match_fields[0]['table']} p
        # WHERE {' AND '.join(conditions)}
        # ORDER BY confidence DESC
        # LIMIT 5
        # """
        
        # 模拟返回结果
        return []
    
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

## 3. 事后补充功能

### 3.1 事后补充管理器

```python
class DocumentSupplementManager:
    """单据事后补充管理器"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.supplement_log = []
    
    def supplement_missing_header(self, detail_data: pd.DataFrame, 
                                 header_data: pd.DataFrame = None,
                                 supplement_rules: dict = None) -> SupplementResult:
        """补充缺失的单据头"""
        
        if header_data is not None:
            # 使用提供的头表数据
            return self.supplement_with_provided_header(detail_data, header_data)
        else:
            # 使用补充规则生成头信息
            return self.supplement_with_rules(detail_data, supplement_rules)
    
    def supplement_missing_details(self, header_data: pd.DataFrame,
                                 detail_data: pd.DataFrame = None,
                                 supplement_rules: dict = None) -> SupplementResult:
        """补充缺失的单据明细"""
        
        if detail_data is not None:
            # 使用提供的明细数据
            return self.supplement_with_provided_details(header_data, detail_data)
        else:
            # 使用补充规则生成明细
            return self.supplement_with_rules(header_data, supplement_rules)
    
    def supplement_with_provided_header(self, detail_data: pd.DataFrame, 
                                      header_data: pd.DataFrame) -> SupplementResult:
        """使用提供的头表数据补充"""
        try:
            # 找到关联字段
            detail_key = self.find_join_key(detail_data)
            header_key = self.find_join_key(header_data)
            
            if not detail_key or not header_key:
                raise ValueError("无法找到关联字段")
            
            # 执行关联
            supplemented_data = detail_data.merge(
                header_data,
                left_on=detail_key,
                right_on=header_key,
                how='left'
            )
            
            # 记录补充操作
            self.log_supplement_operation('header', len(supplemented_data))
            
            return SupplementResult(
                success=True,
                supplemented_data=supplemented_data,
                operation_type='header_supplement',
                records_processed=len(supplemented_data)
            )
            
        except Exception as e:
            return SupplementResult(
                success=False,
                error_message=str(e),
                operation_type='header_supplement'
            )
    
    def supplement_with_provided_details(self, header_data: pd.DataFrame,
                                       detail_data: pd.DataFrame) -> SupplementResult:
        """使用提供的明细数据补充"""
        try:
            # 找到关联字段
            header_key = self.find_join_key(header_data)
            detail_key = self.find_join_key(detail_data)
            
            if not header_key or not detail_key:
                raise ValueError("无法找到关联字段")
            
            # 执行关联
            supplemented_data = header_data.merge(
                detail_data,
                left_on=header_key,
                right_on=detail_key,
                how='left'
            )
            
            # 记录补充操作
            self.log_supplement_operation('details', len(supplemented_data))
            
            return SupplementResult(
                success=True,
                supplemented_data=supplemented_data,
                operation_type='details_supplement',
                records_processed=len(supplemented_data)
            )
            
        except Exception as e:
            return SupplementResult(
                success=False,
                error_message=str(e),
                operation_type='details_supplement'
            )
    
    def supplement_with_rules(self, data: pd.DataFrame, 
                             supplement_rules: dict) -> SupplementResult:
        """使用补充规则生成缺失数据"""
        try:
            supplemented_data = data.copy()
            
            # 应用补充规则
            for field, rule in supplement_rules.items():
                if rule['type'] == 'default_value':
                    supplemented_data[field] = rule['value']
                elif rule['type'] == 'calculated':
                    supplemented_data[field] = self.calculate_field(
                        supplemented_data, rule['formula']
                    )
                elif rule['type'] == 'lookup':
                    supplemented_data[field] = self.lookup_field(
                        supplemented_data, rule['lookup_table'], rule['lookup_field']
                    )
            
            # 记录补充操作
            self.log_supplement_operation('rules', len(supplemented_data))
            
            return SupplementResult(
                success=True,
                supplemented_data=supplemented_data,
                operation_type='rules_supplement',
                records_processed=len(supplemented_data)
            )
            
        except Exception as e:
            return SupplementResult(
                success=False,
                error_message=str(e),
                operation_type='rules_supplement'
            )
    
    def calculate_field(self, data: pd.DataFrame, formula: str) -> pd.Series:
        """计算字段值"""
        # 简单的公式计算，可以扩展为更复杂的表达式
        if formula == 'sum_amount':
            return data['金额'].sum()
        elif formula == 'count_items':
            return data['数量'].sum()
        else:
            return pd.Series([0] * len(data))
    
    def lookup_field(self, data: pd.DataFrame, lookup_table: str, 
                    lookup_field: str) -> pd.Series:
        """查找字段值"""
        # 从数据库查找表获取值
        # 这里简化处理，实际应该查询数据库
        return pd.Series(['lookup_value'] * len(data))
    
    def log_supplement_operation(self, operation_type: str, records_count: int):
        """记录补充操作"""
        log_entry = {
            'timestamp': pd.Timestamp.now(),
            'operation_type': operation_type,
            'records_count': records_count,
            'status': 'success'
        }
        self.supplement_log.append(log_entry)
    
    def get_supplement_history(self) -> pd.DataFrame:
        """获取补充历史"""
        return pd.DataFrame(self.supplement_log)
    
    def find_join_key(self, data: pd.DataFrame) -> str:
        """查找关联字段"""
        key_patterns = ['单据号', 'document_id', '单号', 'id']
        
        for pattern in key_patterns:
            for col in data.columns:
                if pattern in col.lower():
                    return col
        
        return None
```

### 3.2 补充规则配置

```python
@dataclass
class SupplementRule:
    """补充规则"""
    field_name: str
    rule_type: str  # default_value, calculated, lookup
    rule_config: dict
    
    def apply(self, data: pd.DataFrame) -> pd.Series:
        """应用补充规则"""
        if self.rule_type == 'default_value':
            return pd.Series([self.rule_config['value']] * len(data))
        elif self.rule_type == 'calculated':
            return self.calculate_field(data, self.rule_config['formula'])
        elif self.rule_type == 'lookup':
            return self.lookup_field(data, self.rule_config['lookup_table'])
        else:
            return pd.Series([None] * len(data))

@dataclass
class SupplementConfig:
    """补充配置"""
    # 头表补充规则
    header_supplement_rules: List[SupplementRule] = None
    
    # 明细补充规则
    detail_supplement_rules: List[SupplementRule] = None
    
    # 自动补充设置
    auto_supplement: bool = True
    supplement_threshold: float = 0.8  # 80%以上缺失才自动补充
    
    # 补充策略
    supplement_strategy: str = 'conservative'  # conservative, aggressive, manual
    
    def __post_init__(self):
        if self.header_supplement_rules is None:
            self.header_supplement_rules = [
                SupplementRule(
                    field_name='单据日期',
                    rule_type='default_value',
                    rule_config={'value': pd.Timestamp.now().strftime('%Y-%m-%d')}
                ),
                SupplementRule(
                    field_name='客户名称',
                    rule_type='default_value',
                    rule_config={'value': '未知客户'}
                )
            ]
        
        if self.detail_supplement_rules is None:
            self.detail_supplement_rules = [
                SupplementRule(
                    field_name='产品名称',
                    rule_type='default_value',
                    rule_config={'value': '汇总项目'}
                ),
                SupplementRule(
                    field_name='数量',
                    rule_type='default_value',
                    rule_config={'value': 1}
                ),
                # 税务字段补充规则
                SupplementRule(
                    field_name='价税合计',
                    rule_type='calculated',
                    rule_config={
                        'formula': '不含税金额 + 税额',
                        'fields': ['不含税金额', '税额']
                    }
                ),
                SupplementRule(
                    field_name='不含税金额',
                    rule_type='calculated',
                    rule_config={
                        'formula': '价税合计 - 税额',
                        'fields': ['价税合计', '税额']
                    }
                ),
                SupplementRule(
                    field_name='税额',
                    rule_type='calculated',
                    rule_config={
                        'formula': '价税合计 - 不含税金额',
                        'fields': ['价税合计', '不含税金额']
                    }
                )
            ]
```

### 3.3 补充操作示例

```python
# 示例1: 补充缺失的单据头
def supplement_missing_headers():
    """补充缺失的单据头"""
    
    # 加载明细数据
    detail_data = pd.read_excel('detail_only.xlsx')
    
    # 创建补充管理器
    supplement_manager = DocumentSupplementManager(db_connection)
    
    # 定义补充规则
    supplement_rules = {
        '单据号': {
            'type': 'calculated',
            'formula': 'generate_document_id'
        },
        '单据日期': {
            'type': 'default_value',
            'value': '2024-01-01'
        },
        '客户名称': {
            'type': 'lookup',
            'lookup_table': 'customer_master',
            'lookup_field': 'customer_name'
        }
    }
    
    # 执行补充
    result = supplement_manager.supplement_missing_header(
        detail_data, 
        supplement_rules=supplement_rules
    )
    
    if result.success:
        print(f"补充成功，处理了 {result.records_processed} 条记录")
        return result.supplemented_data
    else:
        print(f"补充失败: {result.error_message}")
        return None

# 示例2: 补充缺失的单据明细
def supplement_missing_details():
    """补充缺失的单据明细"""
    
    # 加载头表数据
    header_data = pd.read_excel('header_only.xlsx')
    
    # 创建补充管理器
    supplement_manager = DocumentSupplementManager(db_connection)
    
    # 定义补充规则
    supplement_rules = {
        '产品名称': {
            'type': 'default_value',
            'value': '汇总项目'
        },
        '数量': {
            'type': 'default_value',
            'value': 1
        },
        '金额': {
            'type': 'calculated',
            'formula': 'use_total_amount'
        }
    }
    
    # 执行补充
    result = supplement_manager.supplement_missing_details(
        header_data,
        supplement_rules=supplement_rules
    )
    
    if result.success:
        print(f"补充成功，处理了 {result.records_processed} 条记录")
        return result.supplemented_data
    else:
        print(f"补充失败: {result.error_message}")
        return None

# 示例3: 使用提供的头表数据补充
def supplement_with_provided_header():
    """使用提供的头表数据补充"""
    
    # 加载明细数据和头表数据
    detail_data = pd.read_excel('detail_only.xlsx')
    header_data = pd.read_excel('header_table.xlsx')
    
    # 创建补充管理器
    supplement_manager = DocumentSupplementManager(db_connection)
    
    # 执行补充
    result = supplement_manager.supplement_missing_header(
        detail_data,
        header_data=header_data
    )
    
    if result.success:
        print(f"补充成功，处理了 {result.records_processed} 条记录")
        return result.supplemented_data
    else:
        print(f"补充失败: {result.error_message}")
        return None
```

---

## 4. 配置驱动的处理策略

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

## 5. 字段映射示例和配置

### 5.1 字段映射的重要性

**重要**：在处理单据数据之前，必须先将源文件的字段映射到标准字段名。

#### 为什么需要字段映射？

1. **源文件字段名不一致**：不同的ERP系统、不同的导出格式，字段名可能不同
   - 例如："订单号" vs "单据号" vs "document_id"
   - 例如："不含税金额" vs "金额(不含税)" vs "ex_tax_amount"

2. **可能没有列名**：有些Excel文件第一行就是数据，没有表头
   - 需要使用列索引（col_0, col_1, ...）或位置映射

3. **格式识别需要标准字段名**：格式识别器和字段识别器都基于标准字段名工作

#### 智能字段映射和学习机制 ✅

**系统特性**：
- ✅ **智能推荐**：系统自动推荐字段映射关系，降低用户操作难度
- ✅ **历史记忆**：记录历史映射记录，作为下次智能映射的参考
- ✅ **持续学习**：用户确认的映射会被记录下来，提高后续推荐的准确性
- ✅ **上下文感知**：考虑数据源类型、单据类型、用户ID等上下文信息

**映射优先级**：
1. **历史映射**（最高优先级）：同一数据源、同一单据类型的历史映射，置信度最高
2. **系统规则**：系统级映射规则（如正则表达式匹配）
3. **相似度匹配**：字符串相似度计算，支持多种算法

**详细设计**：参见 [智能字段映射设计文档](./INTELLIGENT_FIELD_MAPPING_DESIGN.md)

### 5.2 字段映射示例

#### 示例1：有列名的源文件

**源文件字段名**:
```python
source_columns = [
    "采购订单号", "订单日期", "供应商", "物料名称", 
    "数量", "单价", "金额", "税", "合计"
]
```

**字段映射配置**:
```python
field_mappings = {
    "采购订单号": "单据号",
    "订单日期": "单据日期",
    "供应商": "客户名称",
    "物料名称": "产品名称",
    "数量": "数量",
    "单价": "单价",
    "金额": "不含税金额",
    "税": "税额",
    "合计": "价税合计"
}
```

**映射后的标准字段名**:
- 单据号 (document_id)
- 单据日期 (document_date)
- 客户名称 (customer_name)
- 产品名称 (product_name)
- 数量 (quantity)
- 单价 (unit_price)
- 不含税金额 (ex_tax_amount)
- 税额 (tax_amount)
- 价税合计 (total_amount_with_tax)

#### 示例2：没有列名的源文件（使用位置映射）

**源文件结构**（第一行就是数据，没有表头）:
```
DOC001 | 2024-01-01 | 客户A | 产品1 | 10 | 100.00 | 1000.00 | 130.00 | 1130.00
DOC002 | 2024-01-02 | 客户B | 产品2 | 5  | 100.00 | 500.00  | 65.00  | 565.00
```

**读取数据时自动添加列索引**:
```python
# 读取时使用 header=None，系统自动使用 col_0, col_1, ...
data = pd.read_excel('no_header.xlsx', header=None)
# 列名自动变为: ['col_0', 'col_1', 'col_2', 'col_3', 'col_4', 'col_5', 'col_6', 'col_7', 'col_8']
```

**位置映射配置**:
```python
position_mappings = {
    "col_0": "单据号",      # 第1列
    "col_1": "单据日期",    # 第2列
    "col_2": "客户名称",    # 第3列
    "col_3": "产品名称",    # 第4列
    "col_4": "数量",        # 第5列
    "col_5": "单价",        # 第6列
    "col_6": "不含税金额",  # 第7列
    "col_7": "税额",        # 第8列
    "col_8": "价税合计"     # 第9列
}
```

### 5.3 自动智能映射

系统可以自动识别字段名的相似度，提供映射建议：

```python
# 自动映射示例
source_fields = ["采购订单号", "订单日期", "供应商", "物料名称", "金额", "税", "合计"]
target_fields = ["单据号", "单据日期", "客户名称", "产品名称", "不含税金额", "税额", "价税合计"]

# 自动映射结果
auto_mappings = {
    "采购订单号": "单据号",      # 相似度匹配
    "订单日期": "单据日期",      # 精确匹配
    "供应商": "客户名称",        # 语义匹配
    "物料名称": "产品名称",      # 语义匹配
    "金额": "不含税金额",        # 需要用户确认（可能是含税金额）
    "税": "税额",                # 精确匹配
    "合计": "价税合计"           # 语义匹配
}
```

### 5.4 标准字段名清单

#### 单据头字段（标准字段名）

| 标准字段名 | 英文标准名 | 常见变体 |
|-----------|-----------|---------|
| 单据号 | document_id | 订单号、采购订单号、单号 |
| 单据日期 | document_date | 订单日期、日期 |
| 客户名称 | customer_name | 供应商、客户、公司名称 |
| 不含税金额 | ex_tax_amount | 金额、金额(不含税)、不含税 |
| 税额 | tax_amount | 税、税额、税金 |
| 价税合计 | total_amount_with_tax | 合计、总金额、含税金额 |

#### 明细字段（标准字段名）

| 标准字段名 | 英文标准名 | 常见变体 |
|-----------|-----------|---------|
| 产品名称 | product_name | 物料名称、商品名称、产品 |
| 数量 | quantity | 数量、qty、数量(个) |
| 单价 | unit_price | 单价、价格、单价(元) |
| 不含税金额 | ex_tax_amount | 金额、金额(不含税)、不含税 |
| 税额 | tax_amount | 税、税额、税金 |
| 价税合计 | total_amount_with_tax | 合计、小计、含税金额 |
| 税率 | tax_rate | 税率、tax_rate、税率(%) |

### 5.5 完整使用示例

```python
# 完整字段映射和处理流程示例（包含用户决策）
import pandas as pd
from intelligent_document_processor import IntelligentDocumentProcessor

# 1. 读取源文件（可能有列名，也可能没有）
data = pd.read_excel('purchase_order.xlsx')

# 2. 配置字段映射（用户手动配置或自动智能映射）
field_mappings = {
    "采购订单号": "单据号",
    "订单日期": "单据日期",
    "供应商": "客户名称",
    # 注意：这里没有映射明细字段（产品名称、数量等）
    "金额": "不含税金额",
    "税": "税额",
    "合计": "价税合计"
}

# 3. 创建处理器
processor = IntelligentDocumentProcessor()

# 4. 处理数据（字段映射会自动应用）
metadata = {}
result = processor.process_document(
    data=data,
    field_mappings=field_mappings,
    metadata=metadata
)

# 5. 处理结果和用户决策
if result.success:
    print(f"检测到格式: {result.format_type}")
    print(f"处理成功，共 {len(result.processed_data)} 条记录")
    processed_data = result.processed_data

elif result.requires_user_decision:
    # 需要用户决策：明细字段缺失
    print(f"⚠️ 需要用户决策: {result.decision_message}")
    print(f"缺失的明细字段: {result.missing_detail_fields}")
    
    # 场景1：用户选择继续导入（作为只有单据头的格式）
    user_decision = 'continue_without_details'
    metadata['user_decision'] = user_decision
    
    # 重新处理，传入用户决策
    result = processor.process_document(
        data=data,
        field_mappings=field_mappings,
        metadata=metadata
    )
    
    if result.success:
        print(f"✅ 用户选择继续导入，格式: {result.format_type}")
        print(f"   将作为只有单据头的格式导入，后续可补充明细")
        processed_data = result.processed_data
    
    # 场景2：用户选择放弃导入
    # user_decision = 'abort'
    # metadata['user_decision'] = user_decision
    # result = processor.process_document(...)
    # if not result.success:
    #     print("❌ 用户选择放弃导入，请补充明细字段后重新导入")
    
else:
    print(f"❌ 处理失败: {result.error_message}")
```

### 5.6 用户决策流程说明

**当字段映射后发现明细字段缺失时**：

1. **系统自动检测**
   - 字段映射完成后，系统自动验证字段完整性
   - 如果发现明细字段缺失，返回需要用户决策的状态

2. **用户决策选项**
   - **选项1：继续导入**
     - 系统将强制识别为"只有单据头的格式"（格式4或格式6）
     - 创建虚拟明细记录（可选）
     - 后续可以通过事后补充功能添加明细
   - **选项2：放弃导入**
     - 系统终止导入流程
     - 提示用户补充缺失的明细字段
     - 用户可以修正源文件或补充字段映射后重新导入

3. **决策后的处理**
   - 如果用户选择继续，系统会根据可用字段自动选择最合适的格式
   - 如果单据头字段完整，使用格式4（只有单据头记录）
   - 如果只有部分单据头字段，使用格式6（纯单据头记录）

4. **后续补充**
   - 导入完成后，用户可以：
     - 通过事后补充功能添加明细记录
     - 通过API或界面导入明细数据
     - 手动编辑添加明细信息

---

## 6. 必填字段和主数据ID处理

### 6.1 必填字段分类

必填字段分为两类：

#### 1. 严格必填字段（Strict Required Fields）

**特点**：
- 必须严格从源文件获取
- 缺失时终止导入，不允许补充
- 通常用于关键业务标识字段

**常见字段**：
- 单据号（document_id）
- 单据日期（document_date）
- 经营主体ID（business_entity_id）- 需通过匹配得到
- 往来单位ID（counterparty_id）- 需通过匹配得到

**处理流程**：
```
检查严格必填字段
    ↓
字段缺失？
    ↓ Yes
终止导入，返回错误信息
    ↓ No
继续处理
```

#### 2. 可补充必填字段（Supplementable Required Fields）

**特点**：
- 允许通过补充策略或人工补充
- 支持多种补充策略：
  - **自动补充**：使用默认值或计算值
  - **规则补充**：使用补充规则生成
  - **人工补充**：提示用户手动输入

**常见字段**：
- 客户名称（customer_name）- 可以从往来单位名称补充
- 产品名称（product_name）- 可以从产品ID查询补充
- 税率（tax_rate）- 可以从税率ID查询补充

**处理流程**：
```
检查可补充必填字段
    ↓
字段缺失？
    ↓ Yes
应用补充策略（自动/规则/人工）
    ↓
补充成功？
    ↓ Yes
继续处理
    ↓ No
提示用户决策（放弃导入 或 手动补充）
```

### 6.2 必填字段配置示例

```python
# 必填字段配置
field_config = {
    # 严格必填字段（必须从源文件严格获取）
    'strict_required_fields': [
        {
            'name': '单据号',
            'columns': ['单据号', 'document_id', '单号'],
            'type': 'string',
            'validation': {
                'required': True,
                'unique': True
            }
        },
        {
            'name': '单据日期',
            'columns': ['单据日期', 'document_date', '日期'],
            'type': 'date',
            'validation': {
                'required': True,
                'format': 'YYYY-MM-DD'
            }
        }
    ],
    
    # 可补充必填字段（允许补充）
    'supplementable_required_fields': [
        {
            'name': '经营主体ID',
            'columns': ['经营主体id', 'business_entity_id'],
            'type': 'uuid',
            'supplement_strategy': 'master_data_match',  # 通过主数据匹配
            'supplement_config': {
                'master_type': 'business_entity',
                'match_fields': ['经营主体名称', '统一社会信用代码']
            }
        },
        {
            'name': '客户名称',
            'columns': ['客户名称', 'customer_name'],
            'type': 'string',
            'supplement_strategy': 'lookup',  # 通过查找补充
            'supplement_config': {
                'lookup_field': '往来单位id',
                'lookup_table': 'dim_counterparty',
                'lookup_column': 'counterparty_name'
            }
        },
        {
            'name': '税率',
            'columns': ['税率', 'tax_rate'],
            'type': 'decimal',
            'supplement_strategy': 'default_value',  # 使用默认值
            'supplement_config': {
                'default_value': 0.13  # 默认13%
            }
        }
    ]
}
```

### 6.3 主数据ID匹配

**主数据ID特点**：
- 不能直接从源文件导入
- 必须通过源文件中的相关信息在系统中匹配查询得到
- 匹配失败或多个匹配时，需要用户决策

**常见主数据ID**：

| 主数据ID | 匹配字段 | 匹配表 | 匹配逻辑 |
|---------|---------|--------|---------|
| 经营主体ID | 经营主体名称、统一社会信用代码 | dim_business_entity | 优先代码，其次名称 |
| 往来单位ID | 往来单位名称、统一社会信用代码 | dim_counterparty | 优先代码，其次名称 |
| 产品ID | 产品名称+规格型号 | dim_product | 组合匹配 |
| 计量单位ID | 计量单位名称 | dim_unit | 精确或模糊匹配 |
| 税率ID | 税率值、税率名称 | dim_tax_rate | 优先精确值，其次名称 |
| 员工ID | 员工姓名、员工工号、身份证号 | dim_employee | 优先工号，其次身份证号，最后姓名 |
| 汇率ID | 币种+汇率日期、汇率值 | dim_exchange_rate | 组合匹配（币种+日期） |

### 6.4 主数据匹配配置示例

```python
# 主数据匹配配置
master_data_config = {
    'matching_rules': {
        'business_entity': {
            'id_field': '经营主体id',
            'match_fields': [
                {
                    'field': '经营主体名称',
                    'table': 'dim_business_entity',
                    'column': 'entity_name',
                    'match_type': 'fuzzy'  # 模糊匹配
                },
                {
                    'field': '统一社会信用代码',
                    'table': 'dim_business_entity',
                    'column': 'credit_code',
                    'match_type': 'exact'  # 精确匹配
                }
            ],
            'priority': ['统一社会信用代码', '经营主体名称'],
            'confidence_threshold': 0.8  # 匹配置信度阈值
        },
        'product': {
            'id_field': '产品id',
            'match_fields': [
                {
                    'field': '产品名称',
                    'table': 'dim_product',
                    'column': 'product_name',
                    'match_type': 'fuzzy'
                },
                {
                    'field': '规格型号',
                    'table': 'dim_product',
                    'column': 'specification',
                    'match_type': 'fuzzy'
                }
            ],
            'match_type': 'combined',  # 需要同时匹配多个字段
            'priority': ['产品名称', '规格型号'],
            'confidence_threshold': 0.85
        },
        'unit': {
            'id_field': '计量单位id',
            'match_fields': [
                {
                    'field': '计量单位名称',
                    'table': 'dim_unit',
                    'column': 'unit_name',
                    'match_type': 'fuzzy'
                }
            ],
            'priority': ['计量单位名称'],
            'confidence_threshold': 0.9
        },
        'tax_rate': {
            'id_field': '税率id',
            'match_fields': [
                {
                    'field': '税率',
                    'table': 'dim_tax_rate',
                    'column': 'tax_rate_value',
                    'match_type': 'exact'
                },
                {
                    'field': '税率名称',
                    'table': 'dim_tax_rate',
                    'column': 'tax_rate_name',
                    'match_type': 'fuzzy'
                }
            ],
            'priority': ['税率', '税率名称'],
            'confidence_threshold': 0.95
        },
        'employee': {
            'id_field': '员工id',
            'match_fields': [
                {
                    'field': '员工姓名',
                    'table': 'dim_employee',
                    'column': 'employee_name',
                    'match_type': 'fuzzy'
                },
                {
                    'field': '员工工号',
                    'table': 'dim_employee',
                    'column': 'employee_code',
                    'match_type': 'exact'
                },
                {
                    'field': '身份证号',
                    'table': 'dim_employee',
                    'column': 'id_card',
                    'match_type': 'exact'
                }
            ],
            'priority': ['员工工号', '身份证号', '员工姓名'],
            'confidence_threshold': 0.85
        },
        'exchange_rate': {
            'id_field': '汇率id',
            'match_fields': [
                {
                    'field': '币种',
                    'table': 'dim_exchange_rate',
                    'column': 'currency_code',
                    'match_type': 'exact'
                },
                {
                    'field': '汇率日期',
                    'table': 'dim_exchange_rate',
                    'column': 'rate_date',
                    'match_type': 'exact'
                },
                {
                    'field': '汇率值',
                    'table': 'dim_exchange_rate',
                    'column': 'rate_value',
                    'match_type': 'fuzzy'
                }
            ],
            'match_type': 'combined',  # 需要同时匹配币种和日期
            'priority': ['币种', '汇率日期', '汇率值'],
            'confidence_threshold': 0.95
        }
    },
    'fallback_strategy': {
        'create_new': False,  # 是否允许创建新的主数据记录
        'use_default': True,   # 是否使用默认值
        'require_user_decision': True  # 是否要求用户决策
    }
}
```

### 6.5 主数据匹配处理流程

```
遍历每一行数据
    ↓
按优先级尝试匹配主数据ID
    ↓
精确匹配成功？
    ↓ Yes
使用匹配的ID
    ↓ No
模糊匹配？
    ↓ Yes
检查匹配结果数量
    ↓
    只有一个匹配？
        ↓ Yes
        检查置信度 >= 阈值？
            ↓ Yes
            使用匹配的ID
            ↓ No
            加入待决策列表
        ↓ No
        多个匹配？
            ↓ Yes
            加入待决策列表（多个候选）
            ↓ No
            没有匹配？
                ↓ Yes
                加入待决策列表（未匹配）
```

### 6.6 用户决策场景

#### 场景1：精确匹配成功
```
源数据：统一社会信用代码 = "91110000123456789X"
匹配结果：找到1条记录，ID = "uuid-123"
处理：自动使用匹配的ID，无需用户决策
```

#### 场景2：模糊匹配，唯一结果且置信度高
```
源数据：经营主体名称 = "北京科技有限公司"
匹配结果：找到1条记录，名称 = "北京科技有限公司"，置信度 = 0.95
处理：自动使用匹配的ID（置信度 > 0.8阈值），无需用户决策
```

#### 场景3：多个匹配结果
```
源数据：产品名称 = "产品A"，规格型号 = "型号1"
匹配结果：
  - 候选1：ID = "uuid-1", 名称 = "产品A", 规格 = "型号1", 置信度 = 0.9
  - 候选2：ID = "uuid-2", 名称 = "产品A", 规格 = "型号1-改", 置信度 = 0.85
处理：提示用户选择，返回：
{
    'requires_user_decision': True,
    'decision_message': '产品匹配到多个候选，请选择',
    'multiple_matches': [
        {
            'row_index': 0,
            'master_type': 'product',
            'source_values': {'产品名称': '产品A', '规格型号': '型号1'},
            'candidates': [
                {'id': 'uuid-1', 'name': '产品A', 'spec': '型号1', 'confidence': 0.9},
                {'id': 'uuid-2', 'name': '产品A', 'spec': '型号1-改', 'confidence': 0.85}
            ]
        }
    ]
}
```

#### 场景4：未匹配到结果
```
源数据：往来单位名称 = "新客户ABC公司"
匹配结果：未找到匹配记录
处理：提示用户决策，返回：
{
    'requires_user_decision': True,
    'decision_message': '往来单位未匹配到，请选择处理方式',
    'unmatched_records': [
        {
            'row_index': 0,
            'master_type': 'counterparty',
            'source_values': {'往来单位名称': '新客户ABC公司'},
            'options': [
                '创建新的往来单位记录',
                '手动选择已有往来单位',
                '跳过该记录'
            ]
        }
    ]
}
```

### 6.7 完整处理流程示例

```python
# 完整的数据导入流程（包含必填字段验证和主数据匹配）
import pandas as pd
from intelligent_document_processor import IntelligentDocumentProcessor

# 1. 读取源文件
data = pd.read_excel('purchase_order.xlsx')

# 2. 配置字段映射
field_mappings = {
    "采购订单号": "单据号",
    "订单日期": "单据日期",
    "供应商": "往来单位名称",
    "物料名称": "产品名称",
    "规格": "规格型号",
    "单位": "计量单位名称",
    "税率": "税率"
}

# 3. 配置必填字段规则
field_config = {
    'strict_required_fields': [
        {'name': '单据号', 'columns': ['单据号', 'document_id']},
        {'name': '单据日期', 'columns': ['单据日期', 'document_date']}
    ],
    'supplementable_required_fields': [
        {
            'name': '经营主体ID',
            'columns': ['经营主体id'],
            'supplement_strategy': 'master_data_match'
        },
        {
            'name': '往来单位ID',
            'columns': ['往来单位id'],
            'supplement_strategy': 'master_data_match'
        }
    ]
}

# 4. 配置主数据匹配规则
master_data_config = {
    'matching_rules': {
        'counterparty': {
            'id_field': '往来单位id',
            'match_fields': [
                {'field': '往来单位名称', 'table': 'dim_counterparty', 'column': 'counterparty_name'},
                {'field': '统一社会信用代码', 'table': 'dim_counterparty', 'column': 'credit_code'}
            ],
            'priority': ['统一社会信用代码', '往来单位名称']
        },
        'product': {
            'id_field': '产品id',
            'match_fields': [
                {'field': '产品名称', 'table': 'dim_product', 'column': 'product_name'},
                {'field': '规格型号', 'table': 'dim_product', 'column': 'specification'}
            ],
            'match_type': 'combined',
            'priority': ['产品名称', '规格型号']
        }
    }
}

# 5. 创建处理器
processor = IntelligentDocumentProcessor()

# 6. 处理数据
metadata = {
    'field_config': field_config,
    'master_data_config': master_data_config,
    'db_connection': db_connection  # 数据库连接
}

result = processor.process_document(
    data=data,
    field_mappings=field_mappings,
    metadata=metadata
)

# 7. 处理结果
if result.success:
    print(f"✅ 导入成功，格式: {result.format_type}")
    processed_data = result.processed_data
    
elif result.requires_user_decision:
    # 需要用户决策
    if result.multiple_matches:
        # 多个匹配结果，让用户选择
        for match in result.multiple_matches:
            print(f"⚠️ 第 {match['row_index']} 行 {match['master_type']} 匹配到多个候选：")
            for i, candidate in enumerate(match['candidates']):
                print(f"  {i+1}. ID={candidate['id']}, 名称={candidate.get('name', '')}, 置信度={candidate.get('confidence', 0)}")
            
            # 用户选择（示例）
            user_choice = 1  # 用户选择第1个候选
            
            # 更新metadata，传入用户选择
            metadata['user_decisions'] = {
                f"{match['master_type']}_{match['row_index']}": match['candidates'][user_choice]['id']
            }
    
    if result.unmatched_records:
        # 未匹配记录，让用户决策
        for record in result.unmatched_records:
            print(f"⚠️ 第 {record['row_index']} 行 {record['master_type']} 未匹配：")
            print(f"  源数据: {record['source_values']}")
            print(f"  选项: 1) 创建新记录 2) 手动选择 3) 跳过")
            
            # 用户选择（示例）
            user_choice = 1  # 用户选择创建新记录
            
            # 更新metadata，传入用户决策
            metadata['user_decisions'] = metadata.get('user_decisions', {})
            metadata['user_decisions'][f"{record['master_type']}_{record['row_index']}"] = {
                'action': 'create_new' if user_choice == 1 else ('manual_select' if user_choice == 2 else 'skip')
            }
    
    # 重新处理，传入用户决策
    result = processor.process_document(
        data=data,
        field_mappings=field_mappings,
        metadata=metadata
    )
    
    if result.success:
        print(f"✅ 用户决策后导入成功")
        processed_data = result.processed_data

else:
    print(f"❌ 处理失败: {result.error_message}")
```

---

## 7. 集成到现有ETL系统

### 6.1 扩展现有ETL处理器

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

## 7.5 两阶段导入策略 ✅

**推荐方案**：使用**两阶段导入**策略，先导入临时表，修正后再导入正式表。

### 为什么使用两阶段导入？

1. ✅ **数据安全**：临时表隔离错误数据，避免影响正式业务数据
2. ✅ **错误处理**：在临时表中批量修正问题，更灵活、更安全
3. ✅ **用户体验**：可以在临时表中预览和验证，提高数据质量
4. ✅ **业务流程**：适合需要审核、协作的业务场景
5. ✅ **系统性能**：减少正式表的写操作和锁竞争

### 两阶段导入流程

**阶段1：导入临时表**
```
1. 数据去重和预处理
2. 导入临时表（staging_document_import）
3. 自动匹配主数据（高置信度自动匹配）
4. 标记问题数据（低置信度、匹配失败、计算冲突等）
5. 状态标记：pending → matched/problem
```

**阶段2：修正和确认**
```
1. 用户在临时表中处理问题：
   - 模糊匹配确认（选择、创建新、废弃）
   - 创建新的主数据记录并自动匹配
   - 废弃错误记录
   - 纠正计算字段冲突（价税合计 = 不含税金额 + 税额）
2. 批量或逐条处理
3. 状态更新：problem → confirmed
```

**阶段3：导入正式表**
```
1. 验证数据完整性
2. 导入正式表（doc_purchase_order_header/detail）
3. 更新临时表状态：confirmed → imported
```

**详细设计**：参见 [两阶段导入分析文档](./IMPORT_STAGING_ANALYSIS.md)

---

## 8. 总结

### 8.1 核心特性

✅ **智能格式识别**: 自动检测6种复杂单据格式，优先支持常见格式（格式1/2/4/6）
✅ **灵活处理策略**: 支持多种处理模式和错误恢复
✅ **事后补充功能**: 支持事后补充缺失的单据头或明细（格式5用于补充明细）
✅ **纯单据头处理**: 专门处理无明细的纯单据头记录（格式4/6）
✅ **字段映射优先**: 先完成字段映射，再进行格式识别和处理
✅ **智能字段映射**: 自动推荐字段映射，记录历史映射，持续学习提高准确性
✅ **历史映射学习**: 记录用户确认的映射，作为下次智能推荐的参考
✅ **必填字段验证**: 区分严格必填和可补充必填字段
✅ **主数据ID自动匹配**: 支持7种主数据ID的自动匹配（经营主体/往来单位/产品/计量单位/税率/员工/汇率）
✅ **用户决策机制**: 在关键决策点（明细缺失、匹配失败等）提示用户选择
✅ **税务字段支持**: 完整支持不含税金额、税额、价税合计等税务字段
✅ **配置驱动**: 通过配置文件灵活调整处理行为
✅ **错误处理**: 完善的错误处理和恢复机制
✅ **扩展性**: 易于扩展新的格式和处理策略

### 8.2 技术亮点

- **模式识别算法**: 基于数据特征自动识别6种单据格式，优先支持常见格式
- **智能数据填充**: 自动填充空值和关联数据（前向填充）
- **虚拟记录生成**: 为不完整数据创建虚拟记录
- **事后补充机制**: 支持事后补充缺失的单据头或明细（格式5用于补充明细）
- **纯单据头处理**: 专门处理无明细的服务类单据（格式4/6）
- **字段映射优先**: 先完成字段映射到标准字段名，再进行识别
- **必填字段分类**: 区分严格必填和可补充必填字段
- **主数据自动匹配**: 7种主数据ID的智能匹配，支持精确和模糊匹配
- **组合字段匹配**: 支持多字段组合匹配（如产品名称+规格型号）
- **置信度评估**: 匹配结果带置信度，自动决策或用户选择
- **多策略处理**: 支持不同的处理策略和错误恢复
- **补充规则引擎**: 灵活的补充规则配置和执行
- **金额字段验证**: 验证价税合计 = 不含税金额 + 税额的一致性

### 8.3 下一步行动

**Cursor的交付物** ✅:
- [x] 复杂单据格式处理算法设计（本文档）

**Lovable的实施任务** ⏳:

**优先级1：常见格式（必须实现）**
1. ✅ 实现格式1处理器（多行明细对应重复单据头）
2. ✅ 实现格式2处理器（多行明细但只有第一行有单据头）
3. ✅ 实现格式4处理器（只有单据头记录）
4. ✅ 实现格式6处理器（纯单据头记录）

**优先级2：特殊场景（可选实现）**
5. ⏳ 实现格式5处理器（只有明细记录，用于补充明细时）

**优先级3：可忽略格式（建议不实现）**
6. ❌ 格式3处理器（分离表格式）- 可忽略，可通过分两次导入实现

**其他功能**
7. ⏳ 实现智能格式识别器（优先识别常见格式）
8. ⏳ 实现字段映射和验证功能
9. ⏳ 实现必填字段验证和补充策略
10. ⏳ 实现主数据ID自动匹配（7种主数据）
11. ⏳ 实现用户决策机制
12. ⏳ 实现事后补充功能管理器
13. ⏳ 集成到现有ETL系统
14. ⏳ 添加配置管理界面
15. ⏳ 实现错误处理和恢复机制
16. ⏳ 实现补充规则引擎

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 1-2周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com
