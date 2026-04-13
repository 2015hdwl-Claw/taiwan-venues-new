import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 狀態
  const apiKey = ref('')
  const isAuthenticated = computed(() => !!apiKey.value)

  // 方法
  function setApiKey(key) {
    apiKey.value = key
    localStorage.setItem('admin_api_key', key)
  }

  function loadFromStorage() {
    const storedKey = localStorage.getItem('admin_api_key')
    if (storedKey) {
      apiKey.value = storedKey
    }
  }

  function clearAuth() {
    apiKey.value = ''
    localStorage.removeItem('admin_api_key')
  }

  function getAuthHeaders() {
    return {
      'X-API-Key': apiKey.value
    }
  }

  return {
    apiKey,
    isAuthenticated,
    setApiKey,
    loadFromStorage,
    clearAuth,
    getAuthHeaders
  }
})
