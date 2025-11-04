# BMOS数据导入前端集成指南

**创建日期**: 2025-11-04  
**版本**: 1.0

---

## 📋 概述

本文档描述BMOS数据导入功能的前端实现，包括组件架构、API集成和使用说明。

---

## 🏗️ 架构设计

### 技术栈

- **前端框架**: React 19 + TypeScript
- **UI库**: shadcn/ui + Tailwind CSS
- **状态管理**: React Hooks + TanStack Query
- **路由**: React Router v7
- **HTTP客户端**: Fetch API

### 项目结构

```
src/
├── pages/
│   └── DataImportPage.tsx          # 数据导入主页面
├── components/
│   └── DataImport/
│       ├── FileUploadZone.tsx      # 文件上传区
│       ├── DataPreviewTable.tsx    # 数据预览表格
│       ├── FieldMappingEditor.tsx  # 字段映射编辑器
│       ├── QualityReportCard.tsx   # 质量报告卡片
│       ├── DataEnhancementPanel.tsx # 数据完善面板
│       └── UnifiedProgressGuide.tsx # 统一进度引导
├── services/
│   └── dataImportApi.ts            # 数据导入API服务
├── hooks/
│   └── useDataImport.ts            # 数据导入自定义Hook
└── types/
    └── dataImport.ts               # 类型定义
```

---

## 🔌 API集成

### API服务 (`dataImportApi.ts`)

提供完整的数据导入API封装：

```typescript
import { dataImportApi } from '@/services/dataImportApi';

// 上传文件
const result = await dataImportApi.uploadFile(file);

// 分析文件格式
const format = await dataImportApi.analyzeFile(file);

// 验证数据质量
const quality = await dataImportApi.validateUploadedFile(fileName);

// 获取导入历史
const history = await dataImportApi.getImportHistory(20);
```

### 自定义Hook (`useDataImport.ts`)

提供统一的数据导入状态管理：

```typescript
import { useDataImport } from '@/hooks/useDataImport';

function MyComponent() {
  const {
    // 状态
    uploadedFile,
    uploadResult,
    qualityReport,
    isUploading,
    isAnalyzing,
    previewData,
    formatDetection,
    
    // 操作
    handleUpload,
    handleValidate,
    resetImport,
    
    // 历史数据
    importHistory,
    importStats,
  } = useDataImport();
  
  // 使用状态和操作
  return <div>...</div>;
}
```

---

## 🎨 核心组件

### 1. DataImportPage (主页面)

**路径**: `src/pages/DataImportPage.tsx`

主要的数据导入页面，协调所有子组件。

**功能**:
- 管理导入流程状态
- 协调文件上传、预览、映射、验证等步骤
- 左右布局：左侧操作区，右侧进度引导

**使用示例**:
```tsx
import DataImportPage from '@/pages/DataImportPage';

// 在路由中使用
<Route path="/data-import" element={<DataImportPage />} />
```

---

### 2. FileUploadZone (文件上传区)

**路径**: `src/components/DataImport/FileUploadZone.tsx`

支持拖拽和点击上传的文件上传组件。

**Props**:
```typescript
interface FileUploadZoneProps {
  currentStage: ImportStage;
  onStageChange: (stage: ImportStage) => void;
  uploadedFile: File | null;
  onFileUpload: (file: File | null) => void;
  onUpload?: (file: File) => void;
  isUploading?: boolean;
}
```

**功能**:
- 拖拽上传
- 点击上传
- 文件格式验证
- 上传进度提示
- 重新上传功能

**支持格式**:
- Excel: `.xlsx`, `.xls`
- CSV: `.csv`
- JSON: `.json`
- XML: `.xml`

---

### 3. DataPreviewTable (数据预览)

**路径**: `src/components/DataImport/DataPreviewTable.tsx`

显示上传文件的数据预览（前10行）。

**Props**:
```typescript
interface DataPreviewTableProps {
  previewData: {
    headers: string[];
    rows: any[][];
  };
}
```

**功能**:
- 显示表头
- 显示前10行数据
- 响应式表格
- 横向滚动

---

### 4. FieldMappingEditor (字段映射编辑器)

**路径**: `src/components/DataImport/FieldMappingEditor.tsx`

智能字段映射配置界面。

**Props**:
```typescript
interface FieldMappingEditorProps {
  previewData: {
    headers: string[];
    rows: any[][];
  };
  formatDetection?: {
    format_type: string;
    confidence: number;
    details: Record<string, any>;
  } | null;
}
```

**功能**:
- AI智能推荐字段映射
- 显示映射置信度
- 源字段→目标字段可视化
- 格式类型显示

---

### 5. QualityReportCard (质量报告)

**路径**: `src/components/DataImport/QualityReportCard.tsx`

显示数据质量分析报告。

**Props**:
```typescript
interface QualityReportCardProps {
  qualityReport: QualityReport;
  uploadResult: UploadFileResponse | null;
}
```

**功能**:
- 质量评分（0-100）
- 质量等级（优秀/良好/一般/较差）
- 问题列表（阻塞性/可修复）
- 改进建议
- 统计信息

---

### 6. DataEnhancementPanel (数据完善面板)

**路径**: `src/components/DataImport/DataEnhancementPanel.tsx`

第二阶段数据完善处理界面。

**功能**:
- 主数据ID匹配
- 计算字段冲突检测
- 一键修复功能
- 完善进度跟踪

---

### 7. UnifiedProgressGuide (统一进度引导)

**路径**: `src/components/DataImport/UnifiedProgressGuide.tsx`

AI驱动的进度引导和任务追踪。

**Props**:
```typescript
interface UnifiedProgressGuideProps {
  currentStage: ImportStage;
  onStageChange?: (stage: ImportStage) => void;
  onFileUpload?: (file: File | null) => void;
  uploadResult?: any;
  qualityReport?: any;
  isLoading?: boolean;
  formatDetection?: any;
}
```

**功能**:
- 步骤进度显示
- 当前阶段高亮
- 智能任务消息
- 快捷操作按钮
- 实时状态更新

---

## 🔄 导入流程

### 完整流程图

```
1. UPLOAD (上传文件)
   ↓
   [用户上传文件] → 触发API调用
   ↓
2. MAPPING (字段映射)
   ↓
   [AI智能推荐映射] → 用户确认
   ↓
3. ANALYZING (格式识别)
   ↓
   [DocumentFormatDetector识别格式] → 返回格式类型和置信度
   ↓
4. QUALITY_CHECK (质量检查)
   ↓
   [7维度质量分析] → 生成质量报告
   ↓
5. READY (准备导入)
   ↓
   [用户确认] → 开始导入
   ↓
6. IMPORTING (导入中)
   ↓
   [批量写入数据库]
   ↓
7. ENHANCEMENT (数据完善)
   ↓
   [主数据匹配、计算验证]
   ↓
8. CONFIRMING (确认入库)
   ↓
   [最终确认]
   ↓
9. COMPLETED (完成)
```

### 阶段类型定义

```typescript
export type ImportStage = 
  | 'UPLOAD'          // 上传文件
  | 'MAPPING'         // 字段映射
  | 'ANALYZING'       // 格式识别
  | 'QUALITY_CHECK'   // 质量检查
  | 'READY'           // 准备导入
  | 'IMPORTING'       // 导入中
  | 'ENHANCEMENT'     // 数据完善
  | 'CONFIRMING'      // 确认入库
  | 'COMPLETED';      // 完成
```

---

## 🎯 使用指南

### 1. 基础使用

```tsx
import DataImportPage from '@/pages/DataImportPage';

// 在应用中使用
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/data-import" element={<DataImportPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 2. 自定义Hook使用

```tsx
import { useDataImport } from '@/hooks/useDataImport';

function CustomImport() {
  const {
    uploadedFile,
    handleUpload,
    isUploading,
    uploadResult,
    qualityReport,
  } = useDataImport();

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileSelect} />
      {isUploading && <p>上传中...</p>}
      {uploadResult && (
        <div>
          <h3>{uploadResult.file_name}</h3>
          <p>行数: {uploadResult.row_count}</p>
          <p>质量评分: {uploadResult.quality_score}</p>
        </div>
      )}
    </div>
  );
}
```

### 3. API直接调用

```tsx
import { dataImportApi } from '@/services/dataImportApi';

async function uploadMyFile(file: File) {
  try {
    // 上传文件
    const uploadResult = await dataImportApi.uploadFile(file);
    console.log('上传成功:', uploadResult);

    // 分析格式
    const formatResult = await dataImportApi.analyzeFile(file);
    console.log('格式识别:', formatResult);

    // 验证质量
    const qualityResult = await dataImportApi.validateUploadedFile(
      uploadResult.file_name
    );
    console.log('质量报告:', qualityResult);
  } catch (error) {
    console.error('导入失败:', error);
  }
}
```

---

## ⚙️ 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# FastAPI Backend URL
VITE_API_URL="http://localhost:8000"

# Supabase (自动配置)
VITE_SUPABASE_URL="https://your-project.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY="your-key"
```

### API端点配置

在 `src/services/dataImportApi.ts` 中：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## 🔍 调试

### 开发者工具

1. **Network标签**: 查看API请求和响应
2. **Console标签**: 查看日志输出
3. **React DevTools**: 查看组件状态

### 常见问题

#### 1. 文件上传失败

**问题**: `Failed to upload file`

**解决**:
- 检查文件大小（最大20MB）
- 检查文件格式是否支持
- 检查后端API是否运行
- 检查CORS配置

#### 2. API连接失败

**问题**: `Failed to fetch`

**解决**:
- 确保后端服务运行在 `http://localhost:8000`
- 检查 `.env` 中的 `VITE_API_URL` 配置
- 检查网络连接
- 检查浏览器控制台错误信息

#### 3. 数据预览不显示

**问题**: 上传成功但看不到数据

**解决**:
- 检查 `uploadResult.preview_data` 是否存在
- 查看控制台是否有错误
- 确认后端返回了正确的预览数据格式

---

## 📊 性能优化

### 1. 大文件处理

- 使用分块上传（未来实现）
- 限制预览数据行数（当前10行）
- 使用虚拟滚动（大数据集）

### 2. API调用优化

- 使用 TanStack Query 缓存
- 防抖/节流用户输入
- 并行API调用

### 3. 渲染优化

- 使用 `React.memo` 防止不必要的重渲染
- 使用 `useCallback` 缓存回调函数
- 懒加载大组件

---

## 🚀 部署

### 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 后端服务（另一个终端）
cd backend
uvicorn main:app --reload
```

### 生产环境

```bash
# 构建前端
npm run build

# 部署前端（Lovable自动部署）
# 部署后端（需要单独部署FastAPI服务）
```

### 环境变量设置

生产环境需要设置：

```bash
VITE_API_URL="https://your-production-api.com"
```

---

## 📚 相关文档

1. [后端API规范](./FASTAPI_DATA_IMPORT_ETL_SPEC.md)
2. [核心算法验收报告](./ACCEPTANCE_REPORT.md)
3. [主数据表规范](./MASTER_DATA_TABLES_SPEC.md)
4. [数据导入分工方案](./DATA_IMPORT_DIVISION_PLAN.md)

---

## 🔗 技术资源

- [React文档](https://react.dev/)
- [TypeScript文档](https://www.typescriptlang.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Tailwind CSS](https://tailwindcss.com/)

---

**文档版本**: 1.0  
**最后更新**: 2025-11-04  
**维护者**: Lovable AI
