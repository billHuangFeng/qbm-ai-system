# 多租户架构设计（100家企业）

## 📋 架构概述

基于用户澄清，系统需要支持100家企业的多租户架构，每家企业独立管理数据，分析师可跨租户访问。

## 🏗️ 多租户数据隔离策略

### 策略选择：Schema隔离（推荐）

**原因**：
- 100家企业规模适中，Schema隔离提供最佳的数据隔离性
- 便于企业间数据完全隔离，符合企业级安全要求
- 支持分析师跨租户查询（通过Union查询）

### 数据库设计调整

#### 1. 租户管理表
```sql
-- 租户信息表
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_name VARCHAR(200) NOT NULL,
    tenant_code VARCHAR(50) UNIQUE NOT NULL, -- 如：T001
    subscription_plan VARCHAR(50) DEFAULT 'standard', -- standard/premium
    max_assets INT DEFAULT 100,
    max_capabilities INT DEFAULT 100,
    max_products INT DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 用户表（关联租户）
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    email VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL, -- enterprise_user/analyst
    permissions JSONB, -- 具体权限配置
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. 动态Schema创建
```sql
-- 为每个租户创建独立的Schema
-- 命名规则：tenant_{tenant_code}
-- 如：tenant_T001, tenant_T002, ...

-- 每个租户Schema包含完整的27张表
-- 表结构相同，但数据完全隔离
```

#### 3. RLS策略配置
```sql
-- 企业用户：只能访问本租户数据
CREATE POLICY tenant_isolation ON {table_name}
    FOR ALL TO enterprise_user
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- 分析师：可访问授权租户数据
CREATE POLICY analyst_cross_tenant ON {table_name}
    FOR ALL TO analyst
    USING (tenant_id = ANY(
        SELECT unnest(permissions->'authorized_tenants')::uuid
        FROM users WHERE user_id = auth.uid()
    ));
```

## 🔐 权限控制设计

### 角色定义

#### 1. 企业用户（Enterprise User）
- **权限范围**：本租户内所有数据
- **功能权限**：
  - 资产清单管理（CRUD）
  - 能力清单管理（CRUD）
  - 价值评估项管理（CRUD）
  - 数据录入（现金流预测、能力成果、价值评估）
  - 报表查看（本企业数据）

#### 2. 分析师（Analyst）
- **权限范围**：授权租户数据
- **功能权限**：
  - 跨租户数据查询
  - 对比分析（多企业数据）
  - 行业基准分析
  - 高级分析功能（Shapley、时间序列）

### 权限配置示例
```json
{
  "enterprise_user": {
    "data_access": "tenant_only",
    "functions": ["crud", "data_entry", "reports"],
    "tables": ["all"]
  },
  "analyst": {
    "data_access": "authorized_tenants",
    "functions": ["query", "analysis", "comparison"],
    "tables": ["read_only"],
    "authorized_tenants": ["T001", "T002", "T003"]
  }
}
```

## 📊 性能优化策略

### 1. 数据量级分析
- **总企业数**：100家
- **每家企业数据**：100资产 + 100能力 + 100产品 + 1000条/月
- **总数据量**：约1000万条记录/年
- **并发用户**：10个

### 2. 性能优化方案

#### 数据库优化
```sql
-- 租户级分区
CREATE TABLE asset_accumulation (
    tenant_id UUID NOT NULL,
    asset_id UUID NOT NULL,
    month_date DATE NOT NULL,
    accumulated_value DECIMAL(15,2),
    monthly_delta DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, asset_id, month_date)
) PARTITION BY HASH (tenant_id);

-- 创建分区
CREATE TABLE asset_accumulation_p0 PARTITION OF asset_accumulation
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
-- ... 其他分区
```

#### 缓存策略
- **Redis缓存**：热点数据（如资产清单、能力清单）
- **查询缓存**：复杂分析结果（如Shapley值、边际贡献）
- **会话缓存**：用户权限、租户信息

#### 查询优化
- **索引策略**：租户ID + 业务字段的复合索引
- **分页查询**：大数据量分页加载
- **异步计算**：复杂分析任务后台执行

## 🚀 实施计划

### 阶段1：多租户基础架构（Week 1-2）
1. **租户管理功能**
   - 租户注册/激活
   - 用户角色分配
   - 权限配置

2. **动态Schema创建**
   - 租户Schema自动创建
   - 表结构同步
   - 索引创建

### 阶段2：权限控制实现（Week 3-4）
1. **RLS策略配置**
   - 企业用户隔离策略
   - 分析师跨租户策略
   - 权限验证中间件

2. **API权限控制**
   - 租户ID自动注入
   - 权限检查中间件
   - 跨租户查询接口

### 阶段3：性能优化（Week 5-6）
1. **数据库优化**
   - 分区表创建
   - 索引优化
   - 查询性能测试

2. **缓存实现**
   - Redis集成
   - 缓存策略配置
   - 缓存失效机制

## 🔍 监控和运维

### 1. 性能监控
- **数据库性能**：查询响应时间、连接数、慢查询
- **应用性能**：API响应时间、内存使用、CPU使用
- **用户行为**：登录频率、功能使用统计

### 2. 数据安全
- **访问日志**：记录所有数据访问操作
- **权限审计**：定期检查权限配置
- **数据备份**：租户级数据备份策略

### 3. 扩展性规划
- **水平扩展**：支持更多租户（1000+）
- **垂直扩展**：支持更大数据量
- **功能扩展**：新增分析功能、集成接口

---

**本架构设计确保100家企业的数据完全隔离，同时支持分析师跨租户分析，满足企业级安全要求和业务需求。**




