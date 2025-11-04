/**
 * 文件解析工具
 * 支持 CSV, Excel, JSON
 */

export interface ParsedFileData {
  data: Array<Record<string, any>>;
  columns: string[];
  rowCount: number;
  columnCount: number;
}

// 解析 CSV 文件
export async function parseCSV(content: string): Promise<ParsedFileData> {
  const lines = content.split('\n').filter(line => line.trim());
  
  if (lines.length === 0) {
    return { data: [], columns: [], rowCount: 0, columnCount: 0 };
  }
  
  // 解析表头
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  
  // 解析数据行
  const data: Array<Record<string, any>> = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    const row: Record<string, any> = {};
    
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    
    data.push(row);
  }
  
  return {
    data,
    columns: headers,
    rowCount: data.length,
    columnCount: headers.length
  };
}

// 解析 Excel 文件（使用 xlsx library）
export async function parseExcel(buffer: ArrayBuffer): Promise<ParsedFileData> {
  try {
    // 动态导入 xlsx - 使用 esm.sh CDN
    const { read, utils } = await import('https://esm.sh/xlsx@0.18.5');
    
    const workbook = read(buffer, { type: 'array' });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    
    // 转换为 JSON
    const jsonData = utils.sheet_to_json(worksheet, { defval: '' });
    
    if (jsonData.length === 0) {
      return { data: [], columns: [], rowCount: 0, columnCount: 0 };
    }
    
    const columns = Object.keys(jsonData[0] as Record<string, any>);
    
    return {
      data: jsonData as Array<Record<string, any>>,
      columns,
      rowCount: jsonData.length,
      columnCount: columns.length
    };
  } catch (error: any) {
    console.error('Excel parsing error:', error);
    throw new Error(`Excel 文件解析失败: ${error?.message || 'Unknown error'}`);
  }
}

// 解析 JSON 文件
export async function parseJSON(content: string): Promise<ParsedFileData> {
  try {
    const jsonData = JSON.parse(content);
    
    // 如果是数组
    if (Array.isArray(jsonData)) {
      if (jsonData.length === 0) {
        return { data: [], columns: [], rowCount: 0, columnCount: 0 };
      }
      
      const columns = Object.keys(jsonData[0]);
      
      return {
        data: jsonData,
        columns,
        rowCount: jsonData.length,
        columnCount: columns.length
      };
    }
    
    // 如果是单个对象，包装成数组
    const columns = Object.keys(jsonData);
    return {
      data: [jsonData],
      columns,
      rowCount: 1,
      columnCount: columns.length
    };
  } catch (error: any) {
    throw new Error(`JSON 文件解析失败: ${error?.message || 'Unknown error'}`);
  }
}

// 主解析函数
export async function parseFile(file: File, fileExtension: string): Promise<ParsedFileData> {
  if (fileExtension === '.csv') {
    const content = await file.text();
    return parseCSV(content);
  } else if (fileExtension === '.xlsx' || fileExtension === '.xls') {
    const buffer = await file.arrayBuffer();
    return parseExcel(buffer);
  } else if (fileExtension === '.json') {
    const content = await file.text();
    return parseJSON(content);
  } else {
    throw new Error(`不支持的文件格式: ${fileExtension}`);
  }
}
