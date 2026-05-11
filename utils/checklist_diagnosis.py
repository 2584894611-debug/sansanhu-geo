# -*- coding: utf-8 -*-
"""
好易易GEO - GEO Checklist 诊断功能
根据GEO 14条Checklist，诊断内容是否符合GEO优化标准
"""

import re
from typing import Dict, List, Any


def diagnose_content(text: str) -> dict:
    """
    诊断内容是否符合GEO优化标准
    
    Args:
        text: 待诊断的文本内容（支持Markdown格式）
        
    Returns:
        dict: 诊断结果，包含：
            - score: 总分 (0-100)
            - passed: 通过数
            - failed: 未通过数
            - details: 详细检查结果列表
            - overall: 总体评价 (优秀/良好/一般/需优化)
            - priority_fixes: 优先修复项
    """
    if not text or not text.strip():
        return _empty_result()
    
    # 定义所有检查项（按优先级排序）
    checks = [
        # 核心检查项（各15分）
        {
            "id": "direct_answer",
            "item": "直接回答（结论先行）",
            "priority": "🔴核心",
            "max_score": 15,
            "checker": _check_direct_answer
        },
        {
            "id": "comparison_table",
            "item": "对比表格",
            "priority": "🔴核心",
            "max_score": 15,
            "checker": _check_comparison_table
        },
        {
            "id": "faq_block",
            "item": "FAQ区块",
            "priority": "🔴核心",
            "max_score": 15,
            "checker": _check_faq_block
        },
        {
            "id": "clear_conclusion",
            "item": "清晰结论句",
            "priority": "🔴核心",
            "max_score": 15,
            "checker": _check_clear_conclusion
        },
        {
            "id": "structured_paragraph",
            "item": "结构化段落",
            "priority": "🔴核心",
            "max_score": 15,
            "checker": _check_structured_paragraph
        },
        # 建议检查项（各10分）
        {
            "id": "schema_markup",
            "item": "Schema标记",
            "priority": "🟡建议",
            "max_score": 10,
            "checker": _check_schema_markup
        },
        {
            "id": "semantic_html",
            "item": "语义化HTML",
            "priority": "🟡建议",
            "max_score": 10,
            "checker": _check_semantic_html
        },
        {
            "id": "content_length",
            "item": "内容长度足够",
            "priority": "🟡建议",
            "max_score": 10,
            "checker": _check_content_length
        },
        {
            "id": "external_citations",
            "item": "外部引用权威来源",
            "priority": "🟡建议",
            "max_score": 10,
            "checker": _check_external_citations
        },
    ]
    
    # 执行所有检查
    details = []
    total_score = 0
    passed_count = 0
    failed_count = 0
    priority_fixes = []
    
    for check in checks:
        result = check["checker"](text)
        detail = {
            "item": check["item"],
            "priority": check["priority"],
            **result
        }
        details.append(detail)
        
        total_score += result["score"]
        
        if result["status"] == "✅通过":
            passed_count += 1
        elif result["status"] == "❌未通过":
            failed_count += 1
            # 核心项未通过需要优先修复
            if check["priority"] == "🔴核心":
                priority_fixes.append(check["item"])
    
    # 限制总分不超过100
    total_score = min(100, total_score)
    
    # 判断总体评价
    if total_score >= 90:
        overall = "优秀"
    elif total_score >= 70:
        overall = "良好"
    elif total_score >= 50:
        overall = "一般"
    else:
        overall = "需优化"
    
    return {
        "score": total_score,
        "passed": passed_count,
        "failed": failed_count,
        "details": details,
        "overall": overall,
        "priority_fixes": priority_fixes
    }


def _empty_result() -> dict:
    """返回空内容的诊断结果"""
    return {
        "score": 0,
        "passed": 0,
        "failed": 9,
        "details": [],
        "overall": "需优化",
        "priority_fixes": ["直接回答（结论先行）", "对比表格", "FAQ区块", 
                          "清晰结论句", "结构化段落"]
    }


# ==================== 各检查项实现 ====================

def _check_direct_answer(content: str) -> dict:
    """
    检查1: 直接回答（结论先行）
    判断：内容开头100字内是否包含结论性回答
    """
    # 获取开头100字
    first_100 = content[:100]
    
    # 结论性关键词
    conclusion_keywords = [
        r"^(是|否|正确|错误|可以|不行|推荐|不建议|最好|最佳)",
        r"^(总体|整体|总体上|整体来看|总体而言)",
        r"^(答案是|结论是|结论：|答案是：)",
        r"^(本文|本文档|本指南|本文将)",
    ]
    
    # 问题导向的关键词（开头应该是答案而非问题）
    question_keywords = [
        r"^(什么是|如何|怎么|怎样|为什么|为何|是否|能不能)",
        r"^(大家好|今天|欢迎|首先|开场)",
    ]
    
    is_passed = False
    evidence = ""
    
    # 检查是否有结论性开头
    for pattern in conclusion_keywords:
        if re.search(pattern, first_100):
            is_passed = True
            match = re.search(pattern, first_100)
            evidence = f"开头包含结论性表述: '{match.group()}'"
            break
    
    # 检查是否是问题导向的开头
    for pattern in question_keywords:
        if re.search(pattern, first_100):
            is_passed = False
            match = re.search(pattern, first_100)
            evidence = f"开头是问题导向: '{match.group()}'，建议改为结论先行"
            break
    
    if is_passed:
        return {
            "status": "✅通过",
            "score": 15,
            "max_score": 15,
            "suggestion": "内容开头已有直接回答，继续保持",
            "evidence": evidence
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 15,
            "suggestion": "建议在开头100字内直接给出结论或答案，避免冗长的背景介绍",
            "evidence": evidence if evidence else "开头100字内未发现明确的结论性表述"
        }


def _check_comparison_table(content: str) -> dict:
    """
    检查2: 对比表格
    判断：是否包含Markdown/HTML表格
    """
    # Markdown表格检测 - 查找包含|的行
    md_lines = [line for line in content.split('\n') if '|' in line and line.strip().startswith('|')]
    has_md_table = len(md_lines) >= 2
    
    # HTML表格模式
    html_table_pattern = r'<table[^>]*>.*?</table>'
    has_html_table = re.search(html_table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if has_md_table or has_html_table:
        evidence = ""
        if has_md_table:
            evidence = f"发现Markdown表格 ({len(md_lines)}行)"
        if has_html_table:
            evidence = f"发现HTML表格"
        
        return {
            "status": "✅通过",
            "score": 15,
            "max_score": 15,
            "suggestion": "已包含结构化对比表格，有助于信息清晰呈现",
            "evidence": evidence
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 15,
            "suggestion": "建议添加对比表格，使用Markdown格式 |列1|列2|列3| 来组织信息",
            "evidence": "未发现Markdown或HTML表格"
        }


def _check_faq_block(content: str) -> dict:
    """
    检查3: FAQ区块
    判断：是否有"Q:"、"问："、"？"格式的问答
    """
    # FAQ格式模式
    faq_patterns = [
        r'Q[：:]\s*\S+',           # Q: 或 Q：
        r'问[：:]\s*\S+',          # 问: 或 问：
        r'\?\s*\n\s*[Aa]nswer',    # ? 后面跟 Answer
        r'常见问题[：:]',           # 常见问题：
        r'FAQ[：:]',               # FAQ:
        r'##\s*(Q问|FAQ|常见问题)',  # # Q问 或 # FAQ
    ]
    
    faq_count = 0
    matched_patterns = []
    
    for pattern in faq_patterns:
        matches = re.findall(pattern, content)
        if matches:
            faq_count += len(matches)
            matched_patterns.extend(matches)
    
    if faq_count > 0:
        return {
            "status": "✅通过",
            "score": 15,
            "max_score": 15,
            "suggestion": "已包含FAQ区块，有助于覆盖用户常见问题",
            "evidence": f"发现{faq_count}处FAQ格式，如: {matched_patterns[0]}"
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 15,
            "suggestion": "建议添加FAQ区块，格式如: 'Q: 什么是xxx?\\nA: xxx是...'",
            "evidence": "未发现FAQ格式（Q:、问:、常见问题等）"
        }


def _check_clear_conclusion(content: str) -> dict:
    """
    检查4: 清晰结论句
    判断：是否有"综上所述"、"总结"、"总之"等总结词
    """
    # 总结性关键词
    conclusion_keywords = [
        r'综上所述',
        r'总结[来可言上看]?',
        r'总之',
        r'总体而言',
        r'整体来看',
        r'总[结的来说]',
        r'归根结底',
        r'简而言之',
        r'关键结论',
        r'最终结论',
    ]
    
    matches = []
    for pattern in conclusion_keywords:
        found = re.findall(pattern, content)
        if found:
            matches.extend(found)
    
    if matches:
        return {
            "status": "✅通过",
            "score": 15,
            "max_score": 15,
            "suggestion": "已有总结性段落，帮助用户快速了解核心观点",
            "evidence": f"发现总结性语句: '{matches[0]}'"
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 15,
            "suggestion": "建议在结尾添加总结段落，使用'综上所述'、'总之'等引导词",
            "evidence": "未发现总结性语句"
        }


def _check_structured_paragraph(content: str) -> dict:
    """
    检查5: 结构化段落
    判断：是否使用## H2 / ### H3标题
    """
    # H2标题
    h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
    
    # H3标题
    h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))
    
    total_headers = h2_count + h3_count
    
    if total_headers >= 2:
        evidence = f"H2标题{h2_count}个，H3标题{h3_count}个"
        return {
            "status": "✅通过",
            "score": 15,
            "max_score": 15,
            "suggestion": "已使用多级标题结构，层次清晰",
            "evidence": evidence
        }
    elif total_headers == 1:
        return {
            "status": "⚠️建议",
            "score": 8,
            "max_score": 15,
            "suggestion": "建议增加更多小标题，使用## 二级标题和### 三级标题分层",
            "evidence": f"仅有{total_headers}个标题，层次不够丰富"
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 15,
            "suggestion": "建议添加## 二级标题和### 三级标题来组织内容结构",
            "evidence": "未发现##或###标题，全文无层次结构"
        }


def _check_schema_markup(content: str) -> dict:
    """
    检查6: Schema标记
    判断：是否包含FAQ/HowTo/Review等Schema
    """
    # Schema类型关键词
    schema_patterns = [
        r'@type.*FAQ',
        r'@type.*HowTo',
        r'@type.*Review',
        r'type.*FAQ',
        r'type.*HowTo',
        r'application/ld\+json',
        r'schema\.org',
    ]
    
    matches = []
    for pattern in schema_patterns:
        found = re.findall(pattern, content, re.IGNORECASE)
        if found:
            matches.extend(found)
    
    if matches:
        return {
            "status": "✅通过",
            "score": 10,
            "max_score": 10,
            "suggestion": "已包含结构化数据标记，有助于搜索引擎理解内容",
            "evidence": f"发现Schema标记: {matches[0]}"
        }
    else:
        return {
            "status": "⚠️建议",
            "score": 0,
            "max_score": 10,
            "suggestion": "建议添加JSON-LD Schema标记，如FAQ、HowTo等类型",
            "evidence": "未发现Schema标记"
        }


def _check_semantic_html(content: str) -> dict:
    """
    检查7: 语义化HTML
    判断：是否使用article/section/aside等语义标签
    """
    # 语义化标签
    semantic_tags = [
        r'<article',
        r'<section',
        r'<aside',
        r'<header',
        r'<footer',
        r'<nav',
        r'<main',
        r'<figure',
        r'<figcaption',
    ]
    
    matches = []
    for tag in semantic_tags:
        found = re.findall(tag, content, re.IGNORECASE)
        if found:
            matches.append(tag.replace('<', ''))
    
    # 检查是否全是div
    all_divs = len(re.findall(r'<div', content, re.IGNORECASE))
    semantic_count = len(matches)
    
    if semantic_count >= 2:
        return {
            "status": "✅通过",
            "score": 10,
            "max_score": 10,
            "suggestion": "已使用语义化HTML标签，结构清晰",
            "evidence": f"发现语义标签: {', '.join(matches[:3])}"
        }
    elif semantic_count == 1:
        return {
            "status": "⚠️建议",
            "score": 5,
            "max_score": 10,
            "suggestion": "建议增加更多语义标签，如<article>、<section>、<aside>等",
            "evidence": f"仅发现{matches[0]}标签"
        }
    else:
        return {
            "status": "⚠️建议",
            "score": 0,
            "max_score": 10,
            "suggestion": "建议使用语义化标签替代div，如<article>、<section>等",
            "evidence": f"未发现语义标签（div数量: {all_divs}）"
        }


def _check_content_length(content: str) -> dict:
    """
    检查8: 内容长度足够
    判断：字符数是否>=600
    """
    # 移除Markdown格式符号后计算字符数
    clean_content = re.sub(r'[#*|`_\[\](){}<>]', '', content)
    char_count = len(clean_content)
    
    if char_count >= 1500:
        return {
            "status": "✅通过",
            "score": 10,
            "max_score": 10,
            "suggestion": "内容长度充足，详细深入",
            "evidence": f"约{char_count}字，内容充实"
        }
    elif char_count >= 600:
        return {
            "status": "✅通过",
            "score": 8,
            "max_score": 10,
            "suggestion": "内容长度基本达标，建议适当扩展以提供更详细信息",
            "evidence": f"约{char_count}字"
        }
    elif char_count >= 300:
        return {
            "status": "⚠️建议",
            "score": 5,
            "max_score": 10,
            "suggestion": "内容偏短，建议扩展至600字以上以提高信息完整度",
            "evidence": f"仅{char_count}字，建议≥600字"
        }
    else:
        return {
            "status": "❌未通过",
            "score": 0,
            "max_score": 10,
            "suggestion": "内容过短，建议扩展至600字以上",
            "evidence": f"仅{char_count}字"
        }


def _check_external_citations(content: str) -> dict:
    """
    检查9: 外部引用权威来源
    判断：是否引用权威来源（政府/学术/知名媒体）
    """
    # 权威来源关键词
    authority_patterns = [
        # 政府机构
        r'(国务院|发改委|工信部|教育部|卫健委|统计局|人民网|新华网|中国政府网)',
        # 知名媒体
        r'(财经网|经济观察报|第一财经|21世纪经济报道|澎湃新闻|36氪|虎嗅|钛媒体)',
        # 学术来源
        r'(知网|万方|维普|cnki\.edu\.cn|wanfangdata\.com)',
        # 国际权威
        r'(麦肯锡|贝恩|波士顿咨询|德勤|普华永道|Gartner|Forrester)',
        # 官方数据
        r'(年鉴|公报|白皮书|统计公报)',
        # 引用格式
        r'\[注?\d+\]|来源：|引用：|数据来源：',
    ]
    
    matches = []
    for pattern in authority_patterns:
        found = re.findall(pattern, content)
        if found:
            matches.extend(found)
    
    # 去重
    unique_matches = list(set(matches))
    
    if len(unique_matches) >= 2:
        return {
            "status": "✅通过",
            "score": 10,
            "max_score": 10,
            "suggestion": "已引用多个权威来源，增强内容可信度",
            "evidence": f"发现权威来源: {', '.join(unique_matches[:3])}"
        }
    elif len(unique_matches) == 1:
        return {
            "status": "⚠️建议",
            "score": 5,
            "max_score": 10,
            "suggestion": "建议增加更多权威数据来源，如政府报告、学术论文等",
            "evidence": f"发现1处权威来源: {unique_matches[0]}"
        }
    else:
        return {
            "status": "⚠️建议",
            "score": 0,
            "max_score": 10,
            "suggestion": "建议添加权威来源引用，如政府数据、学术研究、知名媒体等",
            "evidence": "未发现权威来源引用"
        }


# ==================== 辅助函数 ====================

def print_diagnosis_report(result: dict) -> str:
    """
    格式化打印诊断报告
    
    Args:
        result: diagnose_content返回的诊断结果
        
    Returns:
        str: 格式化的报告文本
    """
    lines = []
    lines.append("=" * 50)
    lines.append("📊 GEO Checklist 诊断报告")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"📈 总分: {result['score']}/100 ({result['overall']})")
    lines.append(f"✅ 通过: {result['passed']} | ❌ 未通过: {result['failed']}")
    lines.append("")
    
    lines.append("📋 详细检查结果:")
    lines.append("-" * 50)
    
    for detail in result["details"]:
        status_icon = detail["status"][0]  # ✅ or ❌ or ⚠️
        priority = detail.get("priority", "")
        lines.append(f"{status_icon} {detail['item']} ({priority})")
        lines.append(f"   得分: {detail['score']}/{detail['max_score']}")
        lines.append(f"   证据: {detail['evidence']}")
        lines.append(f"   建议: {detail['suggestion']}")
        lines.append("")
    
    if result["priority_fixes"]:
        lines.append("-" * 50)
        lines.append("🎯 优先修复项:")
        for item in result["priority_fixes"]:
            lines.append(f"   • {item}")
    
    lines.append("")
    lines.append("=" * 50)
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试样例
    sample_content = """
# 武汉商场美食指南

## 直接回答
是的，武汉确实有许多值得一试的商场美食选择。本文将为您推荐武汉最受欢迎的商场美食。

## 最佳商场推荐

### 1. 武汉K11购物艺术中心
- 地址: 武汉市洪山区关山大道
- 特色: 融合艺术与购物的全新体验

### 2. 武汉天地壹方北馆
- 地址: 武汉市江岸区中山大道
- 特色: 高端餐饮集中地

## 美食对比

| 商场名称 | 餐饮种类 | 人均消费 | 推荐指数 |
|---------|---------|---------|---------|
| K11 | 中西融合 | 80-150元 | ⭐⭐⭐⭐ |
| 壹方北馆 | 高端精致 | 150-300元 | ⭐⭐⭐⭐⭐ |
| 光谷K11 | 网红潮流 | 50-100元 | ⭐⭐⭐ |

## 常见问题FAQ

Q: 武汉K11有哪些必吃的餐厅?
A: 推荐祖母的厨房、西贝莜面村等口碑餐厅。

Q: 哪个商场适合家庭聚餐?
A: 推荐武汉天地壹方北馆，儿童设施完善。

## 总结
综上所述，武汉商场美食选择丰富，无论是高端精致还是平价美味都能找到。建议根据用餐需求选择合适的商场。
"""
    
    result = diagnose_content(sample_content)
    print(print_diagnosis_report(result))
