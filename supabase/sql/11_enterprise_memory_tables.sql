-- 企业记忆系统表
-- 11. 企业记忆和学习系统

-- 企业记忆表（已在07中创建，这里创建相关功能表）

-- 记忆应用历史表
CREATE TABLE memory_application_history (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    memory_id UUID REFERENCES enterprise_memory(memory_id),
    application_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    application_context VARCHAR(200),
    application_type VARCHAR(50) NOT NULL, -- 'prediction_adjustment', 'decision_support', 'pattern_recognition', 'strategy_guidance'
    application_method VARCHAR(100), -- 'direct_application', 'weighted_combination', 'similarity_matching', 'rule_based'
    application_parameters JSONB,
    input_data JSONB,
    memory_relevance_score DECIMAL(5,4),
    application_confidence DECIMAL(5,4),
    application_result JSONB,
    application_effectiveness DECIMAL(5,4),
    performance_improvement JSONB,
    user_feedback JSONB,
    feedback_score DECIMAL(5,4),
    feedback_notes TEXT,
    application_success BOOLEAN,
    application_errors JSONB,
    application_warnings JSONB,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 学习模式识别表
CREATE TABLE learning_pattern_recognition (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    pattern_name VARCHAR(200) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL, -- 'success_pattern', 'failure_pattern', 'anomaly_pattern', 'trend_pattern'
    pattern_category VARCHAR(100), -- 'business_process', 'customer_behavior', 'market_dynamics', 'operational_efficiency'
    pattern_description TEXT,
    pattern_conditions JSONB NOT NULL,
    pattern_frequency INT DEFAULT 1,
    pattern_confidence DECIMAL(5,4),
    pattern_significance DECIMAL(5,4),
    pattern_impact JSONB,
    pattern_recommendations JSONB,
    pattern_examples JSONB,
    pattern_validation_results JSONB,
    pattern_accuracy DECIMAL(5,4),
    pattern_precision DECIMAL(5,4),
    pattern_recall DECIMAL(5,4),
    pattern_f1_score DECIMAL(5,4),
    is_active BOOLEAN DEFAULT true,
    is_validated BOOLEAN DEFAULT false,
    validation_date TIMESTAMP WITH TIME ZONE,
    validated_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, pattern_name)
);

-- 知识图谱表
CREATE TABLE knowledge_graph (
    graph_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'concept', 'process', 'resource', 'capability', 'outcome'
    entity_name VARCHAR(200) NOT NULL,
    entity_description TEXT,
    entity_properties JSONB,
    entity_attributes JSONB,
    entity_relationships JSONB,
    entity_importance DECIMAL(5,4),
    entity_frequency INT DEFAULT 1,
    entity_confidence DECIMAL(5,4),
    entity_context JSONB,
    entity_tags JSONB,
    entity_metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, entity_id, entity_type)
);

-- 知识关系表
CREATE TABLE knowledge_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    source_entity_id UUID NOT NULL,
    target_entity_id UUID NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'causes', 'influences', 'depends_on', 'enables', 'conflicts_with'
    relationship_strength DECIMAL(5,4),
    relationship_direction VARCHAR(20), -- 'directed', 'bidirectional', 'undirected'
    relationship_confidence DECIMAL(5,4),
    relationship_context JSONB,
    relationship_evidence JSONB,
    relationship_frequency INT DEFAULT 1,
    relationship_importance DECIMAL(5,4),
    relationship_metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, source_entity_id, target_entity_id, relationship_type)
);

-- 学习洞察表
CREATE TABLE learning_insights (
    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    insight_title VARCHAR(300) NOT NULL,
    insight_type VARCHAR(50) NOT NULL, -- 'pattern_discovery', 'anomaly_detection', 'trend_analysis', 'correlation_finding'
    insight_category VARCHAR(100), -- 'business', 'operational', 'strategic', 'tactical'
    insight_description TEXT,
    insight_content JSONB NOT NULL,
    insight_evidence JSONB,
    insight_confidence DECIMAL(5,4),
    insight_significance DECIMAL(5,4),
    insight_impact JSONB,
    insight_recommendations JSONB,
    insight_action_items JSONB,
    insight_metrics JSONB,
    insight_validation JSONB,
    insight_source_data JSONB,
    insight_algorithm_used VARCHAR(100),
    insight_parameters JSONB,
    insight_accuracy DECIMAL(5,4),
    insight_precision DECIMAL(5,4),
    insight_recall DECIMAL(5,4),
    insight_f1_score DECIMAL(5,4),
    insight_status VARCHAR(20) DEFAULT 'discovered', -- 'discovered', 'validated', 'applied', 'archived'
    insight_priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    insight_tags JSONB,
    insight_metadata JSONB,
    is_actionable BOOLEAN DEFAULT false,
    is_implemented BOOLEAN DEFAULT false,
    implementation_date TIMESTAMP WITH TIME ZONE,
    implementation_result JSONB,
    created_by UUID REFERENCES user_profiles(user_id),
    validated_by UUID REFERENCES user_profiles(user_id),
    validated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, insight_title)
);

-- 学习效果评估表
CREATE TABLE learning_effectiveness_evaluation (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evaluation_period_start DATE,
    evaluation_period_end DATE,
    evaluation_type VARCHAR(50) NOT NULL, -- 'memory_effectiveness', 'pattern_accuracy', 'insight_value', 'overall_learning'
    evaluation_scope JSONB, -- 评估范围
    evaluation_metrics JSONB NOT NULL,
    baseline_metrics JSONB,
    improvement_metrics JSONB,
    effectiveness_score DECIMAL(5,4),
    learning_rate DECIMAL(5,4),
    adaptation_speed DECIMAL(5,4),
    generalization_ability DECIMAL(5,4),
    robustness_score DECIMAL(5,4),
    efficiency_score DECIMAL(5,4),
    quality_score DECIMAL(5,4),
    impact_score DECIMAL(5,4),
    roi_score DECIMAL(5,4),
    evaluation_results JSONB,
    evaluation_insights JSONB,
    evaluation_recommendations JSONB,
    evaluation_limitations JSONB,
    evaluation_methodology JSONB,
    evaluation_data_sources JSONB,
    evaluation_confidence DECIMAL(5,4),
    evaluation_validated BOOLEAN DEFAULT false,
    validated_by UUID REFERENCES user_profiles(user_id),
    validated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_memory_application_tenant ON memory_application_history(tenant_id);
CREATE INDEX idx_memory_application_memory ON memory_application_history(memory_id);
CREATE INDEX idx_memory_application_date ON memory_application_history(application_date);
CREATE INDEX idx_memory_application_type ON memory_application_history(application_type);
CREATE INDEX idx_memory_application_success ON memory_application_history(application_success);

CREATE INDEX idx_pattern_recognition_tenant ON learning_pattern_recognition(tenant_id);
CREATE INDEX idx_pattern_recognition_type ON learning_pattern_recognition(pattern_type);
CREATE INDEX idx_pattern_recognition_active ON learning_pattern_recognition(is_active);
CREATE INDEX idx_pattern_recognition_validated ON learning_pattern_recognition(is_validated);

CREATE INDEX idx_knowledge_graph_tenant ON knowledge_graph(tenant_id);
CREATE INDEX idx_knowledge_graph_type ON knowledge_graph(entity_type);
CREATE INDEX idx_knowledge_graph_active ON knowledge_graph(is_active);

CREATE INDEX idx_knowledge_relationships_tenant ON knowledge_relationships(tenant_id);
CREATE INDEX idx_knowledge_relationships_source ON knowledge_relationships(source_entity_id);
CREATE INDEX idx_knowledge_relationships_target ON knowledge_relationships(target_entity_id);
CREATE INDEX idx_knowledge_relationships_type ON knowledge_relationships(relationship_type);

CREATE INDEX idx_learning_insights_tenant ON learning_insights(tenant_id);
CREATE INDEX idx_learning_insights_type ON learning_insights(insight_type);
CREATE INDEX idx_learning_insights_status ON learning_insights(insight_status);
CREATE INDEX idx_learning_insights_priority ON learning_insights(insight_priority);
CREATE INDEX idx_learning_insights_actionable ON learning_insights(is_actionable);

CREATE INDEX idx_learning_evaluation_tenant ON learning_effectiveness_evaluation(tenant_id);
CREATE INDEX idx_learning_evaluation_date ON learning_effectiveness_evaluation(evaluation_date);
CREATE INDEX idx_learning_evaluation_type ON learning_effectiveness_evaluation(evaluation_type);

-- 启用RLS
ALTER TABLE memory_application_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_pattern_recognition ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_graph ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_effectiveness_evaluation ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
CREATE POLICY tenant_isolation_policy_memory_application ON memory_application_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_pattern_recognition ON learning_pattern_recognition
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_knowledge_graph ON knowledge_graph
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_knowledge_relationships ON knowledge_relationships
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_learning_insights ON learning_insights
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_learning_evaluation ON learning_effectiveness_evaluation
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
CREATE TRIGGER update_pattern_recognition_updated_at BEFORE UPDATE ON learning_pattern_recognition
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_graph_updated_at BEFORE UPDATE ON knowledge_graph
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_relationships_updated_at BEFORE UPDATE ON knowledge_relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_insights_updated_at BEFORE UPDATE ON learning_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数：记录记忆应用
CREATE OR REPLACE FUNCTION log_memory_application(
    p_tenant_id UUID,
    p_memory_id UUID,
    p_application_type VARCHAR(50),
    p_application_context VARCHAR(200),
    p_application_result JSONB,
    p_effectiveness DECIMAL(5,4)
)
RETURNS UUID AS $$
DECLARE
    v_application_id UUID;
BEGIN
    INSERT INTO memory_application_history (
        tenant_id,
        memory_id,
        application_type,
        application_context,
        application_result,
        application_effectiveness,
        application_success
    ) VALUES (
        p_tenant_id,
        p_memory_id,
        p_application_type,
        p_application_context,
        p_application_result,
        p_effectiveness,
        p_effectiveness > 0.5
    ) RETURNING application_id INTO v_application_id;
    
    RETURN v_application_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建函数：生成学习洞察
CREATE OR REPLACE FUNCTION generate_learning_insight(
    p_tenant_id UUID,
    p_insight_title VARCHAR(300),
    p_insight_type VARCHAR(50),
    p_insight_content JSONB,
    p_insight_confidence DECIMAL(5,4)
)
RETURNS UUID AS $$
DECLARE
    v_insight_id UUID;
BEGIN
    INSERT INTO learning_insights (
        tenant_id,
        insight_title,
        insight_type,
        insight_content,
        insight_confidence
    ) VALUES (
        p_tenant_id,
        p_insight_title,
        p_insight_type,
        p_insight_content,
        p_insight_confidence
    ) RETURNING insight_id INTO v_insight_id;
    
    RETURN v_insight_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建视图：企业记忆效果摘要
CREATE VIEW enterprise_memory_effectiveness_summary AS
SELECT 
    em.tenant_id,
    em.memory_id,
    em.memory_type,
    em.memory_category,
    COUNT(mah.application_id) as application_count,
    AVG(mah.application_effectiveness) as avg_effectiveness,
    AVG(mah.application_confidence) as avg_confidence,
    AVG(mah.feedback_score) as avg_feedback_score,
    COUNT(CASE WHEN mah.application_success THEN 1 END) as success_count,
    COUNT(CASE WHEN mah.application_success THEN 1 END)::DECIMAL / COUNT(mah.application_id)::DECIMAL as success_rate
FROM enterprise_memory em
LEFT JOIN memory_application_history mah ON em.memory_id = mah.memory_id
GROUP BY em.tenant_id, em.memory_id, em.memory_type, em.memory_category;

-- 创建视图：学习洞察摘要
CREATE VIEW learning_insights_summary AS
SELECT 
    tenant_id,
    insight_type,
    insight_category,
    COUNT(*) as total_insights,
    AVG(insight_confidence) as avg_confidence,
    AVG(insight_significance) as avg_significance,
    COUNT(CASE WHEN is_actionable THEN 1 END) as actionable_count,
    COUNT(CASE WHEN is_implemented THEN 1 END) as implemented_count,
    COUNT(CASE WHEN insight_status = 'validated' THEN 1 END) as validated_count
FROM learning_insights
GROUP BY tenant_id, insight_type, insight_category;

