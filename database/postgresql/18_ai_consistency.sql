-- AI 一致性引擎 - 数据表

-- 策略规则
CREATE TABLE IF NOT EXISTS consistency_policies (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(200) NOT NULL,
    rule_definition JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_consistency_policies_active
    ON consistency_policies (is_active);

-- 记录一致性检查结果摘要（可选）
CREATE TABLE IF NOT EXISTS consistency_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    check_type VARCHAR(50) NOT NULL,  -- policy / conflicts
    result_summary JSONB NOT NULL,
    score DECIMAL(5,4),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


