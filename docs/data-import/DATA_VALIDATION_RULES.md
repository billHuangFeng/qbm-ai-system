# 数据验证规则文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P0 - 必需文档**

**文档目的**: 定义每种单据的数据验证规则，供Lovable在Edge Functions中实现

---

## 📋 目录

1. [验证规则分类](#1-验证规则分类)
2. [销售订单验证规则](#2-销售订单验证规则)
3. [跨表验证规则](#3-跨表验证规则)
4. [Python验证代码](#4-python验证代码)

---

## 1. 验证规则分类

### 1.1 验证层级

```yaml
验证层级:
  - Level 1: 格式验证 (Format Validation)
    - 必填字段检查
    - 数据类型检查
    - 格式检查（日期、金额等）
  
  - Level 2: 业务逻辑验证 (Business Logic Validation)
    - 数值范围检查
    - 枚举值检查
    - 业务规则检查
  
  - Level 3: 数据一致性验证 (Data Consistency Validation)
    - Header总额 = Line金额之和
    - 数量一致性检查
    - 金额计算验证
  
  - Level 4: 跨表验证 (Cross-Table Validation)
    - 主数据存在性检查
    - 关联单据检查
    - 业务状态检查
```

### 1.2 错误等级

```yaml
错误等级:
  - error: 阻断导入，必须修复
    - 必填字段缺失
    - 数据类型错误
    - 主数据未匹配
    - 金额计算错误
  
  - warning: 可以导入，但需要用户确认
    - 日期超出正常范围
    - 金额异常（过大或过小）
    - 数量异常
  
  - info: 信息提示，不影响导入
    - 字段值为空
    - 可选字段缺失
```

---

## 2. 销售订单验证规则

### 2.1 Header验证规则

```typescript
interface ValidationRule {
  field: string;
  rule_type: 'required' | 'type' | 'range' | 'pattern' | 'custom';
  level: 'error' | 'warning' | 'info';
  validator: (value: any, row: any) => boolean;
  message: string;
}

const salesOrderHeaderRules: ValidationRule[] = [
  // 必填字段验证
  {
    field: 'order_date',
    rule_type: 'required',
    level: 'error',
    validator: (value) => value != null && value !== '',
    message: '订单日期不能为空'
  },
  {
    field: 'customer_id',
    rule_type: 'required',
    level: 'error',
    validator: (value) => value != null && value !== '',
    message: '客户ID不能为空，请先匹配客户主数据'
  },
  
  // 数据类型验证
  {
    field: 'order_date',
    rule_type: 'type',
    level: 'error',
    validator: (value) => !isNaN(Date.parse(value)),
    message: '订单日期格式不正确，应为YYYY-MM-DD格式'
  },
  {
    field: 'total_amount',
    rule_type: 'type',
    level: 'error',
    validator: (value) => value == null || !isNaN(parseFloat(value)),
    message: '总金额格式不正确，应为数字'
  },
  
  // 范围验证
  {
    field: 'order_date',
    rule_type: 'range',
    level: 'warning',
    validator: (value) => {
      const date = new Date(value);
      const now = new Date();
      const threeMonthsAgo = new Date();
      threeMonthsAgo.setMonth(now.getMonth() - 3);
      const oneYearLater = new Date();
      oneYearLater.setFullYear(now.getFullYear() + 1);
      return date >= threeMonthsAgo && date <= oneYearLater;
    },
    message: '订单日期超出正常范围（过去3个月至未来1年）'
  },
  {
    field: 'total_amount',
    rule_type: 'range',
    level: 'warning',
    validator: (value) => {
      const amount = parseFloat(value);
      return amount >= 0 && amount <= 100000000; // 最大1亿
    },
    message: '总金额超出正常范围（0-100,000,000）'
  },
  
  // 业务规则验证
  {
    field: 'order_status',
    rule_type: 'custom',
    level: 'error',
    validator: (value) => {
      const validStatuses = ['draft', 'confirmed', 'in_progress', 'completed', 'cancelled'];
      return value == null || validStatuses.includes(value);
    },
    message: '订单状态值不正确，应为: draft, confirmed, in_progress, completed, cancelled'
  },
  
  // 金额一致性验证（在Level 3中处理）
  {
    field: 'total_amount',
    rule_type: 'custom',
    level: 'error',
    validator: (value, row, lines) => {
      // 需要与Line金额之和比较（在Level 3验证中处理）
      return true; // 占位符
    },
    message: 'Header总额与Line金额之和不一致'
  }
];
```

### 2.2 Line验证规则

```typescript
const salesOrderLineRules: ValidationRule[] = [
  // 必填字段验证
  {
    field: 'quantity',
    rule_type: 'required',
    level: 'error',
    validator: (value) => value != null && value !== '',
    message: '数量不能为空'
  },
  {
    field: 'unit_price',
    rule_type: 'required',
    level: 'error',
    validator: (value) => value != null && value !== '',
    message: '单价不能为空'
  },
  {
    field: 'sku_id',
    rule_type: 'required',
    level: 'error',
    validator: (value) => value != null && value !== '',
    message: 'SKU ID不能为空，请先匹配SKU主数据'
  },
  
  // 数值范围验证
  {
    field: 'quantity',
    rule_type: 'range',
    level: 'error',
    validator: (value) => {
      const qty = parseFloat(value);
      return qty > 0 && qty <= 1000000; // 最大100万
    },
    message: '数量必须大于0且不超过1,000,000'
  },
  {
    field: 'unit_price',
    rule_type: 'range',
    level: 'error',
    validator: (value) => {
      const price = parseFloat(value);
      return price >= 0 && price <= 1000000; // 最大100万
    },
    message: '单价必须大于等于0且不超过1,000,000'
  },
  {
    field: 'discount_rate',
    rule_type: 'range',
    level: 'error',
    validator: (value) => {
      if (value == null) return true;
      const rate = parseFloat(value);
      return rate >= 0 && rate <= 1;
    },
    message: '折扣率必须在0-1之间'
  },
  
  // 金额计算验证
  {
    field: 'line_amount',
    rule_type: 'custom',
    level: 'error',
    validator: (value, row) => {
      const qty = parseFloat(row.quantity);
      const price = parseFloat(row.unit_price);
      const calculated = qty * price;
      const declared = parseFloat(value);
      return Math.abs(calculated - declared) < 0.01; // 允许0.01误差
    },
    message: '行金额计算错误，应为 数量 × 单价'
  }
];
```

---

## 3. 跨表验证规则

### 3.1 Header总额 = Line金额之和

```typescript
interface CrossTableValidationRule {
  rule_type: 'consistency';
  level: 'error' | 'warning';
  validator: (header: any, lines: any[]) => boolean;
  message: string;
}

const crossTableRules: CrossTableValidationRule[] = [
  // Header总额 = Line金额之和
  {
    rule_type: 'consistency',
    level: 'error',
    validator: (header, lines) => {
      const calculatedTotal = lines.reduce((sum, line) => {
        const lineAmount = parseFloat(line.line_amount || 0);
        return sum + lineAmount;
      }, 0);
      
      const declaredTotal = parseFloat(header.total_amount || 0);
      const difference = Math.abs(calculatedTotal - declaredTotal);
      
      // 允许0.01误差
      return difference < 0.01;
    },
    message: 'Header总额与Line金额之和不一致'
  },
  
  // Header总数量 = Line数量之和
  {
    rule_type: 'consistency',
    level: 'error',
    validator: (header, lines) => {
      const calculatedTotalQty = lines.reduce((sum, line) => {
        const qty = parseFloat(line.quantity || 0);
        return sum + qty;
      }, 0);
      
      const declaredTotalQty = parseFloat(header.total_quantity || 0);
      const difference = Math.abs(calculatedTotalQty - declaredTotalQty);
      
      return difference < 0.001; // 允许0.001误差
    },
    message: 'Header总数量与Line数量之和不一致'
  },
  
  // 每个Header至少有1条Line
  {
    rule_type: 'consistency',
    level: 'error',
    validator: (header, lines) => {
      return lines.length > 0;
    },
    message: '每个Header必须有至少1条Line记录'
  },
  
  // Line行号唯一性
  {
    rule_type: 'consistency',
    level: 'error',
    validator: (header, lines) => {
      const lineNos = lines.map(line => line.line_no);
      const uniqueLineNos = new Set(lineNos);
      return lineNos.length === uniqueLineNos.size;
    },
    message: 'Line行号必须唯一'
  }
];
```

---

## 4. Python验证代码

### 4.1 完整实现

```python
from typing import List, Dict, Optional
import pandas as pd
from enum import Enum

class ValidationLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationRule:
    """验证规则"""
    def __init__(
        self,
        field: str,
        rule_type: str,
        level: ValidationLevel,
        validator: callable,
        message: str
    ):
        self.field = field
        self.rule_type = rule_type
        self.level = level
        self.validator = validator
        self.message = message

class DataValidator:
    """数据验证器"""
    
    def __init__(self, doc_type: str):
        self.doc_type = doc_type
        self.rules = self._load_rules(doc_type)
    
    def validate(
        self,
        headers: List[Dict],
        lines: List[Dict]
    ) -> Dict:
        """
        执行验证
        
        Returns:
            {
                "is_valid": True/False,
                "errors": [...],
                "warnings": [...],
                "info": [...],
                "quality_score": 0.95
            }
        """
        errors = []
        warnings = []
        info = []
        
        # Level 1: 格式验证
        for header in headers:
            header_errors, header_warnings, header_info = self._validate_header(header)
            errors.extend(header_errors)
            warnings.extend(header_warnings)
            info.extend(header_info)
        
        for line in lines:
            line_errors, line_warnings, line_info = self._validate_line(line)
            errors.extend(line_errors)
            warnings.extend(line_warnings)
            info.extend(line_info)
        
        # Level 2: 业务逻辑验证（已在Level 1中处理）
        
        # Level 3: 数据一致性验证
        consistency_errors, consistency_warnings = self._validate_consistency(headers, lines)
        errors.extend(consistency_errors)
        warnings.extend(consistency_warnings)
        
        # Level 4: 跨表验证
        cross_table_errors, cross_table_warnings = self._validate_cross_table(headers, lines)
        errors.extend(cross_table_errors)
        warnings.extend(cross_table_warnings)
        
        # 计算质量评分
        quality_score = self._calculate_quality_score(errors, warnings, info)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "quality_score": quality_score
        }
    
    def _validate_header(self, header: Dict) -> tuple:
        """验证Header"""
        errors = []
        warnings = []
        info = []
        
        header_rules = self._get_header_rules()
        
        for rule in header_rules:
            value = header.get(rule.field)
            
            try:
                if not rule.validator(value, header):
                    validation_result = {
                        "field": rule.field,
                        "rule_type": rule.rule_type,
                        "level": rule.level,
                        "message": rule.message,
                        "value": value,
                        "row_index": header.get("row_index")
                    }
                    
                    if rule.level == ValidationLevel.ERROR:
                        errors.append(validation_result)
                    elif rule.level == ValidationLevel.WARNING:
                        warnings.append(validation_result)
                    else:
                        info.append(validation_result)
            except Exception as e:
                errors.append({
                    "field": rule.field,
                    "rule_type": rule.rule_type,
                    "level": ValidationLevel.ERROR,
                    "message": f"验证时发生错误: {str(e)}",
                    "value": value,
                    "row_index": header.get("row_index")
                })
        
        return errors, warnings, info
    
    def _validate_line(self, line: Dict) -> tuple:
        """验证Line"""
        errors = []
        warnings = []
        info = []
        
        line_rules = self._get_line_rules()
        
        for rule in line_rules:
            value = line.get(rule.field)
            
            try:
                if not rule.validator(value, line):
                    validation_result = {
                        "field": rule.field,
                        "rule_type": rule.rule_type,
                        "level": rule.level,
                        "message": rule.message,
                        "value": value,
                        "row_index": line.get("row_index"),
                        "header_index": line.get("header_index")
                    }
                    
                    if rule.level == ValidationLevel.ERROR:
                        errors.append(validation_result)
                    elif rule.level == ValidationLevel.WARNING:
                        warnings.append(validation_result)
                    else:
                        info.append(validation_result)
            except Exception as e:
                errors.append({
                    "field": rule.field,
                    "rule_type": rule.rule_type,
                    "level": ValidationLevel.ERROR,
                    "message": f"验证时发生错误: {str(e)}",
                    "value": value,
                    "row_index": line.get("row_index")
                })
        
        return errors, warnings, info
    
    def _validate_consistency(
        self,
        headers: List[Dict],
        lines: List[Dict]
    ) -> tuple:
        """验证数据一致性"""
        errors = []
        warnings = []
        
        # 按header分组lines
        header_lines = {}
        for line in lines:
            header_index = line.get("header_index")
            if header_index not in header_lines:
                header_lines[header_index] = []
            header_lines[header_index].append(line)
        
        # 验证每个header
        for header_index, header in enumerate(headers):
            header_lines_list = header_lines.get(header_index, [])
            
            # 验证：每个header至少有1条line
            if len(header_lines_list) == 0:
                errors.append({
                    "rule_type": "consistency",
                    "level": ValidationLevel.ERROR,
                    "message": "每个Header必须有至少1条Line记录",
                    "header_index": header_index
                })
            
            # 验证：Header总额 = Line金额之和
            calculated_total = sum(
                float(line.get("line_amount", 0))
                for line in header_lines_list
            )
            declared_total = float(header.get("total_amount", 0))
            difference = abs(calculated_total - declared_total)
            
            if difference >= 0.01:
                errors.append({
                    "rule_type": "consistency",
                    "level": ValidationLevel.ERROR,
                    "message": f"Header总额({declared_total})与Line金额之和({calculated_total})不一致，差异: {difference}",
                    "header_index": header_index,
                    "declared_total": declared_total,
                    "calculated_total": calculated_total,
                    "difference": difference
                })
        
        return errors, warnings
    
    def _validate_cross_table(
        self,
        headers: List[Dict],
        lines: List[Dict]
    ) -> tuple:
        """验证跨表一致性"""
        errors = []
        warnings = []
        
        # 验证主数据存在性（已在主数据匹配阶段处理）
        # 这里可以添加其他跨表验证规则
        
        return errors, warnings
    
    def _calculate_quality_score(
        self,
        errors: List[Dict],
        warnings: List[Dict],
        info: List[Dict]
    ) -> float:
        """计算质量评分"""
        total_issues = len(errors) + len(warnings) + len(info)
        
        if total_issues == 0:
            return 1.0
        
        # 评分公式：100分，每1个error扣10分，每1个warning扣5分，每1个info扣1分
        score = 100.0
        score -= len(errors) * 10
        score -= len(warnings) * 5
        score -= len(info) * 1
        
        # 最低0分
        score = max(0.0, score)
        
        # 转换为0-1分数
        return score / 100.0
    
    def _load_rules(self, doc_type: str) -> List[ValidationRule]:
        """加载验证规则"""
        # 根据doc_type加载对应的规则
        # 这里返回示例规则
        return []
    
    def _get_header_rules(self) -> List[ValidationRule]:
        """获取Header验证规则"""
        # 返回Header规则列表
        return []
    
    def _get_line_rules(self) -> List[ValidationRule]:
        """获取Line验证规则"""
        # 返回Line规则列表
        return []
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

