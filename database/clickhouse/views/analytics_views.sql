-- 投入-口碑-销售三段式视图
CREATE MATERIALIZED VIEW IF NOT EXISTS v_vpt_performance
ENGINE = AggregatingMergeTree()
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
        o.amt * b.weight AS attrib_sales
    FROM fact_cost c
    JOIN dim_activity a ON a.activity_id = c.activity_id
    JOIN bridge_attribution b ON b.media_id = arrayElement(a.vpt_list, 1)
    JOIN fact_order o ON o.order_id = b.order_id
    LEFT JOIN fact_voice v ON has(a.vpt_list, v.vpt_id)
)
GROUP BY vpt_id, date_key;

-- 客户旅程视图
CREATE MATERIALIZED VIEW IF NOT EXISTS v_customer_journey
ENGINE = MergeTree()
PARTITION BY toYYYYMM(touchpoint_time)
ORDER BY (customer_id, touchpoint_time)
AS SELECT
    customer_id,
    media_id,
    conv_id,
    touchpoint_time,
    weight,
    seq
FROM bridge_attribution
ORDER BY customer_id, touchpoint_time;

-- 价值主张生命周期视图
CREATE MATERIALIZED VIEW IF NOT EXISTS v_vpt_lifecycle
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(publish_time)
ORDER BY (vpt_id, customer_id, publish_time)
AS SELECT
    vpt_id,
    customer_id,
    lifecycle_stage,
    avgState(awareness_level) AS avg_awareness,
    avgState(acceptance_level) AS avg_acceptance,
    avgState(experience_quality) AS avg_experience,
    countState() AS stage_count,
    publish_time
FROM fact_voice
WHERE vpt_id != ''
GROUP BY vpt_id, customer_id, lifecycle_stage, publish_time;

-- 边际变化检测视图
CREATE MATERIALIZED VIEW IF NOT EXISTS v_marginal_changes
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date_key)
ORDER BY (vpt_id, date_key)
AS SELECT
    vpt_id,
    date_key,
    sumState(cost_amt) AS total_cost,
    avgState(avg_cvrs) AS avg_cvrs,
    sumState(attrib_sales) AS total_sales,
    (sumState(attrib_sales) - sumState(cost_amt)) / sumState(cost_amt) AS roi
FROM v_vpt_performance
GROUP BY vpt_id, date_key;


