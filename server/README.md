# 好易易GEO API 服务

让网页能真正调用 DeepSeek API 进行分析的后端服务。

## 🚀 快速开始

### 方式一：直接运行

```bash
# 进入服务目录
cd geo-insight/server

# 安装依赖
pip install -r requirements.txt

# 启动服务
python api_server.py
# 或使用 uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 5000 --reload
```

### 方式二：使用启动脚本

```bash
cd geo-insight/server
chmod +x start.sh
./start.sh
```

### 方式三：Docker 部署

```bash
cd geo-insight
docker-compose up -d
```

## 📡 API 接口

### 健康检查

```bash
GET /api/health
```

响应示例：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "ai_service": "DeepSeek",
  "platforms": ["豆包", "元宝", "Kimi", "通义", "文心", "天工"]
}
```

### 品牌分析

```bash
POST /api/analyze
Content-Type: application/json

{
  "type": "brand_analysis",
  "brand": "武汉万象城",
  "industry": "本地生活"
}
```

响应示例：
```json
{
  "success": true,
  "data": {
    "brand_name": "武汉万象城",
    "industry": "本地生活",
    "ai_mentions": "中等",
    "sentiment": "正面为主",
    "key_features": ["高端定位", "品牌丰富", "地理位置优越"],
    "geo_score": 82,
    "recommendations": [...]
  },
  "ai_used": "DeepSeek",
  "platforms_analyzed": ["豆包", "元宝", "Kimi", "通义", "文心", "天工"]
}
```

### 支持的分析类型

| type 值 | 说明 |
|---------|------|
| `brand_analysis` | 品牌健康度分析 |
| `competitor_analysis` | 竞品对比分析 |
| `content_strategy` | 内容策略生成 |

## 🧪 测试

```bash
cd geo-insight/server
python test_api.py
```

## 📁 目录结构

```
geo-insight/
├── server/
│   ├── api_server.py      # API 服务主文件
│   ├── requirements.txt   # Python 依赖
│   ├── start.sh          # 启动脚本
│   ├── test_api.py       # 测试脚本
│   └── Dockerfile        # Docker 配置
├── web_demo.html         # 前端演示页面
└── docker-compose.yml    # Docker Compose 配置
```

## ⚙️ 配置

DeepSeek API Key 已配置在代码中：
- API URL: `https://api.deepseek.com/v1/chat/completions`
- Model: `deepseek-chat`

如需修改，请编辑 `api_server.py` 中的配置常量。

## 🌐 访问地址

服务启动后：
- API 服务: http://localhost:5000
- API 文档: http://localhost:5000/docs (Swagger UI)
- 健康检查: http://localhost:5000/api/health
