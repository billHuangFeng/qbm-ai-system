# 单据类型规范文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P0 - 必需文档**

---

## 📋 文档目的

定义系统中支持的6种单据类型的完整规范，包括字段定义、业务规则、主数据关联关系，供Lovable实施数据导入功能使用。

---

## 1. 单据类型总览

系统支持以下6种单据类型：

| 单据类型 | 英文代码 | 中文名称 | Header表 | Line表 | 业务流程 |
|---------|---------|---------|---------|--------|---------|
| **销售订单** | SO | Sales Order | `sales_order_header` | `sales_order_line` | 销售流程 |
| **发货单** | SH | Shipment | `shipment_header` | `shipment_line` | 销售流程 |
| **销售发票** | SI | Sales Invoice | `sales_invoice_header` | `sales_invoice_line` | 销售流程 |
| **采购订单** | PO | Purchase Order | `purchase_order_header` | `purchase_order_line` | 采购流程 |
| **收货单** | RC | Receipt | `receipt_header` | `receipt_line` | 采购流程 |
| **采购发票** | PI | Purchase Invoice | `purchase_invoice_header` | `purchase_invoice_line` | 采购流程 |

---

## 2. 销售订单 (Sales Order, SO)

### 2.1 Header字段定义

**表名**: `sales_order_header`

**必填字段**:
- `order_date`: 订单日期 (DATE, 必填)
- `customer_id`: 客户ID (UUID, 必填，通过主数据匹配)
- `customer_name`: 客户名称 (VARCHAR(255), 冗余字段，用于匹配)
- `customer_code`: 客户代码 (VARCHAR(50), 冗余字段，用于匹配)

**可选字段**:
- `order_number`: 订单号 (VARCHAR(50), 唯一，可自动生成)
- `channel_id`: 渠道ID (UUID, 可选)
- `order_status`: 订单状态 (VARCHAR(20), 默认'draft')
- `total_amount`: 总金额 (DECIMAL(18,2), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2), 默认0)
- `currency_code`: 币种 (VARCHAR(10), 默认'CNY')
- `payment_term`: 付款条件 (VARCHAR(50))
- `delivery_address`: 交付地址 (TEXT)
- `contact_person`: 联系人 (VARCHAR(100))
- `contact_phone`: 联系电话 (VARCHAR(50))
- `remark`: 备注 (TEXT)

**系统字段**:
- `order_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)
- `approved_by`: 审批人 (UUID)
- `approved_at`: 审批时间 (TIMESTAMPTZ)

### 2.2 Line字段定义

**表名**: `sales_order_line`

**必填字段**:
- `order_id`: 订单头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填，通过主数据匹配)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段，用于匹配)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段，用于匹配)
- `quantity`: 数量 (DECIMAL(18,3), 必填，>0)
- `unit_price`: 单价 (DECIMAL(18,2), 必填，>=0)

**可选字段**:
- `line_amount`: 行金额 (DECIMAL(18,2), 计算字段 = quantity × unit_price)
- `tax_rate`: 税率 (DECIMAL(5,4), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_rate`: 折扣率 (DECIMAL(5,4), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2))
- `requested_delivery_date`: 要求交付日期 (DATE)
- `promised_delivery_date`: 承诺交付日期 (DATE)
- `shipped_quantity`: 已发货数量 (DECIMAL(18,3), 默认0)
- `invoiced_quantity`: 已开票数量 (DECIMAL(18,3), 默认0)
- `line_status`: 行状态 (VARCHAR(20), 默认'open')
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 2.3 业务规则

1. **金额计算规则**:
   - `line_amount = quantity × unit_price`
   - `net_amount = line_amount - discount_amount`
   - `header.total_amount = SUM(line.line_amount)`
   - `header.net_amount = SUM(line.net_amount)`

2. **数量规则**:
   - `quantity > 0`
   - `unit_price >= 0`
   - `header.total_quantity = SUM(line.quantity)`

3. **关联规则**:
   - 每个header必须有至少1条line
   - `customer_id`必须匹配成功才能导入
   - `sku_id`必须匹配成功才能导入

4. **状态规则**:
   - `order_status`: draft → confirmed → in_progress → completed/cancelled
   - `line_status`: open → partial → closed/cancelled

### 2.4 主数据关联

**主数据匹配字段**:
- `customers`: `customer_name` / `customer_code` → `customer_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`
- `channels`: `channel_name` / `channel_code` → `channel_id` (可选)

---

## 3. 发货单 (Shipment, SH)

### 3.1 Header字段定义

**表名**: `shipment_header`

**必填字段**:
- `shipment_date`: 发货日期 (DATE, 必填)
- `customer_id`: 客户ID (UUID, 必填，通过主数据匹配)
- `customer_name`: 客户名称 (VARCHAR(255), 冗余字段)
- `customer_code`: 客户代码 (VARCHAR(50), 冗余字段)

**可选字段**:
- `shipment_number`: 发货单号 (VARCHAR(50), 唯一，可自动生成)
- `shipment_status`: 发货状态 (VARCHAR(20), 默认'draft')
- `carrier`: 承运商 (VARCHAR(100))
- `tracking_number`: 跟踪号 (VARCHAR(100))
- `shipping_method`: 发货方式 (VARCHAR(50))
- `delivery_address`: 交付地址 (TEXT)
- `contact_person`: 联系人 (VARCHAR(100))
- `contact_phone`: 联系电话 (VARCHAR(50))
- `planned_delivery_date`: 计划交付日期 (DATE)
- `actual_delivery_date`: 实际交付日期 (DATE)
- `remark`: 备注 (TEXT)

**系统字段**:
- `shipment_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 3.2 Line字段定义

**表名**: `shipment_line`

**必填字段**:
- `shipment_id`: 发货单头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段)
- `shipped_quantity`: 发货数量 (DECIMAL(18,3), 必填，>0)

**可选字段**:
- `source_order_id`: 源订单ID (UUID, 关联sales_order_header)
- `source_order_line_id`: 源订单行ID (UUID, 关联sales_order_line)
- `unit_price`: 单价 (DECIMAL(18,2))
- `line_status`: 行状态 (VARCHAR(20), 默认'pending')
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 3.3 业务规则

1. **数量规则**:
   - `shipped_quantity > 0`
   - `shipped_quantity <= source_order_line.quantity` (如果关联订单)

2. **关联规则**:
   - 每个header必须有至少1条line
   - `customer_id`必须匹配成功
   - `sku_id`必须匹配成功
   - 可选择关联源销售订单

### 3.4 主数据关联

**主数据匹配字段**:
- `customers`: `customer_name` / `customer_code` → `customer_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`

---

## 4. 销售发票 (Sales Invoice, SI)

### 4.1 Header字段定义

**表名**: `sales_invoice_header`

**必填字段**:
- `invoice_date`: 发票日期 (DATE, 必填)
- `customer_id`: 客户ID (UUID, 必填)
- `customer_name`: 客户名称 (VARCHAR(255), 冗余字段)
- `customer_code`: 客户代码 (VARCHAR(50), 冗余字段)

**可选字段**:
- `invoice_number`: 发票号 (VARCHAR(50), 唯一，可自动生成)
- `invoice_type`: 发票类型 (VARCHAR(20), 默认'standard')
- `invoice_status`: 发票状态 (VARCHAR(20), 默认'draft')
- `total_amount`: 总金额 (DECIMAL(18,2), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2), 默认0)
- `currency_code`: 币种 (VARCHAR(10), 默认'CNY')
- `payment_term`: 付款条件 (VARCHAR(50))
- `due_date`: 到期日期 (DATE)
- `paid_amount`: 已付金额 (DECIMAL(18,2), 默认0)
- `payment_status`: 付款状态 (VARCHAR(20), 默认'unpaid')
- `remark`: 备注 (TEXT)

**系统字段**:
- `invoice_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 4.2 Line字段定义

**表名**: `sales_invoice_line`

**必填字段**:
- `invoice_id`: 发票头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段)
- `quantity`: 数量 (DECIMAL(18,3), 必填，>0)
- `unit_price`: 单价 (DECIMAL(18,2), 必填，>=0)

**可选字段**:
- `source_order_id`: 源订单ID (UUID)
- `source_order_line_id`: 源订单行ID (UUID)
- `source_shipment_id`: 源发货单ID (UUID)
- `source_shipment_line_id`: 源发货单行ID (UUID)
- `line_amount`: 行金额 (DECIMAL(18,2))
- `tax_rate`: 税率 (DECIMAL(5,4), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2))
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 4.3 业务规则

1. **金额计算规则**:
   - `line_amount = quantity × unit_price`
   - `net_amount = line_amount - discount_amount`
   - `header.total_amount = SUM(line.line_amount)`
   - `header.net_amount = SUM(line.net_amount)`

2. **付款规则**:
   - `payment_status`: unpaid → partial → paid
   - `paid_amount <= net_amount`

3. **关联规则**:
   - 每个header必须有至少1条line
   - `customer_id`必须匹配成功
   - `sku_id`必须匹配成功

### 4.4 主数据关联

**主数据匹配字段**:
- `customers`: `customer_name` / `customer_code` → `customer_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`

---

## 5. 采购订单 (Purchase Order, PO)

### 5.1 Header字段定义

**表名**: `purchase_order_header`

**必填字段**:
- `po_date`: 采购订单日期 (DATE, 必填)
- `supplier_id`: 供应商ID (UUID, 必填，通过主数据匹配)
- `supplier_name`: 供应商名称 (VARCHAR(255), 冗余字段)
- `supplier_code`: 供应商代码 (VARCHAR(50), 冗余字段)

**可选字段**:
- `po_number`: 采购订单号 (VARCHAR(50), 唯一，可自动生成)
- `po_status`: 订单状态 (VARCHAR(20), 默认'draft')
- `total_amount`: 总金额 (DECIMAL(18,2), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2), 默认0)
- `currency_code`: 币种 (VARCHAR(10), 默认'CNY')
- `payment_term`: 付款条件 (VARCHAR(50))
- `delivery_address`: 交付地址 (TEXT)
- `contact_person`: 联系人 (VARCHAR(100))
- `contact_phone`: 联系电话 (VARCHAR(50))
- `remark`: 备注 (TEXT)

**系统字段**:
- `po_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)
- `approved_by`: 审批人 (UUID)
- `approved_at`: 审批时间 (TIMESTAMPTZ)

### 5.2 Line字段定义

**表名**: `purchase_order_line`

**必填字段**:
- `po_id`: 采购订单头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段)
- `quantity`: 数量 (DECIMAL(18,3), 必填，>0)
- `unit_price`: 单价 (DECIMAL(18,2), 必填，>=0)

**可选字段**:
- `line_amount`: 行金额 (DECIMAL(18,2))
- `tax_rate`: 税率 (DECIMAL(5,4), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2))
- `requested_delivery_date`: 要求交付日期 (DATE)
- `promised_delivery_date`: 承诺交付日期 (DATE)
- `received_quantity`: 已收货数量 (DECIMAL(18,3), 默认0)
- `invoiced_quantity`: 已开票数量 (DECIMAL(18,3), 默认0)
- `line_status`: 行状态 (VARCHAR(20), 默认'open')
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 5.3 业务规则

1. **金额计算规则**:
   - `line_amount = quantity × unit_price`
   - `net_amount = line_amount - discount_amount`
   - `header.total_amount = SUM(line.line_amount)`
   - `header.net_amount = SUM(line.net_amount)`

2. **数量规则**:
   - `quantity > 0`
   - `unit_price >= 0`
   - `received_quantity <= quantity`

3. **关联规则**:
   - 每个header必须有至少1条line
   - `supplier_id`必须匹配成功
   - `sku_id`必须匹配成功

### 5.4 主数据关联

**主数据匹配字段**:
- `suppliers`: `supplier_name` / `supplier_code` → `supplier_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`

---

## 6. 收货单 (Receipt, RC)

### 6.1 Header字段定义

**表名**: `receipt_header`

**必填字段**:
- `receipt_date`: 收货日期 (DATE, 必填)
- `supplier_id`: 供应商ID (UUID, 必填)
- `supplier_name`: 供应商名称 (VARCHAR(255), 冗余字段)
- `supplier_code`: 供应商代码 (VARCHAR(50), 冗余字段)

**可选字段**:
- `receipt_number`: 收货单号 (VARCHAR(50), 唯一，可自动生成)
- `receipt_status`: 收货状态 (VARCHAR(20), 默认'draft')
- `carrier`: 承运商 (VARCHAR(100))
- `tracking_number`: 跟踪号 (VARCHAR(100))
- `inspection_status`: 质检状态 (VARCHAR(20))
- `inspector`: 质检员 (UUID)
- `inspection_date`: 质检日期 (DATE)
- `remark`: 备注 (TEXT)

**系统字段**:
- `receipt_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 6.2 Line字段定义

**表名**: `receipt_line`

**必填字段**:
- `receipt_id`: 收货单头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段)
- `received_quantity`: 收货数量 (DECIMAL(18,3), 必填，>0)

**可选字段**:
- `source_po_id`: 源采购订单ID (UUID)
- `source_po_line_id`: 源采购订单行ID (UUID)
- `accepted_quantity`: 接收数量 (DECIMAL(18,3))
- `rejected_quantity`: 拒收数量 (DECIMAL(18,3))
- `unit_price`: 单价 (DECIMAL(18,2))
- `quality_status`: 质检状态 (VARCHAR(20))
- `quality_remark`: 质检备注 (TEXT)
- `line_status`: 行状态 (VARCHAR(20), 默认'pending')
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 6.3 业务规则

1. **数量规则**:
   - `received_quantity > 0`
   - `accepted_quantity + rejected_quantity = received_quantity`
   - `received_quantity <= source_po_line.quantity` (如果关联订单)

2. **关联规则**:
   - 每个header必须有至少1条line
   - `supplier_id`必须匹配成功
   - `sku_id`必须匹配成功

### 6.4 主数据关联

**主数据匹配字段**:
- `suppliers`: `supplier_name` / `supplier_code` → `supplier_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`

---

## 7. 采购发票 (Purchase Invoice, PI)

### 7.1 Header字段定义

**表名**: `purchase_invoice_header`

**必填字段**:
- `invoice_date`: 发票日期 (DATE, 必填)
- `supplier_id`: 供应商ID (UUID, 必填)
- `supplier_name`: 供应商名称 (VARCHAR(255), 冗余字段)
- `supplier_code`: 供应商代码 (VARCHAR(50), 冗余字段)

**可选字段**:
- `invoice_number`: 发票号 (VARCHAR(50), 唯一，可自动生成)
- `invoice_type`: 发票类型 (VARCHAR(20), 默认'standard')
- `invoice_status`: 发票状态 (VARCHAR(20), 默认'draft')
- `total_amount`: 总金额 (DECIMAL(18,2), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2), 默认0)
- `currency_code`: 币种 (VARCHAR(10), 默认'CNY')
- `payment_term`: 付款条件 (VARCHAR(50))
- `due_date`: 到期日期 (DATE)
- `paid_amount`: 已付金额 (DECIMAL(18,2), 默认0)
- `payment_status`: 付款状态 (VARCHAR(20), 默认'unpaid')
- `remark`: 备注 (TEXT)

**系统字段**:
- `invoice_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_by`: 创建人 (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 7.2 Line字段定义

**表名**: `purchase_invoice_line`

**必填字段**:
- `invoice_id`: 发票头ID (UUID, 外键，必填)
- `line_number`: 行号 (INTEGER, 必填)
- `sku_id`: SKU ID (UUID, 必填)
- `sku_code`: SKU代码 (VARCHAR(50), 冗余字段)
- `sku_name`: SKU名称 (VARCHAR(200), 冗余字段)
- `quantity`: 数量 (DECIMAL(18,3), 必填，>0)
- `unit_price`: 单价 (DECIMAL(18,2), 必填，>=0)

**可选字段**:
- `source_po_id`: 源采购订单ID (UUID)
- `source_po_line_id`: 源采购订单行ID (UUID)
- `source_receipt_id`: 源收货单ID (UUID)
- `source_receipt_line_id`: 源收货单行ID (UUID)
- `line_amount`: 行金额 (DECIMAL(18,2))
- `tax_rate`: 税率 (DECIMAL(5,4), 默认0)
- `tax_amount`: 税额 (DECIMAL(18,2), 默认0)
- `discount_amount`: 折扣金额 (DECIMAL(18,2), 默认0)
- `net_amount`: 净金额 (DECIMAL(18,2))
- `remark`: 行备注 (TEXT)

**系统字段**:
- `line_id`: 主键 (UUID)
- `tenant_id`: 租户ID (UUID)
- `created_at`: 创建时间 (TIMESTAMPTZ)
- `updated_at`: 更新时间 (TIMESTAMPTZ)

### 7.3 业务规则

1. **金额计算规则**:
   - `line_amount = quantity × unit_price`
   - `net_amount = line_amount - discount_amount`
   - `header.total_amount = SUM(line.line_amount)`
   - `header.net_amount = SUM(line.net_amount)`

2. **付款规则**:
   - `payment_status`: unpaid → partial → paid
   - `paid_amount <= net_amount`

3. **关联规则**:
   - 每个header必须有至少1条line
   - `supplier_id`必须匹配成功
   - `sku_id`必须匹配成功

### 7.4 主数据关联

**主数据匹配字段**:
- `suppliers`: `supplier_name` / `supplier_code` → `supplier_id`
- `skus`: `sku_name` / `sku_code` → `sku_id`

---

## 8. 单据号生成规则

### 8.1 生成格式

**格式**: `{前缀}-{日期}-{序号}`

**示例**: 
- 销售订单: `SO-20250122-001`
- 发货单: `SH-20250122-001`
- 销售发票: `SI-20250122-001`
- 采购订单: `PO-20250122-001`
- 收货单: `RC-20250122-001`
- 采购发票: `PI-20250122-001`

### 8.2 Python实现

```python
from datetime import datetime
from typing import Optional
import asyncpg

async def generate_document_no(
    doc_type: str,
    date: datetime,
    tenant_id: str,
    db_pool: asyncpg.Pool
) -> str:
    """
    生成单据号
    
    格式: {前缀}-{日期}-{序号}
    示例: SO-20250122-001
    
    Args:
        doc_type: 单据类型代码 (SO/SH/SI/PO/RC/PI)
        date: 单据日期
        tenant_id: 租户ID
        db_pool: 数据库连接池
    
    Returns:
        单据号
    """
    # 前缀映射
    prefix_map = {
        'SO': 'SO',  # Sales Order
        'SH': 'SH',  # Shipment
        'SI': 'SI',  # Sales Invoice
        'PO': 'PO',  # Purchase Order
        'RC': 'RC',  # Receipt
        'PI': 'PI'   # Purchase Invoice
    }
    
    prefix = prefix_map.get(doc_type, doc_type)
    date_str = date.strftime('%Y%m%d')
    
    # 表名映射
    table_map = {
        'SO': 'sales_order_header',
        'SH': 'shipment_header',
        'SI': 'sales_invoice_header',
        'PO': 'purchase_order_header',
        'RC': 'receipt_header',
        'PI': 'purchase_invoice_header'
    }
    
    table_name = table_map.get(doc_type)
    order_number_field = {
        'SO': 'order_number',
        'SH': 'shipment_number',
        'SI': 'invoice_number',
        'PO': 'po_number',
        'RC': 'receipt_number',
        'PI': 'invoice_number'
    }.get(doc_type, 'document_number')
    
    # 查询当天最大序号
    async with db_pool.acquire() as conn:
        query = f"""
        SELECT COALESCE(MAX(CAST(SUBSTRING({order_number_field} FROM '[0-9]+$') AS INTEGER)), 0) as max_seq
        FROM {table_name}
        WHERE tenant_id = $1
        AND {order_number_field} LIKE $2
        """
        
        pattern = f"{prefix}-{date_str}-%"
        max_seq = await conn.fetchval(query, tenant_id, pattern)
        
        # 生成新序号
        new_seq = max_seq + 1
        seq_str = f"{new_seq:03d}"  # 3位数字，不足补0
        
        document_no = f"{prefix}-{date_str}-{seq_str}"
        
        return document_no
```

### 8.3 数据库函数实现

```sql
-- 单据号生成函数
CREATE OR REPLACE FUNCTION generate_document_no(
  p_doc_type VARCHAR,
  p_date DATE,
  p_tenant_id UUID
) RETURNS VARCHAR AS $$
DECLARE
  v_prefix VARCHAR;
  v_date_str VARCHAR;
  v_table_name VARCHAR;
  v_number_field VARCHAR;
  v_pattern VARCHAR;
  v_max_seq INTEGER;
  v_seq_str VARCHAR;
  v_document_no VARCHAR;
BEGIN
  -- 前缀映射
  v_prefix := CASE p_doc_type
    WHEN 'SO' THEN 'SO'
    WHEN 'SH' THEN 'SH'
    WHEN 'SI' THEN 'SI'
    WHEN 'PO' THEN 'PO'
    WHEN 'RC' THEN 'RC'
    WHEN 'PI' THEN 'PI'
    ELSE p_doc_type
  END;
  
  v_date_str := TO_CHAR(p_date, 'YYYYMMDD');
  
  -- 表名和字段映射
  CASE p_doc_type
    WHEN 'SO' THEN
      v_table_name := 'sales_order_header';
      v_number_field := 'order_number';
    WHEN 'SH' THEN
      v_table_name := 'shipment_header';
      v_number_field := 'shipment_number';
    WHEN 'SI' THEN
      v_table_name := 'sales_invoice_header';
      v_number_field := 'invoice_number';
    WHEN 'PO' THEN
      v_table_name := 'purchase_order_header';
      v_number_field := 'po_number';
    WHEN 'RC' THEN
      v_table_name := 'receipt_header';
      v_number_field := 'receipt_number';
    WHEN 'PI' THEN
      v_table_name := 'purchase_invoice_header';
      v_number_field := 'invoice_number';
    ELSE
      RAISE EXCEPTION 'Unknown document type: %', p_doc_type;
  END CASE;
  
  -- 构建查询模式
  v_pattern := v_prefix || '-' || v_date_str || '-%';
  
  -- 查询当天最大序号
  EXECUTE format('
    SELECT COALESCE(MAX(CAST(SUBSTRING(%I FROM ''[0-9]+$'') AS INTEGER)), 0)
    FROM %I
    WHERE tenant_id = $1
    AND %I LIKE $2
  ', v_number_field, v_table_name, v_number_field)
  INTO v_max_seq
  USING p_tenant_id, v_pattern;
  
  -- 生成新序号
  v_max_seq := v_max_seq + 1;
  v_seq_str := LPAD(v_max_seq::TEXT, 3, '0');
  
  -- 生成单据号
  v_document_no := v_prefix || '-' || v_date_str || '-' || v_seq_str;
  
  RETURN v_document_no;
END;
$$ LANGUAGE plpgsql;
```

---

## 9. 头-行识别规则

### 9.1 识别问题

**问题**: 如何从Excel或CSV中识别哪些行是Header，哪些行是Line？

**示例数据**:
```
| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 订单号 | 客户 | 日期 | | | |
| SO001 | 客户A | 2025-01-20 | | | |
| | SKU代码 | SKU名称 | 数量 | 单价 | 金额 |
| | P001 | 产品1 | 10 | 100 | 1000 |
| | P002 | 产品2 | 5 | 200 | 1000 |
| SO002 | 客户B | 2025-01-21 | | | |
| | SKU代码 | SKU名称 | 数量 | 单价 | 金额 |
| | P003 | 产品3 | 20 | 50 | 1000 |
```

### 9.2 识别规则

#### 规则1: 如何判断一行是Header？

**判断逻辑**:
1. **包含单据号字段**: 如果某行的单据号字段（如`order_number`、`shipment_number`等）不为空，且其他关键Header字段（如`customer_name`、`supplier_name`、`order_date`等）也不全为空
2. **字段匹配度**: 该行的非空字段主要匹配Header字段定义（如客户、供应商、日期等），而非Line字段定义（如SKU、数量、单价等）
3. **位置特征**: 通常Header行在Line行之前，且一个Header后面跟随多个Line行

**代码示例**:
```python
def is_header_row(row: pd.Series, doc_type: str) -> bool:
    """
    判断是否为Header行
    
    判断依据:
    1. 包含单据号字段且不为空
    2. 包含客户/供应商字段且不为空
    3. 包含日期字段且不为空
    4. 不包含SKU相关字段（或SKU字段为空）
    """
    header_fields = {
        'SO': ['order_number', 'customer_name', 'order_date'],
        'SH': ['shipment_number', 'customer_name', 'shipment_date'],
        'SI': ['invoice_number', 'customer_name', 'invoice_date'],
        'PO': ['po_number', 'supplier_name', 'po_date'],
        'RC': ['receipt_number', 'supplier_name', 'receipt_date'],
        'PI': ['invoice_number', 'supplier_name', 'invoice_date']
    }
    
    required_fields = header_fields.get(doc_type, [])
    
    # 检查是否包含必需的Header字段
    has_required_fields = all(
        field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
        for field in required_fields
    )
    
    # 检查是否包含SKU字段（Line特征）
    line_indicators = ['sku_code', 'sku_name', 'product_code', 'product_name']
    has_line_fields = any(
        field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
        for field in line_indicators
    )
    
    # Header行：有必需字段 且 没有Line字段
    return has_required_fields and not has_line_fields
```

#### 规则2: 如何判断一行是Line？

**判断逻辑**:
1. **包含SKU字段**: 如果某行包含SKU相关字段（如`sku_code`、`sku_name`、`product_code`等）且不为空
2. **包含数量单价**: 包含数量（`quantity`）和单价（`unit_price`）字段且不为空
3. **位置特征**: 通常Line行在Header行之后，且多个Line行属于同一个Header

**代码示例**:
```python
def is_line_row(row: pd.Series, doc_type: str) -> bool:
    """
    判断是否为Line行
    
    判断依据:
    1. 包含SKU相关字段且不为空
    2. 包含数量字段且不为空
    3. 包含单价字段（可选，可能为空）
    4. 单据号字段可能为空（如果格式2：前向填充）
    """
    line_indicators = ['sku_code', 'sku_name', 'product_code', 'product_name']
    has_sku_field = any(
        field in row.index and pd.notna(row.get(field)) and str(row.get(field)).strip() != ''
        for field in line_indicators
    )
    
    has_quantity = (
        'quantity' in row.index and 
        pd.notna(row.get('quantity')) and 
        str(row.get('quantity')).strip() != ''
    )
    
    # Line行：有SKU字段 且 有数量字段
    return has_sku_field and has_quantity
```

#### 规则3: 如何确定Line归属于哪个Header？

**关联逻辑**:
1. **格式1（重复Header）**: Line行的单据号字段不为空，直接通过单据号匹配Header
2. **格式2（前向填充）**: Line行的单据号字段为空，向上查找最近的非空单据号行，该行即为Header
3. **位置关联**: Line行在Header行之后，且中间没有其他Header行

**代码示例**:
```python
def find_parent_header(line_index: int, headers: List[Dict], format_type: str) -> Optional[int]:
    """
    查找Line行对应的Header
    
    Args:
        line_index: Line行的索引
        headers: Header行列表（已按索引排序）
        format_type: 格式类型（'repeated_header' 或 'first_row_header'）
    
    Returns:
        Header行的索引，如果未找到返回None
    """
    if format_type == 'repeated_header':
        # 格式1：直接通过单据号匹配
        # 已在识别时确定关联关系
        pass
    elif format_type == 'first_row_header':
        # 格式2：向上查找最近的Header
        for header in reversed(headers):
            if header['row_index'] < line_index:
                return header['row_index']
    
    return None
```

### 9.3 边界情况处理

#### 情况1: Header信息跨多行

**处理**: 合并多行为一个Header记录

```python
def merge_header_rows(rows: List[pd.Series]) -> Dict:
    """
    合并多个Header行
    """
    merged = {}
    for row in rows:
        for key, value in row.items():
            if pd.notna(value) and str(value).strip() != '':
                merged[key] = value
    return merged
```

#### 情况2: Line信息跨多行

**处理**: 每个物理行对应一个Line记录，不合并

#### 情况3: 混合格式（有些行是Header+Line合并）

**处理**: 识别为格式1（重复Header），每行既是Header又是Line

---

## 10. 总结

### 10.1 关键字段汇总

**所有单据类型共有的Header字段**:
- 单据号（可自动生成）
- 单据日期（必填）
- 客户/供应商ID（必填，通过主数据匹配）
- 客户/供应商名称（冗余字段，用于匹配）
- 客户/供应商代码（冗余字段，用于匹配）
- 总金额（计算字段）
- 备注

**所有单据类型共有的Line字段**:
- 行号（必填）
- SKU ID（必填，通过主数据匹配）
- SKU代码（冗余字段，用于匹配）
- SKU名称（冗余字段，用于匹配）
- 数量（必填，>0）
- 单价（必填，>=0）
- 行金额（计算字段 = 数量 × 单价）
- 备注

### 10.2 主数据匹配字段汇总

| 主数据类型 | 匹配字段 | 目标表 | 匹配优先级 |
|-----------|---------|--------|-----------|
| 客户 | `customer_name` / `customer_code` | `dim_customer` | 编码 > 名称 |
| 供应商 | `supplier_name` / `supplier_code` | `dim_supplier` | 编码 > 名称 |
| SKU | `sku_name` / `sku_code` | `dim_sku` | 编码 > 名称 |
| 渠道 | `channel_name` / `channel_code` | `dim_channel` | 编码 > 名称 |

### 10.3 业务规则汇总

1. **金额计算**: `line_amount = quantity × unit_price`
2. **总额计算**: `header.total_amount = SUM(line.line_amount)`
3. **数量验证**: `quantity > 0`, `unit_price >= 0`
4. **关联验证**: 每个header必须有至少1条line
5. **主数据验证**: 客户/供应商ID和SKU ID必须匹配成功才能导入

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

