<template>
  <div class="container py-4">
    <div class="mb-3 d-flex justify-content-between align-items-center flex-nowrap">
      <div>
        <button class="btn btn-sm btn-outline-secondary" @click="goBack"><i class="bi bi-arrow-left"></i> Volver</button>
      </div>
      <div class="d-flex align-items-center">
        <template v-if="!canFavorite">
          <button class="btn btn-sm btn-primary" @click="loginWithGoogle">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 48 48" class="me-1">
              <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
              <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
              <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
              <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
            </svg>
            Inicia sesión para añadir a favoritos y dejar reseñas
          </button>
        </template>
        
        <template v-else>
          <button class="btn btn-sm btn-primary me-2" @click="addReview">
            <i class="bi bi-chat-dots-fill"></i> Agregar reseña
          </button>
          <button class="btn btn-sm btn-info me-2" @click="addLiked" :disabled="favLoading">
            <span v-if="favLoading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            <span v-else-if="favorited" class="bi bi-heart-fill me-1"></span>
            <span v-else class="bi bi-heart me-1"></span>
            Añadir a favoritos
          </button>
        </template>
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

    <!-- Reviews list -->
    <div class="mt-4">
      <h5>Reseñas</h5>
      <div v-if="reviewsLoading" class="py-3 text-center">
        <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
      </div>
      <div v-else>
        <div v-if="!reviews || reviews.length === 0" class="text-muted">Aún no hay reseñas para este sitio.</div>
        <div v-else class="table-responsive">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Puntuación</th>
                <th>Comentario</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, i) in reviews" :key="r.id || i">
                <td>{{ r.user_email || r.user_name || r.user || 'Anónimo' }}</td>
                <td>{{ r.rating ?? r.stars ?? '—' }}</td>
                <td>{{ r.comment || r.body || '—' }}</td>
                <td>{{ formatDate(r.created_at || r.created || r.date) }}</td>
              </tr>
            </tbody>
          </table>
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
      apiBaseUrl: import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar',
      siteId: null,
      result: null,
      loading: false,
      error: null,
      showFull: false,
      map: null,
      lightbox: { visible: false, img: null },
      favLoading: false,
      favorited: false,
      currentUser: null,
      canFavorite: false,
      reviews: [],
      reviewsLoading: false,
    }
  },
  created() {
    this.siteId = this.$route.params.id
  },
  async mounted() {
    await this.fetchSite()
  
    // obtener el estado inicial del favorito
    await this.getCurrentUser()
    if(this.currentUser && this.currentUser.id)
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

    loginWithGoogle() {
      // Guardar la URL actual para volver después del login
      const currentUrl = encodeURIComponent(window.location.href)
      
      // Redirigir al login de Google
      window.location.href = `${this.apiBaseUrl}/auth/login-google?origin=public&redirect_to=${currentUrl}`
    },
    async fetchReviews() {
      if (!this.siteId) return
      this.reviewsLoading = true
      try {
        const base = (this.apiBaseUrl || '').replace(/\/$/, '')
        const url = `${base}/api/reviews/list/${encodeURIComponent(this.siteId)}`
        const res = await axios.get(url)
        console.log(res)
        this.reviews = (res && res.data && res.data.data) ? res.data.data : (res.data || [])
      } catch (e) {
        console.error('fetchReviews error', e)
        this.reviews = []
      } finally {
        this.reviewsLoading = false
      }
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
        await this.fetchReviews()
      } catch (e) {
        this.error = e.response?.data?.message || e.message || 'Error desconocido'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async getCurrentUser() {
      const base = this.apiBaseUrl
      const url = `${base}/auth/me`
      const response = await fetch(url, {
        credentials: 'include'
      })
      const payload = await response.json()
      if(payload.id) {
        this.currentUser = payload
        this.canFavorite = true
      }
    },
    async fetchFavoriteStatus() {
      if (!this.siteId) return
      try {
        const base = this.apiBaseUrl || ''
        const url = `${base}/api/sites/${encodeURIComponent(this.siteId)}/get_favorite`
        const res = await axios.get(url, { params: { user_id: this.currentUser.id } })
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
        this.favorited = false
      }
    },
    formatDate(dt) {
      if (!dt) return '—'
      try { return new Date(dt).toLocaleString() } catch { return dt }
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
          console.log('Error al cargar el mapa.')
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
      this.lightbox.lightbox.visible = false
      this.lightbox.img = null
    },
    async addLiked() {
      if (!this.siteId) return
      this.favLoading = true
      this.error = null
      try {
        const base = this.apiBaseUrl
        const url = `${base}/api/sites/${encodeURIComponent(this.siteId)}/favorite`
        const res = await axios.get(url, { params: { user_id: this.currentUser.id } })
        if (res && res.data) {
          const st = res.data.status
          if (st === 'favorited' || st === 'ok') {
            this.favorited = true
          } else if (st === 'unfavorited') {
            this.favorited = false
          } else if (res.data.favorited !== undefined) {
            this.favorited = !!res.data.favorited
          } else {
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
    },
    
    async addReview() {
      if (!this.siteId) {
        console.error("No se puede agregar reseña: siteId no está disponible.");
        return;
      }
      
      try {
        // 1. Construir URL con el email explícito 
        let url = `${this.apiBaseUrl}/api/reviews/check-existing?site_id=${this.siteId}`;
        
        // Si tenemos el usuario cargado, enviamos su email para evitar errores de sesión cruzada
        if (this.currentUser && this.currentUser.email) {
            url += `&user_email=${encodeURIComponent(this.currentUser.email)}`;
        }

        const response = await axios.get(url, { withCredentials: true });
        
        if (response.data.has_review && response.data.review_id) {
          console.log('✅ Reseña existente detectada. Redirigiendo a edición.');
          
          this.$router.push({ 
            name: 'edit-review', 
            params: { reviewId: response.data.review_id, siteId: this.siteId }
          });
          
        } else {
          console.log('ℹ️ No hay reseña existente. Redirigiendo a creación.');
          this.$router.push({ 
            name: 'new-review', 
            query: { site_id: this.siteId } 
          });
        }
      } catch (error) {
        console.error("Error al verificar reseña existente:", error);
        // Fallback
        this.$router.push({ 
          name: 'new-review', 
          query: { site_id: this.siteId } 
        });
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

.btn-primary svg {
  vertical-align: middle;
}

.chip-default { background: #6c757d; } 
.chip-good    { background: #198754; } 
.chip-regular { background: #0d6efd; } 
.chip-bad     { background: #dc3545; } 
</style>