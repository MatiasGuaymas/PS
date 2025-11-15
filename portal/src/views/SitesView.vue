<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SiteCard from '../components/SiteCard.vue'
import Choices from 'choices.js'
import 'choices.js/public/assets/styles/choices.min.css'

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
const selectedCity = ref(route.query.city || '')
const selectedState = ref(route.query.state || '')
const selectedProvince = ref(route.query.province || '')
const selectedTags = ref(route.query.tags ? route.query.tags.split(',') : [])
const showFavoritesOnly = ref(route.query.favorites === 'true')
const sortBy = ref(route.query.sort || 'name')
const sortOrder = ref(route.query.order || 'asc')

// Opciones de filtros (se cargan desde la API)
const states = ref([])
const provinces = ref([])
const tags = ref([])

// UI State
const filtersExpanded = ref(false)
let choicesInstance = null

// Computed: Rango de páginas para mostrar
const paginationRange = computed(() => {
  const range = []
  const delta = 2
  const start = Math.max(1, currentPage.value - delta)
  const end = Math.min(totalPages.value, currentPage.value + delta)
  
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  
  return range
})

// Función para buscar sitios
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
    if (selectedCity.value) params.append('city', selectedCity.value)
    if (selectedState.value) params.append('state', selectedState.value)
    if (selectedTags.value.length > 0) params.append('tags', selectedTags.value.join(','))
    
    // Llamar al endpoint del backend con paginación
    const response = await fetch(`http://localhost:5000/api/sites/?${params}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // Mapeo los datos
    let sitesData = result.data.map(site => ({
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
    
    // Filtrar por favoritos si está activo
    if (showFavoritesOnly.value) {
      const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
      sitesData = sitesData.filter(site => favorites.includes(site.id))
    }
    
    sites.value = sitesData
    totalSites.value = result.pagination.total
    totalPages.value = result.pagination.total_pages
    
  } catch (error) {
    console.error('Error fetching sites:', error)
    sites.value = []
    totalSites.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

const loadProvinces = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/provinces')
    if (response.ok) {
      const result = await response.json()
      provinces.value = result.data
    }
  } catch (error) {
    console.error('Error loading provinces:', error)
  }
}

const loadStates = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/states')
    if (response.ok) {
      const result = await response.json()
      states.value = result.data
    }
  } catch (error) {
    console.error('Error loading states:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sites/tags')
    if (response.ok) {
      const result = await response.json()
      tags.value = result.data
    }
  } catch (error) {
    console.error('Error loading tags:', error)
  }
}

// Inicializar Choices.js para multiselect de tags
const initChoices = async () => {
  await nextTick()
  const tagsElement = document.getElementById('tags-select')
  if (tagsElement && !choicesInstance) {
    choicesInstance = new Choices(tagsElement, {
      removeItemButton: true,
      searchEnabled: true,
      searchPlaceholderValue: 'Buscar tags...',
      noResultsText: 'No se encontraron tags',
      itemSelectText: 'Click para seleccionar',
      placeholder: true,
      placeholderValue: 'Seleccionar tags',
    })
    
    // Listener para actualizar selectedTags
    tagsElement.addEventListener('change', (event) => {
      selectedTags.value = Array.from(event.target.selectedOptions).map(opt => opt.value)
    })
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
  if (selectedCity.value) query.city = selectedCity.value
  if (selectedState.value) query.state = selectedState.value
  if (selectedProvince.value) query.province = selectedProvince.value
  if (selectedTags.value.length > 0) query.tags = selectedTags.value.join(',')
  if (showFavoritesOnly.value) query.favorites = 'true'
  if (sortBy.value !== 'name') query.sort = sortBy.value
  if (sortOrder.value !== 'asc') query.order = sortOrder.value
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
  selectedCity.value = ''
  selectedState.value = ''
  selectedProvince.value = ''
  selectedTags.value = []
  showFavoritesOnly.value = false
  sortBy.value = 'name'
  sortOrder.value = 'asc'
  currentPage.value = 1
  
  // Limpiar el multiselect de Choices.js
  if (choicesInstance) {
    choicesInstance.removeActiveItems()
  }
  
  updateURL()
  fetchSites()
}

// Toggle orden ascendente/descendente
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  handleSearch()
}

// TODO: Abrir vista de mapa
const openMapView = () => {
  alert('Funcionalidad de mapa próximamente disponible')
}

// Cargar al montar
onMounted(async () => {
  await loadProvinces()
  await loadStates()
  await loadTags()
  await initChoices()
  fetchSites()
})

// Watch para cambios en la ruta (navegación back/forward)
watch(() => route.query, () => {
  searchQuery.value = route.query.search || ''
  currentPage.value = parseInt(route.query.page) || 1
  selectedCity.value = route.query.city || ''
  selectedState.value = route.query.state || ''
  selectedProvince.value = route.query.province || ''
  selectedTags.value = route.query.tags ? route.query.tags.split(',') : []
  showFavoritesOnly.value = route.query.favorites === 'true'
  sortBy.value = route.query.sort || 'name'
  sortOrder.value = route.query.order || 'asc'
})
</script>

<template>
  <div class="sites-view">
    <div class="container-fluid">
      <div class="row">
        <!-- Panel de Filtros Lateral (Desktop) / Acordeón (Mobile) -->
        <aside class="col-lg-3 filters-sidebar" :class="{ 'expanded': filtersExpanded }">
          <div class="filters-container">
            <!-- Header de filtros (solo desktop) -->
            <div class="filters-header d-none d-lg-block">
              <h5 class="mb-0">
                <i class="bi bi-funnel me-2"></i>
                Filtros y Búsqueda
              </h5>
            </div>

            <!-- Contenido de filtros (colapsable en mobile) -->
            <div class="filters-content" :class="{ 'show': filtersExpanded }">
              <!-- Búsqueda por texto -->
              <div class="filter-group">
                <label class="form-label">Buscar</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    v-model="searchQuery"
                    @keyup.enter="handleSearch"
                    type="text"
                    class="form-control"
                    placeholder="Nombre o descripción..."
                  >
                </div>
              </div>

              <!-- Ciudad -->
              <div class="filter-group">
                <label class="form-label">Ciudad</label>
                <input
                  v-model="selectedCity"
                  @change="handleSearch"
                  type="text"
                  class="form-control"
                  placeholder="Ej: La Plata"
                >
              </div>

              <!-- Provincia -->
              <div class="filter-group">
                <label class="form-label">Provincia</label>
                <select v-model="selectedProvince" @change="handleSearch" class="form-select">
                  <option value="">Todas</option>
                  <option v-for="province in provinces" :key="province" :value="province">
                    {{ province }}
                  </option>
                </select>
              </div>

              <!-- Estado de conservación -->
              <div class="filter-group">
                <label class="form-label">Estado</label>
                <select v-model="selectedState" @change="handleSearch" class="form-select">
                  <option value="">Todos</option>
                  <option v-for="state in states" :key="state.id" :value="state.name">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <!-- Tags -->
              <div class="filter-group">
                <label class="form-label">Tags</label>
                <select 
                  id="tags-select" 
                  v-model="selectedTags"
                  @change="handleSearch"
                  multiple
                  class="form-select"
                >
                  <option v-for="tag in tags" :key="tag.id" :value="tag.id">
                    {{ tag.name }}
                  </option>
                </select>
              </div>

              <!-- Favoritos -->
              <div class="filter-group">
                <div class="form-check">
                  <input
                    v-model="showFavoritesOnly"
                    @change="handleSearch"
                    class="form-check-input"
                    type="checkbox"
                    id="favoritesCheck"
                  >
                  <label class="form-check-label" for="favoritesCheck">
                    <i class="bi bi-heart-fill text-danger me-1"></i>
                    Solo favoritos
                  </label>
                </div>
              </div>

              <!-- Ordenamiento -->
              <div class="filter-group">
                <label class="form-label">Ordenar por</label>
                <div class="input-group">
                  <select v-model="sortBy" @change="handleSearch" class="form-select">
                    <option value="name">Nombre</option>
                    <option value="recent">Fecha de registro</option>
                    <option value="rating">Mejor rankeados</option>
                  </select>
                  <button 
                    @click="toggleSortOrder"
                    class="btn btn-outline-secondary"
                    type="button"
                    :title="sortOrder === 'asc' ? 'Ascendente' : 'Descendente'"
                  >
                    <i class="bi" :class="sortOrder === 'asc' ? 'bi-sort-alpha-down' : 'bi-sort-alpha-up'"></i>
                  </button>
                </div>
              </div>

              <!-- Botones de acción -->
              <div class="filter-actions">
                <button @click="handleSearch" class="btn btn-primary w-100 mb-2">
                  <i class="bi bi-search me-1"></i>
                  Buscar
                </button>
                <button @click="clearFilters" class="btn btn-outline-secondary w-100 mb-2">
                  <i class="bi bi-x-circle me-1"></i>
                  Limpiar
                </button>
                <button @click="openMapView" class="btn btn-outline-info w-100">
                  <i class="bi bi-map me-1"></i>
                  Ver Mapa
                </button>
              </div>
            </div>
          </div>
        </aside>

        <!-- Contenido Principal -->
        <main class="col-lg-9">
          <div class="content-container">
            <!-- Header -->
            <div class="content-header">
              <div>
                <h1 class="h3 mb-1">Explorar Sitios Históricos</h1>
                <p class="text-muted mb-0">
                  <i class="bi bi-geo-alt"></i>
                  {{ totalSites }} {{ totalSites === 1 ? 'sitio encontrado' : 'sitios encontrados' }}
                </p>
              </div>
              
              <!-- Botón toggle filtros (solo mobile) -->
              <button 
                class="btn btn-primary d-lg-none"
                @click="filtersExpanded = !filtersExpanded"
              >
                <i class="bi bi-funnel"></i>
                Filtros
              </button>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
              <p class="mt-3 text-muted">Cargando sitios históricos...</p>
            </div>

            <!-- Grid de Sitios -->
            <div v-else-if="sites.length > 0" class="sites-grid">
              <SiteCard v-for="site in sites" :key="site.id" :site="site" />
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

            <!-- Paginación -->
            <nav v-if="totalPages > 1 && !loading" aria-label="Paginación" class="mt-4">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" @click.prevent="goToPage(currentPage - 1)">
                    <i class="bi bi-chevron-left"></i>
                  </a>
                </li>
                
                <!-- Primera página -->
                <li v-if="currentPage > 3" class="page-item">
                  <a class="page-link" @click.prevent="goToPage(1)">1</a>
                </li>
                <li v-if="currentPage > 4" class="page-item disabled">
                  <span class="page-link">...</span>
                </li>
                
                <!-- Páginas cercanas -->
                <li 
                  v-for="page in paginationRange" 
                  :key="page"
                  class="page-item" 
                  :class="{ active: page === currentPage }"
                >
                  <a class="page-link" @click.prevent="goToPage(page)">
                    {{ page }}
                  </a>
                </li>
                
                <!-- Última página -->
                <li v-if="currentPage < totalPages - 3" class="page-item disabled">
                  <span class="page-link">...</span>
                </li>
                <li v-if="currentPage < totalPages - 2" class="page-item">
                  <a class="page-link" @click.prevent="goToPage(totalPages)">{{ totalPages }}</a>
                </li>
                
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <a class="page-link" @click.prevent="goToPage(currentPage + 1)">
                    <i class="bi bi-chevron-right"></i>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sites-view {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding-top: 1rem;
}

/* Filtros */
.filters-sidebar {
  padding: 0;
}

.filters-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: none;
}

.filters-sidebar.expanded .filters-container {
  display: block;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.filters-header h5 {
  color: white;
  font-weight: 600;
}

/* En mobile, colapsable */
.filters-content {
  padding: 1rem;
}

/* En desktop, siempre mostrar */
@media (min-width: 992px) {
  .filters-sidebar {
    padding: 0 1rem 0 2rem;
  }
  
  .filters-container {
    display: block !important;
  }
  
  .filters-content {
    padding: 1.5rem;
  }
}

.filter-group {
  margin-bottom: 1.25rem;
}

.filter-group .form-label {
  font-weight: 600;
  font-size: 0.95rem;
  color: #495057;
  margin-bottom: 0.5rem;
}

.filter-group .form-control,
.filter-group .form-select {
  border-radius: 6px;
  border: 1px solid #dee2e6;
  font-size: 0.95rem;
  padding: 0.5rem 0.75rem;
}

.filter-group .form-control:focus,
.filter-group .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.filter-group .input-group-text {
  background-color: white;
  border-right: none;
}

.filter-group .input-group .form-control {
  border-left: none;
}

.filter-actions {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.filter-actions .btn {
  border-radius: 6px;
  font-weight: 500;
}

/* Contenido Principal */
.content-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 2px solid #f0f0f0;
}

.content-header h1 {
  font-weight: 700;
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.content-header p {
  font-size: 1.05rem;
}

/* Grid de sitios */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Paginación */
.pagination {
  flex-wrap: wrap;
}

.page-link {
  cursor: pointer;
  color: #667eea;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin: 0 0.25rem;
  transition: all 0.2s;
}

.page-link:hover {
  background-color: #f0f2ff;
  border-color: #667eea;
  color: #667eea;
}

.page-item.active .page-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Diseño responsive */

/* Mobile (< 576px) */
@media (max-width: 575.98px) {
  .sites-view {
    padding-top: 0;
  }
  
  .filters-sidebar {
    margin-bottom: 1rem;
    padding: 0 0.5rem;
  }
  
  .content-container {
    padding: 1rem;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .sites-grid {
    grid-template-columns: 1fr;
  }
}

/* Tablet (576px - 991px) */
@media (min-width: 576px) and (max-width: 991.98px) {
  .filters-sidebar {
    padding: 0 1rem;
  }
  
  .sites-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop (>= 992px) */
@media (min-width: 992px) {
  .sites-view {
    padding-top: 2rem;
  }
  
  .filters-sidebar {
    position: sticky;
    top: 80px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
  
  .sites-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Large Desktop (>= 1400px) */
@media (min-width: 1400px) {
  .sites-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Scrollbar personalizado para el sidebar */
.filters-sidebar::-webkit-scrollbar {
  width: 6px;
}

.filters-sidebar::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.filters-sidebar::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.filters-sidebar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
</style>
