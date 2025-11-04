import { useEffect, useState, useRef } from 'react';
import { 
  CheckCircle2, 
  Circle, 
  Loader2, 
  AlertTriangle, 
  XCircle,
  ChevronDown,
  ChevronRight,
  Info,
  AlertCircle,
  Bot,
  Sparkles,
  Play,
  Settings,
  ArrowLeft,
  Upload
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ImportStage } from '@/pages/DataImportPage';

interface TaskMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  content: string;
  timestamp: Date;
}

interface TaskStage {
  key: ImportStage;
  label: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'warning' | 'error';
  messages: TaskMessage[];
}

interface UnifiedProgressGuideProps {
  currentStage: ImportStage;
  onStageChange?: (stage: ImportStage) => void;
  onFileUpload?: (file: File | null) => void;
  uploadResult?: any;
  qualityReport?: any;
  isLoading?: boolean;
  formatDetection?: any;
}

const UnifiedProgressGuide = ({ 
  currentStage, 
  onStageChange, 
  onFileUpload,
  uploadResult,
  qualityReport,
  isLoading = false,
  formatDetection
}: UnifiedProgressGuideProps) => {
  const [taskListExpanded, setTaskListExpanded] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [stages, setStages] = useState<TaskStage[]>([
    { key: 'UPLOAD', label: '上传文件', description: '选择数据文件', status: 'pending', messages: [] },
    { key: 'MAPPING', label: '字段映射', description: '智能字段匹配', status: 'pending', messages: [] },
    { key: 'ANALYZING', label: '格式识别', description: '基于映射识别格式', status: 'pending', messages: [] },
    { key: 'QUALITY_CHECK', label: '质量检查', description: '7维度分析', status: 'pending', messages: [] },
    { key: 'READY', label: '准备导入', description: '确认并导入', status: 'pending', messages: [] },
    { key: 'ENHANCEMENT', label: '数据完善', description: '第二阶段处理', status: 'pending', messages: [] },
    { key: 'CONFIRMING', label: '确认入库', description: '最终确认', status: 'pending', messages: [] },
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const getActions = (): Array<{
    label: string;
    variant: 'default' | 'outline';
    icon?: typeof Sparkles;
    position?: 'left' | 'right';
    onClick: () => void;
  }> => {
    if (!onStageChange) return [];

    switch(currentStage) {
      case 'UPLOAD':
        return [
          {
            label: '📤 上传文件',
            variant: 'default' as const,
            icon: Upload,
            position: 'right' as const,
            onClick: () => fileInputRef.current?.click()
          }
        ];
      
      case 'MAPPING':
        return [
          {
            label: '🛠️ 手动配置',
            variant: 'outline' as const,
            icon: Settings,
            position: 'left' as const,
            onClick: () => {}
          },
          {
            label: '✨ 应用 AI 推荐',
            variant: 'default' as const,
            icon: Sparkles,
            position: 'right' as const,
            onClick: () => onStageChange('ANALYZING')
          }
        ];
      
      case 'ANALYZING':
        return [];
      
      case 'QUALITY_CHECK':
        return [
          {
            label: '⏭️ 继续导入',
            variant: 'default' as const,
            position: 'right' as const,
            onClick: () => onStageChange('READY')
          }
        ];
      
      case 'READY':
        const qualityScore = 85;
        
        if (qualityScore >= 95) {
          return [
            {
              label: '🔙 返回调整',
              variant: 'outline' as const,
              icon: ArrowLeft,
              position: 'left' as const,
              onClick: () => onStageChange('MAPPING')
            },
            {
              label: '🚀 直接导入正式表',
              variant: 'default' as const,
              icon: Play,
              position: 'right' as const,
              onClick: () => onStageChange('IMPORTING')
            }
          ];
        } else if (qualityScore >= 70) {
          return [
            {
              label: '🔙 返回调整',
              variant: 'outline' as const,
              icon: ArrowLeft,
              position: 'left' as const,
              onClick: () => onStageChange('MAPPING')
            },
            {
              label: '⚠️ 强制导入正式表',
              variant: 'outline' as const,
              icon: Play,
              position: 'right' as const,
              onClick: () => onStageChange('IMPORTING')
            },
            {
              label: '📥 导入暂存表（推荐）',
              variant: 'default' as const,
              icon: Play,
              position: 'right' as const,
              onClick: () => onStageChange('ENHANCEMENT')
            }
          ];
        } else {
          return [
            {
              label: '⛔ 质量不合格，无法导入',
              variant: 'outline' as const,
              position: 'left' as const,
              onClick: () => {}
            },
            {
              label: '🔙 返回修复',
              variant: 'default' as const,
              icon: ArrowLeft,
              position: 'right' as const,
              onClick: () => onStageChange('MAPPING')
            }
          ];
        }
      
      case 'ENHANCEMENT':
        return [
          {
            label: '✅ 完成并确认',
            variant: 'outline' as const,
            position: 'left' as const,
            onClick: () => onStageChange('CONFIRMING')
          },
          {
            label: '🤖 全部自动修复',
            variant: 'default' as const,
            position: 'right' as const,
            onClick: () => onStageChange('CONFIRMING')
          }
        ];
      
      case 'CONFIRMING':
        return [
          {
            label: '🔙 返回调整',
            variant: 'outline' as const,
            icon: ArrowLeft,
            position: 'left' as const,
            onClick: () => onStageChange('ENHANCEMENT')
          },
          {
            label: '🚀 导入正式表',
            variant: 'default' as const,
            icon: Play,
            position: 'right' as const,
            onClick: () => onStageChange('COMPLETED')
          }
        ];
      
      default:
        return [];
    }
  };

  const generateMessagesForStage = (stage: ImportStage): TaskMessage[] => {
    const timestamp = new Date();
    
    switch(stage) {
      case 'UPLOAD':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '👋 你好！我是智能导入助手', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📤 请选择要导入的数据文件，支持 Excel、CSV、JSON、XML 格式', timestamp: new Date(timestamp.getTime() + 100) },
        ];
      
      case 'MAPPING':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🗺️ 开始智能字段映射...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📋 请确认数据类型：订单 / 生产 / 费用', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '🤖 正在应用历史学习经验...', timestamp: new Date(timestamp.getTime() + 200) },
          { id: `msg-${Date.now()}-4`, type: 'success', content: '✅ 已自动映射 10/12 字段', timestamp: new Date(timestamp.getTime() + 1500) },
          { id: `msg-${Date.now()}-5`, type: 'info', content: '📊 平均置信度: 92%', timestamp: new Date(timestamp.getTime() + 1600) },
          { id: `msg-${Date.now()}-6`, type: 'info', content: '✨ 高置信度字段: 订单号(98%), 日期(95%), 客户名称(90%)...', timestamp: new Date(timestamp.getTime() + 1700) },
          { id: `msg-${Date.now()}-7`, type: 'warning', content: '⚠️ 2 个字段需要手动确认:', timestamp: new Date(timestamp.getTime() + 1800) },
          { id: `msg-${Date.now()}-8`, type: 'warning', content: '   • "SKU编码" → "产品SKU" (置信度 75%)', timestamp: new Date(timestamp.getTime() + 1900) },
          { id: `msg-${Date.now()}-9`, type: 'warning', content: '   • "金额合计" → "订单金额" (置信度 68%)', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-10`, type: 'info', content: '💡 映射完成后，将基于目标字段识别数据格式', timestamp: new Date(timestamp.getTime() + 2100) },
        ];
      
      case 'ANALYZING':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🔍 正在分析数据格式...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📊 已知目标字段组合：订单号、日期、客户、产品SKU、数量、金额...', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '🎯 正在识别"订单数据"的具体格式...', timestamp: new Date(timestamp.getTime() + 200) },
          { id: `msg-${Date.now()}-4`, type: 'success', content: '✅ 检测到"订单数据 - 标准横表格式"（格式1）', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-5`, type: 'info', content: '📋 数据结构: 1,234 行 × 12 列', timestamp: new Date(timestamp.getTime() + 2100) },
          { id: `msg-${Date.now()}-6`, type: 'success', content: '✅ 格式识别完成', timestamp: new Date(timestamp.getTime() + 2200) },
          { id: `msg-${Date.now()}-7`, type: 'warning', content: '⚠️ 检测到 3 处合并单元格，已自动处理', timestamp: new Date(timestamp.getTime() + 2300) },
        ];
      
      case 'QUALITY_CHECK':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🔍 开始7维质量检查...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'success', content: '✅ 完整性检查: 通过 (96%)', timestamp: new Date(timestamp.getTime() + 500) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '   • 缺失 5 个往来单位ID，但存在单位名称可用于匹配', timestamp: new Date(timestamp.getTime() + 600) },
          { id: `msg-${Date.now()}-4`, type: 'success', content: '✅ 准确性检查: 通过 (98%)', timestamp: new Date(timestamp.getTime() + 1000) },
          { id: `msg-${Date.now()}-5`, type: 'success', content: '✅ 唯一性检查: 通过 (无重复)', timestamp: new Date(timestamp.getTime() + 1500) },
          { id: `msg-${Date.now()}-6`, type: 'warning', content: '⚠️ 一致性检查: 发现 3 个可修复的计算冲突', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-7`, type: 'info', content: '   • 订单 #12345: 数量×单价≠金额 (差异: ¥0.01, 可自动修复)', timestamp: new Date(timestamp.getTime() + 2100) },
          { id: `msg-${Date.now()}-8`, type: 'info', content: '   • 订单 #12346: 含税金额存在舍入误差 (可自动修复)', timestamp: new Date(timestamp.getTime() + 2200) },
          { id: `msg-${Date.now()}-9`, type: 'info', content: '   • 订单 #12347: 折扣后金额需要重新计算', timestamp: new Date(timestamp.getTime() + 2300) },
          { id: `msg-${Date.now()}-10`, type: 'success', content: '✅ 有效性检查: 通过', timestamp: new Date(timestamp.getTime() + 2700) },
          { id: `msg-${Date.now()}-11`, type: 'success', content: '✅ 及时性检查: 通过', timestamp: new Date(timestamp.getTime() + 3200) },
          { id: `msg-${Date.now()}-12`, type: 'warning', content: '⚠️ 参照完整性检查: 5 个主数据ID待完善', timestamp: new Date(timestamp.getTime() + 3700) },
          { id: `msg-${Date.now()}-13`, type: 'info', content: '   • 可通过"往来单位名称"自动匹配主数据ID', timestamp: new Date(timestamp.getTime() + 3800) },
          { id: `msg-${Date.now()}-14`, type: 'info', content: '   • 或在第二阶段手动选择关联主数据', timestamp: new Date(timestamp.getTime() + 3900) },
          { id: `msg-${Date.now()}-15`, type: 'info', content: '📊 综合质量评分: 85 分（良好）', timestamp: new Date(timestamp.getTime() + 4200) },
          { id: `msg-${Date.now()}-16`, type: 'success', content: '✅ 可导入性评级: 良好（建议先导入暂存表，完善后再入库）', timestamp: new Date(timestamp.getTime() + 4300) },
          { id: `msg-${Date.now()}-17`, type: 'info', content: '💡 阻塞性问题: 0 个 | 可修复问题: 8 个', timestamp: new Date(timestamp.getTime() + 4400) },
          { id: `msg-${Date.now()}-18`, type: 'success', content: '✅ 所有问题可在第二阶段完善处理', timestamp: new Date(timestamp.getTime() + 4500) },
        ];
      
      case 'READY':
        return [
          { id: `msg-${Date.now()}-1`, type: 'success', content: '🚀 一切就绪！', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📊 数据质量评分: 85 分（良好）', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '📋 映射字段: 12 个', timestamp: new Date(timestamp.getTime() + 200) },
          { id: `msg-${Date.now()}-4`, type: 'info', content: '📈 待导入记录: 1,234 行', timestamp: new Date(timestamp.getTime() + 300) },
          { id: `msg-${Date.now()}-5`, type: 'info', content: '💡 建议先导入暂存表，完善后再入库', timestamp: new Date(timestamp.getTime() + 400) },
          { id: `msg-${Date.now()}-6`, type: 'success', content: '✅ 点击下方按钮选择导入方式', timestamp: new Date(timestamp.getTime() + 500) },
        ];
      
      case 'ENHANCEMENT':
        return [
          { id: `msg-${Date.now()}-1`, type: 'success', content: '✅ 数据已导入暂存表', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '🔧 开始第二阶段数据完善处理...', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '🏢 正在匹配主数据ID...', timestamp: new Date(timestamp.getTime() + 500) },
          { id: `msg-${Date.now()}-4`, type: 'success', content: '   • 自动匹配成功: 3/5 个往来单位', timestamp: new Date(timestamp.getTime() + 1500) },
          { id: `msg-${Date.now()}-5`, type: 'warning', content: '   • 需手动选择: 2 个往来单位', timestamp: new Date(timestamp.getTime() + 1600) },
          { id: `msg-${Date.now()}-6`, type: 'info', content: '🧮 正在处理计算字段冲突...', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-7`, type: 'success', content: '   • 可自动修复: 3 处计算冲突', timestamp: new Date(timestamp.getTime() + 2500) },
          { id: `msg-${Date.now()}-8`, type: 'info', content: '📊 完善进度: 0 / 8 处问题已修复', timestamp: new Date(timestamp.getTime() + 3000) },
          { id: `msg-${Date.now()}-9`, type: 'info', content: '💡 请在左侧面板处理待完善的数据', timestamp: new Date(timestamp.getTime() + 3100) },
        ];
      
      case 'CONFIRMING':
        return [
          { id: `msg-${Date.now()}-1`, type: 'success', content: '✅ 所有问题已完善', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📊 完善统计:', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '   • 主数据ID匹配: 5 处', timestamp: new Date(timestamp.getTime() + 200) },
          { id: `msg-${Date.now()}-4`, type: 'info', content: '   • 计算冲突修复: 3 处', timestamp: new Date(timestamp.getTime() + 300) },
          { id: `msg-${Date.now()}-5`, type: 'success', content: '✅ 数据质量评分: 98 分（优秀）', timestamp: new Date(timestamp.getTime() + 500) },
          { id: `msg-${Date.now()}-6`, type: 'info', content: '🎯 待入库记录: 1,234 行', timestamp: new Date(timestamp.getTime() + 600) },
          { id: `msg-${Date.now()}-7`, type: 'success', content: '✅ 可以导入正式表了', timestamp: new Date(timestamp.getTime() + 700) },
        ];
      
      default:
        return [];
    }
  };

  useEffect(() => {
    const currentIndex = stages.findIndex(s => s.key === currentStage);
    
    setStages(prev => prev.map((stage, index) => {
      if (index < currentIndex) {
        return { ...stage, status: 'completed' as const };
      } else if (index === currentIndex) {
        const newMessages = stage.messages.length === 0 ? generateMessagesForStage(currentStage) : stage.messages;
        const newStatus = currentStage === 'QUALITY_CHECK' ? 'warning' : 'active';
        return { 
          ...stage, 
          status: newStatus,
          messages: newMessages
        };
      } else {
        return { ...stage, status: 'pending' as const };
      }
    }));
  }, [currentStage]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [stages]);

  const getStatusIcon = (status: TaskStage['status']) => {
    switch(status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'active':
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Circle className="w-5 h-5 text-muted-foreground/30" />;
    }
  };

  const getMessageIcon = (type: TaskMessage['type']) => {
    switch(type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />;
      default:
        return <Info className="w-4 h-4 text-blue-500 flex-shrink-0" />;
    }
  };

  const activeStage = stages.find(s => s.status === 'active' || s.status === 'warning');
  const completedCount = stages.filter(s => s.status === 'completed').length;
  const totalCount = stages.length;
  const actions = getActions();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0 && onFileUpload) {
      onFileUpload(files[0]);
      if (onStageChange) {
        onStageChange('MAPPING');
      }
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".xlsx,.xls,.csv,.json,.xml"
        onChange={handleFileSelect}
      />
      
      {/* 当前任务信息卡片 */}
      {activeStage && (
        <div className="border rounded-lg overflow-hidden border-l-4 border-l-primary flex-shrink-0">
          <div className="flex items-center gap-3 px-4 py-3 bg-primary/5">
            <div className="p-2 rounded-lg bg-primary/10 flex-shrink-0">
              <Bot className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                {getStatusIcon(activeStage.status)}
                <h3 className="font-semibold text-foreground">当前任务：{activeStage.label}</h3>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{activeStage.description}</p>
            </div>
          </div>
          
          <div className="px-4 py-3 bg-muted/30 border-t">
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {activeStage.messages.map((message) => (
                <div key={message.id} className="animate-fade-in">
                  <div className="flex gap-2 items-start">
                    {getMessageIcon(message.type)}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground/70 mt-0.5 ml-6">
                    {message.timestamp.toLocaleTimeString('zh-CN', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* 操作按钮区域 - 水平左右分布 */}
          {actions.length > 0 && (
            <div className="px-4 py-3 bg-card border-t flex items-center justify-between gap-3">
              {/* 左侧按钮组 */}
              <div className="flex gap-2">
                {actions
                  .filter(action => action.position === 'left')
                  .map((action, index) => {
                    const Icon = action.icon;
                    return (
                      <Button
                        key={index}
                        variant={action.variant}
                        size="sm"
                        onClick={action.onClick}
                      >
                        {Icon && <Icon className="w-3.5 h-3.5 mr-1.5" />}
                        {action.label}
                      </Button>
                    );
                  })}
              </div>

              {/* 右侧按钮组 */}
              <div className="flex gap-2">
                {actions
                  .filter(action => action.position !== 'left')
                  .map((action, index) => {
                    const Icon = action.icon;
                    return (
                      <Button
                        key={index}
                        variant={action.variant}
                        size="sm"
                        onClick={action.onClick}
                      >
                        {Icon && <Icon className="w-3.5 h-3.5 mr-1.5" />}
                        {action.label}
                      </Button>
                    );
                  })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 任务清单卡片 */}
      <div className="border rounded-lg overflow-hidden">
        <div
          className="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-accent/50 transition-colors"
          onClick={() => setTaskListExpanded(!taskListExpanded)}
        >
          <div className="flex items-center gap-2">
            {taskListExpanded ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            )}
            <span className="font-medium text-foreground">
              {completedCount} / {totalCount} 任务
            </span>
          </div>
        </div>

        {taskListExpanded && (
          <div className="px-4 py-2 space-y-1 border-t bg-muted/30 animate-accordion-down">
            {stages.map((stage) => (
              <div key={stage.key} className="flex items-center gap-2 py-1">
                <div className="flex-shrink-0">
                  {getStatusIcon(stage.status)}
                </div>
                <span className={`text-sm ${stage.status === 'completed' ? 'line-through opacity-60' : ''}`}>
                  {stage.label}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedProgressGuide;
