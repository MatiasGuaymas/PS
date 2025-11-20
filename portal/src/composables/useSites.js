import { ref } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';
const API_BASE_URL = `${API_BASE}/api/sites`

export function useSites() {
  const sites = ref([])
  const loading = ref(false)
  const totalSites = ref(0)
  const totalPages = ref(1)

  const fetchSites = async (filters) => {
    try {
      loading.value = true
      
      // Construcción de params
      const params = {
        page: filters.page || 1,
        per_page: filters.perPage || 12,
        sort: filters.sortBy || 'site_name',
        order: filters.sortOrder || 'asc',
        ...(filters.lat && filters.lng && filters.radius ? {
          lat: filters.lat,
          lng: filters.lng,
          radius: filters.radius,
        } : {})
      }
      
      if (filters.searchQuery) params.q = filters.searchQuery
      if (filters.province) params.province = filters.province
      if (filters.city) params.city = filters.city
      if (filters.state) params.state = filters.state
      if (filters.tags && filters.tags.length > 0) {
        params.tags = filters.tags.join(',')
      }
      
      if (filters.showFavoritesOnly && filters.userId) {
        params.user_id = filters.userId
      }
      
      const response = await axios.get(API_BASE_URL, { params })
      const result = response.data
      
      // Mapear datos
      const sitesData = result.data.map(site => ({
        id: site.id,
        site_name: site.name,
        short_desc: site.short_desc,
        city: site.city,
        province: site.province,
        cover_image: site.cover_image_url || null,
        average_rating: site.rating || site.average_rating || null,
        opening_year: site.opening_year,
        category: { name: site.category_name },
        state: { name: site.state_name },
        tags: site.tags || []
      }))
      
      sites.value = sitesData
      totalSites.value = result.pagination.total
      totalPages.value = result.pagination.total_pages
      
      return { success: true, data: sitesData }
    } catch (error) {
      console.error('Error fetching sites:', error)
      sites.value = []
      totalSites.value = 0
      totalPages.value = 1
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }

  return {
    sites,
    loading,
    totalSites,
    totalPages,
    fetchSites
  }
}