# 检查后端服务状态
Write-Host "========================================"
Write-Host "检查后端服务状态"
Write-Host "========================================"
Write-Host ""

# 检查端口监听
Write-Host "[1] 检查端口 8000 监听状态..."
$portCheck = netstat -ano | Select-String ":8000.*LISTENING"
if ($portCheck) {
    Write-Host "✓ 端口 8000 正在监听" -ForegroundColor Green
    Write-Host "   $portCheck"
} else {
    Write-Host "✗ 端口 8000 未监听" -ForegroundColor Red
}
Write-Host ""

# 检查健康检查端点
Write-Host "[2] 检查健康检查端点..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ 服务运行正常" -ForegroundColor Green
        Write-Host "   Status Code: $($response.StatusCode)"
        Write-Host "   Response: $($response.Content)"
    }
} catch {
    Write-Host "✗ 服务未响应或未启动" -ForegroundColor Red
    Write-Host "   错误: $($_.Exception.Message)"
}
Write-Host ""

# 检查API文档
Write-Host "[3] 检查API文档端点..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API文档可访问" -ForegroundColor Green
        Write-Host "   URL: http://localhost:8000/docs"
    }
} catch {
    Write-Host "✗ API文档不可访问" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================"
Write-Host "服务地址:"
Write-Host "  - API: http://localhost:8000"
Write-Host "  - 健康检查: http://localhost:8000/health"
Write-Host "  - API文档: http://localhost:8000/docs"
Write-Host "  - ReDoc: http://localhost:8000/redoc"
Write-Host "========================================"

