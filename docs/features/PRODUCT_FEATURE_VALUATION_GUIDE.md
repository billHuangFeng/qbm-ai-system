# 产品特性估值引导功能设计

## 📋 功能概述

产品特性估值引导功能帮助用户按照科学的方法对产品特性进行单独估值，支持三种估值方法，并提供定期更新机制。

## 🎯 核心功能

### 1. 产品特性主数据管理

#### 1.1 特性分类管理
```
功能型特性：解决客户具体功能需求，参数可量化
- 示例：67W快充、除菌功能、续航提升
- 估值方法：内部价差法/外部竞品法

体验型特性：优化使用感受，非参数化但可感知
- 示例：触控灵敏度、噪音控制、AI语音助手
- 估值方法：客户支付意愿法

稀缺型特性：独家或限量供应，具备差异化壁垒
- 示例：独家专利技术、定制外观、限量版
- 估值方法：外部竞品法/客户支付意愿法

服务型特性：配套服务支持，延伸特性价值
- 示例：质保时长、上门安装、技术支持
- 估值方法：客户支付意愿法
```

#### 1.2 特性主数据维护
- **特性清单管理**：创建、编辑、删除产品特性
- **特性分类**：按类型和估值方法分类管理
- **特性描述**：详细描述特性功能和价值
- **数据来源**：明确数据来源和质量要求

### 2. 估值方法引导

#### 2.1 内部价差法引导
```
适用场景：自有产品有清晰的"基础-升级"版本划分

引导步骤：
1. 选择对比版本
   - 基础版：无该特性的版本
   - 升级版：仅差异该特性的版本
   - 确保无其他功能叠加

2. 输入价格数据
   - 基础版售价：2999元
   - 升级版售价：3299元
   - 裸价差：300元

3. 输入成本数据
   - 基础版成本：1800元
   - 升级版成本：1880元
   - 边际成本增量：80元

4. 系统自动计算
   - 初步估值 = 裸价差 - 边际成本增量 = 300 - 80 = 220元
```

#### 2.2 外部竞品法引导
```
适用场景：自有产品无多版本，但竞品有明确的特性单独售卖定价

引导步骤：
1. 选择对标竞品
   - 同品类、同定位的竞品
   - 有明确特性单独售卖的竞品

2. 输入竞品数据
   - 竞品特性价格：499元
   - 竞品特性成本：150元
   - 竞品溢价：349元

3. 输入自身数据
   - 自身特性成本：140元
   - 品牌力差异：5%（比竞品弱5%）

4. 系统自动计算
   - 自有特性估值 = (竞品溢价 × (1 - 品牌力差异)) + 成本优势
   - = (349 × 0.95) + (150 - 140) = 331.55 + 10 = 341.55元
```

#### 2.3 客户支付意愿法引导
```
适用场景：全新特性（无竞品参考）或niche市场产品

引导步骤：
1. 设计调研场景
   - 向目标客户描述特性差异
   - 询问最多愿意为该特性多付多少钱

2. 收集WTP数据
   - 调研样本：1000名客户
   - WTP分布：0-50元(20%), 51-100元(50%), 101-150元(30%)
   - 平均WTP：80元

3. 输入成本数据
   - 特性边际成本：25元

4. 系统自动计算
   - 特性估值 = 客户平均WTP - 边际成本 = 80 - 25 = 55元
```

### 3. 修正系数管理

#### 3.1 协同效应修正
```
修正逻辑：
- 多特性叠加可能产生"1+1>2"的协同效应
- 协同修正系数 = 实际价差 ÷ 单独估值之和
- 示例：特性A(200元) + 特性B(150元) = 实际价差400元
- 协同系数 = 400 ÷ (200+150) = 1.14
- 修正后：特性A = 200×1.14 = 228元，特性B = 150×1.14 = 171元
```

#### 3.2 生命周期修正
```
修正逻辑：
- 特性价值随时间变化
- 导入期：1.2（初期独家性强，溢价高）
- 成长期：1.0（竞品跟进，溢价回归正常）
- 成熟期：0.7（普遍标配，溢价大幅降低）

修正示例：
- 快充特性初步估值：220元
- 导入期修正：220×1.2 = 264元
- 成熟期修正：220×0.7 = 154元
```

### 4. 验证数据管理

#### 4.1 销量验证
```
验证逻辑：
- 升级版销量占比反映客户对特性价值的认可
- 占比高（>60%）：估值合理
- 占比低（<20%）：估值偏高，需重新调研

验证示例：
- 快充特性估值：220元
- 升级版销量占比：60%
- 结论：估值合理，客户认可该特性价值
```

#### 4.2 客户反馈验证
```
验证逻辑：
- 客户反馈评分反映特性实际价值
- 评分高（>80分）：特性价值得到认可
- 评分低（<60分）：特性价值需要优化

验证示例：
- AI语音助手估值：66元
- 客户反馈评分：85分
- 结论：特性价值得到客户认可
```

## 🔧 技术实现

### 1. 数据库设计

#### 1.1 产品特性主数据表
```sql
CREATE TABLE dim_product_feature_master (
    feature_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    feature_code VARCHAR(50) UNIQUE NOT NULL,
    feature_name VARCHAR(200) NOT NULL,
    feature_type VARCHAR(20) NOT NULL,
    feature_description TEXT,
    valuation_method VARCHAR(30) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL
);
```

#### 1.2 产品特性估值表
```sql
CREATE TABLE fact_product_feature_valuation (
    valuation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    feature_id UUID NOT NULL,
    product_id UUID NOT NULL,
    valuation_date DATE NOT NULL,
    valuation_method VARCHAR(30) NOT NULL,
    
    -- 内部价差法数据
    base_version_price DECIMAL(15,2),
    feature_version_price DECIMAL(15,2),
    base_version_cost DECIMAL(15,2),
    feature_version_cost DECIMAL(15,2),
    
    -- 外部竞品法数据
    competitor_feature_price DECIMAL(15,2),
    competitor_feature_cost DECIMAL(15,2),
    brand_power_difference DECIMAL(5,2),
    
    -- 客户支付意愿法数据
    customer_wtp DECIMAL(15,2),
    customer_wtp_distribution JSONB,
    
    -- 修正系数
    synergy_coefficient DECIMAL(5,4) DEFAULT 1.0000,
    lifecycle_coefficient DECIMAL(5,4) DEFAULT 1.0000,
    
    -- 计算结果
    preliminary_valuation DECIMAL(15,2),
    final_valuation DECIMAL(15,2),
    
    -- 验证数据
    sales_ratio DECIMAL(5,4),
    customer_feedback DECIMAL(5,2),
    
    -- 版本控制
    version_number INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID NOT NULL,
    updated_by UUID NOT NULL
);
```

### 2. API设计

#### 2.1 特性主数据API
```typescript
// 获取特性清单
GET /api/features
Query: { tenantId, featureType?, isActive? }

// 创建特性
POST /api/features
Body: { featureName, featureType, valuationMethod, description }

// 更新特性
PUT /api/features/:featureId
Body: { featureName, featureType, valuationMethod, description }

// 删除特性
DELETE /api/features/:featureId
```

#### 2.2 特性估值API
```typescript
// 获取特性估值
GET /api/features/:featureId/valuations
Query: { productId?, valuationDate?, isCurrent? }

// 创建特性估值
POST /api/features/:featureId/valuations
Body: { productId, valuationMethod, valuationData, correctionFactors }

// 更新特性估值
PUT /api/features/:featureId/valuations/:valuationId
Body: { valuationData, correctionFactors }

// 计算特性估值
POST /api/features/:featureId/valuations/calculate
Body: { valuationMethod, inputData }
```

### 3. 前端界面设计

#### 3.1 特性管理界面
```
特性清单页面：
- 特性列表（表格形式）
- 筛选器（按类型、估值方法筛选）
- 操作按钮（新增、编辑、删除、估值）

特性详情页面：
- 基本信息（名称、类型、描述）
- 估值方法配置
- 估值历史记录
- 验证数据展示
```

#### 3.2 估值引导界面
```
估值方法选择：
- 内部价差法（适用于有版本差异的产品）
- 外部竞品法（适用于有竞品参考的特性）
- 客户支付意愿法（适用于全新特性）

数据输入表单：
- 根据选择的估值方法显示对应的输入字段
- 实时计算初步估值
- 修正系数设置
- 验证数据输入
```

## 📊 使用流程

### 1. 特性创建流程
```
1. 进入特性管理页面
2. 点击"新增特性"
3. 填写特性基本信息
4. 选择特性类型和估值方法
5. 保存特性
```

### 2. 特性估值流程
```
1. 选择要估值的特性
2. 选择估值方法
3. 根据引导填写数据
4. 设置修正系数
5. 输入验证数据
6. 系统自动计算估值
7. 保存估值结果
```

### 3. 定期更新流程
```
1. 系统提醒更新（每月/每季度）
2. 检查验证数据变化
3. 调整修正系数
4. 重新计算估值
5. 更新估值记录
6. 生成更新报告
```

## 🚀 实施计划

### 阶段1：基础功能（Week 1-2）
1. **特性主数据管理**：实现特性的CRUD操作
2. **估值方法引导**：实现三种估值方法的引导界面
3. **基础计算**：实现初步估值计算

### 阶段2：高级功能（Week 3-4）
1. **修正系数管理**：实现协同效应和生命周期修正
2. **验证数据管理**：实现销量和客户反馈验证
3. **版本控制**：实现估值历史版本管理

### 阶段3：优化功能（Week 5-6）
1. **定期更新提醒**：实现自动提醒和更新机制
2. **数据分析**：实现估值趋势分析
3. **报告生成**：实现估值报告自动生成

---

**本功能设计确保产品特性估值的科学性和准确性，为用户提供完整的估值引导和定期更新机制。**
