# 嵌入式调研页面设计

## 📋 功能概述

为三类价值评估提供嵌入式调研页面，支持嵌入其他软件或独立发送给用户填写，提高数据采集效率和质量。

## 🎯 三类价值评估页面

### 1. 内在价值评估页面

#### 页面功能
- **需求覆盖率评估**：客户对产品功能的需求满足程度
- **满足深度评估**：功能实现的深度和质量
- **独特性评估**：产品与竞品的差异化程度

#### 页面设计
```html
<!-- 内在价值评估页面 -->
<div class="intrinsic-value-survey">
  <h2>产品内在价值评估</h2>
  
  <!-- 需求覆盖率 -->
  <section class="need-coverage">
    <h3>需求覆盖率评估</h3>
    <p>请评估以下功能对您的重要程度和满足程度：</p>
    <div class="feature-list">
      <div class="feature-item">
        <label>加工精度（±0.001mm）</label>
        <div class="rating">
          <span>重要程度：</span>
          <input type="range" min="1" max="5" value="4" name="importance_1">
          <span>满足程度：</span>
          <input type="range" min="1" max="5" value="3" name="satisfaction_1">
        </div>
      </div>
      <!-- 更多功能项... -->
    </div>
  </section>
  
  <!-- 满足深度 -->
  <section class="satisfaction-depth">
    <h3>满足深度评估</h3>
    <p>请评估产品功能的实现深度：</p>
    <div class="depth-questions">
      <div class="question">
        <label>产品是否超出您的期望？</label>
        <select name="exceeds_expectations">
          <option value="1">远低于期望</option>
          <option value="2">低于期望</option>
          <option value="3">符合期望</option>
          <option value="4">超出期望</option>
          <option value="5">远超期望</option>
        </select>
      </div>
      <!-- 更多深度问题... -->
    </div>
  </section>
  
  <!-- 独特性评估 -->
  <section class="uniqueness">
    <h3>独特性评估</h3>
    <p>请评估产品与竞品的差异化程度：</p>
    <div class="uniqueness-questions">
      <div class="question">
        <label>产品是否有独特优势？</label>
        <select name="unique_advantage">
          <option value="1">无独特优势</option>
          <option value="2">略有优势</option>
          <option value="3">明显优势</option>
          <option value="4">显著优势</option>
          <option value="5">绝对优势</option>
        </select>
      </div>
      <!-- 更多独特性问题... -->
    </div>
  </section>
</div>
```

### 2. 认知价值评估页面

#### 页面功能
- **品牌回忆率**：客户对品牌的记忆和识别
- **支付意愿偏差**：客户愿意支付的价格与产品价值的关系
- **认知偏差**：客户对产品价值的认知与实际情况的偏差

#### 页面设计
```html
<!-- 认知价值评估页面 -->
<div class="cognitive-value-survey">
  <h2>产品认知价值评估</h2>
  
  <!-- 品牌回忆率 -->
  <section class="brand-recall">
    <h3>品牌回忆率评估</h3>
    <div class="recall-questions">
      <div class="question">
        <label>提到"精密加工"时，您首先想到哪个品牌？</label>
        <input type="text" name="first_brand" placeholder="请输入品牌名称">
      </div>
      <div class="question">
        <label>您能说出几个精密加工品牌？</label>
        <input type="number" name="brand_count" min="0" max="10">
      </div>
    </div>
  </section>
  
  <!-- 支付意愿偏差 -->
  <section class="wtp-deviation">
    <h3>支付意愿评估</h3>
    <div class="wtp-questions">
      <div class="question">
        <label>您认为这个产品的合理价格是多少？</label>
        <input type="number" name="reasonable_price" placeholder="请输入价格">
      </div>
      <div class="question">
        <label>您最多愿意为这个产品支付多少？</label>
        <input type="number" name="max_price" placeholder="请输入价格">
      </div>
    </div>
  </section>
  
  <!-- 认知偏差 -->
  <section class="cognitive-bias">
    <h3>认知偏差评估</h3>
    <div class="bias-questions">
      <div class="question">
        <label>您认为这个产品的技术水平如何？</label>
        <select name="tech_level">
          <option value="1">很低</option>
          <option value="2">较低</option>
          <option value="3">一般</option>
          <option value="4">较高</option>
          <option value="5">很高</option>
        </select>
      </div>
      <!-- 更多认知问题... -->
    </div>
  </section>
</div>
```

### 3. 体验价值评估页面

#### 页面功能
- **体验偏差**：实际体验与期望体验的偏差
- **场景满意度**：不同使用场景下的满意度
- **行为转化率**：从首次购买到复购的转化

#### 页面设计
```html
<!-- 体验价值评估页面 -->
<div class="experiential-value-survey">
  <h2>产品体验价值评估</h2>
  
  <!-- 体验偏差 -->
  <section class="experience-bias">
    <h3>体验偏差评估</h3>
    <div class="bias-questions">
      <div class="question">
        <label>产品使用体验与您的期望相比如何？</label>
        <select name="experience_vs_expectation">
          <option value="1">远低于期望</option>
          <option value="2">低于期望</option>
          <option value="3">符合期望</option>
          <option value="4">超出期望</option>
          <option value="5">远超期望</option>
        </select>
      </div>
    </div>
  </section>
  
  <!-- 场景满意度 -->
  <section class="scenario-satisfaction">
    <h3>场景满意度评估</h3>
    <div class="scenario-questions">
      <div class="question">
        <label>在紧急订单场景下，您对产品的满意度如何？</label>
        <select name="urgent_order_satisfaction">
          <option value="1">很不满意</option>
          <option value="2">不满意</option>
          <option value="3">一般</option>
          <option value="4">满意</option>
          <option value="5">很满意</option>
        </select>
      </div>
      <!-- 更多场景问题... -->
    </div>
  </section>
  
  <!-- 行为转化 -->
  <section class="behavior-conversion">
    <h3>行为转化评估</h3>
    <div class="conversion-questions">
      <div class="question">
        <label>您是否会再次购买这个产品？</label>
        <select name="repurchase_intention">
          <option value="1">绝对不会</option>
          <option value="2">可能不会</option>
          <option value="3">不确定</option>
          <option value="4">可能会</option>
          <option value="5">绝对会</option>
        </select>
      </div>
      <div class="question">
        <label>您是否会推荐这个产品给其他人？</label>
        <select name="recommendation_intention">
          <option value="1">绝对不会</option>
          <option value="2">可能不会</option>
          <option value="3">不确定</option>
          <option value="4">可能会</option>
          <option value="5">绝对会</option>
        </select>
      </div>
    </div>
  </section>
</div>
```

## 🔧 技术实现

### 1. 嵌入式页面技术

#### 1.1 独立页面（推荐）
- **技术栈**：React + TypeScript + Tailwind CSS
- **部署**：静态页面，可部署到CDN
- **嵌入方式**：iframe嵌入到其他系统

#### 1.2 组件嵌入
- **技术栈**：React组件
- **嵌入方式**：通过npm包或CDN引入
- **配置**：通过props传递配置信息

### 2. 数据收集和存储

#### 2.1 数据收集
```typescript
// 调研数据接口
interface SurveyResponse {
  surveyId: string;
  tenantId: string;
  productId: string;
  valueType: 'intrinsic' | 'cognitive' | 'experiential';
  responses: Record<string, any>;
  completedAt: Date;
  userId?: string;
}

// 数据提交API
async function submitSurveyResponse(response: SurveyResponse): Promise<void> {
  await fetch('/api/survey/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(response)
  });
}
```

#### 2.2 数据存储
```sql
-- 调研响应表
CREATE TABLE survey_responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id VARCHAR(50) NOT NULL,
    tenant_id UUID NOT NULL,
    product_id UUID NOT NULL,
    value_type VARCHAR(50) NOT NULL,
    responses JSONB NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 调研配置表
CREATE TABLE survey_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    value_type VARCHAR(50) NOT NULL,
    questions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. 部署和集成

#### 3.1 独立部署
```bash
# 构建静态页面
npm run build:survey

# 部署到CDN
aws s3 sync dist/ s3://survey-pages-bucket/
```

#### 3.2 嵌入代码
```html
<!-- 嵌入到其他系统 -->
<iframe 
  src="https://survey-pages.example.com/intrinsic-value?tenantId=T001&productId=P001"
  width="100%" 
  height="600px"
  frameborder="0">
</iframe>
```

#### 3.3 组件嵌入
```typescript
// 在其他React应用中
import { IntrinsicValueSurvey } from '@bmos/survey-components';

function ProductPage() {
  return (
    <IntrinsicValueSurvey
      tenantId="T001"
      productId="P001"
      onComplete={(responses) => {
        console.log('Survey completed:', responses);
      }}
    />
  );
}
```

## 📊 数据质量保证

### 1. 数据验证
- **必填项检查**：确保关键问题已回答
- **数据格式验证**：数值范围、文本长度等
- **逻辑一致性**：相关问题的逻辑关系检查

### 2. 数据清洗
- **异常值处理**：识别和处理异常响应
- **缺失值处理**：合理的数据补全策略
- **重复数据**：识别和处理重复提交

### 3. 数据质量监控
- **完成率监控**：调研完成率统计
- **数据质量评分**：基于多个维度的质量评分
- **异常检测**：自动识别异常响应模式

## 🚀 实施计划

### 阶段1：页面开发（Week 1-2）
1. **页面设计**：三类价值评估页面UI/UX设计
2. **功能开发**：表单验证、数据提交、响应式设计
3. **测试**：页面功能测试、兼容性测试

### 阶段2：数据集成（Week 3-4）
1. **API开发**：调研数据提交和查询API
2. **数据库设计**：调研响应表和配置表
3. **数据验证**：数据质量检查和处理

### 阶段3：部署和集成（Week 5-6）
1. **独立部署**：CDN部署、域名配置
2. **嵌入测试**：iframe嵌入测试、组件嵌入测试
3. **用户培训**：使用说明、最佳实践

---

**本设计确保三类价值评估数据的高质量采集，支持多种嵌入方式，满足不同企业的集成需求。**



