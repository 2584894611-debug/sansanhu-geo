#!/bin/bash
#===============================================================================
# 好易易GEO 容器启动脚本
# 
# 使用方式:
#   ./start.sh          # 前台启动
#   ./start.sh -d      # 后台启动
#   ./start.sh stop    # 停止服务
#   ./start.sh restart # 重启服务
#   ./start.sh logs    # 查看日志
#
#===============================================================================

cd "$(dirname "$0")/.."

case "${1:-}" in
    -d|--detach)
        docker-compose -f deploy/docker-compose.yml up -d
        echo "服务已在后台启动"
        ;;
    stop)
        docker-compose -f deploy/docker-compose.yml down
        echo "服务已停止"
        ;;
    restart)
        docker-compose -f deploy/docker-compose.yml restart
        echo "服务已重启"
        ;;
    logs)
        docker-compose -f deploy/docker-compose.yml logs -f
        ;;
    ps)
        docker-compose -f deploy/docker-compose.yml ps
        ;;
    health)
        echo "检查服务健康状态..."
        curl -sf http://localhost:5000/health && echo " - Backend OK" || echo " - Backend FAIL"
        ;;
    *)
        docker-compose -f deploy/docker-compose.yml up
        ;;
esac
