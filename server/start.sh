#!/bin/bash
# GEO智眼 API 服务启动脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "🚀 GEO智眼 API 服务启动中..."
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 创建虚拟环境（如果不存在）
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 安装依赖
echo "📥 安装依赖包..."
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

echo ""
echo "=========================================="
echo "✅ 依赖安装完成"
echo "=========================================="
echo ""
echo "🔧 配置信息:"
echo "   - API服务端口: 5000"
echo "   - API文档地址: http://localhost:5000/docs"
echo "   - 分析接口: POST http://localhost:5000/api/analyze"
echo ""
echo "=========================================="
echo ""

# 启动服务
echo "🚀 启动服务..."
cd "$PROJECT_DIR"
python -m uvicorn server.api_server:app --host 0.0.0.0 --port 5000 --reload
