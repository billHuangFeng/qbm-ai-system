# 同步到bmos-insight仓库指南

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **同步策略说明**

---

## 🎯 同步目标

将最新的价值链可视化设计文档和相关代码同步到 `bmos-insight` 仓库，供Lovable实现前端功能。

---

## 📊 需要同步的内容

### 1. 价值链可视化设计文档（Lovable前端实现需要）

- ✅ `docs/EXECUTIVE_DASHBOARD_DESIGN.md` - 管理仪表盘设计
- ✅ `docs/VALUE_CHAIN_NETWORK_VISUALIZATION_DESIGN.md` - 价值链网络可视化设计
- ✅ `docs/VALUE_CHAIN_SUPPORT_RELATIONSHIP_VISUALIZATION.md` - 价值链支撑关系可视化设计
- ✅ `docs/VALUE_ELEMENTS_QUANTIFICATION_METHODS.md` - 价值要素量化方法
- ✅ `docs/VALUE_CHAIN_OPTIMIZATION_METHODOLOGY.md` - 价值链优化方法论
- ✅ `docs/MARGINAL_INVESTMENT_RETURN_CALCULATION.md` - 边际投入收益计算机制
- ✅ `docs/LOVABLE_FRONTEND_IMPLEMENTATION_GUIDE.md` - Lovable前端实现指南
- ✅ `docs/LOVABLE_FRONTEND_TASK_SUMMARY.md` - Lovable前端实现任务总结

### 2. 价值链相关业务文档

- ✅ `docs/VALUE_CHAIN_DETAILED.md` - 详细价值链设计
- ✅ `docs/CORE_VALUE_CHAIN.md` - 核心价值链路
- ✅ `docs/VALUE_CHAIN_IMPLEMENTATION_CONSISTENCY_CHECK.md` - 价值链实现一致性检查

### 3. 相关API和算法文档（前端调用需要）

- ✅ `docs/api/MARGINAL_ANALYSIS_API_CONTRACT.md` - 边际分析API契约
- ✅ `docs/api/EDGE_FUNCTIONS_API_TEMPLATE.md` - Edge Functions API模板
- ✅ `docs/algorithms/TYPESCRIPT_ALGORITHMS.md` - TypeScript算法实现

---

## 🔄 同步策略

### 方案1: 合并分支（推荐）

```bash
# 1. 创建合并分支
git checkout -b sync-value-chain-docs

# 2. 拉取lovable的最新更改
git fetch lovable
git merge lovable/main

# 3. 解决冲突（如果有）
# 4. 推送合并分支
git push lovable sync-value-chain-docs:sync-value-chain-docs

# 5. 在GitHub上创建Pull Request
```

### 方案2: 直接推送（如果两个仓库完全独立）

```bash
# 1. 创建合并分支
git checkout -b sync-value-chain-docs

# 2. 强制推送（小心使用）
git push lovable sync-value-chain-docs:main --force-with-lease
```

---

## 📋 同步步骤

### 步骤1: 检查差异

```bash
# 检查需要同步的文件
git diff lovable/main..origin/main --name-only | grep "docs/.*VALUE_CHAIN\|docs/.*EXECUTIVE\|docs/.*MARGINAL\|docs/.*LOVABLE"
```

### 步骤2: 创建同步分支

```bash
git checkout -b sync-to-bmos-insight
```

### 步骤3: 合并lovable的更改

```bash
git fetch lovable
git merge lovable/main --no-commit
```

### 步骤4: 解决冲突（如果有）

如果存在冲突，手动解决并提交。

### 步骤5: 推送到lovable远程

```bash
git push lovable sync-to-bmos-insight:main
```

---

## ⚠️ 注意事项

1. **保护Lovable的文件**：确保不覆盖Lovable管理的前端文件
2. **保留RLS相关更改**：lovable/main中的RLS policy更改需要保留
3. **文档路径**：确保文档路径正确，不覆盖现有文档
4. **提交信息**：使用清晰的提交信息说明同步内容

---

## 🔧 手动同步脚本

如果需要手动同步，可以使用以下命令：

```bash
# 只同步文档文件到lovable远程
git checkout sync-to-bmos-insight
git checkout lovable/main -- docs/VALUE_CHAIN_*.md docs/EXECUTIVE_*.md docs/MARGINAL_*.md docs/LOVABLE_*.md
git add docs/
git commit -m "docs: 同步价值链可视化设计文档到bmos-insight"
git push lovable sync-to-bmos-insight:main
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23  
**状态**: ✅ **同步策略说明完整**

