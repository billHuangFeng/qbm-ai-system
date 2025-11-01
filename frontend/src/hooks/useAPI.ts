/**
 * React Query hooks for API状态管理
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import api from './api';

// 通用错误处理
const handleError = (error: any, defaultMessage = '操作失败') => {
  const message = error.response?.data?.error?.message || error.message || defaultMessage;
  toast.error(message);
  console.error('API Error:', error);
};

// 认证相关hooks
export const useAuth = () => {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: api.auth.login,
    onSuccess: (data) => {
      if (data.success && data.data?.access_token) {
        localStorage.setItem('access_token', data.data.access_token);
        queryClient.invalidateQueries({ queryKey: ['user'] });
        toast.success('登录成功');
      }
    },
    onError: (error) => handleError(error, '登录失败'),
  });

  const registerMutation = useMutation({
    mutationFn: api.auth.register,
    onSuccess: () => {
      toast.success('注册成功，请登录');
    },
    onError: (error) => handleError(error, '注册失败'),
  });

  const logout = () => {
    localStorage.removeItem('access_token');
    queryClient.clear();
    toast.success('已退出登录');
  };

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
  };
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: api.auth.getCurrentUser,
    enabled: !!localStorage.getItem('access_token'),
    retry: false,
  });
};

// 模型管理hooks
export const useModels = () => {
  return useQuery({
    queryKey: ['models'],
    queryFn: api.models.getModels,
    select: (data) => data.data || [],
  });
};

export const useModel = (modelId: string) => {
  return useQuery({
    queryKey: ['models', modelId],
    queryFn: () => api.models.getModel(modelId),
    enabled: !!modelId,
    select: (data) => data.data,
  });
};

export const useCreateModel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.models.createModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
      toast.success('模型创建成功');
    },
    onError: (error) => handleError(error, '模型创建失败'),
  });
};

export const useTrainModel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.models.trainModel,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
      toast.success(`模型训练成功，准确率: ${(data.data?.accuracy * 100).toFixed(2)}%`);
    },
    onError: (error) => handleError(error, '模型训练失败'),
  });
};

export const useDeleteModel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.models.deleteModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
      toast.success('模型删除成功');
    },
    onError: (error) => handleError(error, '模型删除失败'),
  });
};

export const useAnalyzeDataRelationships = () => {
  return useMutation({
    mutationFn: ({ data, analysisTypes }: { data: any; analysisTypes?: string[] }) =>
      api.models.analyzeDataRelationships(data, analysisTypes),
    onError: (error) => handleError(error, '数据关系分析失败'),
  });
};

export const useOptimizeWeights = () => {
  return useMutation({
    mutationFn: ({ data, method }: { data: any; method?: string }) =>
      api.models.optimizeWeights(data, method),
    onError: (error) => handleError(error, '权重优化失败'),
  });
};

// 预测服务hooks
export const usePrediction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.predictions.makePrediction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
    onError: (error) => handleError(error, '预测失败'),
  });
};

export const useBatchPrediction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.predictions.makeBatchPrediction,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
      toast.success(`批量预测完成: ${data.data?.success_count}/${data.data?.predictions.length} 成功`);
    },
    onError: (error) => handleError(error, '批量预测失败'),
  });
};

export const usePredictionHistory = (modelId?: string) => {
  return useQuery({
    queryKey: ['predictions', 'history', modelId],
    queryFn: () => api.predictions.getPredictionHistory(modelId),
    select: (data) => data.data || [],
  });
};

export const usePredictionStats = (modelId?: string) => {
  return useQuery({
    queryKey: ['predictions', 'stats', modelId],
    queryFn: () => api.predictions.getPredictionStats(modelId),
    select: (data) => data.data?.stats,
  });
};

// 企业记忆hooks
export const useMemories = (memoryType?: string) => {
  return useQuery({
    queryKey: ['memories', memoryType],
    queryFn: () => api.memories.getMemories(memoryType),
    select: (data) => data.data || [],
  });
};

export const useSearchMemories = () => {
  return useMutation({
    mutationFn: api.memories.searchMemories,
    onError: (error) => handleError(error, '记忆搜索失败'),
  });
};

export const useExtractMemories = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.memories.extractMemories,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
      toast.success('企业记忆提取成功');
    },
    onError: (error) => handleError(error, '记忆提取失败'),
  });
};

export const useMemoryStats = () => {
  return useQuery({
    queryKey: ['memories', 'stats'],
    queryFn: api.memories.getMemoryStats,
    select: (data) => data.data?.stats,
  });
};

// 数据导入hooks
export const useImportData = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, config }: { file: File; config: any }) =>
      api.dataImport.importData(file, config),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['imports'] });
      toast.success(`数据导入完成: ${data.data?.successful_records}/${data.data?.total_records} 成功`);
    },
    onError: (error) => handleError(error, '数据导入失败'),
  });
};

export const usePreviewData = () => {
  return useMutation({
    mutationFn: ({ file, config }: { file: File; config: any }) =>
      api.dataImport.previewData(file, config),
    onError: (error) => handleError(error, '数据预览失败'),
  });
};

export const useImportHistory = () => {
  return useQuery({
    queryKey: ['imports'],
    queryFn: () => api.dataImport.getImportHistory(),
    select: (data) => data.data || [],
  });
};

export const useImportStatus = (importId: string) => {
  return useQuery({
    queryKey: ['imports', importId],
    queryFn: () => api.dataImport.getImportStatus(importId),
    enabled: !!importId,
    refetchInterval: 2000, // 每2秒刷新一次
    select: (data) => data.data,
  });
};

export const useSupportedFormats = () => {
  return useQuery({
    queryKey: ['formats'],
    queryFn: api.dataImport.getSupportedFormats,
    select: (data) => data.data?.supported_formats,
  });
};

// 监控hooks
export const useHealthStatus = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: api.monitoring.getHealthStatus,
    refetchInterval: 30000, // 每30秒刷新一次
    select: (data) => data.data,
  });
};

export const useMetrics = () => {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: api.monitoring.getMetrics,
    refetchInterval: 10000, // 每10秒刷新一次
    select: (data) => data.data,
  });
};

// AI Copilot hooks
export const useAIChat = () => {
  return useMutation({
    mutationFn: api.aiCopilot.chat,
    onError: (error) => handleError(error, 'AI对话失败'),
  });
};

export const useExecuteTool = () => {
  return useMutation({
    mutationFn: api.aiCopilot.executeTool,
    onError: (error) => handleError(error, '工具执行失败'),
  });
};

// 通用hooks
export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();

  return {
    invalidateModels: () => queryClient.invalidateQueries({ queryKey: ['models'] }),
    invalidatePredictions: () => queryClient.invalidateQueries({ queryKey: ['predictions'] }),
    invalidateMemories: () => queryClient.invalidateQueries({ queryKey: ['memories'] }),
    invalidateImports: () => queryClient.invalidateQueries({ queryKey: ['imports'] }),
    invalidateAll: () => queryClient.invalidateQueries(),
  };
};

