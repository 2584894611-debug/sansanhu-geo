/**
 * 好易易GEO - AI搜索推荐分析云函数
 * 分析各AI平台的推荐逻辑和品牌推荐结果
 */

const API_CONFIGS = {
  doubao: {
    name: '字节豆包',
    endpoint: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    model: 'doubao-pro-32k'
  },
  qianwen: {
    name: '阿里千问',
    endpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    model: 'qwen-plus'
  },
  deepseek: {
    name: 'DeepSeek',
    endpoint: 'https://api.deepseek.com/v1/chat/completions',
    model: 'deepseek-chat'
  },
  yuanbao: {
    name: '腾讯元宝',
    endpoint: 'https://api.hunyuan.cloud.tencent.com/hunyuan/v1/chatcompletion',
    model: 'hunyuan-pro'
  }
};

/**
 * 主入口：AI搜索推荐分析
 */
exports.main = async (event, context) => {
  const { 
    query,           // 搜索查询词
    category,        // 品类/行业
    competitors = [], // 竞品列表
    platforms = ['doubao', 'qianwen', 'deepseek', 'yuanbao']
  } = event;

  if (!query) {
    return { success: false, error: '请输入搜索查询词' };
  }

  try {
    // 1. 获取各平台推荐结果
    const platformResults = await Promise.all(
      platforms.map(platform => analyzePlatformRecommendations(platform, query, category))
    );

    // 2. 提取推荐品牌
    const brandRecommendations = extractBrandRecommendations(platformResults);

    // 3. 分析推荐逻辑
    const recommendationLogic = analyzeRecommendationLogic(platformResults);

    // 4. 生成洞察报告
    const insights = generateInsights(query, brandRecommendations, recommendationLogic);

    return {
      success: true,
      query,
      category,
      platformResults,
      brandRecommendations,
      recommendationLogic,
      insights
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * 分析单个平台的推荐结果
 */
async function analyzePlatformRecommendations(platform, query, category) {
  const config = API_CONFIGS[platform];
  if (!config) return null;

  try {
    // 构建分析Prompt
    const analysisPrompt = buildAnalysisPrompt(query, category);
    
    // 调用AI
    const response = await callAI(platform, analysisPrompt);
    
    // 解析结果
    const analysis = parseAIResponse(response);
    
    return {
      platform,
      platformName: config.name,
      success: true,
      recommendations: analysis.recommendations || [],
      reasons: analysis.reasons || [],
      confidence: analysis.confidence || 0.7,
      rawResponse: analysis.raw || ''
    };
  } catch (error) {
    return {
      platform,
      platformName: config.name,
      success: false,
      error: error.message
    };
  }
}

/**
 * 构建分析Prompt
 */
function buildAnalysisPrompt(query, category) {
  const categoryContext = category ? `品类：${category}。` : '';
  
  return `你是一个专业的品牌推荐AI助手。

${categoryContext}用户搜索词："${query}"

请分析：
1. 当用户搜索"${query}"时，你会推荐哪些品牌？
2. 推荐这些品牌的理由是什么？
3. 你的推荐逻辑是什么？

请以JSON格式返回：
{
  "recommendations": [
    {"brand": "品牌名", "reason": "推荐理由", "score": 85}
  ],
  "reasoning_patterns": ["推荐逻辑1", "推荐逻辑2"],
  "key_factors": ["关键因素1", "关键因素2"],
  "confidence": 0.8
}

注意：
- 列出5-10个推荐品牌
- 每个品牌的推荐理由要具体
- 推荐逻辑要能帮助品牌方理解如何被选中`;
}

/**
 * 调用AI API
 */
async function callAI(platform, prompt) {
  const config = API_CONFIGS[platform];
  const API_KEYS = {
    doubao: process.env.DOUBAO_API_KEY || '',
    qianwen: process.env.QIANWEN_API_KEY || '',
    deepseek: process.env.DEEPSEEK_API_KEY || '',
    yuanbao: process.env.YUANBAO_API_KEY || ''
  };

  // 这里需要实现实际的API调用
  // 暂时返回模拟数据用于测试
  return {
    choices: [{
      message: {
        content: JSON.stringify({
          recommendations: [
            { brand: '品牌A', reason: '品质好口碑佳', score: 92 },
            { brand: '品牌B', reason: '性价比高', score: 88 },
            { brand: '品牌C', reason: '服务优质', score: 85 }
          ],
          reasoning_patterns: ['口碑评价', '性价比', '服务质量'],
          key_factors: ['用户评价', '价格策略', '品牌知名度'],
          confidence: 0.85
        })
      }
    }]
  };
}

/**
 * 解析AI响应
 */
function parseAIResponse(response) {
  try {
    const content = response?.choices?.[0]?.message?.content || '';
    
    // 尝试提取JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    return { raw: content };
  } catch (e) {
    return { raw: response?.choices?.[0]?.message?.content || '' };
  }
}

/**
 * 提取品牌推荐
 */
function extractBrandRecommendations(platformResults) {
  const brandMap = new Map();

  platformResults.forEach(result => {
    if (!result?.success) return;

    result.recommendations?.forEach(rec => {
      const brandName = rec.brand;
      if (!brandMap.has(brandName)) {
        brandMap.set(brandName, {
          brand: brandName,
          platforms: [],
          reasons: [],
          avgScore: 0,
          scores: []
        });
      }

      const entry = brandMap.get(brandName);
      entry.platforms.push(result.platformName);
      entry.reasons.push(rec.reason);
      entry.scores.push(rec.score || 0);
    });
  });

  // 计算平均分
  brandMap.forEach(entry => {
    entry.avgScore = entry.scores.length > 0 
      ? Math.round(entry.scores.reduce((a, b) => a + b, 0) / entry.scores.length)
      : 0;
    entry.platformCount = entry.platforms.length;
    delete entry.scores;
  });

  // 按平台数和评分排序
  return Array.from(brandMap.values())
    .sort((a, b) => {
      if (b.platformCount !== a.platformCount) {
        return b.platformCount - a.platformCount;
      }
      return b.avgScore - a.avgScore;
    });
}

/**
 * 分析推荐逻辑
 */
function analyzeRecommendationLogic(platformResults) {
  const allPatterns = [];
  const allFactors = [];

  platformResults.forEach(result => {
    if (!result?.success) return;

    if (result.reasoning_patterns) {
      allPatterns.push(...result.reasoning_patterns);
    }
    if (result.key_factors) {
      allFactors.push(...result.key_factors);
    }
  });

  // 统计出现频率
  const patternCount = countOccurrences(allPatterns);
  const factorCount = countOccurrences(allFactors);

  return {
    top_patterns: patternCount.slice(0, 5).map(([name, count]) => ({ pattern: name, count })),
    top_factors: factorCount.slice(0, 5).map(([name, count]) => ({ factor: name, count })),
    analysis: generatePatternAnalysis(patternCount, factorCount)
  };
}

/**
 * 统计出现频率
 */
function countOccurrences(items) {
  const countMap = new Map();
  items.forEach(item => {
    const normalized = item.trim();
    if (normalized) {
      countMap.set(normalized, (countMap.get(normalized) || 0) + 1);
    }
  });
  return Array.from(countMap.entries()).sort((a, b) => b[1] - a[1]);
}

/**
 * 生成模式分析
 */
function generatePatternAnalysis(patterns, factors) {
  const insights = [];

  // 分析推荐模式
  if (patterns.length > 0) {
    const topPattern = patterns[0][0];
    insights.push(`AI主要依据"${topPattern}"进行品牌推荐`);
  }

  // 分析关键因素
  if (factors.length > 0) {
    const topFactor = factors[0][0];
    insights.push(`"${topFactor}"是影响推荐的最重要因素`);
  }

  // 生成优化建议
  if (patterns.length > 0) {
    insights.push(`建议：针对AI的推荐模式优化品牌内容策略`);
  }

  return insights;
}

/**
 * 生成洞察报告
 */
function generateInsights(query, recommendations, logic) {
  const insights = [];

  // 品牌机会分析
  if (recommendations.length === 0) {
    insights.push({
      type: '空白机会',
      content: '该搜索词下AI推荐较少，存在品牌植入机会'
    });
  } else if (recommendations.length < 5) {
    insights.push({
      type: '轻度竞争',
      content: `当前有${recommendations.length}个品牌被推荐，竞争程度中等`
    });
  } else {
    insights.push({
      type: '高度竞争',
      content: `已有${recommendations.length}个品牌被推荐，竞争激烈，需要差异化策略`
    });
  }

  // 关键词洞察
  const topReasons = recommendations
    .flatMap(r => r.reasons)
    .reduce((acc, reason) => {
      // 简单提取关键词
      const keywords = reason.match(/[\u4e00-\u9fa5]{2,}/g) || [];
      keywords.forEach(kw => {
        acc.set(kw, (acc.get(kw) || 0) + 1);
      });
      return acc;
    }, new Map());

  const hotKeywords = Array.from(topReasons.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([kw]) => kw);

  if (hotKeywords.length > 0) {
    insights.push({
      type: '热门关键词',
      content: `推荐内容高频词：${hotKeywords.join('、')}，建议在内容中融入这些关键词`
    });
  }

  // 平台洞察
  const platformCoverage = recommendations
    .filter(r => r.platforms.length >= 2)
    .map(r => r.brand);

  if (platformCoverage.length > 0) {
    insights.push({
      type: '跨平台品牌',
      content: `${platformCoverage.slice(0, 3).join('、')}等多平台被推荐，跨平台布局很重要`
    });
  }

  return insights;
}
