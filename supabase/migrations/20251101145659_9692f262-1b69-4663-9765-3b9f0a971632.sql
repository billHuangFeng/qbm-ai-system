-- ========================================
-- Phase 1: 创建27张数据库表
-- ========================================

-- ========================================
-- 1. 原始数据层（4张表）
-- ========================================

-- 1.1 原始数据暂存表
CREATE TABLE IF NOT EXISTS public.raw_data_staging (
  staging_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 文件信息
  file_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),
  file_size_kb INTEGER,
  
  -- 单据类型
  document_type VARCHAR(50),
  
  -- 格式识别结果
  detected_format VARCHAR(50),
  format_confidence DECIMAL(5,2),
  format_characteristics JSONB,
  
  -- 原始数据
  raw_data JSONB,
  row_count INTEGER,
  column_count INTEGER,
  
  -- 处理状态
  upload_status VARCHAR(20) DEFAULT 'pending',
  quality_score DECIMAL(5,2),
  error_message TEXT,
  
  -- 处理结果
  processed_row_count INTEGER,
  failed_row_count INTEGER,
  processing_duration_ms INTEGER,
  
  -- 元数据
  uploaded_by UUID REFERENCES auth.users(id),
  uploaded_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.2 数据导入日志表
CREATE TABLE IF NOT EXISTS public.data_import_log (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  staging_id UUID REFERENCES public.raw_data_staging(staging_id),
  
  -- 导入信息
  import_type VARCHAR(50),
  target_table VARCHAR(100),
  
  -- 统计信息
  total_rows INTEGER,
  success_rows INTEGER,
  failed_rows INTEGER,
  duplicate_rows INTEGER,
  
  -- 错误详情
  error_details JSONB,
  
  -- 性能指标
  import_duration_ms INTEGER,
  rows_per_second DECIMAL(10,2),
  
  -- 元数据
  imported_by UUID REFERENCES auth.users(id),
  imported_at TIMESTAMPTZ DEFAULT NOW(),
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.3 数据质量报告表
CREATE TABLE IF NOT EXISTS public.data_quality_report (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  staging_id UUID REFERENCES public.raw_data_staging(staging_id),
  
  -- 质量评分
  overall_quality_score DECIMAL(5,2),
  completeness_score DECIMAL(5,2),
  accuracy_score DECIMAL(5,2),
  consistency_score DECIMAL(5,2),
  
  -- 质量问题
  missing_field_count INTEGER,
  invalid_format_count INTEGER,
  duplicate_count INTEGER,
  outlier_count INTEGER,
  
  -- 详细问题清单
  quality_issues JSONB,
  
  -- 验证规则
  validation_rules JSONB,
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 1.4 数据版本控制表
CREATE TABLE IF NOT EXISTS public.data_version_control (
  version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 版本信息
  data_type VARCHAR(50),
  version_number INTEGER,
  version_date DATE,
  
  -- 变更信息
  change_type VARCHAR(50),
  change_description TEXT,
  affected_rows INTEGER,
  change_details JSONB,
  
  -- 数据快照
  snapshot_file_path VARCHAR(500),
  
  -- 元数据
  changed_by UUID REFERENCES auth.users(id),
  is_current BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- 2. 边际分析层（12张表）
-- ========================================

-- 2.1 历史数据拟合配置表
CREATE TABLE IF NOT EXISTS public.marginal_fitting_config (
  config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 配置信息
  config_name VARCHAR(255) NOT NULL,
  analysis_type VARCHAR(50),
  
  -- 拟合参数
  fitting_method VARCHAR(50),
  time_window_months INTEGER,
  min_data_points INTEGER,
  confidence_level DECIMAL(5,2),
  
  -- 算法参数
  algorithm_params JSONB,
  
  -- 状态
  is_active BOOLEAN DEFAULT TRUE,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.2 模型训练记录表
CREATE TABLE IF NOT EXISTS public.marginal_model_training (
  training_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  config_id UUID REFERENCES public.marginal_fitting_config(config_id),
  
  -- 训练信息
  model_type VARCHAR(50),
  model_version VARCHAR(50),
  training_date DATE,
  
  -- 数据集信息
  training_data_start_date DATE,
  training_data_end_date DATE,
  training_samples INTEGER,
  validation_samples INTEGER,
  
  -- 训练结果
  training_duration_ms INTEGER,
  training_status VARCHAR(50),
  
  -- 模型性能
  r_squared DECIMAL(10,6),
  mae DECIMAL(10,6),
  rmse DECIMAL(10,6),
  mape DECIMAL(10,6),
  
  -- 模型参数
  model_params JSONB,
  feature_importance JSONB,
  
  -- 元数据
  trained_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.3 边际影响分析结果表
CREATE TABLE IF NOT EXISTS public.marginal_impact_analysis (
  analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 分析目标
  target_metric VARCHAR(100),
  analysis_date DATE,
  
  -- 输入变量
  input_variable VARCHAR(100),
  baseline_value DECIMAL(15,4),
  
  -- 边际影响
  marginal_impact DECIMAL(15,6),
  elasticity DECIMAL(10,6),
  
  -- 置信区间
  confidence_lower DECIMAL(15,6),
  confidence_upper DECIMAL(15,6),
  
  -- 统计显著性
  p_value DECIMAL(10,8),
  is_significant BOOLEAN,
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.4 动态权重学习表
CREATE TABLE IF NOT EXISTS public.marginal_dynamic_weights (
  weight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 权重信息
  factor_name VARCHAR(100),
  factor_type VARCHAR(50),
  
  -- 初始权重
  initial_weight DECIMAL(10,6),
  
  -- 学习后权重
  learned_weight DECIMAL(10,6),
  weight_change_pct DECIMAL(10,4),
  
  -- 权重置信度
  weight_confidence DECIMAL(5,2),
  
  -- 时间衰减
  time_decay_factor DECIMAL(10,6),
  
  -- 元数据
  effective_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.5 协同效应分析表
CREATE TABLE IF NOT EXISTS public.marginal_synergy_analysis (
  synergy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 协同因素
  factor_a VARCHAR(100),
  factor_b VARCHAR(100),
  
  -- 单独效应
  factor_a_impact DECIMAL(15,6),
  factor_b_impact DECIMAL(15,6),
  
  -- 协同效应
  combined_impact DECIMAL(15,6),
  synergy_value DECIMAL(15,6),
  synergy_type VARCHAR(50),
  
  -- 统计显著性
  p_value DECIMAL(10,8),
  is_significant BOOLEAN,
  
  -- 元数据
  analysis_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.6 阈值效应分析表
CREATE TABLE IF NOT EXISTS public.marginal_threshold_analysis (
  threshold_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 变量信息
  variable_name VARCHAR(100),
  
  -- 阈值点
  threshold_value DECIMAL(15,4),
  threshold_confidence DECIMAL(5,2),
  
  -- 阈值前后影响
  impact_before_threshold DECIMAL(15,6),
  impact_after_threshold DECIMAL(15,6),
  impact_change DECIMAL(15,6),
  
  -- 阈值类型
  threshold_type VARCHAR(50),
  
  -- 元数据
  identified_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.7 滞后效应分析表
CREATE TABLE IF NOT EXISTS public.marginal_lag_analysis (
  lag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 变量信息
  variable_name VARCHAR(100),
  
  -- 滞后期
  lag_period INTEGER,
  lag_unit VARCHAR(20),
  
  -- 滞后影响
  lagged_impact DECIMAL(15,6),
  cumulative_impact DECIMAL(15,6),
  
  -- 相关系数
  correlation DECIMAL(10,6),
  
  -- 统计显著性
  p_value DECIMAL(10,8),
  is_significant BOOLEAN,
  
  -- 元数据
  analysis_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.8 预测结果表
CREATE TABLE IF NOT EXISTS public.marginal_predictions (
  prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 预测目标
  target_metric VARCHAR(100),
  prediction_date DATE,
  prediction_horizon INTEGER,
  
  -- 预测值
  predicted_value DECIMAL(15,4),
  
  -- 预测区间
  prediction_lower DECIMAL(15,4),
  prediction_upper DECIMAL(15,4),
  
  -- 预测置信度
  confidence_level DECIMAL(5,2),
  
  -- 实际值（用于验证）
  actual_value DECIMAL(15,4),
  prediction_error DECIMAL(15,4),
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.9 优化建议表
CREATE TABLE IF NOT EXISTS public.marginal_optimization_recommendations (
  recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  analysis_id UUID REFERENCES public.marginal_impact_analysis(analysis_id),
  
  -- 建议信息
  recommendation_type VARCHAR(50),
  priority_level VARCHAR(20),
  
  -- 优化目标
  target_metric VARCHAR(100),
  current_value DECIMAL(15,4),
  target_value DECIMAL(15,4),
  improvement_pct DECIMAL(10,4),
  
  -- 优化方案
  recommended_action TEXT,
  action_variables JSONB,
  
  -- 预期影响
  expected_impact DECIMAL(15,6),
  confidence_level DECIMAL(5,2),
  
  -- 实施成本
  estimated_cost DECIMAL(15,2),
  roi_estimate DECIMAL(10,4),
  
  -- 状态
  implementation_status VARCHAR(50),
  
  -- 元数据
  generated_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.10 模型性能监控表
CREATE TABLE IF NOT EXISTS public.marginal_model_performance (
  performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  training_id UUID REFERENCES public.marginal_model_training(training_id),
  
  -- 监控周期
  monitoring_date DATE,
  monitoring_period VARCHAR(50),
  
  -- 性能指标
  current_r_squared DECIMAL(10,6),
  current_mae DECIMAL(10,6),
  current_rmse DECIMAL(10,6),
  current_mape DECIMAL(10,6),
  
  -- 性能变化
  r_squared_change DECIMAL(10,6),
  mae_change DECIMAL(10,6),
  
  -- 预测准确性
  prediction_accuracy DECIMAL(5,2),
  prediction_bias DECIMAL(10,6),
  
  -- 模型稳定性
  stability_score DECIMAL(5,2),
  drift_detected BOOLEAN,
  
  -- 建议
  requires_retraining BOOLEAN,
  performance_status VARCHAR(50),
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.11 权重验证表
CREATE TABLE IF NOT EXISTS public.marginal_weight_validation (
  validation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  weight_id UUID REFERENCES public.marginal_dynamic_weights(weight_id),
  
  -- 验证信息
  validation_date DATE,
  validation_method VARCHAR(50),
  
  -- 验证结果
  is_valid BOOLEAN,
  validation_score DECIMAL(5,2),
  
  -- 偏差分析
  expected_weight DECIMAL(10,6),
  actual_weight DECIMAL(10,6),
  deviation_pct DECIMAL(10,4),
  
  -- 统计显著性
  p_value DECIMAL(10,8),
  is_significant BOOLEAN,
  
  -- 建议
  adjustment_needed BOOLEAN,
  recommended_weight DECIMAL(10,6),
  
  -- 元数据
  validated_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2.12 集成模型表
CREATE TABLE IF NOT EXISTS public.marginal_ensemble_models (
  ensemble_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 集成信息
  ensemble_name VARCHAR(255),
  ensemble_type VARCHAR(50),
  
  -- 成员模型
  member_models JSONB,
  model_weights JSONB,
  
  -- 集成性能
  ensemble_r_squared DECIMAL(10,6),
  ensemble_mae DECIMAL(10,6),
  ensemble_rmse DECIMAL(10,6),
  
  -- 对比基准
  best_single_model_r_squared DECIMAL(10,6),
  improvement_over_best DECIMAL(10,6),
  
  -- 状态
  is_active BOOLEAN DEFAULT TRUE,
  
  -- 元数据
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- 3. 决策管理层（11张表）
-- ========================================

-- 3.1 决策周期配置表
CREATE TABLE IF NOT EXISTS public.decision_cycle_config (
  cycle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 周期信息
  cycle_name VARCHAR(255) NOT NULL,
  cycle_type VARCHAR(50),
  
  -- 周期设置
  frequency VARCHAR(50),
  start_date DATE,
  end_date DATE,
  
  -- 决策范围
  decision_scope JSONB,
  target_metrics JSONB,
  
  -- 状态
  is_active BOOLEAN DEFAULT TRUE,
  
  -- 元数据
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.2 决策事件表
CREATE TABLE IF NOT EXISTS public.decision_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  cycle_id UUID REFERENCES public.decision_cycle_config(cycle_id),
  
  -- 事件信息
  event_date DATE NOT NULL,
  event_type VARCHAR(50),
  event_category VARCHAR(50),
  
  -- 决策层级
  decision_level VARCHAR(50),
  department VARCHAR(100),
  
  -- 决策内容
  decision_description TEXT,
  decision_maker UUID REFERENCES auth.users(id),
  decision_params JSONB,
  
  -- 预期影响
  expected_impact JSONB,
  expected_cost DECIMAL(15,2),
  expected_benefit DECIMAL(15,2),
  
  -- 状态
  approval_status VARCHAR(50),
  implementation_status VARCHAR(50),
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.3 决策执行表
CREATE TABLE IF NOT EXISTS public.decision_executions (
  execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  event_id UUID REFERENCES public.decision_events(event_id),
  
  -- 执行信息
  execution_date DATE,
  executor UUID REFERENCES auth.users(id),
  
  -- 执行内容
  execution_details JSONB,
  resources_allocated JSONB,
  
  -- 执行成本
  actual_cost DECIMAL(15,2),
  budget_variance DECIMAL(15,2),
  
  -- 执行状态
  execution_status VARCHAR(50),
  completion_percentage INTEGER,
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.4 决策效果评估表
CREATE TABLE IF NOT EXISTS public.decision_impact_evaluation (
  evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  event_id UUID REFERENCES public.decision_events(event_id),
  
  -- 评估周期
  evaluation_date DATE,
  evaluation_period VARCHAR(50),
  
  -- 实际影响
  actual_impact JSONB,
  actual_benefit DECIMAL(15,2),
  
  -- 对比分析
  expected_vs_actual JSONB,
  impact_variance_pct DECIMAL(10,4),
  
  -- 归因分析
  attribution_factors JSONB,
  external_factors JSONB,
  
  -- 评估结果
  effectiveness_score DECIMAL(5,2),
  roi DECIMAL(10,4),
  
  -- 元数据
  evaluated_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.5 可控事实表
CREATE TABLE IF NOT EXISTS public.controllable_facts (
  fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 事实信息
  fact_name VARCHAR(255) NOT NULL,
  fact_category VARCHAR(100),
  fact_type VARCHAR(50),
  
  -- 事实值
  fact_value DECIMAL(15,4),
  fact_unit VARCHAR(50),
  
  -- 可控性
  controllability_level VARCHAR(50),
  control_mechanism TEXT,
  
  -- 调整范围
  min_value DECIMAL(15,4),
  max_value DECIMAL(15,4),
  optimal_value DECIMAL(15,4),
  
  -- 关联决策
  related_decisions JSONB,
  
  -- 生效时间
  effective_date DATE,
  expiry_date DATE,
  
  -- 元数据
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.6 外部环境事实表
CREATE TABLE IF NOT EXISTS public.external_business_facts (
  fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 事实信息
  fact_name VARCHAR(255) NOT NULL,
  fact_category VARCHAR(100),
  fact_source VARCHAR(100),
  
  -- 事实值
  fact_value DECIMAL(15,4),
  fact_unit VARCHAR(50),
  
  -- 时间维度
  observation_date DATE,
  
  -- 影响评估
  impact_on_business TEXT,
  relevance_score DECIMAL(5,2),
  
  -- 预测趋势
  trend_direction VARCHAR(50),
  trend_confidence DECIMAL(5,2),
  
  -- 元数据
  data_source VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.7 管理者评估表
CREATE TABLE IF NOT EXISTS public.manager_evaluation (
  evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 被评估者
  manager_id UUID REFERENCES auth.users(id),
  manager_level VARCHAR(50),
  department VARCHAR(100),
  
  -- 评估周期
  evaluation_period_start DATE,
  evaluation_period_end DATE,
  
  -- 决策质量
  decision_quality_score DECIMAL(5,2),
  decision_count INTEGER,
  successful_decisions INTEGER,
  
  -- 执行效率
  execution_efficiency_score DECIMAL(5,2),
  avg_implementation_time INTEGER,
  budget_adherence_pct DECIMAL(5,2),
  
  -- 效果评估
  impact_score DECIMAL(5,2),
  roi_achieved DECIMAL(10,4),
  
  -- 综合评分
  overall_score DECIMAL(5,2),
  performance_level VARCHAR(50),
  
  -- 反馈
  strengths TEXT,
  improvement_areas TEXT,
  recommendations TEXT,
  
  -- 元数据
  evaluated_by UUID REFERENCES auth.users(id),
  evaluation_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.8 决策追溯表
CREATE TABLE IF NOT EXISTS public.decision_audit_trail (
  audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  event_id UUID REFERENCES public.decision_events(event_id),
  
  -- 追溯信息
  audit_timestamp TIMESTAMPTZ DEFAULT NOW(),
  action_type VARCHAR(50),
  
  -- 变更内容
  field_changed VARCHAR(100),
  old_value TEXT,
  new_value TEXT,
  
  -- 变更原因
  change_reason TEXT,
  
  -- 操作者
  changed_by UUID REFERENCES auth.users(id),
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.9 定期报告配置表
CREATE TABLE IF NOT EXISTS public.periodic_report_config (
  config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 报告信息
  report_name VARCHAR(255) NOT NULL,
  report_type VARCHAR(50),
  
  -- 报告周期
  frequency VARCHAR(50),
  schedule_config JSONB,
  
  -- 报告内容
  included_metrics JSONB,
  analysis_dimensions JSONB,
  
  -- 接收者
  recipients JSONB,
  
  -- 状态
  is_active BOOLEAN DEFAULT TRUE,
  last_generated_at TIMESTAMPTZ,
  
  -- 元数据
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.10 报告实例表
CREATE TABLE IF NOT EXISTS public.report_instances (
  instance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  config_id UUID REFERENCES public.periodic_report_config(config_id),
  
  -- 报告信息
  report_date DATE,
  period_start DATE,
  period_end DATE,
  
  -- 报告内容
  report_data JSONB,
  summary_metrics JSONB,
  
  -- 分析结果
  key_findings TEXT,
  recommendations TEXT,
  
  -- 报告文件
  report_file_path VARCHAR(500),
  report_format VARCHAR(20),
  
  -- 状态
  generation_status VARCHAR(50),
  generated_at TIMESTAMPTZ,
  
  -- 元数据
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3.11 警报规则表
CREATE TABLE IF NOT EXISTS public.alert_rules (
  rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES public.tenants(tenant_id),
  
  -- 规则信息
  rule_name VARCHAR(255) NOT NULL,
  alert_type VARCHAR(50),
  
  -- 监控指标
  monitored_metric VARCHAR(100),
  
  -- 触发条件
  condition_type VARCHAR(50),
  threshold_value DECIMAL(15,4),
  comparison_operator VARCHAR(10),
  
  -- 警报级别
  severity_level VARCHAR(50),
  
  -- 通知设置
  notification_channels JSONB,
  recipients JSONB,
  
  -- 状态
  is_active BOOLEAN DEFAULT TRUE,
  last_triggered_at TIMESTAMPTZ,
  
  -- 元数据
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- RLS策略（应用到所有表）
-- ========================================

ALTER TABLE public.raw_data_staging ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_import_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_quality_report ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_version_control ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_fitting_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_model_training ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_impact_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_dynamic_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_synergy_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_threshold_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_lag_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_optimization_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_model_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_weight_validation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marginal_ensemble_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decision_cycle_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decision_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decision_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decision_impact_evaluation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.controllable_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.external_business_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manager_evaluation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decision_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.periodic_report_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_rules ENABLE ROW LEVEL SECURITY;

-- 创建统一RLS策略
DO $$
DECLARE
  table_name TEXT;
BEGIN
  FOR table_name IN 
    SELECT unnest(ARRAY[
      'raw_data_staging', 'data_import_log', 'data_quality_report', 'data_version_control',
      'marginal_fitting_config', 'marginal_model_training', 'marginal_impact_analysis',
      'marginal_dynamic_weights', 'marginal_synergy_analysis', 'marginal_threshold_analysis',
      'marginal_lag_analysis', 'marginal_predictions', 'marginal_optimization_recommendations',
      'marginal_model_performance', 'marginal_weight_validation', 'marginal_ensemble_models',
      'decision_cycle_config', 'decision_events', 'decision_executions', 'decision_impact_evaluation',
      'controllable_facts', 'external_business_facts', 'manager_evaluation', 'decision_audit_trail',
      'periodic_report_config', 'report_instances', 'alert_rules'
    ])
  LOOP
    EXECUTE format('
      CREATE POLICY "tenant_isolation_policy" ON public.%I 
      FOR ALL TO authenticated
      USING (tenant_id = get_user_tenant_id(auth.uid()) OR has_role(auth.uid(), ''admin'') OR (has_role(auth.uid(), ''analyst'') AND has_cross_tenant_access(auth.uid(), tenant_id)))
    ', table_name);
  END LOOP;
END $$;

-- ========================================
-- 索引优化
-- ========================================

-- 原始数据层索引
CREATE INDEX IF NOT EXISTS idx_raw_data_staging_tenant ON public.raw_data_staging(tenant_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_staging_status ON public.raw_data_staging(upload_status);
CREATE INDEX IF NOT EXISTS idx_raw_data_staging_uploaded_at ON public.raw_data_staging(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_import_log_tenant ON public.data_import_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_import_log_staging ON public.data_import_log(staging_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_report_tenant ON public.data_quality_report(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_version_control_tenant ON public.data_version_control(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_version_control_current ON public.data_version_control(is_current) WHERE is_current = TRUE;

-- 边际分析层索引
CREATE INDEX IF NOT EXISTS idx_marginal_fitting_config_tenant ON public.marginal_fitting_config(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marginal_model_training_tenant ON public.marginal_model_training(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marginal_model_training_date ON public.marginal_model_training(training_date DESC);
CREATE INDEX IF NOT EXISTS idx_marginal_impact_analysis_tenant ON public.marginal_impact_analysis(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marginal_dynamic_weights_tenant ON public.marginal_dynamic_weights(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marginal_predictions_tenant ON public.marginal_predictions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_marginal_predictions_date ON public.marginal_predictions(prediction_date DESC);

-- 决策管理层索引
CREATE INDEX IF NOT EXISTS idx_decision_cycle_config_tenant ON public.decision_cycle_config(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decision_events_tenant ON public.decision_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decision_events_date ON public.decision_events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_decision_executions_tenant ON public.decision_executions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decision_impact_evaluation_tenant ON public.decision_impact_evaluation(tenant_id);
CREATE INDEX IF NOT EXISTS idx_controllable_facts_tenant ON public.controllable_facts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_external_business_facts_tenant ON public.external_business_facts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_manager_evaluation_tenant ON public.manager_evaluation(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decision_audit_trail_tenant ON public.decision_audit_trail(tenant_id);
CREATE INDEX IF NOT EXISTS idx_periodic_report_config_tenant ON public.periodic_report_config(tenant_id);
CREATE INDEX IF NOT EXISTS idx_report_instances_tenant ON public.report_instances(tenant_id);
CREATE INDEX IF NOT EXISTS idx_alert_rules_tenant ON public.alert_rules(tenant_id);