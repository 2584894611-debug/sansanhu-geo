/**
 * 好易易GEO - 监测预警模块
 * 追踪品牌在AI搜索中的表现变化
 */

const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();

exports.main = async (event, context) => {
  const { 
    action,  // 'create' | 'check' | 'getHistory' | 'delete'
    brandName,
    keywords = [],
    platforms = ['doubao', 'qianwen', 'deepseek', 'yuanbao'],
    taskId = null
  } = event;

  try {
    switch (action) {
      case 'create':
        return await createMonitorTask(brandName, keywords, platforms);
      
      case 'check':
        return await checkNow(brandName, keywords, platforms);
      
      case 'getHistory':
        return await getMonitorHistory(brandName);
      
      case 'getTasks':
        return await getAllTasks();
      
      case 'delete':
        return await deleteTask(taskId);
      
      default:
        return { success: false, error: '未知操作' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};

/**
 * 创建监测任务
 */
async function createMonitorTask(brandName, keywords, platforms) {
  const task = {
    brandName,
    keywords,
    platforms,
    status: 'active',
    createdAt: new Date(),
    lastCheckAt: null,
    checkInterval: 24 * 60 * 60 * 1000, // 24小时
    alertEnabled: true,
    alertThreshold: 10 // 排名下降超过10位触发预警
  };

  const result = await db.collection('geo_monitor_tasks').add({
    data: task
  });

  return {
    success: true,
    taskId: result.id,
    message: `已为${brandName}创建监测任务，将每24小时自动检查一次`
  };
}

/**
 * 立即检查
 */
async function checkNow(brandName, keywords, platforms) {
  const checkTime = new Date();
  
  // 查询各平台排名
  const platformResults = await Promise.all(
    platforms.map(platform => checkPlatformRanking(platform, brandName, keywords))
  );

  // 与上次结果对比
  const lastResult = await getLastCheckResult(brandName);
  const comparison = compareResults(lastResult, platformResults);

  // 保存本次结果
  await saveCheckResult(brandName, platformResults, checkTime);

  // 生成报告
  const report = generateMonitorReport(brandName, platformResults, comparison);

  // 检查是否需要预警
  if (comparison.significantChange) {
    await triggerAlert(brandName, comparison);
  }

  return {
    success: true,
    checkTime: checkTime.toLocaleString('zh-CN'),
    platformResults,
    comparison,
    report
  };
}

/**
 * 检查单个平台排名
 */
async function checkPlatformRanking(platform, brandName, keywords) {
  // 模拟AI查询
  const results = {
    platform,
    platformName: getPlatformName(platform),
    checkTime: new Date().toISOString(),
    rankings: [],
    visibility: 0,
    mentionedCount: 0
  };

  // 模拟关键词排名数据
  keywords.forEach(keyword => {
    const mockRank = Math.floor(Math.random() * 50) + 1;
    results.rankings.push({
      keyword,
      rank: mockRank,
      change: Math.floor(Math.random() * 20) - 10 // -10 到 +10
    });
    results.visibility += (100 - mockRank) / keywords.length;
    if (mockRank <= 20) results.mentionedCount++;
  });

  results.visibility = Math.round(results.visibility);
  return results;
}

/**
 * 获取平台名称
 */
function getPlatformName(platform) {
  const names = {
    doubao: '字节豆包',
    qianwen: '阿里千问',
    deepseek: 'DeepSeek',
    yuanbao: '腾讯元宝'
  };
  return names[platform] || platform;
}

/**
 * 对比结果
 */
function compareResults(lastResult, currentResults) {
  if (!lastResult) {
    return {
      significantChange: false,
      message: '首次检测，无历史数据对比',
      changes: []
    };
  }

  const changes = [];
  let totalChange = 0;

  currentResults.forEach(current => {
    const last = lastResult.find(r => r.platform === current.platform);
    if (!last) return;

    current.rankings.forEach(ranking => {
      const lastRanking = last.rankings.find(r => r.keyword === ranking.keyword);
      if (!lastRanking) return;

      const change = lastRanking.rank - ranking.rank; // 正数表示上升
      totalChange += change;

      if (Math.abs(change) >= 5) {
        changes.push({
          platform: current.platformName,
          keyword: ranking.keyword,
          lastRank: lastRanking.rank,
          currentRank: ranking.rank,
          change: change,
          direction: change > 0 ? 'up' : 'down'
        });
      }
    });
  });

  return {
    significantChange: Math.abs(totalChange) >= 10,
    totalChange,
    changes,
    message: changes.length > 0 
      ? `发现${changes.length}个显著变化` 
      : '排名稳定，无显著变化'
  };
}

/**
 * 保存检测结果
 */
async function saveCheckResult(brandName, results, checkTime) {
  await db.collection('geo_monitor_history').add({
    data: {
      brandName,
      results,
      checkTime,
      createdAt: new Date()
    }
  });
}

/**
 * 获取上次检测结果
 */
async function getLastCheckResult(brandName) {
  const result = await db.collection('geo_monitor_history')
    .where({ brandName })
    .orderBy('checkTime', 'desc')
    .limit(1)
    .get();

  return result.data?.[0]?.results || null;
}

/**
 * 生成监测报告
 */
function generateMonitorReport(brandName, platformResults, comparison) {
  const avgVisibility = platformResults.reduce((sum, p) => sum + p.visibility, 0) / platformResults.length;
  
  // 评级
  let level = 'D';
  let levelText = '需改进';
  if (avgVisibility >= 80) { level = 'S'; levelText = '优秀'; }
  else if (avgVisibility >= 60) { level = 'A'; levelText = '良好'; }
  else if (avgVisibility >= 40) { level = 'B'; levelText = '一般'; }
  else if (avgVisibility >= 20) { level = 'C'; levelText = '较弱'; }

  return {
    brandName,
    checkTime: new Date().toLocaleString('zh-CN'),
    overallVisibility: Math.round(avgVisibility),
    level,
    levelText,
    platformSummary: platformResults.map(p => ({
      platform: p.platformName,
      visibility: p.visibility,
      mentionedCount: p.mentionedCount
    })),
    comparison,
    recommendations: generateRecommendations(comparison, avgVisibility)
  };
}

/**
 * 生成建议
 */
function generateRecommendations(comparison, visibility) {
  const recommendations = [];

  if (visibility < 30) {
    recommendations.push({
      priority: 'HIGH',
      content: '品牌可见性较低，建议增加内容发布频率'
    });
  }

  if (comparison.changes.some(c => c.direction === 'down')) {
    recommendations.push({
      priority: 'HIGH',
      content: '部分关键词排名下降，建议检查竞品动态并优化内容'
    });
  }

  if (comparison.changes.some(c => c.direction === 'up')) {
    recommendations.push({
      priority: 'MEDIUM',
      content: '部分关键词排名上升，继续保持当前策略'
    });
  }

  recommendations.push({
    priority: 'MEDIUM',
    content: '建议持续监测，及时发现排名变化'
  });

  return recommendations;
}

/**
 * 触发预警
 */
async function triggerAlert(brandName, comparison) {
  // 这里可以接入微信通知、邮件等
  const alertMessage = {
    brandName,
    type: 'GEO排名预警',
    summary: comparison.message,
    changes: comparison.changes,
    time: new Date().toLocaleString('zh-CN')
  };

  // 保存预警记录
  await db.collection('geo_alerts').add({
    data: {
      ...alertMessage,
      status: 'unread',
      createdAt: new Date()
    }
  });

  return alertMessage;
}

/**
 * 获取监测历史
 */
async function getMonitorHistory(brandName) {
  const result = await db.collection('geo_monitor_history')
    .where({ brandName })
    .orderBy('checkTime', 'desc')
    .limit(30)
    .get();

  return {
    success: true,
    history: result.data.map(item => ({
      checkTime: item.checkTime,
      visibility: Math.round(
        item.results.reduce((sum, p) => sum + p.visibility, 0) / item.results.length
      )
    }))
  };
}

/**
 * 获取所有任务
 */
async function getAllTasks() {
  const result = await db.collection('geo_monitor_tasks')
    .where({ status: 'active' })
    .get();

  return {
    success: true,
    tasks: result.data.map(task => ({
      taskId: task._id,
      brandName: task.brandName,
      keywords: task.keywords,
      platforms: task.platforms,
      lastCheckAt: task.lastCheckAt,
      createdAt: task.createdAt
    }))
  };
}

/**
 * 删除任务
 */
async function deleteTask(taskId) {
  await db.collection('geo_monitor_tasks').doc(taskId).remove();
  
  return {
    success: true,
    message: '监测任务已删除'
  };
}
