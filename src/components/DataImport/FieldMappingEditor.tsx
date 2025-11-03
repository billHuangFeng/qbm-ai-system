import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ArrowRight, Sparkles } from 'lucide-react';

const FieldMappingEditor = () => {
  // Mock mappings
  const mockMappings = [
    { source: '订单号', target: 'order_no', confidence: 95, isRecommended: true },
    { source: '日期', target: 'order_date', confidence: 90, isRecommended: true },
    { source: '客户名称', target: 'customer_name', confidence: 88, isRecommended: true },
    { source: '产品SKU', target: 'sku_code', confidence: 92, isRecommended: true },
    { source: '数量', target: 'quantity', confidence: 85, isRecommended: false },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          字段映射配置
          <span className="text-sm font-normal text-muted-foreground ml-2">
            (AI 智能推荐)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {mockMappings.map((mapping, i) => (
            <div 
              key={i}
              className="flex items-center gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex-1">
                <div className="font-medium text-foreground">{mapping.source}</div>
                <div className="text-xs text-muted-foreground mt-1">源字段</div>
              </div>
              
              <ArrowRight className="w-5 h-5 text-muted-foreground" />
              
              <div className="flex-1">
                <div className="font-medium text-foreground">{mapping.target}</div>
                <div className="text-xs text-muted-foreground mt-1">目标字段</div>
              </div>
              
              <div className="flex items-center gap-2">
                {mapping.isRecommended && (
                  <div className="px-2 py-1 rounded text-xs bg-primary/10 text-primary font-medium">
                    AI 推荐
                  </div>
                )}
                <div className="text-sm font-semibold text-muted-foreground">
                  {mapping.confidence}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default FieldMappingEditor;
