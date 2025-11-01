# 数据版本控制与历史归档设计

## 📋 概述

基于用户澄清，系统需要支持数据版本控制和历史归档，确保数据可追溯和审计合规。

## 🏗️ 版本控制策略

### 1. 资产现金流预测版本控制

#### 版本触发条件
- **年度更新**：每年1月更新下一年度预测
- **重大变化**：市场变化、政策变化、技术突破
- **手动触发**：用户主动更新

#### 版本数据结构
```sql
-- 资产现金流预测版本表
CREATE TABLE asset_cashflow_projection_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES core_asset_master(asset_id),
    version_number INT NOT NULL,
    version_type VARCHAR(20) NOT NULL, -- annual/major_change/manual
    version_reason TEXT, -- 版本更新原因
    baseline_year INT,
    baseline_cashflow DECIMAL(15,2),
    year_1_cashflow DECIMAL(15,2),
    year_2_cashflow DECIMAL(15,2),
    year_3_cashflow DECIMAL(15,2),
    year_4_cashflow DECIMAL(15,2),
    year_5_cashflow DECIMAL(15,2),
    discount_rate DECIMAL(5,4),
    npv_total DECIMAL(15,2),
    monthly_asset_delta DECIMAL(15,2),
    projection_date DATE NOT NULL,
    scenario VARCHAR(20),
    data_source VARCHAR(100),
    is_current BOOLEAN DEFAULT false, -- 是否为当前版本
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id)
);

-- 版本历史表（归档）
CREATE TABLE asset_cashflow_projection_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL,
    version_id UUID NOT NULL,
    change_type VARCHAR(20) NOT NULL, -- created/updated/archived
    change_reason TEXT,
    old_values JSONB, -- 变更前的值
    new_values JSONB, -- 变更后的值
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by UUID REFERENCES users(user_id)
);
```

#### 版本管理逻辑
```typescript
// 创建新版本
async function createAssetProjectionVersion(
  assetId: string,
  versionData: AssetProjectionData,
  versionType: 'annual' | 'major_change' | 'manual',
  reason: string,
  userId: string
): Promise<string> {
  // 1. 获取当前版本号
  const currentVersion = await getCurrentVersion(assetId);
  const newVersionNumber = currentVersion + 1;
  
  // 2. 将当前版本标记为非当前
  await markVersionAsArchived(assetId);
  
  // 3. 创建新版本
  const versionId = await createVersion({
    assetId,
    versionNumber: newVersionNumber,
    versionType,
    versionReason: reason,
    ...versionData,
    isCurrent: true,
    createdBy: userId
  });
  
  // 4. 记录版本历史
  await recordVersionHistory(assetId, versionId, 'created', reason, null, versionData, userId);
  
  return versionId;
}

// 获取版本历史
async function getAssetProjectionHistory(assetId: string): Promise<VersionHistory[]> {
  return await db.query(`
    SELECT 
      v.version_number,
      v.version_type,
      v.version_reason,
      v.projection_date,
      v.npv_total,
      v.is_current,
      v.created_at,
      u.user_name as created_by_name
    FROM asset_cashflow_projection_versions v
    LEFT JOIN users u ON v.created_by = u.user_id
    WHERE v.asset_id = $1
    ORDER BY v.version_number DESC
  `, [assetId]);
}
```

### 2. 能力价值评估版本控制

#### 版本触发条件
- **能力建设里程碑**：能力成熟度达到新阶段
- **成果达成**：稳定成果指标达成
- **能力衰退**：能力指标下降

#### 版本数据结构
```sql
-- 能力价值评估版本表
CREATE TABLE capability_value_assessment_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_id UUID NOT NULL REFERENCES core_capability_master(capability_id),
    version_number INT NOT NULL,
    version_type VARCHAR(20) NOT NULL, -- milestone/achievement/decline
    version_reason TEXT,
    outcome_metric VARCHAR(100),
    baseline_value DECIMAL(10,4),
    target_value DECIMAL(10,4),
    current_value DECIMAL(10,4),
    stable_months INT,
    is_stable BOOLEAN,
    annual_revenue_impact DECIMAL(15,2),
    contribution_percentage DECIMAL(5,4),
    monthly_capability_value DECIMAL(15,2),
    assessment_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id)
);

-- 能力价值历史表
CREATE TABLE capability_value_history_versions (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_id UUID NOT NULL,
    version_id UUID NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    change_reason TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by UUID REFERENCES users(user_id)
);
```

### 3. 价值评估数据版本控制

#### 版本触发条件
- **持续收集**：客户调研数据持续更新
- **产品迭代**：产品功能变化时重新评估
- **市场反馈**：市场环境变化时重新评估

#### 版本数据结构
```sql
-- 价值评估数据版本表
CREATE TABLE value_assessment_data_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL, -- 关联到具体评估表
    value_type VARCHAR(50) NOT NULL, -- intrinsic/cognitive/experiential
    version_number INT NOT NULL,
    version_type VARCHAR(20) NOT NULL, -- continuous/iteration/feedback
    version_reason TEXT,
    assessment_data JSONB NOT NULL, -- 评估数据
    overall_score DECIMAL(5,4),
    assessment_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(user_id)
);

-- 价值评估历史表
CREATE TABLE value_assessment_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL,
    version_id UUID NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    change_reason TEXT,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by UUID REFERENCES users(user_id)
);
```

## 📊 历史归档策略

### 1. 归档规则

#### 自动归档
- **年度归档**：每年12月自动归档上一年度数据
- **版本归档**：新版本创建时自动归档旧版本
- **数据归档**：超过5年的历史数据自动归档

#### 手动归档
- **重大变化**：用户主动归档特定版本
- **审计需求**：合规审计时归档相关数据
- **清理需求**：系统维护时归档冗余数据

### 2. 归档存储

#### 冷存储策略
```sql
-- 归档表（冷存储）
CREATE TABLE archived_asset_projections (
    archive_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id UUID NOT NULL,
    asset_id UUID NOT NULL,
    version_data JSONB NOT NULL,
    archive_date TIMESTAMPTZ DEFAULT NOW(),
    archive_reason VARCHAR(100),
    archived_by UUID REFERENCES users(user_id)
);

-- 归档索引
CREATE INDEX idx_archived_asset_date ON archived_asset_projections(archive_date);
CREATE INDEX idx_archived_asset_asset ON archived_asset_projections(asset_id);
```

#### 归档查询
```typescript
// 查询归档数据
async function getArchivedData(
  assetId: string,
  startDate: Date,
  endDate: Date
): Promise<ArchivedData[]> {
  return await db.query(`
    SELECT 
      archive_id,
      original_id,
      version_data,
      archive_date,
      archive_reason
    FROM archived_asset_projections
    WHERE asset_id = $1 
      AND archive_date BETWEEN $2 AND $3
    ORDER BY archive_date DESC
  `, [assetId, startDate, endDate]);
}
```

## 🔄 数据同步策略

### 1. 实时同步

#### 当前数据更新
```typescript
// 更新当前数据时同步版本
async function updateCurrentData(
  assetId: string,
  newData: any,
  userId: string,
  reason: string
): Promise<void> {
  // 1. 获取当前版本
  const currentVersion = await getCurrentVersion(assetId);
  
  // 2. 创建新版本
  const newVersion = await createNewVersion(assetId, newData, userId, reason);
  
  // 3. 更新当前数据
  await updateCurrentData(assetId, newData);
  
  // 4. 记录变更历史
  await recordChangeHistory(assetId, currentVersion, newVersion, reason, userId);
}
```

### 2. 批量同步

#### 年度数据同步
```typescript
// 年度数据同步
async function annualDataSync(): Promise<void> {
  console.log('开始年度数据同步...');
  
  // 1. 获取所有活跃资产
  const assets = await getActiveAssets();
  
  for (const asset of assets) {
    // 2. 检查是否需要更新
    const needsUpdate = await checkUpdateNeeded(asset.id);
    
    if (needsUpdate) {
      // 3. 创建新版本
      await createAnnualVersion(asset.id, 'annual_update');
    }
  }
  
  console.log('年度数据同步完成');
}
```

## 📈 版本分析功能

### 1. 版本对比

#### 版本差异分析
```typescript
// 版本对比分析
async function compareVersions(
  assetId: string,
  version1: number,
  version2: number
): Promise<VersionComparison> {
  const v1 = await getVersion(assetId, version1);
  const v2 = await getVersion(assetId, version2);
  
  return {
    assetId,
    version1: v1.version_number,
    version2: v2.version_number,
    differences: {
      npvChange: v2.npv_total - v1.npv_total,
      npvChangePercent: ((v2.npv_total - v1.npv_total) / v1.npv_total) * 100,
      monthlyDeltaChange: v2.monthly_asset_delta - v1.monthly_asset_delta,
      projectionChanges: compareProjections(v1, v2)
    },
    impact: calculateImpact(v1, v2)
  };
}
```

### 2. 趋势分析

#### 历史趋势分析
```typescript
// 历史趋势分析
async function analyzeHistoricalTrend(
  assetId: string,
  period: '1y' | '3y' | '5y'
): Promise<TrendAnalysis> {
  const versions = await getHistoricalVersions(assetId, period);
  
  return {
    assetId,
    period,
    trend: {
      npvTrend: calculateTrend(versions.map(v => v.npv_total)),
      monthlyDeltaTrend: calculateTrend(versions.map(v => v.monthly_asset_delta)),
      volatility: calculateVolatility(versions.map(v => v.npv_total))
    },
    insights: generateInsights(versions)
  };
}
```

## 🔍 审计和合规

### 1. 审计日志

#### 操作审计
```sql
-- 审计日志表
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID REFERENCES users(user_id),
    action_type VARCHAR(50) NOT NULL, -- create/update/delete/archive
    resource_type VARCHAR(50) NOT NULL, -- asset/capability/value_assessment
    resource_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    change_reason TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. 合规报告

#### 数据合规检查
```typescript
// 数据合规检查
async function checkDataCompliance(tenantId: string): Promise<ComplianceReport> {
  const issues = [];
  
  // 1. 检查数据完整性
  const incompleteData = await checkDataIntegrity(tenantId);
  if (incompleteData.length > 0) {
    issues.push({
      type: 'data_integrity',
      count: incompleteData.length,
      description: '存在不完整的数据记录'
    });
  }
  
  // 2. 检查版本控制
  const versionIssues = await checkVersionControl(tenantId);
  if (versionIssues.length > 0) {
    issues.push({
      type: 'version_control',
      count: versionIssues.length,
      description: '版本控制存在问题'
    });
  }
  
  // 3. 检查归档完整性
  const archiveIssues = await checkArchiveIntegrity(tenantId);
  if (archiveIssues.length > 0) {
    issues.push({
      type: 'archive_integrity',
      count: archiveIssues.length,
      description: '归档数据存在问题'
    });
  }
  
  return {
    tenantId,
    checkDate: new Date(),
    issues,
    complianceScore: calculateComplianceScore(issues)
  };
}
```

## 🚀 实施计划

### 阶段1：版本控制基础（Week 1-2）
1. **版本表设计**：创建版本控制表结构
2. **版本管理API**：实现版本创建、查询、对比功能
3. **历史记录**：实现变更历史记录

### 阶段2：归档策略（Week 3-4）
1. **归档规则**：实现自动归档和手动归档
2. **冷存储**：实现归档数据存储
3. **归档查询**：实现归档数据查询

### 阶段3：分析功能（Week 5-6）
1. **版本对比**：实现版本差异分析
2. **趋势分析**：实现历史趋势分析
3. **审计功能**：实现审计日志和合规检查

---

**本设计确保数据版本控制和历史归档的完整性，支持审计合规和数据分析需求。**





