<template>
  <div class="container py-4">
    <div class="mb-3 d-flex justify-content-between align-items-center flex-nowrap">
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="goBack"><i class="bi bi-arrow-left"></i> Volver</button>
      </div>
      <div class="d-flex align-items-center">
        <button class="btn btn-sm btn-primary me-2" @click="addReview"><i class="bi bi-chat-dots-fill"></i> Agregar reseña</button>
        <button class="btn btn-sm btn-info me-2" @click="addLiked" :disabled="favLoading">
          <span v-if="favLoading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          <span v-else-if="favorited" class="bi bi-heart-fill me-1"></span>
          <span v-else class="bi bi-heart me-1"></span>
          Añadir a favoritos
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="!result" class="alert alert-warning">No se encontró el sitio.</div>

    <div v-else class="card shadow-sm">
      <div class="row g-0">
        <div class="col-md-5">
          <img v-if="coverUrl" :src="coverUrl" :alt="result.name" class="img-fluid rounded-start"
            style="object-fit:cover; width:100%; height:100%; cursor:zoom-in;"
            @click="openLightbox({ public_url: coverUrl, title_alt: result.name })" />
          <div v-else class="d-flex align-items-center justify-content-center bg-light" style="height:100%;">
            <span class="text-muted">Sin imagen de portada</span>
          </div>
        </div>

        <div class="col-md-7">
          <div class="card-body">
            <h2 class="card-title mb-1">{{ result.name }}</h2>
            <div class="mb-2 text-muted">
              <small>{{ result.city }}{{ result.city && result.province ? ' / ' : '' }}{{ result.province }}</small>
              <span v-if="result.state_name" :class="['chip', stateChipClass, 'ms-2']">{{ result.state_name }}</span>
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
                <div v-for="(img, idx) in result.images" :key="idx" class="flex-shrink-0" style="width:120px">
                  <img
                    :src="img.public_url"
                    :alt="img.title_alt"
                    class="img-thumbnail"
                    style="width:100%; height:80px; object-fit:cover; cursor:zoom-in;"
                    @click="openLightbox(img)"
                  />
                </div>
              </div>
            </div>

            <div class="mt-3">
              <h6>Tags</h6>
              <div>
                <button v-if="(!result.tags || result.tags.length === 0)" class="btn btn-sm btn-outline-secondary"
                  disabled>Sin tags</button>
                <button v-for="(tag, i) in result.tags" :key="tag.id || i" class="btn btn-sm btn-outline-info me-1 mb-1"
                  @click="onTagClick(tag)">{{ tag.name || tag }}</button>
              </div>
            </div>

            <div class="mt-3 text-muted small">
              <div>Registro: {{ formattedRegistration }}</div>
            </div>

            <div v-if="hasCoords" class="mt-3">
              <h6>Ubicación</h6>
              <div id="map" style="height:300px; width:100%; border-radius:6px; overflow:hidden;"></div>
            </div>

            <div v-if="lightbox.visible" class="lightbox-overlay" @click.self="closeLightbox">
              <div class="lightbox-content">
                <img :src="lightbox.img.public_url" :alt="lightbox.img.title_alt" />
                <div class="lightbox-caption">{{ lightbox.img.title_alt }}</div>
                <button class="btn btn-sm btn-light lightbox-close" @click="closeLightbox">Cerrar</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_URL || 'https://grupo21.proyecto2025.linti.unlp.edu.ar',
      siteId: null,
      result: null,
      loading: false,
      error: null,
      showFull: false,
      map: null,
      lightbox: { visible: false, img: null },
      favLoading: false,
      favorited: false,
    }
  },
  created() {
    this.siteId = this.$route.params.id
  },
  async mounted() {
    await this.fetchSite()
 
    // obtener el estado inicial del favorito
    await this.fetchFavoriteStatus()
  },
  methods: {
    goBack() {
      const from = this.$route.query.from
      if (from) {
        try {
          const parsed = new URL(from, window.location.origin)
          if (parsed.origin === window.location.origin) {
            const qp = Object.fromEntries(parsed.searchParams.entries())
            return this.$router.push({ path: parsed.pathname, query: qp })
          } else {
            window.location.href = from
            return
          }
        } catch (e) {
          const [path, qs] = from.split('?')
          if (qs) {
            const qp = Object.fromEntries(new URLSearchParams(qs).entries())
            return this.$router.push({ path, query: qp })
          }
          return this.$router.push(from)
        }
      }

      if (window.history.length > 1) {
        this.$router.back()
        return
      }

      const fallbackQuery = {}
      const q = this.$route.query
      ['tag','q','province','category','state','page','per_page'].forEach(k => { if (q[k]) fallbackQuery[k]=q[k] })
      this.$router.push({ path: '/sitios', query: fallbackQuery })
    },
    async fetchSite() {
      if (!this.siteId) {
        this.error = 'No se especificó la ID del sitio.'
        return
      }
      this.loading = true
      this.error = null
      try {
        const base = this.apiBaseUrl
        const url = `${base}/api/sites/${encodeURIComponent(this.siteId)}`
        const response = await axios.get(url)
        const payload = response.data || {}
        this.result = payload.data || payload
        this.$nextTick(() => { this.initMap() })
      } catch (e) {
        this.error = e.response?.data?.message || e.message || 'Error desconocido'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async fetchFavoriteStatus() {
      if (!this.siteId) return
      try {
        const base = this.apiBaseUrl || ''
        const url = `${base}/api/sites/${encodeURIComponent(this.siteId)}/favorite`
        const res = await axios.get(url)
        if (res && res.data) {
          if (res.data.favorited !== undefined) {
            this.favorited = !!res.data.favorited
          } else if (res.data.status) {
            this.favorited = res.data.status === 'favorited' || res.data.status === 'ok'
          } else {
            this.favorited = false
          }
        }
      } catch (e) {
        if (e.response && e.response.status && e.response.status !== 404) console.error(e)
        this.favorited = false
      }
    },
    toggleDescription() {
      this.showFull = !this.showFull
    },
    onTagClick(tag) {
      const id = tag?.id || tag
      this.$router.push({ path: '/sitios', query: { tags: id } })
    },
    async initMap(attempt = 0) {
      if (!this.result) return
      const MAX = 10
      const DELAY = 50
      const el = document.getElementById('map')
      if (!el) {
        if (attempt >= MAX) {
          console.error('Error al cargar el mapa.')
          return
        }
        return setTimeout(() => this.initMap(attempt + 1), DELAY)
      }

      if (this.map) {
        try { this.map.remove() } catch (_) { }
        this.map = null
      }

      const lat = parseFloat(this.result.latitude)
      const lng = parseFloat(this.result.longitude)
      const hasCoords = !Number.isNaN(lat) && !Number.isNaN(lng)
      const center = hasCoords ? [lat, lng] : [-34.6037, -58.3816]

      try {
        this.map = L.map(el, { center, zoom: hasCoords ? 15 : 10, scrollWheelZoom: true })

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map)

        if (hasCoords) {
          L.circleMarker([lat, lng], {
            radius: 9,
            color: '#d00',
            fillColor: '#f03',
            fillOpacity: 0.7
          }).addTo(this.map).bindPopup(this.result.name + ": " + this.result.short_desc || '').openPopup()
        }

        setTimeout(() => { try { this.map.invalidateSize() } catch (e) { } }, 200)
      } catch (err) {
        console.error('Error inicializando Leaflet', err)
      }
    },
    openLightbox(img) {
      this.lightbox.img = img || {}
      this.lightbox.visible = true
    },
    closeLightbox() {
      this.lightbox.visible = false
      this.lightbox.img = null
    },
    async addLiked() {
      if (!this.siteId) return
      this.favLoading = true
      this.error = null
      try {
        const base = this.apiBaseUrl || ''
        const url = `${base.replace(/\/$/, '')}/api/sites/${encodeURIComponent(this.siteId)}/favorite`
        const payload = { user_id: 1 } // temporal: user hardcodeado
        const res = await axios.post(url, payload)
        if (res && res.data) {
          const st = res.data.status
          if (st === 'favorited' || st === 'ok') {
            this.favorited = true
          } else if (st === 'unfavorited') {
            this.favorited = false
          } else if (res.data.favorited !== undefined) {
            this.favorited = !!res.data.favorited
          } else {
            // fallback: alternar localmente
            this.favorited = !this.favorited
          }
        } else {
          this.favorited = !this.favorited
        }
      } catch (e) {
        this.error = e.response?.data?.message || e.message || 'Error al marcar favorito'
        console.error(e)
      } finally {
        this.favLoading = false
      }
    }
  },
  computed: {
    stateChipClass() {
      const s = (this.result?.state_name || '').toLowerCase()
      if (!s) return 'chip-default'
      if (s.includes('bueno') || s.includes('excelente') || s.includes('good') || s.includes('buena')) return 'chip-good'
      if (s.includes('regular') || s.includes('medio') || s.includes('fair')) return 'chip-regular'
      if (s.includes('malo') || s.includes('deficiente') || s.includes('poor') || s.includes('mala')) return 'chip-bad'
      return 'chip-default'
    },
    coverUrl() {
      if (!this.result) return null
      return this.result.cover_image_url || (this.result.images && this.result.images.find(i => i.is_cover)?.public_url) || null
    },
    gallery() {
      if (!this.result) return []
      return this.result.images || []
    },
    hasCoords() {
      return this.result && this.result.latitude != null && this.result.longitude != null
    },
    formattedRegistration() {
      if (!this.result || !this.result.registration) return '—'
      try {
        return new Date(this.result.registration).toLocaleString()
      } catch { return this.result.registration }
    }
  },
  beforeUnmount() {
    if (this.map) {
      try { this.map.remove() } catch (_) { }
      this.map = null
    }
  }
}
</script>

<style scoped>
.card {
  overflow: hidden;
}

#map {
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.lightbox-content {
  position: relative;
  max-width: 1200px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lightbox-content img {
  max-width: 100%;
  max-height: calc(90vh - 60px);
  object-fit: contain;
  border-radius: 6px;
  display: block;
}

.lightbox-caption {
  color: #fff;
  margin-top: 8px;
  text-align: center;
  word-break: break-word;
}

.lightbox-close {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10000;
}
.chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
}
.chip-default { background: #6c757d; } 
.chip-good    { background: #198754; } 
.chip-regular { background: #0d6efd; } 
.chip-bad     { background: #dc3545; } 
</style>
