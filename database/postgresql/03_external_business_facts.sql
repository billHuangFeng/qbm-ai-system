-- 市场价格变化表
CREATE TABLE fact_market_price (
    price_record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    product_category VARCHAR(50),
    price_value DECIMAL(10,2),
    price_date DATE,
    market_source VARCHAR(50),
    change_rate DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 竞争对手动态表
CREATE TABLE fact_competitor_dynamics (
    dynamics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    competitor_name VARCHAR(100),
    dynamics_type VARCHAR(50),
    dynamics_description TEXT,
    impact_assessment TEXT,
    record_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 客户声音事实表（扩展现有表）
CREATE TABLE fact_voice (
    voice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    customer_id VARCHAR(50),
    voice_type VARCHAR(50),
    voice_content TEXT,
    sentiment_score DECIMAL(3,2),
    impact_level VARCHAR(20),
    response_required BOOLEAN,
    record_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);





