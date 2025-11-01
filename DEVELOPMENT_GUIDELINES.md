# BMOS系统开发指南

## 📋 项目概述

**BMOS (Business Model Quantitative Optimization System)** - 商业模式量化优化系统

### 技术栈
- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: FastAPI + Python 3.11
- **数据库**: PostgreSQL (关系型数据库)
- **缓存**: Redis
- **容器化**: Docker + Docker Compose

## 🏗️ 项目结构

```
qbm-ai-system/
├── backend/                 # 后端服务
│   ├── src/                # 源代码
│   │   ├── api/           # API端点
│   │   ├── services/      # 业务服务
│   │   ├── algorithms/    # 算法模块
│   │   ├── security/     # 安全模块
│   │   ├── config/       # 配置管理
│   │   └── main.py       # 主应用
│   ├── tests/             # 测试文件
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile        # Docker配置
├── frontend/              # 前端应用
│   ├── src/              # 源代码
│   ├── public/           # 静态资源
│   ├── package.json      # Node.js依赖
│   └── Dockerfile        # Docker配置
├── database/             # 数据库脚本
│   └── postgresql/       # PostgreSQL脚本
├── docker-compose.yml    # Docker编排
├── env.example           # 环境变量示例
└── docs/                # 文档
```

## 🚀 快速开始

### 1. 环境准备

#### 系统要求
- Docker Desktop
- Node.js 18+
- Python 3.11+

#### 克隆项目
```bash
git clone <repository-url>
cd qbm-ai-system
```

### 2. 环境配置

#### 复制环境变量文件
```bash
cp env.example .env
```

#### 编辑环境变量
```bash
# 数据库配置
POSTGRES_PASSWORD=qbm_password
REDIS_PASSWORD=redis_password

# 应用配置
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key-here

# API配置
API_V1_STR=/api/v1
PROJECT_NAME=BMOS AI System
```

### 3. 启动服务

#### 使用Docker Compose
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 服务访问地址
- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🔧 开发环境

### 1. 后端开发

#### 本地开发
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 测试
```bash
cd backend
pytest tests/ -v
```

#### 代码质量
```bash
# 代码格式化
black src/
isort src/

# 类型检查
mypy src/

# 代码检查
flake8 src/
```

### 2. 前端开发

#### 本地开发
```bash
cd frontend
npm install
npm run dev
```

#### 测试
```bash
cd frontend
npm test
npm run test:coverage
```

#### 代码质量
```bash
# 代码格式化
npm run format

# 代码检查
npm run lint
npm run lint:fix

# 类型检查
npm run type-check
```

## 🗄️ 数据库管理

### 1. 数据库连接

#### PostgreSQL连接
```bash
# 使用Docker连接
docker exec -it qbm-postgres psql -U postgres -d qbm_ai_system

# 本地连接
psql -h localhost -p 5432 -U postgres -d qbm_ai_system
```

### 2. 数据库操作

#### 创建表
```bash
# 运行初始化脚本
docker exec -i qbm-postgres psql -U postgres -d qbm_ai_system < database/postgresql/01_init.sql
```

#### 数据迁移
```bash
# 运行迁移脚本
python backend/src/scripts/database_migration.py
```

### 3. 数据备份

#### 备份数据库
```bash
docker exec qbm-postgres pg_dump -U postgres qbm_ai_system > backup.sql
```

#### 恢复数据库
```bash
docker exec -i qbm-postgres psql -U postgres -d qbm_ai_system < backup.sql
```

## 🧪 测试策略

### 1. 单元测试

#### 后端测试
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### 前端测试
```typescript
// tests/components.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../src/App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('BMOS System')).toBeInTheDocument()
  })
})
```

### 2. 集成测试

#### API集成测试
```python
def test_model_training_api():
    response = client.post("/api/v1/models/train", json={
        "model_type": "marginal_analysis",
        "data": test_data
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### 3. 端到端测试

#### 使用Cypress
```typescript
// cypress/e2e/basic.cy.ts
describe('Basic functionality', () => {
  it('should load the homepage', () => {
    cy.visit('/')
    cy.contains('BMOS System').should('be.visible')
  })
})
```

## 📊 监控和日志

### 1. 应用监控

#### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
curl http://localhost:8000/health/database
```

### 2. 日志管理

#### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 日志配置
```python
# backend/src/logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

## 🚀 部署指南

### 1. 生产环境部署

#### 环境变量配置
```bash
# 生产环境变量
ENVIRONMENT=production
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
POSTGRES_PASSWORD=strong-production-password
```

#### Docker部署
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_fact_order_date ON fact_order(order_date);
CREATE INDEX idx_fact_order_tenant ON fact_order(tenant_id);

-- 分区表
CREATE TABLE fact_order_partitioned (
    LIKE fact_order INCLUDING ALL
) PARTITION BY RANGE (order_date);
```

#### 缓存配置
```python
# Redis缓存配置
CACHE_TTL = 3600  # 1小时
CACHE_MAX_SIZE = 1000
```

## 🔒 安全配置

### 1. 认证授权

#### JWT配置
```python
# JWT配置
JWT_SECRET_KEY = "your-super-secure-jwt-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

#### 权限控制
```python
# 权限装饰器
@require_permission(Permission.READ_DATA)
async def get_data():
    pass
```

### 2. 数据安全

#### 行级安全
```sql
-- 启用RLS
ALTER TABLE fact_order ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY tenant_isolation ON fact_order
    USING (tenant_id = current_setting('app.current_tenant_id'));
```

## 📚 API文档

### 1. API端点

#### 模型训练
```http
POST /api/v1/models/train
Content-Type: application/json

{
  "model_type": "marginal_analysis",
  "data": {...},
  "tenant_id": "tenant_001"
}
```

#### 预测服务
```http
POST /api/v1/predictions/predict
Content-Type: application/json

{
  "model_id": "model_123",
  "input_data": {...},
  "tenant_id": "tenant_001"
}
```

### 2. 响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "模型不存在",
    "details": {...}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🐛 故障排除

### 1. 常见问题

#### 数据库连接失败
```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 重启PostgreSQL
docker-compose restart postgres
```

#### 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 修改端口
# 在docker-compose.yml中修改端口映射
```

### 2. 调试技巧

#### 查看详细日志
```bash
# 启用调试模式
export LOG_LEVEL=DEBUG
docker-compose up
```

#### 进入容器调试
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U postgres -d qbm_ai_system
```

## 📞 支持与联系

### 技术支持
- **邮箱**: support@bmos.ai
- **文档**: https://docs.bmos.ai
- **GitHub**: https://github.com/bmos/bmos-ai-system

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

**注意**: 本指南会持续更新，请定期查看最新版本。