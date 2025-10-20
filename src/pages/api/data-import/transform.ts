import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { rawId } = req.body;
  
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  // 1. 获取原始数据
  const { data: rawData } = await supabase
    .from('raw_data_staging')
    .select('*')
    .eq('raw_id', rawId)
    .single();

  if (!rawData) {
    return res.status(404).json({ error: 'Raw data not found' });
  }

  // 2. 根据source_type路由到不同的转化逻辑
  switch (rawData.source_type) {
    case 'expense':
      await transformExpense(supabase, rawData);
      break;
    case 'asset':
      await transformAsset(supabase, rawData);
      break;
    case 'order':
      await transformOrder(supabase, rawData);
      break;
    case 'feedback':
      await transformFeedback(supabase, rawData);
      break;
    default:
      throw new Error(`Unknown source_type: ${rawData.source_type}`);
  }

  // 3. 更新处理状态
  await supabase
    .from('raw_data_staging')
    .update({ 
      processing_status: 'completed',
      processed_date: new Date().toISOString()
    })
    .eq('raw_id', rawId);

  return res.status(200).json({ success: true });
}

async function transformExpense(supabase: any, rawData: any) {
  const expenseData = rawData.raw_data;
  
  await supabase.from('fact_expense').insert({
    raw_id: rawData.raw_id,
    expense_type: expenseData.type,
    expense_amount: expenseData.amount,
    expense_date: expenseData.date,
    department: expenseData.department,
    description: expenseData.description
  });
}

async function transformAsset(supabase: any, rawData: any) {
  const assetData = rawData.raw_data;
  
  await supabase.from('fact_asset_acquisition').insert({
    raw_id: rawData.raw_id,
    asset_type: assetData.type,
    acquisition_cost: assetData.cost,
    acquisition_date: assetData.date,
    expected_life_years: assetData.life_years
  });
}

async function transformOrder(supabase: any, rawData: any) {
  const orderData = rawData.raw_data;
  
  await supabase.from('fact_order').insert({
    customer_id: orderData.customer_id,
    sku_id: orderData.sku_id,
    order_date: orderData.date,
    order_amount: orderData.amount,
    quantity: orderData.quantity
  });
}

async function transformFeedback(supabase: any, rawData: any) {
  const feedbackData = rawData.raw_data;
  
  await supabase.from('fact_voice').insert({
    raw_id: rawData.raw_id,
    customer_id: feedbackData.customer_id,
    voice_type: feedbackData.type,
    voice_content: feedbackData.content,
    sentiment_score: feedbackData.sentiment_score,
    impact_level: feedbackData.impact_level,
    response_required: feedbackData.response_required,
    record_date: feedbackData.date
  });
}
