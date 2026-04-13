import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useScrapeStore = defineStore('scrape', () => {
  // 狀態
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)

  // 方法
  async function fetchTasks(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/api/v1/admin/scrape-tasks', { params })
      tasks.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch scrape tasks:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createTask(venueIds, taskType = 'full') {
    try {
      const response = await api.post('/api/v1/admin/scrape-tasks', venueIds, {
        params: { task_type: taskType }
      })
      tasks.value.unshift(...response.data.tasks)
      return response.data
    } catch (error) {
      console.error('Failed to create scrape task:', error)
      throw error
    }
  }

  async function fetchTask(id) {
    loading.value = true
    try {
      const response = await api.get(`/api/v1/admin/scrape-tasks/${id}`)
      currentTask.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch scrape task:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function clearTasks() {
    tasks.value = []
    currentTask.value = null
  }

  return {
    tasks,
    currentTask,
    loading,
    fetchTasks,
    createTask,
    fetchTask,
    clearTasks
  }
})
