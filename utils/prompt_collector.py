# -*- coding: utf-8 -*-
"""
好易易GEO - AI对话型Prompt采集模块
采集用户向AI大模型提问时的真实问题，用于GEO优化

核心功能：
1. 构建多类型Prompt种子（品牌咨询、场景推荐、对比分析、评测攻略）
2. 搜索验证Prompt在AI搜索中的出现频率
3. 按类型分类生成结构化Prompt列表
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PromptType(Enum):
    """Prompt类型枚举"""
    BRAND_CONSULT = "品牌咨询"      # 品牌咨询型
    SCENE_RECOMMEND = "场景推荐"    # 场景推荐型
    COMPARE_ANALYSIS = "对比分析"   # 对比分析型
    REVIEW_GUIDE = "评测攻略"       # 评测攻略型


class Frequency(Enum):
    """出现频率枚举"""
    HIGH = "高频"     # 高频（搜索结果多且相关）
    MEDIUM = "中频"   # 中频（搜索结果一般）
    LOW = "低频"      # 低频（搜索结果较少）
    UNKNOWN = "未知"  # 未经搜索验证


@dataclass
class AIPrompt:
    """单个AI Prompt对象"""
    question: str                    # 问题文本
    prompt_type: PromptType           # Prompt类型
    frequency: Frequency = Frequency.UNKNOWN  # 出现频率
    source_hint: str = ""             # 来源提示
    search_verified: bool = False     # 是否经过搜索验证

    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "type": self.prompt_type.value,
            "frequency": self.frequency.value,
            "source_hint": self.source_hint,
            "search_verified": self.search_verified
        }


# 默认场景词库
DEFAULT_SCENE_WORDS = {
    # 购物类
    "购物", "逛街", "买衣服", "买包", "买化妆品", "奢侈品",
    # 餐饮类
    "吃饭", "约会", "聚餐", "商务宴请", "家庭聚餐", "朋友聚会",
    # 休闲类
    "下午茶", "看电影", "喝咖啡", "休闲娱乐",
    # 特殊场景
    "生日", "纪念日", "遛娃", "亲子", "情侣约会",
    # 其他
    "逛商场", "周末去哪", "节假日", "打卡", "拍照"
}

# 场景分类
SCENE_CATEGORIES = {
    "约会场景": ["约会", "情侣约会", "纪念日", "生日", "浪漫"],
    "家庭场景": ["遛娃", "亲子", "家庭聚餐", "带孩子"],
    "社交场景": ["朋友聚会", "聚餐", "下午茶", "喝咖啡"],
    "购物场景": ["购物", "逛街", "买衣服", "买包", "奢侈品", "化妆品"],
    "商务场景": ["商务宴请", "商务接待", "谈事情"],
    "休闲场景": ["看电影", "休闲娱乐", "放松", "打卡"]
}


def build_seed_prompts(brand_name: str, competitor_names: List[str], city: str) -> List[AIPrompt]:
    """
    构建Prompt种子模板
    
    Args:
        brand_name: 品牌名（如"武汉万象城"）
        competitor_names: 竞品列表（如["武汉恒隆广场", "武商MALL"]）
        city: 城市（如"武汉"）
    
    Returns:
        初始Prompt种子列表（未经搜索验证）
    """
    prompts = []
    
    # 1. 品牌咨询型
    brand_consult_templates = [
        "{brand}怎么样？",
        "{brand}好不好？",
        "{brand}品牌档次高吗？",
        "{brand}值得去吗？",
        "{brand}是高端商场吗？",
        "{brand}算什么档次？",
        "{brand}口碑怎么样？",
    ]
    for template in brand_consult_templates:
        prompts.append(AIPrompt(
            question=template.format(brand=brand_name),
            prompt_type=PromptType.BRAND_CONSULT,
            source_hint="品牌咨询模板"
        ))
    
    # 2. 场景推荐型 - 品牌+场景
    scene_with_brand_templates = [
        "{brand}适合约会吗？",
        "{brand}适合遛娃吗？",
        "{brand}吃饭去哪里好？",
        "{brand}有什么好吃的？",
        "{brand}适合购物吗？",
        "{brand}有哪些品牌？",
        "{brand}有电影院吗？",
        "{brand}遛娃方便吗？",
    ]
    for template in scene_with_brand_templates:
        prompts.append(AIPrompt(
            question=template.format(brand=brand_name),
            prompt_type=PromptType.SCENE_RECOMMEND,
            source_hint="品牌场景模板"
        ))
    
    # 3. 城市+场景推荐型
    city_scene_templates = [
        "{city}适合约会的商场有哪些？",
        "{city}高端商场推荐",
        "{city}购物去哪里好？",
        "{city}遛娃的商场推荐",
        "{city}适合聚餐的商场",
        "{city}周末去哪逛街？",
        "{city}商场排名",
        "{city}最好的商场是哪家？",
    ]
    for template in city_scene_templates:
        prompts.append(AIPrompt(
            question=template.format(city=city),
            prompt_type=PromptType.SCENE_RECOMMEND,
            source_hint="城市场景模板"
        ))
    
    # 4. 对比分析型
    for competitor in competitor_names:
        compare_templates = [
            "{brand}和{competitor}哪个好？",
            "{brand}和{competitor}有什么区别？",
            "{brand}vs{competitor}选哪个？",
            "{competitor}好还是{brand}好？",
            "{brand}和{competitor}对比",
        ]
        for template in compare_templates:
            prompts.append(AIPrompt(
                question=template.format(brand=brand_name, competitor=competitor),
                prompt_type=PromptType.COMPARE_ANALYSIS,
                source_hint="竞品对比模板"
            ))
    
    # 5. 评测攻略型
    review_templates = [
        "{brand}逛街攻略",
        "{brand}必逛品牌推荐",
        "{brand}有什么亮点？",
        "{brand}值得打卡吗？",
        "去{brand}怎么逛？",
        "{brand}有哪些值得买的？",
    ]
    for template in review_templates:
        prompts.append(AIPrompt(
            question=template.format(brand=brand_name),
            prompt_type=PromptType.REVIEW_GUIDE,
            source_hint="评测攻略模板"
        ))
    
    return prompts


def build_scene_prompts(brand_name: str, city: str, 
                        scene_words: List[str] = None,
                        custom_scenes: Dict[str, List[str]] = None) -> List[AIPrompt]:
    """
    构建场景化Prompt
    
    Args:
        brand_name: 品牌名
        city: 城市名
        scene_words: 自定义场景词列表
        custom_scenes: 自定义场景分类 {场景类型: [场景词列表]}
    
    Returns:
        场景化Prompt列表
    """
    prompts = []
    scenes = scene_words or list(DEFAULT_SCENE_WORDS)
    
    # 场景分类Prompt
    if custom_scenes:
        for category, words in custom_scenes.items():
            for word in words:
                prompts.append(AIPrompt(
                    question=f"{city}适合{word}的商场有哪些？",
                    prompt_type=PromptType.SCENE_RECOMMEND,
                    source_hint=f"场景分类-{category}"
                ))
                prompts.append(AIPrompt(
                    question=f"{brand_name}适合{word}吗？",
                    prompt_type=PromptType.SCENE_RECOMMEND,
                    source_hint=f"场景分类-{category}"
                ))
    
    # 通用场景Prompt
    for scene in scenes:
        templates = [
            f"{city}哪里适合{scene}？",
            f"{city}哪里{scene}好？",
            f"{brand_name}适合{{0}}吗？".format(scene),
            f"{scene}去{city}哪里好？",
        ]
        for template in templates:
            if "哪里" not in template.split("好")[0] if "好" in template else True:
                prompts.append(AIPrompt(
                    question=template,
                    prompt_type=PromptType.SCENE_RECOMMEND,
                    source_hint="通用场景模板"
                ))
    
    return prompts


def parse_brand_city(brand_name: str) -> Tuple[str, str]:
    """
    从品牌名中解析城市
    
    Args:
        brand_name: 品牌名（如"武汉万象城"）
    
    Returns:
        (城市, 纯品牌名)
    """
    # 常见城市列表
    cities = [
        "北京", "上海", "广州", "深圳", "成都", "杭州", "重庆", "武汉",
        "西安", "苏州", "南京", "天津", "长沙", "郑州", "东莞", "青岛",
        "沈阳", "宁波", "昆明", "大连", "无锡", "佛山", "合肥", "福州",
        "厦门", "济南", "哈尔滨", "长春", "南昌", "贵阳", "南宁", "石家庄"
    ]
    
    city = ""
    pure_brand = brand_name
    
    for c in cities:
        if brand_name.startswith(c):
            city = c
            pure_brand = brand_name[len(c):]
            break
    
    return city, pure_brand


def filter_by_frequency(prompts: List[AIPrompt], 
                        min_frequency: Frequency = Frequency.UNKNOWN) -> List[AIPrompt]:
    """
    按频率过滤Prompt
    
    Args:
        prompts: Prompt列表
        min_frequency: 最低频率要求
    
    Returns:
        过滤后的Prompt列表
    """
    freq_order = {Frequency.UNKNOWN: 0, Frequency.LOW: 1, Frequency.MEDIUM: 2, Frequency.HIGH: 3}
    min_level = freq_order.get(min_frequency, 0)
    
    return [p for p in prompts if freq_order.get(p.frequency, 0) >= min_level]


def group_by_type(prompts: List[AIPrompt]) -> Dict[str, List[Dict]]:
    """
    按类型分组Prompt
    
    Args:
        prompts: Prompt列表
    
    Returns:
        按类型分组的字典
    """
    grouped = {}
    for p in prompts:
        type_name = p.prompt_type.value
        if type_name not in grouped:
            grouped[type_name] = []
        grouped[type_name].append(p.to_dict())
    return grouped


def count_by_category(prompts: List[AIPrompt]) -> Dict[str, int]:
    """
    统计各类型Prompt数量
    
    Args:
        prompts: Prompt列表
    
    Returns:
        各类型数量字典
    """
    counts = {}
    for p in prompts:
        type_name = p.prompt_type.value
        counts[type_name] = counts.get(type_name, 0) + 1
    return counts


def verify_prompt_frequency(query: str) -> Tuple[Frequency, int]:
    """
    通过搜索验证Prompt出现频率
    
    Args:
        query: 搜索词
    
    Returns:
        (频率级别, 预估搜索结果数)
    """
    # 注意：这里需要调用search_web工具验证
    # 在collect_ai_prompts主函数中实现
    return Frequency.UNKNOWN, 0


def collect_ai_prompts(brand_name: str, 
                       competitor_names: List[str] = None,
                       city: str = None,
                       industry: str = "商业地产",
                       max_prompts: int = 50,
                       include_scene_prompts: bool = True) -> Dict:
    """
    采集AI对话型真实Prompt
    
    主函数：构建并可选验证Prompt列表
    
    Args:
        brand_name: 品牌名（如"武汉万象城"）
        competitor_names: 竞品列表（如["武汉恒隆广场", "武商MALL"]）
        city: 城市（如"武汉"，未提供则自动解析）
        industry: 行业（如"商业地产"/"本地生活"）
        max_prompts: 最大Prompt数量
        include_scene_prompts: 是否包含场景Prompt
    
    Returns:
        {
            "prompts": [
                {
                    "question": "武汉万象城怎么样？",
                    "type": "品牌咨询",
                    "frequency": "高频",
                    "source_hint": "AI搜索高频问题"
                },
                ...
            ],
            "categories": {
                "品牌咨询": 10,
                "场景推荐": 20,
                "对比分析": 8,
                "评测攻略": 12
            },
            "metadata": {
                "brand_name": "武汉万象城",
                "city": "武汉",
                "competitors": ["武汉恒隆广场", "武商MALL"],
                "total_count": 50
            }
        }
    """
    # 参数预处理
    if not competitor_names:
        competitor_names = []
    if not city:
        city, _ = parse_brand_city(brand_name)
    if not city:
        city = "本地"
    
    # 1. 构建种子Prompt
    seed_prompts = build_seed_prompts(brand_name, competitor_names, city)
    
    # 2. 构建场景Prompt（可选）
    all_prompts = seed_prompts.copy()
    if include_scene_prompts:
        scene_prompts = build_scene_prompts(brand_name, city)
        all_prompts.extend(scene_prompts)
    
    # 3. 按最大数量截取
    if len(all_prompts) > max_prompts:
        # 优先保留种子Prompt，再按类型均匀抽取场景Prompt
        remaining = max_prompts - len(seed_prompts)
        if remaining > 0 and include_scene_prompts:
            scene_prompts = build_scene_prompts(brand_name, city)
            all_prompts = seed_prompts + scene_prompts[:remaining]
        else:
            all_prompts = all_prompts[:max_prompts]
    
    # 4. 转换为字典格式输出
    prompt_list = [p.to_dict() for p in all_prompts]
    
    # 5. 统计各类型数量
    categories = count_by_category(all_prompts)
    
    # 6. 构建元数据
    metadata = {
        "brand_name": brand_name,
        "city": city,
        "competitors": competitor_names,
        "industry": industry,
        "total_count": len(all_prompts)
    }
    
    return {
        "prompts": prompt_list,
        "categories": categories,
        "metadata": metadata
    }


def get_prompt_templates() -> Dict[str, List[str]]:
    """
    获取Prompt模板库
    
    Returns:
        按类型分类的Prompt模板
    """
    return {
        "品牌咨询": [
            "{brand}怎么样？",
            "{brand}好不好？",
            "{brand}品牌档次高吗？",
            "{brand}值得去吗？",
            "{brand}是高端商场吗？",
            "{brand}算什么档次？",
        ],
        "场景推荐": [
            "{city}适合{场景}的商场有哪些？",
            "{city}哪里适合{场景}？",
            "{brand}适合{场景}吗？",
            "{city}{场景}去哪里好？",
        ],
        "对比分析": [
            "{brand}和{竞品}哪个好？",
            "{brand}和{竞品}有什么区别？",
            "{brand}vs{竞品}选哪个？",
        ],
        "评测攻略": [
            "{brand}逛街攻略",
            "{brand}必逛品牌推荐",
            "去{brand}怎么逛？",
            "{brand}有什么亮点？",
        ]
    }


# 便捷函数
def quick_collect(brand_name: str, competitors: List[str] = None) -> Dict:
    """
    快速采集（自动解析城市）
    
    Args:
        brand_name: 品牌名
        competitors: 竞品列表
    
    Returns:
        Prompt采集结果
    """
    city, pure_brand = parse_brand_city(brand_name)
    return collect_ai_prompts(
        brand_name=brand_name,
        competitor_names=competitors or [],
        city=city,
        max_prompts=50
    )
