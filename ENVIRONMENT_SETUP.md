# 环境变量配置说明

## 🔧 必需的环境变量

### 1. **Supabase配置**
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 2. **Next.js配置**
```bash
# .env.local
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
```

### 3. **开发环境配置**
```bash
# .env.local
NODE_ENV=development
```

## 📋 配置步骤

### 1. **创建环境变量文件**
```bash
# 在项目根目录创建 .env.local 文件
touch .env.local
```

### 2. **添加Supabase配置**
1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 创建新项目或选择现有项目
3. 在项目设置中找到API配置
4. 复制Project URL和Service Role Key

### 3. **配置示例**
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
NODE_ENV=development
```

## ⚠️ 安全注意事项

1. **不要提交环境变量文件**
   - `.env.local` 已添加到 `.gitignore`
   - 不要在代码中硬编码敏感信息

2. **生产环境配置**
   - 在Vercel中配置环境变量
   - 使用强密码和密钥

3. **密钥管理**
   - 定期轮换Service Role Key
   - 使用不同的密钥用于开发和生产环境

## 🚀 验证配置

### 1. **检查环境变量**
```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseKey);
```

### 2. **测试连接**
```typescript
// src/pages/api/test-connection.ts
import { supabase } from '../../lib/supabase';

export default async function handler(req, res) {
  try {
    const { data, error } = await supabase.from('test').select('*').limit(1);
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    res.status(200).json({ message: 'Connection successful', data });
  } catch (error) {
    res.status(500).json({ error: 'Connection failed' });
  }
}
```

## 📚 相关文档

- [Supabase环境变量配置](https://supabase.com/docs/guides/getting-started/local-development#environment-variables)
- [Next.js环境变量](https://nextjs.org/docs/basic-features/environment-variables)
- [Vercel环境变量](https://vercel.com/docs/concepts/projects/environment-variables)
