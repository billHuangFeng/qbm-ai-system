@echo off
echo 正在启动VPN配置脚本...
echo.

REM 检查PowerShell是否可用
powershell -Command "Get-Host" >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误: PowerShell不可用
    pause
    exit /b 1
)

REM 以管理员权限运行PowerShell脚本
powershell -ExecutionPolicy Bypass -File "%~dp0configure_vpn_bypass.ps1"

pause





