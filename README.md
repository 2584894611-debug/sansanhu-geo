# 好易易GEO - B端AI搜索分析工具

> 帮助品牌方洞察AI搜索推荐，优化GEO策略

## 国内GEO完整流程框架

| 步骤 | 功能模块 | 说明 |
|------|----------|------|
| 1️⃣ | AI推荐分析 | 问AI会推荐什么品牌 |
| 2️⃣ | 高权重平台分析 | 小红书/知乎/公众号内容布局 |
| 3️⃣ | 内容优化建议 | 评测/对比/攻略模板 |
| 4️⃣ | 关键词策略 | 植入建议 |
| 5️⃣ | AI Schema生成 | 让AI"认识"品牌 |
| 6️⃣ | 监测预警 | 追踪推荐变化 |

## 核心功能

### 1. 🔍 AI搜索推荐分析
- 输入搜索词，分析6大AI平台的推荐结果
- 提取推荐理由、排名、置信度
- 洞察AI推荐逻辑和热门关键词

### 2. 🏢 竞品GEO分析
- 输入竞品名称，分析竞品在AI搜索中的表现
- 多平台对比，提取推荐理由
- 生成竞品对比报告

### 3. 🏥 品牌健康诊断
- 分析自有品牌在AI搜索中的表现
- 计算GEO健康评分（S/A/B/C/D等级）
- 识别优化机会点

### 4. 📝 内容策略生成
- 根据AI推荐逻辑生成内容布局策略
- 匹配高权重内容类型（评测/对比/攻略）
- 生成平台适配的内容计划
- 提供内容模板和标题建议

### 5. 🏷️ AI Schema生成
- Organization Schema（组织信息）
- Brand Schema（品牌信息）
- Product Schema（产品信息）
- FAQ Schema（常见问题）
- HowTo Schema（操作指南）
- 一键生成部署代码

### 6. 📊 监测预警
- 追踪关键词排名变化
- 品牌可见性评分
- 异常预警通知
- 历史数据对比

### 7. 📄 报告生成
- HTML格式报告（可打印为PDF）
- 数据可视化
- 可下载分享

## 支持平台

| 平台 | 类型 | 数据获取 |
|------|------|----------|
| 字节豆包 | AI搜索 | 搜索API + 爬虫 |
| 阿里千问 | AI搜索 | 搜索API + 爬虫 |
| 深度求索DeepSeek | AI搜索 | 搜索API |
| 腾讯元宝 | AI搜索 | 搜索API + 爬虫 |
| 月之暗面Kimi | AI搜索 | 搜索API |
| 智谱AI | AI搜索 | 搜索API |

## 高权重内容平台

- 小红书
- 知乎
- 微信公众号
- 抖音
- B站

## 项目结构

```
geo-insight/
├── cloudfunctions/
│   ├── aiSearchAnalysis/     # AI搜索推荐分析
│   ├── analyzeCompetitor/    # 竞品GEO分析
│   ├── brandDiagnosis/       # 品牌健康诊断
│   ├── contentStrategy/      # 内容策略生成
│   ├── schemaGenerator/      # AI Schema生成
│   ├── monitoring/          # 监测预警
│   └── generateReport/       # 报告生成
├── components/
│   └── ...                  # 组件
├── pages/
│   ├── aiSearch/            # AI搜索分析页面
│   ├── analyze/             # 竞品分析页面
│   ├── diagnosis/           # 品牌诊断页面
│   ├── content/             # 内容策略页面
│   ├── schema/             # Schema生成页面
│   └── monitor/             # 监测预警页面
├── templates/               # 模板文件
├── utils/                   # 工具函数
│   ├── ai_aggregator.py     # AI聚合接口
│   ├── platform_config.py   # 平台权重配置
│   └── feishu_pusher.py     # 飞书推送模块 ✨
├── cli.py                   # CLI命令行工具 ✨
├── web_demo.html            # Web演示页面
└── README.md
```

## CLI 命令行工具

```bash
# 进入目录
cd geo-insight

# 分析品牌（支持飞书推送）
python cli.py analyze "武汉万象城" --industry 本地生活 --push-feishu

# 竞品分析
python cli.py competitor "武汉万象城" "武商MALL" "恒隆广场"

# 生成报告
python cli.py report "武汉万象城" --format docx

# 查看平台权重
python cli.py weights --industry 本地生活

# 测试飞书连接
python cli.py test
```

## 飞书集成

分析完成后可自动推送结果到飞书多维表格：

| 分析字段 | 飞书表格字段 |
|---------|-------------|
| 品牌名称 | 选题 |
| 行业分类 | 分类 |
| 分析结论 | 爆点分析 |
| 平台数据 | 备注 |

## 版本规划

- v1.0：竞品分析 + 品牌诊断
- v1.1：AI搜索分析 + 内容策略
- v1.2：Schema生成 + 监测预警
- v2.0：数据看板 + 自动化运营

## License

MIT
