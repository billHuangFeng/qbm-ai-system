# QBM AI系统 - 部署和运维指南

## 📋 目录
- [部署概述](#部署概述)
- [环境要求](#环境要求)
- [Docker部署](#docker部署)
- [Kubernetes部署](#kubernetes部署)
- [生产环境配置](#生产环境配置)
- [监控和日志](#监控和日志)
- [备份和恢复](#备份和恢复)
- [性能优化](#性能优化)
- [安全配置](#安全配置)
- [故障排除](#故障排除)

## 🎯 部署概述

QBM AI系统支持多种部署方式，从开发环境的Docker Compose到生产环境的Kubernetes集群部署。

### 部署架构
```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡器 (Nginx)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   应用层 (Kubernetes)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  前端 Pod   │  │  后端 Pod   │  │  API Pod    │          │
│  │  (Next.js)  │  │ (FastAPI)   │  │ (FastAPI)   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   数据层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ PostgreSQL  │  │    Redis     │  │  监控系统    │          │
│  │  (主从)     │  │   (集群)     │  │(Prometheus)  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 环境要求

### 最低硬件要求
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 1Gbps

### 推荐硬件配置
- **CPU**: 8核心
- **内存**: 16GB RAM
- **存储**: 500GB SSD
- **网络**: 10Gbps

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Docker**: 20.10+
- **Kubernetes**: 1.24+
- **Helm**: 3.8+

## 🐳 Docker部署

### 开发环境部署

1. **克隆仓库**
```bash
git clone https://github.com/your-org/qbm-ai-system.git
cd qbm-ai-system
```

2. **环境配置**
```bash
# 复制环境配置文件
cp env.example .env

# 编辑配置文件
vim .env
```

3. **启动服务**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

4. **验证部署**
```bash
# 检查API健康状态
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000

# 检查数据库连接
docker-compose exec postgres psql -U postgres -d qbm_ai_system -c "SELECT version();"
```

### 生产环境Docker部署

1. **创建生产环境配置**
```bash
# 创建生产环境配置
cp docker-compose.yml docker-compose.prod.yml
```

2. **配置生产环境变量**
```bash
# 创建生产环境变量文件
cat > .env.prod << EOF
ENVIRONMENT=production
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_secret_key
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
EOF
```

3. **启动生产服务**
```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 设置自动重启
docker-compose -f docker-compose.prod.yml up -d --restart unless-stopped
```

## ☸️ Kubernetes部署

### 1. 准备Kubernetes集群

```bash
# 检查集群状态
kubectl cluster-info

# 创建命名空间
kubectl create namespace qbm-ai-system

# 设置默认命名空间
kubectl config set-context --current --namespace=qbm-ai-system
```

### 2. 配置存储

```bash
# 创建存储类
kubectl apply -f kubernetes/storage-class.yaml

# 创建持久卷声明
kubectl apply -f kubernetes/pvc.yaml
```

### 3. 部署数据库

```bash
# 部署PostgreSQL
kubectl apply -f kubernetes/postgres.yaml

# 部署Redis
kubectl apply -f kubernetes/redis.yaml

# 等待数据库就绪
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis --timeout=300s
```

### 4. 部署应用

```bash
# 创建配置映射
kubectl apply -f kubernetes/configmap.yaml

# 创建密钥
kubectl create secret generic qbm-secrets \
  --from-literal=POSTGRES_PASSWORD=your_password \
  --from-literal=REDIS_PASSWORD=your_redis_password \
  --from-literal=SECRET_KEY=your_secret_key

# 部署后端服务
kubectl apply -f kubernetes/backend.yaml

# 部署前端服务
kubectl apply -f kubernetes/frontend.yaml

# 部署Nginx
kubectl apply -f kubernetes/nginx.yaml
```

### 5. 配置Ingress

```bash
# 安装Ingress Controller (Nginx)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 等待Ingress Controller就绪
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# 创建Ingress
kubectl apply -f kubernetes/ingress.yaml
```

### 6. 配置SSL证书

```bash
# 安装cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 创建ClusterIssuer
kubectl apply -f kubernetes/certificate.yaml
```

### 7. 部署监控

```bash
# 部署Prometheus
kubectl apply -f kubernetes/monitoring/prometheus.yaml

# 部署Grafana
kubectl apply -f kubernetes/monitoring/grafana.yaml

# 部署AlertManager
kubectl apply -f kubernetes/monitoring/alertmanager.yaml
```

## 🏭 生产环境配置

### 1. 数据库配置

```yaml
# postgresql.conf 优化配置
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. Redis配置

```yaml
# redis.conf 优化配置
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-keepalive 300
timeout 0
```

### 3. 应用配置

```yaml
# 后端配置优化
WORKERS: 4
WORKER_TIMEOUT: 300
REQUEST_TIMEOUT: 60
MAX_WORKERS: 8
WORKER_CONNECTIONS: 1000
```

### 4. 负载均衡配置

```nginx
# nginx.conf 优化配置
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 20M;

upstream backend {
    least_conn;
    server backend-1:8000 max_fails=3 fail_timeout=30s;
    server backend-2:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📊 监控和日志

### 1. Prometheus配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'qbm-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 2. Grafana仪表板

```json
{
  "dashboard": {
    "title": "QBM AI System Dashboard",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Model Accuracy",
        "type": "singlestat",
        "targets": [
          {
            "expr": "avg(model_accuracy_score)",
            "legendFormat": "Average Accuracy"
          }
        ]
      }
    ]
  }
}
```

### 3. 日志配置

```python
# logging.conf
[loggers]
keys=root,qbm

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,jsonFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_qbm]
level=INFO
handlers=consoleHandler,fileHandler
qualname=qbm
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=jsonFormatter
args=('logs/app.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_jsonFormatter]
format={"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}
```

## 💾 备份和恢复

### 1. 数据库备份

```bash
#!/bin/bash
# backup.sh

# 设置变量
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="qbm_ai_system"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
pg_dump -h localhost -U postgres -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_DIR/qbm_backup_$DATE.dump"

# 清理旧备份 (保留30天)
find $BACKUP_DIR -name "qbm_backup_*.dump" -mtime +30 -delete

echo "Backup completed: qbm_backup_$DATE.dump"
```

### 2. 自动备份配置

```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

### 3. 数据恢复

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_NAME="qbm_ai_system"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 停止应用服务
kubectl scale deployment backend --replicas=0
kubectl scale deployment frontend --replicas=0

# 等待服务停止
kubectl wait --for=delete pod -l app=backend --timeout=300s

# 恢复数据库
pg_restore -h localhost -U postgres -d $DB_NAME \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  $BACKUP_FILE

# 重启应用服务
kubectl scale deployment backend --replicas=3
kubectl scale deployment frontend --replicas=2

echo "Restore completed from $BACKUP_FILE"
```

## ⚡ 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX CONCURRENTLY idx_marginal_analysis_date 
ON marginal_analysis_results(analysis_date);

CREATE INDEX CONCURRENTLY idx_prediction_accuracy_model 
ON prediction_accuracy_log(model_id, prediction_date);

-- 分区表
CREATE TABLE prediction_accuracy_log_2024_01 
PARTITION OF prediction_accuracy_log 
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 更新统计信息
ANALYZE marginal_analysis_results;
ANALYZE prediction_accuracy_log;
```

### 2. 缓存优化

```python
# Redis缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 3600,
    'CACHE_KEY_PREFIX': 'qbm:',
    'CACHE_OPTIONS': {
        'CACHE_REDIS_DB': 0,
        'CACHE_REDIS_PASSWORD': 'your_password',
        'CACHE_REDIS_HOST': 'localhost',
        'CACHE_REDIS_PORT': 6379
    }
}

# 缓存策略
@cache.memoize(timeout=3600)
def get_model_predictions(model_id, input_data):
    """缓存模型预测结果"""
    pass

@cache.cached(timeout=1800)
def get_feature_importance(model_id):
    """缓存特征重要性"""
    pass
```

### 3. API优化

```python
# 异步处理
from fastapi import BackgroundTasks
import asyncio

@app.post("/api/v1/models/train")
async def train_model(
    background_tasks: BackgroundTasks,
    model_data: ModelTrainingRequest
):
    """异步训练模型"""
    task_id = str(uuid.uuid4())
    
    # 启动后台任务
    background_tasks.add_task(
        train_model_async, 
        task_id, 
        model_data
    )
    
    return {"task_id": task_id, "status": "started"}

async def train_model_async(task_id: str, model_data: ModelTrainingRequest):
    """异步训练模型任务"""
    try:
        # 更新任务状态
        await update_task_status(task_id, "running")
        
        # 执行训练
        result = await train_model_task(model_data)
        
        # 更新任务状态
        await update_task_status(task_id, "completed", result)
        
    except Exception as e:
        await update_task_status(task_id, "failed", str(e))
```

### 4. 连接池优化

```python
# 数据库连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Redis连接池
import redis
from redis.connection import ConnectionPool

redis_pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    password='your_password',
    max_connections=50,
    retry_on_timeout=True
)

redis_client = redis.Redis(connection_pool=redis_pool)
```

## 🔒 安全配置

### 1. 网络安全

```yaml
# 网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: qbm-network-policy
  namespace: qbm-ai-system
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 2. 密钥管理

```bash
# 创建密钥
kubectl create secret generic qbm-secrets \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=REDIS_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=SECRET_KEY=$(openssl rand -base64 64) \
  --from-literal=JWT_SECRET_KEY=$(openssl rand -base64 64)

# 使用外部密钥管理 (如HashiCorp Vault)
kubectl create secret generic vault-token \
  --from-literal=token=$(vault write -field=token auth/kubernetes/login role=qbm-ai-system)
```

### 3. 访问控制

```yaml
# RBAC配置
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: qbm-ai-system
  name: qbm-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: qbm-role-binding
  namespace: qbm-ai-system
subjects:
- kind: ServiceAccount
  name: qbm-service-account
  namespace: qbm-ai-system
roleRef:
  kind: Role
  name: qbm-role
  apiGroup: rbac.authorization.k8s.io
```

### 4. 安全扫描

```bash
# 容器安全扫描
trivy image qbm-ai-system/backend:latest

# 依赖安全扫描
npm audit
pip check

# 代码安全扫描
bandit -r backend/src/
semgrep --config=auto backend/
```

## 🔧 故障排除

### 1. 常见问题诊断

```bash
# 检查Pod状态
kubectl get pods -n qbm-ai-system

# 查看Pod日志
kubectl logs -f deployment/backend -n qbm-ai-system

# 检查服务状态
kubectl get services -n qbm-ai-system

# 检查Ingress状态
kubectl get ingress -n qbm-ai-system

# 检查事件
kubectl get events -n qbm-ai-system --sort-by='.lastTimestamp'
```

### 2. 性能问题诊断

```bash
# 检查资源使用
kubectl top pods -n qbm-ai-system
kubectl top nodes

# 检查数据库性能
kubectl exec -it postgres-0 -n qbm-ai-system -- psql -U postgres -d qbm_ai_system -c "
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_user_tables;
"

# 检查Redis性能
kubectl exec -it redis-0 -n qbm-ai-system -- redis-cli info stats
```

### 3. 网络问题诊断

```bash
# 测试网络连接
kubectl run test-pod --image=busybox --rm -it -- sh
# 在Pod内测试连接
wget -O- http://backend:8000/health
wget -O- http://postgres:5432

# 检查DNS解析
nslookup backend.qbm-ai-system.svc.cluster.local
```

### 4. 数据问题诊断

```bash
# 检查数据库连接
kubectl exec -it postgres-0 -n qbm-ai-system -- psql -U postgres -d qbm_ai_system -c "
SELECT count(*) FROM marginal_analysis_results;
SELECT count(*) FROM prediction_accuracy_log;
"

# 检查数据质量
kubectl exec -it backend-0 -n qbm-ai-system -- python -c "
from src.services.database_service import DatabaseService
db = DatabaseService()
result = db.execute_query('SELECT * FROM data_quality_check ORDER BY check_date DESC LIMIT 10')
print(result)
"
```

## 📈 扩展和维护

### 1. 水平扩展

```bash
# 扩展后端服务
kubectl scale deployment backend --replicas=5 -n qbm-ai-system

# 扩展前端服务
kubectl scale deployment frontend --replicas=3 -n qbm-ai-system

# 配置HPA
kubectl apply -f kubernetes/hpa.yaml
```

### 2. 滚动更新

```bash
# 更新后端镜像
kubectl set image deployment/backend backend=qbm-ai-system/backend:v2.0.0 -n qbm-ai-system

# 查看更新状态
kubectl rollout status deployment/backend -n qbm-ai-system

# 回滚更新
kubectl rollout undo deployment/backend -n qbm-ai-system
```

### 3. 定期维护

```bash
# 清理旧日志
kubectl exec -it backend-0 -n qbm-ai-system -- find /app/logs -name "*.log" -mtime +30 -delete

# 清理旧数据
kubectl exec -it postgres-0 -n qbm-ai-system -- psql -U postgres -d qbm_ai_system -c "
DELETE FROM prediction_accuracy_log WHERE prediction_date < NOW() - INTERVAL '90 days';
VACUUM ANALYZE prediction_accuracy_log;
"

# 更新依赖
kubectl exec -it backend-0 -n qbm-ai-system -- pip install --upgrade -r requirements.txt
```

---

**部署和运维指南版本**: 1.0.0  
**最后更新**: 2024-01-15


