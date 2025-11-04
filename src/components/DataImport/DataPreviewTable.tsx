import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table2 } from 'lucide-react';

interface DataPreviewTableProps {
  previewData: {
    headers: string[];
    rows: any[][];
  };
}

const DataPreviewTable = ({ previewData }: DataPreviewTableProps) => {
  const { headers, rows } = previewData;
  const displayRows = rows.slice(0, 10); // 只显示前10行

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Table2 className="w-5 h-5 text-primary" />
          数据预览
          <span className="text-sm font-normal text-muted-foreground ml-2">
            (前 {displayRows.length} 行 / 共 {rows.length} 行)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse min-w-max">
            <thead>
              <tr className="border-b bg-accent">
                {headers.map((col, i) => (
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
              {displayRows.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b hover:bg-accent/50 transition-colors">
                  {row.map((value, colIndex) => (
                    <td 
                      key={colIndex}
                      className="px-4 py-3 text-sm text-foreground whitespace-nowrap min-w-[120px]"
                    >
                      {value !== null && value !== undefined ? String(value) : '-'}
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
