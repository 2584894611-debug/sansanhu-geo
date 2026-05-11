#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好易易GEO - AI搜索分析后端API服务 (扩展版)
支持Freemium模式、数据库存储、用户管理、订阅监测和行业数据
"""

import os
import json
import re
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import lru_cache
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-8914498a0fff48e793153ab852a38ae5")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 数据库配置 - 使用环境变量，支持Docker部署
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "geo.db"))

# 平台列表
PLATFORMS = ["豆包", "元宝", "Kimi", "通义", "文心", "天工"]

# Freemium配置
FREE_DAILY_LIMIT = 1  # 免费用户每天1次

# ==================== 行业配置 ====================
INDUSTRIES = [
    {"id": "catering", "name": "餐饮美食", "icon": "🍜", "keywords": ["餐厅", "美食", "餐饮", "小吃", "火锅", "烧烤", "川菜", "粤菜"]},
    {"id": "retail", "name": "零售商业", "icon": "🛒", "keywords": ["超市", "便利店", "商场", "购物中心", "零售", "百货"]},
    {"id": "tourism", "name": "文化旅游", "icon": "🏛️", "keywords": ["旅游", "景区", "酒店", "民宿", "旅行", "度假", "门票"]},
    {"id": "education", "name": "教育培训", "icon": "📚", "keywords": ["培训", "教育", "学校", "课程", "辅导", "家教", "技能"]},
    {"id": "medical", "name": "医疗健康", "icon": "🏥", "keywords": ["医院", "医疗", "健康", "诊所", "药店", "体检", "牙科"]},
    {"id": "tech", "name": "科技互联网", "icon": "💻", "keywords": ["科技", "互联网", "软件", "AI", "电商", "IT", "云计算"]},
    {"id": "realestate", "name": "房产家居", "icon": "🏠", "keywords": ["房产", "房地产", "家居", "装修", "中介", "物业", "公寓"]},
    {"id": "automotive", "name": "汽车出行", "icon": "🚗", "keywords": ["汽车", "4S店", "维修", "保养", "二手车", "加油", "停车"]},
    {"id": "finance", "name": "金融保险", "icon": "💰", "keywords": ["银行", "保险", "理财", "贷款", "投资", "证券", "基金"]},
    {"id": "service", "name": "生活服务", "icon": "🔧", "keywords": ["家政", "洗衣", "美容", "摄影", "婚庆", "搬家", "宠物"]}
]

# 行业基准数据（模拟数据）
INDUSTRY_BENCHMARKS = {
    "catering": {"avg_visibility": 65, "avg_sentiment": 72, "avg_recommendation": 58, "top_issues": ["菜品描述不完善", "缺少用户评价", "品牌故事缺失"]},
    "retail": {"avg_visibility": 70, "avg_sentiment": 68, "avg_recommendation": 65, "top_issues": ["产品信息不完整", "价格信息缺失", "门店信息不准确"]},
    "tourism": {"avg_visibility": 68, "avg_sentiment": 75, "avg_recommendation": 70, "top_issues": ["景点介绍不详细", "缺少游览攻略", "预订信息缺失"]},
    "education": {"avg_visibility": 62, "avg_sentiment": 70, "avg_recommendation": 72, "top_issues": ["课程介绍不清晰", "师资信息缺失", "效果展示不足"]},
    "medical": {"avg_visibility": 60, "avg_sentiment": 65, "avg_recommendation": 68, "top_issues": ["科室介绍不完善", "医生信息缺失", "就诊流程不清晰"]},
    "tech": {"avg_visibility": 75, "avg_sentiment": 72, "avg_recommendation": 78, "top_issues": ["技术文档不完善", "产品功能描述缺失", "案例展示不足"]},
    "realestate": {"avg_visibility": 65, "avg_sentiment": 60, "avg_recommendation": 55, "top_issues": ["楼盘信息不完整", "价格不透明", "户型图缺失"]},
    "automotive": {"avg_visibility": 68, "avg_sentiment": 65, "avg_recommendation": 62, "top_issues": ["车型参数不完整", "报价不透明", "试驾预约复杂"]},
    "finance": {"avg_visibility": 58, "avg_sentiment": 62, "avg_recommendation": 60, "top_issues": ["产品条款复杂", "收益不明确", "风险提示不足"]},
    "service": {"avg_visibility": 63, "avg_sentiment": 70, "avg_recommendation": 65, "top_issues": ["服务内容不清晰", "价格不透明", "案例展示不足"]}
}

# 行业特定优化建议
INDUSTRY_RECOMMENDATIONS = {
    "catering": [
        "完善菜品描述，包括口味、食材、份量等信息",
        "优化餐厅环境和服务描述，增加用户代入感",
        "收集并展示高质量用户点评",
        "制作精美的菜品图片和视频内容",
        "建立标准化品牌故事和口号"
    ],
    "retail": [
        "完善产品详情页信息，包括规格、材质、使用方法",
        "优化商品标题和关键词，提升搜索可见度",
        "展示真实用户评价和使用场景",
        "提供清晰的价格说明和促销活动",
        "优化门店地址和营业时间信息"
    ],
    "tourism": [
        "提供详细的景点介绍和游览攻略",
        "优化酒店/民宿的特色服务和设施描述",
        "展示真实的游客点评和旅行照片",
        "提供预订指南和注意事项说明",
        "制作目的地特色文化内容"
    ],
    "education": [
        "清晰展示课程体系和教学目标",
        "提供师资介绍和教学成果展示",
        "展示学员评价和学习效果",
        "优化课程特色和适用人群描述",
        "提供详细的学习方式和时间安排"
    ],
    "medical": [
        "完善科室介绍和医生专业背景",
        "提供就诊流程和注意事项指南",
        "展示医院特色技术和设备",
        "优化挂号预约流程说明",
        "提供健康科普和疾病知识内容"
    ],
    "tech": [
        "提供详细的产品功能和技术文档",
        "展示应用场景和解决方案案例",
        "优化产品对比和优势说明",
        "提供API文档和技术支持信息",
        "展示客户案例和合作伙伴"
    ],
    "realestate": [
        "提供完整的楼盘信息和户型图",
        "展示小区环境和配套设施",
        "提供价格构成和付款方式说明",
        "优化区位分析和交通配套",
        "展示开发商背景和资质信息"
    ],
    "automotive": [
        "提供详细的车型参数和配置对比",
        "展示车辆实拍图和视频",
        "提供透明的价格和优惠信息",
        "优化试驾预约和服务流程",
        "展示售后服务和保养方案"
    ],
    "finance": [
        "简化产品介绍，突出核心优势和收益",
        "提供清晰的风险提示和条款说明",
        "展示公司资质和监管信息",
        "提供产品对比和选择建议",
        "优化在线投保/投资流程说明"
    ],
    "service": [
        "清晰展示服务内容和服务流程",
        "提供透明的价格体系和服务标准",
        "展示真实的服务案例和效果",
        "优化预约流程和时间安排",
        "提供常见问题解答和服务承诺"
    ]
}

# ==================== 数据库操作 ====================
def get_db_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """初始化数据库"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 用户表
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                token TEXT UNIQUE NOT NULL,
                is_premium INTEGER DEFAULT 0,
                premium_expires_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login_at TEXT
            )
        ''')
        
        # 分析记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                brand TEXT NOT NULL,
                industry TEXT,
                industry_id TEXT,
                geo_score INTEGER,
                visibility_score INTEGER,
                recommendation_score INTEGER,
                sentiment_score INTEGER,
                diagnosis_data TEXT,
                competitor_data TEXT,
                recommendations TEXT,
                is_full_report INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 历史评分表
        c.execute('''
            CREATE TABLE IF NOT EXISTS score_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                industry TEXT,
                industry_id TEXT,
                geo_score INTEGER,
                visibility_score INTEGER,
                recommendation_score INTEGER,
                sentiment_score INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 每日使用统计表
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                usage_date TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                UNIQUE(user_id, usage_date),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 预警记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT,
                old_score INTEGER,
                new_score INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 监测订阅表
        c.execute('''
            CREATE TABLE IF NOT EXISTS monitor_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                brand TEXT NOT NULL,
                industry TEXT,
                industry_id TEXT,
                frequency TEXT DEFAULT 'daily',
                is_active INTEGER DEFAULT 1,
                last_check_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 监测历史数据表
        c.execute('''
            CREATE TABLE IF NOT EXISTS monitor_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER NOT NULL,
                geo_score INTEGER,
                visibility_score INTEGER,
                recommendation_score INTEGER,
                sentiment_score INTEGER,
                score_change INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subscription_id) REFERENCES monitor_subscriptions(id)
            )
        ''')
        
        conn.commit()
        print("✅ 数据库初始化完成")

# ==================== 用户管理 ====================
def get_or_create_user(device_id: str) -> Dict[str, Any]:
    """获取或创建用户"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 查找现有用户
        c.execute("SELECT * FROM users WHERE device_id = ?", (device_id,))
        user = c.fetchone()
        
        if not user:
            # 创建新用户
            token = secrets.token_urlsafe(32)
            c.execute(
                "INSERT INTO users (device_id, token) VALUES (?, ?)",
                (device_id, token)
            )
            conn.commit()
            c.execute("SELECT * FROM users WHERE device_id = ?", (device_id,))
            user = c.fetchone()
        
        # 更新最后登录时间
        c.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user["id"])
        )
        conn.commit()
        
        return dict(user)

def check_user_status(device_id: str) -> Dict[str, Any]:
    """检查用户状态和剩余次数"""
    user = get_or_create_user(device_id)
    
    today = datetime.now().date().isoformat()
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 检查今日使用次数
        c.execute(
            "SELECT usage_count FROM daily_usage WHERE user_id = ? AND usage_date = ?",
            (user["id"], today)
        )
        result = c.fetchone()
        today_usage = result["usage_count"] if result else 0
        
        # 检查是否为付费用户
        is_premium = user["is_premium"] == 1
        if user["premium_expires_at"]:
            expires_at = datetime.fromisoformat(user["premium_expires_at"])
            if expires_at < datetime.now():
                is_premium = False
        
        # 计算剩余次数
        if is_premium:
            remaining = -1  # 无限次
        else:
            remaining = max(0, FREE_DAILY_LIMIT - today_usage)
        
        return {
            "is_premium": is_premium,
            "today_usage": today_usage,
            "remaining": remaining,
            "token": user["token"]
        }

def increment_usage(device_id: str):
    """增加使用次数"""
    user = get_or_create_user(device_id)
    today = datetime.now().date().isoformat()
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO daily_usage (user_id, usage_date, usage_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, usage_date)
            DO UPDATE SET usage_count = usage_count + 1
        ''', (user["id"], today))
        conn.commit()

def save_analysis_record(device_id: str, analysis_data: Dict[str, Any], is_full: bool = False):
    """保存分析记录"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO analysis_records 
            (user_id, brand, industry, industry_id, geo_score, visibility_score, recommendation_score, 
             sentiment_score, diagnosis_data, competitor_data, recommendations, is_full_report)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user["id"],
            analysis_data.get("brand_name", ""),
            analysis_data.get("industry", ""),
            analysis_data.get("industry_id", ""),
            analysis_data.get("geo_score", 0),
            analysis_data.get("visibility_score", 0),
            analysis_data.get("recommendation_score", 0),
            analysis_data.get("sentiment_score", 0),
            json.dumps(analysis_data.get("diagnosis", []), ensure_ascii=False),
            json.dumps(analysis_data.get("competitors", []), ensure_ascii=False),
            json.dumps(analysis_data.get("recommendations", []), ensure_ascii=False),
            1 if is_full else 0
        ))
        conn.commit()
        return c.lastrowid

def save_score_history(brand: str, industry: str, industry_id: str, scores: Dict[str, int]):
    """保存评分历史"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 检查上次评分
        c.execute(
            "SELECT geo_score FROM score_history WHERE brand = ? ORDER BY created_at DESC LIMIT 1",
            (brand,)
        )
        old_record = c.fetchone()
        old_score = old_record["geo_score"] if old_record else None
        
        c.execute('''
            INSERT INTO score_history 
            (brand, industry, industry_id, geo_score, visibility_score, recommendation_score, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            brand, industry, industry_id,
            scores.get("geo_score", 0),
            scores.get("visibility_score", 0),
            scores.get("recommendation_score", 0),
            scores.get("sentiment_score", 0)
        ))
        conn.commit()
        
        # 如果有变化，生成预警
        if old_score is not None and scores.get("geo_score", 0) != old_score:
            change = scores.get("geo_score", 0) - old_score
            alert_type = "rise" if change > 0 else "fall"
            c.execute('''
                INSERT INTO alerts (brand, alert_type, message, old_score, new_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                brand, alert_type,
                f"GEO评分{'上升' if change > 0 else '下降'}{'+' if change > 0 else ''}{change}分",
                old_score, scores.get("geo_score", 0)
            ))
            conn.commit()

def get_analysis_history(device_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """获取分析历史"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM analysis_records 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user["id"], limit))
        
        return [dict(row) for row in c.fetchall()]

def get_brand_score_trend(brand: str, days: int = 30) -> List[Dict[str, Any]]:
    """获取品牌评分趋势"""
    with get_db_connection() as conn:
        c = conn.cursor()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        c.execute('''
            SELECT * FROM score_history 
            WHERE brand = ? AND created_at >= ?
            ORDER BY created_at ASC
        ''', (brand, start_date))
        
        return [dict(row) for row in c.fetchall()]

def get_recent_alerts(brand: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取最近的预警"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        if brand:
            c.execute('''
                SELECT * FROM alerts 
                WHERE brand = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (brand, limit))
        else:
            c.execute('''
                SELECT * FROM alerts 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in c.fetchall()]

# ==================== 监测订阅管理 ====================
def create_monitor_subscription(device_id: str, brand: str, industry: str, industry_id: str, frequency: str) -> Dict[str, Any]:
    """创建监测订阅"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 检查是否已存在
        c.execute(
            "SELECT * FROM monitor_subscriptions WHERE user_id = ? AND brand = ? AND is_active = 1",
            (user["id"], brand)
        )
        existing = c.fetchone()
        if existing:
            return {"success": False, "error": "该品牌已在监测列表中"}
        
        c.execute('''
            INSERT INTO monitor_subscriptions (user_id, brand, industry, industry_id, frequency)
            VALUES (?, ?, ?, ?, ?)
        ''', (user["id"], brand, industry, industry_id, frequency))
        conn.commit()
        
        return {"success": True, "id": c.lastrowid}

def get_monitor_subscriptions(device_id: str) -> List[Dict[str, Any]]:
    """获取用户的监测订阅列表"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT ms.*, 
                   (SELECT geo_score FROM monitor_history WHERE subscription_id = ms.id ORDER BY created_at DESC LIMIT 1) as latest_score,
                   (SELECT geo_score FROM monitor_history WHERE subscription_id = ms.id ORDER BY created_at DESC LIMIT 1, 1) as previous_score
            FROM monitor_subscriptions ms
            WHERE ms.user_id = ? AND ms.is_active = 1
            ORDER BY ms.created_at DESC
        ''', (user["id"],))
        
        subscriptions = []
        for row in c.fetchall():
            sub = dict(row)
            # 计算变化趋势
            if sub.get('latest_score') and sub.get('previous_score'):
                sub['score_change'] = sub['latest_score'] - sub['previous_score']
            else:
                sub['score_change'] = 0
            subscriptions.append(sub)
        
        return subscriptions

def get_monitor_history(subscription_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    """获取监测历史数据"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM monitor_history
            WHERE subscription_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (subscription_id, limit))
        
        return [dict(row) for row in c.fetchall()]

def delete_monitor_subscription(subscription_id: int, device_id: str) -> bool:
    """删除监测订阅"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE monitor_subscriptions SET is_active = 0 WHERE id = ? AND user_id = ?",
            (subscription_id, user["id"])
        )
        conn.commit()
        return c.rowcount > 0

def update_monitor_subscription(subscription_id: int, device_id: str, frequency: str) -> bool:
    """更新监测订阅设置"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE monitor_subscriptions SET frequency = ? WHERE id = ? AND user_id = ?",
            (frequency, subscription_id, user["id"])
        )
        conn.commit()
        return c.rowcount > 0

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title="好易易GEO API",
    description="AI搜索健康度分析API服务",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_database()

# ==================== 数据模型 ====================
class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    type: str = Field(..., description="分析类型: brand_analysis/competitor_analysis/content_strategy")
    brand: str = Field(..., description="品牌/公司名称")
    industry: str = Field(default="通用", description="行业类型")
    industry_id: str = Field(default="tech", description="行业ID")
    device_id: str = Field(default="default", description="设备ID")

class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    ai_used: str = "DeepSeek"
    platforms_analyzed: List[str] = PLATFORMS
    error: Optional[str] = None
    is_full_report: bool = False

class UserStatusResponse(BaseModel):
    """用户状态响应"""
    is_premium: bool
    today_usage: int
    remaining: int
    token: str

class MonitorCreateRequest(BaseModel):
    """创建监测请求"""
    brand: str
    industry: str = "通用"
    industry_id: str = "tech"
    frequency: str = "daily"

class MonitorUpdateRequest(BaseModel):
    """更新监测请求"""
    frequency: str = "daily"

# ==================== DeepSeek API 调用 ====================
async def call_deepseek(prompt: str, system_prompt: Optional[str] = None) -> str:
    """调用DeepSeek API生成内容"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 3000
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

# ==================== 分析提示词模板 ====================
SYSTEM_PROMPT = """你是一位专业的AI搜索优化分析师，擅长分析品牌在AI搜索引擎中的表现。
请基于你的专业知识提供分析，不要编造具体数据，但可以基于合理推断给出专业建议。
输出格式为清晰的JSON结构。"""

@lru_cache(maxsize=128)
def get_brand_analysis_prompt(brand: str, industry: str, industry_id: str, is_full: bool = True) -> str:
    """品牌分析提示词"""
    diagnosis_limit = "全部" if is_full else "前3个"
    
    # 获取行业特定优化建议
    industry_recs = INDUSTRY_RECOMMENDATIONS.get(industry_id, INDUSTRY_RECOMMENDATIONS["tech"])
    industry_specific_tips = "\n".join([f"{i+1}. {tip}" for i, tip in enumerate(industry_recs[:3])])
    
    return f"""请对品牌「{brand}」在{industry}行业进行AI搜索健康度分析。

分析维度：
1. 品牌在AI搜索引擎中的可见度 (0-100)
2. 用户讨论情绪倾向（正面/中性/负面）(0-100)
3. 品牌核心特征和用户认知
4. 问题诊断（{diagnosis_limit}）
5. GEO优化建议

请以JSON格式返回分析结果，包含以下字段：
- brand_name: 品牌名称
- industry: 行业名称
- industry_id: 行业ID
- ai_mentions: AI搜索提及量估算
- sentiment: 用户情绪倾向
- geo_score: GEO综合评分 (0-100)
- visibility_score: 可见度评分 (0-100)
- recommendation_score: 推荐度评分 (0-100)
- sentiment_score: 情感倾向评分 (0-100)
- key_features: 品牌核心特征列表（3-5个）
- diagnosis: 问题诊断列表（每个包含type类型和description描述）
- strengths: 品牌优势（数组，3-5条）
- weaknesses: 待改进点（数组，3-5条）
- recommendations: GEO优化建议（数组，5-8条，付费用户可获得全部）
- industry_specific_tips: {industry}行业专属优化建议

只输出JSON，不要其他内容。"""

@lru_cache(maxsize=128)
def get_competitor_analysis_prompt(brand: str, industry: str) -> str:
    """竞品分析提示词"""
    return f"""请对「{brand}」在{industry}行业进行竞品对比分析。

分析维度：
1. 主要竞争对手识别（3-5个）
2. 竞争优势和劣势对比
3. 市场机会分析

请以JSON格式返回分析结果，包含以下字段：
- main_brand: 主分析品牌
- industry: 行业
- competitive_position: 竞争定位（描述）
- competitors: 竞品列表，每个包含name名称、score评分(0-100)、strengths优势、weaknesses劣势
- advantages: 相对于竞品的竞争优势（数组）
- threats: 竞品威胁（数组）
- opportunities: 市场机会（数组）
- strategic_suggestions: 战略建议（数组，5-8条）

只输出JSON，不要其他内容。"""

@lru_cache(maxsize=128)
def get_content_strategy_prompt(brand: str, industry: str) -> str:
    """内容策略提示词"""
    return f"""请为「{brand}」在{industry}行业制定AI搜索优化内容策略。

策略维度：
1. 目标关键词规划
2. 内容类型建议
3. 平台分发策略
4. 爆款标题创作

请以JSON格式返回策略，包含以下字段：
- target_keywords: 目标关键词列表（5-8个）
- content_types: 推荐内容类型（数组）
- platforms: 重点平台及权重（数组，每个包含name平台名和weight权重0-1）
- sample_titles: 爆款标题示例（5-8个）
- content_calendar: 内容规划建议（按周/月的简单计划）
- seo_tips: SEO优化技巧（数组）
- trending_topics: 当前热点话题建议（数组）

只输出JSON，不要其他内容。"""

# ==================== 辅助函数 ====================
def parse_json_response(text: str) -> Dict[str, Any]:
    """解析API返回的JSON响应"""
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {"raw_response": text, "note": "原始响应，无法解析为结构化JSON"}

def safe_json_loads(text: str) -> Dict[str, Any]:
    """安全地解析JSON"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return parse_json_response(text)

def generate_mock_analysis(brand: str, industry: str, industry_id: str, is_full: bool = True) -> Dict[str, Any]:
    """生成模拟分析数据（当API调用失败时使用）"""
    import random
    base_score = random.randint(55, 75)
    
    diagnosis = [
        {"type": "可见度不足", "description": f"{brand}在AI搜索引擎中的品牌提及量较低"},
        {"type": "内容缺失", "description": "缺少针对AI搜索优化的结构化内容"},
        {"type": "情感偏差", "description": "用户讨论中存在一定的负面情绪需要关注"},
        {"type": "关键词薄弱", "description": "核心关键词在AI搜索结果中排名靠后"},
        {"type": "内容深度不足", "description": "品牌相关内容缺乏专业深度和权威性"}
    ]
    
    # 获取行业特定建议
    industry_recs = INDUSTRY_RECOMMENDATIONS.get(industry_id, INDUSTRY_RECOMMENDATIONS["tech"])
    general_recs = [
        "增加品牌在权威媒体和行业网站的曝光",
        "创建FAQ类型内容，覆盖用户常见问题",
        "优化品牌故事的叙事结构，便于AI理解",
        "建立内容更新机制，保持信息时效性",
        "加强用户评价管理，提升正面口碑"
    ]
    recommendations = general_recs + industry_recs[:3]
    
    competitors = [
        {"name": f"{industry}领先品牌A", "score": random.randint(70, 85), 
         "strengths": ["品牌认知度高", "内容矩阵完善"], "weaknesses": ["价格偏高"]},
        {"name": f"{industry}领先品牌B", "score": random.randint(65, 80),
         "strengths": ["技术创新领先"], "weaknesses": ["用户口碑一般"]},
        {"name": f"{industry}新锐品牌C", "score": random.randint(50, 70),
         "strengths": ["营销活跃"], "weaknesses": ["产品线单一"]}
    ]
    
    result = {
        "brand_name": brand,
        "industry": industry,
        "industry_id": industry_id,
        "ai_mentions": "中等",
        "sentiment": "正面偏中性",
        "geo_score": base_score,
        "visibility_score": random.randint(50, 70),
        "recommendation_score": random.randint(55, 75),
        "sentiment_score": random.randint(60, 80),
        "key_features": ["品质可靠", "服务周到", "性价比高"],
        "diagnosis": diagnosis if is_full else diagnosis[:3],
        "strengths": ["品牌知名度较高", "产品质量稳定", "用户口碑良好"],
        "weaknesses": ["AI搜索优化不足", "内容更新慢", "社交媒体曝光少"],
        "recommendations": recommendations if is_full else recommendations[:3],
        "competitors": competitors if is_full else [],
        "industry_specific_tips": industry_recs[:3] if industry_recs else []
    }
    
    return result

# ==================== API 路由 ====================
@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "好易易GEO API",
        "version": "3.0.0",
        "status": "running",
        "freemium": True,
        "features": ["品牌分析", "订阅监测", "行业基准"],
        "endpoints": {
            "GET /health": "健康检查(简化)",
            "GET /api/health": "健康检查",
            "POST /api/analyze": "品牌分析",
            "GET /api/user/status": "用户状态",
            "GET /api/analysis/history": "分析历史",
            "GET /api/brand/trend": "评分趋势",
            "POST /api/premium/activate": "激活付费",
            "GET /api/industries": "获取行业列表",
            "GET /api/industries/{id}/benchmarks": "获取行业基准",
            "POST /api/monitor": "创建监测订阅",
            "GET /api/monitor": "获取监测列表",
            "DELETE /api/monitor/{id}": "删除监测",
            "GET /api/monitor/{id}/history": "获取监测历史"
        }
    }

@app.get("/health")
async def health_simple():
    """简化健康检查接口 - 用于Docker healthcheck"""
    return {"status": "ok"}

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_service": "DeepSeek",
        "platforms": PLATFORMS,
        "industries_count": len(INDUSTRIES)
    }

@app.get("/api/user/status")
async def get_user_status(device_id: str = Query(default="default")):
    """获取用户状态"""
    status = check_user_status(device_id)
    return UserStatusResponse(**status)

@app.post("/api/premium/activate")
async def activate_premium(device_id: str, token: str = Query(...)):
    """激活付费功能（模拟）"""
    if len(token) < 10:
        raise HTTPException(status_code=400, detail="无效的激活码")
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET is_premium = 1, premium_expires_at = ? WHERE device_id = ?",
            (datetime.now().replace(year=2030).isoformat(), device_id)
        )
        conn.commit()
    
    return {"success": True, "message": "付费功能已激活"}

@app.get("/api/analysis/history")
async def get_history(device_id: str = Query(default="default"), limit: int = Query(default=20)):
    """获取分析历史"""
    history = get_analysis_history(device_id, limit)
    return {"success": True, "data": history}

@app.get("/api/brand/trend")
async def get_trend(brand: str = Query(...), days: int = Query(default=30)):
    """获取品牌评分趋势"""
    trend = get_brand_score_trend(brand, days)
    return {"success": True, "brand": brand, "data": trend}

@app.get("/api/alerts")
async def get_alerts(brand: str = Query(default=None), limit: int = Query(default=10)):
    """获取预警信息"""
    alerts = get_recent_alerts(brand, limit)
    return {"success": True, "data": alerts}

# ==================== 行业相关 API ====================
@app.get("/api/industries")
async def get_industries():
    """获取行业列表"""
    return {
        "success": True,
        "data": INDUSTRIES
    }

@app.get("/api/industries/{industry_id}/benchmarks")
async def get_industry_benchmarks(industry_id: str):
    """获取行业基准数据"""
    # 验证行业ID
    industry = next((ind for ind in INDUSTRIES if ind["id"] == industry_id), None)
    if not industry:
        raise HTTPException(status_code=404, detail="行业不存在")
    
    benchmark = INDUSTRY_BENCHMARKS.get(industry_id, INDUSTRY_BENCHMARKS["tech"])
    
    # 获取该行业的竞品平均分
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT AVG(geo_score) as avg_score, COUNT(*) as count
            FROM analysis_records
            WHERE industry_id = ?
        ''', (industry_id,))
        row = c.fetchone()
        user_avg = row["avg_score"] if row["count"] > 0 else None
    
    return {
        "success": True,
        "industry": industry,
        "benchmark": benchmark,
        "user_average": user_avg
    }

# ==================== 监测订阅 API ====================
@app.post("/api/monitor")
async def create_monitor(request: MonitorCreateRequest, device_id: str = Query(default="default")):
    """创建监测订阅"""
    if not request.brand or len(request.brand.strip()) < 2:
        raise HTTPException(status_code=400, detail="品牌名称不能少于2个字符")
    
    result = create_monitor_subscription(
        device_id, 
        request.brand.strip(), 
        request.industry,
        request.industry_id,
        request.frequency
    )
    
    if result["success"]:
        return {"success": True, "id": result["id"], "message": "监测订阅创建成功"}
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@app.get("/api/monitor")
async def get_monitors(device_id: str = Query(default="default")):
    """获取监测订阅列表"""
    subscriptions = get_monitor_subscriptions(device_id)
    return {"success": True, "data": subscriptions}

@app.get("/api/monitor/{subscription_id}/history")
async def get_monitor_history(subscription_id: int, limit: int = Query(default=30)):
    """获取监测历史数据"""
    history = get_monitor_history(subscription_id, limit)
    return {"success": True, "data": history}

@app.delete("/api/monitor/{subscription_id}")
async def delete_monitor(subscription_id: int, device_id: str = Query(default="default")):
    """删除监测订阅"""
    success = delete_monitor_subscription(subscription_id, device_id)
    if success:
        return {"success": True, "message": "监测订阅已删除"}
    else:
        raise HTTPException(status_code=404, detail="监测订阅不存在或无权删除")

@app.put("/api/monitor/{subscription_id}")
async def update_monitor(subscription_id: int, request: MonitorUpdateRequest, device_id: str = Query(default="default")):
    """更新监测订阅"""
    valid_frequencies = ["daily", "weekly"]
    if request.frequency not in valid_frequencies:
        raise HTTPException(status_code=400, detail=f"无效的监测频率。可选值: {valid_frequencies}")
    
    success = update_monitor_subscription(subscription_id, device_id, request.frequency)
    if success:
        return {"success": True, "message": "监测订阅已更新"}
    else:
        raise HTTPException(status_code=404, detail="监测订阅不存在或无权修改")

# ==================== 核心分析 API ====================
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """核心分析接口"""
    valid_types = ["brand_analysis", "competitor_analysis", "content_strategy"]
    if request.type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的分析类型。可选值: {valid_types}"
        )
    
    if not request.brand or len(request.brand.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="品牌名称不能少于2个字符"
        )
    
    # 检查用户状态
    status = check_user_status(request.device_id)
    if not status["is_premium"] and status["remaining"] <= 0:
        raise HTTPException(
            status_code=429,
            detail="今日免费次数已用完，请明天再来或升级付费版"
        )
    
    try:
        is_full = status["is_premium"]
        
        if request.type == "brand_analysis":
            prompt = get_brand_analysis_prompt(request.brand, request.industry, request.industry_id, is_full)
        elif request.type == "competitor_analysis":
            prompt = get_competitor_analysis_prompt(request.brand, request.industry)
        else:
            prompt = get_content_strategy_prompt(request.brand, request.industry)
        
        # 调用DeepSeek API
        try:
            response_text = await call_deepseek(prompt, SYSTEM_PROMPT)
            analysis_data = safe_json_loads(response_text)
        except Exception as e:
            print(f"API调用失败: {e}，使用模拟数据")
            analysis_data = generate_mock_analysis(request.brand, request.industry, request.industry_id, is_full)
        
        # 添加行业ID
        analysis_data["industry_id"] = request.industry_id
        
        # 保存评分历史
        if request.type == "brand_analysis":
            save_score_history(request.brand, request.industry, request.industry_id, {
                "geo_score": analysis_data.get("geo_score", 0),
                "visibility_score": analysis_data.get("visibility_score", 0),
                "recommendation_score": analysis_data.get("recommendation_score", 0),
                "sentiment_score": analysis_data.get("sentiment_score", 0)
            })
        
        # 保存分析记录
        save_analysis_record(request.device_id, analysis_data, is_full)
        
        # 增加使用次数（免费用户）
        if not status["is_premium"]:
            increment_usage(request.device_id)
        
        # 添加元数据
        analysis_data["_meta"] = {
            "brand": request.brand,
            "industry": request.industry,
            "industry_id": request.industry_id,
            "analysis_type": request.type,
            "analyzed_at": datetime.now().isoformat(),
            "ai_model": DEEPSEEK_MODEL,
            "is_full_report": is_full
        }
        
        return AnalyzeResponse(
            success=True,
            data=analysis_data,
            ai_used="DeepSeek",
            platforms_analyzed=PLATFORMS,
            is_full_report=is_full
        )
        
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            error=f"分析失败: {str(e)}",
            platforms_analyzed=PLATFORMS
        )

# ==================== 启动入口 ====================
if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 好易易GEO API 服务...")
    print(f"📍 服务地址: http://localhost:5000")
    print(f"📡 API端点: http://localhost:5000/api/analyze")
    print(f"🔧 文档地址: http://localhost:5000/docs")
    print(f"💾 数据库: {DATABASE_PATH}")
    print(f"🏢 支持行业: {len(INDUSTRIES)}个")
    print()
    uvicorn.run(app, host="0.0.0.0", port=5000)
