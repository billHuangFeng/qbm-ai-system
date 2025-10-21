# 边际影响分析系统数据库设计（PostgreSQL/Supabase）

## 📋 概述

本文档定义边际影响分析系统的完整数据库Schema，包含6个SQL文件（08-13），共计27张表：
- **清单主数据表**（3张）：核心资产清单、核心能力清单、产品价值评估项清单
- **预测与成果表**（6张）：资产现金流预测、资产累计值、能力稳定成果、能力价值历史
- **价值评估表**（3张）：内在价值评估、认知价值评估、体验价值评估
- **增量指标表**（3张）：效率增量、产品价值增量、收入利润增量
- **动态反馈表**（3张）：利润反哺资产配置、能力价值反馈配置、反馈执行日志
- **模型参数表**（2张）：模型拟合结果、边际贡献缓存

## 🗂️ SQL文件清单

| SQL文件 | 表数量 | 主要内容 | 依赖关系 |
|---------|--------|---------|---------|
| `08_asset_master_and_projection.sql` | 3 | 资产清单+现金流预测+累计值 | 无 |
| `09_capability_master_and_value.sql` | 4 | 能力清单+稳定成果+价值历史 | 无 |
| `10_value_item_master_and_assessment.sql` | 4 | 价值评估项清单+三类价值评估 | 无 |
| `11_monthly_delta_metrics.sql` | 3 | 效率/价值/收入利润增量 | 08, 09, 10 |
| `12_dynamic_feedback_config.sql` | 3 | 动态反馈配置+执行日志 | 08, 09 |
| `13_model_parameters.sql` | 2 | 模型拟合结果+边际贡献缓存 | 所有表 |

---

## 📊 详细表结构设计

### 文件1: `supabase/sql/08_asset_master_and_projection.sql`

#### 表1.1: `core_asset_master` - 核心资产清单表（主数据）

**业务含义**: 管理企业所有核心资产的基础信息，如生产设备、专利、品牌、物流网络、门店等。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `asset_id` | UUID | PRIMARY KEY | 资产唯一标识 | `a1b2c3d4-...` |
| `asset_code` | VARCHAR(50) | UNIQUE NOT NULL | 资产编号（业务唯一） | `A001` |
| `asset_name` | VARCHAR(200) | NOT NULL | 资产名称 | `生产线甲-数控机床` |
| `asset_category` | VARCHAR(50) | NOT NULL | 一级分类 | `production`/`rd`/`dissemination`/`delivery`/`channel` |
| `asset_subcategory` | VARCHAR(50) | NULL | 二级分类 | `设备技术`/`专利`/`品牌`/`物流网络`/`门店` |
| `description` | TEXT | NULL | 资产描述 | `五轴联动数控机床，精度±0.001mm` |
| `acquisition_date` | DATE | NULL | 购置日期 | `2024-01-15` |
| `acquisition_cost` | DECIMAL(15,2) | NULL | 购置成本 | `5000000.00` |
| `ownership_type` | VARCHAR(20) | NULL | 所有权类型 | `owned`/`leased`/`licensed` |
| `expected_life_years` | INT | NULL | 预期使用年限 | `10` |
| `current_status` | VARCHAR(20) | DEFAULT 'active' | 当前状态 | `active`/`inactive`/`disposed` |
| `responsible_department` | VARCHAR(100) | NULL | 责任部门 | `生产部` |
| `responsible_person` | VARCHAR(100) | NULL | 责任人 | `张三` |
| `tags` | JSONB | NULL | 自定义标签 | `{"strategic": true, "core": true}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_asset_master_category ON core_asset_master(asset_category, current_status);
CREATE INDEX idx_asset_master_code ON core_asset_master(asset_code);
```

**业务规则**:
- `asset_code` 必须唯一，建议格式：`{类别首字母}{3位数字}`（如A001-生产资产001）
- `asset_category` 枚举值：`production`（生产）、`rd`（研发）、`dissemination`（播传）、`delivery`（交付）、`channel`（渠道）
- `current_status` 枚举值：`active`（使用中）、`inactive`（闲置）、`disposed`（已处置）

---

#### 表1.2: `asset_cashflow_projection` - 核心资产现金流预测表

**业务含义**: 记录每项核心资产未来5年的现金流预测，用于计算NPV（净现值）和月度资产增量。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `projection_id` | UUID | PRIMARY KEY | 预测记录唯一标识 | `b2c3d4e5-...` |
| `asset_id` | UUID | NOT NULL, FK | 关联资产清单 | `a1b2c3d4-...` |
| `baseline_year` | INT | DEFAULT 2024 | 基准年（历史平均） | `2024` |
| `baseline_cashflow` | DECIMAL(15,2) | NULL | 基准现金流（无该资产时） | `1000000.00` |
| `year_1_cashflow` | DECIMAL(15,2) | NULL | 未来第1年现金流 | `800000.00` |
| `year_2_cashflow` | DECIMAL(15,2) | NULL | 未来第2年现金流 | `900000.00` |
| `year_3_cashflow` | DECIMAL(15,2) | NULL | 未来第3年现金流 | `950000.00` |
| `year_4_cashflow` | DECIMAL(15,2) | NULL | 未来第4年现金流 | `850000.00` |
| `year_5_cashflow` | DECIMAL(15,2) | NULL | 未来第5年现金流 | `750000.00` |
| `discount_rate` | DECIMAL(5,4) | DEFAULT 0.08 | WACC折现率 | `0.0800` |
| `npv_total` | DECIMAL(15,2) | NULL | 5年现金流增量现值 | `3325000.00` |
| `monthly_asset_delta` | DECIMAL(15,2) | NULL | 月度资产增量=npv÷60 | `55416.67` |
| `projection_date` | DATE | NOT NULL | 预测日期 | `2024-10-01` |
| `scenario` | VARCHAR(20) | DEFAULT 'neutral' | 情景类型 | `conservative`/`neutral`/`optimistic` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `ERP财务模块+第三方估值` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_asset_cashflow_asset ON asset_cashflow_projection(asset_id, projection_date);
```

**外键**:
```sql
FOREIGN KEY (asset_id) REFERENCES core_asset_master(asset_id) ON DELETE CASCADE
```

**业务规则**:
- `npv_total` 计算公式: `Σ((year_n_cashflow - baseline_cashflow) / (1 + discount_rate)^n)` for n=1 to 5
- `monthly_asset_delta` 计算公式: `npv_total / 60`（5年=60个月）
- 支持多情景预测（保守/中性/乐观），默认使用中性情景

---

#### 表1.3: `asset_accumulation` - 核心资产累计值表

**业务含义**: 追踪每项核心资产每月的累计值和月度增量，用于计算资产基数和效率。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `accumulation_id` | UUID | PRIMARY KEY | 累计记录唯一标识 | `c3d4e5f6-...` |
| `asset_id` | UUID | NOT NULL, FK | 关联资产清单 | `a1b2c3d4-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `accumulated_value` | DECIMAL(15,2) | NULL | 截至本月累计资产值 | `332500.00` |
| `monthly_delta` | DECIMAL(15,2) | NULL | 本月增量（从projection提取） | `55416.67` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE UNIQUE INDEX idx_asset_accum_unique ON asset_accumulation(asset_id, month_date);
CREATE INDEX idx_asset_accum_date ON asset_accumulation(month_date);
```

**外键**:
```sql
FOREIGN KEY (asset_id) REFERENCES core_asset_master(asset_id) ON DELETE CASCADE
```

**业务规则**:
- `accumulated_value` = 上月累计值 + `monthly_delta`
- 每个资产每月仅一条记录

---

### 文件2: `supabase/sql/09_capability_master_and_value.sql`

#### 表2.1: `core_capability_master` - 核心能力清单表（主数据）

**业务含义**: 管理企业所有核心能力的基础信息，如生产技师团队、研发算法、营销内容能力、物流时效能力、渠道终端能力等。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `capability_id` | UUID | PRIMARY KEY | 能力唯一标识 | `d4e5f6g7-...` |
| `capability_code` | VARCHAR(50) | UNIQUE NOT NULL | 能力编号（业务唯一） | `C001` |
| `capability_name` | VARCHAR(200) | NOT NULL | 能力名称 | `生产技师团队-五轴加工` |
| `capability_category` | VARCHAR(50) | NOT NULL | 一级分类 | `production`/`rd`/`dissemination`/`delivery`/`channel` |
| `capability_subcategory` | VARCHAR(50) | NULL | 二级分类 | `技师`/`工艺`/`算法`/`内容`/`时效`/`终端` |
| `description` | TEXT | NULL | 能力描述 | `掌握五轴联动加工技术的技师团队，平均工龄8年` |
| `build_start_date` | DATE | NULL | 能力建设开始日期 | `2023-01-01` |
| `target_maturity_level` | DECIMAL(5,4) | NULL | 目标成熟度（0-1） | `0.9000` |
| `current_maturity_level` | DECIMAL(5,4) | NULL | 当前成熟度（0-1） | `0.7500` |
| `investment_to_date` | DECIMAL(15,2) | NULL | 累计投入 | `2000000.00` |
| `current_status` | VARCHAR(20) | DEFAULT 'building' | 当前状态 | `building`/`stable`/`declining` |
| `responsible_department` | VARCHAR(100) | NULL | 责任部门 | `生产部` |
| `responsible_person` | VARCHAR(100) | NULL | 责任人 | `李四` |
| `tags` | JSONB | NULL | 自定义标签 | `{"core_competency": true, "transferable": false}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_capability_master_category ON core_capability_master(capability_category, current_status);
CREATE INDEX idx_capability_master_code ON core_capability_master(capability_code);
```

**业务规则**:
- `capability_code` 必须唯一，建议格式：`C{3位数字}`（如C001）
- `capability_category` 枚举值：同资产分类
- `current_status` 枚举值：`building`（建设中）、`stable`（稳定）、`declining`（衰退）
- `current_maturity_level` 取值范围：0-1，0.8以上视为成熟

---

#### 表2.2: `capability_stable_outcome` - 核心能力稳定成果表

**业务含义**: 记录每项核心能力的稳定成果指标，用于判定能力是否稳定（连续6个月达标）并计算能力价值。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `outcome_id` | UUID | PRIMARY KEY | 成果记录唯一标识 | `e5f6g7h8-...` |
| `capability_id` | UUID | NOT NULL, FK | 关联能力清单 | `d4e5f6g7-...` |
| `outcome_metric` | VARCHAR(100) | NULL | 成果指标名称 | `机床精度合格率` |
| `baseline_value` | DECIMAL(10,4) | NULL | 基准值（无能力时） | `0.9000` |
| `target_value` | DECIMAL(10,4) | NULL | 目标值（有能力稳定后） | `0.9600` |
| `current_value` | DECIMAL(10,4) | NULL | 当前值 | `0.9550` |
| `stable_months` | INT | DEFAULT 0 | 连续稳定月数 | `5` |
| `is_stable` | BOOLEAN | DEFAULT false | 是否达到稳定（连续6个月） | `false` |
| `annual_revenue_impact` | DECIMAL(15,2) | NULL | 稳定成果对应年度收益 | `5400000.00` |
| `contribution_percentage` | DECIMAL(5,4) | NULL | 贡献百分比=(target-baseline)/target | `0.0625` |
| `monthly_capability_value` | DECIMAL(15,2) | NULL | 月度能力价值=年度收益×贡献%÷12 | `28125.00` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `MES质检模块` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_capability_outcome_cap ON capability_stable_outcome(capability_id, month_date);
```

**外键**:
```sql
FOREIGN KEY (capability_id) REFERENCES core_capability_master(capability_id) ON DELETE CASCADE
```

**业务规则**:
- `is_stable` = true 当 `stable_months` ≥ 6 且 `|current_value - target_value| / target_value` < 5%
- `contribution_percentage` 计算公式: `(target_value - baseline_value) / target_value`
- `monthly_capability_value` 计算公式: `annual_revenue_impact × contribution_percentage ÷ 12`

---

#### 表2.3: `capability_value_history` - 核心能力价值历史表

**业务含义**: 追踪每项核心能力每月的能力价值和月度增量，用于计算ROI和动态反馈调整。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `history_id` | UUID | PRIMARY KEY | 历史记录唯一标识 | `f6g7h8i9-...` |
| `capability_id` | UUID | NOT NULL, FK | 关联能力清单 | `d4e5f6g7-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `capability_value` | DECIMAL(15,2) | NULL | 本月能力价值 | `28125.00` |
| `value_delta` | DECIMAL(15,2) | NULL | 本月增量（△能力价值） | `1250.00` |
| `roi` | DECIMAL(5,4) | NULL | ROI=能力价值/能力投入成本 | `0.1500` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE UNIQUE INDEX idx_capability_value_unique ON capability_value_history(capability_id, month_date);
CREATE INDEX idx_capability_value_date ON capability_value_history(month_date);
```

**外键**:
```sql
FOREIGN KEY (capability_id) REFERENCES core_capability_master(capability_id) ON DELETE CASCADE
```

**业务规则**:
- `value_delta` = 本月`capability_value` - 上月`capability_value`
- `roi` = `capability_value` / 本月能力投入成本（从其他表关联）

---

### 文件3: `supabase/sql/10_value_item_master_and_assessment.sql`

#### 表3.1: `product_value_item_master` - 产品价值评估项清单表（主数据）

**业务含义**: 管理产品价值评估的具体项目，分为内在价值（需求/功能）、认知价值（品牌/认知）、体验价值（体验点）三大类。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `item_id` | UUID | PRIMARY KEY | 评估项唯一标识 | `g7h8i9j0-...` |
| `item_code` | VARCHAR(50) | UNIQUE NOT NULL | 评估项编号（业务唯一） | `IV001` |
| `item_name` | VARCHAR(200) | NOT NULL | 评估项名称 | `需求点1-加工精度` |
| `value_type` | VARCHAR(50) | NOT NULL | 价值类型 | `intrinsic`/`cognitive`/`experiential` |
| `item_category` | VARCHAR(50) | NULL | 评估项类别 | `need`/`feature`/`brand`/`experience_point` |
| `description` | TEXT | NULL | 评估项描述 | `客户对加工精度的需求，目标±0.001mm` |
| `measurement_method` | TEXT | NULL | 测量方法描述 | `产品测试报告-精度合格率` |
| `target_value` | DECIMAL(10,4) | NULL | 目标值 | `0.9500` |
| `weight` | DECIMAL(5,4) | NULL | 在该类价值中的权重 | `0.2000` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `产品测试报告` |
| `is_active` | BOOLEAN | DEFAULT true | 是否启用 | `true` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_value_item_type ON product_value_item_master(value_type, is_active);
CREATE INDEX idx_value_item_code ON product_value_item_master(item_code);
```

**业务规则**:
- `item_code` 格式建议：`{类型首字母}{序号}`（如IV001-内在价值001，CV001-认知价值001，EV001-体验价值001）
- `value_type` 枚举值：`intrinsic`（内在价值）、`cognitive`（认知价值）、`experiential`（体验价值）
- `weight` 所有同类价值评估项的权重之和应为1.0

---

#### 表3.2: `intrinsic_value_assessment` - 内在价值评估表

**业务含义**: 记录每月产品内在价值的评估结果，包括需求覆盖率、满足深度、独特性分数。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `assessment_id` | UUID | PRIMARY KEY | 评估记录唯一标识 | `h8i9j0k1-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `need_coverage_rate` | DECIMAL(5,4) | NULL | 需求覆盖率 | `0.6670` |
| `satisfaction_depth` | DECIMAL(5,4) | NULL | 满足深度 | `0.6250` |
| `uniqueness_score` | DECIMAL(5,4) | NULL | 独特性分数 | `0.0950` |
| `overall_score` | DECIMAL(5,4) | NULL | 综合得分=加权计算 | `0.6460` |
| `assessment_details` | JSONB | NULL | 评估项明细[{item_id, item_score, weight}] | `[{"item_id": "g7h8i9j0", "item_score": 0.95, "weight": 0.2}]` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `产品测试报告` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_intrinsic_date ON intrinsic_value_assessment(month_date);
```

**业务规则**:
- `overall_score` 计算公式: `(need_coverage_rate × 0.5 + satisfaction_depth × 0.5) × uniqueness_weight`
- `assessment_details` 存储每个评估项的得分，用于追溯

---

#### 表3.3: `cognitive_value_assessment` - 认知价值评估表

**业务含义**: 记录每月产品认知价值的评估结果，包括品牌回忆率、支付意愿偏差、认知偏差。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `assessment_id` | UUID | PRIMARY KEY | 评估记录唯一标识 | `i9j0k1l2-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `brand_recall_rate` | DECIMAL(5,4) | NULL | 品牌回忆率 | `0.5000` |
| `wtp_deviation` | DECIMAL(5,4) | NULL | 支付意愿偏差（实际WTP/内在价值） | `0.9000` |
| `cognitive_deviation` | DECIMAL(5,4) | NULL | 认知偏差（认知价值/内在价值） | `0.9500` |
| `overall_score` | DECIMAL(5,4) | NULL | 综合得分=加权计算 | `0.7100` |
| `assessment_details` | JSONB | NULL | 评估项明细[{item_id, item_score, weight}] | `[{"item_id": "h7h8i9j0", "item_score": 0.5, "weight": 0.3}]` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `客户认知评估表` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_cognitive_date ON cognitive_value_assessment(month_date);
```

**业务规则**:
- `overall_score` 计算公式: `brand_recall_rate × 0.3 + wtp_deviation × 0.4 + cognitive_deviation × 0.3`

---

#### 表3.4: `experiential_value_assessment` - 体验价值评估表

**业务含义**: 记录每月产品体验价值的评估结果，包括体验偏差、场景满意度、行为转化率。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `assessment_id` | UUID | PRIMARY KEY | 评估记录唯一标识 | `j0k1l2m3-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `experience_deviation` | DECIMAL(5,4) | NULL | 体验偏差 | `0.8330` |
| `scenario_satisfaction` | DECIMAL(5,4) | NULL | 场景满意度 | `0.8500` |
| `behavior_conversion` | DECIMAL(5,4) | NULL | 行为转化率（复购/首购） | `0.5400` |
| `overall_score` | DECIMAL(5,4) | NULL | 综合得分=加权计算 | `0.7460` |
| `assessment_details` | JSONB | NULL | 评估项明细[{item_id, item_score, weight}] | `[{"item_id": "i8i9j0k1", "item_score": 0.833, "weight": 0.35}]` |
| `data_source` | VARCHAR(100) | NULL | 数据来源 | `客户体验评估表` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_experiential_date ON experiential_value_assessment(month_date);
```

**业务规则**:
- `overall_score` 计算公式: `experience_deviation × 0.35 + scenario_satisfaction × 0.35 + behavior_conversion × 0.3`

---

### 文件4: `supabase/sql/11_monthly_delta_metrics.sql`

#### 表4.1: `efficiency_delta` - 效率指标增量表

**业务含义**: 记录各环节（生产/研发/播传/交付/渠道）每月的效率值和增量。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `delta_id` | UUID | PRIMARY KEY | 增量记录唯一标识 | `k1l2m3n4-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `efficiency_type` | VARCHAR(50) | NULL | 效率类型 | `production`/`rd`/`dissemination`/`delivery`/`sales` |
| `efficiency_value` | DECIMAL(10,4) | NULL | 效能值 | `0.8500` |
| `value_delta` | DECIMAL(10,4) | NULL | 本月增量（△效能） | `0.0200` |
| `input_factors` | JSONB | NULL | 输入因子{asset_delta, capability_value, asset_base} | `{"asset_delta": 55416.67, "capability_value": 28125, "asset_base": 332500}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_efficiency_date ON efficiency_delta(month_date, efficiency_type);
```

**业务规则**:
- `efficiency_value` 计算公式: `△资产 × △能力价值 ÷ 资产基数`
- `value_delta` = 本月`efficiency_value` - 上月`efficiency_value`

---

#### 表4.2: `product_value_delta` - 产品价值增量表

**业务含义**: 记录三类产品价值（内在/认知/体验）每月的价值分数和增量。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `delta_id` | UUID | PRIMARY KEY | 增量记录唯一标识 | `l2m3n4o5-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `value_type` | VARCHAR(50) | NULL | 价值类型 | `intrinsic`/`cognitive`/`experiential` |
| `value_score` | DECIMAL(10,4) | NULL | 价值分数 | `0.7100` |
| `value_delta` | DECIMAL(10,4) | NULL | 本月增量（△价值） | `0.0150` |
| `contributing_factors` | JSONB | NULL | 贡献因子{efficiency_delta, assessment_score} | `{"efficiency_delta": 0.02, "assessment_score": 0.71}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_product_value_date ON product_value_delta(month_date, value_type);
```

**业务规则**:
- `value_score` 从对应评估表的`overall_score`提取
- `value_delta` = 本月`value_score` - 上月`value_score`

---

#### 表4.3: `revenue_profit_delta` - 收入利润增量表

**业务含义**: 记录每月的首单/复购/追销收入、总收入、总成本、固定成本分摊、利润的增量。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `delta_id` | UUID | PRIMARY KEY | 增量记录唯一标识 | `m3n4o5p6-...` |
| `month_date` | DATE | NOT NULL | 月份（YYYY-MM-01） | `2024-10-01` |
| `first_order_revenue` | DECIMAL(15,2) | NULL | 首单收入增量 | `4070.00` |
| `repeat_order_revenue` | DECIMAL(15,2) | NULL | 复购收入增量 | `3270.00` |
| `cross_sell_revenue` | DECIMAL(15,2) | NULL | 追销收入增量 | `6360.00` |
| `total_revenue_delta` | DECIMAL(15,2) | NULL | 总收入增量 | `13700.00` |
| `total_cost_delta` | DECIMAL(15,2) | NULL | 总成本增量 | `211500.00` |
| `fixed_cost_allocation` | DECIMAL(15,2) | NULL | 固定成本分摊 | `8500.00` |
| `profit_delta` | DECIMAL(15,2) | NULL | 利润增量 | `-206300.00` |
| `breakdown` | JSONB | NULL | 明细{cognitive_value, new_customers, ...} | `{"cognitive_value": 0.71, "new_customers": 500, ...}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_revenue_profit_date ON revenue_profit_delta(month_date);
```

**业务规则**:
- `total_revenue_delta` = `first_order_revenue` + `repeat_order_revenue` + `cross_sell_revenue`
- `profit_delta` = `total_revenue_delta` - `total_cost_delta` - `fixed_cost_allocation`

---

### 文件5: `supabase/sql/12_dynamic_feedback_config.sql`

#### 表5.1: `profit_feedback_asset_config` - 利润反哺资产配置表

**业务含义**: 配置利润反哺各类资产的基准比例和ROI阈值，用于动态调整下季度资产投入。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `config_id` | UUID | PRIMARY KEY | 配置记录唯一标识 | `n4o5p6q7-...` |
| `asset_type` | VARCHAR(50) | NOT NULL | 资产类型 | `production`/`rd`/`dissemination`/`delivery`/`channel` |
| `base_feedback_ratio` | DECIMAL(5,4) | NULL | 基准反哺比例 | `0.2000`（生产20%） |
| `roi_threshold` | DECIMAL(5,4) | DEFAULT 0.15 | ROI阈值（≥则比例+5%） | `0.1500` |
| `adjusted_feedback_ratio` | DECIMAL(5,4) | NULL | 调整后反哺比例 | `0.2500` |
| `is_active` | BOOLEAN | DEFAULT true | 是否启用 | `true` |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_profit_feedback_type ON profit_feedback_asset_config(asset_type, is_active);
```

**业务规则**:
- `adjusted_feedback_ratio` = `base_feedback_ratio` + 0.05（当对应资产的ROI ≥ `roi_threshold`时）
- 基准比例：生产20%、研发30%、播传20%、交付10%、渠道20%

---

#### 表5.2: `capability_value_feedback_config` - 能力-价值反馈配置表

**业务含义**: 配置能力价值优化的目标价值得分和调整系数，用于能力价值动态调整。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `config_id` | UUID | PRIMARY KEY | 配置记录唯一标识 | `o5p6q7r8-...` |
| `capability_type` | VARCHAR(50) | NOT NULL | 能力类型 | `dissemination`（播传） |
| `target_value_score` | DECIMAL(5,4) | NULL | 目标价值得分 | `0.7000`（认知价值70分） |
| `adjustment_coefficient` | DECIMAL(5,4) | NULL | 调整系数（得分低于目标时） | `0.1000`（+10%） |
| `is_active` | BOOLEAN | DEFAULT true | 是否启用 | `true` |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | 更新时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_capability_feedback_type ON capability_value_feedback_config(capability_type, is_active);
```

**业务规则**:
- 触发条件：对应价值得分 < `target_value_score`
- 调整公式：下月能力价值 = 本月能力价值 × (1 + `adjustment_coefficient`)

---

#### 表5.3: `feedback_execution_log` - 反馈执行记录表

**业务含义**: 记录每次动态反馈的执行历史（利润反哺资产/能力价值优化），用于追溯和效果验证。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `log_id` | UUID | PRIMARY KEY | 日志记录唯一标识 | `p6q7r8s9-...` |
| `feedback_type` | VARCHAR(50) | NULL | 反馈类型 | `profit_to_asset`/`capability_to_value` |
| `execution_month` | DATE | NOT NULL | 执行月份 | `2024-10-01` |
| `adjustments` | JSONB | NULL | 调整明细[{asset_type, old_ratio, new_ratio, reason}] | `[{"asset_type": "rd", "old_ratio": 0.3, "new_ratio": 0.35, "reason": "ROI 18%≥15%"}]` |
| `impact_estimation` | JSONB | NULL | 预估影响 | `{"expected_profit_increase": 50000}` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_feedback_log_month ON feedback_execution_log(execution_month, feedback_type);
```

---

### 文件6: `supabase/sql/13_model_parameters.sql`

#### 表6.1: `model_fit_results` - 模型拟合结果表

**业务含义**: 存储时间序列模型拟合的参数和性能指标，用于预测和边际分析。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `model_id` | UUID | PRIMARY KEY | 模型唯一标识 | `q7r8s9t0-...` |
| `function_name` | VARCHAR(100) | NOT NULL | 函数名称 | `asset_cashflow_to_delta` |
| `model_type` | VARCHAR(50) | DEFAULT 'linear_regression' | 模型类型 | `linear_regression`/`prophet` |
| `parameters` | JSONB | NULL | 模型参数{coefficients, r2, mae, ...} | `{"coefficients": [0.5, 0.3], "r2": 0.85, "mae": 0.12}` |
| `r_squared` | DECIMAL(5,4) | NULL | R²（拟合优度） | `0.8500` |
| `mae` | DECIMAL(10,4) | NULL | 平均绝对误差 | `0.1200` |
| `mape` | DECIMAL(5,4) | NULL | 平均绝对百分比误差 | `0.1500` |
| `fitted_date` | DATE | NOT NULL | 拟合日期 | `2024-10-01` |
| `status` | VARCHAR(20) | DEFAULT 'active' | 状态 | `active`/`deprecated` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_model_fit_function ON model_fit_results(function_name, fitted_date);
```

**业务规则**:
- MVP阶段使用`linear_regression`，扩展阶段升级为`prophet`
- 月度重新拟合时，旧模型`status`改为`deprecated`

---

#### 表6.2: `marginal_contribution_cache` - 边际贡献缓存表

**业务含义**: 缓存Shapley边际贡献计算结果，避免重复计算，提高查询性能。

**字段设计**:

| 字段名 | 类型 | 约束 | 说明 | 示例值 |
|--------|------|------|------|--------|
| `calculation_id` | UUID | PRIMARY KEY | 计算记录唯一标识 | `r8s9t0u1-...` |
| `target_metric` | VARCHAR(50) | DEFAULT 'profit' | 目标指标 | `profit`/`revenue` |
| `factor_name` | VARCHAR(100) | NULL | 因子名称 | `△生产资产`/`△研发能力`/`△认知价值` |
| `shapley_value` | DECIMAL(15,4) | NULL | Shapley值 | `12500.5000` |
| `confidence_interval` | JSONB | NULL | 置信区间{lower, upper} | `{"lower": 10000, "upper": 15000}` |
| `calculation_month` | DATE | NOT NULL | 计算月份 | `2024-10-01` |
| `calculation_method` | VARCHAR(50) | DEFAULT 'sensitivity_analysis' | 计算方法 | `sensitivity_analysis`/`shapley_monte_carlo` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | 创建时间 | `2024-10-21 10:30:00+00` |

**索引**:
```sql
CREATE INDEX idx_marginal_contrib_month ON marginal_contribution_cache(calculation_month, target_metric);
CREATE INDEX idx_marginal_contrib_factor ON marginal_contribution_cache(factor_name);
```

**业务规则**:
- MVP阶段使用`sensitivity_analysis`，扩展阶段升级为`shapley_monte_carlo`
- 每月重新计算时更新缓存

---

## 📝 数据流向图

```
┌──────────────────┐
│  清单主数据表    │ (用户手工录入/批量导入)
├──────────────────┤
│ core_asset_master│
│ core_capability_ │
│ product_value_   │
│    item_master   │
└────────┬─────────┘
         │ 关联
         ▼
┌──────────────────┐
│  预测与成果表    │ (通过API计算+录入)
├──────────────────┤
│ asset_cashflow_  │ ← NPV计算引擎
│ capability_      │ ← 能力价值计算引擎
│ *_value_assess   │ ← 价值评估计算引擎
└────────┬─────────┘
         │ 汇总
         ▼
┌──────────────────┐
│  增量指标表      │ (全链路增量计算引擎)
├──────────────────┤
│ efficiency_delta │
│ product_value_   │
│ revenue_profit_  │
└────────┬─────────┘
         │ 分析
         ▼
┌──────────────────┐
│  边际分析与反馈  │ (Shapley+动态反馈引擎)
├──────────────────┤
│ marginal_contrib_│ ← Shapley计算
│ feedback_config  │ ← 动态反馈调整
│ feedback_log     │ ← 执行记录
└──────────────────┘
```

---

## ✅ Lovable实施检查清单

### 数据库创建阶段
- [ ] 创建6个SQL文件，按顺序执行（08→09→10→11→12→13）
- [ ] 验证所有外键关系正确（27张表）
- [ ] 验证所有索引创建成功
- [ ] 配置RLS策略（如果需要多租户隔离）
- [ ] 截图Supabase Schema并提交到GitHub PR

### 数据验证阶段
- [ ] 插入10条测试数据到清单表（资产/能力/价值评估项）
- [ ] 验证外键约束生效（插入无效关联ID应报错）
- [ ] 验证唯一约束生效（插入重复`asset_code`应报错）
- [ ] 验证JSONB字段可正常存储和查询
- [ ] 性能测试：查询月度数据响应时间<500ms

---

**本Schema文档供Lovable在Supabase中创建数据库使用，如有问题请在GitHub Issues中反馈。**

