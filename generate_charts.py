#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成GEO可视化图表"""

import sys
sys.path.insert(0, '.')

import json
from datetime import datetime

# 读取测试数据
with open("reports/00_测试汇总.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

with open("reports/01_data_collection.json", "r", encoding="utf-8") as f:
    collection_data = json.load(f)

with open("reports/02_ai_analysis.json", "r", encoding="utf-8") as f:
    ai_data = json.load(f)

print("=" * 50)
print("📊 步骤4: 可视化图表生成")
print("=" * 50)

# 生成图表数据
chart_data = {
    "title": f"{test_data['brand']} GEO分析数据可视化",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "charts": [
        {
            "type": "platform_radar",
            "title": "AI平台覆盖雷达图",
            "platforms": list(collection_data['platform_mentions'].keys()),
            "values": list(collection_data['platform_mentions'].values())
        },
        {
            "type": "score_gauge",
            "title": "GEO健康度评分",
            "value": test_data['brand_data']['geo_score']
        },
        {
            "type": "sentiment_pie",
            "title": "情感倾向分布",
            "positive": test_data['brand_data']['sentiment']['positive'],
            "neutral": test_data['brand_data']['sentiment']['neutral'],
            "negative": test_data['brand_data']['sentiment']['negative']
        }
    ]
}

# 保存图表数据
with open("reports/03_chart_data.json", "w", encoding="utf-8") as f:
    json.dump(chart_data, f, ensure_ascii=False, indent=2)

print("✅ 图表数据已生成: reports/03_chart_data.json")

# 准备数据
brand = test_data['brand']
industry = test_data['industry']
geo_score = test_data['brand_data']['geo_score']
visibility = test_data['brand_data']['visibility']
recommendation = test_data['brand_data']['recommendation']
total_results = test_data['steps']['data_collection']['results']
platform_names = json.dumps(list(collection_data['platform_mentions'].keys()))
platform_values = json.dumps(list(collection_data['platform_mentions'].values()))
positive = test_data['brand_data']['sentiment']['positive']
neutral = test_data['brand_data']['sentiment']['neutral']
negative = test_data['brand_data']['sentiment']['negative']
competitors_json = json.dumps(ai_data['data'].get('competitors', []), ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand} GEO分析可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .card h3 {{ margin: 0 0 15px 0; color: #333; font-size: 16px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .chart {{ width: 100%; height: 300px; }}
        .metrics {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .metric {{ background: linear-gradient(135deg, #667eea22, #764ba222); padding: 15px 25px; border-radius: 10px; text-align: center; flex: 1; min-width: 120px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {brand} GEO分析报告</h1>
        <p>行业: {industry} | 分析时间: {chart_data['timestamp']}</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">{geo_score}</div>
            <div class="metric-label">GEO评分</div>
        </div>
        <div class="metric">
            <div class="metric-value">{visibility}</div>
            <div class="metric-label">可见度</div>
        </div>
        <div class="metric">
            <div class="metric-value">{recommendation}</div>
            <div class="metric-label">推荐度</div>
        </div>
        <div class="metric">
            <div class="metric-value">{total_results}</div>
            <div class="metric-label">采集数据</div>
        </div>
    </div>
    
    <div class="grid" style="margin-top: 20px;">
        <div class="card">
            <h3>📡 AI平台覆盖分布</h3>
            <div id="platformChart" class="chart"></div>
        </div>
        <div class="card">
            <h3>😊 情感倾向分析</h3>
            <div id="sentimentChart" class="chart"></div>
        </div>
        <div class="card">
            <h3>📈 三维度评分</h3>
            <div id="dimensionChart" class="chart"></div>
        </div>
        <div class="card">
            <h3>🏢 竞品对比</h3>
            <div id="competitorChart" class="chart"></div>
        </div>
    </div>
    
    <script>
        var platformNames = {platform_names};
        var platformValues = {platform_values};
        var competitorsData = {competitors_json};
        
        // 平台覆盖图
        var platformChart = echarts.init(document.getElementById('platformChart'));
        platformChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            xAxis: { type: 'category', data: platformNames, axisLabel: { rotate: 30 } },
            yAxis: { type: 'value', name: '提及次数' },
            series: [{
                type: 'bar',
                data: platformValues,
                itemStyle: { borderRadius: [5, 5, 0, 0], color: '#667eea' }
            }]
        });
        
        // 情感分布图
        var sentimentChart = echarts.init(document.getElementById('sentimentChart'));
        sentimentChart.setOption({
            tooltip: { trigger: 'item' },
            legend: { bottom: 0 },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {c}%' },
                data: [
                    { value: {positive}, name: '正面', itemStyle: {color: '#91cc75'} },
                    { value: {neutral}, name: '中性', itemStyle: {color: '#fac858'} },
                    { value: {negative}, name: '负面', itemStyle: {color: '#ee6666'} }
                ]
            }]
        });
        
        // 三维度评分
        var dimensionChart = echarts.init(document.getElementById('dimensionChart'));
        dimensionChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            xAxis: { type: 'category', data: ['GEO评分', '可见度', '推荐度'] },
            yAxis: { type: 'value', max: 100 },
            series: [{
                type: 'bar',
                data: [
                    { value: {geo_score}, itemStyle: { color: '#667eea' } },
                    { value: {visibility}, itemStyle: { color: '#f5576c' } },
                    { value: {recommendation}, itemStyle: { color: '#4facfe' } }
                ],
                barWidth: '50%',
                itemStyle: { borderRadius: [5, 5, 0, 0] }
            }]
        });
        
        // 竞品对比
        var competitorList = [{{ name: '{brand}', score: {geo_score} }}];
        competitorsData.forEach(function(c) {{ competitorList.push({{ name: c.name, score: c.geo_score }}); }});
        competitorList.sort(function(a, b) {{ return b.score - a.score; }});
        
        var competitorChart = echarts.init(document.getElementById('competitorChart'));
        competitorChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            xAxis: { type: 'value', max: 100 },
            yAxis: { type: 'category', data: competitorList.map(function(d) {{ return d.name; }}) },
            series: [{
                type: 'bar',
                data: competitorList.map(function(d, i) {{ 
                    return {{ 
                        value: d.score,
                        itemStyle: {{ 
                            color: d.name === '{brand}' ? '#667eea' : '#91cc75'
                        }}
                    }};
                }})
            }]
        });
        
        window.addEventListener('resize', function() {{ 
            platformChart.resize(); 
            sentimentChart.resize();
            dimensionChart.resize();
            competitorChart.resize();
        }});
    </script>
</body>
</html>'''

with open("reports/04_visualization.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ 可视化页面已生成: reports/04_visualization.html")
