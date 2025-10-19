-- 订单事实表
CREATE TABLE IF NOT EXISTS fact_order (
    order_id String,
    customer_id String,
    sku_id String,
    conv_id String,
    date_key Date,
    order_type String,
    qty UInt32,
    amt Decimal(18, 2),
    vpt_snap Array(String) COMMENT '价值主张快照',
    pft_snap Array(String) COMMENT '产品特性快照',
    create_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (date_key, customer_id, order_id);

-- 客户声音事实表（整合价值主张生命周期）
CREATE TABLE IF NOT EXISTS fact_voice (
    voice_id String,
    platform String,
    customer_id String,
    vpt_id String,
    pft_id String,
    sentiment String COMMENT '情感：正面/中性/负面',
    mention String COMMENT '提及内容',
    cvrs_score Float32 COMMENT '综合评分',
    -- 【整合1】增加生命周期阶段追踪
    lifecycle_stage Enum8(
        'awareness' = 1,
        'interest' = 2,
        'consideration' = 3,
        'purchase' = 4,
        'retention' = 5,
        'advocacy' = 6
    ) COMMENT '价值主张生命周期阶段',
    stage_transition_from String COMMENT '上一阶段',
    stage_duration_days UInt16 COMMENT '在当前阶段停留时长',
    -- 【整合2】认知质量评分（用于Shapley归因）
    awareness_level Float32 COMMENT '认知水平 1-5分',
    acceptance_level Float32 COMMENT '接纳水平 1-5分',
    experience_quality Float32 COMMENT '体验质量 1-5分',
    publish_time DateTime,
    create_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(publish_time)
ORDER BY (publish_time, platform, customer_id);

-- 成本事实表
CREATE TABLE IF NOT EXISTS fact_cost (
    cost_id String,
    date_key Date,
    activity_id String,
    amount Decimal(18, 2),
    cost_center String,
    vendor_id String,
    create_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (date_key, activity_id, cost_id);

-- 供应商履约事实表
CREATE TABLE IF NOT EXISTS fact_supplier (
    po_id String,
    sku_id String,
    pft_id String,
    supp_id String,
    lead_time UInt16 COMMENT '交货周期(天)',
    fill_rate Float32 COMMENT '订单满足率',
    pass_rate Float32 COMMENT '质检合格率',
    po_date Date,
    create_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(po_date)
ORDER BY (po_date, supp_id, po_id);

-- 生产事实表
CREATE TABLE IF NOT EXISTS fact_produce (
    wo_id String,
    sku_id String,
    pft_id String,
    qty_prod UInt32 COMMENT '生产数量',
    qty_defect UInt32 COMMENT '次品数量',
    yield_rate Float32 COMMENT '良品率',
    produce_date Date,
    create_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(produce_date)
ORDER BY (produce_date, sku_id, wo_id);


