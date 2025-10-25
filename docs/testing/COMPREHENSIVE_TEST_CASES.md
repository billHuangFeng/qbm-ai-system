# 边际影响分析系统 - 综合测试用例设计

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (测试用例设计)
- **实施方**: Lovable (测试实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 测试策略概述

### 1.1 测试金字塔
```
        E2E测试 (10%)
       ┌─────────────┐
      │   用户验收测试   │
     ┌─────────────────┐
    │    集成测试 (20%)   │
   ┌─────────────────────┐
  │     单元测试 (70%)     │
 └─────────────────────────┘
```

### 1.2 测试覆盖率目标
- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 60%
- **关键业务逻辑覆盖率**: ≥ 95%
- **算法模块覆盖率**: ≥ 90%

---

## 2. 单元测试用例

### 2.1 数据导入模块测试

#### 2.1.1 文件格式检测测试
```typescript
describe('DocumentFormatDetector', () => {
  describe('detect_repeated_header', () => {
    it('应该正确识别重复单据头格式', () => {
      const testData = [
        { 单据号: 'DOC001', 客户名称: '客户A', 产品名称: '产品1', 金额: 1000 },
        { 单据号: 'DOC001', 客户名称: '客户A', 产品名称: '产品2', 金额: 500 },
        { 单据号: 'DOC002', 客户名称: '客户B', 产品名称: '产品3', 金额: 800 }
      ];
      
      const detector = new DocumentFormatDetector();
      const result = detector.detect_repeated_header(testData);
      
      expect(result).toBeGreaterThan(0.8);
    });
  });

  describe('detect_first_row_header', () => {
    it('应该正确识别第一行单据头格式', () => {
      const testData = [
        { 单据号: 'DOC001', 客户名称: '客户A', 产品名称: '产品1', 金额: 1000 },
        { 单据号: '', 客户名称: '', 产品名称: '产品2', 金额: 500 },
        { 单据号: '', 客户名称: '', 产品名称: '产品3', 金额: 300 }
      ];
      
      const detector = new DocumentFormatDetector();
      const result = detector.detect_first_row_header(testData);
      
      expect(result).toBeGreaterThan(0.7);
    });
  });

  describe('detect_pure_header', () => {
    it('应该正确识别纯单据头格式', () => {
      const testData = [
        { 单据号: 'DOC001', 单据日期: '2024-01-01', 客户名称: '客户A', 总金额: 1800, 单据类型: '服务费' },
        { 单据号: 'DOC002', 单据日期: '2024-01-02', 客户名称: '客户B', 总金额: 500, 单据类型: '服务费' }
      ];
      
      const detector = new DocumentFormatDetector();
      const result = detector.detect_pure_header(testData);
      
      expect(result).toBeGreaterThan(0.8);
    });
  });
});
```

#### 2.1.2 数据清洗测试
```typescript
describe('DataCleaner', () => {
  describe('clean_missing_values', () => {
    it('应该正确处理缺失值', () => {
      const testData = [
        { 单据号: 'DOC001', 客户名称: '客户A', 金额: 1000 },
        { 单据号: 'DOC002', 客户名称: null, 金额: 500 },
        { 单据号: 'DOC003', 客户名称: '客户C', 金额: null }
      ];
      
      const cleaner = new DataCleaner();
      const result = cleaner.clean_missing_values(testData, 'fill_forward');
      
      expect(result[1].客户名称).toBe('客户A');
      expect(result[2].金额).toBe(500);
    });
  });

  describe('detect_outliers', () => {
    it('应该正确检测异常值', () => {
      const testData = [
        { 金额: 1000 },
        { 金额: 1200 },
        { 金额: 1500 },
        { 金额: 10000 }, // 异常值
        { 金额: 1100 }
      ];
      
      const cleaner = new DataCleaner();
      const outliers = cleaner.detect_outliers(testData, '金额');
      
      expect(outliers).toContain(3); // 索引3是异常值
    });
  });
});
```

#### 2.1.3 数据验证测试
```typescript
describe('DataValidator', () => {
  describe('validate_business_rules', () => {
    it('应该正确验证业务规则', () => {
      const testData = [
        { 单据号: 'DOC001', 金额: 1000, 日期: '2024-01-01' },
        { 单据号: 'DOC002', 金额: -500, 日期: '2024-01-02' }, // 负金额应该被检测
        { 单据号: 'DOC003', 金额: 2000, 日期: 'invalid-date' } // 无效日期
      ];
      
      const validator = new DataValidator();
      const result = validator.validate_business_rules(testData);
      
      expect(result.success).toBe(false);
      expect(result.errors).toContain('金额 存在小于 0 的值');
      expect(result.errors).toContain('日期 格式不正确');
    });
  });

  describe('validate_data_types', () => {
    it('应该正确验证数据类型', () => {
      const testData = [
        { 金额: 1000, 数量: 10 },
        { 金额: 'invalid', 数量: 5 }, // 无效金额
        { 金额: 2000, 数量: 'invalid' } // 无效数量
      ];
      
      const validator = new DataValidator();
      const result = validator.validate_data_types(testData);
      
      expect(result.success).toBe(false);
      expect(result.errors).toContain('金额 包含非数值数据');
      expect(result.errors).toContain('数量 包含非数值数据');
    });
  });
});
```

### 2.2 边际分析算法测试

#### 2.2.1 ΔV-CL信号检测测试
```typescript
describe('DeltaVCLSignalAlgorithm', () => {
  describe('detect_bottleneck_signals', () => {
    it('应该正确检测瓶颈信号', () => {
      const testData = [
        { 日期: '2024-01-01', 效率: 0.85, 成本: 1000, 收入: 1200 },
        { 日期: '2024-01-02', 效率: 0.80, 成本: 1100, 收入: 1150 },
        { 日期: '2024-01-03', 效率: 0.75, 成本: 1200, 收入: 1100 }, // 瓶颈信号
        { 日期: '2024-01-04', 效率: 0.70, 成本: 1300, 收入: 1050 }
      ];
      
      const algorithm = new DeltaVCLSignalAlgorithm();
      const signals = algorithm.detect_bottleneck_signals(testData);
      
      expect(signals).toHaveLength(1);
      expect(signals[0].signal_type).toBe('bottleneck');
      expect(signals[0].severity).toBe('high');
    });
  });

  describe('calculate_marginal_analysis', () => {
    it('应该正确计算边际分析', () => {
      const testData = [
        { 数量: 100, 总成本: 10000, 总收入: 12000 },
        { 数量: 110, 总成本: 10800, 总收入: 13200 },
        { 数量: 120, 总成本: 11600, 总收入: 14400 }
      ];
      
      const algorithm = new DeltaVCLSignalAlgorithm();
      const result = algorithm.calculate_marginal_analysis(testData);
      
      expect(result.marginal_cost).toBe(80); // (11600-10800)/(120-110)
      expect(result.marginal_revenue).toBe(120); // (14400-13200)/(120-110)
      expect(result.marginal_profit).toBe(40); // 120-80
    });
  });
});
```

#### 2.2.2 协同效应分析测试
```typescript
describe('SynergyAnalysis', () => {
  describe('calculate_synergy_effects', () => {
    it('应该正确计算协同效应', () => {
      const testData = {
        resources: [
          { 资源名称: '技术团队', 数量: 10, 质量: 0.85 },
          { 资源名称: '设备', 数量: 5, 质量: 0.90 }
        ],
        capabilities: [
          { 能力名称: '产品开发', 成熟度: 0.80 },
          { 能力名称: '生产制造', 成熟度: 0.75 }
        ]
      };
      
      const analyzer = new SynergyAnalysis();
      const result = analyzer.calculate_synergy_effects(testData);
      
      expect(result.synergy_coefficient).toBeGreaterThan(0);
      expect(result.interaction_strength).toBeGreaterThan(0);
      expect(result.synergy_contribution).toBeGreaterThan(0);
    });
  });
});
```

### 2.3 三大流程管理测试

#### 2.3.1 生产流程效能测试
```typescript
describe('ProductionProcessMonitor', () => {
  describe('calculate_efficiency_metrics', () => {
    it('应该正确计算生产效能指标', () => {
      const testData = [
        { 日期: '2024-01-01', 产量: 1000, 投入成本: 50000, 质量分数: 0.95 },
        { 日期: '2024-01-02', 产量: 1100, 投入成本: 55000, 质量分数: 0.92 },
        { 日期: '2024-01-03', 产量: 1200, 投入成本: 60000, 质量分数: 0.90 }
      ];
      
      const monitor = new ProductionProcessMonitor();
      const result = monitor.calculate_efficiency_metrics(testData);
      
      expect(result.production_efficiency).toBeGreaterThan(0);
      expect(result.quality_efficiency).toBeGreaterThan(0);
      expect(result.cost_efficiency).toBeGreaterThan(0);
    });
  });

  describe('detect_bottlenecks', () => {
    it('应该正确检测生产瓶颈', () => {
      const testData = [
        { 工序: 'A', 产能: 1000, 实际产量: 950 },
        { 工序: 'B', 产能: 800, 实际产量: 800 }, // 瓶颈工序
        { 工序: 'C', 产能: 1200, 实际产量: 800 }
      ];
      
      const monitor = new ProductionProcessMonitor();
      const bottlenecks = monitor.detect_bottlenecks(testData);
      
      expect(bottlenecks).toHaveLength(1);
      expect(bottlenecks[0].工序).toBe('B');
      expect(bottlenecks[0].瓶颈程度).toBeGreaterThan(0.8);
    });
  });
});
```

### 2.4 映射匹配度分析测试

#### 2.4.1 产品特性-客户价值映射测试
```typescript
describe('ProductCustomerMapping', () => {
  describe('calculate_mapping_strength', () => {
    it('应该正确计算映射强度', () => {
      const testData = {
        product_characteristics: [
          { 特性名称: '产品质量', 特性值: 0.85 },
          { 特性名称: '价格', 特性值: 0.70 }
        ],
        customer_values: [
          { 价值名称: '可靠性', 重要性: 0.90 },
          { 价值名称: '性价比', 重要性: 0.80 }
        ]
      };
      
      const mapper = new ProductCustomerMapping();
      const result = mapper.calculate_mapping_strength(testData);
      
      expect(result.mapping_score).toBeGreaterThan(0);
      expect(result.correlation_coefficient).toBeGreaterThan(0);
      expect(result.significance).toBe(true);
    });
  });

  describe('kano_model_analysis', () => {
    it('应该正确进行卡诺模型分析', () => {
      const testData = [
        { 特性: '产品质量', 满意度: 0.9, 不满意度: 0.1 },
        { 特性: '价格', 满意度: 0.6, 不满意度: 0.8 }
      ];
      
      const mapper = new ProductCustomerMapping();
      const result = mapper.kano_model_analysis(testData);
      
      expect(result.categories).toHaveProperty('must_have');
      expect(result.categories).toHaveProperty('one_dimensional');
      expect(result.optimization_priorities).toBeDefined();
    });
  });
});
```

---

## 3. 集成测试用例

### 3.1 数据导入集成测试

#### 3.1.1 完整数据导入流程测试
```typescript
describe('Data Import Integration', () => {
  describe('complete_import_workflow', () => {
    it('应该完成完整的数据导入流程', async () => {
      // 1. 上传文件
      const uploadResponse = await uploadFile('test_data.xlsx');
      expect(uploadResponse.success).toBe(true);
      
      // 2. 检查处理状态
      const statusResponse = await checkProcessingStatus(uploadResponse.batch_id);
      expect(statusResponse.status).toBe('processing');
      
      // 3. 等待处理完成
      await waitForProcessing(uploadResponse.batch_id);
      
      // 4. 获取处理结果
      const resultResponse = await getProcessingResult(uploadResponse.batch_id);
      expect(resultResponse.success).toBe(true);
      expect(resultResponse.data.processed_records).toBeGreaterThan(0);
    });
  });

  describe('error_handling', () => {
    it('应该正确处理导入错误', async () => {
      // 上传无效文件
      const uploadResponse = await uploadFile('invalid_data.xlsx');
      expect(uploadResponse.success).toBe(false);
      expect(uploadResponse.error.code).toBe('VALIDATION_ERROR');
    });
  });
});
```

### 3.2 边际分析集成测试

#### 3.2.1 完整分析流程测试
```typescript
describe('Marginal Analysis Integration', () => {
  describe('complete_analysis_workflow', () => {
    it('应该完成完整的边际分析流程', async () => {
      // 1. 触发ΔV-CL信号检测
      const signalResponse = await detectDeltaVCLSignals({
        analysis_period: { start_date: '2024-01-01', end_date: '2024-12-31' }
      });
      expect(signalResponse.success).toBe(true);
      
      // 2. 计算边际分析
      const analysisResponse = await calculateMarginalAnalysis({
        calculation_type: 'marginal_analysis',
        input_data: testData
      });
      expect(analysisResponse.success).toBe(true);
      
      // 3. 生成优化建议
      const optimizationResponse = await generateOptimizationRecommendations({
        analysis_id: analysisResponse.analysis_id
      });
      expect(optimizationResponse.success).toBe(true);
    });
  });
});
```

### 3.3 决策管理集成测试

#### 3.3.1 决策循环执行测试
```typescript
describe('Decision Management Integration', () => {
  describe('decision_cycle_execution', () => {
    it('应该完成完整的决策循环', async () => {
      // 1. 执行决策循环
      const executionResponse = await executeDecisionCycle({
        trigger_type: 'manual',
        analysis_scope: { business_units: ['销售部', '生产部'] }
      });
      expect(executionResponse.success).toBe(true);
      
      // 2. 等待分析完成
      await waitForAnalysisCompletion(executionResponse.execution_id);
      
      // 3. 提交管理者评价
      const evaluationResponse = await submitManagerEvaluation({
        analysis_id: executionResponse.analysis_id,
        evaluation_type: 'confirm',
        evaluation_content: '同意系统分析结果'
      });
      expect(evaluationResponse.success).toBe(true);
    });
  });
});
```

---

## 4. 端到端测试用例

### 4.1 用户场景测试

#### 4.1.1 数据导入到分析完成场景
```typescript
describe('E2E: Data Import to Analysis', () => {
  it('用户应该能够从数据导入到分析完成', async () => {
    // 1. 用户登录
    await login('admin@company.com', 'password');
    
    // 2. 上传数据文件
    await uploadDataFile('business_data_2024.xlsx');
    
    // 3. 配置导入选项
    await configureImportOptions({
      auto_detect_format: true,
      supplement_missing_data: true
    });
    
    // 4. 开始导入
    await startImport();
    
    // 5. 等待导入完成
    await waitForImportCompletion();
    
    // 6. 查看导入结果
    const importResult = await getImportResult();
    expect(importResult.success).toBe(true);
    
    // 7. 开始边际分析
    await startMarginalAnalysis();
    
    // 8. 等待分析完成
    await waitForAnalysisCompletion();
    
    // 9. 查看分析结果
    const analysisResult = await getAnalysisResult();
    expect(analysisResult.signals_detected).toBeGreaterThan(0);
    
    // 10. 查看优化建议
    const recommendations = await getOptimizationRecommendations();
    expect(recommendations.length).toBeGreaterThan(0);
  });
});
```

#### 4.1.2 管理者评价确认场景
```typescript
describe('E2E: Manager Evaluation', () => {
  it('管理者应该能够评价和确认分析结果', async () => {
    // 1. 管理者登录
    await login('manager@company.com', 'password');
    
    // 2. 查看待评价的分析结果
    const pendingEvaluations = await getPendingEvaluations();
    expect(pendingEvaluations.length).toBeGreaterThan(0);
    
    // 3. 查看分析详情
    const analysisDetails = await getAnalysisDetails(pendingEvaluations[0].analysis_id);
    expect(analysisDetails.signals).toBeDefined();
    
    // 4. 调整指标
    await adjustMetrics({
      metric_id: 'efficiency_score',
      adjusted_value: 0.90,
      adjustment_reason: '基于实际运营情况'
    });
    
    // 5. 提交评价
    await submitEvaluation({
      evaluation_type: 'confirm',
      evaluation_content: '同意系统分析结果，建议立即实施',
      metric_adjustments: [{
        metric_id: 'efficiency_score',
        adjusted_value: 0.90
      }]
    });
    
    // 6. 确认提交成功
    const confirmation = await getEvaluationConfirmation();
    expect(confirmation.status).toBe('confirmed');
  });
});
```

### 4.2 性能测试

#### 4.2.1 大数据量处理测试
```typescript
describe('Performance: Large Dataset', () => {
  it('应该能够处理大数据量', async () => {
    const largeDataset = generateLargeDataset(100000); // 10万条记录
    
    const startTime = Date.now();
    
    // 上传大数据集
    const uploadResponse = await uploadLargeDataset(largeDataset);
    expect(uploadResponse.success).toBe(true);
    
    // 等待处理完成
    await waitForProcessing(uploadResponse.batch_id);
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    // 处理时间应该在合理范围内（例如5分钟内）
    expect(processingTime).toBeLessThan(300000);
    
    // 检查处理结果
    const result = await getProcessingResult(uploadResponse.batch_id);
    expect(result.success).toBe(true);
    expect(result.data.processed_records).toBe(100000);
  });
});
```

#### 4.2.2 并发处理测试
```typescript
describe('Performance: Concurrent Processing', () => {
  it('应该能够处理并发请求', async () => {
    const concurrentRequests = Array.from({ length: 10 }, (_, i) => 
      uploadFile(`test_data_${i}.xlsx`)
    );
    
    const startTime = Date.now();
    
    // 并发上传10个文件
    const responses = await Promise.all(concurrentRequests);
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // 所有请求都应该成功
    responses.forEach(response => {
      expect(response.success).toBe(true);
    });
    
    // 总处理时间应该在合理范围内
    expect(totalTime).toBeLessThan(60000); // 1分钟内
  });
});
```

---

## 5. 安全测试用例

### 5.1 认证授权测试
```typescript
describe('Security: Authentication', () => {
  describe('valid_authentication', () => {
    it('有效用户应该能够访问系统', async () => {
      const token = await authenticate('valid@company.com', 'password');
      expect(token).toBeDefined();
      
      const response = await makeAuthenticatedRequest('/api/data-import/upload', token);
      expect(response.success).toBe(true);
    });
  });

  describe('invalid_authentication', () => {
    it('无效用户应该被拒绝访问', async () => {
      const response = await makeRequest('/api/data-import/upload', 'invalid_token');
      expect(response.success).toBe(false);
      expect(response.error.code).toBe('AUTHENTICATION_ERROR');
    });
  });
});
```

### 5.2 数据安全测试
```typescript
describe('Security: Data Protection', () => {
  describe('data_encryption', () => {
    it('敏感数据应该被加密存储', async () => {
      const sensitiveData = { customer_name: '客户A', amount: 10000 };
      
      const response = await uploadSensitiveData(sensitiveData);
      expect(response.success).toBe(true);
      
      // 检查数据库中数据是否加密
      const storedData = await getStoredData(response.data_id);
      expect(storedData.customer_name).not.toBe('客户A'); // 应该是加密后的值
    });
  });
});
```

---

## 6. 测试数据管理

### 6.1 测试数据生成
```typescript
class TestDataGenerator {
  generateDocumentData(count: number, format: string) {
    const data = [];
    for (let i = 0; i < count; i++) {
      data.push({
        document_id: `DOC${String(i + 1).padStart(3, '0')}`,
        document_date: '2024-01-01',
        customer_name: `客户${i + 1}`,
        amount: Math.random() * 10000 + 1000
      });
    }
    return data;
  }

  generateMarginalAnalysisData() {
    return {
      cost_data: [
        { period: '2024-01', total_cost: 100000, variable_cost: 60000 },
        { period: '2024-02', total_cost: 110000, variable_cost: 65000 }
      ],
      revenue_data: [
        { period: '2024-01', total_revenue: 150000, quantity: 1500 },
        { period: '2024-02', total_revenue: 160000, quantity: 1600 }
      ]
    };
  }
}
```

### 6.2 测试环境配置
```typescript
const testConfig = {
  database: {
    host: 'localhost',
    port: 5432,
    database: 'qbm_test',
    username: 'test_user',
    password: 'test_password'
  },
  redis: {
    host: 'localhost',
    port: 6379,
    database: 1
  },
  api: {
    base_url: 'http://localhost:3000/api',
    timeout: 30000
  }
};
```

---

## 7. 测试自动化

### 7.1 持续集成配置
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run unit tests
      run: npm run test:unit
      
    - name: Run integration tests
      run: npm run test:integration
      
    - name: Run E2E tests
      run: npm run test:e2e
      
    - name: Generate coverage report
      run: npm run test:coverage
```

### 7.2 测试报告
```typescript
// 测试报告生成
const generateTestReport = (testResults) => {
  return {
    summary: {
      total_tests: testResults.length,
      passed: testResults.filter(r => r.status === 'passed').length,
      failed: testResults.filter(r => r.status === 'failed').length,
      coverage: calculateCoverage(testResults)
    },
    details: testResults.map(result => ({
      test_name: result.name,
      status: result.status,
      duration: result.duration,
      error: result.error
    }))
  };
};
```

---

## 8. 总结

本测试用例设计文档提供了完整的测试策略和用例，包括：

1. **单元测试**: 覆盖所有核心模块和算法
2. **集成测试**: 测试模块间的交互
3. **端到端测试**: 测试完整的用户场景
4. **性能测试**: 测试系统性能和并发处理
5. **安全测试**: 测试认证授权和数据安全
6. **测试自动化**: CI/CD集成和自动化测试

所有测试用例都具备完整的实现指导，能够确保系统的质量和可靠性。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 1-2周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com
