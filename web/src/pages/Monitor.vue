<template>
  <div class="monitor-page">
    <div class="page-header">
      <h1 class="page-title">📈 效果监测</h1>
      <p class="page-subtitle">追踪品牌GEO评分变化，掌握竞品动态</p>
    </div>
    
    <div v-if="!userStore.isPremium" class="locked-notice">
      <div class="lock-icon">🔒</div>
      <h2>付费功能</h2>
      <p>效果监测需要付费版才能使用</p>
      <button class="btn btn-primary" @click="showPaywall = true">
        升级解锁
      </button>
    </div>
    
    <div v-else class="monitor-content">
      <!-- 添加监测品牌 -->
      <div class="add-monitor-section card">
        <h3 class="section-title">添加监测品牌</h3>
        <div class="add-form">
          <input 
            v-model="newBrand"
            type="text"
            class="input"
            placeholder="输入品牌名称"
            @keyup.enter="addMonitor"
          />
          <select v-model="newFrequency" class="select">
            <option value="daily">每日</option>
            <option value="weekly">每周</option>
          </select>
          <button class="btn btn-primary" @click="addMonitor" :disabled="!newBrand.trim()">
            + 添加监测
          </button>
        </div>
        <div v-if="addError" class="error-text">{{ addError }}</div>
      </div>
      
      <!-- 监测列表 -->
      <div class="monitor-list-section card">
        <h3 class="section-title">我的监测列表</h3>
        <div v-if="monitors.length === 0" class="empty-state">
          <p>暂无监测品牌，请添加</p>
        </div>
        <div v-else class="monitor-grid">
          <div 
            v-for="monitor in monitors" 
            :key="monitor.id"
            class="monitor-item"
            :class="{ active: selectedMonitor && selectedMonitor.id === monitor.id }"
            @click="selectMonitor(monitor)"
          >
            <div class="monitor-header">
              <span class="monitor-brand">{{ monitor.brand }}</span>
              <button class="delete-btn" @click.stop="deleteMonitor(monitor.id)">×</button>
            </div>
            <div class="monitor-score">
              <span class="score-value">{{ monitor.current_score || '--' }}</span>
              <span class="score-label">分</span>
            </div>
            <div class="monitor-trend" :class="getTrendClass(monitor.trend)">
              <span class="trend-icon">{{ monitor.trend > 0 ? '📈' : monitor.trend < 0 ? '📉' : '➡️' }}</span>
              <span class="trend-value">{{ monitor.trend > 0 ? '+' : '' }}{{ monitor.trend || 0 }}</span>
            </div>
            <div class="monitor-meta">
              <span class="frequency-tag">{{ monitor.frequency === 'daily' ? '每日' : '每周' }}</span>
              <span class="last-check">{{ formatDate(monitor.last_check_at) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 趋势图表 -->
      <div v-if="selectedMonitor" class="chart-section card">
        <div class="chart-header">
          <h3 class="section-title">{{ selectedMonitor.brand }} - 评分趋势</h3>
          <div class="chart-actions">
            <select v-model="chartDays" class="select small" @change="loadMonitorHistory">
              <option :value="7">近7天</option>
              <option :value="30">近30天</option>
              <option :value="90">近90天</option>
            </select>
          </div>
        </div>
        <div ref="chartContainer" class="chart-container"></div>
        <div v-if="historyData.length === 0" class="no-data">
          <p>暂无历史数据</p>
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
        <div v-else class="empty-state">
          <p>暂无预警信息</p>
        </div>
      </div>
    </div>
    
    <PaywallModal v-if="showPaywall" @close="showPaywall = false" @activated="handleActivated" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'
import * as echarts from 'echarts'
import PaywallModal from '../components/PaywallModal.vue'

const userStore = useUserStore()

const newBrand = ref('')
const newFrequency = ref('daily')
const addError = ref('')
const monitors = ref([])
const selectedMonitor = ref(null)
const historyData = ref([])
const alerts = ref([])
const chartContainer = ref(null)
const chartDays = ref(30)
const showPaywall = ref(false)

let chart = null

onMounted(async () => {
  await userStore.checkStatus()
  if (userStore.isPremium) {
    await loadMonitors()
    await loadAlerts()
  }
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
})

async function loadMonitors() {
  try {
    const response = await api.getMonitors()
    monitors.value = response.data.data || []
  } catch (error) {
    console.error('加载监测列表失败:', error)
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

async function addMonitor() {
  if (!newBrand.value.trim()) return
  
  addError.value = ''
  try {
    await api.createMonitor({
      brand: newBrand.value.trim(),
      frequency: newFrequency.value
    })
    newBrand.value = ''
    await loadMonitors()
  } catch (error) {
    addError.value = error.response?.data?.detail || '添加失败'
  }
}

async function deleteMonitor(id) {
  if (!confirm('确定要删除该监测吗？')) return
  
  try {
    await api.deleteMonitor(id)
    if (selectedMonitor.value && selectedMonitor.value.id === id) {
      selectedMonitor.value = null
      historyData.value = []
      if (chart) {
        chart.dispose()
        chart = null
      }
    }
    await loadMonitors()
  } catch (error) {
    console.error('删除监测失败:', error)
  }
}

async function selectMonitor(monitor) {
  selectedMonitor.value = monitor
  chartDays.value = 30
  await loadMonitorHistory()
}

async function loadMonitorHistory() {
  if (!selectedMonitor.value) return
  
  try {
    const response = await api.getMonitorHistory(selectedMonitor.value.id, chartDays.value)
    historyData.value = response.data.data || []
    renderChart()
  } catch (error) {
    console.error('加载历史数据失败:', error)
  }
}

function renderChart() {
  nextTick(() => {
    if (!chartContainer.value || historyData.value.length === 0) return
    
    if (chart) {
      chart.dispose()
    }
    
    chart = echarts.init(chartContainer.value)
    
    const dates = historyData.value.map(d => {
      const date = new Date(d.created_at)
      return `${date.getMonth() + 1}/${date.getDate()}`
    })
    const scores = historyData.value.map(d => d.geo_score || 0)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: (params) => {
          const p = params[0]
          return `${p.name}<br/>GEO评分: <b>${p.value}</b>`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLabel: {
          color: 'rgba(255,255,255,0.6)'
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(255,255,255,0.2)'
          }
        }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLabel: {
          color: 'rgba(255,255,255,0.6)'
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(255,255,255,0.1)'
          }
        }
      },
      series: [
        {
          name: 'GEO评分',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
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
          data: scores
        }
      ]
    }
    
    chart.setOption(option)
  })
}

function getTrendClass(trend) {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-flat'
}

function formatDate(dateStr) {
  if (!dateStr) return '未检测'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

function handleActivated() {
  showPaywall.value = false
  userStore.checkStatus()
  loadMonitors()
}
</script>

<style scoped>
.monitor-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  color: #fff;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.6);
}

.locked-notice {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius);
}

.lock-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.locked-notice h2 {
  color: #fff;
  margin-bottom: 0.5rem;
}

.locked-notice p {
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1.5rem;
}

.add-monitor-section {
  margin-bottom: 1.5rem;
}

.add-form {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.add-form .input {
  flex: 1;
}

.add-form .select {
  width: 120px;
}

.add-form .btn {
  white-space: nowrap;
}

.error-text {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.monitor-list-section {
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.monitor-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius);
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.monitor-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.monitor-item.active {
  border-color: #D4AF37;
  background: rgba(212, 175, 55, 0.1);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.monitor-brand {
  font-weight: 600;
  color: #fff;
}

.delete-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: rgba(229, 62, 62, 0.3);
  color: #e53e3e;
}

.monitor-score {
  margin-bottom: 0.5rem;
}

.score-value {
  font-size: 2rem;
  font-weight: 700;
  color: #D4AF37;
}

.score-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.monitor-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.monitor-trend.trend-up {
  color: #48bb78;
}

.monitor-trend.trend-down {
  color: #f56565;
}

.monitor-trend.trend-flat {
  color: rgba(255, 255, 255, 0.5);
}

.trend-icon {
  font-size: 1rem;
}

.trend-value {
  font-weight: 600;
}

.monitor-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.frequency-tag {
  background: rgba(212, 175, 55, 0.2);
  color: #D4AF37;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

.chart-section {
  margin-bottom: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-actions .select.small {
  width: 100px;
  padding: 0.5rem;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

.alerts-section {
  margin-bottom: 1.5rem;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
}

.alert-item.rise {
  border-left: 3px solid #48bb78;
}

.alert-item.drop {
  border-left: 3px solid #f56565;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-content {
  flex: 1;
}

.alert-brand {
  font-weight: 600;
  color: #fff;
  margin-right: 0.5rem;
}

.alert-message {
  color: rgba(255, 255, 255, 0.7);
}

.alert-time {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .add-form {
    flex-direction: column;
  }
  
  .add-form .select,
  .add-form .btn {
    width: 100%;
  }
  
  .monitor-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
