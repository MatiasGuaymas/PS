<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import HeroSection from '../components/HeroSection.vue'
import SiteCard from '../components/SiteCard.vue'
import { useHomeSections } from '../composables/useHomeSections'
import axios from 'axios'

const router = useRouter()

// Estado usuario
const currentUser = ref(null)
const isAuthenticated = ref(false)
const userId = computed(() => currentUser.value?.id || null)

// Buscar usuario logeado
const fetchCurrentUser = async () => {
  try {
    const base = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar'
    const { data } = await axios.get(`${base}/auth/me`, { withCredentials: true })
    if (data?.id) {
      currentUser.value = data
      isAuthenticated.value = true
    } else {
      currentUser.value = null
      isAuthenticated.value = false
    }
  } catch {
    currentUser.value = null
    isAuthenticated.value = false
  }
}

// Búsqueda
const searchQuery = ref('')

// Refs secciones
const mostVisitedRef = ref(null)
const topRatedRef = ref(null)
const recentlyAddedRef = ref(null)
const favoritesRef = ref(null)

// Composable
const {
  loadingMostVisited,
  loadingTopRated,
  loadingRecentlyAdded,
  loadingFavorites,
  mostVisited,
  topRated,
  recentlyAdded,
  favorites,
  setupLazyLoading
} = useHomeSections()

const handleSearch = () => {
  const q = searchQuery.value.trim()
  router.push(q ? { name: 'sites', query: { search: q } } : { name: 'sites' })
}

let observer = null

const initSections = () => {
  if (observer) observer.disconnect()
  observer = setupLazyLoading(
    { mostVisitedRef, topRatedRef, recentlyAddedRef, favoritesRef },
    isAuthenticated.value,
    userId.value,
    { favoritesLimit: 4 }
  )
}

onMounted(async () => {
  await fetchCurrentUser()
  await nextTick() // Asegurar que <section v-if="isAuthenticated"> exista
  initSections()
})

watch([isAuthenticated, userId], async () => {
  await nextTick() // Esperar render del DOM antes de observar
  initSections()
})
</script>

<template>
  <div class="home-view">
    <HeroSection 
      :searchQuery="searchQuery" 
      @search="handleSearch"
      @update:searchQuery="searchQuery = $event"
    />

    <div class="container pb-5">
      <!-- Sección: Más Visitados -->
      <section ref="mostVisitedRef" data-section="most-visited" class="sites-section">
        <div class="section-header">
          <div class="d-flex align-items-center">
            <div class="icon-wrapper bg-primary">
              <i class="bi bi-eye"></i>
            </div>
            <h2 class="mb-0">Más Visitados</h2>
          </div>
          <router-link to="/sitios" class="btn btn-outline-primary">
            Ver todos
            <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
        </div>

        <div v-if="loadingMostVisited" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else-if="mostVisited.length > 0" class="sites-grid">
          <SiteCard v-for="site in mostVisited" :key="site.id" :site="site" />
        </div>

        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-inbox display-4 d-block mb-2"></i>
          <p>No hay sitios disponibles</p>
        </div>
      </section>

      <!-- TODO: Sección: Mejor Puntuados -->
      <section ref="topRatedRef" data-section="top-rated" class="sites-section">
        <div class="section-header">
          <div class="d-flex align-items-center">
            <div class="icon-wrapper bg-warning">
              <i class="bi bi-star-fill"></i>
            </div>
            <h2 class="mb-0">Mejor Puntuados</h2>
          </div>
          <router-link to="/sitios?sort=rating&order=desc" class="btn btn-outline-warning">
            Ver todos
            <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
        </div>

        <div v-if="loadingTopRated" class="text-center py-5">
          <div class="spinner-border text-warning" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else-if="topRated.length > 0" class="sites-grid">
          <SiteCard v-for="site in topRated" :key="site.id" :site="site" />
        </div>

        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-inbox display-4 d-block mb-2"></i>
          <p>No hay sitios disponibles</p>
        </div>
      </section>

      <!-- Sección: Favoritos -->
      <section v-if="isAuthenticated" ref="favoritesRef" data-section="favorites" class="sites-section">
        <div class="section-header">
          <div class="d-flex align-items-center">
            <div class="icon-wrapper bg-danger">
              <i class="bi bi-heart-fill"></i>
            </div>
            <h2 class="mb-0">Mis Favoritos</h2>
          </div>
          <router-link to="/sitios?favorites=true" class="btn btn-outline-danger">
            Ver todos
            <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
        </div>

        <div v-if="loadingFavorites" class="text-center py-5">
          <div class="spinner-border text-danger" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else-if="favorites.length > 0" class="sites-grid">
          <SiteCard v-for="site in favorites" :key="site.id" :site="site" />
        </div>

        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-heart display-4 d-block mb-2"></i>
          <p>No tienes sitios favoritos aún</p>
        </div>
      </section>

      <!-- Sección: Recientemente Agregados -->
      <section ref="recentlyAddedRef" data-section="recently-added" class="sites-section">
        <div class="section-header">
          <div class="d-flex align-items-center">
            <div class="icon-wrapper bg-success">
              <i class="bi bi-clock-history"></i>
            </div>
            <h2 class="mb-0">Recientemente Agregados</h2>
          </div>
          <router-link to="/sitios?sort=registration&order=desc" class="btn btn-outline-success">
            Ver todos
            <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
        </div>

        <div v-if="loadingRecentlyAdded" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>

        <div v-else-if="recentlyAdded.length > 0" class="sites-grid">
          <SiteCard v-for="site in recentlyAdded" :key="site.id" :site="site" />
        </div>

        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-inbox display-4 d-block mb-2"></i>
          <p>No hay sitios disponibles</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.sites-section {
  margin-bottom: 4rem;
  animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.section-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
  margin-left: 1rem;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 576px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .sites-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 576px) and (max-width: 767px) {
  .sites-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  .sites-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .sites-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1200px) {
  .sites-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>