#!/bin/bash
#===============================================================================
# 好易易GEO 一键部署脚本
# 
# 功能: 自动化完成代码拉取 → 前端构建 → Docker容器启动
# 
# 使用方式:
#   ./deploy.sh                    # 交互式部署
#   ./deploy.sh --skip-build       # 跳过前端构建
#   ./deploy.sh --skip-pull        # 跳过代码拉取
#   ./deploy.sh --env prod         # 使用生产环境配置
#
#===============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_step() { echo -e "${BLUE}>>> $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 默认配置
SKIP_PULL=false
SKIP_BUILD=false
BRANCH="main"
ENV_FILE=".env"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-pull)
            SKIP_PULL=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --env)
            ENV_FILE="$2"
            shift 2
            ;;
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --skip-pull      跳过代码拉取"
            echo "  --skip-build     跳过前端构建"
            echo "  --branch <name>  指定Git分支 (默认: main)"
            echo "  --env <file>     指定环境变量文件 (默认: .env)"
            echo "  --help           显示帮助信息"
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查环境变量文件
if [[ ! -f "$ENV_FILE" ]]; then
    if [[ -f ".env.example" ]]; then
        print_warning "环境变量文件 $ENV_FILE 不存在，复制 .env.example..."
        cp .env.example "$ENV_FILE"
        print_warning "请编辑 $ENV_FILE 填写必要的配置（特别是 DEEPSEEK_API_KEY）"
    fi
fi

# 加载环境变量
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

echo ""
echo "========================================"
echo "  好易易GEO 部署脚本"
echo "========================================"
echo ""

#===============================================================================
# 步骤1: 拉取最新代码
#===============================================================================
if [[ "$SKIP_PULL" == "false" ]]; then
    print_step "步骤1/5: 拉取最新代码..."
    
    # 进入项目目录
    PROJECT_DIR="../"
    if [[ -d "$PROJECT_DIR/.git" ]]; then
        cd "$PROJECT_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
        print_success "代码已更新 (分支: $BRANCH)"
        cd "$SCRIPT_DIR"
    else
        print_warning "非Git仓库或不存在，跳过代码拉取"
    fi
else
    print_warning "跳过代码拉取"
fi

#===============================================================================
# 步骤2: 构建前端
#===============================================================================
if [[ "$SKIP_BUILD" == "false" ]]; then
    print_step "步骤2/5: 构建前端..."
    
    FRONTEND_DIR="../web"
    if [[ -d "$FRONTEND_DIR" ]]; then
        cd "$FRONTEND_DIR"
        
        # 检查依赖
        if [[ ! -d "node_modules" ]]; then
            print_step "安装前端依赖..."
            npm install
        fi
        
        # 构建生产版本
        print_step "执行前端构建..."
        npm run build
        
        if [[ -d "dist" ]]; then
            print_success "前端构建完成"
        else
            print_error "前端构建失败，未找到 dist 目录"
            exit 1
        fi
        
        cd "$SCRIPT_DIR"
    else
        print_warning "前端目录不存在，跳过构建"
    fi
else
    print_warning "跳过前端构建"
fi

#===============================================================================
# 步骤3: 拉取/构建Docker镜像
#===============================================================================
print_step "步骤3/5: 准备Docker镜像..."

# 拉取基础镜像
print_step "拉取基础镜像..."
docker pull redis:7-alpine
docker pull nginx:alpine
print_success "基础镜像拉取完成"

# 构建后端镜像
print_step "构建后端镜像..."
docker-compose build backend
print_success "后端镜像构建完成"

#===============================================================================
# 步骤4: 停止旧容器
#===============================================================================
print_step "步骤4/5: 停止旧容器..."

docker-compose down 2>/dev/null || true
print_success "旧容器已停止"

#===============================================================================
# 步骤5: 启动新容器
#===============================================================================
print_step "步骤5/5: 启动服务..."

docker-compose up -d
print_success "容器启动完成"

# 等待服务就绪
print_step "等待服务就绪..."
sleep 5

#===============================================================================
# 验证部署
#===============================================================================
print_step "验证部署状态..."

# 检查容器状态
BACKEND_STATUS=$(docker inspect --format='{{.State.Health.Status}}' geo-insight-api 2>/dev/null || echo "no-healthcheck")
FRONTEND_RUNNING=$(docker inspect --format='{{.State.Running}}' geo-insight-frontend 2>/dev/null || echo "false")
REDIS_RUNNING=$(docker inspect --format='{{.State.Running}}' geo-insight-redis 2>/dev/null || echo "false")

echo ""
echo "========================================"
echo "  部署状态"
echo "========================================"
echo "  后端API:  ${BACKEND_STATUS}"
echo "  前端:     $([ "$FRONTEND_RUNNING" == "true" ] && echo "运行中" || echo "未运行")"
echo "  Redis:    $([ "$REDIS_RUNNING" == "true" ] && echo "运行中" || echo "未运行")"
echo ""

# 测试API
API_PORT=${BACKEND_PORT:-5000}
if curl -sf "http://localhost:${API_PORT}/health" > /dev/null 2>&1; then
    print_success "API健康检查通过"
else
    print_warning "API健康检查失败，请检查日志: docker-compose logs backend"
fi

echo ""
echo "========================================"
echo "  部署完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:${FRONTEND_PORT:-80}"
echo "  API:  http://localhost:${API_PORT}"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo ""
