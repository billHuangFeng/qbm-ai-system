/**
 * 格式识别算法 (Algorithm 1)
 * 自动识别6种单据格式
 */

export enum DocumentFormatType {
  REPEATED_HEADER = "repeated_header",       // 格式1: 多行明细对应重复单据头
  FIRST_ROW_HEADER = "first_row_header",     // 格式2: 多行明细但只有第一行有单据头
  SEPARATE_HEADER_BODY = "separate_header_body", // 格式3: 单据头和明细分离
  HEADER_ONLY = "header_only",               // 格式4: 只有单据头记录
  DETAIL_ONLY = "detail_only",               // 格式5: 只有明细记录
  PURE_HEADER = "pure_header"                // 格式6: 纯单据头记录
}

export interface FormatDetectionResult {
  formatType: DocumentFormatType;
  confidence: number; // 0-1
  details: Record<string, any>;
}

// 查找列名（支持多种别名）
function findColumn(data: Array<Record<string, any>>, possibleNames: string[]): string | null {
  if (data.length === 0) return null;
  
  const firstRow = data[0];
  const columns = Object.keys(firstRow);
  
  for (const colName of columns) {
    const normalizedCol = colName.toLowerCase().trim();
    for (const possible of possibleNames) {
      if (normalizedCol.includes(possible.toLowerCase()) || 
          possible.toLowerCase().includes(normalizedCol)) {
        return colName;
      }
    }
  }
  
  return null;
}

// 查找多个列名
function findColumns(data: Array<Record<string, any>>, possibleNames: string[]): string[] {
  if (data.length === 0) return [];
  
  const firstRow = data[0];
  const columns = Object.keys(firstRow);
  const found: string[] = [];
  
  for (const colName of columns) {
    const normalizedCol = colName.toLowerCase().trim();
    for (const possible of possibleNames) {
      if (normalizedCol.includes(possible.toLowerCase()) || 
          possible.toLowerCase().includes(normalizedCol)) {
        found.push(colName);
        break;
      }
    }
  }
  
  return found;
}

// 格式1: 重复单据头检测
function detectRepeatedHeader(data: Array<Record<string, any>>): [number, any] {
  const docNumberCol = findColumn(data, ['单据号', 'document_number', 'document_id', '单号', '订单号']);
  if (!docNumberCol) return [0.0, { reason: '未找到单据号字段' }];
  
  const uniqueDocs = new Set(data.map(row => row[docNumberCol])).size;
  const totalRows = data.length;
  
  if (totalRows === 0) return [0.0, { reason: '数据为空' }];
  
  const duplicateRatio = 1.0 - (uniqueDocs / totalRows);
  
  if (duplicateRatio > 0.2) {
    const confidence = Math.min(0.9, 0.7 + duplicateRatio * 0.5);
    return [confidence, {
      uniqueDocs,
      totalRows,
      duplicateRatio,
      reason: `检测到重复单据头，唯一单据数: ${uniqueDocs}, 总行数: ${totalRows}`
    }];
  }
  
  return [0.3, { reason: '单据号重复率较低' }];
}

// 格式2: 第一行单据头检测
function detectFirstRowHeader(data: Array<Record<string, any>>): [number, any] {
  if (data.length < 2) return [0.0, { reason: '数据行数不足' }];
  
  const headerFields = ['单据号', 'document_number', '单据日期', 'document_date', 
                        '客户名称', 'customer_name', '不含税金额', 'ex_tax_amount'];
  const headerCols = findColumns(data, headerFields);
  
  if (headerCols.length === 0) return [0.0, { reason: '未找到单据头字段' }];
  
  let emptyCount = 0;
  let totalFields = 0;
  
  for (let i = 1; i < data.length; i++) {
    for (const col of headerCols) {
      totalFields++;
      if (!data[i][col] || data[i][col] === '' || data[i][col] === null) {
        emptyCount++;
      }
    }
  }
  
  const emptyRatio = emptyCount / totalFields;
  
  if (emptyRatio > 0.3) {
    const confidence = Math.min(0.95, 0.7 + emptyRatio * 0.5);
    return [confidence, {
      emptyRatio,
      reason: `第二行及之后单据头字段空值比例: ${(emptyRatio * 100).toFixed(1)}%`
    }];
  }
  
  return [0.2, { reason: '单据头字段空值比例较低' }];
}

// 格式3: 单据头和明细分离检测
function detectSeparateHeaderBody(data: Array<Record<string, any>>): [number, any] {
  if (data.length < 3) return [0.0, { reason: '数据行数不足' }];
  
  const headerKeywords = ['单据头', 'header', '合计', 'total', '汇总'];
  const detailKeywords = ['明细', 'detail', '行项目', 'line'];
  
  const firstRow = data[0];
  const firstRowStr = JSON.stringify(firstRow).toLowerCase();
  
  const hasHeaderIndicator = headerKeywords.some(kw => firstRowStr.includes(kw));
  const hasDetailIndicator = detailKeywords.some(kw => 
    data.slice(1).some(row => JSON.stringify(row).toLowerCase().includes(kw))
  );
  
  if (hasHeaderIndicator || hasDetailIndicator) {
    return [0.8, {
      hasHeaderIndicator,
      hasDetailIndicator,
      reason: '检测到单据头和明细分离标识'
    }];
  }
  
  return [0.1, { reason: '未检测到分离标识' }];
}

// 格式4: 只有单据头检测
function detectHeaderOnly(data: Array<Record<string, any>>): [number, any] {
  const docNumberCol = findColumn(data, ['单据号', 'document_number', '订单号']);
  if (!docNumberCol) return [0.2, { reason: '未找到单据号字段' }];
  
  const detailKeywords = ['产品', 'product', 'sku', '数量', 'quantity', '单价', 'price'];
  const detailCols = findColumns(data, detailKeywords);
  
  if (detailCols.length === 0) {
    const uniqueDocs = new Set(data.map(row => row[docNumberCol])).size;
    const totalRows = data.length;
    
    if (uniqueDocs === totalRows) {
      return [0.85, {
        reason: '未检测到明细字段，且每行单据号唯一',
        uniqueDocs,
        totalRows
      }];
    }
  }
  
  return [0.15, { reason: '检测到明细字段或单据号重复' }];
}

// 格式5: 只有明细检测
function detectDetailOnly(data: Array<Record<string, any>>): [number, any] {
  const docNumberCol = findColumn(data, ['单据号', 'document_number']);
  const detailKeywords = ['产品', 'product', 'sku', '数量', 'quantity'];
  const detailCols = findColumns(data, detailKeywords);
  
  if (docNumberCol && detailCols.length > 0) {
    const headerFields = ['客户', 'customer', '单据日期', 'date', '金额', 'amount'];
    const headerCols = findColumns(data, headerFields);
    
    if (headerCols.length === 0) {
      return [0.8, {
        reason: '检测到明细字段但无单据头字段',
        detailCols: detailCols.length
      }];
    }
  }
  
  return [0.1, { reason: '未检测到纯明细特征' }];
}

// 格式6: 纯单据头记录检测
function detectPureHeader(data: Array<Record<string, any>>): [number, any] {
  const headerKeywords = ['单据号', 'document', '客户', 'customer', '日期', 'date', '金额', 'amount'];
  const headerCols = findColumns(data, headerKeywords);
  
  const detailKeywords = ['产品', 'product', 'sku', '数量', 'quantity', '单价'];
  const detailCols = findColumns(data, detailKeywords);
  
  if (headerCols.length >= 3 && detailCols.length === 0) {
    return [0.9, {
      reason: '检测到单据头字段但无明细字段',
      headerCols: headerCols.length
    }];
  }
  
  return [0.1, { reason: '未检测到纯单据头特征' }];
}

// 主检测函数
export async function detectFormat(
  data: Array<Record<string, any>>,
  metadata?: Record<string, any>
): Promise<FormatDetectionResult> {
  if (!data || data.length === 0) {
    return {
      formatType: DocumentFormatType.HEADER_ONLY,
      confidence: 0.0,
      details: { reason: '数据为空' }
    };
  }
  
  // 并行检测所有格式类型
  const [repeatedScore, repeatedDetail] = detectRepeatedHeader(data);
  const [firstRowScore, firstRowDetail] = detectFirstRowHeader(data);
  const [separateScore, separateDetail] = detectSeparateHeaderBody(data);
  const [headerOnlyScore, headerOnlyDetail] = detectHeaderOnly(data);
  const [detailOnlyScore, detailOnlyDetail] = detectDetailOnly(data);
  const [pureHeaderScore, pureHeaderDetail] = detectPureHeader(data);
  
  const scores: Record<DocumentFormatType, number> = {
    [DocumentFormatType.REPEATED_HEADER]: repeatedScore,
    [DocumentFormatType.FIRST_ROW_HEADER]: firstRowScore,
    [DocumentFormatType.SEPARATE_HEADER_BODY]: separateScore,
    [DocumentFormatType.HEADER_ONLY]: headerOnlyScore,
    [DocumentFormatType.DETAIL_ONLY]: detailOnlyScore,
    [DocumentFormatType.PURE_HEADER]: pureHeaderScore
  };
  
  const details: Record<string, any> = {
    [DocumentFormatType.REPEATED_HEADER]: repeatedDetail,
    [DocumentFormatType.FIRST_ROW_HEADER]: firstRowDetail,
    [DocumentFormatType.SEPARATE_HEADER_BODY]: separateDetail,
    [DocumentFormatType.HEADER_ONLY]: headerOnlyDetail,
    [DocumentFormatType.DETAIL_ONLY]: detailOnlyDetail,
    [DocumentFormatType.PURE_HEADER]: pureHeaderDetail
  };
  
  // 选择得分最高的格式
  const entries = Object.entries(scores) as [DocumentFormatType, number][];
  const [bestFormat, bestScore] = entries.sort(([, a], [, b]) => b - a)[0];
  
  return {
    formatType: bestFormat,
    confidence: bestScore,
    details: {
      allScores: scores,
      bestDetail: details[bestFormat]
    }
  };
}
