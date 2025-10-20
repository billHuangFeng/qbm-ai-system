# BMOS统一架构文档

## 技术栈

- **前端**: React 19 + TypeScript + Tailwind CSS
- **后端**: Next.js 14 API Routes
- **数据库**: PostgreSQL 15 (Supabase)
- **部署**: Vercel

## 数据流

```
原始数据 → Staging Table → ETL → 业务事实表 → 指标计算 → 管理者评价 → 分析 → 决策
```

## 50张数据表清单

### 原始数据层 (4张表)
1. `raw_data_staging` - 原始数据暂存表
2. `data_import_log` - 数据导入日志表
3. `data_quality_check` - 数据质量检查表
4. `data_mapping_config` - 数据映射配置表

### 业务事实层 (14张表)
#### 决策可控业务事实 (6张表)
5. `fact_expense` - 费用开支事实表
6. `fact_asset_acquisition` - 资产购置事实表
7. `catalog_procurement` - 采购目录管理表
8. `catalog_sales` - 销售目录管理表
9. `fact_rd_project` - 研发项目表
10. `fact_promotion` - 推广活动表

#### 外部业务事实 (3张表)
11. `fact_market_price` - 市场价格变化表
12. `fact_competitor_dynamics` - 竞争对手动态表
13. `fact_voice` - 客户声音事实表

### BMOS核心层 (27张表)
#### 维度表 (9张表)
14. `dim_vpt` - 价值主张标签维度表
15. `dim_pft` - 产品特性标签维度表
16. `dim_core_resource_tags` - 核心资源标签维度表
17. `dim_core_capability_tags` - 核心能力标签维度表
18. `dim_activity` - 活动维度表
19. `dim_media_channel` - 媒体渠道维度表
20. `dim_conv_channel` - 转化渠道维度表
21. `dim_sku` - SKU维度表
22. `dim_customer` - 客户维度表

#### 事实表 (5张表)
23. `fact_order` - 订单事实表
24. `fact_cost` - 成本事实表
25. `fact_supplier` - 供应商事实表
26. `fact_produce` - 生产事实表

#### 桥接表 (5张表)
27. `bridge_media_vpt` - 媒体渠道-价值主张桥接表
28. `bridge_conv_vpt` - 转化渠道-价值主张桥接表
29. `bridge_sku_pft` - SKU-产品特性桥接表
30. `bridge_vpt_pft` - 价值主张-产品特性桥接表
31. `bridge_attribution` - 归因桥接表

#### 层级决策表 (4张表)
32. `hierarchical_decisions` - 层级决策表
33. `decision_decomposition` - 决策分解表
34. `decision_kpi` - 决策KPI表
35. `decision_execution_link` - 决策执行关联表

#### 决策关联表 (4张表)
36. `bridge_decision_core_resources` - 决策-核心资源关联表
37. `bridge_decision_core_capabilities` - 决策-核心能力关联表

### 分析结果层 (5张表)
#### 管理者评价确认 (3张表)
38. `manager_evaluation` - 管理者评价记录表
39. `data_clarification` - 数据澄清记录表
40. `metric_confirmation` - 指标确认记录表

#### 决策循环触发 (2张表)
41. `decision_cycle_trigger_config` - 决策循环触发配置表
42. `decision_cycle_execution` - 决策循环执行记录表

## API端点

### 数据导入
- `POST /api/data-import/upload` - 原始数据上传
- `POST /api/data-import/transform` - ETL数据转化

### 决策循环
- `POST /api/decision-cycle/execute` - 执行决策循环
- `GET /api/decision-cycle/status` - 获取循环状态

### 管理者评价
- `POST /api/manager-evaluation/submit` - 提交管理者评价
- `GET /api/manager-evaluation/tasks` - 获取待评价任务

### 分析引擎
- `POST /api/analysis/shapley-attribution` - Shapley归因分析
- `POST /api/analysis/marginal-impact` - 边际影响分析
- `POST /api/analysis/value-increment` - 价值增量分析

## 组件结构

### 数据导入组件
- `RawDataUploader` - 原始数据上传组件

### 业务事实管理组件
- `ControllableFactsManager` - 可控业务事实管理组件

### 管理者评价组件
- `EvaluationPanel` - 管理者评价面板组件

### 决策循环组件
- `CycleMonitor` - 决策循环监控组件

## 部署架构

```
GitHub Repository
       ↓
   Vercel (自动部署)
       ↓
   Supabase (数据库)
       ↓
   React App (前端)
       ↓
   Next.js API Routes (后端)
```
