"""
好易易GEO 飞书推送模块
将分析结果写入飞书多维表格
"""

import subprocess
import json
from typing import Dict, Optional

# 飞书表格配置
FEISHU_CONFIG = {
    "base_token": "Nul0bWprZaDtzpskf8lc4qPNnPh",
    "table_id": "tblTfNkLRWcEH1LF"
}

# 字段映射
FIELD_MAPPING = {
    "选题": "brand_name",      # 品牌名称 -> 选题
    "分类": "industry",        # 行业分类 -> 分类
    "爆点分析": "analysis",    # 分析结论 -> 爆点分析
    "备注": "platform_data"   # 平台数据 -> 备注
}


def push_analysis_to_feishu(analysis_result: Dict, brand_name: str = "", industry: str = "") -> bool:
    """
    将分析结果写入飞书表格
    
    Args:
        analysis_result: 分析结果字典
        brand_name: 品牌名称
        industry: 行业分类
    
    Returns:
        bool: 推送是否成功
    """
    try:
        # 构建记录数据
        record_data = _build_record_data(analysis_result, brand_name, industry)
        
        # 调用飞书 CLI 写入记录
        result = _upsert_record(record_data)
        
        return result
        
    except Exception as e:
        print(f"❌ 飞书推送失败: {str(e)}")
        return False


def _build_record_data(analysis_result: Dict, brand_name: str, industry: str) -> Dict:
    """构建飞书记录数据"""
    
    # 处理分析结论（爆点分析）
    analysis_text = _format_analysis(analysis_result)
    
    # 处理平台数据（备注）
    platform_data = _format_platform_data(analysis_result)
    
    # 构建字段映射
    record = {
        "选题": brand_name or analysis_result.get("brand_name", "未知品牌"),
        "分类": industry or analysis_result.get("industry", "通用"),
        "爆点分析": analysis_text,
        "备注": platform_data
    }
    
    return record


def _format_analysis(result: Dict) -> str:
    """格式化分析结论"""
    lines = []
    
    if "brand_mentions" in result:
        lines.append(f"📊 品牌提及: {result['brand_mentions']}")
    
    if "sentiment" in result:
        lines.append(f"💬 情感倾向: {result['sentiment']}")
    
    if "key_features" in result and isinstance(result["key_features"], list):
        lines.append("✨ 关键特征:")
        for feature in result["key_features"][:5]:
            lines.append(f"   • {feature}")
    
    if "recommendations" in result and isinstance(result["recommendations"], list):
        lines.append("💡 优化建议:")
        for rec in result["recommendations"][:5]:
            lines.append(f"   • {rec}")
    
    # 处理原始数据
    if "advantages" in result:
        lines.append("✅ 优势:")
        for adv in (result["advantages"] if isinstance(result["advantages"], list) else [result["advantages"]]):
            lines.append(f"   • {adv}")
    
    if "weaknesses" in result:
        lines.append("⚠️ 劣势:")
        for weak in (result["weaknesses"] if isinstance(result["weaknesses"], list) else [result["weaknesses"]]):
            lines.append(f"   • {weak}")
    
    if "opportunities" in result:
        lines.append("🚀 机会:")
        for opp in (result["opportunities"] if isinstance(result["opportunities"], list) else [result["opportunities"]]):
            lines.append(f"   • {opp}")
    
    if "content_types" in result:
        lines.append("📝 内容类型:")
        for ct in result["content_types"]:
            lines.append(f"   • {ct}")
    
    if "platforms" in result:
        lines.append("🌐 推荐平台:")
        for plat in result["platforms"]:
            lines.append(f"   • {plat}")
    
    if "sample_titles" in result:
        lines.append("📌 推荐标题:")
        for title in result["sample_titles"][:3]:
            lines.append(f"   • {title}")
    
    return "\n".join(lines) if lines else str(result)


def _format_platform_data(result: Dict) -> str:
    """格式化平台数据"""
    lines = []
    
    # AI使用信息
    if "ai_used" in result:
        lines.append(f"🤖 分析AI: {result['ai_used']}")
    
    # 竞品信息
    if "competitors" in result:
        comps = result["competitors"]
        if isinstance(comps, list):
            lines.append(f"🏢 主要竞品: {', '.join(comps[:5])}")
    
    # 关键词
    if "target_keywords" in result:
        kws = result["target_keywords"]
        if isinstance(kws, list):
            lines.append(f"🔑 目标关键词: {', '.join(kws[:10])}")
    
    # 品牌定位
    if "brand_position" in result:
        lines.append(f"📍 品牌定位: {result['brand_position']}")
    
    # 错误信息
    if "error" in result and result["error"]:
        lines.append(f"⚠️ 错误: {result['error']}")
    
    return "\n".join(lines) if lines else ""


def _upsert_record(record_data: Dict) -> bool:
    """使用 lark-cli 写入记录"""
    try:
        # 构造 JSON 字符串
        json_str = json.dumps(record_data, ensure_ascii=False)
        
        # 调用 lark-cli base record-upsert
        cmd = [
            "lark-cli", "base", "+record-upsert",
            "--base-token", FEISHU_CONFIG["base_token"],
            "--table-id", FEISHU_CONFIG["table_id"],
            "--json", json_str
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 飞书推送成功")
            return True
        else:
            print(f"❌ 飞书推送失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 飞书推送超时")
        return False
    except Exception as e:
        print(f"❌ 飞书推送异常: {str(e)}")
        return False


def test_connection() -> bool:
    """测试飞书连接"""
    try:
        cmd = [
            "lark-cli", "base", "+table-get",
            "--base-token", FEISHU_CONFIG["base_token"],
            "--table-id", FEISHU_CONFIG["table_id"]
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ 飞书连接正常")
            return True
        else:
            print(f"❌ 飞书连接失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 飞书连接异常: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 飞书推送模块测试\n")
    
    # 测试连接
    print("1️⃣ 测试飞书连接...")
    test_connection()
    
    # 测试推送
    print("\n2️⃣ 测试推送示例数据...")
    sample_result = {
        "brand_name": "武汉万象城",
        "industry": "本地生活",
        "brand_mentions": "约 2.3 万次/月",
        "sentiment": "正面为主",
        "key_features": ["高端定位", "品牌齐全", "地理位置优越"],
        "recommendations": ["加强线上内容种草", "优化会员体系"],
        "ai_used": "DeepSeek"
    }
    
    success = push_analysis_to_feishu(sample_result, "武汉万象城", "本地生活")
    print(f"\n{'✅ 推送成功' if success else '❌ 推送失败'}")
