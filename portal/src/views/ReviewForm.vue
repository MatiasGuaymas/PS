<template>
  <div class="container py-4 review-form-container">
    <div class="mb-3 d-flex justify-content-between align-items-center">
      <button class="btn btn-sm btn-outline-secondary" @click="goBack">
        <i class="bi bi-arrow-left"></i> Volver a {{ siteName || 'el sitio' }}
      </button>
    </div>

    <h2 class="mb-4">{{ isEditing ? 'Editar Reseña' : 'Crear Reseña' }} para: {{ siteName }}</h2>

    <!-- Mensajes de Estado -->
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="isPendingModeration" class="alert alert-warning">
      ¡Atención! Tu reseña editada ha vuelto a estado **"Pendiente de Aprobación"**. Se mostrará una vez sea moderada.
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
    </div>
    
    <!-- Formulario de Reseña -->
    <form v-else @submit.prevent="handleSubmit" class="card p-4 shadow-sm">
      
      <!-- Puntuación -->
      <div class="mb-3">
        <label for="rating" class="form-label">Puntuación (1 a 5)<span class="text-danger">*</span></label>
        <div>
          <template v-for="n in 5" :key="n">
            <i class="bi" 
              :class="{'bi-star-fill text-warning': rating >= n, 'bi-star': rating < n}" 
              @click="rating = n" 
              style="font-size: 1.5rem; cursor: pointer;"></i>
          </template>
        </div>
        <input type="hidden" id="rating" v-model.number="rating" required min="1" max="5">
        <div v-if="validationErrors.rating" class="text-danger small">{{ validationErrors.rating }}</div>
      </div>

      <!-- Texto de la Reseña -->
      <div class="mb-3">
        <label for="reviewText" class="form-label">Tu Reseña<span class="text-danger">*</span></label>
        <textarea 
          id="reviewText" 
          v-model="reviewText" 
          class="form-control" 
          rows="5" 
          required 
          minlength="20" 
          maxlength="1000"
          :placeholder="`Escribe tu reseña (20-1000 caracteres). Caracteres actuales: ${reviewText.length}`"
        ></textarea>
        <div class="text-muted small text-end">{{ reviewText.length }}/1000</div>
        <div v-if="validationErrors.reviewText" class="text-danger small">{{ validationErrors.reviewText }}</div>
      </div>

      <!-- Botones de Acción -->
      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting || loading">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
          {{ isEditing ? 'Guardar Cambios' : 'Enviar Reseña' }}
        </button>

        <button v-if="isEditing" type="button" class="btn btn-danger" @click="showDeleteModal = true" :disabled="isSubmitting">
          <i class="bi bi-trash-fill"></i> Eliminar Reseña
        </button>
      </div>
    </form>

    <!-- Modal de Confirmación de Eliminación -->
    <div v-if="showDeleteModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i> Confirmar Eliminación</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>¿Estás seguro de que quieres eliminar tu reseña? Esta acción no se puede deshacer.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false" :disabled="isSubmitting">Cancelar</button>
            <button type="button" class="btn btn-danger" @click="handleDeleteConfirm" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
              Sí, Eliminar
            </button>
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
    const siteId = this.$route.params.siteId || this.$route.query.site_id;
    return {
      apiBaseUrl: import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar',
      siteId: siteId,
      reviewId: this.$route.params.reviewId || null,
      siteName: 'Cargando...',
      
      rating: 0,
      reviewText: '',
      
      loading: true,
      isSubmitting: false,
      isEditing: !!this.$route.params.reviewId,
      isPendingModeration: false,
      errorMessage: null,
      successMessage: null,
      validationErrors: { rating: null, reviewText: null },
      
      showDeleteModal: false, 
      currentUserEmail: null, 
    };
  },

  async created() {
    
    if (!this.siteId) {
      this.errorMessage = 'No se pudo obtener el ID del sitio. Regresa a la lista.';
      this.loading = false;
      return;
    }

    try {
        // PASO CLAVE: Obtener el email de la sesión antes de hacer cualquier otra cosa
        await this.fetchCurrentUserEmail(); 
    } catch (e) {
        // Si fetchCurrentUserEmail falla, el mensaje de error ya está en this.errorMessage
        return; 
    }
    
    await this.fetchSiteName();
    
    if (this.reviewId) {
      // 1. CASO EDICIÓN (ID viene en la URL)
      await this.fetchReviewToEdit();
    } else {
      // 2. CASO CREACIÓN: Verificar si ya existe una reseña
      const checkResult = await this.checkExistingReview();
      
      if (checkResult.hasReview) {
        
        // REDIRECCIÓN CRÍTICA: Cambia la ruta en el navegador a /edit/:id
        this.$router.replace({ 
            path: `/sitios/${this.siteId}/reviews/${checkResult.reviewId}/edit` 
        }).catch(err => {
           // Se ignora el error si la navegación es redundante
           if (err.name !== 'NavigationDuplicated') {
               throw err;
           }
        });
        
        // Evita que el formulario de creación se muestre por un instante y carga los datos
        this.reviewId = checkResult.reviewId;
        this.isEditing = true;
        await this.fetchReviewToEdit(); 
      }
    }
    
    this.loading = false;
  },
  methods: {
    goBack() {
      this.$router.push({ path: `/sitios/${this.siteId}` });
    },
    
    async fetchSiteName() {
      try {
        const url = `${this.apiBaseUrl}/api/sites/${this.siteId}`;
        const response = await axios.get(url);
        this.siteName = response.data?.data?.name || response.data?.name || 'Sitio Desconocido';
      } catch (e) {
        this.siteName = 'Error al cargar el nombre del sitio';
        console.error("Error fetching site name:", e);
      }
    },

    async fetchCurrentUserEmail() {
        try {
            ///auth/me devuelve { email: 'user@example.com' }
            const url = `${this.apiBaseUrl}/auth/me`;
            // Este endpoint debe  devolver el email del usuario autenticado en el puerto.
            const response = await axios.get(url, { withCredentials: true }); 
            this.currentUserEmail = response.data?.email || response.data?.data?.email;
        } catch (e) {
            // Si falla, al menos el campo se enviará como null, y el backend lo validará.
            console.warn('❌ No se pudo obtener el email del usuario actual. Esto causará un error en el backend si no está logeado.');
            this.currentUserEmail = null;
        }
    },

    async fetchReviewToEdit() {
      this.loading = true;
      try {
        const url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
        const response = await axios.get(url, { withCredentials: true }); 
        const review = response.data?.data || response.data;
        
        if (review.site_id != this.siteId) {
            throw new Error("La reseña no corresponde a este sitio.");
        }
        
        this.rating = review.rating || 0;
        this.reviewText = review.content || review.text || '';
        this.isPendingModeration = (review.status === 'Pendiente'); 
        
      } catch (e) {
        this.errorMessage = e.response?.data?.message || 'Error al cargar la reseña. ¿Es el autor?';
        console.error(e);
        this.$router.push({ path: `/sitios/${this.siteId}`, query: { review_error: 'not_found_or_unauthorized' } });
      } finally {
        this.loading = false;
      }
    },
    

    async checkExistingReview() {
      try {
        // 1. Construir URL con el email explícito
        let url = `${this.apiBaseUrl}/api/reviews/check-existing?site_id=${this.siteId}`;
        
        // Usamos this.currentUserEmail que cargamos en created()
        if (this.currentUserEmail) {
             url += `&user_email=${encodeURIComponent(this.currentUserEmail)}`;
        }

        const response = await axios.get(url, { withCredentials: true });

        if (response.data.has_review && response.data.review_id) {
          // Retorna el ID de la reseña existente
          return { hasReview: true, reviewId: response.data.review_id };
        }
        return { hasReview: false };
      } catch (e) {
        return { hasReview: false };
      }
    }, 
    

    
    validateForm() {
      this.validationErrors = { rating: null, reviewText: null };
      let isValid = true;

      if (this.rating < 1 || this.rating > 5) {
        this.validationErrors.rating = 'La puntuación debe ser entre 1 y 5.';
        isValid = false;
      }

      const len = this.reviewText.length;
      if (len < 20 || len > 1000) {
        this.validationErrors.reviewText = `El texto debe tener entre 20 y 1000 caracteres. Actualmente tiene ${len}.`;
        isValid = false;
      }
      
      return isValid;
    },
    
    async handleSubmit() {
    if (!this.validateForm()) {
        return;
    }

    this.isSubmitting = true;
    this.errorMessage = null;
    this.successMessage = null;
    
    // PASO 1: Usar la variable de email ya cargada y segura
    const userEmail = this.currentUserEmail; 

    // PASO 2: Verificar que el email existe antes de proceder (seguridad)
    if (!userEmail) {
        // Si no hay email, es un error de sesión. 
        this.errorMessage = "Error de autenticación: No se pudo verificar la identidad del usuario. Intenta cerrar sesión y volver a entrar.";
        this.isSubmitting = false;
        return; 
    }

    try {
        const payload = {
            site_id: this.siteId,
            rating: this.rating,
            text: this.reviewText,
            //Usamos la variable local verificada
            userEmailOverride: userEmail,
        };

        let url;
        let method;

        if (this.isEditing) {
            url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
            method = 'put';
        } else {
            url = `${this.apiBaseUrl}/api/reviews`;
            method = 'post';
        }

        const response = await axios({
            method: method,
            url: url,
            data: payload,
            withCredentials: true
        });

        // Manejo de respuesta
        this.successMessage = response.data?.message || 'Reseña enviada exitosamente.';
        
        if (method === 'post' && response.data?.data?.id) {
            this.reviewId = response.data.data.id;
            this.isEditing = true;
        }
        
        // Redireccionar al sitio después de 1.5s
        setTimeout(() => {
           this.$router.push({ path: `/sitios/${this.siteId}` }); 
        }, 1500);


    } catch (e) {
        console.error('❌ Error al enviar reseña:', e);
        
        let message = 'Error al enviar la reseña.';
        if (!e.response) {
            message = 'Error de conexión con el servidor. (Verifica tu servidor backend si persiste).'; 
        } else {
            message = e.response?.data?.error || e.response?.data?.message || message;
        }

        this.errorMessage = message;
    } finally {
        this.isSubmitting = false;
    }
    },
    handleDeleteConfirm() {
      this.showDeleteModal = false;
      this.handleDelete();
    },


    async handleDelete() {
      this.isSubmitting = true;
      this.errorMessage = null;
      this.successMessage = null;
      
      // Verificar que tenemos el email (igual que en handleSubmit)
      if (!this.currentUserEmail) {
          this.errorMessage = "No se pudo verificar tu identidad para eliminar.";
          this.isSubmitting = false;
          return;
      }

      try {
        const url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
        
        // Enviar el email en el cuerpo de la solicitud DELETE
        await axios.delete(url, { 
            data: { 
                userEmailOverride: this.currentUserEmail 
            },
            withCredentials: true 
        });

        this.$router.push({ path: `/sitios/${this.siteId}`, query: { review_deleted: 'true' } });

      } catch (e) {
        this.errorMessage = e.response?.data?.error || e.response?.data?.message || 'Error al eliminar la reseña.';
        console.error(e);
      } finally {
        this.isSubmitting = false;
      }
    }
  }
};
</script>

<style scoped>
/* Estilo para el modal de Bootstrap que debe mostrarse con d-block */
.modal {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 1050;
  overflow: hidden;
  outline: 0;
}
.modal-dialog {
  margin-top: 10vh;
}

.review-form-container {
  max-width: 800px;
  margin: 0 auto;
}

/* Estrellas */
.rating-stars .bi-star,
.rating-stars .bi-star-fill {
  font-size: 1.5rem;
  cursor: pointer;
  color: #ffc107; 
  transition: transform 0.2s;
}

.rating-stars .bi-star:hover,
.rating-stars .bi-star-fill:hover {
  transform: scale(1.1);
}

.star-container {
  display: inline-block;
}

/* Estilo para el chip de estado de la reseña */
.chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
}
.chip-default { background: #6c757d; } 
.chip-pending { background: #ffc107; } 
.chip-approved { background: #198754; } 
.chip-rejected { background: #dc3545; } 

/* Estilos de validación */
.form-group.has-error .form-control,
.form-group.has-error .form-select,
.form-group.has-error .form-check-input {
  border-color: #dc3545;
}
</style>