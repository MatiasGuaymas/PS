<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SiteCard from '../components/SiteCard.vue'
import Choices from 'choices.js'
import 'choices.js/public/assets/styles/choices.min.css'
import { useSites } from '../composables/useSites'
import { useFilters } from '../composables/useFilters'
import { LMap, LTileLayer, LCircle, LControl } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Composables
const { sites, loading, totalSites, totalPages, fetchSites } = useSites()
const { provinces, states, tags, loadAll } = useFilters()

// Estado de autenticación
const currentUser = ref(null)
const isAuthenticated = ref(false)
const userId = computed(() => currentUser.value?.id || null)

// Función para obtener el usuario actual
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

// Estados de filtros
const searchQuery = ref(route.query.search || '')
const currentPage = ref(parseInt(route.query.page) || 1)
const selectedCity = ref(route.query.city || '')
const selectedState = ref(route.query.state || '')
const selectedProvince = ref(route.query.province || '')
const selectedTags = ref(route.query.tags ? route.query.tags.split(',') : [])
const showFavoritesOnly = ref(route.query.favorites === 'true')
const sortBy = ref(route.query.sort || 'site_name')
const sortOrder = ref(route.query.order || 'asc')

const mapCenter = ref([parseFloat(route.query.lat) || -34.6037, parseFloat(route.query.lng) || -58.3816])
const mapRadius = ref(parseInt(route.query.radius) || 50000) 
const isGeoFiltered = ref(route.query.lat && route.query.lng && route.query.radius ? true : false)
const mapZoom = ref(10)
const showMap = ref(false)

const handleMapMove = (event) => {
  const newCenter = event.target.getCenter()
  const newZoom = event.target.getZoom()
  const bounds = event.target.getBounds()
  
  const centerPoint = L.latLng(newCenter.lat, newCenter.lng)
  const cornerPoint = L.latLng(bounds.getNorthEast().lat, bounds.getNorthEast().lng)
  const calculatedRadius = centerPoint.distanceTo(cornerPoint) / Math.sqrt(2)
  
  mapCenter.value = [newCenter.lat, newCenter.lng]
  mapRadius.value = Math.min(Math.round(calculatedRadius), 2000000)
  mapZoom.value = newZoom
  isGeoFiltered.value = true
}

const toggleGeoFilter = () => {
  isGeoFiltered.value = !isGeoFiltered.value
  handleSearch()
}

// UI State
const perPage = 12
const filtersExpanded = ref(false)
let choicesInstance = null

// Computed: Rango de páginas
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

// Construir objeto de filtros
const buildFilters = () => ({
  page: currentPage.value,
  perPage,
  sortBy: sortBy.value,
  sortOrder: sortOrder.value,
  searchQuery: searchQuery.value,
  province: selectedProvince.value,
  city: selectedCity.value,
  state: selectedState.value,
  tags: selectedTags.value,
  showFavoritesOnly: showFavoritesOnly.value,
  userId: userId.value,
  ...(isGeoFiltered.value ? {
    lat: mapCenter.value[0],
    lng: mapCenter.value[1],
    radius: mapRadius.value,
  } : {})
})

// Buscar sitios
const handleSearch = async () => {
  currentPage.value = 1
  updateURL()
  await fetchSites(buildFilters())
}

// Actualizar URL
const updateURL = () => {
  const query = {}
  if (searchQuery.value) query.search = searchQuery.value
  if (selectedCity.value) query.city = selectedCity.value
  if (selectedState.value) query.state = selectedState.value
  if (selectedProvince.value) query.province = selectedProvince.value
  if (selectedTags.value.length > 0) query.tags = selectedTags.value.join(',')
  if (showFavoritesOnly.value) query.favorites = 'true'
  if (sortBy.value !== 'site_name') query.sort = sortBy.value
  if (sortOrder.value !== 'asc') query.order = sortOrder.value
  if (currentPage.value > 1) query.page = currentPage.value
  if (isGeoFiltered.value) {
    query.lat = mapCenter.value[0]
    query.lng = mapCenter.value[1]
    query.radius = mapRadius.value
  }
  router.push({ query })
}

// Cambiar página
const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    updateURL()
    await fetchSites(buildFilters())
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Limpiar filtros
const clearFilters = async () => {
  searchQuery.value = ''
  selectedCity.value = ''
  selectedState.value = ''
  selectedProvince.value = ''
  selectedTags.value = []
  showFavoritesOnly.value = false
  sortBy.value = 'site_name'
  sortOrder.value = 'asc'
  currentPage.value = 1
  isGeoFiltered.value = false
  mapCenter.value = [-34.6037, -58.3816] // Centro por defecto
  mapRadius.value = 50000 // Radio por defecto
  mapZoom.value = 10 // Zoom por defecto
  showMap.value = false // Ocultar mapa
  
  if (choicesInstance) {
    choicesInstance.removeActiveItems()
  }
  
  updateURL()
  await fetchSites(buildFilters())
}

// Toggle orden
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  handleSearch()
}

// Toggle favoritos
const toggleFavorites = () => {
  showFavoritesOnly.value = !showFavoritesOnly.value
  handleSearch()
}

const openMapView = () => {
  showMap.value = true
  filtersExpanded.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Inicializar Choices.js
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
    
    tagsElement.addEventListener('change', (event) => {
      selectedTags.value = Array.from(event.target.selectedOptions).map(opt => opt.value)
    })
  }
}

// Cargar al montar
onMounted(async () => {
  await fetchCurrentUser()
  await loadAll()
  await initChoices()
  await fetchSites(buildFilters())
  if (route.query.lat && route.query.lng && route.query.radius) { 
    isGeoFiltered.value = true
    mapCenter.value = [parseFloat(route.query.lat), parseFloat(route.query.lng)]
    mapRadius.value = parseInt(route.query.radius)
    const radiusToZoom = (r) => Math.round(14 - Math.log(r / 1000) / Math.log(2));
    mapZoom.value = radiusToZoom(mapRadius.value);
  } else {
    isGeoFiltered.value = false
  }
})

// Watch para cambios en la ruta
watch(() => route.query, () => {
  searchQuery.value = route.query.search || ''
  currentPage.value = parseInt(route.query.page) || 1
  selectedCity.value = route.query.city || ''
  selectedState.value = route.query.state || ''
  selectedProvince.value = route.query.province || ''
  selectedTags.value = route.query.tags ? route.query.tags.split(',') : []
  showFavoritesOnly.value = route.query.favorites === 'true'
  sortBy.value = route.query.sort || 'site_name'
  sortOrder.value = route.query.order || 'asc'
  const lat = route.query.lat ? parseFloat(route.query.lat) : undefined
  const lng = route.query.lng ? parseFloat(route.query.lng) : undefined
  const radius = route.query.radius ? parseInt(route.query.radius) : undefined
  
  if (lat && lng && radius) {
    mapCenter.value = [lat, lng]
    mapRadius.value = radius
    isGeoFiltered.value = true
  } else if (!route.query.page || route.query.page === '1') {
    isGeoFiltered.value = false
    mapCenter.value = [-34.6037, -58.3816]
    mapRadius.value = 50000
    mapZoom.value = 10
  }
})
</script>

<template>
  <div class="sites-view">
    <div class="container-fluid">
      <div class="row">
        <aside class="col-lg-3 filters-sidebar" :class="{ 'expanded': filtersExpanded }">
          <div class="filters-container">
            <div class="filters-header d-none d-lg-block">
              <h5 class="mb-0">
                <i class="bi bi-funnel me-2"></i>
                Filtros y Búsqueda
              </h5>
            </div>

            <div class="filters-content" :class="{ 'show': filtersExpanded }">
              
              <div class="filter-group map-filter-group">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <label class="form-label mb-0">
                    <i class="bi bi-compass me-1"></i>
                    Filtro Geográfico
                  </label>
                  <button 
                    @click="showMap = !showMap"
                    class="btn btn-sm bi-map"
                    :class="showMap ? 'btn-outline-secondary' : 'btn-outline-info'"
                  >
                    {{ showMap ? ' Ocultar Mapa' : ' Mostrar Mapa' }}
                  </button>
                </div>

                <div v-if="showMap" class="map-container mb-3">
                  <div style="height: 200px; width: 100%;">
                    <l-map 
                      :zoom="mapZoom" 
                      :center="mapCenter" 
                      @moveend="handleMapMove" 
                      ref="mapRef"
                    >
                      <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap"></l-tile-layer>
                      
                      <l-circle 
                        :lat-lng="mapCenter" 
                        :radius="mapRadius" 
                        color="#764ba2"
                        :fill-opacity="0.1"
                        :weight="2"
                      />
                      
                      <l-control position="topright" class="map-radius-control">
                        Radio: {{ (mapRadius / 1000).toFixed(1) }} km
                      </l-control>
                    </l-map>
                  </div>
                </div>

                <button 
                  @click="toggleGeoFilter"
                  class="btn w-100"
                  :class="isGeoFiltered ? 'btn-success' : 'btn-outline-success'"
                >
                  <i class="bi" :class="isGeoFiltered ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                  {{ isGeoFiltered ? 'Filtro de Radio Activo' : 'Activar Filtro de Radio' }}
                </button>
                <small class="text-muted mt-2 d-block text-center">
                  Radio aprox. de búsqueda: **{{ (mapRadius / 1000).toFixed(1) }} km** <span v-if="isGeoFiltered" class="text-success">(Activo)</span>
                </small>
              </div>
              
              <hr v-if="showMap" />
              
              <div class="filter-group">
                <label class="form-label">Buscar</label>
                <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  type="text"
                  class="form-control"
                  placeholder="Nombre o descripción..."
                >
              </div>

              <div class="filter-group">
                <label class="form-label">Ciudad</label>
                <input
                  v-model="selectedCity"
                  type="text"
                  class="form-control"
                  placeholder="Ej: La Plata"
                >
              </div>

              <div class="filter-group">
                <label class="form-label">Provincia</label>
                <select v-model="selectedProvince" class="form-select">
                  <option value="">Todas</option>
                  <option v-for="province in provinces" :key="province" :value="province">
                    {{ province }}
                  </option>
                </select>
              </div>

              <div class="filter-group">
                <label class="form-label">Estado de conservación</label>
                <select v-model="selectedState" class="form-select">
                  <option value="">Todos</option>
                  <option v-for="state in states" :key="state.id" :value="state.id">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <div v-if="isAuthenticated" class="filter-group">
                <button 
                  @click="toggleFavorites"
                  class="btn w-100"
                  :class="showFavoritesOnly ? 'btn-danger' : 'btn-outline-danger'"
                >
                  <i class="bi" :class="showFavoritesOnly ? 'bi-heart-fill' : 'bi-heart'"></i>
                  {{ showFavoritesOnly ? 'Mostrando Favoritos' : 'Mostrar Favoritos' }}
                </button>
              </div>

              <div class="filter-group">
                <label class="form-label">Tags</label>
                <select 
                  id="tags-select" 
                  v-model="selectedTags"
                  multiple
                  class="form-select"
                >
                  <option v-for="tag in tags" :key="tag.id" :value="tag.id">
                    {{ tag.name }}
                  </option>
                </select>
              </div>

              <div class="filter-group">
                <label class="form-label">Ordenar por</label>
                <div class="input-group">
                  <select v-model="sortBy" class="form-select">
                    <option value="site_name">Nombre</option>
                    <option value="registration">Fecha</option>
                    <option value="rating">Rating</option>
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
              
              <div class="filter-actions">
                <button @click="handleSearch" class="btn btn-primary w-100 mb-2">
                  <i class="bi bi-search me-1"></i>
                  Buscar
                </button>
                <button @click="clearFilters" class="btn btn-outline-secondary w-100 mb-2">
                  <i class="bi bi-x-circle me-1"></i>
                  Limpiar
                </button>
              </div>
            </div>
          </div>
        </aside>

        <main class="col-lg-9">
          <div class="content-container">
            <div class="content-header">
              <div>
                <h1 class="h3 mb-1">Explorar Sitios Históricos</h1>
                <p class="text-muted mb-0">
                  <i class="bi bi-geo-alt"></i>
                  {{ totalSites }} {{ totalSites === 1 ? 'sitio encontrado' : 'sitios encontrados' }}
                </p>
              </div>
              
              <button 
                class="btn btn-primary d-lg-none"
                @click="filtersExpanded = !filtersExpanded"
              >
                <i class="bi bi-funnel"></i>
                Filtros
              </button>
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
              <p class="mt-3 text-muted">Cargando sitios históricos...</p>
            </div>

            <div v-else-if="sites.length > 0" class="sites-grid">
              <SiteCard v-for="site in sites" :key="site.id" :site="site" />
            </div>

            <div v-else class="text-center py-5">
              <i class="bi bi-search display-1 text-muted mb-3"></i>
              <h3>No se encontraron sitios</h3>
              <p class="text-muted">Intenta ajustar los filtros de búsqueda</p>
              <button @click="clearFilters" class="btn btn-primary">
                Limpiar Filtros
              </button>
            </div>

            <nav v-if="totalPages > 1 && !loading" aria-label="Paginación" class="mt-4">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" @click.prevent="goToPage(currentPage - 1)">
                    <i class="bi bi-chevron-left"></i>
                  </a>
                </li>
                
                <li v-if="currentPage > 3" class="page-item">
                  <a class="page-link" @click.prevent="goToPage(1)">1</a>
                </li>
                <li v-if="currentPage > 4" class="page-item disabled">
                  <span class="page-link">...</span>
                </li>
                
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
  min-height: calc(100vh - 200px);
  background-color: #f8f9fa;
  padding-top: 1rem;
  padding-bottom: 2rem;
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

/* Estilos específicos para el mapa */
.map-container {
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 0 5px rgba(0,0,0,0.1);
}

.map-radius-control {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 5px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #764ba2;
  border: 1px solid #764ba2;
}

.map-filter-group {
    padding: 0.5rem 0;
    border-bottom: 1px dashed #dee2e6;
    margin-bottom: 1rem;
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
    position: sticky;
    top: 80px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }
  
  .filters-content {
    padding: 1.5rem;
  }
}

.filter-group {
  margin-bottom: 1rem;
}

.filter-group .form-label {
  font-weight: 600;
  font-size: 0.875rem;
  color: #495057;
  margin-bottom: 0.4rem;
}

.filter-group .form-control,
.filter-group .form-select {
  border-radius: 6px;
  border: 1px solid #dee2e6;
  font-size: 0.875rem;
  padding: 0.5rem 0.625rem;
}

.filter-group .form-control:focus,
.filter-group .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.filter-group .input-group-text {
  background-color: white;
  border-right: none;
  font-size: 0.875rem;
}

.filter-group .input-group .form-control {
  border-left: none;
}

/* Botón de favoritos */
.filter-group .btn-outline-danger {
  border-width: 2px;
  transition: all 0.3s ease;
}

.filter-group .btn-outline-danger:hover {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.filter-group .btn-danger {
  transition: all 0.3s ease;
  animation: heartBeat 0.3s ease-in-out;
}

.filter-group .btn-danger:hover {
  transform: scale(1.05);
}

@keyframes heartBeat {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.filter-group .btn i {
  margin-right: 0.5rem;
  font-size: 1rem;
}

.filter-actions {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.filter-actions .btn {
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
}

/* Contenido Principal */
.content-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  min-height: calc(100vh - 200px);
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
  margin-bottom: 2rem;
}

/* Paginación */
.pagination {
  flex-wrap: wrap;
  margin-bottom: 2rem;
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
    min-height: auto;
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
    margin-bottom: 1.5rem;
  }
  
  .sites-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-container {
    min-height: auto;
  }
}

/* Desktop (>= 992px) */
@media (min-width: 992px) {
  .sites-view {
    padding-top: 2rem;
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
.filters-container::-webkit-scrollbar {
  width: 6px;
}

.filters-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.filters-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.filters-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
</style>
