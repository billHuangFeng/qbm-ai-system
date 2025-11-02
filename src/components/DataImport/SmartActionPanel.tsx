import { Button } from '@/components/ui/button';
import { Sparkles, Play, Settings, ArrowLeft } from 'lucide-react';
import type { ImportStage } from '@/pages/DataImportPage';

interface SmartActionPanelProps {
  currentStage: ImportStage;
  onStageChange: (stage: ImportStage) => void;
}

const SmartActionPanel = ({ currentStage, onStageChange }: SmartActionPanelProps) => {
  const getActions = (): Array<{
    label: string;
    variant: 'default' | 'outline';
    icon?: typeof Sparkles;
    onClick: () => void;
  }> => {
    switch(currentStage) {
      case 'UPLOAD':
        return [];
      
      case 'ANALYZING':
        return [];
      
      case 'MAPPING':
        return [
          {
            label: '✨ 应用 AI 推荐',
            variant: 'default' as const,
            icon: Sparkles,
            onClick: () => onStageChange('QUALITY_CHECK')
          },
          {
            label: '🛠️ 手动配置',
            variant: 'outline' as const,
            icon: Settings,
            onClick: () => {}
          }
        ];
      
      case 'QUALITY_CHECK':
        return [
          {
            label: '🔧 一键修复问题',
            variant: 'default' as const,
            onClick: () => {}
          },
          {
            label: '⏭️ 继续导入',
            variant: 'outline' as const,
            onClick: () => onStageChange('READY')
          }
        ];
      
      case 'READY':
        return [
          {
            label: '🚀 开始导入',
            variant: 'default' as const,
            icon: Play,
            onClick: () => onStageChange('IMPORTING')
          },
          {
            label: '🔙 返回调整',
            variant: 'outline' as const,
            icon: ArrowLeft,
            onClick: () => onStageChange('MAPPING')
          }
        ];
      
      default:
        return [];
    }
  };

  const actions = getActions();

  if (actions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2 pt-4 border-t">
      {actions.map((action, index) => {
        const Icon = action.icon;
        return (
          <Button
            key={index}
            variant={action.variant}
            className="w-full justify-start"
            onClick={action.onClick}
          >
            {Icon && <Icon className="w-4 h-4 mr-2" />}
            {action.label}
          </Button>
        );
      })}
    </div>
  );
};

export default SmartActionPanel;
