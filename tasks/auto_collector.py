#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好易易GEO - 自动化数据采集脚本
每天凌晨自动采集品牌数据，记录历史评分，评分变化时发送预警
"""

import os
import sys
import json
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-8914498a0fff48e793153ab852a38ae5")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "geo.db")

# 日志配置
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f'collector_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 品牌监控列表 ====================
# 可以从数据库读取，也可以配置文件定义
BRAND_WATCHLIST = [
    {"brand": "武汉万象城", "industry": "商业地产"},
    {"brand": "武汉国际广场", "industry": "商业地产"},
    {"brand": "武商集团", "industry": "商业零售"},
]

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
        
        # 监控品牌表
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT UNIQUE NOT NULL,
                industry TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 采集任务日志表
        c.execute('''
            CREATE TABLE IF NOT EXISTS collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                brands_processed INTEGER DEFAULT 0,
                brands_success INTEGER DEFAULT 0,
                brands_failed INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def get_watchlist_from_db() -> List[Dict[str, str]]:
    """从数据库获取监控列表"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT brand, industry FROM watchlist WHERE is_active = 1")
        return [dict(row) for row in c.fetchall()]

def add_to_watchlist(brand: str, industry: str = "通用"):
    """添加品牌到监控列表"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO watchlist (brand, industry) VALUES (?, ?)",
            (brand, industry)
        )
        conn.commit()

def remove_from_watchlist(brand: str):
    """从监控列表移除品牌"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE watchlist SET is_active = 0 WHERE brand = ?", (brand,))
        conn.commit()

def get_last_score(brand: str) -> Optional[Dict[str, Any]]:
    """获取品牌最近一次评分"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM score_history 
            WHERE brand = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (brand,))
        row = c.fetchone()
        return dict(row) if row else None

def save_score_history(brand: str, industry: str, scores: Dict[str, int]) -> Optional[int]:
    """保存评分历史，返回分数变化值"""
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 获取上次评分
        last_score = get_last_score(brand)
        old_score = last_score["geo_score"] if last_score else None
        
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
        
        # 检查是否需要创建预警
        score_change = None
        if old_score is not None:
            new_score = scores.get("geo_score", 0)
            score_change = new_score - old_score
            
            if abs(score_change) >= 5:  # 变化超过5分
                alert_type = "rise" if score_change > 0 else "drop"
                c.execute('''
                    INSERT INTO alerts (brand, alert_type, message, old_score, new_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    brand, alert_type,
                    f"GEO评分{'上升' if score_change > 0 else '下降'}了{abs(score_change)}分",
                    old_score, new_score
                ))
                conn.commit()
                
                logger.info(f"📢 预警: {brand} 评分变化 {old_score} -> {new_score} ({score_change:+d})")
        
        return score_change

def log_collection_task(task_type: str, status: str, **kwargs):
    """记录采集任务日志"""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO collection_logs 
            (task_type, status, brands_processed, brands_success, brands_failed, 
             error_message, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_type,
            status,
            kwargs.get("processed", 0),
            kwargs.get("success", 0),
            kwargs.get("failed", 0),
            kwargs.get("error", None),
            kwargs.get("started_at", None),
            datetime.now().isoformat()
        ))
        conn.commit()

# ==================== DeepSeek API 调用 ====================
async def call_deepseek(prompt: str, system_prompt: Optional[str] = None) -> str:
    """调用DeepSeek API"""
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
        "max_tokens": 2000
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

SYSTEM_PROMPT = """你是一位专业的AI搜索优化分析师。请基于合理推断给出分析结果。"""

def get_analysis_prompt(brand: str, industry: str) -> str:
    """获取分析提示词"""
    return f"""请对品牌「{brand}」在{industry}行业进行AI搜索健康度快速评估。

请以JSON格式返回：
- geo_score: GEO综合评分 (0-100)
- visibility_score: 可见度评分 (0-100)
- recommendation_score: 推荐度评分 (0-100)
- sentiment_score: 情感倾向评分 (0-100)

只输出JSON。"""

def parse_json_response(text: str) -> Dict[str, Any]:
    """解析JSON响应"""
    import re
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {"geo_score": 0}

async def analyze_brand(brand: str, industry: str) -> Optional[Dict[str, int]]:
    """分析单个品牌"""
    try:
        prompt = get_analysis_prompt(brand, industry)
        response_text = await call_deepseek(prompt, SYSTEM_PROMPT)
        data = parse_json_response(response_text)
        
        return {
            "geo_score": data.get("geo_score", 0),
            "visibility_score": data.get("visibility_score", 0),
            "recommendation_score": data.get("recommendation_score", 0),
            "sentiment_score": data.get("sentiment_score", 0)
        }
    except Exception as e:
        logger.error(f"分析失败 {brand}: {e}")
        return None

# ==================== 预警通知 ====================
def generate_alert_message(brand: str, old_score: int, new_score: int, change: int) -> str:
    """生成预警消息"""
    direction = "📈 上升" if change > 0 else "📉 下降"
    return f"""{direction} 品牌评分变化提醒

品牌: {brand}
原评分: {old_score}
新评分: {new_score}
变化: {change:+d}分

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请登录GEO智眼查看详情。
"""

async def send_alert_notification(brand: str, old_score: int, new_score: int, change: int):
    """发送预警通知（可以扩展为飞书/邮件等）"""
    message = generate_alert_message(brand, old_score, new_score, change)
    
    # 目前仅记录日志，可扩展为：
    # - 飞书webhook通知
    # - 邮件通知
    # - 短信通知
    
    logger.info(f"📬 预警通知:\n{message}")
    
    # TODO: 集成飞书webhook
    # await send_feishu_notification(message)
    
    return message

# ==================== 主采集任务 ====================
async def run_collection_task():
    """执行自动化采集任务"""
    logger.info("=" * 50)
    logger.info(f"🕐 开始执行数据采集任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    task_start = datetime.now()
    processed = 0
    success = 0
    failed = 0
    alerts = []
    
    try:
        # 获取监控列表
        watchlist = get_watchlist_from_db()
        if not watchlist:
            logger.warning("⚠️ 监控列表为空，使用默认列表")
            watchlist = BRAND_WATCHLIST
        
        logger.info(f"📋 待采集品牌: {len(watchlist)} 个")
        
        for item in watchlist:
            brand = item["brand"]
            industry = item.get("industry", "通用")
            processed += 1
            
            logger.info(f"\n🔍 正在分析: {brand} ({industry})")
            
            # 获取上次评分
            last_score = get_last_score(brand)
            if last_score:
                logger.info(f"   上次评分: {last_score['geo_score']}")
            
            # 执行分析
            scores = await analyze_brand(brand, industry)
            
            if scores:
                # 保存评分
                change = save_score_history(brand, industry, scores)
                
                logger.info(f"   新评分: {scores['geo_score']}")
                if change is not None:
                    logger.info(f"   变化: {change:+d}")
                    
                    # 发送预警
                    if abs(change) >= 5:
                        await send_alert_notification(
                            brand,
                            last_score['geo_score'] if last_score else 0,
                            scores['geo_score'],
                            change
                        )
                        alerts.append({
                            "brand": brand,
                            "change": change,
                            "new_score": scores['geo_score']
                        })
                
                success += 1
            else:
                logger.error(f"   ❌ 分析失败")
                failed += 1
            
            # 避免API限流
            await asyncio.sleep(2)
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 采集任务完成")
        logger.info(f"   总计: {processed}")
        logger.info(f"   成功: {success}")
        logger.info(f"   失败: {failed}")
        if alerts:
            logger.info(f"   触发预警: {len(alerts)} 个")
        logger.info(f"   耗时: {(datetime.now() - task_start).total_seconds():.1f}秒")
        logger.info("=" * 50)
        
        # 记录任务日志
        log_collection_task(
            "daily_collection",
            "completed",
            processed=processed,
            success=success,
            failed=failed,
            started_at=task_start.isoformat()
        )
        
        return {
            "status": "completed",
            "processed": processed,
            "success": success,
            "failed": failed,
            "alerts": alerts,
            "duration": (datetime.now() - task_start).total_seconds()
        }
        
    except Exception as e:
        logger.error(f"❌ 采集任务异常: {e}")
        
        log_collection_task(
            "daily_collection",
            "failed",
            processed=processed,
            success=success,
            failed=failed,
            error=str(e),
            started_at=task_start.isoformat()
        )
        
        return {
            "status": "failed",
            "error": str(e)
        }

# ==================== 定时任务入口 ====================
def run_as_scheduled_task():
    """作为定时任务运行（可配合cron或系统调度器）"""
    asyncio.run(run_collection_task())

# ==================== 命令行接口 ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GEO数据自动化采集脚本")
    parser.add_argument("--brand", "-b", type=str, help="单独采集指定品牌")
    parser.add_argument("--add", "-a", type=str, nargs=2, metavar=("BRAND", "INDUSTRY"), 
                        help="添加品牌到监控列表")
    parser.add_argument("--remove", "-r", type=str, help="从监控列表移除品牌")
    parser.add_argument("--list", "-l", action="store_true", help="显示监控列表")
    parser.add_argument("--alerts", action="store_true", help="显示最近预警")
    
    args = parser.parse_args()
    
    # 初始化数据库
    init_database()
    
    if args.add:
        brand, industry = args.add
        add_to_watchlist(brand, industry)
        print(f"✅ 已添加 {brand} 到监控列表")
    
    elif args.remove:
        remove_from_watchlist(args.remove)
        print(f"✅ 已从监控列表移除 {args.remove}")
    
    elif args.list:
        watchlist = get_watchlist_from_db()
        print(f"\n📋 当前监控列表 ({len(watchlist)} 个品牌):")
        for i, item in enumerate(watchlist, 1):
            last = get_last_score(item["brand"])
            score_str = f" (最近: {last['geo_score']})" if last else ""
            print(f"  {i}. {item['brand']} - {item.get('industry', '通用')}{score_str}")
    
    elif args.alerts:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 20")
            alerts = [dict(row) for row in c.fetchall()]
        
        print(f"\n📢 最近预警 ({len(alerts)} 条):")
        for alert in alerts:
            print(f"  [{alert['created_at']}] {alert['brand']}: {alert['message']}")
    
    elif args.brand:
        # 单独采集指定品牌
        asyncio.run(run_collection_task())
    
    else:
        # 默认执行采集任务
        asyncio.run(run_collection_task())
