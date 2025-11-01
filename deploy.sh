#!/bin/bash

# QBM历史数据拟合优化系统部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ $# -eq 0 ]; then
    log_error "请指定部署环境: dev 或 prod"
    echo "使用方法: ./deploy.sh [dev|prod]"
    exit 1
fi

ENVIRONMENT=$1

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
    log_error "无效的环境参数: $ENVIRONMENT"
    echo "请使用: dev 或 prod"
    exit 1
fi

log_info "开始部署QBM历史数据拟合优化系统到 $ENVIRONMENT 环境..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查必要的文件
REQUIRED_FILES=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "nginx/nginx.conf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "缺少必要文件: $file"
        exit 1
    fi
done

# 创建必要的目录
log_info "创建必要的目录..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p monitoring/grafana/dashboards
mkdir -p nginx/ssl

# 设置环境变量
if [ "$ENVIRONMENT" = "prod" ]; then
    log_info "设置生产环境变量..."
    export COMPOSE_FILE=docker-compose.prod.yml
    export ENVIRONMENT=production
    export LOG_LEVEL=INFO
else
    log_info "设置开发环境变量..."
    export COMPOSE_FILE=docker-compose.yml
    export ENVIRONMENT=development
    export LOG_LEVEL=DEBUG
fi

# 停止现有服务
log_info "停止现有服务..."
docker-compose -f $COMPOSE_FILE down --remove-orphans

# 清理旧的镜像（可选）
if [ "$ENVIRONMENT" = "prod" ]; then
    log_info "清理旧的Docker镜像..."
    docker system prune -f
fi

# 构建镜像
log_info "构建Docker镜像..."
docker-compose -f $COMPOSE_FILE build --no-cache

# 启动服务
log_info "启动服务..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
log_info "等待服务启动..."
sleep 30

# 检查服务状态
log_info "检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

# 运行数据库迁移
log_info "运行数据库迁移..."
docker-compose -f $COMPOSE_FILE exec backend python -m alembic upgrade head

# 运行数据库初始化
log_info "初始化数据库..."
docker-compose -f $COMPOSE_FILE exec backend python -c "
from src.database import init_database
init_database()
"

# 运行测试（开发环境）
if [ "$ENVIRONMENT" = "dev" ]; then
    log_info "运行测试..."
    docker-compose -f $COMPOSE_FILE exec backend python -m pytest tests/ -v
fi

# 检查服务健康状态
log_info "检查服务健康状态..."
services=("backend" "frontend" "postgres" "redis")

for service in "${services[@]}"; do
    if docker-compose -f $COMPOSE_FILE ps | grep -q "$service.*Up"; then
        log_success "$service 服务运行正常"
    else
        log_error "$service 服务启动失败"
        exit 1
    fi
done

# 显示访问信息
log_success "部署完成！"
echo ""
echo "=========================================="
echo "QBM历史数据拟合优化系统部署信息"
echo "=========================================="
echo "环境: $ENVIRONMENT"
echo "前端地址: http://localhost:3000"
echo "后端API: http://localhost:8000"
echo "数据库: postgresql://localhost:5432/qbm_db"
echo "Redis: redis://localhost:6379"
echo ""

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "生产环境额外服务:"
    echo "监控面板: http://localhost:3001"
    echo "Prometheus: http://localhost:9090"
    echo "Loki: http://localhost:3100"
    echo ""
fi

echo "查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "停止服务: docker-compose -f $COMPOSE_FILE down"
echo "重启服务: docker-compose -f $COMPOSE_FILE restart"
echo ""

# 显示服务状态
log_info "当前服务状态:"
docker-compose -f $COMPOSE_FILE ps

log_success "部署脚本执行完成！"



