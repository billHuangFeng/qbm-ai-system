# QBM AI System - 部署指南

## 🚀 快速部署

### 1. 环境要求

#### 系统要求
- **操作系统**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python版本**: 3.8+ (推荐 3.11+)
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 10GB 可用空间

#### 数据库要求
- **PostgreSQL**: 12+ (推荐 14+)
- **Redis**: 6.0+ (用于缓存)

### 2. 安装步骤

#### 2.1 克隆项目
```bash
git clone <repository-url>
cd qbm-ai-system
```

#### 2.2 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 2.4 环境变量配置
创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/qbm_db
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=False

# AI模型配置
AI_MODEL_CACHE_SIZE=1000
AI_PREDICTION_TIMEOUT=30
```

### 3. 数据库设置

#### 3.1 安装PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# 下载并安装 PostgreSQL from https://www.postgresql.org/download/

# macOS
brew install postgresql
```

#### 3.2 创建数据库
```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE qbm_db;
CREATE USER qbm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE qbm_db TO qbm_user;

-- 退出
\q
```

#### 3.3 运行数据库迁移
```bash
# 进入项目目录
cd qbm-ai-system/backend

# 运行迁移脚本
psql -U qbm_user -d qbm_db -f ../database/postgresql/15_ai_strategic_layer.sql
psql -U qbm_user -d qbm_db -f ../database/postgresql/16_ai_planning_loop.sql
```

### 4. Redis设置

#### 4.1 安装Redis
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Windows
# 下载并安装 Redis from https://github.com/microsoftarchive/redis/releases

# macOS
brew install redis
```

#### 4.2 启动Redis
```bash
# Linux/macOS
redis-server

# Windows
redis-server.exe
```

### 5. 启动服务

#### 5.1 开发环境启动
```bash
cd backend
python main.py
```

#### 5.2 生产环境启动
```bash
# 使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 使用gunicorn (Linux/macOS)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. 验证部署

#### 6.1 健康检查
```bash
curl http://localhost:8000/health
```

#### 6.2 API文档
访问 http://localhost:8000/docs 查看Swagger文档

#### 6.3 运行测试
```bash
pytest tests/ -v
```

---

## 🐳 Docker部署

### 1. 创建Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: qbm_db
      POSTGRES_USER: qbm_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/postgresql:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://qbm_user:your_password@db:5432/qbm_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### 3. 启动服务
```bash
docker-compose up -d
```

---

## 🔧 配置说明

### 1. 数据库配置
```python
# 连接池配置
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

### 2. Redis配置
```python
# 缓存配置
REDIS_MAX_CONNECTIONS = 100
REDIS_SOCKET_TIMEOUT = 5
REDIS_SOCKET_CONNECT_TIMEOUT = 5
```

### 3. AI模型配置
```python
# 模型配置
AI_MODEL_CACHE_SIZE = 1000
AI_PREDICTION_TIMEOUT = 30
AI_BATCH_SIZE = 32
AI_MAX_RETRIES = 3
```

---

## 📊 监控和日志

### 1. 日志配置
```python
# 日志级别
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志文件
LOG_FILE = "logs/app.log"
LOG_MAX_SIZE = 100MB
LOG_BACKUP_COUNT = 5
```

### 2. 监控指标
- **API响应时间**: < 500ms
- **数据库连接数**: < 80%
- **内存使用率**: < 80%
- **CPU使用率**: < 70%

### 3. 健康检查端点
```bash
# 基础健康检查
GET /health

# 详细健康检查
GET /health/detailed

# 数据库健康检查
GET /health/database

# Redis健康检查
GET /health/redis
```

---

## 🚨 故障排除

### 1. 常见问题

#### 数据库连接失败
```bash
# 检查PostgreSQL服务
sudo systemctl status postgresql

# 检查连接
psql -U qbm_user -d qbm_db -h localhost
```

#### Redis连接失败
```bash
# 检查Redis服务
redis-cli ping

# 检查端口
netstat -tlnp | grep 6379
```

#### 依赖包问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清理缓存
pip cache purge
```

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看警告日志
grep WARNING logs/app.log
```

---

## 🔒 安全配置

### 1. 环境变量安全
- 使用强密码
- 定期轮换密钥
- 限制环境变量访问权限

### 2. 数据库安全
- 使用专用数据库用户
- 限制网络访问
- 启用SSL连接

### 3. API安全
- 启用HTTPS
- 使用JWT认证
- 实施速率限制

---

## 📈 性能优化

### 1. 数据库优化
- 创建适当索引
- 使用连接池
- 定期清理数据

### 2. 缓存优化
- 启用Redis缓存
- 设置合理过期时间
- 监控缓存命中率

### 3. 应用优化
- 使用异步处理
- 实施请求限流
- 优化AI模型加载

---

## 🎯 生产环境检查清单

### 部署前检查
- [ ] 环境变量配置正确
- [ ] 数据库连接正常
- [ ] Redis连接正常
- [ ] 所有测试通过
- [ ] 日志配置正确
- [ ] 监控配置完成

### 部署后检查
- [ ] 服务启动正常
- [ ] API端点可访问
- [ ] 健康检查通过
- [ ] 日志输出正常
- [ ] 性能指标正常

---

**部署完成后，系统即可投入使用！** 🚀

