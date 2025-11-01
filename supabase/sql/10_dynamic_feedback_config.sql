-- 动态反馈配置表
-- 10. 动态反馈和自动化优化

-- 动态反馈配置表（已在08中创建，这里创建相关功能表）

-- 反馈触发记录表
CREATE TABLE feedback_trigger_log (
    trigger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    config_id UUID REFERENCES dynamic_feedback_config(config_id),
    trigger_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trigger_type VARCHAR(50) NOT NULL, -- 'threshold', 'trend', 'anomaly', 'performance'
    trigger_condition JSONB NOT NULL,
    trigger_value DECIMAL(15,4),
    trigger_threshold DECIMAL(15,4),
    trigger_severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    trigger_context JSONB,
    action_triggered VARCHAR(50), -- 'alert', 'adjust', 'optimize', 'retrain'
    action_parameters JSONB,
    action_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executing', 'completed', 'failed'
    action_result JSONB,
    action_duration_seconds INT,
    feedback_generated BOOLEAN DEFAULT false,
    feedback_content JSONB,
    feedback_recipients JSONB,
    feedback_delivery_status VARCHAR(20), -- 'sent', 'delivered', 'read', 'acted'
    escalation_level INT DEFAULT 0,
    escalation_reason VARCHAR(200),
    resolution_status VARCHAR(20), -- 'open', 'in_progress', 'resolved', 'closed'
    resolution_notes TEXT,
    resolved_by UUID REFERENCES user_profiles(user_id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 自动化优化记录表
CREATE TABLE automation_optimization_log (
    optimization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    trigger_id UUID REFERENCES feedback_trigger_log(trigger_id),
    optimization_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    optimization_type VARCHAR(50) NOT NULL, -- 'model_retrain', 'parameter_adjust', 'weight_update', 'threshold_adjust'
    optimization_target VARCHAR(100), -- 优化目标
    optimization_method VARCHAR(100), -- 优化方法
    optimization_parameters JSONB,
    pre_optimization_metrics JSONB,
    post_optimization_metrics JSONB,
    optimization_improvement JSONB,
    optimization_duration_seconds INT,
    optimization_status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    optimization_result JSONB,
    optimization_errors JSONB,
    optimization_warnings JSONB,
    rollback_available BOOLEAN DEFAULT false,
    rollback_parameters JSONB,
    validation_passed BOOLEAN,
    validation_metrics JSONB,
    approval_required BOOLEAN DEFAULT false,
    approval_status VARCHAR(20), -- 'pending', 'approved', 'rejected'
    approved_by UUID REFERENCES user_profiles(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 反馈循环配置表
CREATE TABLE feedback_loop_config (
    loop_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    loop_name VARCHAR(200) NOT NULL,
    loop_type VARCHAR(50) NOT NULL, -- 'continuous', 'batch', 'event_driven', 'scheduled'
    loop_description TEXT,
    trigger_conditions JSONB NOT NULL,
    feedback_mechanisms JSONB NOT NULL,
    optimization_strategies JSONB NOT NULL,
    learning_algorithms JSONB,
    adaptation_rules JSONB,
    performance_thresholds JSONB,
    quality_gates JSONB,
    loop_frequency VARCHAR(20), -- 'real_time', 'hourly', 'daily', 'weekly'
    loop_schedule JSONB,
    is_active BOOLEAN DEFAULT true,
    priority_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    max_iterations INT,
    convergence_criteria JSONB,
    stopping_criteria JSONB,
    monitoring_config JSONB,
    alerting_config JSONB,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, loop_name)
);

-- 反馈循环执行记录表
CREATE TABLE feedback_loop_execution (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    loop_id UUID REFERENCES feedback_loop_config(loop_id),
    execution_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    execution_type VARCHAR(50) NOT NULL, -- 'scheduled', 'triggered', 'manual'
    execution_status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed', 'cancelled'
    execution_context JSONB,
    input_data JSONB,
    processing_steps JSONB,
    intermediate_results JSONB,
    final_results JSONB,
    performance_metrics JSONB,
    improvement_metrics JSONB,
    learning_insights JSONB,
    adaptation_changes JSONB,
    execution_duration_seconds INT,
    iterations_completed INT,
    convergence_achieved BOOLEAN,
    convergence_metrics JSONB,
    stopping_reason VARCHAR(100),
    execution_errors JSONB,
    execution_warnings JSONB,
    rollback_performed BOOLEAN DEFAULT false,
    rollback_reason VARCHAR(200),
    validation_results JSONB,
    approval_status VARCHAR(20), -- 'pending', 'approved', 'rejected'
    approved_by UUID REFERENCES user_profiles(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 自适应学习配置表
CREATE TABLE adaptive_learning_config (
    learning_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    learning_name VARCHAR(200) NOT NULL,
    learning_type VARCHAR(50) NOT NULL, -- 'online', 'incremental', 'transfer', 'meta'
    learning_algorithm VARCHAR(100) NOT NULL,
    learning_parameters JSONB NOT NULL,
    adaptation_strategy VARCHAR(100), -- 'gradient_based', 'bayesian', 'evolutionary', 'reinforcement'
    learning_rate_schedule JSONB,
    forgetting_factor DECIMAL(5,4),
    regularization_parameters JSONB,
    validation_strategy JSONB,
    performance_monitoring JSONB,
    drift_detection_config JSONB,
    concept_drift_handling JSONB,
    data_stream_config JSONB,
    batch_size INT,
    update_frequency VARCHAR(20), -- 'real_time', 'hourly', 'daily'
    learning_thresholds JSONB,
    stopping_criteria JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, learning_name)
);

-- 自适应学习记录表
CREATE TABLE adaptive_learning_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    learning_id UUID REFERENCES adaptive_learning_config(learning_id),
    learning_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    learning_trigger VARCHAR(100), -- 'new_data', 'performance_degradation', 'concept_drift', 'scheduled'
    learning_context JSONB,
    input_data_size INT,
    input_data_period_start TIMESTAMP WITH TIME ZONE,
    input_data_period_end TIMESTAMP WITH TIME ZONE,
    learning_parameters_used JSONB,
    learning_iterations INT,
    learning_duration_seconds INT,
    learning_loss_final DECIMAL(15,8),
    learning_loss_history JSONB,
    performance_before JSONB,
    performance_after JSONB,
    performance_improvement JSONB,
    adaptation_changes JSONB,
    concept_drift_detected BOOLEAN,
    concept_drift_severity DECIMAL(5,4),
    concept_drift_details JSONB,
    learning_success BOOLEAN,
    learning_errors JSONB,
    learning_warnings JSONB,
    validation_results JSONB,
    learning_insights JSONB,
    next_learning_schedule TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_feedback_trigger_tenant ON feedback_trigger_log(tenant_id);
CREATE INDEX idx_feedback_trigger_config ON feedback_trigger_log(config_id);
CREATE INDEX idx_feedback_trigger_date ON feedback_trigger_log(trigger_date);
CREATE INDEX idx_feedback_trigger_type ON feedback_trigger_log(trigger_type);
CREATE INDEX idx_feedback_trigger_status ON feedback_trigger_log(action_status);

CREATE INDEX idx_automation_optimization_tenant ON automation_optimization_log(tenant_id);
CREATE INDEX idx_automation_optimization_trigger ON automation_optimization_log(trigger_id);
CREATE INDEX idx_automation_optimization_date ON automation_optimization_log(optimization_date);
CREATE INDEX idx_automation_optimization_type ON automation_optimization_log(optimization_type);

CREATE INDEX idx_feedback_loop_config_tenant ON feedback_loop_config(tenant_id);
CREATE INDEX idx_feedback_loop_config_active ON feedback_loop_config(is_active);
CREATE INDEX idx_feedback_loop_config_type ON feedback_loop_config(loop_type);

CREATE INDEX idx_feedback_loop_execution_tenant ON feedback_loop_execution(tenant_id);
CREATE INDEX idx_feedback_loop_execution_loop ON feedback_loop_execution(loop_id);
CREATE INDEX idx_feedback_loop_execution_date ON feedback_loop_execution(execution_date);
CREATE INDEX idx_feedback_loop_execution_status ON feedback_loop_execution(execution_status);

CREATE INDEX idx_adaptive_learning_config_tenant ON adaptive_learning_config(tenant_id);
CREATE INDEX idx_adaptive_learning_config_active ON adaptive_learning_config(is_active);
CREATE INDEX idx_adaptive_learning_config_type ON adaptive_learning_config(learning_type);

CREATE INDEX idx_adaptive_learning_log_tenant ON adaptive_learning_log(tenant_id);
CREATE INDEX idx_adaptive_learning_log_learning ON adaptive_learning_log(learning_id);
CREATE INDEX idx_adaptive_learning_log_date ON adaptive_learning_log(learning_date);
CREATE INDEX idx_adaptive_learning_log_success ON adaptive_learning_log(learning_success);

-- 启用RLS
ALTER TABLE feedback_trigger_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_optimization_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_loop_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_loop_execution ENABLE ROW LEVEL SECURITY;
ALTER TABLE adaptive_learning_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE adaptive_learning_log ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
CREATE POLICY tenant_isolation_policy_feedback_trigger ON feedback_trigger_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_automation_optimization ON automation_optimization_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_feedback_loop_config ON feedback_loop_config
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_feedback_loop_execution ON feedback_loop_execution
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_adaptive_learning_config ON adaptive_learning_config
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_adaptive_learning_log ON adaptive_learning_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建更新时间触发器
CREATE TRIGGER update_feedback_loop_config_updated_at BEFORE UPDATE ON feedback_loop_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adaptive_learning_config_updated_at BEFORE UPDATE ON adaptive_learning_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数：触发反馈循环
CREATE OR REPLACE FUNCTION trigger_feedback_loop(
    p_tenant_id UUID,
    p_loop_id UUID,
    p_trigger_type VARCHAR(50),
    p_trigger_context JSONB
)
RETURNS UUID AS $$
DECLARE
    v_execution_id UUID;
BEGIN
    INSERT INTO feedback_loop_execution (
        tenant_id,
        loop_id,
        execution_type,
        execution_context,
        input_data
    ) VALUES (
        p_tenant_id,
        p_loop_id,
        'triggered',
        p_trigger_context,
        p_trigger_context
    ) RETURNING execution_id INTO v_execution_id;
    
    RETURN v_execution_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建函数：记录自动化优化
CREATE OR REPLACE FUNCTION log_automation_optimization(
    p_tenant_id UUID,
    p_trigger_id UUID,
    p_optimization_type VARCHAR(50),
    p_optimization_parameters JSONB,
    p_pre_metrics JSONB
)
RETURNS UUID AS $$
DECLARE
    v_optimization_id UUID;
BEGIN
    INSERT INTO automation_optimization_log (
        tenant_id,
        trigger_id,
        optimization_type,
        optimization_parameters,
        pre_optimization_metrics
    ) VALUES (
        p_tenant_id,
        p_trigger_id,
        p_optimization_type,
        p_optimization_parameters,
        p_pre_metrics
    ) RETURNING optimization_id INTO v_optimization_id;
    
    RETURN v_optimization_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

