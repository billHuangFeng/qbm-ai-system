-- 费用开支事实表
CREATE TABLE fact_expense (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    expense_type VARCHAR(50),
    expense_amount DECIMAL(15,2),
    expense_date DATE,
    department VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 资产购置事实表
CREATE TABLE fact_asset_acquisition (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    asset_type VARCHAR(50),
    acquisition_cost DECIMAL(15,2),
    acquisition_date DATE,
    expected_life_years INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 采购目录管理表
CREATE TABLE catalog_procurement (
    catalog_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    material_id VARCHAR(50),
    supplier_id VARCHAR(50),
    approved_date DATE,
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 销售目录管理表
CREATE TABLE catalog_sales (
    catalog_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    product_id VARCHAR(50),
    customer_id VARCHAR(50),
    approved_date DATE,
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 研发项目表
CREATE TABLE fact_rd_project (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    project_name VARCHAR(100),
    budget DECIMAL(15,2),
    start_date DATE,
    expected_completion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 推广活动表
CREATE TABLE fact_promotion (
    promotion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID,
    raw_id UUID REFERENCES raw_data_staging(raw_id),
    promotion_name VARCHAR(100),
    budget DECIMAL(15,2),
    start_date DATE,
    end_date DATE,
    target_audience TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



