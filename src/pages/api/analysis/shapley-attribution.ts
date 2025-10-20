import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { orderId } = req.body;
  
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  // 1. 获取订单的所有触点
  const { data: touchpoints, error } = await supabase
    .from('customer_journey')
    .select('*')
    .eq('order_id', orderId);

  if (error || !touchpoints || touchpoints.length === 0) {
    return res.status(404).json({ success: false, error: 'No touchpoints found for this order' });
  }

  // 2. 计算Shapley值
  const shapleyValues = calculateShapleyValues(touchpoints);

  // 3. 保存归因结果
  for (const touchpoint of touchpoints) {
    await supabase.from('bridge_attribution').insert({
      order_id: orderId,
      touchpoint_type: (touchpoint as any).type,
      touchpoint_id: (touchpoint as any).id,
      attribution_value: shapleyValues[(touchpoint as any).id]
    });
  }

  return res.status(200).json({ 
    success: true, 
    shapleyValues 
  });
}

function calculateShapleyValues(touchpoints: any[]): Record<string, number> {
  const n = touchpoints.length;
  const shapleyValues: Record<string, number> = {};
  
  for (let i = 0; i < n; i++) {
    const tp = touchpoints[i];
    const id = (tp as any).id as string;
    const withTouchpoint = evaluateCoalition([...touchpoints.slice(0, i + 1)]);
    const withoutTouchpoint = evaluateCoalition([...touchpoints.slice(0, i)]);
    const marginalContribution = withTouchpoint - withoutTouchpoint;
    shapleyValues[id] = marginalContribution / n;
  }
  
  return shapleyValues;
}

function evaluateCoalition(coalition: any[]): number {
  return coalition.length * 0.1; // 简化示例
}
