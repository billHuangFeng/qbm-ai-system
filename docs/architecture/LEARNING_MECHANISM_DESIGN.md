# BMOS系统 - "越用越聪明"机制设计文档

## 📋 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-25
- **负责人**: Cursor (系统架构设计)
- **状态**: ✅ 设计完成, 待实施

---

## 1. 核心设计理念

BMOS系统的"越用越聪明"能力建立在以下四个核心机制之上:

### 1.1 反馈闭环 (Feedback Loop)
```
用户行为/管理者反馈 → 数据收集 → 模型更新 → 更准确的预测 → 更好的决策 → 用户满意
                                                           ↑                    ↓
                                                           └──── 循环优化 ────┘
```

### 1.2 误差驱动学习 (Error-Driven Learning)
```
预测 → 收集实际值 → 计算误差 → 分析误差原因 → 调整模型参数 → 提升预测准确性
```

### 1.3 企业记忆系统 (Enterprise Memory)
```
学习模式 → 存储经验 → 检索相似场景 → 应用成功模式 → 提升决策质量
```

### 1.4 自动化优化循环 (Automated Optimization Cycle)
```
定时触发 → 重训练模型 → 性能对比 → 选择最佳模型 → 部署新模型 → 监控效果
```

---

## 2. 数据库设计

### 2.1 管理者评价系统 (`06_manager_evaluation.sql`)

**核心表**:
- `manager_evaluation` - 管理者评价记录
- `metric_adjustment_history` - 指标调整历史
- `data_clarification` - 数据澄清请求
- `model_update_log` - 模型更新日志

**关键字段**:
```sql
manager_evaluation {
    evaluation_type: 'confirm' | 'adjust' | 'reject'  -- 评价类型
    metric_adjustments: JSONB  -- 指标调整记录
    is_applied: BOOLEAN  -- 是否已应用到模型
}

metric_adjustment_history {
    original_value: DECIMAL(15,4)  -- 原始值
    adjusted_value: DECIMAL(15,4)  -- 调整后的值
    adjustment_reason: TEXT  -- 调整原因
    is_applied: BOOLEAN  -- 是否已应用
    application_effect: JSONB  -- 应用效果记录
}
```

### 2.2 企业记忆系统 (`07_enterprise_memory.sql`)

**核心表**:
- `enterprise_memory` - 企业记忆主表
- `memory_application_history` - 记忆应用历史
- `prediction_accuracy_log` - 预测准确度日志
- `model_training_history` - 模型训练历史

**关键字段**:
```sql
enterprise_memory {
    memory_type: 'pattern' | 'strategy' | 'lesson_learned'
    memory_content: JSONB  -- 记忆内容
    confidence_score: DECIMAL(5,4)  -- 置信度
    success_rate: DECIMAL(5,4)  -- 成功率
    applied_count: INTEGER  -- 应用次数
}

prediction_accuracy_log {
    predicted_value: DECIMAL(15,4)
    actual_value: DECIMAL(15,4)
    absolute_error: DECIMAL(15,4)  -- |predicted - actual|
    relative_error: DECIMAL(8,4)  -- |predicted - actual| / actual * 100
    error_causes: JSONB  -- 误差原因分析
}
```

---

## 3. 实现流程设计

### 3.1 管理者评价反馈流程

```typescript
// 1. 管理者提交评价
POST /api/manager-evaluation/submit
{
  analysisId: string,
  evaluationType: 'confirm' | 'adjust' | 'reject',
  evaluationContent: string,
  metricAdjustments: [...]
}

// 2. 系统处理反馈
async function processManagerEvaluation(evaluation) {
  // 2.1 保存评价记录
  await saveEvaluationRecord(evaluation);
  
  // 2.2 如果是指标调整,记录调整历史
  if (evaluation.evaluationType === 'adjust') {
    await saveMetricAdjustments(evaluation.metricAdjustments);
  }
  
  // 2.3 触发模型更新
  if (shouldUpdateModel(evaluation)) {
    await triggerModelUpdate({
      triggerType: 'manager_evaluation',
      evaluationId: evaluation.id,
      updateStrategy: determineUpdateStrategy(evaluation)
    });
  }
}

// 3. 应用反馈到模型
async function applyFeedbackToModel(evaluation) {
  // 3.1 提取调整的指标和原因
  const adjustments = evaluation.metricAdjustments;
  
  // 3.2 分析调整模式
  const patterns = await analyzeAdjustmentPatterns(adjustments);
  
  // 3.3 更新模型参数或权重
  await updateModelParameters({
    adjustments,
    patterns,
    confidenceLevel: calculateConfidenceLevel(evaluation)
  });
  
  // 3.4 记录更新日志
  await logModelUpdate({
    triggerType: 'manager_evaluation',
    evaluationId: evaluation.id,
    updateContent: {...}
  });
}
```

### 3.2 预测误差自动纠正流程

```typescript
// 1. 定时任务: 每月计算预测误差
async function monthlyPredictionErrorCheck() {
  // 1.1 获取上月所有预测
  const lastMonth = getPreviousMonth();
  const predictions = await getPredictions(lastMonth);
  
  // 1.2 获取实际值
  const actuals = await getActualValues(lastMonth);
  
  // 1.3 计算误差
  for (const prediction of predictions) {
    const actual = actuals.find(a => a.matches(prediction));
    if (actual) {
      const error = calculateError(prediction, actual);
      
      // 1.4 保存误差日志
      await savePredictionAccuracyLog({
        prediction_id: prediction.id,
        predicted_value: prediction.value,
        actual_value: actual.value,
        absolute_error: error.absolute,
        relative_error: error.relative,
        error_causes: await analyzeErrorCauses(prediction, actual)
      });
      
      // 1.5 检查是否需要重训练
      if (error.relative > ERROR_THRESHOLD) {
        await triggerModelRetraining({
          triggerType: 'accuracy_threshold',
          prediction_id: prediction.id,
          error_analysis: error
        });
      }
    }
  }
}

// 2. 模型重训练流程
async function retrainModel(trigger) {
  // 2.1 分析误差原因
  const errorAnalysis = await analyzeErrorCauses(trigger);
  
  // 2.2 准备训练数据
  const trainingData = await prepareTrainingData({
    includeRecentErrors: true,
    errorWeighting: calculateErrorWeighting(errorAnalysis)
  });
  
  // 2.3 训练新模型
  const newModel = await trainModel({
    trainingData,
    hyperparameters: optimizeHyperparameters(errorAnalysis),
    features: selectFeatures(errorAnalysis)
  });
  
  // 2.4 对比性能
  const performance = await compareModels(oldModel, newModel);
  
  // 2.5 如果新模型更好,部署它
  if (performance.improvement > MIN_IMPROVEMENT_THRESHOLD) {
    await deployNewModel(newModel);
    await updateModelParameters(newModel.parameters);
  }
  
  // 2.6 记录训练历史
  await saveModelTrainingHistory({
    model_type: newModel.type,
    training_trigger: trigger.triggerType,
    performance_improvement: performance.improvement
  });
}
```

### 3.3 企业记忆应用流程

```typescript
// 1. 记忆提取
async function extractMemoryFromFeedback(feedback) {
  // 1.1 分析反馈内容
  const analysis = await analyzeFeedback(feedback);
  
  // 1.2 提取模式
  const patterns = await extractPatterns(analysis);
  
  // 1.3 形成企业记忆
  for (const pattern of patterns) {
    await saveEnterpriseMemory({
      memory_type: determineMemoryType(pattern),
      memory_content: pattern,
      source_type: 'manager_feedback',
      source_reference_id: feedback.id,
      confidence_score: calculateConfidence(pattern)
    });
  }
}

// 2. 记忆检索与应用
async function applyMemoryToPrediction(context) {
  // 2.1 检索相关记忆
  const memories = await retrieveRelevantMemories(context, {
    minConfidence: 0.7,
    minRelevance: 0.6
  });
  
  // 2.2 应用记忆到预测
  const adjustedPrediction = await adjustPredictionWithMemory({
    basePrediction: context.prediction,
    memories,
    adjustmentStrategy: 'weighted_average'
  });
  
  // 2.3 记录记忆应用
  for (const memory of memories) {
    await saveMemoryApplicationHistory({
      memory_id: memory.id,
      application_context: context.id,
      application_type: 'prediction_adjustment'
    });
  }
  
  return adjustedPrediction;
}

// 3. 记忆效果追踪
async function trackMemoryEffectiveness(memoryId, applicationResult) {
  // 3.1 更新应用历史
  await updateMemoryApplicationHistory({
    memory_id: memoryId,
    was_successful: applicationResult.success,
    impact_score: applicationResult.impact
  });
  
  // 3.2 计算成功率
  const stats = await calculateMemoryStatistics(memoryId);
  
  // 3.3 更新置信度
  await updateMemoryConfidence(memoryId, {
    new_success_rate: stats.successRate,
    applied_count: stats.appliedCount
  });
  
  // 3.4 如果记忆效果不好,降低其优先级
  if (stats.successRate < LOW_SUCCESS_RATE_THRESHOLD) {
    await deprecateMemory(memoryId);
  }
}
```

### 3.4 自动化优化循环

```typescript
// 定时任务: 每月自动重训练
cron.schedule('0 2 1 * *', async () => { // 每月1号凌晨2点
  await executeMonthlyRetraining();
});

async function executeMonthlyRetraining() {
  // 1. 对所有模型类型进行重训练
  const modelTypes = ['shapley', 'timeseries', 'npv', 'capability_value'];
  
  for (const modelType of modelTypes) {
    // 1.1 收集新的训练数据
    const newData = await collectNewTrainingData(modelType);
    
    // 1.2 检查数据质量
    if (await checkDataQuality(newData)) {
      // 1.3 训练新模型
      const newModel = await trainModel(modelType, newData);
      
      // 1.4 性能对比
      const comparison = await compareModelPerformance(oldModel, newModel);
      
      // 1.5 决定是否部署
      if (comparison.improvement > SCHEDULED_IMPROVEMENT_THRESHOLD) {
        await deployModel(newModel);
        
        // 1.6 记录更新日志
        await logModelUpdate({
          triggerType: 'scheduled_retrain',
          modelType,
          performanceImprovement: comparison
        });
      }
    }
  }
  
  // 2. 清理过期数据
  await cleanupOldData();
  
  // 3. 生成月度优化报告
  await generateMonthlyOptimizationReport();
}
```

---

## 4. API设计

### 4.1 管理者评价API

```typescript
// POST /api/manager-evaluation/submit
interface ManagerEvaluationRequest {
  analysisId: string;
  evaluationType: 'confirm' | 'adjust' | 'reject';
  evaluationContent: string;
  metricAdjustments?: Array<{
    metricId: string;
    metricName: string;
    currentValue: number;
    adjustedValue: number;
    adjustmentReason: string;
  }>;
  implementationPlan?: {
    startDate: string;
    duration: number;
    responsiblePerson: string;
    budgetRequired: number;
  };
}

// Response
interface ManagerEvaluationResponse {
  success: boolean;
  evaluationId: string;
  modelUpdateTriggered: boolean;
  estimatedUpdateTime: string;
}
```

### 4.2 模型更新API

```typescript
// POST /api/model/update
interface ModelUpdateRequest {
  modelType: 'shapley' | 'timeseries' | 'npv' | 'capability_value';
  triggerType: 'manual' | 'manager_evaluation' | 'prediction_error' | 'scheduled';
  updateStrategy: 'incremental' | 'full_retrain' | 'parameter_adjustment';
  additionalContext?: JSONB;
}

// Response
interface ModelUpdateResponse {
  success: boolean;
  updateId: string;
  status: 'completed' | 'training' | 'queued';
  estimatedCompletionTime: string;
  performanceProjection?: {
    expectedAccuracyImprovement: number;
    expectedMAEReduction: number;
  };
}
```

### 4.3 企业记忆API

```typescript
// GET /api/enterprise-memory/search
interface MemorySearchRequest {
  context: JSONB; // 当前业务上下文
  memoryType?: 'pattern' | 'strategy' | 'lesson_learned';
  minConfidence?: number;
  minRelevance?: number;
  limit?: number;
}

// Response
interface MemorySearchResponse {
  memories: Array<{
    id: string;
    title: string;
    description: string;
    confidenceScore: number;
    relevanceScore: number;
    successRate: number;
    content: JSONB;
  }>;
}
```

---

## 5. 关键指标监控

### 5.1 模型性能指标
- **预测准确度**: MAE, RMSE, MAPE
- **模型稳定性**: 预测方差, 异常值检测
- **学习效果**: 每月的MAE改善百分比

### 5.2 反馈闭环效率
- **反馈应用率**: 管理者评价被应用的百分比
- **反馈响应时间**: 从反馈提交到模型更新的时间
- **反馈影响度**: 基于反馈的模型更新带来的准确度提升

### 5.3 企业记忆质量
- **记忆置信度分布**: 高置信度记忆的占比
- **记忆应用成功率**: 企业记忆应用的成功率
- **记忆主动发现**: 系统自动发现的记忆数量

---

## 6. 实施优先级

### Phase 1: 数据基础设施 (已完成) ✅
- [x] 创建管理者评价表
- [x] 创建企业记忆表
- [x] 创建预测准确度日志表
- [x] 创建模型更新日志表

### Phase 2: 反馈收集与应用 (Priority: High)
- [ ] 实现管理者评价API
- [ ] 实现反馈触发模型更新逻辑
- [ ] 实现指标调整应用逻辑

### Phase 3: 误差追踪与纠正 (Priority: High)
- [ ] 实现预测误差自动计算
- [ ] 实现误差阈值告警
- [ ] 实现自动重训练触发器

### Phase 4: 企业记忆系统 (Priority: Medium)
- [ ] 实现记忆提取算法
- [ ] 实现记忆检索算法
- [ ] 实现记忆应用逻辑

### Phase 5: 自动化优化 (Priority: Medium)
- [ ] 实现月度自动重训练任务
- [ ] 实现模型性能对比
- [ ] 实现自动化报告生成

---

## 7. 技术栈

### 后端
- **Python**: scikit-learn, XGBoost, LightGBM
- **PostgreSQL**: 数据存储
- **Supabase Edge Functions**: API实现

### 前端
- **React + TypeScript**: 用户界面
- **Recharts**: 可视化

### 部署
- **GitHub Actions**: CI/CD
- **Supabase**: 托管数据库和Edge Functions

---

## 8. 预期效果

### 8.1 预测准确度提升
- **第1个月**: MAE降低5-10%
- **第3个月**: MAE降低15-25%
- **第6个月**: MAE降低30-40%

### 8.2 反馈循环效率
- **反馈应用时间**: 从提交到应用 < 24小时
- **反馈应用率**: > 80%的管理者评价被应用
- **模型更新频率**: 每周至少1次模型更新

### 8.3 企业记忆质量
- **记忆数量**: 每月新增5-10个高质量记忆
- **记忆置信度**: > 80%的记忆置信度 > 0.7
- **记忆应用成功率**: > 70%

---

## 9. 下一步行动

1. **立即**: 实施管理者评价API
2. **本周**: 实现预测误差自动追踪
3. **本月**: 完成企业记忆系统
4. **下月**: 实现自动化优化循环

---

**该设计文档完整描述了BMOS系统"越用越聪明"的完整机制。现在可以开始实施!**



