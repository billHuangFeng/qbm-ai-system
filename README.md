# BMOS AI System - 商业模式动态优化与决策管理综合系统

## 🎯 系统概述

本系统以《商业模式动态优化与决策管理综合方案》为核心理论框架，采用React-centric架构，整合了BMOS系统、integrated_business_model_system和QBM系统的技术优势，打造企业级商业模式动态优化平台。

## 📊 核心架构

### 理论框架 (6大模块)
```
模块1: 全链条价值传递 (价值链分析)
模块2: 动态管理脉络 (数据驱动)
模块3: 利益协同与风险管控 (利益分配)
模块4: 现金流健康管理 (现金流分析)
模块5: 关键量化方法应用 (归因分析)
模块6: 决策管理支撑系统 (层级决策)
```

### 技术架构 (Next.js全栈)
- **前端**: React + TypeScript + Tailwind CSS + shadcn/ui + Recharts
- **后端**: Next.js API Routes + TypeScript
- **数据库**: PostgreSQL (Supabase)
- **部署**: Vercel (Lovable原生支持)
- **AI/ML**: Shapley归因算法 + 滚动预测 + 动态学习

### 数据模型 (27张表)
- **BMOS核心表**: 23张表 (维度表9张 + 事实表5张 + 桥接表5张 + 分析视图4张)
- **层级决策表**: 4张表 (决策层级 + 分解关系 + KPI + 执行关联)

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 启动系统
```bash
# 启动开发环境
docker-compose -f docker-compose-dev.yml up -d

# 访问系统
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
```

## 📋 核心功能

### 1. 全链条价值传递
- 价值链分析引擎
- 归因分析 (Shapley算法)
- 优化建议生成

### 2. 动态管理脉络
- 数据采集与指标计算
- 初步分析与关注点识别
- 决策落地与结果追踪

### 3. 利益协同与风险管控
- 价值贡献度计算
- 利益分配算法
- 风险监控与预警

### 4. 现金流健康管理
- 现金流效率分析
- NPV计算与评估
- 健康状态监控

### 5. 关键量化方法应用
- TOC瓶颈定位
- 边际分析
- 价值增量计算

### 6. 决策管理支撑系统
- 层级决策管理 (战略层→战术层→执行层)
- 决策追溯分析
- 定期分析报告

## 📚 文档结构

### 核心文档
- **`COLLABORATIVE_DEVELOPMENT_FRAMEWORK.md`**: Cursor与Lovable协同开发框架
- **`docs/requirements/REQUIREMENTS_ANALYSIS_TEMPLATE.md`**: 需求分析模板
- **`docs/requirements/MODULE1_VALUE_CHAIN_ANALYSIS.md`**: 模块1需求规格说明书
- **`docs/requirements/REQUIREMENTS_WORK_PLAN.md`**: 需求梳理工作计划

### 系统文档
- **`BMOS_SYSTEM_COMPLETE.md`**: BMOS系统完成总结
- **`BMOS_SYSTEM_STATUS.md`**: 系统状态说明
- **`BMOS_SYSTEM_TEST_RESULTS.md`**: 系统测试结果

### 部署文档
- **`DEPLOYMENT_GUIDE.md`**: 部署指南
- **`DEVELOPMENT_GUIDELINES.md`**: 开发指南
- **`TESTING_GUIDE.md`**: 测试指南
- **`TESTING_STRATEGY.md`**: 测试策略

### 问题解决文档
- **`WINDOWS_COMPILATION_SOLUTION.md`**: Windows编译问题解决方案
- **`DOCKER_ISSUE_RESOLUTION.md`**: Docker问题解决方案
- **`VPN_SOLUTION_SIMPLE.md`**: VPN网络问题解决方案

## 🔧 开发指南

### 项目结构 (React-centric)
```
qbm-ai-system/
├── src/                    # React前端源码
│   ├── components/         # React组件
│   ├── pages/             # 页面组件
│   ├── hooks/             # 自定义Hooks
│   └── lib/               # 工具库
├── backend/               # 后端API服务
│   ├── app/
│   │   ├── api/          # API端点
│   │   ├── models/       # 数据模型
│   │   ├── engines/      # 分析引擎
│   │   └── main.py       # 主应用
│   └── requirements.txt  # 依赖
├── database/             # 数据库配置
│   ├── clickhouse/       # ClickHouse配置
│   └── schema/           # 数据库架构
├── scripts/              # 工具脚本
└── docker-compose-dev.yml # 开发环境
```

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd qbm-ai-system

# 启动开发环境
docker-compose -f docker-compose-dev.yml up -d

# 查看日志
docker-compose -f docker-compose-dev.yml logs -f
```

## 📈 系统特性

### 技术特性
- **高性能**: PostgreSQL数据库，支持复杂查询和分析
- **实时性**: Supabase实时订阅，毫秒级响应
- **可扩展**: Next.js全栈架构，支持水平扩展
- **简化部署**: Vercel一键部署，环境一致性
- **现代化**: React + TypeScript + Tailwind CSS
- **完全协同**: Lovable原生支持，前后端统一开发

### 业务特性
- **理论指导**: 基于完整的商业模式理论框架
- **数据驱动**: 全链路数据追溯和分析
- **决策支持**: 层级决策管理和效果评估
- **持续优化**: AI增强的动态学习能力

## 🎯 使用场景

### 适用企业
- 中大型企业
- 需要商业模式优化的企业
- 重视数据驱动决策的企业
- 需要决策追溯和效果评估的企业

### 应用领域
- 商业模式优化
- 营销归因分析
- 价值链管理
- 决策效果评估
- 利益分配优化

## 📞 技术支持

### 常见问题
- 查看 `WINDOWS_COMPILATION_SOLUTION.md` 解决Windows编译问题
- 查看 `DOCKER_ISSUE_RESOLUTION.md` 解决Docker问题
- 查看 `VPN_SOLUTION_SIMPLE.md` 解决VPN网络问题

### 系统监控
- 访问 `http://localhost:8000/health` 检查后端健康状态
- 访问 `http://localhost:3000` 使用前端界面
- 查看系统日志了解运行状态

## 📄 许可证

详见 [LICENSE](LICENSE) 文件。

---

**这个系统将理论框架、技术实现和实际应用完美结合，采用React-centric架构，为企业提供完整的商业模式动态优化解决方案！** 🎉