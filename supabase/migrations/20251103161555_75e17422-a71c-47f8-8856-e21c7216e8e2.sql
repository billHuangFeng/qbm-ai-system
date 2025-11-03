-- ============================================
-- 单据头-单据体表结构设计
-- 包含：销售订单、发货单、销售发票、采购订单、收货单、采购发票
-- ============================================

-- ============================================
-- 销售流程表
-- ============================================

-- 销售订单头表
CREATE TABLE sales_order_header (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    order_date DATE NOT NULL,
    customer_id UUID REFERENCES dim_customer(customer_id),
    channel_id UUID REFERENCES dim_channel(channel_id),
    
    -- 单据状态
    order_status VARCHAR(20) DEFAULT 'draft', -- draft, confirmed, in_progress, completed, cancelled
    
    -- 头部金额汇总
    total_amount NUMERIC(15,2) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) DEFAULT 0,
    
    -- 其他信息
    currency_code VARCHAR(10) DEFAULT 'CNY',
    payment_term VARCHAR(50),
    delivery_address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    remark TEXT,
    
    -- 审计字段
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by UUID,
    approved_at TIMESTAMPTZ
);

-- 销售订单明细表
CREATE TABLE sales_order_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES sales_order_header(order_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    -- 数量和单价
    quantity NUMERIC(15,3) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    
    -- 金额计算
    line_amount NUMERIC(15,2) NOT NULL,
    tax_rate NUMERIC(5,4) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_rate NUMERIC(5,4) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) NOT NULL,
    
    -- 交付信息
    requested_delivery_date DATE,
    promised_delivery_date DATE,
    
    -- 执行状态
    shipped_quantity NUMERIC(15,3) DEFAULT 0,
    invoiced_quantity NUMERIC(15,3) DEFAULT 0,
    line_status VARCHAR(20) DEFAULT 'open', -- open, partial, closed, cancelled
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(order_id, line_number)
);

-- 发货单头表
CREATE TABLE shipment_header (
    shipment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    shipment_number VARCHAR(50) NOT NULL UNIQUE,
    shipment_date DATE NOT NULL,
    
    customer_id UUID REFERENCES dim_customer(customer_id),
    
    -- 单据状态
    shipment_status VARCHAR(20) DEFAULT 'draft', -- draft, confirmed, in_transit, delivered, cancelled
    
    -- 物流信息
    carrier VARCHAR(100),
    tracking_number VARCHAR(100),
    shipping_method VARCHAR(50),
    
    delivery_address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    
    -- 预计和实际交付
    planned_delivery_date DATE,
    actual_delivery_date DATE,
    
    remark TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 发货单明细表
CREATE TABLE shipment_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipment_header(shipment_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    -- 关联销售订单
    source_order_id UUID REFERENCES sales_order_header(order_id),
    source_order_line_id UUID REFERENCES sales_order_line(line_id),
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    shipped_quantity NUMERIC(15,3) NOT NULL,
    unit_price NUMERIC(15,2),
    
    line_status VARCHAR(20) DEFAULT 'pending', -- pending, shipped, delivered
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(shipment_id, line_number)
);

-- 销售发票头表
CREATE TABLE sales_invoice_header (
    invoice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    
    customer_id UUID REFERENCES dim_customer(customer_id),
    
    -- 发票类型
    invoice_type VARCHAR(20) DEFAULT 'standard', -- standard, credit_note, debit_note
    
    -- 单据状态
    invoice_status VARCHAR(20) DEFAULT 'draft', -- draft, issued, paid, overdue, cancelled
    
    -- 金额信息
    total_amount NUMERIC(15,2) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) DEFAULT 0,
    
    currency_code VARCHAR(10) DEFAULT 'CNY',
    
    -- 付款信息
    payment_term VARCHAR(50),
    due_date DATE,
    paid_amount NUMERIC(15,2) DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, partial, paid
    
    remark TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 销售发票明细表
CREATE TABLE sales_invoice_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES sales_invoice_header(invoice_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    -- 关联源单据
    source_order_id UUID REFERENCES sales_order_header(order_id),
    source_order_line_id UUID REFERENCES sales_order_line(line_id),
    source_shipment_id UUID REFERENCES shipment_header(shipment_id),
    source_shipment_line_id UUID REFERENCES shipment_line(line_id),
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    quantity NUMERIC(15,3) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    
    line_amount NUMERIC(15,2) NOT NULL,
    tax_rate NUMERIC(5,4) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) NOT NULL,
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(invoice_id, line_number)
);

-- ============================================
-- 采购流程表
-- ============================================

-- 采购订单头表
CREATE TABLE purchase_order_header (
    po_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    po_number VARCHAR(50) NOT NULL UNIQUE,
    po_date DATE NOT NULL,
    
    supplier_id UUID REFERENCES dim_supplier(supplier_id),
    
    -- 单据状态
    po_status VARCHAR(20) DEFAULT 'draft', -- draft, confirmed, in_progress, completed, cancelled
    
    -- 金额汇总
    total_amount NUMERIC(15,2) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) DEFAULT 0,
    
    currency_code VARCHAR(10) DEFAULT 'CNY',
    payment_term VARCHAR(50),
    
    -- 交付信息
    delivery_address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    
    remark TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by UUID,
    approved_at TIMESTAMPTZ
);

-- 采购订单明细表
CREATE TABLE purchase_order_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_id UUID NOT NULL REFERENCES purchase_order_header(po_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    quantity NUMERIC(15,3) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    
    line_amount NUMERIC(15,2) NOT NULL,
    tax_rate NUMERIC(5,4) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) NOT NULL,
    
    -- 交付信息
    requested_delivery_date DATE,
    promised_delivery_date DATE,
    
    -- 执行状态
    received_quantity NUMERIC(15,3) DEFAULT 0,
    invoiced_quantity NUMERIC(15,3) DEFAULT 0,
    line_status VARCHAR(20) DEFAULT 'open', -- open, partial, closed, cancelled
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(po_id, line_number)
);

-- 收货单头表
CREATE TABLE receipt_header (
    receipt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    receipt_number VARCHAR(50) NOT NULL UNIQUE,
    receipt_date DATE NOT NULL,
    
    supplier_id UUID REFERENCES dim_supplier(supplier_id),
    
    -- 单据状态
    receipt_status VARCHAR(20) DEFAULT 'draft', -- draft, confirmed, inspected, accepted, rejected
    
    -- 物流信息
    carrier VARCHAR(100),
    tracking_number VARCHAR(100),
    
    -- 质检信息
    inspection_status VARCHAR(20), -- pending, passed, failed, partial
    inspector UUID,
    inspection_date DATE,
    
    remark TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 收货单明细表
CREATE TABLE receipt_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID NOT NULL REFERENCES receipt_header(receipt_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    -- 关联采购订单
    source_po_id UUID REFERENCES purchase_order_header(po_id),
    source_po_line_id UUID REFERENCES purchase_order_line(line_id),
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    received_quantity NUMERIC(15,3) NOT NULL,
    accepted_quantity NUMERIC(15,3),
    rejected_quantity NUMERIC(15,3),
    unit_price NUMERIC(15,2),
    
    -- 质检结果
    quality_status VARCHAR(20), -- pending, passed, failed
    quality_remark TEXT,
    
    line_status VARCHAR(20) DEFAULT 'pending',
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(receipt_id, line_number)
);

-- 采购发票头表
CREATE TABLE purchase_invoice_header (
    invoice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    
    supplier_id UUID REFERENCES dim_supplier(supplier_id),
    
    -- 发票类型
    invoice_type VARCHAR(20) DEFAULT 'standard',
    
    -- 单据状态
    invoice_status VARCHAR(20) DEFAULT 'draft', -- draft, received, verified, paid, cancelled
    
    -- 金额信息
    total_amount NUMERIC(15,2) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) DEFAULT 0,
    
    currency_code VARCHAR(10) DEFAULT 'CNY',
    
    -- 付款信息
    payment_term VARCHAR(50),
    due_date DATE,
    paid_amount NUMERIC(15,2) DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    
    remark TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 采购发票明细表
CREATE TABLE purchase_invoice_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES purchase_invoice_header(invoice_id) ON DELETE CASCADE,
    tenant_id UUID,
    line_number INTEGER NOT NULL,
    
    -- 关联源单据
    source_po_id UUID REFERENCES purchase_order_header(po_id),
    source_po_line_id UUID REFERENCES purchase_order_line(line_id),
    source_receipt_id UUID REFERENCES receipt_header(receipt_id),
    source_receipt_line_id UUID REFERENCES receipt_line(line_id),
    
    sku_id UUID REFERENCES dim_sku(sku_id),
    sku_code VARCHAR(50),
    sku_name VARCHAR(200),
    
    quantity NUMERIC(15,3) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    
    line_amount NUMERIC(15,2) NOT NULL,
    tax_rate NUMERIC(5,4) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    discount_amount NUMERIC(15,2) DEFAULT 0,
    net_amount NUMERIC(15,2) NOT NULL,
    
    remark TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(invoice_id, line_number)
);

-- ============================================
-- 单据关系表
-- ============================================

-- 单据关联关系表（追溯单据之间的转换关系）
CREATE TABLE document_relation (
    relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    
    -- 源单据
    source_doc_type VARCHAR(50) NOT NULL, -- sales_order, purchase_order, shipment, receipt, etc.
    source_doc_id UUID NOT NULL,
    source_doc_line_id UUID,
    
    -- 目标单据
    target_doc_type VARCHAR(50) NOT NULL,
    target_doc_id UUID NOT NULL,
    target_doc_line_id UUID,
    
    -- 关联数量（如果是明细行关联）
    related_quantity NUMERIC(15,3),
    
    relation_type VARCHAR(50), -- full, partial
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 确保同一对单据不重复关联
    UNIQUE(source_doc_type, source_doc_id, source_doc_line_id, target_doc_type, target_doc_id, target_doc_line_id)
);

-- ============================================
-- 索引优化
-- ============================================

-- 销售订单索引
CREATE INDEX idx_sales_order_header_tenant ON sales_order_header(tenant_id);
CREATE INDEX idx_sales_order_header_date ON sales_order_header(order_date);
CREATE INDEX idx_sales_order_header_customer ON sales_order_header(customer_id);
CREATE INDEX idx_sales_order_header_status ON sales_order_header(order_status);
CREATE INDEX idx_sales_order_line_order ON sales_order_line(order_id);
CREATE INDEX idx_sales_order_line_sku ON sales_order_line(sku_id);

-- 发货单索引
CREATE INDEX idx_shipment_header_tenant ON shipment_header(tenant_id);
CREATE INDEX idx_shipment_header_date ON shipment_header(shipment_date);
CREATE INDEX idx_shipment_header_customer ON shipment_header(customer_id);
CREATE INDEX idx_shipment_line_shipment ON shipment_line(shipment_id);
CREATE INDEX idx_shipment_line_source_order ON shipment_line(source_order_id);

-- 销售发票索引
CREATE INDEX idx_sales_invoice_header_tenant ON sales_invoice_header(tenant_id);
CREATE INDEX idx_sales_invoice_header_date ON sales_invoice_header(invoice_date);
CREATE INDEX idx_sales_invoice_header_customer ON sales_invoice_header(customer_id);
CREATE INDEX idx_sales_invoice_line_invoice ON sales_invoice_line(invoice_id);

-- 采购订单索引
CREATE INDEX idx_purchase_order_header_tenant ON purchase_order_header(tenant_id);
CREATE INDEX idx_purchase_order_header_date ON purchase_order_header(po_date);
CREATE INDEX idx_purchase_order_header_supplier ON purchase_order_header(supplier_id);
CREATE INDEX idx_purchase_order_line_po ON purchase_order_line(po_id);

-- 收货单索引
CREATE INDEX idx_receipt_header_tenant ON receipt_header(tenant_id);
CREATE INDEX idx_receipt_header_date ON receipt_header(receipt_date);
CREATE INDEX idx_receipt_line_receipt ON receipt_line(receipt_id);
CREATE INDEX idx_receipt_line_source_po ON receipt_line(source_po_id);

-- 采购发票索引
CREATE INDEX idx_purchase_invoice_header_tenant ON purchase_invoice_header(tenant_id);
CREATE INDEX idx_purchase_invoice_header_date ON purchase_invoice_header(invoice_date);
CREATE INDEX idx_purchase_invoice_line_invoice ON purchase_invoice_line(invoice_id);

-- 单据关系索引
CREATE INDEX idx_document_relation_source ON document_relation(source_doc_type, source_doc_id);
CREATE INDEX idx_document_relation_target ON document_relation(target_doc_type, target_doc_id);

-- ============================================
-- RLS 策略
-- ============================================

-- 销售订单
ALTER TABLE sales_order_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_order_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON sales_order_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON sales_order_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 发货单
ALTER TABLE shipment_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipment_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON shipment_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON shipment_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 销售发票
ALTER TABLE sales_invoice_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_invoice_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON sales_invoice_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON sales_invoice_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 采购订单
ALTER TABLE purchase_order_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON purchase_order_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON purchase_order_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 收货单
ALTER TABLE receipt_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipt_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON receipt_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON receipt_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 采购发票
ALTER TABLE purchase_invoice_header ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_invoice_line ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON purchase_invoice_header
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy ON purchase_invoice_line
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 单据关系表
ALTER TABLE document_relation ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON document_relation
    FOR ALL USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );