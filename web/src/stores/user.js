import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  const isPremium = ref(false)
  const todayUsage = ref(0)
  const remaining = ref(1)
  const token = ref('')
  const isLoading = ref(false)
  
  // 计算属性
  const canAnalyze = computed(() => remaining.value !== 0 || isPremium.value)
  
  // 方法
  async function checkStatus() {
    try {
      isLoading.value = true
      const response = await api.getUserStatus()
      const data = response.data
      
      isPremium.value = data.is_premium
      todayUsage.value = data.today_usage
      remaining.value = data.remaining === -1 ? Infinity : data.remaining
      token.value = data.token
      
      // 保存到本地存储
      localStorage.setItem('geo_premium', data.is_premium ? '1' : '0')
    } catch (error) {
      console.error('获取用户状态失败:', error)
      // 使用默认值
      remaining.value = 1
    } finally {
      isLoading.value = false
    }
  }
  
  async function activatePremium(tokenStr) {
    try {
      isLoading.value = true
      const response = await api.activatePremium(tokenStr)
      
      if (response.data.success) {
        isPremium.value = true
        remaining.value = Infinity
        localStorage.setItem('geo_premium', '1')
        return { success: true }
      }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || '激活失败' }
    } finally {
      isLoading.value = false
    }
  }
  
  function decrementUsage() {
    if (remaining.value !== Infinity && remaining.value > 0) {
      remaining.value--
    }
  }
  
  return {
    isPremium,
    todayUsage,
    remaining,
    token,
    isLoading,
    canAnalyze,
    checkStatus,
    activatePremium,
    decrementUsage
  }
})
