import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/Home.vue')
  },
  {
    path: '/report/:id?',
    name: 'Report',
    component: () => import('../pages/Report.vue')
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('../pages/Monitor.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../pages/Profile.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../pages/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
