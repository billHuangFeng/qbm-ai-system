@echo off
echo ========================================
echo BMOS系统访问脚本
echo ========================================
echo.
echo 当前容器IP地址:
echo   前端容器: 172.21.0.3
echo   后端容器: 172.21.0.4
echo.
echo 访问方式:
echo   方案1: 使用容器IP访问（推荐）
echo     前端界面: http://172.21.0.3:3000
echo     后端API: http://172.21.0.4:8000
echo     健康检查: http://172.21.0.4:8000/health
echo.
echo   方案2: 使用PowerShell测试连接
echo     Invoke-WebRequest -Uri "http://172.21.0.4:8000/health"
echo.
echo 按任意键打开前端界面...
pause > nul
start http://172.21.0.3:3000
echo.
echo 前端界面已打开，如果无法访问，请尝试:
echo 1. 检查防火墙设置
echo 2. 重启Docker Desktop
echo 3. 使用PowerShell测试: Invoke-WebRequest -Uri "http://172.21.0.4:8000/health"
echo.
pause




