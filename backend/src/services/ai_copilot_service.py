"""
AI Copilot工具服务器
实现15个核心工具函数，支持Agent Loop和智能路由
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import text
import openai
from anthropic import Anthropic

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolType(Enum):
    """工具类型枚举"""

    ANALYSIS = "analysis"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"
    RESEARCH = "research"
    SIMULATION = "simulation"


class ExecutionStatus(Enum):
    """执行状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ToolRequest:
    """工具请求数据结构"""

    tool_id: str
    tool_name: str
    tool_type: ToolType
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    user_id: str
    session_id: str
    request_id: str
    timestamp: datetime


@dataclass
class ToolResponse:
    """工具响应数据结构"""

    request_id: str
    tool_id: str
    status: ExecutionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    timestamp: datetime = None


class AICopilotToolServer:
    """AI Copilot工具服务器"""

    def __init__(
        self, db_service, cache_service, openai_api_key: str, anthropic_api_key: str
    ):
        self.db_service = db_service
        self.cache_service = cache_service
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)

        # 工具注册表
        self.tools = self._register_tools()

        # 执行队列
        self.execution_queue = asyncio.Queue()
        self.active_executions = {}

        # 智能路由配置
        self.routing_rules = self._setup_routing_rules()

    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """注册所有工具"""
        return {
            # MVP阶段 - 5个核心工具
            "marginal_analysis": {
                "name": "边际影响分析",
                "type": ToolType.ANALYSIS,
                "description": "分析业务决策的边际影响",
                "function": self._execute_marginal_analysis,
                "parameters": [
                    "business_scenario",
                    "decision_variables",
                    "time_horizon",
                ],
                "priority": 1,
            },
            "synergy_detection": {
                "name": "协同效应检测",
                "type": ToolType.ANALYSIS,
                "description": "检测业务要素间的协同效应",
                "function": self._execute_synergy_detection,
                "parameters": ["feature_data", "target_metric", "analysis_depth"],
                "priority": 1,
            },
            "threshold_analysis": {
                "name": "阈值效应分析",
                "type": ToolType.ANALYSIS,
                "description": "识别关键业务阈值",
                "function": self._execute_threshold_analysis,
                "parameters": [
                    "metric_data",
                    "threshold_candidates",
                    "sensitivity_level",
                ],
                "priority": 1,
            },
            "scenario_simulation": {
                "name": "场景模拟",
                "type": ToolType.SIMULATION,
                "description": "模拟不同业务场景",
                "function": self._execute_scenario_simulation,
                "parameters": [
                    "scenario_params",
                    "simulation_period",
                    "monte_carlo_runs",
                ],
                "priority": 1,
            },
            "optimization_suggestion": {
                "name": "优化建议生成",
                "type": ToolType.OPTIMIZATION,
                "description": "生成业务优化建议",
                "function": self._execute_optimization_suggestion,
                "parameters": ["current_state", "constraints", "optimization_goals"],
                "priority": 1,
            },
            # 扩展阶段 - 5个新增工具
            "trend_forecasting": {
                "name": "趋势预测",
                "type": ToolType.PREDICTION,
                "description": "预测业务趋势",
                "function": self._execute_trend_forecasting,
                "parameters": [
                    "historical_data",
                    "forecast_horizon",
                    "confidence_level",
                ],
                "priority": 2,
            },
            "risk_assessment": {
                "name": "风险评估",
                "type": ToolType.ANALYSIS,
                "description": "评估业务风险",
                "function": self._execute_risk_assessment,
                "parameters": ["risk_factors", "impact_matrix", "probability_data"],
                "priority": 2,
            },
            "competitor_analysis": {
                "name": "竞争对手分析",
                "type": ToolType.RESEARCH,
                "description": "分析竞争对手动态",
                "function": self._execute_competitor_analysis,
                "parameters": [
                    "competitor_list",
                    "analysis_dimensions",
                    "data_sources",
                ],
                "priority": 2,
            },
            "market_research": {
                "name": "市场研究",
                "type": ToolType.RESEARCH,
                "description": "进行市场研究分析",
                "function": self._execute_market_research,
                "parameters": [
                    "market_scope",
                    "research_questions",
                    "data_requirements",
                ],
                "priority": 2,
            },
            "performance_benchmarking": {
                "name": "性能基准测试",
                "type": ToolType.ANALYSIS,
                "description": "进行性能基准测试",
                "function": self._execute_performance_benchmarking,
                "parameters": ["benchmark_metrics", "comparison_group", "time_period"],
                "priority": 2,
            },
            # 完整阶段 - 5个高级工具
            "deep_research": {
                "name": "深度研究",
                "type": ToolType.RESEARCH,
                "description": "进行深度业务研究",
                "function": self._execute_deep_research,
                "parameters": ["research_topic", "depth_level", "data_sources"],
                "priority": 3,
            },
            "strategic_planning": {
                "name": "战略规划",
                "type": ToolType.OPTIMIZATION,
                "description": "制定战略规划",
                "function": self._execute_strategic_planning,
                "parameters": [
                    "strategic_goals",
                    "resource_constraints",
                    "time_horizon",
                ],
                "priority": 3,
            },
            "change_impact_analysis": {
                "name": "变革影响分析",
                "type": ToolType.ANALYSIS,
                "description": "分析变革影响",
                "function": self._execute_change_impact_analysis,
                "parameters": [
                    "change_proposal",
                    "stakeholder_map",
                    "impact_dimensions",
                ],
                "priority": 3,
            },
            "resource_optimization": {
                "name": "资源优化",
                "type": ToolType.OPTIMIZATION,
                "description": "优化资源配置",
                "function": self._execute_resource_optimization,
                "parameters": [
                    "resource_pool",
                    "demand_forecast",
                    "optimization_objectives",
                ],
                "priority": 3,
            },
            "insight_synthesis": {
                "name": "洞察综合",
                "type": ToolType.ANALYSIS,
                "description": "综合多维度洞察",
                "function": self._execute_insight_synthesis,
                "parameters": ["insight_sources", "synthesis_method", "output_format"],
                "priority": 3,
            },
        }

    def _setup_routing_rules(self) -> Dict[str, Any]:
        """设置智能路由规则"""
        return {
            "priority_routing": {
                "high_priority_keywords": ["urgent", "critical", "immediate"],
                "priority_boost": 2.0,
            },
            "context_routing": {
                "analysis_context": [
                    "marginal_analysis",
                    "synergy_detection",
                    "threshold_analysis",
                ],
                "prediction_context": ["trend_forecasting", "scenario_simulation"],
                "research_context": [
                    "market_research",
                    "competitor_analysis",
                    "deep_research",
                ],
            },
            "user_preference_routing": {
                "preferred_tools": {},
                "avoided_tools": {},
                "execution_preferences": {},
            },
        }

    async def process_tool_request(self, request: ToolRequest) -> ToolResponse:
        """处理工具请求"""
        try:
            # 智能路由
            routed_tool = await self._route_request(request)

            # 执行工具
            start_time = datetime.now()
            result = await self._execute_tool(routed_tool, request)
            execution_time = (datetime.now() - start_time).total_seconds()

            # 生成洞察和建议
            insights, recommendations = (
                await self._generate_insights_and_recommendations(request, result)
            )

            return ToolResponse(
                request_id=request.request_id,
                tool_id=routed_tool["tool_id"],
                status=ExecutionStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                insights=insights,
                recommendations=recommendations,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return ToolResponse(
                request_id=request.request_id,
                tool_id=request.tool_id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                timestamp=datetime.now(),
            )

    async def _route_request(self, request: ToolRequest) -> Dict[str, Any]:
        """智能路由请求"""
        # 基于关键词的路由
        if any(
            keyword in request.context.get("query", "").lower()
            for keyword in self.routing_rules["priority_routing"][
                "high_priority_keywords"
            ]
        ):
            # 高优先级请求，选择最快的工具
            return self._select_fastest_tool(request)

        # 基于上下文的路由
        context_type = self._determine_context_type(request)
        context_tools = self.routing_rules["context_routing"].get(context_type, [])

        if context_tools:
            # 选择上下文相关的工具
            return self._select_context_tool(request, context_tools)

        # 默认路由
        return self.tools[request.tool_id]

    def _determine_context_type(self, request: ToolRequest) -> str:
        """确定上下文类型"""
        query = request.context.get("query", "").lower()

        if any(word in query for word in ["分析", "影响", "效应", "阈值"]):
            return "analysis_context"
        elif any(word in query for word in ["预测", "趋势", "模拟", "场景"]):
            return "prediction_context"
        elif any(word in query for word in ["研究", "市场", "竞争", "深度"]):
            return "research_context"

        return "general_context"

    def _select_fastest_tool(self, request: ToolRequest) -> Dict[str, Any]:
        """选择最快的工具"""
        # 优先选择MVP阶段的工具（优先级1）
        mvp_tools = [tool for tool in self.tools.values() if tool["priority"] == 1]
        if mvp_tools:
            return mvp_tools[0]
        return self.tools[request.tool_id]

    def _select_context_tool(
        self, request: ToolRequest, context_tools: List[str]
    ) -> Dict[str, Any]:
        """选择上下文相关的工具"""
        for tool_name in context_tools:
            if tool_name in self.tools:
                return self.tools[tool_name]
        return self.tools[request.tool_id]

    async def _execute_tool(
        self, tool: Dict[str, Any], request: ToolRequest
    ) -> Dict[str, Any]:
        """执行工具"""
        tool_function = tool["function"]
        return await tool_function(request.parameters, request.context)

    async def _generate_insights_and_recommendations(
        self, request: ToolRequest, result: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """生成洞察和建议"""
        try:
            # 使用AI生成洞察
            prompt = f"""
            基于以下分析结果，生成3-5个关键洞察和2-3个具体建议：
            
            请求上下文: {request.context}
            分析结果: {result}
            
            请以JSON格式返回：
            {{
                "insights": ["洞察1", "洞察2", "洞察3"],
                "recommendations": ["建议1", "建议2"]
            }}
            """

            response = await self._call_ai_model(prompt)
            ai_result = json.loads(response)

            return ai_result.get("insights", []), ai_result.get("recommendations", [])

        except Exception as e:
            logger.error(f"Failed to generate insights: {str(e)}")
            return [], []

    async def _call_ai_model(self, prompt: str) -> str:
        """调用AI模型"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # 降级到Anthropic
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            except Exception as e2:
                logger.error(f"Anthropic API call failed: {str(e2)}")
                return "AI模型调用失败，无法生成洞察和建议"

    # ==================== 工具实现 ====================

    async def _execute_marginal_analysis(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行边际影响分析"""
        try:
            business_scenario = parameters.get("business_scenario")
            decision_variables = parameters.get("decision_variables", [])
            time_horizon = parameters.get("time_horizon", 12)

            # 获取相关数据
            data = await self._get_analysis_data(business_scenario, time_horizon)

            # 执行边际分析
            analysis_result = await self._perform_marginal_analysis(
                data, decision_variables
            )

            return {
                "analysis_type": "marginal_analysis",
                "scenario": business_scenario,
                "decision_variables": decision_variables,
                "time_horizon": time_horizon,
                "marginal_effects": analysis_result["marginal_effects"],
                "sensitivity_analysis": analysis_result["sensitivity_analysis"],
                "recommendations": analysis_result["recommendations"],
                "confidence_score": analysis_result["confidence_score"],
            }

        except Exception as e:
            logger.error(f"Marginal analysis failed: {str(e)}")
            raise

    async def _execute_synergy_detection(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行协同效应检测"""
        try:
            feature_data = parameters.get("feature_data")
            target_metric = parameters.get("target_metric")
            analysis_depth = parameters.get("analysis_depth", "medium")

            # 执行协同效应分析
            synergy_result = await self._detect_synergies(
                feature_data, target_metric, analysis_depth
            )

            return {
                "analysis_type": "synergy_detection",
                "target_metric": target_metric,
                "analysis_depth": analysis_depth,
                "synergy_effects": synergy_result["synergy_effects"],
                "interaction_matrix": synergy_result["interaction_matrix"],
                "significance_scores": synergy_result["significance_scores"],
                "optimization_opportunities": synergy_result[
                    "optimization_opportunities"
                ],
            }

        except Exception as e:
            logger.error(f"Synergy detection failed: {str(e)}")
            raise

    async def _execute_threshold_analysis(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行阈值效应分析"""
        try:
            metric_data = parameters.get("metric_data")
            threshold_candidates = parameters.get("threshold_candidates", [])
            sensitivity_level = parameters.get("sensitivity_level", "medium")

            # 执行阈值分析
            threshold_result = await self._analyze_thresholds(
                metric_data, threshold_candidates, sensitivity_level
            )

            return {
                "analysis_type": "threshold_analysis",
                "sensitivity_level": sensitivity_level,
                "identified_thresholds": threshold_result["thresholds"],
                "threshold_effects": threshold_result["effects"],
                "stability_analysis": threshold_result["stability"],
                "recommended_thresholds": threshold_result["recommendations"],
            }

        except Exception as e:
            logger.error(f"Threshold analysis failed: {str(e)}")
            raise

    async def _execute_scenario_simulation(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行场景模拟"""
        try:
            scenario_params = parameters.get("scenario_params")
            simulation_period = parameters.get("simulation_period", 12)
            monte_carlo_runs = parameters.get("monte_carlo_runs", 1000)

            # 执行蒙特卡洛模拟
            simulation_result = await self._run_scenario_simulation(
                scenario_params, simulation_period, monte_carlo_runs
            )

            return {
                "analysis_type": "scenario_simulation",
                "simulation_period": simulation_period,
                "monte_carlo_runs": monte_carlo_runs,
                "scenario_results": simulation_result["results"],
                "probability_distributions": simulation_result["distributions"],
                "risk_metrics": simulation_result["risk_metrics"],
                "sensitivity_analysis": simulation_result["sensitivity"],
            }

        except Exception as e:
            logger.error(f"Scenario simulation failed: {str(e)}")
            raise

    async def _execute_optimization_suggestion(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行优化建议生成"""
        try:
            current_state = parameters.get("current_state")
            constraints = parameters.get("constraints", [])
            optimization_goals = parameters.get("optimization_goals", [])

            # 生成优化建议
            optimization_result = await self._generate_optimization_suggestions(
                current_state, constraints, optimization_goals
            )

            return {
                "analysis_type": "optimization_suggestion",
                "current_state": current_state,
                "constraints": constraints,
                "optimization_goals": optimization_goals,
                "suggestions": optimization_result["suggestions"],
                "expected_improvements": optimization_result["improvements"],
                "implementation_roadmap": optimization_result["roadmap"],
                "risk_assessment": optimization_result["risks"],
            }

        except Exception as e:
            logger.error(f"Optimization suggestion failed: {str(e)}")
            raise

    # ==================== 辅助方法 ====================

    async def _get_analysis_data(
        self, scenario: str, time_horizon: int
    ) -> pd.DataFrame:
        """获取分析数据"""
        # 从数据库获取相关数据
        query = """
        SELECT * FROM marginal_analysis_results 
        WHERE business_scenario = :scenario 
        AND analysis_date >= :start_date
        ORDER BY analysis_date DESC
        LIMIT 1000
        """

        start_date = datetime.now() - timedelta(days=time_horizon * 30)

        result = await self.db_service.execute_query(
            query, {"scenario": scenario, "start_date": start_date}
        )

        return pd.DataFrame(result)

    async def _perform_marginal_analysis(
        self, data: pd.DataFrame, decision_variables: List[str]
    ) -> Dict[str, Any]:
        """执行边际分析"""
        # 这里调用之前实现的边际分析算法
        from src.algorithms.marginal_analysis import MarginalAnalysis

        analyzer = MarginalAnalysis()
        result = analyzer.analyze_marginal_effects(data, decision_variables)

        return result

    async def _detect_synergies(
        self, feature_data: Dict[str, Any], target_metric: str, analysis_depth: str
    ) -> Dict[str, Any]:
        """检测协同效应"""
        from src.algorithms.synergy_analysis import SynergyAnalysis

        analyzer = SynergyAnalysis()

        # 转换数据格式
        X = pd.DataFrame(feature_data["features"])
        y = pd.Series(feature_data["target"])

        result = analyzer.detect_synergy_effects(X, y)

        return result

    async def _analyze_thresholds(
        self,
        metric_data: Dict[str, Any],
        threshold_candidates: List[float],
        sensitivity_level: str,
    ) -> Dict[str, Any]:
        """分析阈值"""
        from src.algorithms.threshold_analysis import ThresholdAnalysis

        analyzer = ThresholdAnalysis()

        # 转换数据格式
        X = pd.DataFrame(metric_data["features"])
        y = pd.Series(metric_data["target"])

        result = analyzer.detect_threshold_effects(X, y)

        return result

    async def _run_scenario_simulation(
        self,
        scenario_params: Dict[str, Any],
        simulation_period: int,
        monte_carlo_runs: int,
    ) -> Dict[str, Any]:
        """运行场景模拟"""
        # 实现蒙特卡洛模拟逻辑
        results = []

        for run in range(monte_carlo_runs):
            # 生成随机场景
            scenario = self._generate_random_scenario(scenario_params)

            # 计算场景结果
            result = await self._calculate_scenario_result(scenario, simulation_period)
            results.append(result)

        # 统计分析
        results_df = pd.DataFrame(results)

        return {
            "results": results_df.to_dict("records"),
            "distributions": self._calculate_distributions(results_df),
            "risk_metrics": self._calculate_risk_metrics(results_df),
            "sensitivity": self._calculate_sensitivity(results_df, scenario_params),
        }

    async def _generate_optimization_suggestions(
        self,
        current_state: Dict[str, Any],
        constraints: List[str],
        optimization_goals: List[str],
    ) -> Dict[str, Any]:
        """生成优化建议"""
        # 基于当前状态和目标生成优化建议
        suggestions = []

        for goal in optimization_goals:
            suggestion = await self._generate_goal_specific_suggestion(
                current_state, goal, constraints
            )
            suggestions.append(suggestion)

        return {
            "suggestions": suggestions,
            "improvements": self._calculate_expected_improvements(suggestions),
            "roadmap": self._create_implementation_roadmap(suggestions),
            "risks": self._assess_implementation_risks(suggestions),
        }

    # ==================== 其他工具实现 ====================

    async def _execute_trend_forecasting(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行趋势预测"""
        # 实现趋势预测逻辑
        pass

    async def _execute_risk_assessment(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行风险评估"""
        # 实现风险评估逻辑
        pass

    async def _execute_competitor_analysis(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行竞争对手分析"""
        # 实现竞争对手分析逻辑
        pass

    async def _execute_market_research(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行市场研究"""
        # 实现市场研究逻辑
        pass

    async def _execute_performance_benchmarking(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行性能基准测试"""
        # 实现性能基准测试逻辑
        pass

    async def _execute_deep_research(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行深度研究"""
        # 实现深度研究逻辑
        pass

    async def _execute_strategic_planning(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行战略规划"""
        # 实现战略规划逻辑
        pass

    async def _execute_change_impact_analysis(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行变革影响分析"""
        # 实现变革影响分析逻辑
        pass

    async def _execute_resource_optimization(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行资源优化"""
        # 实现资源优化逻辑
        pass

    async def _execute_insight_synthesis(
        self, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行洞察综合"""
        # 实现洞察综合逻辑
        pass


# ==================== Agent Loop实现 ====================


class AgentLoop:
    """Agent循环执行器"""

    def __init__(self, tool_server: AICopilotToolServer):
        self.tool_server = tool_server
        self.conversation_history = []
        self.current_context = {}

    async def process_conversation(
        self, user_input: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """处理对话"""
        try:
            # 解析用户意图
            intent = await self._parse_user_intent(user_input)

            # 确定需要的工具
            required_tools = await self._determine_required_tools(intent)

            # 执行工具链
            results = []
            for tool_config in required_tools:
                request = ToolRequest(
                    tool_id=tool_config["tool_id"],
                    tool_name=tool_config["name"],
                    tool_type=tool_config["type"],
                    parameters=tool_config["parameters"],
                    context=self.current_context,
                    user_id=user_id,
                    session_id=session_id,
                    request_id=f"{session_id}_{len(results)}",
                    timestamp=datetime.now(),
                )

                response = await self.tool_server.process_tool_request(request)
                results.append(response)

            # 综合结果
            final_response = await self._synthesize_results(results, user_input)

            # 更新上下文
            self._update_context(final_response)

            return final_response

        except Exception as e:
            logger.error(f"Agent loop failed: {str(e)}")
            return {
                "status": "error",
                "message": f"处理失败: {str(e)}",
                "suggestions": ["请重新描述您的问题", "尝试使用更具体的业务场景"],
            }

    async def _parse_user_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图"""
        prompt = f"""
        分析以下用户输入的业务意图：
        
        用户输入: {user_input}
        
        请返回JSON格式的意图分析：
        {{
            "intent_type": "analysis|prediction|optimization|research|simulation",
            "business_domain": "销售|营销|运营|财务|战略",
            "urgency_level": "low|medium|high",
            "complexity_level": "simple|medium|complex",
            "required_data": ["数据1", "数据2"],
            "expected_output": "期望的输出类型"
        }}
        """

        response = await self.tool_server._call_ai_model(prompt)
        return json.loads(response)

    async def _determine_required_tools(
        self, intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """确定需要的工具"""
        intent_type = intent["intent_type"]
        complexity = intent["complexity_level"]

        tool_chain = []

        if intent_type == "analysis":
            if complexity == "simple":
                tool_chain.append(
                    {
                        "tool_id": "marginal_analysis",
                        "name": "边际影响分析",
                        "type": ToolType.ANALYSIS,
                        "parameters": intent["required_data"],
                    }
                )
            else:
                tool_chain.extend(
                    [
                        {
                            "tool_id": "marginal_analysis",
                            "name": "边际影响分析",
                            "type": ToolType.ANALYSIS,
                            "parameters": intent["required_data"],
                        },
                        {
                            "tool_id": "synergy_detection",
                            "name": "协同效应检测",
                            "type": ToolType.ANALYSIS,
                            "parameters": intent["required_data"],
                        },
                    ]
                )

        elif intent_type == "prediction":
            tool_chain.append(
                {
                    "tool_id": "trend_forecasting",
                    "name": "趋势预测",
                    "type": ToolType.PREDICTION,
                    "parameters": intent["required_data"],
                }
            )

        elif intent_type == "optimization":
            tool_chain.append(
                {
                    "tool_id": "optimization_suggestion",
                    "name": "优化建议生成",
                    "type": ToolType.OPTIMIZATION,
                    "parameters": intent["required_data"],
                }
            )

        return tool_chain

    async def _synthesize_results(
        self, results: List[ToolResponse], user_input: str
    ) -> Dict[str, Any]:
        """综合结果"""
        # 收集所有洞察和建议
        all_insights = []
        all_recommendations = []

        for result in results:
            if result.insights:
                all_insights.extend(result.insights)
            if result.recommendations:
                all_recommendations.extend(result.recommendations)

        # 使用AI综合结果
        synthesis_prompt = f"""
        基于以下分析结果，为用户问题生成综合回答：
        
        用户问题: {user_input}
        
        分析结果:
        {json.dumps([asdict(result) for result in results], default=str, indent=2)}
        
        关键洞察:
        {all_insights}
        
        建议:
        {all_recommendations}
        
        请生成一个结构化的回答，包括：
        1. 问题理解
        2. 分析发现
        3. 关键洞察
        4. 具体建议
        5. 下一步行动
        """

        synthesis_result = await self.tool_server._call_ai_model(synthesis_prompt)

        return {
            "status": "success",
            "user_input": user_input,
            "analysis_results": [asdict(result) for result in results],
            "synthesis": synthesis_result,
            "insights": all_insights,
            "recommendations": all_recommendations,
            "next_actions": self._generate_next_actions(results),
        }

    def _generate_next_actions(self, results: List[ToolResponse]) -> List[str]:
        """生成下一步行动"""
        actions = []

        for result in results:
            if result.status == ExecutionStatus.COMPLETED:
                if "optimization" in result.tool_id:
                    actions.append("考虑实施优化建议")
                elif "prediction" in result.tool_id:
                    actions.append("监控预测指标变化")
                elif "analysis" in result.tool_id:
                    actions.append("深入分析关键发现")

        return list(set(actions))  # 去重

    def _update_context(self, response: Dict[str, Any]):
        """更新上下文"""
        self.current_context.update(
            {
                "last_analysis": response.get("analysis_results", []),
                "last_insights": response.get("insights", []),
                "last_recommendations": response.get("recommendations", []),
            }
        )


# ==================== API接口 ====================


class AICopilotAPI:
    """AI Copilot API接口"""

    def __init__(self, tool_server: AICopilotToolServer, agent_loop: AgentLoop):
        self.tool_server = tool_server
        self.agent_loop = agent_loop

    async def chat_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """聊天端点"""
        user_input = request_data.get("message", "")
        user_id = request_data.get("user_id", "anonymous")
        session_id = request_data.get("session_id", "default")

        if not user_input:
            return {"status": "error", "message": "请输入您的问题"}

        # 使用Agent Loop处理对话
        response = await self.agent_loop.process_conversation(
            user_input, user_id, session_id
        )

        return response

    async def tool_execution_endpoint(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """工具执行端点"""
        tool_id = request_data.get("tool_id")
        parameters = request_data.get("parameters", {})
        context = request_data.get("context", {})
        user_id = request_data.get("user_id", "anonymous")
        session_id = request_data.get("session_id", "default")

        if not tool_id:
            return {"status": "error", "message": "请指定工具ID"}

        # 创建工具请求
        request = ToolRequest(
            tool_id=tool_id,
            tool_name=self.tool_server.tools[tool_id]["name"],
            tool_type=self.tool_server.tools[tool_id]["type"],
            parameters=parameters,
            context=context,
            user_id=user_id,
            session_id=session_id,
            request_id=f"{session_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
        )

        # 执行工具
        response = await self.tool_server.process_tool_request(request)

        return asdict(response)

    async def get_available_tools(self) -> Dict[str, Any]:
        """获取可用工具列表"""
        tools_info = {}
        for tool_id, tool_config in self.tool_server.tools.items():
            tools_info[tool_id] = {
                "name": tool_config["name"],
                "type": tool_config["type"].value,
                "description": tool_config["description"],
                "parameters": tool_config["parameters"],
                "priority": tool_config["priority"],
            }

        return {
            "status": "success",
            "tools": tools_info,
            "total_count": len(tools_info),
        }
