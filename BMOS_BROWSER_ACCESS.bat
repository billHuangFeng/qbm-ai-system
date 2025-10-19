@echo off
echo ========================================
echo BMOS系统浏览器访问脚本
echo ========================================
echo.
echo 当前容器IP地址:
echo   前端容器: 172.21.0.4
echo   后端容器: 172.21.0.7
echo.
echo 访问方式:
echo   方案1: 使用localhost访问（推荐）
echo     前端界面: http://localhost:3000
echo     后端API: http://localhost:8000
echo     健康检查: http://localhost:8000/health
echo.
echo   方案2: 使用容器IP访问
echo     前端界面: http://172.21.0.4:3000
echo     后端API: http://172.21.0.7:8000
echo.
echo   方案3: 使用PowerShell测试
echo     Invoke-WebRequest -Uri "http://localhost:8000/health"
echo.
echo 按任意键打开前端界面...
pause > nul
start http://localhost:3000
echo.
echo 前端界面已打开！
echo.
echo 如果无法访问，请尝试:
echo 1. 以管理员身份运行此脚本
echo 2. 检查Windows防火墙设置
echo 3. 重启Docker Desktop
echo 4. 使用容器内访问方式
echo.
pause