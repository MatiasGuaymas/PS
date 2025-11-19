import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';

export function useHomeSections() {
  const loadingMostVisited = ref(false)
  const loadingTopRated = ref(false)
  const loadingRecentlyAdded = ref(false)
  const loadingFavorites = ref(false)

  const mostVisitedLoaded = ref(false)
  const topRatedLoaded = ref(false)
  const recentlyAddedLoaded = ref(false)
  const favoritesLoaded = ref(false)

  const mostVisited = ref([])
  const topRated = ref([])
  const recentlyAdded = ref([])
  const favorites = ref([])

  // Mapeo que funcionaba antes (con site_name y cover_image)
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

  const extractSites = (data) => {
    if (!data) return []
    if (Array.isArray(data.data)) return data.data
    if (Array.isArray(data.data?.sites)) return data.data.sites
    if (Array.isArray(data.data?.favorites)) return data.data.favorites.map(f => f.site || f)
    if (Array.isArray(data.favorites)) return data.favorites.map(f => f.site || f)
    if (Array.isArray(data)) return data
    return []
  }

  const fetchMostVisited = async () => {
    if (mostVisitedLoaded.value) return
    loadingMostVisited.value = true
    try {
      const { data } = await axios.get(`${API_BASE_URL}/api/sites/most-visited`, { params: { limit: 8 } })
      mostVisited.value = extractSites(data).map(mapSiteData).filter(Boolean)
      mostVisitedLoaded.value = true
    } catch {
      mostVisited.value = []
    } finally {
      loadingMostVisited.value = false
    }
  }

  // TODO: !!!!
  const fetchTopRated = async () => {
    if (topRatedLoaded.value) return
    loadingTopRated.value = true
    try {
      const { data } = await axios.get(`${API_BASE_URL}/api/sites/`, {
        params: { sort: 'rating', order: 'desc', per_page: 4, page: 1 }
      })
      topRated.value = extractSites(data).map(mapSiteData).filter(Boolean)
      topRatedLoaded.value = true
    } catch {
      topRated.value = []
    } finally {
      loadingTopRated.value = false
    }
  }

  const fetchRecentlyAdded = async () => {
    if (recentlyAddedLoaded.value) return
    loadingRecentlyAdded.value = true
    try {
      const { data } = await axios.get(`${API_BASE_URL}/api/sites/recently-added`, { params: { limit: 8 } })
      recentlyAdded.value = extractSites(data).map(mapSiteData).filter(Boolean)
      recentlyAddedLoaded.value = true
    } catch {
      recentlyAdded.value = []
    } finally {
      loadingRecentlyAdded.value = false
    }
  }

  const fetchFavorites = async (userId, limit = 4) => {
    if (!userId) {
      favorites.value = []
      favoritesLoaded.value = true
      return
    }
    loadingFavorites.value = true
    try {
      let sites = []

      // 1: /api/favorites?user_id=&limit=
      try {
        const { data } = await axios.get(`${API_BASE_URL}/api/favorites`, {
          params: { user_id: userId, limit }
        })
        sites = extractSites(data)
      } catch { }

      // 2: /api/users/:id/favorites?limit=
      if (!sites.length) {
        try {
          const { data } = await axios.get(`${API_BASE_URL}/api/users/${encodeURIComponent(userId)}/favorites`, {
            params: { limit },
            withCredentials: true
          })
          sites = extractSites(data)
        } catch { }
      }

      // 3: /api/sites/favorites?user_id=&limit=
      if (!sites.length) {
        try {
          const { data } = await axios.get(`${API_BASE_URL}/api/sites/favorites`, {
            params: { user_id: userId, limit }
          })
          sites = extractSites(data)
        } catch { }
      }

      favorites.value = (sites || []).map(mapSiteData).filter(Boolean)
      favoritesLoaded.value = true
    } catch {
      favorites.value = []
      favoritesLoaded.value = true
    } finally {
      loadingFavorites.value = false
    }
  }

  const setupLazyLoading = (refs, isAuth, uid, opts = {}) => {
    const { favoritesLimit = 4 } = opts
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        const section = entry.target.dataset.section
        switch (section) {
          case 'most-visited': fetchMostVisited(); break
          case 'top-rated': fetchTopRated(); break
          case 'recently-added': fetchRecentlyAdded(); break
          case 'favorites':
            if (isAuth && uid) fetchFavorites(uid, favoritesLimit)
            break
        }
        io.unobserve(entry.target)
      })
    }, { root: null, rootMargin: '100px', threshold: 0.1 })

    Object.values(refs).forEach((r) => { if (r?.value) io.observe(r.value) })
    return io
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