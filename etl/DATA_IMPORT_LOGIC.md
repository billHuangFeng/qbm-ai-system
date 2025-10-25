# 数据导入ETL逻辑文档

## 概述

本文档定义了边际分析系统的ETL（Extract, Transform, Load）数据处理逻辑，包括数据提取、转换、加载和验证流程。

## ETL架构

### 数据流图
```
原始数据源 → 数据提取 → 数据清洗 → 数据转换 → 数据验证 → 数据加载 → 目标数据库
     ↓           ↓         ↓         ↓         ↓         ↓
   Excel/CSV   解析器    清洗器    转换器    验证器    加载器    PostgreSQL
```

## 1. 数据提取层 (Extract)

### 1.1 支持的数据源
- **Excel文件**: .xlsx, .xls格式
- **CSV文件**: .csv格式，支持多种分隔符
- **JSON文件**: .json格式
- **API接口**: REST API数据源

### 1.2 文件解析器
```typescript
interface FileParser {
  parseExcel(file: File): Promise<ExcelData>;
  parseCSV(file: File, delimiter?: string): Promise<CSVData>;
  parseJSON(file: File): Promise<JSONData>;
  validateFileFormat(file: File): ValidationResult;
}

class ExcelParser implements FileParser {
  async parseExcel(file: File): Promise<ExcelData> {
    const workbook = XLSX.read(await file.arrayBuffer(), { type: 'array' });
    const sheets = workbook.SheetNames.map(name => ({
      name,
      data: XLSX.utils.sheet_to_json(workbook.Sheets[name])
    }));
    return { sheets, metadata: { fileName: file.name, size: file.size } };
  }
}
```

### 1.3 数据源配置
```typescript
interface DataSourceConfig {
  sourceType: 'excel' | 'csv' | 'json' | 'api';
  sourcePath: string;
  sheetName?: string;
  delimiter?: string;
  encoding?: string;
  headers?: string[];
  skipRows?: number;
  maxRows?: number;
}
```

## 2. 数据转换层 (Transform)

### 2.1 数据清洗
```typescript
interface DataCleaner {
  cleanData(data: any[]): CleanedData;
  removeDuplicates(data: any[]): any[];
  handleMissingValues(data: any[]): any[];
  standardizeFormats(data: any[]): any[];
}

class DataCleaner implements DataCleaner {
  cleanData(data: any[]): CleanedData {
    return {
      cleaned: this.removeDuplicates(
        this.handleMissingValues(
          this.standardizeFormats(data)
        )
      ),
      errors: this.collectErrors(data),
      statistics: this.generateStatistics(data)
    };
  }

  handleMissingValues(data: any[]): any[] {
    return data.map(row => {
      const cleanedRow = { ...row };
      Object.keys(cleanedRow).forEach(key => {
        if (cleanedRow[key] === null || cleanedRow[key] === undefined || cleanedRow[key] === '') {
          cleanedRow[key] = this.getDefaultValue(key);
        }
      });
      return cleanedRow;
    });
  }
}
```

### 2.2 数据转换
```typescript
interface DataTransformer {
  transformData(data: any[], mapping: FieldMapping): TransformedData;
  validateBusinessRules(data: any[]): ValidationResult;
  calculateDerivedFields(data: any[]): any[];
}

interface FieldMapping {
  sourceField: string;
  targetField: string;
  transformation: TransformationRule;
  validation: ValidationRule;
}

interface TransformationRule {
  type: 'direct' | 'formula' | 'lookup' | 'calculation';
  formula?: string;
  lookupTable?: string;
  parameters?: any;
}
```

### 2.3 业务规则转换
```typescript
class BusinessRuleTransformer {
  transformAssetData(data: any[]): AssetData[] {
    return data.map(row => ({
      asset_code: row['资产编码'],
      asset_name: row['资产名称'],
      asset_type: this.mapAssetType(row['资产类型']),
      acquisition_date: this.parseDate(row['购置日期']),
      acquisition_cost: this.parseNumber(row['购置成本']),
      useful_life_years: this.parseInteger(row['使用年限']),
      residual_value: this.parseNumber(row['残值']) || 0,
      depreciation_method: this.mapDepreciationMethod(row['折旧方法']),
      discount_rate: this.parseNumber(row['折现率']) || 0.10,
      cash_flow_years: this.parseInteger(row['现金流年数']) || 5,
      annual_cash_flow: this.extractCashFlow(row)
    }));
  }

  transformCapabilityData(data: any[]): CapabilityData[] {
    return data.map(row => ({
      capability_code: row['能力编码'],
      capability_name: row['能力名称'],
      capability_type: this.mapCapabilityType(row['能力类型']),
      capability_level: this.mapCapabilityLevel(row['能力级别']),
      description: row['描述'],
      contribution_percentage: this.parseNumber(row['贡献百分比']) || 0,
      annual_benefit: this.parseNumber(row['年度收益']),
      benefit_measurement_period: this.parseInteger(row['收益测量周期']) || 12
    }));
  }
}
```

## 3. 数据验证层 (Validation)

### 3.1 数据质量检查
```typescript
interface DataQualityChecker {
  checkCompleteness(data: any[]): QualityReport;
  checkAccuracy(data: any[]): QualityReport;
  checkConsistency(data: any[]): QualityReport;
  checkValidity(data: any[]): QualityReport;
}

class DataQualityChecker implements DataQualityChecker {
  checkCompleteness(data: any[]): QualityReport {
    const requiredFields = ['asset_code', 'asset_name', 'asset_type'];
    const missingFields = data.map(row => 
      requiredFields.filter(field => !row[field])
    );
    
    return {
      score: this.calculateCompletenessScore(missingFields),
      issues: missingFields,
      recommendations: this.generateCompletenessRecommendations(missingFields)
    };
  }

  checkAccuracy(data: any[]): QualityReport {
    const accuracyIssues = data.map(row => {
      const issues = [];
      if (row.acquisition_cost && row.acquisition_cost <= 0) {
        issues.push('购置成本必须大于0');
      }
      if (row.useful_life_years && row.useful_life_years <= 0) {
        issues.push('使用年限必须大于0');
      }
      return issues;
    });

    return {
      score: this.calculateAccuracyScore(accuracyIssues),
      issues: accuracyIssues,
      recommendations: this.generateAccuracyRecommendations(accuracyIssues)
    };
  }
}
```

### 3.2 业务规则验证
```typescript
interface BusinessRuleValidator {
  validateAssetRules(data: AssetData[]): ValidationResult;
  validateCapabilityRules(data: CapabilityData[]): ValidationResult;
  validateValueItemRules(data: ValueItemData[]): ValidationResult;
}

class BusinessRuleValidator implements BusinessRuleValidator {
  validateAssetRules(data: AssetData[]): ValidationResult {
    const errors = [];
    
    data.forEach((asset, index) => {
      // 资产编码唯一性检查
      const duplicateCodes = data.filter(a => a.asset_code === asset.asset_code);
      if (duplicateCodes.length > 1) {
        errors.push(`行${index + 1}: 资产编码 ${asset.asset_code} 重复`);
      }

      // 购置成本验证
      if (asset.acquisition_cost <= 0) {
        errors.push(`行${index + 1}: 购置成本必须大于0`);
      }

      // 使用年限验证
      if (asset.useful_life_years <= 0) {
        errors.push(`行${index + 1}: 使用年限必须大于0`);
      }

      // 折现率验证
      if (asset.discount_rate < 0 || asset.discount_rate > 1) {
        errors.push(`行${index + 1}: 折现率必须在0-1之间`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
      warnings: this.generateWarnings(data)
    };
  }
}
```

## 4. 数据加载层 (Load)

### 4.1 批量插入
```typescript
interface DataLoader {
  loadData(data: any[], tableName: string): Promise<LoadResult>;
  batchInsert(data: any[], batchSize?: number): Promise<LoadResult>;
  handleConflicts(data: any[], conflictStrategy: ConflictStrategy): Promise<LoadResult>;
}

class DataLoader implements DataLoader {
  async loadData(data: any[], tableName: string): Promise<LoadResult> {
    const batchSize = 1000;
    const batches = this.createBatches(data, batchSize);
    const results = [];

    for (const batch of batches) {
      try {
        const result = await this.insertBatch(batch, tableName);
        results.push(result);
      } catch (error) {
        return {
          success: false,
          error: error.message,
          processedCount: results.reduce((sum, r) => sum + r.count, 0)
        };
      }
    }

    return {
      success: true,
      processedCount: data.length,
      insertedCount: results.reduce((sum, r) => sum + r.count, 0),
      updatedCount: 0,
      errorCount: 0
    };
  }

  private async insertBatch(batch: any[], tableName: string): Promise<BatchResult> {
    const query = this.buildInsertQuery(batch, tableName);
    const result = await this.database.query(query);
    return {
      count: result.rowCount,
      batch: batch.length
    };
  }
}
```

### 4.2 冲突处理
```typescript
interface ConflictStrategy {
  type: 'ignore' | 'update' | 'replace' | 'error';
  keyFields: string[];
  updateFields?: string[];
}

class ConflictHandler {
  handleConflicts(data: any[], strategy: ConflictStrategy): Promise<ConflictResult> {
    switch (strategy.type) {
      case 'ignore':
        return this.handleIgnoreConflicts(data, strategy);
      case 'update':
        return this.handleUpdateConflicts(data, strategy);
      case 'replace':
        return this.handleReplaceConflicts(data, strategy);
      case 'error':
        return this.handleErrorConflicts(data, strategy);
    }
  }

  private async handleUpdateConflicts(data: any[], strategy: ConflictStrategy): Promise<ConflictResult> {
    const conflicts = await this.detectConflicts(data, strategy.keyFields);
    const updates = conflicts.map(conflict => ({
      ...conflict.newData,
      updated_at: new Date()
    }));

    await this.batchUpdate(updates, strategy.keyFields);
    
    return {
      success: true,
      conflictsResolved: conflicts.length,
      conflictsIgnored: 0
    };
  }
}
```

## 5. 数据质量监控

### 5.1 质量指标
```typescript
interface QualityMetrics {
  completeness: number;      // 完整性 (0-1)
  accuracy: number;          // 准确性 (0-1)
  consistency: number;       // 一致性 (0-1)
  validity: number;          // 有效性 (0-1)
  timeliness: number;        // 及时性 (0-1)
  overall: number;           // 总体质量 (0-1)
}

class QualityMonitor {
  calculateQualityMetrics(data: any[]): QualityMetrics {
    return {
      completeness: this.calculateCompleteness(data),
      accuracy: this.calculateAccuracy(data),
      consistency: this.calculateConsistency(data),
      validity: this.calculateValidity(data),
      timeliness: this.calculateTimeliness(data),
      overall: this.calculateOverallQuality(data)
    };
  }

  private calculateCompleteness(data: any[]): number {
    const totalFields = data.length * this.getRequiredFields().length;
    const missingFields = this.countMissingFields(data);
    return 1 - (missingFields / totalFields);
  }
}
```

### 5.2 质量报告
```typescript
interface QualityReport {
  metrics: QualityMetrics;
  issues: QualityIssue[];
  recommendations: string[];
  trends: QualityTrend[];
}

interface QualityIssue {
  type: 'completeness' | 'accuracy' | 'consistency' | 'validity';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedRows: number[];
  suggestedFix: string;
}
```

## 6. 错误处理和恢复

### 6.1 错误分类
```typescript
enum ErrorType {
  VALIDATION_ERROR = 'validation_error',
  TRANSFORMATION_ERROR = 'transformation_error',
  LOAD_ERROR = 'load_error',
  CONNECTION_ERROR = 'connection_error',
  PERMISSION_ERROR = 'permission_error'
}

interface ErrorHandler {
  handleError(error: Error, context: ErrorContext): ErrorResult;
  retryOperation(operation: () => Promise<any>, maxRetries: number): Promise<any>;
  rollbackTransaction(transactionId: string): Promise<void>;
}
```

### 6.2 重试机制
```typescript
class RetryHandler {
  async retryOperation<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        
        if (attempt === maxRetries) {
          throw lastError;
        }
        
        await this.delay(delay * Math.pow(2, attempt - 1)); // 指数退避
      }
    }
    
    throw lastError;
  }
}
```

## 7. 性能优化

### 7.1 批量处理
```typescript
class BatchProcessor {
  async processBatches<T>(
    data: T[],
    batchSize: number,
    processor: (batch: T[]) => Promise<void>
  ): Promise<void> {
    const batches = this.createBatches(data, batchSize);
    
    for (const batch of batches) {
      await processor(batch);
    }
  }

  private createBatches<T>(data: T[], batchSize: number): T[][] {
    const batches = [];
    for (let i = 0; i < data.length; i += batchSize) {
      batches.push(data.slice(i, i + batchSize));
    }
    return batches;
  }
}
```

### 7.2 内存优化
```typescript
class MemoryOptimizer {
  processLargeFile(file: File): AsyncGenerator<any[], void, unknown> {
    return this.streamProcessFile(file);
  }

  private async *streamProcessFile(file: File): AsyncGenerator<any[], void, unknown> {
    const stream = file.stream();
    const reader = stream.getReader();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += new TextDecoder().decode(value);
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        yield lines.map(line => this.parseLine(line));
      }
    } finally {
      reader.releaseLock();
    }
  }
}
```

## 8. 监控和日志

### 8.1 ETL监控
```typescript
interface ETLMonitor {
  startJob(jobId: string): void;
  updateProgress(jobId: string, progress: number): void;
  logEvent(jobId: string, event: ETLEvent): void;
  completeJob(jobId: string, result: ETLResult): void;
  failJob(jobId: string, error: Error): void;
}

interface ETLEvent {
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  data?: any;
}
```

### 8.2 日志记录
```typescript
class ETLLogger {
  logExtraction(source: string, recordCount: number): void {
    this.log('info', `Extracted ${recordCount} records from ${source}`);
  }

  logTransformation(transformation: string, inputCount: number, outputCount: number): void {
    this.log('info', `Transformed ${inputCount} records to ${outputCount} using ${transformation}`);
  }

  logLoading(table: string, recordCount: number): void {
    this.log('info', `Loaded ${recordCount} records into ${table}`);
  }

  logError(error: Error, context: string): void {
    this.log('error', `Error in ${context}: ${error.message}`, { error: error.stack });
  }
}
```

## 9. 配置管理

### 9.1 ETL配置
```typescript
interface ETLConfig {
  extraction: ExtractionConfig;
  transformation: TransformationConfig;
  loading: LoadingConfig;
  validation: ValidationConfig;
  monitoring: MonitoringConfig;
}

interface ExtractionConfig {
  batchSize: number;
  maxFileSize: number;
  supportedFormats: string[];
  timeout: number;
}

interface TransformationConfig {
  rules: TransformationRule[];
  mappings: FieldMapping[];
  businessRules: BusinessRule[];
}

interface LoadingConfig {
  batchSize: number;
  conflictStrategy: ConflictStrategy;
  transactionMode: 'auto' | 'manual';
  rollbackOnError: boolean;
}
```

### 9.2 环境配置
```typescript
interface EnvironmentConfig {
  development: ETLConfig;
  staging: ETLConfig;
  production: ETLConfig;
}

const etlConfig: EnvironmentConfig = {
  development: {
    extraction: { batchSize: 100, maxFileSize: 10485760, supportedFormats: ['xlsx', 'csv'], timeout: 30000 },
    transformation: { rules: [], mappings: [], businessRules: [] },
    loading: { batchSize: 100, conflictStrategy: { type: 'update' }, transactionMode: 'auto', rollbackOnError: true }
  },
  staging: {
    extraction: { batchSize: 500, maxFileSize: 52428800, supportedFormats: ['xlsx', 'csv'], timeout: 60000 },
    transformation: { rules: [], mappings: [], businessRules: [] },
    loading: { batchSize: 500, conflictStrategy: { type: 'update' }, transactionMode: 'auto', rollbackOnError: true }
  },
  production: {
    extraction: { batchSize: 1000, maxFileSize: 104857600, supportedFormats: ['xlsx', 'csv'], timeout: 120000 },
    transformation: { rules: [], mappings: [], businessRules: [] },
    loading: { batchSize: 1000, conflictStrategy: { type: 'update' }, transactionMode: 'auto', rollbackOnError: true }
  }
};
```

## 10. 使用示例

### 10.1 完整ETL流程
```typescript
class ETLPipeline {
  async executeETL(file: File, config: ETLConfig): Promise<ETLResult> {
    const jobId = this.generateJobId();
    this.monitor.startJob(jobId);

    try {
      // 1. 数据提取
      this.monitor.updateProgress(jobId, 10);
      const rawData = await this.extractor.extract(file);
      this.logger.logExtraction(file.name, rawData.length);

      // 2. 数据清洗
      this.monitor.updateProgress(jobId, 30);
      const cleanedData = await this.cleaner.cleanData(rawData);
      this.logger.logCleaning(cleanedData.cleaned.length, cleanedData.errors.length);

      // 3. 数据转换
      this.monitor.updateProgress(jobId, 50);
      const transformedData = await this.transformer.transformData(cleanedData.cleaned, config.transformation);
      this.logger.logTransformation('business_rules', cleanedData.cleaned.length, transformedData.length);

      // 4. 数据验证
      this.monitor.updateProgress(jobId, 70);
      const validationResult = await this.validator.validateData(transformedData);
      if (!validationResult.isValid) {
        throw new ValidationError('Data validation failed', validationResult.errors);
      }

      // 5. 数据加载
      this.monitor.updateProgress(jobId, 90);
      const loadResult = await this.loader.loadData(transformedData, config.loading);
      this.logger.logLoading('target_table', loadResult.insertedCount);

      // 6. 完成
      this.monitor.updateProgress(jobId, 100);
      const result = {
        success: true,
        processedCount: transformedData.length,
        insertedCount: loadResult.insertedCount,
        errorCount: loadResult.errorCount,
        qualityMetrics: this.qualityMonitor.calculateQualityMetrics(transformedData)
      };

      this.monitor.completeJob(jobId, result);
      return result;

    } catch (error) {
      this.monitor.failJob(jobId, error);
      this.logger.logError(error, 'ETL Pipeline');
      throw error;
    }
  }
}
```

### 10.2 错误恢复
```typescript
class ETLRecovery {
  async recoverFromError(jobId: string, error: Error): Promise<void> {
    const jobState = await this.getJobState(jobId);
    
    switch (error.name) {
      case 'ValidationError':
        await this.handleValidationError(jobId, error);
        break;
      case 'TransformationError':
        await this.handleTransformationError(jobId, error);
        break;
      case 'LoadError':
        await this.handleLoadError(jobId, error);
        break;
      default:
        await this.handleUnknownError(jobId, error);
    }
  }

  private async handleLoadError(jobId: string, error: Error): Promise<void> {
    // 回滚已插入的数据
    await this.rollbackTransaction(jobId);
    
    // 重试加载
    const retryResult = await this.retryHandler.retryOperation(
      () => this.loader.loadData(this.getTransformedData(jobId), this.getLoadingConfig()),
      3
    );
    
    if (retryResult.success) {
      this.logger.log('info', `Successfully recovered from load error for job ${jobId}`);
    } else {
      this.logger.log('error', `Failed to recover from load error for job ${jobId}`);
    }
  }
}
```
