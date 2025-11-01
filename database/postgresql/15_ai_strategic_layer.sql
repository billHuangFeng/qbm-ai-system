-- ============================================================
-- AI增强战略层数据表设计
-- 文件: 15_ai_strategic_layer.sql
-- 说明: 包含使命愿景、北极星指标、OKR等战略层核心表
-- 创建日期: 2025-01-26
-- ============================================================

-- ============================================================
-- 1. 战略目标表 (strategic_objectives)
-- 用途: 存储使命、愿景、战略目标等最高层决策内容
-- AI增强: 支持协同效应分析、阈值识别
-- ============================================================
CREATE TABLE strategic_objectives (
    objective_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objective_name VARCHAR(200) NOT NULL,
    objective_type VARCHAR(50) NOT NULL, -- 'mission', 'vision', 'strategic_goal', 'value'
    objective_content TEXT NOT NULL,
    objective_description TEXT,
    
    -- 层级关系
    parent_objective_id UUID REFERENCES strategic_objectives(objective_id),
    hierarchy_level INT DEFAULT 1, -- L1=战略层
    
    -- 优先级和状态
    priority_level INT DEFAULT 1, -- 1-10，数字越大优先级越高
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'cancelled', 'archived'
    
    -- 时间管理
    target_date DATE,
    start_date DATE,
    completion_date DATE,
    
    -- AI增强字段
    synergy_score DECIMAL(5,4), -- AI协同效应分析得分 (0-1)
    synergy_analysis JSONB, -- 与其他目标的协同效应分析结果
    threshold_indicators JSONB, -- AI识别出的关键阈值指标
    ai_recommendations JSONB, -- AI推荐和优化建议
    
    -- 关联决策
    related_decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    
    -- 元数据
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_strategic_objectives_type ON strategic_objectives(objective_type);
CREATE INDEX idx_strategic_objectives_status ON strategic_objectives(status);
CREATE INDEX idx_strategic_objectives_parent ON strategic_objectives(parent_objective_id);
CREATE INDEX idx_strategic_objectives_hierarchy ON strategic_objectives(hierarchy_level);
CREATE INDEX idx_strategic_objectives_synergy ON strategic_objectives(synergy_score) WHERE synergy_score IS NOT NULL;

-- ============================================================
-- 2. 北极星指标表 (north_star_metrics)
-- 用途: 存储北极星指标，这是衡量战略目标的关键指标
-- AI增强: AI权重优化、趋势预测
-- ============================================================
CREATE TABLE north_star_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(200) NOT NULL,
    metric_description TEXT,
    metric_code VARCHAR(100) UNIQUE, -- 指标编码，如 'NSM_001'
    
    -- 关联战略目标
    strategic_objective_id UUID REFERENCES strategic_objectives(objective_id),
    
    -- 指标定义
    metric_type VARCHAR(50), -- 'revenue', 'growth', 'engagement', 'retention', 'custom'
    unit VARCHAR(50), -- 'count', 'percentage', 'currency', 'ratio'
    calculation_formula TEXT, -- 计算公式
    data_source VARCHAR(200), -- 数据来源
    
    -- 目标值管理
    target_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    baseline_value DECIMAL(15,2), -- 基线值
    
    -- 时间管理
    measurement_frequency VARCHAR(20) DEFAULT 'monthly', -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    target_date DATE,
    start_date DATE,
    
    -- AI增强字段
    ai_weight DECIMAL(5,4), -- AI动态权重 (0-1)
    ai_weight_history JSONB, -- 权重变化历史
    ai_trend_prediction JSONB, -- AI趋势预测结果 (ARIMA模型)
    ai_recommendation_priority INT DEFAULT 5, -- AI推荐优先级 (1-10)
    ai_insights JSONB, -- AI洞察和建议
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'deprecated', 'archived'
    is_primary BOOLEAN DEFAULT false, -- 是否为主要北极星指标
    
    -- 元数据
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_north_star_metrics_objective ON north_star_metrics(strategic_objective_id);
CREATE INDEX idx_north_star_metrics_code ON north_star_metrics(metric_code);
CREATE INDEX idx_north_star_metrics_status ON north_star_metrics(status);
CREATE INDEX idx_north_star_metrics_primary ON north_star_metrics(is_primary) WHERE is_primary = true;
CREATE INDEX idx_north_star_metrics_weight ON north_star_metrics(ai_weight);

-- ============================================================
-- 3. OKR目标表 (okr_objectives)
-- 用途: 存储OKR目标，连接战略目标和执行
-- AI增强: AI达成概率预测、最佳实践推荐
-- ============================================================
CREATE TABLE okr_objectives (
    okr_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    okr_name VARCHAR(200) NOT NULL,
    okr_description TEXT,
    okr_code VARCHAR(100) UNIQUE, -- OKR编码，如 'OKR_2025_Q1_001'
    
    -- 层级关系
    strategic_objective_id UUID REFERENCES strategic_objectives(objective_id),
    parent_okr_id UUID REFERENCES okr_objectives(okr_id), -- 支持OKR嵌套
    
    -- 时间周期
    period_type VARCHAR(20) NOT NULL, -- 'quarterly', 'annual', 'custom'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- 目标定义
    objective_statement TEXT NOT NULL, -- 目标描述
    
    -- AI增强字段
    ai_achievement_probability DECIMAL(5,4), -- AI预测达成概率 (0-1)
    ai_achievement_prediction JSONB, -- AI达成概率预测详情 (XGBoost模型)
    ai_best_practices JSONB, -- AI推荐的最佳实践 (来自企业记忆系统)
    ai_risk_factors JSONB, -- AI识别的风险因素
    ai_recommendations JSONB, -- AI优化建议
    
    -- 进度跟踪
    current_progress DECIMAL(5,2) DEFAULT 0, -- 当前进度 (0-100)
    expected_progress DECIMAL(5,2), -- 预期进度
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'active', 'completed', 'failed', 'cancelled'
    
    -- 负责人
    owner_id VARCHAR(100), -- 负责人ID
    owner_name VARCHAR(200), -- 负责人名称
    
    -- 元数据
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_okr_objectives_strategic ON okr_objectives(strategic_objective_id);
CREATE INDEX idx_okr_objectives_parent ON okr_objectives(parent_okr_id);
CREATE INDEX idx_okr_objectives_code ON okr_objectives(okr_code);
CREATE INDEX idx_okr_objectives_period ON okr_objectives(period_start, period_end);
CREATE INDEX idx_okr_objectives_status ON okr_objectives(status);
CREATE INDEX idx_okr_objectives_probability ON okr_objectives(ai_achievement_probability) WHERE ai_achievement_probability IS NOT NULL;

-- ============================================================
-- 4. OKR关键结果表 (okr_key_results)
-- 用途: 存储OKR的关键结果(KR)，量化OKR目标
-- AI增强: 智能阈值分析、关键指标识别
-- ============================================================
CREATE TABLE okr_key_results (
    kr_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kr_name VARCHAR(200) NOT NULL,
    kr_description TEXT,
    kr_code VARCHAR(100), -- KR编码
    
    -- 关联OKR
    okr_id UUID NOT NULL REFERENCES okr_objectives(okr_id),
    
    -- 关键结果定义
    kr_statement TEXT NOT NULL, -- 关键结果描述
    kr_type VARCHAR(50), -- 'metric', 'milestone', 'deliverable'
    metric_name VARCHAR(200), -- 如果类型是metric，指定指标名称
    
    -- 目标值
    target_value DECIMAL(15,2), -- 目标值
    current_value DECIMAL(15,2), -- 当前值
    baseline_value DECIMAL(15,2), -- 基线值
    unit VARCHAR(50), -- 单位
    
    -- AI增强字段
    ai_threshold_analysis JSONB, -- AI阈值分析结果 (ThresholdAnalysis)
    ai_key_indicators JSONB, -- AI识别的关键指标
    ai_achievement_probability DECIMAL(5,4), -- AI预测达成概率
    ai_insights JSONB, -- AI洞察
    
    -- 权重和优先级
    weight DECIMAL(5,4) DEFAULT 1.0, -- 在OKR中的权重
    priority INT DEFAULT 5, -- 优先级 (1-10)
    
    -- 进度跟踪
    current_progress DECIMAL(5,2) DEFAULT 0, -- 当前进度 (0-100)
    status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'at_risk', 'failed'
    
    -- 负责人
    owner_id VARCHAR(100),
    owner_name VARCHAR(200),
    
    -- 时间管理
    due_date DATE,
    completed_date DATE,
    
    -- 元数据
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_okr_key_results_okr ON okr_key_results(okr_id);
CREATE INDEX idx_okr_key_results_code ON okr_key_results(kr_code);
CREATE INDEX idx_okr_key_results_status ON okr_key_results(status);
CREATE INDEX idx_okr_key_results_progress ON okr_key_results(current_progress);
CREATE INDEX idx_okr_key_results_probability ON okr_key_results(ai_achievement_probability) WHERE ai_achievement_probability IS NOT NULL;

-- ============================================================
-- 5. 战略目标关联表 (strategic_objective_links)
-- 用途: 记录战略目标之间的关联关系，用于协同效应分析
-- ============================================================
CREATE TABLE strategic_objective_links (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_objective_id UUID NOT NULL REFERENCES strategic_objectives(objective_id),
    target_objective_id UUID NOT NULL REFERENCES strategic_objectives(objective_id),
    
    -- 关联类型
    link_type VARCHAR(50) NOT NULL, -- 'supports', 'conflicts', 'depends', 'synergizes'
    relationship_strength DECIMAL(5,4) DEFAULT 0.5, -- 关系强度 (0-1)
    
    -- AI增强字段
    ai_synergy_score DECIMAL(5,4), -- AI计算的协同效应得分
    ai_analysis JSONB, -- AI关联分析结果
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 避免重复关联
    UNIQUE(source_objective_id, target_objective_id)
);

-- 索引
CREATE INDEX idx_strategic_links_source ON strategic_objective_links(source_objective_id);
CREATE INDEX idx_strategic_links_target ON strategic_objective_links(target_objective_id);
CREATE INDEX idx_strategic_links_type ON strategic_objective_links(link_type);
CREATE INDEX idx_strategic_links_synergy ON strategic_objective_links(ai_synergy_score) WHERE ai_synergy_score IS NOT NULL;

-- ============================================================
-- 6. 北极星指标历史表 (north_star_metric_history)
-- 用途: 存储北极星指标的历史值，用于趋势分析和预测
-- ============================================================
CREATE TABLE north_star_metric_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_id UUID NOT NULL REFERENCES north_star_metrics(metric_id),
    
    -- 时间和数值
    measurement_date DATE NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    
    -- 上下文信息
    measurement_period VARCHAR(20), -- 'daily', 'weekly', 'monthly', etc.
    context_data JSONB, -- 上下文数据
    
    -- AI增强字段
    ai_trend_analysis JSONB, -- AI趋势分析
    ai_anomaly_detected BOOLEAN DEFAULT false, -- 是否检测到异常
    ai_prediction JSONB, -- AI预测值
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 确保每个指标每天只有一个记录
    UNIQUE(metric_id, measurement_date)
);

-- 索引
CREATE INDEX idx_north_star_history_metric ON north_star_metric_history(metric_id);
CREATE INDEX idx_north_star_history_date ON north_star_metric_history(measurement_date);
CREATE INDEX idx_north_star_history_anomaly ON north_star_metric_history(ai_anomaly_detected) WHERE ai_anomaly_detected = true;

-- ============================================================
-- 7. OKR进度跟踪表 (okr_progress_tracking)
-- 用途: 跟踪OKR和KR的进度变化历史
-- ============================================================
CREATE TABLE okr_progress_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    okr_id UUID REFERENCES okr_objectives(okr_id),
    kr_id UUID REFERENCES okr_key_results(kr_id),
    
    -- 跟踪时间
    tracking_date DATE NOT NULL,
    tracking_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 进度数据
    progress_value DECIMAL(5,2) NOT NULL, -- 进度值 (0-100)
    target_value DECIMAL(15,2), -- 目标值
    actual_value DECIMAL(15,2), -- 实际值
    
    -- 变化信息
    progress_change DECIMAL(5,2), -- 相比上次的变化量
    change_rate DECIMAL(5,4), -- 变化率
    
    -- AI增强字段
    ai_predicted_progress DECIMAL(5,2), -- AI预测的进度
    ai_variance DECIMAL(5,2), -- 实际值与预测值的差异
    ai_at_risk BOOLEAN DEFAULT false, -- AI判断是否处于风险状态
    
    -- 备注
    notes TEXT,
    updated_by VARCHAR(100),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_okr_tracking_okr ON okr_progress_tracking(okr_id, tracking_date);
CREATE INDEX idx_okr_tracking_kr ON okr_progress_tracking(kr_id, tracking_date);
CREATE INDEX idx_okr_tracking_date ON okr_progress_tracking(tracking_date);
CREATE INDEX idx_okr_tracking_risk ON okr_progress_tracking(ai_at_risk) WHERE ai_at_risk = true;

-- ============================================================
-- 注释说明
-- ============================================================
COMMENT ON TABLE strategic_objectives IS '战略目标表：存储使命、愿景、战略目标等最高层决策内容，支持AI协同效应分析和阈值识别';
COMMENT ON TABLE north_star_metrics IS '北极星指标表：存储关键战略指标，支持AI权重优化和趋势预测';
COMMENT ON TABLE okr_objectives IS 'OKR目标表：存储OKR目标，支持AI达成概率预测和最佳实践推荐';
COMMENT ON TABLE okr_key_results IS 'OKR关键结果表：存储KR，支持AI阈值分析和关键指标识别';
COMMENT ON TABLE strategic_objective_links IS '战略目标关联表：记录战略目标之间的关联关系，用于协同效应分析';
COMMENT ON TABLE north_star_metric_history IS '北极星指标历史表：存储指标历史值，用于趋势分析和预测';
COMMENT ON TABLE okr_progress_tracking IS 'OKR进度跟踪表：跟踪OKR和KR的进度变化历史';

COMMENT ON COLUMN strategic_objectives.synergy_score IS 'AI计算的协同效应得分，基于SynergyAnalysis算法';
COMMENT ON COLUMN strategic_objectives.synergy_analysis IS '协同效应分析结果JSON，包含与其他目标的关系分析';
COMMENT ON COLUMN strategic_objectives.threshold_indicators IS 'AI识别出的关键阈值指标，基于ThresholdAnalysis算法';
COMMENT ON COLUMN north_star_metrics.ai_weight IS 'AI动态权重，基于DynamicWeights算法优化';
COMMENT ON COLUMN north_star_metrics.ai_trend_prediction IS 'AI趋势预测结果，基于ARIMAModel或VARModel';
COMMENT ON COLUMN okr_objectives.ai_achievement_probability IS 'AI预测的达成概率，基于XGBoost模型';
COMMENT ON COLUMN okr_objectives.ai_best_practices IS 'AI推荐的最佳实践，来自企业记忆系统';
COMMENT ON COLUMN okr_key_results.ai_threshold_analysis IS 'AI阈值分析结果，基于ThresholdAnalysis算法';


