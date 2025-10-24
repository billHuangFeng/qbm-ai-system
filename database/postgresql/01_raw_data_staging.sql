-- 原始数据暂存表
CREATE TABLE raw_data_staging (
    raw_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system VARCHAR(50) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL,
    file_path VARCHAR(500),
    import_method VARCHAR(50),
    import_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    processed_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_raw_staging_status ON raw_data_staging(processing_status);
CREATE INDEX idx_raw_staging_source ON raw_data_staging(source_system, source_type);

-- 数据导入日志表
CREATE TABLE data_import_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    import_batch_id UUID,
    source_system VARCHAR(50),
    import_method VARCHAR(50),
    records_total INT,
    records_success INT,
    records_failed INT,
    import_start TIMESTAMP WITH TIME ZONE,
    import_end TIMESTAMP WITH TIME ZONE,
    import_status VARCHAR(20),
    error_details JSONB
);

-- 数据质量检查表
CREATE TABLE data_quality_check (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    check_type VARCHAR(50),
    check_result VARCHAR(20),
    check_message TEXT,
    check_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 数据映射配置表
CREATE TABLE data_mapping_config (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system VARCHAR(50),
    source_type VARCHAR(50),
    source_field VARCHAR(100),
    target_table VARCHAR(100),
    target_field VARCHAR(100),
    mapping_rule JSONB,
    validation_rule JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



