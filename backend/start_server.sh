#!/bin/bash
# 启动后端FastAPI服务
# 确保后端服务运行在 http://localhost:8000

echo "========================================"
echo "启动 BMOS 后端服务"
echo "========================================"
echo

cd "$(dirname "$0")"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python 未安装或不在 PATH 中"
    exit 1
fi

echo "[信息] Python 版本:"
python3 --version

# 检查是否在虚拟环境中
if [ -n "$VIRTUAL_ENV" ]; then
    echo "[信息] 在虚拟环境中: $VIRTUAL_ENV"
else
    echo "[警告] 未检测到虚拟环境，建议使用虚拟环境"
fi

# 检查依赖是否安装
echo
echo "[信息] 检查依赖..."
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "[错误] uvicorn 未安装，正在安装..."
    pip install uvicorn[standard]
fi

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "[错误] fastapi 未安装，请先安装依赖"
    echo "[提示] 运行: pip install -r requirements.txt"
    exit 1
fi

echo "[信息] 依赖检查通过"
echo

# 设置环境变量（如果.env文件存在）
if [ -f "../.env" ]; then
    echo "[信息] 发现 .env 文件，将加载环境变量"
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo "[警告] 未找到 .env 文件，使用默认配置"
    echo "[提示] 请复制 env.example 为 .env 并配置"
fi

# 启动服务
echo "========================================"
echo "启动服务: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo "========================================"
echo
echo "[提示] 按 Ctrl+C 停止服务"
echo

python3 main_optimized.py

