import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useProblemStore = defineStore('problem', () => {
  // 狀態
  const problems = ref([])
  const currentProblem = ref(null)
  const loading = ref(false)
  const total = ref(0)
  const stats = ref({
    open: 0,
    diagnosing: 0,
    fixing: 0,
    fixed: 0,
    wontfix: 0
  })

  // 方法
  async function fetchProblems(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/api/v1/admin/problems', { params })
      problems.value = response.data.items || []
      total.value = response.data.total || 0
      return response.data
    } catch (error) {
      console.error('Failed to fetch problems:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchProblem(id) {
    loading.value = true
    try {
      const response = await api.get(`/api/v1/admin/problems/${id}`)
      currentProblem.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch problem:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function diagnoseProblem(id) {
    try {
      const response = await api.post(`/api/v1/admin/problems/${id}/diagnose`)
      // 更新本地狀態
      const index = problems.value.findIndex(p => p.id === id)
      if (index !== -1 && response.data.problem) {
        problems.value[index] = response.data.problem
      }
      return response.data
    } catch (error) {
      console.error('Failed to diagnose problem:', error)
      throw error
    }
  }

  async function updateProblemStatus(id, status, notes) {
    try {
      const response = await api.put(`/api/v1/admin/problems/${id}/status`, null, {
        params: { status, notes }
      })
      // 更新本地狀態
      const index = problems.value.findIndex(p => p.id === id)
      if (index !== -1) {
        problems.value[index] = response.data.problem
      }
      return response.data
    } catch (error) {
      console.error('Failed to update problem status:', error)
      throw error
    }
  }

  async function fetchStats() {
    try {
      const [openResponse, diagnosingResponse, fixingResponse] = await Promise.all([
        api.get('/api/v1/admin/problems', { params: { status: 'open', limit: 1 } }),
        api.get('/api/v1/admin/problems', { params: { status: 'diagnosing', limit: 1 } }),
        api.get('/api/v1/admin/problems', { params: { status: 'fixing', limit: 1 } })
      ])

      stats.value = {
        open: openResponse.data.total || 0,
        diagnosing: diagnosingResponse.data.total || 0,
        fixing: fixingResponse.data.total || 0,
        fixed: 0,
        wontfix: 0
      }
    } catch (error) {
      console.error('Failed to fetch problem stats:', error)
    }
  }

  function clearProblems() {
    problems.value = []
    currentProblem.value = null
    total.value = 0
  }

  return {
    problems,
    currentProblem,
    loading,
    total,
    stats,
    fetchProblems,
    fetchProblem,
    diagnoseProblem,
    updateProblemStatus,
    fetchStats,
    clearProblems
  }
})
