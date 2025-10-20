# BMOS - 商业模式动态优化与决策管理综合系统

## 🚀 项目简介

BMOS (Business Model Quantitative Optimization System) 是一个AI增强的商业模式量化优化与决策管理综合系统。它以《商业模式动态优化与决策管理综合方案（含全链路追溯）》为核心理论框架，结合现代技术栈，旨在为企业提供数据驱动的商业决策支持，实现全链路价值追溯和动态优化。

## 🎯 核心框架 (6大模块)

系统基于以下六大核心模块构建，确保商业模式的完整性和决策的有效性：

1.  模块1: 全链条价值传递 (价值链分析)
2.  模块2: 动态管理脉络 (数据驱动决策)
3.  模块3: 利益协同与风险管控 (贡献度与风险评估)
4.  模块4: 现金流健康管理 (现金流分析)
5.  模块5: 关键量化方法应用 (归因分析)
6.  模块6: 决策管理支撑系统 (层级决策)

## 🛠️ 技术架构（统一版）

- **前端**: React 19 + TypeScript + Tailwind CSS + shadcn/ui
- **后端**: Next.js 14 API Routes + TypeScript
- **数据库**: PostgreSQL 15 (Supabase)
- **部署**: Vercel (Lovable 原生支持)
- **AI/ML**: TypeScript实现 + 外部Python服务（可选）

## 数据模型

- **原始数据层**: 4张暂存表
- **业务事实层**: 11张决策可控事实表 + 3张外部事实表
- **BMOS核心层**: 27张表（9维度 + 5事实 + 5桥接 + 4分析视图 + 4决策管理）
- **分析结果层**: 3张评价确认表 + 2张循环触发表

**总计**: 50张表

## 🤝 协同开发模式

本项目采用 Cursor 与 Lovable 协同开发模式：

-   **Lovable 负责**: React 前端开发、Supabase/PostgreSQL 数据库设计、UI/UX 设计。
-   **Cursor 负责**: 详细需求梳理、FastAPI 后端逻辑、ClickHouse 数据库设计（如果需要高性能分析）、AI 分析引擎、Docker 部署配置、技术文档编写。

## 🚀 快速开始 (开发环境)

### 1. 环境要求

-   Node.js 18+ (或 Bun)
-   Git
-   Supabase 账户

### 2. 克隆仓库

```bash
git clone https://github.com/billHuangFeng/bmos-insight.git
cd bmos-insight
```

### 3. 安装依赖

```bash
npm install
```

### 4. 配置环境变量

创建 `.env.local` 文件：

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 5. 启动开发服务器

```bash
npm run dev
```

### 6. 访问系统

-   **前端界面**: `http://localhost:3000`
-   **API文档**: `http://localhost:3000/api`

## 📈 系统特性

### 技术特性

-   **高性能**: PostgreSQL数据库，支持复杂查询和分析
-   **实时性**: Supabase实时订阅，毫秒级响应
-   **可扩展**: Next.js全栈架构，支持水平扩展
-   **简化部署**: Vercel一键部署，环境一致性
-   **现代化**: React + TypeScript + Tailwind CSS
-   **完全协同**: Lovable原生支持，前后端统一开发

### 业务特性

-   **理论指导**: 基于完整的商业模式理论框架
-   **数据驱动**: 全链路数据追溯和分析
-   **决策支持**: 层级决策管理和效果评估
-   **智能优化**: AI驱动的归因分析和优化建议
-   **全链路追溯**: 从决策到执行到结果的完整追溯

## 📚 文档结构

-   `docs/requirements/`: 详细的需求规格说明书
-   `docs/architecture/`: 系统架构设计文档
-   `docs/development/`: 开发指南
-   `docs/testing/`: 测试策略与指南
-   `docs/deployment/`: 部署指南

## 🔧 开发指南

### 项目结构

```
qbm-ai-system/
├── src/                          # React前端源码
│   ├── components/               # React组件
│   ├── pages/                   # 页面组件 + API Routes
│   │   ├── api/                # Next.js API Routes
│   │   │   ├── data-import/    # 数据导入API
│   │   │   ├── decision-cycle/ # 决策循环API
│   │   │   ├── manager-evaluation/ # 管理者评价API
│   │   │   └── analysis/       # 分析引擎API
│   │   └── [页面组件]
│   ├── hooks/                   # 自定义Hooks
│   ├── lib/                     # 工具库
│   └── types/                   # TypeScript类型定义
├── database/                    # 数据库Schema
│   └── postgresql/             # PostgreSQL表结构
├── docs/                       # 文档
└── package.json                # 项目配置
```

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/billHuangFeng/bmos-insight.git
cd bmos-insight

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📞 技术支持

### 常见问题

- 查看 `docs/` 目录下的相关文档
- 检查 Supabase 项目配置
- 确认环境变量设置

### 系统监控

- 访问 `http://localhost:3000` 使用前端界面
- 访问 `http://localhost:3000/api/health` 检查API健康状态
- 查看 Supabase 仪表板监控数据库状态

## 📄 许可证

详见 [LICENSE](LICENSE) 文件。

---

**这个系统将理论框架、技术实现和实际应用完美结合，采用统一的技术架构，为企业提供完整的商业模式动态优化解决方案！** 🎉