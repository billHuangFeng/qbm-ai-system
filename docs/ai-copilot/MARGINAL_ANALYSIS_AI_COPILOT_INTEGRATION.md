# 边际影响分析系统 - AI Copilot集成文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-10-23
- **负责人**: Cursor (算法设计与技术架构)
- **实施方**: Lovable (前端集成与UI实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 系统概述

### 1.1 目标
为边际影响分析系统集成AI Copilot，提供智能化的数据洞察、决策支持和自然语言交互能力，帮助用户：
- 快速理解复杂的边际影响分析结果
- 通过自然语言查询数据和执行分析
- 获得智能化的优化建议和决策支持
- 自动生成分析报告和可视化

### 1.2 核心价值
1. **降低使用门槛**: 通过自然语言交互，让非技术用户也能轻松使用系统
2. **提升分析效率**: 自动化数据查询、分析和报告生成，节省80%的人工时间
3. **增强决策质量**: 基于AI的洞察和建议，提供更全面的决策支持
4. **知识沉淀**: 构建企业专属知识库，积累最佳实践

### 1.3 技术特点
- **混合部署**: Gemini API处理复杂推理 + 本地模型处理简单任务
- **分阶段实现**: MVP 5个工具 → 扩展10个 → 完整15个
- **智能路由**: 根据问题复杂度自动选择处理模式
- **成本优化**: 缓存策略 + 本地模型优先 + API按需调用

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 聊天界面  │  │ 仪表板   │  │ 报告生成  │  │ API调用   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │      智能路由层 (Question Router)    │
        │  - 问题复杂度分析                     │
        │  - 模式选择 (简单/深度/混合)          │
        │  - 负载均衡                          │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │                                     │
   ┌────▼────┐                         ┌─────▼────┐
   │ 简单问答 │                         │ 深度研究  │
   │  模式   │                         │   模式   │
   │(本地模型)│                         │(Gemini API)│
   └────┬────┘                         └─────┬────┘
        │                                     │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │        Agent Loop (核心引擎)         │
        │  ┌────────────────────────────┐    │
        │  │ 1. 问题理解 (Intent Parser) │    │
        │  └──────────┬─────────────────┘    │
        │             ▼                       │
        │  ┌────────────────────────────┐    │
        │  │ 2. 工具规划 (Tool Planner)  │    │
        │  └──────────┬─────────────────┘    │
        │             ▼                       │
        │  ┌────────────────────────────┐    │
        │  │ 3. 执行调用 (Tool Executor) │    │
        │  └──────────┬─────────────────┘    │
        │             ▼                       │
        │  ┌────────────────────────────┐    │
        │  │ 4. 结果合成 (Synthesizer)   │    │
        │  └────────────────────────────┘    │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │       Tool Server (工具服务层)       │
        │  ┌──────┐ ┌──────┐ ┌──────┐       │
        │  │ 数据  │ │ 分析  │ │ 外部  │       │
        │  │ 查询  │ │ 执行  │ │ 集成  │       │
        │  └──┬───┘ └──┬───┘ └──┬───┘       │
        └─────┼────────┼────────┼────────────┘
              │        │        │
        ┌─────▼────────▼────────▼────────────┐
        │         数据与服务层                 │
        │  ┌──────────┐  ┌──────────┐        │
        │  │PostgreSQL│  │  Redis   │        │
        │  │ (Supabase)│  │ (Cache)  │        │
        │  └──────────┘  └──────────┘        │
        │  ┌──────────┐  ┌──────────┐        │
        │  │ Backend  │  │ External │        │
        │  │   API    │  │   APIs   │        │
        │  └──────────┘  └──────────┘        │
        └────────────────────────────────────┘
```

### 2.2 混合部署策略

#### 2.2.1 模型选择矩阵

| 任务类型 | 复杂度 | 模型选择 | 预期响应时间 | 成本/请求 |
|---------|-------|---------|------------|----------|
| 数据查询 | 低 | 本地模型 (Qwen2.5-7B) | <1秒 | $0 |
| 简单分析 | 低-中 | 本地模型 | 1-3秒 | $0 |
| 报告生成 | 中 | 本地模型 + 缓存 | 3-10秒 | $0 |
| 复杂推理 | 高 | Gemini 1.5 Pro | 5-15秒 | $0.001-0.005 |
| 深度研究 | 极高 | Gemini 1.5 Pro + Tools | 30-120秒 | $0.01-0.05 |

#### 2.2.2 智能路由规则

```python
# 智能路由决策树
def route_question(question: str, context: Dict) -> str:
    """
    根据问题特征选择处理模式
    
    返回值:
        - "local_simple": 本地模型处理简单问题
        - "local_cached": 使用缓存结果
        - "gemini_complex": Gemini API处理复杂问题
        - "hybrid": 混合模式（先本地，必要时升级到API）
    """
    
    # 1. 检查缓存
    if cache_hit(question):
        return "local_cached"
    
    # 2. 问题特征提取
    features = extract_question_features(question)
    
    # 3. 复杂度评分 (0-10)
    complexity_score = calculate_complexity(features)
    
    # 4. 路由决策
    if complexity_score <= 3:
        # 简单问题：数据查询、状态查看
        return "local_simple"
    elif complexity_score <= 7:
        # 中等问题：单次分析、报告生成
        return "hybrid"  # 先尝试本地，失败则升级
    else:
        # 复杂问题：多步推理、深度分析
        return "gemini_complex"

def calculate_complexity(features: Dict) -> float:
    """
    计算问题复杂度
    
    考虑因素:
        - 查询数据量 (0-2分)
        - 分析步骤数 (0-3分)
        - 推理深度 (0-3分)
        - 时间范围 (0-1分)
        - 外部依赖 (0-1分)
    """
    score = 0.0
    
    # 数据量评分
    if features["data_volume"] == "single_record":
        score += 0
    elif features["data_volume"] == "small_query":
        score += 1
    else:
        score += 2
    
    # 分析步骤评分
    score += min(features["analysis_steps"], 3)
    
    # 推理深度评分
    if "why" in features["question_type"] or "explain" in features["question_type"]:
        score += 2
    if "predict" in features["question_type"] or "optimize" in features["question_type"]:
        score += 1
    
    # 时间范围评分
    if features["time_range"] == "multi_period":
        score += 1
    
    # 外部依赖评分
    if features["requires_external_data"]:
        score += 1
    
    return min(score, 10.0)
```

### 2.3 Agent Loop设计

#### 2.3.1 四阶段处理流程

```python
class AIAgent:
    """AI Copilot核心Agent"""
    
    def __init__(self, model_type: str = "hybrid"):
        self.model_type = model_type
        self.conversation_history = []
        self.tool_server = ToolServer()
        self.cache = RedisCache()
    
    async def process_query(self, user_query: str) -> AgentResponse:
        """
        处理用户查询的完整流程
        """
        
        # 阶段1: 问题理解
        intent = await self.parse_intent(user_query)
        
        # 阶段2: 工具规划
        plan = await self.plan_tools(intent)
        
        # 阶段3: 执行调用
        results = await self.execute_tools(plan)
        
        # 阶段4: 结果合成
        response = await self.synthesize_response(results, user_query)
        
        # 更新历史
        self.conversation_history.append({
            "query": user_query,
            "intent": intent,
            "plan": plan,
            "results": results,
            "response": response
        })
        
        return response
    
    async def parse_intent(self, query: str) -> Intent:
        """
        阶段1: 问题理解
        
        提取用户意图、实体和参数
        """
        # 使用本地NLU模型或简单规则
        intent_classifier = IntentClassifier()
        entity_extractor = EntityExtractor()
        
        intent_type = intent_classifier.predict(query)
        entities = entity_extractor.extract(query)
        
        return Intent(
            type=intent_type,  # "query_data", "execute_analysis", etc.
            entities=entities,  # {"asset": "研发资产", "month": "2024-10"}
            confidence=0.95,
            requires_clarification=False
        )
    
    async def plan_tools(self, intent: Intent) -> ToolPlan:
        """
        阶段2: 工具规划
        
        根据意图选择合适的工具链
        """
        if intent.type == "query_asset_data":
            return ToolPlan(
                steps=[
                    ToolCall(name="query_asset_data", params=intent.entities)
                ]
            )
        
        elif intent.type == "execute_marginal_analysis":
            return ToolPlan(
                steps=[
                    ToolCall(name="query_asset_data", params={"month": intent.entities["month"]}),
                    ToolCall(name="query_capability_data", params={"month": intent.entities["month"]}),
                    ToolCall(name="execute_marginal_analysis", params={
                        "asset_data": "$step_1_result",
                        "capability_data": "$step_2_result"
                    }),
                    ToolCall(name="get_insights", params={"analysis_result": "$step_3_result"})
                ]
            )
        
        elif intent.type == "generate_report":
            return ToolPlan(
                steps=[
                    ToolCall(name="query_analysis_results", params=intent.entities),
                    ToolCall(name="generate_report", params={
                        "data": "$step_1_result",
                        "format": "pdf"
                    })
                ]
            )
        
        else:
            # 对于未知意图，使用LLM动态规划
            return await self.llm_plan_tools(intent)
    
    async def execute_tools(self, plan: ToolPlan) -> List[ToolResult]:
        """
        阶段3: 执行调用
        
        按顺序执行工具链，处理依赖和错误
        """
        results = []
        context = {}
        
        for step in plan.steps:
            try:
                # 解析参数中的变量引用 ($step_N_result)
                resolved_params = self.resolve_params(step.params, context)
                
                # 检查缓存
                cache_key = f"{step.name}:{resolved_params}"
                cached_result = await self.cache.get(cache_key)
                
                if cached_result:
                    result = cached_result
                else:
                    # 调用工具
                    result = await self.tool_server.call(step.name, resolved_params)
                    
                    # 缓存结果
                    await self.cache.set(cache_key, result, ttl=3600)
                
                results.append(result)
                context[f"step_{len(results)}_result"] = result.data
                
            except Exception as e:
                # 错误处理和重试
                if step.retry_on_error:
                    result = await self.retry_tool_call(step, resolved_params)
                    results.append(result)
                else:
                    results.append(ToolResult(
                        success=False,
                        error=str(e),
                        data=None
                    ))
        
        return results
    
    async def synthesize_response(self, results: List[ToolResult], 
                                  original_query: str) -> AgentResponse:
        """
        阶段4: 结果合成
        
        将工具执行结果合成自然语言响应
        """
        # 检查是否所有步骤都成功
        all_success = all(r.success for r in results)
        
        if not all_success:
            return AgentResponse(
                success=False,
                message="抱歉，执行过程中遇到了一些问题。",
                data=None,
                suggestions=["请检查输入参数是否正确", "稍后再试"]
            )
        
        # 使用LLM合成响应（本地模型或Gemini）
        if self.model_type == "local" or len(results) == 1:
            # 简单情况：使用模板
            response_text = self.template_response(results, original_query)
        else:
            # 复杂情况：使用LLM
            response_text = await self.llm_synthesize(results, original_query)
        
        return AgentResponse(
            success=True,
            message=response_text,
            data=[r.data for r in results],
            suggestions=self.generate_suggestions(results)
        )
```

---

## 3. 工具函数定义（分三阶段实现）

### 3.1 MVP阶段（5个核心工具）

实施优先级：⭐⭐⭐⭐⭐ (最高优先级)

#### 3.1.1 query_analysis_results

**功能**: 查询历史分析结果

**输入参数**:
```python
{
    "tenant_id": str,  # 租户ID (从认证Token获取)
    "analysis_type": str,  # 分析类型: "marginal_impact", "weight_optimization", etc.
    "time_range": {
        "start_month": str,  # "2024-01"
        "end_month": str     # "2024-10"
    },
    "filters": {  # 可选过滤条件
        "asset_type": str,  # "研发资产", "生产资产", etc.
        "capability_type": str,
        "min_impact_score": float
    },
    "sort_by": str,  # "date", "impact_score", "r2_score"
    "limit": int  # 返回结果数量限制
}
```

**输出格式**:
```python
{
    "success": bool,
    "data": [
        {
            "analysis_id": str,
            "analysis_type": str,
            "created_at": str,
            "parameters": dict,
            "results": {
                "impact_scores": dict,
                "r2_score": float,
                "insights": list
            },
            "summary": str
        }
    ],
    "total_count": int,
    "execution_time_ms": int
}
```

**API实现**:
```python
# backend/src/api/endpoints/ai_copilot.py
@router.post("/tools/query_analysis_results")
async def query_analysis_results(
    params: QueryAnalysisParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询历史分析结果"""
    
    # 构建查询
    query = db.query(AnalysisResult).filter(
        AnalysisResult.tenant_id == current_user.tenant_id,
        AnalysisResult.analysis_type == params.analysis_type
    )
    
    # 应用时间范围过滤
    if params.time_range:
        query = query.filter(
            AnalysisResult.analysis_month >= params.time_range.start_month,
            AnalysisResult.analysis_month <= params.time_range.end_month
        )
    
    # 应用其他过滤条件
    if params.filters:
        if params.filters.asset_type:
            query = query.filter(AnalysisResult.asset_type == params.filters.asset_type)
    
    # 排序和限制
    query = query.order_by(getattr(AnalysisResult, params.sort_by).desc())
    query = query.limit(params.limit)
    
    results = query.all()
    
    return {
        "success": True,
        "data": [serialize_analysis_result(r) for r in results],
        "total_count": len(results)
    }
```

**使用示例**:
```python
# Agent调用示例
result = await tool_server.call("query_analysis_results", {
    "tenant_id": "enterprise_001",
    "analysis_type": "marginal_impact",
    "time_range": {
        "start_month": "2024-01",
        "end_month": "2024-10"
    },
    "limit": 10
})

# 返回: 最近10次边际影响分析结果
```

#### 3.1.2 execute_marginal_analysis

**功能**: 执行边际影响分析

**输入参数**:
```python
{
    "tenant_id": str,
    "analysis_month": str,  # "2024-10"
    "analysis_scope": {
        "assets": list,  # ["研发资产", "生产资产"] 或 "all"
        "capabilities": list,  # ["研发能力", "生产能力"] 或 "all"
        "value_types": list  # ["产品内在价值", "客户认知价值"] 或 "all"
    },
    "options": {
        "use_historical_fitting": bool,  # 是否使用历史数据拟合
        "optimize_weights": bool,  # 是否优化权重
        "generate_insights": bool  # 是否生成洞察
    }
}
```

**输出格式**:
```python
{
    "success": bool,
    "analysis_id": str,
    "results": {
        "delta_formulas": {
            "资产边际影响": {
                "研发资产": {
                    "current_value": float,
                    "delta": float,
                    "npv_contribution": float
                },
                // ...其他资产
            },
            "能力边际影响": {
                "研发能力": {
                    "current_value": float,
                    "delta": float,
                    "stable_outcome_score": float
                },
                // ...其他能力
            },
            "效能指标": {
                "研发效能": {
                    "value": float,
                    "formula": "产品特性估值 ÷ (△研发能力×a2 + △研发资产×b2)",
                    "interpretation": "研发投入产出比提升15%"
                },
                // ...其他效能
            },
            "价值评估": {
                "产品内在价值": {
                    "value": float,
                    "delta": float,
                    "wtp_score": float
                },
                // ...其他价值
            },
            "收入影响": {
                "首单收入": float,
                "复购收入": float,
                "追销收入": float,
                "总收入": float
            },
            "利润与ROI": {
                "经营利润": float,
                "净利润": float,
                "ROI": float,
                "reinvestment_suggestion": dict
            }
        },
        "model_performance": {
            "r2_score": float,
            "mse": float,
            "feature_importance": dict
        },
        "insights": [
            {
                "type": "opportunity",  # "opportunity", "risk", "recommendation"
                "title": str,
                "description": str,
                "priority": str,  # "high", "medium", "low"
                "action_items": list
            }
        ]
    },
    "execution_time_ms": int
}
```

**API实现**: 
```python
@router.post("/tools/execute_marginal_analysis")
async def execute_marginal_analysis(
    params: ExecuteAnalysisParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行边际影响分析"""
    
    # 1. 获取输入数据
    asset_data = await get_asset_data(params.tenant_id, params.analysis_month)
    capability_data = await get_capability_data(params.tenant_id, params.analysis_month)
    value_data = await get_value_data(params.tenant_id, params.analysis_month)
    
    # 2. 执行分析
    algorithm_service = AlgorithmService()
    
    if params.options.use_historical_fitting:
        # 使用历史数据拟合优化
        historical_data = await get_historical_data(params.tenant_id, months=12)
        results = await algorithm_service.analyze_with_fitting(
            asset_data, capability_data, value_data, historical_data
        )
    else:
        # 使用固定公式计算
        results = await algorithm_service.analyze_with_formulas(
            asset_data, capability_data, value_data
        )
    
    # 3. 生成洞察
    if params.options.generate_insights:
        insights = await algorithm_service.generate_insights(results)
        results["insights"] = insights
    
    # 4. 保存结果
    analysis_record = AnalysisResult(
        tenant_id=params.tenant_id,
        analysis_type="marginal_impact",
        analysis_month=params.analysis_month,
        parameters=params.dict(),
        results=results,
        created_by=current_user.id
    )
    db.add(analysis_record)
    db.commit()
    
    return {
        "success": True,
        "analysis_id": analysis_record.id,
        "results": results
    }
```

#### 3.1.3 optimize_weights

**功能**: 优化权重参数（a1-a6, b1-b6）

**输入参数**:
```python
{
    "tenant_id": str,
    "optimization_scope": str,  # "all", "efficiency", "specific"
    "target_weights": list,  # ["a1", "a2", "b1", ...] 或 "all"
    "historical_months": int,  # 使用多少个月的历史数据，默认12
    "optimization_method": str,  # "grid_search", "bayesian", "genetic"
    "constraints": {
        "weight_sum": float,  # 权重和约束，如 a1+a2+...+a6=1.0
        "weight_bounds": dict  # {"a1": [0.0, 1.0], ...}
    },
    "objective": str  # "maximize_r2", "minimize_mse", "maximize_profit_roi"
}
```

**输出格式**:
```python
{
    "success": bool,
    "optimized_weights": {
        "a1": float,  # 产品设计能力权重
        "a2": float,  # 研发能力权重
        // ...
        "b1": float,  # 产品设计资产权重
        "b2": float,  # 研发资产权重
        // ...
    },
    "performance": {
        "before": {
            "r2_score": float,
            "mse": float,
            "profit_roi": float
        },
        "after": {
            "r2_score": float,
            "mse": float,
            "profit_roi": float
        },
        "improvement_pct": float
    },
    "validation_results": {
        "cross_validation_score": float,
        "stability_score": float,
        "confidence_level": float
    },
    "recommendations": [
        {
            "weight_name": str,
            "old_value": float,
            "new_value": float,
            "rationale": str
        }
    ]
}
```

**API实现**:
```python
@router.post("/tools/optimize_weights")
async def optimize_weights(
    params: OptimizeWeightsParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """优化权重参数"""
    
    # 1. 获取历史数据
    historical_data = await get_historical_data(
        params.tenant_id, 
        months=params.historical_months
    )
    
    # 2. 执行权重优化
    algorithm_service = AlgorithmService()
    optimization_results = await algorithm_service.optimize_weights(
        data=historical_data,
        method=params.optimization_method,
        constraints=params.constraints,
        objective=params.objective
    )
    
    # 3. 验证优化结果
    validation_results = await algorithm_service.validate_weights(
        optimized_weights=optimization_results["optimized_weights"],
        test_data=historical_data[-3:]  # 使用最近3个月作为验证集
    )
    
    # 4. 保存优化记录
    optimization_record = WeightOptimizationRecord(
        tenant_id=params.tenant_id,
        optimization_date=datetime.now(),
        parameters=params.dict(),
        results=optimization_results,
        validation=validation_results,
        created_by=current_user.id
    )
    db.add(optimization_record)
    db.commit()
    
    return {
        "success": True,
        "optimized_weights": optimization_results["optimized_weights"],
        "performance": optimization_results["performance"],
        "validation_results": validation_results
    }
```

#### 3.1.4 get_insights

**功能**: 获取智能分析洞察

**输入参数**:
```python
{
    "tenant_id": str,
    "analysis_id": str,  # 可选，如果提供则基于特定分析生成洞察
    "insight_types": list,  # ["opportunity", "risk", "trend", "benchmark", "recommendation"]
    "time_range": {
        "start_month": str,
        "end_month": str
    },
    "focus_areas": list  # ["assets", "capabilities", "efficiency", "value", "revenue"]
}
```

**输出格式**:
```python
{
    "success": bool,
    "insights": [
        {
            "id": str,
            "type": str,  # "opportunity", "risk", "trend", "benchmark", "recommendation"
            "category": str,  # "assets", "capabilities", etc.
            "priority": str,  # "high", "medium", "low"
            "title": str,
            "description": str,
            "evidence": {
                "data_points": list,
                "trend_analysis": dict,
                "comparison": dict
            },
            "impact_assessment": {
                "revenue_impact": str,  # "±X万元"
                "efficiency_impact": str,  # "±X%"
                "confidence": float  # 0-1
            },
            "action_items": [
                {
                    "action": str,
                    "expected_outcome": str,
                    "effort": str,  # "low", "medium", "high"
                    "timeline": str  # "1-2周", "1-3月"
                }
            ],
            "created_at": str
        }
    ],
    "summary": {
        "total_insights": int,
        "by_type": dict,
        "by_priority": dict,
        "key_findings": list
    }
}
```

**API实现**:
```python
@router.post("/tools/get_insights")
async def get_insights(
    params: GetInsightsParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取智能分析洞察"""
    
    # 1. 获取分析数据
    if params.analysis_id:
        analysis_data = db.query(AnalysisResult).filter(
            AnalysisResult.id == params.analysis_id
        ).first()
    else:
        # 获取时间范围内的所有分析
        analysis_data = db.query(AnalysisResult).filter(
            AnalysisResult.tenant_id == params.tenant_id,
            AnalysisResult.analysis_month >= params.time_range.start_month,
            AnalysisResult.analysis_month <= params.time_range.end_month
        ).all()
    
    # 2. 生成洞察
    algorithm_service = AlgorithmService()
    insights = await algorithm_service.generate_insights(
        analysis_data=analysis_data,
        insight_types=params.insight_types,
        focus_areas=params.focus_areas
    )
    
    # 3. 排序和过滤
    insights = sorted(insights, key=lambda x: (
        {"high": 0, "medium": 1, "low": 2}[x["priority"]],
        -x["impact_assessment"]["confidence"]
    ))
    
    return {
        "success": True,
        "insights": insights,
        "summary": {
            "total_insights": len(insights),
            "by_type": count_by_field(insights, "type"),
            "by_priority": count_by_field(insights, "priority")
        }
    }
```

#### 3.1.5 search_knowledge_base

**功能**: 搜索内部知识库

**输入参数**:
```python
{
    "tenant_id": str,
    "query": str,  # 自然语言查询
    "search_scope": list,  # ["formulas", "best_practices", "historical_analyses", "documentation"]
    "filters": {
        "date_range": dict,
        "relevance_threshold": float  # 0-1, 最低相关性阈值
    },
    "max_results": int,  # 默认10
    "include_similar": bool  # 是否包含相似问题
}
```

**输出格式**:
```python
{
    "success": bool,
    "results": [
        {
            "id": str,
            "type": str,  # "formula", "best_practice", "analysis", "doc"
            "title": str,
            "content": str,
            "relevance_score": float,  # 0-1
            "metadata": {
                "created_at": str,
                "updated_at": str,
                "author": str,
                "tags": list,
                "category": str
            },
            "related_items": list  # 相关内容ID列表
        }
    ],
    "suggested_queries": list,  # 推荐的相关搜索
    "total_results": int
}
```

**API实现**:
```python
@router.post("/tools/search_knowledge_base")
async def search_knowledge_base(
    params: SearchKnowledgeBaseParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索内部知识库"""
    
    # 1. 向量化查询
    embedding_service = EmbeddingService()
    query_vector = await embedding_service.embed(params.query)
    
    # 2. 向量搜索
    search_results = await vector_search(
        query_vector=query_vector,
        collection=f"knowledge_base_{params.tenant_id}",
        filters=params.filters,
        limit=params.max_results
    )
    
    # 3. 过滤和排序
    filtered_results = [
        r for r in search_results 
        if r["relevance_score"] >= params.filters.relevance_threshold
    ]
    
    # 4. 获取相关内容
    if params.include_similar:
        for result in filtered_results:
            result["related_items"] = await get_related_items(result["id"])
    
    # 5. 生成推荐查询
    suggested_queries = await generate_suggested_queries(
        params.query, filtered_results
    )
    
    return {
        "success": True,
        "results": filtered_results,
        "suggested_queries": suggested_queries,
        "total_results": len(filtered_results)
    }
```

### 3.2 扩展阶段（新增5个工具，共10个）

实施优先级：⭐⭐⭐⭐ (高优先级)

#### 3.2.1 query_asset_data

**功能**: 查询核心资产数据

**输入参数**:
```python
{
    "tenant_id": str,
    "asset_types": list,  # ["研发资产", "产品设计资产", ...] 或 "all"
    "time_range": {
        "start_month": str,
        "end_month": str
    },
    "include_metrics": list,  # ["npv", "cash_flow", "roi", "trends"]
    "aggregation": str  # "monthly", "quarterly", "yearly", "total"
}
```

**输出格式**: 略（详见完整文档）

#### 3.2.2 query_capability_data

**功能**: 查询核心能力数据

#### 3.2.3 predict_trend

**功能**: 趋势预测（基于历史数据）

#### 3.2.4 compare_benchmarks

**功能**: 行业基准对比

#### 3.2.5 generate_report

**功能**: 生成分析报告（PDF/Excel/PPT）

### 3.3 完整阶段（新增5个工具，共15个）

实施优先级：⭐⭐⭐ (中等优先级，扩展功能）

#### 3.3.1 search_industry_data

**功能**: 外部行业数据搜索（Serper API）

#### 3.3.2 read_research_report

**功能**: 读取研究报告（Jina API）

#### 3.3.3 analyze_correlation

**功能**: 相关性分析

#### 3.3.4 simulate_scenario

**功能**: 场景模拟

#### 3.3.5 recommend_optimization

**功能**: 优化建议推荐

---

## 4. Agent交互模式

### 4.1 简单问答模式

**适用场景**: 数据查询、状态查看、简单计算

**特点**:
- 单轮对话
- 响应时间 < 30秒
- 使用本地模型 (Qwen2.5-7B)
- 缓存友好

**示例对话**:
```
用户: 帮我查一下2024年10月的研发资产NPV
Agent: [调用 query_asset_data]
      
      2024年10月研发资产NPV数据如下：
      
      - 研发资产总值：500万元
      - 未来5年现金流现值：620万元
      - NPV：120万元
      - 月度增量：+15万元（较9月）
      
      📊 趋势分析：研发资产NPV连续3个月正增长，主要贡献来自
      新产品研发投入的预期收益提升。
```

### 4.2 深度研究模式

**适用场景**: 复杂分析、多步推理、战略决策

**特点**:
- 多轮对话
- 响应时间 2-5分钟
- 使用Gemini 1.5 Pro + 多工具链
- 深度推理和洞察

**示例对话**:
```
用户: 我想了解如何优化研发效能以提升整体利润率

Agent: [深度研究模式已启动]
      
      我将从以下几个维度为您进行深度分析：
      
      1. 📊 当前研发效能现状评估
      2. 🔍 历史趋势和模式识别
      3. ⚖️ 行业基准对比
      4. 💡 优化机会识别
      5. 🎯 具体行动建议
      
      [执行工具链...]
      
      ### 1. 当前研发效能现状
      [调用 execute_marginal_analysis, query_capability_data]
      
      您的研发效能当前为 1.25 (产品特性估值 / 研发投入)
      - 高于行业平均水平 (1.08) 16%
      - 但低于行业领先水平 (1.45) 14%
      
      ### 2. 历史趋势分析
      [调用 predict_trend, analyze_correlation]
      
      过去12个月研发效能呈现以下特征：
      - 波动较大（标准差0.18），说明稳定性不足
      - 与研发资产投入相关性为0.72，强正相关
      - 与研发能力提升相关性仅0.48，弱相关
      
      🔍 关键发现：您的研发效能主要依赖资产投入，而非能力
      提升，这可能导致边际效益递减。
      
      ### 3. 行业基准对比
      [调用 compare_benchmarks, search_industry_data]
      
      对比行业TOP 10企业：
      - 研发资产投入占比：您 12% vs 行业均值 15%
      - 研发能力得分：您 75分 vs 行业均值 82分
      - 研发效能：您 1.25 vs 行业均值 1.08
      
      💡 洞察：您的研发效能虽高于平均，但投入不足可能限制
      长期增长潜力。
      
      ### 4. 优化机会识别
      [调用 get_insights, analyze_correlation]
      
      识别到3个高优先级优化机会：
      
      ⭐ 机会1：提升需求洞察准确率
      - 当前：68% → 目标：85%
      - 预期收益：研发效能提升15-20%
      - 投入：需求分析能力培训 + 工具优化
      
      ⭐ 机会2：优化产品特性开发优先级
      - 当前：无系统化排序 → 目标：基于价值排序
      - 预期收益：避免30%的无效研发投入
      - 投入：建立特性价值评估体系
      
      ⭐ 机会3：增加研发资产投入
      - 当前：500万/月 → 建议：650万/月 (+30%)
      - 预期收益：NPV增长45%，ROI提升至1.82
      - 投入：财务重新配置
      
      ### 5. 具体行动建议
      [调用 recommend_optimization, simulate_scenario]
      
      **优先级排序**（基于ROI和实施难度）：
      
      1️⃣ 立即执行（1-2周）：
         - 建立产品特性价值评估机制
         - 梳理当前在研项目优先级
         - 预期快速提效10%
      
      2️⃣ 短期执行（1-3月）：
         - 组织需求洞察能力培训
         - 引入客户研究工具
         - 预期3个月后见效，提效15%
      
      3️⃣ 中期规划（3-6月）：
         - 申请研发预算增加30%
         - 招聘核心研发人才
         - 预期6个月后见效，整体利润率提升3-5%
      
      **场景模拟**（如果全部实施）：
      - 6个月后研发效能预计达到 1.58 (+26%)
      - 产品内在价值提升 25%
      - 整体利润率提升 4.2%
      - 投资回收期：8-10个月
      
      您是否需要我进一步展开某个具体建议，或者生成详细的
      实施计划？
```

### 4.3 混合模式（智能路由）

**特点**: 根据问题复杂度自动选择处理策略

**决策逻辑**:
```python
def determine_mode(question: str, context: Dict) -> str:
    features = extract_features(question)
    complexity = calculate_complexity(features)
    
    if complexity <= 3:
        return "simple_qa"  # 简单问答模式
    elif complexity <= 7:
        # 尝试本地处理，失败则升级
        result = try_local_processing(question)
        if result.confidence < 0.7:
            return "deep_research"  # 升级到深度研究
        return "simple_qa"
    else:
        return "deep_research"  # 深度研究模式
```

---

## 5. 技术实现

### 5.1 Tool Server实现

```python
# backend/src/services/tool_server.py
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Callable
import asyncio
from redis import Redis
import hashlib
import json

class ToolServer:
    """AI Copilot工具服务器"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.cache = Redis(host='localhost', port=6379, db=0)
        self.app = FastAPI(title="AI Copilot Tool Server")
        
        # 注册所有工具
        self._register_tools()
        
        # 设置健康检查
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "tools_count": len(self.tools)}
    
    def _register_tools(self):
        """注册所有工具函数"""
        from .tools import (
            query_analysis_results,
            execute_marginal_analysis,
            optimize_weights,
            get_insights,
            search_knowledge_base,
            query_asset_data,
            query_capability_data,
            predict_trend,
            compare_benchmarks,
            generate_report,
            search_industry_data,
            read_research_report,
            analyze_correlation,
            simulate_scenario,
            recommend_optimization
        )
        
        # MVP阶段工具
        self.register("query_analysis_results", query_analysis_results)
        self.register("execute_marginal_analysis", execute_marginal_analysis)
        self.register("optimize_weights", optimize_weights)
        self.register("get_insights", get_insights)
        self.register("search_knowledge_base", search_knowledge_base)
        
        # 扩展阶段工具
        self.register("query_asset_data", query_asset_data)
        self.register("query_capability_data", query_capability_data)
        self.register("predict_trend", predict_trend)
        self.register("compare_benchmarks", compare_benchmarks)
        self.register("generate_report", generate_report)
        
        # 完整阶段工具
        self.register("search_industry_data", search_industry_data)
        self.register("read_research_report", read_research_report)
        self.register("analyze_correlation", analyze_correlation)
        self.register("simulate_scenario", simulate_scenario)
        self.register("recommend_optimization", recommend_optimization)
    
    def register(self, name: str, func: Callable):
        """注册工具函数"""
        self.tools[name] = func
        
        # 动态创建FastAPI端点
        @self.app.post(f"/tools/{name}")
        async def tool_endpoint(params: Dict[str, Any]):
            return await self.call(name, params)
    
    async def call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具函数
        
        支持缓存、错误处理、日志记录
        """
        if tool_name not in self.tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # 生成缓存键
        cache_key = self._generate_cache_key(tool_name, params)
        
        # 检查缓存
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # 执行工具
        try:
            result = await self.tools[tool_name](params)
            
            # 缓存结果（TTL 1小时）
            self.cache.setex(
                cache_key,
                3600,
                json.dumps(result, ensure_ascii=False)
            )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def _generate_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        param_str = json.dumps(params, sort_keys=True)
        hash_str = hashlib.md5(f"{tool_name}:{param_str}".encode()).hexdigest()
        return f"tool_cache:{tool_name}:{hash_str}"
```

### 5.2 Redis缓存策略

```python
# 缓存策略配置
CACHE_CONFIG = {
    # MVP阶段工具
    "query_analysis_results": {
        "ttl": 3600,  # 1小时
        "invalidate_on": ["new_analysis_created"]
    },
    "execute_marginal_analysis": {
        "ttl": 7200,  # 2小时
        "invalidate_on": ["data_updated"]
    },
    "optimize_weights": {
        "ttl": 86400,  # 24小时
        "invalidate_on": ["weights_manually_updated"]
    },
    "get_insights": {
        "ttl": 1800,  # 30分钟
        "invalidate_on": ["new_analysis_created"]
    },
    "search_knowledge_base": {
        "ttl": 600,  # 10分钟
        "invalidate_on": ["knowledge_base_updated"]
    },
    
    # 外部API调用（更长缓存）
    "search_industry_data": {
        "ttl": 604800,  # 7天
        "invalidate_on": []
    },
    "read_research_report": {
        "ttl": 2592000,  # 30天
        "invalidate_on": []
    }
}

# 缓存失效触发器
class CacheInvalidator:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def invalidate_pattern(self, pattern: str):
        """使匹配模式的所有缓存失效"""
        for key in self.redis.scan_iter(match=f"tool_cache:*{pattern}*"):
            self.redis.delete(key)
    
    def on_new_analysis_created(self, analysis_id: str):
        """新分析创建时的缓存失效"""
        self.invalidate_pattern("query_analysis_results")
        self.invalidate_pattern("get_insights")
    
    def on_data_updated(self, data_type: str, month: str):
        """数据更新时的缓存失效"""
        self.invalidate_pattern(f"execute_marginal_analysis:*{month}*")
        self.invalidate_pattern(f"query_{data_type}_data:*{month}*")
```

### 5.3 vLLM Serving配置

```python
# 本地模型部署配置
# docker-compose.yml
services:
  vllm-server:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
    environment:
      - MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
      - TENSOR_PARALLEL_SIZE=1
      - MAX_MODEL_LEN=8192
      - GPU_MEMORY_UTILIZATION=0.9
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model /models/Qwen2.5-7B-Instruct
      --served-model-name qwen2.5-7b
      --max-model-len 8192
      --tensor-parallel-size 1
```

```python
# 模型客户端
# backend/src/services/llm_client.py
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, use_local: bool = True):
        if use_local:
            self.client = AsyncOpenAI(
                base_url="http://localhost:8000/v1",
                api_key="dummy"  # vLLM不需要API key
            )
            self.model = "qwen2.5-7b"
        else:
            self.client = AsyncOpenAI(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = "gemini-1.5-pro"
    
    async def generate(self, messages: list, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
```

---

## 6. 成本优化策略

### 6.1 成本估算

#### 6.1.1 API调用成本（Gemini 1.5 Pro）

| 功能 | 月调用量 | 单次Token消耗 | 月成本（USD） |
|-----|---------|-------------|-------------|
| 简单问答（本地） | 10,000 | 0 | $0 |
| 深度研究 | 500 | 5,000 input + 2,000 output | $17.5 |
| 报告生成 | 200 | 3,000 input + 5,000 output | $9.8 |
| 洞察生成 | 1,000 | 2,000 input + 1,000 output | $10.5 |
| 外部搜索 | 300 | 1,000 input + 500 output | $1.8 |
| **总计** | **12,000** | - | **$39.6/月** |

#### 6.1.2 基础设施成本

| 组件 | 配置 | 月成本（USD） |
|-----|------|-------------|
| Google Cloud Run (Backend API) | 2 vCPU, 4GB RAM | $30 |
| Supabase PostgreSQL | Pro Plan | $25 |
| Redis Cloud | 1GB | $0 (免费套餐) |
| vLLM Server (可选，本地部署) | 1x T4 GPU | $50-100 |
| **总计（无本地GPU）** | - | **$94.6/月** |
| **总计（含本地GPU）** | - | **$144.6-194.6/月** |

### 6.2 缓存优化策略

**目标**: 缓存命中率 > 70%

```python
# 智能缓存预热
class CacheWarmer:
    """缓存预热服务"""
    
    async def warm_up_common_queries(self):
        """预热常见查询"""
        common_patterns = [
            # 最近月份的分析结果
            ("query_analysis_results", {"time_range": {"start_month": last_month}}),
            
            # 核心资产/能力数据
            ("query_asset_data", {"asset_types": "all", "month": current_month}),
            ("query_capability_data", {"capability_types": "all", "month": current_month}),
            
            # 常见洞察
            ("get_insights", {"insight_types": ["opportunity", "risk"], "limit": 10})
        ]
        
        for tool_name, params in common_patterns:
            await tool_server.call(tool_name, params)
    
    async def predict_and_cache(self):
        """基于用户行为预测并缓存"""
        # 分析用户查询模式
        user_patterns = analyze_user_query_patterns()
        
        # 预测可能的查询
        predicted_queries = predict_next_queries(user_patterns)
        
        # 提前执行并缓存
        for query in predicted_queries:
            await execute_and_cache(query)
```

### 6.3 本地模型 vs API切换策略

```python
class AdaptiveModelRouter:
    """自适应模型路由"""
    
    def __init__(self):
        self.local_model = LLMClient(use_local=True)
        self.api_model = LLMClient(use_local=False)
        self.fallback_threshold = 0.7  # 置信度阈值
    
    async def route_with_fallback(self, messages: list) -> str:
        """
        先尝试本地模型，置信度不足时回退到API
        """
        # 1. 尝试本地模型
        local_response = await self.local_model.generate(
            messages, 
            temperature=0.3,
            max_tokens=2000
        )
        
        # 2. 评估置信度
        confidence = self.evaluate_confidence(local_response)
        
        # 3. 如果置信度不足，使用API模型
        if confidence < self.fallback_threshold:
            logger.info(f"本地模型置信度不足 ({confidence:.2f})，回退到Gemini API")
            return await self.api_model.generate(messages)
        
        return local_response
    
    def evaluate_confidence(self, response: str) -> float:
        """
        评估响应的置信度
        
        考虑因素:
        - 响应长度是否合理
        - 是否包含不确定性表达 ("可能", "大概", "不确定")
        - 是否包含具体数据和事实
        - 是否符合预期格式
        """
        confidence = 1.0
        
        # 长度检查
        if len(response) < 50:
            confidence *= 0.6
        
        # 不确定性表达检查
        uncertain_phrases = ["可能", "大概", "不太确定", "或许", "也许"]
        for phrase in uncertain_phrases:
            if phrase in response:
                confidence *= 0.8
        
        # 数据和事实检查
        has_numbers = bool(re.search(r'\d+', response))
        has_specific_terms = bool(re.search(r'(资产|能力|效能|价值|ROI)', response))
        if not (has_numbers and has_specific_terms):
            confidence *= 0.7
        
        return confidence
```

### 6.4 Google Cloud Run部署优化

```yaml
# cloudrun-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: qbm-ai-copilot
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"  # 保持1个实例热启动
        autoscaling.knative.dev/maxScale: "10"
        autoscaling.knative.dev/target: "80"  # 80% CPU使用率时扩容
    spec:
      containers:
      - image: gcr.io/project-id/qbm-ai-copilot:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
          requests:
            memory: "1Gi"
            cpu: "1"
        env:
        - name: USE_LOCAL_MODEL
          value: "false"  # Cloud Run上不部署本地模型
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

**成本优化要点**:
1. **最小实例数设为1**: 避免冷启动，保证响应速度
2. **最大实例数设为10**: 控制突发流量成本
3. **目标CPU使用率80%**: 平衡性能和成本
4. **仅使用Gemini API**: Cloud Run上不部署GPU，降低成本

---

## 7. 集成示例

### 7.1 Python SDK示例

```python
# qbm_ai_copilot_sdk.py
from typing import Dict, Any, List
import requests

class QBMCopilot:
    """QBM AI Copilot Python SDK"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.session_id = None
    
    def ask(self, question: str, mode: str = "auto") -> Dict[str, Any]:
        """
        向AI Copilot提问
        
        Args:
            question: 用户问题
            mode: 处理模式 "simple"/"deep"/"auto"
        
        Returns:
            响应字典
        """
        response = requests.post(
            f"{self.api_url}/api/v1/copilot/ask",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "question": question,
                "mode": mode,
                "session_id": self.session_id
            }
        )
        
        result = response.json()
        self.session_id = result.get("session_id")
        
        return result
    
    def execute_analysis(self, month: str, options: Dict = None) -> Dict:
        """执行边际影响分析"""
        return self._call_tool("execute_marginal_analysis", {
            "analysis_month": month,
            "options": options or {}
        })
    
    def optimize_weights(self, historical_months: int = 12) -> Dict:
        """优化权重"""
        return self._call_tool("optimize_weights", {
            "historical_months": historical_months
        })
    
    def get_insights(self, time_range: Dict = None) -> List[Dict]:
        """获取洞察"""
        result = self._call_tool("get_insights", {
            "time_range": time_range or {}
        })
        return result.get("insights", [])
    
    def _call_tool(self, tool_name: str, params: Dict) -> Dict:
        """调用工具"""
        response = requests.post(
            f"{self.api_url}/api/v1/copilot/tools/{tool_name}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=params
        )
        return response.json()

# 使用示例
copilot = QBMCopilot(
    api_url="https://qbm-api.example.com",
    api_key="your-api-key"
)

# 简单问答
response = copilot.ask("2024年10月的研发资产NPV是多少？")
print(response["message"])

# 执行分析
analysis = copilot.execute_analysis("2024-10", {
    "use_historical_fitting": True,
    "generate_insights": True
})
print(f"ROI: {analysis['results']['利润与ROI']['ROI']}")

# 获取洞察
insights = copilot.get_insights({"start_month": "2024-01", "end_month": "2024-10"})
for insight in insights:
    print(f"[{insight['priority']}] {insight['title']}")
```

### 7.2 REST API调用示例

```bash
# 1. 认证
curl -X POST https://qbm-api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@enterprise.com",
    "password": "password"
  }'

# 响应: { "access_token": "eyJ0...", "token_type": "bearer" }

# 2. 提问
curl -X POST https://qbm-api.example.com/api/v1/copilot/ask \
  -H "Authorization: Bearer eyJ0..." \
  -H "Content-Type: application/json" \
  -d '{
    "question": "帮我分析一下最近3个月的研发效能趋势",
    "mode": "deep"
  }'

# 3. 调用工具
curl -X POST https://qbm-api.example.com/api/v1/copilot/tools/execute_marginal_analysis \
  -H "Authorization: Bearer eyJ0..." \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_month": "2024-10",
    "options": {
      "use_historical_fitting": true,
      "generate_insights": true
    }
  }'
```

### 7.3 Frontend集成代码

```typescript
// frontend/src/services/copilotService.ts
import axios from 'axios';

interface CopilotQuestion {
  question: string;
  mode?: 'simple' | 'deep' | 'auto';
  sessionId?: string;
}

interface CopilotResponse {
  success: boolean;
  message: string;
  data?: any;
  suggestions?: string[];
  sessionId: string;
}

class CopilotService {
  private baseURL: string;
  private sessionId: string | null = null;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async ask(question: string, mode: string = 'auto'): Promise<CopilotResponse> {
    const response = await axios.post<CopilotResponse>(
      `${this.baseURL}/api/v1/copilot/ask`,
      {
        question,
        mode,
        session_id: this.sessionId
      }
    );

    // 保存session ID以支持多轮对话
    this.sessionId = response.data.sessionId;
    
    return response.data;
  }

  async callTool(toolName: string, params: any): Promise<any> {
    const response = await axios.post(
      `${this.baseURL}/api/v1/copilot/tools/${toolName}`,
      params
    );
    return response.data;
  }

  resetSession() {
    this.sessionId = null;
  }
}

export const copilotService = new CopilotService();
```

```typescript
// frontend/src/components/CopilotChat.tsx
import React, { useState } from 'react';
import { copilotService } from '../services/copilotService';

export const CopilotChat: React.FC = () => {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      // 调用AI Copilot
      const response = await copilotService.ask(input);
      
      // 添加AI响应
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.message 
      }]);
    } catch (error) {
      console.error('Error calling copilot:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '抱歉，处理您的请求时出现了错误。' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="copilot-chat">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && <div className="message assistant loading">思考中...</div>}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="问我任何关于边际影响分析的问题..."
        />
        <button onClick={handleSend} disabled={loading}>
          发送
        </button>
      </div>
    </div>
  );
};
```

### 7.4 Gradio UI示例

```python
# gradio_app.py
import gradio as gr
from qbm_ai_copilot_sdk import QBMCopilot

copilot = QBMCopilot(
    api_url="http://localhost:8000",
    api_key="your-api-key"
)

def chat(message, history):
    """聊天接口"""
    response = copilot.ask(message, mode="auto")
    return response["message"]

def execute_analysis(month, use_fitting, gen_insights):
    """执行分析"""
    result = copilot.execute_analysis(month, {
        "use_historical_fitting": use_fitting,
        "generate_insights": gen_insights
    })
    
    # 格式化输出
    output = f"""
    ### 分析结果 ({month})
    
    **ROI**: {result['results']['利润与ROI']['ROI']:.2f}
    **研发效能**: {result['results']['效能指标']['研发效能']['value']:.2f}
    **生产效能**: {result['results']['效能指标']['生产效能']['value']:.2f}
    
    ### 主要洞察
    """
    
    if result['results'].get('insights'):
        for insight in result['results']['insights'][:3]:
            output += f"\n- [{insight['priority']}] {insight['title']}"
    
    return output

# 创建Gradio界面
with gr.Blocks(title="QBM AI Copilot") as demo:
    gr.Markdown("# 🤖 QBM边际影响分析 AI Copilot")
    
    with gr.Tab("💬 智能问答"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox(placeholder="问我任何问题...")
        clear = gr.Button("清除对话")
        
        msg.submit(chat, [msg, chatbot], [chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
    
    with gr.Tab("📊 执行分析"):
        with gr.Row():
            month_input = gr.Textbox(label="分析月份", value="2024-10")
            use_fitting = gr.Checkbox(label="使用历史数据拟合", value=True)
            gen_insights = gr.Checkbox(label="生成洞察", value=True)
        
        analyze_btn = gr.Button("执行分析")
        analysis_output = gr.Markdown()
        
        analyze_btn.click(
            execute_analysis,
            inputs=[month_input, use_fitting, gen_insights],
            outputs=analysis_output
        )
    
    with gr.Tab("⚙️ 权重优化"):
        hist_months = gr.Slider(minimum=3, maximum=24, value=12, step=1, 
                               label="历史数据月数")
        optimize_btn = gr.Button("开始优化")
        optimization_output = gr.JSON()
        
        optimize_btn.click(
            lambda months: copilot.optimize_weights(months),
            inputs=hist_months,
            outputs=optimization_output
        )

demo.launch()
```

---

## 8. 部署和运维指南

### 8.1 本地开发环境部署

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/qbm-ai-system.git
cd qbm-ai-system

# 2. 设置环境变量
cp .env.example .env
# 编辑.env，填入API keys等配置

# 3. 启动服务（使用Docker Compose）
docker-compose up -d

# 包括的服务:
# - PostgreSQL (5432)
# - Redis (6379)
# - Backend API (8000)
# - Frontend (3000)
# - vLLM Server (8001，可选）

# 4. 初始化数据库
docker-compose exec backend python -m scripts.init_database

# 5. 测试AI Copilot
curl http://localhost:8000/api/v1/copilot/health
```

### 8.2 生产环境部署（Google Cloud Run）

```bash
# 1. 构建Docker镜像
docker build -t gcr.io/your-project/qbm-backend:latest -f backend/Dockerfile .
docker build -t gcr.io/your-project/qbm-frontend:latest -f frontend/Dockerfile .

# 2. 推送到Google Container Registry
docker push gcr.io/your-project/qbm-backend:latest
docker push gcr.io/your-project/qbm-frontend:latest

# 3. 部署到Cloud Run
gcloud run deploy qbm-backend \
  --image gcr.io/your-project/qbm-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://...,GEMINI_API_KEY=..." \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10

gcloud run deploy qbm-frontend \
  --image gcr.io/your-project/qbm-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 8.3 监控和日志

```python
# backend/src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
copilot_requests_total = Counter(
    'copilot_requests_total',
    'Total AI Copilot requests',
    ['tool_name', 'mode', 'status']
)

copilot_request_duration = Histogram(
    'copilot_request_duration_seconds',
    'AI Copilot request duration',
    ['tool_name', 'mode']
)

copilot_cache_hits = Counter(
    'copilot_cache_hits_total',
    'Total cache hits',
    ['tool_name']
)

copilot_llm_api_calls = Counter(
    'copilot_llm_api_calls_total',
    'Total LLM API calls',
    ['model', 'status']
)

copilot_llm_tokens = Counter(
    'copilot_llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']  # type: input/output
)

# 使用示例
@copilot_request_duration.time()
async def handle_copilot_request(tool_name: str, params: dict):
    start_time = time.time()
    
    try:
        result = await execute_tool(tool_name, params)
        copilot_requests_total.labels(
            tool_name=tool_name,
            mode=params.get('mode', 'auto'),
            status='success'
        ).inc()
        return result
        
    except Exception as e:
        copilot_requests_total.labels(
            tool_name=tool_name,
            mode=params.get('mode', 'auto'),
            status='error'
        ).inc()
        raise
```

**监控仪表板（Grafana）**:
- 请求量和成功率
- 响应时间（P50, P95, P99）
- 缓存命中率
- API调用次数和成本
- Token使用量
- 错误率和类型分布

### 8.4 故障排查

常见问题和解决方案:

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| 响应超时 | 1. 数据库查询慢<br>2. API调用超时<br>3. 缓存未命中 | 1. 优化SQL查询<br>2. 增加超时时间<br>3. 预热缓存 |
| 成本过高 | 1. 缓存命中率低<br>2. 过度使用Gemini API | 1. 调整缓存策略<br>2. 优化路由逻辑 |
| 响应质量差 | 1. 本地模型能力不足<br>2. Prompt设计问题 | 1. 升级到API模型<br>2. 优化Prompt模板 |
| 并发处理慢 | 1. 实例数不足<br>2. 数据库连接池满 | 1. 增加max-instances<br>2. 扩大连接池 |

---

## 9. 附录

### 9.1 术语表

| 术语 | 定义 |
|-----|------|
| Agent Loop | AI代理的核心处理循环：问题理解→工具规划→执行→合成 |
| Tool Server | 工具服务器，管理和执行所有工具函数 |
| 智能路由 | 根据问题复杂度自动选择处理模式（本地/API） |
| 混合部署 | 结合本地模型和云API的部署策略 |
| vLLM | 高效的大模型推理服务器 |
| Gemini 1.5 Pro | Google的大语言模型API |

### 9.2 参考资料

- [PokeeResearchOSS GitHub](https://github.com/Pokee-AI/PokeeResearchOSS) - Agent Loop设计参考
- [vLLM Documentation](https://docs.vllm.ai/) - 本地模型部署
- [Gemini API Documentation](https://ai.google.dev/docs) - Google AI API
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs) - 部署指南

### 9.3 变更日志

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v1.0.0 | 2025-10-23 | 初始版本，包含MVP 5个工具 |
| v1.1.0 | TBD | 扩展至10个工具 |
| v2.0.0 | TBD | 完整15个工具 + 外部API集成 |

---

## 10. 下一步行动

### 10.1 Cursor的交付物 ✅

- [x] AI Copilot集成文档（本文档）
- [ ] Tool Server实现代码
- [ ] Agent Loop实现代码
- [ ] 智能路由实现代码
- [ ] 单元测试和集成测试

### 10.2 Lovable的实施任务 ⏳

**优先级1（MVP阶段）**:
1. 创建AI Copilot聊天界面组件
2. 集成5个核心工具函数API
3. 实现简单问答模式UI
4. 实现会话历史管理

**优先级2（扩展阶段）**:
5. 集成10个工具函数（含5个新增）
6. 实现深度研究模式UI（进度条、多步骤展示）
7. 实现报告生成和下载功能
8. 添加洞察可视化组件

**优先级3（完整阶段）**:
9. 集成15个完整工具函数
10. 实现外部数据搜索UI
11. 添加场景模拟交互界面
12. 优化建议的可视化呈现

### 10.3 协作检查点

- [ ] **检查点1**: MVP 5个工具函数API测试通过（Cursor → Lovable）
- [ ] **检查点2**: 聊天界面集成完成并联调（Lovable → Cursor）
- [ ] **检查点3**: 扩展阶段10个工具全部集成（Lovable）
- [ ] **检查点4**: 完整15个工具上线并性能优化（Cursor + Lovable）

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计交付时间**:
- MVP阶段（5个工具）: 2周
- 扩展阶段（10个工具）: +2周
- 完整阶段（15个工具）: +3周
- **总计**: 7周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com


