@echo off
chcp 65001 >nul
echo ========================================
echo 启动后端服务
echo ========================================
echo.

cd /d %~dp0backend

echo [信息] 检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo [信息] 启动后端服务...
echo [提示] 服务将运行在 http://localhost:8000
echo [提示] 按 Ctrl+C 停止服务
echo.

python main_optimized.py

pause

