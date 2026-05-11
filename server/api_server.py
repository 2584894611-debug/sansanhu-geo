#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好易易GEO - AI搜索分析后端API服务 (扩展版)
支持Freemium模式、数据库存储、用户管理和自动化采集
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
                frequency TEXT DEFAULT 'daily',
                is_active INTEGER DEFAULT 1,
                last_check_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, brand)
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
            (user_id, brand, industry, geo_score, visibility_score, recommendation_score, 
             sentiment_score, diagnosis_data, competitor_data, recommendations, is_full_report)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user["id"],
            analysis_data.get("brand_name", ""),
            analysis_data.get("industry", ""),
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

def save_score_history(brand: str, industry: str, scores: Dict[str, int]):
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
        
        # 保存新评分
        c.execute('''
            INSERT INTO score_history (brand, industry, geo_score, visibility_score, 
                                       recommendation_score, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            brand, industry,
            scores.get("geo_score", 0),
            scores.get("visibility_score", 0),
            scores.get("recommendation_score", 0),
            scores.get("sentiment_score", 0)
        ))
        conn.commit()
        
        # 检查是否需要预警
        if old_score is not None:
            diff = scores.get("geo_score", 0) - old_score
            if abs(diff) >= 5:  # 变化超过5分
                alert_type = "rise" if diff > 0 else "drop"
                c.execute('''
                    INSERT INTO alerts (brand, alert_type, message, old_score, new_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    brand, alert_type,
                    f"GEO评分{'上升' if diff > 0 else '下降'}了{abs(diff)}分",
                    old_score, scores.get("geo_score", 0)
                ))
                conn.commit()
        
        return old_score

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
        c.execute('''
            SELECT * FROM score_history 
            WHERE brand = ? AND created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at ASC
        ''', (brand, days))
        
        return [dict(row) for row in c.fetchall()]

def get_recent_alerts(brand: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取最近预警"""
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
def create_monitor_subscription(device_id: str, brand: str, frequency: str = 'daily') -> Dict[str, Any]:
    """创建监测订阅"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 检查是否已存在
        c.execute(
            "SELECT * FROM monitor_subscriptions WHERE user_id = ? AND brand = ?",
            (user["id"], brand)
        )
        existing = c.fetchone()
        
        if existing:
            # 更新现有订阅
            c.execute('''
                UPDATE monitor_subscriptions 
                SET frequency = ?, is_active = 1, last_check_at = ?
                WHERE id = ?
            ''', (frequency, datetime.now().isoformat(), existing["id"]))
            conn.commit()
            return dict(existing)
        
        # 创建新订阅
        c.execute('''
            INSERT INTO monitor_subscriptions (user_id, brand, frequency, is_active, last_check_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (user["id"], brand, frequency, datetime.now().isoformat()))
        conn.commit()
        
        return {
            "id": c.lastrowid,
            "brand": brand,
            "frequency": frequency,
            "is_active": 1
        }

def get_monitor_subscriptions(device_id: str) -> List[Dict[str, Any]]:
    """获取用户的监测订阅列表"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 获取订阅列表
        c.execute('''
            SELECT ms.*, 
                   (SELECT MAX(geo_score) FROM score_history WHERE brand = ms.brand) as current_score,
                   (SELECT COUNT(*) FROM score_history WHERE brand = ms.brand) as data_points
            FROM monitor_subscriptions ms
            WHERE ms.user_id = ? AND ms.is_active = 1
            ORDER BY ms.created_at DESC
        ''', (user["id"],))
        
        subscriptions = [dict(row) for row in c.fetchall()]
        
        # 计算每个订阅的变化趋势
        for sub in subscriptions:
            # 获取最新两个评分
            c.execute('''
                SELECT geo_score FROM score_history 
                WHERE brand = ? 
                ORDER BY created_at DESC LIMIT 2
            ''', (sub["brand"],))
            scores = [row["geo_score"] for row in c.fetchall()]
            
            if len(scores) >= 2:
                sub["trend"] = scores[0] - scores[1]
                sub["change_percent"] = round((scores[0] - scores[1]) / max(scores[1], 1) * 100, 1) if scores[1] > 0 else 0
            else:
                sub["trend"] = 0
                sub["change_percent"] = 0
        
        return subscriptions

def delete_monitor_subscription(device_id: str, subscription_id: int) -> bool:
    """删除监测订阅"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE monitor_subscriptions 
            SET is_active = 0 
            WHERE id = ? AND user_id = ?
        ''', (subscription_id, user["id"]))
        conn.commit()
        return c.rowcount > 0

def get_monitor_history(device_id: str, subscription_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """获取监测历史数据"""
    user = get_or_create_user(device_id)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 获取订阅信息
        c.execute('''
            SELECT brand FROM monitor_subscriptions 
            WHERE id = ? AND user_id = ?
        ''', (subscription_id, user["id"]))
        subscription = c.fetchone()
        
        if not subscription:
            return []
        
        # 获取历史数据
        c.execute('''
            SELECT * FROM score_history 
            WHERE brand = ? AND created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at ASC
        ''', (subscription["brand"], days))
        
        return [dict(row) for row in c.fetchall()]

# ==================== 行业数据 ====================
INDUSTRIES_DATA = {
    "knowledge_gap": {
        "name": "🧠 知识盲区品类",
        "description": "用户认知有限，需要建立品牌认知",
        "industries": [
            {"id": "consumer_electronics", "name": "消费电子"},
            {"id": "baby_products", "name": "母婴用品"},
            {"id": "fitness", "name": "运动健身"}
        ],
        "benchmark_geo_score": 45,
        "key_factors": ["品牌权威性", "专业内容覆盖", "问答内容布局"]
    },
    "high_value_low_freq": {
        "name": "💰 低频高客单",
        "description": "决策周期长，需要建立信任和专业形象",
        "industries": [
            {"id": "real_estate", "name": "商业地产"},
            {"id": "tourism", "name": "文旅"},
            {"id": "renovation", "name": "装修建材"},
            {"id": "wedding", "name": "婚纱摄影"},
            {"id": "postpartum", "name": "月子中心"}
        ],
        "benchmark_geo_score": 50,
        "key_factors": ["口碑管理", "案例展示", "专业背书", "用户评价"]
    },
    "innovation_niche": {
        "name": "🔍 长尾痛点微创新",
        "description": "满足细分需求，需要突出差异化优势",
        "industries": [
            {"id": "smart_hardware", "name": "智能硬件"},
            {"id": "personal_care", "name": "个护创新"},
            {"id": "home_appliances", "name": "小家电"}
        ],
        "benchmark_geo_score": 40,
        "key_factors": ["产品差异化", "使用场景内容", "用户评测"]
    },
    "to_b_business": {
        "name": "🏢 To B业务",
        "description": "面向企业客户，需要建立专业权威形象",
        "industries": [
            {"id": "saas", "name": "SaaS软件"},
            {"id": "industrial", "name": "工业设备"},
            {"id": "enterprise_service", "name": "企业服务"}
        ],
        "benchmark_geo_score": 55,
        "key_factors": ["行业解决方案", "客户案例", "技术文档", "专业资质"]
    }
}

def get_all_industries() -> List[Dict[str, Any]]:
    """获取所有行业分类"""
    result = []
    for category_id, category_data in INDUSTRIES_DATA.items():
        for industry in category_data["industries"]:
            result.append({
                "category_id": category_id,
                "category_name": category_data["name"],
                "category_description": category_data["description"],
                "id": industry["id"],
                "name": industry["name"],
                "benchmark_geo_score": category_data["benchmark_geo_score"],
                "key_factors": category_data["key_factors"]
            })
    return result

def get_industry_by_id(industry_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取行业详情"""
    for category_id, category_data in INDUSTRIES_DATA.items():
        for industry in category_data["industries"]:
            if industry["id"] == industry_id:
                return {
                    "category_id": category_id,
                    "category_name": category_data["name"],
                    "category_description": category_data["description"],
                    "id": industry["id"],
                    "name": industry["name"],
                    "benchmark_geo_score": category_data["benchmark_geo_score"],
                    "key_factors": category_data["key_factors"]
                }
    return None

def get_industry_benchmarks(industry_id: str) -> Dict[str, Any]:
    """获取行业基准数据"""
    industry = get_industry_by_id(industry_id)
    if not industry:
        return {}
    
    # 生成行业基准数据
    benchmark = {
        "industry": industry,
        "benchmarks": {
            "geo_score": {
                "excellent": industry["benchmark_geo_score"] + 20,
                "good": industry["benchmark_geo_score"] + 10,
                "average": industry["benchmark_geo_score"],
                "poor": industry["benchmark_geo_score"] - 15
            },
            "visibility": {
                "excellent": 85,
                "good": 70,
                "average": 55,
                "poor": 40
            },
            "recommendation": {
                "excellent": 80,
                "good": 65,
                "average": 50,
                "poor": 35
            },
            "sentiment": {
                "excellent": 85,
                "good": 70,
                "average": 60,
                "poor": 45
            }
        },
        "recommendations_by_level": {
            "excellent": [
                "继续保持内容输出节奏",
                "关注新兴AI搜索平台动态",
                "深化行业垂直内容布局"
            ],
            "good": [
                "加强竞品对比内容建设",
                "提升问答类内容覆盖",
                "优化品牌故事叙事结构"
            ],
            "average": [
                "增加专业权威内容发布频率",
                "建立品牌FAQ知识库",
                "布局长尾关键词内容"
            ],
            "poor": [
                "优先解决基础品牌信息覆盖",
                "创建品牌百科类内容",
                "加强用户评价管理"
            ]
        }
    }
    
    return benchmark

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title="好易易GEO API",
    description="AI搜索优化分析后端服务 - Freemium版本",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_database()

# ==================== 数据模型 ====================
class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    type: str = Field(..., description="分析类型: brand_analysis/competitor_analysis/content_strategy")
    brand: str = Field(..., description="品牌/公司名称")
    industry: str = Field(default="通用", description="行业类型")
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
def get_brand_analysis_prompt(brand: str, industry: str, is_full: bool = True) -> str:
    """品牌分析提示词"""
    diagnosis_limit = "全部" if is_full else "前3个"
    return f"""请对品牌「{brand}」在{industry}行业进行AI搜索健康度分析。

分析维度：
1. 品牌在AI搜索引擎中的可见度 (0-100)
2. 用户讨论情绪倾向（正面/中性/负面）(0-100)
3. 品牌核心特征和用户认知
4. 问题诊断（{diagnosis_limit}）
5. GEO优化建议

请以JSON格式返回分析结果，包含以下字段：
- brand_name: 品牌名称
- industry: 行业
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

def generate_mock_analysis(brand: str, industry: str, is_full: bool = True) -> Dict[str, Any]:
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
    
    recommendations = [
        "增加品牌在权威媒体和行业网站的曝光",
        "创建FAQ类型内容，覆盖用户常见问题",
        "优化品牌故事的叙事结构，便于AI理解",
        "建立内容更新机制，保持信息时效性",
        "加强用户评价管理，提升正面口碑",
        "布局长尾关键词，覆盖更多搜索场景",
        "定期发布行业洞察内容，建立专业形象",
        "优化官网内容结构，提升AI抓取效率"
    ]
    
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
        "competitors": competitors if is_full else []
    }
    
    return result

# ==================== API 路由 ====================
@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "好易易GEO API",
        "version": "2.0.0",
        "status": "running",
        "freemium": True,
        "endpoints": {
            "GET /health": "健康检查(简化)",
            "GET /api/health": "健康检查",
            "POST /api/analyze": "品牌分析",
            "GET /api/user/status": "用户状态",
            "GET /api/analysis/history": "分析历史",
            "GET /api/brand/trend": "评分趋势",
            "POST /api/premium/activate": "激活付费"
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
        "platforms": PLATFORMS
    }

@app.get("/api/user/status")
async def get_user_status(device_id: str = Query(default="default")):
    """获取用户状态"""
    status = check_user_status(device_id)
    return UserStatusResponse(**status)

@app.post("/api/premium/activate")
async def activate_premium(device_id: str, token: str = Query(...)):
    """激活付费功能（模拟）"""
    # 简单的token验证
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

# ==================== 监测订阅 API ====================
class MonitorCreateRequest(BaseModel):
    """创建监测订阅请求"""
    brand: str = Field(..., description="品牌名称")
    frequency: str = Field(default="daily", description="监测频率: daily/weekly")

@app.post("/api/monitor")
async def create_monitor(
    request: MonitorCreateRequest,
    device_id: str = Query(default="default")
):
    """创建监测订阅"""
    if not request.brand or len(request.brand.strip()) < 2:
        raise HTTPException(status_code=400, detail="品牌名称不能少于2个字符")
    
    if request.frequency not in ["daily", "weekly"]:
        raise HTTPException(status_code=400, detail="无效的监测频率")
    
    subscription = create_monitor_subscription(device_id, request.brand.strip(), request.frequency)
    return {"success": True, "data": subscription}

@app.get("/api/monitor")
async def get_monitors(device_id: str = Query(default="default")):
    """获取监测订阅列表"""
    subscriptions = get_monitor_subscriptions(device_id)
    return {"success": True, "data": subscriptions}

@app.get("/api/monitor/{subscription_id}/history")
async def get_monitor_history_api(
    subscription_id: int,
    days: int = Query(default=30),
    device_id: str = Query(default="default")
):
    """获取监测历史数据"""
    history = get_monitor_history(device_id, subscription_id, days)
    return {"success": True, "data": history}

@app.delete("/api/monitor/{subscription_id}")
async def delete_monitor(
    subscription_id: int,
    device_id: str = Query(default="default")
):
    """删除监测订阅"""
    success = delete_monitor_subscription(device_id, subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="监测订阅不存在")
    return {"success": True, "message": "监测订阅已删除"}

# ==================== 行业 API ====================
@app.get("/api/industries")
async def get_industries():
    """获取所有行业列表"""
    industries = get_all_industries()
    return {"success": True, "data": industries}

@app.get("/api/industries/benchmarks/{industry_id}")
async def get_industry_benchmarks_api(industry_id: str):
    """获取行业基准数据"""
    benchmark = get_industry_benchmarks(industry_id)
    if not benchmark:
        raise HTTPException(status_code=404, detail="行业不存在")
    return {"success": True, "data": benchmark}

# ==================== 分析 API ====================
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
        # 根据分析类型选择提示词
        is_full = status["is_premium"]
        
        if request.type == "brand_analysis":
            prompt = get_brand_analysis_prompt(request.brand, request.industry, is_full)
        elif request.type == "competitor_analysis":
            prompt = get_competitor_analysis_prompt(request.brand, request.industry)
        else:
            prompt = get_content_strategy_prompt(request.brand, request.industry)
        
        # 调用DeepSeek API
        try:
            response_text = await call_deepseek(prompt, SYSTEM_PROMPT)
            analysis_data = safe_json_loads(response_text)
        except Exception as e:
            # API调用失败时使用模拟数据
            print(f"API调用失败: {e}，使用模拟数据")
            analysis_data = generate_mock_analysis(request.brand, request.industry, is_full)
        
        # 保存评分历史
        if request.type == "brand_analysis":
            save_score_history(request.brand, request.industry, {
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
    print()
    uvicorn.run(app, host="0.0.0.0", port=5000)
