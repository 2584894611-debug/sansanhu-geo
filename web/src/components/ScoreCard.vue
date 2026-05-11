<template>
  <div class="score-card card">
    <div class="main-score">
      <div class="score-circle" :class="scoreClass">
        <span class="score-value">{{ score }}</span>
        <span class="score-label">GEO评分</span>
      </div>
    </div>
    
    <div class="sub-scores">
      <div class="sub-score-item">
        <span class="sub-score-icon">👁️</span>
        <span class="sub-score-name">可见度</span>
        <span class="sub-score-value">{{ visibilityScore }}</span>
      </div>
      <div class="sub-score-item">
        <span class="sub-score-icon">👍</span>
        <span class="sub-score-name">推荐度</span>
        <span class="sub-score-value">{{ recommendationScore }}</span>
      </div>
      <div class="sub-score-item">
        <span class="sub-score-icon">💬</span>
        <span class="sub-score-name">情感倾向</span>
        <span class="sub-score-value">{{ sentimentScore }}</span>
      </div>
    </div>
    
    <div class="sentiment-info">
      <span class="sentiment-label">用户情绪：</span>
      <span class="sentiment-value" :class="sentimentClass">{{ sentiment }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: {
    type: Number,
    default: 0
  },
  visibilityScore: {
    type: Number,
    default: 0
  },
  recommendationScore: {
    type: Number,
    default: 0
  },
  sentimentScore: {
    type: Number,
    default: 0
  },
  sentiment: {
    type: String,
    default: '中性'
  }
})

const scoreClass = computed(() => {
  if (props.score >= 80) return 'excellent'
  if (props.score >= 60) return 'good'
  if (props.score >= 40) return 'average'
  return 'poor'
})

const sentimentClass = computed(() => {
  if (props.sentiment.includes('正面') || props.sentiment.includes('积极')) return 'positive'
  if (props.sentiment.includes('负面') || props.sentiment.includes('消极')) return 'negative'
  return 'neutral'
})
</script>

<style scoped>
.score-card {
  text-align: center;
  padding: 2rem;
}

.main-score {
  margin-bottom: 2rem;
}

.score-circle {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--bg-light) 0%, #fff 100%);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.score-circle:hover {
  transform: scale(1.05);
}

.score-circle.excellent {
  background: linear-gradient(135deg, #48bb78 0%, #68d391 100%);
  color: white;
}

.score-circle.good {
  background: linear-gradient(135deg, #4299e1 0%, #63b3ed 100%);
  color: white;
}

.score-circle.average {
  background: linear-gradient(135deg, #ed8936 0%, #f6ad55 100%);
  color: white;
}

.score-circle.poor {
  background: linear-gradient(135deg, #e53e3e 0%, #fc8181 100%);
  color: white;
}

.score-value {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 0.875rem;
  opacity: 0.9;
  margin-top: 0.5rem;
}

.sub-scores {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.sub-score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
}

.sub-score-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.sub-score-name {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}

.sub-score-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.sentiment-info {
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.sentiment-label {
  color: var(--text-secondary);
}

.sentiment-value {
  font-weight: 600;
}

.sentiment-value.positive {
  color: #48bb78;
}

.sentiment-value.neutral {
  color: #718096;
}

.sentiment-value.negative {
  color: #e53e3e;
}

@media (max-width: 480px) {
  .sub-scores {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }
  
  .sub-score-item {
    padding: 0.75rem 0.5rem;
  }
  
  .sub-score-icon {
    font-size: 1.25rem;
  }
  
  .sub-score-name {
    font-size: 0.625rem;
  }
  
  .sub-score-value {
    font-size: 1.25rem;
  }
}
</style>
