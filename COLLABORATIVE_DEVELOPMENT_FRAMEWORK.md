# Cursor与Lovable协同开发框架

## 🎯 协同开发目标

建立Cursor与Lovable的协同开发环境，实现高效分工合作：

- **Lovable负责**: 前端开发、数据库设计、UI/UX实现
- **Cursor负责**: 需求梳理、后端逻辑、业务分析、系统架构设计

## 📋 分工职责

### Lovable职责范围
- ✅ **前端开发**: React 19 + Vite + TypeScript + Tailwind CSS + shadcn/ui
- ✅ **UI/UX实现**: 用户界面、交互设计、响应式布局
- ✅ **前端组件**: 图表组件、表单组件、导航组件
- ✅ **前端路由**: 页面路由、状态管理
- ✅ **后端开发**: Supabase Edge Functions (Deno Runtime, 非Next.js)
- ✅ **API实现**: 轻量级业务逻辑、简单CRUD、快速响应（执行时间≤10秒，O(n)复杂度）
- ✅ **前端测试**: 组件测试、集成测试
- ✅ **后端测试**: Edge Function单元测试
- ✅ **数据库设计**: Supabase PostgreSQL + Row Level Security + Real-time
- ✅ **Supabase集成**: 数据库配置、实时订阅、认证、Edge Functions部署

### Cursor职责范围
- 🎯 **需求梳理**: 业务需求分析、功能规格定义
- 🎯 **系统架构**: 整体架构设计、模块划分
- 🎯 **业务分析**: 商业模式分析、算法设计
- 🎯 **API设计**: RESTful API、数据模型设计
- 🎯 **算法设计**: 归因算法、机器学习模型设计
- 🎯 **技术指导**: 提供算法实现指导和技术支持
- 🎯 **文档编写**: 技术文档、API文档、算法文档
- 🎯 **质量保证**: 代码审查、架构审查、性能优化建议

## 🔄 协同工作流

### 1. 需求梳理阶段 (Cursor主导)
```
Cursor工作:
├── 业务需求分析
├── 功能规格定义
├── API接口设计
├── 数据模型设计
└── 技术架构规划

输出文档:
├── 需求规格说明书
├── API接口文档
├── 数据库设计文档
└── 系统架构文档
```

### 2. 开发实现阶段 (Lovable主导)
```
Lovable工作:
├── 前端界面实现 (React + Vite)
├── 后端API实现 (Supabase Edge Functions - 轻量级逻辑)
├── 数据库表创建 (Supabase PostgreSQL)
├── UI组件开发
├── 业务逻辑开发 (Edge Functions + FastAPI混合架构)
└── 前后端功能集成

Cursor协助:
├── 复杂算法实现 (FastAPI端点)
├── 技术架构审查
├── 代码质量审查
└── 性能优化建议
```

### 3. 集成测试阶段 (共同协作)
```
共同工作:
├── 前后端集成测试
├── 功能验证
├── 性能测试
└── 问题修复
```

## 📁 项目结构分工

### Lovable负责的目录
```
src/                          # React前端源码 (Vite)
├── components/               # React组件
├── pages/                    # 页面组件
│   └── [页面组件]
├── hooks/                    # 自定义Hooks
├── lib/                      # 工具库
└── types/                    # TypeScript类型定义

supabase/
├── functions/                # Supabase Edge Functions
│   ├── value-chain/         # 价值链分析API (轻量级)
│   ├── attribution/         # 归因分析API (简单查询)
│   ├── optimization/        # 优化建议API (CRUD)
│   └── decision/            # 决策管理API (状态管理)
└── migrations/              # 数据库迁移文件

public/                       # 静态资源
├── favicon.ico
├── placeholder.svg
└── robots.txt

# Lovable配置文件
package.json                 # 项目依赖配置
vite.config.ts               # Vite构建配置
tailwind.config.ts           # Tailwind CSS配置
tsconfig.json                # TypeScript配置
```

### Cursor负责的目录
```
docs/                       # 文档
├── requirements/           # 需求文档
├── api/                   # API文档
├── architecture/          # 架构文档
├── business/              # 业务文档
└── algorithms/            # 算法文档

algorithms/                 # 算法实现指导
├── shapley/               # Shapley归因算法
├── optimization/          # 优化算法
├── prediction/            # 预测算法
└── decision/              # 决策算法

research/                   # 研究资料
├── papers/                # 相关论文
├── benchmarks/            # 性能基准
└── experiments/           # 实验数据

scripts/                    # 工具脚本
├── analysis/              # 分析脚本
├── testing/               # 测试脚本
└── deployment/            # 部署脚本

# 部署配置
docker-compose.yml          # Docker编排
.github/workflows/          # CI/CD配置
```

## 🎯 Cursor需求梳理工作重点

### 1. 商业模式动态优化需求分析
- **价值链分析需求**: 如何量化价值链各环节效率
- **归因分析需求**: 如何计算各渠道/活动的贡献度
- **决策管理需求**: 如何实现层级决策管理
- **效果评估需求**: 如何量化决策效果

### 2. 技术架构需求设计
- **API接口设计**: RESTful API规范、数据格式
- **数据模型设计**: 数据库表结构、关系设计
- **业务逻辑设计**: 核心算法、计算逻辑
- **集成需求设计**: 前后端集成、第三方集成

### 3. 功能模块需求定义
- **模块1: 全链条价值传递**
  - 价值链分析引擎需求
  - 归因分析算法需求
  - 优化建议生成需求

- **模块2: 动态管理脉络**
  - 数据采集需求
  - 指标计算需求
  - 分析报告需求

- **模块3: 利益协同与风险管控**
  - 价值贡献计算需求
  - 利益分配算法需求
  - 风险监控需求

- **模块4: 现金流健康管理**
  - 现金流分析需求
  - NPV计算需求
  - 健康评估需求

- **模块5: 关键量化方法应用**
  - TOC瓶颈定位需求
  - 边际分析需求
  - 价值增量计算需求

- **模块6: 决策管理支撑系统**
  - 层级决策管理需求
  - 决策追溯需求
  - 定期报告需求

## 📝 需求梳理输出模板

### 功能需求文档模板
```markdown
# [功能名称] 需求规格说明书

## 1. 功能概述
- 功能描述
- 业务价值
- 用户角色

## 2. 功能需求
- 功能列表
- 输入输出
- 业务规则

## 3. 技术需求
- API接口
- 数据模型
- 算法逻辑

## 4. 验收标准
- 功能验收
- 性能验收
- 质量验收
```

### API接口文档模板
```markdown
# [模块名称] API接口文档

## 接口列表
- GET /api/v1/[module]/[resource]
- POST /api/v1/[module]/[resource]
- PUT /api/v1/[module]/[resource]
- DELETE /api/v1/[module]/[resource]

## 数据模型
- 请求参数
- 响应格式
- 错误码

## 示例
- 请求示例
- 响应示例
```

## 🔧 开发环境配置

### Cursor开发环境
```bash
# 后端开发环境
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 文档生成
cd docs
mkdocs serve
```

### Lovable开发环境
```bash
# 前端开发环境
npm install
npm run dev

# 数据库开发环境
docker-compose -f docker-compose-dev.yml up -d
```

## 📊 协同开发检查清单

### Cursor工作检查清单
- [ ] 需求规格说明书完成
- [ ] API接口文档完成
- [ ] 数据模型设计完成
- [ ] 业务逻辑实现完成
- [ ] 后端测试完成
- [ ] 技术文档更新完成

### Lovable工作检查清单
- [ ] 前端界面实现完成
- [ ] 数据库表创建完成
- [ ] UI组件开发完成
- [ ] 前端功能集成完成
- [ ] 前端测试完成
- [ ] 用户界面优化完成

## 🚀 下一步行动

### 立即开始的工作
1. **Cursor**: 开始详细的需求梳理工作
2. **Lovable**: 等待Cursor的需求输出，准备前端开发
3. **共同**: 建立沟通机制，确保信息同步

### 沟通机制
- **需求变更**: 通过GitHub Issues进行沟通
- **技术讨论**: 通过GitHub Discussions进行讨论
- **进度同步**: 通过GitHub Projects进行跟踪

---

**这个协同开发框架确保Cursor专注于需求梳理和后端逻辑，Lovable专注于前端和数据库开发，实现高效分工合作！** 🎉
