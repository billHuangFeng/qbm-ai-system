# QBM历史数据拟合优化系统

## 项目概述

QBM历史数据拟合优化系统是一个基于机器学习的边际影响分析系统，专门用于分析企业核心资产、核心能力和产品价值之间的复杂关系。系统采用动态权重优化算法，能够自动识别和量化各种非线性关系，为企业决策提供数据支持。

## 核心功能

### 1. 数据关系分析
- **协同效应分析**: 识别特征间的协同作用
- **阈值效应分析**: 发现关键阈值点
- **时间滞后分析**: 分析时间序列中的滞后效应
- **高级关系识别**: 使用机器学习识别复杂非线性关系

### 2. 动态权重优化
- **多种权重计算方法**: 相关性、重要性、回归系数、时间序列
- **6种优化算法**: 梯度下降、遗传算法、模拟退火、粒子群、贝叶斯、约束优化
- **多目标优化**: 同时优化R²、MSE、MAE等指标
- **权重验证**: 交叉验证、自助法、时间序列验证等

### 3. 权重监控系统
- **实时监控**: 性能、权重漂移、稳定性、数据质量
- **异常检测**: 多维度异常识别和警报
- **监控历史**: 完整的监控数据记录
- **智能建议**: 基于监控数据的优化建议

## 技术架构

### 后端技术栈
- **Python 3.11+**: 主要开发语言
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和实时数据处理
- **Docker**: 容器化部署

### 前端技术栈
- **React 18**: 用户界面框架
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 样式框架
- **Vite**: 构建工具

### 微服务架构
- **数据预处理服务**: 数据清洗和特征工程
- **模型训练服务**: 机器学习模型训练
- **预测服务**: 实时预测和推理
- **优化服务**: 权重优化和参数调优

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (本地开发)
- Node.js 18+ (本地开发)

### 安装部署

1. **克隆项目**
```bash
git clone <repository-url>
cd qbm-ai-system
```

2. **开发环境部署**
```bash
./deploy.sh dev
```

3. **生产环境部署**
```bash
./deploy.sh prod
```

### 本地开发

1. **后端开发**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. **前端开发**
```bash
cd frontend
npm install
npm run dev
```

## API文档

### 核心API端点

#### 数据关系分析
```http
POST /api/v1/models/analyze
Content-Type: application/json

{
  "data": {
    "features": {
      "feature1": [1, 2, 3, ...],
      "feature2": [4, 5, 6, ...]
    },
    "target": [10, 20, 30, ...]
  },
  "analysis_types": ["synergy", "threshold", "lag", "advanced"]
}
```

#### 权重优化
```http
POST /api/v1/models/optimize-weights
Content-Type: application/json

{
  "data": {
    "features": {...},
    "target": [...]
  },
  "optimization_method": "comprehensive",
  "validation_methods": ["cross_validation", "bootstrap"]
}
```

#### 预测
```http
POST /api/v1/models/predict
Content-Type: application/json

{
  "data": {
    "features": {...},
    "target": [...],
    "test_features": {...}
  },
  "weights": {
    "feature1": 0.5,
    "feature2": 0.3,
    "feature3": 0.2
  }
}
```

## 算法详解

### 动态权重计算

系统支持多种权重计算方法：

1. **相关性权重**: 基于Pearson相关系数
2. **重要性权重**: 基于随机森林特征重要性
3. **回归权重**: 基于线性回归系数
4. **时间序列权重**: 基于滞后相关性
5. **综合权重**: 多方法加权平均

### 优化算法

1. **梯度下降**: L-BFGS-B算法
2. **遗传算法**: 差分进化
3. **模拟退火**: 双重退火
4. **粒子群优化**: PSO算法
5. **贝叶斯优化**: 高斯过程
6. **约束优化**: SLSQP算法

### 验证方法

1. **交叉验证**: 5折交叉验证
2. **自助法**: Bootstrap重采样
3. **时间序列验证**: 时间序列交叉验证
4. **稳定性验证**: 噪声鲁棒性测试
5. **敏感性分析**: 权重变化影响
6. **鲁棒性测试**: 数据子集测试

## 监控和运维

### 系统监控
- **Prometheus**: 指标收集
- **Grafana**: 可视化面板
- **Loki**: 日志聚合
- **健康检查**: 自动服务监控

### 日志管理
- **结构化日志**: JSON格式日志
- **日志级别**: DEBUG, INFO, WARNING, ERROR
- **日志轮转**: 自动日志清理
- **集中收集**: 统一日志管理

### 性能优化
- **缓存策略**: Redis缓存
- **数据库优化**: 索引优化
- **负载均衡**: Nginx反向代理
- **容器优化**: Docker镜像优化

## 测试

### 运行测试
```bash
# 单元测试
python -m pytest backend/tests/unit/ -v

# 集成测试
python -m pytest backend/tests/integration/ -v

# 所有测试
python -m pytest backend/tests/ -v
```

### 测试覆盖
- **单元测试**: 算法模块测试
- **集成测试**: API接口测试
- **性能测试**: 大数据量测试
- **端到端测试**: 完整工作流测试

## 部署指南

### 开发环境
```bash
# 启动开发环境
./deploy.sh dev

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境
```bash
# 启动生产环境
./deploy.sh prod

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 监控面板
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@host:port/database

# Redis配置
REDIS_URL=redis://host:port/db

# JWT配置
JWT_SECRET_KEY=your-secret-key

# 日志级别
LOG_LEVEL=INFO
```

### 数据库配置
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和会话存储
- **多租户**: 租户隔离
- **数据版本**: 数据版本管理

## 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request
5. 代码审查
6. 合并代码

### 代码规范
- **Python**: PEP 8规范
- **TypeScript**: ESLint规范
- **Git**: 语义化提交
- **文档**: Markdown格式

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- **项目维护者**: QBM团队
- **技术支持**: support@qbm.com
- **问题反馈**: GitHub Issues

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 核心算法实现
- API接口完成
- 基础监控功能

### 未来计划
- 更多机器学习算法
- 实时数据流处理
- 高级可视化功能
- 企业级安全特性