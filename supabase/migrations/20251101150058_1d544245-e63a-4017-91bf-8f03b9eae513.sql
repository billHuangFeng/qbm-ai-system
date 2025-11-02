-- 修复RLS策略问题：为所有新创建的表添加RLS策略

DO $$
BEGIN
  -- 为所有新创建的表添加tenant_isolation_policy
  -- 如果策略已存在则跳过
  
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'raw_data_staging' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.raw_data_staging 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'data_import_log' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.data_import_log 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'data_quality_report' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.data_quality_report 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'data_version_control' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.data_version_control 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_fitting_config' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_fitting_config 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_model_training' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_model_training 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_impact_analysis' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_impact_analysis 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_dynamic_weights' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_dynamic_weights 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_synergy_analysis' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_synergy_analysis 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_threshold_analysis' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_threshold_analysis 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_lag_analysis' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_lag_analysis 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_predictions' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_predictions 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_optimization_recommendations' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_optimization_recommendations 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_model_performance' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_model_performance 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_weight_validation' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_weight_validation 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'marginal_ensemble_models' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.marginal_ensemble_models 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'decision_cycle_config' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.decision_cycle_config 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'decision_events' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.decision_events 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'decision_executions' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.decision_executions 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'decision_impact_evaluation' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.decision_impact_evaluation 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'controllable_facts' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.controllable_facts 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'external_business_facts' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.external_business_facts 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'manager_evaluation' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.manager_evaluation 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'decision_audit_trail' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.decision_audit_trail 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'periodic_report_config' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.periodic_report_config 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'report_instances' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.report_instances 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'alert_rules' 
    AND policyname = 'tenant_isolation_policy'
  ) THEN
    CREATE POLICY "tenant_isolation_policy" ON public.alert_rules 
    FOR ALL TO authenticated
    USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));
  END IF;
  
END $$;