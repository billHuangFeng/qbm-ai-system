import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ArrowRight, Sparkles } from 'lucide-react';

interface FieldMappingEditorProps {
  previewData: {
    headers: string[];
    rows: any[][];
  };
  formatDetection?: {
    format_type: string;
    confidence: number;
    details: Record<string, any>;
  } | null;
}

const FieldMappingEditor = ({ previewData, formatDetection }: FieldMappingEditorProps) => {
  // 基于数据生成智能映射建议
  const generateMappings = () => {
    const { headers } = previewData;
    
    // 简单的字段映射逻辑
    const mappingRules: Record<string, string> = {
      '订单号': 'order_no',
      '单据号': 'document_number',
      '日期': 'order_date',
      '订单日期': 'order_date',
      '客户名称': 'customer_name',
      '供应商名称': 'supplier_name',
      '产品SKU': 'sku_code',
      'SKU': 'sku_code',
      '数量': 'quantity',
      '单价': 'unit_price',
      '金额': 'amount',
      '总金额': 'total_amount',
    };

    return headers.map(header => {
      const targetField = mappingRules[header] || header.toLowerCase().replace(/\s+/g, '_');
      const confidence = mappingRules[header] ? 90 + Math.floor(Math.random() * 10) : 70 + Math.floor(Math.random() * 15);
      
      return {
        source: header,
        target: targetField,
        confidence,
        isRecommended: confidence >= 85,
      };
    });
  };

  const mockMappings = generateMappings();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          字段映射配置
          <span className="text-sm font-normal text-muted-foreground ml-2">
            (AI 智能推荐)
          </span>
          {formatDetection && (
            <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary ml-auto">
              格式: {formatDetection.format_type} ({(formatDetection.confidence * 100).toFixed(0)}%)
            </span>
          )}
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
