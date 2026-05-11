# 好易易GEO - 数据采集模块

从6个AI搜索平台采集搜索结果的模块。

## 支持的平台

| 平台 | URL | API状态 | 说明 |
|------|-----|---------|------|
| 豆包 | doubao.com | ✗ 无API | 字节跳动，无公开搜索API |
| DeepSeek | chat.deepseek.com | ✓ 有API | 对话API，非搜索API |
| 元宝 | yuanbao.tencent.com | ✗ 无API | 腾讯，无公开搜索API |
| Kimi | kimi.moonshot.cn | ✓ 有API | 支持Tool Calling |
| 通义千问 | tongyi.aliyun.com | ✓ 有API | 阿里云，需要API Key |
| 智谱 | zhipuai.cn | ✓ 有API | 智谱AI，需要API Key |

## 安装

```bash
# 确保在 geo-insight 目录
cd geo-insight

# 运行测试
python utils/test_data_collector.py
```

## 使用方法

### 1. 单平台采集

```python
from utils.data_collector import collect_from_platform

# 从单个平台采集
result = collect_from_platform("DeepSeek", "咖啡厅推荐", use_mock=True)

print(f"平台: {result['platform']}")
print(f"结果数: {result['count']}")
for r in result['results']:
    print(f"  - {r['title']}")
```

### 2. 全平台采集

```python
from utils.data_collector import collect_from_all_platforms

# 从所有平台采集
result = collect_from_all_platforms("北京周末好去处", use_mock=True)

print(f"关键词: {result['keyword']}")
print(f"总结果数: {result['total_count']}")

# 遍历各平台结果
for platform, data in result['platforms'].items():
    print(f"{platform}: {data['count']} 条")
```

### 3. 快速搜索

```python
from utils.data_collector import quick_search

# 一行代码快速搜索
result = quick_search("附近火锅店")
print(f"共获取 {result['total_count']} 条结果")
```

## API配置

如需使用真实API，设置环境变量：

```bash
# Kimi API
export MOONSHOT_API_KEY="your-api-key"

# 通义千问 API
export DASHSCOPE_API_KEY="your-api-key"

# 智谱 API
export ZHIPU_API_KEY="your-api-key"
```

## 返回格式

```python
{
    "keyword": "搜索关键词",
    "total_count": 15,
    "platforms": {
        "DeepSeek": {
            "results": [
                {
                    "title": "结果标题",
                    "content": "结果内容摘要",
                    "source": "来源",
                    "url": "https://..."
                }
            ],
            "count": 3,
            "success": True,
            "error": None,
            "is_mock": True  # 是否使用模拟数据
        },
        # ... 其他平台
    },
    "summary": {
        "total_platforms": 6,
        "success_count": 6,
        "failed_count": 0,
        "success_platforms": ["DeepSeek", "Kimi", ...],
        "message": "从 6/6 个平台采集成功，共获取 15 条结果"
    }
}
```

## 技术说明

### 为什么需要模拟数据？

目前这些AI平台的官方API主要是**对话API**，不是专门的**搜索API**：

- **DeepSeek API**: 提供对话能力，无内置搜索
- **Kimi API**: 支持Tool Calling，可调用web_search，但需要额外配置
- **通义千问/智谱**: 对话API，搜索功能需单独申请

因此本模块采用：
1. 优先尝试真实API调用
2. 自动降级到模拟数据（用于演示和测试）
3. 返回结果标注 `is_mock: True` 提示数据来源

### 获取真实搜索数据的方式

1. **豆包/元宝**: 无公开API，需使用平台官方APP手动搜索
2. **DeepSeek/Kimi**: 可申请开发者API，配置Tool Calling
3. **通义千问/智谱**: 搜索API需单独申请企业资质

## 文件结构

```
geo-insight/
├── utils/
│   ├── data_collector.py      # 数据采集模块 (本文件)
│   ├── test_data_collector.py # 测试脚本
│   ├── ai_aggregator.py      # AI聚合接口
│   └── platform_config.py    # 平台权重配置
└── ...
```
