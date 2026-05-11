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
        <optgroup label="🧠 知识盲区品类">
          <option value="消费电子">消费电子</option>
          <option value="母婴用品">母婴用品</option>
          <option value="运动健身">运动健身</option>
        </optgroup>
        <optgroup label="💰 低频高客单">
          <option value="商业地产">商业地产</option>
          <option value="文旅">文旅</option>
          <option value="装修建材">装修建材</option>
          <option value="婚纱摄影">婚纱摄影</option>
          <option value="月子中心">月子中心</option>
        </optgroup>
        <optgroup label="🔍 长尾痛点微创新">
          <option value="智能硬件">智能硬件</option>
          <option value="个护创新">个护创新</option>
          <option value="小家电">小家电</option>
        </optgroup>
        <optgroup label="🏢 To B业务">
          <option value="SaaS软件">SaaS软件</option>
          <option value="工业设备">工业设备</option>
          <option value="企业服务">企业服务</option>
        </optgroup>
        <optgroup label="通用">
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
        </optgroup>
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
import { ref, computed, watch } from 'vue'
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

// 行业基准分映射
const benchmarkMap = {
  '消费电子': 45, '母婴用品': 45, '运动健身': 45,
  '商业地产': 50, '文旅': 50, '装修建材': 50, '婚纱摄影': 50, '月子中心': 50,
  '智能硬件': 40, '个护创新': 40, '小家电': 40,
  'SaaS软件': 55, '工业设备': 55, '企业服务': 55,
  '科技': 50, '金融': 50, '教育': 50, '医疗健康': 50, '零售': 50,
  '餐饮': 50, '旅游': 50, '房地产': 50, '制造业': 50, '媒体娱乐': 50, '其他': 50, '通用': 50
}

const industryBenchmark = computed(() => {
  return benchmarkMap[form.value.industry] || 50
})

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

.benchmark-tip {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #D4AF37;
  background: rgba(212, 175, 55, 0.1);
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-sm);
  display: inline-block;
}
</style>
