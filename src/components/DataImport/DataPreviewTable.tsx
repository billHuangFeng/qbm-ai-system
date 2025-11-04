import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table2 } from 'lucide-react';

const DataPreviewTable = () => {
  // Mock data for skeleton
  const mockColumns = ['订单号', '日期', '客户名称', '产品SKU', '数量', '单价', '金额'];
  const mockRows = Array(10).fill(null).map((_, i) => ({
    id: i,
    values: mockColumns.map(() => '数据加载中...')
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Table2 className="w-5 h-5 text-primary" />
          数据预览
          <span className="text-sm font-normal text-muted-foreground ml-2">
            (前 10 行)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse min-w-max">
            <thead>
              <tr className="border-b bg-accent">
                {mockColumns.map((col, i) => (
                  <th 
                    key={i}
                    className="px-4 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap min-w-[120px]"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockRows.map((row) => (
                <tr key={row.id} className="border-b hover:bg-accent/50 transition-colors">
                  {row.values.map((value, i) => (
                    <td 
                      key={i}
                      className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap min-w-[120px]"
                    >
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataPreviewTable;
