import axios from 'axios'

const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加device_id
apiClient.interceptors.request.use(config => {
  const deviceId = localStorage.getItem('geo_device_id') || generateDeviceId()
  config.params = {
    ...config.params,
    device_id: deviceId
  }
  return config
})

function generateDeviceId() {
  const id = 'geo_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36)
  localStorage.setItem('geo_device_id', id)
  return id
}

// API 函数
export const api = {
  // 用户状态
  getUserStatus: () => apiClient.get('/user/status'),
  
  // 品牌分析
  analyze: (data) => apiClient.post('/analyze', data),
  
  // 分析历史
  getHistory: (limit = 20) => apiClient.get('/analysis/history', { params: { limit } }),
  
  // 评分趋势
  getBrandTrend: (brand, days = 30) => apiClient.get('/brand/trend', { params: { brand, days } }),

  // ===== PRD 监控仪表盘 API =====
  getDashboardBrands: () => apiClient.get('/v1/dashboard/brands'),
  getDashboardScoreTrend: (brand, days = 30) =>
    apiClient.get('/v1/dashboard/score-trend', { params: { brand, days } }),
  getDashboardKeywordPenetration: (brand, days = 30) =>
    apiClient.get('/v1/dashboard/keyword-penetration', { params: { brand, days } }),
  getDashboardPlatformDistribution: (brand, days = 30) =>
    apiClient.get('/v1/dashboard/platform-distribution', { params: { brand, days } }),
  getDashboardCompetitorComparison: (brand, days = 30) =>
    apiClient.get('/v1/dashboard/competitor-comparison', { params: { brand, days } }),
  getDashboardAlerts: (brand, days = 30) =>
    apiClient.get('/v1/dashboard/alerts', { params: { brand, days } }),
  refreshDashboard: (data) => apiClient.post('/v1/dashboard/refresh', data),
  
  // 预警信息
  getAlerts: (brand = null) => apiClient.get('/alerts', { params: { brand } }),
  
  // 激活付费
  activatePremium: (token) => apiClient.post('/premium/activate', null, { params: { token } }),
  
  // 健康检查
  healthCheck: () => apiClient.get('/health'),
  
  // ===== 监测订阅 API =====
  // 创建监测订阅
  createMonitor: (data) => apiClient.post('/monitor', data),
  
  // 获取监测列表
  getMonitors: () => apiClient.get('/monitor'),
  
  // 获取监测历史
  getMonitorHistory: (subscriptionId, days = 30) => 
    apiClient.get(`/monitor/${subscriptionId}/history`, { params: { days } }),
  
  // 删除监测订阅
  deleteMonitor: (subscriptionId) => apiClient.delete(`/monitor/${subscriptionId}`),
  
  // ===== 行业 API =====
  // 获取行业列表
  getIndustries: () => apiClient.get('/industries'),
  
  // 获取行业基准数据
  getIndustryBenchmarks: (industryId) => 
    apiClient.get(`/industries/benchmarks/${industryId}`)
}

export default api
