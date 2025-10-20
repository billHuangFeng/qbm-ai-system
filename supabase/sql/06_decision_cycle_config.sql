-- 决策循环触发配置表
CREATE TABLE decision_cycle_trigger_config (
    trigger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_type VARCHAR(50),
    trigger_name VARCHAR(100),
    trigger_condition TEXT,
    schedule_expression VARCHAR(100),
    threshold_metric VARCHAR(50),
    threshold_value DECIMAL(10,4),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 决策循环执行记录表
CREATE TABLE decision_cycle_execution (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_id UUID REFERENCES decision_cycle_trigger_config(trigger_id),
    execution_start TIMESTAMP WITH TIME ZONE,
    execution_end TIMESTAMP WITH TIME ZONE,
    execution_status VARCHAR(20),
    decisions_generated INT,
    execution_log JSONB
);
