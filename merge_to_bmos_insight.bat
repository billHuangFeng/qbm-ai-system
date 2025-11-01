@echo off
chcp 65001 >nul
echo ========================================
echo BMOS项目合并到bmos-insight仓库
echo ========================================
echo.

REM 检查参数
if "%1"=="" (
    echo 用法: merge_to_bmos_insight.bat ^<目标仓库URL^>
    echo 示例: merge_to_bmos_insight.bat https://github.com/billHuangFeng/bmos-insight.git
    pause
    exit /b 1
)

set TARGET_REPO_URL=%1
set TARGET_DIR=bmos-insight
set BACKUP_DIR=bmos-insight-backup

echo 目标仓库: %TARGET_REPO_URL%
echo 当前目录: %CD%
echo.

REM 检查Git是否可用
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误: Git不可用，请安装Git
    pause
    exit /b 1
)

echo 1. 检查当前Git状态...
git status >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误: 当前目录不是Git仓库
    pause
    exit /b 1
)
echo   ✓ Git状态正常

echo.
echo 2. 克隆目标仓库...
if exist "%TARGET_DIR%" (
    echo 目标目录已存在，是否删除并重新克隆?
    set /p choice="输入 y 确认删除: "
    if /i "%choice%"=="y" (
        rmdir /s /q "%TARGET_DIR%"
    ) else (
        echo 使用现有目录
        goto :merge_files
    )
)

git clone %TARGET_REPO_URL% %TARGET_DIR%
if %errorLevel% neq 0 (
    echo 错误: 克隆仓库失败
    pause
    exit /b 1
)
echo   ✓ 目标仓库克隆成功

:merge_files
echo.
echo 3. 备份目标仓库...
if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
xcopy "%TARGET_DIR%" "%BACKUP_DIR%\" /E /I /H /Y >nul
echo   ✓ 目标仓库已备份

echo.
echo 4. 识别lovable管理的文件...
echo 正在搜索lovable相关文件...
dir /s /b "%TARGET_DIR%\*lovable*" > lovable_files.txt 2>nul
dir /s /b "%TARGET_DIR%\.lovable*" >> lovable_files.txt 2>nul
echo   ✓ lovable文件列表已保存到 lovable_files.txt

echo.
echo 5. 创建合并分支...
cd "%TARGET_DIR%"
git checkout -b merge-bmos-system
if %errorLevel% neq 0 (
    echo 错误: 创建分支失败
    cd ..
    pause
    exit /b 1
)
echo   ✓ 合并分支创建成功
cd ..

echo.
echo 6. 复制BMOS核心文件...

REM 复制后端
if exist "backend" (
    if exist "%TARGET_DIR%\backend" rmdir /s /q "%TARGET_DIR%\backend"
    xcopy "backend" "%TARGET_DIR%\backend\" /E /I /H /Y >nul
    echo   ✓ 后端文件已复制
)

REM 复制前端
if exist "frontend" (
    if exist "%TARGET_DIR%\frontend" rmdir /s /q "%TARGET_DIR%\frontend"
    xcopy "frontend" "%TARGET_DIR%\frontend\" /E /I /H /Y >nul
    echo   ✓ 前端文件已复制
)

REM 复制数据库配置
if exist "database" (
    if exist "%TARGET_DIR%\database" rmdir /s /q "%TARGET_DIR%\database"
    xcopy "database" "%TARGET_DIR%\database\" /E /I /H /Y >nul
    echo   ✓ 数据库配置已复制
)

REM 复制脚本
if exist "scripts" (
    if exist "%TARGET_DIR%\scripts" rmdir /s /q "%TARGET_DIR%\scripts"
    xcopy "scripts" "%TARGET_DIR%\scripts\" /E /I /H /Y >nul
    echo   ✓ 脚本文件已复制
)

REM 复制Docker配置文件
if exist "docker-compose-dev.yml" (
    copy "docker-compose-dev.yml" "%TARGET_DIR%\docker-compose-dev.yml" >nul
    echo   ✓ Docker开发配置已复制
)

if exist "docker-compose-clickhouse.yml" (
    copy "docker-compose-clickhouse.yml" "%TARGET_DIR%\docker-compose-clickhouse.yml" >nul
    echo   ✓ Docker ClickHouse配置已复制
)

REM 复制文档文件
if not exist "%TARGET_DIR%\docs" mkdir "%TARGET_DIR%\docs"
if not exist "%TARGET_DIR%\docs\windows" mkdir "%TARGET_DIR%\docs\windows"
if not exist "%TARGET_DIR%\docs\docker" mkdir "%TARGET_DIR%\docs\docker"
if not exist "%TARGET_DIR%\docs\testing" mkdir "%TARGET_DIR%\docs\testing"
if not exist "%TARGET_DIR%\docs\development" mkdir "%TARGET_DIR%\docs\development"
if not exist "%TARGET_DIR%\docs\project" mkdir "%TARGET_DIR%\docs\project"
if not exist "%TARGET_DIR%\docs\vpn" mkdir "%TARGET_DIR%\docs\vpn"
if not exist "%TARGET_DIR%\docs\merge" mkdir "%TARGET_DIR%\docs\merge"

REM 复制各种文档
for %%f in (BMOS_*.md WINDOWS_*.md DOCKER_*.md TESTING_*.md DEVELOPMENT_*.md PROJECT_*.md VPN_*.md MERGE_TO_BMOS_INSIGHT.md) do (
    if exist "%%f" (
        copy "%%f" "%TARGET_DIR%\docs\%%f" >nul
        echo   ✓ 文档已复制: %%f
    )
)

REM 复制README和LICENSE
if exist "README.md" (
    copy "README.md" "%TARGET_DIR%\README_BMOS.md" >nul
    echo   ✓ BMOS README已复制
)

if exist "LICENSE" (
    copy "LICENSE" "%TARGET_DIR%\LICENSE_BMOS" >nul
    echo   ✓ BMOS LICENSE已复制
)

echo.
echo 7. 更新README文件...
cd "%TARGET_DIR%"
echo # BMOS Insight - 商业模式量化优化系统 > README.md
echo. >> README.md
echo ## 🎯 项目概述 >> README.md
echo. >> README.md
echo 这是一个集成了完整BMOS系统的商业智能平台，提供商业模式量化分析和优化建议。 >> README.md
echo. >> README.md
echo ## 🚀 快速开始 >> README.md
echo. >> README.md
echo ### 环境要求 >> README.md
echo - Docker ^& Docker Compose >> README.md
echo - Python 3.8+ >> README.md
echo - Node.js 16+ >> README.md
echo. >> README.md
echo ### 启动系统 >> README.md
echo ```bash >> README.md
echo # 启动开发环境 >> README.md
echo docker-compose -f docker-compose-dev.yml up -d >> README.md
echo. >> README.md
echo # 访问系统 >> README.md
echo # 前端: http://localhost:3000 >> README.md
echo # 后端API: http://localhost:8000 >> README.md
echo ``` >> README.md
echo. >> README.md
echo ## 📁 项目结构 >> README.md
echo. >> README.md
echo - `backend/` - FastAPI后端服务 >> README.md
echo - `frontend/` - Vue.js前端界面 >> README.md
echo - `database/` - ClickHouse数据库配置 >> README.md
echo - `scripts/` - 工具脚本 >> README.md
echo - `docs/` - 项目文档 >> README.md
echo. >> README.md
echo ## 🔧 核心功能 >> README.md
echo. >> README.md
echo - **数据管理**: 11张核心业务表 >> README.md
echo - **归因分析**: Shapley值计算 >> README.md
echo - **优化建议**: 智能优化推荐 >> README.md
echo - **可视化**: 实时数据图表 >> README.md
echo - **系统监控**: 健康状态监控 >> README.md
echo. >> README.md
echo ## 📚 文档 >> README.md
echo. >> README.md
echo 详细文档请查看 `docs/` 目录。 >> README.md
echo. >> README.md
echo ## 🤝 贡献 >> README.md
echo. >> README.md
echo 欢迎提交Issue和Pull Request。 >> README.md
echo. >> README.md
echo ## 📄 许可证 >> README.md
echo. >> README.md
echo 详见 [LICENSE_BMOS](LICENSE_BMOS) 文件。 >> README.md
echo   ✓ README文件已更新
cd ..

echo.
echo 8. 验证合并结果...
if exist "%TARGET_DIR%\backend\app\main.py" (
    echo   ✓ 后端主文件存在
) else (
    echo   ❌ 后端主文件缺失
)

if exist "%TARGET_DIR%\frontend\package.json" (
    echo   ✓ 前端配置文件存在
) else (
    echo   ❌ 前端配置文件缺失
)

if exist "%TARGET_DIR%\database\clickhouse\schema\bmos_core_tables.sql" (
    echo   ✓ 数据库架构文件存在
) else (
    echo   ❌ 数据库架构文件缺失
)

if exist "%TARGET_DIR%\docker-compose-dev.yml" (
    echo   ✓ Docker配置文件存在
) else (
    echo   ❌ Docker配置文件缺失
)

echo.
echo 9. 提交更改...
cd "%TARGET_DIR%"
git add .
git commit -m "Merge BMOS system into bmos-insight

- 添加完整的BMOS后端系统
- 添加Vue.js前端界面  
- 添加ClickHouse数据库配置
- 添加Docker容器化配置
- 保护lovable管理的文件
- 更新项目文档"
if %errorLevel% neq 0 (
    echo 错误: 提交失败
    cd ..
    pause
    exit /b 1
)
echo   ✓ 更改已提交
cd ..

echo.
echo ========================================
echo 合并完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 推送到远程仓库:
echo    cd %TARGET_DIR%
echo    git push origin merge-bmos-system
echo.
echo 2. 在GitHub上创建Pull Request
echo.
echo 3. 请求lovable进行代码审查
echo.
echo 备份目录: %BACKUP_DIR%
echo lovable文件列表: lovable_files.txt
echo.
pause




