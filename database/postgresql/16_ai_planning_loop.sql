-- ============================================================
-- AI增强制定闭环数据表设计
-- 文件: 16_ai_planning_loop.sql
-- 说明: 包含决策需求、决策基线、对齐检查、审批流程等制定闭环核心表
-- 创建日期: 2025-01-26
-- ============================================================

-- ============================================================
-- 1. 决策需求表 (decision_requirements)
-- 用途: 存储决策需求的申请和审批
-- AI增强: AI需求分析、历史模式识别
-- ============================================================
CREATE TABLE decision_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_code VARCHAR(100) UNIQUE, -- 需求编码，如 'REQ_2025_001'
    
    -- 需求基本信息
    requirement_title VARCHAR(200) NOT NULL,
    requirement_description TEXT NOT NULL,
    requirement_type VARCHAR(50) NOT NULL, -- 'strategic', 'tactical', 'operational', 'emergency'
    requirement_category VARCHAR(100), -- 'investment', 'resource', 'process', 'technology', etc.
    
    -- 关联关系
    parent_decision_id UUID REFERENCES hierarchical_decisions(decision_id), -- 必须关联父决策
    strategic_objective_id UUID REFERENCES strategic_objectives(objective_id), -- 关联的战略目标
    
    -- 需求提出人
    requester_id VARCHAR(100) NOT NULL,
    requester_name VARCHAR(200) NOT NULL,
    requester_department VARCHAR(100),
    
    -- AI增强字段
    ai_priority_score DECIMAL(5,4), -- AI计算的优先级得分 (0-1)
    ai_priority_analysis JSONB, -- AI优先级分析详情 (基于MLPModel)
    ai_similar_requirements JSONB, -- AI识别出的相似历史需求 (来自企业记忆系统)
    ai_best_practices JSONB, -- AI推荐的最佳实践 (来自企业记忆系统)
    ai_risk_assessment JSONB, -- AI风险评估
    
    -- 需求状态
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'submitted', 'approved', 'rejected', 'cancelled'
    priority_level INT DEFAULT 5, -- 人工设置的优先级 (1-10)
    
    -- 时间管理
    requested_date DATE DEFAULT CURRENT_DATE,
    required_by_date DATE, -- 需求截止日期
    approved_date DATE,
    rejected_date DATE,
    
    -- 审批信息
    approver_id VARCHAR(100),
    approver_name VARCHAR(200),
    approval_notes TEXT,
    rejection_reason TEXT,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_decision_requirements_parent ON decision_requirements(parent_decision_id);
CREATE INDEX idx_decision_requirements_strategic ON decision_requirements(strategic_objective_id);
CREATE INDEX idx_decision_requirements_code ON decision_requirements(requirement_code);
CREATE INDEX idx_decision_requirements_type ON decision_requirements(requirement_type);
CREATE INDEX idx_decision_requirements_status ON decision_requirements(status);
CREATE INDEX idx_decision_requirements_priority ON decision_requirements(ai_priority_score) WHERE ai_priority_score IS NOT NULL;
CREATE INDEX idx_decision_requirements_requester ON decision_requirements(requester_id);

-- ============================================================
-- 2. 决策基线表 (decision_baselines)
-- 用途: 存储决策的冻结快照，包含目标、预算、KR、依赖等
-- AI增强: AI预测基线、基线优化
-- ============================================================
CREATE TABLE decision_baselines (
    baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_name VARCHAR(200) NOT NULL,
    baseline_code VARCHAR(100) UNIQUE, -- 基线编码，如 'BL_2025_Q1_001'
    
    -- 关联决策
    decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    
    -- 基线版本
    baseline_version INT NOT NULL DEFAULT 1,
    is_current BOOLEAN DEFAULT true, -- 是否当前版本
    
    -- 基线内容 (JSONB存储完整的基线快照)
    baseline_data JSONB NOT NULL, -- 完整的决策快照数据
    
    -- 基线包含的核心内容（结构化存储，便于查询）
    target_kpis JSONB, -- 目标KPI列表
    budget_allocation JSONB, -- 预算分配
    key_results JSONB, -- 关键结果
    dependencies JSONB, -- 依赖关系
    assumptions JSONB, -- 假设条件
    
    -- AI增强字段
    ai_predicted_outcomes JSONB, -- AI预测的结果 (基于VARModel或LightGBM)
    ai_baseline_confidence DECIMAL(5,4), -- AI基线置信度 (0-1)
    ai_optimization_suggestions JSONB, -- AI基线优化建议
    ai_risk_factors JSONB, -- AI识别的风险因素
    
    -- 冻结信息
    frozen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    frozen_by VARCHAR(100) NOT NULL,
    frozen_reason TEXT, -- 冻结原因
    
    -- 基线状态
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'superseded', 'archived'
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_decision_baselines_decision ON decision_baselines(decision_id);
CREATE INDEX idx_decision_baselines_code ON decision_baselines(baseline_code);
CREATE INDEX idx_decision_baselines_current ON decision_baselines(is_current) WHERE is_current = true;
CREATE INDEX idx_decision_baselines_version ON decision_baselines(decision_id, baseline_version);
CREATE INDEX idx_decision_baselines_confidence ON decision_baselines(ai_baseline_confidence) WHERE ai_baseline_confidence IS NOT NULL;
-- GIN索引用于JSONB字段查询
CREATE INDEX idx_decision_baselines_data ON decision_baselines USING GIN(baseline_data);
CREATE INDEX idx_decision_baselines_target_kpis ON decision_baselines USING GIN(target_kpis);

-- ============================================================
-- 3. 决策对齐检查表 (decision_alignment_checks)
-- 用途: 存储决策对齐检查的结果，包括冲突检测、一致性验证等
-- AI增强: AI冲突预测、一致性评分、对齐建议
-- ============================================================
CREATE TABLE decision_alignment_checks (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_code VARCHAR(100) UNIQUE, -- 检查编码
    
    -- 关联决策
    decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    
    -- 检查类型
    check_type VARCHAR(50) NOT NULL, -- 'full_alignment', 'resource_conflict', 'goal_consistency', 'circular_dependency'
    
    -- 检查时间
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checked_by VARCHAR(100), -- 执行检查的用户或系统
    
    -- 检查结果
    alignment_status VARCHAR(20) NOT NULL, -- 'pass', 'warning', 'fail'
    alignment_score DECIMAL(5,4), -- 对齐得分 (0-1)
    
    -- AI增强字段
    ai_conflict_probability DECIMAL(5,4), -- AI预测的冲突概率 (基于RandomForest)
    ai_conflict_details JSONB, -- AI冲突详情分析
    ai_consistency_score DECIMAL(5,4), -- AI一致性得分 (基于MLPModel和SynergyAnalysis)
    ai_consistency_analysis JSONB, -- AI一致性分析结果
    ai_circular_dependencies JSONB, -- AI检测到的循环依赖
    ai_alignment_suggestions JSONB, -- AI对齐建议
    
    -- 检查详细信息
    conflicts_detected JSONB, -- 检测到的冲突列表
    consistency_issues JSONB, -- 一致性问题列表
    dependencies_found JSONB, -- 发现的依赖关系
    
    -- 检查报告
    check_report TEXT, -- 检查报告摘要
    detailed_report JSONB, -- 详细检查报告
    
    -- 处理状态
    resolution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'resolved', 'ignored'
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_alignment_checks_decision ON decision_alignment_checks(decision_id);
CREATE INDEX idx_alignment_checks_code ON decision_alignment_checks(check_code);
CREATE INDEX idx_alignment_checks_type ON decision_alignment_checks(check_type);
CREATE INDEX idx_alignment_checks_status ON decision_alignment_checks(alignment_status);
CREATE INDEX idx_alignment_checks_score ON decision_alignment_checks(alignment_score) WHERE alignment_score IS NOT NULL;
CREATE INDEX idx_alignment_checks_conflict_prob ON decision_alignment_checks(ai_conflict_probability) WHERE ai_conflict_probability IS NOT NULL;
CREATE INDEX idx_alignment_checks_resolution ON decision_alignment_checks(resolution_status);

-- ============================================================
-- 4. 决策审批流程表 (decision_approval_flow)
-- 用途: 存储决策的审批流程和审批记录
-- AI增强: AI风险评估、审批建议
-- ============================================================
CREATE TABLE decision_approval_flow (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联决策或需求
    decision_id UUID REFERENCES hierarchical_decisions(decision_id),
    requirement_id UUID REFERENCES decision_requirements(requirement_id),
    
    -- 审批流程定义
    approval_workflow JSONB NOT NULL, -- 审批流程定义 (审批节点、顺序等)
    current_step INT NOT NULL DEFAULT 1, -- 当前审批步骤
    total_steps INT NOT NULL, -- 总审批步骤数
    
    -- AI增强字段
    ai_risk_score DECIMAL(5,4), -- AI风险评估得分 (0-1)
    ai_risk_assessment JSONB, -- AI风险评估详情
    ai_approval_recommendation VARCHAR(20), -- 'approve', 'reject', 'request_changes'
    ai_recommendation_reason TEXT, -- AI推荐理由
    
    -- 审批状态
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'cancelled'
    
    -- 时间信息
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    
    -- 提交人
    submitted_by VARCHAR(100),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_approval_flow_decision ON decision_approval_flow(decision_id);
CREATE INDEX idx_approval_flow_requirement ON decision_approval_flow(requirement_id);
CREATE INDEX idx_approval_flow_status ON decision_approval_flow(status);
CREATE INDEX idx_approval_flow_risk_score ON decision_approval_flow(ai_risk_score) WHERE ai_risk_score IS NOT NULL;

-- ============================================================
-- 5. 审批记录表 (approval_records)
-- 用途: 存储每个审批步骤的详细记录
-- ============================================================
CREATE TABLE approval_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联审批流程
    approval_id UUID NOT NULL REFERENCES decision_approval_flow(approval_id),
    
    -- 审批步骤信息
    step_number INT NOT NULL, -- 步骤序号
    step_name VARCHAR(200), -- 步骤名称
    step_type VARCHAR(50), -- 'auto', 'manual', 'conditional'
    
    -- 审批人信息
    approver_id VARCHAR(100),
    approver_name VARCHAR(200),
    approver_role VARCHAR(100), -- 审批人角色
    
    -- 审批结果
    approval_action VARCHAR(20) NOT NULL, -- 'approve', 'reject', 'request_changes', 'delegate'
    approval_notes TEXT, -- 审批意见
    approval_conditions JSONB, -- 审批条件（如果有）
    
    -- 时间信息
    action_taken_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE, -- 审批截止时间
    
    -- 委托信息
    delegated_to VARCHAR(100), -- 如果委托给他人
    delegated_to_name VARCHAR(200),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_approval_records_approval ON approval_records(approval_id);
CREATE INDEX idx_approval_records_step ON approval_records(approval_id, step_number);
CREATE INDEX idx_approval_records_approver ON approval_records(approver_id);
CREATE INDEX idx_approval_records_action ON approval_records(approval_action);

-- ============================================================
-- 6. 资源需求表 (resource_requirements)
-- 用途: 存储决策所需的资源需求，用于冲突检测
-- ============================================================
CREATE TABLE resource_requirements (
    resource_req_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联决策
    decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    
    -- 资源信息
    resource_type VARCHAR(100) NOT NULL, -- 'budget', 'personnel', 'equipment', 'time', 'other'
    resource_category VARCHAR(100), -- 资源分类
    resource_name VARCHAR(200) NOT NULL, -- 资源名称
    
    -- 资源需求
    required_amount DECIMAL(15,2) NOT NULL, -- 需求数量
    required_unit VARCHAR(50), -- 单位
    available_amount DECIMAL(15,2), -- 可用数量
    
    -- 时间信息
    required_period_start DATE NOT NULL,
    required_period_end DATE NOT NULL,
    
    -- 优先级
    priority INT DEFAULT 5, -- 优先级 (1-10)
    
    -- AI增强字段（冲突检测相关）
    ai_conflict_detected BOOLEAN DEFAULT false, -- AI是否检测到冲突
    ai_conflicting_decisions JSONB, -- AI检测到的冲突决策列表
    ai_conflict_severity DECIMAL(5,4), -- AI冲突严重程度 (0-1)
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'allocated', 'rejected', 'cancelled'
    
    -- 分配信息
    allocated_amount DECIMAL(15,2),
    allocated_at TIMESTAMP WITH TIME ZONE,
    allocated_by VARCHAR(100),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_resource_requirements_decision ON resource_requirements(decision_id);
CREATE INDEX idx_resource_requirements_type ON resource_requirements(resource_type);
CREATE INDEX idx_resource_requirements_period ON resource_requirements(required_period_start, required_period_end);
CREATE INDEX idx_resource_requirements_conflict ON resource_requirements(ai_conflict_detected) WHERE ai_conflict_detected = true;
CREATE INDEX idx_resource_requirements_status ON resource_requirements(status);

-- ============================================================
-- 7. 目标一致性检查表 (goal_consistency_checks)
-- 用途: 存储目标一致性检查的详细结果
-- ============================================================
CREATE TABLE goal_consistency_checks (
    consistency_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联决策
    decision_id UUID NOT NULL REFERENCES hierarchical_decisions(decision_id),
    
    -- 检查的目标对
    source_goal_id UUID, -- 源目标（可以是decision_id或其他）
    target_goal_id UUID, -- 目标目标
    
    -- AI增强字段
    ai_consistency_score DECIMAL(5,4), -- AI一致性得分 (基于余弦相似度)
    ai_cosine_similarity DECIMAL(5,4), -- 目标向量余弦相似度
    ai_goal_vectors JSONB, -- AI生成的目标向量
    ai_analysis JSONB, -- AI一致性分析详情
    
    -- 一致性判断
    is_consistent BOOLEAN, -- 是否一致
    consistency_level VARCHAR(20), -- 'high', 'medium', 'low', 'conflict'
    
    -- 检查时间
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_goal_consistency_decision ON goal_consistency_checks(decision_id);
CREATE INDEX idx_goal_consistency_score ON goal_consistency_checks(ai_consistency_score) WHERE ai_consistency_score IS NOT NULL;
CREATE INDEX idx_goal_consistency_level ON goal_consistency_checks(consistency_level);

-- ============================================================
-- 注释说明
-- ============================================================
COMMENT ON TABLE decision_requirements IS '决策需求表：存储决策需求的申请和审批，支持AI需求分析和历史模式识别';
COMMENT ON TABLE decision_baselines IS '决策基线表：存储决策的冻结快照，支持AI预测基线和基线优化';
COMMENT ON TABLE decision_alignment_checks IS '决策对齐检查表：存储对齐检查结果，支持AI冲突预测和一致性评分';
COMMENT ON TABLE decision_approval_flow IS '决策审批流程表：存储审批流程，支持AI风险评估和审批建议';
COMMENT ON TABLE approval_records IS '审批记录表：存储每个审批步骤的详细记录';
COMMENT ON TABLE resource_requirements IS '资源需求表：存储决策所需的资源需求，用于AI冲突检测';
COMMENT ON TABLE goal_consistency_checks IS '目标一致性检查表：存储目标一致性检查的详细结果';

COMMENT ON COLUMN decision_requirements.ai_priority_score IS 'AI计算的优先级得分，基于MLPModel';
COMMENT ON COLUMN decision_requirements.ai_similar_requirements IS 'AI识别出的相似历史需求，来自企业记忆系统';
COMMENT ON COLUMN decision_baselines.ai_predicted_outcomes IS 'AI预测的结果，基于VARModel或LightGBM';
COMMENT ON COLUMN decision_alignment_checks.ai_conflict_probability IS 'AI预测的冲突概率，基于RandomForest';
COMMENT ON COLUMN decision_alignment_checks.ai_consistency_score IS 'AI一致性得分，基于MLPModel和SynergyAnalysis';

