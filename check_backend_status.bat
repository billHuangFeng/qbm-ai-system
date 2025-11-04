@echo off
chcp 65001 >nul
echo ========================================
echo 检查后端服务状态
echo ========================================
echo.

echo [1] 检查端口 8000 监听状态...
netstat -ano | findstr ":8000.*LISTENING"
if errorlevel 1 (
    echo [状态] 端口 8000 未监听
) else (
    echo [状态] 端口 8000 正在监听
)
echo.

echo [2] 检查健康检查端点...
curl -s http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo [状态] 服务未响应，可能正在启动中...
) else (
    echo [状态] 服务运行正常
)
echo.

echo ========================================
echo 服务地址:
echo   - API: http://localhost:8000
echo   - 健康检查: http://localhost:8000/health
echo   - API文档: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo ========================================
echo.

pause

