/**
 * 好易易GEO - 内容策略模块
 * 根据AI推荐逻辑生成内容布局策略
 */

exports.main = async (event, context) => {
  const { 
    brandName,
    category,
    targetPlatforms = ['xiaohongshu', 'zhihu', 'wechat'],
    competitors = [],
    aiInsights = null  // 从AI推荐分析获取的洞察
  } = event;

  if (!brandName) {
    return { success: false, error: '请输入品牌名称' };
  }

  try {
    // 1. 分析高权重内容类型
    const contentTypes = analyzeHighValueContentTypes(aiInsights, category);

    // 2. 生成平台适配策略
    const platformStrategies = generatePlatformStrategies(brandName, targetPlatforms, contentTypes);

    // 3. 生成内容模板
    const contentTemplates = generateContentTemplates(brandName, category, contentTypes);

    // 4. 关键词植入策略
    const keywordStrategy = generateKeywordStrategy(brandName, category, aiInsights);

    // 5. 生成完整内容计划
    const contentPlan = generateContentPlan(platformStrategies, contentTemplates, keywordStrategy);

    return {
      success: true,
      brandName,
      contentTypes,
      platformStrategies,
      contentTemplates,
      keywordStrategy,
      contentPlan
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

/**
 * 分析高权重内容类型
 */
function analyzeHighValueContentTypes(aiInsights, category) {
  // 基于行业特点推荐内容类型
  const contentTypeRecommendations = {
    '评测类': {
      types: ['横评', '纵评', '对比评测', '长期体验'],
      weight: 0.9,
      description: 'AI最推荐的类型，用户决策参考价值高'
    },
    '攻略类': {
      types: ['选购指南', '避坑指南', '入门教程', '进阶攻略'],
      weight: 0.85,
      description: '搜索意图明确，用户获取成本低'
    },
    '对比类': {
      types: ['品牌对比', '产品对比', '场景对比', '价格对比'],
      weight: 0.8,
      description: '决策辅助型内容，AI引用率高'
    },
    '体验类': {
      types: ['真实体验', '深度测评', '长期使用报告'],
      weight: 0.75,
      description: '真实用户视角，可信度高'
    },
    '知识类': {
      types: ['行业科普', '技术解析', '选购知识', '使用技巧'],
      weight: 0.7,
      description: '建立专业形象，利于品牌背书'
    }
  };

  // 根据品类特点调整权重
  const categoryOverrides = {
    '科技数码': ['评测类', '对比类', '知识类'],
    '美妆护肤': ['体验类', '评测类', '攻略类'],
    '食品饮料': ['体验类', '攻略类', '知识类'],
    '家居家电': ['评测类', '攻略类', '对比类'],
    '本地生活': ['攻略类', '体验类', '对比类']
  };

  const recommendedTypes = categoryOverrides[category] || ['评测类', '攻略类', '对比类'];
  
  return recommendedTypes.map(type => ({
    type,
    ...contentTypeRecommendations[type],
    priority: recommendedTypes.indexOf(type) + 1
  }));
}

/**
 * 生成平台适配策略
 */
function generatePlatformStrategies(brandName, targetPlatforms, contentTypes) {
  const platformConfigs = {
    xiaohongshu: {
      name: '小红书',
      features: ['种草强', '年轻用户多', '搜索权重高'],
      bestContent: ['体验笔记', '好物推荐', '选购攻略'],
      format: ['图文笔记', '短视频', '合集'],
      keywords: ['推荐', '种草', '宝藏', '必买', '超好用'],
      postingFrequency: '每周3-5篇',
      tips: '标题用数字+感叹句，正文注重真实体验感'
    },
    zhihu: {
      name: '知乎',
      features: ['专业性强', '长尾流量大', 'AI引用率高'],
      bestContent: ['深度分析', '专业评测', '行业解读'],
      format: ['深度文章', '问答', '测评报告'],
      keywords: ['分析', '评测', '对比', '深度', '专业'],
      postingFrequency: '每周1-2篇',
      tips: '注重专业性和数据支撑，适合长文深度内容'
    },
    wechat: {
      name: '微信公众号',
      features: ['私域沉淀', '品牌背书', '深度内容'],
      bestContent: ['品牌故事', '深度测评', '行业洞察'],
      format: ['图文文章', '系列专题', '品牌故事'],
      keywords: ['深度', '解读', '干货', '分享', '揭秘'],
      postingFrequency: '每周1篇',
      tips: '注重内容深度和品牌调性，建立专业形象'
    },
    douyin: {
      name: '抖音',
      features: ['流量大', '传播快', '年轻用户多'],
      bestContent: ['产品展示', '使用场景', '真实体验'],
      format: ['短视频', '直播', '种草视频'],
      keywords: ['推荐', '测评', '必买', '宝藏', '好用'],
      postingFrequency: '每周5-10条',
      tips: '前3秒抓注意力，注重画面质感和BGM'
    },
    bilibili: {
      name: 'B站',
      features: ['年轻用户多', '粘性高', '深度内容'],
      bestContent: ['深度测评', '横评对比', '使用教程'],
      format: ['中长视频', '系列视频', '横评视频'],
      keywords: ['测评', '横评', '对比', '深度', '解析'],
      postingFrequency: '每周1-2条',
      tips: '内容要有干货，时长10-20分钟最佳'
    }
  };

  return targetPlatforms.map(platformId => {
    const config = platformConfigs[platformId];
    if (!config) return null;

    return {
      platform: platformId,
      platformName: config.name,
      features: config.features,
      postingFrequency: config.postingFrequency,
      tips: config.tips,
      recommendedContentTypes: config.bestContent,
      recommendedFormats: config.format,
      recommendedKeywords: config.keywords,
      contentPlan: generatePlatformContentPlan(brandName, config, contentTypes)
    };
  }).filter(Boolean);
}

/**
 * 生成单个平台的内容计划
 */
function generatePlatformContentPlan(brandName, config, contentTypes) {
  const plans = [];

  // 按内容类型生成计划
  contentTypes.slice(0, 3).forEach((contentType, index) => {
    plans.push({
      contentType: contentType.type,
      title: generateContentTitle(brandName, contentType.type, index),
      format: config.format[index % config.format.length],
      keywords: config.keywords.slice(0, 3),
      purpose: contentType.description
    });
  });

  return plans;
}

/**
 * 生成内容标题
 */
function generateContentTitle(brandName, contentType, index) {
  const templates = {
    '评测类': [
      `${brandName}真实测评：用了3个月说说真实感受`,
      `深度评测 | ${brandName}到底值不值得买？`,
      `${brandName} vs 竞品：谁才是真正的性价比之王`
    ],
    '攻略类': [
      `${brandName}选购指南：99%的人都踩过这些坑`,
      `新手必看 | ${brandName}入门完全指南`,
      `${brandName}避坑指南：看完少花冤枉钱`
    ],
    '对比类': [
      `${brandName}横向对比：3分钟看懂选哪个`,
      `${brandName} PK 竞品：真实数据说话`,
      `${brandName}真实对比：看完你就知道怎么选了`
    ],
    '体验类': [
      `真实体验 | ${brandName}一个月后我后悔了吗`,
      `${brandName}素人测评：普通人的真实反馈`,
      `使用90天真实报告 | ${brandName}值得入手吗`
    ],
    '知识类': [
      `${brandName}技术解析：为什么这么多人推荐`,
      `深度解读 | ${brandName}背后的核心竞争力`,
      `${brandName}行业分析：为什么它能脱颖而出`
    ]
  };

  return templates[contentType]?.[index] || `${brandName}${contentType}指南`;
}

/**
 * 生成内容模板
 */
function generateContentTemplates(brandName, category, contentTypes) {
  const templates = {
    evaluation: {
      name: '评测类模板',
      structure: [
        '一、开篇：引入使用场景和痛点',
        '二、产品介绍：核心卖点和参数',
        '三、核心功能测评：真实测试数据和结果',
        '四、优缺点分析：客观评价',
        '五、适用人群：谁适合买',
        '六、总结：是否推荐及理由'
      ],
      tips: [
        '用真实数据和场景说话',
        '客观呈现优缺点',
        '明确目标用户群体'
      ]
    },
    comparison: {
      name: '对比类模板',
      structure: [
        '一、先说结论：哪个更值得买',
        '二、基础参数对比：表格一目了然',
        '三、核心功能对比：逐项PK',
        '四、各自优势分析：场景化推荐',
        '五、选购建议：不同需求选哪个'
      ],
      tips: [
        '结论先行，减少阅读成本',
        '用表格呈现参数对比',
        '场景化推荐更实用'
      ]
    },
    guide: {
      name: '攻略类模板',
      structure: [
        '一、选购要点：关键看这5点',
        '二、常见误区：90%的人都踩过这些坑',
        '三、预算建议：多少钱才够用',
        '四、产品推荐：不同价位怎么选',
        '五、避坑指南：记住这3条就够了'
      ],
      tips: [
        '结构清晰，便于快速浏览',
        '实用性第一，避免废话',
        '给出具体可操作的建议'
      ]
    }
  };

  // 根据内容类型匹配模板
  const templateMap = {
    '评测类': 'evaluation',
    '对比类': 'comparison',
    '攻略类': 'guide',
    '体验类': 'evaluation',
    '知识类': 'guide'
  };

  return contentTypes.map(contentType => {
    const templateKey = templateMap[contentType.type] || 'evaluation';
    return {
      contentType: contentType.type,
      ...templates[templateKey]
    };
  });
}

/**
 * 生成关键词策略
 */
function generateKeywordStrategy(brandName, category, aiInsights) {
  // 关键词分类
  const keywordCategories = {
    brand: {
      name: '品牌词',
      keywords: [brandName, `${brandName}官网`, `${brandName}旗舰店`],
      usage: '品牌曝光基础，必须布局'
    },
    product: {
      name: '产品词',
      keywords: [`${brandName}产品`, `${brandName}型号`, `${brandName}系列`],
      usage: '产品页面必备'
    },
    category: {
      name: '品类词',
      keywords: [category, `${category}推荐`, `${category}排行榜`],
      usage: '品类流量入口'
    },
    longtail: {
      name: '长尾词',
      keywords: [
        `${brandName}怎么样`,
        `${brandName}好不好`,
        `${brandName}值得买吗`,
        `${category}哪个牌子好`,
        `${category}怎么选`
      ],
      usage: '精准流量，竞争小'
    },
    scenario: {
      name: '场景词',
      keywords: [
        `送礼物${category}`,
        `自用${category}`,
        `新手${category}`,
        `${category}入门`
      ],
      usage: '场景化搜索意图明确'
    }
  };

  // 从AI洞察中提取关键词
  const extractedKeywords = aiInsights?.hotKeywords || [];

  return {
    categories: Object.entries(keywordCategories).map(([key, value]) => ({
      type: key,
      ...value
    })),
    extractedFromAI: extractedKeywords,
    recommendations: [
      {
        priority: 'HIGH',
        action: '品牌词+品类词组合',
        example: `${brandName} ${category}推荐`,
        platform: '全平台'
      },
      {
        priority: 'HIGH',
        action: '长尾词+疑问词组合',
        example: `${brandName}怎么样 ${brandName}值得买吗`,
        platform: '知乎/小红书'
      },
      {
        priority: 'MEDIUM',
        action: '场景词精准匹配',
        example: `送父母的${category}推荐 ${brandName}`,
        platform: '小红书/抖音'
      }
    ]
  };
}

/**
 * 生成完整内容计划
 */
function generateContentPlan(platformStrategies, contentTemplates, keywordStrategy) {
  // 按周生成内容日历
  const weeklyPlan = [];
  const contentTypes = contentTemplates.map(t => t.name);

  for (let week = 1; week <= 4; week++) {
    const weekPlan = {
      week,
      themes: [],
      content: []
    };

    // 每周主题
    const themes = [
      '品牌认知 - 建立品牌基础认知',
      '产品评测 - 深度体验和测评',
      '对比分析 - 竞品对比和选购',
      '场景化内容 - 实用场景应用'
    ];
    weekPlan.themes = [themes[(week - 1) % 4]];

    // 每周内容安排
    platformStrategies.forEach(platform => {
      const frequency = platform.postingFrequency;
      const count = parseInt(frequency.match(/\d+/)?.[0] || '1');

      for (let i = 0; i < count; i++) {
        weekPlan.content.push({
          platform: platform.platformName,
          contentType: contentTypes[(week + i) % contentTypes.length],
          suggestedTitle: `Week${week} ${platform.platformName} 内容${i + 1}`
        });
      }
    });

    weeklyPlan.push(weekPlan);
  }

  return {
    monthlyOutput: platformStrategies.reduce((sum, p) => {
      const count = parseInt(p.postingFrequency.match(/\d+/)?.[0] || '1');
      return sum + count * 4;
    }, 0),
    weeklyPlan,
    summary: `每月产出约${weeklyPlan.reduce((s, w) => s + w.content.length, 0)}篇内容，覆盖${platformStrategies.length}个平台`
  };
}
