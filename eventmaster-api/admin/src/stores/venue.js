import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useVenueStore = defineStore('venue', () => {
  // 狀態
  const venues = ref([])
  const currentVenue = ref(null)
  const loading = ref(false)
  const total = ref(0)

  // 方法
  async function fetchVenues(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/api/v1/venues', { params })
      // 處理不同的 API 響應格式
      const data = response.data
      if (data.success && data.data) {
        venues.value = data.data.venues || []
        total.value = data.data.pagination?.total || venues.value.length
      } else {
        venues.value = data.items || data || []
        total.value = data.total || venues.value.length
      }
      return response.data
    } catch (error) {
      console.error('Failed to fetch venues:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchVenue(id) {
    loading.value = true
    try {
      const response = await api.get(`/api/v1/venues/${id}`)
      // 處理不同的 API 響應格式
      const data = response.data
      if (data.success && data.data) {
        currentVenue.value = data.data.venue || data.data
      } else {
        currentVenue.value = data
      }
      return currentVenue.value
    } catch (error) {
      console.error('Failed to fetch venue:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createVenue(data) {
    try {
      const response = await api.post('/api/v1/venues', data)
      venues.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to create venue:', error)
      throw error
    }
  }

  async function updateVenue(id, data) {
    try {
      const response = await api.put(`/api/v1/venues/${id}`, data)
      const index = venues.value.findIndex(v => v.id === id)
      if (index !== -1) {
        venues.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to update venue:', error)
      throw error
    }
  }

  async function deleteVenue(id) {
    try {
      await api.delete(`/api/v1/venues/${id}`)
      venues.value = venues.value.filter(v => v.id !== id)
    } catch (error) {
      console.error('Failed to delete venue:', error)
      throw error
    }
  }

  function clearVenues() {
    venues.value = []
    currentVenue.value = null
    total.value = 0
  }

  return {
    venues,
    currentVenue,
    loading,
    total,
    fetchVenues,
    fetchVenue,
    createVenue,
    updateVenue,
    deleteVenue,
    clearVenues
  }
})
