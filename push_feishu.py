#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推送到飞书表格"""

import sys
sys.path.insert(0, '.')

import json
from datetime import datetime

# 读取测试数据
with open("reports/00_测试汇总.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

print("=" * 50)
print("📱 步骤5: 飞书表格推送")
print("=" * 50)

# 构造符合push_analysis_to_feishu格式的数据
analysis_result = {
    "success": True,
    "brand_name": test_data['brand'],
    "industry": test_data['industry'],
    "data": {
        "geo_score": test_data['brand_data']['geo_score'],
        "visibility": test_data['brand_data']['visibility'],
        "recommendation": test_data['brand_data']['recommendation'],
        "sentiment": test_data['brand_data']['sentiment'],
        "key_features": test_data['brand_data']['key_features'],
        "recommendations": test_data['brand_data']['recommendations'],
        "competitors": test_data['brand_data'].get('competitors', []),
        "platform_performance": test_data['brand_data'].get('platform_performance', {}),
        "ai_used": test_data['steps']['ai_analysis'].get('ai_used', 'N/A'),
        "total_results": test_data['steps']['data_collection']['results'],
        "test_duration": test_data['total_duration']
    }
}

try:
    from utils.feishu_pusher import push_analysis_to_feishu
    
    result = push_analysis_to_feishu(analysis_result, test_data['brand'], test_data['industry'])
    
    if result:
        print("✅ 飞书推送成功!")
    else:
        print("⚠️ 飞书推送返回False")

except Exception as e:
    print(f"❌ 飞书推送失败: {str(e)}")
