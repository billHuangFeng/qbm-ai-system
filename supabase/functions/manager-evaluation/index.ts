// BMOS系统 - 管理者评价反馈API
// 作用: 接收管理者评价,触发模型更新
// 位置: Supabase Edge Function

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface ManagerEvaluationRequest {
  analysisId: string;
  evaluationType: 'confirm' | 'adjust' | 'reject';
  evaluationContent: string;
  metricAdjustments?: Array<{
    metricId: string;
    metricName: string;
    currentValue: number;
    adjustedValue: number;
    adjustmentReason: string;
  }>;
  implementationPlan?: {
    startDate: string;
    duration: number;
    responsiblePerson: string;
    budgetRequired: number;
  };
}

serve(async (req) => {
  // CORS 预检请求
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // 创建 Supabase 客户端
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // 获取认证信息
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ success: false, error: 'Missing authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 获取当前用户
    const { data: { user } } = await supabaseClient.auth.getUser(authHeader);
    if (!user) {
      return new Response(
        JSON.stringify({ success: false, error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 获取用户的租户ID
    const { data: userProfile } = await supabaseClient
      .from('user_profiles')
      .select('tenant_id')
      .eq('id', user.id)
      .single();

    if (!userProfile) {
      return new Response(
        JSON.stringify({ success: false, error: 'User profile not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const tenantId = userProfile.tenant_id;

    // 解析请求体
    const requestData: ManagerEvaluationRequest = await req.json();

    // 验证输入
    if (!requestData.analysisId || !requestData.evaluationType) {
      return new Response(
        JSON.stringify({ success: false, error: 'Missing required fields' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 1. 保存管理者评价记录
    const { data: evaluationRecord, error: saveError } = await supabaseClient
      .from('manager_evaluation')
      .insert({
        tenant_id: tenantId,
        analysis_id: requestData.analysisId,
        analysis_type: 'marginal_analysis', // 可以根据实际情况调整
        evaluation_type: requestData.evaluationType,
        evaluation_content: requestData.evaluationContent,
        metric_adjustments: requestData.metricAdjustments || null,
        implementation_plan: requestData.implementationPlan || null,
        created_by: user.id,
      })
      .select()
      .single();

    if (saveError) {
      console.error('Error saving evaluation:', saveError);
      return new Response(
        JSON.stringify({ success: false, error: saveError.message }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 2. 如果是指标调整,保存调整历史
    if (requestData.metricAdjustments && requestData.metricAdjustments.length > 0) {
      const adjustmentRecords = requestData.metricAdjustments.map(adjustment => ({
        tenant_id: tenantId,
        evaluation_id: evaluationRecord.id,
        metric_id: adjustment.metricId,
        metric_name: adjustment.metricName,
        original_value: adjustment.currentValue,
        adjusted_value: adjustment.adjustedValue,
        adjustment_reason: adjustment.adjustmentReason,
        created_by: user.id,
      }));

      await supabaseClient
        .from('metric_adjustment_history')
        .insert(adjustmentRecords);
    }

    // 3. 判断是否需要触发模型更新
    let modelUpdateTriggered = false;
    let updateId: string | null = null;

    if (requestData.evaluationType === 'adjust' && requestData.metricAdjustments) {
      // 触发模型更新
      modelUpdateTriggered = true;

      const updateLog = await supabaseClient
        .from('model_update_log')
        .insert({
          tenant_id: tenantId,
          trigger_type: 'manager_evaluation',
          trigger_reference_id: evaluationRecord.id,
          trigger_description: `触发原因: 管理者调整了${requestData.metricAdjustments.length}个指标`,
          model_type: 'shapley', // 可以根据实际情况调整
          old_model_version: 'current',
          new_model_version: 'pending',
          update_content: {
            adjustments: requestData.metricAdjustments,
            evaluation_content: requestData.evaluationContent,
          },
          status: 'pending',
          created_by: user.id,
        })
        .select()
        .single();

      updateId = updateLog.data?.id || null;

      // TODO: 在实际实现中,这里应该:
      // 1. 调用模型更新服务
      // 2. 异步处理模型重训练
      // 3. 更新模型参数
      console.log('Model update triggered for evaluation:', evaluationRecord.id);
    }

    // 4. 返回结果
    return new Response(
      JSON.stringify({
        success: true,
        evaluationId: evaluationRecord.id,
        modelUpdateTriggered,
        updateId,
        message: '评价已成功保存',
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error processing manager evaluation:', error);
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});



