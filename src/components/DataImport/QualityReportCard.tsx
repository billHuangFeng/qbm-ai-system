import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

const QualityReportCard = () => {
  // Mock quality data
  const qualityScore = 85;
  const issues = [
    { type: 'warning', message: '发现 3 个缺失值', field: '客户名称' },
    { type: 'warning', message: '日期格式不一致', field: '日期' },
    { type: 'info', message: '建议清理空格', field: '产品SKU' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-primary" />
          数据质量报告
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Quality Score */}
        <div className="flex items-center gap-6 mb-6">
          <div className="flex items-center justify-center w-24 h-24 rounded-full bg-primary/10">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">{qualityScore}</div>
              <div className="text-xs text-muted-foreground">分</div>
            </div>
          </div>
          <div>
            <h4 className="text-lg font-semibold text-foreground mb-1">良好</h4>
            <p className="text-sm text-muted-foreground">
              数据质量整体良好，建议修复以下问题
            </p>
          </div>
        </div>

        {/* Issues List */}
        <div className="space-y-2">
          <h5 className="text-sm font-semibold text-foreground mb-3">发现的问题</h5>
          {issues.map((issue, i) => (
            <div 
              key={i}
              className="flex items-start gap-3 p-3 rounded-lg border bg-card"
            >
              <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                issue.type === 'warning' ? 'text-yellow-500' : 'text-blue-500'
              }`} />
              <div className="flex-1">
                <div className="text-sm font-medium text-foreground">{issue.message}</div>
                <div className="text-xs text-muted-foreground mt-1">字段: {issue.field}</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default QualityReportCard;
