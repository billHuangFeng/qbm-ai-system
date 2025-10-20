import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface TableProps {
  data: any[];
  columns: { key: string; label: string }[];
}

function Table({ data, columns }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full table-auto">
        <thead>
          <tr className="bg-gray-50">
            {columns.map((column) => (
              <th key={column.key} className="px-4 py-2 text-left">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className="border-b">
              {columns.map((column) => (
                <td key={column.key} className="px-4 py-2">
                  {row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ControllableFactsManager() {
  const [expenses, setExpenses] = useState([]);
  const [assets, setAssets] = useState([]);
  const [selectedTab, setSelectedTab] = useState('expense');

  useEffect(() => {
    loadBusinessFacts();
  }, [selectedTab]);

  const loadBusinessFacts = async () => {
    // 从Supabase加载业务事实数据
    // 这里需要实现具体的API调用
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">业务事实管理</h1>

      <div className="flex gap-2">
        <Button 
          onClick={() => setSelectedTab('expense')}
          className={selectedTab === 'expense' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          费用开支
        </Button>
        <Button 
          onClick={() => setSelectedTab('asset')}
          className={selectedTab === 'asset' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          资产购置
        </Button>
        <Button 
          onClick={() => setSelectedTab('procurement')}
          className={selectedTab === 'procurement' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          采购目录
        </Button>
        <Button 
          onClick={() => setSelectedTab('sales')}
          className={selectedTab === 'sales' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          销售目录
        </Button>
        <Button 
          onClick={() => setSelectedTab('rd')}
          className={selectedTab === 'rd' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          研发项目
        </Button>
        <Button 
          onClick={() => setSelectedTab('promotion')}
          className={selectedTab === 'promotion' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}
        >
          推广活动
        </Button>
      </div>

      {selectedTab === 'expense' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">费用开支</h2>
          <Table data={expenses} columns={[
            { key: 'expense_type', label: '费用类型' },
            { key: 'expense_amount', label: '金额' },
            { key: 'expense_date', label: '日期' },
            { key: 'department', label: '部门' }
          ]} />
        </Card>
      )}

      {selectedTab === 'asset' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">资产购置</h2>
          <Table data={assets} columns={[
            { key: 'asset_type', label: '资产类型' },
            { key: 'acquisition_cost', label: '购置成本' },
            { key: 'acquisition_date', label: '购置日期' },
            { key: 'expected_life_years', label: '预期年限' }
          ]} />
        </Card>
      )}

      {/* 其他标签页类似实现 */}
    </div>
  );
}
