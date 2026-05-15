<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">
          <span class="logo-mark">三</span>
          <span class="logo-text">三三狐GEO</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/" class="nav-link">分析</router-link>
          <router-link to="/monitor" class="nav-link" :class="{ locked: !userStore.isPremium }">
            监控仪表盘
          </router-link>
          <router-link to="/profile" class="nav-link">个人中心</router-link>
          <router-link to="/about" class="nav-link">关于我们</router-link>
        </nav>
        <div class="user-status">
          <span v-if="!userStore.isPremium" class="free-tag">免费版</span>
          <span v-else class="premium-tag">付费版</span>
          <span class="usage-info">{{ userStore.remaining }}次/天</span>
        </div>
      </div>
    </header>
    
    <main class="app-main">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <p>好易易GEO © 2025 · 鄂ICP备2025150688号 · 联系我们: 189 8603 4050</p>
    </footer>
    
    <PaywallModal v-if="showPaywall" @close="showPaywall = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from './stores/user'
import PaywallModal from './components/PaywallModal.vue'

const userStore = useUserStore()
const showPaywall = ref(false)

onMounted(async () => {
  await userStore.checkStatus()
})

// 暴露给子组件使用
const openPaywall = () => {
  showPaywall.value = true
}

defineExpose({ openPaywall })
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F8FAFC;
}

.app-header {
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #E5E7EB;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  color: #1A1A2E;
}

.logo-mark {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #FF6B35;
  color: #FFFFFF;
  font-weight: 700;
  font-size: 1rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1A1A2E;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #4B5563;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #FF6B35;
}

.nav-link.locked {
  opacity: 0.6;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.free-tag,
.premium-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.free-tag {
  background: #F3F4F6;
  color: #6B7280;
}

.premium-tag {
  background: rgba(255, 107, 53, 0.12);
  color: #FF6B35;
}

.usage-info {
  color: #6B7280;
  font-size: 0.875rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
}

.app-footer {
  text-align: center;
  padding: 1.5rem;
  color: #6B7280;
  font-size: 0.875rem;
  border-top: 1px solid #E5E7EB;
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
    gap: 1rem;
  }
}
</style>
