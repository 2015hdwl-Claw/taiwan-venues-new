import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 創建 axios 實例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      config.headers['X-API-Key'] = authStore.apiKey
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('未授權，請重新登入')
          const authStore = useAuthStore()
          authStore.clearAuth()
          router.push('/login')
          break
        case 403:
          ElMessage.error('沒有權限執行此操作')
          break
        case 404:
          ElMessage.error('請求的資源不存在')
          break
        case 500:
          ElMessage.error('伺服器錯誤，請稍後再試')
          break
        default:
          ElMessage.error(error.response.data?.detail || '請求失敗')
      }
    } else if (error.request) {
      ElMessage.error('網路錯誤，請檢查您的連線')
    } else {
      ElMessage.error('請求配置錯誤')
    }
    return Promise.reject(error)
  }
)

export default api
