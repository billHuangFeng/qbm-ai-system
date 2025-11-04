# 后端服务启动指南

## 快速启动

### 方法1: 使用启动脚本（推荐）

**Windows:**
```bash
# 双击运行或在命令行执行
start_backend.bat
```

**Linux/Mac:**
```bash
chmod +x backend/start_server.sh
./backend/start_server.sh
```

### 方法2: 直接运行Python脚本

**简单启动（推荐用于测试）:**
```bash
cd backend
python start_simple.py
```

**完整功能启动:**
```bash
cd backend
python main_optimized.py
```

### 方法3: 使用uvicorn命令

```bash
cd backend
uvicorn main_optimized:app --host 0.0.0.0 --port 8000 --reload
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

### 3. 访问API文档

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. 使用检查脚本

**Windows:**
```bash
check_backend_status.bat
```

## 常见问题

### 问题1: JWT_SECRET_KEY 未配置

**错误信息**: `Field required [type=missing, input_value={}, input_type=dict]`

**解决方案**:
1. 确保 `.env` 文件存在
2. 检查 `.env` 文件中的 `JWT_SECRET_KEY` 配置
3. 如果使用默认值，需要生成一个安全的密钥：

```bash
# 在 .env 文件中设置
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-minimum-32-characters-long
```

### 问题2: 端口被占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换 <PID> 为实际进程ID）
taskkill /PID <PID> /F
```

### 问题3: 数据库连接失败

**错误信息**: `Could not connect to database`

**解决方案**:
1. 确认 PostgreSQL 服务正在运行
2. 检查 `.env` 文件中的数据库配置
3. 确认数据库已创建

### 问题4: Redis 连接失败

**错误信息**: `Could not connect to Redis`

**解决方案**:
1. 确认 Redis 服务正在运行
2. 检查 `.env` 文件中的 Redis 配置

### 问题5: 依赖包未安装

**错误信息**: `ModuleNotFoundError`

**解决方案**:
```bash
cd backend
pip install -r requirements.txt
```

## 服务状态检查

### 使用检查脚本

**Windows:**
```bash
check_backend_status.bat
```

该脚本会检查：
1. 端口 8000 监听状态
2. 健康检查端点响应
3. 显示服务地址

### 手动检查

```bash
# 检查端口
netstat -ano | findstr :8000

# 检查健康状态
curl http://localhost:8000/health

# 检查API文档
curl http://localhost:8000/docs
```

## 服务地址

启动成功后，服务将在以下地址运行：

- **API**: http://localhost:8000
- **健康检查**: http://localhost:8000/health
- **API文档 (Swagger)**: http://localhost:8000/docs
- **API文档 (ReDoc)**: http://localhost:8000/redoc

## 停止服务

### 在运行窗口

按 `Ctrl+C` 停止服务

### 查找并结束进程

```bash
# 查找Python进程
tasklist | findstr python

# 结束进程（替换 <PID> 为实际进程ID）
taskkill /PID <PID> /F
```

## 日志查看

服务日志会输出到：
- 控制台（开发模式）
- `backend/logs/app.log`（如果配置了日志文件）

## 下一步

1. ✅ 确认服务运行在 http://localhost:8000
2. ✅ 验证健康检查端点响应正常
3. ✅ 测试前端是否能连接到后端
4. ✅ 验证数据导入功能是否正常工作

## 相关文档

- [后端服务状态检查](./BACKEND_SERVICE_STATUS.md)
- [快速启动后端](./QUICK_START_BACKEND.md)
- [Lovable 后端配置指南](./LOVABLE_BACKEND_CONFIGURATION.md)

