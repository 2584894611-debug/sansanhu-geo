<template>
  <div class="diagnosis-list card">
    <div class="card-header">
      <h3 class="card-title">🔍 问题诊断</h3>
      <span class="diagnosis-count">{{ displayList.length }} 项</span>
    </div>
    
    <ul class="diagnosis-items">
      <li v-for="(item, index) in displayList" :key="index" class="diagnosis-item">
        <div class="diagnosis-icon" :class="getIconClass(item.type)">
          {{ getIcon(item.type) }}
        </div>
        <div class="diagnosis-content">
          <span class="diagnosis-type">{{ item.type }}</span>
          <p class="diagnosis-desc">{{ item.description }}</p>
        </div>
      </li>
    </ul>
    
    <div v-if="!isFull && hasMore" class="more-indicator">
      <span>还有 {{ remaining }} 项问题未显示</span>
    </div>
    
    <div v-if="!isFull" class="unlock-section">
      <p class="unlock-hint">解锁完整诊断报告，查看全部问题</p>
      <button class="btn btn-primary" @click="$emit('unlock')">
        🔓 解锁完整报告
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  limit: {
    type: Number,
    default: 3
  },
  isFull: {
    type: Boolean,
    default: false
  }
})

defineEmits(['unlock'])

const displayList = computed(() => {
  if (props.isFull) return props.items
  return props.items.slice(0, props.limit)
})

const hasMore = computed(() => props.items.length > props.limit)
const remaining = computed(() => props.items.length - props.limit)

function getIcon(type) {
  const icons = {
    '可见度不足': '👁️',
    '内容缺失': '📝',
    '情感偏差': '💭',
    '关键词薄弱': '🔑',
    '内容深度不足': '📚',
    '品牌认知低': '🏷️',
    '竞品劣势': '⚔️',
    '用户体验': '👤',
    'default': '❓'
  }
  return icons[type] || icons.default
}

function getIconClass(type) {
  const classes = {
    '可见度不足': 'icon-blue',
    '内容缺失': 'icon-purple',
    '情感偏差': 'icon-orange',
    '关键词薄弱': 'icon-teal',
    '内容深度不足': 'icon-indigo',
    'default': 'icon-gray'
  }
  return classes[type] || classes.default
}
</script>

<style scoped>
.diagnosis-list {
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

.diagnosis-count {
  font-size: 0.875rem;
  color: var(--text-secondary);
  background: var(--bg-light);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.diagnosis-items {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.diagnosis-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
  transition: transform 0.2s;
}

.diagnosis-item:hover {
  transform: translateX(4px);
}

.diagnosis-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1.25rem;
}

.icon-blue {
  background: rgba(66, 153, 225, 0.1);
}

.icon-purple {
  background: rgba(128, 90, 213, 0.1);
}

.icon-orange {
  background: rgba(237, 137, 54, 0.1);
}

.icon-teal {
  background: rgba(49, 151, 149, 0.1);
}

.icon-indigo {
  background: rgba(76, 81, 191, 0.1);
}

.icon-gray {
  background: rgba(113, 128, 150, 0.1);
}

.diagnosis-content {
  flex: 1;
}

.diagnosis-type {
  font-weight: 600;
  color: var(--text-primary);
  display: block;
  margin-bottom: 0.25rem;
}

.diagnosis-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.more-indicator {
  text-align: center;
  padding: 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.unlock-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border-color);
  text-align: center;
}

.unlock-hint {
  color: var(--text-secondary);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}
</style>
