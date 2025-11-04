/**
 * 数据导入API服务
 * 使用 Supabase Edge Functions
 */

// 延迟导入 supabase client，避免环境变量未加载时初始化失败
const getSupabaseClient = () => {
  // 动态导入确保环境变量已加载
  const { supabase } = require("@/integrations/supabase/client");
  return supabase;
};

export interface UploadFileResponse {
  success: boolean;
  file_name: string;
  file_size: number;
  row_count: number;
  column_count: number;
  import_time: number;
  quality_score: number;
  warnings: string[];
  errors: string[];
  preview_data?: {
    headers: string[];
    rows: any[][];
  };
}

export interface FieldMapping {
  source_field: string;
  target_field: string;
  data_type: string;
  transformation_rule?: string;
  validation_rule?: string;
  is_required: boolean;
}

export interface QualityReport {
  total_rows: number;
  total_columns: number;
  missing_values: Record<string, number>;
  duplicate_rows: number;
  data_types: Record<string, string>;
  quality_score: number;
  quality_level: 'excellent' | 'good' | 'fair' | 'poor';
  recommendations: string[];
}

export interface ImportHistoryItem {
  id: string;
  file_name: string;
  file_size: number;
  row_count: number;
  quality_score: number;
  import_time: string;
  status: 'success' | 'failed' | 'partial';
}

export interface DocumentFormatResult {
  format_type: string;
  confidence: number;
  details: Record<string, any>;
}

export interface MasterDataMatchResult {
  field: string;
  original_value: string;
  matched_id?: string;
  matched_name?: string;
  confidence: number;
  match_type: string;
}

class DataImportApiService {
  /**
   * 上传文件到 Supabase Edge Function
   */
  async uploadFile(file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const supabase = getSupabaseClient();
    const { data, error } = await supabase.functions.invoke('data-import-upload', {
      body: formData
    });

    if (error) {
      throw new Error(error.message || 'Failed to upload file');
    }

    if (!data.success) {
      throw new Error(data.error?.message || 'Upload failed');
    }

    // 转换响应格式以匹配原有接口
    return {
      success: data.success,
      file_name: data.file_name,
      file_size: data.file_size,
      row_count: data.row_count,
      column_count: data.column_count,
      import_time: 0, // Edge Function 不返回这个字段
      quality_score: data.format_detection.confidence * 100,
      warnings: [],
      errors: [],
      preview_data: {
        headers: [],
        rows: []
      }
    };
  }

  /**
   * 批量上传文件
   */
  async uploadMultipleFiles(files: File[]): Promise<{
    total_files: number;
    successful_files: number;
    failed_files: number;
    results: UploadFileResponse[];
  }> {
    // 并行上传所有文件
    const uploadPromises = files.map(file => 
      this.uploadFile(file).catch(error => ({
        success: false,
        file_name: file.name,
        error: error.message
      }))
    );

    const results = await Promise.all(uploadPromises);
    const successful = results.filter(r => r.success);

    return {
      total_files: files.length,
      successful_files: successful.length,
      failed_files: files.length - successful.length,
      results: results as UploadFileResponse[]
    };
  }

  /**
   * 验证已上传的文件
   * TODO: 实现 data-import-validate Edge Function
   */
  async validateUploadedFile(fileName: string): Promise<QualityReport> {
    // 临时实现 - 返回模拟数据
    console.warn('validateUploadedFile: Edge Function 未实现');
    return {
      total_rows: 0,
      total_columns: 0,
      missing_values: {},
      duplicate_rows: 0,
      data_types: {},
      quality_score: 0,
      quality_level: 'fair',
      recommendations: ['Edge Function 正在开发中']
    };
  }

  /**
   * 分析文件结构（文档格式识别）
   * TODO: 实现 data-import-analyze Edge Function
   */
  async analyzeFile(file: File): Promise<DocumentFormatResult> {
    // 临时实现 - 先上传文件，格式识别已经在 upload 中完成
    const uploadResult = await this.uploadFile(file);
    
    return {
      format_type: 'unknown',
      confidence: uploadResult.quality_score / 100,
      details: {}
    };
  }

  /**
   * 获取导入历史
   */
  async getImportHistory(limit: number = 20): Promise<ImportHistoryItem[]> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from('data_import_uploads')
      .select('*')
      .order('uploaded_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching import history:', error);
      return [];
    }

    return data.map((item: any) => ({
      id: item.id,
      file_name: item.file_name,
      file_size: item.file_size,
      row_count: item.row_count || 0,
      quality_score: (item.format_confidence || 0) * 100,
      import_time: item.uploaded_at,
      status: item.status === 'uploaded' ? 'success' as const : 'failed' as const
    }));
  }

  /**
   * 获取导入详情
   */
  async getImportDetails(importId: string): Promise<any> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from('data_import_uploads')
      .select('*')
      .eq('id', importId)
      .single();

    if (error) {
      throw new Error(error.message);
    }

    return data;
  }

  /**
   * 清理旧文件
   * TODO: 实现 data-import-cleanup Edge Function
   */
  async cleanupOldFiles(days: number = 7): Promise<{
    deleted_files: number;
    freed_space: number;
  }> {
    console.warn('cleanupOldFiles: Edge Function 未实现');
    return {
      deleted_files: 0,
      freed_space: 0
    };
  }

  /**
   * 获取支持的文件格式
   */
  async getSupportedFormats(): Promise<{
    formats: Array<{
      extension: string;
      mime_type: string;
      description: string;
    }>;
  }> {
    return {
      formats: [
        { extension: '.csv', mime_type: 'text/csv', description: 'CSV 文件' },
        { extension: '.xlsx', mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', description: 'Excel 文件 (xlsx)' },
        { extension: '.xls', mime_type: 'application/vnd.ms-excel', description: 'Excel 文件 (xls)' },
        { extension: '.json', mime_type: 'application/json', description: 'JSON 文件' }
      ]
    };
  }

  /**
   * 创建演示数据
   * TODO: 实现演示数据创建
   */
  async createDemoData(rows: number = 100): Promise<UploadFileResponse> {
    console.warn('createDemoData: 功能未实现');
    throw new Error('Demo data creation not implemented yet');
  }

  /**
   * 获取导入统计
   */
  async getImportStats(): Promise<{
    total_imports: number;
    total_rows: number;
    average_quality_score: number;
    recent_imports: ImportHistoryItem[];
  }> {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from('data_import_uploads')
      .select('*')
      .order('uploaded_at', { ascending: false })
      .limit(5);

    if (error) {
      console.error('Error fetching import stats:', error);
      return {
        total_imports: 0,
        total_rows: 0,
        average_quality_score: 0,
        recent_imports: []
      };
    }

    const totalRows = data.reduce((sum: number, item: any) => sum + (item.row_count || 0), 0);
    const avgQuality = data.length > 0
      ? data.reduce((sum: number, item: any) => sum + (item.format_confidence || 0), 0) / data.length * 100
      : 0;

    return {
      total_imports: data.length,
      total_rows: totalRows,
      average_quality_score: avgQuality,
      recent_imports: data.map((item: any) => ({
        id: item.id,
        file_name: item.file_name,
        file_size: item.file_size,
        row_count: item.row_count || 0,
        quality_score: (item.format_confidence || 0) * 100,
        import_time: item.uploaded_at,
        status: item.status === 'uploaded' ? 'success' as const : 'failed' as const
      }))
    };
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{
    status: string;
    version: string;
    upload_dir_exists: boolean;
    upload_dir_writable: boolean;
  }> {
    // 简单的健康检查 - 测试 Supabase 连接
    try {
      const supabase = getSupabaseClient();
      const { error } = await supabase.from('data_import_uploads').select('id').limit(1);
      return {
        status: error ? 'unhealthy' : 'healthy',
        version: '2.0.0-edge-functions',
        upload_dir_exists: true,
        upload_dir_writable: true
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        version: '2.0.0-edge-functions',
        upload_dir_exists: false,
        upload_dir_writable: false
      };
    }
  }

  /**
   * 主数据匹配
   * TODO: 实现 data-import-match-master Edge Function
   */
  async matchMasterData(data: {
    data_type: string;
    records: Array<{
      name: string;
      credit_code?: string;
      [key: string]: any;
    }>;
  }): Promise<MasterDataMatchResult[]> {
    console.warn('matchMasterData: Edge Function 未实现');
    return [];
  }

  /**
   * 单据头匹配
   * TODO: 实现 data-import-match-headers Edge Function
   */
  async matchDocumentHeaders(documentNumbers: string[]): Promise<Array<{
    document_number: string;
    header_id?: string;
    found: boolean;
    confidence: number;
    message: string;
  }>> {
    console.warn('matchDocumentHeaders: Edge Function 未实现');
    return documentNumbers.map(num => ({
      document_number: num,
      found: false,
      confidence: 0,
      message: 'Edge Function 未实现'
    }));
  }
}

export const dataImportApi = new DataImportApiService();
