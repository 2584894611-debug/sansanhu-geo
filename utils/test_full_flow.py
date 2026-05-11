# -*- coding: utf-8 -*-
"""
好易易GEO - 完整流程测试
测试 Prompt采集 → GEO报告 → 内容诊断 → 优化建议 全流程
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.full_geo_analysis import (
    full_geo_analysis,
    quick_geo_analysis,
    print_full_report
)


def test_full_geo_analysis():
    """测试完整GEO分析流程"""
    print("=" * 60)
    print("测试：好易易GEO 完整分析流程")
    print("=" * 60)
    
    # 测试武汉万象城
    result = full_geo_analysis(
        brand_name="武汉万象城",
        competitor_names=["武汉恒隆广场", "武商MALL"],
        city="武汉",
        industry="商业地产"
    )
    
    # 验证返回结构
    assert "brand" in result, "缺少brand字段"
    assert "city" in result, "缺少city字段"
    assert "industry" in result, "缺少industry字段"
    assert "prompt_analysis" in result, "缺少prompt_analysis字段"
    assert "geo_score" in result, "缺少geo_score字段"
    assert "diagnosis" in result, "缺少diagnosis字段"
    assert "optimization_suggestions" in result, "缺少optimization_suggestions字段"
    assert "report" in result, "缺少report字段"
    
    print(f"\n✅ 品牌: {result['brand']}")
    print(f"✅ 城市: {result['city']}")
    print(f"✅ 行业: {result['industry']}")
    
    # 验证Prompt分析
    pa = result["prompt_analysis"]
    assert "total" in pa, "缺少total字段"
    assert "categories" in pa, "缺少categories字段"
    assert pa["total"] > 0, "Prompt总数应大于0"
    
    print(f"\n✅ Prompt分析:")
    print(f"   - 采集数量: {pa['total']}条")
    print(f"   - 类型分布: {pa['categories']}")
    
    # 验证GEO评分
    geo = result["geo_score"]
    assert "total" in geo, "缺少total字段"
    assert "level" in geo, "缺少level字段"
    assert 0 <= geo["total"] <= 100, "GEO评分应在0-100之间"
    
    print(f"\n✅ GEO评分:")
    print(f"   - 综合评分: {geo['total']}分 ({geo['level']})")
    print(f"   - 可见度: {geo['visibility']}分")
    print(f"   - 推荐度: {geo['recommendation']}分")
    
    # 验证诊断结果
    diag = result["diagnosis"]
    assert "score" in diag, "缺少score字段"
    assert "passed" in diag, "缺少passed字段"
    assert "failed" in diag, "缺少failed字段"
    assert "priority_fixes" in diag, "缺少priority_fixes字段"
    
    print(f"\n✅ 内容诊断:")
    print(f"   - 诊断得分: {diag['score']}分 ({diag['overall']})")
    print(f"   - 通过项: {diag['passed']}")
    print(f"   - 未通过项: {diag['failed']}项")
    print(f"   - 优先修复: {diag['priority_fixes']}")
    
    # 验证优化建议
    suggestions = result["optimization_suggestions"]
    assert isinstance(suggestions, list), "优化建议应为列表"
    
    print(f"\n✅ 优化建议 ({len(suggestions)}项):")
    for s in suggestions[:3]:
        print(f"   - [{s['priority']}] {s['issue']}")
    
    # 验证报告
    report = result["report"]
    assert isinstance(report, str), "报告应为字符串"
    assert len(report) > 500, "报告内容过短"
    
    print(f"\n✅ 完整报告已生成 ({len(report)}字符)")
    
    return result


def test_quick_analysis():
    """测试快速分析函数"""
    print("\n" + "=" * 60)
    print("测试：快速GEO分析")
    print("=" * 60)
    
    # 自动解析城市
    result = quick_geo_analysis(
        brand_name="北京三里屯",
        competitors=["北京国贸", "北京朝阳大悦城"]
    )
    
    print(f"\n✅ 品牌: {result['brand']}")
    print(f"✅ 自动解析城市: {result['city']}")
    print(f"✅ GEO评分: {result['geo_score']['total']}分")
    
    return result


def test_different_brands():
    """测试不同品牌"""
    print("\n" + "=" * 60)
    print("测试：多品牌分析")
    print("=" * 60)
    
    test_brands = [
        {"brand": "上海IFC", "competitors": ["上海IFC"], "city": "上海"},
        {"brand": "成都太古里", "competitors": ["成都IFS", "成都万象城"], "city": "成都"},
        {"brand": "深圳万象城", "competitors": ["深圳海岸城", "深圳金光华"], "city": "深圳"},
    ]
    
    results = []
    for test in test_brands:
        result = full_geo_analysis(
            brand_name=test["brand"],
            competitor_names=test["competitors"],
            city=test["city"],
            industry="商业地产"
        )
        results.append(result)
        print(f"\n✅ {result['brand']}: GEO {result['geo_score']['total']}分")
    
    return results


def test_with_custom_content():
    """测试自定义内容诊断"""
    print("\n" + "=" * 60)
    print("测试：自定义内容诊断")
    print("=" * 60)
    
    custom_content = """
    # 武汉万象城怎么样？
    
    武汉万象城是武汉知名的高端购物中心。
    
    ## 对比表格
    
    | 商场 | 定位 | 品牌档次 | 推荐指数 |
    |------|------|----------|----------|
    | 武汉万象城 | 高端 | ★★★★★ | 4.5 |
    | 武汉恒隆广场 | 高端 | ★★★★★ | 4.3 |
    
    ## FAQ
    
    Q: 武汉万象城适合约会吗？
    A: 非常适合，餐厅和影院设施完善。
    
    Q: 武汉万象城和恒隆广场哪个好？
    A: 各有特色，万象城业态更丰富。
    """
    
    result = full_geo_analysis(
        brand_name="武汉万象城",
        competitor_names=["武汉恒隆广场"],
        city="武汉",
        content=custom_content  # 传入自定义内容
    )
    
    print(f"\n✅ 诊断得分: {result['diagnosis']['score']}分")
    total_checks = result['diagnosis']['passed'] + result['diagnosis']['failed']
    print(f"✅ 通过项: {result['diagnosis']['passed']}/{total_checks}")
    print(f"✅ 未通过项: {result['diagnosis']['failed']}项")
    
    return result


def print_report_preview(result: dict):
    """打印报告预览"""
    print("\n" + "=" * 60)
    print("报告预览（控制台格式化）")
    print("=" * 60)
    
    print_full_report(result)


def save_report_to_file(result: dict, filename: str = "test_geo_report.md"):
    """保存报告到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["report"])
    print(f"\n✅ 报告已保存到: {filename}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 好易易GEO 完整流程测试套件")
    print("=" * 60)
    
    # 1. 测试完整分析流程
    result = test_full_geo_analysis()
    
    # 2. 测试快速分析
    test_quick_analysis()
    
    # 3. 测试不同品牌
    test_different_brands()
    
    # 4. 测试自定义内容
    test_with_custom_content()
    
    # 5. 打印报告预览
    print_report_preview(result)
    
    # 6. 保存报告
    save_report_to_file(result, "test_wuhan_mixc_report.md")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()
