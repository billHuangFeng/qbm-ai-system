# 数据导入完善系统 - 第3阶段快速开始

**创建时间**: 2025-01-23  
**版本**: 1.0  

---

## 📦 安装依赖

```bash
cd backend
pip install fuzzywuzzy python-Levenshtein pypinyin scikit-learn pandas numpy asyncpg
```

---

## 🚀 已完成的服务

### ✅ 1. 主数据匹配服务
**文件**: `backend/src/services/data_enhancement/master_data_matcher.py`

**使用示例**:
```python
from backend.src.services.data_enhancement import MasterDataMatcher
from backend.src.security.database import SecureDatabaseService

# 初始化服务
db_service = SecureDatabaseService(database_url)
await db_service.initialize()
matcher = MasterDataMatcher(db_service)

# 匹配主数据
records = [
    {"row_index": 0, "name": "北京科技有限公司", "credit_code": "91110000123456789X"},
    {"row_index": 1, "name": "上海贸易公司", "credit_code": None}
]

result = await matcher.match_master_data(
    data_type="order",
    records=records,
    master_data_table="customer_master",
    tenant_id="tenant_001",
    confidence_threshold=0.8
)

print(result["statistics"])
```

### ✅ 2. 计算冲突检测服务
**文件**: `backend/src/services/data_enhancement/calculation_conflict_detector.py`

**使用示例**:
```python
from backend.src.services.data_enhancement import CalculationConflictDetector

detector = CalculationConflictDetector(db_service)

calculation_rules = [
    {"formula": "订单金额 = 数量 × 单价"},
    {"formula": "税额 = 订单金额 × 税率"}
]

records = [
    {"row_index": 0, "数量": 10, "单价": 100, "订单金额": 1000},
    {"row_index": 1, "数量": 20, "单价": 50, "订单金额": 950}  # 冲突：应该是1000
]

result = await detector.detect_conflicts(
    data_type="order",
    records=records,
    calculation_rules=calculation_rules,
    tolerance=0.01
)

print(f"发现 {result['statistics']['conflicts_found']} 个冲突")
```

### ✅ 3. 智能补值服务
**文件**: `backend/src/services/data_enhancement/smart_value_imputer.py`

**使用示例**:
```python
from backend.src.services.data_enhancement import SmartValueImputer

imputer = SmartValueImputer(db_service)

field_configs = {
    "单价": {"field_type": "numeric", "default_value": None},
    "币种": {"field_type": "categorical", "rule_name": "currency"}
}

records = [
    {"单价": 100, "币种": "CNY"},
    {"单价": None, "币种": None},  # 缺失值
    {"单价": 200, "币种": "USD"}
]

result = await imputer.impute_values(
    data_type="order",
    records=records,
    field_configs=field_configs,
    strategy="auto"
)

print(f"补值了 {result['statistics']['imputed_count']} 个值")
```

---

## ⏳ 待完成的服务

### 4. 数据质量评估服务 (data_quality_assessor.py)
**状态**: 基于现有的 `data_quality_service.py` 进行适配
**预计**: 需要根据文档要求进行7维度质量检查的实现

### 5. 暂存表管理服务 (staging_table_manager.py)
**状态**: 待创建
**预计**: 200行代码

---

## 📝 下一步

1. 完成数据质量评估服务的适配
2. 创建暂存表管理服务
3. 创建API端点
4. 编写单元测试
5. 编写API文档

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23

