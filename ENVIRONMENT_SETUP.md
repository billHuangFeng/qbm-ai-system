# 环境变量配置说明

## 本地开发环境

创建 `.env.local` 文件，包含以下环境变量：

```bash
# Supabase配置
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# 其他配置
NODE_ENV=development
```

## Supabase项目配置

1. 访问 https://supabase.com
2. 创建新项目 `bmos-production`
3. 在项目设置中获取以下信息：
   - Project URL (NEXT_PUBLIC_SUPABASE_URL)
   - anon public key (NEXT_PUBLIC_SUPABASE_ANON_KEY)
   - service_role key (SUPABASE_SERVICE_ROLE_KEY)

## 数据库迁移

在Supabase SQL Editor中依次执行以下SQL文件：

1. `database/postgresql/01_raw_data_staging.sql`
2. `database/postgresql/02_decision_controllable_facts.sql`
3. `database/postgresql/03_external_business_facts.sql`
4. `database/postgresql/04_bmos_core_tables.sql`
5. `database/postgresql/05_manager_evaluation.sql`
6. `database/postgresql/06_decision_cycle_config.sql`

## Vercel部署配置

在Vercel项目设置中添加相同的环境变量：

- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY