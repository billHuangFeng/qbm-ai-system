# Supabase 数据库设计（BMOS）

本文件描述 BMOS 在 Supabase(PostgreSQL) 上的核心数据模型：维度表、事实表、桥接表、决策管理表与管理者评价/决策循环表，并给出索引与 RLS 策略纲要。

## 表分层
- 维度表（9）: `dim_vpt`, `dim_pft`, `dim_customer`, `dim_channel`, `dim_sku`, `dim_activity`, `dim_media_channel`, `dim_conv_channel`, `dim_supplier`
- 事实表（5）: `fact_order`, `fact_voice`, `fact_expense`, `fact_produce`, `fact_supplier`
- 桥接表（5）: `bridge_media_vpt`, `bridge_conv_vpt`, `bridge_sku_pft`, `bridge_vpt_pft`, `bridge_attribution`
- 决策管理（4）: `decision_hierarchy`, `decision_decomposition`, `decision_kpi`, `decision_execution_link`
- 管理者评价（3）: `manager_evaluation`, `data_clarification`, `metric_confirmation`
- 决策循环（2）: `decision_cycle_trigger_config`, `decision_cycle_execution`

详细字段与 SQL 见 `supabase/sql/*.sql`。

## 主键与外键
- 所有表主键为 `UUID DEFAULT gen_random_uuid()`（维度少数可自然键时保留 UUID 便于一致性）
- 外键均显式声明并在业务关键查询字段上建立索引

## 索引建议
- 订单事实：`fact_order(order_date)`, `fact_order(customer_id)`, `fact_order(channel_id)`
- 归因桥接：`bridge_attribution(order_id)`, `bridge_attribution(touchpoint_type, touchpoint_id)`
- 决策循环：`decision_cycle_execution(trigger_id, execution_status)`
- 评价表：`manager_evaluation(analysis_id, evaluation_date)`

## 视图（示例）
- `vw_order_daily`：按天统计订单金额/数量
- `vw_attribution_summary`：按触点聚合 Shapley 值

## RLS 策略纲要
开启 RLS：
- 对所有表 `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;`
- 策略按组织/项目隔离：
  - 在相关表添加 `org_id UUID` 字段
  - 策略：`USING (auth.uid() = owner_id OR auth.jwt() ->> 'org_id' = org_id::text)`
- 只读匿名策略（如需公开看板）：对特定视图开启只读策略

## 审计与时间戳
- 统一 `created_at TIMESTAMPTZ DEFAULT NOW()`
- 可选 `updated_at` 触发器

## 约束与校验
- `fact_voice.satisfaction_score BETWEEN 1 AND 5`
- 数值字段使用 `NUMERIC/DECIMAL`，金额保留两位小数

## 数据导入与函数
- 通过 Edge Functions 完成 CSV/Excel 导入并落地至事实表
- 复杂计算（Shapley/TOC）通过 Edge Functions 写入 `bridge_attribution` 与分析结果表

## 迁移顺序
1. 01_raw_data_staging.sql
2. 02_decision_controllable_facts.sql
3. 03_external_business_facts.sql
4. 04_bmos_core_tables.sql
5. 05_manager_evaluation.sql
6. 06_decision_cycle_config.sql
