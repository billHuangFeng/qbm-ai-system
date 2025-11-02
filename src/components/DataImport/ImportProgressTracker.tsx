import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import type { ImportStage } from '@/pages/DataImportPage';

interface ImportProgressTrackerProps {
  currentStage: ImportStage;
}

const ImportProgressTracker = ({ currentStage }: ImportProgressTrackerProps) => {
  const stages = [
    { key: 'UPLOAD', label: '上传文件', description: '选择数据文件' },
    { key: 'ANALYZING', label: '格式识别', description: '分析文件结构' },
    { key: 'MAPPING', label: '字段映射', description: '智能字段匹配' },
    { key: 'QUALITY_CHECK', label: '质量检查', description: '7维度分析' },
    { key: 'READY', label: '准备导入', description: '确认并导入' },
  ] as const;

  const currentIndex = stages.findIndex(s => s.key === currentStage);

  const getStageStatus = (index: number) => {
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="space-y-1">
      {stages.map((stage, index) => {
        const status = getStageStatus(index);
        
        return (
          <div key={stage.key} className="flex items-center gap-3">
            <div className="flex-shrink-0">
              {status === 'completed' && (
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              )}
              {status === 'active' && (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              )}
              {status === 'pending' && (
                <Circle className="w-5 h-5 text-muted-foreground/30" />
              )}
            </div>
            
            <div className="flex-1 py-2">
              <div className={`text-sm font-medium transition-colors ${
                status === 'active' ? 'text-foreground' :
                status === 'completed' ? 'text-muted-foreground' :
                'text-muted-foreground/50'
              }`}>
                {stage.label}
              </div>
              <div className={`text-xs transition-colors ${
                status === 'active' ? 'text-muted-foreground' : 'text-muted-foreground/50'
              }`}>
                {stage.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ImportProgressTracker;
