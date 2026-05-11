/**
 * 好易易GEO - 品牌健康诊断云函数
 * 分析自有品牌在AI搜索中的表现
 */

const API_ENDPOINTS = {
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
 * 诊断品牌在AI搜索中的表现
 */
exports.main = async (event, context) => {
  const { 
    brandName, 
    industry, 
    keywords = [],
    platforms = ['doubao', 'qianwen', 'deepseek', 'yuanbao'] 
  } = event;

  if (!brandName) {
    return { success: false, error: '请输入品牌名称' };
  }

  try {
    // 1. 查询各平台推荐情况
    const platformResults = await Promise.all(
      platforms.map(platform => diagnosePlatform(platform, brandName, industry))
    );

    // 2. 分析关键词覆盖
    const keywordCoverage = await analyzeKeywordCoverage(brandName, keywords, platforms);

    // 3. 生成健康评分
    const healthScore = calculateHealthScore(platformResults, keywordCoverage);

    // 4. 生成诊断报告
    const diagnosis = generateDiagnosis(brandName, platformResults, keywordCoverage, healthScore);

    return {
      success: true,
      brandName,
      healthScore,
      platformResults,
      keywordCoverage,
      diagnosis
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * 诊断单个平台
 */
async function diagnosePlatform(platform, brandName, industry) {
  const config = API_ENDPOINTS[platform];
  if (!config) return null;

  const prompts = [
    `搜索"${industry || '该行业'}"时，你会推荐哪些品牌？请列出前5个。`,
    `"${brandName}"这个品牌怎么样？值得推荐吗？`,
    `如果要选择一个好的${industry || '行业'}品牌，你会考虑哪些因素？`
  ];

  try {
    const results = await Promise.all(
      prompts.map(prompt => queryAI(platform, prompt))
    );

    // 分析品牌是否被推荐
    const isRecommended = results.some(r => 
      r.toLowerCase().includes(brandName.toLowerCase())
    );

    // 提取推荐理由
    const reasons = extractReasons(results, brandName);

    // 计算推荐指数
    const recommendationIndex = calculateRecommendationIndex(results, brandName);

    return {
      platform: platform,
      platformName: config.name,
      success: true,
      isRecommended,
      recommendationIndex,
      reasons,
      rawResponses: results
    };
  } catch (error) {
    return {
      platform: platform,
      platformName: config.name,
      success: false,
      error: error.message
    };
  }
}

/**
 * 查询AI
 */
async function queryAI(platform, prompt) {
  // 这里需要调用实际的API
  // 暂时返回模拟数据
  return `模拟AI回复：关于${prompt}`;
}

/**
 * 提取推荐理由
 */
function extractReasons(responses, brandName) {
  const reasons = [];
  
  responses.forEach(response => {
    // 简单的关键词提取
    const keywords = ['质量', '服务', '口碑', '性价比', '创新', '专业'];
    keywords.forEach(kw => {
      if (response.includes(kw) && !reasons.includes(kw)) {
        reasons.push(kw);
      }
    });
  });

  return reasons.slice(0, 5);
}

/**
 * 计算推荐指数
 */
function calculateRecommendationIndex(responses, brandName) {
  let score = 0;
  const brandNameLower = brandName.toLowerCase();
  
  responses.forEach(response => {
    if (response.toLowerCase().includes(brandNameLower)) {
      score += 30;
    }
    if (response.includes('推荐') || response.includes('建议')) {
      score += 10;
    }
  });

  return Math.min(100, score);
}

/**
 * 分析关键词覆盖
 */
async function analyzeKeywordCoverage(brandName, keywords, platforms) {
  const coverage = [];

  for (const keyword of keywords) {
    const platformCoverage = await Promise.all(
      platforms.map(platform => checkKeywordOnPlatform(platform, keyword, brandName))
    );

    const coverageRate = platformCoverage.filter(c => c.mentioned).length / platforms.length;
    
    coverage.push({
      keyword,
      coverageRate,
      mentionedPlatforms: platformCoverage.filter(c => c.mentioned).map(c => c.platform),
      suggestions: generateKeywordSuggestions(coverageRate, keyword, brandName)
    });
  }

  return coverage;
}

/**
 * 检查关键词在平台的表现
 */
async function checkKeywordOnPlatform(platform, keyword, brandName) {
  // 实际实现需要调用API
  return {
    platform,
    mentioned: Math.random() > 0.5, // 模拟数据
    position: Math.floor(Math.random() * 10) + 1
  };
}

/**
 * 生成关键词建议
 */
function generateKeywordSuggestions(coverageRate, keyword, brandName) {
  if (coverageRate === 0) {
    return `建议在内容中增加"${keyword}+${brandName}"的组合关键词`;
  } else if (coverageRate < 0.5) {
    return `建议加强"${keyword}"相关内容的发布频率`;
  } else {
    return `关键词"${keyword}"覆盖良好，继续保持`;
  }
}

/**
 * 计算健康评分
 */
function calculateHealthScore(platformResults, keywordCoverage) {
  // 平台推荐得分（40%权重）
  const recommendedCount = platformResults.filter(p => p.success && p.isRecommended).length;
  const platformScore = (recommendedCount / platformResults.length) * 40;

  // 关键词覆盖得分（40%权重）
  const avgCoverage = keywordCoverage.length > 0 
    ? keywordCoverage.reduce((sum, k) => sum + k.coverageRate, 0) / keywordCoverage.length 
    : 0;
  const keywordScore = avgCoverage * 40;

  // 推荐指数得分（20%权重）
  const avgRecommendation = platformResults
    .filter(p => p.success)
    .reduce((sum, p) => sum + (p.recommendationIndex || 0), 0) / platformResults.length;
  const recommendationScore = avgRecommendation * 0.2;

  const totalScore = Math.round(platformScore + keywordScore + recommendationScore);

  // 评级
  let level = 'D';
  if (totalScore >= 90) level = 'S';
  else if (totalScore >= 80) level = 'A';
  else if (totalScore >= 70) level = 'B';
  else if (totalScore >= 60) level = 'C';

  return {
    totalScore,
    level,
    breakdown: {
      platformScore: Math.round(platformScore),
      keywordScore: Math.round(keywordScore),
      recommendationScore: Math.round(recommendationScore)
    }
  };
}

/**
 * 生成诊断报告
 */
function generateDiagnosis(brandName, platformResults, keywordCoverage, healthScore) {
  const recommendations = [];

  // 平台建议
  platformResults.forEach(p => {
    if (p.success && !p.isRecommended) {
      recommendations.push({
        priority: 'HIGH',
        type: `${p.platformName}优化`,
        content: `建议在${p.platformName}相关平台增加品牌曝光内容`
      });
    }
  });

  // 关键词建议
  keywordCoverage.forEach(k => {
    if (k.coverageRate < 0.5) {
      recommendations.push({
        priority: 'MEDIUM',
        type: '关键词布局',
        content: k.suggestions
      });
    }
  });

  // 综合建议
  if (healthScore.totalScore < 60) {
    recommendations.push({
      priority: 'HIGH',
      type: '整体策略',
      content: '品牌GEO基础薄弱，建议系统性地在知乎、小红书等高权重平台布局内容'
    });
  } else if (healthScore.totalScore < 80) {
    recommendations.push({
      priority: 'MEDIUM',
      type: '优化方向',
      content: '品牌有一定GEO基础，建议针对薄弱平台定向优化'
    });
  } else {
    recommendations.push({
      priority: 'LOW',
      type: '持续维护',
      content: '品牌GEO表现良好，建议保持内容更新频率'
    });
  }

  return recommendations;
}
