#!/usr/bin/env python3
"""
部署脚本
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def build_backend():
    """构建后端"""
    print("🔨 构建后端...")
    
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # 安装依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # 运行数据库迁移
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
        
        print("✅ 后端构建完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端构建失败: {e}")
        return False

def build_frontend():
    """构建前端"""
    print("🔨 构建前端...")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        # 安装依赖
        subprocess.run(["npm", "install"], check=True)
        
        # 构建生产版本
        subprocess.run(["npm", "run", "build"], check=True)
        
        print("✅ 前端构建完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端构建失败: {e}")
        return False

def build_docker():
    """构建Docker镜像"""
    print("🐳 构建Docker镜像...")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # 构建后端镜像
        subprocess.run([
            "docker", "build", 
            "-t", "qbm-ai-backend:latest",
            "-f", "Dockerfile",
            "."
        ], check=True)
        
        # 构建前端镜像
        subprocess.run([
            "docker", "build", 
            "-t", "qbm-ai-frontend:latest",
            "-f", "frontend/Dockerfile",
            "frontend/"
        ], check=True)
        
        print("✅ Docker镜像构建完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker镜像构建失败: {e}")
        return False

def deploy_local():
    """本地部署"""
    print("🚀 开始本地部署...")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # 停止现有容器
        subprocess.run(["docker-compose", "down"], check=False)
        
        # 启动服务
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ 本地部署完成!")
        print("🌐 前端访问地址: http://localhost:8080")
        print("🔧 后端API地址: http://localhost:8000")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 本地部署失败: {e}")
        return False

def deploy_production():
    """生产环境部署"""
    print("🚀 开始生产环境部署...")
    
    # 这里可以添加生产环境部署逻辑
    # 例如：部署到云服务器、Kubernetes等
    
    print("⚠️  生产环境部署功能待实现")
    return True

def cleanup():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    project_root = Path(__file__).parent.parent
    
    # 清理Python缓存
    for pycache in project_root.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    
    # 清理前端构建文件
    frontend_dist = project_root / "frontend" / "dist"
    if frontend_dist.exists():
        shutil.rmtree(frontend_dist, ignore_errors=True)
    
    print("✅ 清理完成!")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QBM AI System 部署脚本")
    parser.add_argument("--env", choices=["local", "production"], default="local", help="部署环境")
    parser.add_argument("--build-only", action="store_true", help="仅构建，不部署")
    parser.add_argument("--cleanup", action="store_true", help="清理构建文件")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup()
        return
    
    print("🚀 开始部署流程...")
    
    # 构建步骤
    build_success = True
    
    if not build_backend():
        build_success = False
    
    if not build_frontend():
        build_success = False
    
    if not build_docker():
        build_success = False
    
    if not build_success:
        print("💥 构建失败，停止部署!")
        sys.exit(1)
    
    if args.build_only:
        print("✅ 构建完成!")
        return
    
    # 部署步骤
    if args.env == "local":
        if deploy_local():
            print("🎉 本地部署成功!")
        else:
            print("💥 本地部署失败!")
            sys.exit(1)
    elif args.env == "production":
        if deploy_production():
            print("🎉 生产环境部署成功!")
        else:
            print("💥 生产环境部署失败!")
            sys.exit(1)

if __name__ == "__main__":
    main()





