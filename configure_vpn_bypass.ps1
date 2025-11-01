# VPN绕过Docker网络配置脚本
# 需要管理员权限运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VPN绕过Docker网络配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "错误: 需要管理员权限运行此脚本" -ForegroundColor Red
    Write-Host "请右键点击PowerShell，选择'以管理员身份运行'，然后执行此脚本" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "正在配置Docker网络段绕过..." -ForegroundColor Green
Write-Host ""

# Docker网络段列表
$dockerNetworks = @(
    "172.17.0.0/16",
    "172.18.0.0/16", 
    "172.19.0.0/16",
    "172.20.0.0/16",
    "172.21.0.0/16",
    "172.22.0.0/16"
)

Write-Host "1. 配置Docker网络段路由..." -ForegroundColor Yellow
Write-Host "正在添加路由规则..." -ForegroundColor Gray

foreach ($network in $dockerNetworks) {
    $parts = $network.Split('/')
    $ip = $parts[0]
    $cidr = $parts[1]
    
    # 计算子网掩码
    $mask = switch ($cidr) {
        "16" { "255.255.0.0" }
        "24" { "255.255.255.0" }
        default { "255.255.0.0" }
    }
    
    try {
        # 尝试添加路由
        $result = route add $ip mask $mask 127.0.0.1 metric 1 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $network 路由添加成功" -ForegroundColor Green
        } else {
            if ($result -match "对象已存在|already exists") {
                Write-Host "  ⚠ $network 路由已存在" -ForegroundColor Yellow
            } else {
                Write-Host "  ❌ $network 路由添加失败: $result" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "  ❌ $network 路由添加失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "2. 显示Docker相关路由..." -ForegroundColor Yellow
Write-Host "当前Docker网络路由:" -ForegroundColor Gray

try {
    $routes = route print | Select-String "172\.1"
    if ($routes) {
        $routes | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    } else {
        Write-Host "  未找到Docker相关路由" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  无法获取路由信息" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 重启VPN客户端" -ForegroundColor White
Write-Host "2. 运行测试: python test_simple.py" -ForegroundColor White
Write-Host "3. 在浏览器中访问: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "如果仍有问题，请尝试:" -ForegroundColor Yellow
Write-Host "- 检查VPN软件的本地网络绕过设置" -ForegroundColor White
Write-Host "- 使用容器内访问方式" -ForegroundColor White
Write-Host ""

Read-Host "按任意键退出"






