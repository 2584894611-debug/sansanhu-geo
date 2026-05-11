<template>
  <div class="report-page">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载报告...</p>
    </div>
    
    <div v-else-if="!reportData" class="empty-state">
      <div class="empty-icon">📋</div>
      <h2>暂无报告数据</h2>
      <p>请先在首页进行品牌分析</p>
      <router-link to="/" class="btn btn-primary">去分析</router-link>
    </div>
    
    <div v-else class="report-content">
      <div class="report-header">
        <div class="brand-info">
          <h1 class="brand-name">{{ reportData.brand_name }}</h1>
          <span class="industry-tag">{{ reportData.industry }}</span>
        </div>
        <div class="report-meta">
          <span>分析时间: {{ formatDate(reportData._meta?.analyzed_at) }}</span>
          <span v-if="!isFullReport" class="preview-tag">预览版</span>
        </div>
      </div>
      
      <div class="report-grid">
        <div class="main-score-section">
          <ScoreCard 
            :score="reportData.geo_score"
            :visibility-score="reportData.visibility_score"
            :recommendation-score="reportData.recommendation_score"
            :sentiment-score="reportData.sentiment_score"
            :sentiment="reportData.sentiment"
          />
        </div>
        
        <div class="features-section">
          <div class="card">
            <h3 class="card-title">✨ 品牌优势</h3>
            <ul class="feature-list">
              <li v-for="(item, index) in reportData.strengths" :key="index">
                <span class="check-icon">✓</span>
                {{ item }}
              </li>
            </ul>
          </div>
          
          <div class="card">
            <h3 class="card-title">⚠️ 待改进点</h3>
            <ul class="feature-list weakness">
              <li v-for="(item, index) in reportData.weaknesses" :key="index">
                <span class="x-icon">!</span>
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- 行业对标数据 -->
      <div v-if="industryBenchmark" class="benchmark-section card">
        <h3 class="card-title">📊 行业对标</h3>
        <div class="benchmark-content">
          <div class="benchmark-category">
            <span class="category-icon">{{ industryBenchmark.category_icon }}</span>
            <span class="category-name">{{ industryBenchmark.category_name }}</span>
          </div>
          <div class="benchmark-score">
            <div class="score-compare">
              <div class="compare-item">
                <span class="compare-label">您的评分</span>
                <span class="compare-value user">{{ reportData.geo_score }}</span>
              </div>
              <div class="compare-divider">vs</div>
              <div class="compare-item">
                <span class="compare-label">行业基准</span>
                <span class="compare-value benchmark">{{ industryBenchmark.benchmark_geo_score }}</span>
              </div>
            </div>
            <div class="compare-result" :class="getCompareClass()">
              {{ getCompareResult() }}
            </div>
          </div>
          <div class="benchmark-factors">
            <span class="factors-label">关键因素：</span>
            <span v-for="factor in industryBenchmark.key_factors" :key="factor" class="factor-tag">
              {{ factor }}
            </span>
          </div>
        </div>
      </div>
      
      <DiagnosisList 
        :items="reportData.diagnosis || []"
        :limit="3"
        :is-full="isFullReport"
        @unlock="openPaywall"
      />
      
      <CompetitorTable 
        :competitors="reportData.competitors || []"
        :is-full="isFullReport"
        @unlock="openPaywall"
      />
      
      <div class="recommendations-section card">
        <div class="card-header">
          <h3 class="card-title">💡 优化建议</h3>
          <span v-if="!isFullReport" class="limited-hint">展示前3条</span>
        </div>
        
        <div v-if="isFullReport || reportData.recommendations?.length > 0" class="recommendations-list">
          <div 
            v-for="(rec, index) in displayRecommendations" 
            :key="index"
            class="recommendation-item"
          >
            <span class="rec-number">{{ index + 1 }}</span>
            <div class="rec-content">
              <p class="rec-text">{{ rec }}</p>
            </div>
          </div>
        </div>
        
        <div v-if="!isFullReport && reportData.recommendations?.length > 3" class="unlock-prompt">
          <p>还有 {{ reportData.recommendations.length - 3 }} 条优化建议未显示</p>
          <button class="btn btn-primary" @click="openPaywall">
            🔓 解锁完整建议
          </button>
        </div>
      </div>
      
      <div v-if="isFullReport" class="action-buttons">
        <button class="btn btn-secondary">
          📥 下载报告
        </button>
        <router-link to="/" class="btn btn-primary">
          🔄 重新分析
        </router-link>
      </div>
    </div>
    
    <PaywallModal v-if="showPaywall" @close="showPaywall = false" @activated="handleActivated" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import ScoreCard from '../components/ScoreCard.vue'
import DiagnosisList from '../components/DiagnosisList.vue'
import CompetitorTable from '../components/CompetitorTable.vue'
import PaywallModal from '../components/PaywallModal.vue'

const route = useRoute()
const userStore = useUserStore()

const loading = ref(true)
const reportData = ref(null)
const showPaywall = ref(false)

// 行业分类映射
const industryCategoryMap = {
  '消费电子': { category_id: 'knowledge_gap', category_name: '知识盲区品类', category_icon: '🧠', benchmark_geo_score: 45, key_factors: ['品牌权威性', '专业内容覆盖', '问答内容布局'] },
  '母婴用品': { category_id: 'knowledge_gap', category_name: '知识盲区品类', category_icon: '🧠', benchmark_geo_score: 45, key_factors: ['品牌权威性', '专业内容覆盖', '问答内容布局'] },
  '运动健身': { category_id: 'knowledge_gap', category_name: '知识盲区品类', category_icon: '🧠', benchmark_geo_score: 45, key_factors: ['品牌权威性', '专业内容覆盖', '问答内容布局'] },
  '商业地产': { category_id: 'high_value_low_freq', category_name: '低频高客单', category_icon: '💰', benchmark_geo_score: 50, key_factors: ['口碑管理', '案例展示', '专业背书', '用户评价'] },
  '文旅': { category_id: 'high_value_low_freq', category_name: '低频高客单', category_icon: '💰', benchmark_geo_score: 50, key_factors: ['口碑管理', '案例展示', '专业背书', '用户评价'] },
  '装修建材': { category_id: 'high_value_low_freq', category_name: '低频高客单', category_icon: '💰', benchmark_geo_score: 50, key_factors: ['口碑管理', '案例展示', '专业背书', '用户评价'] },
  '婚纱摄影': { category_id: 'high_value_low_freq', category_name: '低频高客单', category_icon: '💰', benchmark_geo_score: 50, key_factors: ['口碑管理', '案例展示', '专业背书', '用户评价'] },
  '月子中心': { category_id: 'high_value_low_freq', category_name: '低频高客单', category_icon: '💰', benchmark_geo_score: 50, key_factors: ['口碑管理', '案例展示', '专业背书', '用户评价'] },
  '智能硬件': { category_id: 'innovation_niche', category_name: '长尾痛点微创新', category_icon: '🔍', benchmark_geo_score: 40, key_factors: ['产品差异化', '使用场景内容', '用户评测'] },
  '个护创新': { category_id: 'innovation_niche', category_name: '长尾痛点微创新', category_icon: '🔍', benchmark_geo_score: 40, key_factors: ['产品差异化', '使用场景内容', '用户评测'] },
  '小家电': { category_id: 'innovation_niche', category_name: '长尾痛点微创新', category_icon: '🔍', benchmark_geo_score: 40, key_factors: ['产品差异化', '使用场景内容', '用户评测'] },
  'SaaS软件': { category_id: 'to_b_business', category_name: 'To B业务', category_icon: '🏢', benchmark_geo_score: 55, key_factors: ['行业解决方案', '客户案例', '技术文档', '专业资质'] },
  '工业设备': { category_id: 'to_b_business', category_name: 'To B业务', category_icon: '🏢', benchmark_geo_score: 55, key_factors: ['行业解决方案', '客户案例', '技术文档', '专业资质'] },
  '企业服务': { category_id: 'to_b_business', category_name: 'To B业务', category_icon: '🏢', benchmark_geo_score: 55, key_factors: ['行业解决方案', '客户案例', '技术文档', '专业资质'] }
}

const industryBenchmark = computed(() => {
  if (!reportData.value?.industry) return null
  return industryCategoryMap[reportData.value.industry] || {
    category_id: 'general',
    category_name: '通用行业',
    category_icon: '📋',
    benchmark_geo_score: 50,
    key_factors: ['品牌认知', '内容质量', '用户口碑']
  }
})

const isFullReport = computed(() => {
  return userStore.isPremium || reportData.value?._meta?.is_full_report
})

const displayRecommendations = computed(() => {
  if (!reportData.value?.recommendations) return []
  if (isFullReport.value) return reportData.value.recommendations
  return reportData.value.recommendations.slice(0, 3)
})

function getCompareClass() {
  if (!industryBenchmark.value || !reportData.value) return ''
  const diff = reportData.value.geo_score - industryBenchmark.value.benchmark_geo_score
  if (diff >= 15) return 'result-excellent'
  if (diff >= 5) return 'result-good'
  if (diff >= -10) return 'result-average'
  return 'result-poor'
}

function getCompareResult() {
  if (!industryBenchmark.value || !reportData.value) return ''
  const diff = reportData.value.geo_score - industryBenchmark.value.benchmark_geo_score
  if (diff >= 15) return '🌟 领先行业水平'
  if (diff >= 5) return '👍 高于行业平均'
  if (diff >= -10) return '➡️ 接近行业平均'
  return '📈 需重点提升'
}

onMounted(async () => {
  await loadReport()
})

async function loadReport() {
  loading.value = true
  
  try {
    // 尝试从URL参数获取数据
    if (route.query.data) {
      reportData.value = JSON.parse(route.query.data)
    } else if (route.params.id === 'latest') {
      // 获取最新的分析记录
      const { default: api } = await import('../api')
      const response = await api.getHistory(1)
      if (response.data.data?.length > 0) {
        const latest = response.data.data[0]
        reportData.value = {
          brand_name: latest.brand,
          industry: latest.industry,
          geo_score: latest.geo_score,
          visibility_score: latest.visibility_score,
          recommendation_score: latest.recommendation_score,
          sentiment_score: latest.sentiment_score,
          _meta: {
            analyzed_at: latest.created_at,
            is_full_report: latest.is_full_report === 1
          }
        }
        
        try {
          reportData.value.diagnosis = JSON.parse(latest.diagnosis_data || '[]')
          reportData.value.recommendations = JSON.parse(latest.recommendations || '[]')
        } catch (e) {}
      }
    }
  } catch (error) {
    console.error('加载报告失败:', error)
  } finally {
    loading.value = false
  }
}

function openPaywall() {
  showPaywall.value = true
}

function handleActivated() {
  // 刷新页面数据
  loadReport()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.report-page {
  max-width: 1200px;
  margin: 0 auto;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-light);
}

.loading-spinner {
  margin: 0 auto 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h2 {
  margin-bottom: 0.5rem;
}

.empty-state p {
  opacity: 0.7;
  margin-bottom: 1.5rem;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-name {
  font-size: 2rem;
  color: var(--text-light);
  margin-bottom: 0.5rem;
}

.industry-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(212, 175, 55, 0.2);
  color: var(--accent-color);
  border-radius: 20px;
  font-size: 0.875rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.preview-tag {
  padding: 0.25rem 0.5rem;
  background: rgba(237, 137, 54, 0.2);
  color: #ed8936;
  border-radius: 4px;
  font-size: 0.75rem;
}

.report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.main-score-section .card {
  padding: 0;
}

.features-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.feature-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.feature-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.check-icon {
  color: #48bb78;
  font-weight: 700;
}

.x-icon {
  color: #ed8936;
  font-weight: 700;
}

.recommendations-section {
  margin: 2rem 0;
  padding: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.limited-hint {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
}

.rec-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
  color: var(--primary-color);
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
}

.rec-content {
  flex: 1;
}

.rec-text {
  color: var(--text-primary);
  line-height: 1.6;
}

.unlock-prompt {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.05), rgba(212, 175, 55, 0.05));
  border-radius: var(--radius-md);
  margin-top: 1rem;
}

.unlock-prompt p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 行业对标样式 */
.benchmark-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
}

.benchmark-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.benchmark-category {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-icon {
  font-size: 1.5rem;
}

.category-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.benchmark-score {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius);
}

.score-compare {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.compare-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.compare-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.25rem;
}

.compare-value {
  font-size: 1.75rem;
  font-weight: 700;
}

.compare-value.user {
  color: #D4AF37;
}

.compare-value.benchmark {
  color: rgba(255, 255, 255, 0.6);
}

.compare-divider {
  color: rgba(255, 255, 255, 0.3);
  font-size: 0.875rem;
}

.compare-result {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.result-excellent {
  background: rgba(72, 187, 120, 0.2);
  color: #48bb78;
}

.result-good {
  background: rgba(72, 187, 120, 0.15);
  color: #68d391;
}

.result-average {
  background: rgba(212, 175, 55, 0.15);
  color: #f6e05e;
}

.result-poor {
  background: rgba(237, 137, 54, 0.2);
  color: #ed8936;
}

.benchmark-factors {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.factors-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

.factor-tag {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .report-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .report-meta {
    align-items: flex-start;
  }
  
  .report-grid {
    grid-template-columns: 1fr;
  }
}
</style>
