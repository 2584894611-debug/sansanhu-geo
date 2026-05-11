#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好易易GEO API 测试脚本
用于验证后端服务是否正常工作
"""

import requests
import json
import sys

API_BASE = "http://localhost:5000"

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        resp = requests.get(f"{API_BASE}/api/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 服务正常运行")
            print(f"   - 状态: {data['status']}")
            print(f"   - AI服务: {data['ai_service']}")
            print(f"   - 分析平台: {', '.join(data['platforms'])}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保服务已启动")
        print("💡 提示: 运行 ./start.sh 启动服务")
        return False

def test_brand_analysis():
    """测试品牌分析接口"""
    print("\n🔍 测试品牌分析接口...")
    payload = {
        "type": "brand_analysis",
        "brand": "武汉万象城",
        "industry": "本地生活"
    }
    try:
        resp = requests.post(
            f"{API_BASE}/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        data = resp.json()
        if data.get("success"):
            print(f"✅ 品牌分析成功")
            print(f"   - 使用AI: {data['ai_used']}")
            print(f"   - 分析平台: {len(data['platforms_analyzed'])}个")
            return True
        else:
            print(f"❌ 分析失败: {data.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 好易易GEO API 测试")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health():
        sys.exit(1)
    
    # 测试品牌分析
    test_brand_analysis()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
