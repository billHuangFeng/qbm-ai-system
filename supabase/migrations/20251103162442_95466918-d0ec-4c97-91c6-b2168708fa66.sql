-- 创建经营主体表
CREATE TABLE IF NOT EXISTS public.dim_business_entity (
    entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_code VARCHAR(50) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50),  -- '总部', '分公司', '子公司', '事业部'
    legal_name VARCHAR(255),  -- 法定名称
    tax_id VARCHAR(50),  -- 统一社会信用代码/税号
    region VARCHAR(100),
    address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, entity_code)
);

-- 创建部门表
CREATE TABLE IF NOT EXISTS public.dim_department (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_id UUID,  -- 关联经营主体
    department_code VARCHAR(50) NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    department_type VARCHAR(50),  -- '销售', '采购', '生产', '财务', '人力'
    parent_department_id UUID,  -- 上级部门（支持层级结构）
    department_level INTEGER DEFAULT 1,  -- 部门层级
    manager_id UUID,  -- 部门负责人
    cost_center VARCHAR(50),  -- 成本中心
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, department_code),
    FOREIGN KEY (parent_department_id) REFERENCES public.dim_department(department_id)
);

-- 创建员工表
CREATE TABLE IF NOT EXISTS public.dim_employee (
    employee_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_id UUID,  -- 关联经营主体
    department_id UUID,  -- 关联部门
    employee_code VARCHAR(50) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    employee_name_en VARCHAR(100),  -- 英文名
    gender VARCHAR(10),  -- '男', '女'
    birth_date DATE,
    mobile_phone VARCHAR(50),
    email VARCHAR(255),
    position VARCHAR(100),  -- 职位
    job_level VARCHAR(50),  -- 职级
    employment_type VARCHAR(50),  -- '正式', '合同', '实习', '外包'
    hire_date DATE,  -- 入职日期
    leave_date DATE,  -- 离职日期
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'inactive', 'resigned'
    supervisor_id UUID,  -- 直属上级
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, employee_code),
    FOREIGN KEY (department_id) REFERENCES public.dim_department(department_id),
    FOREIGN KEY (supervisor_id) REFERENCES public.dim_employee(employee_id)
);

-- 创建项目表
CREATE TABLE IF NOT EXISTS public.dim_project (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_id UUID,  -- 关联经营主体
    project_code VARCHAR(50) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(50),  -- '研发', '营销', '建设', '咨询'
    project_status VARCHAR(50) DEFAULT 'planning',  -- 'planning', 'in_progress', 'completed', 'suspended', 'cancelled'
    priority VARCHAR(20),  -- 'high', 'medium', 'low'
    start_date DATE,
    end_date DATE,
    planned_budget NUMERIC(18,2),
    actual_budget NUMERIC(18,2),
    project_manager_id UUID,  -- 项目经理
    sponsor_id UUID,  -- 项目发起人/赞助人
    department_id UUID,  -- 归属部门
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, project_code),
    FOREIGN KEY (project_manager_id) REFERENCES public.dim_employee(employee_id),
    FOREIGN KEY (department_id) REFERENCES public.dim_department(department_id)
);

-- 为经营主体表启用RLS
ALTER TABLE public.dim_business_entity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation_policy" ON public.dim_business_entity
    AS RESTRICTIVE
    USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 为部门表启用RLS
ALTER TABLE public.dim_department ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation_policy" ON public.dim_department
    AS RESTRICTIVE
    USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 为员工表启用RLS
ALTER TABLE public.dim_employee ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation_policy" ON public.dim_employee
    AS RESTRICTIVE
    USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 为项目表启用RLS
ALTER TABLE public.dim_project ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation_policy" ON public.dim_project
    AS RESTRICTIVE
    USING (
        tenant_id = get_user_tenant_id(auth.uid()) 
        OR has_role(auth.uid(), 'admin'::app_role)
        OR (has_role(auth.uid(), 'analyst'::app_role) AND has_cross_tenant_access(auth.uid(), tenant_id))
    );

-- 创建索引以提高查询性能
CREATE INDEX idx_business_entity_tenant ON public.dim_business_entity(tenant_id);
CREATE INDEX idx_business_entity_code ON public.dim_business_entity(tenant_id, entity_code);

CREATE INDEX idx_department_tenant ON public.dim_department(tenant_id);
CREATE INDEX idx_department_code ON public.dim_department(tenant_id, department_code);
CREATE INDEX idx_department_parent ON public.dim_department(parent_department_id);

CREATE INDEX idx_employee_tenant ON public.dim_employee(tenant_id);
CREATE INDEX idx_employee_code ON public.dim_employee(tenant_id, employee_code);
CREATE INDEX idx_employee_department ON public.dim_employee(department_id);
CREATE INDEX idx_employee_name ON public.dim_employee(tenant_id, employee_name);

CREATE INDEX idx_project_tenant ON public.dim_project(tenant_id);
CREATE INDEX idx_project_code ON public.dim_project(tenant_id, project_code);
CREATE INDEX idx_project_status ON public.dim_project(tenant_id, project_status);
CREATE INDEX idx_project_dates ON public.dim_project(start_date, end_date);

-- 为部门表添加更新时间戳触发器函数（如果不存在）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为各表添加自动更新updated_at的触发器
CREATE TRIGGER update_business_entity_updated_at
    BEFORE UPDATE ON public.dim_business_entity
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_department_updated_at
    BEFORE UPDATE ON public.dim_department
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_updated_at
    BEFORE UPDATE ON public.dim_employee
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_updated_at
    BEFORE UPDATE ON public.dim_project
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();