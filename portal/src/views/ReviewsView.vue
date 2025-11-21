<script setup>
import { ref, computed, onMounted } from 'vue'
import { authStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar'

const router = useRouter()
const reviews = ref([])
const loading = ref(true)
const error = ref(null)

// Paginación
const pagination = ref({
  page: 1,
  per_page: 25,
  total: 0,
  total_pages: 0,
  has_prev: false,
  has_next: false
})

const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const fetchReviews = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {    
    const response = await axios.get(`${API_BASE_URL}/api/reviews/user/${user.value.id}`, {
      params: {
        page: page,
        per_page: 10,
        sort: 'created_at',
        order: 'desc'
      }
    })
        
    reviews.value = response.data.data || []
    pagination.value = response.data.pagination || pagination.value
    
  } catch (err) {
    console.error('Error al cargar reseñas:', err)
    console.error('Error response:', err.response?.data)
    error.value = err.response?.data?.error || err.message || 'Error al cargar reseñas'
  } finally {
    loading.value = false
  }
}

const goToSite = (siteId) => {
  router.push(`/sitios/${siteId}`)
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchReviews(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const getRatingStars = (rating) => {
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
  
  let stars = ''
  stars += '<i class="bi bi-star-fill text-warning"></i>'.repeat(fullStars)
  if (hasHalfStar) stars += '<i class="bi bi-star-half text-warning"></i>'
  stars += '<i class="bi bi-star text-warning"></i>'.repeat(emptyStars)
  
  return stars
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }
  
  fetchReviews()
})
</script>

<template>
  <div class="reviews-view">
    <div class="container py-5">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="display-5 fw-bold mb-2">
            <i class="bi bi-star-fill text-warning me-2"></i>
            Mis Reseñas
          </h1>
          <p class="text-muted">Aquí encontrarás todas las reseñas que has escrito</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-3 text-muted">Cargando tus reseñas...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <button @click="fetchReviews()" class="btn btn-sm btn-outline-danger ms-3">
          Reintentar
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="reviews.length === 0" class="text-center py-5">
        <i class="bi bi-star display-1 text-muted mb-3"></i>
        <h3 class="text-muted mb-3">No tienes reseñas aún</h3>
        <p class="text-muted mb-4">Visita un sitio y escribe tu primera reseña</p>
        <RouterLink to="/sitios" class="btn btn-primary">
          <i class="bi bi-geo-alt me-2"></i>
          Explorar Sitios
        </RouterLink>
      </div>

      <!-- Reviews List -->
      <div v-else>
        <div class="row g-4">
          <div 
            v-for="review in reviews" 
            :key="review.id"
            class="col-12"
          >
            <div class="card shadow-sm hover-card">
              <div class="card-body">
                <div class="row">
                  <!-- Columna izquierda: Info del sitio -->
                  <div class="col-md-3 text-center border-end">
                    <img 
                      :src="review.site?.image || '/placeholder-site.jpg'" 
                      :alt="review.site?.name"
                      class="site-thumbnail mb-3"
                    >
                    <h6 class="fw-bold mb-2">{{ review.site?.name }}</h6>
                    <button 
                      @click="goToSite(review.site?.id)" 
                      class="btn btn-sm btn-outline-primary"
                    >
                      <i class="bi bi-eye me-1"></i>
                      Ver Sitio
                    </button>
                  </div>

                  <!-- Columna derecha: Contenido de la reseña -->
                  <div class="col-md-9">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                      <div>
                        <!-- Rating -->
                        <div class="rating mb-2" v-html="getRatingStars(review.rating)"></div>
                        
                        <!-- Fecha -->
                        <div class="text-muted small">
                          <i class="bi bi-calendar me-1"></i>
                          {{ formatDate(review.created_at) }}
                        </div>
                      </div>
                    </div>

                    <!-- Comentario -->
                    <div class="review-comment">
                      <p class="mb-0">{{ review.comment }}</p>
                    </div>

                    <!-- Estado -->
                    <div class="mt-3">
                      <span 
                        class="badge"
                        :class="{
                          'bg-success': review.status === 'approved',
                          'bg-warning': review.status === 'pending',
                          'bg-danger': review.status === 'rejected'
                        }"
                      >
                        <i class="bi" :class="{
                          'bi-check-circle': review.status === 'approved',
                          'bi-clock': review.status === 'pending',
                          'bi-x-circle': review.status === 'rejected'
                        }"></i>
                        {{ 
                          review.status === 'approved' ? 'Aprobada' :
                          review.status === 'pending' ? 'Pendiente' :
                          'Rechazada'
                        }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Paginación -->
        <div v-if="pagination.total_pages > 1" class="row mt-5">
          <div class="col">
            <nav aria-label="Navegación de reseñas">
              <ul class="pagination justify-content-center">
                <!-- Anterior -->
                <li class="page-item" :class="{ disabled: !pagination.has_prev }">
                  <button 
                    class="page-link" 
                    @click="goToPage(pagination.page - 1)"
                    :disabled="!pagination.has_prev"
                  >
                    <i class="bi bi-chevron-left"></i>
                    Anterior
                  </button>
                </li>

                <!-- Páginas -->
                <li 
                  v-for="page in pagination.total_pages" 
                  :key="page"
                  class="page-item"
                  :class="{ active: page === pagination.page }"
                >
                  <button class="page-link" @click="goToPage(page)">
                    {{ page }}
                  </button>
                </li>

                <!-- Siguiente -->
                <li class="page-item" :class="{ disabled: !pagination.has_next }">
                  <button 
                    class="page-link" 
                    @click="goToPage(pagination.page + 1)"
                    :disabled="!pagination.has_next"
                  >
                    Siguiente
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>

        <!-- Stats -->
        <div class="row mt-4">
          <div class="col">
            <div class="alert alert-info d-flex align-items-center">
              <i class="bi bi-info-circle me-2"></i>
              Tienes <strong class="mx-1">{{ pagination.total }}</strong> 
              {{ pagination.total === 1 ? 'reseña' : 'reseñas' }}
              <span v-if="pagination.total_pages > 1" class="ms-2">
                (Página {{ pagination.page }} de {{ pagination.total_pages }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reviews-view {
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

.site-thumbnail {
  width: 100%;
  max-width: 200px;
  height: 150px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rating {
  font-size: 1.25rem;
}

.review-comment {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.review-comment p {
  line-height: 1.6;
  color: #495057;
}

.badge {
  font-weight: 600;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

/* Paginación */
.pagination {
  margin-top: 2rem;
}

.page-link {
  color: #667eea;
  border-color: #dee2e6;
  transition: all 0.3s ease;
}

.page-link:hover {
  background-color: #667eea;
  border-color: #667eea;
  color: white;
  transform: translateY(-2px);
}

.page-item.active .page-link {
  background-color: #667eea;
  border-color: #667eea;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .reviews-view {
    padding-top: 1rem;
  }

  .display-5 {
    font-size: 2rem;
  }

  .col-md-3 {
    border-right: none !important;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
  }

  .site-thumbnail {
    max-width: 150px;
    height: 120px;
  }

  .pagination {
    font-size: 0.875rem;
  }
}
</style>