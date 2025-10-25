-- ============================================
-- BMOS 多租户架构 + RLS 策略
-- ============================================

-- 1. 创建角色枚举
CREATE TYPE public.app_role AS ENUM ('admin', 'analyst', 'manager', 'operator');

-- 2. 租户表（企业/组织）
CREATE TABLE public.tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_code VARCHAR(20) UNIQUE NOT NULL,
    tenant_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 用户配置表（关联到 auth.users）
CREATE TABLE public.user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    full_name VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 用户角色表（多对多关系）
CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role app_role NOT NULL,
    tenant_id UUID REFERENCES public.tenants(tenant_id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES auth.users(id),
    UNIQUE (user_id, role, tenant_id)
);

-- 5. 跨租户分析授权表（分析师专用）
CREATE TABLE public.cross_tenant_access (
    access_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analyst_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    tenant_id UUID REFERENCES public.tenants(tenant_id) ON DELETE CASCADE NOT NULL,
    access_level VARCHAR(20) DEFAULT 'read',
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ,
    UNIQUE (analyst_id, tenant_id)
);

-- ============================================
-- 安全函数（防止RLS递归）
-- ============================================

-- 检查用户是否有指定角色
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id
      AND role = _role
  )
$$;

-- 获取用户的租户ID
CREATE OR REPLACE FUNCTION public.get_user_tenant_id(_user_id UUID)
RETURNS UUID
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT tenant_id
  FROM public.user_profiles
  WHERE user_id = _user_id
$$;

-- 检查用户是否有跨租户访问权限
CREATE OR REPLACE FUNCTION public.has_cross_tenant_access(_user_id UUID, _tenant_id UUID)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.cross_tenant_access
    WHERE analyst_id = _user_id
      AND tenant_id = _tenant_id
      AND (expires_at IS NULL OR expires_at > NOW())
  )
$$;

-- ============================================
-- 启用RLS（基础表）
-- ============================================

ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cross_tenant_access ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS 策略：tenants 表
-- ============================================

CREATE POLICY "Admins can view all tenants"
ON public.tenants FOR SELECT
TO authenticated
USING (public.has_role(auth.uid(), 'admin'));

CREATE POLICY "Users can view own tenant"
ON public.tenants FOR SELECT
TO authenticated
USING (tenant_id = public.get_user_tenant_id(auth.uid()));

CREATE POLICY "Analysts can view authorized tenants"
ON public.tenants FOR SELECT
TO authenticated
USING (
  public.has_role(auth.uid(), 'analyst') 
  AND public.has_cross_tenant_access(auth.uid(), tenant_id)
);

-- ============================================
-- RLS 策略：user_profiles 表
-- ============================================

CREATE POLICY "Users can view own profile"
ON public.user_profiles FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can update own profile"
ON public.user_profiles FOR UPDATE
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Admins can view same tenant users"
ON public.user_profiles FOR SELECT
TO authenticated
USING (
  public.has_role(auth.uid(), 'admin')
  AND tenant_id = public.get_user_tenant_id(auth.uid())
);

-- ============================================
-- RLS 策略：user_roles 表
-- ============================================

CREATE POLICY "Users can view own roles"
ON public.user_roles FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Admins can manage same tenant roles"
ON public.user_roles FOR ALL
TO authenticated
USING (
  public.has_role(auth.uid(), 'admin')
  AND tenant_id = public.get_user_tenant_id(auth.uid())
);

-- ============================================
-- 自动创建用户配置的触发器
-- ============================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE PLPGSQL
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  default_tenant_id UUID;
BEGIN
  -- 获取或创建默认租户
  SELECT tenant_id INTO default_tenant_id
  FROM public.tenants
  WHERE tenant_code = 'T001'
  LIMIT 1;

  -- 如果没有默认租户，创建一个
  IF default_tenant_id IS NULL THEN
    INSERT INTO public.tenants (tenant_code, tenant_name, industry)
    VALUES ('T001', 'Default Organization', 'General')
    RETURNING tenant_id INTO default_tenant_id;
  END IF;

  -- 插入用户配置
  INSERT INTO public.user_profiles (user_id, tenant_id, email, full_name)
  VALUES (
    NEW.id,
    default_tenant_id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
  );

  -- 赋予默认角色 'operator'
  INSERT INTO public.user_roles (user_id, role, tenant_id)
  VALUES (NEW.id, 'operator', default_tenant_id);

  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- 示例数据
-- ============================================

INSERT INTO public.tenants (tenant_code, tenant_name, industry) VALUES
  ('T001', 'Demo Corporation', 'Manufacturing'),
  ('T002', 'Tech Solutions Ltd', 'Technology'),
  ('T003', 'Retail Global Inc', 'Retail');