# QBM AI System - 性能监控指南

## 📊 监控概览

QBM AI System提供全面的性能监控和运维支持，确保系统稳定高效运行。

---

## 🔍 监控指标

### 1. 系统性能指标

#### 1.1 API性能
- **响应时间**: 平均响应时间 < 500ms
- **吞吐量**: 每秒请求数 (RPS)
- **错误率**: 4xx/5xx错误率 < 1%
- **可用性**: 系统可用性 > 99.9%

#### 1.2 数据库性能
- **连接数**: 活跃连接数 < 80% 最大连接数
- **查询时间**: 平均查询时间 < 100ms
- **慢查询**: 慢查询数量 < 5%
- **连接池**: 连接池使用率 < 80%

#### 1.3 缓存性能
- **命中率**: Redis缓存命中率 > 90%
- **响应时间**: 缓存操作响应时间 < 10ms
- **内存使用**: Redis内存使用率 < 80%
- **键过期**: 过期键清理效率

### 2. AI模型性能

#### 2.1 预测准确性
- **准确率**: 预测准确率 > 80%
- **置信度**: 平均置信度 > 0.7
- **召回率**: 模型召回率 > 75%
- **F1分数**: 综合评估分数 > 0.8

#### 2.2 模型性能
- **推理时间**: 单次预测时间 < 2s
- **批处理**: 批处理吞吐量
- **内存使用**: 模型内存占用
- **GPU使用**: GPU利用率 (如适用)

---

## 🛠️ 监控工具配置

### 1. 日志监控

#### 1.1 日志级别配置
```python
# logging_config.py
import logging
import structlog

# 配置日志级别
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

#### 1.2 日志文件配置
```python
# 日志文件轮转
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### 2. 性能监控

#### 2.1 Prometheus指标
```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# API请求指标
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')

# AI模型指标
AI_PREDICTION_COUNT = Counter('ai_predictions_total', 'Total AI predictions', ['model', 'status'])
AI_PREDICTION_DURATION = Histogram('ai_prediction_duration_seconds', 'AI prediction duration')
AI_MODEL_ACCURACY = Gauge('ai_model_accuracy', 'AI model accuracy', ['model'])

# 数据库指标
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration')
DB_CONNECTION_POOL = Gauge('db_connection_pool_size', 'Database connection pool size')

# 缓存指标
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['cache_type'])
CACHE_SIZE = Gauge('cache_size_bytes', 'Cache size in bytes', ['cache_type'])
```

#### 2.2 健康检查端点
```python
# health_check.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
import redis
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(
    db: DatabaseService = Depends(get_database_service),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """详细健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # 数据库检查
    try:
        result = await db.execute_query("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": "< 10ms"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Redis检查
    try:
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time": "< 5ms"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # 系统资源检查
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    health_status["checks"]["system"] = {
        "cpu_usage": f"{cpu_percent}%",
        "memory_usage": f"{memory_percent}%",
        "disk_usage": f"{disk_percent}%",
        "status": "healthy" if cpu_percent < 80 and memory_percent < 80 and disk_percent < 90 else "warning"
    }
    
    return health_status
```

### 3. 告警配置

#### 3.1 告警规则
```yaml
# alerting_rules.yml
groups:
- name: qbm_ai_system
  rules:
  - alert: HighErrorRate
    expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.01
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionHigh
    expr: db_connection_pool_size / db_connection_pool_max > 0.8
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High database connection usage"
      description: "Database connection pool is {{ $value }}% full"
  
  - alert: LowCacheHitRate
    expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Low cache hit rate"
      description: "Cache hit rate is {{ $value }}%"
  
  - alert: AIModelAccuracyLow
    expr: ai_model_accuracy < 0.7
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "AI model accuracy is low"
      description: "Model {{ $labels.model }} accuracy is {{ $value }}"
```

#### 3.2 告警通知
```python
# alerting.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

class AlertManager:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "alerts@company.com"
        self.password = "your_password"
        self.webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
    def send_email_alert(self, alert_data):
        """发送邮件告警"""
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = "admin@company.com"
        msg['Subject'] = f"QBM AI System Alert: {alert_data['alertname']}"
        
        body = f"""
        Alert: {alert_data['alertname']}
        Severity: {alert_data['severity']}
        Description: {alert_data['description']}
        Time: {alert_data['timestamp']}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.email, self.password)
        server.send_message(msg)
        server.quit()
    
    def send_slack_alert(self, alert_data):
        """发送Slack告警"""
        payload = {
            "text": f"🚨 QBM AI System Alert",
            "attachments": [
                {
                    "color": "danger" if alert_data['severity'] == 'critical' else "warning",
                    "fields": [
                        {"title": "Alert", "value": alert_data['alertname'], "short": True},
                        {"title": "Severity", "value": alert_data['severity'], "short": True},
                        {"title": "Description", "value": alert_data['description'], "short": False}
                    ]
                }
            ]
        }
        requests.post(self.webhook_url, json=payload)
```

---

## 📈 性能优化建议

### 1. 数据库优化

#### 1.1 索引优化
```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_objectives_priority ON strategic_objectives(priority);
CREATE INDEX idx_metrics_type ON north_star_metrics(metric_type);
CREATE INDEX idx_okr_period ON okrs(period_start, period_end);
CREATE INDEX idx_decisions_status ON decision_requirements(status);

-- 复合索引
CREATE INDEX idx_okr_objective_period ON okrs(strategic_objective_id, period_start);
CREATE INDEX idx_metrics_health ON north_star_metrics(health_score, last_updated);
```

#### 1.2 查询优化
```python
# 使用连接查询减少数据库往返
async def get_okr_with_metrics(okr_id: str):
    query = """
    SELECT o.*, k.kr_name, k.target_value, k.current_value
    FROM okrs o
    LEFT JOIN key_results k ON o.id = k.okr_id
    WHERE o.id = :okr_id
    """
    return await db.execute_query(query, {"okr_id": okr_id})

# 使用分页查询
async def get_objectives_paginated(page: int, size: int):
    offset = (page - 1) * size
    query = """
    SELECT * FROM strategic_objectives
    ORDER BY created_at DESC
    LIMIT :size OFFSET :offset
    """
    return await db.execute_query(query, {"size": size, "offset": offset})
```

### 2. 缓存优化

#### 2.1 Redis缓存策略
```python
# cache_strategies.py
import redis
import json
from typing import Any, Optional

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def get_or_set(self, key: str, fetch_func, ttl: int = 3600):
        """获取缓存或设置缓存"""
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        
        data = await fetch_func()
        self.redis_client.setex(key, ttl, json.dumps(data))
        return data
    
    def invalidate_pattern(self, pattern: str):
        """批量删除缓存"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

# 缓存配置
CACHE_CONFIG = {
    "objectives": {"ttl": 3600, "pattern": "objectives:*"},
    "metrics": {"ttl": 1800, "pattern": "metrics:*"},
    "okrs": {"ttl": 1800, "pattern": "okrs:*"},
    "predictions": {"ttl": 300, "pattern": "predictions:*"}
}
```

### 3. AI模型优化

#### 3.1 模型缓存
```python
# model_cache.py
from functools import lru_cache
import joblib

class ModelCache:
    def __init__(self):
        self.model_cache = {}
        self.prediction_cache = {}
    
    @lru_cache(maxsize=100)
    def get_model(self, model_name: str):
        """缓存模型实例"""
        if model_name not in self.model_cache:
            self.model_cache[model_name] = joblib.load(f"models/{model_name}.pkl")
        return self.model_cache[model_name]
    
    def cache_prediction(self, key: str, prediction: Any, ttl: int = 300):
        """缓存预测结果"""
        self.prediction_cache[key] = {
            "prediction": prediction,
            "timestamp": time.time(),
            "ttl": ttl
        }
    
    def get_cached_prediction(self, key: str) -> Optional[Any]:
        """获取缓存的预测结果"""
        if key in self.prediction_cache:
            cached = self.prediction_cache[key]
            if time.time() - cached["timestamp"] < cached["ttl"]:
                return cached["prediction"]
            else:
                del self.prediction_cache[key]
        return None
```

#### 3.2 批处理优化
```python
# batch_processing.py
import asyncio
from typing import List, Any

class BatchProcessor:
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
    
    async def process_predictions(self, data_list: List[Any]):
        """批量处理预测"""
        results = []
        for i in range(0, len(data_list), self.batch_size):
            batch = data_list[i:i + self.batch_size]
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
        return results
    
    async def _process_batch(self, batch: List[Any]):
        """处理单个批次"""
        tasks = [self._predict_single(item) for item in batch]
        return await asyncio.gather(*tasks)
```

---

## 🚨 故障处理

### 1. 常见问题诊断

#### 1.1 性能问题
```bash
# 检查系统资源
top
htop
iostat -x 1

# 检查数据库性能
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;

# 检查Redis性能
redis-cli info stats
redis-cli slowlog get 10
```

#### 1.2 错误排查
```bash
# 查看应用日志
tail -f logs/app.log
grep ERROR logs/app.log
grep WARNING logs/app.log

# 查看系统日志
journalctl -u qbm-ai-system -f
dmesg | tail -20
```

### 2. 自动恢复

#### 2.1 服务重启
```python
# auto_recovery.py
import subprocess
import time
import requests

class AutoRecovery:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 30
    
    async def check_service_health(self):
        """检查服务健康状态"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def restart_service(self):
        """重启服务"""
        subprocess.run(["systemctl", "restart", "qbm-ai-system"])
        time.sleep(10)
    
    async def auto_recovery_loop(self):
        """自动恢复循环"""
        while True:
            if not await self.check_service_health():
                for attempt in range(self.max_retries):
                    await self.restart_service()
                    if await self.check_service_health():
                        break
                    time.sleep(self.retry_delay)
            time.sleep(60)
```

---

## 📊 监控仪表板

### 1. Grafana配置

#### 1.1 仪表板配置
```json
{
  "dashboard": {
    "title": "QBM AI System Monitoring",
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "AI Model Accuracy",
        "type": "singlestat",
        "targets": [
          {
            "expr": "ai_model_accuracy",
            "legendFormat": "{{model}}"
          }
        ]
      }
    ]
  }
}
```

---

**通过完善的监控体系，确保QBM AI System稳定高效运行！** 🚀
