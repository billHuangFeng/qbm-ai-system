# Cursor与Lovable协同开发：边际影响分析系统

## 📋 协作概览

本文档定义Cursor与Lovable在**边际影响分析系统**（基于完整优化版商业增量模型）的具体分工与协作流程。

## 🎯 系统目标

实现**核心资产→核心能力→效率→产品价值→收入→利润→动态反馈**的全链路增量分析，所有变量为月度增量（△），嵌入：
- 核心资产量化：未来5年现金流增量现值（NPV）
- 核心能力量化：稳定成果对应收益×贡献百分比
- 产品价值三分法：内在/认知/体验价值评估
- 边际影响分析：Shapley值扩展（TypeScript简化版→Python完整版）

## 🔧 技术架构决策

### 成本优化方案（已确认）

| 组件 | MVP阶段（立即实施） | 扩展阶段（按需升级） | 成本 |
|------|---------------------|----------------------|------|
| **Shapley边际贡献计算** | TypeScript简化版（线性回归+敏感性分析） | Google Cloud Run Python服务（完整Shapley） | MVP: $0<br>扩展: $2-3/月 |
| **时间序列拟合** | TypeScript简化版（线性回归+滞后项） | Google Cloud Run Prophet服务 | MVP: $0<br>扩展: $2-3/月 |
| **其他API** | Next.js API Routes | Next.js API Routes | $0（Vercel免费额度内） |

**触发升级条件**：
- Shapley计算调用>1万次/月 → 迁移到Cloud Run完整版
- 时间序列MAE需求<15% → 迁移到Cloud Run Prophet

## 📂 Cursor交付文档清单（优先级1-高）

在Lovable开始编码前，Cursor需要先提交以下文档到 `qbm-ai-system/docs/` 目录：

### 1. 数据库设计文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `database/MARGINAL_ANALYSIS_SCHEMA.md` | 6个SQL文件的完整表结构+字段说明+索引 | ⏳ 待提交 |

**包含表**：
- 08: 核心资产清单+现金流预测+累计值表
- 09: 核心能力清单+稳定成果+价值历史表
- 10: 产品价值评估项清单+三类评估表
- 11: 月度增量指标表（效率/价值/收入利润）
- 12: 动态反馈配置表+执行日志表
- 13: 模型参数存储表（拟合结果+Shapley缓存）

### 2. 算法设计文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `algorithms/ASSET_NPV_CALCULATION.md` | 资产NPV折现算法+公式+Excel示例 | ⏳ 待提交 |
| `algorithms/CAPABILITY_VALUE_FORMULA.md` | 能力价值计算公式+贡献百分比+稳定性判定 | ⏳ 待提交 |
| `algorithms/PRODUCT_VALUE_ASSESSMENT.md` | 三类价值评估方法+加权得分+评估项明细 | ⏳ 待提交 |
| `algorithms/FULL_CHAIN_DELTA_FORMULAS.md` | 全链路增量公式汇总（22个△函数） | ⏳ 待提交 |
| `algorithms/typescript/simplified-shapley.ts` | TypeScript简化版Shapley算法代码 | ⏳ 待提交 |
| `algorithms/typescript/simplified-timeseries.ts` | TypeScript简化版时间序列算法代码 | ⏳ 待提交 |
| `algorithms/python/shapley_service.py` | Python完整版Shapley服务（Cloud Run） | ⏳ 待提交 |
| `algorithms/python/prophet_service.py` | Python Prophet服务（Cloud Run） | ⏳ 待提交 |
| `algorithms/python/Dockerfile` | Docker配置文件 | ⏳ 待提交 |

### 3. API契约规范

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `api/MARGINAL_ANALYSIS_API_SPEC.md` | 11个API端点的I/O契约+错误码+伪代码 | ⏳ 待提交 |

**包含API**：
- 清单管理CRUD（资产/能力/价值评估项）×3
- 计算引擎（资产NPV/能力价值/价值评估/全链路增量）×4
- 边际分析（Shapley简化版/完整版/时间序列简化版/完整版）×4

### 4. UI/UX设计文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `ui-ux/MARGINAL_ANALYSIS_UI_SPEC.md` | 9个页面的线框图+交互流程 | ⏳ 待提交 |
| `visualization/CHART_REQUIREMENTS.md` | 7个图表的数据格式+样式要求 | ⏳ 待提交 |

**包含页面**：
- 清单管理（资产/能力/价值评估项）×3
- 仪表盘（资产价值/能力价值/产品价值雷达图/边际影响分析）×4
- 监控诊断（动态反馈监控/模型诊断）×2

### 5. 数据导入模板

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `data-import-templates/asset_master_template.xlsx` | 资产清单模板+列定义 | ⏳ 待提交 |
| `data-import-templates/capability_master_template.xlsx` | 能力清单模板+列定义 | ⏳ 待提交 |
| `data-import-templates/value_item_master_template.xlsx` | 价值评估项模板+列定义 | ⏳ 待提交 |
| `data-import-templates/asset_cashflow_template.xlsx` | 资产现金流预测模板 | ⏳ 待提交 |
| `data-import-templates/capability_outcome_template.xlsx` | 能力稳定成果模板 | ⏳ 待提交 |
| `data-import-templates/value_assessment_template.xlsx` | 三类价值评估模板 | ⏳ 待提交 |
| `data-import-templates/monthly_finance_template.xlsx` | 月度财务数据模板 | ⏳ 待提交 |
| `etl/DATA_IMPORT_LOGIC.md` | ETL逻辑+验证规则+错误处理 | ⏳ 待提交 |

### 6. AI Copilot集成文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `interaction/MARGINAL_ANALYSIS_COPILOT_INTENTS.md` | 15个AI意图+工具映射+Prompt工程 | ⏳ 待提交 |

### 7. 测试与验证文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `testing/MARGINAL_ANALYSIS_TEST_CASES.md` | 单元测试用例+期望输出 | ⏳ 待提交 |
| `testing/VALIDATION_DATA.md` | 6个月业务数据+手工计算结果 | ⏳ 待提交 |
| `testing/ACCEPTANCE_CRITERIA.md` | 30个验收测试清单 | ⏳ 待提交 |

### 8. 成本优化文档

| 文档路径 | 内容 | 状态 |
|---------|------|------|
| `cost-optimization/SERVERLESS_COST_ANALYSIS.md` | 各方案成本对比+迁移阈值+监控指标 | ⏳ 待提交 |

## 🚀 Lovable执行任务（等待Cursor文档后）

### 阶段1: 数据库创建（Week 1）
- 在Supabase Console中创建6个SQL文件的表（基于Cursor的Schema文档）
- 配置RLS策略（如果需要多租户隔离）
- 创建索引和外键关系

### 阶段2: API实现（Week 2-4）
- **选择实现方式**：Next.js API Routes（推荐，成本$0）
- 实现11个API端点（基于Cursor的API契约文档）：
  - 3个清单CRUD API（资产/能力/价值评估项）
  - 4个计算引擎API（资产NPV/能力价值/价值评估/全链路增量）
  - 2个边际分析MVP API（TypeScript简化版Shapley+时间序列）
  - 2个动态反馈与场景模拟API
- 单元测试（基于Cursor的测试用例）

### 阶段3: 前端开发（Week 5-8）
- 创建9个页面组件（基于Cursor的UI/UX文档）
- 实现7个可视化组件（使用Recharts/D3.js）
- 集成API调用（调用自己的Next.js API Routes）
- 响应式布局与加载状态

### 阶段4: 数据导入ETL（Week 9）
- 实现数据导入API（解析Excel+验证+调用计算引擎）
- 前端上传界面（文件选择器+进度条+结果展示）

### 阶段5: AI Copilot集成（Week 10）
- 扩展AI Copilot组件（注册15个新工具函数）
- 解析AI响应并渲染结果

### 阶段6: 测试与交付（Week 11）
- 集成测试（端到端流程）
- 性能测试（API响应时间）
- 业务验证（使用Cursor提供的验证数据）

## 🤝 协作检查点

### 检查点1: 文档评审（Cursor→Lovable）
- **时间**: Week 1开始前
- **Cursor行动**: 提交所有8类文档到GitHub
- **Lovable行动**: 在GitHub Issues中提问（如"Shapley算法不清楚""UI交互逻辑需要澄清"）
- **Cursor响应**: 在Issue中回复并更新文档
- **确认标准**: Lovable确认所有文档清晰可实施 → 打上"ready-for-implementation"标签

### 检查点2: 数据库创建验证（Cursor←Lovable）
- **时间**: Week 1结束
- **Lovable行动**: 创建所有表并截图Supabase Schema，提交到GitHub PR
- **Cursor审查**: 验证表结构/索引/外键是否正确
- **确认标准**: Cursor批准PR → Lovable merge

### 检查点3: API实现验证（Cursor←Lovable）
- **时间**: Week 2-4，每周五
- **Lovable行动**: 提交API代码到GitHub PR，附带Postman测试结果截图
- **Cursor审查**: 验证算法实现正确性（如NPV计算偏差<5%）
- **协作处理**: 如果Lovable遇到算法问题（如Shapley性能），Cursor在Issue中提供简化方案
- **确认标准**: 单元测试通过 + Cursor批准PR → Lovable merge

### 检查点4: 前端实现验证（Cursor←Lovable）
- **时间**: Week 5-8，每周五
- **Lovable行动**: 部署到测试环境，提供预览链接
- **Cursor审查**: 验证UI/UX是否符合设计文档，数据可视化是否正确
- **确认标准**: Cursor批准 → Lovable继续下一页面

### 检查点5: 集成测试验证（Cursor+Lovable）
- **时间**: Week 11
- **共同行动**: 使用Cursor提供的验证数据进行端到端测试
- **确认标准**: 通过30个验收测试清单 → 系统交付

## 🔄 沟通机制

| 沟通类型 | 工具 | 响应时间 |
|---------|------|---------|
| 文档提交 | GitHub commit+push | 实时同步 |
| 问题反馈 | GitHub Issues | <24小时 |
| 代码审查 | GitHub Pull Requests | <48小时 |
| 进度同步 | GitHub Projects | 每周更新 |
| 紧急问题 | （如需要，补充联系方式） | <4小时 |

## 🎯 成功标准

### Cursor交付标准
- ✅ 15个文档全部提交到GitHub（Week 1前）
- ✅ TypeScript简化版算法代码通过单元测试（偏差<5%）
- ✅ Python完整版算法代码+Docker配置可部署到Cloud Run
- ✅ 所有GitHub Issues中的问题在48小时内回复

### Lovable交付标准
- ✅ 6个SQL文件的表在Supabase中创建完成
- ✅ 11个API端点实现并通过单元测试
- ✅ 9个页面+7个可视化组件开发完成
- ✅ 集成测试通过，性能达标（API<3s，Shapley简化版<5s）
- ✅ 业务验证通过（资产NPV偏差<5%，能力价值偏差<15%）

## ⚠️ 风险预案

| 风险 | 责任方 | 预案 |
|------|-------|------|
| TypeScript简化版Shapley精度不足 | Lovable发现 → Cursor提供完整版迁移方案 | 部署Python服务到Cloud Run |
| 时间序列简化版MAE>20% | Lovable发现 → Cursor提供Prophet迁移方案 | 部署Prophet服务到Cloud Run |
| 数据库RLS冲突 | Lovable发现 → Cursor调整SQL设计 | 修改外键关系或增加字段 |
| UI交互不清晰 | Cursor审查发现 → Lovable调整 | 补充交互说明或重新设计 |
| API性能不达标 | Lovable发现 → Cursor优化算法 | 简化计算逻辑或增加缓存 |

## 📝 附录：关键术语对照

| 中文术语 | 英文术语 | 说明 |
|---------|---------|------|
| 核心资产 | Core Asset | 未来5年现金流增量现值 |
| 核心能力 | Core Capability | 稳定成果对应收益×贡献百分比 |
| 产品价值 | Product Value | 内在/认知/体验三类价值 |
| 边际贡献 | Marginal Contribution | Shapley值或敏感性分析结果 |
| 月度增量 | Monthly Delta (△) | 本月值 - 上月值 |
| 动态反馈 | Dynamic Feedback | 利润反哺资产+能力价值优化 |

---

**此协作框架确保Cursor与Lovable在边际影响分析系统开发中高效分工，通过文档驱动和检查点机制实现双方理解一致，最终交付高质量系统。**




