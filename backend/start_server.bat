@echo off
REM 启动后端FastAPI服务
REM 确保后端服务运行在 http://localhost:8000

echo ========================================
echo 启动 BMOS 后端服务
echo ========================================
echo.

cd /d %~dp0

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

echo [信息] Python 版本:
python --version

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo [信息] 在虚拟环境中: %VIRTUAL_ENV%
) else (
    echo [警告] 未检测到虚拟环境，建议使用虚拟环境
)

REM 检查依赖是否安装
echo.
echo [信息] 检查依赖...
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [错误] uvicorn 未安装，正在安装...
    pip install uvicorn[standard]
)

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [错误] fastapi 未安装，请先安装依赖
    echo [提示] 运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [信息] 依赖检查通过
echo.

REM 设置环境变量（如果.env文件存在）
if exist ..\\.env (
    echo [信息] 发现 .env 文件，将加载环境变量
) else (
    echo [警告] 未找到 .env 文件，使用默认配置
    echo [提示] 请复制 env.example 为 .env 并配置
)

REM 启动服务
echo ========================================
echo 启动服务: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo ========================================
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

python main_optimized.py

pause

