"""
API路由配置
"""

import os
from fastapi import APIRouter
from .endpoints import (
    auth,
    ai_strategic_layer,
    ai_planning_loop,
    ai_retrospective,
    ai_consistency,
    ai_influence,
    marginal_analysis,
    ingestion,
    expert_knowledge,
    learning,
    attribution,
    data_enhancement,
)

# 创建主API路由器
api_router = APIRouter()

ENABLE_AUTH = os.getenv("ENABLE_AUTH", "1") == "1"
ENABLE_AI = os.getenv("ENABLE_AI", "1") == "1"
ENABLE_MARGINAL = os.getenv("ENABLE_MARGINAL", "1") == "1"
ENABLE_INGESTION = os.getenv("ENABLE_INGESTION", "1") == "1"
ENABLE_EXPERT_KNOWLEDGE = os.getenv("ENABLE_EXPERT_KNOWLEDGE", "1") == "1"

# 接回认证端点
if ENABLE_AUTH:
    api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

if ENABLE_AI:
    # AI增强战略层相关路由
    api_router.include_router(ai_strategic_layer.router, prefix="", tags=["AI战略层"])

if ENABLE_AI:
    # AI增强制定闭环相关路由
    api_router.include_router(ai_planning_loop.router, prefix="", tags=["AI制定闭环"])

if ENABLE_AI:
    # AI复盘闭环相关路由
    api_router.include_router(ai_retrospective.router, prefix="", tags=["AI复盘闭环"])

if ENABLE_AI:
    # AI一致性引擎相关路由
    api_router.include_router(ai_consistency.router, prefix="", tags=["AI一致性引擎"])

if ENABLE_AI:
    # AI影响传播引擎相关路由
    api_router.include_router(ai_influence.router, prefix="", tags=["AI影响传播引擎"])

if ENABLE_MARGINAL:
    # 边际分析只读Mock路由
    api_router.include_router(
        marginal_analysis.router, prefix="/marginal", tags=["边际分析（Mock）"]
    )

if ENABLE_INGESTION:
    # 数据采集/编排 Mock 路由
    api_router.include_router(
        ingestion.router, prefix="/ingestion", tags=["数据采集（Mock）"]
    )

if ENABLE_EXPERT_KNOWLEDGE:
    # 专家知识库路由
    api_router.include_router(expert_knowledge.router, prefix="", tags=["专家知识库"])
    api_router.include_router(learning.router, prefix="", tags=["学习模块"])

# 归因分析路由（始终启用）
api_router.include_router(attribution.router, prefix="", tags=["归因分析"])

# 数据增强路由（第3阶段）
ENABLE_DATA_ENHANCEMENT = os.getenv("ENABLE_DATA_ENHANCEMENT", "1") == "1"
if ENABLE_DATA_ENHANCEMENT:
    api_router.include_router(
        data_enhancement.router, prefix="/api/v1", tags=["数据增强"]
    )
