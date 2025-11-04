/**
 * 主数据匹配器
 * 功能：自动匹配主数据（客户、SKU、供应商等）、模糊匹配、相似度评分、多候选项推荐
 */

import { createClient, SupabaseClient } from 'jsr:@supabase/supabase-js@2';

export type EntityType = 'customer' | 'sku' | 'supplier' | 'channel';

export interface MatchConfig {
  entity_type: EntityType;
  match_fields: string[];
  threshold?: number;
}

export interface MatchCandidate {
  id: string;
  name: string;
  code?: string;
  similarity: number;
}

export interface MatchResult {
  source_value: string;
  matched: boolean;
  master_id?: string;
  master_name?: string;
  master_code?: string;
  confidence: number;
  candidates?: MatchCandidate[];
}

/**
 * 计算 Levenshtein 距离（编辑距离）
 */
function levenshteinDistance(str1: string, str2: string): number {
  const m = str1.length;
  const n = str2.length;
  const dp: number[][] = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,     // 删除
          dp[i][j - 1] + 1,     // 插入
          dp[i - 1][j - 1] + 1  // 替换
        );
      }
    }
  }

  return dp[m][n];
}

/**
 * 计算相似度分数 (0-1)
 */
function calculateSimilarity(str1: string, str2: string): number {
  if (!str1 || !str2) return 0;
  
  const s1 = str1.toLowerCase().trim();
  const s2 = str2.toLowerCase().trim();
  
  if (s1 === s2) return 1.0;
  
  const maxLen = Math.max(s1.length, s2.length);
  if (maxLen === 0) return 0;
  
  const distance = levenshteinDistance(s1, s2);
  return 1 - distance / maxLen;
}

/**
 * 计算综合相似度（考虑多个字段）
 */
function calculateCompositeSimilarity(
  sourceValue: string,
  masterRecord: Record<string, any>,
  matchFields: string[]
): number {
  const similarities: number[] = [];
  
  for (const field of matchFields) {
    const masterValue = masterRecord[field];
    if (masterValue) {
      const similarity = calculateSimilarity(sourceValue, String(masterValue));
      similarities.push(similarity);
    }
  }
  
  if (similarities.length === 0) return 0;
  
  // 取最高相似度（最优匹配）
  return Math.max(...similarities);
}

/**
 * 获取主数据表名
 */
function getMasterTableName(entityType: EntityType): string {
  const tableMap: Record<EntityType, string> = {
    customer: 'dim_customer',
    sku: 'dim_sku',
    supplier: 'dim_supplier',
    channel: 'dim_channel',
  };
  return tableMap[entityType];
}

/**
 * 获取主数据字段映射
 */
function getMasterFieldMap(entityType: EntityType): { id: string; name: string; code: string } {
  const fieldMaps: Record<EntityType, { id: string; name: string; code: string }> = {
    customer: { id: 'customer_id', name: 'customer_name', code: 'customer_code' },
    sku: { id: 'sku_id', name: 'sku_name', code: 'sku_code' },
    supplier: { id: 'supplier_id', name: 'supplier_name', code: 'supplier_code' },
    channel: { id: 'channel_id', name: 'channel_name', code: 'channel_code' },
  };
  return fieldMaps[entityType];
}

/**
 * 匹配主数据
 */
export async function matchMasterData(
  supabase: SupabaseClient,
  tenantId: string,
  sourceValues: string[],
  config: MatchConfig
): Promise<MatchResult[]> {
  const { entity_type, match_fields, threshold = 0.7 } = config;
  
  // 获取表名和字段映射
  const tableName = getMasterTableName(entity_type);
  const fieldMap = getMasterFieldMap(entity_type);
  
  console.log(`Matching ${sourceValues.length} values against ${tableName}`);
  
  // 查询主数据
  const { data: masterRecords, error } = await supabase
    .from(tableName)
    .select('*')
    .eq('tenant_id', tenantId);
  
  if (error) {
    console.error('Failed to fetch master data:', error);
    throw error;
  }
  
  if (!masterRecords || masterRecords.length === 0) {
    console.log('No master records found');
    return sourceValues.map(value => ({
      source_value: value,
      matched: false,
      confidence: 0,
      candidates: [],
    }));
  }
  
  console.log(`Found ${masterRecords.length} master records`);
  
  // 对每个源值进行匹配
  const results: MatchResult[] = [];
  
  for (const sourceValue of sourceValues) {
    if (!sourceValue || sourceValue.trim() === '') {
      results.push({
        source_value: sourceValue,
        matched: false,
        confidence: 0,
        candidates: [],
      });
      continue;
    }
    
    // 计算与所有主数据的相似度
    const candidates: MatchCandidate[] = masterRecords
      .map(record => {
        const similarity = calculateCompositeSimilarity(
          sourceValue,
          record,
          match_fields
        );
        
        return {
          id: record[fieldMap.id],
          name: record[fieldMap.name],
          code: record[fieldMap.code],
          similarity,
        };
      })
      .filter(c => c.similarity > 0)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, 5); // 只保留前5个候选项
    
    // 判断是否匹配成功
    const bestMatch = candidates[0];
    const matched = bestMatch && bestMatch.similarity >= threshold;
    
    results.push({
      source_value: sourceValue,
      matched: matched || false,
      master_id: matched ? bestMatch.id : undefined,
      master_name: matched ? bestMatch.name : undefined,
      master_code: matched ? bestMatch.code : undefined,
      confidence: bestMatch?.similarity || 0,
      candidates: candidates.length > 0 ? candidates : undefined,
    });
  }
  
  const matchedCount = results.filter(r => r.matched).length;
  console.log(`Matched ${matchedCount}/${sourceValues.length} values (${(matchedCount/sourceValues.length*100).toFixed(1)}%)`);
  
  return results;
}

/**
 * 从文件数据中提取唯一值
 */
export function extractUniqueValues(
  data: Record<string, any>[],
  fieldName: string
): string[] {
  const uniqueValues = new Set<string>();
  
  for (const row of data) {
    const value = row[fieldName];
    if (value !== null && value !== undefined && value !== '') {
      uniqueValues.add(String(value).trim());
    }
  }
  
  return Array.from(uniqueValues);
}
