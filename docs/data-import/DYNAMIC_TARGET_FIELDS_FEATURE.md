# 动态获取目标字段功能说明

**创建时间**: 2025-01-22  
**状态**: ✅ **已实现**

---

## 📋 功能概述

Cursor已经在后端实现了**根据导入目标表动态获取目标字段**的功能。该功能通过查询PostgreSQL的`information_schema`系统表，动态获取目标表的所有字段，用于智能字段映射推荐。

---

## ✅ 已实现的功能

### 1. 核心实现 (`IntelligentFieldMapper`类)

**文件位置**: `backend/src/services/data_enhancement/intelligent_field_mapper.py`

#### 1.1 `_get_target_table_fields` 方法

```python
async def _get_target_table_fields(
    self,
    target_table: str,
    use_cache: bool = True
) -> List[str]:
    """获取目标表的所有字段名（带缓存）
    
    Args:
        target_table: 目标表名
        use_cache: 是否使用缓存（默认True）
    
    Returns:
        字段名列表
    
    Raises:
        ValueError: 如果数据库服务不可用或查询失败
    """
    # 查询PostgreSQL系统表获取列信息
    query_sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = :table_name
          AND table_schema = 'public'
        ORDER BY ordinal_position
    """
    results = await self.db_service.fetch_all(query_sql, {
        'table_name': target_table
    })
    
    field_names = [row['column_name'] for row in results]
    return field_names
```

**功能特点**:
- ✅ 动态查询数据库表结构
- ✅ 支持缓存（内存缓存 + Redis缓存）
- ✅ 缓存TTL: 24小时（表结构变化不频繁）
- ✅ 按字段顺序返回（`ordinal_position`）

#### 1.2 `_get_standard_fields_from_db` 方法

```python
async def _get_standard_fields_from_db(
    self,
    target_table: str,
    document_type: Optional[str] = None,
    use_cache: bool = True
) -> List[str]:
    """从数据库获取标准字段列表（带缓存）
    
    包括：
    1. 目标表的所有字段
    2. 主数据匹配字段（通过外键关联）
    """
    standard_fields = []
    
    # 并发查询：同时获取表字段和主数据匹配字段
    table_fields_task = self._get_target_table_fields(target_table, use_cache)
    master_data_fields_task = self._get_master_data_match_fields(
        target_table, document_type, use_cache
    )
    
    # 等待两个任务完成
    table_fields, master_data_fields = await asyncio.gather(
        table_fields_task,
        master_data_fields_task,
        return_exceptions=True
    )
    
    standard_fields.extend(table_fields)
    standard_fields.extend(master_data_fields)
    
    return list(set(standard_fields))  # 去重
```

**功能特点**:
- ✅ 并发查询表字段和主数据匹配字段
- ✅ 自动识别主数据ID字段（通过外键约束）
- ✅ 返回主数据表的匹配字段（如`entity_name`, `credit_code`）

#### 1.3 `recommend_mappings` 方法

```python
async def recommend_mappings(
    self,
    source_fields: List[str],
    source_system: str,
    target_table: str,  # 必需参数，用于动态获取字段
    document_type: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> List[FieldMappingRecommendation]:
    """推荐字段映射
    
    Args:
        source_fields: 源文件字段列表
        source_system: 数据源系统
        target_table: 目标表名（必需，用于动态获取字段）
        document_type: 单据类型
        user_id: 用户ID（可选）
        context: 额外上下文信息
    
    Returns:
        映射推荐列表
    """
    if not target_table:
        raise ValueError("target_table 是必需的，必须提供目标表名以从数据库获取字段")
    
    # 从数据库动态获取标准字段列表（使用缓存）
    standard_fields = await self._get_standard_fields_from_db(
        target_table, document_type, use_cache=True
    )
    
    # 对每个源字段推荐映射
    for source_field in source_fields:
        # 使用standard_fields进行相似度匹配
        # ...
```

**功能特点**:
- ✅ 必须提供`target_table`参数
- ✅ 自动从数据库获取目标表字段
- ✅ 支持历史映射、规则匹配、相似度计算

---

## 📊 缓存策略

### 缓存层级

1. **内存缓存**（进程内缓存）
   - 缓存键: `{target_table}:fields`
   - 生命周期: 进程生命周期
   - 用途: 快速访问

2. **Redis缓存**（分布式缓存）
   - 缓存键: `field_mapper:table_fields:{target_table}`
   - TTL: 24小时（86400秒）
   - 用途: 跨进程共享

### 缓存更新

- **自动更新**: 查询时如果缓存不存在，自动查询并更新
- **手动清除**: 支持手动清除缓存（表结构变更后）

---

## 🔌 API端点

### 当前状态

**❌ 问题**: 目前没有专门的API端点暴露"获取目标表字段"功能

**✅ 已实现**: `recommend_mappings`方法内部会调用`_get_target_table_fields`，但这是内部方法

### 建议添加的API端点

```python
# 建议在 data_enhancement.py 中添加

@router.get("/target-table-fields")
async def get_target_table_fields(
    target_table: str,
    document_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_service: SecureDatabaseService = Depends(get_db_service)
):
    """获取目标表的字段列表
    
    Args:
        target_table: 目标表名（如 'sales_order_header'）
        document_type: 单据类型（可选，用于获取主数据匹配字段）
    
    Returns:
        {
            "table_fields": ["id", "order_number", "order_date", ...],
            "master_data_fields": ["customer_name", "customer_code", ...],
            "all_fields": [...]
        }
    """
    from ...services.data_enhancement.intelligent_field_mapper import IntelligentFieldMapper
    
    mapper = IntelligentFieldMapper(db_service)
    
    # 获取表字段
    table_fields = await mapper._get_target_table_fields(target_table)
    
    # 获取主数据匹配字段
    master_data_fields = await mapper._get_master_data_match_fields(
        target_table, document_type
    )
    
    return {
        "table_fields": table_fields,
        "master_data_fields": master_data_fields,
        "all_fields": list(set(table_fields + master_data_fields))
    }
```

---

## 📝 使用示例

### 后端使用示例

```python
from src.services.data_enhancement.intelligent_field_mapper import IntelligentFieldMapper

# 初始化映射器
mapper = IntelligentFieldMapper(db_service)

# 获取目标表字段
target_fields = await mapper._get_target_table_fields('sales_order_header')
# 返回: ['id', 'tenant_id', 'order_number', 'order_date', 'customer_id', ...]

# 推荐字段映射
recommendations = await mapper.recommend_mappings(
    source_fields=['订单号', '客户名称', '订单日期'],
    source_system='ERP_SYSTEM_A',
    target_table='sales_order_header',  # 必需参数
    document_type='SO'
)
```

### 前端调用示例（需要添加API端点后）

```typescript
// 获取目标表字段
const response = await fetch('/api/v1/data-enhancement/target-table-fields', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  params: {
    target_table: 'sales_order_header',
    document_type: 'SO'
  }
});

const { table_fields, master_data_fields, all_fields } = await response.json();

// 使用字段列表进行字段映射
// ...
```

---

## ✅ 功能完整性评估

| 功能项 | 状态 | 说明 |
|--------|------|------|
| 动态查询表结构 | ✅ 已实现 | 通过`information_schema.columns`查询 |
| 缓存机制 | ✅ 已实现 | 内存缓存 + Redis缓存 |
| 主数据字段识别 | ✅ 已实现 | 通过外键约束自动识别 |
| API端点暴露 | ❌ 未实现 | 需要添加API端点 |
| 字段类型信息 | ⚠️ 部分实现 | 目前只返回字段名，不返回类型 |

---

## 🔧 建议改进

### 1. 添加API端点

**优先级**: 高

添加专门的API端点，让前端可以动态获取目标表字段：

```python
GET /api/v1/data-enhancement/target-table-fields?target_table={table_name}&document_type={doc_type}
```

### 2. 返回字段详细信息

**优先级**: 中

不仅返回字段名，还返回字段类型、是否必填、默认值等信息：

```python
{
    "table_fields": [
        {
            "name": "order_number",
            "type": "VARCHAR(50)",
            "nullable": False,
            "default": None,
            "is_primary_key": False,
            "is_foreign_key": False
        },
        ...
    ]
}
```

### 3. 支持Header和Line字段分离

**优先级**: 高

根据单据类型，自动区分Header字段和Line字段：

```python
{
    "header_fields": [...],
    "line_fields": [...],
    "all_fields": [...]
}
```

---

## 📚 相关文档

- `docs/data-import/DOCUMENT_TYPES_SPECIFICATION.md` - 单据类型规范
- `docs/data-import/DATABASE_SCHEMA_DESIGN.md` - 数据库设计
- `docs/data-import/FASTAPI_API_DESIGN.md` - FastAPI API设计

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

