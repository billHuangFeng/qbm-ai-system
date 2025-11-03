"""
BMOS企业记忆API端点 - 增强版
提供知识提取、经验积累和智能推荐功能
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime
import asyncio
import pandas as pd

from ..services.enhanced_enterprise_memory import (
    EnterpriseMemoryService,
    KnowledgePattern,
    BusinessInsight,
    Experience,
    Recommendation,
    enterprise_memory_service
)
from ..services.enhanced_data_import import data_import_service
from ..api.dependencies import get_current_user
from ..models.base import User

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/enterprise-memory", tags=["企业记忆"])

@router.post("/extract-patterns")
async def extract_patterns_from_data(
    data_file: str,
    target_column: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    从数据中提取知识模式
    
    - **data_file**: 数据文件名
    - **target_column**: 目标列名（可选）
    - **context**: 上下文信息（可选）
    - **current_user**: 当前用户
    
    返回提取的知识模式
    """
    try:
        logger.info(f"用户 {current_user.username} 开始提取知识模式: {data_file}")
        
        # 获取数据文件
        file_path = data_import_service.upload_dir / data_file
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="数据文件不存在")
        
        # 解析数据
        df = await data_import_service.parse_file(str(file_path))
        
        # 提取模式
        patterns = await enterprise_memory_service.extract_patterns_from_data(
            df, target_column, context
        )
        
        logger.info(f"知识模式提取完成: {len(patterns)} 个模式")
        
        return {
            "message": "知识模式提取完成",
            "total_patterns": len(patterns),
            "patterns": [pattern.dict() for pattern in patterns],
            "extracted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"知识模式提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"知识模式提取失败: {str(e)}")

@router.post("/generate-insights")
async def generate_business_insights(
    pattern_ids: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    生成业务洞察
    
    - **pattern_ids**: 模式ID列表（可选，为空则使用所有模式）
    - **context**: 上下文信息（可选）
    - **current_user**: 当前用户
    
    返回生成的业务洞察
    """
    try:
        logger.info(f"用户 {current_user.username} 开始生成业务洞察")
        
        # 获取模式
        if pattern_ids:
            patterns = []
            for pattern_id in pattern_ids:
                pattern = await enterprise_memory_service.get_patterns()
                pattern = next((p for p in pattern if p.pattern_id == pattern_id), None)
                if pattern:
                    patterns.append(pattern)
        else:
            patterns = await enterprise_memory_service.get_patterns()
        
        # 生成洞察
        insights = await enterprise_memory_service.generate_business_insights(
            patterns, context
        )
        
        logger.info(f"业务洞察生成完成: {len(insights)} 个洞察")
        
        return {
            "message": "业务洞察生成完成",
            "total_insights": len(insights),
            "insights": [insight.dict() for insight in insights],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"业务洞察生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"业务洞察生成失败: {str(e)}")

@router.post("/generate-recommendations")
async def generate_intelligent_recommendations(
    insight_ids: Optional[List[str]] = None,
    current_context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    生成智能推荐
    
    - **insight_ids**: 洞察ID列表（可选，为空则使用所有洞察）
    - **current_context**: 当前上下文（可选）
    - **current_user**: 当前用户
    
    返回生成的智能推荐
    """
    try:
        logger.info(f"用户 {current_user.username} 开始生成智能推荐")
        
        # 获取洞察
        if insight_ids:
            insights = []
            for insight_id in insight_ids:
                insight = await enterprise_memory_service.get_insights()
                insight = next((i for i in insight if i.insight_id == insight_id), None)
                if insight:
                    insights.append(insight)
        else:
            insights = await enterprise_memory_service.get_insights()
        
        # 生成推荐
        recommendations = await enterprise_memory_service.generate_recommendations(
            insights, current_context
        )
        
        logger.info(f"智能推荐生成完成: {len(recommendations)} 个推荐")
        
        return {
            "message": "智能推荐生成完成",
            "total_recommendations": len(recommendations),
            "recommendations": [rec.dict() for rec in recommendations],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"智能推荐生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"智能推荐生成失败: {str(e)}")

@router.get("/patterns")
async def get_knowledge_patterns(
    pattern_type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取知识模式
    
    - **pattern_type**: 模式类型（可选）
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回知识模式列表
    """
    try:
        logger.info(f"用户 {current_user.username} 查询知识模式")
        
        patterns = await enterprise_memory_service.get_patterns(pattern_type)
        
        # 限制返回数量
        if limit > 0:
            patterns = patterns[:limit]
        
        return {
            "total_patterns": len(patterns),
            "patterns": [pattern.dict() for pattern in patterns],
            "pattern_type": pattern_type
        }
        
    except Exception as e:
        logger.error(f"获取知识模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取知识模式失败: {str(e)}")

@router.get("/insights")
async def get_business_insights(
    category: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取业务洞察
    
    - **category**: 洞察类别（可选）
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回业务洞察列表
    """
    try:
        logger.info(f"用户 {current_user.username} 查询业务洞察")
        
        insights = await enterprise_memory_service.get_insights(category)
        
        # 限制返回数量
        if limit > 0:
            insights = insights[:limit]
        
        return {
            "total_insights": len(insights),
            "insights": [insight.dict() for insight in insights],
            "category": category
        }
        
    except Exception as e:
        logger.error(f"获取业务洞察失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取业务洞察失败: {str(e)}")

@router.get("/recommendations")
async def get_intelligent_recommendations(
    priority: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取智能推荐
    
    - **priority**: 优先级（可选）
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回智能推荐列表
    """
    try:
        logger.info(f"用户 {current_user.username} 查询智能推荐")
        
        recommendations = await enterprise_memory_service.get_recommendations(priority)
        
        # 限制返回数量
        if limit > 0:
            recommendations = recommendations[:limit]
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": [rec.dict() for rec in recommendations],
            "priority": priority
        }
        
    except Exception as e:
        logger.error(f"获取智能推荐失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取智能推荐失败: {str(e)}")

@router.post("/search-patterns")
async def search_similar_patterns(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """
    搜索相似模式
    
    - **query**: 搜索查询
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回相似模式列表
    """
    try:
        logger.info(f"用户 {current_user.username} 搜索相似模式: {query}")
        
        similar_patterns = await enterprise_memory_service.search_similar_patterns(
            query, limit
        )
        
        return {
            "query": query,
            "total_found": len(similar_patterns),
            "similar_patterns": [pattern.dict() for pattern in similar_patterns]
        }
        
    except Exception as e:
        logger.error(f"搜索相似模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索相似模式失败: {str(e)}")

@router.post("/add-experience")
async def add_business_experience(
    scenario: str,
    context: Dict[str, Any],
    actions_taken: List[str],
    results: Dict[str, Any],
    success: bool,
    lessons_learned: List[str],
    tags: List[str],
    current_user: User = Depends(get_current_user)
):
    """
    添加业务经验
    
    - **scenario**: 场景描述
    - **context**: 上下文信息
    - **actions_taken**: 采取的行动
    - **results**: 结果
    - **success**: 是否成功
    - **lessons_learned**: 经验教训
    - **tags**: 标签
    - **current_user**: 当前用户
    
    返回添加的经验记录
    """
    try:
        logger.info(f"用户 {current_user.username} 添加业务经验: {scenario}")
        
        experience = Experience(
            experience_id=enterprise_memory_service._generate_id(f"{scenario}_{datetime.now()}"),
            scenario=scenario,
            context=context,
            actions_taken=actions_taken,
            results=results,
            success=success,
            lessons_learned=lessons_learned,
            tags=tags,
            created_at=datetime.now()
        )
        
        # 保存经验
        await enterprise_memory_service.save_experience(experience)
        
        logger.info(f"业务经验添加完成: {experience.experience_id}")
        
        return {
            "message": "业务经验添加成功",
            "experience": experience.dict()
        }
        
    except Exception as e:
        logger.error(f"添加业务经验失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加业务经验失败: {str(e)}")

@router.get("/experiences")
async def get_business_experiences(
    success_only: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取业务经验
    
    - **success_only**: 只获取成功经验（可选）
    - **tags**: 标签过滤（可选）
    - **limit**: 返回数量限制
    - **current_user**: 当前用户
    
    返回业务经验列表
    """
    try:
        logger.info(f"用户 {current_user.username} 查询业务经验")
        
        experiences = await enterprise_memory_service.get_experiences()
        
        # 过滤
        if success_only is not None:
            experiences = [e for e in experiences if e.success == success_only]
        
        if tags:
            experiences = [e for e in experiences if any(tag in e.tags for tag in tags)]
        
        # 限制返回数量
        if limit > 0:
            experiences = experiences[:limit]
        
        return {
            "total_experiences": len(experiences),
            "experiences": [exp.dict() for exp in experiences]
        }
        
    except Exception as e:
        logger.error(f"获取业务经验失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取业务经验失败: {str(e)}")

@router.get("/stats")
async def get_memory_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    获取企业记忆统计信息
    
    - **current_user**: 当前用户
    
    返回统计信息
    """
    try:
        logger.info(f"用户 {current_user.username} 查询记忆统计")
        
        stats = await enterprise_memory_service.get_memory_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"获取记忆统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取记忆统计失败: {str(e)}")

@router.post("/demo-extract")
async def demo_pattern_extraction(
    current_user: User = Depends(get_current_user)
):
    """
    演示模式提取功能
    
    - **current_user**: 当前用户
    
    返回演示结果
    """
    try:
        logger.info(f"用户 {current_user.username} 开始演示模式提取")
        
        # 创建演示数据
        import numpy as np
        
        np.random.seed(42)
        n_samples = 300
        
        demo_data = pd.DataFrame({
            'sales': np.random.normal(1000, 200, n_samples),
            'marketing_spend': np.random.normal(100, 30, n_samples),
            'customer_satisfaction': np.random.normal(4.0, 0.5, n_samples),
            'profit_margin': np.random.normal(0.15, 0.05, n_samples),
            'success': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
        })
        
        # 提取模式
        patterns = await enterprise_memory_service.extract_patterns_from_data(
            demo_data, target_column="success"
        )
        
        # 生成洞察
        insights = await enterprise_memory_service.generate_business_insights(patterns)
        
        # 生成推荐
        recommendations = await enterprise_memory_service.generate_recommendations(insights)
        
        logger.info(f"演示模式提取完成")
        
        return {
            "message": "演示模式提取完成",
            "demo_data_info": {
                "rows": len(demo_data),
                "columns": list(demo_data.columns),
                "success_rate": demo_data["success"].mean()
            },
            "extracted_patterns": len(patterns),
            "generated_insights": len(insights),
            "generated_recommendations": len(recommendations),
            "patterns": [pattern.dict() for pattern in patterns[:3]],  # 只返回前3个
            "insights": [insight.dict() for insight in insights[:3]],  # 只返回前3个
            "recommendations": [rec.dict() for rec in recommendations[:3]]  # 只返回前3个
        }
        
    except Exception as e:
        logger.error(f"演示模式提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"演示模式提取失败: {str(e)}")

@router.get("/health")
async def health_check():
    """企业记忆服务健康检查"""
    try:
        # 检查记忆目录
        memory_dir_exists = enterprise_memory_service.memory_dir.exists()
        
        # 检查权限
        can_write = os.access(enterprise_memory_service.memory_dir, os.W_OK)
        
        # 获取统计信息
        stats = await enterprise_memory_service.get_memory_stats()
        
        return {
            "status": "healthy" if memory_dir_exists and can_write else "unhealthy",
            "memory_directory": str(enterprise_memory_service.memory_dir),
            "directory_exists": memory_dir_exists,
            "can_write": can_write,
            "total_patterns": stats.get("total_patterns", 0),
            "total_insights": stats.get("total_insights", 0),
            "total_recommendations": stats.get("total_recommendations", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


