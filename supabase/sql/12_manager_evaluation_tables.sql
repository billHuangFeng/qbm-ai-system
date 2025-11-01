-- 管理者评价表
-- 12. 管理者评价和反馈系统

-- 管理者评价表（已在06中创建，这里创建相关功能表）

-- 评价反馈处理表
CREATE TABLE evaluation_feedback_processing (
    processing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluation_id UUID REFERENCES manager_evaluation(evaluation_id),
    processing_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_type VARCHAR(50) NOT NULL, -- 'confirmation', 'adjustment', 'rejection', 'clarification'
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    processing_context JSONB,
    original_evaluation JSONB,
    processing_rules JSONB,
    processing_result JSONB,
    processing_changes JSONB,
    impact_assessment JSONB,
    follow_up_actions JSONB,
    processing_duration_seconds INT,
    processing_errors JSONB,
    processing_warnings JSONB,
    validation_results JSONB,
    approval_required BOOLEAN DEFAULT false,
    approval_status VARCHAR(20), -- 'pending', 'approved', 'rejected'
    approved_by UUID REFERENCES user_profiles(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评价质量评估表
CREATE TABLE evaluation_quality_assessment (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluation_id UUID REFERENCES manager_evaluation(evaluation_id),
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assessment_type VARCHAR(50) NOT NULL, -- 'completeness', 'accuracy', 'consistency', 'timeliness'
    assessment_criteria JSONB NOT NULL,
    assessment_score DECIMAL(5,4),
    assessment_details JSONB,
    assessment_findings JSONB,
    assessment_recommendations JSONB,
    assessment_improvements JSONB,
    assessment_validator UUID REFERENCES user_profiles(user_id),
    assessment_confidence DECIMAL(5,4),
    assessment_status VARCHAR(20) DEFAULT 'completed', -- 'completed', 'pending', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评价一致性检查表
CREATE TABLE evaluation_consistency_check (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    check_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_type VARCHAR(50) NOT NULL, -- 'inter_evaluator', 'temporal', 'cross_metric', 'historical'
    check_scope JSONB NOT NULL,
    check_criteria JSONB NOT NULL,
    check_results JSONB NOT NULL,
    consistency_score DECIMAL(5,4),
    inconsistency_details JSONB,
    inconsistency_severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    inconsistency_causes JSONB,
    resolution_recommendations JSONB,
    resolution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'resolved', 'escalated'
    resolved_by UUID REFERENCES user_profiles(user_id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评价学习记录表
CREATE TABLE evaluation_learning_record (
    learning_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluation_id UUID REFERENCES manager_evaluation(evaluation_id),
    learning_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    learning_type VARCHAR(50) NOT NULL, -- 'pattern_recognition', 'bias_detection', 'improvement_suggestion', 'best_practice'
    learning_context JSONB,
    learning_pattern JSONB,
    learning_insight TEXT,
    learning_confidence DECIMAL(5,4),
    learning_significance DECIMAL(5,4),
    learning_impact JSONB,
    learning_recommendations JSONB,
    learning_action_items JSONB,
    learning_validation JSONB,
    learning_feedback JSONB,
    learning_status VARCHAR(20) DEFAULT 'discovered', -- 'discovered', 'validated', 'applied', 'archived'
    learning_priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    is_actionable BOOLEAN DEFAULT false,
    is_implemented BOOLEAN DEFAULT false,
    implementation_date TIMESTAMP WITH TIME ZONE,
    implementation_result JSONB,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评价改进建议表
CREATE TABLE evaluation_improvement_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluation_id UUID REFERENCES manager_evaluation(evaluation_id),
    suggestion_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    suggestion_type VARCHAR(50) NOT NULL, -- 'process_improvement', 'tool_enhancement', 'training_need', 'guideline_update'
    suggestion_category VARCHAR(100), -- 'evaluation_process', 'data_quality', 'user_experience', 'system_functionality'
    suggestion_title VARCHAR(300) NOT NULL,
    suggestion_description TEXT,
    suggestion_rationale TEXT,
    suggestion_benefits JSONB,
    suggestion_implementation JSONB,
    suggestion_resources JSONB,
    suggestion_timeline VARCHAR(100),
    suggestion_priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    suggestion_impact VARCHAR(20), -- 'low', 'medium', 'high'
    suggestion_feasibility VARCHAR(20), -- 'low', 'medium', 'high'
    suggestion_status VARCHAR(20) DEFAULT 'proposed', -- 'proposed', 'under_review', 'approved', 'implemented', 'rejected'
    suggestion_approval JSONB,
    suggestion_implementation_status VARCHAR(20), -- 'not_started', 'in_progress', 'completed', 'cancelled'
    implementation_progress DECIMAL(5,4),
    implementation_result JSONB,
    implementation_feedback JSONB,
    suggested_by UUID REFERENCES user_profiles(user_id),
    reviewed_by UUID REFERENCES user_profiles(user_id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES user_profiles(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    implemented_by UUID REFERENCES user_profiles(user_id),
    implemented_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评价绩效跟踪表
CREATE TABLE evaluation_performance_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluator_id UUID REFERENCES user_profiles(user_id),
    tracking_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tracking_period_start DATE,
    tracking_period_end DATE,
    total_evaluations INT,
    completed_evaluations INT,
    pending_evaluations INT,
    overdue_evaluations INT,
    evaluation_quality_score DECIMAL(5,4),
    evaluation_consistency_score DECIMAL(5,4),
    evaluation_timeliness_score DECIMAL(5,4),
    evaluation_accuracy_score DECIMAL(5,4),
    evaluation_completeness_score DECIMAL(5,4),
    average_evaluation_time_minutes INT,
    evaluation_feedback_score DECIMAL(5,4),
    evaluation_improvement_rate DECIMAL(5,4),
    evaluation_trend JSONB,
    performance_metrics JSONB,
    performance_insights JSONB,
    performance_recommendations JSONB,
    performance_goals JSONB,
    performance_achievements JSONB,
    performance_challenges JSONB,
    performance_development_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_evaluation_feedback_tenant ON evaluation_feedback_processing(tenant_id);
CREATE INDEX idx_evaluation_feedback_evaluation ON evaluation_feedback_processing(evaluation_id);
CREATE INDEX idx_evaluation_feedback_date ON evaluation_feedback_processing(processing_date);
CREATE INDEX idx_evaluation_feedback_type ON evaluation_feedback_processing(processing_type);
CREATE INDEX idx_evaluation_feedback_status ON evaluation_feedback_processing(processing_status);

CREATE INDEX idx_evaluation_quality_tenant ON evaluation_quality_assessment(tenant_id);
CREATE INDEX idx_evaluation_quality_evaluation ON evaluation_quality_assessment(evaluation_id);
CREATE INDEX idx_evaluation_quality_date ON evaluation_quality_assessment(assessment_date);
CREATE INDEX idx_evaluation_quality_type ON evaluation_quality_assessment(assessment_type);

CREATE INDEX idx_evaluation_consistency_tenant ON evaluation_consistency_check(tenant_id);
CREATE INDEX idx_evaluation_consistency_date ON evaluation_consistency_check(check_date);
CREATE INDEX idx_evaluation_consistency_type ON evaluation_consistency_check(check_type);
CREATE INDEX idx_evaluation_consistency_severity ON evaluation_consistency_check(inconsistency_severity);

CREATE INDEX idx_evaluation_learning_tenant ON evaluation_learning_record(tenant_id);
CREATE INDEX idx_evaluation_learning_evaluation ON evaluation_learning_record(evaluation_id);
CREATE INDEX idx_evaluation_learning_date ON evaluation_learning_record(learning_date);
CREATE INDEX idx_evaluation_learning_type ON evaluation_learning_record(learning_type);
CREATE INDEX idx_evaluation_learning_status ON evaluation_learning_record(learning_status);

CREATE INDEX idx_evaluation_suggestions_tenant ON evaluation_improvement_suggestions(tenant_id);
CREATE INDEX idx_evaluation_suggestions_evaluation ON evaluation_improvement_suggestions(evaluation_id);
CREATE INDEX idx_evaluation_suggestions_date ON evaluation_improvement_suggestions(suggestion_date);
CREATE INDEX idx_evaluation_suggestions_type ON evaluation_improvement_suggestions(suggestion_type);
CREATE INDEX idx_evaluation_suggestions_status ON evaluation_improvement_suggestions(suggestion_status);
CREATE INDEX idx_evaluation_suggestions_priority ON evaluation_improvement_suggestions(suggestion_priority);

CREATE INDEX idx_evaluation_performance_tenant ON evaluation_performance_tracking(tenant_id);
CREATE INDEX idx_evaluation_performance_evaluator ON evaluation_performance_tracking(evaluator_id);
CREATE INDEX idx_evaluation_performance_date ON evaluation_performance_tracking(tracking_date);

-- 启用RLS
ALTER TABLE evaluation_feedback_processing ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_quality_assessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_consistency_check ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_learning_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_improvement_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluation_performance_tracking ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
CREATE POLICY tenant_isolation_policy_evaluation_feedback ON evaluation_feedback_processing
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_evaluation_quality ON evaluation_quality_assessment
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_evaluation_consistency ON evaluation_consistency_check
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_evaluation_learning ON evaluation_learning_record
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_evaluation_suggestions ON evaluation_improvement_suggestions
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_evaluation_performance ON evaluation_performance_tracking
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 创建函数：处理评价反馈
CREATE OR REPLACE FUNCTION process_evaluation_feedback(
    p_tenant_id UUID,
    p_evaluation_id UUID,
    p_processing_type VARCHAR(50),
    p_processing_result JSONB,
    p_processing_changes JSONB
)
RETURNS UUID AS $$
DECLARE
    v_processing_id UUID;
BEGIN
    INSERT INTO evaluation_feedback_processing (
        tenant_id,
        evaluation_id,
        processing_type,
        processing_result,
        processing_changes,
        processing_status
    ) VALUES (
        p_tenant_id,
        p_evaluation_id,
        p_processing_type,
        p_processing_result,
        p_processing_changes,
        'completed'
    ) RETURNING processing_id INTO v_processing_id;
    
    RETURN v_processing_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建函数：评估评价质量
CREATE OR REPLACE FUNCTION assess_evaluation_quality(
    p_tenant_id UUID,
    p_evaluation_id UUID,
    p_assessment_type VARCHAR(50),
    p_assessment_score DECIMAL(5,4),
    p_assessment_details JSONB
)
RETURNS UUID AS $$
DECLARE
    v_assessment_id UUID;
BEGIN
    INSERT INTO evaluation_quality_assessment (
        tenant_id,
        evaluation_id,
        assessment_type,
        assessment_score,
        assessment_details
    ) VALUES (
        p_tenant_id,
        p_evaluation_id,
        p_assessment_type,
        p_assessment_score,
        p_assessment_details
    ) RETURNING assessment_id INTO v_assessment_id;
    
    RETURN v_assessment_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建函数：记录评价学习
CREATE OR REPLACE FUNCTION record_evaluation_learning(
    p_tenant_id UUID,
    p_evaluation_id UUID,
    p_learning_type VARCHAR(50),
    p_learning_insight TEXT,
    p_learning_confidence DECIMAL(5,4)
)
RETURNS UUID AS $$
DECLARE
    v_learning_id UUID;
BEGIN
    INSERT INTO evaluation_learning_record (
        tenant_id,
        evaluation_id,
        learning_type,
        learning_insight,
        learning_confidence
    ) VALUES (
        p_tenant_id,
        p_evaluation_id,
        p_learning_type,
        p_learning_insight,
        p_learning_confidence
    ) RETURNING learning_id INTO v_learning_id;
    
    RETURN v_learning_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建视图：评价质量摘要
CREATE VIEW evaluation_quality_summary AS
SELECT 
    me.tenant_id,
    me.evaluator_id,
    DATE_TRUNC('month', me.evaluation_date) as evaluation_month,
    COUNT(*) as total_evaluations,
    AVG(eqa.assessment_score) as avg_quality_score,
    AVG(eqa.assessment_confidence) as avg_confidence,
    COUNT(CASE WHEN eqa.assessment_score >= 0.8 THEN 1 END) as high_quality_count,
    COUNT(CASE WHEN eqa.assessment_score < 0.6 THEN 1 END) as low_quality_count
FROM manager_evaluation me
LEFT JOIN evaluation_quality_assessment eqa ON me.evaluation_id = eqa.evaluation_id
GROUP BY me.tenant_id, me.evaluator_id, DATE_TRUNC('month', me.evaluation_date);

-- 创建视图：评价改进建议摘要
CREATE VIEW evaluation_improvement_summary AS
SELECT 
    tenant_id,
    suggestion_type,
    suggestion_category,
    COUNT(*) as total_suggestions,
    COUNT(CASE WHEN suggestion_status = 'implemented' THEN 1 END) as implemented_count,
    COUNT(CASE WHEN suggestion_status = 'approved' THEN 1 END) as approved_count,
    AVG(suggestion_priority::INT) as avg_priority,
    AVG(implementation_progress) as avg_implementation_progress
FROM evaluation_improvement_suggestions
GROUP BY tenant_id, suggestion_type, suggestion_category;

