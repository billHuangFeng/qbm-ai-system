# 性能优化方案（100家企业，1000万条数据/年）

## 📊 数据量级分析

### 系统规模
- **企业数量**：100家企业
- **每家企业数据**：
  - 100个资产 × 12个月 = 1,200条资产记录
  - 100个能力 × 12个月 = 1,200条能力记录
  - 100个产品 × 12个月 = 1,200条产品记录
  - 1,000条/月 × 12个月 = 12,000条业务数据
- **总数据量**：约1,500万条记录/年
- **并发用户**：10个用户同时使用

### 性能要求
- **API响应时间**：<3秒（简单查询），<10秒（复杂分析）
- **页面加载时间**：<2秒（首屏），<5秒（完整页面）
- **数据库查询**：<1秒（单表查询），<5秒（复杂关联查询）
- **并发处理**：支持10个用户同时操作

## 🚀 数据库优化策略

### 1. 分区表设计

#### 按租户分区
```sql
-- 资产累计值表分区
CREATE TABLE asset_accumulation (
    tenant_id UUID NOT NULL,
    asset_id UUID NOT NULL,
    month_date DATE NOT NULL,
    accumulated_value DECIMAL(15,2),
    monthly_delta DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, asset_id, month_date)
) PARTITION BY HASH (tenant_id);

-- 创建4个分区
CREATE TABLE asset_accumulation_p0 PARTITION OF asset_accumulation
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE asset_accumulation_p1 PARTITION OF asset_accumulation
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE asset_accumulation_p2 PARTITION OF asset_accumulation
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE asset_accumulation_p3 PARTITION OF asset_accumulation
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

#### 按时间分区
```sql
-- 收入利润增量表按时间分区
CREATE TABLE revenue_profit_delta (
    delta_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    month_date DATE NOT NULL,
    total_revenue_delta DECIMAL(15,2),
    profit_delta DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (month_date);

-- 按年创建分区
CREATE TABLE revenue_profit_delta_2024 PARTITION OF revenue_profit_delta
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE revenue_profit_delta_2025 PARTITION OF revenue_profit_delta
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### 2. 索引优化

#### 复合索引策略
```sql
-- 租户级查询索引
CREATE INDEX idx_asset_accum_tenant_date ON asset_accumulation(tenant_id, month_date);
CREATE INDEX idx_capability_value_tenant_date ON capability_value_history(tenant_id, month_date);
CREATE INDEX idx_revenue_profit_tenant_date ON revenue_profit_delta(tenant_id, month_date);

-- 业务查询索引
CREATE INDEX idx_asset_master_tenant_category ON core_asset_master(tenant_id, asset_category);
CREATE INDEX idx_capability_master_tenant_category ON core_capability_master(tenant_id, capability_category);

-- 分析查询索引
CREATE INDEX idx_marginal_contrib_tenant_month ON marginal_contribution_cache(tenant_id, calculation_month);
CREATE INDEX idx_model_fit_tenant_function ON model_fit_results(tenant_id, function_name);
```

#### 部分索引
```sql
-- 只对活跃数据建索引
CREATE INDEX idx_active_assets ON core_asset_master(asset_category) 
WHERE current_status = 'active';

-- 只对最近数据建索引
CREATE INDEX idx_recent_accumulation ON asset_accumulation(month_date) 
WHERE month_date >= CURRENT_DATE - INTERVAL '12 months';
```

### 3. 查询优化

#### 分页查询
```sql
-- 资产列表分页查询
SELECT * FROM core_asset_master 
WHERE tenant_id = $1 
ORDER BY created_at DESC 
LIMIT 20 OFFSET $2;

-- 使用游标分页（推荐）
SELECT * FROM core_asset_master 
WHERE tenant_id = $1 AND created_at < $2
ORDER BY created_at DESC 
LIMIT 20;
```

#### 聚合查询优化
```sql
-- 月度汇总查询（使用物化视图）
CREATE MATERIALIZED VIEW mv_monthly_summary AS
SELECT 
    tenant_id,
    month_date,
    SUM(accumulated_value) as total_assets,
    SUM(capability_value) as total_capabilities,
    SUM(profit_delta) as total_profit
FROM (
    SELECT tenant_id, month_date, accumulated_value, 0 as capability_value, 0 as profit_delta
    FROM asset_accumulation
    UNION ALL
    SELECT tenant_id, month_date, 0, capability_value, 0
    FROM capability_value_history
    UNION ALL
    SELECT tenant_id, month_date, 0, 0, profit_delta
    FROM revenue_profit_delta
) combined
GROUP BY tenant_id, month_date;

-- 刷新物化视图
REFRESH MATERIALIZED VIEW mv_monthly_summary;
```

## 🔄 缓存策略

### 1. Redis缓存设计

#### 缓存层级
```
L1: 应用内存缓存（热点数据）
L2: Redis缓存（共享数据）
L3: 数据库（持久化数据）
```

#### 缓存策略
```typescript
// 缓存配置
const cacheConfig = {
  // 资产清单缓存（1小时）
  assetMaster: { ttl: 3600, key: 'asset_master:{tenantId}' },
  
  // 能力清单缓存（1小时）
  capabilityMaster: { ttl: 3600, key: 'capability_master:{tenantId}' },
  
  // 月度汇总缓存（6小时）
  monthlySummary: { ttl: 21600, key: 'monthly_summary:{tenantId}:{month}' },
  
  // 边际贡献缓存（24小时）
  marginalContribution: { ttl: 86400, key: 'marginal_contrib:{tenantId}:{month}' },
  
  // 模型参数缓存（7天）
  modelParameters: { ttl: 604800, key: 'model_params:{functionName}' }
};
```

#### 缓存实现
```typescript
// Redis缓存服务
class CacheService {
  private redis: Redis;
  
  async get<T>(key: string): Promise<T | null> {
    const cached = await this.redis.get(key);
    return cached ? JSON.parse(cached) : null;
  }
  
  async set(key: string, value: any, ttl: number): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }
  
  async invalidate(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}
```

### 2. 应用层缓存

#### 内存缓存
```typescript
// 热点数据内存缓存
class MemoryCache {
  private cache = new Map<string, { value: any; expires: number }>();
  
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item || Date.now() > item.expires) {
      this.cache.delete(key);
      return null;
    }
    return item.value;
  }
  
  set(key: string, value: any, ttl: number): void {
    this.cache.set(key, {
      value,
      expires: Date.now() + ttl * 1000
    });
  }
}
```

## ⚡ 异步处理

### 1. 复杂计算异步化

#### 任务队列
```typescript
// 使用Bull队列处理复杂计算
import Bull from 'bull';

const calculationQueue = new Bull('calculation-queue', {
  redis: { host: 'localhost', port: 6379 }
});

// 添加计算任务
async function addCalculationTask(tenantId: string, month: string) {
  await calculationQueue.add('marginal-contribution', {
    tenantId,
    month,
    type: 'shapley'
  }, {
    delay: 0,
    attempts: 3,
    backoff: 'exponential'
  });
}

// 处理计算任务
calculationQueue.process('marginal-contribution', async (job) => {
  const { tenantId, month } = job.data;
  
  // 执行Shapley计算
  const result = await calculateShapleyValues(tenantId, month);
  
  // 缓存结果
  await cacheService.set(
    `marginal_contrib:${tenantId}:${month}`,
    result,
    86400
  );
  
  return result;
});
```

#### 进度跟踪
```typescript
// 计算进度跟踪
interface CalculationProgress {
  taskId: string;
  tenantId: string;
  month: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  result?: any;
  error?: string;
}

// 进度更新
async function updateProgress(taskId: string, progress: number, status: string) {
  await redis.hset(`progress:${taskId}`, {
    progress: progress.toString(),
    status,
    updatedAt: new Date().toISOString()
  });
}
```

### 2. 数据预计算

#### 定时任务
```typescript
// 每日数据预计算
import cron from 'node-cron';

// 每天凌晨2点执行
cron.schedule('0 2 * * *', async () => {
  console.log('开始每日数据预计算...');
  
  // 获取所有活跃租户
  const tenants = await getActiveTenants();
  
  for (const tenant of tenants) {
    // 预计算月度汇总
    await preCalculateMonthlySummary(tenant.id);
    
    // 预计算边际贡献
    await preCalculateMarginalContribution(tenant.id);
    
    // 预计算模型参数
    await preCalculateModelParameters(tenant.id);
  }
  
  console.log('每日数据预计算完成');
});
```

## 📊 监控和调优

### 1. 性能监控

#### 数据库监控
```sql
-- 慢查询监控
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE mean_time > 1000  -- 超过1秒的查询
ORDER BY mean_time DESC;

-- 索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### 应用监控
```typescript
// API响应时间监控
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} - ${duration}ms`);
    
    // 记录慢请求
    if (duration > 3000) {
      console.warn(`Slow request: ${req.method} ${req.path} - ${duration}ms`);
    }
  });
  
  next();
});
```

### 2. 性能调优

#### 数据库调优
```sql
-- PostgreSQL配置优化
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

#### 应用调优
```typescript
// 连接池配置
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'bmos',
  user: 'bmos_user',
  password: 'password',
  max: 20, // 最大连接数
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

## 🚀 实施计划

### 阶段1：数据库优化（Week 1-2）
1. **分区表创建**：按租户和时间分区
2. **索引优化**：复合索引、部分索引
3. **查询优化**：分页查询、聚合查询

### 阶段2：缓存实现（Week 3-4）
1. **Redis集成**：缓存服务、缓存策略
2. **应用缓存**：内存缓存、缓存失效
3. **缓存监控**：命中率、性能指标

### 阶段3：异步处理（Week 5-6）
1. **任务队列**：复杂计算异步化
2. **预计算**：定时任务、数据预计算
3. **进度跟踪**：任务状态、进度更新

### 阶段4：监控调优（Week 7-8）
1. **性能监控**：数据库、应用监控
2. **性能调优**：配置优化、参数调整
3. **压力测试**：负载测试、性能验证

---

**本性能优化方案确保系统在100家企业、1000万条数据的规模下稳定运行，满足10个并发用户的性能要求。**





