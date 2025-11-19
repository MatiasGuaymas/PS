<script setup>
import { ref, computed, onMounted } from 'vue'
import { authStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://grupo21.proyecto2025.linti.unlp.edu.ar'

const router = useRouter()
const favorites = ref([])
const loading = ref(true)
const error = ref(null)

const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const fetchFavorites = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('🔍 Fetching favorites for user:', user.value?.id)
    
    const response = await axios.get(`${API_BASE_URL}/api/sites/favorites`, {
      params: {
        user_id: user.value.id,
        page: 1,
        per_page: 12
      }
    })
    
    console.log('✅ Response:', response.data)
    
    // ✅ Axios devuelve los datos en response.data
    favorites.value = response.data.data || []
    
  } catch (err) {
    console.error('❌ Error al cargar favoritos:', err)
    console.error('❌ Error response:', err.response?.data)
    error.value = err.response?.data?.error || err.message || 'Error al cargar favoritos'
  } finally {
    loading.value = false
  }
}


const goToSite = (siteId) => {
  router.push(`/sitios/${siteId}`)
}

onMounted(() => {
  console.log('🎯 FavoritesView mounted')
  console.log('   - isAuthenticated:', isAuthenticated.value)
  console.log('   - user:', user.value)
  
  if (!isAuthenticated.value) {
    console.log('❌ Not authenticated, redirecting to login')
    router.push('/login')
    return
  }
  
  fetchFavorites()
})
</script>

<template>
  <div class="favorites-view">
    <div class="container py-5">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="display-5 fw-bold mb-2">
            <i class="bi bi-heart-fill text-danger me-2"></i>
            Mis Sitios Favoritos
          </h1>
          <p class="text-muted">Aquí encontrarás todos los sitios que has marcado como favoritos</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-3 text-muted">Cargando tus favoritos...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <button @click="fetchFavorites" class="btn btn-sm btn-outline-danger ms-3">
          Reintentar
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="favorites.length === 0" class="text-center py-5">
        <i class="bi bi-heart display-1 text-muted mb-3"></i>
        <h3 class="text-muted mb-3">No tienes favoritos aún</h3>
        <p class="text-muted mb-4">Explora sitios y marca tus favoritos para verlos aquí</p>
        <RouterLink to="/sitios" class="btn btn-primary">
          <i class="bi bi-geo-alt me-2"></i>
          Explorar Sitios
        </RouterLink>
      </div>

      <!-- Favorites Grid -->
      <div v-else class="row g-4">
        <div 
          v-for="site in favorites" 
          :key="site.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <div class="card h-100 shadow-sm hover-card">
            <!-- Imagen del sitio -->
            <div class="card-img-wrapper">
              <img 
                :src="site.cover_image_url || '/placeholder-site.jpg'" 
                :alt="site.name"
                class="card-img-top"
              >
            </div>

            <div class="card-body d-flex flex-column">
              <h5 class="card-title fw-bold mb-2">{{ site.name }}</h5>
              
              <div class="mb-2">
                <span class="badge bg-primary-subtle text-primary">
                  <i class="bi bi-geo-alt me-1"></i>
                  {{ site.location || 'Sin ubicación' }}
                </span>
              </div>

              <p class="card-text text-muted flex-grow-1">
                {{ site.brief_description || site.description || 'Sin descripción disponible' }}
              </p>

              <div class="d-flex gap-2 mt-3">
                <button 
                  @click="goToSite(site.id)" 
                  class="btn btn-outline-primary flex-grow-1"
                >
                  <i class="bi bi-eye me-1"></i>
                  Ver Detalles
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="favorites.length > 0" class="row mt-5">
        <div class="col">
          <div class="alert alert-info d-flex align-items-center">
            <i class="bi bi-info-circle me-2"></i>
            Tienes <strong class="mx-1">{{ favorites.length }}</strong> 
            {{ favorites.length === 1 ? 'sitio favorito' : 'sitios favoritos' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-view {
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.hover-card {
  transition: all 0.3s ease;
  border: none;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

.card-img-wrapper {
  position: relative;
  overflow: hidden;
  height: 200px;
}

.card-img-top {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.hover-card:hover .card-img-top {
  transform: scale(1.05);
}

.favorite-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
}

.favorite-btn:hover {
  transform: scale(1.1);
}

.card-title {
  color: #2c3e50;
}

.btn-outline-primary {
  border-width: 2px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .favorites-view {
    padding-top: 1rem;
  }

  .display-5 {
    font-size: 2rem;
  }
}
</style>