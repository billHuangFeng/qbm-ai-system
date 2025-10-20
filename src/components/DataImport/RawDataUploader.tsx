import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface SelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}

function Select({ label, value, onChange, options }: SelectProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-2">{label}</label>
      <select
        className="w-full p-2 border rounded"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">请选择</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function RawDataUploader() {
  const [sourceSystem, setSourceSystem] = useState('');
  const [sourceType, setSourceType] = useState('');
  const [rawData, setRawData] = useState('');

  const handleUpload = async () => {
    try {
      const response = await fetch('/api/data-import/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sourceSystem,
          sourceType,
          rawData: JSON.parse(rawData),
          importMethod: 'manual'
        })
      });

      const result = await response.json();
      
      if (result.success) {
        alert('数据上传成功！');
        setRawData('');
      } else {
        alert('上传失败：' + (result.error ?? 'Unknown error'));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      alert('上传失败：' + message);
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">原始数据导入</h2>
      
      <Select 
        label="数据来源系统"
        value={sourceSystem}
        onChange={setSourceSystem}
        options={[
          { value: 'erp', label: 'ERP系统' },
          { value: 'crm', label: 'CRM系统' },
          { value: 'oa', label: 'OA系统' },
          { value: 'manual', label: '手动输入' }
        ]}
      />

      <Select 
        label="数据类型"
        value={sourceType}
        onChange={setSourceType}
        options={[
          { value: 'expense', label: '费用开支' },
          { value: 'asset', label: '资产购置' },
          { value: 'order', label: '订单数据' },
          { value: 'feedback', label: '客户反馈' }
        ]}
      />

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">原始数据 (JSON格式)</label>
        <textarea
          className="w-full h-64 p-2 border rounded"
          placeholder="粘贴JSON格式的原始数据"
          value={rawData}
          onChange={(e) => setRawData(e.target.value)}
        />
      </div>

      <Button onClick={handleUpload}>
        上传并处理
      </Button>
    </Card>
  );
}
