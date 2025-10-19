-- 价值主张维度表
CREATE TABLE IF NOT EXISTS dim_vpt (
    vpt_id String,
    vpt_name String,
    category String,
    definition String,
    owner String,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY vpt_id;

-- 产品特性维度表
CREATE TABLE IF NOT EXISTS dim_pft (
    pft_id String,
    pft_name String,
    unit String,
    module String,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY pft_id;

-- 活动维度表
CREATE TABLE IF NOT EXISTS dim_activity (
    activity_id String,
    activity_name String,
    type String,
    vpt_list Array(String),
    pft_list Array(String),
    start_date Date,
    end_date Date,
    dept String,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY activity_id;

-- 媒体渠道维度表
CREATE TABLE IF NOT EXISTS dim_media_channel (
    media_id String,
    media_name String,
    type String,
    vpt_list Array(String),
    pft_list Array(String),
    start_date Date,
    end_date Date,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY media_id;

-- 转化渠道维度表
CREATE TABLE IF NOT EXISTS dim_conv_channel (
    conv_id String,
    conv_name String,
    platform String,
    vpt_list Array(String),
    pft_list Array(String),
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY conv_id;

-- SKU维度表
CREATE TABLE IF NOT EXISTS dim_sku (
    sku_id String,
    sku_name String,
    category String,
    pft_list Array(String),
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY sku_id;

-- 客户维度表
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id String,
    first_media_id String,
    first_conv_id String,
    reg_date Date,
    customer_segment String,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY customer_id;

-- 日期维度表
CREATE TABLE IF NOT EXISTS dim_date (
    date_key Date,
    year UInt16,
    month UInt8,
    week UInt8,
    day UInt8,
    quarter UInt8,
    is_weekend UInt8
) ENGINE = ReplacingMergeTree()
ORDER BY date_key;

-- 供应商维度表
CREATE TABLE IF NOT EXISTS dim_supplier (
    supp_id String,
    supp_name String,
    category String,
    create_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree()
ORDER BY supp_id;


