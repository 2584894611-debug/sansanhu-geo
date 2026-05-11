#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好易易GEO - 完整链路测试脚本
目标：武汉万象城
"""

import sys
import time
import json
from datetime import datetime

sys.path.insert(0, '.')

from utils.data_collector import collect_from_platform, PLATFORMS
from utils.ai_aggregator import call_ai

BRAND_NAME = "武汉万象城"
INDUSTRY = "商业地产/本地生活"

print("=" * 60)
print("🚀 好易易GEO 完整链路测试")
print(f"📍 目标品牌: {BRAND_NAME}")
print(f"🏷️  行业类型: {INDUSTRY}")
print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ========== 步骤1: 数据采集 ==========
print("\n📊 步骤1: 数据采集")
collect_start = time.time()

keywords = [BRAND_NAME, f"{BRAND_NAME}美食", f"{BRAND_NAME}购物", "武汉购物中心推荐"]
platform_mentions = {p: 0 for p in PLATFORMS.keys()}
total_results = 0

for platform_name in PLATFORMS.keys():
    print(f"\n🔍 正在采集: {platform_name}...")
    for keyword in keywords:
        result = collect_from_platform(platform_name, keyword, use_mock=True)
        platform_mentions[platform_name] += result.get("count", 0)
        total_results += result.get("count", 0)
    print(f"   ✅ {platform_name} - 获取 {platform_mentions[platform_name]} 条")

collect_time = time.time() - collect_start
print(f"\n📈 数据采集完成! 共获取 {total_results} 条结果，耗时 {collect_time:.2f}秒")

with open("reports/01_data_collection.json", "w", encoding="utf-8") as f:
    json.dump({"brand": BRAND_NAME, "industry": INDUSTRY, "platform_mentions": platform_mentions, "total_results": total_results, "duration": collect_time}, f, ensure_ascii=False, indent=2)

# ========== 步骤2: AI分析 ==========
print("\n🤖 步骤2: AI分析")
ai_start = time.time()

prompt = f"""请对【{BRAND_NAME}】进行GEO分析，输出JSON格式：
{{
    "brand_mentions": "高频/中频/低频",
    "geo_score": 75,
    "visibility": 70,
    "recommendation": 72,
    "sentiment": {{"positive": 65, "neutral": 25, "negative": 10}},
    "key_features": ["特点1", "特点2", "特点3"],
    "competitors": [{{"name": "竞品1", "geo_score": 78}}, {{"name": "竞品2", "geo_score": 72}}],
    "recommendations": [{{"title": "建议1", "priority": "high", "difficulty": "medium"}}, {{"title": "建议2", "priority": "medium", "difficulty": "easy"}}],
    "advantages": [{{"title": "优势1", "description": "描述"}}],
    "weaknesses": [{{"title": "劣势1", "description": "描述"}}],
    "platform_performance": {{"豆包": "描述", "DeepSeek": "描述"}}
}}"""

print("\n🔄 正在调用DeepSeek AI进行GEO分析...")
ai_result = call_ai(prompt, "brand_analysis")
ai_time = time.time() - ai_start

if ai_result["success"]:
    print(f"✅ AI分析完成，使用模型: {ai_result.get('ai_used')}")
    ai_data = ai_result.get("data", {})
else:
    print(f"⚠️ AI分析失败，使用模拟数据")
    ai_data = {
        "brand_mentions": "中频",
        "geo_score": 72,
        "visibility": 68,
        "recommendation": 75,
        "sentiment": {"positive": 65, "neutral": 25, "negative": 10},
        "key_features": ["高端定位", "品牌齐全", "地理位置优越"],
        "competitors": [{"name": "武汉恒隆广场", "geo_score": 78}, {"name": "武商梦时代", "geo_score": 74}],
        "recommendations": [{"title": "加强社交媒体投放", "priority": "high", "difficulty": "medium"}, {"title": "优化关键词布局", "priority": "medium", "difficulty": "easy"}],
        "advantages": [{"title": "品牌影响力", "description": "万象城品牌全国知名"}],
        "weaknesses": [{"title": "线上曝光", "description": "AI搜索中曝光度有提升空间"}],
        "platform_performance": {"豆包": "中等可见", "DeepSeek": "稳定可见"}
    }

with open("reports/02_ai_analysis.json", "w", encoding="utf-8") as f:
    json.dump({"brand": BRAND_NAME, "ai_used": ai_result.get("ai_used", "模拟"), "success": ai_result["success"], "data": ai_data, "duration": ai_time}, f, ensure_ascii=False, indent=2)

# ========== 步骤3: 报告生成 ==========
print("\n📝 步骤3: 报告生成")
report_start = time.time()

from utils.report_generator import generate_geo_report

brand_data = {
    "brand_name": BRAND_NAME,
    "industry": INDUSTRY,
    "geo_score": ai_data.get("geo_score", 70),
    "visibility": ai_data.get("visibility", 65),
    "recommendation": ai_data.get("recommendation", 72),
    "sentiment": ai_data.get("sentiment", {"positive": 60, "neutral": 30, "negative": 10}),
    "mentions": ai_data.get("brand_mentions", "中等"),
    "competitors": ai_data.get("competitors", []),
    "recommendations": ai_data.get("recommendations", []),
    "key_features": ai_data.get("key_features", []),
    "advantages": ai_data.get("advantages", []),
    "weaknesses": ai_data.get("weaknesses", []),
    "platform_performance": ai_data.get("platform_performance", {})
}

report = generate_geo_report(brand_data, platform_mentions)
report_path = f"reports/GEO分析报告_{BRAND_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)

report_time = time.time() - report_start
print(f"✅ 报告已生成: {report_path}")

# ========== 汇总 ==========
total_time = collect_time + ai_time + report_time
print("\n" + "=" * 60)
print("📊 测试结果汇总")
print("=" * 60)

print(f"""
┌──────────────────────────────────────────────────┐
│         好易易GEO 完整链路测试报告                   │
├──────────────────────────────────────────────────┤
│ 目标品牌: {BRAND_NAME:<32}│
│ 行业类型: {INDUSTRY:<32}│
├──────────────────────────────────────────────────┤
│ 步骤           │ 状态    │ 耗时                  │
│ 1.数据采集     │ ✅成功  │ {collect_time:>8.2f}秒           │
│ 2.AI分析       │ {'✅成功' if ai_result['success'] else '⚠️模拟'}  │ {ai_time:>8.2f}秒           │
│ 3.报告生成     │ ✅成功  │ {report_time:>8.2f}秒           │
├──────────────────────────────────────────────────┤
│ 总耗时: {total_time:>48.2f}秒         │
│ 采集结果: {total_results:>47}条         │
└──────────────────────────────────────────────────┘

📈 GEO评分: {brand_data['geo_score']}分
👁️ 可见度: {brand_data['visibility']}分  
⭐ 推荐度: {brand_data['recommendation']}分
💬 情感: 正面{brand_data['sentiment']['positive']}% / 中性{brand_data['sentiment']['neutral']}% / 负面{brand_data['sentiment']['negative']}%

🏆 品牌特点:
""")
for i, f in enumerate(brand_data['key_features'], 1):
    print(f"   {i}. {f}")

print("\n🎯 优化建议:")
for i, r in enumerate(brand_data['recommendations'], 1):
    print(f"   {i}. {r.get('title', r) if isinstance(r, dict) else r}")

# 保存汇总
with open("reports/00_测试汇总.json", "w", encoding="utf-8") as f:
    json.dump({
        "test_time": datetime.now().isoformat(),
        "brand": BRAND_NAME,
        "industry": INDUSTRY,
        "steps": {
            "data_collection": {"status": "success", "duration": collect_time, "results": total_results},
            "ai_analysis": {"status": "success" if ai_result["success"] else "mock", "duration": ai_time},
            "report_generation": {"status": "success", "duration": report_time}
        },
        "total_duration": total_time,
        "brand_data": brand_data
    }, f, ensure_ascii=False, indent=2)

print(f"\n🎉 好易易GEO完整链路测试完成！")
print(f"📄 报告文件: {report_path}")
