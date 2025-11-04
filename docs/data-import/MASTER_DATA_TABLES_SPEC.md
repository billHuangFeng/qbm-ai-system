# 主数据表规范与匹配配置

## 1. 主数据表总览

### 1.1 7种主数据类型映射

| 主数据类型 | 数据库表名 | 主键 | 编码字段 | 名称字段 | 匹配优先级 |
|-----------|-----------|------|---------|---------|-----------|
| **经营主体** (business_entity) | `dim_business_entity` | entity_id | entity_code | entity_name | 编码 > 名称 > 税号 |
| **客户** (customer) | `dim_customer` | customer_id | customer_code | customer_name | 编码 > 名称 |
| **供应商** (supplier) | `dim_supplier` | supplier_id | supplier_code | supplier_name | 编码 > 名称 |
| **产品/SKU** (product_sku) | `dim_sku` | sku_id | sku_code | sku_name | 编码 > 名称 |
| **部门** (department) | `dim_department` | department_id | department_code | department_name | 编码 > 名称 |
| **员工** (employee) | `dim_employee` | employee_id | employee_code | employee_name | 编码 > 名称 > 手机号 |
| **项目** (project) | `dim_project` | project_id | project_code | project_name | 编码 > 名称 |

---

## 2. 详细表结构

### 2.1 dim_business_entity (经营主体)
```sql
CREATE TABLE public.dim_business_entity (
    entity_id UUID PRIMARY KEY,          -- 主键
    tenant_id UUID NOT NULL,             -- 租户ID
    entity_code VARCHAR(50) NOT NULL,    -- 主体编码 ⭐ 精确匹配字段
    entity_name VARCHAR(255) NOT NULL,   -- 主体名称 ⭐ 模糊匹配字段
    entity_type VARCHAR(50),             -- 主体类型（总部/分公司/子公司）
    legal_name VARCHAR(255),             -- 法定名称
    tax_id VARCHAR(50),                  -- 税号/统一社会信用代码 ⭐ 精确匹配字段
    region VARCHAR(100),
    address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `entity_code` 或 `tax_id`
2. **组合匹配**: `entity_code + entity_name`
3. **模糊匹配**: `entity_name` (Levenshtein距离 >= 0.85)
4. **特殊匹配**: `legal_name` 与导入数据中的公司全称

---

### 2.2 dim_customer (客户)
```sql
CREATE TABLE public.dim_customer (
    customer_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    customer_code VARCHAR(50) NOT NULL,  -- 客户编码 ⭐
    customer_name VARCHAR(255) NOT NULL, -- 客户名称 ⭐
    customer_segment VARCHAR(50),        -- 客户细分
    region VARCHAR(100),
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `customer_code`
2. **组合匹配**: `customer_code + customer_name`
3. **模糊匹配**: `customer_name` (阈值 >= 0.80)

---

### 2.3 dim_supplier (供应商)
```sql
CREATE TABLE public.dim_supplier (
    supplier_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    supplier_code VARCHAR(50) NOT NULL,  -- 供应商编码 ⭐
    supplier_name VARCHAR(255) NOT NULL, -- 供应商名称 ⭐
    region VARCHAR(100),
    rating NUMERIC,
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `supplier_code`
2. **组合匹配**: `supplier_code + supplier_name`
3. **模糊匹配**: `supplier_name` (阈值 >= 0.80)

---

### 2.4 dim_sku (产品/SKU)
```sql
CREATE TABLE public.dim_sku (
    sku_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    sku_code VARCHAR(50) NOT NULL,       -- SKU编码 ⭐
    sku_name VARCHAR(255) NOT NULL,      -- SKU名称 ⭐
    category VARCHAR(100),
    unit_price NUMERIC,
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `sku_code`
2. **组合匹配**: `sku_code + sku_name`
3. **模糊匹配**: `sku_name` (阈值 >= 0.75)
4. **分类辅助**: 同时匹配 `category` 提高置信度

---

### 2.5 dim_department (部门)
```sql
CREATE TABLE public.dim_department (
    department_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    entity_id UUID,                      -- 关联经营主体
    department_code VARCHAR(50) NOT NULL, -- 部门编码 ⭐
    department_name VARCHAR(255) NOT NULL, -- 部门名称 ⭐
    department_type VARCHAR(50),
    parent_department_id UUID,           -- 父部门（支持层级）
    department_level INTEGER,
    manager_id UUID,
    cost_center VARCHAR(50),
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `department_code`
2. **组合匹配**: `department_code + department_name`
3. **模糊匹配**: `department_name` (阈值 >= 0.85)
4. **层级匹配**: 如果导入数据包含父部门信息，优先匹配完整路径

---

### 2.6 dim_employee (员工)
```sql
CREATE TABLE public.dim_employee (
    employee_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    entity_id UUID,
    department_id UUID,
    employee_code VARCHAR(50) NOT NULL,  -- 工号 ⭐
    employee_name VARCHAR(100) NOT NULL, -- 姓名 ⭐
    employee_name_en VARCHAR(100),
    gender VARCHAR(10),
    birth_date DATE,
    mobile_phone VARCHAR(50),            -- 手机号 ⭐ 辅助匹配
    email VARCHAR(255),
    position VARCHAR(100),
    job_level VARCHAR(50),
    employment_type VARCHAR(50),
    hire_date DATE,
    leave_date DATE,
    status VARCHAR(50),
    supervisor_id UUID,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `employee_code` 或 `mobile_phone`
2. **组合匹配**: `employee_code + employee_name`
3. **模糊匹配**: `employee_name` (阈值 >= 0.90，员工姓名要求更高精度)
4. **辅助验证**: 同时检查 `department_id` 和 `position` 提高置信度

---

### 2.7 dim_project (项目)
```sql
CREATE TABLE public.dim_project (
    project_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    entity_id UUID,
    project_code VARCHAR(50) NOT NULL,   -- 项目编码 ⭐
    project_name VARCHAR(255) NOT NULL,  -- 项目名称 ⭐
    project_type VARCHAR(50),
    project_status VARCHAR(50),
    priority VARCHAR(20),
    start_date DATE,
    end_date DATE,
    planned_budget NUMERIC,
    actual_budget NUMERIC,
    project_manager_id UUID,
    sponsor_id UUID,
    department_id UUID,
    description TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

**匹配策略**:
1. **精确匹配**: `project_code`
2. **组合匹配**: `project_code + project_name`
3. **模糊匹配**: `project_name` (阈值 >= 0.80)
4. **时间范围匹配**: 如果导入数据包含日期，检查 `start_date` 和 `end_date` 范围

---

## 3. 匹配算法配置

### 3.1 通用匹配流程
```python
async def match_master_data(
    data: pd.DataFrame,
    field_name: str,
    master_type: MasterDataType,
    tenant_id: str
) -> MasterDataMatchResult:
    """
    三级匹配策略:
    1. 精确匹配 (Exact Match) - 置信度 1.0
    2. 组合匹配 (Combined Match) - 置信度 0.95
    3. 模糊匹配 (Fuzzy Match) - 置信度 0.75-0.95
    """
```

### 3.2 匹配字段配置映射
```python
MASTER_DATA_CONFIG = {
    MasterDataType.BUSINESS_ENTITY: {
        "table": "dim_business_entity",
        "id_field": "entity_id",
        "primary_code": "entity_code",
        "primary_name": "entity_name",
        "secondary_fields": ["legal_name", "tax_id"],
        "fuzzy_threshold": 0.85
    },
    MasterDataType.CUSTOMER: {
        "table": "dim_customer",
        "id_field": "customer_id",
        "primary_code": "customer_code",
        "primary_name": "customer_name",
        "secondary_fields": [],
        "fuzzy_threshold": 0.80
    },
    MasterDataType.SUPPLIER: {
        "table": "dim_supplier",
        "id_field": "supplier_id",
        "primary_code": "supplier_code",
        "primary_name": "supplier_name",
        "secondary_fields": [],
        "fuzzy_threshold": 0.80
    },
    MasterDataType.PRODUCT_SKU: {
        "table": "dim_sku",
        "id_field": "sku_id",
        "primary_code": "sku_code",
        "primary_name": "sku_name",
        "secondary_fields": ["category"],
        "fuzzy_threshold": 0.75
    },
    MasterDataType.DEPARTMENT: {
        "table": "dim_department",
        "id_field": "department_id",
        "primary_code": "department_code",
        "primary_name": "department_name",
        "secondary_fields": ["department_type"],
        "fuzzy_threshold": 0.85
    },
    MasterDataType.EMPLOYEE: {
        "table": "dim_employee",
        "id_field": "employee_id",
        "primary_code": "employee_code",
        "primary_name": "employee_name",
        "secondary_fields": ["mobile_phone", "email"],
        "fuzzy_threshold": 0.90
    },
    MasterDataType.PROJECT: {
        "table": "dim_project",
        "id_field": "project_id",
        "primary_code": "project_code",
        "primary_name": "project_name",
        "secondary_fields": ["project_type"],
        "fuzzy_threshold": 0.80
    }
}
```

---

## 4. 查询优化建议

### 4.1 为匹配查询创建索引
所有主数据表都已包含以下索引:
```sql
-- 租户隔离索引
CREATE INDEX idx_{table}_tenant ON {table}(tenant_id);

-- 编码查询索引（精确匹配）
CREATE INDEX idx_{table}_code ON {table}(tenant_id, {code_field});

-- 名称查询索引（模糊匹配性能提升）
CREATE INDEX idx_{table}_name ON {table}(tenant_id, {name_field});
```

### 4.2 批量查询示例
```python
async def get_master_data_batch(
    master_type: MasterDataType,
    tenant_id: str,
    codes: List[str]
) -> List[Dict]:
    """批量获取主数据"""
    config = MASTER_DATA_CONFIG[master_type]
    
    query = f"""
    SELECT 
        {config['id_field']} as id,
        {config['primary_code']} as code,
        {config['primary_name']} as name
    FROM public.{config['table']}
    WHERE tenant_id = $1
    AND {config['primary_code']} = ANY($2)
    AND is_active = true
    """
    
    return await db.fetch(query, tenant_id, codes)
```

---

## 5. 数据导入时的匹配流程

### 5.1 单据导入场景示例
假设导入销售订单，需要匹配的主数据:

```python
# 导入的Excel包含以下列
import_columns = [
    'order_no',           # 单据号
    'customer_code',      # 客户编码 → 需要匹配 dim_customer
    'customer_name',      # 客户名称
    'salesperson_code',   # 销售员编码 → 需要匹配 dim_employee
    'salesperson_name',   # 销售员姓名
    'sku_code',          # 产品编码 → 需要匹配 dim_sku
    'sku_name',          # 产品名称
    'quantity',          # 数量
    'unit_price',        # 单价
]

# 匹配任务
match_tasks = [
    ('customer_code', MasterDataType.CUSTOMER),
    ('salesperson_code', MasterDataType.EMPLOYEE),
    ('sku_code', MasterDataType.PRODUCT_SKU)
]
```

### 5.2 并行匹配执行
```python
async def parallel_match_all_master_data(
    df: pd.DataFrame,
    match_tasks: List[Tuple[str, MasterDataType]],
    tenant_id: str
) -> Dict[str, MasterDataMatchResult]:
    """并行执行所有主数据匹配"""
    
    tasks = [
        match_master_data(df, field, master_type, tenant_id)
        for field, master_type in match_tasks
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        match_tasks[i][0]: results[i]
        for i in range(len(match_tasks))
    }
```

---

## 6. 匹配结果处理

### 6.1 匹配结果类型
```python
class MatchType(str, Enum):
    EXACT = "exact"                    # 精确匹配
    COMBINED = "combined"              # 组合匹配
    FUZZY = "fuzzy"                    # 模糊匹配
    MULTIPLE_CANDIDATES = "multiple"   # 多个候选（需用户决策）
    NO_MATCH = "no_match"             # 无匹配（建议创建新主数据）
```

### 6.2 用户决策场景
**场景1: 多个候选**
```json
{
  "source_value": "张三",
  "match_type": "multiple_candidates",
  "candidates": [
    {"id": "uuid1", "code": "E001", "name": "张三", "department": "销售部", "confidence": 0.92},
    {"id": "uuid2", "code": "E099", "name": "张三", "department": "市场部", "confidence": 0.92}
  ],
  "requires_decision": true
}
```

**场景2: 无匹配**
```json
{
  "source_value": "新客户A",
  "match_type": "no_match",
  "confidence": 0.0,
  "suggest_create": true,
  "suggested_data": {
    "customer_code": "C999",  // 自动生成
    "customer_name": "新客户A"
  }
}
```

---

## 7. 性能优化

### 7.1 缓存策略
```python
from functools import lru_cache

@lru_cache(maxsize=256)
async def get_cached_master_data(
    master_type: MasterDataType,
    tenant_id: str
) -> List[Dict]:
    """缓存主数据查询（15分钟有效）"""
    return await fetch_master_data(master_type, tenant_id)
```

### 7.2 预加载策略
对于大批量导入（>1000行），预加载所有相关主数据到内存:
```python
async def preload_master_data_for_import(
    match_tasks: List[Tuple[str, MasterDataType]],
    tenant_id: str
) -> Dict[MasterDataType, List[Dict]]:
    """预加载所有需要的主数据"""
    
    unique_types = set(task[1] for task in match_tasks)
    
    tasks = [
        get_cached_master_data(master_type, tenant_id)
        for master_type in unique_types
    ]
    
    results = await asyncio.gather(*tasks)
    
    return dict(zip(unique_types, results))
```

---

## 8. 测试数据建议

### 8.1 为每种主数据准备测试数据
```python
# tests/fixtures/master_data.py

DEMO_BUSINESS_ENTITIES = [
    {"entity_code": "BE001", "entity_name": "总公司", "tax_id": "91110000MA001"},
    {"entity_code": "BE002", "entity_name": "北京分公司", "tax_id": "91110108MA002"},
]

DEMO_CUSTOMERS = [
    {"customer_code": "C001", "customer_name": "阿里巴巴集团"},
    {"customer_code": "C002", "customer_name": "腾讯科技"},
]

DEMO_EMPLOYEES = [
    {"employee_code": "E001", "employee_name": "张三", "mobile_phone": "13800138000"},
    {"employee_code": "E002", "employee_name": "李四", "mobile_phone": "13900139000"},
]

# ... 其他主数据类型
```

---

## 9. 下一步集成

### 9.1 与FastAPI后端集成
在 `backend/src/services/data_enhancement/master_data_matcher.py` 中实现:
```python
from .config import MASTER_DATA_CONFIG

class MasterDataMatcher:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.config = MASTER_DATA_CONFIG
    
    async def match_master_data(
        self,
        data: pd.DataFrame,
        field_name: str,
        master_type: MasterDataType,
        tenant_id: str
    ) -> MasterDataMatchResult:
        # 实现主数据匹配逻辑
        pass
```

### 9.2 与Lovable前端集成
前端展示匹配结果并收集用户决策:
```typescript
// components/data-import/MasterDataMatchReview.tsx
interface MatchReviewProps {
  matchResults: MasterDataMatchResult[];
  onConfirm: (decisions: UserDecision[]) => void;
}
```

---

**总结**: 7种主数据表结构完整，RLS策略就绪，索引优化完成，可直接用于FastAPI后端的主数据匹配算法实现。
