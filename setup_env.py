#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置环境变量脚本
自动创建.env文件并生成JWT_SECRET_KEY
"""

import os
import sys
import secrets
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 获取项目根目录
project_root = Path(__file__).parent
env_file = project_root / '.env'
env_example = project_root / 'env.example'

print("=" * 50)
print("配置环境变量")
print("=" * 50)
print()

# 检查.env文件是否存在
if not env_file.exists():
    print("[1] 创建 .env 文件...")
    if env_example.exists():
        # 从env.example复制
        env_file.write_text(env_example.read_text(), encoding='utf-8')
        print("    [OK] 从 env.example 创建 .env 文件")
    else:
        print("    ✗ env.example 不存在，创建基本 .env 文件")
        env_file.write_text("", encoding='utf-8')
else:
    print("[1] .env 文件已存在")

# 读取.env文件内容
content = env_file.read_text(encoding='utf-8')

# 生成JWT_SECRET_KEY
print("[2] 配置 JWT_SECRET_KEY...")
secret_key = secrets.token_urlsafe(64)

# 检查是否需要更新JWT_SECRET_KEY
if 'JWT_SECRET_KEY=' not in content:
    # 添加JWT_SECRET_KEY
    content += f"\nJWT_SECRET_KEY={secret_key}\n"
    print("    [OK] 添加 JWT_SECRET_KEY")
elif 'JWT_SECRET_KEY=your-super-secure' in content or (content.split('JWT_SECRET_KEY=')[1].split('\n')[0] if 'JWT_SECRET_KEY=' in content else '') == '':
    # 更新默认的JWT_SECRET_KEY
    import re
    content = re.sub(r'JWT_SECRET_KEY=.*', f'JWT_SECRET_KEY={secret_key}', content)
    print("    [OK] 更新 JWT_SECRET_KEY")
else:
    print("    [OK] JWT_SECRET_KEY 已配置")

# 确保VITE_API_URL已配置
print("[3] 配置 VITE_API_URL...")
if 'VITE_API_URL=' not in content:
    content += "\nVITE_API_URL=http://localhost:8000\n"
    print("    [OK] 添加 VITE_API_URL")
elif 'VITE_API_URL=http://localhost:8000' not in content:
    import re
    content = re.sub(r'VITE_API_URL=.*', 'VITE_API_URL=http://localhost:8000', content)
    print("    [OK] 更新 VITE_API_URL")
else:
    print("    [OK] VITE_API_URL 已配置")

# 保存.env文件
env_file.write_text(content, encoding='utf-8')
print()
print("=" * 50)
print("环境配置完成！")
print("=" * 50)
print()
print("下一步：启动后端服务")
print("  cd backend")
print("  python start_simple.py")
print()

