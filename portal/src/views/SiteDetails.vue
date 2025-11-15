<script>
import axios from 'axios'; 

export default {
  data() {
    return {
      siteId: null,
      result: null,
      loading: false,
      error: null
    }
  },
  created() {
    this.siteId = this.$route.params.id
  },
  async mounted() {
    await this.fetchSite()
  },
  methods: {
    async fetchSite() {
      if (!this.siteId) {
        this.error = 'Site ID no provisto'
        return
      }
      this.loading = true
      this.error = null
      try {
        const url = `http://localhost:5000/api/sites/${encodeURIComponent(this.siteId)}`
        const response = await axios.get(url)
        const payload = response.data || {}
        this.result = payload.data || payload
      } catch (e) {
        this.error = e.response?.data?.message || e.message || 'Error desconocido'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    toggleDescription() {
      this.showFull = !this.showFull
    },
    onTagClick(tag) {
      const name = tag?.name || tag
      this.$router.push({ path: '/sitios', query: { tag: name } })
    }
  },
  computed: {
    coverUrl() {
      if (!this.result) return null
      return this.result.cover_image_url || (this.result.images && this.result.images.find(i => i.is_cover)?.public_url) || null
    },
    gallery() {
      if (!this.result) return []
      return this.result.images || []
    }
  }
}
</script>

<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="!result" class="alert alert-warning">No se encontró el sitio.</div>

    <div v-else class="card shadow-sm">
      <div class="row g-0">
        <div class="col-md-5">
          <img v-if="coverUrl" :src="coverUrl" :alt="result.name" class="img-fluid rounded-start" style="object-fit:cover; width:100%; height:100%;">
          <div v-else class="d-flex align-items-center justify-content-center bg-light" style="height:100%;">
            <span class="text-muted">Sin imagen de portada</span>
          </div>
        </div>

        <div class="col-md-7">
          <div class="card-body">
            <h2 class="card-title mb-1">{{ result.name }}</h2>
            <div class="mb-2 text-muted">
              <small>{{ result.city }}{{ result.city && result.province ? ' / ' : '' }}{{ result.province }}</small>
              <span v-if="result.state_name" class="badge bg-secondary ms-2">{{ result.state_name }}</span>
            </div>

            <p class="mb-1"><strong>Categoría:</strong> {{ result.category_name || '—' }}</p>
            <p class="mb-1"><strong>Año de apertura:</strong> {{ result.opening_year || result.openingYear || '—' }}</p>

            <hr>

            <div>
              <p v-if="result.short_desc && !showFull" class="mb-2">{{ result.short_desc }}</p>
              <p v-if="showFull && result.full_desc" class="mb-2">{{ result.full_desc }}</p>
              <p v-else-if="!result.short_desc && result.full_desc" class="mb-2">{{ result.full_desc }}</p>

              <button v-if="result.full_desc" class="btn btn-sm btn-outline-primary" @click="toggleDescription">
                {{ showFull ? 'Ver menos' : 'Ver más' }}
              </button>
            </div>

            <div class="mt-3">
              <h6>Imágenes</h6>
              <div class="d-flex gap-2 overflow-auto py-2">
                <div v-for="(img, idx) in gallery" :key="idx" class="flex-shrink-0" style="width:120px">
                  <img :src="img.public_url || img.file_path" :alt="img.title_alt || img.description || result.name" class="img-thumbnail" style="width:100%; height:80px; object-fit:cover;">
                </div>
              </div>
            </div>

            <div class="mt-3">
              <h6>Tags</h6>
              <div>
                <button v-if="(!result.tags || result.tags.length===0)" class="btn btn-sm btn-outline-secondary" disabled>Sin tags</button>
                <button v-for="(tag, i) in result.tags" :key="tag.id || i" class="btn btn-sm btn-outline-info me-1 mb-1" @click="onTagClick(tag)">{{ tag.name || tag }}</button>
              </div>
            </div>

            <div class="mt-3 text-muted small">
              <div>Registro: {{ new Date(result.registration).toLocaleString() }}</div>
              <div v-if="result.latitude && result.longitude">Coordenadas: {{ result.latitude }}, {{ result.longitude }}</div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card { overflow: hidden; }
</style>
