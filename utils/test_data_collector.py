"""
好易易GEO - 数据采集模块测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_collector import (
    collect_from_platform,
    collect_from_all_platforms,
    quick_search,
    PLATFORMS
)


def test_single_platform():
    """测试单个平台采集"""
    print("=" * 60)
    print("测试: 单个平台采集")
    print("=" * 60)
    
    keyword = "咖啡厅推荐"
    platform = "DeepSeek"
    
    result = collect_from_platform(platform, keyword, use_mock=True)
    
    print(f"\n平台: {result['platform']}")
    print(f"成功: {result['success']}")
    print(f"结果数: {result['count']}")
    print(f"使用模拟数据: {result.get('is_mock', False)}")
    
    if result['results']:
        print("\n示例结果:")
        for i, r in enumerate(result['results'][:2], 1):
            print(f"  [{i}] {r['title']}")
            print(f"      {r['content'][:50]}...")
    
    return result


def test_all_platforms():
    """测试全平台采集"""
    print("\n" + "=" * 60)
    print("测试: 全平台采集")
    print("=" * 60)
    
    keyword = "北京周末好去处"
    
    result = collect_from_all_platforms(keyword, use_mock=True)
    
    print(f"\n关键词: {result['keyword']}")
    print(f"总结果数: {result['total_count']}")
    print(f"\n采集摘要:")
    print(f"  - 总平台数: {result['summary']['total_platforms']}")
    print(f"  - 成功: {result['summary']['success_count']}")
    print(f"  - 失败: {result['summary']['failed_count']}")
    print(f"  - 消息: {result['summary']['message']}")
    
    print("\n各平台结果:")
    for platform, data in result['platforms'].items():
        status = "✓" if data['success'] else "✗"
        mock_tag = " [模拟]" if data.get('is_mock') else ""
        print(f"  {status} {platform}: {data['count']} 条结果{mock_tag}")
    
    return result


def test_quick_search():
    """测试快速搜索"""
    print("\n" + "=" * 60)
    print("测试: 快速搜索")
    print("=" * 60)
    
    result = quick_search("附近火锅店")
    
    print(f"\n总结果数: {result['total_count']}")
    print(f"成功平台数: {len(result['summary']['success_platforms'])}")
    
    return result


def show_platform_info():
    """显示平台信息"""
    print("\n" + "=" * 60)
    print("支持的平台列表")
    print("=" * 60)
    
    for name, info in PLATFORMS.items():
        has_api = "✓ 有API" if info.get("has_api") else "✗ 无API"
        print(f"\n{name} ({info['url']})")
        print(f"  API状态: {has_api}")
        print(f"  说明: {info['note']}")


def main():
    print("好易易GEO - 数据采集模块测试")
    print("=" * 60)
    
    # 显示平台信息
    show_platform_info()
    
    # 测试单个平台
    test_single_platform()
    
    # 测试全平台
    test_all_platforms()
    
    # 测试快速搜索
    test_quick_search()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
