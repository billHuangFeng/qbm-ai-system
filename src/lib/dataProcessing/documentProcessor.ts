/**
 * 复杂单据格式处理器
 * 支持6种复杂单据格式的智能处理
 */

export interface DocumentData {
  [key: string]: any;
}

export interface ProcessResult {
  success: boolean;
  processedData?: DocumentData[];
  error?: string;
  formatType?: string;
  recordsProcessed?: number;
  qualityScore?: number;
}

export interface DocumentFormat {
  type: 'repeated_header' | 'first_row_header' | 'separated_tables' | 'header_only' | 'detail_only' | 'pure_header';
  confidence: number;
  characteristics: string[];
}

/**
 * 单据格式检测器
 */
export class DocumentFormatDetector {
  private formatPatterns = {
    repeated_header: this.detectRepeatedHeader.bind(this),
    first_row_header: this.detectFirstRowHeader.bind(this),
    separated_tables: this.detectSeparatedTables.bind(this),
    header_only: this.detectHeaderOnly.bind(this),
    detail_only: this.detectDetailOnly.bind(this),
    pure_header: this.detectPureHeader.bind(this)
  };

  /**
   * 检测单据格式
   */
  detectFormat(data: DocumentData[], metadata?: any): DocumentFormat {
    const scores: Record<string, number> = {};
    
    // 计算各种格式的得分
    for (const [formatType, detector] of Object.entries(this.formatPatterns)) {
      scores[formatType] = detector(data);
    }
    
    // 找到得分最高的格式
    const bestFormat = Object.entries(scores).reduce((a, b) => 
      scores[a[0]] > scores[b[0]] ? a : b
    );
    
    return {
      type: bestFormat[0] as any,
      confidence: bestFormat[1],
      characteristics: this.getFormatCharacteristics(bestFormat[0])
    };
  }

  /**
   * 检测重复单据头格式
   */
  private detectRepeatedHeader(data: DocumentData[]): number {
    let score = 0;
    
    // 检查是否有单据头字段
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name'];
    const hasHeaderFields = headerFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (hasHeaderFields) score += 0.4;
    
    // 检查是否有明细字段
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity', '金额', 'amount'];
    const hasDetailFields = detailFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (hasDetailFields) score += 0.3;
    
    // 检查数据完整性
    const completeRows = data.filter(row => 
      headerFields.some(field => row[field] !== undefined && row[field] !== null && row[field] !== '') &&
      detailFields.some(field => row[field] !== undefined && row[field] !== null && row[field] !== '')
    ).length;
    
    if (completeRows / data.length > 0.8) score += 0.3;
    
    return Math.min(score, 1);
  }

  /**
   * 检测第一行单据头格式
   */
  private detectFirstRowHeader(data: DocumentData[]): number {
    let score = 0;
    
    if (data.length < 2) return 0;
    
    const firstRow = data[0];
    const otherRows = data.slice(1);
    
    // 检查第一行是否有单据头信息
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name'];
    const firstRowHasHeader = headerFields.some(field => 
      firstRow[field] !== undefined && firstRow[field] !== null && firstRow[field] !== ''
    );
    
    if (firstRowHasHeader) score += 0.4;
    
    // 检查其他行是否缺少单据头信息
    const otherRowsMissingHeader = otherRows.every(row => 
      headerFields.every(field => 
        row[field] === undefined || row[field] === null || row[field] === ''
      )
    );
    
    if (otherRowsMissingHeader) score += 0.4;
    
    // 检查其他行是否有明细信息
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity', '金额', 'amount'];
    const otherRowsHaveDetails = otherRows.some(row => 
      detailFields.some(field => 
        row[field] !== undefined && row[field] !== null && row[field] !== ''
      )
    );
    
    if (otherRowsHaveDetails) score += 0.2;
    
    return Math.min(score, 1);
  }

  /**
   * 检测分离表格式
   */
  private detectSeparatedTables(data: DocumentData[]): number {
    let score = 0;
    
    // 检查是否只有单据头字段
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name', '总金额', 'total_amount'];
    const hasOnlyHeaderFields = data.every(row => 
      Object.keys(row).every(key => headerFields.includes(key))
    );
    
    if (hasOnlyHeaderFields) score += 0.5;
    
    // 检查是否只有明细字段
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity', '金额', 'amount'];
    const hasOnlyDetailFields = data.every(row => 
      Object.keys(row).every(key => detailFields.includes(key))
    );
    
    if (hasOnlyDetailFields) score += 0.5;
    
    return Math.min(score, 1);
  }

  /**
   * 检测只有单据头格式
   */
  private detectHeaderOnly(data: DocumentData[]): number {
    let score = 0;
    
    // 检查是否有单据头字段
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name', '总金额', 'total_amount'];
    const headerFieldCount = headerFields.filter(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    ).length;
    
    if (headerFieldCount >= 3) score += 0.4;
    
    // 检查是否没有明细字段
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity'];
    const hasDetailFields = detailFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (!hasDetailFields) score += 0.3;
    
    // 检查行数是否较少
    if (data.length < 100) score += 0.3;
    
    return Math.min(score, 1);
  }

  /**
   * 检测只有明细格式
   */
  private detectDetailOnly(data: DocumentData[]): number {
    let score = 0;
    
    // 检查是否有明细字段
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity', '金额', 'amount'];
    const detailFieldCount = detailFields.filter(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    ).length;
    
    if (detailFieldCount >= 3) score += 0.5;
    
    // 检查是否没有单据头字段
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name'];
    const hasHeaderFields = headerFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (!hasHeaderFields) score += 0.3;
    
    // 检查是否有部门等分类字段
    const categoryFields = ['部门', 'department', '类别', 'category'];
    const hasCategoryFields = categoryFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (hasCategoryFields) score += 0.2;
    
    return Math.min(score, 1);
  }

  /**
   * 检测纯单据头格式
   */
  private detectPureHeader(data: DocumentData[]): number {
    let score = 0;
    
    // 检查是否有单据头字段
    const headerFields = ['单据号', 'document_id', '客户名称', 'customer_name', '总金额', 'total_amount'];
    const headerFieldCount = headerFields.filter(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    ).length;
    
    if (headerFieldCount >= 3) score += 0.4;
    
    // 检查是否有服务类型等纯头字段
    const serviceFields = ['单据类型', 'document_type', '服务类型', 'service_type'];
    const hasServiceFields = serviceFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (hasServiceFields) score += 0.3;
    
    // 检查是否没有明细字段
    const detailFields = ['产品名称', 'product_name', '数量', 'quantity'];
    const hasDetailFields = detailFields.some(field => 
      data.some(row => row[field] !== undefined && row[field] !== null && row[field] !== '')
    );
    
    if (!hasDetailFields) score += 0.3;
    
    // 检查行数是否较少
    if (data.length < 100) score += 0.2;
    
    return Math.min(score, 1);
  }

  /**
   * 获取格式特征
   */
  private getFormatCharacteristics(formatType: string): string[] {
    const characteristics: Record<string, string[]> = {
      repeated_header: ['每行都是完整记录', '包含单据头和明细信息', '数据完整度高'],
      first_row_header: ['第一行包含单据头', '后续行缺少单据头', '需要智能填充'],
      separated_tables: ['头表和明细表分离', '需要表关联处理', '数据结构清晰'],
      header_only: ['只有单据头信息', '需要创建虚拟明细', '汇总类数据'],
      detail_only: ['只有明细信息', '需要创建虚拟单据头', '明细类数据'],
      pure_header: ['纯单据头记录', '无明细数据', '服务类单据']
    };
    
    return characteristics[formatType] || [];
  }
}

/**
 * 智能单据处理器
 */
export class IntelligentDocumentProcessor {
  private formatDetector = new DocumentFormatDetector();
  private processors = {
    repeated_header: this.processRepeatedHeader.bind(this),
    first_row_header: this.processFirstRowHeader.bind(this),
    separated_tables: this.processSeparatedTables.bind(this),
    header_only: this.processHeaderOnly.bind(this),
    detail_only: this.processDetailOnly.bind(this),
    pure_header: this.processPureHeader.bind(this)
  };

  /**
   * 处理单据数据
   */
  async processDocument(data: DocumentData[], metadata?: any): Promise<ProcessResult> {
    try {
      // 1. 检测格式
      const format = this.formatDetector.detectFormat(data, metadata);
      
      // 2. 选择处理器
      const processor = this.processors[format.type];
      if (!processor) {
        throw new Error(`不支持的格式类型: ${format.type}`);
      }
      
      // 3. 处理数据
      const processedData = await processor(data);
      
      // 4. 计算质量分数
      const qualityScore = this.calculateQualityScore(processedData);
      
      return {
        success: true,
        processedData,
        formatType: format.type,
        recordsProcessed: processedData.length,
        qualityScore
      };
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 处理重复单据头格式
   */
  private async processRepeatedHeader(data: DocumentData[]): Promise<DocumentData[]> {
    // 重复单据头格式直接返回，无需特殊处理
    return data.map(row => ({
      ...row,
      record_type: 'complete',
      has_header: true,
      has_details: true
    }));
  }

  /**
   * 处理第一行单据头格式
   */
  private async processFirstRowHeader(data: DocumentData[]): Promise<DocumentData[]> {
    if (data.length === 0) return [];
    
    const firstRow = data[0];
    const otherRows = data.slice(1);
    
    // 识别单据头字段
    const headerFields = this.identifyHeaderFields(firstRow);
    
    // 为其他行填充单据头信息
    const processedRows = otherRows.map(row => {
      const processedRow = { ...row };
      
      // 填充单据头信息
      for (const field of headerFields) {
        if (firstRow[field] !== undefined && firstRow[field] !== null && firstRow[field] !== '') {
          processedRow[field] = firstRow[field];
        }
      }
      
      processedRow.record_type = 'detail_with_header';
      processedRow.has_header = true;
      processedRow.has_details = true;
      
      return processedRow;
    });
    
    // 处理第一行
    const processedFirstRow = {
      ...firstRow,
      record_type: 'complete',
      has_header: true,
      has_details: true
    };
    
    return [processedFirstRow, ...processedRows];
  }

  /**
   * 处理分离表格式
   */
  private async processSeparatedTables(data: DocumentData[]): Promise<DocumentData[]> {
    // 分离表格式需要外部提供头表数据
    // 这里返回原始数据，实际处理需要头表数据
    return data.map(row => ({
      ...row,
      record_type: 'separated',
      needs_header_table: true
    }));
  }

  /**
   * 处理只有单据头格式
   */
  private async processHeaderOnly(data: DocumentData[]): Promise<DocumentData[]> {
    // 为汇总数据创建虚拟明细记录
    const processedData: DocumentData[] = [];
    
    for (const row of data) {
      // 创建虚拟明细记录
      const virtualDetail = {
        ...row,
        record_type: 'header_with_virtual_detail',
        has_header: true,
        has_details: false,
        virtual_detail: {
          product_name: '汇总项目',
          quantity: 1,
          amount: row.total_amount || row.amount || 0
        }
      };
      
      processedData.push(virtualDetail);
    }
    
    return processedData;
  }

  /**
   * 处理只有明细格式
   */
  private async processDetailOnly(data: DocumentData[]): Promise<DocumentData[]> {
    // 为明细数据创建虚拟单据头
    const processedData: DocumentData[] = [];
    
    // 按部门或其他字段分组
    const groupedData = this.groupDataByCategory(data);
    
    for (const [category, groupData] of Object.entries(groupedData)) {
      // 计算汇总信息
      const totalAmount = groupData.reduce((sum, row) => sum + (row.amount || 0), 0);
      const totalQuantity = groupData.reduce((sum, row) => sum + (row.quantity || 0), 0);
      
      // 为每组创建虚拟单据头
      const virtualHeader = {
        document_id: `VIRTUAL_${category}_${Date.now()}`,
        document_date: new Date().toISOString().split('T')[0],
        customer_name: category,
        total_amount: totalAmount,
        total_quantity: totalQuantity,
        record_type: 'virtual_header',
        has_header: true,
        has_details: false
      };
      
      processedData.push(virtualHeader);
      
      // 添加明细记录
      for (const row of groupData) {
        processedData.push({
          ...row,
          document_id: virtualHeader.document_id,
          record_type: 'detail_with_virtual_header',
          has_header: false,
          has_details: true
        });
      }
    }
    
    return processedData;
  }

  /**
   * 处理纯单据头格式
   */
  private async processPureHeader(data: DocumentData[]): Promise<DocumentData[]> {
    // 纯单据头记录直接使用，不需要创建明细
    return data.map(row => ({
      ...row,
      record_type: 'header_only',
      has_details: false
    }));
  }

  /**
   * 识别单据头字段
   */
  private identifyHeaderFields(row: DocumentData): string[] {
    const headerPatterns = [
      '单据号', 'document_id', '单号',
      '单据日期', 'document_date', '日期',
      '客户名称', 'customer_name', '客户',
      '总金额', 'total_amount', '金额'
    ];
    
    return Object.keys(row).filter(key => 
      headerPatterns.some(pattern => key.includes(pattern))
    );
  }

  /**
   * 按类别分组数据
   */
  private groupDataByCategory(data: DocumentData[]): Record<string, DocumentData[]> {
    const groups: Record<string, DocumentData[]> = {};
    
    for (const row of data) {
      const category = row.部门 || row.department || row.类别 || row.category || '未分类';
      
      if (!groups[category]) {
        groups[category] = [];
      }
      
      groups[category].push(row);
    }
    
    return groups;
  }

  /**
   * 计算数据质量分数
   */
  private calculateQualityScore(data: DocumentData[]): number {
    if (data.length === 0) return 0;
    
    let totalScore = 0;
    
    for (const row of data) {
      let rowScore = 0;
      const fields = Object.keys(row);
      
      // 检查必填字段
      const requiredFields = ['document_id', 'amount'];
      const hasRequiredFields = requiredFields.every(field => 
        row[field] !== undefined && row[field] !== null && row[field] !== ''
      );
      
      if (hasRequiredFields) rowScore += 0.5;
      
      // 检查数据完整性
      const nonEmptyFields = fields.filter(field => 
        row[field] !== undefined && row[field] !== null && row[field] !== ''
      ).length;
      
      const completeness = nonEmptyFields / fields.length;
      rowScore += completeness * 0.5;
      
      totalScore += rowScore;
    }
    
    return totalScore / data.length;
  }
}

/**
 * 事后补充管理器
 */
export class DocumentSupplementManager {
  /**
   * 补充缺失的单据头
   */
  async supplementMissingHeader(
    detailData: DocumentData[],
    headerData?: DocumentData[],
    supplementRules?: Record<string, any>
  ): Promise<ProcessResult> {
    try {
      if (headerData) {
        // 使用提供的头表数据
        return await this.supplementWithProvidedHeader(detailData, headerData);
      } else if (supplementRules) {
        // 使用补充规则
        return await this.supplementWithRules(detailData, supplementRules);
      } else {
        throw new Error('需要提供头表数据或补充规则');
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '补充失败'
      };
    }
  }

  /**
   * 使用提供的头表数据补充
   */
  private async supplementWithProvidedHeader(
    detailData: DocumentData[],
    headerData: DocumentData[]
  ): Promise<ProcessResult> {
    // 找到关联字段
    const detailKey = this.findJoinKey(detailData);
    const headerKey = this.findJoinKey(headerData);
    
    if (!detailKey || !headerKey) {
      throw new Error('无法找到关联字段');
    }
    
    // 执行关联
    const supplementedData = detailData.map(detailRow => {
      const matchingHeader = headerData.find(headerRow => 
        headerRow[headerKey] === detailRow[detailKey]
      );
      
      if (matchingHeader) {
        return { ...detailRow, ...matchingHeader };
      }
      
      return detailRow;
    });
    
    return {
      success: true,
      processedData: supplementedData,
      recordsProcessed: supplementedData.length
    };
  }

  /**
   * 使用补充规则补充
   */
  private async supplementWithRules(
    data: DocumentData[],
    supplementRules: Record<string, any>
  ): Promise<ProcessResult> {
    const supplementedData = data.map(row => {
      const supplementedRow = { ...row };
      
      // 应用补充规则
      for (const [field, rule] of Object.entries(supplementRules)) {
        if (rule.type === 'default_value') {
          supplementedRow[field] = rule.value;
        } else if (rule.type === 'calculated') {
          supplementedRow[field] = this.calculateField(supplementedRow, rule.formula);
        } else if (rule.type === 'lookup') {
          supplementedRow[field] = this.lookupField(supplementedRow, rule.lookup_table, rule.lookup_field);
        }
      }
      
      return supplementedRow;
    });
    
    return {
      success: true,
      processedData: supplementedData,
      recordsProcessed: supplementedData.length
    };
  }

  /**
   * 查找关联字段
   */
  private findJoinKey(data: DocumentData[]): string | null {
    const keyPatterns = ['单据号', 'document_id', '单号', 'id'];
    
    for (const pattern of keyPatterns) {
      for (const row of data) {
        for (const key of Object.keys(row)) {
          if (key.toLowerCase().includes(pattern.toLowerCase())) {
            return key;
          }
        }
      }
    }
    
    return null;
  }

  /**
   * 计算字段值
   */
  private calculateField(data: DocumentData, formula: string): any {
    if (formula === 'sum_amount') {
      return data.amount || 0;
    } else if (formula === 'count_items') {
      return data.quantity || 1;
    } else {
      return 0;
    }
  }

  /**
   * 查找字段值
   */
  private lookupField(data: DocumentData, lookupTable: string, lookupField: string): any {
    // 这里简化处理，实际应该查询数据库
    return 'lookup_value';
  }
}
