# -*- coding: utf-8 -*-
"""
好易易GEO - 使用示例
展示如何生成GEO分析报告和可视化图表
"""

from datetime import datetime
from utils.report_generator import generate_geo_report
from utils.chart_generator import (
    generate_horizontal_bar_chart,
    generate_donut_chart,
    generate_comparison_chart,
    generate_table,
    generate_platform_mentions_chart,
    generate_sentiment_pie_chart,
    generate_progress_bar,
    generate_emoji_rating
)


def example_basic_report():
    """基础报告生成示例"""
    print("=" * 60)
    print("示例1: 基础GEO报告生成")
    print("=" * 60)
    
    # 品牌数据
    brand_data = {
        'brand_name': '武商梦时代',
        'industry': '商业地产',
        'geo_score': 85,
        'visibility': 90,
        'recommendation': 82,
        'sentiment': {
            'positive': 72,
            'neutral': 18,
            'negative': 10
        },
        'mentions': 156,
        'trend': 'rising',
        'strengths': [
            '亚洲最大纯商业体',
            '室内滑雪场特色鲜明',
            'WS梦乐园吸引亲子客群'
        ],
        'challenges': [
            '负面舆情管理需加强',
            '与新兴商场竞争加剧'
        ],
        'advantages': [
            {'title': '体量优势', 'description': '80万方商业体，品类最全'},
            {'title': '特色标签', 'description': '"亚洲最大"标签辨识度极高'},
            {'title': '客流稳定', 'description': '高德显示稳定高位客流'}
        ],
        'weaknesses': [
            {'title': '内容覆盖', 'description': '知乎内容相对不足'}
        ],
        'competitors': [
            {'name': '武汉SKP', 'geo_score': 92, 'visibility': 88, 'recommendation': 90},
            {'name': '武商MALL', 'geo_score': 78, 'visibility': 75, 'recommendation': 76},
            {'name': '武汉万象城', 'geo_score': 75, 'visibility': 72, 'recommendation': 74},
            {'name': '永旺梦乐城', 'geo_score': 68, 'visibility': 65, 'recommendation': 70}
        ],
        'recommendations': [
            {
                'title': '强化知乎内容布局',
                'description': '增加知乎高质量回答和文章',
                'priority': 'high',
                'effect': '提升知识平台可见度',
                'difficulty': 'medium',
                'actions': [
                    '发布商场攻略类文章',
                    '回答与商场相关的问题',
                    '与知乎达人合作内容'
                ]
            },
            {
                'title': '优化情感监测',
                'description': '加强负面舆情的监测和应对',
                'priority': 'urgent',
                'effect': '改善品牌情感倾向',
                'difficulty': 'easy',
                'actions': [
                    '建立舆情监测机制',
                    '制定负面舆情应对预案',
                    '增加正面内容产出'
                ]
            }
        ],
        'risks': [
            {'level': 'medium', 'title': '新开业商场竞争', 'description': '武汉SKP等新商场分流客流'}
        ],
        'keywords': [
            {'keyword': '武汉商场', 'type': 'industry'},
            {'keyword': '武商梦时代', 'type': 'brand'},
            {'keyword': '室内滑雪', 'type': 'scene'},
            {'keyword': '亚洲最大', 'type': 'product'}
        ]
    }
    
    # 平台数据
    platform_data = {
        '小红书': 85,
        '知乎': 65,
        '微信公众号': 72,
        '抖音': 58,
        'B站': 42
    }
    
    # 生成报告
    report = generate_geo_report(brand_data, platform_data)
    
    # 保存报告
    with open('geo_report_example.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ 报告已生成: geo_report_example.md")
    print("\n报告预览（前100行）：")
    print('\n'.join(report.split('\n')[:100]))
    
    return report


def example_chart_generation():
    """图表生成示例"""
    print("\n" + "=" * 60)
    print("示例2: 数据可视化图表")
    print("=" * 60)
    
    # 平台提及数据
    platform_data = {
        '武商梦时代': 95,
        '武汉SKP': 90,
        '武商MALL': 78,
        '武汉万象城': 72,
        '永旺梦乐城': 65,
        '武昌万象城': 55
    }
    
    print("\n📊 商场GEO评分对比图：")
    print(generate_horizontal_bar_chart(platform_data, "商场GEO评分对比"))
    
    # 情感分析数据
    sentiment_data = {
        '正面评价': 65,
        '中性评价': 25,
        '负面评价': 10
    }
    
    print("\n" + generate_sentiment_pie_chart(sentiment_data))
    
    # 竞品对比数据
    brand_data = {
        '可见度': 85,
        '推荐度': 78,
        '情感倾向': 72,
        '内容质量': 80
    }
    
    competitor_data = {
        '武汉SKP': {
            '可见度': 88,
            '推荐度': 90,
            '情感倾向': 75,
            '内容质量': 82
        }
    }
    
    print("\n" + generate_comparison_chart(brand_data, competitor_data, "品牌对比分析"))
    
    # 进度条和评分
    print("\n📈 GEO评分进度：")
    print(generate_progress_bar(85, 100, prefix="GEO评分: "))
    
    print("\n⭐ 评分表情：")
    print(f"GEO评分: {generate_emoji_rating(85)} (85/100)")
    
    # 表格示例
    print("\n📋 数据表格：")
    print(generate_table(
        ['商场名称', 'GEO评分', '排名', '健康度'],
        [
            ['武商梦时代', '85', '1', '优秀'],
            ['武汉SKP', '92', '2', '非常优秀'],
            ['武商MALL', '78', '3', '良好'],
            ['武汉万象城', '75', '4', '良好']
        ],
        title="武汉主要商场GEO评分"
    ))


def example_word_export():
    """Word导出示例（需要python-docx库）"""
    print("\n" + "=" * 60)
    print("示例3: Word文档导出")
    print("=" * 60)
    
    try:
        from utils.docx_exporter import markdown_to_docx
        
        # 读取之前生成的Markdown报告
        with open('geo_report_example.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 转换为Word文档
        output_file = 'geo_report_example.docx'
        success = markdown_to_docx(
            markdown_content,
            output_file,
            title='武商梦时代GEO分析报告',
            author='好易易GEO'
        )
        
        if success:
            print(f"✅ Word文档已生成: {output_file}")
        else:
            print("❌ Word文档生成失败")
            
    except ImportError:
        print("⚠️ python-docx库未安装，无法生成Word文档")
        print("请运行: pip install python-docx")
    except FileNotFoundError:
        print("⚠️ 找不到Markdown报告文件，请先运行示例1")


def example_full_workflow():
    """完整工作流程示例"""
    print("\n" + "=" * 60)
    print("示例4: 完整GEO分析工作流程")
    print("=" * 60)
    
    # 步骤1: 准备数据
    print("\n📋 步骤1: 准备分析数据")
    
    brand_data = {
        'brand_name': '测试品牌',
        'industry': '零售',
        'geo_score': 78,
        'visibility': 75,
        'recommendation': 72,
        'sentiment': {'positive': 65, 'neutral': 25, 'negative': 10},
        'mentions': 50,
        'competitors': [
            {'name': '竞品A', 'geo_score': 85, 'visibility': 80, 'recommendation': 82},
            {'name': '竞品B', 'geo_score': 70, 'visibility': 68, 'recommendation': 65}
        ],
        'recommendations': [
            {'title': '优化小红书内容', 'priority': 'high', 'effect': '提升可见度', 'difficulty': 'medium', 'actions': ['发布笔记', '与KOL合作']}
        ]
    }
    
    platform_data = {
        '小红书': 45,
        '知乎': 30,
        '微信公众号': 25,
        '抖音': 20
    }
    
    print(f"  - 品牌: {brand_data['brand_name']}")
    print(f"  - GEO评分: {brand_data['geo_score']}")
    print(f"  - 分析平台数: {len(platform_data)}")
    
    # 步骤2: 生成报告
    print("\n📝 步骤2: 生成GEO分析报告")
    report = generate_geo_report(brand_data, platform_data)
    print(f"  - 报告长度: {len(report)} 字符")
    
    # 步骤3: 生成可视化
    print("\n📊 步骤3: 生成数据可视化")
    print(generate_platform_mentions_chart(platform_data))
    
    # 步骤4: 导出文档
    print("\n📄 步骤4: 导出Word文档")
    print("  - (需要python-docx库支持)")
    
    print("\n✅ 完整流程执行完成！")


if __name__ == '__main__':
    # 运行所有示例
    example_basic_report()
    example_chart_generation()
    example_word_export()
    example_full_workflow()
