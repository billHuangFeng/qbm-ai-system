import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Wrench, AlertTriangle, CheckCircle2, Building2, Calculator } from 'lucide-react';

const DataEnhancementPanel = () => {
  // Mock enhancement tasks
  interface MasterDataItem {
    rowId: string;
    field: string;
    currentValue: null;
    auxiliaryInfo: string;
    suggestedValue: string | null;
    confidence: number;
  }

  interface CalculationItem {
    rowId: string;
    field: string;
    currentValue: string;
    calculatedValue: string;
    formula: string;
    suggestion: string;
  }

  const enhancementTasks = [
    {
      id: 1,
      type: 'master_data' as const,
      icon: Building2,
      title: '主数据ID匹配',
      description: '5 个往来单位需要匹配主数据ID',
      status: 'pending',
      items: [
        { 
          rowId: '#12', 
          field: '往来单位ID', 
          currentValue: null, 
          auxiliaryInfo: '北京科技有限公司',
          suggestedValue: 'PARTNER_001',
          confidence: 92 
        },
        { 
          rowId: '#45', 
          field: '往来单位ID', 
          currentValue: null, 
          auxiliaryInfo: '上海商贸公司',
          suggestedValue: 'PARTNER_023',
          confidence: 88 
        },
        { 
          rowId: '#78', 
          field: '往来单位ID', 
          currentValue: null, 
          auxiliaryInfo: '广州实业集团',
          suggestedValue: null,
          confidence: 0 
        },
      ] as MasterDataItem[]
    },
    {
      id: 2,
      type: 'calculation' as const,
      icon: Calculator,
      title: '计算字段冲突',
      description: '3 个订单存在计算冲突',
      status: 'pending',
      items: [
        { 
          rowId: '#12345', 
          field: '订单金额', 
          currentValue: '1000.01', 
          calculatedValue: '1000.00',
          formula: '数量(10) × 单价(100)',
          suggestion: '使用计算值 ¥1000.00' 
        },
        { 
          rowId: '#12346', 
          field: '含税金额', 
          currentValue: '1130.50', 
          calculatedValue: '1130.00',
          formula: '金额(1000) × (1 + 税率(0.13))',
          suggestion: '使用计算值 ¥1130.00' 
        },
      ] as CalculationItem[]
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wrench className="w-5 h-5 text-primary" />
          数据完善处理
          <span className="text-sm font-normal text-muted-foreground ml-2">
            (第二阶段)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {enhancementTasks.map((task) => {
            const Icon = task.icon;
            return (
              <div key={task.id} className="space-y-3">
                {/* Task Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className="w-5 h-5 text-primary" />
                    <div>
                      <h4 className="font-semibold text-foreground">{task.title}</h4>
                      <p className="text-xs text-muted-foreground">{task.description}</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    一键修复
                  </Button>
                </div>

                {/* Task Items */}
                <div className="space-y-2 pl-7">
                  {task.items.map((item, idx) => {
                    const isMasterData = task.type === 'master_data';
                    const masterItem = isMasterData ? item as MasterDataItem : null;
                    const calcItem = !isMasterData ? item as CalculationItem : null;
                    
                    return (
                      <div 
                        key={idx}
                        className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono text-muted-foreground">{item.rowId}</span>
                            <span className="text-sm font-medium text-foreground">{item.field}</span>
                          </div>
                          {isMasterData && masterItem && masterItem.confidence > 0 ? (
                            <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                              置信度 {masterItem.confidence}%
                            </span>
                          ) : isMasterData && masterItem && masterItem.confidence === 0 ? (
                            <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                              需手动选择
                            </span>
                          ) : null}
                        </div>

                        {/* Master Data Matching */}
                        {isMasterData && masterItem && (
                          <div className="space-y-1 text-sm">
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <span className="text-xs">辅助信息:</span>
                              <span>{masterItem.auxiliaryInfo}</span>
                            </div>
                            {masterItem.suggestedValue ? (
                              <div className="flex items-center gap-2 text-green-700">
                                <CheckCircle2 className="w-4 h-4" />
                                <span className="text-xs">建议匹配:</span>
                                <span className="font-medium">{masterItem.suggestedValue}</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2 text-yellow-700">
                                <AlertTriangle className="w-4 h-4" />
                                <span className="text-xs">未找到匹配，请手动选择</span>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Calculation Conflict */}
                        {!isMasterData && calcItem && (
                          <div className="space-y-1 text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-muted-foreground">当前值:</span>
                              <span className="text-red-600 line-through">¥{calcItem.currentValue}</span>
                            </div>
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <span className="text-xs">计算公式:</span>
                              <span className="text-xs font-mono">{calcItem.formula}</span>
                            </div>
                            <div className="flex items-center gap-2 text-green-700">
                              <CheckCircle2 className="w-4 h-4" />
                              <span className="text-xs">计算值:</span>
                              <span className="font-medium">¥{calcItem.calculatedValue}</span>
                            </div>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2 mt-3">
                          <Button variant="default" size="sm" className="flex-1">
                            应用建议
                          </Button>
                          <Button variant="outline" size="sm">
                            手动调整
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="mt-6 p-4 rounded-lg bg-primary/5 border border-primary/20">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-foreground">完善进度</div>
              <div className="text-xs text-muted-foreground mt-1">0 / 8 处问题已修复</div>
            </div>
            <Button variant="default">
              全部自动修复
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataEnhancementPanel;
