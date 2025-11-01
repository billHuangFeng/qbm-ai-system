# 嵌入式调研页面实时数据同步方案

## 📋 需求概述

嵌入式调研页面收集的数据需要**立即同步**到主系统，确保数据实时性和一致性。

## 🎯 技术方案对比

### 方案A：WebSocket实时同步（推荐）

#### 优势
- **实时性**：毫秒级数据同步
- **双向通信**：支持服务端推送更新
- **连接状态**：可监控连接状态
- **用户体验**：无刷新实时更新

#### 实现架构
```
调研页面 → WebSocket → 主系统 → 数据库
    ↓
实时更新UI
```

#### 技术实现
```typescript
// 调研页面WebSocket客户端
class SurveyWebSocketClient {
  private ws: WebSocket;
  private tenantId: string;
  private surveyId: string;
  
  constructor(tenantId: string, surveyId: string) {
    this.tenantId = tenantId;
    this.surveyId = surveyId;
    this.connect();
  }
  
  private connect(): void {
    this.ws = new WebSocket(`wss://api.bmos.com/survey/ws?tenantId=${this.tenantId}&surveyId=${this.surveyId}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket连接已关闭，尝试重连...');
      setTimeout(() => this.connect(), 3000);
    };
  }
  
  // 发送调研数据
  async sendSurveyData(surveyData: SurveyResponse): Promise<void> {
    const message = {
      type: 'survey_response',
      tenantId: this.tenantId,
      surveyId: this.surveyId,
      data: surveyData,
      timestamp: new Date().toISOString()
    };
    
    this.ws.send(JSON.stringify(message));
  }
  
  // 处理服务端消息
  private handleMessage(data: any): void {
    switch (data.type) {
      case 'sync_success':
        this.showSyncSuccess();
        break;
      case 'sync_error':
        this.showSyncError(data.error);
        break;
      case 'data_updated':
        this.updateUI(data.updatedData);
        break;
    }
  }
}
```

#### 服务端WebSocket处理
```typescript
// WebSocket服务端处理
import { WebSocketServer } from 'ws';
import { Server } from 'http';

class SurveyWebSocketServer {
  private wss: WebSocketServer;
  
  constructor(server: Server) {
    this.wss = new WebSocketServer({ server, path: '/survey/ws' });
    this.setupHandlers();
  }
  
  private setupHandlers(): void {
    this.wss.on('connection', (ws, req) => {
      const url = new URL(req.url!, `http://${req.headers.host}`);
      const tenantId = url.searchParams.get('tenantId');
      const surveyId = url.searchParams.get('surveyId');
      
      // 验证权限
      this.validatePermissions(tenantId, surveyId).then(valid => {
        if (!valid) {
          ws.close(1008, 'Unauthorized');
          return;
        }
        
        // 设置消息处理
        ws.on('message', async (data) => {
          try {
            const message = JSON.parse(data.toString());
            await this.handleSurveyMessage(ws, message);
          } catch (error) {
            ws.send(JSON.stringify({
              type: 'error',
              message: 'Invalid message format'
            }));
          }
        });
      });
    });
  }
  
  private async handleSurveyMessage(ws: WebSocket, message: any): Promise<void> {
    switch (message.type) {
      case 'survey_response':
        await this.processSurveyResponse(message);
        ws.send(JSON.stringify({
          type: 'sync_success',
          message: '数据同步成功'
        }));
        break;
      case 'heartbeat':
        ws.send(JSON.stringify({ type: 'heartbeat_ack' }));
        break;
    }
  }
  
  private async processSurveyResponse(message: any): Promise<void> {
    const { tenantId, surveyId, data } = message;
    
    // 1. 保存调研数据
    await this.saveSurveyResponse(tenantId, surveyId, data);
    
    // 2. 触发数据计算
    await this.triggerDataCalculation(tenantId, surveyId, data);
    
    // 3. 通知相关用户
    await this.notifyRelevantUsers(tenantId, surveyId, data);
  }
}
```

### 方案B：Server-Sent Events (SSE)

#### 优势
- **简单实现**：基于HTTP协议
- **自动重连**：浏览器自动处理重连
- **轻量级**：比WebSocket更轻量

#### 实现架构
```
调研页面 → HTTP POST → 主系统 → 数据库
    ↓
SSE连接 ← 主系统 ← 数据库更新
```

#### 技术实现
```typescript
// 调研页面SSE客户端
class SurveySSEClient {
  private eventSource: EventSource;
  private tenantId: string;
  private surveyId: string;
  
  constructor(tenantId: string, surveyId: string) {
    this.tenantId = tenantId;
    this.surveyId = surveyId;
    this.connect();
  }
  
  private connect(): void {
    this.eventSource = new EventSource(`/api/survey/sse?tenantId=${this.tenantId}&surveyId=${this.surveyId}`);
    
    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.eventSource.onerror = () => {
      console.log('SSE连接错误，尝试重连...');
      setTimeout(() => this.connect(), 3000);
    };
  }
  
  // 发送调研数据
  async sendSurveyData(surveyData: SurveyResponse): Promise<void> {
    const response = await fetch('/api/survey/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tenantId: this.tenantId,
        surveyId: this.surveyId,
        data: surveyData
      })
    });
    
    if (!response.ok) {
      throw new Error('数据提交失败');
    }
  }
}
```

### 方案C：轮询同步（备选）

#### 优势
- **兼容性好**：所有浏览器支持
- **实现简单**：基于HTTP请求
- **容错性强**：网络中断后自动恢复

#### 实现架构
```
调研页面 → HTTP POST → 主系统 → 数据库
    ↓
定时轮询 ← 主系统 ← 数据库更新
```

## 🚀 推荐方案：WebSocket + 数据库触发器

### 1. 完整实现架构

#### 数据流设计
```
调研页面 → WebSocket → 主系统API → 数据库
    ↓
数据库触发器 → 实时计算 → 更新相关表
    ↓
WebSocket推送 → 调研页面UI更新
```

#### 数据库触发器
```sql
-- 调研数据提交触发器
CREATE OR REPLACE FUNCTION trigger_survey_data_sync()
RETURNS TRIGGER AS $$
BEGIN
  -- 1. 更新价值评估表
  IF NEW.value_type = 'intrinsic' THEN
    UPDATE intrinsic_value_assessment 
    SET overall_score = calculate_intrinsic_score(NEW.responses),
        assessment_details = NEW.responses,
        updated_at = NOW()
    WHERE month_date = NEW.assessment_date;
  ELSIF NEW.value_type = 'cognitive' THEN
    UPDATE cognitive_value_assessment 
    SET overall_score = calculate_cognitive_score(NEW.responses),
        assessment_details = NEW.responses,
        updated_at = NOW()
    WHERE month_date = NEW.assessment_date;
  ELSIF NEW.value_type = 'experiential' THEN
    UPDATE experiential_value_assessment 
    SET overall_score = calculate_experiential_score(NEW.responses),
        assessment_details = NEW.responses,
        updated_at = NOW()
    WHERE month_date = NEW.assessment_date;
  END IF;
  
  -- 2. 触发全链路增量计算
  PERFORM calculate_full_chain_delta(NEW.tenant_id, NEW.assessment_date);
  
  -- 3. 通知WebSocket客户端
  PERFORM pg_notify('survey_data_updated', 
    json_build_object(
      'tenantId', NEW.tenant_id,
      'surveyId', NEW.survey_id,
      'valueType', NEW.value_type,
      'timestamp', NOW()
    )::text
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER survey_data_sync_trigger
  AFTER INSERT ON survey_responses
  FOR EACH ROW
  EXECUTE FUNCTION trigger_survey_data_sync();
```

#### 实时计算函数
```sql
-- 全链路增量计算函数
CREATE OR REPLACE FUNCTION calculate_full_chain_delta(
  p_tenant_id UUID,
  p_month_date DATE
) RETURNS VOID AS $$
DECLARE
  v_intrinsic_score DECIMAL(5,4);
  v_cognitive_score DECIMAL(5,4);
  v_experiential_score DECIMAL(5,4);
BEGIN
  -- 1. 获取最新价值评估分数
  SELECT overall_score INTO v_intrinsic_score
  FROM intrinsic_value_assessment 
  WHERE tenant_id = p_tenant_id AND month_date = p_month_date;
  
  SELECT overall_score INTO v_cognitive_score
  FROM cognitive_value_assessment 
  WHERE tenant_id = p_tenant_id AND month_date = p_month_date;
  
  SELECT overall_score INTO v_experiential_score
  FROM experiential_value_assessment 
  WHERE tenant_id = p_tenant_id AND month_date = p_month_date;
  
  -- 2. 计算产品价值增量
  INSERT INTO product_value_delta (
    tenant_id, month_date, value_type, value_score, value_delta
  ) VALUES (
    p_tenant_id, p_month_date, 'intrinsic', v_intrinsic_score, 
    v_intrinsic_score - COALESCE((
      SELECT value_score FROM product_value_delta 
      WHERE tenant_id = p_tenant_id AND value_type = 'intrinsic' 
      ORDER BY month_date DESC LIMIT 1
    ), 0)
  ) ON CONFLICT (tenant_id, month_date, value_type) 
  DO UPDATE SET 
    value_score = EXCLUDED.value_score,
    value_delta = EXCLUDED.value_delta,
    updated_at = NOW();
  
  -- 3. 计算收入利润增量
  PERFORM calculate_revenue_profit_delta(p_tenant_id, p_month_date);
  
END;
$$ LANGUAGE plpgsql;
```

### 2. 前端实时更新

#### 调研页面实时更新
```typescript
// 调研页面实时更新组件
class RealTimeSurveyPage extends React.Component {
  private wsClient: SurveyWebSocketClient;
  private [surveyData, setSurveyData] = useState<SurveyData | null>(null);
  private [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');
  
  componentDidMount() {
    this.wsClient = new SurveyWebSocketClient(this.props.tenantId, this.props.surveyId);
    this.setupEventListeners();
  }
  
  private setupEventListeners(): void {
    this.wsClient.on('sync_success', () => {
      setSyncStatus('success');
      this.showSuccessMessage('数据同步成功');
    });
    
    this.wsClient.on('sync_error', (error) => {
      setSyncStatus('error');
      this.showErrorMessage(`同步失败: ${error.message}`);
    });
    
    this.wsClient.on('data_updated', (updatedData) => {
      setSurveyData(updatedData);
      this.updateUI(updatedData);
    });
  }
  
  // 提交调研数据
  private async submitSurveyData(): Promise<void> {
    setSyncStatus('syncing');
    
    try {
      await this.wsClient.sendSurveyData(this.surveyData);
    } catch (error) {
      setSyncStatus('error');
      this.showErrorMessage('数据提交失败');
    }
  }
  
  // 实时更新UI
  private updateUI(updatedData: any): void {
    // 更新价值评估分数
    this.updateValueScores(updatedData.valueScores);
    
    // 更新边际贡献
    this.updateMarginalContributions(updatedData.marginalContributions);
    
    // 更新趋势图表
    this.updateTrendCharts(updatedData.trendData);
  }
}
```

### 3. 性能优化

#### 数据批量处理
```typescript
// 批量数据处理
class SurveyDataBatcher {
  private batchQueue: SurveyResponse[] = [];
  private batchSize = 10;
  private batchTimeout = 1000; // 1秒
  
  async addSurveyData(data: SurveyResponse): Promise<void> {
    this.batchQueue.push(data);
    
    if (this.batchQueue.length >= this.batchSize) {
      await this.processBatch();
    } else {
      setTimeout(() => this.processBatch(), this.batchTimeout);
    }
  }
  
  private async processBatch(): Promise<void> {
    if (this.batchQueue.length === 0) return;
    
    const batch = this.batchQueue.splice(0, this.batchSize);
    
    try {
      await this.batchProcessSurveyData(batch);
      this.notifyBatchSuccess(batch);
    } catch (error) {
      this.notifyBatchError(batch, error);
    }
  }
}
```

#### 缓存策略
```typescript
// 调研数据缓存
class SurveyDataCache {
  private cache = new Map<string, any>();
  private ttl = 300000; // 5分钟
  
  get(key: string): any {
    const item = this.cache.get(key);
    if (!item || Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    return item.value;
  }
  
  set(key: string, value: any): void {
    this.cache.set(key, {
      value,
      expires: Date.now() + this.ttl
    });
  }
  
  invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}
```

## 📊 监控和诊断

### 1. 实时监控

#### 同步状态监控
```typescript
// 同步状态监控
class SurveySyncMonitor {
  private metrics = {
    totalSubmissions: 0,
    successfulSyncs: 0,
    failedSyncs: 0,
    averageSyncTime: 0,
    lastSyncTime: null
  };
  
  recordSubmission(): void {
    this.metrics.totalSubmissions++;
  }
  
  recordSyncSuccess(syncTime: number): void {
    this.metrics.successfulSyncs++;
    this.metrics.averageSyncTime = 
      (this.metrics.averageSyncTime * (this.metrics.successfulSyncs - 1) + syncTime) / 
      this.metrics.successfulSyncs;
    this.metrics.lastSyncTime = new Date();
  }
  
  recordSyncFailure(): void {
    this.metrics.failedSyncs++;
  }
  
  getHealthStatus(): HealthStatus {
    const successRate = this.metrics.successfulSyncs / this.metrics.totalSubmissions;
    
    return {
      status: successRate > 0.95 ? 'healthy' : 'degraded',
      metrics: this.metrics,
      recommendations: this.generateRecommendations()
    };
  }
}
```

### 2. 错误处理

#### 重试机制
```typescript
// 重试机制
class SurveySyncRetry {
  private maxRetries = 3;
  private retryDelay = 1000; // 1秒
  
  async syncWithRetry(surveyData: SurveyResponse): Promise<void> {
    let attempts = 0;
    
    while (attempts < this.maxRetries) {
      try {
        await this.syncSurveyData(surveyData);
        return; // 成功，退出重试
      } catch (error) {
        attempts++;
        
        if (attempts >= this.maxRetries) {
          throw new Error(`同步失败，已重试${this.maxRetries}次: ${error.message}`);
        }
        
        // 指数退避
        await this.delay(this.retryDelay * Math.pow(2, attempts - 1));
      }
    }
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## 🚀 实施计划

### 阶段1：WebSocket基础（Week 1-2）
1. **WebSocket服务**：实现WebSocket服务器
2. **客户端连接**：实现调研页面WebSocket客户端
3. **基础同步**：实现调研数据实时同步

### 阶段2：数据库触发器（Week 3-4）
1. **触发器实现**：实现数据库触发器
2. **实时计算**：实现全链路增量实时计算
3. **数据一致性**：确保数据一致性

### 阶段3：性能优化（Week 5-6）
1. **批量处理**：实现数据批量处理
2. **缓存策略**：实现数据缓存
3. **监控诊断**：实现同步监控和错误处理

---

**本方案确保嵌入式调研页面数据实时同步到主系统，支持毫秒级数据更新和实时UI反馈。**




