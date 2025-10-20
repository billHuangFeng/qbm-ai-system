import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { 
    analysisId, 
    evaluationType, 
    evaluationContent, 
    metricAdjustments 
  } = req.body;
  
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  // 记录管理者评价
  await supabase.from('manager_evaluation').insert({
    analysis_id: analysisId,
    manager_id: req.headers['user-id'], // 从认证中获取
    evaluation_type: evaluationType,
    evaluation_content: evaluationContent,
    status: 'completed'
  });

  // 处理指标调整
  if (metricAdjustments) {
    for (const adjustment of metricAdjustments) {
      await supabase.from('metric_confirmation').insert({
        metric_id: adjustment.metricId,
        confirmed_value: adjustment.newValue,
        confidence_level: adjustment.confidence,
        confirmed_by: req.headers['user-id']
      });
    }
  }

  // 触发后续分析流程
  await triggerNextAnalysisStep(supabase, analysisId);

  return res.status(200).json({ success: true });
}

async function triggerNextAnalysisStep(supabase: any, analysisId: string) {
  // 触发关联分析、优化诊断、决策建议生成
}
