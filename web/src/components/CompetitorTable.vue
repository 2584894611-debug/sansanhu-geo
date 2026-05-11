<template>
  <div class="competitor-table card">
    <div class="card-header">
      <h3 class="card-title">🏆 竞品对比</h3>
      <span class="competitor-count">{{ competitors.length }} 个</span>
    </div>
    
    <div v-if="isFull" class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>品牌</th>
            <th>GEO评分</th>
            <th>优势</th>
            <th>劣势</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(comp, index) in competitors" :key="index">
            <td class="brand-name">
              <span class="rank-badge" :class="getRankClass(index)">{{ index + 1 }}</span>
              {{ comp.name }}
            </td>
            <td class="score-cell">
              <span class="score-bar">
                <span class="score-fill" :style="{ width: comp.score + '%' }"></span>
              </span>
              <span class="score-num">{{ comp.score }}</span>
            </td>
            <td class="strengths-cell">
              <span v-for="(s, i) in comp.strengths.slice(0, 2)" :key="i" class="tag tag-success">
                {{ s }}
              </span>
            </td>
            <td class="weaknesses-cell">
              <span v-for="(w, i) in comp.weaknesses.slice(0, 2)" :key="i" class="tag tag-warning">
                {{ w }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else class="locked-content">
      <div class="lock-icon">🔒</div>
      <p class="lock-message">查看完整竞品对比分析</p>
      <p class="lock-hint">升级付费版解锁竞品对比功能</p>
      <button class="btn btn-primary" @click="$emit('unlock')">
        升级解锁
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  competitors: {
    type: Array,
    default: () => []
  },
  isFull: {
    type: Boolean,
    default: false
  }
})

defineEmits(['unlock'])

function getRankClass(index) {
  const classes = ['gold', 'silver', 'bronze']
  return classes[index] || ''
}
</script>

<style scoped>
.competitor-table {
  padding: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.competitor-count {
  font-size: 0.875rem;
  color: var(--text-secondary);
  background: var(--bg-light);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table th {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table tbody tr:hover {
  background: var(--bg-light);
}

.brand-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  background: #718096;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #D4AF37, #F4D03F);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #A0AEC0, #CBD5E0);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #C97B4B, #DD9866);
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 150px;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-light);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--accent-color), var(--accent-light));
  border-radius: 4px;
  transition: width 0.3s;
}

.score-num {
  font-weight: 700;
  color: var(--primary-color);
  min-width: 30px;
}

.strengths-cell,
.weaknesses-cell {
  max-width: 200px;
}

.tag {
  margin-right: 0.25rem;
  margin-bottom: 0.25rem;
}

.locked-content {
  text-align: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, rgba(26, 54, 93, 0.05), rgba(212, 175, 55, 0.05));
  border-radius: var(--radius-md);
}

.lock-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.lock-message {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.lock-hint {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}
</style>
