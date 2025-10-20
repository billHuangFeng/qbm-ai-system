import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface EvaluationPanelProps {
  analysisId: string;
}

export function EvaluationPanel({ analysisId }: EvaluationPanelProps) {
  const [metrics, setMetrics] = useState([]);
  const [evaluationContent, setEvaluationContent] = useState('');
  const [adjustments, setAdjustments] = useState([]);

  useEffect(() => {
    loadAnalysisResults();
  }, [analysisId]);

  const loadAnalysisResults = async () => {
    // 加载系统初步分析结果
    // 这里需要实现具体的API调用
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/manager-evaluation/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysisId,
          evaluationType: 'confirm',
          evaluationContent,
          metricAdjustments: adjustments
        })
      });

      const result = await response.json();
      
      if (result.success) {
        alert('评价提交成功！');
        setEvaluationContent('');
        setAdjustments([]);
      } else {
        alert('提交失败：' + (result.error ?? 'Unknown error'));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      alert('提交失败：' + message);
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">管理者评价确认</h2>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">系统初步分析结果</h3>
        <div className="bg-gray-50 p-4 rounded">
          {/* 显示指标和分析结果 */}
          <p>这里显示系统自动计算的指标和分析结果</p>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">评价意见</h3>
        <textarea
          className="w-full h-32 p-2 border rounded"
          placeholder="请输入您的评价、确认或澄清意见"
          value={evaluationContent}
          onChange={(e) => setEvaluationContent(e.target.value)}
        />
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">指标调整</h3>
        <div className="bg-gray-50 p-4 rounded">
          {/* 指标调整界面 */}
          <p>这里显示可调整的指标列表</p>
        </div>
      </div>

      <Button onClick={handleSubmit}>提交评价</Button>
    </Card>
  );
}
