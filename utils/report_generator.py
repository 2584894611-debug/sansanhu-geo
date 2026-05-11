# -*- coding: utf-8 -*-
"""
好易易GEO - 报告生成器
生成结构化GEO分析报告（Markdown格式）
集成Prompt采集模块，支持AI搜索Prompt分析
"""

from datetime import datetime
from typing import Dict, List, Optional

# 导入Prompt采集模块
from .prompt_collector import (
    PromptType, Frequency, AIPrompt,
    collect_ai_prompts, count_by_category, group_by_type,
    build_seed_prompts, quick_collect
)


def generate_geo_report(brand_data: Dict, platform_data: Dict) -> str:
    """
    生成结构化GEO分析报告
    
    Args:
        brand_data: 品牌数据，包含:
            - brand_name: 品牌名称
            - industry: 行业
            - geo_score: GEO健康评分
            - visibility: 可见度评分
            - recommendation: 推荐度评分
            - sentiment: 情感倾向
            - mentions: AI提及次数
            - competitors: 竞品列表
            - recommendations: 优化建议
        platform_data: 平台数据，包含各平台的提及情况
    
    Returns:
        Markdown格式的报告文本
    """
    brand_name = brand_data.get('brand_name', '未知品牌')
    industry = brand_data.get('industry', '未知行业')
    geo_score = brand_data.get('geo_score', 0)
    report_date = datetime.now().strftime('%Y年%m月%d日')
    
    # 生成评分等级
    score_level = _get_score_level(geo_score)
    
    report = f"""# {brand_name} GEO分析报告

> **报告日期**：{report_date}  
> **所属行业**：{industry}  
> **分析工具**：好易易GEO

---

## 执行摘要

{_generate_executive_summary(brand_data)}

---

## 一、AI搜索表现

### 1.1 品牌可见度分析

{_generate_visibility_analysis(brand_data, platform_data)}

### 1.2 平台提及详情

{_generate_platform_mentions_table(platform_data)}

### 1.3 AI推荐理由

{_generate_recommendation_reasons(brand_data)}

---

## 二、品牌健康度

### 2.1 GEO健康评分

{_generate_health_score_section(brand_data)}

### 2.2 三维度评估

{_generate_three_dimension_evaluation(brand_data)}

### 2.3 健康度趋势

{_generate_health_trend(brand_data)}

---

## 三、竞品对比

### 3.1 竞品概述

{_generate_competitor_overview(brand_data)}

### 3.2 竞品对比分析

{_generate_competitor_comparison(brand_data)}

### 3.3 竞争优势识别

{_generate_competitive_advantage(brand_data)}

---

## 四、AI搜索Prompt分析

### 4.1 Prompt采集概述

{_generate_prompt_overview(brand_data)}

### 4.2 品牌相关Prompt列表

{_generate_brand_prompts_list(brand_data)}

### 4.3 Prompt分布统计

{_generate_prompt_distribution(brand_data)}

### 4.4 Prompt优化建议

{_generate_prompt_optimization_suggestions(brand_data)}

---

## 五、优化建议

### 5.1 优先级矩阵

{_generate_optimization_priority_matrix(brand_data)}

### 4.2 具体优化措施

{_generate_specific_optimization_measures(brand_data)}

### 4.3 风险预警

{_generate_risk_alerts(brand_data)}

---

## 六、内容策略

### 6.1 关键词布局

{_generate_keyword_strategy(brand_data)}

### 5.2 内容类型建议

{_generate_content_type_suggestions(brand_data)}

### 5.3 平台投放策略

{_generate_platform_strategy(platform_data)}

---

## 附录

### A. 数据来源

- AI搜索平台：豆包、千问、DeepSeek、元宝、Kimi、智谱AI
- 高权重内容平台：小红书、知乎、微信公众号、抖音、B站
- 数据采集时间：{report_date}

### B. 评分标准

| 评分范围 | 等级 | 说明 |
|:---:|:---:|:---|
| 90-100 | S | 极优秀，AI搜索首选推荐 |
| 80-89 | A | 优秀，AI搜索高频提及 |
| 70-79 | B | 良好，AI搜索稳定可见 |
| 60-69 | C | 一般，AI搜索偶尔提及 |
| <60 | D | 不足，需要重点优化 |

### C. 术语说明

| 术语 | 说明 |
|:---|:---|
| GEO | Generative Engine Optimization，生成式引擎优化 |
| 可见度 | 品牌在AI搜索结果中被提及的频率 |
| 推荐度 | AI搜索结果中品牌被推荐的概率 |
| 情感倾向 | 品牌相关内容的正面/中性/负面比例 |

---

> 本报告由 **好易易GEO** 自动生成  
> 如有疑问，请联系技术支持
"""
    
    return report


def _get_score_level(score: float) -> str:
    """根据评分返回等级标签"""
    if score >= 90:
        return "S级 ⭐⭐⭐⭐⭐"
    elif score >= 80:
        return "A级 ⭐⭐⭐⭐"
    elif score >= 70:
        return "B级 ⭐⭐⭐"
    elif score >= 60:
        return "C级 ⭐⭐"
    else:
        return "D级 ⭐"


def _generate_executive_summary(brand_data: Dict) -> str:
    """生成执行摘要"""
    brand_name = brand_data.get('brand_name', '')
    geo_score = brand_data.get('geo_score', 0)
    visibility = brand_data.get('visibility', 0)
    recommendation = brand_data.get('recommendation', 0)
    sentiment = brand_data.get('sentiment', {})
    competitors = brand_data.get('competitors', [])
    
    positive_ratio = sentiment.get('positive', 50)
    negative_ratio = sentiment.get('negative', 20)
    
    summary = f"""通过对 **{brand_name}** 在主流AI搜索平台的表现进行综合分析，得出以下核心发现：

- **GEO健康评分**：{geo_score}分（{_get_score_level(geo_score)}），整体表现**{"优秀" if geo_score >= 80 else "良好" if geo_score >= 70 else "一般" if geo_score >= 60 else "需重点优化"}**
- **可见度评分**：{visibility}分，在AI搜索中具有**{"极高的" if visibility >= 80 else "较高的" if visibility >= 70 else "一般的" if visibility >= 60 else "较低的"}可见性**
- **推荐度评分**：{recommendation}分，AI对品牌的推荐意愿**{"很强" if recommendation >= 80 else "较强" if recommendation >= 70 else "一般" if recommendation >= 60 else "较弱"}**
- **情感倾向**：正面评价占比{positive_ratio}%，负面评价占比{negative_ratio}%，整体舆情**{"积极" if positive_ratio > 60 else "中性偏正" if positive_ratio > 40 else "中性偏负" if negative_ratio < 30 else "需要关注"}**

**核心优势**：
{_generate_core_strengths(brand_data)}

**主要挑战**：
{_generate_core_challenges(brand_data)}
"""
    return summary


def _generate_core_strengths(brand_data: Dict) -> str:
    """生成核心优势描述"""
    strengths = brand_data.get('strengths', [])
    if strengths:
        return '\n'.join([f"{i+1}. {s}" for i, s in enumerate(strengths[:3])])
    return "数据不足，请补充品牌信息"


def _generate_core_challenges(brand_data: Dict) -> str:
    """生成主要挑战描述"""
    challenges = brand_data.get('challenges', [])
    if challenges:
        return '\n'.join([f"{i+1}. {c}" for i, c in enumerate(challenges[:3])])
    return "暂无明显挑战"


def _generate_visibility_analysis(brand_data: Dict, platform_data: Dict) -> str:
    """生成可见度分析"""
    total_mentions = brand_data.get('mentions', 0)
    visibility = brand_data.get('visibility', 0)
    
    analysis = f"""在本次AI搜索分析中，**{brand_data.get('brand_name', '')}** 累计获得 **{total_mentions}次** AI平台提及。

可见度评估结果：
- 整体可见度得分：{visibility}/100
- {"品牌在AI搜索中具有极高的曝光率，是用户查询时的首选推荐对象" if visibility >= 80 else "品牌在AI搜索中具有较高的可见性，但仍有提升空间" if visibility >= 70 else "品牌在AI搜索中的可见性一般，需要加强内容布局" if visibility >= 60 else "品牌在AI搜索中的可见性不足，需要重点优化"}
- 高权重平台覆盖率：{_calculate_platform_coverage(platform_data)}%

**可见度提升关键点**：
1. 增加在{_get_high_weight_platforms(platform_data)}等高权重平台的内容布局
2. 强化品牌核心关键词的结构化呈现
3. 建立品牌与场景词的关联
"""
    return analysis


def _calculate_platform_coverage(platform_data: Dict) -> int:
    """计算平台覆盖率"""
    if not platform_data:
        return 0
    covered = sum(1 for mentions in platform_data.values() if mentions > 0)
    total = len(platform_data) if platform_data else 1
    return int((covered / total) * 100)


def _get_high_weight_platforms(platform_data: Dict) -> str:
    """获取高权重平台列表"""
    high_weight = ['小红书', '知乎', '微信公众号']
    if not platform_data:
        return '、'.join(high_weight)
    
    available = [p for p in high_weight if platform_data.get(p, 0) > 0]
    return '、'.join(available) if available else '、'.join(high_weight)


def _generate_platform_mentions_table(platform_data: Dict) -> str:
    """生成平台提及详情表格"""
    if not platform_data:
        return "暂无平台数据"
    
    table = """| 平台 | 类型 | 提及次数 | 权重 | 表现 |
|:---|:---:|:---:|:---:|:---:|
"""
    platform_types = {
        '豆包': 'AI搜索', '千问': 'AI搜索', 'DeepSeek': 'AI搜索',
        '元宝': 'AI搜索', 'Kimi': 'AI搜索', '智谱AI': 'AI搜索',
        '小红书': '种草平台', '知乎': '知识平台', '微信公众号': '私域平台',
        '抖音': '短视频平台', 'B站': '视频平台'
    }
    
    for platform, mentions in platform_data.items():
        ptype = platform_types.get(platform, '其他')
        weight = "⭐⭐⭐" if ptype in ['种草平台', '知识平台'] else "⭐⭐"
        performance = "优秀" if mentions >= 10 else "良好" if mentions >= 5 else "一般"
        table += f"| {platform} | {ptype} | {mentions} | {weight} | {performance} |\n"
    
    return table


def _generate_recommendation_reasons(brand_data: Dict) -> str:
    """生成AI推荐理由"""
    reasons = brand_data.get('ai_reasons', [])
    if not reasons:
        return "暂无AI推荐理由数据"
    
    content = "AI平台在推荐该品牌时，主要基于以下理由：\n\n"
    for i, reason in enumerate(reasons[:5], 1):
        content += f"{i}. **{reason['title']}**：{reason['description']}\n"
    
    return content


def _generate_health_score_section(brand_data: Dict) -> str:
    """生成健康评分部分"""
    geo_score = brand_data.get('geo_score', 0)
    score_level = _get_score_level(geo_score)
    
    # 生成ASCII评分条
    bar_length = 20
    filled = int((geo_score / 100) * bar_length)
    score_bar = "█" * filled + "░" * (bar_length - filled)
    
    section = f"""### GEO健康评分：{geo_score}/100

```
[{score_bar}] {geo_score}%
```

**评分等级**：{score_level}

{_get_score_description(geo_score)}
"""
    return section


def _get_score_description(score: float) -> str:
    """根据评分生成描述"""
    if score >= 90:
        return "品牌在AI搜索生态中表现极佳，是用户查询时的首选推荐对象。建议保持当前策略，持续优化内容质量。"
    elif score >= 80:
        return "品牌在AI搜索中具有较强的竞争力，处于行业领先地位。建议关注竞品动态，持续保持优势。"
    elif score >= 70:
        return "品牌在AI搜索中表现良好，具有一定的可见性。建议加强内容优化，进一步提升排名。"
    elif score >= 60:
        return "品牌在AI搜索中表现一般，需要加强GEO优化。建议制定系统性的内容策略，提升品牌可见度。"
    else:
        return "品牌在AI搜索中可见性不足，建议立即制定GEO优化计划，重点突破关键领域。"


def _generate_three_dimension_evaluation(brand_data: Dict) -> str:
    """生成三维度评估"""
    visibility = brand_data.get('visibility', 0)
    recommendation = brand_data.get('recommendation', 0)
    sentiment = brand_data.get('sentiment', {})
    positive = sentiment.get('positive', 50)
    
    section = """| 评估维度 | 评分 | 等级 | 状态 |
|:---|:---:|:---:|:---:|
"""
    
    dimensions = [
        ('可见度', visibility),
        ('推荐度', recommendation),
        ('情感倾向', positive)
    ]
    
    for name, score in dimensions:
        level = "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D"
        status = "🟢 优秀" if score >= 80 else "🟡 良好" if score >= 70 else "🟠 一般" if score >= 60 else "🔴 需改善"
        section += f"| {name} | {score}/100 | {level}级 | {status} |\n"
    
    section += "\n**评估说明**：\n"
    section += "- **可见度**：品牌在AI搜索结果中被提及的频率和覆盖范围\n"
    section += "- **推荐度**：AI在回答相关问题时推荐该品牌的概率\n"
    section += "- **情感倾向**：与品牌相关内容的正面评价占比\n"
    
    return section


def _generate_health_trend(brand_data: Dict) -> str:
    """生成健康度趋势"""
    trend = brand_data.get('trend', 'stable')
    
    trend_desc = {
        'rising': '📈 上升趋势 - 品牌在AI搜索中的表现持续改善',
        'stable': '➡️ 稳定趋势 - 品牌表现保持平稳',
        'declining': '📉 下降趋势 - 品牌可见度有所下滑，需要关注'
    }
    
    return trend_desc.get(trend, trend_desc['stable'])


def _generate_competitor_overview(brand_data: Dict) -> str:
    """生成竞品概述"""
    competitors = brand_data.get('competitors', [])
    
    if not competitors:
        return "暂无竞品数据"
    
    overview = f"""本次分析纳入了{len(competitors)}个主要竞品进行对比分析：

"""
    
    for i, comp in enumerate(competitors[:5], 1):
        name = comp.get('name', '未知')
        score = comp.get('geo_score', 0)
        rank = comp.get('rank', i)
        overview += f"{i}. **{name}** - GEO评分：{score}分 - 排名第{rank}\n"
    
    return overview


def _generate_competitor_comparison(brand_data: Dict) -> str:
    """生成竞品对比分析"""
    brand_name = brand_data.get('brand_name', '')
    brand_score = brand_data.get('geo_score', 0)
    competitors = brand_data.get('competitors', [])
    
    if not competitors:
        return "暂无竞品对比数据"
    
    # 找出排名
    all_brands = [{'name': brand_name, 'geo_score': brand_score}] + competitors
    all_brands.sort(key=lambda x: x['geo_score'], reverse=True)
    brand_rank = next((i+1 for i, b in enumerate(all_brands) if b['name'] == brand_name), 0)
    
    content = f"""### {brand_name} vs 竞品

**当前排名**：{brand_rank}/{len(all_brands)}

| 对比维度 | {brand_name} | 竞品均值 | 差距 |
|:---|:---:|:---:|:---:|
"""
    
    # 计算各维度对比
    metrics = [
        ('GEO评分', 'geo_score'),
        ('可见度', 'visibility'),
        ('推荐度', 'recommendation')
    ]
    
    for label, key in metrics:
        brand_val = brand_data.get(key, 0)
        comp_avg = sum(c.get(key, 0) for c in competitors) / len(competitors) if competitors else 0
        diff = brand_val - comp_avg
        diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
        content += f"| {label} | {brand_val:.1f} | {comp_avg:.1f} | {diff_str} |\n"
    
    return content


def _generate_competitive_advantage(brand_data: Dict) -> str:
    """生成竞争优势识别"""
    advantages = brand_data.get('advantages', [])
    
    content = "### 差异化竞争优势\n\n"
    
    if advantages:
        for i, adv in enumerate(advantages[:3], 1):
            content += f"**{i}. {adv.get('title', '优势点')}**：{adv.get('description', '')}\n\n"
    else:
        content += "暂无明确的差异化竞争优势数据\n"
    
    content += "\n### 劣势分析\n\n"
    weaknesses = brand_data.get('weaknesses', [])
    if weaknesses:
        for i, weak in enumerate(weaknesses[:3], 1):
            content += f"**{i}. {weak.get('title', '劣势点')}**：{weak.get('description', '')}\n\n"
    else:
        content += "暂无明显的竞争劣势\n"
    
    return content


def _generate_optimization_priority_matrix(brand_data: Dict) -> str:
    """生成优化优先级矩阵"""
    recommendations = brand_data.get('recommendations', [])
    
    if not recommendations:
        return "暂无优化建议数据"
    
    table = """| 优先级 | 优化方向 | 预期效果 | 实施难度 |
|:---:|:---|:---|:---:|
"""
    
    priority_map = {
        'urgent': '🔴 紧急',
        'high': '🟠 高',
        'medium': '🟡 中',
        'low': '🟢 低'
    }
    
    difficulty_map = {
        'hard': '高',
        'medium': '中',
        'easy': '低'
    }
    
    for rec in recommendations[:6]:
        priority = priority_map.get(rec.get('priority', 'medium'), '🟡 中')
        direction = rec.get('title', '待优化项')
        effect = rec.get('effect', '待评估')
        difficulty = difficulty_map.get(rec.get('difficulty', 'medium'), '中')
        table += f"| {priority} | {direction} | {effect} | {difficulty} |\n"
    
    return table


def _generate_specific_optimization_measures(brand_data: Dict) -> str:
    """生成具体优化措施"""
    recommendations = brand_data.get('recommendations', [])
    
    content = ""
    
    for i, rec in enumerate(recommendations[:4], 1):
        title = rec.get('title', f'优化项{i}')
        description = rec.get('description', '')
        actions = rec.get('actions', [])
        
        content += f"### {i}. {title}\n\n"
        content += f"{description}\n\n"
        
        if actions:
            content += "**实施步骤**：\n"
            for j, action in enumerate(actions[:4], 1):
                content += f"{j}. {action}\n"
            content += "\n"
    
    return content if content else "暂无具体优化措施数据"


# ============== Prompt分析相关函数 ==============

def _generate_prompt_overview(brand_data: Dict) -> str:
    """生成Prompt采集概述"""
    brand_name = brand_data.get('brand_name', '未知品牌')
    competitors = brand_data.get('competitors', [])
    competitor_names = [c.get('name', '') for c in competitors] if competitors else []
    
    # 调用prompt_collector采集Prompt
    prompt_data = collect_ai_prompts(
        brand_name=brand_name,
        competitor_names=competitor_names,
        max_prompts=50,
        include_scene_prompts=True
    )
    
    total_prompts = prompt_data.get('metadata', {}).get('total_count', 0)
    categories = prompt_data.get('categories', {})
    
    # 计算品牌直接相关的Prompt数量
    brand_related = sum(1 for p in prompt_data.get('prompts', []) 
                       if brand_name in p.get('question', ''))
    
    overview = f"""通过采集用户在AI搜索平台上的真实提问，分析 **{brand_name}** 在各类型Prompt下的表现。

**采集统计**：
- **Prompt总数**：{total_prompts}个
- **品牌直接相关**：{brand_related}个
- **Prompt类型覆盖**：{len(categories)}类

**采集方法**：
1. 品牌咨询型：直接提及品牌名称的问题
2. 场景推荐型：城市+场景词组合的泛化问题
3. 对比分析型：与竞品对比的相关问题
4. 评测攻略型：攻略、评测类深度问题
"""
    return overview


def _generate_brand_prompts_list(brand_data: Dict) -> str:
    """生成品牌相关Prompt列表"""
    brand_name = brand_data.get('brand_name', '未知品牌')
    competitors = brand_data.get('competitors', [])
    competitor_names = [c.get('name', '') for c in competitors] if competitors else []
    
    # 采集Prompt
    prompt_data = collect_ai_prompts(
        brand_name=brand_name,
        competitor_names=competitor_names,
        max_prompts=30,
        include_scene_prompts=False  # 只采集种子Prompt
    )
    
    prompts = prompt_data.get('prompts', [])
    
    # 按类型分组展示
    grouped = group_by_type([AIPrompt(
        question=p['question'],
        prompt_type=PromptType(p['type']),
        frequency=Frequency(p['frequency']),
        source_hint=p.get('source_hint', '')
    ) for p in prompts])
    
    content = ""
    
    # 品牌咨询类
    if '品牌咨询' in grouped:
        content += "#### 1️⃣ 品牌咨询类（万象城怎么样？）\n\n"
        for p in grouped['品牌咨询'][:5]:
            content += f"- {p['question']}\n"
        content += "\n"
    
    # 场景推荐类
    if '场景推荐' in grouped:
        content += "#### 2️⃣ 场景推荐类（适合约会的商场）\n\n"
        for p in grouped['场景推荐'][:5]:
            content += f"- {p['question']}\n"
        content += "\n"
    
    # 对比分析类
    if '对比分析' in grouped:
        content += "#### 3️⃣ 对比分析类（万象城vs恒隆）\n\n"
        for p in grouped['对比分析'][:4]:
            content += f"- {p['question']}\n"
        content += "\n"
    
    # 评测攻略类
    if '评测攻略' in grouped:
        content += "#### 4️⃣ 评测攻略类（值得去吗？）\n\n"
        for p in grouped['评测攻略'][:5]:
            content += f"- {p['question']}\n"
        content += "\n"
    
    return content if content else "暂无品牌相关Prompt数据"


def _generate_prompt_distribution(brand_data: Dict) -> str:
    """生成Prompt分布统计"""
    brand_name = brand_data.get('brand_name', '未知品牌')
    competitors = brand_data.get('competitors', [])
    competitor_names = [c.get('name', '') for c in competitors] if competitors else []
    
    # 采集Prompt
    prompt_data = collect_ai_prompts(
        brand_name=brand_name,
        competitor_names=competitor_names,
        max_prompts=50
    )
    
    categories = prompt_data.get('categories', {})
    total = sum(categories.values()) if categories else 1
    
    # 生成ASCII饼图
    type_names = {
        '品牌咨询': '咨询',
        '场景推荐': '场景',
        '对比分析': '对比',
        '评测攻略': '攻略'
    }
    
    # ASCII柱状图
    max_bar = 25
    chart = "```\n📊 Prompt类型分布\n════════════════════════════════════════════════\n"
    
    for ptype, count in sorted(categories.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        bar_len = int((count / total) * max_bar) if total > 0 else 0
        bar = '█' * bar_len + '░' * (max_bar - bar_len)
        short_name = type_names.get(ptype, ptype[:2])
        chart += f"{short_name:>4} │ {bar} │ {count:>2} ({pct:>5.1f}%)\n"
    
    chart += "════════════════════════════════════════\n```\n"
    
    # 表格
    table = "| Prompt类型 | 数量 | 占比 | 说明 |\n"
    table += "|:---|:---:|:---:|:---|\n"
    
    descriptions = {
        '品牌咨询': '直接提问品牌的评价、口碑',
        '场景推荐': '包含场景需求的泛化问题',
        '对比分析': '与竞品进行对比的问题',
        '评测攻略': '攻略、评测、体验类问题'
    }
    
    for ptype, count in sorted(categories.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        desc = descriptions.get(ptype, '')
        table += f"| {ptype} | {count} | {pct:.1f}% | {desc} |\n"
    
    return chart + "\n" + table


def _generate_prompt_optimization_suggestions(brand_data: Dict) -> str:
    """生成Prompt优化建议"""
    brand_name = brand_data.get('brand_name', '未知品牌')
    geo_score = brand_data.get('geo_score', 0)
    visibility = brand_data.get('visibility', 0)
    
    suggestions = []
    
    # 基于评分生成建议
    if geo_score < 70:
        suggestions.append({
            'type': '品牌咨询类',
            'issue': f'当前GEO评分({geo_score}分)偏低，品牌在AI搜索中的可见度不足',
            'action': f'建议加强品牌正面内容建设，在小红书、知乎等平台发布品牌评测文章',
            'priority': '🔴 高优先级'
        })
    
    if visibility < 70:
        suggestions.append({
            'type': '场景推荐类',
            'issue': '场景推荐类Prompt下品牌提及率低',
            'action': '建议创作「周末去哪」「约会圣地」等场景化内容，建立场景与品牌的强关联',
            'priority': '🟠 中优先级'
        })
    
    # 通用建议
    suggestions.extend([
        {
            'type': '对比分析类',
            'issue': '竞品对比类问题中品牌容易被竞品压制',
            'action': '建议制作「万象城VS竞品」系列内容，突出差异化优势',
            'priority': '🟡 中优先级'
        },
        {
            'type': '评测攻略类',
            'issue': '攻略类内容覆盖不足，深度不够',
            'action': '建议发布「必逛指南」「隐藏打卡点」等攻略类内容',
            'priority': '🟡 中优先级'
        }
    ])
    
    content = "基于Prompt分析，建议优先优化以下方向：\n\n"
    
    for i, sug in enumerate(suggestions, 1):
        content += f"#### {sug['priority']} {sug['type']}\n\n"
        content += f"**问题**：{sug['issue']}\n\n"
        content += f"**优化方向**：{sug['action']}\n\n"
    
    return content


def _generate_risk_alerts(brand_data: Dict) -> str:
    """生成风险预警"""
    risks = brand_data.get('risks', [])
    
    if not risks:
        return "✅ 暂未发现明显风险，建议保持当前优化策略"
    
    content = "⚠️ 以下风险需要重点关注：\n\n"
    
    for i, risk in enumerate(risks[:3], 1):
        level = risk.get('level', 'medium')
        level_icon = '🔴' if level == 'high' else '🟠' if level == 'medium' else '🟡'
        content += f"**{level_icon} {risk.get('title', f'风险{i}')}**：{risk.get('description', '')}\n\n"
    
    return content


def _generate_keyword_strategy(brand_data: Dict) -> str:
    """生成关键词策略"""
    keywords = brand_data.get('keywords', [])
    
    if not keywords:
        return "暂无关键词策略数据"
    
    content = "### 核心关键词布局\n\n"
    
    # 分类展示关键词
    keyword_groups = {
        'brand': {'name': '品牌词', 'keywords': []},
        'product': {'name': '产品词', 'keywords': []},
        'scene': {'name': '场景词', 'keywords': []},
        'industry': {'name': '行业词', 'keywords': []}
    }
    
    for kw in keywords:
        ktype = kw.get('type', 'industry')
        if ktype in keyword_groups:
            keyword_groups[ktype]['keywords'].append(kw.get('keyword', ''))
    
    for group in keyword_groups.values():
        if group['keywords']:
            content += f"**{group['name']}**：{'、'.join(group['keywords'][:5])}\n"
    
    content += "\n### 关键词优化建议\n\n"
    content += "1. 优先优化场景词，与品牌词形成强关联\n"
    content += "2. 布局长尾关键词，捕获细分需求\n"
    content += "3. 监控关键词排名变化，及时调整策略\n"
    
    return content


def _generate_content_type_suggestions(brand_data: Dict) -> str:
    """生成内容类型建议"""
    content_types = brand_data.get('content_types', [
        {'type': '评测类', 'weight': 30, 'description': '产品/服务深度评测'},
        {'type': '对比类', 'weight': 25, 'description': '与竞品形成差异化对比'},
        {'type': '攻略类', 'weight': 25, 'description': '场景化使用指南'},
        {'type': '故事类', 'weight': 20, 'description': '品牌/用户故事'}
    ])
    
    table = """| 内容类型 | 建议占比 | 说明 |
|:---|:---:|:---|
"""
    
    for ct in content_types:
        table += f"| {ct.get('type', '')} | {ct.get('weight', 0)}% | {ct.get('description', '')} |\n"
    
    return table


def _generate_platform_strategy(platform_data: Dict) -> str:
    """生成平台投放策略"""
    if not platform_data:
        return "暂无平台策略数据"
    
    # 按权重排序
    platform_priority = [
        ('小红书', '种草平台', '⭐⭐⭐'),
        ('知乎', '知识平台', '⭐⭐⭐'),
        ('微信公众号', '私域平台', '⭐⭐⭐'),
        ('抖音', '短视频平台', '⭐⭐'),
        ('B站', '视频平台', '⭐⭐')
    ]
    
    content = """| 平台 | 类型 | 优先级 | 投放建议 |
|:---|:---:|:---:|:---|
"""
    
    for name, ptype, priority in platform_priority:
        mentions = platform_data.get(name, 0)
        suggestion = "重点投放" if mentions == 0 else "持续优化" if mentions < 5 else "保持现状"
        content += f"| {name} | {ptype} | {priority} | {suggestion} |\n"
    
    return content


# 便捷函数
def generate_simple_report(brand_name: str, geo_score: int) -> str:
    """生成简化版报告（用于快速测试）"""
    return generate_geo_report(
        brand_data={
            'brand_name': brand_name,
            'industry': '通用',
            'geo_score': geo_score,
            'visibility': 75,
            'recommendation': 70,
            'sentiment': {'positive': 65, 'negative': 15},
            'mentions': 15,
            'competitors': [],
            'recommendations': []
        },
        platform_data={
            '小红书': 8,
            '知乎': 5,
            '微信公众号': 4,
            '抖音': 3,
            'B站': 2
        }
    )


if __name__ == '__main__':
    # 测试报告生成
    test_report = generate_simple_report('测试品牌', 78)
    print(test_report)
