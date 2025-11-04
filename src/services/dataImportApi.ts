/**
 * 数据导入API服务
 * 连接后端FastAPI数据导入端点
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  private async fetchWithAuth(url: string, options: RequestInit = {}) {
    // TODO: Add authentication token from Supabase
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * 上传文件
   */
  async uploadFile(file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/data-import/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Upload failed' }));
      throw new Error(error.message || 'Failed to upload file');
    }

    return response.json();
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
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${API_BASE_URL}/api/v1/data-import/upload-multiple`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload multiple files');
    }

    return response.json();
  }

  /**
   * 验证已上传的文件
   */
  async validateUploadedFile(fileName: string): Promise<QualityReport> {
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/validate/${fileName}`,
      { method: 'POST' }
    );
  }

  /**
   * 分析文件结构（文档格式识别）
   */
  async analyzeFile(file: File): Promise<DocumentFormatResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/data-import/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to analyze file');
    }

    return response.json();
  }

  /**
   * 获取导入历史
   */
  async getImportHistory(limit: number = 20): Promise<ImportHistoryItem[]> {
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/history?limit=${limit}`
    );
  }

  /**
   * 获取导入详情
   */
  async getImportDetails(importId: string): Promise<any> {
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/${importId}`
    );
  }

  /**
   * 清理旧文件
   */
  async cleanupOldFiles(days: number = 7): Promise<{
    deleted_files: number;
    freed_space: number;
  }> {
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/cleanup?days=${days}`,
      { method: 'DELETE' }
    );
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
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/supported-formats`
    );
  }

  /**
   * 创建演示数据
   */
  async createDemoData(rows: number = 100): Promise<UploadFileResponse> {
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/demo-data?rows=${rows}`,
      { method: 'POST' }
    );
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
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/stats`
    );
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
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/health`
    );
  }

  /**
   * 主数据匹配（模拟，实际需要后端实现）
   */
  async matchMasterData(data: {
    data_type: string;
    records: Array<{
      name: string;
      credit_code?: string;
      [key: string]: any;
    }>;
  }): Promise<MasterDataMatchResult[]> {
    // TODO: 实现主数据匹配API调用
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/match-master-data`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  /**
   * 单据头匹配（模拟，实际需要后端实现）
   */
  async matchDocumentHeaders(documentNumbers: string[]): Promise<Array<{
    document_number: string;
    header_id?: string;
    found: boolean;
    confidence: number;
    message: string;
  }>> {
    // TODO: 实现单据头匹配API调用
    return this.fetchWithAuth(
      `${API_BASE_URL}/api/v1/data-import/match-document-headers`,
      {
        method: 'POST',
        body: JSON.stringify({ document_numbers: documentNumbers }),
      }
    );
  }
}

export const dataImportApi = new DataImportApiService();
