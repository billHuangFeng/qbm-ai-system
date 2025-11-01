# BMOS系统 - PostgreSQL性能优化与扩展方案

## 📋 执行摘要

**当前状态**: PostgreSQL作为MVP主数据库  
**性能目标**: 支持100家企业，1000万条数据/年  
**优化策略**: 渐进式优化，从单机到分布式  
**实施周期**: 6个月分阶段实施

---

## 🎯 一、PostgreSQL性能优化策略

### 1.1 数据库配置优化

#### 基础配置调优
```sql
-- postgresql.conf 关键参数优化
# 内存配置
shared_buffers = 2GB                    # 25% of RAM
effective_cache_size = 6GB              # 75% of RAM
work_mem = 64MB                         # 排序和哈希操作内存
maintenance_work_mem = 512MB            # 维护操作内存

# 连接配置
max_connections = 200                    # 最大连接数
shared_preload_libraries = 'pg_stat_statements'

# 查询优化
random_page_cost = 1.1                  # SSD优化
effective_io_concurrency = 200          # SSD并发
checkpoint_completion_target = 0.9       # 检查点优化
wal_buffers = 16MB                      # WAL缓冲区
```

#### 分区表设计
```sql
-- 按时间分区的事实表
CREATE TABLE fact_order (
    id UUID DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    order_date DATE NOT NULL,
    customer_id UUID,
    amount DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (order_date);

-- 创建月度分区
CREATE TABLE fact_order_2024_01 PARTITION OF fact_order
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE fact_order_2024_02 PARTITION OF fact_order
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 按租户分区的配置表
CREATE TABLE tenant_config (
    tenant_id UUID NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB,
    PRIMARY KEY (tenant_id, config_key)
) PARTITION BY HASH (tenant_id);

-- 创建4个租户分区
CREATE TABLE tenant_config_p0 PARTITION OF tenant_config
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE tenant_config_p1 PARTITION OF tenant_config
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE tenant_config_p2 PARTITION OF tenant_config
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE tenant_config_p3 PARTITION OF tenant_config
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 1.2 索引优化策略

#### 复合索引设计
```sql
-- 业务查询优化索引
CREATE INDEX CONCURRENTLY idx_fact_order_analysis 
ON fact_order (tenant_id, order_date, amount) 
WHERE order_date >= '2024-01-01';

-- 时间序列查询索引
CREATE INDEX CONCURRENTLY idx_fact_order_timeseries
ON fact_order (tenant_id, order_date DESC, created_at DESC);

-- 部分索引优化
CREATE INDEX CONCURRENTLY idx_fact_order_active
ON fact_order (tenant_id, order_date)
WHERE amount > 0;

-- 表达式索引
CREATE INDEX CONCURRENTLY idx_fact_order_month
ON fact_order (tenant_id, EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date));
```

#### 索引维护策略
```sql
-- 自动索引维护函数
CREATE OR REPLACE FUNCTION maintain_indexes()
RETURNS void AS $$
DECLARE
    idx RECORD;
BEGIN
    -- 重建使用率低的索引
    FOR idx IN 
        SELECT schemaname, tablename, indexname
        FROM pg_stat_user_indexes 
        WHERE idx_scan < 100 AND schemaname = 'public'
    LOOP
        EXECUTE format('REINDEX INDEX CONCURRENTLY %I.%I', idx.schemaname, idx.indexname);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定时执行索引维护
SELECT cron.schedule('index-maintenance', '0 2 * * 0', 'SELECT maintain_indexes();');
```

### 1.3 查询优化

#### 查询重写优化
```sql
-- 优化前: N+1查询问题
-- 前端代码
const orders = await db.query('SELECT * FROM fact_order WHERE tenant_id = $1', [tenantId]);
for (const order of orders) {
    const customer = await db.query('SELECT * FROM dim_customer WHERE id = $1', [order.customer_id]);
    order.customer = customer;
}

-- 优化后: JOIN查询
SELECT 
    o.*,
    c.customer_name,
    c.customer_type
FROM fact_order o
LEFT JOIN dim_customer c ON o.customer_id = c.id
WHERE o.tenant_id = $1
ORDER BY o.order_date DESC;
```

#### 物化视图优化
```sql
-- 创建预计算视图
CREATE MATERIALIZED VIEW mv_monthly_summary AS
SELECT 
    tenant_id,
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MAX(amount) as max_amount
FROM fact_order
WHERE order_date >= '2024-01-01'
GROUP BY tenant_id, DATE_TRUNC('month', order_date);

-- 创建索引
CREATE UNIQUE INDEX idx_mv_monthly_summary_unique
ON mv_monthly_summary (tenant_id, month);

-- 自动刷新物化视图
CREATE OR REPLACE FUNCTION refresh_monthly_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_summary;
END;
$$ LANGUAGE plpgsql;

-- 定时刷新
SELECT cron.schedule('refresh-summary', '0 1 * * *', 'SELECT refresh_monthly_summary();');
```

---

## 🚀 二、缓存层设计

### 2.1 Redis缓存策略

#### 多级缓存架构
```python
# 缓存层级设计
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379)
        self.local_cache = {}  # 本地缓存
        self.cache_ttl = {
            'user_session': 3600,      # 1小时
            'tenant_config': 1800,     # 30分钟
            'model_result': 300,        # 5分钟
            'query_result': 60,        # 1分钟
        }
    
    async def get_cached_data(self, key: str, cache_type: str = 'query_result'):
        # L1: 本地缓存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # L2: Redis缓存
        cached_data = self.redis_client.get(f"{cache_type}:{key}")
        if cached_data:
            data = json.loads(cached_data)
            self.local_cache[key] = data  # 回填本地缓存
            return data
        
        return None
    
    async def set_cached_data(self, key: str, data: any, cache_type: str = 'query_result'):
        ttl = self.cache_ttl.get(cache_type, 60)
        
        # 设置本地缓存
        self.local_cache[key] = data
        
        # 设置Redis缓存
        self.redis_client.setex(
            f"{cache_type}:{key}",
            ttl,
            json.dumps(data, default=str)
        )
```

#### 缓存预热策略
```python
# 缓存预热
class CacheWarmup:
    def __init__(self, db_client, cache_manager):
        self.db = db_client
        self.cache = cache_manager
    
    async def warmup_tenant_data(self, tenant_id: str):
        """预热租户数据"""
        # 1. 预热租户配置
        config = await self.db.query(
            "SELECT * FROM tenant_config WHERE tenant_id = $1",
            [tenant_id]
        )
        await self.cache.set_cached_data(
            f"tenant_config:{tenant_id}",
            config,
            'tenant_config'
        )
        
        # 2. 预热月度汇总
        summary = await self.db.query("""
            SELECT * FROM mv_monthly_summary 
            WHERE tenant_id = $1 
            ORDER BY month DESC LIMIT 12
        """, [tenant_id])
        await self.cache.set_cached_data(
            f"monthly_summary:{tenant_id}",
            summary,
            'query_result'
        )
        
        # 3. 预热模型结果
        models = await self.db.query("""
            SELECT * FROM model_parameters_storage 
            WHERE tenant_id = $1 AND model_status = 'active'
        """, [tenant_id])
        await self.cache.set_cached_data(
            f"active_models:{tenant_id}",
            models,
            'model_result'
        )
```

### 2.2 应用层缓存

#### 查询结果缓存
```python
from functools import wraps
import hashlib

def cached_query(cache_type='query_result', ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = hashlib.md5(
                f"{func.__name__}:{str(args)}:{str(kwargs)}".encode()
            ).hexdigest()
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get_cached_data(cache_key, cache_type)
            if cached_result:
                return cached_result
            
            # 执行查询
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache_manager.set_cached_data(cache_key, result, cache_type)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cached_query('query_result', 300)
async def get_monthly_analysis(tenant_id: str, month: str):
    return await db.query("""
        SELECT * FROM mv_monthly_summary 
        WHERE tenant_id = $1 AND month = $2
    """, [tenant_id, month])
```

---

## 📊 三、读写分离架构

### 3.1 主从复制配置

#### 主库配置
```sql
-- postgresql.conf (主库)
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
hot_standby = on
```

#### 从库配置
```sql
-- postgresql.conf (从库)
hot_standby = on
max_standby_streaming_delay = 30s
wal_receiver_status_interval = 10s
hot_standby_feedback = on
```

#### 应用层读写分离
```python
class DatabaseManager:
    def __init__(self):
        self.master_db = create_connection(MASTER_DB_URL)
        self.slave_db = create_connection(SLAVE_DB_URL)
        self.cache_manager = CacheManager()
    
    async def read_query(self, query: str, params: list = None):
        """读操作路由到从库"""
        try:
            return await self.slave_db.query(query, params)
        except Exception as e:
            # 从库失败时回退到主库
            logger.warning(f"Slave query failed, fallback to master: {e}")
            return await self.master_db.query(query, params)
    
    async def write_query(self, query: str, params: list = None):
        """写操作路由到主库"""
        return await self.master_db.query(query, params)
    
    async def transactional_query(self, queries: list):
        """事务操作必须在主库"""
        async with self.master_db.transaction():
            results = []
            for query, params in queries:
                result = await self.master_db.query(query, params)
                results.append(result)
            return results
```

---

## 🔄 四、后期扩展方案

### 4.1 分片策略 (Sharding)

#### 水平分片设计
```python
class ShardManager:
    def __init__(self):
        self.shard_count = 4
        self.shard_connections = [
            create_connection(f"postgresql://shard_{i}_url")
            for i in range(self.shard_count)
        ]
    
    def get_shard_for_tenant(self, tenant_id: str) -> int:
        """根据租户ID确定分片"""
        return hash(tenant_id) % self.shard_count
    
    async def query_by_tenant(self, tenant_id: str, query: str, params: list = None):
        """按租户查询"""
        shard_id = self.get_shard_for_tenant(tenant_id)
        shard_db = self.shard_connections[shard_id]
        
        # 在查询中添加分片过滤
        sharded_query = f"{query} AND tenant_id = $1"
        sharded_params = [tenant_id] + (params or [])
        
        return await shard_db.query(sharded_query, sharded_params)
    
    async def cross_shard_query(self, query: str, params: list = None):
        """跨分片查询"""
        results = []
        for shard_db in self.shard_connections:
            result = await shard_db.query(query, params)
            results.extend(result)
        return results
```

#### 分片迁移策略
```python
class ShardMigration:
    def __init__(self, source_shard, target_shard):
        self.source = source_shard
        self.target = target_shard
    
    async def migrate_tenant_data(self, tenant_id: str):
        """迁移租户数据"""
        # 1. 锁定源分片数据
        await self.source.query("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        
        # 2. 复制数据到目标分片
        tables = ['fact_order', 'dim_customer', 'manager_evaluation']
        for table in tables:
            data = await self.source.query(f"SELECT * FROM {table} WHERE tenant_id = $1", [tenant_id])
            if data:
                await self.target.bulk_insert(table, data)
        
        # 3. 验证数据完整性
        await self.verify_data_integrity(tenant_id)
        
        # 4. 提交事务
        await self.source.query("COMMIT")
        await self.target.query("COMMIT")
        
        # 5. 更新路由表
        await self.update_routing_table(tenant_id)
```

### 4.2 混合架构 (PostgreSQL + ClickHouse)

#### 数据分层策略
```python
class HybridDataManager:
    def __init__(self):
        self.postgres = PostgreSQLClient()  # 业务数据
        self.clickhouse = ClickHouseClient()  # 分析数据
        self.redis = RedisClient()  # 缓存
    
    async def store_business_data(self, data: dict):
        """存储业务数据到PostgreSQL"""
        return await self.postgres.insert('fact_order', data)
    
    async def store_analytics_data(self, data: dict):
        """存储分析数据到ClickHouse"""
        return await self.clickhouse.insert('analytics_events', data)
    
    async def sync_to_analytics(self, tenant_id: str, date_range: tuple):
        """同步业务数据到分析数据库"""
        # 从PostgreSQL读取业务数据
        business_data = await self.postgres.query("""
            SELECT * FROM fact_order 
            WHERE tenant_id = $1 AND order_date BETWEEN $2 AND $3
        """, [tenant_id, date_range[0], date_range[1]])
        
        # 转换并写入ClickHouse
        analytics_data = self.transform_for_analytics(business_data)
        await self.clickhouse.bulk_insert('analytics_events', analytics_data)
    
    def transform_for_analytics(self, business_data: list) -> list:
        """数据转换"""
        return [
            {
                'tenant_id': row['tenant_id'],
                'event_date': row['order_date'],
                'event_type': 'order',
                'amount': row['amount'],
                'customer_id': row['customer_id'],
                'created_at': row['created_at']
            }
            for row in business_data
        ]
```

#### 查询路由策略
```python
class QueryRouter:
    def __init__(self, postgres_client, clickhouse_client):
        self.postgres = postgres_client
        self.clickhouse = clickhouse_client
    
    async def route_query(self, query_type: str, params: dict):
        """查询路由"""
        if query_type in ['business_lookup', 'transactional']:
            # 业务查询 -> PostgreSQL
            return await self.postgres.query(params['sql'], params['params'])
        
        elif query_type in ['analytics', 'reporting', 'aggregation']:
            # 分析查询 -> ClickHouse
            return await self.clickhouse.query(params['sql'], params['params'])
        
        elif query_type == 'hybrid':
            # 混合查询
            pg_result = await self.postgres.query(params['pg_sql'], params['pg_params'])
            ch_result = await self.clickhouse.query(params['ch_sql'], params['ch_params'])
            return self.merge_results(pg_result, ch_result)
```

---

## 📈 五、性能监控与调优

### 5.1 性能监控

#### 关键指标监控
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'query_duration': [],
            'cache_hit_rate': 0,
            'connection_pool_usage': 0,
            'slow_queries': []
        }
    
    async def monitor_query_performance(self, query: str, duration: float):
        """监控查询性能"""
        self.metrics['query_duration'].append(duration)
        
        # 慢查询记录
        if duration > 1.0:  # 超过1秒
            self.metrics['slow_queries'].append({
                'query': query,
                'duration': duration,
                'timestamp': datetime.now()
            })
    
    async def get_performance_report(self):
        """生成性能报告"""
        avg_duration = sum(self.metrics['query_duration']) / len(self.metrics['query_duration'])
        
        return {
            'average_query_duration': avg_duration,
            'slow_query_count': len(self.metrics['slow_queries']),
            'cache_hit_rate': self.metrics['cache_hit_rate'],
            'connection_pool_usage': self.metrics['connection_pool_usage']
        }
```

#### 自动调优
```python
class AutoTuner:
    def __init__(self, db_client, monitor):
        self.db = db_client
        self.monitor = monitor
    
    async def auto_tune_indexes(self):
        """自动调优索引"""
        # 分析查询模式
        query_stats = await self.db.query("""
            SELECT query, calls, total_time, mean_time
            FROM pg_stat_statements
            WHERE mean_time > 100  -- 平均超过100ms
            ORDER BY total_time DESC
        """)
        
        for stat in query_stats:
            if self.should_create_index(stat['query']):
                await self.create_suggested_index(stat['query'])
    
    def should_create_index(self, query: str) -> bool:
        """判断是否需要创建索引"""
        # 简单的启发式规则
        if 'WHERE' in query and 'ORDER BY' in query:
            return True
        if 'JOIN' in query and 'WHERE' in query:
            return True
        return False
```

---

## 🎯 六、实施计划

### Phase 1: 基础优化 (Month 1-2)
- [ ] PostgreSQL配置调优
- [ ] 索引优化
- [ ] 查询重写
- [ ] 基础监控

### Phase 2: 缓存层 (Month 2-3)
- [ ] Redis缓存实现
- [ ] 多级缓存架构
- [ ] 缓存预热
- [ ] 缓存监控

### Phase 3: 读写分离 (Month 3-4)
- [ ] 主从复制配置
- [ ] 读写分离实现
- [ ] 故障转移
- [ ] 负载均衡

### Phase 4: 分片扩展 (Month 4-5)
- [ ] 分片策略设计
- [ ] 分片实现
- [ ] 数据迁移工具
- [ ] 跨分片查询

### Phase 5: 混合架构 (Month 5-6)
- [ ] ClickHouse集成
- [ ] 数据同步
- [ ] 查询路由
- [ ] 性能对比

---

## 📊 七、性能预期

### 优化效果对比

| 指标 | 优化前 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------|--------|---------|---------|---------|---------|---------|
| 查询响应时间 | 5-10s | 2-5s | 0.5-2s | 0.3-1s | 0.2-0.5s | 0.1-0.3s |
| 并发支持 | 10 | 50 | 100 | 200 | 500 | 1000+ |
| 数据量支持 | 100万 | 500万 | 1000万 | 5000万 | 1亿+ | 10亿+ |
| 缓存命中率 | 0% | 0% | 80% | 85% | 90% | 95% |

### 成本效益分析

**Phase 1-2 (单机优化)**:
- 成本: 低 (仅配置调优)
- 效果: 3-5倍性能提升
- ROI: 高

**Phase 3-4 (读写分离+分片)**:
- 成本: 中等 (需要额外服务器)
- 效果: 10-20倍性能提升
- ROI: 高

**Phase 5 (混合架构)**:
- 成本: 高 (需要ClickHouse集群)
- 效果: 50-100倍分析性能提升
- ROI: 中等 (适合大数据场景)

---

## 🎉 总结

### 核心建议

1. **渐进式优化**: 从单机PostgreSQL开始，逐步扩展
2. **缓存优先**: Redis缓存能解决80%的性能问题
3. **读写分离**: 成本低，效果显著
4. **分片扩展**: 支持大规模数据
5. **混合架构**: 业务数据用PostgreSQL，分析数据用ClickHouse

### 关键成功因素

- **监控驱动**: 基于实际性能数据优化
- **自动化**: 减少人工干预
- **测试验证**: 每个阶段都要性能测试
- **文档维护**: 保持架构文档更新

**按照此方案实施，PostgreSQL可以支撑从MVP到大规模生产的所有需求！** 🚀


