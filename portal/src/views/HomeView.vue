<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import HeroSection from '../components/HeroSection.vue'
import SitesSection from '../components/SitesSection.vue'

const router = useRouter()

// URL base de la API
const API_BASE_URL = 'http://localhost:5000/api/sites'

// Estado de autenticación (simulado por ahora)
const isAuthenticated = ref(false) // Cambiar a true cuando el usuario inicie sesión
const userId = ref(1) // ID del usuario autenticado

// Estados de carga independientes
const loadingMostVisited = ref(true)
const loadingTopRated = ref(true)
const loadingRecentlyAdded = ref(true)
const loadingFavorites = ref(false)

// Datos de las secciones
const mostVisited = ref([])
const topRated = ref([])
const recentlyAdded = ref([])
const favorites = ref([])

const searchQuery = ref('')

// Manejo de búsqueda
const handleSearch = () => {
  const trimmedQuery = searchQuery.value.trim()
  
  if (trimmedQuery) {
    router.push({
      name: 'sites',
      query: { search: trimmedQuery }
    })
  } else {
    router.push({ name: 'sites' })
  }
}

// Función para obtener sitios más visitados
const fetchMostVisited = async () => {
  try {
    loadingMostVisited.value = true
    
    const response = await axios.get(`${API_BASE_URL}/most-visited`)
    mostVisited.value = response.data.data || []
  } catch (error) {
    console.error('Error fetching most visited:', error)
    mostVisited.value = []
  } finally {
    loadingMostVisited.value = false
  }
}

// TODO: Función para obtener sitios mejor puntuados
const fetchTopRated = async () => {
  try {
    loadingTopRated.value = true
    
    // Ordenar por rating descendente, limitado a 4
    const response = await axios.get(`${API_BASE_URL}/`, {
      params: {
        sort: 'rating',
        order: 'desc',
        per_page: 4,
        page: 1
      }
    })
    
    topRated.value = response.data.data || []
  } catch (error) {
    console.error('Error fetching top rated:', error)
    topRated.value = []
  } finally {
    loadingTopRated.value = false
  }
}

// Función para obtener sitios recientemente agregados
const fetchRecentlyAdded = async () => {
  try {
    loadingRecentlyAdded.value = true
    
    const response = await axios.get(`${API_BASE_URL}/recently-added`)
    recentlyAdded.value = response.data.data || []
  } catch (error) {
    console.error('Error fetching recently added:', error)
    recentlyAdded.value = []
  } finally {
    loadingRecentlyAdded.value = false
  }
}

// TODO: Función para obtener favoritos (solo si está autenticado)
const fetchFavorites = async () => {
  if (!isAuthenticated.value) return
  
  try {
    loadingFavorites.value = true
    
    const response = await axios.get(`${API_BASE_URL}/favorites`, {
      params: {
        user_id: userId.value
      }
    })
    
    favorites.value = response.data.data || []
  } catch (error) {
    console.error('Error fetching favorites:', error)
    favorites.value = []
  } finally {
    loadingFavorites.value = false
  }
}

// Cargar datos al montar el componente
onMounted(() => {
  fetchMostVisited()
  
  setTimeout(() => fetchTopRated(), 200)
  setTimeout(() => fetchRecentlyAdded(), 400)
  
  if (isAuthenticated.value) {
    setTimeout(() => fetchFavorites(), 600)
  }
})
</script>

<template>
  <div class="home-view">
    <!-- 
    HeroSection: 
    
    Props que envía al hijo:
    :searchQuery="searchQuery" → Se envía el texto de búsqueda actual para que lo muestre en el input
    
    Eventos que escucha del hijo:
    @search="handleSearch"
      → Cuando el usuario hace clic en "Buscar" o presiona Enter: Ejecuta la función handleSearch() que redirige a /sites
    
    @update:searchQuery="searchQuery = $event"
      → Cuando el usuario escribe en el input: Actualiza nuestro searchQuery con el nuevo valor ($event)
    -->
    <HeroSection 
      :searchQuery="searchQuery" 
      @search="handleSearch"
      @update:searchQuery="searchQuery = $event"
    />

    <div class="container pb-5">
      <!-- Sección: Más Visitados -->
      <SitesSection
        title="Más Visitados"
        icon="eye"
        icon-color="primary"
        :sites="mostVisited"
        :loading="loadingMostVisited"
        view-all-link="/sitios?orden=visitas"
      />

      <!-- Sección: Mejor Puntuados -->
      <SitesSection
        title="Mejor Puntuados"
        icon="star-fill"
        icon-color="warning"
        :sites="topRated"
        :loading="loadingTopRated"
        view-all-link="/sitios?orden=rating"
      />

      <!-- Sección: Favoritos (solo si está autenticado) -->
      <SitesSection
        v-if="isAuthenticated"
        title="Mis Favoritos"
        icon="heart-fill"
        icon-color="danger"
        :sites="favorites"
        :loading="loadingFavorites"
        view-all-link="/favoritos"
      />

      <!-- Sección: Recientemente Agregados -->
      <SitesSection
        title="Recientemente Agregados"
        icon="clock-history"
        icon-color="success"
        :sites="recentlyAdded"
        :loading="loadingRecentlyAdded"
        view-all-link="/sitios?orden=fecha"
      />
    </div>
  </div>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
