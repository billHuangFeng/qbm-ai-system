-- ============================================================
-- Phase 2: AI复盘闭环服务 - 数据库表结构
-- 文件名: 17_ai_retrospective.sql
-- 描述: 复盘会话、数据、洞察和建议相关表
-- 创建时间: 2025年1月
-- ============================================================

-- ============================================================
-- 1. 复盘会话表 (retrospective_sessions)
-- 用途: 存储复盘会话的基本信息
-- ============================================================
CREATE TABLE IF NOT EXISTS retrospective_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 会话基本信息
    session_name VARCHAR(255) NOT NULL,
    session_type VARCHAR(50) NOT NULL, -- 'decision', 'project', 'quarterly', 'annual'
    session_description TEXT,
    
    -- 关联信息
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    strategic_objective_id UUID REFERENCES strategic_objectives(objective_id),
    okr_id UUID REFERENCES okrs(id),
    
    -- 会话状态
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'archived'
    
    -- 时间信息
    period_start DATE,
    period_end DATE,
    
    -- 元数据
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_type ON retrospective_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_status ON retrospective_sessions(status);
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_decision ON retrospective_sessions(decision_id) WHERE decision_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_objective ON retrospective_sessions(strategic_objective_id) WHERE strategic_objective_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_okr ON retrospective_sessions(okr_id) WHERE okr_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_retrospective_sessions_period ON retrospective_sessions(period_start, period_end);

-- ============================================================
-- 2. 复盘数据表 (retrospective_data)
-- 用途: 存储收集的复盘相关数据
-- ============================================================
CREATE TABLE IF NOT EXISTS retrospective_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联会话
    session_id UUID NOT NULL REFERENCES retrospective_sessions(id) ON DELETE CASCADE,
    
    -- 数据类型和内容
    data_type VARCHAR(50) NOT NULL, -- 'decision_outcome', 'metric_change', 'anomaly', 'user_feedback', 'event'
    data_source VARCHAR(100), -- 数据来源
    data_content JSONB NOT NULL, -- 实际数据内容
    
    -- 数据质量
    data_quality_score DECIMAL(3,2), -- 数据质量评分 (0-1)
    is_validated BOOLEAN DEFAULT FALSE,
    
    -- 时间信息
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_timestamp TIMESTAMP WITH TIME ZONE, -- 事件发生时间
    
    -- 元数据
    collected_by VARCHAR(255),
    metadata JSONB
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_retrospective_data_session ON retrospective_data(session_id);
CREATE INDEX IF NOT EXISTS idx_retrospective_data_type ON retrospective_data(data_type);
CREATE INDEX IF NOT EXISTS idx_retrospective_data_collected ON retrospective_data(collected_at);
CREATE INDEX IF NOT EXISTS idx_retrospective_data_quality ON retrospective_data(data_quality_score) WHERE data_quality_score IS NOT NULL;

-- ============================================================
-- 3. 复盘洞察表 (retrospective_insights)
-- 用途: 存储AI生成的复盘洞察
-- ============================================================
CREATE TABLE IF NOT EXISTS retrospective_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联会话
    session_id UUID NOT NULL REFERENCES retrospective_sessions(id) ON DELETE CASCADE,
    
    -- 洞察信息
    insight_type VARCHAR(50) NOT NULL, -- 'root_cause', 'pattern', 'success_factor', 'failure_reason', 'trend'
    insight_title VARCHAR(255),
    insight_content TEXT NOT NULL,
    
    -- AI增强字段
    confidence_score DECIMAL(3,2), -- 置信度 (0-1)
    ai_model_used VARCHAR(100), -- 使用的AI模型
    ai_analysis_details JSONB, -- AI分析的详细信息
    
    -- 关联数据
    related_data_ids UUID[], -- 关联的retrospective_data IDs
    
    -- 重要性评分
    importance_score DECIMAL(3,2), -- 重要性评分 (0-1)
    
    -- 时间信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 元数据
    created_by VARCHAR(255) DEFAULT 'ai_system'
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_retrospective_insights_session ON retrospective_insights(session_id);
CREATE INDEX IF NOT EXISTS idx_retrospective_insights_type ON retrospective_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_retrospective_insights_confidence ON retrospective_insights(confidence_score) WHERE confidence_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_retrospective_insights_importance ON retrospective_insights(importance_score) WHERE importance_score IS NOT NULL;

-- ============================================================
-- 4. 复盘建议表 (retrospective_recommendations)
-- 用途: 存储基于复盘生成的改进建议
-- ============================================================
CREATE TABLE IF NOT EXISTS retrospective_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联会话
    session_id UUID NOT NULL REFERENCES retrospective_sessions(id) ON DELETE CASCADE,
    
    -- 关联洞察
    insight_id UUID REFERENCES retrospective_insights(id),
    
    -- 建议信息
    recommendation_type VARCHAR(50) NOT NULL, -- 'best_practice', 'process_optimization', 'risk_alert', 'learning_opportunity'
    recommendation_title VARCHAR(255),
    recommendation_content TEXT NOT NULL,
    
    -- 优先级和状态
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'implemented'
    
    -- AI增强字段
    ai_generated BOOLEAN DEFAULT TRUE,
    expected_impact VARCHAR(50), -- 'low', 'medium', 'high'
    implementation_difficulty VARCHAR(50), -- 'easy', 'medium', 'hard'
    estimated_effort INTEGER, -- 预计工作量（小时）
    
    -- 关联建议
    related_recommendations UUID[], -- 相关建议IDs
    
    -- 实施信息
    implemented_at TIMESTAMP WITH TIME ZONE,
    implemented_by VARCHAR(255),
    implementation_notes TEXT,
    
    -- 效果评估
    effectiveness_score DECIMAL(3,2), -- 效果评分 (0-1)
    feedback TEXT,
    
    -- 时间信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 元数据
    created_by VARCHAR(255) DEFAULT 'ai_system',
    metadata JSONB
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_retrospective_recommendations_session ON retrospective_recommendations(session_id);
CREATE INDEX IF NOT EXISTS idx_retrospective_recommendations_type ON retrospective_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_retrospective_recommendations_priority ON retrospective_recommendations(priority);
CREATE INDEX IF NOT EXISTS idx_retrospective_recommendations_status ON retrospective_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_retrospective_recommendations_insight ON retrospective_recommendations(insight_id) WHERE insight_id IS NOT NULL;

-- ============================================================
-- 注释说明
-- ============================================================
COMMENT ON TABLE retrospective_sessions IS '复盘会话表：存储复盘会话的基本信息';
COMMENT ON TABLE retrospective_data IS '复盘数据表：存储收集的复盘相关数据，包括决策结果、指标变化、异常事件等';
COMMENT ON TABLE retrospective_insights IS '复盘洞察表：存储AI生成的复盘洞察，包括根因分析、模式识别、成功因素等';
COMMENT ON TABLE retrospective_recommendations IS '复盘建议表：存储基于复盘生成的改进建议，包括最佳实践、流程优化、风险预警等';

