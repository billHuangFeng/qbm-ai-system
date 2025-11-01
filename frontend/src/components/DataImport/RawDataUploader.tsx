/**
 * 数据导入组件 - 使用真实API
 */

import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useImportData, usePreviewData, useSupportedFormats, useImportHistory } from '@/hooks/useAPI';
import { toast } from 'react-hot-toast';

interface FieldMapping {
  source_field: string;
  target_field: string;
}

interface ImportConfig {
  source_type: string;
  document_format: string;
  field_mappings: FieldMapping[];
  target_table: string;
  import_config: Record<string, any>;
}

const DataImportUploader: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importConfig, setImportConfig] = useState<ImportConfig>({
    source_type: 'file_upload',
    document_format: 'excel',
    field_mappings: [],
    target_table: 'fact_order',
    import_config: {},
  });
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [previewColumns, setPreviewColumns] = useState<string[]>([]);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const { data: supportedFormats } = useSupportedFormats();
  const { data: importHistory } = useImportHistory();
  const importDataMutation = useImportData();
  const previewDataMutation = usePreviewData();

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setPreviewData([]);
    setPreviewColumns([]);
    
    // 自动检测文件格式
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (extension === 'xlsx' || extension === 'xls') {
      setImportConfig(prev => ({ ...prev, document_format: 'excel' }));
    } else if (extension === 'csv') {
      setImportConfig(prev => ({ ...prev, document_format: 'csv' }));
    } else if (extension === 'json') {
      setImportConfig(prev => ({ ...prev, document_format: 'json' }));
    }
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, [handleFileSelect]);

  const handlePreview = async () => {
    if (!selectedFile) {
      toast.error('请先选择文件');
      return;
    }

    setIsPreviewing(true);
    try {
      const result = await previewDataMutation.mutateAsync({
        file: selectedFile,
        config: {
          source_type: importConfig.source_type,
          document_format: importConfig.document_format,
          preview_rows: 10,
        },
      });

      if (result.success) {
        setPreviewData(result.data.preview_data);
        setPreviewColumns(result.data.columns);
        toast.success('数据预览成功');
      }
    } catch (error) {
      console.error('数据预览失败:', error);
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      toast.error('请先选择文件');
      return;
    }

    if (importConfig.field_mappings.length === 0) {
      toast.error('请配置字段映射');
      return;
    }

    try {
      const result = await importDataMutation.mutateAsync({
        file: selectedFile,
        config: importConfig,
      });

      if (result.success) {
        toast.success(`数据导入完成: ${result.data.successful_records}/${result.data.total_records} 成功`);
        // 重置表单
        setSelectedFile(null);
        setPreviewData([]);
        setPreviewColumns([]);
        setImportConfig({
          source_type: 'file_upload',
          document_format: 'excel',
          field_mappings: [],
          target_table: 'fact_order',
          import_config: {},
        });
      }
    } catch (error) {
      console.error('数据导入失败:', error);
    }
  };

  const addFieldMapping = () => {
    setImportConfig(prev => ({
      ...prev,
      field_mappings: [...prev.field_mappings, { source_field: '', target_field: '' }],
    }));
  };

  const updateFieldMapping = (index: number, field: keyof FieldMapping, value: string) => {
    setImportConfig(prev => ({
      ...prev,
      field_mappings: prev.field_mappings.map((mapping, i) =>
        i === index ? { ...mapping, [field]: value } : mapping
      ),
    }));
  };

  const removeFieldMapping = (index: number) => {
    setImportConfig(prev => ({
      ...prev,
      field_mappings: prev.field_mappings.filter((_, i) => i !== index),
    }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'processing':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">数据导入</h1>
        <p className="text-gray-600">上传数据文件并配置导入参数</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 文件上传区域 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              文件上传
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 拖拽上传区域 */}
            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {selectedFile ? (
                <div className="space-y-2">
                  <FileText className="h-8 w-8 text-blue-600 mx-auto" />
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-600">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedFile(null)}
                  >
                    重新选择
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="h-8 w-8 text-gray-400 mx-auto" />
                  <p className="text-gray-600">拖拽文件到此处或点击选择</p>
                  <Input
                    type="file"
                    accept=".xlsx,.xls,.csv,.json"
                    onChange={(e) => {
                      if (e.target.files?.[0]) {
                        handleFileSelect(e.target.files[0]);
                      }
                    }}
                    className="hidden"
                    id="file-upload"
                  />
                  <Label htmlFor="file-upload" className="cursor-pointer">
                    <Button variant="outline" asChild>
                      <span>选择文件</span>
                    </Button>
                  </Label>
                </div>
              )}
            </div>

            {/* 文件格式选择 */}
            <div className="space-y-2">
              <Label>文档格式</Label>
              <Select
                value={importConfig.document_format}
                onValueChange={(value) =>
                  setImportConfig(prev => ({ ...prev, document_format: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {supportedFormats?.document_formats.map((format) => (
                    <SelectItem key={format} value={format}>
                      {format.toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 目标表选择 */}
            <div className="space-y-2">
              <Label>目标表</Label>
              <Select
                value={importConfig.target_table}
                onValueChange={(value) =>
                  setImportConfig(prev => ({ ...prev, target_table: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {supportedFormats?.target_tables.map((table) => (
                    <SelectItem key={table} value={table}>
                      {table}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 预览按钮 */}
            <Button
              onClick={handlePreview}
              disabled={!selectedFile || isPreviewing}
              className="w-full"
            >
              {isPreviewing ? '预览中...' : '预览数据'}
            </Button>
          </CardContent>
        </Card>

        {/* 配置区域 */}
        <Card>
          <CardHeader>
            <CardTitle>导入配置</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 字段映射 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>字段映射</Label>
                <Button size="sm" onClick={addFieldMapping}>
                  添加映射
                </Button>
              </div>
              <div className="space-y-2">
                {importConfig.field_mappings.map((mapping, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <Input
                      placeholder="源字段"
                      value={mapping.source_field}
                      onChange={(e) =>
                        updateFieldMapping(index, 'source_field', e.target.value)
                      }
                    />
                    <span className="text-gray-500">→</span>
                    <Input
                      placeholder="目标字段"
                      value={mapping.target_field}
                      onChange={(e) =>
                        updateFieldMapping(index, 'target_field', e.target.value)
                      }
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeFieldMapping(index)}
                    >
                      删除
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* 导入配置 */}
            <div className="space-y-2">
              <Label>导入配置 (JSON)</Label>
              <Textarea
                placeholder='{"skip_rows": 1, "delimiter": ","}'
                value={JSON.stringify(importConfig.import_config, null, 2)}
                onChange={(e) => {
                  try {
                    const config = JSON.parse(e.target.value);
                    setImportConfig(prev => ({ ...prev, import_config: config }));
                  } catch (error) {
                    // 忽略JSON解析错误，让用户继续输入
                  }
                }}
                rows={3}
              />
            </div>

            {/* 导入按钮 */}
            <Button
              onClick={handleImport}
              disabled={!selectedFile || importDataMutation.isPending}
              className="w-full"
            >
              {importDataMutation.isPending ? '导入中...' : '开始导入'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* 数据预览 */}
      {previewData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>数据预览</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {previewColumns.map((column) => (
                      <th
                        key={column}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {previewData.map((row, index) => (
                    <tr key={index}>
                      {previewColumns.map((column) => (
                        <td
                          key={column}
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                        >
                          {row[column]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 导入历史 */}
      {importHistory && importHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>导入历史</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {importHistory.slice(0, 5).map((record) => (
                <div
                  key={record.import_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(record.status)}
                    <div>
                      <p className="font-medium text-sm">
                        {record.import_id.substring(0, 8)}...
                      </p>
                      <p className="text-xs text-gray-600">
                        {record.successful_records}/{record.total_records} 成功
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        record.status === 'completed'
                          ? 'default'
                          : record.status === 'failed'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {record.status}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {new Date(record.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DataImportUploader;


