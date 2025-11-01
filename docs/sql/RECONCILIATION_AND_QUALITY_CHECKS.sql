-- Reconciliation & Data Quality SQL checklist (sales/purchase/expense)

-- 1) SALES - header totals vs fact aggregation (monthly)
-- Replace table names/keys to your L0/L1 naming
-- 业务对账：原系统订单表（月）与标准事实聚合（月）差异
WITH src AS (
  SELECT DATE_TRUNC('month', order_ts) AS ym, SUM(amount_cny) AS total_src
  FROM l0_sales_orders
  GROUP BY 1
), fact AS (
  SELECT order_ym AS ym, SUM(amount_cny) AS total_fact
  FROM l1_sales_fact
  GROUP BY 1
)
SELECT s.ym, s.total_src, f.total_fact, (s.total_src - f.total_fact) AS diff
FROM src s
FULL JOIN fact f ON s.ym = f.ym
ORDER BY 1;

-- 2) PURCHASE - duplicates check (order_id + line)
SELECT order_id, order_line_id, COUNT(*) AS cnt
FROM l1_purchase_fact
GROUP BY 1,2
HAVING COUNT(*) > 1;

-- 3) EXPENSE - FK integrity (employee_sk)
SELECT e.expense_id
FROM l1_expense_fact e
LEFT JOIN dim_employee d ON e.employee_sk = d.employee_sk
WHERE d.employee_sk IS NULL
LIMIT 100;

-- 4) SALES - delta vs current-previous sanity
WITH cur AS (
  SELECT order_ym, SUM(amount_cny) AS cur_val
  FROM l1_sales_fact
  GROUP BY 1
), prev AS (
  SELECT order_ym + INTERVAL '1 month' AS order_ym, SUM(amount_cny) AS prev_val
  FROM l1_sales_fact
  GROUP BY 1
), delta AS (
  SELECT reporting_month, SUM(delta_value) AS delta_sum
  FROM monthly_delta_metrics
  WHERE metric_code = 'sales_amount'
  GROUP BY 1
)
SELECT c.order_ym, (c.cur_val - p.prev_val) AS calc_delta, d.delta_sum
FROM cur c
LEFT JOIN prev p ON c.order_ym = p.order_ym
LEFT JOIN delta d ON c.order_ym = d.reporting_month
ORDER BY 1;

-- 5) QUALITY - basic ranges & enums
-- 日期越界
SELECT * FROM l1_sales_fact WHERE order_ts < '2000-01-01' OR order_ts > NOW();
-- 金额负值（按需保留或排除）
SELECT * FROM l1_sales_fact WHERE amount_cny < 0 LIMIT 100;
-- 枚举非法
SELECT DISTINCT channel FROM l1_sales_fact WHERE channel NOT IN ('B2B','B2C','DTC');



