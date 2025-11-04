# 快速启动后端服务

## 前置要求

1. **Python 3.8+** 已安装
2. **依赖包** 已安装（运行 `pip install -r requirements.txt`）
3. **环境变量** 已配置（`.env` 文件）

## 快速启动

### Windows 用户

双击运行启动脚本：
```
backend\start_server.bat
```

或使用命令行：
```bash
cd backend
python main_optimized.py
```

### Linux/Mac 用户

运行启动脚本：
```bash
chmod +x backend/start_server.sh
./backend/start_server.sh
```

或使用命令行：
```bash
cd backend
python3 main_optimized.py
```

## 验证服务运行

### 1. 检查端口监听

**Windows:**
```bash
netstat -ano | findstr :8000
```

**Linux/Mac:**
```bash
lsof -i :8000
```

应该看到端口 8000 正在监听。

### 2. 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "database": true,
  "redis": true,
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0"
}
```

### 3. 访问 API 文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 环境配置

### 创建 .env 文件

在项目根目录（`qbm-ai-system/`）创建 `.env` 文件：

```bash
cp env.example .env
```

### 必需的环境变量

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 前端 API URL（用于 Vite）
VITE_API_URL=http://localhost:8000

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/qbm_ai_system

# Redis 配置
REDIS_URL=redis://:password@localhost:6379/0

# JWT 密钥（必须修改为安全值）
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-minimum-32-characters-long
```

## 常见问题

### 问题1: 端口被占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr :8000

# Linux/Mac: 查找占用端口的进程
lsof -i :8000

# 结束进程（替换 <PID> 为实际进程ID）
# Windows:
taskkill /PID <PID> /F

# Linux/Mac:
kill -9 <PID>
```

### 问题2: 数据库连接失败

**错误信息**: `Could not connect to database`

**解决方案**:
1. 确认 PostgreSQL 服务正在运行
2. 检查 `.env` 文件中的 `DATABASE_URL` 配置
3. 确认数据库已创建：
   ```bash
   createdb qbm_ai_system
   ```

### 问题3: Redis 连接失败

**错误信息**: `Could not connect to Redis`

**解决方案**:
1. 确认 Redis 服务正在运行
2. 检查 `.env` 文件中的 `REDIS_URL` 配置
3. 测试 Redis 连接：
   ```bash
   redis-cli ping
   ```

### 问题4: 模块导入错误

**错误信息**: `ModuleNotFoundError`

**解决方案**:
```bash
# 安装依赖
pip install -r requirements.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 生产环境部署

### 使用 uvicorn 直接启动

```bash
uvicorn main_optimized:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

### 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/bmos-backend.service`:

```ini
[Unit]
Description=BMOS Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/qbm-ai-system/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main_optimized:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start bmos-backend
sudo systemctl enable bmos-backend
```

## 下一步

1. ✅ 后端服务运行在 http://localhost:8000
2. ✅ 前端可以连接到后端（配置 `VITE_API_URL`）
3. ✅ 测试数据导入功能

## 相关文档

- [后端服务状态检查](./BACKEND_SERVICE_STATUS.md)
- [Lovable 后端配置指南](./LOVABLE_BACKEND_CONFIGURATION.md)

