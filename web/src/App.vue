<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">
          <span class="logo-icon">🔍</span>
          <span class="logo-text">好易易GEO</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/" class="nav-link">分析</router-link>
          <router-link to="/monitor" class="nav-link" :class="{ locked: !userStore.isPremium }">
            监测 <span v-if="!userStore.isPremium" class="lock-icon">🔒</span>
          </router-link>
          <router-link to="/profile" class="nav-link">个人中心</router-link>
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
      <p>好易易GEO © 2024 | 联系我们: 189 8603 4050</p>
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
  background: linear-gradient(135deg, #1a365d 0%, #2d4a6f 100%);
}

.app-header {
  background: rgba(26, 54, 93, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
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
  gap: 0.5rem;
  text-decoration: none;
  color: #fff;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #D4AF37 0%, #F4D03F 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #D4AF37;
}

.nav-link.locked {
  opacity: 0.6;
}

.lock-icon {
  font-size: 0.75rem;
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
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.premium-tag {
  background: linear-gradient(135deg, #D4AF37 0%, #F4D03F 100%);
  color: #1a365d;
}

.usage-info {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
}

.app-footer {
  text-align: center;
  padding: 1.5rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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
