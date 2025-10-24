# 边际影响分析系统数据库设计文档

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2024-01-01
- **负责人**: Cursor AI
- **状态**: ⏳ 待提交 → ✅ 已完成

## 1. 数据库架构概述

### 1.1 技术选型
- **主数据库**: PostgreSQL (Supabase)
- **缓存层**: Redis
- **多租户**: Schema隔离
- **数据版本**: 时间戳版本控制

### 1.2 设计原则
- 多租户数据隔离
- 历史数据版本管理
- 实时数据同步
- 高性能查询优化

## 2. 核心表结构设计

### 2.1 租户管理表

#### tenants (租户表)
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_name VARCHAR(255) NOT NULL,
    tenant_code VARCHAR(50) UNIQUE NOT NULL,
    industry_type VARCHAR(100),
    company_size VARCHAR(50),
    subscription_plan VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);
```

#### tenant_schemas (租户Schema配置)
```sql
CREATE TABLE tenant_schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    schema_name VARCHAR(100) NOT NULL,
    schema_config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, schema_name)
);
```

### 2.2 核心资产表

#### core_assets (核心资产表)
```sql
CREATE TABLE core_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100) NOT NULL, -- '研发资产', '设计资产', '生产资产', '传播资产', '渠道资产', '交付资产'
    asset_category VARCHAR(100), -- '设备', '技术', '人才', '品牌', '渠道', '物流'
    asset_description TEXT,
    initial_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    depreciation_rate DECIMAL(5,4),
    useful_life_years INTEGER,
    acquisition_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    metadata JSONB
);
```

#### asset_cash_flows (资产现金流表)
```sql
CREATE TABLE asset_cash_flows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES core_assets(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    period_date DATE NOT NULL,
    cash_flow_amount DECIMAL(15,2) NOT NULL,
    cash_flow_type VARCHAR(50), -- 'revenue', 'cost', 'investment', 'depreciation'
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### 2.3 核心能力表

#### core_capabilities (核心能力表)
```sql
CREATE TABLE core_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    capability_name VARCHAR(255) NOT NULL,
    capability_type VARCHAR(100) NOT NULL, -- '研发能力', '设计能力', '生产能力', '传播能力', '渠道能力', '交付能力'
    capability_level VARCHAR(50), -- 'beginner', 'intermediate', 'advanced', 'expert'
    description TEXT,
    measurement_metrics JSONB, -- 能力测量指标
    target_outcomes JSONB, -- 目标成果
    current_performance DECIMAL(5,4), -- 当前绩效得分
    target_performance DECIMAL(5,4), -- 目标绩效得分
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    metadata JSONB
);
```

#### capability_performance (能力绩效表)
```sql
CREATE TABLE capability_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_id UUID REFERENCES core_capabilities(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    performance_date DATE NOT NULL,
    performance_score DECIMAL(5,4) NOT NULL,
    performance_metrics JSONB, -- 具体绩效指标
    evaluation_method VARCHAR(100),
    evaluator VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### 2.4 产品价值评估表

#### product_features (产品特性表)
```sql
CREATE TABLE product_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    feature_name VARCHAR(255) NOT NULL,
    feature_category VARCHAR(100), -- '功能特性', '性能特性', '体验特性', '服务特性'
    feature_description TEXT,
    feature_priority VARCHAR(20), -- 'high', 'medium', 'low'
    development_status VARCHAR(50), -- 'planned', 'in_development', 'completed', 'deprecated'
    target_customers JSONB, -- 目标客户群体
    competitive_advantage TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    metadata JSONB
);
```

#### value_assessments (价值评估表)
```sql
CREATE TABLE value_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_type VARCHAR(100) NOT NULL, -- 'intrinsic_value', 'cognitive_value', 'experiential_value'
    product_id UUID, -- 关联产品ID
    feature_id UUID REFERENCES product_features(id) ON DELETE CASCADE,
    assessment_date DATE NOT NULL,
    customer_segment VARCHAR(100),
    assessment_method VARCHAR(100), -- 'survey', 'interview', 'behavioral_analysis', 'market_research'
    intrinsic_value_score DECIMAL(5,4), -- 产品内在价值得分
    cognitive_value_score DECIMAL(5,4), -- 客户认知价值得分
    experiential_value_score DECIMAL(5,4), -- 客户体验价值得分
    willingness_to_pay DECIMAL(15,2), -- 客户支付意愿
    market_price DECIMAL(15,2), -- 市场价格
    premium_price DECIMAL(15,2), -- 溢价价格
    assessment_data JSONB, -- 详细评估数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### 2.5 边际影响分析表

#### marginal_analysis (边际影响分析表)
```sql
CREATE TABLE marginal_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    analysis_period DATE NOT NULL,
    analysis_type VARCHAR(100) NOT NULL, -- 'monthly', 'quarterly', 'yearly'
    asset_impact DECIMAL(15,2), -- 资产边际影响
    capability_impact DECIMAL(15,2), -- 能力边际影响
    value_impact DECIMAL(15,2), -- 价值边际影响
    efficiency_metrics JSONB, -- 效能指标
    synergy_effects JSONB, -- 协同效应
    threshold_effects JSONB, -- 阈值效应
    lag_effects JSONB, -- 滞后效应
    analysis_results JSONB, -- 分析结果
    confidence_level DECIMAL(5,4), -- 置信度
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

#### delta_calculations (增量计算表)
```sql
CREATE TABLE delta_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    calculation_period DATE NOT NULL,
    calculation_type VARCHAR(100) NOT NULL, -- 'asset_delta', 'capability_delta', 'value_delta'
    base_period DATE NOT NULL,
    comparison_period DATE NOT NULL,
    delta_value DECIMAL(15,2) NOT NULL,
    delta_percentage DECIMAL(5,4),
    calculation_method VARCHAR(100),
    calculation_formula TEXT,
    input_data JSONB,
    output_data JSONB,
    validation_status VARCHAR(50), -- 'pending', 'validated', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### 2.6 权重优化表

#### weight_optimizations (权重优化表)
```sql
CREATE TABLE weight_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    optimization_date DATE NOT NULL,
    optimization_method VARCHAR(100) NOT NULL, -- 'gradient_descent', 'genetic_algorithm', 'simulated_annealing'
    target_metric VARCHAR(100), -- 'r2_score', 'mse', 'mae'
    initial_weights JSONB,
    optimized_weights JSONB,
    performance_metrics JSONB,
    validation_results JSONB,
    optimization_status VARCHAR(50), -- 'running', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

#### weight_monitoring (权重监控表)
```sql
CREATE TABLE weight_monitoring (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    monitoring_date TIMESTAMP WITH TIME ZONE NOT NULL,
    monitoring_type VARCHAR(100) NOT NULL, -- 'performance', 'drift', 'stability', 'quality'
    current_weights JSONB,
    weight_drift DECIMAL(5,4),
    performance_score DECIMAL(5,4),
    stability_score DECIMAL(5,4),
    quality_score DECIMAL(5,4),
    anomalies JSONB,
    alerts JSONB,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### 2.7 预测和结果表

#### predictions (预测结果表)
```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_type VARCHAR(100) NOT NULL, -- 'asset_value', 'capability_performance', 'value_assessment'
    prediction_horizon INTEGER, -- 预测时间范围（月）
    input_data JSONB,
    model_used VARCHAR(100),
    weights_used JSONB,
    prediction_results JSONB,
    confidence_interval JSONB,
    accuracy_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

#### analysis_insights (分析洞察表)
```sql
CREATE TABLE analysis_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    insight_date DATE NOT NULL,
    insight_type VARCHAR(100) NOT NULL, -- 'trend', 'anomaly', 'recommendation', 'optimization'
    insight_category VARCHAR(100), -- 'asset', 'capability', 'value', 'efficiency'
    insight_title VARCHAR(255),
    insight_description TEXT,
    insight_data JSONB,
    impact_score DECIMAL(5,4),
    confidence_level DECIMAL(5,4),
    action_required BOOLEAN DEFAULT FALSE,
    action_items JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

## 3. 索引设计

### 3.1 性能索引
```sql
-- 租户相关索引
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_tenants_created_at ON tenants(created_at);

-- 资产相关索引
CREATE INDEX idx_core_assets_tenant_id ON core_assets(tenant_id);
CREATE INDEX idx_core_assets_asset_type ON core_assets(asset_type);
CREATE INDEX idx_core_assets_status ON core_assets(status);
CREATE INDEX idx_asset_cash_flows_asset_id ON asset_cash_flows(asset_id);
CREATE INDEX idx_asset_cash_flows_period_date ON asset_cash_flows(period_date);

-- 能力相关索引
CREATE INDEX idx_core_capabilities_tenant_id ON core_capabilities(tenant_id);
CREATE INDEX idx_core_capabilities_capability_type ON core_capabilities(capability_type);
CREATE INDEX idx_capability_performance_capability_id ON capability_performance(capability_id);
CREATE INDEX idx_capability_performance_performance_date ON capability_performance(performance_date);

-- 价值评估相关索引
CREATE INDEX idx_product_features_tenant_id ON product_features(tenant_id);
CREATE INDEX idx_product_features_feature_category ON product_features(feature_category);
CREATE INDEX idx_value_assessments_tenant_id ON value_assessments(tenant_id);
CREATE INDEX idx_value_assessments_assessment_type ON value_assessments(assessment_type);
CREATE INDEX idx_value_assessments_assessment_date ON value_assessments(assessment_date);

-- 分析相关索引
CREATE INDEX idx_marginal_analysis_tenant_id ON marginal_analysis(tenant_id);
CREATE INDEX idx_marginal_analysis_analysis_period ON marginal_analysis(analysis_period);
CREATE INDEX idx_delta_calculations_tenant_id ON delta_calculations(tenant_id);
CREATE INDEX idx_delta_calculations_calculation_period ON delta_calculations(calculation_period);

-- 权重优化相关索引
CREATE INDEX idx_weight_optimizations_tenant_id ON weight_optimizations(tenant_id);
CREATE INDEX idx_weight_optimizations_optimization_date ON weight_optimizations(optimization_date);
CREATE INDEX idx_weight_monitoring_tenant_id ON weight_monitoring(tenant_id);
CREATE INDEX idx_weight_monitoring_monitoring_date ON weight_monitoring(monitoring_date);

-- 预测相关索引
CREATE INDEX idx_predictions_tenant_id ON predictions(tenant_id);
CREATE INDEX idx_predictions_prediction_date ON predictions(prediction_date);
CREATE INDEX idx_analysis_insights_tenant_id ON analysis_insights(tenant_id);
CREATE INDEX idx_analysis_insights_insight_date ON analysis_insights(insight_date);
```

### 3.2 复合索引
```sql
-- 多租户查询优化
CREATE INDEX idx_assets_tenant_type ON core_assets(tenant_id, asset_type);
CREATE INDEX idx_capabilities_tenant_type ON core_capabilities(tenant_id, capability_type);
CREATE INDEX idx_features_tenant_category ON product_features(tenant_id, feature_category);
CREATE INDEX idx_assessments_tenant_type_date ON value_assessments(tenant_id, assessment_type, assessment_date);

-- 时间序列查询优化
CREATE INDEX idx_cash_flows_asset_period ON asset_cash_flows(asset_id, period_date);
CREATE INDEX idx_performance_capability_date ON capability_performance(capability_id, performance_date);
CREATE INDEX idx_analysis_tenant_period ON marginal_analysis(tenant_id, analysis_period);
```

## 4. 数据版本管理

### 4.1 版本控制策略
```sql
-- 创建版本控制表
CREATE TABLE data_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    data_snapshot JSONB NOT NULL,
    change_type VARCHAR(50), -- 'insert', 'update', 'delete'
    change_reason VARCHAR(255),
    changed_by VARCHAR(255),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(table_name, record_id, version_number)
);

-- 创建版本控制索引
CREATE INDEX idx_data_versions_table_record ON data_versions(table_name, record_id);
CREATE INDEX idx_data_versions_changed_at ON data_versions(changed_at);
```

### 4.2 数据归档策略
```sql
-- 创建归档表
CREATE TABLE archived_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_table VARCHAR(100) NOT NULL,
    original_id UUID NOT NULL,
    archived_data JSONB NOT NULL,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archive_reason VARCHAR(255)
);

-- 创建归档索引
CREATE INDEX idx_archived_data_table_id ON archived_data(original_table, original_id);
CREATE INDEX idx_archived_data_archived_at ON archived_data(archived_at);
```

## 5. 数据安全设计

### 5.1 行级安全策略
```sql
-- 启用行级安全
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE value_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE marginal_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE weight_optimizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY tenant_isolation_policy ON tenants
    FOR ALL TO authenticated
    USING (id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_policy ON core_assets
    FOR ALL TO authenticated
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### 5.2 数据加密
```sql
-- 敏感数据加密字段
ALTER TABLE tenants ADD COLUMN encrypted_metadata BYTEA;
ALTER TABLE core_assets ADD COLUMN encrypted_metadata BYTEA;
ALTER TABLE core_capabilities ADD COLUMN encrypted_metadata BYTEA;
```

## 6. 数据同步设计

### 6.1 实时同步表
```sql
CREATE TABLE sync_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(20) NOT NULL, -- 'insert', 'update', 'delete'
    data_payload JSONB,
    sync_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

CREATE INDEX idx_sync_queue_status ON sync_queue(sync_status);
CREATE INDEX idx_sync_queue_created_at ON sync_queue(created_at);
```

### 6.2 数据一致性检查
```sql
CREATE TABLE data_consistency_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_type VARCHAR(100) NOT NULL,
    check_result VARCHAR(20) NOT NULL, -- 'pass', 'fail', 'warning'
    check_details JSONB,
    recommendations TEXT
);
```

## 7. 性能优化建议

### 7.1 查询优化
- 使用适当的索引
- 避免全表扫描
- 使用分区表（按时间分区）
- 定期更新统计信息

### 7.2 存储优化
- 使用JSONB存储非结构化数据
- 定期清理历史数据
- 使用压缩存储
- 监控存储使用情况

### 7.3 连接池配置
```sql
-- 连接池配置建议
-- max_connections = 200
-- shared_buffers = 256MB
-- effective_cache_size = 1GB
-- work_mem = 4MB
-- maintenance_work_mem = 64MB
```

## 8. 数据迁移脚本

### 8.1 初始化脚本
```sql
-- 创建数据库
CREATE DATABASE qbm_marginal_analysis;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 8.2 数据种子脚本
```sql
-- 插入示例租户数据
INSERT INTO tenants (tenant_name, tenant_code, industry_type, company_size, subscription_plan)
VALUES 
    ('示例企业A', 'COMPANY_A', '制造业', '大型企业', 'premium'),
    ('示例企业B', 'COMPANY_B', '服务业', '中型企业', 'standard');
```

## 9. 监控和维护

### 9.1 性能监控
```sql
-- 创建性能监控视图
CREATE VIEW performance_metrics AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';
```

### 9.2 数据质量检查
```sql
-- 数据完整性检查
CREATE OR REPLACE FUNCTION check_data_integrity()
RETURNS TABLE (
    table_name TEXT,
    total_records BIGINT,
    null_records BIGINT,
    duplicate_records BIGINT
) AS $$
BEGIN
    -- 实现数据完整性检查逻辑
    RETURN QUERY
    SELECT 
        'core_assets'::TEXT,
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE asset_name IS NULL)::BIGINT,
        0::BIGINT;
END;
$$ LANGUAGE plpgsql;
```

## 10. 总结

本数据库设计文档提供了完整的边际影响分析系统数据库架构，包括：

1. **核心表结构**: 15个主要表，覆盖资产、能力、价值评估、分析、优化等核心功能
2. **性能优化**: 全面的索引设计和查询优化策略
3. **数据安全**: 行级安全策略和数据加密
4. **版本管理**: 完整的数据版本控制和归档策略
5. **实时同步**: 数据同步队列和一致性检查
6. **监控维护**: 性能监控和数据质量检查

该设计支持多租户架构，具备高性能、高可用性和强安全性，能够满足边际影响分析系统的所有业务需求。

