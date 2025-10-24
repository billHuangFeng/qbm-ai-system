@echo off
echo ========================================
echo BMOS系统端口转发设置（需要管理员权限）
echo ========================================
echo.
echo 正在请求管理员权限...
echo.

powershell -Command "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0setup_port_forwarding.ps1\"' -Verb RunAs"

echo.
echo 如果UAC提示，请点击"是"以允许管理员权限
echo.
pause




