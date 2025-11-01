-- Migration: 001_initial_schema
-- Created: 2025-10-22
-- Description: 创建初始数据库架构，包括多租户支持和核心表结构

-- 创建多租户Schema
CREATE SCHEMA IF NOT EXISTS tenant_001;
CREATE SCHEMA IF NOT EXISTS tenant_002;

-- 设置默认搜索路径
SET search_path TO public, tenant_001, tenant_002;

-- 创建租户管理表
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) UNIQUE NOT NULL,
    tenant_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- 创建历史数据表
CREATE TABLE IF NOT EXISTS historical_data (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    data_id VARCHAR(255) UNIQUE NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_date TIMESTAMP NOT NULL,
    period_type VARCHAR(20) NOT NULL,
    
    -- 核心资产数据
    rd_asset DECIMAL(15,2),
    design_asset DECIMAL(15,2),
    production_asset DECIMAL(15,2),
    marketing_asset DECIMAL(15,2),
    delivery_asset DECIMAL(15,2),
    channel_asset DECIMAL(15,2),
    
    -- 核心能力数据
    rd_capability DECIMAL(15,2),
    design_capability DECIMAL(15,2),
    production_capability DECIMAL(15,2),
    marketing_capability DECIMAL(15,2),
    delivery_capability DECIMAL(15,2),
    channel_capability DECIMAL(15,2),
    
    -- 产品价值数据
    product_intrinsic_value DECIMAL(15,2),
    customer_cognitive_value DECIMAL(15,2),
    customer_experiential_value DECIMAL(15,2),
    product_feature_valuation DECIMAL(15,2),
    product_cost_advantage DECIMAL(15,2),
    
    -- 收入数据
    first_order_revenue DECIMAL(15,2),
    repurchase_revenue DECIMAL(15,2),
    upsell_revenue DECIMAL(15,2),
    total_revenue DECIMAL(15,2),
    profit DECIMAL(15,2),
    
    -- 效能数据
    product_efficiency DECIMAL(15,2),
    production_efficiency DECIMAL(15,2),
    rd_efficiency DECIMAL(15,2),
    marketing_efficiency DECIMAL(15,2),
    delivery_efficiency DECIMAL(15,2),
    channel_efficiency DECIMAL(15,2),
    
    -- 元数据
    data_source VARCHAR(255),
    data_quality_score DECIMAL(5,2),
    raw_data JSONB,
    metadata JSONB,
    
    -- 数据状态
    is_validated VARCHAR(10) DEFAULT 'pending',
    validation_notes TEXT,
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- 创建拟合模型表
CREATE TABLE IF NOT EXISTS fitted_models (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) UNIQUE NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_parameters JSONB,
    model_metrics JSONB,
    model_file_path VARCHAR(500),
    training_data_size INTEGER,
    training_duration_seconds INTEGER,
    status VARCHAR(50) DEFAULT 'training',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- 创建预测结果表
CREATE TABLE IF NOT EXISTS prediction_results (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    prediction_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    input_data JSONB NOT NULL,
    prediction_data JSONB NOT NULL,
    confidence_score DECIMAL(5,2),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (model_id) REFERENCES fitted_models(model_id)
);

-- 创建优化建议表
CREATE TABLE IF NOT EXISTS optimization_recommendations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    recommendation_id VARCHAR(255) UNIQUE NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    impact_score DECIMAL(5,2),
    implementation_effort VARCHAR(20),
    expected_roi DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- 创建模型性能监控表
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    threshold_value DECIMAL(15,6),
    is_alert BOOLEAN DEFAULT FALSE,
    alert_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (model_id) REFERENCES fitted_models(model_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_historical_data_tenant_date ON historical_data(tenant_id, data_date);
CREATE INDEX IF NOT EXISTS idx_historical_data_type ON historical_data(data_type);
CREATE INDEX IF NOT EXISTS idx_fitted_models_tenant ON fitted_models(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fitted_models_type ON fitted_models(model_type);
CREATE INDEX IF NOT EXISTS idx_prediction_results_tenant ON prediction_results(tenant_id);
CREATE INDEX IF NOT EXISTS idx_prediction_results_model ON prediction_results(model_id);
CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_tenant ON optimization_recommendations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_model_performance_tenant_model ON model_performance(tenant_id, model_id);

-- 创建触发器函数用于自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加updated_at触发器
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_historical_data_updated_at BEFORE UPDATE ON historical_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fitted_models_updated_at BEFORE UPDATE ON fitted_models FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prediction_results_updated_at BEFORE UPDATE ON prediction_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_optimization_recommendations_updated_at BEFORE UPDATE ON optimization_recommendations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始租户数据
INSERT INTO tenants (tenant_id, tenant_name, schema_name, created_by) VALUES
('tenant_001', 'Enterprise 001', 'tenant_001', 'system'),
('tenant_002', 'Enterprise 002', 'tenant_002', 'system')
ON CONFLICT (tenant_id) DO NOTHING;

-- 插入初始用户数据
INSERT INTO users (tenant_id, user_id, username, email, password_hash, role, created_by) VALUES
('tenant_001', 'user_001', 'admin_001', 'admin@enterprise001.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8', 'admin', 'system'),
('tenant_002', 'user_002', 'admin_002', 'admin@enterprise002.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8', 'admin', 'system')
ON CONFLICT (email) DO NOTHING;




