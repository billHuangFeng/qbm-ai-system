-- ============================================
-- 为业务表添加 tenant_id 并启用 RLS
-- ============================================

-- 1. 为所有业务表添加 tenant_id 字段
ALTER TABLE public.dim_vpt ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_pft ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_customer ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_channel ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_sku ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_activity ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_media_channel ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_conv_channel ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.dim_supplier ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);

ALTER TABLE public.fact_order ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.fact_voice ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.fact_expense ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.fact_produce ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.fact_supplier ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);

ALTER TABLE public.bridge_media_vpt ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.bridge_conv_vpt ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.bridge_sku_pft ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.bridge_vpt_pft ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);
ALTER TABLE public.bridge_attribution ADD COLUMN tenant_id UUID REFERENCES public.tenants(tenant_id);

-- 2. 启用 RLS
ALTER TABLE public.dim_vpt ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_pft ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_customer ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_channel ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_sku ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_media_channel ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_conv_channel ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_supplier ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.fact_order ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_voice ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_expense ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_produce ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_supplier ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.bridge_media_vpt ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bridge_conv_vpt ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bridge_sku_pft ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bridge_vpt_pft ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bridge_attribution ENABLE ROW LEVEL SECURITY;

-- 3. 创建 RLS 策略（统一模板）
-- 用户可以查看和管理自己租户的数据
CREATE POLICY "tenant_isolation_policy" ON public.dim_vpt
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_pft
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_customer
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_channel
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_sku
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_activity
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_media_channel
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_conv_channel
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.dim_supplier
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.fact_order
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.fact_voice
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.fact_expense
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.fact_produce
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.fact_supplier
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.bridge_media_vpt
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.bridge_conv_vpt
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.bridge_sku_pft
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.bridge_vpt_pft
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);

CREATE POLICY "tenant_isolation_policy" ON public.bridge_attribution
FOR ALL TO authenticated
USING (
  tenant_id = public.get_user_tenant_id(auth.uid())
  OR public.has_role(auth.uid(), 'admin')
  OR (public.has_role(auth.uid(), 'analyst') AND public.has_cross_tenant_access(auth.uid(), tenant_id))
);