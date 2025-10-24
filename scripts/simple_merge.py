#!/usr/bin/env python3
"""
简化的BMOS项目合并脚本
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, encoding='utf-8', errors='ignore'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=== BMOS项目合并到bmos-insight仓库 ===")
    
    # 设置路径
    source_dir = Path("qbm-ai-system")
    target_repo_url = "https://github.com/billHuangFeng/bmos-insight.git"
    target_dir = Path("bmos-insight")
    
    print(f"源目录: {source_dir}")
    print(f"目标仓库: {target_repo_url}")
    print()
    
    # 1. 检查Git状态
    print("1. 检查Git状态...")
    success, stdout, stderr = run_command("git status", cwd=source_dir)
    if not success:
        print("错误: 当前目录不是Git仓库")
        return False
    print("  Git状态正常")
    
    # 2. 克隆目标仓库
    print("\n2. 克隆目标仓库...")
    if target_dir.exists():
        print("  目标目录已存在，删除并重新克隆")
        shutil.rmtree(target_dir)
    
    success, stdout, stderr = run_command(f"git clone {target_repo_url} {target_dir}")
    if not success:
        print(f"  克隆失败: {stderr}")
        return False
    print("  目标仓库克隆成功")
    
    # 3. 创建合并分支
    print("\n3. 创建合并分支...")
    success, stdout, stderr = run_command("git checkout -b merge-bmos-system", cwd=target_dir)
    if not success:
        print(f"  创建分支失败: {stderr}")
        return False
    print("  合并分支创建成功")
    
    # 4. 复制核心文件
    print("\n4. 复制BMOS核心文件...")
    
    # 复制后端
    if (source_dir / "backend").exists():
        backend_target = target_dir / "backend"
        if backend_target.exists():
            shutil.rmtree(backend_target)
        shutil.copytree(source_dir / "backend", backend_target)
        print("  后端文件已复制")
    
    # 复制前端
    if (source_dir / "frontend").exists():
        frontend_target = target_dir / "frontend"
        if frontend_target.exists():
            shutil.rmtree(frontend_target)
        shutil.copytree(source_dir / "frontend", frontend_target)
        print("  前端文件已复制")
    
    # 复制数据库配置
    if (source_dir / "database").exists():
        database_target = target_dir / "database"
        if database_target.exists():
            shutil.rmtree(database_target)
        shutil.copytree(source_dir / "database", database_target)
        print("  数据库配置已复制")
    
    # 复制脚本
    if (source_dir / "scripts").exists():
        scripts_target = target_dir / "scripts"
        if scripts_target.exists():
            shutil.rmtree(scripts_target)
        shutil.copytree(source_dir / "scripts", scripts_target)
        print("  脚本文件已复制")
    
    # 复制Docker配置文件
    docker_files = [
        "docker-compose-dev.yml",
        "docker-compose-clickhouse.yml",
        "docker-compose-simple.yml"
    ]
    
    for docker_file in docker_files:
        source_file = source_dir / docker_file
        if source_file.exists():
            shutil.copy2(source_file, target_dir / docker_file)
            print(f"  {docker_file} 已复制")
    
    # 5. 创建docs目录并复制文档
    print("\n5. 复制文档文件...")
    docs_dir = target_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    subdirs = ["windows", "docker", "testing", "development", "project", "vpn", "merge"]
    for subdir in subdirs:
        (docs_dir / subdir).mkdir(exist_ok=True)
    
    # 复制文档文件
    doc_patterns = {
        "BMOS_*.md": docs_dir,
        "WINDOWS_*.md": docs_dir / "windows",
        "DOCKER_*.md": docs_dir / "docker",
        "TESTING_*.md": docs_dir / "testing",
        "DEVELOPMENT_*.md": docs_dir / "development",
        "PROJECT_*.md": docs_dir / "project",
        "VPN_*.md": docs_dir / "vpn",
        "MERGE_TO_BMOS_INSIGHT.md": docs_dir / "merge",
        "FINAL_MERGE_GUIDE.md": docs_dir / "merge"
    }
    
    for pattern, target_dir_path in doc_patterns.items():
        # 简化：直接复制所有.md文件到对应目录
        for md_file in source_dir.glob("*.md"):
            if pattern.startswith(md_file.stem.split("_")[0]):
                shutil.copy2(md_file, target_dir_path / md_file.name)
                print(f"  {md_file.name} 已复制到 {target_dir_path.name}")
    
    # 6. 复制README和LICENSE
    print("\n6. 复制README和LICENSE...")
    if (source_dir / "README.md").exists():
        shutil.copy2(source_dir / "README.md", target_dir / "README_BMOS.md")
        print("  README_BMOS.md 已复制")
    
    if (source_dir / "LICENSE").exists():
        shutil.copy2(source_dir / "LICENSE", target_dir / "LICENSE_BMOS")
        print("  LICENSE_BMOS 已复制")
    
    # 7. 更新README
    print("\n7. 更新README文件...")
    readme_content = """# BMOS Insight - 商业模式量化优化系统

## 项目概述

这是一个集成了完整BMOS系统的商业智能平台，提供商业模式量化分析和优化建议。

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.8+
- Node.js 16+

### 启动系统
```bash
# 启动开发环境
docker-compose -f docker-compose-dev.yml up -d

# 访问系统
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
```

## 项目结构

- `backend/` - FastAPI后端服务
- `frontend/` - Vue.js前端界面
- `database/` - ClickHouse数据库配置
- `scripts/` - 工具脚本
- `docs/` - 项目文档

## 核心功能

- **数据管理**: 11张核心业务表
- **归因分析**: Shapley值计算
- **优化建议**: 智能优化推荐
- **可视化**: 实时数据图表
- **系统监控**: 健康状态监控

## 文档

详细文档请查看 `docs/` 目录。

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

详见 [LICENSE_BMOS](LICENSE_BMOS) 文件。

---

## 原始BMOS系统文档

详见 [README_BMOS.md](README_BMOS.md) 文件。
"""
    
    with open(target_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("  README.md 已更新")
    
    # 8. 验证合并结果
    print("\n8. 验证合并结果...")
    key_files = [
        "backend/app/main.py",
        "frontend/package.json",
        "database/clickhouse/schema/bmos_core_tables.sql",
        "docker-compose-dev.yml"
    ]
    
    all_exist = True
    for file_path in key_files:
        full_path = target_dir / file_path
        if full_path.exists():
            print(f"  {file_path} 存在")
        else:
            print(f"  {file_path} 缺失")
            all_exist = False
    
    if not all_exist:
        print("  警告: 部分关键文件缺失")
    
    # 9. 提交更改
    print("\n9. 提交更改...")
    success, stdout, stderr = run_command("git add .", cwd=target_dir)
    if not success:
        print(f"  添加文件失败: {stderr}")
        return False
    
    success, stdout, stderr = run_command(
        'git commit -m "Merge BMOS system into bmos-insight\n\n- 添加完整的BMOS后端系统\n- 添加Vue.js前端界面\n- 添加ClickHouse数据库配置\n- 添加Docker容器化配置\n- 更新项目文档"',
        cwd=target_dir
    )
    
    if not success:
        print(f"  提交失败: {stderr}")
        return False
    
    print("  更改已提交")
    
    # 10. 创建合并报告
    print("\n10. 创建合并报告...")
    report = {
        "merge_timestamp": str(Path().cwd()),
        "source_directory": str(source_dir),
        "target_repository": target_repo_url,
        "merge_status": "completed",
        "files_copied": [
            "backend/",
            "frontend/",
            "database/",
            "scripts/",
            "docker-compose-dev.yml",
            "docker-compose-clickhouse.yml",
            "docker-compose-simple.yml",
            "docs/",
            "README_BMOS.md",
            "LICENSE_BMOS"
        ]
    }
    
    import json
    with open("merge_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("  合并报告已创建: merge_report.json")
    
    print("\n=== 合并完成！ ===")
    print("\n下一步操作:")
    print("1. 推送到远程仓库:")
    print(f"   cd {target_dir}")
    print("   git push origin merge-bmos-system")
    print("\n2. 在GitHub上创建Pull Request")
    print("\n3. 请求lovable进行代码审查")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)



