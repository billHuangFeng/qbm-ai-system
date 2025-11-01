// BMOS系统 - 预测误差追踪API
// 作用: 自动计算预测误差,触发模型重训练
// 位置: Supabase Edge Function

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const ERROR_THRESHOLD = {
  RELATIVE_ERROR: 15, // 相对误差阈值(百分比)
  ABSOLUTE_ERROR: 1000, // 绝对误差阈值
  CRITICAL_ERROR: 50, // 严重误差阈值
};

interface PredictionAccuracyCheckRequest {
  period: string; // '2025-01', '2025-Q1' 等
  predictionTypes?: string[]; // ['npv', 'capability_value', ...]
  autoRetrain?: boolean; // 是否自动触发重训练
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const requestData: PredictionAccuracyCheckRequest = await req.json();
    const period = requestData.period || getPreviousMonth();

    // 获取所有租户的预测记录(在实际使用中应该按租户过滤)
    const { data: predictions } = await supabaseClient
      .from('prediction_accuracy_log')
      .select('*')
      .eq('target_period', period)
      .eq('has_actual_value', true);

    if (!predictions || predictions.length === 0) {
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: 'No predictions found for the period',
          checkedCount: 0
        }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    let errorCount = 0;
    let retrainTriggers = [];

    // 分析每个预测的误差
    for (const prediction of predictions) {
      const relativeError = parseFloat(prediction.relative_error);
      const absoluteError = parseFloat(prediction.absolute_error);

      // 检查是否需要重训练
      const needsRetrain = relativeError > ERROR_THRESHOLD.RELATIVE_ERROR || 
                          absoluteError > ERROR_THRESHOLD.ABSOLUTE_ERROR;

      if (needsRetrain) {
        errorCount++;
        
        // 分析误差原因
        const errorAnalysis = await analyzeErrorCauses(supabaseClient, prediction);
        
        // 确定误差严重性
        const severity = relativeError > ERROR_THRESHOLD.CRITICAL_ERROR ? 'critical' : 'high';

        retrainTriggers.push({
          predictionId: prediction.id,
          relativeError,
          absoluteError,
          severity,
          errorAnalysis,
        });

        // 如果设置了自动重训练,触发重训练
        if (requestData.autoRetrain !== false) {
          await triggerModelRetrain(supabaseClient, {
            tenantId: prediction.tenant_id,
            modelType: prediction.prediction_type,
            triggerType: 'prediction_error',
            predictionId: prediction.id,
            errorAnalysis,
            severity,
          });
        }
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        period,
        checkedCount: predictions.length,
        errorCount,
        errorRate: ((errorCount / predictions.length) * 100).toFixed(2) + '%',
        retrainTriggers,
        message: `Checked ${predictions.length} predictions, found ${errorCount} errors`,
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error checking prediction accuracy:', error);
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

// 分析误差原因
async function analyzeErrorCauses(supabaseClient: any, prediction: any) {
  const causes = [];

  // 1. 检查预测置信度
  if (prediction.confidence_level < 0.7) {
    causes.push({
      reason: 'low_confidence',
      description: '预测置信度过低',
      suggestion: '增加历史数据量或改进模型特征',
    });
  }

  // 2. 检查市场环境变化(如果有相关数据)
  // TODO: 查询实际的市场变化数据
  causes.push({
    reason: 'market_change',
    description: '市场环境可能发生重大变化',
    suggestion: '更新市场环境特征到模型中',
  });

  // 3. 检查模型版本是否过时
  // TODO: 查询模型版本信息

  return causes;
}

// 触发模型重训练
async function triggerModelRetrain(supabaseClient: any, config: any) {
  console.log('Triggering model retrain:', config);

  // 记录重训练日志
  const { data: updateLog } = await supabaseClient
    .from('model_update_log')
    .insert({
      tenant_id: config.tenantId,
      trigger_type: config.triggerType,
      trigger_reference_id: config.predictionId,
      trigger_description: `触发原因: ${config.modelType}模型预测误差过大(相对误差: ${config.errorAnalysis?.relativeError || 'N/A'}%)`,
      model_type: config.modelType,
      old_model_version: 'current',
      new_model_version: 'retraining',
      update_content: {
        error_analysis: config.errorAnalysis,
        severity: config.severity,
      },
      status: 'pending',
    })
    .select()
    .single();

  // TODO: 在实际实现中,这里应该:
  // 1. 调用模型训练服务
  // 2. 传入新的训练数据
  // 3. 训练新模型
  // 4. 对比性能
  // 5. 如果更好,部署新模型

  return updateLog;
}

// 获取上月
function getPreviousMonth(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() === 0 ? 12 : now.getMonth();
  const formattedMonth = month < 10 ? `0${month}` : `${month}`;
  return `${year}-${formattedMonth}`;
}


