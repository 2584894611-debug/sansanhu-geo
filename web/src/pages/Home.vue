<template>
  <div class="home-page">
    <div class="hero-section">
      <h1 class="page-title">GEO健康度分析</h1>
      <p class="page-subtitle">输入品牌名称，一键获取AI搜索优化分析报告</p>
    </div>
    
    <div class="content-grid">
      <div class="form-section">
        <AnalyzeForm @analyzed="handleAnalyzed" @error="handleError" />
      </div>
      
      <div v-if="currentAnalysis" class="result-section">
        <ScoreCard 
          :score="currentAnalysis.geo_score"
          :visibility-score="currentAnalysis.visibility_score"
          :recommendation-score="currentAnalysis.recommendation_score"
          :sentiment-score="currentAnalysis.sentiment_score"
          :sentiment="currentAnalysis.sentiment"
        />
        
        <div class="quick-actions">
          <button class="btn btn-secondary" @click="viewFullReport">
            查看完整报告 →
          </button>
        </div>
      </div>
      
      <div v-else class="placeholder-section">
        <div class="placeholder-icon">📊</div>
        <p>分析结果将显示在这里</p>
      </div>
    </div>
    
    <div v-if="recentAnalyses.length > 0" class="history-section">
      <h2 class="section-title">最近分析</h2>
      <div class="history-list">
        <div 
          v-for="item in recentAnalyses" 
          :key="item.id"
          class="history-item"
          @click="loadHistoryItem(item)"
        >
          <span class="history-brand">{{ item.brand }}</span>
          <span class="history-score">{{ item.geo_score }}分</span>
          <span class="history-date">{{ formatDate(item.created_at) }}</span>
        </div>
      </div>
    </div>
    
    <div class="features-section">
      <h2 class="section-title">为什么选择好易易GEO</h2>
      <div class="features-grid">
        <div class="feature-card">
          <span class="feature-icon">⚡</span>
          <h3>快速分析</h3>
          <p>一键分析，即时获取GEO评分和建议</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">🎯</span>
          <h3>精准诊断</h3>
          <p>AI驱动的品牌健康度诊断</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">📈</span>
          <h3>趋势追踪</h3>
          <p>持续监测评分变化</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">💡</span>
          <h3>优化建议</h3>
          <p>针对性的GEO优化方案</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AnalyzeForm from '../components/AnalyzeForm.vue'
import ScoreCard from '../components/ScoreCard.vue'
import api from '../api'

const router = useRouter()

const currentAnalysis = ref(null)
const recentAnalyses = ref([])

onMounted(async () => {
  await loadHistory()
})

async function loadHistory() {
  try {
    const response = await api.getHistory(5)
    recentAnalyses.value = response.data.data || []
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

function handleAnalyzed(data) {
  currentAnalysis.value = data
  loadHistory()
}

function handleError(error) {
  console.error('分析错误:', error)
}

function viewFullReport() {
  if (currentAnalysis.value) {
    router.push({
      name: 'Report',
      params: { id: 'latest' },
      query: { data: JSON.stringify(currentAnalysis.value) }
    })
  }
}

function loadHistoryItem(item) {
  // 重新组装数据
  const data = {
    brand_name: item.brand,
    industry: item.industry,
    geo_score: item.geo_score,
    visibility_score: item.visibility_score,
    recommendation_score: item.recommendation_score,
    sentiment_score: item.sentiment_score
  }
  
  try {
    const diagnosis = JSON.parse(item.diagnosis_data || '[]')
    const recommendations = JSON.parse(item.recommendations || '[]')
    data.diagnosis = diagnosis
    data.recommendations = recommendations
  } catch (e) {}
  
  currentAnalysis.value = data
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  opacity: 0.8;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.placeholder-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  padding: 3rem;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.quick-actions {
  margin-top: 1rem;
  text-align: center;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-light);
  margin-bottom: 1rem;
}

.history-section {
  margin-bottom: 3rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.history-brand {
  flex: 1;
  font-weight: 500;
}

.history-score {
  font-weight: 700;
  color: var(--accent-color);
}

.history-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
}

.features-section {
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, background 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.1);
}

.feature-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.75rem;
}

.feature-card h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-light);
}

.feature-card p {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
}
</style>
