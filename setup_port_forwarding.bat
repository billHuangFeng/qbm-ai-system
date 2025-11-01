@echo off
echo ========================================
echo BMOS系统端口转发设置
echo ========================================
echo.
echo 正在设置端口转发...
echo.

echo 1. 清除现有端口转发规则...
netsh interface portproxy delete v4tov4 listenport=3000
netsh interface portproxy delete v4tov4 listenport=8000

echo 2. 添加新的端口转发规则...
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=172.21.0.4
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.21.0.7

echo 3. 显示端口转发规则...
netsh interface portproxy show all

echo.
echo ========================================
echo 端口转发设置完成！
echo ========================================
echo.
echo 现在可以使用以下地址访问BMOS系统:
echo   前端界面: http://localhost:3000
echo   后端API: http://localhost:8000
echo   健康检查: http://localhost:8000/health
echo.
echo 按任意键打开前端界面...
pause > nul
start http://localhost:3000
echo.
echo 前端界面已打开！
echo.
pause





