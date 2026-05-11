# 好易易GEO 后端 FastAPI 服务 Dockerfile
# 多阶段构建：构建阶段 + 运行阶段

# ============ 阶段1: 构建阶段 ============
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============ 阶段2: 运行阶段 ============
FROM python:3.11-slim

LABEL maintainer="好易易GEO Team"
LABEL description="好易易GEO AI搜索分析后端API服务"

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    WORKDIR=/app

# 安装运行时依赖（非root用户）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && useradd --create-home --shell /bin/bash appuser \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY --chown=appuser:appuser api_server.py .

# 创建数据目录
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# 切换到非root用户
USER appuser

# 添加pip bin到PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "5000"]
