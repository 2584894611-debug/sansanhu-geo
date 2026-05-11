<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">👤 个人中心</h1>
    </div>
    
    <div class="profile-content">
      <div class="profile-card card">
        <div class="user-header">
          <div class="avatar">
            {{ userInitial }}
          </div>
          <div class="user-info">
            <h2 class="user-name">用户</h2>
            <span class="user-id">ID: {{ shortDeviceId }}</span>
          </div>
        </div>
        
        <div class="membership-section">
          <div class="membership-badge" :class="{ premium: userStore.isPremium }">
            <span class="badge-icon">{{ userStore.isPremium ? '⭐' : '👤' }}</span>
            <span class="badge-text">{{ userStore.isPremium ? '付费版' : '免费版' }}</span>
          </div>
          
          <div class="usage-stats">
            <div class="stat-item">
              <span class="stat-label">今日使用</span>
              <span class="stat-value">{{ userStore.todayUsage }} 次</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">剩余次数</span>
              <span class="stat-value">{{ userStore.remaining === Infinity ? '无限' : userStore.remaining + ' 次' }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="!userStore.isPremium" class="upgrade-section">
          <h3>升级付费版</h3>
          <p>解锁无限次分析和完整功能</p>
          <div class="feature-list">
            <div class="feature-item">
              <span>✓</span> 无限次品牌分析
            </div>
            <div class="feature-item">
              <span>✓</span> 完整诊断报告
            </div>
            <div class="feature-item">
              <span>✓</span> 竞品对比分析
            </div>
            <div class="feature-item">
              <span>✓</span> 效果监测追踪
            </div>
            <div class="feature-item">
              <span>✓</span> 报告下载
            </div>
          </div>
          <button class="btn btn-primary upgrade-btn" @click="showPaywall = true">
            立即升级
          </button>
        </div>
        
        <div class="premium-info" v-else>
          <div class="info-row">
            <span class="info-label">会员状态</span>
            <span class="info-value success">已激活</span>
          </div>
          <div class="info-row">
            <span class="info-label">到期时间</span>
            <span class="info-value">长期有效</span>
          </div>
        </div>
      </div>
      
      <div class="history-card card">
        <h3 class="section-title">使用历史</h3>
        <div v-if="history.length > 0" class="history-list">
          <div v-for="item in history" :key="item.id" class="history-item">
            <div class="history-brand">{{ item.brand }}</div>
            <div class="history-meta">
              <span class="history-industry">{{ item.industry }}</span>
              <span class="history-score">{{ item.geo_score }}分</span>
            </div>
            <div class="history-time">{{ formatDate(item.created_at) }}</div>
          </div>
        </div>
        <div v-else class="empty-history">
          <p>暂无使用记录</p>
        </div>
      </div>
      
      <div class="contact-card card">
        <h3 class="section-title">联系我们</h3>
        <div class="contact-item">
          <span class="contact-icon">📞</span>
          <div class="contact-content">
            <span class="contact-label">电话</span>
            <a href="tel:18986034050" class="contact-value">189 8603 4050</a>
          </div>
        </div>
        <div class="contact-item">
          <span class="contact-icon">💬</span>
          <div class="contact-content">
            <span class="contact-label">微信</span>
            <span class="contact-value">备注"GEO智眼"</span>
          </div>
        </div>
        <div class="contact-item">
          <span class="contact-icon">⏰</span>
          <div class="contact-content">
            <span class="contact-label">服务时间</span>
            <span class="contact-value">周一至周五 9:00-18:00</span>
          </div>
        </div>
      </div>
    </div>
    
    <PaywallModal v-if="showPaywall" @close="showPaywall = false" @activated="handleActivated" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import api from '../api'
import PaywallModal from '../components/PaywallModal.vue'

const userStore = useUserStore()

const history = ref([])
const showPaywall = ref(false)

const deviceId = localStorage.getItem('geo_device_id') || ''

const shortDeviceId = computed(() => {
  return deviceId.slice(-8).toUpperCase()
})

const userInitial = computed(() => {
  return 'G'
})

onMounted(async () => {
  await userStore.checkStatus()
  await loadHistory()
})

async function loadHistory() {
  try {
    const response = await api.getHistory(20)
    history.value = response.data.data || []
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

function handleActivated() {
  showPaywall.value = false
  userStore.checkStatus()
  loadHistory()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card {
  padding: 2rem;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.user-name {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.user-id {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.membership-section {
  margin-bottom: 1.5rem;
}

.membership-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-light);
  border-radius: 20px;
  margin-bottom: 1rem;
}

.membership-badge.premium {
  background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
}

.badge-icon {
  font-size: 1.25rem;
}

.badge-text {
  font-weight: 600;
  color: var(--text-primary);
}

.membership-badge.premium .badge-text {
  color: var(--primary-color);
}

.usage-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.upgrade-section {
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.upgrade-section h3 {
  font-size: 1.125rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.upgrade-section > p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.feature-item span {
  color: #48bb78;
  font-weight: 700;
}

.upgrade-btn {
  width: 100%;
}

.premium-info {
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.info-label {
  color: var(--text-secondary);
}

.info-value {
  font-weight: 500;
}

.info-value.success {
  color: #48bb78;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-light);
  border-radius: var(--radius-sm);
}

.history-brand {
  flex: 1;
  font-weight: 500;
}

.history-meta {
  display: flex;
  gap: 0.75rem;
  margin-right: 1rem;
}

.history-industry {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: white;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

.history-score {
  font-weight: 700;
  color: var(--accent-color);
}

.history-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.empty-history {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.contact-card {
  padding: 1.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-color);
}

.contact-item:last-child {
  border-bottom: none;
}

.contact-icon {
  font-size: 1.5rem;
}

.contact-content {
  display: flex;
  flex-direction: column;
}

.contact-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.contact-value {
  font-weight: 500;
  color: var(--text-primary);
}

a.contact-value {
  color: var(--primary-color);
  text-decoration: none;
}

a.contact-value:hover {
  color: var(--accent-color);
}
</style>
