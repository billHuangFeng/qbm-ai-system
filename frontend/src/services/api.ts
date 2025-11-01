/**
 * API服务层 - 统一管理所有API调用
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 通用API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
}

// 认证相关API
export const authAPI = {
  // 用户注册
  async register(userData: {
    username: string;
    email: string;
    password: string;
  }): Promise<ApiResponse<{ user_id: string }>> {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  // 用户登录
  async login(credentials: {
    username: string;
    password: string;
  }): Promise<ApiResponse<{ access_token: string; token_type: string }>> {
    const response = await apiClient.post('/auth/token', credentials);
    return response.data;
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<ApiResponse<{
    user_id: string;
    tenant_id: string;
    roles: string[];
  }>> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  // 刷新token
  async refreshToken(): Promise<ApiResponse<{ access_token: string }>> {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },
};

// 模型管理API
export const modelsAPI = {
  // 创建模型
  async createModel(modelData: {
    model_name: string;
    model_type: string;
    target_variable: string;
    features: string[];
    hyperparameters: Record<string, any>;
    training_data: Record<string, any>;
  }): Promise<ApiResponse<{
    id: string;
    model_name: string;
    model_type: string;
    accuracy_score: number;
  }>> {
    const response = await apiClient.post('/models/', modelData);
    return response.data;
  },

  // 获取模型列表
  async getModels(): Promise<ApiResponse<Array<{
    id: string;
    model_name: string;
    model_type: string;
    accuracy_score: number;
    created_at: string;
  }>>> {
    const response = await apiClient.get('/models/');
    return response.data;
  },

  // 获取单个模型
  async getModel(modelId: string): Promise<ApiResponse<{
    id: string;
    model_name: string;
    model_type: string;
    accuracy_score: number;
    features: string[];
    hyperparameters: Record<string, any>;
  }>> {
    const response = await apiClient.get(`/models/${modelId}`);
    return response.data;
  },

  // 训练模型
  async trainModel(trainingData: {
    model_type: string;
    target_variable: string;
    features: string[];
    hyperparameters: Record<string, any>;
    training_data: Record<string, any>;
  }): Promise<ApiResponse<{
    model_id: string;
    accuracy: number;
  }>> {
    const response = await apiClient.post('/models/train', trainingData);
    return response.data;
  },

  // 删除模型
  async deleteModel(modelId: string): Promise<ApiResponse> {
    const response = await apiClient.delete(`/models/${modelId}`);
    return response.data;
  },

  // 数据关系分析
  async analyzeDataRelationships(data: {
    features: Record<string, any>;
    target: any[];
  }, analysisTypes?: string[]): Promise<ApiResponse<{
    analysis_results: any;
    status: string;
  }>> {
    const response = await apiClient.post('/models/analyze', {
      data,
      analysis_types: analysisTypes,
    });
    return response.data;
  },

  // 权重优化
  async optimizeWeights(data: {
    features: Record<string, any>;
    target: any[];
  }, optimizationMethod = 'comprehensive'): Promise<ApiResponse<{
    optimization_results: any;
    status: string;
  }>> {
    const response = await apiClient.post('/models/optimize-weights', {
      data,
      optimization_method: optimizationMethod,
    });
    return response.data;
  },
};

// 预测服务API
export const predictionsAPI = {
  // 单个预测
  async makePrediction(predictionData: {
    model_id: string;
    input_data: Record<string, any>;
    prediction_type?: string;
    confidence_threshold?: number;
  }): Promise<ApiResponse<{
    prediction_id: string;
    prediction_value: number;
    confidence_score: number;
    prediction_details: Record<string, any>;
  }>> {
    const response = await apiClient.post('/predictions/predict', predictionData);
    return response.data;
  },

  // 批量预测
  async makeBatchPrediction(batchData: {
    model_id: string;
    input_data_list: Record<string, any>[];
    prediction_type?: string;
    confidence_threshold?: number;
  }): Promise<ApiResponse<{
    batch_id: string;
    predictions: Array<{
      prediction_id: string;
      prediction_value: number;
      confidence_score: number;
    }>;
    success_count: number;
    failed_count: number;
  }>> {
    const response = await apiClient.post('/predictions/predict/batch', batchData);
    return response.data;
  },

  // 带反馈的预测
  async makePredictionWithFeedback(predictionData: {
    model_id: string;
    input_data: Record<string, any>;
    feedback_data?: Record<string, any>;
  }): Promise<ApiResponse<{
    prediction_id: string;
    prediction_value: number;
    confidence_score: number;
  }>> {
    const response = await apiClient.post('/predictions/predict/with-feedback', predictionData);
    return response.data;
  },

  // 获取预测历史
  async getPredictionHistory(modelId?: string, limit = 100): Promise<ApiResponse<Array<{
    prediction_id: string;
    prediction_value: number;
    confidence_score: number;
    created_at: string;
  }>>> {
    const params = new URLSearchParams();
    if (modelId) params.append('model_id', modelId);
    params.append('limit', limit.toString());
    
    const response = await apiClient.get(`/predictions/history?${params}`);
    return response.data;
  },

  // 获取预测统计
  async getPredictionStats(modelId?: string): Promise<ApiResponse<{
    stats: Record<string, any>;
  }>> {
    const params = modelId ? `?model_id=${modelId}` : '';
    const response = await apiClient.get(`/predictions/stats${params}`);
    return response.data;
  },
};

// 企业记忆API
export const memoriesAPI = {
  // 提取企业记忆
  async extractMemories(evaluationData: {
    evaluation_data: Record<string, any>;
    tenant_id: string;
    extraction_type?: string;
  }): Promise<ApiResponse<{
    memory_id: string;
    extracted_memories: Array<{
      id: string;
      memory_type: string;
      content: string;
      confidence_score: number;
    }>;
  }>> {
    const response = await apiClient.post('/memories/extract', evaluationData);
    return response.data;
  },

  // 搜索企业记忆
  async searchMemories(searchData: {
    query: string;
    memory_type?: string;
    limit?: number;
  }): Promise<ApiResponse<Array<{
    id: string;
    memory_type: string;
    content: string;
    confidence_score: number;
    usage_count: number;
  }>>> {
    const response = await apiClient.post('/memories/search', searchData);
    return response.data;
  },

  // 获取企业记忆列表
  async getMemories(memoryType?: string, limit = 100): Promise<ApiResponse<Array<{
    id: string;
    memory_type: string;
    content: string;
    confidence_score: number;
    usage_count: number;
    created_at: string;
  }>>> {
    const params = new URLSearchParams();
    if (memoryType) params.append('memory_type', memoryType);
    params.append('limit', limit.toString());
    
    const response = await apiClient.get(`/memories/?${params}`);
    return response.data;
  },

  // 获取企业记忆统计
  async getMemoryStats(): Promise<ApiResponse<{
    stats: Record<string, any>;
  }>> {
    const response = await apiClient.get('/memories/stats');
    return response.data;
  },
};

// 数据导入API
export const dataImportAPI = {
  // 导入数据文件
  async importData(file: File, importConfig: {
    source_type: string;
    document_format: string;
    field_mappings: Array<{ source_field: string; target_field: string }>;
    target_table: string;
    import_config?: Record<string, any>;
  }): Promise<ApiResponse<{
    import_id: string;
    status: string;
    total_records: number;
    successful_records: number;
    failed_records: number;
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', importConfig.source_type);
    formData.append('document_format', importConfig.document_format);
    formData.append('field_mappings', JSON.stringify(importConfig.field_mappings));
    formData.append('target_table', importConfig.target_table);
    formData.append('import_config', JSON.stringify(importConfig.import_config || {}));

    const response = await apiClient.post('/data/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 预览数据文件
  async previewData(file: File, previewConfig: {
    source_type: string;
    document_format: string;
    preview_rows?: number;
  }): Promise<ApiResponse<{
    preview_data: any[];
    columns: string[];
    total_rows: number;
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', previewConfig.source_type);
    formData.append('document_format', previewConfig.document_format);
    formData.append('preview_rows', (previewConfig.preview_rows || 10).toString());

    const response = await apiClient.post('/data/preview', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 获取支持的文件格式
  async getSupportedFormats(): Promise<ApiResponse<{
    supported_formats: {
      document_formats: string[];
      source_types: string[];
      target_tables: string[];
    };
  }>> {
    const response = await apiClient.get('/data/formats');
    return response.data;
  },

  // 获取导入历史
  async getImportHistory(limit = 100): Promise<ApiResponse<Array<{
    import_id: string;
    status: string;
    total_records: number;
    successful_records: number;
    failed_records: number;
    created_at: string;
  }>>> {
    const response = await apiClient.get(`/data/import/history?limit=${limit}`);
    return response.data;
  },

  // 获取导入状态
  async getImportStatus(importId: string): Promise<ApiResponse<{
    import_id: string;
    status: string;
    total_records: number;
    successful_records: number;
    failed_records: number;
  }>> {
    const response = await apiClient.get(`/data/import/${importId}/status`);
    return response.data;
  },
};

// 监控API
export const monitoringAPI = {
  // 获取系统健康状态
  async getHealthStatus(): Promise<ApiResponse<{
    status: string;
    database: boolean;
    redis: boolean;
  }>> {
    const response = await apiClient.get('/monitoring/health');
    return response.data;
  },

  // 获取系统指标
  async getMetrics(): Promise<ApiResponse<{
    cpu_usage: number;
    memory_usage: number;
    api_latency_p95: number;
  }>> {
    const response = await apiClient.get('/monitoring/metrics');
    return response.data;
  },
};

// AI Copilot API
export const aiCopilotAPI = {
  // 聊天对话
  async chat(chatData: {
    user_message: string;
    conversation_history?: Array<{
      role: 'user' | 'assistant';
      content: string;
    }>;
    context?: Record<string, any>;
  }): Promise<ApiResponse<{
    response: string;
    tool_calls?: Array<{
      tool_name: string;
      parameters: Record<string, any>;
    }>;
  }>> {
    const response = await apiClient.post('/ai-copilot/chat', chatData);
    return response.data;
  },

  // 执行工具调用
  async executeTool(toolData: {
    tool_name: string;
    parameters: Record<string, any>;
  }): Promise<ApiResponse<{
    result: any;
    success: boolean;
  }>> {
    const response = await apiClient.post('/ai-copilot/execute-tool', toolData);
    return response.data;
  },
};

// 导出所有API
export default {
  auth: authAPI,
  models: modelsAPI,
  predictions: predictionsAPI,
  memories: memoriesAPI,
  dataImport: dataImportAPI,
  monitoring: monitoringAPI,
  aiCopilot: aiCopilotAPI,
};

