-- 预测准确性日志表
-- 09. 预测准确性跟踪

-- 预测准确性日志表
CREATE TABLE prediction_accuracy_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_id UUID REFERENCES model_parameters_storage(model_id),
    prediction_id UUID,
    prediction_type VARCHAR(50) NOT NULL, -- 'marginal_analysis', 'time_series', 'npv', 'capability_value'
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actual_value DECIMAL(15,4),
    predicted_value DECIMAL(15,4),
    prediction_error DECIMAL(15,4),
    absolute_error DECIMAL(15,4),
    percentage_error DECIMAL(8,4),
    confidence_interval_lower DECIMAL(15,4),
    confidence_interval_upper DECIMAL(15,4),
    prediction_accuracy DECIMAL(8,6),
    prediction_bias DECIMAL(15,4),
    prediction_variance DECIMAL(15,4),
    feature_values JSONB,
    prediction_context JSONB,
    validation_method VARCHAR(50), -- 'holdout', 'cross_validation', 'bootstrap'
    validation_score DECIMAL(8,6),
    is_outlier BOOLEAN DEFAULT false,
    outlier_reason VARCHAR(200),
    correction_applied BOOLEAN DEFAULT false,
    correction_method VARCHAR(100),
    correction_value DECIMAL(15,4),
    feedback_provided BOOLEAN DEFAULT false,
    feedback_source VARCHAR(50), -- 'user', 'system', 'external'
    feedback_value DECIMAL(15,4),
    feedback_confidence DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 模型性能历史表
CREATE TABLE model_performance_history (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_id UUID REFERENCES model_parameters_storage(model_id),
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evaluation_period_start DATE,
    evaluation_period_end DATE,
    total_predictions INT,
    accurate_predictions INT,
    accuracy_rate DECIMAL(8,6),
    mean_absolute_error DECIMAL(15,4),
    mean_squared_error DECIMAL(15,4),
    root_mean_squared_error DECIMAL(15,4),
    mean_absolute_percentage_error DECIMAL(8,4),
    r_squared DECIMAL(8,6),
    adjusted_r_squared DECIMAL(8,6),
    prediction_bias DECIMAL(15,4),
    prediction_variance DECIMAL(15,4),
    confidence_interval_coverage DECIMAL(8,6),
    calibration_score DECIMAL(8,6),
    reliability_score DECIMAL(8,6),
    stability_score DECIMAL(8,6),
    performance_trend VARCHAR(20), -- 'improving', 'stable', 'declining'
    performance_level VARCHAR(20), -- 'excellent', 'good', 'fair', 'poor'
    evaluation_method VARCHAR(50), -- 'holdout', 'cross_validation', 'bootstrap', 'walk_forward'
    evaluation_metrics JSONB,
    performance_insights JSONB,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 预测错误分析表
CREATE TABLE prediction_error_analysis (
    error_analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_id UUID REFERENCES model_parameters_storage(model_id),
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_period_start DATE,
    analysis_period_end DATE,
    total_errors INT,
    error_types JSONB, -- 错误类型统计
    error_patterns JSONB, -- 错误模式分析
    error_causes JSONB, -- 错误原因分析
    error_severity_distribution JSONB, -- 错误严重程度分布
    error_frequency_distribution JSONB, -- 错误频率分布
    error_temporal_patterns JSONB, -- 错误时间模式
    error_feature_correlations JSONB, -- 错误与特征相关性
    error_threshold_analysis JSONB, -- 错误阈值分析
    error_clustering_results JSONB, -- 错误聚类结果
    error_prediction_models JSONB, -- 错误预测模型
    error_prevention_strategies JSONB, -- 错误预防策略
    error_correction_methods JSONB, -- 错误纠正方法
    error_impact_assessment JSONB, -- 错误影响评估
    error_cost_analysis JSONB, -- 错误成本分析
    improvement_recommendations JSONB, -- 改进建议
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 模型训练历史表
CREATE TABLE model_training_history (
    training_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_id UUID REFERENCES model_parameters_storage(model_id),
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_type VARCHAR(50) NOT NULL, -- 'initial', 'retrain', 'incremental', 'transfer'
    training_trigger VARCHAR(100), -- 'scheduled', 'performance_degradation', 'data_drift', 'manual'
    training_data_size INT,
    training_data_period_start DATE,
    training_data_period_end DATE,
    training_features JSONB,
    training_parameters JSONB,
    training_algorithm VARCHAR(100),
    training_duration_seconds INT,
    training_iterations INT,
    training_convergence BOOLEAN,
    training_loss_final DECIMAL(15,8),
    training_loss_history JSONB,
    validation_data_size INT,
    validation_score DECIMAL(8,6),
    validation_metrics JSONB,
    cross_validation_scores JSONB,
    feature_importance JSONB,
    model_complexity_score DECIMAL(8,6),
    overfitting_risk DECIMAL(8,6),
    training_status VARCHAR(20), -- 'success', 'failed', 'partial'
    training_errors JSONB,
    training_warnings JSONB,
    training_insights JSONB,
    performance_improvement DECIMAL(8,6),
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 预测质量监控表
CREATE TABLE prediction_quality_monitoring (
    monitoring_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_id UUID REFERENCES model_parameters_storage(model_id),
    monitoring_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    monitoring_window_start TIMESTAMP WITH TIME ZONE,
    monitoring_window_end TIMESTAMP WITH TIME ZONE,
    total_predictions INT,
    quality_metrics JSONB,
    drift_detection_results JSONB,
    anomaly_detection_results JSONB,
    performance_degradation_alerts JSONB,
    data_quality_issues JSONB,
    model_stability_metrics JSONB,
    prediction_confidence_distribution JSONB,
    prediction_accuracy_distribution JSONB,
    error_rate_trend JSONB,
    bias_trend JSONB,
    variance_trend JSONB,
    calibration_trend JSONB,
    reliability_trend JSONB,
    monitoring_alerts JSONB,
    monitoring_recommendations JSONB,
    action_items JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_prediction_accuracy_tenant ON prediction_accuracy_log(tenant_id);
CREATE INDEX idx_prediction_accuracy_model ON prediction_accuracy_log(model_id);
CREATE INDEX idx_prediction_accuracy_date ON prediction_accuracy_log(prediction_date);
CREATE INDEX idx_prediction_accuracy_type ON prediction_accuracy_log(prediction_type);
CREATE INDEX idx_prediction_accuracy_outlier ON prediction_accuracy_log(is_outlier);

CREATE INDEX idx_model_performance_tenant ON model_performance_history(tenant_id);
CREATE INDEX idx_model_performance_model ON model_performance_history(model_id);
CREATE INDEX idx_model_performance_date ON model_performance_history(evaluation_date);
CREATE INDEX idx_model_performance_trend ON model_performance_history(performance_trend);

CREATE INDEX idx_error_analysis_tenant ON prediction_error_analysis(tenant_id);
CREATE INDEX idx_error_analysis_model ON prediction_error_analysis(model_id);
CREATE INDEX idx_error_analysis_date ON prediction_error_analysis(analysis_date);

CREATE INDEX idx_training_history_tenant ON model_training_history(tenant_id);
CREATE INDEX idx_training_history_model ON model_training_history(model_id);
CREATE INDEX idx_training_history_date ON model_training_history(training_date);
CREATE INDEX idx_training_history_type ON model_training_history(training_type);

CREATE INDEX idx_quality_monitoring_tenant ON prediction_quality_monitoring(tenant_id);
CREATE INDEX idx_quality_monitoring_model ON prediction_quality_monitoring(model_id);
CREATE INDEX idx_quality_monitoring_date ON prediction_quality_monitoring(monitoring_date);

-- 启用RLS
ALTER TABLE prediction_accuracy_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_performance_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_error_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_training_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_quality_monitoring ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
CREATE POLICY tenant_isolation_policy_prediction_accuracy ON prediction_accuracy_log
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_model_performance ON model_performance_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_error_analysis ON prediction_error_analysis
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_training_history ON model_training_history
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_quality_monitoring ON prediction_quality_monitoring
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 创建视图：预测准确性摘要
CREATE VIEW prediction_accuracy_summary AS
SELECT 
    tenant_id,
    model_id,
    prediction_type,
    DATE_TRUNC('day', prediction_date) as prediction_day,
    COUNT(*) as total_predictions,
    AVG(prediction_accuracy) as avg_accuracy,
    AVG(absolute_error) as avg_absolute_error,
    AVG(percentage_error) as avg_percentage_error,
    STDDEV(prediction_accuracy) as accuracy_std,
    COUNT(CASE WHEN is_outlier THEN 1 END) as outlier_count,
    COUNT(CASE WHEN feedback_provided THEN 1 END) as feedback_count
FROM prediction_accuracy_log
GROUP BY tenant_id, model_id, prediction_type, DATE_TRUNC('day', prediction_date);

-- 创建视图：模型性能趋势
CREATE VIEW model_performance_trend AS
SELECT 
    tenant_id,
    model_id,
    evaluation_date,
    accuracy_rate,
    mean_absolute_error,
    r_squared,
    performance_trend,
    performance_level,
    LAG(accuracy_rate) OVER (PARTITION BY tenant_id, model_id ORDER BY evaluation_date) as prev_accuracy_rate,
    accuracy_rate - LAG(accuracy_rate) OVER (PARTITION BY tenant_id, model_id ORDER BY evaluation_date) as accuracy_change
FROM model_performance_history
ORDER BY tenant_id, model_id, evaluation_date;

-- 创建函数：计算预测准确性统计
CREATE OR REPLACE FUNCTION calculate_prediction_accuracy_stats(
    p_tenant_id UUID,
    p_model_id UUID DEFAULT NULL,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    total_predictions BIGINT,
    avg_accuracy DECIMAL(8,6),
    avg_absolute_error DECIMAL(15,4),
    avg_percentage_error DECIMAL(8,4),
    accuracy_std DECIMAL(8,6),
    outlier_rate DECIMAL(8,6),
    feedback_rate DECIMAL(8,6)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_predictions,
        AVG(pal.prediction_accuracy) as avg_accuracy,
        AVG(pal.absolute_error) as avg_absolute_error,
        AVG(pal.percentage_error) as avg_percentage_error,
        STDDEV(pal.prediction_accuracy) as accuracy_std,
        (COUNT(CASE WHEN pal.is_outlier THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL) as outlier_rate,
        (COUNT(CASE WHEN pal.feedback_provided THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL) as feedback_rate
    FROM prediction_accuracy_log pal
    WHERE pal.tenant_id = p_tenant_id
        AND (p_model_id IS NULL OR pal.model_id = p_model_id)
        AND (p_start_date IS NULL OR pal.prediction_date >= p_start_date)
        AND (p_end_date IS NULL OR pal.prediction_date <= p_end_date);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

