<script setup>
defineProps({
  site: {
    type: Object,
    required: true
  }
})

// Helper para verificar si tiene imagen
const hasImage = (site) => {
  return !!(site.cover_image && site.cover_image.trim() !== '')
}

// Helper para obtener imagen
const getImageUrl = (site) => {
  if (site.cover_image && site.cover_image.trim() !== '') {
    return site.cover_image
  }
  return null
}

// Manejar error de carga de imagen
const handleImageError = (event) => {
  event.target.style.display = 'none'
  event.target.nextElementSibling.style.display = 'flex'
}

// Mostrar máximo 5 tags
const displayTags = (tags) => {
  if (!tags) return []
  return tags.slice(0, 5)
}

// Verifica si tiene calificación
const hasRating = (site) => {
  return site.reviews_average && site.reviews_average > 0
}

// Obtener texto de calificación
const getRatingText = (site) => {
  if (!site.reviews_average || site.reviews_average === 0) {
    return 'Sin calificaciones'
  }
  return site.reviews_average.toFixed(1)
}

</script>

<template>
  <div class="site-card card h-100 shadow-sm">
    <!-- Imagen -->
    <div class="card-img-wrapper">
      <img
        v-if="hasImage(site)"
        :src="getImageUrl(site)"
        class="card-img-top"
        :alt="site.site_name || site.name"
        @error="handleImageError"
      >
      <!-- Placeholder cuando no hay imagen -->
      <div v-else class="no-image-placeholder">
        <i class="bi bi-image display-1 text-muted"></i>
        <p class="text-muted mt-2 mb-0">Sin imagen</p>
      </div>
      
      <!-- Calificación -->
      <div class="rating-badge" :class="{ 'no-rating': !hasRating(site) }">
        <template v-if="hasRating(site)">
          <i class="bi bi-star-fill text-warning"></i>
          <span class="fw-bold">{{ getRatingText(site) }}</span>
        </template>
        <template v-else>
          <i class="bi bi-star text-muted"></i>
          <span class="text-muted small">Sin calificaciones</span>
        </template>
      </div>
      
      <!-- Estado -->
      <div v-if="site.state" class="state-badge" :class="`state-${site.state.name.toLowerCase()}`">
        {{ site.state.name }}
      </div>
    </div>

    <!-- Contenido -->
    <div class="card-body d-flex flex-column">
      <h5 class="card-title fw-bold mb-2">{{ site.site_name || site.name }}</h5>
      
      <p class="card-text text-muted mb-2">
        <i class="bi bi-geo-alt-fill text-danger"></i>
        {{ site.city }}, {{ site.province }}
      </p>

      <!-- Descripción corta -->
      <p class="card-text text-secondary small mb-3">
        {{ site.short_desc }}
      </p>

      <!-- Tags -->
      <div v-if="site.tags && site.tags.length > 0" class="tags-container mb-3">
        <span 
          v-for="tag in displayTags(site.tags)" 
          :key="tag.id || tag.name" 
          class="badge bg-light text-dark me-1 mb-1"
        >
          <i class="bi bi-tag-fill me-1"></i>{{ tag.name }}
        </span>
      </div>

      <!-- Ver detalle -->
      <a 
        :href="`/sitios/${site.id}`" 
        class="btn btn-primary w-100 mt-auto"
      >
        <i class="bi bi-eye me-1"></i>
        Ver detalle
      </a>
    </div>
  </div>
</template>

<style scoped>
.site-card {
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.site-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 0.75rem 1.5rem rgba(0, 0, 0, 0.15) !important;
}

.card-img-wrapper {
  position: relative;
  overflow: hidden;
  height: 220px;
}

.card-img-top {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.no-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
}

.site-card:hover .card-img-top {
  transform: scale(1.05);
}

/* Califación */

.rating-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.rating-badge.no-rating {
  background: rgba(248, 249, 250, 0.95);
  padding: 6px 10px;
}

.rating-badge.no-rating .small {
  font-size: 0.75rem;
  font-weight: 500;
}

.state-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Estados con colores específicos */
.state-bueno {
  background: rgba(40, 167, 69, 0.95);
  color: white;
}

.state-regular {
  background: rgba(255, 193, 7, 0.95);
  color: #212529;
}

.state-malo {
  background: rgba(220, 53, 69, 0.95);
  color: white;
}

.state-publicado {
  background: rgba(40, 167, 69, 0.95);
  color: white;
}

.state-borrador {
  background: rgba(108, 117, 125, 0.95);
  color: white;
}

.card-title {
  font-size: 1.1rem;
  color: #2c3e50;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-text.small {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
  flex-grow: 1;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tags-container .badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.35rem 0.6rem;
  border: 1px solid #dee2e6;
}

@media (max-width: 576px) {
  .card-img-wrapper {
    height: 180px;
  }
  .rating-badge {
    padding: 4px 8px;
    font-size: 0.8rem;
  }
  .rating-badge.no-rating .small {
    font-size: 0.7rem;
  }
}
</style>
