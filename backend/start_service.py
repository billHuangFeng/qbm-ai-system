#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动后端服务（简化版）
自动配置环境并启动服务
"""

import sys
import os
import io
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "bmos-development-secret-key-minimum-32-characters-long-for-testing-only",
)
os.environ.setdefault("API_HOST", "0.0.0.0")
os.environ.setdefault("API_PORT", "8000")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("LOG_LEVEL", "INFO")

# 设置数据库和Redis（使用默认值，如果未配置）
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "password")
os.environ.setdefault("POSTGRES_DB", "bmos")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")

print("=" * 60)
print("启动 BMOS 后端服务")
print("=" * 60)
print()
print("服务配置:")
print(f"  - 主机: {os.environ.get('API_HOST', '0.0.0.0')}")
print(f"  - 端口: {os.environ.get('API_PORT', '8000')}")
print(f"  - 环境: {os.environ.get('ENVIRONMENT', 'development')}")
print()
print("服务地址:")
print("  - API: http://localhost:8000")
print("  - 健康检查: http://localhost:8000/health")
print("  - API文档: http://localhost:8000/docs")
print("  - ReDoc: http://localhost:8000/redoc")
print()
print("=" * 60)
print("服务启动中...")
print("按 Ctrl+C 停止服务")
print("=" * 60)
print()

try:
    import uvicorn

    # 使用简单启动脚本
    uvicorn.run(
        "start_simple:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", "8000")),
        reload=True,
        log_level="info",
    )
except KeyboardInterrupt:
    print()
    print("服务已停止")
except Exception as e:
    print(f"启动失败: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
