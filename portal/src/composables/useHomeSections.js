import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';

export function useHomeSections() {
  // Estados de carga
  const loadingMostVisited = ref(false)
  const loadingTopRated = ref(false)
  const loadingRecentlyAdded = ref(false)
  const loadingFavorites = ref(false)

  // Control de carga completada (para evitar recargas)
  const mostVisitedLoaded = ref(false)
  const topRatedLoaded = ref(false)
  const recentlyAddedLoaded = ref(false)
  const favoritesLoaded = ref(false)

  // Datos de las secciones
  const mostVisited = ref([])
  const topRated = ref([])
  const recentlyAdded = ref([])
  const favorites = ref([])

  /**
   * Normaliza los datos del sitio para asegurar estructura consistente -> ()
   */
  const mapSiteData = (site) => {
    let coverImage = null

    if (site.cover_image_url) {
      coverImage = site.cover_image_url.startsWith('http')
        ? site.cover_image_url
        : `${API_BASE_URL}${site.cover_image_url}`
    } else if (site.images && Array.isArray(site.images) && site.images.length > 0) {
      const firstImage = site.images[0]
      if (firstImage?.path) {
        coverImage = firstImage.path.startsWith('http')
          ? firstImage.path
          : `${API_BASE_URL}${firstImage.path}`
      }
    } else if (site.cover_image) {
      coverImage = site.cover_image.startsWith('http')
        ? site.cover_image
        : `${API_BASE_URL}${site.cover_image}`
    }

    return {
      id: site.id,
      site_name: site.site_name || site.name,
      short_desc: site.short_desc || '',
      city: site.city || '',
      province: site.province || '',
      cover_image: coverImage,
      average_rating: site.rating || site.average_rating || null,
      opening_year: site.opening_year || null,
      category: site.category || (site.category_name ? { name: site.category_name } : null),
      state: site.state || (site.state_name ? { name: site.state_name } : null),
      tags: site.tags || [],
      rating: site.rating || site.average_rating || null
    }
  }

  // Más visitados
  const fetchMostVisited = async () => {
    if (mostVisitedLoaded.value) return

    try {
      loadingMostVisited.value = true
      const response = await axios.get(`${API_BASE_URL}/api/sites/most-visited`)
      mostVisited.value = (response.data.data || []).map(mapSiteData)
      mostVisitedLoaded.value = true
    } catch (error) {
      console.error('Error fetching most visited:', error)
      mostVisited.value = []
    } finally {
      loadingMostVisited.value = false
    }
  }

  // Mejor rankeados
  const fetchTopRated = async () => {
    if (topRatedLoaded.value) return

    try {
      loadingTopRated.value = true
      const response = await axios.get(`${API_BASE_URL}/api/sites/`, {
        params: {
          sort: 'rating',
          order: 'desc',
          per_page: 4,
          page: 1
        }
      })
      topRated.value = (response.data.data || []).map(mapSiteData)
      topRatedLoaded.value = true
    } catch (error) {
      console.error('Error fetching top rated:', error)
      topRated.value = []
    } finally {
      loadingTopRated.value = false
    }
  }

  // Recientemente agregados
  const fetchRecentlyAdded = async () => {
    if (recentlyAddedLoaded.value) return

    try {
      loadingRecentlyAdded.value = true
      const response = await axios.get(`${API_BASE_URL}/api/sites/recently-added`)
      recentlyAdded.value = (response.data.data || []).map(mapSiteData)
      recentlyAddedLoaded.value = true
    } catch (error) {
      console.error('Error fetching recently added:', error)
      recentlyAdded.value = []
    } finally {
      loadingRecentlyAdded.value = false
    }
  }

  // Favoritos del usuario
  const fetchFavorites = async (userId) => {
    if (favoritesLoaded.value) return

    try {
      loadingFavorites.value = true
      const response = await axios.get(`${API_BASE_URL}/api/sites/favorites`, {
        params: { user_id: userId }
      })
      favorites.value = (response.data.data || []).map(mapSiteData)
      favoritesLoaded.value = true
    } catch (error) {
      console.error('Error fetching favorites:', error)
      favorites.value = []
    } finally {
      loadingFavorites.value = false
    }
  }

  /**
   * Intersection Observer para lazy loading
   */
  const setupLazyLoading = (refs, isAuthenticated, userId) => {
    const options = {
      root: null,
      rootMargin: '100px',
      threshold: 0.1
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return

        const target = entry.target

        switch (target.dataset.section) {
          case 'most-visited':
            fetchMostVisited()
            break
          case 'top-rated':
            fetchTopRated()
            break
          case 'recently-added':
            fetchRecentlyAdded()
            break
          case 'favorites':
            if (isAuthenticated.value) {
              fetchFavorites(userId.value)
            }
            break
        }

        observer.unobserve(target)
      })
    }, options)

    Object.values(refs).forEach((refObj) => {
      if (refObj.value) observer.observe(refObj.value)
    })

    return observer
  }

  return {
    loadingMostVisited,
    loadingTopRated,
    loadingRecentlyAdded,
    loadingFavorites,
    mostVisited,
    topRated,
    recentlyAdded,
    favorites,
    setupLazyLoading
  }
}