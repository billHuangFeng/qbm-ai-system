# Windows Tesseract-OCR 安装辅助脚本
# 此脚本帮助检查和配置 Tesseract-OCR

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Tesseract-OCR 安装检查与配置" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装
Write-Host "1. 检查 Tesseract-OCR 是否已安装..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Tesseract-OCR 已安装" -ForegroundColor Green
        Write-Host "   版本信息:" -ForegroundColor Gray
        Write-Host "   $tesseractVersion" -ForegroundColor Gray
    } else {
        throw "Tesseract not found"
    }
} catch {
    Write-Host "   ❌ Tesseract-OCR 未找到" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 Tesseract-OCR:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "2. 下载最新的 tesseract-ocr-w64-setup-v*.exe" -ForegroundColor White
    Write-Host "3. 运行安装程序" -ForegroundColor White
    Write-Host "4. 记住安装路径（默认: C:\Program Files\Tesseract-OCR）" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""

# 检查可用语言
Write-Host "2. 检查可用语言..." -ForegroundColor Yellow
try {
    $languages = tesseract --list-langs 2>&1
    Write-Host "   可用语言:" -ForegroundColor Gray
    $languages | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
    
    # 检查中文
    if ($languages -match "chi_sim") {
        Write-Host "   ✅ 中文简体已安装" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ 中文简体未安装" -ForegroundColor Yellow
        Write-Host "   如需使用中文OCR，请下载 chi_sim.traineddata" -ForegroundColor White
        Write-Host "   下载地址: https://github.com/tesseract-ocr/tessdata" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️ 无法列出语言" -ForegroundColor Yellow
}

Write-Host ""

# 检查环境变量
Write-Host "3. 检查环境变量配置..." -ForegroundColor Yellow
$tesseractPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$fullPath = "$tesseractPath;$userPath"

if ($fullPath -match "Tesseract-OCR") {
    Write-Host "   ✅ Tesseract-OCR 已在 PATH 中" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ Tesseract-OCR 不在 PATH 中" -ForegroundColor Yellow
    
    # 尝试找到安装路径
    $possiblePaths = @(
        "C:\Program Files\Tesseract-OCR",
        "C:\Program Files (x86)\Tesseract-OCR",
        "$env:ProgramFiles\Tesseract-OCR"
    )
    
    $foundPath = $null
    foreach ($path in $possiblePaths) {
        if (Test-Path "$path\tesseract.exe") {
            $foundPath = $path
            break
        }
    }
    
    if ($foundPath) {
        Write-Host "   找到 Tesseract-OCR 安装路径: $foundPath" -ForegroundColor Cyan
        $response = Read-Host "   是否添加到系统 PATH? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y") {
            try {
                # 需要管理员权限
                if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
                    Write-Host "   ⚠️ 需要管理员权限" -ForegroundColor Yellow
                    Write-Host "   请以管理员身份运行此脚本" -ForegroundColor Yellow
                } else {
                    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
                    if ($currentPath -notlike "*$foundPath*") {
                        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$foundPath", "Machine")
                        Write-Host "   ✅ 已添加到系统 PATH" -ForegroundColor Green
                        Write-Host "   ⚠️ 请重新打开命令行窗口使更改生效" -ForegroundColor Yellow
                    }
                }
            } catch {
                Write-Host "   ❌ 添加失败: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "   ❌ 未找到 Tesseract-OCR 安装路径" -ForegroundColor Red
        Write-Host "   请手动添加到 PATH:" -ForegroundColor Yellow
        Write-Host "   1. Win+R -> sysdm.cpl -> 高级 -> 环境变量" -ForegroundColor White
        Write-Host "   2. 编辑系统变量 Path" -ForegroundColor White
        Write-Host "   3. 添加 Tesseract-OCR 安装路径" -ForegroundColor White
    }
}

Write-Host ""

# 测试 Python 集成
Write-Host "4. 测试 Python pytesseract 集成..." -ForegroundColor Yellow
try {
    python -c "import pytesseract; print('   ✅ pytesseract 已安装')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ pytesseract 已安装" -ForegroundColor Green
        
        # 测试能否找到 tesseract
        try {
            python -c "import pytesseract; print('Tesseract版本:', pytesseract.get_tesseract_version())" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Python 可以找到 Tesseract-OCR" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Python 无法找到 Tesseract-OCR" -ForegroundColor Yellow
                Write-Host "   可能需要重新打开命令行窗口" -ForegroundColor Yellow
                Write-Host "   或在代码中指定路径" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠️ 无法获取 Tesseract 版本" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ pytesseract 未安装" -ForegroundColor Red
        Write-Host "   运行: pip install pytesseract" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️ 无法测试 Python 集成" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "检查完成" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 提供下一步指导
Write-Host "📖 详细安装指南: docs/INSTALL_TESSERACT_WINDOWS.md" -ForegroundColor Cyan
Write-Host ""


