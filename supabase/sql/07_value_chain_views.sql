-- 价值链桑基图相关视图（简化示例，按最近30天）

-- 示例：按天订单金额
CREATE OR REPLACE VIEW vw_order_daily AS
SELECT date_trunc('day', order_date)::date AS d,
       SUM(order_amount) AS total_amount,
       COUNT(*) AS orders
FROM fact_order
WHERE order_date >= now() - interval '30 days'
GROUP BY 1
ORDER BY 1;

-- 节点视图：固定阶段节点
CREATE OR REPLACE VIEW vw_value_chain_nodes AS
SELECT 'n0'::text AS id, '投入资源'::text AS name UNION ALL
SELECT 'n1','生产' UNION ALL
SELECT 'n2','产品特性' UNION ALL
SELECT 'n3','产品价值' UNION ALL
SELECT 'n4','客户体验' UNION ALL
SELECT 'n5','销售' UNION ALL
SELECT 'n6','销售收入' UNION ALL
SELECT 'n7','成本开支';

-- 链接视图：以订单金额与费用为示例聚合
CREATE OR REPLACE VIEW vw_value_chain_links AS
SELECT 'n0' AS source, 'n1' AS target, COALESCE(SUM(e.expense_amount),0) AS value
FROM fact_expense e
WHERE e.expense_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n1','n2', COALESCE(SUM(p.quantity),0) * 1.0
FROM fact_produce p
WHERE p.produce_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n2','n3',  COALESCE(SUM(o.order_amount),0) * 0.82
FROM fact_order o
WHERE o.order_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n3','n4',  COALESCE(SUM(o.order_amount),0) * 0.78
FROM fact_order o
WHERE o.order_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n4','n5',  COALESCE(SUM(o.order_amount),0) * 0.68
FROM fact_order o
WHERE o.order_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n5','n6',  COALESCE(SUM(o.order_amount),0) * 0.66
FROM fact_order o
WHERE o.order_date >= now() - interval '30 days'
GROUP BY 1,2
UNION ALL
SELECT 'n0','n7', COALESCE(SUM(e.expense_amount),0)
FROM fact_expense e
WHERE e.expense_date >= now() - interval '30 days'
GROUP BY 1,2;





