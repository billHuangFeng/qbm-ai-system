# 数据库设计文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P0 - 必需文档**

**文档目的**: 提供12张单据表的完整DDL和优化方案，供Lovable在Supabase中实施

---

## 📋 目录

1. [表结构DDL](#1-表结构ddl)
2. [索引设计](#2-索引设计)
3. [数据库函数](#3-数据库函数)
4. [触发器](#4-触发器)
5. [RLS策略](#5-rls策略)

---

## 1. 表结构DDL

### 1.1 销售订单 (Sales Order, SO)

#### Header表
```sql
CREATE TABLE sales_order_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  order_number VARCHAR(50) NOT NULL,
  order_date DATE NOT NULL,
  customer_id UUID REFERENCES dim_customer(customer_id),
  customer_name VARCHAR(255),  -- 冗余字段，用于匹配
  customer_code VARCHAR(50),   -- 冗余字段，用于匹配
  channel_id UUID REFERENCES dim_channel(channel_id),
  total_amount DECIMAL(18,2) DEFAULT 0,
  total_quantity DECIMAL(18,3) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) DEFAULT 0,
  currency_code VARCHAR(10) DEFAULT 'CNY',
  order_status VARCHAR(20) DEFAULT 'draft',
  payment_term VARCHAR(50),
  delivery_address TEXT,
  contact_person VARCHAR(100),
  contact_phone VARCHAR(50),
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  approved_by UUID REFERENCES auth.users(id),
  approved_at TIMESTAMPTZ,
  
  CONSTRAINT uk_sales_order_number UNIQUE (tenant_id, order_number)
);
```

#### Line表
```sql
CREATE TABLE sales_order_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES sales_order_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),        -- 冗余字段
  sku_name VARCHAR(200),       -- 冗余字段
  quantity DECIMAL(18,3) NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(18,2) NOT NULL CHECK (unit_price >= 0),
  line_amount DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  discount_rate DECIMAL(5,4) DEFAULT 0 CHECK (discount_rate >= 0 AND discount_rate <= 1),
  discount_amount DECIMAL(18,2) DEFAULT 0,
  tax_rate DECIMAL(5,4) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) GENERATED ALWAYS AS (line_amount - discount_amount) STORED,
  requested_delivery_date DATE,
  promised_delivery_date DATE,
  shipped_quantity DECIMAL(18,3) DEFAULT 0,
  invoiced_quantity DECIMAL(18,3) DEFAULT 0,
  line_status VARCHAR(20) DEFAULT 'open',
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_sales_order_line_no UNIQUE (header_id, line_no)
);
```

### 1.2 发货单 (Shipment, SH)

#### Header表
```sql
CREATE TABLE shipment_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  shipment_number VARCHAR(50) NOT NULL,
  shipment_date DATE NOT NULL,
  customer_id UUID REFERENCES dim_customer(customer_id),
  customer_name VARCHAR(255),
  customer_code VARCHAR(50),
  shipment_status VARCHAR(20) DEFAULT 'draft',
  carrier VARCHAR(100),
  tracking_number VARCHAR(100),
  shipping_method VARCHAR(50),
  delivery_address TEXT,
  contact_person VARCHAR(100),
  contact_phone VARCHAR(50),
  planned_delivery_date DATE,
  actual_delivery_date DATE,
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_shipment_number UNIQUE (tenant_id, shipment_number)
);
```

#### Line表
```sql
CREATE TABLE shipment_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES shipment_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  source_order_id UUID REFERENCES sales_order_header(id),
  source_order_line_id UUID REFERENCES sales_order_line(id),
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),
  sku_name VARCHAR(200),
  shipped_quantity DECIMAL(18,3) NOT NULL CHECK (shipped_quantity > 0),
  unit_price DECIMAL(18,2),
  line_status VARCHAR(20) DEFAULT 'pending',
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_shipment_line_no UNIQUE (header_id, line_no)
);
```

### 1.3 销售发票 (Sales Invoice, SI)

#### Header表
```sql
CREATE TABLE sales_invoice_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  invoice_number VARCHAR(50) NOT NULL,
  invoice_date DATE NOT NULL,
  customer_id UUID REFERENCES dim_customer(customer_id),
  customer_name VARCHAR(255),
  customer_code VARCHAR(50),
  invoice_type VARCHAR(20) DEFAULT 'standard',
  invoice_status VARCHAR(20) DEFAULT 'draft',
  total_amount DECIMAL(18,2) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) DEFAULT 0,
  currency_code VARCHAR(10) DEFAULT 'CNY',
  payment_term VARCHAR(50),
  due_date DATE,
  paid_amount DECIMAL(18,2) DEFAULT 0,
  payment_status VARCHAR(20) DEFAULT 'unpaid',
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_sales_invoice_number UNIQUE (tenant_id, invoice_number)
);
```

#### Line表
```sql
CREATE TABLE sales_invoice_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES sales_invoice_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  source_order_id UUID REFERENCES sales_order_header(id),
  source_order_line_id UUID REFERENCES sales_order_line(id),
  source_shipment_id UUID REFERENCES shipment_header(id),
  source_shipment_line_id UUID REFERENCES shipment_line(id),
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),
  sku_name VARCHAR(200),
  quantity DECIMAL(18,3) NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(18,2) NOT NULL CHECK (unit_price >= 0),
  line_amount DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  tax_rate DECIMAL(5,4) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) GENERATED ALWAYS AS (line_amount - discount_amount) STORED,
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_sales_invoice_line_no UNIQUE (header_id, line_no)
);
```

### 1.4 采购订单 (Purchase Order, PO)

#### Header表
```sql
CREATE TABLE purchase_order_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  po_number VARCHAR(50) NOT NULL,
  po_date DATE NOT NULL,
  supplier_id UUID REFERENCES dim_supplier(supplier_id),
  supplier_name VARCHAR(255),
  supplier_code VARCHAR(50),
  po_status VARCHAR(20) DEFAULT 'draft',
  total_amount DECIMAL(18,2) DEFAULT 0,
  total_quantity DECIMAL(18,3) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) DEFAULT 0,
  currency_code VARCHAR(10) DEFAULT 'CNY',
  payment_term VARCHAR(50),
  delivery_address TEXT,
  contact_person VARCHAR(100),
  contact_phone VARCHAR(50),
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  approved_by UUID REFERENCES auth.users(id),
  approved_at TIMESTAMPTZ,
  
  CONSTRAINT uk_purchase_order_number UNIQUE (tenant_id, po_number)
);
```

#### Line表
```sql
CREATE TABLE purchase_order_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES purchase_order_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),
  sku_name VARCHAR(200),
  quantity DECIMAL(18,3) NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(18,2) NOT NULL CHECK (unit_price >= 0),
  line_amount DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  discount_rate DECIMAL(5,4) DEFAULT 0 CHECK (discount_rate >= 0 AND discount_rate <= 1),
  discount_amount DECIMAL(18,2) DEFAULT 0,
  tax_rate DECIMAL(5,4) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) GENERATED ALWAYS AS (line_amount - discount_amount) STORED,
  requested_delivery_date DATE,
  promised_delivery_date DATE,
  received_quantity DECIMAL(18,3) DEFAULT 0,
  invoiced_quantity DECIMAL(18,3) DEFAULT 0,
  line_status VARCHAR(20) DEFAULT 'open',
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_purchase_order_line_no UNIQUE (header_id, line_no)
);
```

### 1.5 收货单 (Receipt, RC)

#### Header表
```sql
CREATE TABLE receipt_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  receipt_number VARCHAR(50) NOT NULL,
  receipt_date DATE NOT NULL,
  supplier_id UUID REFERENCES dim_supplier(supplier_id),
  supplier_name VARCHAR(255),
  supplier_code VARCHAR(50),
  receipt_status VARCHAR(20) DEFAULT 'draft',
  carrier VARCHAR(100),
  tracking_number VARCHAR(100),
  inspection_status VARCHAR(20),
  inspector UUID REFERENCES auth.users(id),
  inspection_date DATE,
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_receipt_number UNIQUE (tenant_id, receipt_number)
);
```

#### Line表
```sql
CREATE TABLE receipt_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES receipt_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  source_po_id UUID REFERENCES purchase_order_header(id),
  source_po_line_id UUID REFERENCES purchase_order_line(id),
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),
  sku_name VARCHAR(200),
  received_quantity DECIMAL(18,3) NOT NULL CHECK (received_quantity > 0),
  accepted_quantity DECIMAL(18,3),
  rejected_quantity DECIMAL(18,3),
  unit_price DECIMAL(18,2),
  quality_status VARCHAR(20),
  quality_remark TEXT,
  line_status VARCHAR(20) DEFAULT 'pending',
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_receipt_line_no UNIQUE (header_id, line_no),
  CONSTRAINT chk_receipt_quantity CHECK (
    COALESCE(accepted_quantity, 0) + COALESCE(rejected_quantity, 0) <= received_quantity
  )
);
```

### 1.6 采购发票 (Purchase Invoice, PI)

#### Header表
```sql
CREATE TABLE purchase_invoice_header (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  invoice_number VARCHAR(50) NOT NULL,
  invoice_date DATE NOT NULL,
  supplier_id UUID REFERENCES dim_supplier(supplier_id),
  supplier_name VARCHAR(255),
  supplier_code VARCHAR(50),
  invoice_type VARCHAR(20) DEFAULT 'standard',
  invoice_status VARCHAR(20) DEFAULT 'draft',
  total_amount DECIMAL(18,2) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) DEFAULT 0,
  currency_code VARCHAR(10) DEFAULT 'CNY',
  payment_term VARCHAR(50),
  due_date DATE,
  paid_amount DECIMAL(18,2) DEFAULT 0,
  payment_status VARCHAR(20) DEFAULT 'unpaid',
  remark TEXT,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_purchase_invoice_number UNIQUE (tenant_id, invoice_number)
);
```

#### Line表
```sql
CREATE TABLE purchase_invoice_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  header_id UUID NOT NULL REFERENCES purchase_invoice_header(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  line_no INTEGER NOT NULL,
  source_po_id UUID REFERENCES purchase_order_header(id),
  source_po_line_id UUID REFERENCES purchase_order_line(id),
  source_receipt_id UUID REFERENCES receipt_header(id),
  source_receipt_line_id UUID REFERENCES receipt_line(id),
  sku_id UUID REFERENCES dim_sku(sku_id),
  sku_code VARCHAR(50),
  sku_name VARCHAR(200),
  quantity DECIMAL(18,3) NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(18,2) NOT NULL CHECK (unit_price >= 0),
  line_amount DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  tax_rate DECIMAL(5,4) DEFAULT 0,
  tax_amount DECIMAL(18,2) DEFAULT 0,
  discount_amount DECIMAL(18,2) DEFAULT 0,
  net_amount DECIMAL(18,2) GENERATED ALWAYS AS (line_amount - discount_amount) STORED,
  remark TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT uk_purchase_invoice_line_no UNIQUE (header_id, line_no)
);
```

---

## 2. 索引设计

### 2.1 查询性能优化索引

```sql
-- 销售订单
CREATE INDEX idx_sales_order_header_tenant_date 
  ON sales_order_header(tenant_id, order_date DESC);
CREATE INDEX idx_sales_order_header_customer 
  ON sales_order_header(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX idx_sales_order_line_header 
  ON sales_order_line(header_id, line_no);

-- 发货单
CREATE INDEX idx_shipment_header_tenant_date 
  ON shipment_header(tenant_id, shipment_date DESC);
CREATE INDEX idx_shipment_header_customer 
  ON shipment_header(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX idx_shipment_line_header 
  ON shipment_line(header_id, line_no);

-- 销售发票
CREATE INDEX idx_sales_invoice_header_tenant_date 
  ON sales_invoice_header(tenant_id, invoice_date DESC);
CREATE INDEX idx_sales_invoice_header_customer 
  ON sales_invoice_header(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX idx_sales_invoice_line_header 
  ON sales_invoice_line(header_id, line_no);

-- 采购订单
CREATE INDEX idx_purchase_order_header_tenant_date 
  ON purchase_order_header(tenant_id, po_date DESC);
CREATE INDEX idx_purchase_order_header_supplier 
  ON purchase_order_header(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_purchase_order_line_header 
  ON purchase_order_line(header_id, line_no);

-- 收货单
CREATE INDEX idx_receipt_header_tenant_date 
  ON receipt_header(tenant_id, receipt_date DESC);
CREATE INDEX idx_receipt_header_supplier 
  ON receipt_header(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_receipt_line_header 
  ON receipt_line(header_id, line_no);

-- 采购发票
CREATE INDEX idx_purchase_invoice_header_tenant_date 
  ON purchase_invoice_header(tenant_id, invoice_date DESC);
CREATE INDEX idx_purchase_invoice_header_supplier 
  ON purchase_invoice_header(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_purchase_invoice_line_header 
  ON purchase_invoice_line(header_id, line_no);
```

### 2.2 模糊匹配索引（使用pg_trgm）

```sql
-- 启用pg_trgm扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 主数据表模糊匹配索引
CREATE INDEX idx_customers_name_trgm 
  ON dim_customer USING GIN (customer_name gin_trgm_ops);
CREATE INDEX idx_customers_code_trgm 
  ON dim_customer USING GIN (customer_code gin_trgm_ops);

CREATE INDEX idx_suppliers_name_trgm 
  ON dim_supplier USING GIN (supplier_name gin_trgm_ops);
CREATE INDEX idx_suppliers_code_trgm 
  ON dim_supplier USING GIN (supplier_code gin_trgm_ops);

CREATE INDEX idx_skus_name_trgm 
  ON dim_sku USING GIN (sku_name gin_trgm_ops);
CREATE INDEX idx_skus_code_trgm 
  ON dim_sku USING GIN (sku_code gin_trgm_ops);
```

---

## 3. 数据库函数

### 3.1 单据号生成函数

```sql
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

### 3.2 模糊匹配函数

```sql
-- 客户模糊匹配函数
CREATE OR REPLACE FUNCTION fuzzy_match_customer(
  p_name VARCHAR,
  p_code VARCHAR,
  p_tenant_id UUID,
  p_threshold FLOAT DEFAULT 0.3
) RETURNS TABLE (
  customer_id UUID,
  customer_name VARCHAR,
  customer_code VARCHAR,
  name_score FLOAT,
  code_score FLOAT,
  total_score FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_code,
    similarity(c.customer_name, p_name) as name_score,
    CASE 
      WHEN p_code IS NOT NULL THEN similarity(c.customer_code, p_code)
      ELSE 0.0
    END as code_score,
    CASE
      WHEN p_code IS NOT NULL THEN
        similarity(c.customer_name, p_name) * 0.4 + 
        similarity(c.customer_code, p_code) * 0.6
      ELSE
        similarity(c.customer_name, p_name)
    END as total_score
  FROM dim_customer c
  WHERE c.tenant_id = p_tenant_id
  AND c.is_active = true
  AND (
    similarity(c.customer_name, p_name) > p_threshold
    OR (p_code IS NOT NULL AND similarity(c.customer_code, p_code) > p_threshold)
  )
  ORDER BY total_score DESC
  LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- 类似的，请提供：
-- - fuzzy_match_supplier()
-- - fuzzy_match_sku()
-- - fuzzy_match_channel()
```

---

## 4. 触发器

### 4.1 自动更新updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加触发器
CREATE TRIGGER update_sales_order_header_updated_at
  BEFORE UPDATE ON sales_order_header
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_order_line_updated_at
  BEFORE UPDATE ON sales_order_line
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 请为所有12张表添加类似触发器
```

### 4.2 自动更新Header总额

```sql
CREATE OR REPLACE FUNCTION update_header_totals()
RETURNS TRIGGER AS $$
DECLARE
  v_header_table VARCHAR;
  v_header_id_field VARCHAR;
  v_header_id_value UUID;
BEGIN
  -- 根据表名确定Header表
  IF TG_TABLE_NAME LIKE '%_line' THEN
    v_header_table := REPLACE(TG_TABLE_NAME, '_line', '_header');
    v_header_id_field := REPLACE(SPLIT_PART(TG_TABLE_NAME, '_', 1), 'sales', 'order') || '_id';
    
    -- 获取header_id
    IF TG_TABLE_NAME LIKE 'sales_%' THEN
      v_header_id_value := NEW.order_id;
    ELSIF TG_TABLE_NAME LIKE 'shipment_%' THEN
      v_header_id_value := NEW.shipment_id;
    -- ... 其他表
    END IF;
    
    -- 更新Header总额
    EXECUTE format('
      UPDATE %I
      SET 
        total_amount = (
          SELECT COALESCE(SUM(line_amount), 0)
          FROM %I
          WHERE header_id = $1
        ),
        total_quantity = (
          SELECT COALESCE(SUM(quantity), 0)
          FROM %I
          WHERE header_id = $1
        )
      WHERE id = $1
    ', v_header_table, TG_TABLE_NAME, TG_TABLE_NAME)
    USING v_header_id_value;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有Line表添加触发器
CREATE TRIGGER update_sales_order_header_totals
  AFTER INSERT OR UPDATE OR DELETE ON sales_order_line
  FOR EACH ROW
  EXECUTE FUNCTION update_header_totals();

-- 请为所有6张Line表添加类似触发器
```

---

## 5. RLS策略

### 5.1 销售订单RLS策略

```sql
ALTER TABLE sales_order_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_order_line ENABLE ROW LEVEL SECURITY;

-- 查看策略
CREATE POLICY "Users can view their tenant's sales orders"
  ON sales_order_header
  FOR SELECT
  USING (
    tenant_id IN (
      SELECT tenant_id 
      FROM user_profiles 
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert sales orders for their tenant"
  ON sales_order_header
  FOR INSERT
  WITH CHECK (
    tenant_id IN (
      SELECT tenant_id 
      FROM user_profiles 
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their tenant's sales orders"
  ON sales_order_header
  FOR UPDATE
  USING (
    tenant_id IN (
      SELECT tenant_id 
      FROM user_profiles 
      WHERE user_id = auth.uid()
    )
  );

-- Line表策略（继承Header的租户隔离）
CREATE POLICY "Users can view lines for their tenant's orders"
  ON sales_order_line
  FOR SELECT
  USING (
    tenant_id IN (
      SELECT tenant_id 
      FROM user_profiles 
      WHERE user_id = auth.uid()
    )
  );

-- 请为所有12张表提供完整的RLS策略
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

