<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import HeroSection from '../components/HeroSection.vue'
import SitesSection from '../components/SitesSection.vue'

const router = useRouter()

// Estado de autenticación (simulado por ahora)
const isAuthenticated = ref(false) // Cambiar a true cuando el usuario inicie sesión

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
    
    // TODO: Reemplazar con la API
    // const response = await fetch('http://localhost:5000/api/sites/most-visited')
    // mostVisited.value = await response.json()
    
    // Datos de ejemplo
    await new Promise(resolve => setTimeout(resolve, 800))
    mostVisited.value = [
      {
        id: 1,
        name: 'Cabildo de Buenos Aires',
        short_desc: 'Sede histórica de la Revolución de Mayo de 1810',
        city: 'Buenos Aires',
        province: 'CABA',
        image: 'https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=400',
        rating: 4.5
      },
      {
        id: 2,
        name: 'Casa Rosada',
        short_desc: 'Sede del Poder Ejecutivo Nacional argentino',
        city: 'Buenos Aires',
        province: 'CABA',
        image: 'https://images.unsplash.com/photo-1589802829985-817e51171b92?w=400',
        rating: 4.8
      },
      {
        id: 3,
        name: 'Puente de la Mujer',
        short_desc: 'Icónico puente giratorio diseñado por Calatrava',
        city: 'Buenos Aires',
        province: 'CABA',
        image: 'https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=400',
        rating: 4.6
      },
      {
        id: 4,
        name: 'Teatro Colón',
        short_desc: 'Uno de los teatros de ópera más importantes del mundo',
        city: 'Buenos Aires',
        province: 'CABA',
        image: 'https://images.unsplash.com/photo-1580809361436-42a7ec204889?w=400',
        rating: 4.9
      }
    ]
  } catch (error) {
    console.error('Error fetching most visited:', error)
    mostVisited.value = []
  } finally {
    loadingMostVisited.value = false
  }
}

// Función para obtener sitios mejor puntuados
const fetchTopRated = async () => {
  try {
    loadingTopRated.value = true
    
    // TODO: Reemplazar con la API
    // const response = await fetch('http://localhost:5000/api/sites/top-rated')
    // topRated.value = await response.json()
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    topRated.value = [
      {
        id: 5,
        name: 'Catedral de Salta',
        short_desc: 'Templo principal de la provincia de Salta',
        city: 'Salta',
        province: 'Salta',
        image: 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400',
        rating: 4.9
      },
      {
        id: 6,
        name: 'Manzana Jesuítica',
        short_desc: 'Patrimonio de la Humanidad UNESCO',
        city: 'Córdoba',
        province: 'Córdoba',
        image: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=400',
        rating: 4.8
      },
      {
        id: 7,
        name: 'Casa Histórica de Tucumán',
        short_desc: 'Lugar de la Declaración de la Independencia',
        city: 'San Miguel de Tucumán',
        province: 'Tucumán',
        image: 'https://images.unsplash.com/photo-1564415315949-7a0c4c73aab4?w=400',
        rating: 4.7
      }
    ]
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
    
    // TODO: Reemplazar con la API
    // const response = await fetch('http://localhost:5000/api/sites/recently-added')
    // recentlyAdded.value = await response.json()
    
    await new Promise(resolve => setTimeout(resolve, 1200))
    recentlyAdded.value = [
      {
        id: 8,
        name: 'Monumento al Ejército de los Andes',
        short_desc: 'Homenaje a la gesta sanmartiniana',
        city: 'Mendoza',
        province: 'Mendoza',
        image: 'https://images.unsplash.com/photo-1601933973783-43cf8a7d4c5f?w=400',
        rating: 4.7
      },
      {
        id: 9,
        name: 'Pucará de Tilcara',
        short_desc: 'Antigua fortaleza preincaica',
        city: 'Tilcara',
        province: 'Jujuy',
        image: 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400',
        rating: 4.6
      }
    ]
  } catch (error) {
    console.error('Error fetching recently added:', error)
    recentlyAdded.value = []
  } finally {
    loadingRecentlyAdded.value = false
  }
}

// Función para obtener favoritos (solo si está autenticado)
const fetchFavorites = async () => {
  if (!isAuthenticated.value) return
  
  try {
    loadingFavorites.value = true
    
    // TODO: Reemplazar con la API
    // const response = await fetch('http://localhost:5000/api/sites/favorites', {
    //   headers: { 'Authorization': `Bearer ${token}` }
    // })
    // favorites.value = await response.json()
    
    await new Promise(resolve => setTimeout(resolve, 600))
    favorites.value = [
      {
        id: 10,
        name: 'Glaciar Perito Moreno',
        short_desc: 'Imponente glaciar en la Patagonia argentina',
        city: 'El Calafate',
        province: 'Santa Cruz',
        image: 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=400',
        rating: 5.0
      }
    ]
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
