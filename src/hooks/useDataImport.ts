/**
 * 数据导入自定义 Hook
 * 提供数据导入相关的状态管理和API调用
 */

import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { dataImportApi, type UploadFileResponse, type QualityReport } from '@/services/dataImportApi';
import { useToast } from '@/hooks/use-toast';

export interface ImportState {
  uploadedFile: File | null;
  uploadResult: UploadFileResponse | null;
  qualityReport: QualityReport | null;
  isUploading: boolean;
  isAnalyzing: boolean;
  isValidating: boolean;
  error: string | null;
  previewData: {
    headers: string[];
    rows: any[][];
  } | null;
  formatDetection: {
    format_type: string;
    confidence: number;
    details: Record<string, any>;
  } | null;
}

export const useDataImport = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [state, setState] = useState<ImportState>({
    uploadedFile: null,
    uploadResult: null,
    qualityReport: null,
    isUploading: false,
    isAnalyzing: false,
    isValidating: false,
    error: null,
    previewData: null,
    formatDetection: null,
  });

  // 文件上传
  const uploadMutation = useMutation({
    mutationFn: (file: File) => dataImportApi.uploadFile(file),
    onMutate: () => {
      setState(prev => ({ ...prev, isUploading: true, error: null }));
    },
    onSuccess: (data) => {
      setState(prev => ({
        ...prev,
        uploadResult: data,
        previewData: data.preview_data || null,
        isUploading: false,
      }));
      
      toast({
        title: "文件上传成功",
        description: `已上传 ${data.file_name}，共 ${data.row_count} 行 ${data.column_count} 列`,
      });

      // 自动触发格式分析
      if (state.uploadedFile) {
        analyzeFileMutation.mutate(state.uploadedFile);
      }
    },
    onError: (error: Error) => {
      setState(prev => ({ ...prev, isUploading: false, error: error.message }));
      toast({
        variant: "destructive",
        title: "上传失败",
        description: error.message,
      });
    },
  });

  // 文件格式分析
  const analyzeFileMutation = useMutation({
    mutationFn: (file: File) => dataImportApi.analyzeFile(file),
    onMutate: () => {
      setState(prev => ({ ...prev, isAnalyzing: true }));
    },
    onSuccess: (data) => {
      setState(prev => ({
        ...prev,
        formatDetection: data,
        isAnalyzing: false,
      }));
      
      toast({
        title: "格式识别完成",
        description: `检测到格式类型: ${data.format_type} (置信度: ${(data.confidence * 100).toFixed(1)}%)`,
      });
    },
    onError: (error: Error) => {
      setState(prev => ({ ...prev, isAnalyzing: false }));
      toast({
        variant: "destructive",
        title: "格式分析失败",
        description: error.message,
      });
    },
  });

  // 数据验证
  const validateMutation = useMutation({
    mutationFn: (fileName: string) => dataImportApi.validateUploadedFile(fileName),
    onMutate: () => {
      setState(prev => ({ ...prev, isValidating: true }));
    },
    onSuccess: (data) => {
      setState(prev => ({
        ...prev,
        qualityReport: data,
        isValidating: false,
      }));
      
      const qualityText = 
        data.quality_level === 'excellent' ? '优秀' :
        data.quality_level === 'good' ? '良好' :
        data.quality_level === 'fair' ? '一般' : '较差';
      
      toast({
        title: "数据验证完成",
        description: `质量评分: ${(data.quality_score * 100).toFixed(1)}% (${qualityText})`,
      });
    },
    onError: (error: Error) => {
      setState(prev => ({ ...prev, isValidating: false }));
      toast({
        variant: "destructive",
        title: "验证失败",
        description: error.message,
      });
    },
  });

  // 获取导入历史
  const { data: importHistory, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['import-history'],
    queryFn: () => dataImportApi.getImportHistory(20),
  });

  // 获取支持的格式
  const { data: supportedFormats } = useQuery({
    queryKey: ['supported-formats'],
    queryFn: () => dataImportApi.getSupportedFormats(),
  });

  // 获取导入统计
  const { data: importStats } = useQuery({
    queryKey: ['import-stats'],
    queryFn: () => dataImportApi.getImportStats(),
  });

  // 上传文件
  const handleUpload = useCallback((file: File) => {
    setState(prev => ({ ...prev, uploadedFile: file }));
    uploadMutation.mutate(file);
  }, [uploadMutation]);

  // 验证数据
  const handleValidate = useCallback((fileName: string) => {
    validateMutation.mutate(fileName);
  }, [validateMutation]);

  // 重置状态
  const resetImport = useCallback(() => {
    setState({
      uploadedFile: null,
      uploadResult: null,
      qualityReport: null,
      isUploading: false,
      isAnalyzing: false,
      isValidating: false,
      error: null,
      previewData: null,
      formatDetection: null,
    });
  }, []);

  // 创建演示数据
  const createDemoMutation = useMutation({
    mutationFn: (rows: number) => dataImportApi.createDemoData(rows),
    onSuccess: (data) => {
      toast({
        title: "演示数据创建成功",
        description: `已创建 ${data.row_count} 行演示数据`,
      });
      queryClient.invalidateQueries({ queryKey: ['import-history'] });
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "创建演示数据失败",
        description: error.message,
      });
    },
  });

  return {
    // 状态
    ...state,
    importHistory,
    isLoadingHistory,
    supportedFormats,
    importStats,
    
    // 操作
    handleUpload,
    handleValidate,
    resetImport,
    createDemoData: createDemoMutation.mutate,
    
    // 加载状态
    isLoading: state.isUploading || state.isAnalyzing || state.isValidating,
  };
};
