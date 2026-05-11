/**
 * 好易易GEO - 报告生成云函数
 * 生成PDF/Word格式的GEO分析报告
 */

const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

/**
 * 生成GEO分析报告
 */
exports.main = async (event, context) => {
  const { brandName, results, type = 'competitor' } = event;
  
  try {
    // 构建报告内容
    const reportContent = buildReportContent(brandName, results, type);
    
    // 生成HTML模板
    const htmlContent = generateHTMLReport(brandName, reportContent);
    
    // 上传到云存储
    const fileName = `GEO报告_${brandName}_${Date.now()}.html`;
    const uploadResult = await cloud.uploadFile({
      cloudPath: `reports/${fileName}`,
      fileContent: Buffer.from(htmlContent, 'utf-8')
    });

    return {
      success: true,
      fileID: uploadResult.fileID,
      fileName: fileName,
      downloadUrl: `https://${uploadResult.fileID}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * 构建报告内容结构
 */
function buildReportContent(brandName, results, type) {
  const { platforms, report } = results;
  
  // 平台统计
  const platformStats = platforms.map(p => ({
    name: p.platformName,
    status: p.success ? '成功' : '失败',
    brands: p.success ? p.data?.recommended_brands || [] : [],
    reasons: p.success ? p.data?.reasons || [] : []
  }));

  // 品牌排名
  const brandRanking = report?.ranking || [];
  
  // 优化建议
  const suggestions = report?.recommendations || [];

  return {
    type,
    generateTime: new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }),
    platformStats,
    brandRanking,
    suggestions,
    summary: report?.summary || {}
  };
}

/**
 * 生成HTML报告
 */
function generateHTMLReport(brandName, content) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GEO分析报告 - ${brandName}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
    .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; margin-bottom: 30px; }
    .header h1 { font-size: 32px; margin-bottom: 10px; }
    .header .subtitle { opacity: 0.9; }
    .header .brand { font-size: 24px; margin-top: 15px; font-weight: bold; }
    .card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .card-title { font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
    .platform-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
    .platform-card { background: #f8f9fa; padding: 15px; border-radius: 8px; }
    .platform-card.success { border-left: 4px solid #52c41a; }
    .platform-card.failed { border-left: 4px solid #ff4d4f; }
    .platform-name { font-weight: bold; display: block; margin-bottom: 8px; }
    .platform-status { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .platform-status.success { background: #d9f7be; color: #52c41a; }
    .platform-status.failed { background: #fff1f0; color: #ff4d4f; }
    .ranking-list { counter-reset: ranking; }
    .ranking-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
    .ranking-item:last-child { border-bottom: none; }
    .rank-num { width: 30px; height: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; }
    .brand-name { flex: 1; font-weight: 500; }
    .platform-count { color: #888; font-size: 14px; }
    .suggestion-item { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
    .suggestion-item:last-child { margin-bottom: 0; }
    .suggestion-header { display: flex; align-items: center; margin-bottom: 8px; }
    .priority { font-size: 12px; padding: 2px 8px; border-radius: 4px; margin-right: 10px; }
    .priority.HIGH { background: #fff1f0; color: #ff4d4f; }
    .priority.MEDIUM { background: #fff7e6; color: #fa8c16; }
    .suggestion-type { font-weight: bold; color: #333; }
    .suggestion-content { color: #666; font-size: 14px; }
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    .stats-row { display: flex; justify-content: space-around; margin-bottom: 20px; }
    .stat-item { text-align: center; }
    .stat-value { font-size: 28px; font-weight: bold; color: #667eea; }
    .stat-label { color: #888; font-size: 14px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🔍 好易易GEO分析报告</h1>
      <div class="subtitle">AI搜索竞品分析</div>
      <div class="brand">${brandName}</div>
      <div class="subtitle">生成时间：${content.generateTime}</div>
    </div>

    <!-- 统计概览 -->
    <div class="card">
      <div class="card-title">📊 分析概览</div>
      <div class="stats-row">
        <div class="stat-item">
          <div class="stat-value">${content.summary.totalPlatforms || 0}</div>
          <div class="stat-label">分析平台</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${content.summary.successful || 0}</div>
          <div class="stat-label">成功</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">${content.summary.failed || 0}</div>
          <div class="stat-label">失败</div>
        </div>
      </div>
    </div>

    <!-- 平台分析 -->
    <div class="card">
      <div class="card-title">🤖 各平台AI推荐结果</div>
      <div class="platform-grid">
        ${content.platformStats.map(p => `
          <div class="platform-card ${p.status === '成功' ? 'success' : 'failed'}">
            <span class="platform-name">${p.name}</span>
            <span class="platform-status ${p.status === '成功' ? 'success' : 'failed'}">${p.status}</span>
            ${p.status === '成功' ? `
              <div style="margin-top: 10px; font-size: 14px;">
                <div><strong>推荐品牌：</strong>${p.brands.join('、') || '无'}</div>
              </div>
            ` : `<div style="margin-top: 10px; color: #ff4d4f; font-size: 14px;">查询失败</div>`}
          </div>
        `).join('')}
      </div>
    </div>

    <!-- 品牌排名 -->
    <div class="card">
      <div class="card-title">🏆 品牌推荐排名</div>
      <div class="ranking-list">
        ${content.brandRanking.length > 0 ? content.brandRanking.map((item, index) => `
          <div class="ranking-item">
            <span class="rank-num">${index + 1}</span>
            <span class="brand-name">${item.brand}</span>
            <span class="platform-count">${item.platforms}个平台推荐</span>
          </div>
        `).join('') : '<div style="color: #888; text-align: center; padding: 20px;">暂无数据</div>'}
      </div>
    </div>

    <!-- 优化建议 -->
    <div class="card">
      <div class="card-title">💡 GEO优化建议</div>
      ${content.suggestions.length > 0 ? content.suggestions.map(s => `
        <div class="suggestion-item">
          <div class="suggestion-header">
            <span class="priority ${s.priority}">${s.priority === 'HIGH' ? '高优' : '中优'}</span>
            <span class="suggestion-type">${s.type}</span>
          </div>
          <div class="suggestion-content">${s.content}</div>
        </div>
      `).join('') : '<div style="color: #888; text-align: center; padding: 20px;">暂无建议</div>'}
    </div>

    <div class="footer">
      <p>本报告由好易易GEO自动生成</p>
      <p>仅供战略参考，不构成投资建议</p>
    </div>
  </div>
</body>
</html>`;
}
