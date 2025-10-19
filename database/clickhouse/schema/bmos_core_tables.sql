-- BMOS系统核心表结构
-- 基于PRD设计的11张表：7张维度表 + 4张桥接表 + 5张事实表

-- ============================================
-- 1. 维度表 (7张)
-- ============================================

-- 1.1 价值主张维度表 (VPT - Value Proposition Tag)
CREATE TABLE IF NOT EXISTS bmos.dim_vpt (
    vpt_id String,
    vpt_name String,
    vpt_category String,
    vpt_description String,
    owner String,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (vpt_id);

-- 1.2 产品特性维度表 (PFT - Product Feature Tag)
CREATE TABLE IF NOT EXISTS bmos.dim_pft (
    pft_id String,
    pft_name String,
    pft_category String,
    pft_description String,
    unit String,
    module String,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (pft_id);

-- 1.3 活动维度表
CREATE TABLE IF NOT EXISTS bmos.dim_activity (
    activity_id String,
    activity_name String,
    activity_type String,
    activity_channel String,
    vpt_list Array(String),
    pft_list Array(String),
    start_date Date,
    end_date Date,
    dept String,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (activity_id);

-- 1.4 媒体渠道维度表
CREATE TABLE IF NOT EXISTS bmos.dim_media_channel (
    media_channel_id String,
    channel_name String,
    channel_type String,
    platform String,
    vpt_list Array(String),
    pft_list Array(String),
    start_date Date,
    end_date Date,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (media_channel_id);

-- 1.5 转化渠道维度表
CREATE TABLE IF NOT EXISTS bmos.dim_conv_channel (
    conv_channel_id String,
    channel_name String,
    channel_type String,
    platform String,
    vpt_list Array(String),
    pft_list Array(String),
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (conv_channel_id);

-- 1.6 SKU维度表
CREATE TABLE IF NOT EXISTS bmos.dim_sku (
    sku_id String,
    sku_code String,
    sku_name String,
    product_category String,
    brand String,
    pft_list Array(String),
    unit_price Float64,
    cost_price Float64,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (sku_id);

-- 1.7 客户维度表
CREATE TABLE IF NOT EXISTS bmos.dim_customer (
    customer_id String,
    customer_segment String,
    region String,
    age_group String,
    gender String,
    first_media_id String,
    first_conv_id String,
    reg_date Date,
    acquisition_channel String,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (customer_id);

-- 1.8 日期维度表
CREATE TABLE IF NOT EXISTS bmos.dim_date (
    date_key Date,
    year UInt16,
    quarter UInt8,
    month UInt8,
    day_of_month UInt8,
    day_of_week UInt8,
    week_of_year UInt8,
    is_weekend UInt8,
    is_holiday UInt8
) ENGINE = MergeTree()
ORDER BY (date_key);

-- 1.9 供应商维度表
CREATE TABLE IF NOT EXISTS bmos.dim_supplier (
    supplier_id String,
    supplier_name String,
    supplier_type String,
    contact_person String,
    contact_email String,
    create_time DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (supplier_id);

-- ============================================
-- 2. 桥接表 (5张)
-- ============================================

-- 2.1 媒体-价值主张桥接表
CREATE TABLE IF NOT EXISTS bmos.bridge_media_vpt (
    media_channel_id String,
    vpt_id String,
    relevance_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (media_channel_id, vpt_id);

-- 2.2 转化渠道-价值主张桥接表
CREATE TABLE IF NOT EXISTS bmos.bridge_conv_vpt (
    conv_channel_id String,
    vpt_id String,
    relevance_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (conv_channel_id, vpt_id);

-- 2.3 SKU-产品特性桥接表
CREATE TABLE IF NOT EXISTS bmos.bridge_sku_pft (
    sku_id String,
    pft_id String,
    relevance_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (sku_id, pft_id);

-- 2.4 价值主张-产品特性因果桥接表
CREATE TABLE IF NOT EXISTS bmos.bridge_vpt_pft (
    vpt_id String,
    pft_id String,
    alignment_score Float64,
    causal_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (vpt_id, pft_id);

-- 2.5 订单归因桥接表（多触点Shapley值）
CREATE TABLE IF NOT EXISTS bmos.bridge_attribution (
    attribution_id String,
    order_id String,
    activity_id String,
    media_channel_id String,
    conv_channel_id String,
    contribution_score Float64,
    contribution_type String,
    seq UInt8,
    touchpoint_time DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (attribution_id, order_id, touchpoint_time);

-- ============================================
-- 3. 事实表 (5张)
-- ============================================

-- 3.1 订单事实表
CREATE TABLE IF NOT EXISTS bmos.fact_order (
    order_id String,
    customer_id String,
    sku_id String,
    conv_channel_id String,
    order_date Date,
    order_timestamp DateTime,
    order_type String,
    quantity UInt32,
    price_per_unit Float64,
    total_revenue Float64,
    total_cost Float64,
    profit Float64,
    order_status String,
    payment_method String,
    vpt_snap Array(String),
    pft_snap Array(String),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_id, customer_id, sku_id, order_timestamp);

-- 3.2 客户声音事实表（整合价值主张生命周期）
CREATE TABLE IF NOT EXISTS bmos.fact_voice (
    voice_id String,
    platform String,
    customer_id String,
    vpt_id String,
    pft_id String,
    feedback_text String,
    sentiment_polarity String,
    sentiment_score Float64,
    emotion_category String,
    mention String,
    cvrs_score Float64,
    -- 价值主张生命周期阶段追踪
    lifecycle_stage Enum8(
        'awareness' = 1,
        'interest' = 2,
        'consideration' = 3,
        'purchase' = 4,
        'retention' = 5,
        'advocacy' = 6
    ),
    stage_transition_from String,
    stage_duration_days UInt16,
    -- 认知质量评分（用于Shapley归因）
    awareness_level Float64,
    acceptance_level Float64,
    experience_quality Float64,
    value_proposition_awareness_score Float64,
    experience_quality_score Float64,
    feedback_source String,
    publish_time DateTime,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(publish_time)
ORDER BY (publish_time, platform, customer_id);

-- 3.3 成本事实表
CREATE TABLE IF NOT EXISTS bmos.fact_cost (
    cost_id String,
    date_key Date,
    cost_timestamp DateTime,
    activity_id String,
    sku_id String,
    supplier_id String,
    amount Float64,
    cost_type String,
    cost_center String,
    vendor_id String,
    description String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (date_key, activity_id, cost_id);

-- 3.4 供应商履约事实表
CREATE TABLE IF NOT EXISTS bmos.fact_supplier (
    supplier_interaction_id String,
    supplier_id String,
    order_id String,
    sku_id String,
    pft_id String,
    interaction_date Date,
    interaction_timestamp DateTime,
    interaction_type String,
    amount Float64,
    lead_time UInt16,
    fill_rate Float64,
    pass_rate Float64,
    delivery_performance_score Float64,
    quality_score Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(interaction_date)
ORDER BY (interaction_date, supplier_id, supplier_interaction_id);

-- 3.5 生产事实表
CREATE TABLE IF NOT EXISTS bmos.fact_produce (
    production_id String,
    sku_id String,
    pft_id String,
    production_date Date,
    production_timestamp DateTime,
    quantity_produced UInt32,
    quantity_defective UInt32,
    production_line String,
    production_cost_per_unit Float64,
    labor_cost Float64,
    material_cost Float64,
    energy_cost Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(production_date)
ORDER BY (production_date, sku_id, production_id);

-- ============================================
-- 4. 分析视图
-- ============================================

-- 4.1 投入-口碑-销售三段式视图
CREATE MATERIALIZED VIEW IF NOT EXISTS bmos.view_vpt_performance
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (vpt_id, date_key)
AS SELECT
    vpt_id,
    date_key,
    sumState(cost_amt) AS cost_amt,
    avgState(cvrs_score) AS avg_cvrs,
    sumState(attrib_sales) AS attrib_sales
FROM (
    SELECT
        a.vpt_id,
        c.date_key,
        c.amount AS cost_amt,
        v.cvrs_score,
        o.total_revenue * b.contribution_score AS attrib_sales
    FROM bmos.fact_cost c
    JOIN bmos.dim_activity a ON a.activity_id = c.activity_id
    JOIN bmos.bridge_attribution b ON b.activity_id = c.activity_id
    JOIN bmos.fact_order o ON o.order_id = b.order_id
    LEFT JOIN bmos.fact_voice v ON has(a.vpt_list, v.vpt_id)
)
GROUP BY vpt_id, date_key;

-- 4.2 客户价值细分视图
CREATE MATERIALIZED VIEW IF NOT EXISTS bmos.view_customer_value_segment
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (customer_id, date_key)
AS SELECT
    c.customer_id,
    toDate(o.order_timestamp) AS date_key,
    sumState(o.total_revenue) AS total_revenue,
    sumState(o.profit) AS total_profit,
    countState(o.order_id) AS order_count,
    countState(v.voice_id) AS feedback_count,
    avgState(v.experience_quality_score) AS avg_satisfaction,
    avgState(v.value_proposition_awareness_score) AS avg_awareness
FROM bmos.dim_customer c
LEFT JOIN bmos.fact_order o ON c.customer_id = o.customer_id
LEFT JOIN bmos.fact_voice v ON c.customer_id = v.customer_id
GROUP BY c.customer_id, date_key;

-- 4.3 归因汇总视图
CREATE MATERIALIZED VIEW IF NOT EXISTS bmos.view_attribution_summary
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (activity_id, media_channel_id, conv_channel_id, contribution_type, date_key)
AS SELECT
    ba.activity_id,
    ba.media_channel_id,
    ba.conv_channel_id,
    ba.contribution_type,
    toDate(ba.touchpoint_time) AS date_key,
    sumState(ba.contribution_score) AS total_contribution_score,
    sumState(fo.total_revenue * ba.contribution_score) AS total_revenue_attributed
FROM bmos.bridge_attribution ba
LEFT JOIN bmos.fact_order fo ON ba.order_id = fo.order_id
GROUP BY ba.activity_id, ba.media_channel_id, ba.conv_channel_id, ba.contribution_type, date_key;

-- 4.4 资源成本效率视图
CREATE MATERIALIZED VIEW IF NOT EXISTS bmos.view_resource_cost_efficiency
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (sku_id, date_key)
AS SELECT
    fp.sku_id,
    toDate(fp.production_timestamp) AS date_key,
    sumState(fp.production_cost_per_unit * fp.quantity_produced) AS total_production_cost,
    sumState(fo.total_revenue) AS total_revenue,
    sumState(fp.quantity_produced) AS total_quantity_produced,
    avgState(fp.quantity_defective) AS avg_defective_quantity
FROM bmos.fact_produce fp
LEFT JOIN bmos.fact_order fo ON fp.sku_id = fo.sku_id AND toDate(fp.production_timestamp) = toDate(fo.order_timestamp)
GROUP BY fp.sku_id, date_key;

