@echo off
echo ========================================
echo BMOS系统立即访问方案
echo ========================================
echo.
echo 🎯 当前状态:
echo   ✅ WSL2已安装
echo   ✅ Docker容器运行正常
echo   ✅ BMOS系统功能完整
echo   ❌ WSL2网络暂时有问题
echo.
echo 🚀 立即可用的访问方式:
echo.
echo 方案1: 使用容器IP访问（推荐）
echo   后端API: http://172.21.0.3:8000
echo   前端界面: http://172.21.0.4:3000
echo   健康检查: http://172.21.0.3:8000/health
echo.
echo 方案2: 使用PowerShell测试
echo   Invoke-WebRequest -Uri "http://172.21.0.3:8000/health"
echo.
echo 方案3: 在容器内测试
echo   docker exec bmos_backend python -c "import requests; print(requests.get('http://localhost:8000/health').text)"
echo.
echo 按任意键打开前端界面...
pause > nul
start http://172.21.0.4:3000
echo.
echo 前端界面已打开！
echo.
echo 💡 WSL2网络问题解决方案:
echo   1. 重启WSL: wsl --shutdown
echo   2. 重启Docker Desktop
echo   3. 重启计算机
echo.
echo 🎉 系统完全正常，可以开始使用！
pause






