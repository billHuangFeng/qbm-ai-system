-- AI 影响传播引擎 - 数据表

-- 分析结果
CREATE TABLE IF NOT EXISTS influence_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 优化记录
CREATE TABLE IF NOT EXISTS influence_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objective VARCHAR(50) NOT NULL,
    constraints JSONB,
    selected_paths JSONB,
    total_score DECIMAL(8,3),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);



