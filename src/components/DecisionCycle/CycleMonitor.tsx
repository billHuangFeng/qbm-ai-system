import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export function CycleMonitor() {
  const [executions, setExecutions] = useState([]);
  const [triggers, setTriggers] = useState([]);

  useEffect(() => {
    loadCycleData();
  }, []);

  const loadCycleData = async () => {
    // 从Supabase加载循环执行记录和触发器配置
    // 这里需要实现具体的API调用
  };

  const handleManualTrigger = async () => {
    try {
      const response = await fetch('/api/decision-cycle/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ triggerId: 'manual' })
      });

      const result = await response.json();
      
      if (result.success) {
        alert('决策循环已触发！');
        loadCycleData(); // 重新加载数据
      } else {
        alert('触发失败：' + result.error);
      }
    } catch (error) {
      alert('触发失败：' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">决策循环监控</h1>
        <Button onClick={handleManualTrigger}>手动触发分析</Button>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">当前循环状态</h2>
        <div className="bg-gray-50 p-4 rounded">
          {/* 显示当前正在运行的循环 */}
          <p>当前没有正在运行的决策循环</p>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">循环执行历史</h2>
        <div className="bg-gray-50 p-4 rounded">
          {/* 显示历史执行记录 */}
          <p>暂无执行记录</p>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">触发器配置</h2>
        <div className="bg-gray-50 p-4 rounded">
          {/* 显示和管理触发器 */}
          <p>暂无触发器配置</p>
        </div>
      </Card>
    </div>
  );
}
