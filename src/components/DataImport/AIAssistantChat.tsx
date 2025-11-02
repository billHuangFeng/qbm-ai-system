import { useEffect, useState } from 'react';
import { Bot, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import type { ImportStage } from '@/pages/DataImportPage';

interface AIMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  content: string;
  timestamp: Date;
}

interface AIAssistantChatProps {
  currentStage: ImportStage;
}

const AIAssistantChat = ({ currentStage }: AIAssistantChatProps) => {
  const [messages, setMessages] = useState<AIMessage[]>([]);

  useEffect(() => {
    // Generate messages based on stage
    const newMessages = getMessagesForStage(currentStage);
    setMessages(prev => [...prev, ...newMessages]);
  }, [currentStage]);

  const getMessagesForStage = (stage: ImportStage): AIMessage[] => {
    const timestamp = new Date();
    
    switch(stage) {
      case 'UPLOAD':
        return [{
          id: `msg-${Date.now()}`,
          type: 'info',
          content: '👋 你好！我是智能导入助手。请上传您的数据文件，我会帮您自动处理。',
          timestamp
        }];
      
      case 'ANALYZING':
        return [{
          id: `msg-${Date.now()}`,
          type: 'info',
          content: '🔍 正在分析文件格式和内容...',
          timestamp
        }];
      
      case 'MAPPING':
        return [{
          id: `msg-${Date.now()}`,
          type: 'success',
          content: '✅ 文件分析完成！发现标准订单格式，已自动识别字段映射。',
          timestamp
        }, {
          id: `msg-${Date.now() + 1}`,
          type: 'info',
          content: '📊 检测到 5 个字段，映射置信度平均 90%。您可以在左侧查看和调整映射关系。',
          timestamp
        }];
      
      case 'QUALITY_CHECK':
        return [{
          id: `msg-${Date.now()}`,
          type: 'warning',
          content: '⚠️ 质量检查发现 3 个需要注意的问题，但不影响导入。建议查看并修复。',
          timestamp
        }];
      
      case 'READY':
        return [{
          id: `msg-${Date.now()}`,
          type: 'success',
          content: '🚀 一切就绪！数据质量良好，可以开始导入了。',
          timestamp
        }];
      
      default:
        return [];
    }
  };

  const getIcon = (type: AIMessage['type']) => {
    switch(type) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Bot className="w-5 h-5 text-primary" />;
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4 pb-4 border-b">
        <div className="p-2 rounded-lg bg-primary/10">
          <Bot className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-semibold text-foreground">AI 智能助手</h3>
          <p className="text-xs text-muted-foreground">实时引导和反馈</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2">
        {messages.map((message) => (
          <div 
            key={message.id}
            className="flex gap-3 animate-fade-in"
          >
            <div className="flex-shrink-0 mt-1">
              {getIcon(message.type)}
            </div>
            <div className="flex-1">
              <div className="text-sm text-foreground leading-relaxed">
                {message.content}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {message.timestamp.toLocaleTimeString('zh-CN', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
          </div>
        ))}
        
        {currentStage === 'ANALYZING' && (
          <div className="flex gap-3">
            <Loader2 className="w-5 h-5 text-primary animate-spin" />
            <div className="text-sm text-muted-foreground">处理中...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistantChat;
