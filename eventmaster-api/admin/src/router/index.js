import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '儀表板' }
      },
      {
        path: 'venues',
        name: 'Venues',
        component: () => import('@/views/Venues.vue'),
        meta: { title: '場地管理' }
      },
      {
        path: 'venues/:id',
        name: 'VenueDetail',
        component: () => import('@/views/VenueDetail.vue'),
        meta: { title: '場地詳情' }
      },
      {
        path: 'problems',
        name: 'Problems',
        component: () => import('@/views/Problems.vue'),
        meta: { title: '問題追蹤' }
      },
      {
        path: 'scrape-tasks',
        name: 'ScrapeTasks',
        component: () => import('@/views/ScrapeTasks.vue'),
        meta: { title: '爬蟲任務' }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/Analytics.vue'),
        meta: { title: '數據分析' }
      },
      {
        path: 'conversations',
        name: 'Conversations',
        component: () => import('@/views/Conversations.vue'),
        meta: { title: '對話記錄' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 導航守衛
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
