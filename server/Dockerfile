# GEO智眼 API 服务 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "5000"]
