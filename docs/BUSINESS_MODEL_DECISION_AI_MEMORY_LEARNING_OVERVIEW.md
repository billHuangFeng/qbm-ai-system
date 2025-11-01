## 商业模式—决策—AI—企业记忆—学习进化 一体化说明文档

### 文档目的
- 用统一视角解释系统如何把商业模式的关键要素转译为可计算的链路、可优化的决策、可沉淀的组织记忆，并形成持续进化的闭环。

---

## 一、核心认知框架（要素→价值→结果→资源）

- 逻辑闭环
  - 资产/能力决定 产品特性表现
  - 特性形成 价值（内在/认知/体验/WTP）
  - 价值作用于 销售结果（首单/复购/交叉）
  - 销售与成本决定 利润
  - 利润反哺 资产/能力，进入新一轮优化

- 可算表达（核心等式）
  - 特性表现: `feature_score = f(asset_stock, capability_perf, context)`
  - 价值生成: `product_value = g(feature_score)`
    - `cognitive/experience = h(marketing/delivery_ability, touchpoint_quality)`
    - `WTP = k(value, persona)`
  - 销量弹性: `dq/q ≈ −ε·dp/p`；sales 随 WTP 与价值提升而上升
  - 成本映射: `cost = operating_cost(product_line, volume) + invest(asset/capability, period)`
  - 边际收益: `profit = revenue − cost`；`marginal_ROI = Δprofit/Δinvest`
  - 资源最优: `max Σ Δprofit_i(invest_i) s.t. Σ invest_i ≤ B`（优先投“单位投入Δprofit”最大的瓶颈）

- 找到“边际收益最大点”的准则
  - 识别高斜率未饱和段（阈值内侧）
  - 判断资产/能力/特性/市场侧哪个环节的 `Δprofit/Δinvest` 当前最高
  - 达到阈值或递减后，切换下一瓶颈，滚动推进

---

## 二、数据到决策的最短路径（系统化实现）

- 数据层（结构化承载）
  - 主数据：核心资产、核心能力、产品价值评估项
  - 价值评估：内在/认知/体验与 WTP
  - 业务结果：销售分解（产品×客户×首单/复购/交叉）、成本
  - 投入台账：对资产/能力/产品线的投资记录
  - 增量标准：所有关键量统一以月度增量 Δ（本月-上月）存储；配套基线/带宽/阈值

- 推断层（认知）
  - 基线与带宽：ARIMA/VAR/LightGBM 生成趋势与置信带
  - 异常/阈值：分位/标准差/IQR 与 ThresholdAnalysis
  - 协同/冲突：SynergyAnalysis、图上环/冲突检测
  - 弹性识别：各链段“斜率”和“饱和度”估计，定位瓶颈

- 决策层（优化）
  - 目标与约束：战略权重 w、预算 B、风险与一致性约束
  - 求解：在约束下最大化 Δprofit，按 `Δprofit/Δinvest` 排序并给出投放节奏
  - 治理：一致性策略与冲突规避，形成可执行清单

- 学习层（进化）
  - 复盘采集：投入→链路增量→实际 Δprofit/ΔROI
  - 因果与证据加权：区分共现/因果，更新权重/阈值/规则
  - 组织记忆：沉淀“场景→动作→效果”的最佳实践与反例，支持下轮先验

---

## 三、系统模块与框架映射（服务级）

- 目标对齐层（Why/What）
  - `AINorthStarService`: 目标分解与动态权重
  - `AIStrategicObjectivesService`: 协同与冲突分析
  - `AIOKRService`: 达成概率（XGBoost）与风险提示

- 经营认知层（Know）
  - `AIBaselineGenerator`: ARIMA/VAR/LGB 基线与带宽
  - `SynergyAnalysis` / `ThresholdAnalysis`: 协同与阈值识别
  - 一致性/影响分析：结构冲突与作用路径

- 决策制定层（Decide）
  - `AIAlignmentChecker`: 约束/冲突/可行性
  - `AIInfluenceOptimizer`: 预算约束最优化（贪心/线性近似）
  - `AIDecisionRequirementsService`: 需求优先级与资源竞争协调

- 执行与监测层（Act/Measure）
  - 行动清单与只读监控；`monthly_delta_metrics` 跟踪 Δprofit/Δ价值/Δ效率/Δ收入
  - 告警：越界/逼近阈值触发事件与建议

- 复盘学习层（Learn）
  - `AIRetrospectiveAnalyzer`: 因果/证据加权复盘（数据不足回退到规则+记忆）
  - `AIRetrospectiveRecommender`: 策略升级与风险预案
  - 企业记忆：相似案例检索与先验参数/坑点提示

---

## 四、企业记忆（组织大脑）的角色

- 作为强先验
  - 冷启动/数据稀疏时提供“已验证方案+适用前置条件”
  - 给模型提供特征工程线索与参数初值
- 作为风险库
  - 检索“相似场景失败原因/冲突规则”，提前降风险
- 作为迁移与复制
  - 将有效策略跨产品/区域复制，缩短试错时间

---

## 五、学习进化机制（参数与知识双通道）

- 参数化更新
  - 模型（ARIMA/VAR/LGB/XGB/RF）按复盘误差批量/在线校正
  - 策略权重 w 与阈值按“受控策略漂移”更新
- 知识化沉淀
  - 企业记忆增补“场景→动作→效果→边界条件”
  - 规则库吸收“可解释的决策约束与洞察”，辅助下轮快速收敛

---

## 六、度量与验收（闭环达成的判据）

- 充分性：每环节有指标/基线/阈值与行动映射；投入台账可追溯
- 可解释：建议可还原到“弹性/阈值证据”和“Δprofit/Δinvest”
- 稳定性：关键链路在带宽内波动，接近阈值时能自动换瓶颈
- 学习性：复盘后，下一周期策略能体现“更快更准”的收敛

---

## 七、最小样例（思路示意）

- 输入：生产设备与交付能力各 50 万投入；三条链路的月度增量
- 推断：设备→成本斜率大且未饱和；交付→复购提升但接近阈值
- 决策：本期设备投放 60%、交付 40%，叠加价格微调与触达优化
- 学习：记录 Δprofit、复购与价格弹性；更新阈值与规则；记忆库新增“场景卡”

---

## 八、与数据结构的对照（要素→实体表）

- 主数据：`core_asset_master`（资产NPV）、`core_capability_master`（能力绩效）、`product_value_item_master`（价值项）
- 价值评估：内在/认知/体验与 WTP（价值评估表组）
- 增量：`monthly_delta_metrics`（效率/价值/收入/利润分项）
- 投入与反馈：投入台账、`dynamic_feedback_config`（利润反哺规则）、执行日志
- 模型与参数：`model_parameters_storage`、边际贡献缓存

说明：在无数据库模式下，系统提供只读 Mock 接口用于快速验收；数据库就绪后执行 08–13 SQL 迁移并切换到持久化。

---

## 九、结语（一句话）

系统把商业模式的“结构化理解”落为可测的链路、可解的优化与可控的反馈，用“单位投入带来的利润增量最大化”驱动资源流向最敏感的环节，并以复盘将有效策略沉淀为组织记忆与模型先验，实现自我进化的经营闭环。



