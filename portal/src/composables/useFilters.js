import { ref } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';
const API_BASE_URL = `${API_BASE}/api/sites`

export function useFilters() {
  const provinces = ref([])
  const states = ref([])
  const tags = ref([])

  const loadProvinces = async () => {
    try {
      console.log(API_BASE_URL)
      const response = await axios.get(`${API_BASE_URL}/provinces`)
      provinces.value = response.data.data
    } catch (error) {
      console.error('Error loading provinces:', error)
    }
  }

  const loadStates = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/states`)
      states.value = response.data.data
    } catch (error) {
      console.error('Error loading states:', error)
    }
  }

  const loadTags = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tags`)
      tags.value = response.data.data
    } catch (error) {
      console.error('Error loading tags:', error)
    }
  }

  const loadAll = async () => {
    await Promise.all([loadProvinces(), loadStates(), loadTags()])
  }

  return {
    provinces,
    states,
    tags,
    loadProvinces,
    loadStates,
    loadTags,
    loadAll
  }
}