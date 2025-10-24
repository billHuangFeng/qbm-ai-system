# BMOS系统端口转发设置脚本
# 需要管理员权限运行

Write-Host "========================================" -ForegroundColor Green
Write-Host "BMOS系统端口转发设置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "1. 清除现有端口转发规则..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=3000
netsh interface portproxy delete v4tov4 listenport=8000

Write-Host "2. 添加新的端口转发规则..." -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=172.21.0.4
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.21.0.7

Write-Host "3. 显示端口转发规则..." -ForegroundColor Yellow
netsh interface portproxy show all

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "端口转发设置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "现在可以使用以下地址访问BMOS系统:" -ForegroundColor Cyan
Write-Host "  前端界面: http://localhost:3000" -ForegroundColor White
Write-Host "  后端API: http://localhost:8000" -ForegroundColor White
Write-Host "  健康检查: http://localhost:8000/health" -ForegroundColor White
Write-Host ""

Write-Host "按任意键打开前端界面..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "前端界面已打开！" -ForegroundColor Green
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")




