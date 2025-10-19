-- 媒体-价值主张桥接表
CREATE TABLE IF NOT EXISTS bridge_media_vpt (
    media_id String,
    vpt_id String,
    weight Float32,
    update_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(update_time)
ORDER BY (media_id, vpt_id);

-- 转化渠道-价值主张桥接表
CREATE TABLE IF NOT EXISTS bridge_conv_vpt (
    conv_id String,
    vpt_id String,
    update_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(update_time)
ORDER BY (conv_id, vpt_id);

-- SKU-产品特性桥接表
CREATE TABLE IF NOT EXISTS bridge_sku_pft (
    sku_id String,
    pft_id String,
    weight Float32,
    update_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(update_time)
ORDER BY (sku_id, pft_id);

-- 价值主张-产品特性因果桥接表
CREATE TABLE IF NOT EXISTS bridge_vpt_pft (
    vpt_id String,
    pft_id String,
    causal_score Float32,
    update_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(update_time)
ORDER BY (vpt_id, pft_id);

-- 订单归因桥接表（多触点Shapley值）
CREATE TABLE IF NOT EXISTS bridge_attribution (
    order_id String,
    media_id String,
    conv_id String,
    weight Float32 COMMENT 'Shapley归因权重',
    seq UInt8 COMMENT '触点序号',
    touchpoint_time DateTime COMMENT '触点时间',
    update_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(update_time)
ORDER BY (order_id, seq);


