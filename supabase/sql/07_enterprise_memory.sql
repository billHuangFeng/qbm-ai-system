-- =====================================================
-- BMOS系统 - 企业记忆系统表
-- 作用: 持久化存储系统学习到的模式、策略和规律
-- 重要性: "越用越聪明"的核心记忆层
-- =====================================================

-- 1. 企业记忆主表
CREATE TABLE IF NOT EXISTS enterprise_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 记忆类型
    memory_type VARCHAR(50) NOT NULL, -- 'pattern', 'strategy', 'lesson_learned', 'optimization_rule', 'anomaly_pattern'
    memory_category VARCHAR(50), -- 'business_model', 'cost_optimization', 'resource_allocation', 'capability_enhancement'
    
    -- 记忆内容
    memory_title VARCHAR(200) NOT NULL, -- 记忆标题
    memory_description TEXT, -- 记忆详细描述
    memory_content JSONB NOT NULL, -- 记忆的具体内容(存储模式、策略、规则等)
    
    -- 来源追踪
    source_type VARCHAR(50) NOT NULL, -- 'manager_feedback', 'prediction_error', 'anomaly_detection', 'optimization_cycle', 'user_behavior'
    source_reference_id UUID, -- 来源的参考ID
    source_description TEXT, -- 来源描述
    
    -- 上下文信息
    business_context JSONB, -- 业务上下文(时间、部门、产品等)
    related_facts JSONB, -- 相关的事实数据
    
    -- 应用追踪
    applied_count INTEGER DEFAULT 0, -- 应用次数
    successful_application_count INTEGER DEFAULT 0, -- 成功应用次数
    success_rate DECIMAL(5,4), -- 成功率 (successful_application_count / applied_count)
    average_impact_score DECIMAL(5,4), -- 平均影响力得分
    
    -- 置信度与衰减
    confidence_score DECIMAL(5,4) NOT NULL DEFAULT 0.5, -- 置信度 (0-1)
    decay_factor DECIMAL(5,4) DEFAULT 0.95, -- 时间衰减系数
    relevance_score DECIMAL(5,4) NOT NULL DEFAULT 0.5, -- 相关性得分
    
    -- 状态
    is_active BOOLEAN DEFAULT true, -- 是否激活
    is_verified BOOLEAN DEFAULT false, -- 是否已验证
    verification_count INTEGER DEFAULT 0, -- 验证次数
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_applied_at TIMESTAMP WITH TIME ZONE, -- 最后应用时间
    last_verified_at TIMESTAMP WITH TIME ZONE, -- 最后验证时间
    deprecated_at TIMESTAMP WITH TIME ZONE, -- 废弃时间
    
    -- 元数据
    created_by UUID REFERENCES user_profiles(id),
    verified_by UUID REFERENCES user_profiles(id),
    
    -- 约束
    CONSTRAINT valid_memory_type CHECK (memory_type IN ('pattern', 'strategy', 'lesson_learned', 'optimization_rule', 'anomaly_pattern', 'threshold', 'synergy_effect')),
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT valid_success_rate CHECK (success_rate >= 0 AND success_rate <= 1),
    CONSTRAINT valid_relevance CHECK (relevance_score >= 0 AND relevance_score <= 1)
);

-- 2. 记忆应用历史表
CREATE TABLE IF NOT EXISTS memory_application_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    memory_id UUID NOT NULL REFERENCES enterprise_memory(id) ON DELETE CASCADE,
    
    -- 应用场景
    application_context VARCHAR(100), -- 应用场景标识
    application_type VARCHAR(50), -- 'prediction', 'optimization', 'anomaly_detection', 'recommendation'
    
    -- 应用结果
    was_successful BOOLEAN, -- 是否成功
    impact_score DECIMAL(5,4), -- 影响得分
    actual_result JSONB, -- 实际结果
    expected_result JSONB, -- 预期结果
    
    -- 反馈
    user_feedback VARCHAR(20), -- 'positive', 'negative', 'neutral'
    feedback_comment TEXT,
    
    -- 元数据
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by UUID REFERENCES user_profiles(id) -- 如果是人工应用,记录用户;如果是系统自动应用,则为null
);

-- 3. 预测准确度日志表
CREATE TABLE IF NOT EXISTS prediction_accuracy_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 预测信息
    prediction_type VARCHAR(50) NOT NULL, -- 'npv', 'capability_value', 'product_value', 'margin', 'revenue'
    target_period VARCHAR(20) NOT NULL, -- '2025-01', '2025-Q1' 等
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL, -- 预测时间
    
    -- 预测值
    predicted_value DECIMAL(15,4),
    confidence_level DECIMAL(5,4), -- 预测置信度
    prediction_method VARCHAR(50), -- 使用的预测方法
    model_version VARCHAR(20), -- 使用的模型版本
    
    -- 实际值(可能延后更新)
    actual_value DECIMAL(15,4), -- 实际值
    actual_date TIMESTAMP WITH TIME ZONE, -- 实际值更新时间
    has_actual_value BOOLEAN DEFAULT false, -- 是否已有实际值
    
    -- 误差分析
    absolute_error DECIMAL(15,4), -- |predicted - actual|
    relative_error DECIMAL(8,4), -- |predicted - actual| / actual * 100
    squared_error DECIMAL(15,6), -- (predicted - actual)²
    
    -- 误差类型
    error_type VARCHAR(50), -- 'overestimate', 'underestimate', 'accurate', 'significant_error'
    error_severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    error_causes JSONB, -- 误差原因分析
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT valid_confidence CHECK (confidence_level >= 0 AND confidence_level <= 1)
);

-- 4. 模型训练历史表
CREATE TABLE IF NOT EXISTS model_training_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 模型信息
    model_type VARCHAR(50) NOT NULL, -- 'shapley', 'timeseries', 'npv', 'capability_value'
    model_version VARCHAR(20) NOT NULL,
    training_trigger VARCHAR(50), -- 'manual', 'scheduled', 'accuracy_threshold', 'new_data', 'feedback'
    
    -- 训练数据
    training_data_period VARCHAR(50), -- 训练数据的时间范围
    training_data_size INTEGER, -- 训练数据量
    feature_count INTEGER, -- 特征数量
    
    -- 超参数
    hyperparameters JSONB, -- 训练使用的超参数
    feature_selection JSONB, -- 使用的特征
    
    -- 训练性能
    training_duration_seconds INTEGER, -- 训练时长
    training_status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'training', 'completed', 'failed'
    error_message TEXT,
    
    -- 模型性能指标
    accuracy_score DECIMAL(8,6),
    r_squared DECIMAL(8,6),
    mae DECIMAL(15,6), -- 平均绝对误差
    rmse DECIMAL(15,6), -- 均方根误差
    mape DECIMAL(8,4), -- 平均绝对百分比误差
    
    -- 与前一版本对比
    performance_improvement JSONB, -- {"accuracy_delta": 0.05, "mae_delta": -2.3, "improvement_percentage": 15.2}
    
    -- 元数据
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    trained_by UUID REFERENCES user_profiles(id) -- 如果是手动触发,记录用户
);

-- 索引
CREATE INDEX idx_enterprise_memory_tenant_id ON enterprise_memory(tenant_id);
CREATE INDEX idx_enterprise_memory_type ON enterprise_memory(memory_type);
CREATE INDEX idx_enterprise_memory_category ON enterprise_memory(memory_category);
CREATE INDEX idx_enterprise_memory_active ON enterprise_memory(is_active) WHERE is_active = true;
CREATE INDEX idx_enterprise_memory_confidence ON enterprise_memory(confidence_score DESC);
CREATE INDEX idx_enterprise_memory_relevance ON enterprise_memory(relevance_score DESC);
CREATE INDEX idx_enterprise_memory_created_at ON enterprise_memory(created_at DESC);

CREATE INDEX idx_memory_application_tenant_id ON memory_application_history(tenant_id);
CREATE INDEX idx_memory_application_memory_id ON memory_application_history(memory_id);
CREATE INDEX idx_memory_application_successful ON memory_application_history(was_successful);
CREATE INDEX idx_memory_application_date ON memory_application_history(applied_at DESC);

CREATE INDEX idx_prediction_accuracy_tenant_id ON prediction_accuracy_log(tenant_id);
CREATE INDEX idx_prediction_accuracy_type ON prediction_accuracy_log(prediction_type);
CREATE INDEX idx_prediction_accuracy_period ON prediction_accuracy_log(target_period);
CREATE INDEX idx_prediction_accuracy_has_actual ON prediction_accuracy_log(has_actual_value) WHERE has_actual_value = true;
CREATE INDEX idx_prediction_accuracy_error ON prediction_accuracy_log(relative_error DESC);

CREATE INDEX idx_model_training_tenant_id ON model_training_history(tenant_id);
CREATE INDEX idx_model_training_type ON model_training_history(model_type);
CREATE INDEX idx_model_training_status ON model_training_history(training_status);
CREATE INDEX idx_model_training_started_at ON model_training_history(started_at DESC);

-- RLS策略
ALTER TABLE enterprise_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON enterprise_memory
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE memory_application_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON memory_application_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE prediction_accuracy_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON prediction_accuracy_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

ALTER TABLE model_training_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON model_training_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 注释
COMMENT ON TABLE enterprise_memory IS '企业记忆表 - 存储系统学习到的模式、策略和规律';
COMMENT ON TABLE memory_application_history IS '记忆应用历史 - 记录企业记忆的应用情况';
COMMENT ON TABLE prediction_accuracy_log IS '预测准确度日志 - 记录预测值和实际值的对比';
COMMENT ON TABLE model_training_history IS '模型训练历史 - 记录模型训练和性能改进历史';


