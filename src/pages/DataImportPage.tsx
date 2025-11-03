import { useState } from 'react';
import FileUploadZone from '@/components/DataImport/FileUploadZone';
import DataPreviewTable from '@/components/DataImport/DataPreviewTable';
import FieldMappingEditor from '@/components/DataImport/FieldMappingEditor';
import QualityReportCard from '@/components/DataImport/QualityReportCard';
import DataEnhancementPanel from '@/components/DataImport/DataEnhancementPanel';
import UnifiedProgressGuide from '@/components/DataImport/UnifiedProgressGuide';
import { ChevronRight } from 'lucide-react';

export type ImportStage = 
  | 'UPLOAD' 
  | 'MAPPING' 
  | 'ANALYZING' 
  | 'QUALITY_CHECK' 
  | 'READY' 
  | 'IMPORTING' 
  | 'ENHANCEMENT'
  | 'CONFIRMING'
  | 'COMPLETED';

const DataImportPage = () => {
  const [currentStage, setCurrentStage] = useState<ImportStage>('UPLOAD');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  return (
    <div className="min-h-screen bg-background">
      {/* Header with Breadcrumb */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <span className="hover:text-foreground cursor-pointer transition-colors">数据管理</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-foreground font-medium">智能数据导入</span>
          </div>
          <h1 className="text-3xl font-bold text-foreground">智能数据导入</h1>
          <p className="text-muted-foreground mt-1">AI 驱动的数据导入系统，自动识别格式、智能映射字段、深度质量检查</p>
        </div>
      </header>

      {/* Main Content: Two-Column Layout */}
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 xl:grid-cols-[60%_40%] gap-6 min-h-[calc(100vh-200px)]">
          
          {/* Left: Data Operations Area */}
          <div className="flex flex-col gap-6 overflow-y-auto pr-2 max-h-[calc(100vh-200px)]">
            
            {/* File Upload Zone */}
            <FileUploadZone 
              currentStage={currentStage}
              onStageChange={setCurrentStage}
              uploadedFile={uploadedFile}
              onFileUpload={setUploadedFile}
            />
            
            {/* Data Preview Table */}
            {uploadedFile && (
              <DataPreviewTable />
            )}
            
            {/* Field Mapping Editor */}
            {uploadedFile && (currentStage === 'MAPPING' || currentStage === 'ANALYZING' || currentStage === 'QUALITY_CHECK' || currentStage === 'READY') && (
              <FieldMappingEditor />
            )}
            
            {/* Quality Report Card */}
            {uploadedFile && (currentStage === 'QUALITY_CHECK' || currentStage === 'READY') && (
              <QualityReportCard />
            )}
            
            {/* Data Enhancement Panel */}
            {uploadedFile && (currentStage === 'ENHANCEMENT' || currentStage === 'CONFIRMING') && (
              <DataEnhancementPanel />
            )}
            
          </div>

          {/* Right: AI Smart Guide Area */}
          <div className="flex flex-col gap-4 bg-card border rounded-lg p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
            
            {/* Unified Progress Guide with integrated actions */}
            <UnifiedProgressGuide
                currentStage={currentStage}
                onStageChange={setCurrentStage}
              />
          </div>

        </div>
      </div>
    </div>
  );
};

export default DataImportPage;
