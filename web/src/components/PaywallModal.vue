<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        <button class="close-btn" @click="$emit('close')">×</button>
        
        <div class="modal-header">
          <span class="premium-icon">⭐</span>
          <h2>升级付费版</h2>
          <p>解锁全部功能，获得更专业的分析服务</p>
        </div>
        
        <div class="features-grid">
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>无限次分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>完整诊断报告</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>竞品对比分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>详细优化建议</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>效果监测追踪</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✅</span>
            <span>报告下载</span>
          </div>
        </div>
        
        <div class="activation-section">
          <label class="activation-label">输入激活码</label>
          <div class="activation-input-group">
            <input 
              v-model="activationCode"
              type="text"
              class="input activation-input"
              placeholder="请输入激活码"
              :disabled="loading"
            />
            <button 
              class="btn btn-primary"
              :disabled="!activationCode || loading"
              @click="handleActivate"
            >
              {{ loading ? '激活中...' : '激活' }}
            </button>
          </div>
          <p v-if="error" class="error-text">{{ error }}</p>
          <p v-if="success" class="success-text">激活成功！</p>
        </div>
        
        <div class="contact-section">
          <p>没有激活码？联系我们：</p>
          <a href="tel:18986034050" class="contact-phone">📞 189 8603 4050</a>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../stores/user'

const emit = defineEmits(['close', 'activated'])

const userStore = useUserStore()

const activationCode = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleActivate() {
  if (!activationCode.value || loading.value) return
  
  loading.value = true
  error.value = ''
  success.value = false
  
  try {
    const result = await userStore.activatePremium(activationCode.value)
    
    if (result.success) {
      success.value = true
      setTimeout(() => {
        emit('activated')
        emit('close')
      }, 1000)
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = '激活失败，请检查激活码是否正确'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  max-width: 480px;
  width: 100%;
  padding: 2rem;
  position: relative;
  animation: modalIn 0.3s ease;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--bg-light);
}

.modal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.premium-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.modal-header h2 {
  font-size: 1.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.modal-header p {
  color: var(--text-secondary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
}

.feature-icon {
  font-size: 1rem;
}

.activation-section {
  margin-bottom: 1.5rem;
}

.activation-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.activation-input-group {
  display: flex;
  gap: 0.5rem;
}

.activation-input {
  flex: 1;
}

.error-text {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.success-text {
  color: #48bb78;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.contact-section {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.contact-phone {
  display: inline-block;
  margin-top: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
}

.contact-phone:hover {
  color: var(--accent-color);
}
</style>
