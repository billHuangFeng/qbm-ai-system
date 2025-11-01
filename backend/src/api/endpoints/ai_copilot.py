"""
AI Copilot API端点
提供聊天、工具执行、工具列表等API接口
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..services.ai_copilot_service import (
    AICopilotToolServer, 
    AgentLoop, 
    AICopilotAPI,
    ToolRequest,
    ToolType,
    ExecutionStatus
)
from ..services.database_service import DatabaseService
from ..services.cache_service import CacheService
from ..api.dependencies import get_db_service, get_cache_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/ai-copilot", tags=["AI Copilot"])

# 全局变量存储服务实例
ai_copilot_api: Optional[AICopilotAPI] = None

# Pydantic模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    user_id: str = Field(default="anonymous", description="用户ID")
    session_id: str = Field(default="default", description="会话ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")

class ToolExecutionRequest(BaseModel):
    """工具执行请求模型"""
    tool_id: str = Field(..., description="工具ID")
    parameters: Dict[str, Any] = Field(default={}, description="工具参数")
    context: Dict[str, Any] = Field(default={}, description="执行上下文")
    user_id: str = Field(default="anonymous", description="用户ID")
    session_id: str = Field(default="default", description="会话ID")

class ToolInfo(BaseModel):
    """工具信息模型"""
    tool_id: str
    name: str
    type: str
    description: str
    parameters: List[str]
    priority: int

class ChatResponse(BaseModel):
    """聊天响应模型"""
    status: str
    message: Optional[str] = None
    user_input: Optional[str] = None
    analysis_results: Optional[List[Dict[str, Any]]] = None
    synthesis: Optional[str] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    next_actions: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ToolExecutionResponse(BaseModel):
    """工具执行响应模型"""
    request_id: str
    tool_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    timestamp: datetime

class ToolsListResponse(BaseModel):
    """工具列表响应模型"""
    status: str
    tools: Dict[str, ToolInfo]
    total_count: int

# 依赖注入
async def get_ai_copilot_api(
    db_service: DatabaseService = Depends(get_db_service),
    cache_service: CacheService = Depends(get_cache_service)
) -> AICopilotAPI:
    """获取AI Copilot API实例"""
    global ai_copilot_api
    
    if ai_copilot_api is None:
        # 初始化AI Copilot服务
        openai_api_key = "your-openai-api-key"  # 从环境变量获取
        anthropic_api_key = "your-anthropic-api-key"  # 从环境变量获取
        
        tool_server = AICopilotToolServer(
            db_service=db_service,
            cache_service=cache_service,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key
        )
        
        agent_loop = AgentLoop(tool_server)
        ai_copilot_api = AICopilotAPI(tool_server, agent_loop)
    
    return ai_copilot_api

# API端点
@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    api: AICopilotAPI = Depends(get_ai_copilot_api)
):
    """
    与AI Copilot聊天
    
    这个端点允许用户与AI Copilot进行自然语言对话，
    AI会自动选择合适的工具来回答用户的问题。
    """
    try:
        # 准备请求数据
        request_data = {
            "message": request.message,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "context": request.context or {}
        }
        
        # 调用AI Copilot API
        response = await api.chat_endpoint(request_data)
        
        # 记录对话日志（后台任务）
        background_tasks.add_task(
            log_conversation,
            request.user_id,
            request.session_id,
            request.message,
            response
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"聊天处理失败: {str(e)}"
        )

@router.post("/execute-tool", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    background_tasks: BackgroundTasks,
    api: AICopilotAPI = Depends(get_ai_copilot_api)
):
    """
    直接执行指定工具
    
    这个端点允许直接调用特定的AI工具，
    绕过自然语言处理，直接执行工具功能。
    """
    try:
        # 准备请求数据
        request_data = {
            "tool_id": request.tool_id,
            "parameters": request.parameters,
            "context": request.context,
            "user_id": request.user_id,
            "session_id": request.session_id
        }
        
        # 调用工具执行API
        response = await api.tool_execution_endpoint(request_data)
        
        # 记录工具执行日志（后台任务）
        background_tasks.add_task(
            log_tool_execution,
            request.user_id,
            request.session_id,
            request.tool_id,
            response
        )
        
        return ToolExecutionResponse(**response)
        
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"工具执行失败: {str(e)}"
        )

@router.get("/tools", response_model=ToolsListResponse)
async def get_available_tools(
    api: AICopilotAPI = Depends(get_ai_copilot_api)
):
    """
    获取可用工具列表
    
    返回所有可用的AI工具及其详细信息。
    """
    try:
        response = await api.get_available_tools()
        
        # 转换工具信息格式
        tools_info = {}
        for tool_id, tool_config in response["tools"].items():
            tools_info[tool_id] = ToolInfo(
                tool_id=tool_id,
                name=tool_config["name"],
                type=tool_config["type"],
                description=tool_config["description"],
                parameters=tool_config["parameters"],
                priority=tool_config["priority"]
            )
        
        return ToolsListResponse(
            status=response["status"],
            tools=tools_info,
            total_count=response["total_count"]
        )
        
    except Exception as e:
        logger.error(f"Get tools error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取工具列表失败: {str(e)}"
        )

@router.get("/tools/{tool_id}")
async def get_tool_info(
    tool_id: str,
    api: AICopilotAPI = Depends(get_ai_copilot_api)
):
    """
    获取特定工具的详细信息
    """
    try:
        response = await api.get_available_tools()
        
        if tool_id not in response["tools"]:
            raise HTTPException(
                status_code=404,
                detail=f"工具 {tool_id} 不存在"
            )
        
        tool_config = response["tools"][tool_id]
        
        return {
            "status": "success",
            "tool": ToolInfo(
                tool_id=tool_id,
                name=tool_config["name"],
                type=tool_config["type"],
                description=tool_config["description"],
                parameters=tool_config["parameters"],
                priority=tool_config["priority"]
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tool info error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取工具信息失败: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    AI Copilot健康检查
    """
    return {
        "status": "healthy",
        "service": "AI Copilot",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/stats")
async def get_copilot_stats(
    api: AICopilotAPI = Depends(get_ai_copilot_api)
):
    """
    获取AI Copilot使用统计
    """
    try:
        # 这里可以从数据库获取统计信息
        stats = {
            "total_tools": len(api.tool_server.tools),
            "active_sessions": 0,  # 从缓存或数据库获取
            "total_conversations": 0,  # 从数据库获取
            "most_used_tools": [],  # 从数据库获取
            "average_response_time": 0.0  # 从数据库获取
        }
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

# 后台任务函数
async def log_conversation(
    user_id: str,
    session_id: str,
    user_message: str,
    response: Dict[str, Any]
):
    """记录对话日志"""
    try:
        # 这里可以将对话记录保存到数据库
        conversation_log = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到数据库的逻辑
        logger.info(f"Conversation logged: {conversation_log}")
        
    except Exception as e:
        logger.error(f"Failed to log conversation: {str(e)}")

async def log_tool_execution(
    user_id: str,
    session_id: str,
    tool_id: str,
    response: Dict[str, Any]
):
    """记录工具执行日志"""
    try:
        # 这里可以将工具执行记录保存到数据库
        execution_log = {
            "user_id": user_id,
            "session_id": session_id,
            "tool_id": tool_id,
            "execution_result": response,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到数据库的逻辑
        logger.info(f"Tool execution logged: {execution_log}")
        
    except Exception as e:
        logger.error(f"Failed to log tool execution: {str(e)}")

# 错误处理
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return {
        "status": "error",
        "error_code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.now().isoformat()
    }

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "status": "error",
        "error_code": 500,
        "message": "内部服务器错误",
        "timestamp": datetime.now().isoformat()
    }

