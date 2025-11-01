-- 维度表（9张）
CREATE TABLE dim_vpt (
    vpt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vpt_name VARCHAR(100) NOT NULL,
    vpt_category VARCHAR(50),
    vpt_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_pft (
    pft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pft_name VARCHAR(100) NOT NULL,
    pft_category VARCHAR(50),
    pft_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_core_resource_tags (
    crt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crt_name VARCHAR(100) NOT NULL,
    crt_category VARCHAR(50) NOT NULL,
    crt_type VARCHAR(20) NOT NULL,
    crt_description TEXT,
    crt_value DECIMAL(15,2),
    crt_rarity VARCHAR(20),
    crt_control_level DECIMAL(3,2),
    crt_competitiveness DECIMAL(3,2),
    crt_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_core_capability_tags (
    cct_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cct_name VARCHAR(100) NOT NULL,
    cct_category VARCHAR(50) NOT NULL,
    cct_type VARCHAR(20) NOT NULL,
    cct_description TEXT,
    cct_maturity_level DECIMAL(3,2),
    cct_development_cost DECIMAL(15,2),
    cct_competitive_advantage DECIMAL(3,2),
    cct_transferability DECIMAL(3,2),
    cct_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_activity (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_name VARCHAR(100),
    activity_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_media_channel (
    media_channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_name VARCHAR(100),
    channel_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_conv_channel (
    conv_channel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_name VARCHAR(100),
    channel_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_sku (
    sku_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_name VARCHAR(200),
    sku_category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE dim_customer (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name VARCHAR(200),
    customer_segment VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 事实表（5张）
CREATE TABLE fact_order (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES dim_customer(customer_id),
    sku_id UUID REFERENCES dim_sku(sku_id),
    order_date DATE,
    order_amount DECIMAL(15,2),
    quantity INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE fact_cost (
    cost_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID REFERENCES dim_activity(activity_id),
    cost_date DATE,
    cost_amount DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE fact_supplier (
    supplier_record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id VARCHAR(50),
    supply_date DATE,
    supply_amount DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE fact_produce (
    produce_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID REFERENCES dim_sku(sku_id),
    produce_date DATE,
    quantity INT,
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 桥接表（5张）
CREATE TABLE bridge_media_vpt (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_channel_id UUID REFERENCES dim_media_channel(media_channel_id),
    vpt_id UUID REFERENCES dim_vpt(vpt_id),
    weight DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bridge_conv_vpt (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conv_channel_id UUID REFERENCES dim_conv_channel(conv_channel_id),
    vpt_id UUID REFERENCES dim_vpt(vpt_id),
    weight DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bridge_sku_pft (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID REFERENCES dim_sku(sku_id),
    pft_id UUID REFERENCES dim_pft(pft_id),
    weight DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bridge_vpt_pft (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vpt_id UUID REFERENCES dim_vpt(vpt_id),
    pft_id UUID REFERENCES dim_pft(pft_id),
    correlation DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bridge_attribution (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES fact_order(order_id),
    touchpoint_type VARCHAR(50),
    touchpoint_id UUID,
    attribution_value DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 层级决策表（4张）
CREATE TABLE hierarchical_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_name VARCHAR(200),
    decision_level VARCHAR(20),
    parent_decision_id UUID,
    decision_date DATE,
    decision_status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE decision_decomposition (
    decomposition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    child_decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    decomposition_logic TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE decision_kpi (
    kpi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    kpi_name VARCHAR(100),
    target_value DECIMAL(10,2),
    actual_value DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE decision_execution_link (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    execution_type VARCHAR(50),
    execution_id UUID,
    link_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 决策-核心资源关联表
CREATE TABLE bridge_decision_core_resources (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    crt_id UUID REFERENCES dim_core_resource_tags(crt_id),
    resource_intent VARCHAR(100),
    control_target DECIMAL(3,2),
    current_control_level DECIMAL(3,2),
    investment_amount DECIMAL(15,2),
    expected_roi DECIMAL(5,4),
    priority_level VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 决策-核心能力关联表
CREATE TABLE bridge_decision_core_capabilities (
    bridge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    cct_id UUID REFERENCES dim_core_capability_tags(cct_id),
    capability_intent VARCHAR(100),
    development_target DECIMAL(3,2),
    current_maturity_level DECIMAL(3,2),
    development_investment DECIMAL(15,2),
    expected_advantage DECIMAL(3,2),
    priority_level VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);




