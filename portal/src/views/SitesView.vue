<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SiteCard from '../components/SiteCard.vue'

const route = useRoute()
const router = useRouter()

// Estados
const sites = ref([])
const loading = ref(true)
const searchQuery = ref(route.query.search || '')
const currentPage = ref(parseInt(route.query.page) || 1)
const totalPages = ref(1)
const totalSites = ref(0)
const perPage = 12

// Filtros
const selectedCategory = ref(route.query.category || '')
const selectedState = ref(route.query.state || '')
const selectedProvince = ref(route.query.province || '')
const sortBy = ref(route.query.sort || 'name')

// Opciones de filtros (se cargan desde la API)
const categories = ref([])
const states = ref([])
const provinces = ref([])

// Función para buscar sitios --> TODO: Reacomodar
const fetchSites = async () => {
  try {
    loading.value = true
    
    // Construir query params para la API
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage,
      sort: sortBy.value
    })
    
    if (searchQuery.value) params.append('q', searchQuery.value)
    if (selectedProvince.value) params.append('province', selectedProvince.value)
    if (selectedCategory.value) params.append('category', selectedCategory.value)
    if (selectedState.value) params.append('state', selectedState.value)
    
    // Llamar al endpoint del backend con paginación
    const response = await fetch(`http://localhost:5000/api/sites/?${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    console.log('Datos recibidos del backend:', result) // Debug
    
    // Mapeo los datos
    sites.value = result.data.map(site => ({
      id: site.id,
      site_name: site.name,
      short_desc: site.short_desc,
      city: site.city,
      province: site.province,
      cover_image: site.cover_image_url || null,
      average_rating: null,
      operning_year: site.opening_year,
      category: { name: site.category_name },
      state: { name: site.state_name },
      tags: site.tags || []
    }))
    
    totalSites.value = result.pagination.total
    totalPages.value = result.pagination.total_pages
    
    console.log('Sitios mapeados:', sites.value) // Debug
    
  } catch (error) {
    console.error('Error fetching sites:', error)
    sites.value = []
    totalSites.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

// Cargar provincias disponibles --> REACOMODAR
const loadProvinces = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/?per_page=1000')
    if (response.ok) {
      const result = await response.json()
      const uniqueProvinces = [...new Set(result.data.map(site => site.province).filter(Boolean))]
      provinces.value = uniqueProvinces.sort()
    }
  } catch (error) {
    console.error('Error loading provinces:', error)
  }
}

// Cargar estados disponibles: --> REACOMODAR
const loadStates = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/?per_page=1000')
    if (response.ok) {
      const result = await response.json()
      const uniqueStates = [...new Set(result.data.map(site => site.state_name).filter(Boolean))]
      states.value = uniqueStates
    }
  } catch (error) {
    console.error('Error loading states:', error)
  }
}

// Cargar categorías disponibles --> REACOMODAR
const loadCategories = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/?per_page=1000')
    if (response.ok) {
      const result = await response.json()
      const uniqueCategories = [...new Set(result.data.map(site => site.category_name).filter(Boolean))]
      categories.value = uniqueCategories
    }
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

// Función para manejar búsqueda
const handleSearch = () => {
  currentPage.value = 1
  updateURL()
  fetchSites()
}

// Actualizar URL con parámetros
const updateURL = () => {
  const query = {}
  if (searchQuery.value) query.search = searchQuery.value
  if (selectedCategory.value) query.category = selectedCategory.value
  if (selectedState.value) query.state = selectedState.value
  if (selectedProvince.value) query.province = selectedProvince.value
  if (sortBy.value !== 'name') query.sort = sortBy.value
  if (currentPage.value > 1) query.page = currentPage.value
  
  router.push({ query })
}

// Cambiar página
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    updateURL()
    fetchSites()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Limpiar filtros
const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedState.value = ''
  selectedProvince.value = ''
  sortBy.value = 'name'
  currentPage.value = 1
  updateURL()
  fetchSites()
}

// Cargar al montar
onMounted(() => {
  loadProvinces()
  loadStates()
  loadCategories()
  fetchSites()
})

// Watch para cambios en la ruta
watch(() => route.query, () => {
  searchQuery.value = route.query.search || ''
  currentPage.value = parseInt(route.query.page) || 1
  selectedCategory.value = route.query.category || ''
  selectedState.value = route.query.state || ''
  selectedProvince.value = route.query.province || ''
  sortBy.value = route.query.sort || 'name'
})
</script>

<template>
  <div class="sites-view">
    <div class="container py-5">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <h1 class="display-5 fw-bold mb-2">Explorar Sitios Históricos</h1>
          <p class="text-muted">
            Encontrados {{ totalSites }} sitios históricos en Argentina
          </p>
        </div>
      </div>

      <!-- Buscador y Filtros -->
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <div class="row g-3">
            <!-- Búsqueda -->
            <div class="col-md-6">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-search"></i>
                </span>
                <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  type="text"
                  class="form-control"
                  placeholder="Buscar por nombre..."
                >
                <button @click="handleSearch" class="btn btn-primary">
                  Buscar
                </button>
              </div>
            </div>

            <!-- Ordenar -->
            <div class="col-md-3">
              <select v-model="sortBy" @change="handleSearch" class="form-select">
                <option value="name">Ordenar por Nombre</option>
                <option value="rating">Mejor Puntuados</option>
                <option value="visits">Más Visitados</option>
                <option value="recent">Más Recientes</option>
              </select>
            </div>

            <!-- Botón limpiar filtros -->
            <div class="col-md-3">
              <button @click="clearFilters" class="btn btn-outline-secondary w-100">
                <i class="bi bi-x-circle me-1"></i>
                Limpiar Filtros
              </button>
            </div>
          </div>

          <!-- Filtros adicionales -->
          <div class="row g-3 mt-2">
            <div class="col-md-4">
              <label class="form-label small text-muted">Provincia</label>
              <select v-model="selectedProvince" @change="handleSearch" class="form-select form-select-sm">
                <option value="">Todas las provincias</option>
                <option v-for="province in provinces" :key="province" :value="province">
                  {{ province }}
                </option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label small text-muted">Categoría</label>
              <select v-model="selectedCategory" @change="handleSearch" class="form-select form-select-sm">
                <option value="">Todas las categorías</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label small text-muted">Estado</label>
              <select v-model="selectedState" @change="handleSearch" class="form-select form-select-sm">
                <option value="">Todos los estados</option>
                <option v-for="state in states" :key="state" :value="state">
                  {{ state }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-3 text-muted">Cargando sitios históricos...</p>
      </div>

      <!-- Grid de Sitios -->
      <div v-else-if="sites.length > 0" class="row g-4 mb-4">
        <div v-for="site in sites" :key="site.id" class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <SiteCard :site="site" />
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-else class="text-center py-5">
        <i class="bi bi-search display-1 text-muted mb-3"></i>
        <h3>No se encontraron sitios</h3>
        <p class="text-muted">Intenta ajustar los filtros de búsqueda</p>
        <button @click="clearFilters" class="btn btn-primary">
          Limpiar Filtros
        </button>
      </div>

      <!-- Paginación: REACOMODAR -->
      <nav v-if="totalPages > 1 && !loading" aria-label="Paginación">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" @click.prevent="goToPage(currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </a>
          </li>
          
          <li 
            v-for="page in totalPages" 
            :key="page"
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <a class="page-link" @click.prevent="goToPage(page)">
              {{ page }}
            </a>
          </li>
          
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" @click.prevent="goToPage(currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.sites-view {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.card {
  border: none;
}

.input-group-text {
  background-color: white;
  border-right: none;
}

.input-group .form-control {
  border-left: none;
}

.input-group .form-control:focus {
  border-color: #dee2e6;
  box-shadow: none;
}

.page-link {
  cursor: pointer;
}

.page-item.active .page-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}
</style>
