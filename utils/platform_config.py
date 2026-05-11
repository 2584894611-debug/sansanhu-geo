"""
好易易GEO - 平台权重配置
基于2026年5月AI产品月活数据 + 本地生活场景分析
"""

# =============================================
# 通用行业权重（综合参考）
# =============================================
PLATFORM_WEIGHTS = {
    "豆包": {
        "weight": 0.35,
        "monthly_active": "3.45亿",
        "rank": 1,
        "note": "行业第一，AI推荐影响力最大"
    },
    "通义千问": {
        "weight": 0.20,
        "monthly_active": "1.66亿",
        "rank": 2,
        "note": "电商场景强"
    },
    "DeepSeek": {
        "weight": 0.20,
        "monthly_active": "1.27亿",
        "rank": 3,
        "note": "技术派，API调用量高"
    },
    "Kimi": {
        "weight": 0.12,
        "monthly_active": "~1亿",
        "rank": 4,
        "note": "专业用户，长文本"
    },
    "元宝": {
        "weight": 0.08,
        "monthly_active": "5700万",
        "rank": 5,
        "note": "腾讯生态"
    },
    "智谱": {
        "weight": 0.05,
        "monthly_active": "<5000万",
        "rank": 6,
        "note": "垂直领域"
    }
}

# =============================================
# 本地生活类权重（商场/餐饮/本地服务）
# 核心逻辑：微信生态 + 种草内容 + 地理定位
# =============================================
LOCAL_LIFE_WEIGHTS = {
    "元宝": {
        "weight": 0.30,
        "monthly_active": "5700万",
        "rank": 1,
        "reason": "微信搜一搜、本地生活推荐最强，公众号/朋友圈种草闭环"
    },
    "豆包": {
        "weight": 0.28,
        "monthly_active": "3.45亿",
        "rank": 2,
        "reason": "抖音本地生活、小红书种草，用户最多"
    },
    "通义千问": {
        "weight": 0.18,
        "monthly_active": "1.66亿",
        "rank": 3,
        "reason": "高德/饿了么场景，消费决策参考"
    },
    "DeepSeek": {
        "weight": 0.12,
        "monthly_active": "1.27亿",
        "rank": 4,
        "reason": "攻略/测评类内容，决策参考"
    },
    "Kimi": {
        "weight": 0.08,
        "monthly_active": "~1亿",
        "rank": 5,
        "reason": "长攻略/深度测评，本地场景弱"
    },
    "智谱": {
        "weight": 0.04,
        "monthly_active": "<5000万",
        "rank": 6,
        "reason": "补充参考"
    }
}

# =============================================
# 行业分类权重
# =============================================
INDUSTRY_PLATFORM_WEIGHTS = {
    "通用": PLATFORM_WEIGHTS,
    "本地生活": LOCAL_LIFE_WEIGHTS,
    "商场/商业地产": LOCAL_LIFE_WEIGHTS,  # 归为本地生活
    "餐饮": LOCAL_LIFE_WEIGHTS,
    "本地服务": LOCAL_LIFE_WEIGHTS,
    
    "科技/数码": {
        "DeepSeek": {"weight": 0.30, "reason": "技术用户最集中"},
        "豆包": {"weight": 0.25, "reason": "大众科技内容"},
        "通义千问": {"weight": 0.20, "reason": "电商场景强"},
        "Kimi": {"weight": 0.15, "reason": "专业评测"},
        "元宝": {"weight": 0.07, "reason": "社交分享"},
        "智谱": {"weight": 0.03, "reason": "补充参考"}
    },
    
    "美妆/护肤": {
        "豆包": {"weight": 0.35, "reason": "小红书种草最强"},
        "通义千问": {"weight": 0.25, "reason": "电商转化高"},
        "元宝": {"weight": 0.18, "reason": "口碑传播"},
        "Kimi": {"weight": 0.10, "reason": "成分分析"},
        "DeepSeek": {"weight": 0.08, "reason": "技术对比"},
        "智谱": {"weight": 0.04, "reason": "补充参考"}
    },
    
    "汽车": {
        "通义千问": {"weight": 0.30, "reason": "汽车之家/易车合作"},
        "DeepSeek": {"weight": 0.25, "reason": "参数分析强"},
        "豆包": {"weight": 0.22, "reason": "新车推荐"},
        "Kimi": {"weight": 0.12, "reason": "深度测评"},
        "元宝": {"weight": 0.08, "reason": "社交分享"},
        "智谱": {"weight": 0.03, "reason": "补充参考"}
    }
}

# 行业关键词映射
INDUSTRY_KEYWORDS = {
    "本地生活": ["附近", "推荐", "好吃", "好玩", "逛街", "商场", "购物中心", "餐厅", "奶茶", "火锅", "烧烤", "网红店"],
    "商场/商业地产": ["商场", "购物中心", "商圈", "万达", "万象城", "大悦城", "恒隆", "SKP", "武商", "银泰", "金鹰"],
    "餐饮": ["餐厅", "美食", "火锅", "烧烤", "咖啡", "奶茶", "餐饮", "网红店", "必吃", "探店"],
    "科技/数码": ["手机", "电脑", "芯片", "AI", "科技", "数码", "智能硬件", "手机", "电脑"],
    "美妆/护肤": ["化妆品", "护肤品", "美妆", "护肤", "口红", "香水", "精华", "面霜"],
    "汽车": ["汽车", "电动车", "新车", "4S店", "试驾", "购车", "买车", "新能源"]
}

def get_industry_from_keywords(text: str) -> str:
    """根据关键词识别行业"""
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return industry
    return "通用"

def get_platform_weights(industry: str = "通用") -> dict:
    """获取行业对应的平台权重"""
    return INDUSTRY_PLATFORM_WEIGHTS.get(industry, PLATFORM_WEIGHTS)

def print_weights_table():
    """打印权重对比表"""
    print("\n📊 本地生活类平台权重（商场/餐饮/本地服务）\n")
    print("-" * 60)
    for platform, info in sorted(LOCAL_LIFE_WEIGHTS.items(), key=lambda x: -x[1]['weight']):
        bar = "█" * int(info['weight'] * 40)
        print(f"{platform:8s} {info['weight']*100:5.1f}% {bar}")
        print(f"{'':8s} {'':6s} └─ {info['reason']}")
    print("-" * 60)

if __name__ == "__main__":
    print("🔍 好易易GEO 平台权重配置\n")
    print_weights_table()
