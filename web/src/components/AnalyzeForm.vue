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
      
      <!-- 一级行业选择 -->
      <select 
        v-model="selectedPrimaryId" 
        class="select"
        :disabled="loading"
        @change="onPrimaryChange"
      >
        <option value="">请选择行业大类</option>
        <option 
          v-for="industry in industries" 
          :key="industry.id" 
          :value="industry.id"
        >
          {{ industry.name }}
        </option>
      </select>
      
      <!-- 二级行业选择（有子行业时显示） -->
      <select 
        v-if="currentPrimary && currentPrimary.children && currentPrimary.children.length > 0"
        v-model="form.industry"
        class="select sub-select"
        :disabled="loading"
      >
        <option value="">请选择子行业</option>
        <option 
          v-for="child in currentPrimary.children" 
          :key="child.id" 
          :value="child.name"
        >
          {{ child.name }}
        </option>
      </select>
      
      <div v-if="form.industry && industryBenchmark" class="benchmark-tip">
        行业基准分: {{ industryBenchmark }}分
      </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'

const emit = defineEmits(['analyzed', 'error'])

const userStore = useUserStore()

const form = ref({
  brand: '',
  industry: ''
})

const selectedPrimaryId = ref('')
const industries = ref([])
const loading = ref(false)
const error = ref('')

// 行业基准分映射
const benchmarkMap = {
  '餐饮美食': 73, '商场': 70, '零售百货': 70, '服饰鞋包': 70,
  '本地生活服务': 71, '文旅休闲': 68, '快消品': 72,
  '食品饮料': 72, '日化美妆': 72, '母婴': 72,
  '互联网服务': 75, '电商': 75, '游戏': 75, '社交': 75, '工具': 75,
  '传媒广告': 72, '房地产及家居': 68, '教育培训': 66,
  '医疗健康': 60, '金融服务': 65, '汽车交通': 70,
  '工业制造': 62, '能源化工': 58, '政务及公共事业': 55
}

const currentPrimary = computed(() => {
  if (!selectedPrimaryId.value) return null
  return industries.value.find(ind => ind.id === selectedPrimaryId.value) || null
})

const industryBenchmark = computed(() => {
  return benchmarkMap[form.value.industry] || 50
})

const canSubmit = computed(() => {
  return form.value.brand.trim().length >= 2 && form.value.industry && userStore.canAnalyze
})

function onPrimaryChange() {
  const primary = currentPrimary.value
  if (primary) {
    // 如果没有子行业，直接选中一级
    if (!primary.children || primary.children.length === 0) {
      form.value.industry = primary.name
    } else {
      // 有子行业，清空子行业选择
      form.value.industry = ''
    }
  }
}

// 监听 industry 变化（用户选择子行业时）
watch(() => form.value.industry, (newVal) => {
  if (newVal && currentPrimary.value && currentPrimary.value.children) {
    const found = currentPrimary.value.children.find(c => c.name === newVal)
    if (found) {
      selectedPrimaryId.value = currentPrimary.value.id
    }
  }
})

async function loadIndustries() {
  try {
    const response = await api.getIndustries()
    if (response.data.success) {
      industries.value = response.data.data
    }
  } catch (err) {
    console.error('加载行业列表失败:', err)
  }
}

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

onMounted(() => {
  loadIndustries()
})
</script>

<style scoped>
.analyze-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: #4f46e5;
}

.select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.select:focus {
  outline: none;
  border-color: #4f46e5;
}

.sub-select {
  margin-top: 10px;
}

.benchmark-tip {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  color: #0369a1;
  font-size: 14px;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analyze-btn {
  width: 100%;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 600;
}

.limit-warning {
  text-align: center;
  color: #dc2626;
  font-size: 14px;
}

.error-message {
  margin-top: 12px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
