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
  Bot
} from 'lucide-react';
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
  isExpanded: boolean;
}

interface UnifiedProgressGuideProps {
  currentStage: ImportStage;
}

const UnifiedProgressGuide = ({ currentStage }: UnifiedProgressGuideProps) => {
  const [stages, setStages] = useState<TaskStage[]>([
    { key: 'UPLOAD', label: '上传文件', description: '选择数据文件', status: 'pending', messages: [], isExpanded: false },
    { key: 'ANALYZING', label: '格式识别', description: '分析文件结构', status: 'pending', messages: [], isExpanded: false },
    { key: 'MAPPING', label: '字段映射', description: '智能字段匹配', status: 'pending', messages: [], isExpanded: false },
    { key: 'QUALITY_CHECK', label: '质量检查', description: '7维度分析', status: 'pending', messages: [], isExpanded: false },
    { key: 'READY', label: '准备导入', description: '确认并导入', status: 'pending', messages: [], isExpanded: false },
  ]);

  const messagesEndRef = useRef<{ [key: string]: HTMLDivElement | null }>({});

  const generateMessagesForStage = (stage: ImportStage): TaskMessage[] => {
    const timestamp = new Date();
    
    switch(stage) {
      case 'UPLOAD':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '👋 你好！我是智能导入助手', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📤 请选择要导入的数据文件，支持 Excel、CSV、JSON、XML 格式', timestamp: new Date(timestamp.getTime() + 100) },
        ];
      
      case 'ANALYZING':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🔍 正在分析文件格式和内容结构...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '⏱️ 预计需要 3 秒', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'success', content: '✅ 检测到"标准横表格式"（格式1）', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-4`, type: 'info', content: '📋 识别出 12 个字段', timestamp: new Date(timestamp.getTime() + 2100) },
          { id: `msg-${Date.now()}-5`, type: 'info', content: '📊 数据行: 1,234 行 × 12 列', timestamp: new Date(timestamp.getTime() + 2200) },
          { id: `msg-${Date.now()}-6`, type: 'success', content: '✅ 表头识别成功', timestamp: new Date(timestamp.getTime() + 2300) },
        ];
      
      case 'MAPPING':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🗺️ 开始智能字段映射...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '🤖 正在应用历史学习经验', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'success', content: '✅ 已自动映射 10/12 字段', timestamp: new Date(timestamp.getTime() + 1500) },
          { id: `msg-${Date.now()}-4`, type: 'info', content: '📊 平均置信度: 92%', timestamp: new Date(timestamp.getTime() + 1600) },
          { id: `msg-${Date.now()}-5`, type: 'info', content: '✨ 高置信度字段: 订单号(98%), 日期(95%), 客户名称(90%)...', timestamp: new Date(timestamp.getTime() + 1700) },
          { id: `msg-${Date.now()}-6`, type: 'warning', content: '⚠️ 2 个字段需要手动确认', timestamp: new Date(timestamp.getTime() + 1800) },
          { id: `msg-${Date.now()}-7`, type: 'warning', content: '   • "SKU编码" → "产品SKU" (置信度 75%)', timestamp: new Date(timestamp.getTime() + 1900) },
          { id: `msg-${Date.now()}-8`, type: 'warning', content: '   • "金额合计" → "订单金额" (置信度 68%)', timestamp: new Date(timestamp.getTime() + 2000) },
        ];
      
      case 'QUALITY_CHECK':
        return [
          { id: `msg-${Date.now()}-1`, type: 'info', content: '🔍 开始7维质量检查...', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'success', content: '✅ 完整性检查: 通过 (100%)', timestamp: new Date(timestamp.getTime() + 500) },
          { id: `msg-${Date.now()}-3`, type: 'success', content: '✅ 准确性检查: 通过 (98%)', timestamp: new Date(timestamp.getTime() + 1000) },
          { id: `msg-${Date.now()}-4`, type: 'success', content: '✅ 唯一性检查: 通过 (无重复)', timestamp: new Date(timestamp.getTime() + 1500) },
          { id: `msg-${Date.now()}-5`, type: 'warning', content: '⚠️ 一致性检查: 发现 3 个需要注意的问题', timestamp: new Date(timestamp.getTime() + 2000) },
          { id: `msg-${Date.now()}-6`, type: 'info', content: '   • 订单 #12345: 数量 × 单价 ≠ 金额 (差异: ¥0.01)', timestamp: new Date(timestamp.getTime() + 2100) },
          { id: `msg-${Date.now()}-7`, type: 'info', content: '   • 订单 #12346: 含税金额计算存在舍入误差', timestamp: new Date(timestamp.getTime() + 2200) },
          { id: `msg-${Date.now()}-8`, type: 'success', content: '✅ 有效性检查: 通过', timestamp: new Date(timestamp.getTime() + 2700) },
          { id: `msg-${Date.now()}-9`, type: 'success', content: '✅ 及时性检查: 通过', timestamp: new Date(timestamp.getTime() + 3200) },
          { id: `msg-${Date.now()}-10`, type: 'success', content: '✅ 参照完整性检查: 通过', timestamp: new Date(timestamp.getTime() + 3700) },
          { id: `msg-${Date.now()}-11`, type: 'info', content: '📊 综合质量评分: 85 分（良好）', timestamp: new Date(timestamp.getTime() + 4000) },
          { id: `msg-${Date.now()}-12`, type: 'info', content: '💡 建议查看并修复一致性问题，但不影响导入', timestamp: new Date(timestamp.getTime() + 4100) },
          { id: `msg-${Date.now()}-13`, type: 'success', content: '✅ 可以继续导入', timestamp: new Date(timestamp.getTime() + 4200) },
        ];
      
      case 'READY':
        return [
          { id: `msg-${Date.now()}-1`, type: 'success', content: '🚀 一切就绪！', timestamp },
          { id: `msg-${Date.now()}-2`, type: 'info', content: '📊 数据质量评分: 85 分（良好）', timestamp: new Date(timestamp.getTime() + 100) },
          { id: `msg-${Date.now()}-3`, type: 'info', content: '📋 映射字段: 12 个', timestamp: new Date(timestamp.getTime() + 200) },
          { id: `msg-${Date.now()}-4`, type: 'info', content: '📈 待导入记录: 1,234 行', timestamp: new Date(timestamp.getTime() + 300) },
          { id: `msg-${Date.now()}-5`, type: 'success', content: '✅ 点击下方"开始导入"按钮即可开始', timestamp: new Date(timestamp.getTime() + 400) },
        ];
      
      default:
        return [];
    }
  };

  useEffect(() => {
    const currentIndex = stages.findIndex(s => s.key === currentStage);
    
    setStages(prev => prev.map((stage, index) => {
      if (index < currentIndex) {
        return { ...stage, status: 'completed' as const, isExpanded: false };
      } else if (index === currentIndex) {
        const newMessages = stage.messages.length === 0 ? generateMessagesForStage(currentStage) : stage.messages;
        const newStatus = currentStage === 'QUALITY_CHECK' ? 'warning' : 'active';
        return { 
          ...stage, 
          status: newStatus,
          isExpanded: true,
          messages: newMessages
        };
      } else {
        return { ...stage, status: 'pending' as const, isExpanded: false };
      }
    }));
  }, [currentStage]);

  useEffect(() => {
    const activeStage = stages.find(s => s.isExpanded);
    if (activeStage && messagesEndRef.current[activeStage.key]) {
      messagesEndRef.current[activeStage.key]?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [stages]);

  const toggleStage = (stageKey: ImportStage) => {
    setStages(prev => prev.map(stage => 
      stage.key === stageKey 
        ? { ...stage, isExpanded: !stage.isExpanded }
        : stage
    ));
  };

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

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4 pb-4 border-b">
        <div className="p-2 rounded-lg bg-primary/10">
          <Bot className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-semibold text-foreground">AI 智能导入引导</h3>
          <p className="text-xs text-muted-foreground">实时进度与反馈</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-2">
        {stages.map((stage) => (
          <div key={stage.key} className="border rounded-lg overflow-hidden">
            <div
              className={`
                flex items-center gap-3 px-4 py-3 cursor-pointer transition-all
                hover:bg-accent/50
                ${stage.status === 'active' ? 'bg-primary/5 border-l-4 border-l-primary' : ''}
                ${stage.status === 'completed' ? 'opacity-70' : ''}
              `}
              onClick={() => toggleStage(stage.key)}
            >
              <div className="flex-shrink-0">
                {getStatusIcon(stage.status)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground">
                  {stage.label}
                </div>
                <div className="text-xs text-muted-foreground">
                  {stage.description}
                </div>
              </div>

              <div className="flex-shrink-0">
                {stage.isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </div>

            {stage.isExpanded && (
              <div className="px-4 py-3 bg-muted/30 border-t animate-accordion-down">
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {stage.messages.map((message) => (
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
                  <div ref={(el) => { messagesEndRef.current[stage.key] = el; }} />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default UnifiedProgressGuide;
