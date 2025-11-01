# 边际分析测试用例文档

## 概述

本文档定义了边际分析系统的全面测试用例，包括单元测试、集成测试、端到端测试和性能测试。

## 测试策略

### 测试金字塔
```
        E2E Tests (10%)
      ──────────────────
    Integration (30%)
    ──────────────────────
  Unit Tests (60%)
─────────────────────────
```

### 测试覆盖率目标
- **单元测试**: 90%+
- **集成测试**: 80%+
- **端到端测试**: 70%+
- **整体覆盖率**: 85%+

## 1. 单元测试用例

### 1.1 边际分析算法测试

#### 测试用例: 资产NPV计算
```typescript
describe('Asset NPV Calculation', () => {
  it('should calculate NPV correctly for positive cash flows', () => {
    const asset = {
      acquisitionCost: 1000000,
      discountRate: 0.10,
      annualCashFlow: [120000, 130000, 140000, 150000, 160000]
    };
    
    const npv = calculateAssetNPV(asset);
    
    expect(npv).toBeCloseTo(1350000, 2);
  });

  it('should handle zero cash flows', () => {
    const asset = {
      acquisitionCost: 1000000,
      discountRate: 0.10,
      annualCashFlow: [0, 0, 0, 0, 0]
    };
    
    const npv = calculateAssetNPV(asset);
    
    expect(npv).toBe(-1000000);
  });

  it('should handle negative discount rate', () => {
    const asset = {
      acquisitionCost: 1000000,
      discountRate: -0.05,
      annualCashFlow: [120000, 130000, 140000, 150000, 160000]
    };
    
    expect(() => calculateAssetNPV(asset)).toThrow('Discount rate must be positive');
  });
});
```

#### 测试用例: Shapley值计算
```typescript
describe('Shapley Value Calculation', () => {
  it('should calculate Shapley values correctly', () => {
    const factors = [
      { id: 'A', contribution: 0.6 },
      { id: 'B', contribution: 0.4 }
    ];
    const totalValue = 1000000;
    
    const shapleyValues = calculateShapleyValues(factors, totalValue);
    
    expect(shapleyValues.A).toBeCloseTo(600000, 2);
    expect(shapleyValues.B).toBeCloseTo(400000, 2);
  });

  it('should handle single factor', () => {
    const factors = [{ id: 'A', contribution: 1.0 }];
    const totalValue = 1000000;
    
    const shapleyValues = calculateShapleyValues(factors, totalValue);
    
    expect(shapleyValues.A).toBe(1000000);
  });

  it('should handle empty factors array', () => {
    const factors = [];
    const totalValue = 1000000;
    
    const shapleyValues = calculateShapleyValues(factors, totalValue);
    
    expect(shapleyValues).toEqual({});
  });
});
```

### 1.2 数据验证测试

#### 测试用例: 资产数据验证
```typescript
describe('Asset Data Validation', () => {
  it('should validate required fields', () => {
    const assetData = {
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    const result = validateAssetData(assetData);
    
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('should reject invalid asset type', () => {
    const assetData = {
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'invalid_type',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    const result = validateAssetData(assetData);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Invalid asset type');
  });

  it('should reject negative acquisition cost', () => {
    const assetData = {
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: -1000000,
      useful_life_years: 10
    };
    
    const result = validateAssetData(assetData);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Acquisition cost must be positive');
  });
});
```

### 1.3 数据转换测试

#### 测试用例: Excel数据转换
```typescript
describe('Excel Data Transformation', () => {
  it('should transform Excel data to asset format', () => {
    const excelData = [
      {
        '资产编码': 'ASSET-001',
        '资产名称': '生产设备A',
        '资产类型': 'tangible',
        '购置日期': '2024-01-01',
        '购置成本': 1000000,
        '使用年限': 10
      }
    ];
    
    const transformedData = transformExcelToAssetData(excelData);
    
    expect(transformedData).toHaveLength(1);
    expect(transformedData[0]).toEqual({
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: new Date('2024-01-01'),
      acquisition_cost: 1000000,
      useful_life_years: 10
    });
  });

  it('should handle missing optional fields', () => {
    const excelData = [
      {
        '资产编码': 'ASSET-001',
        '资产名称': '生产设备A',
        '资产类型': 'tangible',
        '购置日期': '2024-01-01',
        '购置成本': 1000000,
        '使用年限': 10
        // 缺少可选字段
      }
    ];
    
    const transformedData = transformExcelToAssetData(excelData);
    
    expect(transformedData[0].residual_value).toBe(0);
    expect(transformedData[0].depreciation_method).toBe('straight_line');
  });
});
```

## 2. 集成测试用例

### 2.1 API集成测试

#### 测试用例: 资产清单API
```typescript
describe('Asset API Integration', () => {
  it('should create asset successfully', async () => {
    const assetData = {
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    const response = await request(app)
      .post('/api/assets')
      .send(assetData)
      .expect(201);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data.asset_code).toBe('ASSET-001');
  });

  it('should retrieve asset list', async () => {
    const response = await request(app)
      .get('/api/assets')
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(Array.isArray(response.body.data.assets)).toBe(true);
  });

  it('should update asset successfully', async () => {
    const assetId = 'asset-uuid';
    const updateData = {
      asset_name: '更新后的设备名称'
    };
    
    const response = await request(app)
      .put(`/api/assets/${assetId}`)
      .send(updateData)
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data.asset_name).toBe('更新后的设备名称');
  });
});
```

#### 测试用例: 计算引擎API
```typescript
describe('Calculation Engine API', () => {
  it('should calculate asset NPV', async () => {
    const calculationData = {
      asset_id: 'asset-uuid',
      discount_rate: 0.10,
      cash_flow_years: 5,
      annual_cash_flow: [120000, 130000, 140000, 150000, 160000]
    };
    
    const response = await request(app)
      .post('/api/calculate/asset-npv')
      .send(calculationData)
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data.npv).toBeCloseTo(1350000, 2);
  });

  it('should calculate capability value', async () => {
    const calculationData = {
      capability_id: 'capability-uuid',
      calculation_method: 'stable_output',
      contribution_percentage: 0.25,
      annual_benefit: 500000
    };
    
    const response = await request(app)
      .post('/api/calculate/capability-value')
      .send(calculationData)
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data.calculated_value).toBe(125000);
  });
});
```

### 2.2 数据库集成测试

#### 测试用例: 数据库操作
```typescript
describe('Database Operations', () => {
  beforeEach(async () => {
    await setupTestDatabase();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
  });

  it('should insert asset data correctly', async () => {
    const assetData = {
      tenant_id: 'test-tenant',
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    const result = await insertAsset(assetData);
    
    expect(result.id).toBeDefined();
    expect(result.asset_code).toBe('ASSET-001');
  });

  it('should enforce RLS policies', async () => {
    const assetData = {
      tenant_id: 'other-tenant',
      asset_code: 'ASSET-001',
      asset_name: '生产设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    // 使用不同租户的用户
    await expect(insertAsset(assetData)).rejects.toThrow('Permission denied');
  });
});
```

## 3. 端到端测试用例

### 3.1 用户流程测试

#### 测试用例: 完整数据导入流程
```typescript
describe('Data Import E2E Flow', () => {
  it('should complete full data import process', async () => {
    // 1. 用户登录
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // 2. 导航到数据导入页面
    await page.goto('/data-import');
    
    // 3. 选择资产清单模板
    await page.click('[data-testid="asset-template"]');
    
    // 4. 上传Excel文件
    const filePath = path.join(__dirname, 'fixtures', 'asset_data.xlsx');
    await page.setInputFiles('[data-testid="file-upload"]', filePath);
    
    // 5. 验证数据预览
    await expect(page.locator('[data-testid="data-preview"]')).toBeVisible();
    await expect(page.locator('[data-testid="row-count"]')).toContainText('10');
    
    // 6. 确认导入
    await page.click('[data-testid="confirm-import"]');
    
    // 7. 验证导入结果
    await expect(page.locator('[data-testid="import-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="imported-count"]')).toContainText('10');
    
    // 8. 验证数据在资产清单中显示
    await page.goto('/assets');
    await expect(page.locator('[data-testid="asset-list"]')).toContainText('ASSET-001');
  });
});
```

#### 测试用例: 边际分析完整流程
```typescript
describe('Marginal Analysis E2E Flow', () => {
  it('should complete marginal analysis workflow', async () => {
    // 1. 准备测试数据
    await setupTestData();
    
    // 2. 导航到边际分析页面
    await page.goto('/marginal-analysis');
    
    // 3. 配置分析参数
    await page.selectOption('[data-testid="target-metric"]', 'revenue');
    await page.selectOption('[data-testid="time-period"]', '2024-01-01');
    await page.selectOption('[data-testid="analysis-method"]', 'shapley');
    
    // 4. 选择分析因素
    await page.check('[data-testid="factor-asset-1"]');
    await page.check('[data-testid="factor-capability-1"]');
    
    // 5. 执行分析
    await page.click('[data-testid="run-analysis"]');
    
    // 6. 等待分析完成
    await expect(page.locator('[data-testid="analysis-progress"]')).toBeVisible();
    await expect(page.locator('[data-testid="analysis-complete"]')).toBeVisible({ timeout: 30000 });
    
    // 7. 验证分析结果
    await expect(page.locator('[data-testid="shapley-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="contribution-chart"]')).toBeVisible();
    
    // 8. 导出分析报告
    await page.click('[data-testid="export-report"]');
    await expect(page.locator('[data-testid="download-link"]')).toBeVisible();
  });
});
```

### 3.2 决策循环测试

#### 测试用例: 决策循环执行
```typescript
describe('Decision Cycle E2E Flow', () => {
  it('should execute decision cycle workflow', async () => {
    // 1. 触发决策循环
    await page.goto('/decision-cycle');
    await page.click('[data-testid="trigger-cycle"]');
    
    // 2. 配置分析范围
    await page.selectOption('[data-testid="business-units"]', 'production');
    await page.selectOption('[data-testid="time-period"]', '2024-Q1');
    
    // 3. 选择分析类型
    await page.check('[data-testid="marginal-analysis"]');
    await page.check('[data-testid="synergy-analysis"]');
    
    // 4. 执行分析
    await page.click('[data-testid="execute-analysis"]');
    
    // 5. 等待分析完成
    await expect(page.locator('[data-testid="analysis-status"]')).toContainText('completed');
    
    // 6. 查看分析结果
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="recommendations"]')).toBeVisible();
    
    // 7. 管理者评价
    await page.click('[data-testid="manager-evaluation"]');
    await page.selectOption('[data-testid="evaluation-type"]', 'confirm');
    await page.fill('[data-testid="evaluation-content"]', '分析结果准确，建议采纳');
    
    // 8. 提交评价
    await page.click('[data-testid="submit-evaluation"]');
    await expect(page.locator('[data-testid="evaluation-success"]')).toBeVisible();
  });
});
```

## 4. 性能测试用例

### 4.1 负载测试

#### 测试用例: API性能测试
```typescript
describe('API Performance Tests', () => {
  it('should handle concurrent asset creation', async () => {
    const concurrentRequests = 100;
    const requests = Array.from({ length: concurrentRequests }, (_, i) => 
      request(app)
        .post('/api/assets')
        .send({
          asset_code: `ASSET-${i}`,
          asset_name: `设备${i}`,
          asset_type: 'tangible',
          acquisition_date: '2024-01-01',
          acquisition_cost: 1000000,
          useful_life_years: 10
        })
    );
    
    const startTime = Date.now();
    const responses = await Promise.all(requests);
    const endTime = Date.now();
    
    const successCount = responses.filter(r => r.status === 201).length;
    const averageResponseTime = (endTime - startTime) / concurrentRequests;
    
    expect(successCount).toBe(concurrentRequests);
    expect(averageResponseTime).toBeLessThan(1000); // 1秒内
  });

  it('should handle large dataset calculation', async () => {
    const largeDataset = generateLargeDataset(10000);
    
    const startTime = Date.now();
    const response = await request(app)
      .post('/api/analysis/shapley-simplified')
      .send({
        target_metric: 'revenue',
        factors: largeDataset,
        time_period: {
          start_date: '2024-01-01',
          end_date: '2024-12-31'
        }
      });
    const endTime = Date.now();
    
    expect(response.status).toBe(200);
    expect(endTime - startTime).toBeLessThan(30000); // 30秒内
  });
});
```

### 4.2 内存测试

#### 测试用例: 内存使用测试
```typescript
describe('Memory Usage Tests', () => {
  it('should not exceed memory limits during large data processing', async () => {
    const initialMemory = process.memoryUsage().heapUsed;
    
    // 处理大量数据
    const largeDataset = generateLargeDataset(100000);
    await processLargeDataset(largeDataset);
    
    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;
    
    expect(memoryIncrease).toBeLessThan(500 * 1024 * 1024); // 500MB
  });
});
```

## 5. 安全测试用例

### 5.1 认证测试

#### 测试用例: 用户认证
```typescript
describe('Authentication Tests', () => {
  it('should require authentication for protected endpoints', async () => {
    const response = await request(app)
      .get('/api/assets')
      .expect(401);
    
    expect(response.body.error).toContain('Unauthorized');
  });

  it('should validate JWT tokens', async () => {
    const invalidToken = 'invalid.jwt.token';
    
    const response = await request(app)
      .get('/api/assets')
      .set('Authorization', `Bearer ${invalidToken}`)
      .expect(401);
    
    expect(response.body.error).toContain('Invalid token');
  });
});
```

### 5.2 授权测试

#### 测试用例: 权限控制
```typescript
describe('Authorization Tests', () => {
  it('should enforce tenant isolation', async () => {
    const userToken = await getTokenForUser('user1@tenant1.com');
    const otherTenantAsset = await createAssetForTenant('tenant2');
    
    const response = await request(app)
      .get(`/api/assets/${otherTenantAsset.id}`)
      .set('Authorization', `Bearer ${userToken}`)
      .expect(404);
    
    expect(response.body.error).toContain('Not found');
  });

  it('should restrict admin functions to admin users', async () => {
    const userToken = await getTokenForUser('user@tenant.com', 'user');
    
    const response = await request(app)
      .delete('/api/assets/asset-id')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(403);
    
    expect(response.body.error).toContain('Insufficient permissions');
  });
});
```

## 6. 数据质量测试用例

### 6.1 数据完整性测试

#### 测试用例: 数据完整性
```typescript
describe('Data Integrity Tests', () => {
  it('should maintain referential integrity', async () => {
    const asset = await createAsset();
    const capability = await createCapability();
    
    // 创建关联关系
    await createAssetCapabilityRelation(asset.id, capability.id);
    
    // 删除资产
    await deleteAsset(asset.id);
    
    // 验证关联关系被正确处理
    const relation = await getAssetCapabilityRelation(asset.id, capability.id);
    expect(relation).toBeNull();
  });

  it('should enforce unique constraints', async () => {
    const assetData = {
      asset_code: 'ASSET-001',
      asset_name: '设备A',
      asset_type: 'tangible',
      acquisition_date: '2024-01-01',
      acquisition_cost: 1000000,
      useful_life_years: 10
    };
    
    // 创建第一个资产
    await createAsset(assetData);
    
    // 尝试创建相同编码的资产
    await expect(createAsset(assetData)).rejects.toThrow('Unique constraint violation');
  });
});
```

### 6.2 数据一致性测试

#### 测试用例: 数据一致性
```typescript
describe('Data Consistency Tests', () => {
  it('should maintain data consistency across transactions', async () => {
    const transaction = await beginTransaction();
    
    try {
      // 创建资产
      const asset = await createAsset(assetData, transaction);
      
      // 创建能力
      const capability = await createCapability(capabilityData, transaction);
      
      // 创建关联
      await createRelation(asset.id, capability.id, transaction);
      
      // 提交事务
      await commitTransaction(transaction);
      
      // 验证所有数据都存在
      const savedAsset = await getAsset(asset.id);
      const savedCapability = await getCapability(capability.id);
      const savedRelation = await getRelation(asset.id, capability.id);
      
      expect(savedAsset).toBeDefined();
      expect(savedCapability).toBeDefined();
      expect(savedRelation).toBeDefined();
    } catch (error) {
      await rollbackTransaction(transaction);
      throw error;
    }
  });
});
```

## 7. 用户体验测试用例

### 7.1 界面响应测试

#### 测试用例: 界面响应性
```typescript
describe('UI Responsiveness Tests', () => {
  it('should load pages within acceptable time', async () => {
    const startTime = Date.now();
    await page.goto('/assets');
    await page.waitForSelector('[data-testid="asset-list"]');
    const endTime = Date.now();
    
    expect(endTime - startTime).toBeLessThan(3000); // 3秒内
  });

  it('should handle large datasets gracefully', async () => {
    await page.goto('/assets');
    
    // 加载大量数据
    await page.click('[data-testid="load-all-assets"]');
    
    // 验证分页功能
    await expect(page.locator('[data-testid="pagination"]')).toBeVisible();
    await expect(page.locator('[data-testid="page-info"]')).toContainText('共');
  });
});
```

### 7.2 错误处理测试

#### 测试用例: 错误处理
```typescript
describe('Error Handling Tests', () => {
  it('should display user-friendly error messages', async () => {
    await page.goto('/assets');
    
    // 尝试创建无效资产
    await page.fill('[data-testid="asset-code"]', '');
    await page.fill('[data-testid="asset-name"]', '');
    await page.click('[data-testid="create-asset"]');
    
    // 验证错误消息
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('请填写必填字段');
  });

  it('should handle network errors gracefully', async () => {
    // 模拟网络错误
    await page.route('**/api/assets', route => route.abort());
    
    await page.goto('/assets');
    
    // 验证错误处理
    await expect(page.locator('[data-testid="error-boundary"]')).toBeVisible();
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });
});
```

## 8. 测试数据管理

### 8.1 测试数据生成
```typescript
class TestDataGenerator {
  generateAssetData(count: number): AssetData[] {
    return Array.from({ length: count }, (_, i) => ({
      asset_code: `ASSET-${i.toString().padStart(3, '0')}`,
      asset_name: `测试设备${i}`,
      asset_type: this.randomChoice(['tangible', 'intangible', 'financial']),
      acquisition_date: this.randomDate(),
      acquisition_cost: this.randomNumber(100000, 10000000),
      useful_life_years: this.randomNumber(1, 20)
    }));
  }

  generateCapabilityData(count: number): CapabilityData[] {
    return Array.from({ length: count }, (_, i) => ({
      capability_code: `CAP-${i.toString().padStart(3, '0')}`,
      capability_name: `测试能力${i}`,
      capability_type: this.randomChoice(['technical', 'business', 'management', 'operational']),
      capability_level: this.randomChoice(['beginner', 'intermediate', 'advanced', 'expert']),
      contribution_percentage: this.randomNumber(0, 1),
      annual_benefit: this.randomNumber(100000, 1000000)
    }));
  }
}
```

### 8.2 测试环境管理
```typescript
class TestEnvironmentManager {
  async setupTestEnvironment(): Promise<void> {
    await this.createTestDatabase();
    await this.seedTestData();
    await this.setupTestUsers();
  }

  async cleanupTestEnvironment(): Promise<void> {
    await this.cleanTestDatabase();
    await this.removeTestFiles();
  }

  async resetTestData(): Promise<void> {
    await this.truncateTables();
    await this.seedTestData();
  }
}
```

## 9. 持续集成测试

### 9.1 CI/CD流水线测试
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:coverage

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - run: npm run test:e2e
```

### 9.2 测试报告生成
```typescript
class TestReporter {
  generateTestReport(results: TestResults): TestReport {
    return {
      summary: {
        total: results.total,
        passed: results.passed,
        failed: results.failed,
        skipped: results.skipped,
        duration: results.duration
      },
      coverage: {
        statements: results.coverage.statements,
        branches: results.coverage.branches,
        functions: results.coverage.functions,
        lines: results.coverage.lines
      },
      failures: results.failures.map(failure => ({
        test: failure.test,
        error: failure.error,
        stack: failure.stack
      })),
      recommendations: this.generateRecommendations(results)
    };
  }
}
```

## 10. 测试最佳实践

### 10.1 测试命名规范
```typescript
// 好的测试命名
describe('Asset NPV Calculation', () => {
  it('should calculate NPV correctly for positive cash flows', () => {});
  it('should handle zero cash flows', () => {});
  it('should throw error for negative discount rate', () => {});
});

// 避免的测试命名
describe('Test', () => {
  it('should work', () => {});
  it('test1', () => {});
});
```

### 10.2 测试数据隔离
```typescript
describe('Asset Management', () => {
  beforeEach(async () => {
    await setupTestData();
  });

  afterEach(async () => {
    await cleanupTestData();
  });

  it('should create asset', async () => {
    // 测试逻辑
  });
});
```

### 10.3 异步测试处理
```typescript
describe('Async Operations', () => {
  it('should handle async operations correctly', async () => {
    const result = await asyncOperation();
    expect(result).toBeDefined();
  });

  it('should timeout for long operations', async () => {
    await expect(longOperation()).rejects.toThrow('Timeout');
  }, 10000);
});
```

