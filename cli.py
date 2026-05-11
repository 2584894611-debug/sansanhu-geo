#!/usr/bin/env python3
"""
好易易GEO CLI 命令行工具

用法:
    python cli.py analyze "武汉万象城" --industry 本地生活 --push-feishu
    python cli.py competitor "武汉万象城" "武商MALL" "恒隆广场"
    python cli.py report "武汉万象城" --format docx
"""

import sys
import json
import argparse
from typing import List

# 添加 utils 路径
sys.path.insert(0, '.')

from utils.ai_aggregator import (
    analyze_brand,
    analyze_competitor,
    generate_content_strategy
)
from utils.platform_config import get_platform_weights, print_weights_table
from utils.feishu_pusher import test_connection, push_analysis_to_feishu


def cmd_analyze(args):
    """品牌分析命令"""
    print(f"\n🔍 正在分析品牌: {args.brand}")
    print(f"📂 行业分类: {args.industry}")
    print("-" * 50)
    
    # 执行分析
    result = analyze_brand(
        brand_name=args.brand,
        industry=args.industry,
        push_to_feishu=args.push_feishu
    )
    
    if result["success"]:
        print(f"\n✅ 分析完成 (使用AI: {result['ai_used']})")
        print("\n📊 分析结果:")
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
        
        if args.push_feishu:
            print("\n📤 已推送至飞书")
    else:
        print(f"\n❌ 分析失败: {result['error']}")
        sys.exit(1)


def cmd_competitor(args):
    """竞品分析命令"""
    main_brand = args.main
    competitors = args.competitors
    
    print(f"\n🏢 竞品分析")
    print(f"📍 主品牌: {main_brand}")
    print(f"⚔️ 竞品: {', '.join(competitors)}")
    print("-" * 50)
    
    # 执行分析
    result = analyze_competitor(
        main_brand=main_brand,
        competitors=competitors,
        push_to_feishu=args.push_feishu
    )
    
    if result["success"]:
        print(f"\n✅ 分析完成 (使用AI: {result['ai_used']})")
        print("\n📊 分析结果:")
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
        
        if args.push_feishu:
            print("\n📤 已推送至飞书")
    else:
        print(f"\n❌ 分析失败: {result['error']}")
        sys.exit(1)


def cmd_report(args):
    """生成报告命令"""
    print(f"\n📝 正在生成报告: {args.brand}")
    print(f"📄 格式: {args.format}")
    print("-" * 50)
    
    # 先分析品牌
    result = analyze_brand(args.brand, args.industry)
    
    if result["success"]:
        print(f"\n✅ 报告生成完成 (使用AI: {result['ai_used']})")
        print("\n📊 报告内容:")
        
        report_content = _build_report(args.brand, result["data"])
        print(report_content)
        
        # 保存报告
        if args.format == "docx":
            # 保存为 markdown，后续可用 pandoc 转换
            output_file = f"report_{args.brand}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"\n💾 报告已保存: {output_file}")
        
        if args.push_feishu:
            push_analysis_to_feishu(result["data"], args.brand, args.industry)
            print("📤 已推送至飞书")
    else:
        print(f"\n❌ 报告生成失败: {result['error']}")
        sys.exit(1)


def cmd_weights(args):
    """平台权重命令"""
    print("\n📊 好易易GEO 平台权重配置\n")
    print_weights_table()
    
    if args.industry:
        print(f"\n📌 {args.industry} 行业平台权重:")
        weights = get_platform_weights(args.industry)
        for platform, info in sorted(weights.items(), key=lambda x: -x[1]['weight']):
            print(f"   {platform}: {info['weight']*100:.1f}%")


def cmd_test(args):
    """测试飞书连接"""
    print("\n🔧 飞书连接测试\n")
    test_connection()


def _build_report(brand: str, data: dict) -> str:
    """构建报告内容"""
    lines = [
        f"# {brand} GEO分析报告",
        "",
        "## 📊 品牌概述",
    ]
    
    if "brand_mentions" in data:
        lines.append(f"- **AI提及量**: {data['brand_mentions']}")
    
    if "sentiment" in data:
        lines.append(f"- **情感倾向**: {data['sentiment']}")
    
    if "key_features" in data:
        lines.append("\n## ✨ 关键特征")
        for feature in data["key_features"]:
            lines.append(f"- {feature}")
    
    if "recommendations" in data:
        lines.append("\n## 💡 优化建议")
        for rec in data["recommendations"]:
            lines.append(f"- {rec}")
    
    lines.append("\n---\n*由 好易易GEO 自动生成*")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="好易易GEO - AI搜索引擎优化分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析品牌GEO表现")
    analyze_parser.add_argument("brand", help="品牌名称")
    analyze_parser.add_argument("--industry", "-i", default="通用", help="行业分类")
    analyze_parser.add_argument("--push-feishu", "-p", action="store_true", help="推送结果到飞书")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # competitor 命令
    competitor_parser = subparsers.add_parser("competitor", help="竞品对比分析")
    competitor_parser.add_argument("main", help="主品牌")
    competitor_parser.add_argument("competitors", nargs="+", help="竞品列表")
    competitor_parser.add_argument("--push-feishu", "-p", action="store_true", help="推送结果到飞书")
    competitor_parser.set_defaults(func=cmd_competitor)
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成分析报告")
    report_parser.add_argument("brand", help="品牌名称")
    report_parser.add_argument("--industry", "-i", default="通用", help="行业分类")
    report_parser.add_argument("--format", "-f", default="md", choices=["md", "docx"], help="报告格式")
    report_parser.add_argument("--push-feishu", "-p", action="store_true", help="推送结果到飞书")
    report_parser.set_defaults(func=cmd_report)
    
    # weights 命令
    weights_parser = subparsers.add_parser("weights", help="查看平台权重配置")
    weights_parser.add_argument("--industry", "-i", help="查看特定行业权重")
    weights_parser.set_defaults(func=cmd_weights)
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="测试飞书连接")
    test_parser.set_defaults(func=cmd_test)
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
