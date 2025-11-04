/**
 * 数据验证器
 * 功能：数据完整性检查、字段类型验证、空值检测、异常值识别、重复数据检测
 */

import { ParsedFileData } from './file-parser.ts';

export interface ValidationRule {
  required_fields?: string[];
  max_null_ratio?: number;
  check_duplicates?: boolean;
  field_types?: Record<string, 'string' | 'number' | 'date' | 'boolean'>;
}

export interface ValidationIssue {
  type: 'missing_field' | 'invalid_format' | 'null_value' | 'duplicate' | 'outlier' | 'type_mismatch';
  severity: 'error' | 'warning' | 'info';
  field?: string;
  description: string;
  affected_rows: number;
  row_indices?: number[];
}

export interface QualityReport {
  overall_quality_score: number;
  completeness_score: number;
  accuracy_score: number;
  consistency_score: number;
  issues: ValidationIssue[];
}

/**
 * 检查必填字段
 */
function checkRequiredFields(
  data: ParsedFileData,
  requiredFields: string[]
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const columns = data.columns;

  for (const field of requiredFields) {
    if (!columns.includes(field)) {
      issues.push({
        type: 'missing_field',
        severity: 'error',
        field,
        description: `必填字段 "${field}" 不存在`,
        affected_rows: data.rowCount,
      });
    }
  }

  return issues;
}

/**
 * 检查空值比例
 */
function checkNullRatio(
  data: ParsedFileData,
  maxNullRatio: number
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const totalRows = data.rowCount;

  for (const column of data.columns) {
    let nullCount = 0;
    const nullRowIndices: number[] = [];

    for (let i = 0; i < data.data.length; i++) {
      const value = data.data[i][column];
      if (value === null || value === undefined || value === '') {
        nullCount++;
        nullRowIndices.push(i);
      }
    }

    const nullRatio = nullCount / totalRows;
    if (nullRatio > maxNullRatio) {
      issues.push({
        type: 'null_value',
        severity: nullRatio > 0.5 ? 'error' : 'warning',
        field: column,
        description: `字段 "${column}" 空值比例过高: ${(nullRatio * 100).toFixed(1)}%`,
        affected_rows: nullCount,
        row_indices: nullRowIndices.slice(0, 10), // 只返回前10个
      });
    }
  }

  return issues;
}

/**
 * 检查字段类型
 */
function checkFieldTypes(
  data: ParsedFileData,
  fieldTypes: Record<string, string>
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  for (const [field, expectedType] of Object.entries(fieldTypes)) {
    if (!data.columns.includes(field)) continue;

    const invalidRowIndices: number[] = [];

    for (let i = 0; i < data.data.length; i++) {
      const value = data.data[i][field];
      if (value === null || value === undefined || value === '') continue;

      let isValid = true;
      switch (expectedType) {
        case 'number':
          isValid = !isNaN(Number(value));
          break;
        case 'date':
          isValid = !isNaN(Date.parse(String(value)));
          break;
        case 'boolean':
          isValid = ['true', 'false', '1', '0', 'yes', 'no'].includes(
            String(value).toLowerCase()
          );
          break;
        case 'string':
          isValid = typeof value === 'string';
          break;
      }

      if (!isValid) {
        invalidRowIndices.push(i);
      }
    }

    if (invalidRowIndices.length > 0) {
      issues.push({
        type: 'type_mismatch',
        severity: 'error',
        field,
        description: `字段 "${field}" 类型不匹配，期望 ${expectedType}`,
        affected_rows: invalidRowIndices.length,
        row_indices: invalidRowIndices.slice(0, 10),
      });
    }
  }

  return issues;
}

/**
 * 检查重复数据
 */
function checkDuplicates(data: ParsedFileData): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const seen = new Map<string, number[]>();

  for (let i = 0; i < data.data.length; i++) {
    const row = data.data[i];
    const rowKey = JSON.stringify(row);

    if (seen.has(rowKey)) {
      seen.get(rowKey)!.push(i);
    } else {
      seen.set(rowKey, [i]);
    }
  }

  const duplicates = Array.from(seen.entries()).filter(
    ([_, indices]) => indices.length > 1
  );

  if (duplicates.length > 0) {
    const totalDuplicateRows = duplicates.reduce(
      (sum, [_, indices]) => sum + indices.length - 1,
      0
    );

    issues.push({
      type: 'duplicate',
      severity: 'warning',
      description: `发现 ${duplicates.length} 组重复数据，共 ${totalDuplicateRows} 行重复`,
      affected_rows: totalDuplicateRows,
    });
  }

  return issues;
}

/**
 * 检测异常值（数值字段）
 */
function checkOutliers(data: ParsedFileData): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  for (const column of data.columns) {
    const numericValues: number[] = [];

    for (const row of data.data) {
      const value = row[column];
      if (value !== null && value !== undefined && !isNaN(Number(value))) {
        numericValues.push(Number(value));
      }
    }

    if (numericValues.length < 10) continue; // 数据太少，不检测异常值

    // 计算 IQR (四分位距)
    numericValues.sort((a, b) => a - b);
    const q1 = numericValues[Math.floor(numericValues.length * 0.25)];
    const q3 = numericValues[Math.floor(numericValues.length * 0.75)];
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;

    const outlierIndices: number[] = [];
    for (let i = 0; i < data.data.length; i++) {
      const value = Number(data.data[i][column]);
      if (!isNaN(value) && (value < lowerBound || value > upperBound)) {
        outlierIndices.push(i);
      }
    }

    if (outlierIndices.length > 0) {
      issues.push({
        type: 'outlier',
        severity: 'info',
        field: column,
        description: `字段 "${column}" 发现 ${outlierIndices.length} 个异常值`,
        affected_rows: outlierIndices.length,
        row_indices: outlierIndices.slice(0, 10),
      });
    }
  }

  return issues;
}

/**
 * 计算质量分数
 */
function calculateQualityScores(
  data: ParsedFileData,
  issues: ValidationIssue[]
): { completeness: number; accuracy: number; consistency: number; overall: number } {
  const totalCells = data.rowCount * data.columnCount;
  
  // 完整性分数：基于空值问题
  const nullIssues = issues.filter(i => i.type === 'null_value');
  const nullCells = nullIssues.reduce((sum, i) => sum + i.affected_rows, 0);
  const completeness = Math.max(0, 100 - (nullCells / totalCells) * 100);

  // 准确性分数：基于类型不匹配和格式错误
  const accuracyIssues = issues.filter(
    i => i.type === 'type_mismatch' || i.type === 'invalid_format'
  );
  const inaccurateCells = accuracyIssues.reduce((sum, i) => sum + i.affected_rows, 0);
  const accuracy = Math.max(0, 100 - (inaccurateCells / totalCells) * 100);

  // 一致性分数：基于重复数据和异常值
  const consistencyIssues = issues.filter(
    i => i.type === 'duplicate' || i.type === 'outlier'
  );
  const inconsistentRows = consistencyIssues.reduce((sum, i) => sum + i.affected_rows, 0);
  const consistency = Math.max(0, 100 - (inconsistentRows / data.rowCount) * 100);

  // 总体分数：加权平均
  const overall = (completeness * 0.4 + accuracy * 0.4 + consistency * 0.2);

  return {
    completeness: Math.round(completeness * 10) / 10,
    accuracy: Math.round(accuracy * 10) / 10,
    consistency: Math.round(consistency * 10) / 10,
    overall: Math.round(overall * 10) / 10,
  };
}

/**
 * 验证数据质量
 */
export async function validateData(
  data: ParsedFileData,
  rules?: ValidationRule
): Promise<QualityReport> {
  const issues: ValidationIssue[] = [];

  // 1. 检查必填字段
  if (rules?.required_fields && rules.required_fields.length > 0) {
    issues.push(...checkRequiredFields(data, rules.required_fields));
  }

  // 2. 检查空值比例
  const maxNullRatio = rules?.max_null_ratio ?? 0.3;
  issues.push(...checkNullRatio(data, maxNullRatio));

  // 3. 检查字段类型
  if (rules?.field_types) {
    issues.push(...checkFieldTypes(data, rules.field_types));
  }

  // 4. 检查重复数据
  if (rules?.check_duplicates !== false) {
    issues.push(...checkDuplicates(data));
  }

  // 5. 检测异常值
  issues.push(...checkOutliers(data));

  // 6. 计算质量分数
  const scores = calculateQualityScores(data, issues);

  return {
    overall_quality_score: scores.overall,
    completeness_score: scores.completeness,
    accuracy_score: scores.accuracy,
    consistency_score: scores.consistency,
    issues,
  };
}
