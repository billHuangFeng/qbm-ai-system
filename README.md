# QBM AI System - AI增强的商业模式量化分析系统

## 项目简介

这是一个AI增强的商业模式量化分析系统，集成了企业专属记忆、商业模式量化分析、滚动预测、动态学习机制等核心功能。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + MySQL
- **前端**: Vue.js 3 + Element Plus + ECharts
- **AI引擎**: scikit-learn + spaCy + pandas
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **部署**: Docker + Docker Compose

## 快速开始

### 1. 环境要求

- Python 3.11+
- Node.js 16+
- Docker & Docker Compose
- MySQL 8.0
- Redis

### 2. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install

# AI引擎依赖
cd ai_engine
pip install -r requirements.txt
```

### 3. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 4. 启动服务

```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 或者分别启动
# 启动数据库和缓存
docker-compose up -d mysql redis

# 启动后端服务
cd backend
uvicorn app.main:app --reload

# 启动前端服务
cd frontend
npm run dev
```

### 5. 访问应用

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
qbm-ai-system/
├── backend/          # 后端服务
├── frontend/         # 前端应用
├── ai_engine/        # AI分析引擎
├── database/         # 数据库相关
└── docker-compose.yml
```

## 开发指南

### 后端开发

1. 创建新的API路由
2. 定义数据模型
3. 实现业务逻辑
4. 编写测试用例

### 前端开发

1. 创建Vue组件
2. 配置路由
3. 实现API调用
4. 添加数据可视化

### AI引擎开发

1. 实现分析算法
2. 训练机器学习模型
3. 优化模型性能
4. 集成到后端服务

## 部署说明

### 生产环境部署

1. 配置生产环境变量
2. 构建Docker镜像
3. 部署到云服务器
4. 配置域名和SSL

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

MIT License
