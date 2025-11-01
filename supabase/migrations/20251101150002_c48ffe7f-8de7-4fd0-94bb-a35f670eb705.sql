-- 修复RLS策略问题：为所有新创建的表添加RLS策略
-- 使用DROP + CREATE方式确保策略正确创建

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.raw_data_staging;
CREATE POLICY "tenant_isolation_policy" ON public.raw_data_staging 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.data_import_log;
CREATE POLICY "tenant_isolation_policy" ON public.data_import_log 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.data_quality_report;
CREATE POLICY "tenant_isolation_policy" ON public.data_quality_report 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.data_version_control;
CREATE POLICY "tenant_isolation_policy" ON public.data_version_control 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_fitting_config;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_fitting_config 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_model_training;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_model_training 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_impact_analysis;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_impact_analysis 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_dynamic_weights;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_dynamic_weights 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_synergy_analysis;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_synergy_analysis 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_threshold_analysis;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_threshold_analysis 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_lag_analysis;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_lag_analysis 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_predictions;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_predictions 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_optimization_recommendations;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_optimization_recommendations 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_model_performance;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_model_performance 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_weight_validation;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_weight_validation 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.marginal_ensemble_models;
CREATE POLICY "tenant_isolation_policy" ON public.marginal_ensemble_models 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.decision_cycle_config;
CREATE POLICY "tenant_isolation_policy" ON public.decision_cycle_config 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.decision_events;
CREATE POLICY "tenant_isolation_policy" ON public.decision_events 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.decision_executions;
CREATE POLICY "tenant_isolation_policy" ON public.decision_executions 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.decision_impact_evaluation;
CREATE POLICY "tenant_isolation_policy" ON public.decision_impact_evaluation 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.controllable_facts;
CREATE POLICY "tenant_isolation_policy" ON public.controllable_facts 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.external_business_facts;
CREATE POLICY "tenant_isolation_policy" ON public.external_business_facts 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.manager_evaluation;
CREATE POLICY "tenant_isolation_policy" ON public.manager_evaluation 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.decision_audit_trail;
CREATE POLICY "tenant_isolation_policy" ON public.decision_audit_trail 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.periodic_report_config;
CREATE POLICY "tenant_isolation_policy" ON public.periodic_report_config 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.report_instances;
CREATE POLICY "tenant_isolation_policy" ON public.report_instances 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));

DROP POLICY IF EXISTS "tenant_isolation_policy" ON public.alert_rules;
CREATE POLICY "tenant_isolation_policy" ON public.alert_rules 
FOR ALL TO authenticated
USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), 'admin') OR (has_role(auth.uid(), 'analyst') AND has_cross_tenant_access(auth.uid(), tenant_id)));