## 数据溯源与采集设计（ERP/第三方/人工导入 → 商业模式分析）

### 目标
- 将企业现有系统（ERP/财务/CRM/供应链等）与人工导入的数据，按“分层建模 + 血缘溯源”的方式接入，并生成可用于商业模式分析（资产/能力/价值/增量/反馈/模型参数）的标准数据；支持端到端对账、质量控制与可追溯性。
---

## 三点五、编排与人机协同（自动 + 人工）

- 自动化流水线（统一编排）
  - 入口：系统同步（API/CDC/SFTP/消息）与人工导入（模板化文件）共用同一批次引擎。
  - 步骤：结构/类型校验 → 标准化与维表匹配 → 业务口径与派生 → 质量/异常检测 → 入库落地。
  - 结果：每步产出写入批次与日志表，失败行进入“待处理队列”。

- 人工参与（最小必要）
  - 待处理队列：结构错误、枚举缺失、低置信匹配、对账偏差、时序异常。
  - 批量修复：候选别名/标准值一键替换、差异预览（before/after）、CSV 导出/回传。
  - 审计闭环：`ingestion_actions_log` 记录操作者、前后差异与规则变更。

- 可学习机制
  - 学习来源：人工确认结果沉淀为别名字典/规则参数；低置信阈值自适应。
  - 回滚与版本：`transform_rules` 带版本与校验和；效果不佳可快速回退。

### API 设计概览（可先以 Mock 形式上线）

- 批次与文件
  - POST `/ingestion/batches:start`（启动批次）
  - GET  `/ingestion/batches/{id}`（查询状态）
  - POST `/ingestion/upload`（上传文件并做头部/样例校验）

- 校验与异常
  - GET  `/ingestion/issues?batch_id=...`（待处理项列表）
  - GET  `/ingestion/issues/{id}/preview`（修复前后预览）
  - POST `/ingestion/issues/{id}/apply`、POST `/ingestion/issues/bulk-apply`（应用修复）

- 规则与字典
  - GET/POST `/ingestion/rules`（转换/匹配规则）
  - GET/POST `/ingestion/alias-dictionary`（别名字典/标准值映射）

- 对账与质量
  - GET `/ingestion/reconcile/report?batch_id=...`
  - GET `/data-quality/checks?batch_id=...`

- 审计与回放
  - GET `/ingestion/actions?batch_id=...`
  - POST `/ingestion/batches/{id}:replay`

---

## 一、总体架构与分层

- L0 原始分层（Raw Staging / 01）
  - 作用：按批次原样落库，保留源系统主键、字段与文件指纹；仅做轻清洗（强制类型/时间/编码）。
  - 关键列：`source_system`、`source_table`、`source_pk`、`extract_ts`、`batch_id`、`payload_json`/镜像列、`row_checksum`。
  - 来源：
    - 系统同步：API/CDC/导出文件（CSV/Excel/Parquet）。
    - 人工导入：模板化 Excel/CSV（见 templates/EXCEL_TEMPLATES_SPEC.md）。

- L1 标准事实与维度（Decision Controllable Facts / 02）
  - 作用：统一业务键（客户/产品/组织/渠道），币种/时区/税率口径对齐；绑定维表（SCD2）；沉淀可控事实。
  - 保留血缘：`source_batch_id`、`src_row_ref`、`transform_rule_id`、`standardized_ts`。

- L2 外部/行业事实（External Business Facts / 03）
  - 作用：行业基准、竞品、宏观数据与内部事实对齐；标注 `source_provider`、`license_tag`。

- L3 商业模式分析层（Marginal Analysis / 08–13）
  - 主数据：`core_asset_master`、`core_capability_master`、`product_value_item_master`。
  - 增量指标：`monthly_delta_metrics`（效率/价值/收入/利润子集，统一“月度增量 Δ（本月-上月）+ 基线/带宽/阈值”）。
  - 动态反馈：`dynamic_feedback_config`、`feedback_execution_logs`。
  - 模型参数：`model_parameters_storage`、边际贡献缓存。
  - 溯源：`calc_batch_id`、`upstream_fact_ref`、`params_hash`、`quality_score(aic/r2/ci)`。

---

## 二、采集方式（支持人工与系统双通道）

- 系统同步（推荐优先）
  - 批量/增量：定时 API 拉取、SFTP 文件、消息队列/CDC。
  - 接口策略：分页+时间窗口；失败重试与幂等；批次日志。

- 人工导入（可运营自助）
  - 模板：客户/产品/订单行/费用/采购/入库等标准模板，字段、类型、枚举与示例详见 `templates/EXCEL_TEMPLATES_SPEC.md`。
  - 校验：表头校验、类型/必填/枚举/外键检查；失败回执与定位。
  - 归档：原文件以 `batch_id` 命名归档，留存文件指纹与存储 URI。

---

## 三、质量控制与对账

- 质量检查（L0→L1 / L1→L3）
  - 规则：重复/缺失、主外键、金额合计、日期越界、币种与税率口径。
  - 执行：每批 `data_quality_checks` 写入结果（规则 ID、通过/失败、失败明细数）。

- 对账
  - 业务对账：ERP 日/周/月总额 vs 标准事实聚合差异 < 阈值；差异清单可追溯到 L0 源行。
  - 统计对账：增量合计 ≈ 当期值-上期值；基线与预测残差在置信区间内。

---

## 四、血缘登记与可追溯性

- 批次日志：`ingestion_batches(batch_id, source_system, window, file_list, started_at, completed_at, status)`、`ingestion_logs(batch_id, table, row_cnt, checksum, error_cnt)`。
- 行级血缘：分析层每张表带 `source_batch_id`、`upstream_table`、`upstream_pk(s)`、`transform_rule_id`。
- 规则登记：`transform_rules(rule_id, rule_name, rule_sql, version, checksum)`；分析表记录 `calc_batch_id`、`model_type`、`params_hash`、`quality_score`。

---

## 五、计算与口径（商业模式分析专用）

- 统一月度增量 Δ：所有链路量以 Δ（本月-上月）建模；同时保留当期值、基线、置信带与阈值。
- 价值三分与销量分解：内在/认知/体验与 WTP；首单/复购/交叉销售分项；利润=收入-成本。
- 弹性与阈值：估计“单位投入→Δprofit”的斜率，并识别饱和区；用于优化器排序。

---

## 六、现有实现状态（本仓库）

- 已有
  - 分层脚本：`database/postgresql/01_raw_data_staging.sql`、`02_decision_controllable_facts.sql`、`03_external_business_facts.sql`。
  - 商业模式表组：`docs/database/MARGINAL_ANALYSIS_DATABASE_DESIGN.md` 与 `supabase/sql/08–13`（资产/能力/价值项、月度增量、动态反馈、模型参数）。
  - 文档：ETL/模板/算法/基线与阈值说明（`docs/data-import/*`、`docs/algorithms/*`）。
  - 运行：当前支持“无数据库 Mock”验收；服务可加载核心 AI 路由与边际分析 Mock 路由。

- 待补
  - 批次与质量表：`ingestion_batches`、`ingestion_logs`、`data_quality_checks`、`transform_rules`（脚本可合并入 01–03）。
  - 一键迁移与编排脚本：扩展 `scripts/database_migration.py`；推荐 DBT/Airflow/Prefect 工作流。
  - 数据导入 API：保留文件上传与批次登记接口（当前部分通用端点为稳定起见未挂载，需要以 Mock/只读方式逐步接回）。
  - 对账报表：差异报表/质量仪表盘（可先以 SQL + 简单 API 导出）。

---

## 七、与 Lovable 的分工建议

- Lovable 侧（数据面/运维）
  - 连接与采集：对接 ERP/财务/CRM/API 与 SFTP/消息；落地 L0 批次表与文件归档。
  - 编排与运维：DBT/Airflow 作业编排、调度与监控；生产库权限与存储策略。
  - 质量与对账：实施规则库、失败回执、差异报表；建设数据字典与口径说明。

- Cursor 侧（逻辑面/算法与接口）
  - 标准化转换与维度：L1/L2 规则定义与 SQL；SCD2 维表设计。
  - 分析层计算：月度增量/基线/阈值/弹性估计与参数存储；优化器与建议生成。
  - API 与文档：导入/质量/对账/分析结果的 API（可 Mock 先上线）与用户文档、验收脚本。

---

## 八、阶段性规划（建议三阶段）

1) M1：落地与可见
   - 增补批次/质量/规则表；完善 01–03 与 08–13 脚本；提供批次级导入与查询 API（Mock 可用）。
   - 交付对账 SQL 与简易报表；完成从样例 ERP 文件→分析层的端到端演示。

2) M2：稳态与自动化
   - 接入 1 个真实 ERP 源（或 SFTP 文件）；引入编排（DBT/Airflow）与质量门禁；
   - 统一“增量 + 置信带 + 阈值”产出；上线边际优化建议的只读接口。

3) M3：规模与治理
   - 多源并行与冲突合并；治理策略与权限分层；指标字典/血缘可视化；
   - 完成 Mock→持久化切换与压测；建设仪表盘（质量/对账/效能）。

---

## 九、样例字段清单（摘录）

- L0（销售行）：`batch_id, source_system, source_table, source_pk, order_id, order_line_id, customer_code, product_code, currency, amount, tax, order_ts, payload_json, row_checksum, extract_ts`
- L1（标准销售事实）：`fact_id, order_line_sk, customer_sk, product_sk, org_sk, channel_sk, amount_ccy, amount_cny, tax_cny, order_ym, source_batch_id, src_row_ref, transform_rule_id`
- L3（月度增量）：`metric_code, reporting_month, delta_value, baseline_value, band_low, band_high, threshold_low, threshold_high, trend_strength, calc_batch_id, upstream_fact_ref`

---

## 十、说明
- 在 Lovable 未就绪前，系统以 Mock/只读模式提供端到端演示；连库后可直接执行 01–03、08–13 的 SQL 迁移并启用持久化。
- 质量与对账优先，确保“每个分析结果都可溯源到原始批次与源行”。


