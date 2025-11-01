-- 边际分析专用表
-- 08. 边际分析核心表

-- 核心资产清单表
CREATE TABLE core_asset_master (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    asset_code VARCHAR(50) NOT NULL,
    asset_name VARCHAR(200) NOT NULL,
    asset_type VARCHAR(50) NOT NULL, -- 'tangible', 'intangible', 'financial'
    asset_category VARCHAR(100), -- 'equipment', 'technology', 'brand', 'patent', etc.
    acquisition_date DATE,
    acquisition_cost DECIMAL(15,2),
    current_value DECIMAL(15,2),
    depreciation_rate DECIMAL(5,4),
    useful_life_years INT,
    residual_value DECIMAL(15,2),
    maintenance_cost_monthly DECIMAL(15,2),
    utilization_rate DECIMAL(5,4),
    performance_score DECIMAL(5,4),
    strategic_importance VARCHAR(20), -- 'high', 'medium', 'low'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, asset_code)
);

-- 核心能力清单表
CREATE TABLE core_capability_master (
    capability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    capability_code VARCHAR(50) NOT NULL,
    capability_name VARCHAR(200) NOT NULL,
    capability_type VARCHAR(50) NOT NULL, -- 'technical', 'managerial', 'operational', 'strategic'
    capability_category VARCHAR(100), -- 'R&D', 'manufacturing', 'marketing', 'sales', etc.
    capability_level VARCHAR(20), -- 'beginner', 'intermediate', 'advanced', 'expert'
    development_cost DECIMAL(15,2),
    maintenance_cost_monthly DECIMAL(15,2),
    proficiency_score DECIMAL(5,4),
    utilization_rate DECIMAL(5,4),
    performance_impact DECIMAL(5,4),
    strategic_importance VARCHAR(20), -- 'high', 'medium', 'low'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, capability_code)
);

-- 产品价值评估项表
CREATE TABLE product_value_item_master (
    value_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    value_item_code VARCHAR(50) NOT NULL,
    value_item_name VARCHAR(200) NOT NULL,
    value_type VARCHAR(50) NOT NULL, -- 'functional', 'emotional', 'social'
    value_category VARCHAR(100), -- 'quality', 'price', 'convenience', 'brand', etc.
    measurement_unit VARCHAR(50),
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),
    weight_factor DECIMAL(5,4),
    importance_score DECIMAL(5,4),
    customer_satisfaction_score DECIMAL(5,4),
    market_demand_score DECIMAL(5,4),
    competitive_advantage_score DECIMAL(5,4),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, value_item_code)
);

-- 月度增量指标表
CREATE TABLE monthly_delta_metrics (
    delta_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'revenue', 'cost', 'profit', 'volume', 'quality'
    metric_category VARCHAR(100), -- 'product', 'customer', 'operation', 'financial'
    metric_name VARCHAR(200) NOT NULL,
    current_value DECIMAL(15,4),
    previous_value DECIMAL(15,4),
    delta_value DECIMAL(15,4),
    delta_percentage DECIMAL(8,4),
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),
    variance_from_target DECIMAL(15,4),
    variance_percentage DECIMAL(8,4),
    trend_direction VARCHAR(20), -- 'increasing', 'decreasing', 'stable'
    trend_strength DECIMAL(5,4),
    seasonality_factor DECIMAL(5,4),
    external_impact_factor DECIMAL(5,4),
    internal_impact_factor DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, metric_date, metric_type, metric_name)
);

-- 动态反馈配置表
CREATE TABLE dynamic_feedback_config (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    config_name VARCHAR(200) NOT NULL,
    config_type VARCHAR(50) NOT NULL, -- 'threshold', 'trend', 'anomaly', 'performance'
    trigger_condition JSONB NOT NULL,
    trigger_threshold DECIMAL(15,4),
    trigger_operator VARCHAR(10), -- '>', '<', '=', '>=', '<=', '!='
    action_type VARCHAR(50) NOT NULL, -- 'alert', 'adjust', 'optimize', 'retrain'
    action_parameters JSONB,
    feedback_mechanism VARCHAR(50), -- 'automatic', 'manual', 'hybrid'
    feedback_frequency VARCHAR(20), -- 'real_time', 'hourly', 'daily', 'weekly'
    is_active BOOLEAN DEFAULT true,
    priority_level VARCHAR(20), -- 'high', 'medium', 'low'
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, config_name)
);

-- 模型参数存储表
CREATE TABLE model_parameters_storage (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    model_name VARCHAR(200) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'marginal_analysis', 'time_series', 'npv', 'capability_value'
    model_version VARCHAR(20) NOT NULL,
    model_parameters JSONB NOT NULL,
    model_weights JSONB,
    feature_importance JSONB,
    performance_metrics JSONB,
    training_data_hash VARCHAR(64),
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validation_score DECIMAL(8,6),
    cross_validation_scores JSONB,
    model_status VARCHAR(20) DEFAULT 'active', -- 'active', 'deprecated', 'testing'
    is_production BOOLEAN DEFAULT false,
    created_by UUID REFERENCES user_profiles(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, model_name, model_version)
);

-- 创建索引
CREATE INDEX idx_core_asset_tenant ON core_asset_master(tenant_id);
CREATE INDEX idx_core_asset_type ON core_asset_master(asset_type);
CREATE INDEX idx_core_asset_active ON core_asset_master(is_active);

CREATE INDEX idx_core_capability_tenant ON core_capability_master(tenant_id);
CREATE INDEX idx_core_capability_type ON core_capability_master(capability_type);
CREATE INDEX idx_core_capability_active ON core_capability_master(is_active);

CREATE INDEX idx_product_value_tenant ON product_value_item_master(tenant_id);
CREATE INDEX idx_product_value_type ON product_value_item_master(value_type);
CREATE INDEX idx_product_value_active ON product_value_item_master(is_active);

CREATE INDEX idx_monthly_delta_tenant ON monthly_delta_metrics(tenant_id);
CREATE INDEX idx_monthly_delta_date ON monthly_delta_metrics(metric_date);
CREATE INDEX idx_monthly_delta_type ON monthly_delta_metrics(metric_type);

CREATE INDEX idx_dynamic_feedback_tenant ON dynamic_feedback_config(tenant_id);
CREATE INDEX idx_dynamic_feedback_type ON dynamic_feedback_config(config_type);
CREATE INDEX idx_dynamic_feedback_active ON dynamic_feedback_config(is_active);

CREATE INDEX idx_model_params_tenant ON model_parameters_storage(tenant_id);
CREATE INDEX idx_model_params_type ON model_parameters_storage(model_type);
CREATE INDEX idx_model_params_status ON model_parameters_storage(model_status);

-- 启用RLS
ALTER TABLE core_asset_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_capability_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_value_item_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_delta_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE dynamic_feedback_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_parameters_storage ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
CREATE POLICY tenant_isolation_policy_core_asset ON core_asset_master
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_core_capability ON core_capability_master
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_product_value ON product_value_item_master
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_monthly_delta ON monthly_delta_metrics
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_dynamic_feedback ON dynamic_feedback_config
    USING (
        tenant_id = get_user_tenant_id(auth.uid())
        OR has_role(auth.uid(), 'admin')
        OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

CREATE POLICY tenant_isolation_policy_model_params ON model_parameters_storage
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
CREATE TRIGGER update_core_asset_updated_at BEFORE UPDATE ON core_asset_master
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_core_capability_updated_at BEFORE UPDATE ON core_capability_master
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_value_updated_at BEFORE UPDATE ON product_value_item_master
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dynamic_feedback_updated_at BEFORE UPDATE ON dynamic_feedback_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_params_updated_at BEFORE UPDATE ON model_parameters_storage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

