# 测试计划文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P1 - 重要文档**

**文档目的**: 提供数据导入功能的完整测试计划，供Lovable在实施时参考

---

## 📋 目录

1. [单元测试用例](#1-单元测试用例)
2. [集成测试用例](#2-集成测试用例)
3. [性能测试用例](#3-性能测试用例)
4. [测试数据准备](#4-测试数据准备)
5. [测试环境配置](#5-测试环境配置)

---

## 1. 单元测试用例

### 1.1 头行识别算法测试

```python
# Python单元测试（FastAPI端）
import unittest
import pandas as pd
from src.services.data_enhancement.document_header_matcher import HeaderLineIdentifier

class TestHeaderLineIdentifier(unittest.TestCase):
    """头行识别算法单元测试"""
    
    def test_standard_format(self):
        """测试标准格式（格式1：重复表头）"""
        # 测试数据
        data = {
            '订单号': ['SO001', None, None, 'SO002', None, None],
            '客户名称': ['客户A', None, None, '客户B', None, None],
            '订单日期': ['2025-01-20', None, None, '2025-01-21', None, None],
            'SKU代码': [None, 'P001', 'P002', None, 'P003', 'P004'],
            'SKU名称': [None, '产品1', '产品2', None, '产品3', '产品4'],
            '数量': [None, 10, 5, None, 20, 15],
            '单价': [None, 100, 200, None, 50, 60]
        }
        df = pd.DataFrame(data)
        
        # 执行识别
        identifier = HeaderLineIdentifier('SO')
        result = identifier.identify(df)
        
        # 验证结果
        self.assertEqual(len(result['headers']), 2)
        self.assertEqual(len(result['lines']), 4)
        self.assertEqual(result['headers'][0]['document_no'], 'SO001')
        self.assertEqual(result['lines'][0]['sku_code'], 'P001')
    
    def test_complex_format(self):
        """测试复杂格式（格式2：单表头+前向填充）"""
        # 测试数据
        data = {
            '订单号': ['SO001', 'SO001', 'SO001', 'SO002', 'SO002'],
            '客户名称': ['客户A', None, None, '客户B', None],
            '订单日期': ['2025-01-20', None, None, '2025-01-21', None],
            'SKU代码': ['P001', 'P002', 'P003', 'P004', 'P005'],
            '数量': [10, 5, 20, 15, 25],
            '单价': [100, 200, 50, 60, 70]
        }
        df = pd.DataFrame(data)
        
        # 执行识别
        identifier = HeaderLineIdentifier('SO')
        result = identifier.identify(df)
        
        # 验证结果
        self.assertEqual(len(result['headers']), 2)
        self.assertEqual(len(result['lines']), 5)
        self.assertEqual(result['lines'][1]['customer_name'], '客户A')  # 前向填充
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试数据：空数据
        df = pd.DataFrame()
        
        identifier = HeaderLineIdentifier('SO')
        result = identifier.identify(df)
        
        # 验证结果
        self.assertEqual(len(result['headers']), 0)
        self.assertEqual(len(result['lines']), 0)
```

### 1.2 主数据匹配算法测试

```python
# Python单元测试（FastAPI端）
import unittest
from src.services.data_enhancement.master_data_matcher import MasterDataMatcher

class TestMasterDataMatcher(unittest.TestCase):
    """主数据匹配算法单元测试"""
    
    def test_exact_match(self):
        """测试精确匹配（编码）"""
        matcher = MasterDataMatcher()
        
        result = await matcher.match_customer(
            input_name="阿里巴巴",
            input_code="C001",
            tenant_id="tenant-123",
            db_pool=db_pool
        )
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result['confidence'], 1.0)
        self.assertEqual(result['match_type'], 'exact')
    
    def test_fuzzy_match(self):
        """测试模糊匹配（名称）"""
        matcher = MasterDataMatcher()
        
        result = await matcher.match_customer(
            input_name="阿里巴巴集团",
            input_code=None,
            tenant_id="tenant-123",
            db_pool=db_pool
        )
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result['confidence'], 0.8)
        self.assertEqual(result['match_type'], 'fuzzy')
    
    def test_combined_match(self):
        """测试组合匹配（编码+名称）"""
        matcher = MasterDataMatcher()
        
        result = await matcher.match_customer(
            input_name="阿里巴巴",
            input_code="C001",
            tenant_id="tenant-123",
            db_pool=db_pool
        )
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result['confidence'], 0.8)
        self.assertEqual(result['match_type'], 'combined')
```

### 1.3 数据验证算法测试

```python
# Python单元测试（FastAPI端）
import unittest
from src.services.data_enhancement.data_validator import DataValidator

class TestDataValidator(unittest.TestCase):
    """数据验证算法单元测试"""
    
    def test_required_fields(self):
        """测试必填字段验证"""
        validator = DataValidator('SO')
        
        headers = [{
            'order_date': '2025-01-22',
            'customer_name': '客户A',
            # customer_id 缺失
        }]
        
        lines = [{
            'quantity': 10,
            'unit_price': 100,
            # sku_id 缺失
        }]
        
        result = validator.validate(headers, lines)
        
        # 验证结果
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_amount_consistency(self):
        """测试金额一致性验证"""
        validator = DataValidator('SO')
        
        headers = [{
            'order_date': '2025-01-22',
            'customer_id': 'uuid',
            'total_amount': 1000  # 声明总额
        }]
        
        lines = [
            {'quantity': 10, 'unit_price': 100, 'line_amount': 1000},  # 实际总额2000
            {'quantity': 10, 'unit_price': 100, 'line_amount': 1000}
        ]
        
        result = validator.validate(headers, lines)
        
        # 验证结果
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_data_type_validation(self):
        """测试数据类型验证"""
        validator = DataValidator('SO')
        
        headers = [{
            'order_date': 'invalid-date',  # 无效日期
            'customer_id': 'uuid',
            'total_amount': 'not-a-number'  # 无效数字
        }]
        
        result = validator.validate(headers, [])
        
        # 验证结果
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
```

---

## 2. 集成测试用例

### 2.1 TypeScript集成测试（Edge Functions）

```typescript
// Edge Functions集成测试
import { assertEquals, assertExists } from "https://deno.land/std@0.192.0/testing/asserts.ts";

Deno.test("导入销售订单端到端测试", async () => {
  // 1. 上传文件
  const uploadResponse = await fetch("http://localhost:54321/functions/v1/data-import-upload", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "multipart/form-data",
    },
    body: formData,  // 包含测试文件
  });
  
  const uploadResult = await uploadResponse.json();
  assertEquals(uploadResult.success, true);
  assertExists(uploadResult.file_id);
  
  // 2. 识别格式
  const formatResponse = await fetch("http://localhost:54321/functions/v1/data-import-recognize-format", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id: uploadResult.file_id }),
  });
  
  const formatResult = await formatResponse.json();
  assertEquals(formatResult.document_type, "SO");
  assertEquals(formatResult.format_type, "repeated_header");
  
  // 3. 识别头行
  const headerLineResponse = await fetch("http://localhost:54321/functions/v1/data-import-identify-headers", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id: uploadResult.file_id }),
  });
  
  const headerLineResult = await headerLineResponse.json();
  assertEquals(headerLineResult.headers.length, 2);
  assertEquals(headerLineResult.lines.length, 4);
  
  // 4. 匹配主数据
  const matchResponse = await fetch("http://localhost:54321/functions/v1/data-import-match-master", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id: uploadResult.file_id }),
  });
  
  const matchResult = await matchResponse.json();
  assertEquals(matchResult.matches.length, 4);
  
  // 5. 数据验证
  const validateResponse = await fetch("http://localhost:54321/functions/v1/data-import-validate", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id: uploadResult.file_id }),
  });
  
  const validateResult = await validateResponse.json();
  assertEquals(validateResult.is_valid, true);
  
  // 6. 执行导入
  const importResponse = await fetch("http://localhost:54321/functions/v1/data-import-execute", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${testToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ file_id: uploadResult.file_id }),
  });
  
  const importResult = await importResponse.json();
  assertEquals(importResult.success, true);
  
  // 7. 验证数据库
  const { data: orders } = await supabase
    .from('sales_order_headers')
    .select('*, sales_order_lines(*)')
    .eq('order_number', 'SO-20250122-001');
  
  assertEquals(orders.length, 1);
  assertEquals(orders[0].sales_order_lines.length, 2);
});
```

### 2.2 端到端测试场景

```typescript
// 完整导入流程测试
describe('数据导入端到端测试', () => {
  
  it('应该成功导入销售订单', async () => {
    // 1. 上传文件
    const uploadResult = await uploadFile('test-data/sales-order.xlsx');
    expect(uploadResult.success).toBe(true);
    
    // 2. 识别格式
    const formatResult = await recognizeFormat(uploadResult.file_id);
    expect(formatResult.document_type).toBe('SO');
    expect(formatResult.format_type).toBe('repeated_header');
    
    // 3. 识别头行
    const headerLineResult = await identifyHeaders(uploadResult.file_id);
    expect(headerLineResult.headers.length).toBe(2);
    expect(headerLineResult.lines.length).toBe(4);
    
    // 4. 匹配主数据
    const matchResult = await matchMasterData(uploadResult.file_id);
    expect(matchResult.matches.length).toBeGreaterThan(0);
    
    // 5. 数据验证
    const validateResult = await validateData(uploadResult.file_id);
    expect(validateResult.is_valid).toBe(true);
    
    // 6. 执行导入
    const importResult = await executeImport(uploadResult.file_id);
    expect(importResult.success).toBe(true);
    
    // 7. 验证数据库
    const dbResult = await supabase
      .from('sales_order_headers')
      .select('*, sales_order_lines(*)')
      .eq('order_number', 'SO-20250122-001');
    
    expect(dbResult.data.length).toBe(1);
    expect(dbResult.data[0].sales_order_lines.length).toBe(2);
  });
  
  it('应该处理格式2（单表头+前向填充）', async () => {
    // 测试格式2的导入流程
    // ...
  });
  
  it('应该处理主数据匹配失败的情况', async () => {
    // 测试主数据匹配失败时的处理流程
    // ...
  });
  
  it('应该处理数据验证失败的情况', async () => {
    // 测试数据验证失败时的处理流程
    // ...
  });
});
```

---

## 3. 性能测试用例

### 3.1 性能基准测试

```typescript
// 性能测试
describe('性能测试', () => {
  
  it('应该在5秒内处理1000行数据', async () => {
    const startTime = Date.now();
    
    await importDocument(generateTestData(1000));
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(5000);  // 5秒内完成
  });
  
  it('应该在30秒内处理10000行数据', async () => {
    const startTime = Date.now();
    
    await importDocument(generateTestData(10000));
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(30000);  // 30秒内完成
  });
  
  it('应该在60秒内匹配1000条主数据记录', async () => {
    const startTime = Date.now();
    
    await matchMasterData(generateTestMasterData(1000));
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(60000);  // 60秒内完成
  });
});
```

### 3.2 性能基准定义

**Cursor提供的性能基准**:

| 场景 | 数据量 | 目标响应时间 | 吞吐量 |
|------|--------|------------|--------|
| 格式识别 | 10MB Excel | < 5秒 | 2MB/s |
| 头行识别 | 10,000行 | < 10秒 | 1,000行/s |
| 主数据匹配 | 1,000条记录 | < 30秒 | 33条/s |
| 批量插入 | 10,000行 | < 5秒 | 2,000行/s |
| 完整导入流程 | 1,000行 | < 60秒 | - |

---

## 4. 测试数据准备

### 4.1 测试数据生成脚本

```python
# 测试数据生成脚本
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('zh_CN')

def generate_sales_order_data(num_orders: int = 10, lines_per_order: int = 5):
    """生成销售订单测试数据"""
    orders = []
    lines = []
    
    for i in range(num_orders):
        order_no = f"SO-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
        order_date = fake.date_between(start_date='-30d', end_date='today')
        customer_name = fake.company()
        
        orders.append({
            '订单号': order_no,
            '客户名称': customer_name,
            '订单日期': order_date.strftime('%Y-%m-%d'),
            '总金额': 0  # 待计算
        })
        
        total_amount = 0
        for j in range(lines_per_order):
            sku_code = f"SKU-{random.randint(1000, 9999)}"
            sku_name = fake.word()
            quantity = random.randint(1, 100)
            unit_price = round(random.uniform(10, 1000), 2)
            line_amount = quantity * unit_price
            total_amount += line_amount
            
            lines.append({
                '订单号': order_no,
                'SKU代码': sku_code,
                'SKU名称': sku_name,
                '数量': quantity,
                '单价': unit_price,
                '金额': line_amount
            })
        
        # 更新订单总金额
        orders[-1]['总金额'] = round(total_amount, 2)
    
    return pd.DataFrame(orders), pd.DataFrame(lines)

# 生成测试数据
orders_df, lines_df = generate_sales_order_data(100, 5)

# 保存为Excel
with pd.ExcelWriter('test-data/sales-order-1000-rows.xlsx') as writer:
    orders_df.to_excel(writer, sheet_name='Orders', index=False)
    lines_df.to_excel(writer, sheet_name='Lines', index=False)
```

### 4.2 测试文件清单

| 文件名 | 数据量 | 格式 | 用途 |
|--------|--------|------|------|
| `test-data/sales-order-100-rows.xlsx` | 100行 | 格式1 | 单元测试 |
| `test-data/sales-order-1000-rows.xlsx` | 1,000行 | 格式1 | 集成测试 |
| `test-data/sales-order-10000-rows.xlsx` | 10,000行 | 格式1 | 性能测试 |
| `test-data/sales-order-format2.xlsx` | 500行 | 格式2 | 格式测试 |
| `test-data/sales-order-invalid.xlsx` | 100行 | 格式1 | 错误测试 |

---

## 5. 测试环境配置

### 5.1 测试环境要求

**环境变量**:
```bash
# .env.test
FASTAPI_URL=http://localhost:8000
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://user:password@localhost:5432/test_db
REDIS_URL=redis://localhost:6379
```

**测试数据库**:
- 使用独立的测试数据库
- 每次测试前清理数据
- 使用事务回滚（避免数据污染）

### 5.2 测试工具配置

**Deno测试配置**:
```json
// deno.json
{
  "test": {
    "include": ["**/*_test.ts", "**/*.test.ts"],
    "exclude": ["node_modules/**"],
    "files": {
      "allow": ["read", "write", "net"]
    }
  }
}
```

**运行测试**:
```bash
# 运行所有测试
deno test --allow-all

# 运行特定测试文件
deno test --allow-all tests/data-import_test.ts

# 运行性能测试
deno test --allow-all --bench tests/performance_test.ts
```

---

## 6. 测试覆盖率要求

### 6.1 覆盖率目标

| 类型 | 覆盖率目标 | 当前覆盖率 |
|------|-----------|-----------|
| 单元测试 | 80%+ | ⏳ 待测试 |
| 集成测试 | 70%+ | ⏳ 待测试 |
| 端到端测试 | 50%+ | ⏳ 待测试 |

### 6.2 测试报告

**测试报告格式**:
```json
{
  "test_summary": {
    "total_tests": 100,
    "passed": 95,
    "failed": 5,
    "coverage": 85.5
  },
  "test_results": [
    {
      "test_name": "test_standard_format",
      "status": "passed",
      "duration": 150,
      "coverage": 90.0
    }
  ],
  "performance_benchmarks": [
    {
      "test_name": "1000行导入",
      "duration": 4500,
      "target": 5000,
      "status": "passed"
    }
  ]
}
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

