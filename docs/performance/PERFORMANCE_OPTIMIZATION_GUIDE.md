# 边际影响分析系统 - 性能优化指导文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (性能优化设计)
- **实施方**: Lovable (性能优化实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 性能优化概述

### 1.1 性能目标
- **响应时间**: API响应时间 < 2秒
- **并发处理**: 支持100个并发用户
- **数据处理**: 10万条记录处理时间 < 5分钟
- **内存使用**: 峰值内存使用 < 2GB
- **CPU使用**: 平均CPU使用率 < 70%

### 1.2 性能瓶颈分析
```
数据导入 → 数据清洗 → 算法计算 → 结果存储 → 响应返回
    ↓         ↓         ↓         ↓         ↓
  文件解析   数据验证   边际分析   数据库写入   JSON序列化
   (I/O)    (CPU)     (CPU)     (I/O)     (CPU)
```

---

## 2. 数据库性能优化

### 2.1 索引优化策略

#### 2.1.1 核心表索引设计
```sql
-- 原始数据表索引
CREATE INDEX idx_raw_data_staging_date ON raw_data_staging(created_at);
CREATE INDEX idx_raw_data_staging_source ON raw_data_staging(source_system);
CREATE INDEX idx_raw_data_staging_batch ON raw_data_staging(batch_id);

-- 业务事实表索引
CREATE INDEX idx_fact_order_date ON fact_order(order_date);
CREATE INDEX idx_fact_order_customer ON fact_order(customer_id);
CREATE INDEX idx_fact_order_amount ON fact_order(amount);
CREATE INDEX idx_fact_order_composite ON fact_order(order_date, customer_id, amount);

-- 维度表索引
CREATE INDEX idx_dim_customer_name ON dim_customer(customer_name);
CREATE INDEX idx_dim_sku_name ON dim_sku(sku_name);
CREATE INDEX idx_dim_activity_name ON dim_activity(activity_name);
```

#### 2.1.2 复合索引优化
```sql
-- 查询优化复合索引
CREATE INDEX idx_fact_order_analysis ON fact_order(
    order_date, 
    customer_id, 
    amount, 
    business_unit
) WHERE order_date >= '2024-01-01';

-- 分区表索引
CREATE INDEX idx_fact_order_partition ON fact_order(
    order_date, 
    customer_id
) WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

### 2.2 查询优化策略

#### 2.2.1 查询重写优化
```sql
-- 原始查询（性能差）
SELECT * FROM fact_order 
WHERE order_date >= '2024-01-01' 
  AND customer_id IN (SELECT customer_id FROM dim_customer WHERE customer_name LIKE '%客户%');

-- 优化后查询（性能好）
SELECT fo.* FROM fact_order fo
INNER JOIN dim_customer dc ON fo.customer_id = dc.customer_id
WHERE fo.order_date >= '2024-01-01' 
  AND dc.customer_name LIKE '%客户%';
```

#### 2.2.2 分页查询优化
```sql
-- 使用游标分页（推荐）
SELECT * FROM fact_order 
WHERE order_date >= '2024-01-01' 
  AND order_id > :last_order_id
ORDER BY order_id 
LIMIT 1000;

-- 使用OFFSET分页（不推荐大数据量）
SELECT * FROM fact_order 
WHERE order_date >= '2024-01-01' 
ORDER BY order_id 
LIMIT 1000 OFFSET :offset;
```

### 2.3 数据库连接池优化
```typescript
// 数据库连接池配置
const dbConfig = {
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20, // 最大连接数
  min: 5,  // 最小连接数
  acquireTimeoutMillis: 30000, // 获取连接超时
  idleTimeoutMillis: 30000,    // 空闲连接超时
  connectionTimeoutMillis: 2000, // 连接超时
  pool: {
    max: 20,
    min: 5,
    acquire: 30000,
    idle: 10000
  }
};
```

---

## 3. 算法性能优化

### 3.1 边际分析算法优化

#### 3.1.1 并行计算优化
```typescript
class OptimizedMarginalAnalysis {
  async calculateMarginalAnalysis(data: any[]) {
    // 并行计算不同指标
    const [marginalCost, marginalRevenue, efficiencyMetrics] = await Promise.all([
      this.calculateMarginalCost(data),
      this.calculateMarginalRevenue(data),
      this.calculateEfficiencyMetrics(data)
    ]);

    return {
      marginalCost,
      marginalRevenue,
      efficiencyMetrics
    };
  }

  async calculateMarginalCost(data: any[]) {
    // 使用Web Workers进行并行计算
    const workers = new Array(4).fill(null).map(() => new Worker('./marginal-cost-worker.js'));
    
    const chunkSize = Math.ceil(data.length / workers.length);
    const chunks = this.chunkArray(data, chunkSize);
    
    const results = await Promise.all(
      chunks.map((chunk, index) => 
        this.runWorker(workers[index], chunk)
      )
    );
    
    return this.mergeResults(results);
  }
}
```

#### 3.1.2 缓存优化
```typescript
class CachedMarginalAnalysis {
  private cache = new Map<string, any>();
  private cacheTimeout = 5 * 60 * 1000; // 5分钟缓存

  async calculateMarginalAnalysis(data: any[], options: any) {
    const cacheKey = this.generateCacheKey(data, options);
    
    // 检查缓存
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.result;
      }
    }

    // 计算新结果
    const result = await this.performCalculation(data, options);
    
    // 更新缓存
    this.cache.set(cacheKey, {
      result,
      timestamp: Date.now()
    });

    return result;
  }

  private generateCacheKey(data: any[], options: any): string {
    const dataHash = this.hashData(data);
    const optionsHash = this.hashOptions(options);
    return `${dataHash}_${optionsHash}`;
  }
}
```

### 3.2 协同效应分析优化

#### 3.2.1 矩阵运算优化
```typescript
class OptimizedSynergyAnalysis {
  async calculateSynergyEffects(resources: any[], capabilities: any[]) {
    // 使用TensorFlow.js进行矩阵运算
    const resourceMatrix = tf.tensor2d(resources.map(r => [r.quantity, r.quality]));
    const capabilityMatrix = tf.tensor2d(capabilities.map(c => [c.maturity, c.investment]));
    
    // 并行矩阵运算
    const [interactionMatrix, synergyMatrix] = await Promise.all([
      this.calculateInteractionMatrix(resourceMatrix, capabilityMatrix),
      this.calculateSynergyMatrix(resourceMatrix, capabilityMatrix)
    ]);
    
    // 清理内存
    resourceMatrix.dispose();
    capabilityMatrix.dispose();
    
    return {
      interactionMatrix: await interactionMatrix.data(),
      synergyMatrix: await synergyMatrix.data()
    };
  }
}
```

### 3.3 时间序列分析优化

#### 3.3.1 增量计算优化
```typescript
class IncrementalTimeSeriesAnalysis {
  private previousResults = new Map<string, any>();

  async calculateTimeSeriesAnalysis(data: any[], isIncremental: boolean = false) {
    if (isIncremental && this.previousResults.has('time_series')) {
      const previous = this.previousResults.get('time_series');
      const newData = data.slice(previous.lastIndex);
      
      // 只计算新增数据
      const incrementalResult = await this.calculateIncremental(newData, previous);
      
      // 更新结果
      const updatedResult = this.mergeResults(previous, incrementalResult);
      this.previousResults.set('time_series', updatedResult);
      
      return updatedResult;
    }

    // 全量计算
    const result = await this.calculateFull(data);
    this.previousResults.set('time_series', result);
    
    return result;
  }
}
```

---

## 4. 前端性能优化

### 4.1 组件性能优化

#### 4.1.1 React组件优化
```typescript
// 使用React.memo优化组件渲染
const OptimizedDataTable = React.memo(({ data, columns, onRowClick }) => {
  const memoizedData = useMemo(() => 
    data.map(row => ({ ...row, id: row.id || Math.random() })), 
    [data]
  );

  const memoizedColumns = useMemo(() => columns, [columns]);

  return (
    <Table data={memoizedData} columns={memoizedColumns} onRowClick={onRowClick} />
  );
});

// 使用useCallback优化事件处理
const DataImportComponent = () => {
  const [data, setData] = useState([]);
  
  const handleDataChange = useCallback((newData) => {
    setData(newData);
  }, []);

  const handleFileUpload = useCallback(async (file) => {
    const result = await uploadFile(file);
    handleDataChange(result.data);
  }, [handleDataChange]);

  return (
    <div>
      <FileUploader onUpload={handleFileUpload} />
      <OptimizedDataTable data={data} />
    </div>
  );
};
```

#### 4.1.2 虚拟滚动优化
```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualizedDataTable = ({ data, columns }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <TableRow data={data[index]} columns={columns} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={data.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

### 4.2 数据获取优化

#### 4.2.1 分页加载优化
```typescript
const useInfiniteData = (endpoint: string) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const response = await fetch(`${endpoint}?page=${page}&limit=100`);
      const newData = await response.json();
      
      setData(prev => [...prev, ...newData.data]);
      setPage(prev => prev + 1);
      setHasMore(newData.hasMore);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }, [endpoint, page, loading, hasMore]);

  return { data, loadMore, loading, hasMore };
};
```

#### 4.2.2 缓存优化
```typescript
import { useQuery, useQueryClient } from '@tanstack/react-query';

const useCachedData = (key: string, fetcher: () => Promise<any>) => {
  return useQuery({
    queryKey: [key],
    queryFn: fetcher,
    staleTime: 5 * 60 * 1000, // 5分钟缓存
    cacheTime: 10 * 60 * 1000, // 10分钟缓存
    refetchOnWindowFocus: false
  });
};

// 使用示例
const DataComponent = () => {
  const { data, isLoading } = useCachedData(
    'business-facts',
    () => fetchBusinessFacts()
  );

  if (isLoading) return <LoadingSpinner />;
  
  return <DataTable data={data} />;
};
```

---

## 5. 后端性能优化

### 5.1 API响应优化

#### 5.1.1 响应压缩
```typescript
import compression from 'compression';

app.use(compression({
  level: 6, // 压缩级别
  threshold: 1024, // 最小压缩大小
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));
```

#### 5.1.2 响应缓存
```typescript
import NodeCache from 'node-cache';

const cache = new NodeCache({ stdTTL: 300 }); // 5分钟缓存

const cachedHandler = async (req: Request, res: Response) => {
  const cacheKey = `api_${req.path}_${JSON.stringify(req.query)}`;
  
  // 检查缓存
  const cached = cache.get(cacheKey);
  if (cached) {
    return res.json(cached);
  }

  // 执行实际处理
  const result = await processRequest(req);
  
  // 缓存结果
  cache.set(cacheKey, result);
  
  return res.json(result);
};
```

### 5.2 数据处理优化

#### 5.2.1 流式处理
```typescript
import { Transform } from 'stream';

class DataProcessingStream extends Transform {
  constructor(options = {}) {
    super({ objectMode: true });
    this.batchSize = options.batchSize || 1000;
    this.batch = [];
  }

  _transform(chunk, encoding, callback) {
    this.batch.push(chunk);
    
    if (this.batch.length >= this.batchSize) {
      this.processBatch();
    }
    
    callback();
  }

  _flush(callback) {
    if (this.batch.length > 0) {
      this.processBatch();
    }
    callback();
  }

  async processBatch() {
    const batch = this.batch.splice(0, this.batchSize);
    
    // 并行处理批次
    const results = await Promise.all(
      batch.map(item => this.processItem(item))
    );
    
    results.forEach(result => this.push(result));
  }
}
```

### 5.3 内存优化

#### 5.3.1 内存监控
```typescript
class MemoryMonitor {
  private memoryThreshold = 1024 * 1024 * 1024; // 1GB
  private checkInterval = 30000; // 30秒

  startMonitoring() {
    setInterval(() => {
      const memoryUsage = process.memoryUsage();
      
      if (memoryUsage.heapUsed > this.memoryThreshold) {
        this.handleMemoryPressure();
      }
    }, this.checkInterval);
  }

  private handleMemoryPressure() {
    // 清理缓存
    this.clearCaches();
    
    // 强制垃圾回收
    if (global.gc) {
      global.gc();
    }
    
    // 记录内存压力事件
    console.warn('Memory pressure detected, cleanup performed');
  }
}
```

---

## 6. 系统监控和调优

### 6.1 性能监控

#### 6.1.1 指标收集
```typescript
class PerformanceMonitor {
  private metrics = new Map<string, number[]>();

  recordMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    this.metrics.get(name)!.push(value);
    
    // 保持最近1000个值
    if (this.metrics.get(name)!.length > 1000) {
      this.metrics.get(name)!.shift();
    }
  }

  getMetricStats(name: string) {
    const values = this.metrics.get(name) || [];
    if (values.length === 0) return null;

    const sorted = [...values].sort((a, b) => a - b);
    const len = sorted.length;
    
    return {
      min: sorted[0],
      max: sorted[len - 1],
      avg: values.reduce((a, b) => a + b, 0) / len,
      p50: sorted[Math.floor(len * 0.5)],
      p95: sorted[Math.floor(len * 0.95)],
      p99: sorted[Math.floor(len * 0.99)]
    };
  }
}
```

#### 6.1.2 性能分析
```typescript
class PerformanceProfiler {
  private timers = new Map<string, number>();

  startTimer(name: string) {
    this.timers.set(name, Date.now());
  }

  endTimer(name: string): number {
    const startTime = this.timers.get(name);
    if (!startTime) return 0;

    const duration = Date.now() - startTime;
    this.timers.delete(name);
    
    return duration;
  }

  async profileFunction<T>(name: string, fn: () => Promise<T>): Promise<T> {
    this.startTimer(name);
    try {
      const result = await fn();
      return result;
    } finally {
      const duration = this.endTimer(name);
      console.log(`${name} took ${duration}ms`);
    }
  }
}
```

### 6.2 自动调优

#### 6.2.1 动态配置调整
```typescript
class AutoTuner {
  private config = {
    batchSize: 1000,
    maxConcurrency: 10,
    cacheSize: 100
  };

  async adjustConfiguration() {
    const performance = await this.getPerformanceMetrics();
    
    if (performance.avgResponseTime > 2000) {
      // 响应时间过长，减少批次大小
      this.config.batchSize = Math.max(500, this.config.batchSize - 100);
    }
    
    if (performance.memoryUsage > 0.8) {
      // 内存使用过高，减少并发数
      this.config.maxConcurrency = Math.max(5, this.config.maxConcurrency - 1);
    }
    
    if (performance.cacheHitRate < 0.7) {
      // 缓存命中率低，增加缓存大小
      this.config.cacheSize = Math.min(1000, this.config.cacheSize + 50);
    }
  }
}
```

---

## 7. 部署优化

### 7.1 容器优化

#### 7.1.1 Dockerfile优化
```dockerfile
# 多阶段构建
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime

# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app

# 复制构建产物
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY . .

# 设置用户
USER nextjs

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

EXPOSE 3000

CMD ["npm", "start"]
```

#### 7.1.2 资源限制
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    environment:
      - NODE_ENV=production
      - NODE_OPTIONS=--max-old-space-size=1536
```

### 7.2 负载均衡

#### 7.2.1 Nginx配置
```nginx
upstream app_servers {
    server app1:3000 weight=3;
    server app2:3000 weight=3;
    server app3:3000 weight=2;
}

server {
    listen 80;
    server_name api.qbm-system.com;

    # 启用gzip压缩
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API请求
    location /api/ {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## 8. 总结

本性能优化指导文档提供了全面的性能优化策略，包括：

1. **数据库优化**: 索引设计、查询优化、连接池配置
2. **算法优化**: 并行计算、缓存策略、增量计算
3. **前端优化**: 组件优化、虚拟滚动、数据缓存
4. **后端优化**: 响应压缩、流式处理、内存管理
5. **系统监控**: 性能指标、自动调优、负载均衡
6. **部署优化**: 容器优化、资源限制、负载均衡

所有优化策略都具备具体的实现指导，能够显著提升系统性能。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 2-3周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com


