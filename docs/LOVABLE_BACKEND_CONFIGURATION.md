# Lovable 后端配置指南

本文档说明如何配置后端 FastAPI 服务地址，以便 lovable 完成的前端导入功能能够正确连接后端。

## 配置要求

### 1. 后端 FastAPI 服务

后端 FastAPI 服务必须运行在 **http://localhost:8000**

#### 检查后端配置

后端配置在 `backend/src/config/unified.py` 中，默认端口为 8000：

```python
api_port: int = Field(default=8000, env="API_PORT")
```

#### 启动后端服务

```bash
cd backend
uvicorn main_optimized:app --host 0.0.0.0 --port 8000 --reload
```

或者使用环境变量：

```bash
export API_PORT=8000
uvicorn main_optimized:app --host 0.0.0.0 --port $API_PORT --reload
```

### 2. 前端环境变量配置

#### 创建 `.env` 文件

在项目根目录（`qbm-ai-system/`）创建 `.env` 文件：

```bash
cp env.example .env
```

#### 配置 VITE_API_URL

在 `.env` 文件中添加或修改以下配置：

```env
# Frontend API URL Configuration (for Vite)
VITE_API_URL=http://localhost:8000
```

#### 完整 `.env` 配置示例

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend API URL Configuration (for Vite)
VITE_API_URL=http://localhost:8000

# Database Configuration
POSTGRES_PASSWORD=qbm_password_2024
DATABASE_URL=postgresql://postgres:qbm_password_2024@localhost:5432/qbm_ai_system

# Redis Configuration
REDIS_PASSWORD=redis_password_2024
REDIS_URL=redis://:redis_password_2024@localhost:6379/0

# Security (REQUIRED - Generate secure keys for production)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-minimum-32-characters-long
```

### 3. 前端代码使用

前端代码已经更新为支持 `VITE_API_URL` 环境变量：

**文件**: `frontend/src/services/api.ts`

```typescript
// 优先使用 VITE_API_URL，如果不存在则使用 VITE_API_BASE_URL（向后兼容）
const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

### 4. 验证配置

#### 检查后端服务

访问后端健康检查端点：

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

#### 检查前端配置

在前端代码中，可以通过以下方式验证：

```typescript
console.log('API Base URL:', import.meta.env.VITE_API_URL);
```

### 5. 开发环境启动顺序

1. **启动后端服务**：
   ```bash
   cd backend
   uvicorn main_optimized:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **启动前端服务**：
   ```bash
   npm run dev
   ```

3. **验证连接**：
   - 打开浏览器开发者工具
   - 查看 Network 标签
   - 确认 API 请求发送到 `http://localhost:8000`

### 6. 常见问题

#### 问题 1: 前端无法连接到后端

**解决方案**：
- 确认后端服务正在运行：`curl http://localhost:8000/health`
- 检查 `.env` 文件中的 `VITE_API_URL` 配置
- 确认 CORS 配置允许前端域名

#### 问题 2: CORS 错误

**解决方案**：
在 `.env` 文件中添加前端地址到 CORS 配置：

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

#### 问题 3: 环境变量未生效

**解决方案**：
- 重启前端开发服务器（Vite 需要重启才能读取新的环境变量）
- 确认 `.env` 文件在项目根目录
- 确认变量名以 `VITE_` 开头

### 7. 生产环境配置

生产环境配置应使用实际的后端服务地址：

```env
VITE_API_URL=https://api.yourdomain.com
```

## 总结

- ✅ 后端服务运行在 `http://localhost:8000`
- ✅ `.env` 文件中配置 `VITE_API_URL=http://localhost:8000`
- ✅ 前端代码已更新支持 `VITE_API_URL`
- ✅ 重启前端开发服务器使配置生效

配置完成后，lovable 开发的导入功能应该能够正常连接到后端 FastAPI 服务。

