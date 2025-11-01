#!/usr/bin/env python3
"""
BMOS项目合并到bmos-insight仓库脚本
保护lovable管理的文件，安全合并BMOS系统
"""
import os
import shutil
import subprocess
import json
from pathlib import Path
import sys

class BMOSMerger:
    def __init__(self, source_dir, target_repo_url):
        self.source_dir = Path(source_dir)
        self.target_repo_url = target_repo_url
        self.target_dir = Path("bmos-insight")
        self.backup_dir = Path("bmos-insight-backup")
        
        # lovable保护文件模式
        self.lovable_patterns = [
            "lovable*",
            ".lovable*",
            "*lovable*",
            "lovable.config.*",
            ".lovable/",
            "lovable_*"
        ]
        
        # BMOS核心文件映射
        self.bmos_file_mapping = {
            "backend/": "backend/",
            "frontend/": "frontend/", 
            "database/": "database/",
            "scripts/": "scripts/",
            "docker-compose-dev.yml": "docker-compose-dev.yml",
            "docker-compose-clickhouse.yml": "docker-compose-clickhouse.yml",
            "docker-compose-simple.yml": "docker-compose-simple.yml",
            "README.md": "README_BMOS.md",
            "LICENSE": "LICENSE_BMOS"
        }
        
        # 文档文件映射到docs目录
        self.docs_mapping = {
            "BMOS_*.md": "docs/",
            "WINDOWS_*.md": "docs/windows/",
            "DOCKER_*.md": "docs/docker/",
            "TESTING_*.md": "docs/testing/",
            "DEVELOPMENT_*.md": "docs/development/",
            "PROJECT_*.md": "docs/project/",
            "VPN_*.md": "docs/vpn/",
            "MERGE_TO_BMOS_INSIGHT.md": "docs/merge/"
        }

    def run_command(self, cmd, cwd=None, timeout=300):
        """运行命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=cwd, encoding='utf-8', errors='ignore'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def check_git_status(self):
        """检查Git状态"""
        print("=== 检查Git状态 ===")
        
        # 检查是否在Git仓库中
        success, stdout, stderr = self.run_command("git status", cwd=self.source_dir)
        if not success:
            print("❌ 当前目录不是Git仓库")
            return False
        
        print("✅ Git状态正常")
        return True

    def clone_target_repo(self):
        """克隆目标仓库"""
        print("\n=== 克隆目标仓库 ===")
        
        if self.target_dir.exists():
            print(f"⚠️ 目标目录 {self.target_dir} 已存在")
            response = input("是否删除现有目录并重新克隆? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(self.target_dir)
            else:
                print("使用现有目录")
                return True
        
        print(f"正在克隆 {self.target_repo_url}...")
        success, stdout, stderr = self.run_command(
            f"git clone {self.target_repo_url} {self.target_dir}"
        )
        
        if success:
            print("✅ 目标仓库克隆成功")
            return True
        else:
            print(f"❌ 克隆失败: {stderr}")
            return False

    def backup_target_repo(self):
        """备份目标仓库"""
        print("\n=== 备份目标仓库 ===")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.target_dir, self.backup_dir)
        print(f"✅ 目标仓库已备份到 {self.backup_dir}")
        return True

    def identify_lovable_files(self):
        """识别lovable管理的文件"""
        print("\n=== 识别lovable管理的文件 ===")
        
        lovable_files = []
        
        for pattern in self.lovable_patterns:
            success, stdout, stderr = self.run_command(
                f"find {self.target_dir} -name '{pattern}' -type f",
                cwd=self.target_dir
            )
            if success and stdout.strip():
                files = stdout.strip().split('\n')
                lovable_files.extend(files)
        
        # 也检查目录
        for pattern in self.lovable_patterns:
            success, stdout, stderr = self.run_command(
                f"find {self.target_dir} -name '{pattern}' -type d",
                cwd=self.target_dir
            )
            if success and stdout.strip():
                dirs = stdout.strip().split('\n')
                lovable_files.extend(dirs)
        
        # 保存lovable文件列表
        lovable_info = {
            "files": lovable_files,
            "patterns": self.lovable_patterns,
            "timestamp": str(Path().cwd())
        }
        
        with open("lovable_files.json", "w", encoding="utf-8") as f:
            json.dump(lovable_info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 识别到 {len(lovable_files)} 个lovable管理的文件/目录")
        for file in lovable_files:
            print(f"  - {file}")
        
        return lovable_files

    def create_merge_branch(self):
        """创建合并分支"""
        print("\n=== 创建合并分支 ===")
        
        # 切换到目标仓库
        success, stdout, stderr = self.run_command(
            "git checkout -b merge-bmos-system",
            cwd=self.target_dir
        )
        
        if success:
            print("✅ 合并分支创建成功")
            return True
        else:
            print(f"❌ 创建分支失败: {stderr}")
            return False

    def copy_bmos_files(self):
        """复制BMOS文件"""
        print("\n=== 复制BMOS文件 ===")
        
        copied_files = []
        
        # 复制核心文件
        for source_pattern, target_path in self.bmos_file_mapping.items():
            source_path = self.source_dir / source_pattern
            target_path = self.target_dir / target_path
            
            if source_path.exists():
                if source_path.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                    print(f"✅ 复制目录: {source_pattern} -> {target_path}")
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    print(f"✅ 复制文件: {source_pattern} -> {target_path}")
                
                copied_files.append(str(target_path))
            else:
                print(f"⚠️ 源文件不存在: {source_pattern}")
        
        # 复制文档文件
        docs_dir = self.target_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        for pattern, target_dir in self.docs_mapping.items():
            target_dir_path = self.target_dir / target_dir
            target_dir_path.mkdir(parents=True, exist_ok=True)
            
            # 查找匹配的文件
            success, stdout, stderr = self.run_command(
                f"find {self.source_dir} -name '{pattern}' -type f"
            )
            
            if success and stdout.strip():
                files = stdout.strip().split('\n')
                for file_path in files:
                    file_name = Path(file_path).name
                    target_file = target_dir_path / file_name
                    shutil.copy2(file_path, target_file)
                    print(f"✅ 复制文档: {file_name} -> {target_dir}")
                    copied_files.append(str(target_file))
        
        return copied_files

    def update_readme(self):
        """更新README文件"""
        print("\n=== 更新README文件 ===")
        
        readme_path = self.target_dir / "README.md"
        bmos_readme_path = self.target_dir / "README_BMOS.md"
        
        if bmos_readme_path.exists():
            # 读取BMOS README内容
            with open(bmos_readme_path, 'r', encoding='utf-8') as f:
                bmos_content = f.read()
            
            # 创建合并后的README
            merged_content = f"""# BMOS Insight - 商业模式量化优化系统

## 🎯 项目概述

这是一个集成了完整BMOS系统的商业智能平台，提供商业模式量化分析和优化建议。

## 🚀 快速开始

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

## 📁 项目结构

- `backend/` - FastAPI后端服务
- `frontend/` - Vue.js前端界面
- `database/` - ClickHouse数据库配置
- `scripts/` - 工具脚本
- `docs/` - 项目文档

## 🔧 核心功能

- **数据管理**: 11张核心业务表
- **归因分析**: Shapley值计算
- **优化建议**: 智能优化推荐
- **可视化**: 实时数据图表
- **系统监控**: 健康状态监控

## 📚 文档

详细文档请查看 `docs/` 目录：
- [Windows环境配置](docs/windows/)
- [Docker部署指南](docs/docker/)
- [测试指南](docs/testing/)
- [开发指南](docs/development/)

## 🤝 贡献

欢迎提交Issue和Pull Request。

## 📄 许可证

详见 [LICENSE_BMOS](LICENSE_BMOS) 文件。

---

## 原始BMOS系统文档

{bmos_content}
"""
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            
            print("✅ README文件已更新")
        else:
            print("⚠️ 未找到BMOS README文件")

    def verify_merge(self):
        """验证合并结果"""
        print("\n=== 验证合并结果 ===")
        
        # 检查关键文件是否存在
        key_files = [
            "backend/app/main.py",
            "frontend/package.json",
            "database/clickhouse/schema/bmos_core_tables.sql",
            "docker-compose-dev.yml"
        ]
        
        missing_files = []
        for file_path in key_files:
            full_path = self.target_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ 以下关键文件缺失:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        else:
            print("✅ 所有关键文件都存在")
        
        # 检查lovable文件是否被保护
        with open("lovable_files.json", "r", encoding="utf-8") as f:
            lovable_info = json.load(f)
        
        protected_files = []
        for file_path in lovable_info["files"]:
            if Path(file_path).exists():
                protected_files.append(file_path)
        
        print(f"✅ {len(protected_files)} 个lovable文件被保护")
        
        return True

    def commit_changes(self):
        """提交更改"""
        print("\n=== 提交更改 ===")
        
        # 添加所有文件
        success, stdout, stderr = self.run_command(
            "git add .",
            cwd=self.target_dir
        )
        
        if not success:
            print(f"❌ 添加文件失败: {stderr}")
            return False
        
        # 提交更改
        success, stdout, stderr = self.run_command(
            'git commit -m "Merge BMOS system into bmos-insight\n\n- 添加完整的BMOS后端系统\n- 添加Vue.js前端界面\n- 添加ClickHouse数据库配置\n- 添加Docker容器化配置\n- 保护lovable管理的文件\n- 更新项目文档"',
            cwd=self.target_dir
        )
        
        if success:
            print("✅ 更改已提交")
            return True
        else:
            print(f"❌ 提交失败: {stderr}")
            return False

    def create_merge_report(self):
        """创建合并报告"""
        print("\n=== 创建合并报告 ===")
        
        report = {
            "merge_timestamp": str(Path().cwd()),
            "source_directory": str(self.source_dir),
            "target_repository": self.target_repo_url,
            "bmos_files_mapped": list(self.bmos_file_mapping.keys()),
            "docs_mapped": list(self.docs_mapping.keys()),
            "lovable_files_protected": [],
            "merge_status": "completed"
        }
        
        # 读取lovable文件信息
        if Path("lovable_files.json").exists():
            with open("lovable_files.json", "r", encoding="utf-8") as f:
                lovable_info = json.load(f)
                report["lovable_files_protected"] = lovable_info["files"]
        
        with open("merge_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("✅ 合并报告已创建: merge_report.json")

    def run_merge(self):
        """执行完整合并流程"""
        print("=== BMOS项目合并到bmos-insight仓库 ===")
        print(f"源目录: {self.source_dir}")
        print(f"目标仓库: {self.target_repo_url}")
        print()
        
        try:
            # 1. 检查Git状态
            if not self.check_git_status():
                return False
            
            # 2. 克隆目标仓库
            if not self.clone_target_repo():
                return False
            
            # 3. 备份目标仓库
            if not self.backup_target_repo():
                return False
            
            # 4. 识别lovable文件
            self.identify_lovable_files()
            
            # 5. 创建合并分支
            if not self.create_merge_branch():
                return False
            
            # 6. 复制BMOS文件
            self.copy_bmos_files()
            
            # 7. 更新README
            self.update_readme()
            
            # 8. 验证合并结果
            if not self.verify_merge():
                print("❌ 合并验证失败")
                return False
            
            # 9. 提交更改
            if not self.commit_changes():
                return False
            
            # 10. 创建合并报告
            self.create_merge_report()
            
            print("\n🎉 合并完成！")
            print("\n下一步操作:")
            print("1. 推送到远程仓库: git push origin merge-bmos-system")
            print("2. 在GitHub上创建Pull Request")
            print("3. 请求lovable进行代码审查")
            
            return True
            
        except Exception as e:
            print(f"❌ 合并过程中发生错误: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python merge_to_bmos_insight.py <源目录> <目标仓库URL>")
        print("示例: python merge_to_bmos_insight.py . https://github.com/billHuangFeng/bmos-insight.git")
        return False
    
    source_dir = sys.argv[1]
    target_repo_url = sys.argv[2]
    
    merger = BMOSMerger(source_dir, target_repo_url)
    return merger.run_merge()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)




