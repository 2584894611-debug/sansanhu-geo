# -*- coding: utf-8 -*-
"""
好易易GEO - Prompt采集模块测试

测试用例：
1. 基础Prompt构建测试
2. 场景Prompt扩展测试
3. 竞品对比Prompt测试
4. 频率验证测试
5. 端到端采集测试
"""

import unittest
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_collector import (
    build_seed_prompts,
    build_scene_prompts,
    parse_brand_city,
    filter_by_frequency,
    group_by_type,
    count_by_category,
    collect_ai_prompts,
    quick_collect,
    get_prompt_templates,
    AIPrompt,
    PromptType,
    Frequency,
    DEFAULT_SCENE_WORDS,
    SCENE_CATEGORIES
)


class TestPromptCollector(unittest.TestCase):
    """Prompt采集模块测试"""
    
    def setUp(self):
        """测试初始化"""
        self.brand_name = "武汉万象城"
        self.competitors = ["武汉恒隆广场", "武商MALL", "武汉国际广场"]
        self.city = "武汉"
    
    def test_parse_brand_city(self):
        """测试品牌名城市解析"""
        # 测试武汉
        city, brand = parse_brand_city("武汉万象城")
        self.assertEqual(city, "武汉")
        self.assertEqual(brand, "万象城")
        
        # 测试上海
        city, brand = parse_brand_city("上海恒隆广场")
        self.assertEqual(city, "上海")
        self.assertEqual(brand, "恒隆广场")
        
        # 测试无城市
        city, brand = parse_brand_city("万象城")
        self.assertEqual(city, "")
        self.assertEqual(brand, "万象城")
        
        print("✓ 城市解析测试通过")
    
    def test_build_seed_prompts(self):
        """测试种子Prompt构建"""
        prompts = build_seed_prompts(self.brand_name, self.competitors, self.city)
        
        # 验证返回类型
        self.assertIsInstance(prompts, list)
        self.assertTrue(len(prompts) > 0)
        
        # 验证包含AIPrompt对象
        self.assertTrue(all(isinstance(p, AIPrompt) for p in prompts))
        
        # 验证包含各种类型
        types = {p.prompt_type for p in prompts}
        self.assertIn(PromptType.BRAND_CONSULT, types)
        self.assertIn(PromptType.SCENE_RECOMMEND, types)
        self.assertIn(PromptType.COMPARE_ANALYSIS, types)
        self.assertIn(PromptType.REVIEW_GUIDE, types)
        
        # 验证竞品对比Prompt数量
        compare_prompts = [p for p in prompts if p.prompt_type == PromptType.COMPARE_ANALYSIS]
        self.assertGreaterEqual(len(compare_prompts), len(self.competitors) * 3)
        
        # 验证品牌名正确替换
        brand_prompts = [p for p in prompts if self.brand_name in p.question]
        self.assertGreater(len(brand_prompts), 0)
        
        print(f"✓ 种子Prompt构建测试通过，共生成 {len(prompts)} 个Prompt")
        for p in prompts[:5]:
            print(f"  - [{p.prompt_type.value}] {p.question}")
    
    def test_build_scene_prompts(self):
        """测试场景Prompt构建"""
        prompts = build_scene_prompts(self.brand_name, self.city)
        
        self.assertIsInstance(prompts, list)
        self.assertTrue(len(prompts) > 0)
        
        # 验证场景词使用
        scene_words_used = set()
        for p in prompts:
            for scene in DEFAULT_SCENE_WORDS:
                if scene in p.question:
                    scene_words_used.add(scene)
        
        self.assertGreater(len(scene_words_used), 0)
        
        print(f"✓ 场景Prompt构建测试通过，共生成 {len(prompts)} 个场景Prompt")
    
    def test_custom_scenes(self):
        """测试自定义场景"""
        custom_scenes = {
            "约会场景": ["约会", "情侣"],
            "遛娃场景": ["遛娃", "亲子"]
        }
        
        prompts = build_scene_prompts(
            self.brand_name, 
            self.city,
            custom_scenes=custom_scenes
        )
        
        # 验证自定义场景被使用
        custom_prompts = [p for p in prompts if "场景分类" in p.source_hint]
        self.assertGreater(len(custom_prompts), 0)
        
        print(f"✓ 自定义场景测试通过，生成 {len(custom_prompts)} 个自定义场景Prompt")
    
    def test_count_by_category(self):
        """测试分类统计"""
        prompts = build_seed_prompts(self.brand_name, self.competitors, self.city)
        counts = count_by_category(prompts)
        
        self.assertIsInstance(counts, dict)
        self.assertIn("品牌咨询", counts)
        self.assertIn("场景推荐", counts)
        self.assertIn("对比分析", counts)
        self.assertIn("评测攻略", counts)
        
        # 验证总数
        total = sum(counts.values())
        self.assertEqual(total, len(prompts))
        
        print(f"✓ 分类统计测试通过: {counts}")
    
    def test_group_by_type(self):
        """测试类型分组"""
        prompts = build_seed_prompts(self.brand_name, self.competitors, self.city)
        grouped = group_by_type(prompts)
        
        self.assertIsInstance(grouped, dict)
        
        for type_name, items in grouped.items():
            self.assertIsInstance(items, list)
            for item in items:
                self.assertEqual(item["type"], type_name)
        
        print(f"✓ 类型分组测试通过，共 {len(grouped)} 个分组")
    
    def test_collect_ai_prompts_full(self):
        """测试完整采集流程"""
        result = collect_ai_prompts(
            brand_name=self.brand_name,
            competitor_names=self.competitors,
            city=self.city,
            industry="商业地产",
            max_prompts=50,
            include_scene_prompts=True
        )
        
        # 验证返回结构
        self.assertIn("prompts", result)
        self.assertIn("categories", result)
        self.assertIn("metadata", result)
        
        # 验证metadata
        metadata = result["metadata"]
        self.assertEqual(metadata["brand_name"], self.brand_name)
        self.assertEqual(metadata["city"], self.city)
        self.assertEqual(metadata["industry"], "商业地产")
        
        # 验证Prompt数量不超过限制
        self.assertLessEqual(len(result["prompts"]), 50)
        
        # 验证Prompt格式
        for prompt in result["prompts"]:
            self.assertIn("question", prompt)
            self.assertIn("type", prompt)
            self.assertIn("frequency", prompt)
        
        print(f"✓ 完整采集测试通过")
        print(f"  - 生成 {len(result['prompts'])} 个Prompt")
        print(f"  - 分类统计: {result['categories']}")
    
    def test_quick_collect(self):
        """测试快速采集"""
        result = quick_collect(
            brand_name="武汉万象城",
            competitors=["武汉恒隆广场"]
        )
        
        self.assertIn("prompts", result)
        self.assertIn("categories", result)
        
        print(f"✓ 快速采集测试通过")
    
    def test_prompt_templates(self):
        """测试Prompt模板库"""
        templates = get_prompt_templates()
        
        self.assertIsInstance(templates, dict)
        self.assertIn("品牌咨询", templates)
        self.assertIn("场景推荐", templates)
        self.assertIn("对比分析", templates)
        self.assertIn("评测攻略", templates)
        
        for type_name, template_list in templates.items():
            self.assertIsInstance(template_list, list)
            self.assertTrue(len(template_list) > 0)
            for t in template_list:
                # 确保模板包含至少一个占位符
                has_placeholder = ("{brand}" in t or "{city}" in t or 
                                   "{竞品}" in t or "{场景}" in t)
                self.assertTrue(has_placeholder, f"模板缺少占位符: {t}")
        
        print(f"✓ Prompt模板库测试通过，共 {sum(len(v) for v in templates.values())} 个模板")
    
    def test_frequency_filter(self):
        """测试频率过滤"""
        prompts = build_seed_prompts(self.brand_name, self.competitors, self.city)
        
        # 设置一些测试频率
        prompts[0].frequency = Frequency.HIGH
        prompts[1].frequency = Frequency.MEDIUM
        prompts[2].frequency = Frequency.LOW
        
        # 过滤高频
        high_freq = filter_by_frequency(prompts, Frequency.HIGH)
        self.assertTrue(all(p.frequency == Frequency.HIGH for p in high_freq))
        
        print("✓ 频率过滤测试通过")
    
    def test_scene_words_coverage(self):
        """测试场景词覆盖度"""
        print(f"\n场景词库统计:")
        print(f"  - 默认场景词: {len(DEFAULT_SCENE_WORDS)} 个")
        print(f"  - 场景分类: {len(SCENE_CATEGORIES)} 类")
        
        for category, words in SCENE_CATEGORIES.items():
            print(f"    {category}: {len(words)} 个词")
        
        self.assertGreater(len(DEFAULT_SCENE_WORDS), 10)
        self.assertGreater(len(SCENE_CATEGORIES), 0)
        print("✓ 场景词覆盖度测试通过")


class TestRealWorldScenarios(unittest.TestCase):
    """真实场景测试"""
    
    def test_wuhan_mall_scenario(self):
        """测试武汉商场场景"""
        result = collect_ai_prompts(
            brand_name="武汉万象城",
            competitor_names=["武汉恒隆广场", "武商MALL", "武汉国际广场", "K11"],
            city="武汉",
            industry="商业地产",
            max_prompts=60
        )
        
        # 验证包含真实场景的Prompt
        questions = [p["question"] for p in result["prompts"]]
        
        # 检查关键Prompt
        has_brand_consult = any("武汉万象城" in q and "怎么样" in q for q in questions)
        has_compare = any("哪个好" in q or "区别" in q for q in questions)
        has_scene = any("适合" in q or "哪里" in q for q in questions)
        
        self.assertTrue(has_brand_consult, "缺少品牌咨询类Prompt")
        self.assertTrue(has_compare, "缺少对比分析类Prompt")
        self.assertTrue(has_scene, "缺少场景推荐类Prompt")
        
        print(f"✓ 武汉商场场景测试通过")
        print(f"  - 品牌咨询: {result['categories'].get('品牌咨询', 0)} 个")
        print(f"  - 场景推荐: {result['categories'].get('场景推荐', 0)} 个")
        print(f"  - 对比分析: {result['categories'].get('对比分析', 0)} 个")
    
    def test_multi_city_scenario(self):
        """测试多城市场景"""
        brands = [
            ("上海恒隆广场", "上海"),
            ("成都太古里", "成都"),
            ("深圳万象城", "深圳"),
        ]
        
        for brand, expected_city in brands:
            city, pure_brand = parse_brand_city(brand)
            self.assertEqual(city, expected_city, f"{brand} 城市解析失败")
        
        print(f"✓ 多城市场景测试通过")


def run_demo():
    """运行演示"""
    print("\n" + "="*60)
    print("好易易GEO - Prompt采集模块演示")
    print("="*60)
    
    # 演示完整采集
    result = collect_ai_prompts(
        brand_name="武汉万象城",
        competitor_names=["武汉恒隆广场", "武商MALL", "武汉国际广场"],
        city="武汉",
        industry="商业地产",
        max_prompts=30
    )
    
    print(f"\n📊 采集结果统计:")
    print(f"   总计生成 {len(result['prompts'])} 个Prompt")
    print(f"   分类分布: {result['categories']}")
    
    print(f"\n📝 Prompt示例:")
    for i, prompt in enumerate(result["prompts"][:10], 1):
        print(f"   {i}. [{prompt['type']}] {prompt['question']}")
    
    print(f"\n📂 元数据:")
    for key, value in result["metadata"].items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # 运行测试
    print("\n🚀 开始运行测试...\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestPromptCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # 运行演示
    if result.wasSuccessful():
        run_demo()
    else:
        print("\n⚠️ 测试未全部通过，跳过演示")
