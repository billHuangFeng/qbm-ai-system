-- 管理者评价记录表
CREATE TABLE manager_evaluation (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID,
    manager_id UUID,
    evaluation_type VARCHAR(50),
    evaluation_content TEXT,
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20)
);

-- 数据澄清记录表
CREATE TABLE data_clarification (
    clarification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_data_id UUID,
    clarification_reason TEXT,
    clarified_value TEXT,
    clarified_by UUID,
    clarified_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 指标确认记录表
CREATE TABLE metric_confirmation (
    confirmation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_id UUID,
    confirmed_value DECIMAL(10,4),
    confidence_level DECIMAL(3,2),
    confirmed_by UUID,
    confirmation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);




