import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { orderId } = req.body;
  
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  // 1. 获取订单的所有触点
  const { data: touchpoints } = await supabase
    .from('customer_journey')
    .select('*')
    .eq('order_id', orderId);

  // 2. 计算Shapley值
  const shapleyValues = calculateShapleyValues(touchpoints);

  // 3. 保存归因结果
  for (const touchpoint of touchpoints) {
    await supabase.from('bridge_attribution').insert({
      order_id: orderId,
      touchpoint_type: touchpoint.type,
      touchpoint_id: touchpoint.id,
      attribution_value: shapleyValues[touchpoint.id]
    });
  }

  return res.status(200).json({ 
    success: true, 
    shapleyValues 
  });
}

function calculateShapleyValues(touchpoints: any[]): Record<string, number> {
  // Shapley值计算逻辑（TypeScript实现）
  const n = touchpoints.length;
  const shapleyValues: Record<string, number> = {};
  
  // 简化的Shapley计算（实际需要更复杂的排列组合）
  for (let i = 0; i < n; i++) {
    const touchpoint = touchpoints[i];
    let marginalContribution = 0;
    
    // 计算边际贡献
    const withTouchpoint = evaluateCoalition([...touchpoints.slice(0, i+1)]);
    const withoutTouchpoint = evaluateCoalition([...touchpoints.slice(0, i)]);
    marginalContribution = withTouchpoint - withoutTouchpoint;
    
    shapleyValues[touchpoint.id] = marginalContribution / n;
  }
  
  return shapleyValues;
}

function evaluateCoalition(coalition: any[]): number {
  // 评估触点联盟的价值
  // 这里需要业务逻辑来评估多个触点组合的转化效果
  return coalition.length * 0.1; // 简化示例
}
