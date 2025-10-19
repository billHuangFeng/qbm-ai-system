# QBM AI System 部署指南

## 概述

本指南将帮助您部署QBM AI System到生产环境。系统支持多种部署方式，包括Docker容器化部署、云服务器部署等。

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 100Mbps 带宽

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 50GB SSD
- **网络**: 1Gbps 带宽

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+

## 部署方式

### 方式一：Docker容器化部署（推荐）

#### 1. 克隆项目
```bash
git clone https://github.com/billHuangFeng/qbm-ai-system.git
cd qbm-ai-system
```

#### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

主要配置项：
```env
# 数据库配置
DATABASE_URL=mysql+pymysql://qbm_user:your_password@mysql:3306/qbm_ai
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_PASSWORD=your_password

# Redis配置
REDIS_URL=redis://redis:6379

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
```

#### 3. 启动服务
```bash
# 使用启动脚本
python scripts/start.py start

# 或使用Docker Compose
docker-compose up -d
```

#### 4. 验证部署
```bash
# 检查服务状态
python scripts/start.py status

# 运行健康检查
python scripts/health_check.py

# 查看服务日志
python scripts/start.py logs
```

### 方式二：手动部署

#### 1. 安装依赖

**后端依赖**：
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖**：
```bash
cd frontend
npm install
```

#### 2. 数据库设置
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE qbm_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'qbm_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON qbm_ai.* TO 'qbm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 运行数据库迁移
cd backend
alembic upgrade head
```

#### 3. 启动服务

**启动后端**：
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**启动前端**：
```bash
cd frontend
npm run build
npm run preview
```

## 生产环境配置

### 1. 安全配置

#### 修改默认密码
```bash
# 修改数据库密码
mysql -u root -p
ALTER USER 'qbm_user'@'localhost' IDENTIFIED BY 'new_strong_password';

# 修改JWT密钥
export SECRET_KEY="your-very-secure-secret-key-here"
```

#### 配置防火墙
```bash
# 只开放必要端口
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

#### 配置SSL证书
```bash
# 使用Let's Encrypt
certbot --nginx -d your-domain.com
```

### 2. 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_customers_created_at ON customers(created_at);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_products_category ON products(category);

-- 配置MySQL
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
```

#### Redis优化
```bash
# 配置Redis
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. 监控和日志

#### 配置日志轮转
```bash
# 创建logrotate配置
cat > /etc/logrotate.d/qbm-ai-system << EOF
/var/log/qbm-ai-system/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
```

#### 配置监控
```bash
# 安装监控工具
pip install prometheus-client
pip install grafana-api

# 配置Prometheus
# 配置Grafana仪表板
```

## 云服务器部署

### AWS部署

#### 1. 创建EC2实例
```bash
# 使用Ubuntu 20.04 LTS
# 实例类型：t3.medium 或更大
# 安全组：开放22, 80, 443端口
```

#### 2. 安装Docker
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. 部署应用
```bash
# 克隆项目
git clone https://github.com/billHuangFeng/qbm-ai-system.git
cd qbm-ai-system

# 配置环境变量
cp .env.example .env
# 编辑.env文件

# 启动服务
docker-compose up -d
```

### 阿里云部署

#### 1. 创建ECS实例
- 选择Ubuntu 20.04 LTS
- 实例规格：2核4GB或更高
- 安全组：开放22, 80, 443端口

#### 2. 配置域名解析
```bash
# 在阿里云DNS中添加A记录
# 将域名指向ECS实例的公网IP
```

#### 3. 部署应用
```bash
# 按照AWS部署步骤进行
```

## 备份和恢复

### 数据备份

#### 1. 数据库备份
```bash
# 创建备份脚本
cat > backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
docker exec qbm-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD qbm_ai > $BACKUP_DIR/qbm_ai_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/qbm_ai_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup_database.sh

# 设置定时备份
crontab -e
# 添加：0 2 * * * /path/to/backup_database.sh
```

#### 2. 文件备份
```bash
# 备份上传文件
rsync -av /path/to/uploads/ /backup/uploads/

# 备份配置文件
cp -r /path/to/qbm-ai-system/.env /backup/config/
```

### 数据恢复

#### 1. 数据库恢复
```bash
# 解压备份文件
gunzip /backup/mysql/qbm_ai_20240115_020000.sql.gz

# 恢复数据库
docker exec -i qbm-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD qbm_ai < /backup/mysql/qbm_ai_20240115_020000.sql
```

#### 2. 文件恢复
```bash
# 恢复上传文件
rsync -av /backup/uploads/ /path/to/uploads/

# 恢复配置文件
cp /backup/config/.env /path/to/qbm-ai-system/
```

## 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查Docker状态
docker ps -a

# 查看服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql

# 检查端口占用
netstat -tlnp | grep :8000
netstat -tlnp | grep :8080
```

#### 2. 数据库连接失败
```bash
# 检查MySQL状态
docker exec qbm-mysql mysqladmin -u root -p status

# 检查网络连接
docker exec qbm-backend ping mysql

# 检查环境变量
docker exec qbm-backend env | grep DATABASE
```

#### 3. 前端无法访问
```bash
# 检查Nginx配置
docker exec qbm-frontend nginx -t

# 检查前端构建
docker exec qbm-frontend ls -la /usr/share/nginx/html

# 检查API代理
curl -I http://localhost/api/v1/system/health
```

### 性能问题

#### 1. 响应慢
```bash
# 检查系统资源
docker stats

# 检查数据库性能
docker exec qbm-mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 检查Redis性能
docker exec qbm-redis redis-cli info stats
```

#### 2. 内存不足
```bash
# 检查内存使用
free -h
docker system df

# 清理Docker缓存
docker system prune -a

# 调整容器内存限制
# 在docker-compose.yml中设置mem_limit
```

## 维护和更新

### 系统更新

#### 1. 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

#### 2. 数据库迁移
```bash
# 运行数据库迁移
docker exec qbm-backend alembic upgrade head
```

### 定期维护

#### 1. 日志清理
```bash
# 清理Docker日志
docker system prune -f

# 清理应用日志
find /var/log/qbm-ai-system -name "*.log" -mtime +30 -delete
```

#### 2. 系统监控
```bash
# 检查磁盘空间
df -h

# 检查系统负载
uptime

# 检查服务状态
docker-compose ps
```

## 安全建议

1. **定期更新系统**：保持操作系统和依赖包的最新版本
2. **使用强密码**：为所有账户设置强密码
3. **配置防火墙**：只开放必要的端口
4. **启用SSL**：使用HTTPS加密传输
5. **定期备份**：建立自动备份机制
6. **监控日志**：定期检查系统日志
7. **访问控制**：限制管理员访问权限

## 技术支持

如果您在部署过程中遇到问题，可以通过以下方式获取帮助：

- **GitHub Issues**: https://github.com/billHuangFeng/qbm-ai-system/issues
- **邮箱支持**: support@qbm-ai.com
- **在线文档**: https://docs.qbm-ai.com

---

**注意**: 本指南基于Ubuntu 20.04 LTS系统编写，其他Linux发行版可能需要调整部分命令。


