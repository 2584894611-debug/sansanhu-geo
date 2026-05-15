<template>
  <div class="analyze-form card">
    <div class="form-group">
      <label class="form-label">品牌名称</label>
      <input 
        v-model="form.brand"
        type="text" 
        class="input"
        placeholder="输入要分析的品牌名称"
        :disabled="loading"
        @keyup.enter="handleAnalyze"
      />
    </div>
    
    <div class="form-group">
      <label class="form-label">所属行业</label>
      <select v-model="form.industry" class="select" :disabled="loading">
        <option value="通用">通用</option>
        <option value="科技">科技</option>
        <option value="金融">金融</option>
        <option value="教育">教育</option>
        <option value="医疗健康">医疗健康</option>
        <option value="零售">零售</option>
        <option value="餐饮">餐饮</option>
        <option value="旅游">旅游</option>
        <option value="房地产">房地产</option>
        <option value="制造业">制造业</option>
        <option value="媒体娱乐">媒体娱乐</option>
        <option value="其他">其他</option>
      </select>
    </div>
    
    <div class="form-actions">
      <button 
        class="btn btn-primary analyze-btn"
        :disabled="!canSubmit || loading"
        @click="handleAnalyze"
      >
        <span v-if="loading" class="loading-spinner small"></span>
        <span v-else>🔍</span>
        {{ loading ? '分析中...' : '一键分析' }}
      </button>
      
      <div v-if="!userStore.canAnalyze && !userStore.isPremium" class="limit-warning">
        今日免费次数已用完
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'

const emit = defineEmits(['analyzed', 'error'])

const userStore = useUserStore()

const form = ref({
  brand: '',
  industry: '通用'
})

const loading = ref(false)
const error = ref('')

const canSubmit = computed(() => {
  return form.value.brand.trim().length >= 2 && userStore.canAnalyze
})

async function handleAnalyze() {
  if (!canSubmit.value || loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.analyze({
      type: 'brand_analysis',
      brand: form.value.brand.trim(),
      industry: form.value.industry
    })
    
    if (response.data.success) {
      userStore.decrementUsage()
      emit('analyzed', response.data.data)
    } else {
      error.value = response.data.error || '分析失败，请稍后重试'
      emit('error', error.value)
    }
  } catch (err) {
    if (err.response?.status === 429) {
      error.value = '今日免费次数已用完，请明天再来或升级付费版'
    } else {
      error.value = err.response?.data?.detail || '网络错误，请检查连接后重试'
    }
    emit('error', error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.analyze-form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.analyze-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.125rem;
}

.analyze-btn .loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.limit-warning {
  text-align: center;
  color: #e53e3e;
  font-size: 0.875rem;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(229, 62, 62, 0.1);
  border-radius: var(--radius-sm);
  color: #e53e3e;
  font-size: 0.875rem;
  text-align: center;
}
</style>
