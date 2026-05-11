/**
 * 好易易GEO - 竞品GEO分析云函数
 * 支持：豆包、千问、DeepSeek、元宝
 */

const API_ENDPOINTS = {
  doubao: {
    name: '字节豆包',
    // 豆包API（需替换为实际API）
    endpoint: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    model: 'doubao-pro-32k'
  },
  qianwen: {
    name: '阿里千问',
    // 千问API（需替换为实际API）
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
    // 元宝API（需替换为实际API）
    endpoint: 'https://api.hunyuan.cloud.tencent.com/hunyuan/v1/chatcompletion',
    model: 'hunyuan-pro'
  }
};

/**
 * 查询单个AI平台的推荐结果
 */
async function queryAIPlatform(platform, brandName, competitorList) {
  const config = API_ENDPOINTS[platform];
  if (!config) return null;
  
  const prompt = `你是一个专业的品牌分析助手。请分析搜索"${brandName}"时，你会推荐哪些品牌？
  
竞品参考：${competitorList.join('、')}
  
请以JSON格式返回，结构如下：
{
  "recommended_brands": ["品牌1", "品牌2", "品牌3"],
  "reasons": ["推荐理由1", "推荐理由2", "推荐理由3"],
  "confidence": 0.85,
  "key_factors": ["关键因素1", "关键因素2"]
}`;

  try {
    // 根据不同平台调用API
    const response = await callAPI(platform, config, prompt);
    return {
      platform: platform,
      platformName: config.name,
      success: true,
      data: parseResponse(response)
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
 * 调用各平台API
 */
async function callAPI(platform, config, prompt) {
  // 这里需要填入各平台的API Key
  const API_KEYS = {
    doubao: process.env.DOUBAO_API_KEY || '',
    qianwen: process.env.QIANWEN_API_KEY || '',
    deepseek: process.env.DEEPSEEK_API_KEY || '',
    yuanbao: process.env.YUANBAO_API_KEY || ''
  };

  const response = await wx.cloud.callContainer({
    config: {
      env: 'your-env-id'
    },
    path: '/api/analyze',
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEYS[platform]}`
    },
    data: {
      model: config.model,
      messages: [{ role: 'user', content: prompt }]
    }
  });

  return response.data;
}

/**
 * 解析API响应
 */
function parseResponse(data) {
  try {
    // 从响应中提取内容
    const content = data.choices?.[0]?.message?.content || '';
    // 尝试解析JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    return { raw_response: content };
  } catch (e) {
    return { raw_response: data.choices?.[0]?.message?.content || '' };
  }
}

/**
 * 主入口
 */
exports.main = async (event, context) => {
  const { brandName, competitors = [], platforms = ['doubao', 'qianwen', 'deepseek', 'yuanbao'] } = event;

  if (!brandName) {
    return { success: false, error: '请输入品牌名称' };
  }

  // 并行查询所有平台
  const results = await Promise.all(
    platforms.map(platform => queryAIPlatform(platform, brandName, competitors))
  );

  // 生成分析报告
  const report = generateReport(brandName, results);

  return {
    success: true,
    brandName,
    platforms: results,
    report
  };
};

/**
 * 生成分析报告
 */
function generateReport(brandName, results) {
  const successfulResults = results.filter(r => r.success);
  
  // 统计各平台推荐的品牌
  const brandCount = {};
  successfulResults.forEach(result => {
    const brands = result.data?.recommended_brands || [];
    brands.forEach(brand => {
      brandCount[brand] = (brandCount[brand] || 0) + 1;
    });
  });

  // 按推荐次数排序
  const ranking = Object.entries(brandCount)
    .sort((a, b) => b[1] - a[1])
    .map(([brand, count]) => ({ brand, count, platforms: count }));

  return {
    summary: {
      totalPlatforms: results.length,
      successful: successfulResults.length,
      failed: results.length - successfulResults.length
    },
    ranking,
    recommendations: generateRecommendations(brandName, ranking)
  };
}

/**
 * 生成优化建议
 */
function generateRecommendations(brandName, ranking) {
  const suggestions = [];
  
  // 检查品牌是否在推荐中
  const isRecommended = ranking.some(r => r.brand.includes(brandName));
  
  if (!isRecommended) {
    suggestions.push({
      priority: 'HIGH',
      type: '品牌曝光',
      content: '建议加强品牌在主流内容平台的曝光，提高AI推荐概率'
    });
  }

  suggestions.push({
    priority: 'MEDIUM',
    type: '内容优化',
    content: '在知乎、小红书等高权重平台发布品牌相关内容'
  });

  return suggestions;
}
