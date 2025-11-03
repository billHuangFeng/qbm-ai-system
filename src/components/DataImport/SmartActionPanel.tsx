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
      
      case 'MAPPING':
        return [
          {
            label: '✨ 应用 AI 推荐',
            variant: 'default' as const,
            icon: Sparkles,
            onClick: () => onStageChange('ANALYZING')
          },
          {
            label: '🛠️ 手动配置',
            variant: 'outline' as const,
            icon: Settings,
            onClick: () => {}
          }
        ];
      
      case 'ANALYZING':
        return [];
      
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
        // Mock quality score - in real app, get from quality check result
        const qualityScore = 85;
        
        if (qualityScore >= 95) {
          // Excellent quality - allow direct import to final table
          return [
            {
              label: '🚀 直接导入正式表',
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
        } else if (qualityScore >= 70) {
          // Good/Fixable quality - recommend staging table
          return [
            {
              label: '📥 导入暂存表（推荐）',
              variant: 'default' as const,
              icon: Play,
              onClick: () => {
                // TODO: Import to staging table, then go to ENHANCEMENT stage
                onStageChange('IMPORTING');
              }
            },
            {
              label: '⚠️ 强制导入正式表',
              variant: 'outline' as const,
              icon: Play,
              onClick: () => {
                // TODO: Show confirmation dialog
                onStageChange('IMPORTING');
              }
            },
            {
              label: '🔙 返回调整',
              variant: 'outline' as const,
              icon: ArrowLeft,
              onClick: () => onStageChange('MAPPING')
            }
          ];
        } else {
          // Poor quality - reject import
          return [
            {
              label: '⛔ 质量不合格，无法导入',
              variant: 'outline' as const,
              onClick: () => {}
            },
            {
              label: '🔙 返回修复',
              variant: 'default' as const,
              icon: ArrowLeft,
              onClick: () => onStageChange('MAPPING')
            }
          ];
        }
      
      
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
