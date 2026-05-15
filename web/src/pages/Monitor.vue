<template>
  <div class="monitor-page" v-loading="pageLoading">
    <section class="dashboard-toolbar">
      <div class="brand-filter">
        <span class="filter-label">监控品牌</span>
        <el-select
          v-model="selectedBrand"
          class="brand-select"
          placeholder="选择品牌"
          size="large"
          @change="loadDashboard"
        >
          <el-option
            v-for="brand in brands"
            :key="brand.value"
            :label="brand.label"
            :value="brand.value"
          >
            <div class="brand-option">
              <span>{{ brand.label }}</span>
              <small>{{ brand.industry }} · {{ brand.latest_score }}分</small>
            </div>
          </el-option>
        </el-select>
      </div>

      <div class="toolbar-actions">
        <el-segmented
          v-model="selectedDays"
          :options="rangeOptions"
          size="large"
          @change="loadDashboard"
        />
        <el-button type="primary" :icon="Refresh" size="large" :loading="refreshing" @click="refreshDashboard">
          刷新
        </el-button>
      </div>
    </section>

    <section class="metric-grid">
      <button
        v-for="metric in metricCards"
        :key="metric.key"
        class="metric-card"
        type="button"
        @click="scrollTo(metric.target)"
      >
        <div class="metric-head">
          <el-icon><component :is="metric.icon" /></el-icon>
          <span>{{ metric.label }}</span>
        </div>
        <div class="metric-value">{{ metric.value }}</div>
        <div class="metric-change" :class="metric.changeClass">
          <el-icon><component :is="metric.changeIcon" /></el-icon>
          <span>{{ metric.changeText }}</span>
        </div>
      </button>
    </section>

    <section ref="trendSection" class="dashboard-card trend-card">
      <div class="section-header">
        <div>
          <h2>品牌GEO分数趋势</h2>
          <p>{{ overview?.brand || selectedBrand }} · 叠加竞品趋势与预警标记</p>
        </div>
        <el-button :icon="FullScreen" @click="openFullscreen">全屏</el-button>
      </div>
      <div ref="trendChartRef" class="trend-chart chart-surface"></div>
    </section>

    <section class="two-column">
      <div ref="keywordSection" class="dashboard-card keyword-card">
        <div class="section-header compact">
          <h2>关键词渗透率</h2>
          <el-tag type="success" effect="plain">
            {{ keywordData?.summary?.hits || 0 }}/{{ keywordData?.summary?.total || 50 }}
          </el-tag>
        </div>
        <div class="keyword-cloud" aria-label="关键词词云">
          <span
            v-for="word in keywordCloud"
            :key="word.name"
            class="cloud-word"
            :style="word.style"
          >
            {{ word.name }}
          </span>
        </div>
        <el-table :data="keywordRows" size="small" class="compact-table" :header-cell-style="tableHeaderStyle">
          <el-table-column prop="keyword" label="关键词" min-width="120" />
          <el-table-column prop="rate" label="渗透率" width="90">
            <template #default="{ row }">{{ row.rate }}%</template>
          </el-table-column>
          <el-table-column label="趋势" width="76">
            <template #default="{ row }">
              <span class="inline-trend" :class="trendClass(row.trend)">
                {{ trendSymbol(row.trend) }}{{ Math.abs(row.trend) || '' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div ref="platformSection" class="dashboard-card platform-card">
        <div class="section-header compact">
          <h2>各AI平台品牌提及率</h2>
          <el-tag effect="plain">9个平台</el-tag>
        </div>
        <div ref="platformChartRef" class="platform-chart chart-surface"></div>
      </div>
    </section>

    <section ref="competitorSection" class="dashboard-card competitor-card">
      <div class="section-header">
        <div>
          <h2>竞品对比</h2>
          <p>本品 vs 竞品A vs 竞品B · 多维指标横向比较</p>
        </div>
        <el-button :icon="Edit">编辑</el-button>
      </div>
      <div class="competitor-layout">
        <div ref="radarChartRef" class="radar-chart chart-surface"></div>
        <div class="comparison-table-wrap">
          <el-table :data="competitorRows" border :header-cell-style="tableHeaderStyle">
            <el-table-column prop="dimension" label="维度" min-width="120" fixed />
            <el-table-column
              v-for="name in competitorNames"
              :key="name"
              :prop="name"
              :label="name"
              width="100"
              align="center"
            >
              <template #default="{ row }">
                <span :class="{ ownScore: name === selectedBrand }">{{ row[name] }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>

    <section ref="alertSection" class="dashboard-card alert-card">
      <div class="section-header">
        <div>
          <h2>预警记录</h2>
          <p>分数波动、竞品超越与平台表现变化</p>
        </div>
        <el-button :icon="Setting">设置</el-button>
      </div>
      <el-timeline class="alert-timeline">
        <el-timeline-item
          v-for="alert in alertRows"
          :key="alert.id"
          :type="alert.type"
          :timestamp="formatAlertDate(alert.date)"
          placement="top"
        >
          <div class="alert-title">{{ alert.title }}</div>
          <div class="alert-description">{{ alert.description }}</div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="alertRows.length === 0" description="当前周期暂无预警" :image-size="90" />
    </section>

    <el-dialog
      v-model="fullscreenVisible"
      title="品牌GEO分数趋势"
      fullscreen
      append-to-body
      @opened="renderFullscreenChart"
      @closed="disposeFullscreenChart"
    >
      <div ref="fullscreenChartRef" class="fullscreen-chart"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import {
  Aim,
  DataAnalysis,
  Edit,
  FullScreen,
  Minus,
  Rank,
  Refresh,
  Setting,
  TrendCharts,
  WarningFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const rangeOptions = [
  { label: '7天', value: 7 },
  { label: '30天', value: 30 },
  { label: '90天', value: 90 },
  { label: '1年', value: 365 }
]

const brands = ref([])
const selectedBrand = ref('')
const selectedDays = ref(30)
const overview = ref(null)
const keywordData = ref(null)
const platformData = ref(null)
const competitorData = ref(null)
const alertRows = ref([])
const pageLoading = ref(false)
const refreshing = ref(false)
const fullscreenVisible = ref(false)

const trendSection = ref(null)
const keywordSection = ref(null)
const platformSection = ref(null)
const competitorSection = ref(null)
const alertSection = ref(null)
const trendChartRef = ref(null)
const platformChartRef = ref(null)
const radarChartRef = ref(null)
const fullscreenChartRef = ref(null)

let trendChart = null
let platformChart = null
let radarChart = null
let fullscreenChart = null

const tableHeaderStyle = {
  background: '#F8FAFC',
  color: '#374151',
  fontWeight: 600
}

const metricCards = computed(() => {
  const metrics = overview.value?.metrics || {}
  return [
    {
      key: 'geo_score',
      label: 'GEO总分',
      value: formatMetricValue(metrics.geo_score, '72'),
      icon: TrendCharts,
      target: trendSection,
      ...formatChange(metrics.geo_score)
    },
    {
      key: 'mention_rate',
      label: 'AI平台提及率',
      value: formatMetricValue(metrics.mention_rate, '67%'),
      icon: DataAnalysis,
      target: platformSection,
      ...formatChange(metrics.mention_rate)
    },
    {
      key: 'keyword_penetration',
      label: '关键词渗透率',
      value: metrics.keyword_penetration?.display || '12/50',
      icon: Aim,
      target: keywordSection,
      ...formatChange(metrics.keyword_penetration)
    },
    {
      key: 'competitor_rank',
      label: '竞品排名',
      value: metrics.competitor_rank?.display || '第3名',
      icon: Rank,
      target: competitorSection,
      ...formatChange(metrics.competitor_rank, '名')
    }
  ]
})

const keywordRows = computed(() => keywordData.value?.table || [])

const keywordCloud = computed(() => {
  const words = keywordData.value?.cloud || []
  const max = Math.max(...words.map(item => item.value), 1)
  const min = Math.min(...words.map(item => item.value), 0)
  return words.map((item, index) => {
    const ratio = (item.value - min) / Math.max(max - min, 1)
    const size = 14 + ratio * 14
    const colors = ['#FF6B35', '#1A1A2E', '#00D4AA', '#6366F1', '#06B6D4']
    return {
      ...item,
      style: {
        fontSize: `${size}px`,
        color: colors[index % colors.length],
        fontWeight: ratio > 0.68 ? 700 : 600,
        opacity: 0.72 + ratio * 0.28
      }
    }
  })
})

const competitorRows = computed(() => competitorData.value?.table || [])
const competitorNames = computed(() => competitorData.value?.series?.map(item => item.name) || [])

onMounted(async () => {
  await userStore.checkStatus()
  await loadBrands()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeCharts()
})

async function loadBrands() {
  pageLoading.value = true
  try {
    const response = await api.getDashboardBrands()
    brands.value = response.data.data || []
    selectedBrand.value = brands.value[0]?.value || '武汉万象城'
    await loadDashboard()
  } catch (error) {
    console.error('加载仪表盘品牌失败:', error)
    ElMessage.error('加载仪表盘品牌失败')
  } finally {
    pageLoading.value = false
  }
}

async function loadDashboard() {
  if (!selectedBrand.value) return
  pageLoading.value = true
  try {
    const [overviewRes, keywordRes, platformRes, competitorRes, alertRes] = await Promise.all([
      api.getDashboardScoreTrend(selectedBrand.value, selectedDays.value),
      api.getDashboardKeywordPenetration(selectedBrand.value, selectedDays.value),
      api.getDashboardPlatformDistribution(selectedBrand.value, selectedDays.value),
      api.getDashboardCompetitorComparison(selectedBrand.value, selectedDays.value),
      api.getDashboardAlerts(selectedBrand.value, selectedDays.value)
    ])

    overview.value = overviewRes.data.data
    keywordData.value = keywordRes.data.data
    platformData.value = platformRes.data.data
    competitorData.value = competitorRes.data.data
    alertRows.value = alertRes.data.data || []

    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('加载仪表盘失败:', error)
    ElMessage.error('加载仪表盘失败')
  } finally {
    pageLoading.value = false
  }
}

async function refreshDashboard() {
  if (!selectedBrand.value) return
  refreshing.value = true
  try {
    const currentBrand = brands.value.find(item => item.value === selectedBrand.value)
    await api.refreshDashboard({
      brand: selectedBrand.value,
      industry: currentBrand?.industry || '通用'
    })
    await loadDashboard()
    ElMessage.success('仪表盘数据已刷新')
  } catch (error) {
    console.error('刷新仪表盘失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

function renderCharts() {
  renderTrendChart(trendChartRef.value, false)
  renderPlatformChart()
  renderRadarChart()
}

function renderTrendChart(container, large = false) {
  if (!container || !overview.value?.trend) return
  const target = large ? fullscreenChart : trendChart
  if (target) target.dispose()

  const chart = echarts.init(container)
  const trend = overview.value.trend
  const markPointData = trend.alert_points.map(item => ({
    coord: [item.date, item.score],
    value: `${item.change_percent}%`,
    itemStyle: { color: '#FF4757' }
  }))

  chart.setOption({
    color: ['#FF6B35', '#6366F1', '#06B6D4'],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#E5E7EB',
      borderWidth: 1,
      textStyle: { color: '#374151' },
      extraCssText: 'box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12); border-radius: 8px;'
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#374151' }
    },
    grid: {
      top: 24,
      left: 36,
      right: 24,
      bottom: 54,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trend.dates,
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisTick: { show: false },
      axisLabel: { color: '#6B7280', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { color: '#6B7280', fontSize: 12 },
      splitLine: { lineStyle: { color: '#E5E7EB', type: 'dashed' } }
    },
    series: trend.series.map((serie, index) => ({
      name: serie.name,
      type: 'line',
      smooth: true,
      data: serie.data,
      symbol: 'circle',
      symbolSize: index === 0 ? 7 : 5,
      lineStyle: {
        width: index === 0 ? 3 : 2,
        type: serie.type === 'dashed' ? 'dashed' : 'solid'
      },
      areaStyle: index === 0 ? { color: 'rgba(255, 107, 53, 0.1)' } : undefined,
      markPoint: index === 0 ? {
        symbol: 'circle',
        symbolSize: 12,
        data: markPointData
      } : undefined
    }))
  })

  if (large) {
    fullscreenChart = chart
  } else {
    trendChart = chart
  }
}

function renderPlatformChart() {
  if (!platformChartRef.value || !platformData.value?.platforms) return
  if (platformChart) platformChart.dispose()
  platformChart = echarts.init(platformChartRef.value)
  const platforms = platformData.value.platforms

  platformChart.setOption({
    grid: { top: 8, left: 74, right: 24, bottom: 20 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#FFFFFF',
      borderColor: '#E5E7EB',
      textStyle: { color: '#374151' }
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%', color: '#6B7280' },
      splitLine: { lineStyle: { color: '#E5E7EB', type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: platforms.map(item => item.name),
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { color: '#374151', fontSize: 12 }
    },
    series: [
      {
        type: 'bar',
        data: platforms.map(item => item.rate),
        barWidth: 14,
        itemStyle: {
          color: '#FF6B35',
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          color: '#374151',
          fontSize: 12
        }
      }
    ]
  })
}

function renderRadarChart() {
  if (!radarChartRef.value || !competitorData.value?.series) return
  if (radarChart) radarChart.dispose()
  radarChart = echarts.init(radarChartRef.value)

  radarChart.setOption({
    color: competitorData.value.series.map(item => item.color),
    tooltip: {
      backgroundColor: '#FFFFFF',
      borderColor: '#E5E7EB',
      textStyle: { color: '#374151' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#374151' }
    },
    radar: {
      radius: '62%',
      indicator: competitorData.value.indicators,
      axisName: { color: '#374151', fontSize: 12 },
      splitLine: { lineStyle: { color: '#E5E7EB' } },
      splitArea: { areaStyle: { color: ['#FFFFFF', '#F8FAFC'] } },
      axisLine: { lineStyle: { color: '#E5E7EB' } }
    },
    series: [
      {
        type: 'radar',
        data: competitorData.value.series.map(item => ({
          name: item.name,
          value: item.values,
          areaStyle: { opacity: item.name === selectedBrand.value ? 0.16 : 0.06 }
        }))
      }
    ]
  })
}

function renderFullscreenChart() {
  nextTick(() => renderTrendChart(fullscreenChartRef.value, true))
}

function disposeFullscreenChart() {
  if (fullscreenChart) {
    fullscreenChart.dispose()
    fullscreenChart = null
  }
}

function disposeCharts() {
  ;[trendChart, platformChart, radarChart, fullscreenChart].forEach(chart => {
    if (chart) chart.dispose()
  })
}

function resizeCharts() {
  ;[trendChart, platformChart, radarChart, fullscreenChart].forEach(chart => {
    if (chart) chart.resize()
  })
}

function openFullscreen() {
  fullscreenVisible.value = true
}

function scrollTo(targetRef) {
  targetRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function formatMetricValue(metric, fallback) {
  if (!metric) return fallback
  if (metric.display) return metric.display
  return `${metric.value}${metric.suffix || ''}`
}

function formatChange(metric, suffixOverride = null) {
  const change = metric?.change ?? 0
  const direction = metric?.direction || 'flat'
  const positive = metric?.positive
  const suffix = suffixOverride || metric?.suffix || ''
  const absChange = Math.abs(change)
  const changeText = change === 0 ? '持平 较上期' : `${absChange}${suffix} 较上期`
  return {
    changeText,
    changeClass: positive === true ? 'change-up' : positive === false ? 'change-down' : 'change-flat',
    changeIcon: direction === 'up' ? TrendCharts : direction === 'down' ? WarningFilled : Minus
  }
}

function trendClass(value) {
  if (value > 0) return 'trend-up'
  if (value < 0) return 'trend-down'
  return 'trend-flat'
}

function trendSymbol(value) {
  if (value > 0) return '↑'
  if (value < 0) return '↓'
  return '→'
}

function formatAlertDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<style scoped>
.monitor-page {
  width: min(1200px, 100%);
  margin: 0 auto;
  color: #1A1A2E;
}

.dashboard-toolbar {
  min-height: 48px;
  padding: 12px 16px;
  background: #EEF2F7;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.brand-filter,
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.brand-select {
  width: 240px;
}

.brand-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand-option small {
  color: #6B7280;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.metric-card {
  min-height: 148px;
  padding: 24px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  border-color: #FF6B35;
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(255, 107, 53, 0.14);
}

.metric-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #6B7280;
}

.metric-head .el-icon {
  color: #FF6B35;
  font-size: 18px;
}

.metric-value {
  margin-top: 14px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 32px;
  line-height: 1.2;
  font-weight: 700;
  color: #1A1A2E;
}

.metric-change {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
}

.change-up,
.trend-up {
  color: #00D4AA;
}

.change-down,
.trend-down {
  color: #FF4757;
}

.change-flat,
.trend-flat {
  color: #6B7280;
}

.dashboard-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-header.compact {
  align-items: center;
}

.section-header h2 {
  font-size: 20px;
  line-height: 1.3;
  font-weight: 600;
  color: #1A1A2E;
  margin: 0;
}

.section-header p {
  margin: 6px 0 0;
  color: #6B7280;
  font-size: 14px;
}

.chart-surface {
  width: 100%;
  min-height: 320px;
}

.trend-chart {
  height: 380px;
}

.two-column {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
}

.keyword-cloud {
  min-height: 162px;
  padding: 18px;
  margin-bottom: 18px;
  border: 1px dashed #E5E7EB;
  border-radius: 8px;
  background: #F8FAFC;
  display: flex;
  align-items: center;
  justify-content: center;
  align-content: center;
  flex-wrap: wrap;
  gap: 10px 16px;
}

.cloud-word {
  line-height: 1;
  white-space: nowrap;
}

.platform-chart {
  height: 348px;
}

.compact-table {
  width: 100%;
}

.inline-trend {
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.competitor-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(0, 1.1fr);
  gap: 24px;
  align-items: center;
}

.radar-chart {
  height: 360px;
}

.comparison-table-wrap {
  overflow-x: auto;
}

.ownScore {
  color: #FF6B35;
  font-weight: 700;
}

.alert-timeline {
  padding-top: 4px;
}

.alert-title {
  font-size: 16px;
  font-weight: 600;
  color: #1A1A2E;
}

.alert-description {
  margin-top: 6px;
  color: #6B7280;
  font-size: 14px;
}

.fullscreen-chart {
  width: 100%;
  height: calc(100vh - 110px);
}

:deep(.el-button--primary) {
  --el-button-bg-color: #FF6B35;
  --el-button-border-color: #FF6B35;
  --el-button-hover-bg-color: #F05D2C;
  --el-button-hover-border-color: #F05D2C;
  --el-button-active-bg-color: #E24F20;
  --el-button-active-border-color: #E24F20;
}

:deep(.el-segmented) {
  --el-segmented-item-selected-bg-color: #FF6B35;
  --el-segmented-item-selected-color: #FFFFFF;
}

@media (max-width: 1023px) {
  .dashboard-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar-actions {
    justify-content: space-between;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .two-column,
  .competitor-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .dashboard-toolbar,
  .brand-filter,
  .toolbar-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .brand-select {
    width: 100%;
  }

  .metric-grid {
    gap: 12px;
  }

  .metric-card,
  .dashboard-card {
    padding: 16px;
  }

  .metric-value {
    font-size: 26px;
  }

  .trend-card {
    overflow-x: auto;
  }

  .trend-chart {
    min-width: 680px;
  }

  .section-header {
    align-items: stretch;
    flex-direction: column;
  }

  .chart-surface {
    min-height: 300px;
  }
}
</style>
