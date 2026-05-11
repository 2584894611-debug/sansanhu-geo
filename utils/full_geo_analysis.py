# -*- coding: utf-8 -*-
"""
好易易GEO - 完整GEO分析流程集成
整合Prompt采集、GEO报告生成、内容诊断三大模块

使用方法：
    from full_geo_analysis import full_geo_analysis
    
    result = full_geo_analysis(
        brand_name="武汉万象城",
        competitor_names=["武汉恒隆广场", "武商MALL"],
        city="武汉",
        industry="商业地产"
    )
"""

from typing import Dict, List, Optional
from datetime import datetime

# 导入三个核心模块
from .prompt_collector import (
    collect_ai_prompts,
    count_by_category,
    group_by_type,
    PromptType,
    build_seed_prompts,
    parse_brand_city
)

from .checklist_diagnosis import diagnose_content

from .report_generator import generate_geo_report


def full_geo_analysis(
    brand_name: str,
    competitor_names: List[str],
    city: str = None,
    industry: str = "商业地产",
    content: str = None,
    max_prompts: int = 50,
    include_scene_prompts: bool = True
) -> dict:
    """
    完整GEO分析流程
    
    步骤：
    1. Prompt采集 - 采集品牌相关AI搜索Prompt
    2. GEO报告生成 - 生成GEO分析报告
    3. 内容诊断 - 诊断客户内容的GEO达标情况
    4. 优化建议 - 综合输出优化方案
    
    Args:
        brand_name: 品牌名称（如"武汉万象城"）
        competitor_names: 竞品列表（如["武汉恒隆广场", "武商MALL"]）
        city: 城市（如"武汉"，未提供则自动解析）
        industry: 行业（如"商业地产"/"本地生活"）
        content: 可选，客户自有内容，用于诊断
        max_prompts: 最大Prompt采集数量，默认50
        include_scene_prompts: 是否包含场景Prompt，默认True
    
    Returns:
        dict: 完整分析结果，包含:
            - brand: 品牌名称
            - city: 城市
            - industry: 行业
            - prompt_analysis: Prompt分析结果
            - geo_score: GEO综合评分
            - diagnosis: 内容诊断结果
            - optimization_suggestions: 优化建议
            - report: Markdown格式完整报告
    """
    # 步骤1：自动解析城市（如果未提供）
    if not city:
        city, _ = parse_brand_city(brand_name)
    if not city:
        city = "本地"
    
    # 步骤2：Prompt采集
    prompt_result = collect_ai_prompts(
        brand_name=brand_name,
        competitor_names=competitor_names,
        city=city,
        industry=industry,
        max_prompts=max_prompts,
        include_scene_prompts=include_scene_prompts
    )
    
    # 步骤3：生成示例内容（如果没有提供内容）
    if not content:
        content = _generate_sample_content(brand_name, competitor_names, city)
    
    # 步骤4：内容诊断
    diagnosis = diagnose_content(content)
    
    # 步骤5：计算GEO综合评分
    geo_score = _calculate_geo_score(prompt_result, diagnosis)
    
    # 步骤6：生成优化建议
    optimization_suggestions = _generate_optimization_suggestions(diagnosis)
    
    # 步骤7：构建Prompt分析摘要
    prompt_analysis = {
        "total": prompt_result["metadata"]["total_count"],
        "categories": prompt_result["categories"],
        "high_frequency_prompts": _extract_high_frequency_prompts(prompt_result)
    }
    
    # 步骤8：生成完整Markdown报告
    report = _generate_full_report(
        brand_name=brand_name,
        city=city,
        industry=industry,
        prompt_analysis=prompt_analysis,
        geo_score=geo_score,
        diagnosis=diagnosis,
        optimization_suggestions=optimization_suggestions,
        competitor_names=competitor_names
    )
    
    # 返回完整结果
    return {
        "brand": brand_name,
        "city": city,
        "industry": industry,
        "competitors": competitor_names,
        "prompt_analysis": prompt_analysis,
        "geo_score": geo_score,
        "diagnosis": {
            "score": diagnosis["score"],
            "passed": diagnosis["passed"],
            "failed": diagnosis["failed"],
            "overall": diagnosis["overall"],
            "priority_fixes": diagnosis["priority_fixes"]
        },
        "optimization_suggestions": optimization_suggestions,
        "report": report
    }


def _generate_sample_content(brand_name: str, competitor_names: List[str], city: str) -> str:
    """
    生成示例品牌内容用于诊断
    
    Args:
        brand_name: 品牌名
        competitor_names: 竞品列表
        city: 城市
    
    Returns:
        示例Markdown内容
    """
    competitors_str = "、".join(competitor_names) if competitor_names else "其他商场"
    
    return f"""# {brand_name}怎么样？

{brand_name}是{city}知名的高端商业综合体，涵盖购物、餐饮、娱乐、休闲等多种业态。

## 基本信息

- 位置：{city}核心商圈
- 定位：高端商业综合体
- 业态：购物、餐饮、娱乐、休闲

## 品牌推荐

{brand_name}汇聚了众多国内外知名品牌，包括国际奢侈品、时尚服饰、特色餐饮等。

{brand_name}逛街攻略：
1. 一楼以国际品牌和化妆品为主
2. 二三楼聚焦时尚服饰
3. 四楼餐饮汇聚各类美食
4. 五楼休闲娱乐设施完善

去{brand_name}怎么逛？
- 建议从一楼开始，逐层向上
- 热门品牌集中在中庭区域
- 餐饮集中在顶层

## 常见问答

Q: {brand_name}和{competitors_str}哪个好？
A: 各有特色，{brand_name}定位高端，业态齐全，适合追求品质的消费者。

Q: {brand_name}适合约会吗？
A: 非常适合，有众多餐厅和影院，氛围很好。

Q: {brand_name}有停车位吗？
A: 地下停车场充足，停车便利。
"""


def _extract_high_frequency_prompts(prompt_result: Dict, limit: int = 5) -> List[str]:
    """
    提取高频Prompt（按类型选取代表性样本）
    
    Args:
        prompt_result: Prompt采集结果
        limit: 每类型提取数量
    
    Returns:
        高频Prompt列表
    """
    prompts = prompt_result.get("prompts", [])
    if not prompts:
        return []
    
    # 按类型分组
    by_type = {}
    for p in prompts:
        ptype = p.get("type", "未知")
        if ptype not in by_type:
            by_type[ptype] = []
        by_type[ptype].append(p["question"])
    
    # 从各类型选取代表性样本
    samples = []
    for ptype, questions in by_type.items():
        samples.extend(questions[:2])  # 每类型取2个
    
    return samples[:limit]


def _calculate_geo_score(prompt_result: Dict, diagnosis: Dict) -> Dict:
    """
    计算GEO综合评分
    
    基于Prompt覆盖度、内容诊断得分、行业基准计算综合评分
    
    Args:
        prompt_result: Prompt采集结果
        diagnosis: 内容诊断结果
    
    Returns:
        GEO评分详情
    """
    # Prompt覆盖度得分（满分30）
    total_prompts = prompt_result["metadata"]["total_count"]
    prompt_score = min(30, total_prompts * 0.6)  # 每条Prompt约0.6分
    
    # 内容诊断得分（满分70）
    diagnosis_score = diagnosis["score"] * 0.7
    
    # 综合评分
    total_score = round(prompt_score + diagnosis_score)
    
    # 评分等级
    if total_score >= 90:
        level = "S级"
        level_desc = "优秀"
    elif total_score >= 75:
        level = "A级"
        level_desc = "良好"
    elif total_score >= 60:
        level = "B级"
        level_desc = "一般"
    else:
        level = "C级"
        level_desc = "需优化"
    
    # 可见度评分（Prompt数量转化）
    visibility = min(100, round(total_prompts * 2))
    
    # 推荐度评分（基于内容诊断）
    recommendation = diagnosis["score"]
    
    # 情感倾向（示例数据，实际应从外部获取）
    sentiment = min(100, diagnosis["score"] + 10)
    
    return {
        "total": total_score,
        "level": level,
        "level_desc": level_desc,
        "visibility": visibility,
        "recommendation": recommendation,
        "sentiment": sentiment,
        "prompt_contribution": round(prompt_score),
        "content_contribution": round(diagnosis_score)
    }


def _generate_optimization_suggestions(diagnosis: Dict) -> List[Dict]:
    """
    生成优化建议
    
    Args:
        diagnosis: 内容诊断结果
    
    Returns:
        优化建议列表，按优先级排序
    """
    suggestions = []
    
    # 优先级映射
    priority_map = {
        "🔴核心": ("P0", 15),
        "🟡建议": ("P1", 10),
    }
    
    for detail in diagnosis.get("details", []):
        if detail["status"] != "✅通过":
            priority_info = priority_map.get(detail["priority"], ("P2", 5))
            suggestions.append({
                "priority": priority_info[0],
                "issue": detail["item"],
                "suggestion": detail["suggestion"],
                "impact_score": priority_info[1],
                "status": detail["status"]
            })
    
    # 按优先级和影响分数排序
    suggestions.sort(key=lambda x: (x["priority"], -x["impact_score"]))
    
    return suggestions


def _generate_full_report(
    brand_name: str,
    city: str,
    industry: str,
    prompt_analysis: Dict,
    geo_score: Dict,
    diagnosis: Dict,
    optimization_suggestions: List[Dict],
    competitor_names: List[str]
) -> str:
    """
    生成完整Markdown分析报告
    
    Args:
        brand_name: 品牌名称
        city: 城市
        industry: 行业
        prompt_analysis: Prompt分析结果
        geo_score: GEO评分
        diagnosis: 诊断结果
        optimization_suggestions: 优化建议
        competitor_names: 竞品列表
    
    Returns:
        Markdown格式完整报告
    """
    report_date = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    # Prompt类型分布统计
    categories = prompt_analysis.get("categories", {})
    total = prompt_analysis.get("total", 0)
    category_lines = []
    for cat, count in categories.items():
        pct = round(count / total * 100) if total > 0 else 0
        category_lines.append(f"|   ├── {cat}：{count}条 ({pct}%)")
    category_dist = "\n".join(category_lines) if category_lines else "|   └── 暂无数据"
    
    # 高频Prompt列表
    high_freq = prompt_analysis.get("high_frequency_prompts", [])
    high_freq_lines = []
    for i, p in enumerate(high_freq, 1):
        high_freq_lines.append(f"{i}. {p}")
    high_freq_text = "\n".join(high_freq_lines) if high_freq_lines else "暂无数据"
    
    # 诊断详情
    diagnosis_details = diagnosis.get("details", [])
    diag_lines = []
    for d in diagnosis_details:
        status_icon = "✅" if d["status"] == "✅通过" else "❌" if "❌" in d["status"] else "⚠️"
        diag_lines.append(f"| {status_icon} {d['item']} | {d['status']} | {d['suggestion'][:30]}... |")
    diag_table = "\n".join(diag_lines) if diag_lines else "| 暂无诊断数据 |"
    
    # 优化建议
    sugg_lines = []
    for s in optimization_suggestions[:5]:  # 最多5条
        sugg_lines.append(f"- [{s['priority']}] {s['issue']} - {s['suggestion']}")
    sugg_text = "\n".join(sugg_lines) if sugg_lines else "暂无优化建议"
    
    # 竞品信息
    competitors_text = "、".join(competitor_names) if competitor_names else "暂无"
    
    report = f"""# 好易易GEO 完整分析报告

> **品牌**：{brand_name}  
> **城市**：{city}  
> **行业**：{industry}  
> **竞品**：{competitors_text}  
> **报告时间**：{report_date}

---

## 一、AI搜索Prompt分析

### Prompt采集概况

| 指标 | 数值 |
|------|------|
| 采集数量 | {total}条 |
| Prompt类型 | {len(categories)}种 |
| 覆盖场景 | 品牌咨询、场景推荐、对比分析、评测攻略 |

### Prompt类型分布

{category_dist}

### 高频Prompt样例

{high_freq_text}

---

## 二、GEO健康度评估

### 综合评分

| 维度 | 得分 | 权重 |
|------|------|------|
| **GEO综合评分** | **{geo_score['total']}分** ({geo_score['level']}) | 100% |
| 可见度评分 | {geo_score['visibility']}分 | 30% |
| 推荐度评分 | {geo_score['recommendation']}分 | 40% |
| 情感倾向 | {geo_score['sentiment']}% | 30% |

### 评分说明

- GEO评分 = Prompt覆盖度得分({geo_score['prompt_contribution']}) + 内容质量得分({geo_score['content_contribution']})
- 评分等级：S级(90+) > A级(75+) > B级(60+) > C级(60以下)
- 当前等级：**{geo_score['level']} {geo_score['level_desc']}**

---

## 三、内容诊断结果

### 诊断概览

| 指标 | 数值 |
|------|------|
| 诊断得分 | **{diagnosis['score']}分** ({diagnosis['overall']}) |
| 通过项 | {diagnosis['passed']}/{len(diagnosis_details)} |
| 未通过项 | {diagnosis['failed']}项 |
| 优先修复 | {len(diagnosis.get('priority_fixes', []))}项 |

### 详细诊断

| 检查项 | 状态 | 建议 |
|--------|------|------|
{diag_table}

### 优先修复项

{chr(10).join([f"- ❌ {p}" for p in diagnosis.get('priority_fixes', [])]) or '- 暂无核心项需修复'}

---

## 四、优化建议

### 优化优先级

{sugg_text}

### 优化效果预估

| 优先级 | 优化项 | 预估加分 |
|--------|--------|----------|
| P0 | 添加核心GEO元素 | +15分 |
| P1 | 完善建议项 | +10分 |
| P2 | 增强技术优化 | +5分 |

---

## 五、执行摘要

基于对{brand_name}的完整GEO分析，我们得出以下结论：

1. **Prompt覆盖度**：已采集{total}条AI搜索Prompt，覆盖{city}市场主要搜索场景
2. **内容健康度**：当前内容{diagnosis['overall']}，GEO评分为{geo_score['level']}
3. **核心问题**：{diagnosis['failed']}项检查未通过，主要集中在{diagnosis.get('priority_fixes', ['未知'])[0] if diagnosis.get('priority_fixes') else '综合优化'}
4. **优化建议**：建议优先处理{optimization_suggestions[0]['issue'] if optimization_suggestions else '内容结构优化'}

---

> 本报告由**好易易GEO**自动生成
> 集成 Prompt采集 → GEO报告 → 内容诊断 → 优化建议 全流程
"""
    
    return report


def print_full_report(result: dict) -> None:
    """
    打印完整报告到控制台
    
    Args:
        result: full_geo_analysis返回的结果
    """
    print("\n" + "=" * 50)
    print("         好易易GEO 完整分析报告")
    print("=" * 50)
    
    print(f"\n📊 品牌：{result['brand']}")
    print(f"🏙️ 城市：{result['city']}")
    print(f"🏢 行业：{result['industry']}")
    
    # Prompt分析
    print("\n一、AI搜索Prompt分析")
    print(f"├── 采集数量：{result['prompt_analysis']['total']}条")
    print("├── Prompt类型分布：")
    for cat, count in result['prompt_analysis']['categories'].items():
        print(f"│   ├── {cat}：{count}条")
    print("└── 高频Prompt：")
    for p in result['prompt_analysis']['high_frequency_prompts'][:3]:
        print(f"    - {p}")
    
    # GEO评分
    geo = result['geo_score']
    print(f"\n二、GEO健康度评估")
    print(f"├── GEO评分：{geo['total']}分 ({geo['level']})")
    print(f"├── 可见度：{geo['visibility']}分")
    print(f"├── 推荐度：{geo['recommendation']}分")
    print(f"└── 情感倾向：{geo['sentiment']}%")
    
    # 诊断结果
    diag = result['diagnosis']
    print(f"\n三、内容诊断")
    print(f"├── 诊断得分：{diag['score']}分 ({diag['overall']})")
    print(f"├── 通过项：{diag['passed']}")
    print(f"├── 未通过项：{diag['failed']}项")
    print("└── 优先修复：")
    for p in diag['priority_fixes'][:3]:
        print(f"    ├── ❌ {p}")
    
    # 优化建议
    print("\n四、优化建议")
    for i, s in enumerate(result['optimization_suggestions'][:3], 1):
        print(f"├── [{s['priority']}] {s['issue']}")
        print(f"│   建议：{s['suggestion']}")
    
    print("\n" + "=" * 50)


# 便捷函数
def quick_geo_analysis(brand_name: str, competitors: List[str] = None) -> dict:
    """
    快速GEO分析（自动解析城市）
    
    Args:
        brand_name: 品牌名
        competitors: 竞品列表
    
    Returns:
        完整分析结果
    """
    city, _ = parse_brand_city(brand_name)
    return full_geo_analysis(
        brand_name=brand_name,
        competitor_names=competitors or [],
        city=city
    )


if __name__ == "__main__":
    # 测试完整流程
    result = full_geo_analysis(
        brand_name="武汉万象城",
        competitor_names=["武汉恒隆广场", "武商MALL"],
        city="武汉",
        industry="商业地产"
    )
    
    # 打印报告
    print_full_report(result)
    
    # 保存完整报告
    with open("geo_full_report.md", "w", encoding="utf-8") as f:
        f.write(result["report"])
    print("\n✅ 完整报告已保存到 geo_full_report.md")
