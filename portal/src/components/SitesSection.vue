<script setup>
import { computed } from 'vue'
import SiteCard from './SiteCard.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: 'primary'
  },
  sites: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  viewAllLink: {
    type: String,
    default: '#'
  }
})

const hasSites = computed(() => props.sites && props.sites.length > 0)
</script>

<template>
  <section class="sites-section mb-5">
    <!-- Header -->
    <div class="section-header d-flex justify-content-between align-items-center mb-4">
      <h2 class="h3 fw-bold mb-0">
        <i :class="`bi bi-${icon} text-${iconColor} me-2`"></i>
        {{ title }}
      </h2>
      <a 
        v-if="hasSites"
        :href="viewAllLink" 
        class="btn btn-outline-primary btn-sm"
      >
        Ver todos
        <i class="bi bi-arrow-right ms-1"></i>
      </a>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <p class="mt-3 text-muted">Cargando sitios...</p>
    </div>

    <!-- Grid de tarjetas -->
    <div v-else-if="hasSites" class="row g-4">
      <div
        v-for="site in sites"
        :key="site.id"
        class="col-12 col-sm-6 col-lg-4 col-xl-3"
      >
        <SiteCard :site="site" />
      </div>
    </div>

    <!-- Mensaje sin contenido -->
    <div v-else class="alert alert-info d-flex align-items-center">
      <i class="bi bi-info-circle me-2 fs-5"></i>
      <div>
        <strong>No hay sitios disponibles</strong>
        <p class="mb-0 small">Esta sección estará disponible próximamente.</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sites-section {
  animation: fadeIn 0.5s ease-out;
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
  border-bottom: 3px solid #f0f0f0;
  padding-bottom: 1rem;
}

.section-header h2 {
  color: #2c3e50;
}

@media (max-width: 576px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 1rem;
  }
  
  .section-header .btn {
    width: 100%;
  }
}
</style>
