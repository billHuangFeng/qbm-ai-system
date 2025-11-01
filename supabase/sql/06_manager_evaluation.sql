-- =====================================================
-- BMOS系统 - 管理者评价系统表
-- 作用: 存储管理者对系统分析结果的确认、调整或拒绝
-- 重要性: "越用越聪明"的核心反馈入口
-- =====================================================

-- 1. 管理者评价记录表
CREATE TABLE IF NOT EXISTS manager_evaluation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 关联信息
    analysis_id UUID NOT NULL, -- 关联的分析结果ID
    analysis_type VARCHAR(50) NOT NULL, -- 'marginal_analysis', 'synergy_analysis', 'process_optimization'
    
    -- 评价类型
    evaluation_type VARCHAR(20) NOT NULL, -- 'confirm', 'adjust', 'reject'
    evaluation_content TEXT, -- 管理者评价意见
    
    -- 指标调整记录
    metric_adjustments JSONB, -- [{"metric_id": "xxx", "metric_name": "xxx", "current_value": 100, "adjusted_value": 120, "adjustment_reason": "市场环境变化"}]
    
    -- 实施计划
    implementation_plan JSONB, -- {"start_date": "2025-02-01", "duration": 90, "responsible_person": "张三", "budget_required": 100000}
    
    -- 优先级和影响
    priority_level VARCHAR(20), -- 'high', 'medium', 'low'
    expected_impact TEXT, -- 预期影响描述
    
    -- 状态跟踪
    status VARCHAR(20) DEFAULT 'submitted', -- 'submitted', 'in_progress', 'completed', 'cancelled'
    is_applied BOOLEAN DEFAULT false, -- 是否已应用到模型
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES user_profiles(id),
    updated_by UUID REFERENCES user_profiles(id),
    
    -- 约束
    CONSTRAINT valid_evaluation_type CHECK (evaluation_type IN ('confirm', 'adjust', 'reject')),
    CONSTRAINT valid_status CHECK (status IN ('submitted', 'in_progress', 'completed', 'cancelled'))
);

-- 2. 指标调整历史表
CREATE TABLE IF NOT EXISTS metric_adjustment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    evaluation_id UUID NOT NULL REFERENCES manager_evaluation(id) ON DELETE CASCADE,
    
    -- 调整详情
    metric_id VARCHAR(100) NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    metric_type VARCHAR(50), -- 'npv', 'margin', 'cost', 'revenue', 'capability_value'
    
    -- 值
    original_value DECIMAL(15,4),
    adjusted_value DECIMAL(15,4),
    adjustment_reason TEXT,
    
    -- 应用结果
    is_applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMP,
    application_effect JSONB, -- 应用效果记录
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES user_profiles(id)
);

-- 3. 数据澄清请求表
CREATE TABLE IF NOT EXISTS data_clarification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 澄清对象
    clarification_type VARCHAR(50), -- 'data_source', 'calculation_method', 'assumption', 'parameter'
    reference_id UUID, -- 关联的数据或分析ID
    reference_type VARCHAR(50), -- 'fact_order', 'fact_cost', 'analysis_result'
    
    -- 澄清内容
    clarification_question TEXT NOT NULL,
    clarification_answer TEXT,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'answered', 'resolved'
    priority_level VARCHAR(20), -- 'high', 'medium', 'low'
    
    -- 处理信息
    answered_at TIMESTAMP,
    answered_by UUID REFERENCES user_profiles(id),
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES user_profiles(id)
);

-- 4. 模型更新日志表 (用于跟踪基于反馈的模型改进)
CREATE TABLE IF NOT EXISTS model_update_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 更新触发器
    trigger_type VARCHAR(50) NOT NULL, -- 'manager_evaluation', 'prediction_error', 'scheduled_retrain', 'accuracy_threshold'
    trigger_reference_id UUID, -- 触发本次更新的参考ID
    trigger_description TEXT,
    
    -- 模型信息
    model_type VARCHAR(50) NOT NULL, -- 'shapley', 'timeseries', 'npv', 'capability_value'
    old_model_version VARCHAR(20),
    new_model_version VARCHAR(20),
    
    -- 更新内容
    update_content JSONB, -- 更新了哪些参数、权重、特征
    performance_improvement JSONB, -- {"old_mae": 10.5, "new_mae": 8.2, "improvement_percentage": 21.9}
    
    -- 状态
    status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'training', 'completed', 'failed'
    error_message TEXT,
    
    -- 元数据
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES user_profiles(id)
);

-- 索引
CREATE INDEX idx_manager_evaluation_tenant_id ON manager_evaluation(tenant_id);
CREATE INDEX idx_manager_evaluation_analysis ON manager_evaluation(analysis_id, analysis_type);
CREATE INDEX idx_manager_evaluation_status ON manager_evaluation(status);
CREATE INDEX idx_manager_evaluation_created_at ON manager_evaluation(created_at DESC);

CREATE INDEX idx_metric_adjustment_tenant_id ON metric_adjustment_history(tenant_id);
CREATE INDEX idx_metric_adjustment_evaluation ON metric_adjustment_history(evaluation_id);
CREATE INDEX idx_metric_adjustment_metric ON metric_adjustment_history(metric_id);

CREATE INDEX idx_data_clarification_tenant_id ON data_clarification(tenant_id);
CREATE INDEX idx_data_clarification_status ON data_clarification(status);
CREATE INDEX idx_data_clarification_reference ON data_clarification(reference_id, reference_type);

CREATE INDEX idx_model_update_log_tenant_id ON model_update_log(tenant_id);
CREATE INDEX idx_model_update_log_model_type ON model_update_log(model_type);
CREATE INDEX idx_model_update_log_status ON model_update_log(status);
CREATE INDEX idx_model_update_log_started_at ON model_update_log(started_at DESC);

-- RLS策略
ALTER TABLE manager_evaluation ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON manager_evaluation
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE metric_adjustment_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON metric_adjustment_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE data_clarification ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON data_clarification
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE model_update_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON model_update_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 注释
COMMENT ON TABLE manager_evaluation IS '管理者评价表 - 记录管理者对系统分析结果的反馈';
COMMENT ON TABLE metric_adjustment_history IS '指标调整历史表 - 记录基于管理者反馈的指标调整';
COMMENT ON TABLE data_clarification IS '数据澄清表 - 记录对数据和分析结果的澄清请求';
COMMENT ON TABLE model_update_log IS '模型更新日志 - 记录基于反馈的模型改进历史';



