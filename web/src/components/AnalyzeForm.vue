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
      <select v-model="form.industryId" class="select" :disabled="loading" @change="onIndustryChange">
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
        <option value="general">通用</option>
      </select>
      <p class="industry-hint" v-if="currentIndustry">正在分析: {{ currentIndustry.name }}</p>
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
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'

const emit = defineEmits(['analyzed', 'error', 'industryChange'])

const userStore = useUserStore()

const industries = ref([])
const form = ref({
  brand: '',
  industryId: 'tech',
  industry: '科技互联网'
})

const loading = ref(false)
const error = ref('')

const currentIndustry = computed(() => {
  return industries.value.find(ind => ind.id === form.value.industryId)
})

const canSubmit = computed(() => {
  return form.value.brand.trim().length >= 2 && userStore.canAnalyze
})

onMounted(async () => {
  await loadIndustries()
})

async function loadIndustries() {
  try {
    const response = await api.getIndustries()
    industries.value = response.data.data || []
  } catch (err) {
    console.error('加载行业列表失败:', err)
    // 使用默认行业列表
    industries.value = [
      { id: 'catering', name: '餐饮美食', icon: '🍜' },
      { id: 'retail', name: '零售商业', icon: '🛒' },
      { id: 'tourism', name: '文化旅游', icon: '🏛️' },
      { id: 'education', name: '教育培训', icon: '📚' },
      { id: 'medical', name: '医疗健康', icon: '🏥' },
      { id: 'tech', name: '科技互联网', icon: '💻' },
      { id: 'realestate', name: '房产家居', icon: '🏠' },
      { id: 'automotive', name: '汽车出行', icon: '🚗' },
      { id: 'finance', name: '金融保险', icon: '💰' },
      { id: 'service', name: '生活服务', icon: '🔧' }
    ]
  }
}

function onIndustryChange() {
  const ind = currentIndustry.value
  form.value.industry = ind ? ind.name : '通用'
  emit('industryChange', { industryId: form.value.industryId, industry: form.value.industry })
}

async function handleAnalyze() {
  if (!canSubmit.value || loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await api.analyze({
      type: 'brand_analysis',
      brand: form.value.brand.trim(),
      industry: form.value.industry,
      industry_id: form.value.industryId
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

// 暴露方法供外部调用
defineExpose({
  setBrand: (brand) => { form.value.brand = brand }
})
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

.industry-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--accent-color);
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
