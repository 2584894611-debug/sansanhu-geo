<template>
  <div class="monitor-page">
    <div class="page-header">
      <h1 class="page-title">📈 订阅监测</h1>
      <p class="page-subtitle">追踪品牌GEO评分变化，掌握竞品动态</p>
    </div>
    
    <!-- 添加监测弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content card">
        <h3 class="modal-title">添加监测品牌</h3>
        <div class="form-group">
          <label class="form-label">品牌名称</label>
          <input 
            v-model="newBrand"
            type="text" 
            class="input"
            placeholder="输入要监测的品牌名称"
          />
        </div>
        <div class="form-group">
          <label class="form-label">所属行业</label>
          <select v-model="newIndustryId" class="select">
            <option value="catering">🍜 餐饮美食</option>
            <option value="retail">🛒 零售商业</option>
            <option value="tourism">🏛️ 文化旅游</option>
            <option value="education">📚 教育培训</option>
            <option value="medical">🏥 医疗健康</option>
            <option value="tech">💻 科技互联网</option>
            <option value="realestate">🏠 房产家居</option>
            <option value="automotive">🚗 汽车出行</option>
            <option value="finance">💰 金融保险</option>
            <option value="service">🔧 生活服务</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">监测频率</label>
          <select v-model="newFrequency" class="select">
            <option value="daily">每日监测</option>
            <option value="weekly">每周监测</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showAddModal = false">取消</button>
          <button class="btn btn-primary" @click="handleAddBrand" :disabled="!newBrand.trim()">添加</button>
        </div>
      </div>
    </div>
    
    <!-- 趋势详情弹窗 -->
    <div v-if="selectedSubscription" class="modal-overlay" @click.self="selectedSubscription = null">
      <div class="modal-content card trend-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ selectedSubscription.brand }} - 评分趋势</h3>
          <button class="close-btn" @click="selectedSubscription = null">×</button>
        </div>
        <div class="frequency-selector">
          <button 
            class="freq-btn" 
            :class="{ active: trendDays === 7 }" 
            @click="trendDays = 7; loadTrendData()"
          >近7天</button>
          <button 
            class="freq-btn" 
            :class="{ active: trendDays === 30 }" 
            @click="trendDays = 30; loadTrendData()"
          >近30天</button>
          <button 
            class="freq-btn" 
            :class="{ active: trendDays === 90 }" 
            @click="trendDays = 90; loadTrendData()"
          >近90天</button>
        </div>
        <div ref="trendChartContainer" class="trend-chart"></div>
        <div class="trend-stats">
          <div class="stat-item">
            <span class="stat-label">最新评分</span>
            <span class="stat-value">{{ selectedSubscription.latest_score || '-' }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">评分变化</span>
            <span class="stat-value" :class="getChangeClass(selectedSubscription.score_change)">
              {{ selectedSubscription.score_change > 0 ? '+' : '' }}{{ selectedSubscription.score_change || 0 }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">监测频率</span>
            <span class="stat-value">{{ selectedSubscription.frequency === 'daily' ? '每日' : '每周' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="monitor-content">
      <div class="monitor-grid">
        <!-- 监测列表 -->
        <div class="monitor-list-section card">
          <div class="section-header">
            <h3 class="section-title">我的监测</h3>
            <button class="btn btn-primary btn-sm" @click="showAddModal = true">
              + 添加品牌
            </button>
          </div>
          
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          
          <div v-else-if="subscriptions.length === 0" class="empty-state">
            <div class="empty-icon">📊</div>
            <p>暂无监测品牌</p>
            <button class="btn btn-primary" @click="showAddModal = true">添加第一个品牌</button>
          </div>
          
          <div v-else class="subscription-list">
            <div 
              v-for="sub in subscriptions" 
              :key="sub.id"
              class="subscription-item"
              @click="selectSubscription(sub)"
            >
              <div class="sub-info">
                <span class="sub-brand">{{ sub.brand }}</span>
                <span class="sub-industry">{{ sub.industry }}</span>
              </div>
              <div class="sub-score">
                <span class="score-value">{{ sub.latest_score || '-' }}</span>
                <span 
                  v-if="sub.score_change !== 0" 
                  class="score-change"
                  :class="getChangeClass(sub.score_change)"
                >
                  {{ sub.score_change > 0 ? '↑' : '↓' }}{{ Math.abs(sub.score_change) }}
                </span>
              </div>
              <div class="sub-actions" @click.stop>
                <select 
                  class="freq-select" 
                  :value="sub.frequency"
                  @change="handleFrequencyChange(sub, $event)"
                >
                  <option value="daily">每日</option>
                  <option value="weekly">每周</option>
                </select>
                <button class="delete-btn" @click="handleDelete(sub.id)" title="删除">🗑️</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 预警信息 -->
        <div class="alerts-section card">
          <h3 class="section-title">📢 最新预警</h3>
          <div v-if="alerts.length > 0" class="alerts-list">
            <div 
              v-for="alert in alerts" 
              :key="alert.id"
              class="alert-item"
              :class="alert.alert_type"
            >
              <span class="alert-icon">{{ alert.alert_type === 'rise' ? '📈' : '📉' }}</span>
              <div class="alert-content">
                <span class="alert-brand">{{ alert.brand }}</span>
                <span class="alert-message">{{ alert.message }}</span>
              </div>
              <span class="alert-time">{{ formatDate(alert.created_at) }}</span>
            </div>
          </div>
          <div v-else class="empty-alerts">
            <p>暂无预警信息</p>
          </div>
        </div>
      </div>
      
      <!-- 趋势图表区域 -->
      <div v-if="selectedSubscription" class="quick-trend card">
        <h3 class="section-title">{{ selectedSubscription.brand }} - 评分趋势</h3>
        <div ref="quickChartContainer" class="quick-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'
import * as echarts from 'echarts'

const userStore = useUserStore()

const subscriptions = ref([])
const alerts = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const selectedSubscription = ref(null)
const trendDays = ref(30)
const trendData = ref([])

const newBrand = ref('')
const newIndustryId = ref('tech')
const newFrequency = ref('daily')

const quickChartContainer = ref(null)
const trendChartContainer = ref(null)
let quickChart = null
let trendChart = null

onMounted(async () => {
  await userStore.checkStatus()
  await loadSubscriptions()
  await loadAlerts()
})

watch(selectedSubscription, async (sub) => {
  if (sub) {
    await loadTrendData()
    await nextTick()
    initTrendChart()
  }
})

async function loadSubscriptions() {
  loading.value = true
  try {
    const response = await api.getMonitors()
    subscriptions.value = response.data.data || []
  } catch (error) {
    console.error('加载监测列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadAlerts() {
  try {
    const response = await api.getAlerts(null, 10)
    alerts.value = response.data.data || []
  } catch (error) {
    console.error('加载预警失败:', error)
  }
}

async function loadTrendData() {
  if (!selectedSubscription.value) return
  try {
    const response = await api.getMonitorHistory(selectedSubscription.value.id, trendDays.value)
    trendData.value = response.data.data || []
    selectedSubscription.value.history = trendData.value
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    trendData.value = []
  }
}

async function handleAddBrand() {
  if (!newBrand.value.trim()) return
  
  try {
    const industryMap = {
      'catering': '餐饮美食', 'retail': '零售商业', 'tourism': '文化旅游',
      'education': '教育培训', 'medical': '医疗健康', 'tech': '科技互联网',
      'realestate': '房产家居', 'automotive': '汽车出行', 'finance': '金融保险',
      'service': '生活服务'
    }
    
    await api.createMonitor({
      brand: newBrand.value.trim(),
      industry: industryMap[newIndustryId.value] || '通用',
      industry_id: newIndustryId.value,
      frequency: newFrequency.value
    })
    
    showAddModal.value = false
    newBrand.value = ''
    await loadSubscriptions()
  } catch (error) {
    console.error('添加监测品牌失败:', error)
    alert(error.response?.data?.detail || '添加失败')
  }
}

async function handleDelete(subscriptionId) {
  if (!confirm('确定要删除该监测吗？')) return
  
  try {
    await api.deleteMonitor(subscriptionId)
    await loadSubscriptions()
    if (selectedSubscription.value?.id === subscriptionId) {
      selectedSubscription.value = null
    }
  } catch (error) {
    console.error('删除监测失败:', error)
  }
}

async function handleFrequencyChange(sub, event) {
  const newFrequency = event.target.value
  try {
    await api.updateMonitor(sub.id, { frequency: newFrequency })
    await loadSubscriptions()
  } catch (error) {
    console.error('更新频率失败:', error)
  }
}

function selectSubscription(sub) {
  selectedSubscription.value = sub
}

function initTrendChart() {
  if (!trendChartContainer.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartContainer.value)
  
  const dates = trendData.value.map(d => {
    const date = new Date(d.created_at)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }).reverse()
  
  const scores = trendData.value.map(d => d.geo_score).reverse()
  const changes = trendData.value.map(d => d.score_change || 0).reverse()
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        const change = changes[params[0].dataIndex]
        return `${data.axisValue}<br/>GEO评分: ${data.value}<br/>变化: ${change > 0 ? '+' : ''}${change}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        color: '#666'
      }
    },
    series: [
      {
        name: 'GEO评分',
        type: 'line',
        smooth: true,
        data: scores,
        lineStyle: {
          color: '#D4AF37',
          width: 3
        },
        itemStyle: {
          color: '#D4AF37'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(212, 175, 55, 0.3)' },
              { offset: 1, color: 'rgba(212, 175, 55, 0)' }
            ]
          }
        },
        markPoint: {
          data: [
            { type: 'max', name: '最高分' },
            { type: 'min', name: '最低分' }
          ]
        }
      }
    ]
  }
  
  trendChart.setOption(option)
  
  window.addEventListener('resize', () => {
    trendChart?.resize()
  })
}

function getChangeClass(change) {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.monitor-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.monitor-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.monitor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subscription-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.subscription-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.subscription-item:hover {
  background: rgba(212, 175, 55, 0.1);
}

.sub-info {
  flex: 1;
}

.sub-brand {
  font-weight: 600;
  display: block;
  color: var(--text-primary);
}

.sub-industry {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.sub-score {
  text-align: center;
  margin: 0 1rem;
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-color);
  display: block;
}

.score-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.change-positive {
  color: #48bb78;
}

.change-negative {
  color: #e53e3e;
}

.sub-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.freq-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.75rem;
  background: white;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.delete-btn:hover {
  opacity: 1;
}

.alerts-section {
  padding: 1.5rem;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-content {
  flex: 1;
}

.alert-brand {
  font-weight: 600;
  display: block;
  color: var(--text-primary);
}

.alert-message {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.alert-time {
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.5);
}

.empty-alerts {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  padding: 2rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* 趋势弹窗 */
.trend-modal {
  max-width: 700px;
}

.frequency-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.freq-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.freq-btn.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.trend-chart {
  width: 100%;
  height: 300px;
}

.trend-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.quick-trend {
  padding: 1.5rem;
}

.quick-chart {
  width: 100%;
  height: 250px;
}

@media (max-width: 768px) {
  .monitor-grid {
    grid-template-columns: 1fr;
  }
  
  .subscription-item {
    flex-wrap: wrap;
  }
  
  .sub-actions {
    width: 100%;
    justify-content: space-between;
    margin-top: 0.5rem;
  }
}
</style>
