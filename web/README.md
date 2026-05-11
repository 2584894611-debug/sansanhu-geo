# 好易易GEO Web平台

AI搜索优化分析平台 - Vue3 + FastAPI 完整项目

## 项目结构

```
geo-insight/
├── web/                      # Vue3 前端项目
│   ├── src/
│   │   ├── api/              # API 调用
│   │   ├── components/       # Vue 组件
│   │   ├── pages/            # 页面
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── styles/           # 样式
│   │   ├── router/           # 路由配置
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── server/                    # FastAPI 后端
│   ├── api_server.py        # API 服务
│   └── requirements.txt
├── tasks/                     # 自动化脚本
│   └── auto_collector.py    # 数据采集
└── data/                      # 数据库
    └── geo.db
```

## 功能特性

### Freemium 模式

| 功能 | 免费用户 | 付费用户 |
|:---|:---:|:---:|
| 品牌基础分析 | ✅ 1次/天 | ✅ 无限 |
| GEO评分展示 | ✅ | ✅ |
| 问题诊断 | ✅ 简要(3条) | ✅ 完整 |
| 竞品对比 | ❌ | ✅ |
| 优化建议 | ❌ | ✅ |
| 效果监测 | ❌ | ✅ |
| 报告下载 | ❌ | ✅ |

### Web 界面

1. **首页** - 品牌分析入口
2. **报告详情页** - 完整分析报告
3. **监测页** - 评分趋势追踪
4. **个人中心** - 用户状态管理

## 快速开始

### 1. 后端服务

```bash
# 进入后端目录
cd geo-insight/server

# 安装依赖
pip install fastapi uvicorn httpx

# 启动服务
python api_server.py
```

服务地址: http://localhost:5000

### 2. 前端项目

```bash
# 进入前端目录
cd geo-insight/web

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

前端地址: http://localhost:3000

### 3. 自动化采集

```bash
# 查看帮助
python geo-insight/tasks/auto_collector.py --help

# 添加品牌到监控
python geo-insight/tasks/auto_collector.py --add "品牌名" "行业"

# 查看监控列表
python geo-insight/tasks/auto_collector.py --list

# 执行采集任务
python geo-insight/tasks/auto_collector.py
```

### 4. 定时任务配置 (Linux/Mac)

```bash
# 编辑 crontab
crontab -e

# 添加定时任务 (每天凌晨2点执行)
0 2 * * * cd /path/to/geo-insight && python tasks/auto_collector.py >> logs/cron.log 2>&1
```

## API 接口

### 用户状态
```
GET /api/user/status?device_id=xxx
```

### 品牌分析
```
POST /api/analyze
{
  "type": "brand_analysis",
  "brand": "品牌名",
  "industry": "行业",
  "device_id": "设备ID"
}
```

### 分析历史
```
GET /api/analysis/history?device_id=xxx&limit=20
```

### 评分趋势
```
GET /api/brand/trend?brand=品牌名&days=30
```

### 预警信息
```
GET /api/alerts?brand=品牌名
```

### 激活付费
```
POST /api/premium/activate?token=激活码&device_id=xxx
```

## 环境变量

```bash
# DeepSeek API Key
DEEPSEEK_API_KEY=sk-xxxxxxxx

# 数据库路径 (可选)
DATABASE_PATH=./data/geo.db
```

## 技术栈

- **前端**: Vue 3 + Vite + Vue Router + Pinia + ECharts
- **后端**: FastAPI + Python 3.10+
- **数据库**: SQLite
- **AI服务**: DeepSeek API

## 设计规范

### 配色方案
- 主色: #1a365d (深蓝)
- 强调色: #D4AF37 (金色)
- 背景: 渐变 #1a365d -> #2d4a6f

### 字体
- 主字体: 系统默认 (SF Pro / Segoe UI / Roboto)

## 联系方式

- 电话: 189 8603 4050
- 服务时间: 周一至周五 9:00-18:00

## License

MIT License
