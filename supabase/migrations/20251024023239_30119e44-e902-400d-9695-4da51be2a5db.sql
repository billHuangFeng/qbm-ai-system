-- ============================================
-- BMOS 初始数据模型（维度表和事实表）
-- ============================================

-- 价值特性标签维度表
CREATE TABLE public.dim_vpt (
    vpt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vpt_code VARCHAR(50) UNIQUE NOT NULL,
    vpt_name VARCHAR(100) NOT NULL,
    vpt_category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 产品特性标签维度表
CREATE TABLE public.dim_pft (
    pft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pft_code VARCHAR(50) UNIQUE NOT NULL,
    pft_name VARCHAR(100) NOT NULL,
    pft_category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 客户维度表
CREATE TABLE public.dim_customer (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_segment VARCHAR(50),
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 渠道维度表
CREATE TABLE public.dim_channel (
    channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_code VARCHAR(50) UNIQUE NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SKU维度表
CREATE TABLE public.dim_sku (
    sku_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_code VARCHAR(50) UNIQUE NOT NULL,
    sku_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 活动维度表
CREATE TABLE public.dim_activity (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_code VARCHAR(50) UNIQUE NOT NULL,
    activity_name VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 媒体渠道维度表
CREATE TABLE public.dim_media_channel (
    media_channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_code VARCHAR(50) UNIQUE NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50),
    cost_per_impression DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转化渠道维度表
CREATE TABLE public.dim_conv_channel (
    conv_channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_code VARCHAR(50) UNIQUE NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 供应商维度表
CREATE TABLE public.dim_supplier (
    supplier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    rating DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 订单事实表
CREATE TABLE public.fact_order (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES public.dim_customer(customer_id),
    sku_id UUID REFERENCES public.dim_sku(sku_id),
    channel_id UUID REFERENCES public.dim_channel(channel_id),
    order_amount DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    order_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 客户声音事实表
CREATE TABLE public.fact_voice (
    voice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES public.dim_customer(customer_id),
    sku_id UUID REFERENCES public.dim_sku(sku_id),
    satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 5),
    voice_content TEXT,
    sentiment VARCHAR(20),
    voice_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 费用事实表
CREATE TABLE public.fact_expense (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID REFERENCES public.dim_activity(activity_id),
    expense_type VARCHAR(50),
    expense_amount DECIMAL(10,2) NOT NULL,
    expense_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 生产事实表
CREATE TABLE public.fact_produce (
    produce_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID REFERENCES public.dim_sku(sku_id),
    quantity INT NOT NULL,
    cost DECIMAL(10,2),
    produce_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 供应商事实表
CREATE TABLE public.fact_supplier (
    supplier_fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID REFERENCES public.dim_supplier(supplier_id),
    sku_id UUID REFERENCES public.dim_sku(sku_id),
    supply_amount DECIMAL(10,2),
    supply_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 媒体-价值特性桥接表
CREATE TABLE public.bridge_media_vpt (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_channel_id UUID REFERENCES public.dim_media_channel(media_channel_id),
    vpt_id UUID REFERENCES public.dim_vpt(vpt_id),
    impression_count INT,
    reach_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转化-价值特性桥接表
CREATE TABLE public.bridge_conv_vpt (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conv_channel_id UUID REFERENCES public.dim_conv_channel(conv_channel_id),
    vpt_id UUID REFERENCES public.dim_vpt(vpt_id),
    conversion_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SKU-产品特性桥接表
CREATE TABLE public.bridge_sku_pft (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID REFERENCES public.dim_sku(sku_id),
    pft_id UUID REFERENCES public.dim_pft(pft_id),
    weight DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 价值特性-产品特性桥接表
CREATE TABLE public.bridge_vpt_pft (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vpt_id UUID REFERENCES public.dim_vpt(vpt_id),
    pft_id UUID REFERENCES public.dim_pft(pft_id),
    correlation DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 归因桥接表
CREATE TABLE public.bridge_attribution (
    attribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES public.fact_order(order_id),
    touchpoint_type VARCHAR(20),
    touchpoint_id UUID,
    attribution_value DECIMAL(10,2),
    shapley_value DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_order_date ON public.fact_order(order_date);
CREATE INDEX idx_order_customer ON public.fact_order(customer_id);
CREATE INDEX idx_order_channel ON public.fact_order(channel_id);
CREATE INDEX idx_attribution_order ON public.bridge_attribution(order_id);
CREATE INDEX idx_attribution_touchpoint ON public.bridge_attribution(touchpoint_type, touchpoint_id);