"""
好易易GEO AI聚合接口
支持多AI自动切换：DeepSeek → Kimi → 智谱
"""

import requests
import json
from typing import Optional, Dict, List

# API配置
AIS = {
    "deepseek": {
        "name": "DeepSeek",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": "sk-8914498a0fff48e793153ab852a38ae5",
        "model": "deepseek-chat",
        "enabled": True
    },
    "kimi": {
        "name": "Kimi",
        "api_url": "https://api.moonshot.cn/v1/chat/completions",
        "api_key": "",  # 待配置
        "model": "moonshot-v1-8k",
        "enabled": False
    },
    "zhipu": {
        "name": "智谱AI",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key": "",  # 待配置
        "model": "glm-4",
        "enabled": False
    }
}

def call_ai(prompt: str, analysis_type: str = "brand_analysis") -> Dict:
    """
    调用AI进行GEO分析，支持自动切换
    
    Args:
        prompt: 分析提示词
        analysis_type: 分析类型（brand_analysis/competitor_analysis/content_strategy）
    
    Returns:
        {"success": bool, "data": {}, "ai_used": str, "error": str}
    """
    
    # 根据分析类型构造系统提示
    system_prompts = {
        "brand_analysis": """你是一个专业的GEO（生成式引擎优化）分析师。
请分析用户输入的品牌在AI搜索中的表现，输出JSON格式：
{
    "brand_mentions": "品牌被提及次数",
    "sentiment": "正面/中性/负面",
    "key_features": ["特点1", "特点2"],
    "recommendations": ["优化建议1", "优化建议2"]
}""",
        
        "competitor_analysis": """你是一个专业的竞品分析专家。
分析输入品牌与竞品的对比，输出JSON格式：
{
    "brand_position": "品牌定位",
    "competitors": ["竞品1", "竞品2"],
    "advantages": ["优势1", "优势2"],
    "weaknesses": ["劣势1", "劣势2"],
    "opportunities": ["机会1", "机会2"]
}""",
        
        "content_strategy": """你是一个内容营销专家。
根据品牌特点，输出内容策略，输出JSON格式：
{
    "target_keywords": ["关键词1", "关键词2"],
    "content_types": ["类型1", "类型2"],
    "platforms": ["平台1", "平台2"],
    "sample_titles": ["标题1", "标题2"]
}"""
    }
    
    system_prompt = system_prompts.get(analysis_type, system_prompts["brand_analysis"])
    
    # 按优先级尝试调用AI
    for ai_key, ai_config in AIS.items():
        if not ai_config.get("enabled", False):
            continue
            
        try:
            response = _call_single_ai(
                api_url=ai_config["api_url"],
                api_key=ai_config["api_key"],
                model=ai_config["model"],
                system_prompt=system_prompt,
                user_prompt=prompt
            )
            
            if response["success"]:
                return {
                    "success": True,
                    "data": response["data"],
                    "ai_used": ai_config["name"],
                    "error": None
                }
        except Exception as e:
            print(f"{ai_config['name']} 调用失败: {str(e)}，尝试下一个...")
            continue
    
    # 所有AI都失败
    return {
        "success": False,
        "data": None,
        "ai_used": None,
        "error": "所有AI服务暂时不可用，请稍后重试"
    }


def _call_single_ai(api_url: str, api_key: str, model: str, system_prompt: str, user_prompt: str) -> Dict:
    """调用单个AI服务"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    result = response.json()
    
    if "choices" in result and len(result["choices"]) > 0:
        content = result["choices"][0]["message"]["content"]
        # 尝试解析JSON
        try:
            # 提取JSON（处理可能的markdown格式）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            return {"success": True, "data": data}
        except:
            return {"success": True, "data": {"raw_response": content}}
    
    return {"success": False, "error": result.get("error", "Unknown error")}


def analyze_brand(brand_name: str, industry: str = "通用", push_to_feishu: bool = False) -> Dict:
    """
    分析品牌GEO健康度
    
    Args:
        brand_name: 品牌名称
        industry: 行业分类
        push_to_feishu: 是否推送结果到飞书
    """
    prompt = f"请分析【{brand_name}】（{industry}）在AI搜索中的表现"
    result = call_ai(prompt, "brand_analysis")
    result["brand_name"] = brand_name
    result["industry"] = industry
    
    # 分析完成后自动推送飞书（可选）
    if push_to_feishu:
        try:
            from .feishu_pusher import push_analysis_to_feishu
            push_analysis_to_feishu(result, brand_name, industry)
        except Exception as e:
            print(f"⚠️ 飞书推送失败: {str(e)}")
    
    return result


def analyze_competitor(main_brand: str, competitors: List[str], push_to_feishu: bool = False) -> Dict:
    """
    竞品对比分析
    
    Args:
        main_brand: 主品牌
        competitors: 竞品列表
        push_to_feishu: 是否推送结果到飞书
    """
    prompt = f"主品牌：【{main_brand}】\n竞品：{', '.join(competitors)}\n请分析竞品格局"
    result = call_ai(prompt, "competitor_analysis")
    result["brand_name"] = main_brand
    result["competitors_raw"] = competitors
    
    # 分析完成后自动推送飞书（可选）
    if push_to_feishu:
        try:
            from .feishu_pusher import push_analysis_to_feishu
            push_analysis_to_feishu(result, main_brand, "竞品分析")
        except Exception as e:
            print(f"⚠️ 飞书推送失败: {str(e)}")
    
    return result


def generate_content_strategy(brand_name: str, target_audience: str = "") -> Dict:
    """生成内容策略"""
    prompt = f"品牌：【{brand_name}】\n目标受众：{target_audience}\n请制定内容策略"
    return call_ai(prompt, "content_strategy")


# 快速测试
if __name__ == "__main__":
    print("🧪 好易易GEO AI聚合接口测试\n")
    
    # 测试品牌分析
    result = analyze_brand("武汉万象城", "商场")
    
    if result["success"]:
        print(f"✅ 分析成功，使用AI：{result['ai_used']}")
        print(f"📊 结果：{json.dumps(result['data'], ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ 分析失败：{result['error']}")
