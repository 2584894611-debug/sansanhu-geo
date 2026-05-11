# -*- coding: utf-8 -*-
"""
生成测试报告 - 武汉万象城GEO报告v2
包含Prompt分析章节
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from utils.report_generator import generate_geo_report

# 武汉万象城测试数据
brand_data = {
    'brand_name': '武汉万象城',
    'industry': '商业地产/本地生活',
    'geo_score': 75,
    'visibility': 70,
    'recommendation': 72,
    'sentiment': {
        'positive': 65,
        'negative': 10,
        'neutral': 25
    },
    'mentions': 50,
    'competitors': [
        {'name': '武汉恒隆广场', 'geo_score': 82, 'visibility': 78, 'recommendation': 80},
        {'name': '武商MALL', 'geo_score': 78, 'visibility': 75, 'recommendation': 74},
        {'name': '武汉K11', 'geo_score': 70, 'visibility': 68, 'recommendation': 65}
    ],
    'strengths': [
        '高端品牌阵容齐全',
        '地理位置优越',
        '业态组合丰富'
    ],
    'challenges': [
        '与竞品差异化不明显',
        '社交媒体声量不足'
    ],
    'recommendations': [
        {
            'title': '强化场景化内容',
            'description': '针对约会、遛娃等场景创作专属内容',
            'priority': 'high',
            'actions': ['制作场景化短视频', '发布小红书攻略']
        },
        {
            'title': '优化对比内容',
            'description': '制作与竞品的差异化对比内容',
            'priority': 'medium',
            'actions': ['策划PK内容', '发布对比评测']
        }
    ]
}

platform_data = {
    '豆包': 13,
    'DeepSeek': 11,
    '元宝': 10,
    'Kimi': 10,
    '通义千问': 11,
    '智谱': 14,
    '小红书': 8,
    '知乎': 5,
    '微信公众号': 4,
    '抖音': 3,
    'B站': 2
}

# 生成报告
print("正在生成武汉万象城GEO报告v2...")
report = generate_geo_report(brand_data, platform_data)

# 保存报告
output_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'reports',
    '武汉万象城_GEO报告_v2.md'
)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ 报告已生成：{output_path}")
print(f"📊 报告长度：{len(report)} 字符")
