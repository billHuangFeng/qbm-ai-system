@echo off
chcp 65001 >nul
echo ========================================
echo 启动后端服务（简单模式）
echo ========================================
echo.

cd /d %~dp0

echo [1] 配置环境变量...
python setup_env.py
if errorlevel 1 (
    echo [错误] 环境配置失败
    pause
    exit /b 1
)

echo.
echo [2] 启动后端服务...
cd backend

echo.
echo ========================================
echo 服务启动中...
echo ========================================
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo ========================================
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

python start_simple.py

pause

