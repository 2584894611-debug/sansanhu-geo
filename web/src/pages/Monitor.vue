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
      <div class="monitor-grid">
        <div class="brand-selector card">
          <h3 class="section-title">选择品牌</h3>
          <select v-model="selectedBrand" class="select" @change="loadTrend">
            <option value="">请选择品牌</option>
            <option v-for="brand in watchedBrands" :key="brand" :value="brand">
              {{ brand }}
            </option>
          </select>
          <button class="btn btn-secondary add-brand-btn" @click="showAddBrand = true">
            + 添加品牌
          </button>
        </div>
        
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
      
      <div class="chart-section card">
        <h3 class="section-title">评分趋势</h3>
        <div ref="chartContainer" class="chart-container"></div>
      </div>
      
      <div class="history-table card">
        <h3 class="section-title">历史记录</h3>
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>日期</th>
                <th>品牌</th>
                <th>GEO评分</th>
                <th>变化</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in historyRecords" :key="record.id">
                <td>{{ formatDate(record.created_at) }}</td>
                <td>{{ record.brand }}</td>
                <td class="score-cell">{{ record.geo_score }}</td>
                <td>
                  <span v-if="record.change !== undefined" :class="getChangeClass(record.change)">
                    {{ record.change > 0 ? '+' : '' }}{{ record.change }}
                  </span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <PaywallModal v-if="showPaywall" @close="showPaywall = false" @activated="handleActivated" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'
import * as echarts from 'echarts'
import PaywallModal from '../components/PaywallModal.vue'

const userStore = useUserStore()

const selectedBrand = ref('')
const watchedBrands = ref(['武汉万象城', '武汉国际广场', '武商集团'])
const alerts = ref([])
const historyRecords = ref([])
const chartContainer = ref(null)
const showPaywall = ref(false)
const showAddBrand = ref(false)

let chart = null

onMounted(async () => {
  await userStore.checkStatus()
  if (userStore.isPremium) {
    await loadAlerts()
    await loadHistory()
  }
})

async function loadAlerts() {
  try {
    const response = await api.getAlerts(null, 10)
    alerts.value = response.data.data || []
  } catch (error) {
    console.error('加载预警失败:', error)
  }
}

async function loadHistory() {
  try {
    const response = await api.getHistory(30)
    historyRecords.value = response.data.data || []
    
    // 为每条记录计算变化
    const brandScores = {}
    historyRecords.value.forEach(record => {
      if (record.brand) {
        if (brandScores[record.brand]) {
          record.change = record.geo_score - brandScores[record.brand]
        }
        brandScores[record.brand] = record.geo_score
      }
    })
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

async function loadTrend() {
  if (!selectedBrand.value) return
  
  try {
    const response = await api.getBrandTrend(selectedBrand.value, 30)
    const data = response.data.data || []
    renderChart(data)
  } catch (error) {
    console.error('加载趋势失败:', error)
  }
}

function renderChart(data) {
  if (!chartContainer.value) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartContainer.value)
  
  const dates = data.map(d => d.created_at?.split('T')[0] || '')
  const scores = data.map(d => d.geo_score || 0)
  
  const option = {
    tooltip: {
      trigger: 'axis'
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
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart?.resize()
  })
}

function handleActivated() {
  showPaywall.value = false
  loadAlerts()
  loadHistory()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function getChangeClass(change) {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return ''
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

.locked-notice {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
}

.lock-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.locked-notice h2 {
  color: var(--text-light);
  margin-bottom: 0.5rem;
}

.locked-notice p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1.5rem;
}

.monitor-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.brand-selector {
  padding: 1.5rem;
}

.add-brand-btn {
  width: 100%;
  margin-top: 1rem;
}

.alerts-section {
  padding: 1.5rem;
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
  color: rgba(255, 255, 255, 0.5);
}

.empty-alerts {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.chart-section {
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.history-table {
  padding: 1.5rem;
}

.table-wrapper {
  overflow-x: auto;
}

.score-cell {
  font-weight: 700;
  color: var(--primary-color);
}

.change-positive {
  color: #48bb78;
}

.change-negative {
  color: #e53e3e;
}

@media (max-width: 768px) {
  .monitor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
