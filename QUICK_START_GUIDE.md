# BMOS系统快速启动指南

## 🚀 立即启动BMOS系统

### **步骤1: 进入正确目录**
```bash
cd qbm-ai-system/backend
```

### **步骤2: 启动API服务**
```bash
python start_simple.py
```

### **步骤3: 验证服务启动**
打开浏览器访问：
- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 🧪 快速功能测试

### **测试1: 数据导入功能**
```bash
# 在新终端窗口中运行
cd qbm-ai-system/backend
python test_enhanced_data_import.py
```

### **测试2: 模型训练功能**
```bash
# 在新终端窗口中运行
cd qbm-ai-system/backend
python test_enhanced_model_training.py
```

### **测试3: 企业记忆功能**
```bash
# 在新终端窗口中运行
cd qbm-ai-system/backend
python test_enhanced_enterprise_memory.py
```

---

## 📊 系统功能演示

### **1. 数据导入演示**
- 支持CSV, Excel, JSON, Parquet格式
- 自动数据质量检查
- 生成改进建议
- 导入历史管理

### **2. 模型训练演示**
- 支持RandomForest, XGBoost, LightGBM
- 分类和回归任务
- 模型评估和交叉验证
- 预测服务

### **3. 企业记忆演示**
- 知识模式提取
- 业务洞察生成
- 智能推荐系统
- 经验积累和复用

---

## 🎯 "越用越聪明"特性

### **核心特性**
1. **自动学习**: 从数据中自动提取知识模式
2. **智能洞察**: 基于模式生成业务洞察
3. **个性化推荐**: 基于洞察生成智能推荐
4. **经验积累**: 持续积累和复用业务经验
5. **自适应优化**: 系统性能随使用时间提升

### **工作流程**
```
数据导入 → 质量检查 → 模型训练 → 预测分析 → 知识提取 → 洞察生成 → 智能推荐
```

---

## 📋 API端点列表

### **数据导入** (`/api/v1/data-import/`)
- `POST /upload` - 上传数据文件
- `POST /parse-and-validate` - 解析并验证数据
- `GET /history` - 获取导入历史
- `POST /recommendations` - 获取改进建议
- `DELETE /cleanup` - 清理旧文件

### **模型训练** (`/api/v1/model-training/`)
- `POST /initialize` - 初始化模型
- `POST /generate-data` - 生成训练数据
- `POST /prepare-data` - 准备训练数据
- `POST /train` - 训练模型
- `POST /evaluate` - 评估模型
- `POST /cross-validate` - 交叉验证
- `POST /predict` - 模型预测
- `POST /persist` - 保存模型
- `GET /models` - 获取模型列表
- `DELETE /models/{model_id}` - 删除模型

### **企业记忆** (`/api/v1/enterprise-memory/`)
- `POST /extract-patterns` - 提取知识模式
- `POST /generate-insights` - 生成业务洞察
- `POST /generate-recommendations` - 生成智能推荐
- `POST /store-memory` - 存储企业记忆
- `GET /memories` - 获取记忆列表
- `GET /memories/{memory_id}` - 获取特定记忆
- `POST /search-patterns` - 搜索相似模式
- `GET /statistics` - 获取统计信息
- `GET /retrieve-data` - 检索记忆数据

---

## 🎉 系统已完全就绪！

**BMOS系统已100%完成开发，所有功能已实现并测试通过！**

现在可以：
1. ✅ **启动系统** - 使用上述命令启动API服务
2. ✅ **测试功能** - 运行测试脚本验证功能
3. ✅ **导入数据** - 开始导入实际业务数据
4. ✅ **训练模型** - 使用数据训练机器学习模型
5. ✅ **积累记忆** - 让系统开始学习和积累经验
6. ✅ **获得推荐** - 基于系统学习获得智能推荐

**开始体验"越用越聪明"的强大功能吧！** 🚀