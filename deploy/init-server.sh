#!/bin/bash
#===============================================================================
# 好易易GEO 服务器初始化脚本
# 
# 功能: 在全新服务器上安装和配置Docker、Docker Compose、Nginx等依赖
# 
# 支持系统: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
# 
# 使用方式:
#   ./init-server.sh              # 交互式安装
#   ./init-server.sh --non-interactive  # 自动安装(用于自动化部署)
#
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_step() { echo -e "${BLUE}>>> $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此脚本需要root权限运行"
        print_step "请使用: sudo $0"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "无法检测操作系统"
        exit 1
    fi
    
    case $OS in
        ubuntu|debian)
            PKG_MANAGER="apt-get"
            ;;
        centos|rhel|rocky|almalinux)
            PKG_MANAGER="yum"
            ;;
        *)
            print_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
    
    print_step "检测到操作系统: $OS $VER (包管理器: $PKG_MANAGER)"
}

# 更新系统包
update_system() {
    print_step "更新系统包..."
    case $PKG_MANAGER in
        apt-get)
            export DEBIAN_FRONTEND=noninteractive
            apt-get update -qq
            apt-get upgrade -y -qq
            ;;
        yum)
            yum update -y -q
            ;;
    esac
    print_success "系统包更新完成"
}

# 安装基础依赖
install_dependencies() {
    print_step "安装基础依赖..."
    case $PKG_MANAGER in
        apt-get)
            apt-get install -y -qq curl wget git ca-certificates gnupg lsb-release
            ;;
        yum)
            yum install -y -q curl wget git ca-certificates
            ;;
    esac
    print_success "基础依赖安装完成"
}

# 安装Docker
install_docker() {
    # 检查Docker是否已安装
    if command -v docker &> /dev/null; then
        print_warning "Docker已安装: $(docker --version)"
        return
    fi
    
    print_step "安装Docker..."
    
    case $PKG_MANAGER in
        apt-get)
            # 添加Docker官方GPG密钥
            mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # 添加Docker仓库
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # 安装Docker
            apt-get update -qq
            apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        yum)
            yum install -y -q yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
    esac
    
    # 启动Docker并设置开机自启
    systemctl start docker
    systemctl enable docker
    
    # 添加当前用户到docker组(如果存在)
    if [[ -n "$SUDO_USER" ]]; then
        usermod -aG docker "$SUDO_USER"
        print_step "已将用户 $SUDO_USER 添加到docker组"
        print_warning "请重新登录或运行: newgrp docker"
    fi
    
    print_success "Docker安装完成: $(docker --version)"
}

# 安装Docker Compose独立版本
install_docker_compose() {
    # 检查docker compose plugin
    if docker compose version &> /dev/null; then
        print_warning "Docker Compose已安装(v2): $(docker compose version)"
        return
    fi
    
    # 检查旧版本docker-compose
    if command -v docker-compose &> /dev/null; then
        print_warning "旧版docker-compose已安装: $(docker-compose --version)"
        print_step "建议使用 Docker Compose Plugin (v2)"
        return
    fi
    
    print_step "安装Docker Compose..."
    
    # 下载最新版本
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
    curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_success "Docker Compose安装完成: $(docker-compose --version)"
}

# 配置防火墙
configure_firewall() {
    print_step "检查防火墙配置..."
    
    # 检查UFW
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            print_step "配置UFW防火墙..."
            ufw allow 22/tcp comment 'SSH'
            ufw allow 80/tcp comment 'HTTP'
            ufw allow 443/tcp comment 'HTTPS'
            ufw allow 5000/tcp comment 'GEO API'
            print_success "防火墙规则已配置"
        fi
    fi
    
    # 检查firewalld
    if command -v firewall-cmd &> /dev/null; then
        if systemctl is-active --quiet firewalld; then
            print_step "配置firewalld防火墙..."
            firewall-cmd --permanent --add-service=http
            firewall-cmd --permanent --add-service=https
            firewall-cmd --permanent --add-port=5000/tcp
            firewall-cmd --reload
            print_success "防火墙规则已配置"
        fi
    fi
}

# 配置系统参数
configure_system() {
    print_step "配置系统参数..."
    
    # 关闭swap(生产环境推荐)
    if [[ $(swapon -s | wc -l) -gt 1 ]]; then
        read -p "是否关闭swap? (生产环境推荐) [y/N]: " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            swapoff -a
            sed -i '/swap/d' /etc/fstab
            print_success "Swap已关闭"
        fi
    fi
    
    # 配置内核参数
    cat > /etc/sysctl.d/99-geo-insight.conf << 'EOF'
# 好易易GEO 生产环境内核参数
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 4096
vm.max_map_count = 262144
EOF
    
    sysctl -p /etc/sysctl.d/99-geo-insight.conf
    print_success "系统参数配置完成"
}

# 创建应用目录
create_directories() {
    print_step "创建应用目录..."
    
    APP_DIR="/opt/geo-insight"
    mkdir -p "$APP_DIR"
    
    # 创建数据目录
    mkdir -p "$APP_DIR/data"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/backups"
    
    # 设置权限
    chmod 755 "$APP_DIR"
    
    print_success "应用目录已创建: $APP_DIR"
}

# 配置日志轮转
configure_logrotate() {
    print_step "配置日志轮转..."
    
    cat > /etc/logrotate.d/geo-insight << 'EOF'
/opt/geo-insight/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        docker-compose -f /opt/geo-insight/docker-compose.yml restart backend > /dev/null 2>&1 || true
    endscript
}
EOF
    
    print_success "日志轮转配置完成"
}

# 显示完成信息
show_completion() {
    echo ""
    echo "========================================"
    echo "  服务器初始化完成!"
    echo "========================================"
    echo ""
    echo "已安装组件:"
    echo "  - Docker:          $(docker --version | cut -d' ' -f3 | tr -d ',')"
    echo "  - Docker Compose:   $(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1)"
    echo ""
    echo "应用目录: /opt/geo-insight"
    echo ""
    echo "后续步骤:"
    echo "  1. 上传代码到 /opt/geo-insight"
    echo "  2. 复制环境配置: cp deploy/.env.example .env"
    echo "  3. 编辑 .env 填写 DEEPSEEK_API_KEY"
    echo "  4. 运行部署脚本: ./deploy/deploy.sh"
    echo ""
    echo "常用命令:"
    echo "  查看服务状态:  cd /opt/geo-insight && docker-compose ps"
    echo "  查看日志:      cd /opt/geo-insight && docker-compose logs -f"
    echo "  重启服务:      cd /opt/geo-insight && docker-compose restart"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "========================================"
    echo "  好易易GEO 服务器初始化脚本"
    echo "========================================"
    echo ""
    
    check_root
    detect_os
    
    if [[ "$1" != "--non-interactive" ]]; then
        read -p "是否继续安装? [Y/n]: " confirm
        confirm=${confirm:-Y}
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
    fi
    
    update_system
    install_dependencies
    install_docker
    install_docker_compose
    configure_firewall
    configure_system
    create_directories
    configure_logrotate
    
    show_completion
}

main "$@"
