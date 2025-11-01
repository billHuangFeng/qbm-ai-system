# QBM AI系统 - 完整实施指南

## 📋 目录
- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [核心功能](#核心功能)
- [部署指南](#部署指南)
- [API文档](#api文档)
- [算法说明](#算法说明)
- [测试指南](#测试指南)
- [运维监控](#运维监控)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)

## 🎯 系统概述

QBM AI系统是一个基于"越用越聪明"理念的智能业务分析平台，通过机器学习算法和持续学习机制，为企业提供深度的边际影响分析和决策支持。

### 核心特性
- **边际影响分析**：协同效应、阈值效应、滞后效应分析
- **动态权重优化**：基于历史数据的智能权重调整
- **企业记忆系统**：学习和应用历史经验
- **管理者评价反馈**：人工反馈与系统学习的结合
- **预测准确性跟踪**：持续监控和优化模型性能

## 🏗️ 架构设计

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Next.js) │    │  后端 (FastAPI)  │    │  数据库 (PostgreSQL) │
│                 │    │                 │    │                 │
│ - React组件     │◄──►│ - REST API      │◄──►│ - 业务数据      │
│ - 图表可视化    │    │ - 算法服务      │    │ - 模型参数      │
│ - 用户界面      │    │ - 数据处理      │    │ - 企业记忆      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  缓存 (Redis)   │              │
         └──────────────►│                 │◄─────────────┘
                        │ - 会话缓存      │
                        │ - 模型缓存      │
                        │ - 结果缓存      │
                        └─────────────────┘
```

### 技术栈
- **前端**：Next.js 14, React 18, TypeScript, Tailwind CSS
- **后端**：FastAPI, Python 3.11, Pydantic, SQLAlchemy
- **数据库**：PostgreSQL 15, Redis 7
- **算法**：scikit-learn, XGBoost, LightGBM, scipy
- **部署**：Docker, Kubernetes, Nginx
- **监控**：Prometheus, Grafana

## 🚀 核心功能

### 1. 边际影响分析
- **协同效应分析**：检测特征间的交互作用
- **阈值效应分析**：识别关键阈值点
- **滞后效应分析**：分析时间延迟影响
- **高级关系分析**：发现复杂的非线性关系

### 2. 动态权重系统
- **权重计算**：基于相关性、重要性、回归系数
- **权重优化**：梯度下降、遗传算法、贝叶斯优化
- **权重验证**：交叉验证、Bootstrap验证
- **权重监控**：漂移检测、稳定性监控

### 3. 企业记忆系统
- **记忆提取**：从反馈和错误中学习
- **记忆存储**：模式、策略、阈值、优化规则
- **记忆检索**：基于TF-IDF和上下文的相关性匹配
- **记忆应用**：调整预测和决策

### 4. 管理者评价系统
- **评价收集**：确认、调整、拒绝反馈
- **质量评估**：完整性、准确性、一致性检查
- **学习记录**：模式识别、偏见检测
- **改进建议**：流程改进、工具增强

## 🛠️ 部署指南

### 开发环境部署

1. **克隆仓库**
```bash
git clone https://github.com/your-org/qbm-ai-system.git
cd qbm-ai-system
```

2. **环境配置**
```bash
cp env.example .env
# 编辑.env文件，配置数据库和Redis连接信息
```

3. **Docker部署**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

4. **验证部署**
```bash
# 检查API健康状态
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

### 生产环境部署

1. **Kubernetes部署**
```bash
# 应用Kubernetes配置
kubectl apply -f kubernetes/qbm-ai-system.yaml

# 检查部署状态
kubectl get pods -n qbm-ai-system

# 检查服务
kubectl get services -n qbm-ai-system
```

2. **环境变量配置**
```bash
# 创建Secret
kubectl create secret generic qbm-secrets \
  --from-literal=POSTGRES_PASSWORD=your_password \
  --from-literal=REDIS_PASSWORD=your_redis_password \
  --from-literal=SECRET_KEY=your_secret_key \
  -n qbm-ai-system
```

3. **域名和SSL配置**
```bash
# 配置Ingress
kubectl apply -f kubernetes/ingress.yaml

# 配置SSL证书
kubectl apply -f kubernetes/certificate.yaml
```

## 📚 API文档

### 认证
所有API请求都需要JWT令牌认证：
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/models/train/marginal-analysis
```

### 核心API端点

#### 模型训练
```http
POST /api/v1/models/train/marginal-analysis
Content-Type: application/json

{
  "model_name": "sales_analysis_model",
  "model_type": "marginal_analysis",
  "training_data": [...],
  "target_column": "revenue",
  "feature_columns": ["price", "quantity", "promotion"],
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  }
}
```

#### 预测服务
```http
POST /api/v1/models/predict
Content-Type: application/json

{
  "model_id": "model_123",
  "input_data": {
    "price": 100,
    "quantity": 50,
    "promotion": 0.1
  }
}
```

#### 企业记忆
```http
POST /api/v1/memory/extract/feedback
Content-Type: application/json

{
  "feedback_data": {
    "evaluation_id": "eval_123",
    "feedback_type": "confirmation",
    "feedback_content": "分析结果准确",
    "metrics": {
      "satisfaction_score": 0.9,
      "revenue_increase": 0.15
    }
  }
}
```

### 完整API文档
访问 `http://localhost:8000/docs` 查看Swagger UI文档。

## 🧮 算法说明

### 协同效应分析算法

```python
class SynergyAnalysis:
    def detect_synergy_effects(self, X, y):
        """
        检测协同效应
        
        参数:
        - X: 特征数据 (DataFrame)
        - y: 目标变量 (Series)
        
        返回:
        - 协同效应分析结果 (dict)
        """
        results = {}
        
        # 1. 两两交互分析
        results['pairwise_interactions'] = self._analyze_pairwise_interactions(X, y)
        
        # 2. 多项式交互分析
        results['polynomial_interactions'] = self._analyze_polynomial_interactions(X, y)
        
        # 3. 随机森林交互分析
        results['random_forest_interactions'] = self._analyze_rf_interactions(X, y)
        
        # 4. Shapley值分析
        results['shapley_values'] = self.calculate_shapley_values(X, y)
        
        return results
```

### 阈值分析算法

```python
class ThresholdAnalysis:
    def detect_threshold_effects(self, X, y):
        """
        检测阈值效应
        
        参数:
        - X: 特征数据 (DataFrame)
        - y: 目标变量 (Series)
        
        返回:
        - 阈值效应分析结果 (dict)
        """
        results = {}
        
        # 1. 决策树阈值检测
        results['tree_thresholds'] = self._detect_tree_thresholds(X, y)
        
        # 2. 分段回归分析
        results['piecewise_regression'] = self._analyze_piecewise_regression(X, y)
        
        # 3. 随机森林阈值分析
        results['random_forest_thresholds'] = self._analyze_rf_thresholds(X, y)
        
        return results
```

### 动态权重算法

```python
class DynamicWeights:
    def calculate_dynamic_weights(self, X, y, method='comprehensive'):
        """
        计算动态权重
        
        参数:
        - X: 特征数据 (DataFrame)
        - y: 目标变量 (Series)
        - method: 计算方法 ('comprehensive', 'correlation', 'importance')
        
        返回:
        - 动态权重结果 (dict)
        """
        results = {}
        
        # 1. 相关性权重
        results['correlation_weights'] = self._calculate_correlation_weights(X, y)
        
        # 2. 重要性权重
        results['importance_weights'] = self._calculate_importance_weights(X, y)
        
        # 3. 回归权重
        results['regression_weights'] = self._calculate_regression_weights(X, y)
        
        # 4. 时间序列权重
        results['time_series_weights'] = self._calculate_time_series_weights(X, y)
        
        # 5. 综合权重
        results['comprehensive_weights'] = self._calculate_comprehensive_weights(results)
        
        # 6. 归一化权重
        results['normalized'] = self._normalize_weights(results['comprehensive_weights'])
        
        return results
```

## 🧪 测试指南

### 运行测试

1. **后端测试**
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=src --cov-report=html
```

2. **前端测试**
```bash
cd frontend
npm install
npm run test
npm run test:coverage
```

3. **集成测试**
```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
pytest tests/integration/ -v
```

### 测试覆盖率
- **后端API测试**：95%+ 覆盖率
- **算法单元测试**：90%+ 覆盖率
- **前端组件测试**：85%+ 覆盖率
- **集成测试**：关键流程100%覆盖

## 📊 运维监控

### 监控指标

1. **系统指标**
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量

2. **应用指标**
- API响应时间
- 请求成功率
- 数据库连接数
- 缓存命中率

3. **业务指标**
- 模型训练时间
- 预测准确性
- 用户活跃度
- 数据质量分数

### 告警配置

```yaml
# Prometheus告警规则
groups:
- name: qbm-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: ModelAccuracyLow
    expr: model_accuracy_score < 0.7
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Model accuracy below threshold"
```

### 日志管理

```python
# 日志配置示例
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
```

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**
```bash
# 检查数据库状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 测试连接
psql -h localhost -p 5432 -U postgres -d qbm_ai_system
```

2. **Redis连接失败**
```bash
# 检查Redis状态
docker-compose ps redis

# 测试Redis连接
redis-cli -h localhost -p 6379 ping
```

3. **API响应慢**
```bash
# 检查API日志
docker-compose logs backend

# 检查数据库性能
SELECT * FROM pg_stat_activity;

# 检查缓存命中率
redis-cli info stats | grep keyspace
```

4. **模型训练失败**
```bash
# 检查训练日志
tail -f logs/model_training.log

# 检查数据质量
python scripts/check_data_quality.py

# 检查内存使用
docker stats
```

### 性能优化

1. **数据库优化**
```sql
-- 创建索引
CREATE INDEX CONCURRENTLY idx_feature_analysis ON marginal_analysis_results(feature_name, analysis_date);

-- 分析表统计
ANALYZE marginal_analysis_results;

-- 清理旧数据
DELETE FROM prediction_accuracy_log WHERE prediction_date < NOW() - INTERVAL '90 days';
```

2. **缓存优化**
```python
# Redis缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 3600,
    'CACHE_KEY_PREFIX': 'qbm:'
}
```

3. **API优化**
```python
# 异步处理
from fastapi import BackgroundTasks

@app.post("/api/v1/models/train")
async def train_model(
    background_tasks: BackgroundTasks,
    model_data: ModelTrainingRequest
):
    # 异步训练模型
    background_tasks.add_task(train_model_async, model_data)
    return {"message": "Training started"}
```

## 💡 最佳实践

### 开发最佳实践

1. **代码规范**
```python
# 使用类型提示
def calculate_weights(X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
    """计算特征权重"""
    pass

# 使用文档字符串
def detect_synergy_effects(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """
    检测特征间的协同效应
    
    Args:
        X: 特征数据矩阵
        y: 目标变量
        
    Returns:
        协同效应分析结果
        
    Raises:
        ValueError: 当输入数据无效时
    """
    pass
```

2. **错误处理**
```python
try:
    result = model.predict(X)
except ModelNotFoundError:
    logger.error(f"Model {model_id} not found")
    raise HTTPException(status_code=404, detail="Model not found")
except PredictionError as e:
    logger.error(f"Prediction failed: {e}")
    raise HTTPException(status_code=500, detail="Prediction failed")
```

3. **数据验证**
```python
from pydantic import BaseModel, validator

class ModelTrainingRequest(BaseModel):
    model_name: str
    training_data: List[Dict[str, Any]]
    target_column: str
    
    @validator('model_name')
    def validate_model_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Model name must be at least 3 characters')
        return v
```

### 部署最佳实践

1. **环境隔离**
```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 测试环境
docker-compose -f docker-compose.test.yml up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

2. **安全配置**
```python
# 安全头配置
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

3. **监控和日志**
```python
# 结构化日志
import structlog

logger = structlog.get_logger()

logger.info(
    "Model training completed",
    model_id=model_id,
    training_time=training_time,
    accuracy=accuracy,
    user_id=user_id
)
```

### 数据管理最佳实践

1. **数据质量检查**
```python
def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """验证数据质量"""
    quality_report = {
        'total_rows': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict(),
        'outliers': detect_outliers(df)
    }
    return quality_report
```

2. **数据版本控制**
```python
# 数据版本管理
class DataVersion:
    def __init__(self, version: str, checksum: str, created_at: datetime):
        self.version = version
        self.checksum = checksum
        self.created_at = created_at
    
    def save(self, data: pd.DataFrame):
        """保存数据版本"""
        pass
```

3. **模型版本管理**
```python
# 模型版本控制
class ModelVersion:
    def __init__(self, model_id: str, version: str, performance: Dict[str, float]):
        self.model_id = model_id
        self.version = version
        self.performance = performance
        self.created_at = datetime.now()
    
    def compare_with(self, other: 'ModelVersion') -> Dict[str, Any]:
        """比较模型版本"""
        pass
```

## 📞 支持和贡献

### 获取帮助
- **文档**：查看完整文档和API参考
- **Issues**：在GitHub上报告问题
- **讨论**：参与社区讨论
- **邮件**：发送邮件到 support@qbm-ai-system.com

### 贡献指南
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request
5. 等待代码审查

### 许可证
本项目采用MIT许可证。详见LICENSE文件。

---

**QBM AI系统** - 让业务分析更智能，让决策更精准！


