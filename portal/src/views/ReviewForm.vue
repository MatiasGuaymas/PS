<template>
  <div class="container py-4">
    <div class="mb-3 d-flex justify-content-between align-items-center">
      <button class="btn btn-sm btn-outline-secondary" @click="goBack">
        <i class="bi bi-arrow-left"></i> Volver a {{ siteName || 'el sitio' }}
      </button>
    </div>

    <h2 class="mb-4">{{ isEditing ? 'Editar Reseña' : 'Crear Reseña' }} para: {{ siteName }}</h2>

    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="isPendingModeration" class="alert alert-warning">
      ¡Atención! Tu reseña editada ha vuelto a estado **"Pendiente de Aprobación"**. Se mostrará una vez sea moderada.
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
    </div>
    
    <form v-else @submit.prevent="handleSubmit" class="card p-4 shadow-sm">
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

      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting || loading">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
          {{ isEditing ? 'Guardar Cambios' : 'Enviar Reseña' }}
        </button>

        <button v-if="isEditing" type="button" class="btn btn-danger" @click="handleDelete" :disabled="isSubmitting">
          <i class="bi bi-trash-fill"></i> Eliminar Reseña
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar',
      siteId: this.$route.params.siteId,
      reviewId: this.$route.params.reviewId || null,
      siteName: 'Cargando...',
      
      // Datos del Formulario
      rating: 0,
      reviewText: '',
      
      // Estados de la Interfaz
      loading: true,
      isSubmitting: false,
      isEditing: !!this.$route.params.reviewId,
      isPendingModeration: false,
      errorMessage: null,
      successMessage: null,
      validationErrors: { rating: null, reviewText: null },
    };
  },
  async created() {
    await this.fetchSiteName(); // Para el título "Volver a..."
    
    // Si estamos editando, cargamos la reseña existente
    if (this.isEditing) {
      await this.fetchReviewToEdit();
    } else {
      this.loading = false; // Si es nueva, no hay que cargar nada
    }
  },
  methods: {
    goBack() {
      // Simple navegación de vuelta al detalle del sitio
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

    async fetchReviewToEdit() {
      this.loading = true;
      try {
        const url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
        // Se asume que la API verifica si el usuario autenticado es el autor
        const response = await axios.get(url, { withCredentials: true }); 
        const review = response.data?.data || response.data;
        
        if (review.site_id != this.siteId) {
            throw new Error("La reseña no corresponde a este sitio.");
        }
        
        this.rating = review.rating || 0;
        this.reviewText = review.text || '';
        this.isPendingModeration = (review.status === 'pending'); // Asumiendo que la API envía el estado
        
      } catch (e) {
        this.errorMessage = e.response?.data?.message || 'Error al cargar la reseña. ¿Es el autor?';
        console.error(e);
        // Si falla, redirigimos al sitio para evitar que el usuario intente editar algo que no es suyo
        this.$router.push({ path: `/sitios/${this.siteId}`, query: { review_error: 'not_found_or_unauthorized' } });
      } finally {
        this.loading = false;
      }
    },
    
    validateForm() {
      this.validationErrors = { rating: null, reviewText: null };
      let isValid = true;

      // Validación Puntuación
      if (this.rating < 1 || this.rating > 5) {
        this.validationErrors.rating = 'La puntuación debe ser entre 1 y 5.';
        isValid = false;
      }

      // Validación Texto
      const len = this.reviewText.length;
      if (len < 20 || len > 1000) {
        this.validationErrors.reviewText = `El texto debe tener entre 20 y 1000 caracteres. Actualmente tiene ${len}.`;
        isValid = false;
      }
      
      return isValid;
    },
    
    async handleSubmit() {
      this.errorMessage = null;
      this.successMessage = null;
      this.isPendingModeration = false;

      if (!this.validateForm()) {
        this.errorMessage = 'Por favor, corrige los errores del formulario.';
        return;
      }

      this.isSubmitting = true;
      const data = {
        rating: this.rating,
        text: this.reviewText,
        site_id: this.siteId // Necesario para la creación
      };

      try {
        let response;
        if (this.isEditing) {
          // EDITAR: PUT o PATCH a la reseña específica
          const url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
          response = await axios.put(url, data, { withCredentials: true }); 
        } else {
          // CREAR: POST a la colección de reseñas
          const url = `${this.apiBaseUrl.replace(/\/$/,'')}/api/sites/${this.siteId}/reviews`;
          response = await axios.post(url, data, { withCredentials: true }); 
        }

        this.successMessage = `Reseña ${this.isEditing ? 'actualizada' : 'creada'} con éxito.`;
        
        // La API debe retornar el estado de la reseña
        const newStatus = response.data?.data?.status || response.data?.status || 'approved'; 

        if (this.isEditing && newStatus === 'pending') {
          this.isPendingModeration = true;
        }

        // Si es una creación, actualizamos el reviewId para permitir la eliminación inmediata
        if (!this.isEditing) {
            this.reviewId = response.data?.data?.id || response.data?.id;
            this.isEditing = true; // Ahora que existe, el formulario debe comportarse como edición
        }

      } catch (e) {
        this.errorMessage = e.response?.data?.message || 'Error al enviar la reseña. Verifica permisos o datos.';
        console.error(e);
      } finally {
        this.isSubmitting = false;
      }
    },
    
    async handleDelete() {
      if (!confirm('¿Estás seguro de que quieres eliminar tu reseña? Esta acción no se puede deshacer.')) {
        return;
      }

      this.isSubmitting = true;
      this.errorMessage = null;
      this.successMessage = null;

      try {
        const url = `${this.apiBaseUrl}/api/reviews/${this.reviewId}`;
        await axios.delete(url, { withCredentials: true });

        alert('Reseña eliminada con éxito.');
        // Redirigir al detalle del sitio después de eliminar
        this.$router.push({ path: `/sitios/${this.siteId}` });

      } catch (e) {
        this.errorMessage = e.response?.data?.message || 'Error al eliminar la reseña. Verifica permisos.';
        console.error(e);
      } finally {
        this.isSubmitting = false;
      }
    }
  },
  // Se puede agregar un watch a reviewText para actualizar el contador en tiempo real si es necesario.
};
</script>

<style scoped>
/* Estilos de chip y lightbox ya están en el componente de detalle, 
   solo se necesitaría un estilo base para el formulario si no usas un framework de CSS */

.form-control:invalid:not(:placeholder-shown) {
    border-color: #dc3545;
}
</style>