import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { triggerId } = req.body;
  
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const executionId = crypto.randomUUID();

  // 记录执行开始
  await supabase.from('decision_cycle_execution').insert({
    execution_id: executionId,
    trigger_id: triggerId,
    execution_start: new Date().toISOString(),
    execution_status: 'running'
  });

  try {
    // 1. 收集业务事实
    const businessFacts = await collectBusinessFacts(supabase);

    // 2. 计算业务事实指标
    const metrics = await calculateMetrics(supabase, businessFacts);

    // 3. 等待管理者评价（创建待评价任务）
    const evaluationTaskId = await createEvaluationTask(supabase, metrics);

    // 4. 关联分析（在管理者评价后触发）
    // 5. 优化诊断（在关联分析后触发）
    // 6. 生成决策建议（在优化诊断后触发）

    // 更新执行记录
    await supabase.from('decision_cycle_execution').update({
      execution_end: new Date().toISOString(),
      execution_status: 'waiting_evaluation',
      execution_log: { evaluationTaskId }
    }).eq('execution_id', executionId);

    return res.status(200).json({ 
      success: true, 
      executionId,
      evaluationTaskId 
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    await supabase.from('decision_cycle_execution').update({
      execution_end: new Date().toISOString(),
      execution_status: 'failed',
      execution_log: { error: errorMessage }
    }).eq('execution_id', executionId);

    return res.status(500).json({ error: errorMessage });
  }
}

async function collectBusinessFacts(supabase: any) {
  // 收集可控业务事实
  const expenses = await supabase.from('fact_expense').select('*');
  const assets = await supabase.from('fact_asset_acquisition').select('*');
  const orders = await supabase.from('fact_order').select('*');
  const voices = await supabase.from('fact_voice').select('*');
  const marketPrices = await supabase.from('fact_market_price').select('*');
  
  return { expenses, assets, orders, voices, marketPrices };
}

async function calculateMetrics(supabase: any, businessFacts: any) {
  // 计算各类指标
  return {
    efficiencyMetrics: {},
    conversionMetrics: {},
    costMetrics: {},
    satisfactionMetrics: {}
  };
}

async function createEvaluationTask(supabase: any, metrics: any) {
  // 创建管理者评价任务
  const taskId = crypto.randomUUID();
  // 保存到待评价任务表
  return taskId;
}
