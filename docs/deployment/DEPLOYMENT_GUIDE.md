# 边际影响分析系统 - 部署指导文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (部署设计)
- **实施方**: Lovable (部署实施)
- **状态**: ⏳ 待Lovable实施

---

## 1. 部署架构概述

### 1.1 部署目标
- **高可用性**: 99.9%系统可用性
- **可扩展性**: 支持水平扩展
- **安全性**: 生产级安全防护
- **性能**: 支持1000+并发用户
- **监控**: 完整的监控和告警体系

### 1.2 部署架构图
```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │    (Nginx)      │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │   CDN/Static   │
                    │   (CloudFlare) │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  App 1  │          │  App 2  │          │  App 3  │
   │(Node.js)│          │(Node.js)│          │(Node.js)│
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Supabase      │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

---

## 2. 环境准备

### 2.1 系统要求

#### 2.1.1 服务器配置
```yaml
# 生产环境配置
production:
  app_servers:
    count: 3
    cpu: 4 cores
    memory: 8GB
    storage: 100GB SSD
    os: Ubuntu 20.04 LTS
  
  database:
    cpu: 8 cores
    memory: 16GB
    storage: 500GB SSD
    backup: daily
  
  load_balancer:
    cpu: 2 cores
    memory: 4GB
    storage: 50GB SSD
```

#### 2.1.2 软件依赖
```bash
# 系统依赖
sudo apt update
sudo apt install -y curl wget git nginx certbot python3-certbot-nginx

# Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2.2 环境变量配置

#### 2.2.1 生产环境变量
```bash
# .env.production
NODE_ENV=production
PORT=3000

# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/qbm_production
DB_HOST=localhost
DB_PORT=5432
DB_NAME=qbm_production
DB_USER=qbm_user
DB_PASSWORD=secure_password_here

# Redis配置
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=redis_password_here

# JWT配置
JWT_SECRET=your_super_secret_jwt_key_here
JWT_EXPIRY=3600

# 加密配置
ENCRYPTION_KEY=your_encryption_key_here
ENCRYPTION_ALGORITHM=aes-256-gcm

# 外部服务
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# 监控配置
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=info

# 安全配置
CORS_ORIGINS=https://app.qbm-system.com,https://admin.qbm-system.com
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100
```

---

## 3. 容器化部署

### 3.1 Docker配置

#### 3.1.1 应用容器
```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产镜像
FROM node:18-alpine AS production

# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app

# 复制构建产物
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# 设置用户
USER nextjs

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

EXPOSE 3000

CMD ["npm", "start"]
```

#### 3.1.2 Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3.2 Kubernetes部署

#### 3.2.1 应用部署配置
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qbm-app
  labels:
    app: qbm-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qbm-app
  template:
    metadata:
      labels:
        app: qbm-app
    spec:
      containers:
      - name: qbm-app
        image: qbm-system:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: qbm-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 3.2.2 服务配置
```yaml
# k8s-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: qbm-app-service
spec:
  selector:
    app: qbm-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

---

## 4. 数据库部署

### 4.1 PostgreSQL配置

#### 4.1.1 数据库初始化
```sql
-- init.sql
CREATE DATABASE qbm_production;
CREATE USER qbm_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE qbm_production TO qbm_user;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建表结构
\i /docker-entrypoint-initdb.d/schema.sql
```

#### 4.1.2 性能优化配置
```conf
# postgresql.conf
# 内存配置
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 256MB
maintenance_work_mem = 1GB

# 连接配置
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# 日志配置
log_statement = 'all'
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on

# 性能配置
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 4.2 Redis配置

#### 4.2.1 Redis配置优化
```conf
# redis.conf
# 内存配置
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# 安全配置
requirepass your_redis_password_here
rename-command FLUSHDB ""
rename-command FLUSHALL ""

# 性能配置
tcp-keepalive 300
timeout 0
```

---

## 5. 负载均衡配置

### 5.1 Nginx配置

#### 5.1.1 主配置文件
```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # 上游服务器
    upstream app_servers {
        least_conn;
        server app1:3000 weight=3;
        server app2:3000 weight=3;
        server app3:3000 weight=2;
        keepalive 32;
    }
    
    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # 主服务器配置
    server {
        listen 80;
        server_name api.qbm-system.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name api.qbm-system.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;
        
        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # API路由
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://app_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # 登录接口特殊限流
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://app_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        
        # 静态文件
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## 6. 监控与日志

### 6.1 应用监控

#### 6.1.1 Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'qbm-app'
    static_configs:
      - targets: ['app1:3000', 'app2:3000', 'app3:3000']
    metrics_path: '/api/metrics'
    scrape_interval: 5s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

#### 6.1.2 Grafana仪表板
```json
{
  "dashboard": {
    "title": "QBM System Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

### 6.2 日志管理

#### 6.2.1 日志配置
```typescript
// logger.ts
import winston from 'winston';
import { Logtail } from '@logtail/node';

const logtail = new Logtail(process.env.LOGTAIL_TOKEN);

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
});

// 生产环境发送到Logtail
if (process.env.NODE_ENV === 'production') {
  logger.add(new winston.transports.Stream({
    stream: logtail.stream
  }));
}

export default logger;
```

#### 6.2.2 日志轮转配置
```conf
# logrotate.conf
/var/log/qbm-system/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload nginx
    endscript
}
```

---

## 7. 安全配置

### 7.1 SSL/TLS配置

#### 7.1.1 证书申请
```bash
# 使用Let's Encrypt申请证书
sudo certbot --nginx -d api.qbm-system.com -d app.qbm-system.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

#### 7.1.2 安全加固
```bash
# 防火墙配置
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 3000/tcp

# 系统安全配置
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 7.2 数据库安全

#### 7.2.1 数据库访问控制
```sql
-- 创建只读用户
CREATE USER qbm_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE qbm_production TO qbm_readonly;
GRANT USAGE ON SCHEMA public TO qbm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO qbm_readonly;

-- 创建备份用户
CREATE USER qbm_backup WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE qbm_production TO qbm_backup;
GRANT USAGE ON SCHEMA public TO qbm_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO qbm_backup;
```

---

## 8. 备份与恢复

### 8.1 数据库备份

#### 8.1.1 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/qbm-system"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="qbm_production"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
pg_dump -h localhost -U qbm_user -d $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

# 上传到云存储
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://qbm-backups/database/
```

#### 8.1.2 备份恢复
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_NAME="qbm_production"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 解压备份文件
gunzip $BACKUP_FILE

# 恢复数据库
psql -h localhost -U qbm_user -d $DB_NAME < ${BACKUP_FILE%.gz}

echo "Database restored from $BACKUP_FILE"
```

### 8.2 应用备份

#### 8.2.1 配置文件备份
```bash
#!/bin/bash
# config_backup.sh

BACKUP_DIR="/var/backups/qbm-system/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz \
    /etc/nginx/nginx.conf \
    /etc/nginx/sites-available/ \
    /etc/ssl/certs/ \
    /etc/ssl/private/ \
    /var/log/nginx/

# 上传到云存储
aws s3 cp $BACKUP_DIR/config_backup_$DATE.tar.gz s3://qbm-backups/config/
```

---

## 9. 部署脚本

### 9.1 自动化部署

#### 9.1.1 部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

# 配置变量
APP_NAME="qbm-system"
APP_VERSION="latest"
DOCKER_REGISTRY="your-registry.com"
KUBE_NAMESPACE="qbm-production"

echo "开始部署 $APP_NAME v$APP_VERSION"

# 1. 构建镜像
echo "构建Docker镜像..."
docker build -t $DOCKER_REGISTRY/$APP_NAME:$APP_VERSION .
docker push $DOCKER_REGISTRY/$APP_NAME:$APP_VERSION

# 2. 更新Kubernetes部署
echo "更新Kubernetes部署..."
kubectl set image deployment/$APP_NAME $APP_NAME=$DOCKER_REGISTRY/$APP_NAME:$APP_VERSION -n $KUBE_NAMESPACE

# 3. 等待部署完成
echo "等待部署完成..."
kubectl rollout status deployment/$APP_NAME -n $KUBE_NAMESPACE

# 4. 健康检查
echo "执行健康检查..."
kubectl get pods -n $KUBE_NAMESPACE -l app=$APP_NAME

echo "部署完成！"
```

#### 9.1.2 回滚脚本
```bash
#!/bin/bash
# rollback.sh

APP_NAME="qbm-system"
KUBE_NAMESPACE="qbm-production"

echo "回滚 $APP_NAME 到上一个版本..."

kubectl rollout undo deployment/$APP_NAME -n $KUBE_NAMESPACE

echo "等待回滚完成..."
kubectl rollout status deployment/$APP_NAME -n $KUBE_NAMESPACE

echo "回滚完成！"
```

---

## 10. 性能优化

### 10.1 应用性能优化

#### 10.1.1 Node.js优化
```javascript
// 性能优化配置
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  // 创建worker进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
} else {
  // Worker进程
  require('./app');
}
```

#### 10.1.2 缓存策略
```typescript
// Redis缓存配置
import Redis from 'ioredis';

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  password: process.env.REDIS_PASSWORD,
  retryDelayOnFailover: 100,
  maxRetriesPerRequest: 3
});

// 缓存中间件
const cacheMiddleware = (ttl: number = 300) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    const key = `cache:${req.originalUrl}`;
    
    try {
      const cached = await redis.get(key);
      if (cached) {
        return res.json(JSON.parse(cached));
      }
      
      // 缓存响应
      const originalSend = res.json;
      res.json = function(data) {
        redis.setex(key, ttl, JSON.stringify(data));
        return originalSend.call(this, data);
      };
      
      next();
    } catch (error) {
      next();
    }
  };
};
```

---

## 11. 总结

本部署指导文档提供了完整的部署方案，包括：

1. **环境准备**: 系统要求、软件依赖、环境变量
2. **容器化部署**: Docker配置、Kubernetes部署
3. **数据库部署**: PostgreSQL配置、Redis配置
4. **负载均衡**: Nginx配置、SSL/TLS配置
5. **监控日志**: Prometheus、Grafana、日志管理
6. **安全配置**: 防火墙、数据库安全、SSL证书
7. **备份恢复**: 数据库备份、应用备份、恢复流程
8. **自动化部署**: 部署脚本、回滚脚本
9. **性能优化**: 应用优化、缓存策略

所有部署步骤都具备详细的配置和脚本，能够确保系统的稳定运行。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 2-3周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com


