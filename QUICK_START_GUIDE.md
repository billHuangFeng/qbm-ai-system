# BMOS 快速启动指南

## 🚀 立即开始使用

### 1. 环境准备

确保您的系统已安装：
- Node.js 18+ 
- Git

### 2. 克隆并安装依赖

```bash
# 如果还没有克隆项目
git clone https://github.com/billHuangFeng/bmos-insight.git
cd bmos-insight

# 安装依赖
npm install
```

### 3. 配置Supabase（必需）

#### 3.1 创建Supabase项目
1. 访问 [https://supabase.com](https://supabase.com)
2. 注册/登录账户
3. 点击 "New Project"
4. 项目名称：`bmos-production`
5. 选择地区（推荐：Singapore）
6. 设置数据库密码（请记住此密码）

#### 3.2 获取环境变量
在Supabase项目仪表板中：
1. 进入 Settings → API
2. 复制以下信息：
   - Project URL
   - anon public key
   - service_role key

#### 3.3 配置环境变量
在项目根目录创建 `.env.local` 文件：

```bash
# Supabase配置
NEXT_PUBLIC_SUPABASE_URL=your_project_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# 其他配置
NODE_ENV=development
```

### 4. 数据库迁移

#### 4.1 在Supabase中执行SQL
1. 在Supabase项目仪表板中，进入 SQL Editor
2. 依次执行以下SQL文件的内容：

```sql
-- 1. 执行 01_raw_data_staging.sql
-- 2. 执行 02_decision_controllable_facts.sql  
-- 3. 执行 03_external_business_facts.sql
-- 4. 执行 04_bmos_core_tables.sql
-- 5. 执行 05_manager_evaluation.sql
-- 6. 执行 06_decision_cycle_config.sql
```

**或者**，您可以复制每个SQL文件的内容到SQL Editor中执行。

### 5. 启动开发服务器

```bash
npm run dev
```

### 6. 访问系统

- **主页面**: [http://localhost:3000](http://localhost:3000)
- **测试页面**: [http://localhost:3000/test](http://localhost:3000/test)

## 🧪 测试系统功能

### 测试原始数据导入
1. 访问测试页面
2. 在"原始数据导入"卡片中：
   - 选择数据来源系统（如：手动输入）
   - 选择数据类型（如：费用开支）
   - 粘贴JSON格式的测试数据：

```json
{
  "type": "办公用品",
  "amount": 1000.00,
  "date": "2024-01-15",
  "department": "行政部",
  "description": "购买办公用品"
}
```

3. 点击"上传并处理"

### 测试业务事实管理
1. 在测试页面中，点击"业务事实管理"
2. 尝试切换不同的标签页（费用开支、资产购置等）
3. 查看数据表格显示

### 测试管理者评价
1. 在测试页面中，找到"管理者评价确认"卡片
2. 在评价意见文本框中输入测试内容
3. 点击"提交评价"

### 测试决策循环
1. 在测试页面中，找到"决策循环监控"卡片
2. 点击"手动触发分析"按钮
3. 查看系统响应

## 🔧 故障排除

### 常见问题

#### 1. 环境变量未配置
**错误**: `NEXT_PUBLIC_SUPABASE_URL is not defined`
**解决**: 确保 `.env.local` 文件存在且包含正确的Supabase配置

#### 2. 数据库连接失败
**错误**: `Failed to connect to database`
**解决**: 
- 检查Supabase项目是否正常运行
- 验证环境变量是否正确
- 确认数据库迁移是否完成

#### 3. 页面无法访问
**错误**: `This site can't be reached`
**解决**: 
- 确保开发服务器正在运行 (`npm run dev`)
- 检查端口3000是否被占用
- 尝试访问 `http://127.0.0.1:3000`

#### 4. 组件渲染错误
**错误**: `Cannot find module '@/components/ui/...'`
**解决**: 
- 确保所有依赖已安装 (`npm install`)
- 检查文件路径是否正确
- 重启开发服务器

### 获取帮助

如果遇到问题：
1. 查看浏览器控制台错误信息
2. 检查终端中的错误日志
3. 参考 `ARCHITECTURE_UNIFICATION_COMPLETE.md` 文档
4. 查看 `API_REFERENCE.md` 了解API接口

## 📚 下一步

系统启动成功后，您可以：

1. **探索功能**: 测试各个组件的功能
2. **添加数据**: 通过原始数据导入添加真实业务数据
3. **自定义开发**: 基于现有架构添加新功能
4. **部署到生产**: 使用Vercel部署到生产环境

## 🎉 恭喜！

您已成功启动BMOS系统！现在可以开始使用这个统一的商业模式动态优化与决策管理平台了。

---

**需要帮助？** 查看 `ARCHITECTURE_UNIFICATION_COMPLETE.md` 获取完整的系统说明。



