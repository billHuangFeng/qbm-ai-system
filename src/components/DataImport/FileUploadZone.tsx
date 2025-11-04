import { useState, useCallback, useRef } from 'react';
import { Upload, File, CheckCircle2, RefreshCw, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { ImportStage } from '@/pages/DataImportPage';

interface FileUploadZoneProps {
  currentStage: ImportStage;
  onStageChange: (stage: ImportStage) => void;
  uploadedFile: File | null;
  onFileUpload: (file: File | null) => void;
  onUpload?: (file: File) => void;
  isUploading?: boolean;
}

const FileUploadZone = ({ 
  currentStage, 
  onStageChange, 
  uploadedFile, 
  onFileUpload,
  onUpload,
  isUploading = false 
}: FileUploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileUpload = (file: File) => {
    onFileUpload(file);
    if (onUpload) {
      onUpload(file);
    } else {
      onStageChange('MAPPING');
    }
  };

  const handleReupload = () => {
    fileInputRef.current?.click();
  };

  if (currentStage !== 'UPLOAD' && uploadedFile) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <File className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-foreground">{uploadedFile.name}</h3>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-sm text-muted-foreground">
                {(uploadedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReupload}
              disabled={isUploading}
              className="flex items-center gap-2"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  上传中...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  重新上传
                </>
              )}
            </Button>
          </div>
          
          {/* 隐藏的文件输入 */}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".xlsx,.xls,.csv,.json,.xml"
            onChange={handleFileSelect}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-8">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer
            ${isDragging 
              ? 'border-primary bg-primary/5 scale-105' 
              : 'border-border hover:border-primary/50 hover:bg-accent/50'
            }
          `}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".xlsx,.xls,.csv,.json,.xml"
            onChange={handleFileSelect}
          />
          
          <label htmlFor="file-upload" className={isUploading ? 'pointer-events-none' : 'cursor-pointer'}>
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 rounded-full bg-primary/10">
                {isUploading ? (
                  <Loader2 className="w-8 h-8 text-primary animate-spin" />
                ) : (
                  <Upload className="w-8 h-8 text-primary" />
                )}
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {isUploading ? '正在上传...' : '拖拽文件到这里或点击上传'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  支持 Excel (.xlsx, .xls)、CSV、JSON、XML 格式
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  最大支持 20MB
                </p>
              </div>
            </div>
          </label>
        </div>
      </CardContent>
    </Card>
  );
};

export default FileUploadZone;
