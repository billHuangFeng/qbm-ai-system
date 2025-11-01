"""
BMOS系统 - AI制定闭环测试套件
测试AI增强制定闭环服务的功能，包括对齐检查、基线生成、需求分析等
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

# 导入被测试的模块
from src.services.ai_planning_loop.ai_alignment_checker import AIAlignmentChecker
from src.services.ai_planning_loop.ai_baseline_generator import AIBaselineGenerator
from src.services.ai_planning_loop.ai_requirement_analyzer import AIRequirementAnalyzer
from src.services.database_service import DatabaseService
from src.services.enhanced_enterprise_memory import EnterpriseMemoryService

# 测试数据
TEST_DECISION_ID = "test_decision_001"
TEST_BASELINE_ID = "test_baseline_001"
TEST_REQUIREMENT_ID = "test_requirement_001"

class TestAIAlignmentChecker:
    """决策对齐检查服务测试"""
    
    @pytest.fixture
    def mock_db_service(self):
        """模拟数据库服务"""
        db = AsyncMock(spec=DatabaseService)
        db.execute_insert = AsyncMock(return_value="mock_check_id")
        db.execute_query = AsyncMock(return_value=[])
        db.execute_one = AsyncMock(return_value=None)
        return db
    
    @pytest.fixture
    def mock_memory_service(self):
        """模拟企业记忆服务"""
        memory = AsyncMock(spec=EnterpriseMemoryService)
        memory.search_similar_patterns = AsyncMock(return_value=[])
        return memory
    
    @pytest.fixture
    def alignment_checker(self, mock_db_service, mock_memory_service):
        """创建对齐检查服务实例"""
        return AIAlignmentChecker(
            db_service=mock_db_service,
            memory_service=mock_memory_service
        )
    
    @pytest.mark.asyncio
    async def test_check_decision_alignment(self, alignment_checker, mock_db_service):
        """测试决策对齐检查"""
        # 模拟决策数据
        mock_db_service.execute_one.return_value = {
            "decision_id": TEST_DECISION_ID,
            "decision_name": "测试决策",
            "budget": 100000.0,
            "goals": [{"title": "目标1", "priority": 8}],
            "resources": {"human": 10, "budget": 100000}
        }
        
        mock_db_service.execute_query.return_value = []
        
        result = await alignment_checker.check_decision_alignment(
            decision_id=TEST_DECISION_ID,
            check_type="full_alignment"
        )
        
        assert result["success"] is True
        assert result["decision_id"] == TEST_DECISION_ID
        assert "alignment_status" in result
        assert "alignment_score" in result
        assert 0.0 <= result["alignment_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_predict_conflicts(self, alignment_checker, mock_db_service):
        """测试冲突预测"""
        # 模拟决策数据
        mock_db_service.execute_one.side_effect = [
            {
                "decision_id": TEST_DECISION_ID,
                "budget": 100000.0,
                "goals": [],
                "resources": {"human": 10}
            },
            {
                "decision_id": "related_001",
                "budget": 150000.0,
                "goals": [],
                "resources": {"human": 15}
            }
        ]
        
        mock_db_service.execute_query.return_value = [{"decision_id": "related_001"}]
        
        result = await alignment_checker._predict_conflicts(
            decision_data={"budget": 100000.0, "resources": {"human": 10}},
            related_decisions=[{"budget": 150000.0, "resources": {"human": 15}}]
        )
        
        assert "conflict_probability" in result
        assert 0.0 <= result["conflict_probability"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_goal_consistency(self, alignment_checker):
        """测试目标一致性分析"""
        result = await alignment_checker._analyze_goal_consistency(
            decision_data={"goals": [{"title": "目标1"}]},
            related_decisions=[{"goals": [{"title": "目标2"}]}]
        )
        
        assert "consistency_score" in result
        assert 0.0 <= result["consistency_score"] <= 1.0

class TestAIBaselineGenerator:
    """基线生成服务测试"""
    
    @pytest.fixture
    def mock_db_service(self):
        """模拟数据库服务"""
        db = AsyncMock(spec=DatabaseService)
        db.execute_insert = AsyncMock(return_value="baseline_123")
        db.execute_query = AsyncMock(return_value=[])
        db.execute_one = AsyncMock(return_value=None)
        return db
    
    @pytest.fixture
    def mock_memory_service(self):
        """模拟企业记忆服务"""
        memory = AsyncMock(spec=EnterpriseMemoryService)
        return memory
    
    @pytest.fixture
    def baseline_generator(self, mock_db_service, mock_memory_service):
        """创建基线生成服务实例"""
        return AIBaselineGenerator(
            db_service=mock_db_service,
            memory_service=mock_memory_service
        )
    
    @pytest.mark.asyncio
    async def test_generate_baseline(self, baseline_generator, mock_db_service):
        """测试生成基线"""
        # 模拟决策数据
        mock_db_service.execute_one.return_value = {
            "decision_id": TEST_DECISION_ID,
            "decision_name": "测试决策",
            "target_kpis": [{"name": "KPI1", "target_value": 100}],
            "budget_allocation": {"total": 100000},
            "key_results": [],
            "dependencies": [],
            "assumptions": []
        }
        
        mock_db_service.execute_query.return_value = []
        
        result = await baseline_generator.generate_baseline(
            decision_id=TEST_DECISION_ID,
            baseline_name="Q1基线",
            include_predictions=True
        )
        
        assert result["success"] is True
        assert result["baseline_id"] == "baseline_123"
        assert "baseline_data" in result
        assert "ai_confidence" in result
    
    @pytest.mark.asyncio
    async def test_predict_baseline_outcomes(self, baseline_generator):
        """测试预测基线结果"""
        # 模拟历史数据
        historical_data = [
            {"revenue": 100000 + i * 5000, "cost": 80000 + i * 4000}
            for i in range(15)
        ]
        
        result = await baseline_generator._predict_baseline_outcomes(
            decision_data={"target_kpis": [{"name": "revenue"}]},
            historical_data=historical_data,
            prediction_periods=4
        )
        
        assert "predicted_outcomes" in result or "method" in result

class TestAIRequirementAnalyzer:
    """需求分析服务测试"""
    
    @pytest.fixture
    def mock_db_service(self):
        """模拟数据库服务"""
        db = AsyncMock(spec=DatabaseService)
        db.execute_query = AsyncMock(return_value=[])
        db.execute_one = AsyncMock(return_value=None)
        return db
    
    @pytest.fixture
    def mock_memory_service(self):
        """模拟企业记忆服务"""
        memory = AsyncMock(spec=EnterpriseMemoryService)
        memory.search_similar_patterns = AsyncMock(return_value=[])
        return memory
    
    @pytest.fixture
    def requirement_analyzer(self, mock_db_service, mock_memory_service):
        """创建需求分析服务实例"""
        return AIRequirementAnalyzer(
            db_service=mock_db_service,
            memory_service=mock_memory_service
        )
    
    @pytest.mark.asyncio
    async def test_analyze_requirement_depth(self, requirement_analyzer, mock_db_service):
        """测试深度分析需求"""
        # 模拟需求数据
        mock_db_service.execute_one.return_value = {
            "requirement_id": TEST_REQUIREMENT_ID,
            "requirement_title": "测试需求",
            "requirement_description": "这是一个测试需求，需要10000预算，30天内完成",
            "requirement_type": "strategic",
            "priority_level": 8,
            "required_by_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        mock_db_service.execute_query.return_value = []
        
        result = await requirement_analyzer.analyze_requirement_depth(
            requirement_id=TEST_REQUIREMENT_ID,
            analysis_type="full"
        )
        
        assert result["success"] is True
        assert result["requirement_id"] == TEST_REQUIREMENT_ID
        assert "analysis_results" in result
    
    @pytest.mark.asyncio
    async def test_find_similar_requirements(self, requirement_analyzer, mock_db_service, mock_memory_service):
        """测试查找相似需求"""
        mock_db_service.execute_one.return_value = {
            "requirement_id": TEST_REQUIREMENT_ID,
            "requirement_type": "strategic",
            "requirement_title": "测试需求",
            "requirement_description": "需要增加预算"
        }
        
        mock_db_service.execute_query.return_value = [
            {
                "requirement_id": "similar_001",
                "requirement_title": "类似需求",
                "requirement_description": "也需要增加预算",
                "requirement_type": "strategic",
                "status": "approved",
                "ai_priority_score": 0.8
            }
        ]
        
        result = await requirement_analyzer._find_similar_requirements({
            "requirement_id": TEST_REQUIREMENT_ID,
            "requirement_type": "strategic",
            "requirement_title": "测试需求",
            "requirement_description": "需要增加预算"
        })
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_identify_critical_requirements(self, requirement_analyzer):
        """测试识别关键需求"""
        result = await requirement_analyzer._identify_critical_requirements({
            "requirement_title": "测试需求",
            "requirement_description": "需要100000预算，30%增长，在30天内完成",
            "priority_level": 9,
            "required_by_date": (datetime.now() + timedelta(days=7)).isoformat()
        })
        
        assert isinstance(result, list)
        assert len(result) > 0

class TestServiceIntegration:
    """服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_baseline_workflow(self):
        """测试端到端基线生成工作流"""
        # 创建模拟服务
        mock_db = AsyncMock(spec=DatabaseService)
        mock_memory = AsyncMock(spec=EnterpriseMemoryService)
        
        # 创建服务实例
        baseline_service = AIBaselineGenerator(
            db_service=mock_db,
            memory_service=mock_memory
        )
        
        # 模拟数据库操作
        mock_db.execute_one.return_value = {
            "decision_id": TEST_DECISION_ID,
            "target_kpis": [{"name": "revenue", "target_value": 1000000}],
            "budget_allocation": {"total": 500000}
        }
        mock_db.execute_query.return_value = []
        mock_db.execute_insert.return_value = "baseline_123"
        
        # 生成基线
        result = await baseline_service.generate_baseline(
            decision_id=TEST_DECISION_ID,
            baseline_name="测试基线",
            include_predictions=True
        )
        
        assert result["success"] is True
        assert result["baseline_id"] == "baseline_123"

# 运行测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

