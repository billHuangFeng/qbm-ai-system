import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import type { QualityReport, UploadFileResponse } from '@/services/dataImportApi';

interface QualityIssue {
  severity: 'error' | 'warning';
  count: number;
  message: string;
  description: string;
  autoFixable: boolean;
  field: string;
  examples?: string[];
}

interface QualityReportCardProps {
  qualityReport: QualityReport;
  uploadResult: UploadFileResponse | null;
}

const QualityReportCard = ({ qualityReport, uploadResult }: QualityReportCardProps) => {
  const qualityScore = Math.round(qualityReport.quality_score * 100);
  const importability = qualityReport.quality_level;
  
  // 根据质量报告生成问题列表
  const blockingIssues: QualityIssue[] = [];
  const fixableIssues: QualityIssue[] = [];

  // 检查缺失值
  Object.entries(qualityReport.missing_values).forEach(([field, count]) => {
    if (count > 0) {
      fixableIssues.push({
        severity: 'warning',
        count,
        message: '存在缺失值',
        description: `字段 ${field} 有 ${count} 个缺失值`,
        autoFixable: false,
        field,
      });
    }
  });

  // 检查重复行
  if (qualityReport.duplicate_rows > 0) {
    fixableIssues.push({
      severity: 'warning',
      count: qualityReport.duplicate_rows,
      message: '存在重复记录',
      description: `发现 ${qualityReport.duplicate_rows} 行重复数据`,
      autoFixable: true,
      field: '全部字段',
    });
  }

  // 添加推荐建议作为问题
  qualityReport.recommendations.forEach((rec, index) => {
    fixableIssues.push({
      severity: 'warning',
      count: 1,
      message: '数据质量建议',
      description: rec,
      autoFixable: false,
      field: '多个字段',
    });
  });

  const getImportabilityInfo = () => {
    switch(importability) {
      case 'excellent':
        return { 
          label: '优秀', 
          color: 'text-green-600', 
          bgColor: 'bg-green-500/10',
          recommendation: '数据质量优秀，可直接导入正式表' 
        };
      case 'good':
        return { 
          label: '良好', 
          color: 'text-blue-600', 
          bgColor: 'bg-blue-500/10',
          recommendation: '建议先导入暂存表，完善后再入库' 
        };
      case 'fair':
        return { 
          label: '一般', 
          color: 'text-yellow-600', 
          bgColor: 'bg-yellow-500/10',
          recommendation: '存在可修复问题，需要完善处理' 
        };
      case 'poor':
        return { 
          label: '较差', 
          color: 'text-red-600', 
          bgColor: 'bg-red-500/10',
          recommendation: '数据质量较差，建议清理后重新导入' 
        };
      default:
        return { label: '未知', color: 'text-muted-foreground', bgColor: 'bg-muted', recommendation: '' };
    }
  };

  const importabilityInfo = getImportabilityInfo();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-primary" />
          数据质量报告
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Quality Score & Importability */}
        <div className="flex items-center gap-6 mb-6">
          <div className={`flex items-center justify-center w-24 h-24 rounded-full ${importabilityInfo.bgColor}`}>
            <div className="text-center">
              <div className={`text-3xl font-bold ${importabilityInfo.color}`}>{qualityScore}</div>
              <div className="text-xs text-muted-foreground">分</div>
            </div>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className={`text-lg font-semibold ${importabilityInfo.color}`}>
                {importabilityInfo.label}
              </h4>
              <span className={`text-xs px-2 py-1 rounded-full ${importabilityInfo.bgColor} ${importabilityInfo.color}`}>
                可导入
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              {importabilityInfo.recommendation}
            </p>
          </div>
        </div>

        {/* Issue Summary */}
        <div className="grid grid-cols-2 gap-4 mb-6 p-3 rounded-lg bg-muted/50">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{blockingIssues.length}</div>
            <div className="text-xs text-muted-foreground">阻塞性问题</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{fixableIssues.length}</div>
            <div className="text-xs text-muted-foreground">可修复问题</div>
          </div>
        </div>

        {/* Blocking Issues */}
        {blockingIssues.length > 0 && (
          <div className="space-y-2 mb-4">
            <h5 className="text-sm font-semibold text-red-600 mb-3">⛔ 阻塞性问题（必须修复）</h5>
            {blockingIssues.map((issue, i) => (
              <div 
                key={i}
                className="flex items-start gap-3 p-3 rounded-lg border border-red-200 bg-red-50/50"
              >
                <AlertTriangle className="w-5 h-5 mt-0.5 text-red-500" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-foreground">{issue.message}</div>
                  <div className="text-xs text-muted-foreground mt-1">{issue.description}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Fixable Issues */}
        <div className="space-y-2">
          <h5 className="text-sm font-semibold text-foreground mb-3">
            🔧 可修复问题（第二阶段处理）
          </h5>
          {fixableIssues.map((issue, i) => (
            <div 
              key={i}
              className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <AlertTriangle className="w-5 h-5 mt-0.5 text-yellow-500" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="text-sm font-medium text-foreground">{issue.message}</div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">
                    {issue.count} 处
                  </span>
                  {issue.autoFixable && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                      可自动修复
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground mb-2">{issue.description}</div>
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">字段:</span> {issue.field}
                  {issue.examples && issue.examples.length > 0 && (
                    <span className="ml-2">
                      <span className="font-medium">示例:</span> {issue.examples.join(', ')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default QualityReportCard;
