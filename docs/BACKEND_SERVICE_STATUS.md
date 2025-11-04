# 后端服务状态检查

## 当前状态

### 端口监听状态
- **端口 8000**: 正在监听（LISTENING）
- **进程ID**: 6552 (svchost.exe - Windows服务)

### 健康检查
- **状态**: ❌ 连接失败（连接被拒绝）
- **可能原因**:
  1. 服务未正常启动
  2. 服务配置错误
  3. 防火墙阻止连接
  4. 端口被其他服务占用

## 启动后端服务

### 方法1: 使用 uvicorn 直接启动

```bash
cd backend
uvicorn main_optimized:app --host 0.0.0.0 --port 8000 --reload
```

### 方法2: 使用 Python 脚本启动

```bash
cd backend
python main_optimized.py
```

### 方法3: 使用 Docker Compose

```bash
docker-compose up backend
```

## 验证服务运行

### 1. 检查端口监听

```bash
netstat -ano | findstr :8000
```

应该看到：
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       <PID>
```

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

### 3. API 文档

访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 常见问题

### 问题1: 端口被占用

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F
```

### 问题2: 数据库连接失败

**检查**:
1. PostgreSQL 是否运行
2. 数据库连接配置是否正确（`.env` 文件）
3. 数据库是否已创建

### 问题3: Redis 连接失败

**检查**:
1. Redis 是否运行
2. Redis 连接配置是否正确（`.env` 文件）

## 服务日志

后端服务日志通常输出到：
- 控制台（开发模式）
- `logs/app.log`（生产模式）

查看日志：
```bash
tail -f logs/app.log
```

## 下一步

1. ✅ 确认后端服务正在运行
2. ✅ 验证健康检查端点响应正常
3. ✅ 测试前端是否能连接到后端
4. ✅ 验证数据导入功能是否正常工作

