@echo off
chcp 65001 >nul
echo ========================================
echo VPN绕过Docker网络配置
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误: 需要管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo 正在配置Docker网络段绕过...
echo.

echo 1. 配置Docker网络段路由...
echo 正在添加路由规则...

REM 使用正确的路由命令格式
route add 172.17.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.17.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.17.0.0/16 路由可能已存在或添加失败
)

route add 172.18.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.18.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.18.0.0/16 路由可能已存在或添加失败
)

route add 172.19.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.19.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.19.0.0/16 路由可能已存在或添加失败
)

route add 172.20.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.20.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.20.0.0/16 路由可能已存在或添加失败
)

route add 172.21.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.21.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.21.0.0/16 路由可能已存在或添加失败
)

route add 172.22.0.0 mask 255.255.0.0 127.0.0.1 metric 1 >nul 2>&1
if %errorLevel% equ 0 (
    echo   ✓ 172.22.0.0/16 路由添加成功
) else (
    echo   ⚠ 172.22.0.0/16 路由可能已存在或添加失败
)

echo.
echo 2. 显示Docker相关路由...
echo 当前Docker网络路由:
route print | findstr "172.1"

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 重启VPN客户端
echo 2. 运行测试: python test_simple.py
echo 3. 在浏览器中访问: http://localhost:3000
echo.
echo 如果仍有问题，请尝试:
echo - 检查VPN软件的本地网络绕过设置
echo - 使用容器内访问方式
echo.
pause
