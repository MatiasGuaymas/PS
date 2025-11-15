<script setup>
import { ref, computed, onMounted } from 'vue'
import { authStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = computed(() => authStore.user)
const loading = ref(false)
const editing = ref(false)
const message = ref({ text: '', type: '' })

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
})

onMounted(() => {
  if (user.value) {
    formData.value = {
      first_name: user.value.first_name || '',
      last_name: user.value.last_name || '',
      email: user.value.email || '',
    }
  }
})


const userAvatar = computed(() => {
  console.log('🔍 Verificando avatar...', user.value?.avatar)
  
  if (user.value?.avatar) {
    console.log('✅ Avatar encontrado:', user.value.avatar)
    return user.value.avatar
  }
  
  console.log('❌ No hay avatar')
  return null
})

const enableEdit = () => {
  editing.value = true
  formData.value = {
    first_name: user.value.first_name || '',
    last_name: user.value.last_name || '',
    email: user.value.email || '',
  }
}

const cancelEdit = () => {
  editing.value = false
  formData.value = {
    first_name: user.value.first_name || '',
    last_name: user.value.last_name || '',
    email: user.value.email || '',
  }
  message.value = { text: '', type: '' }
}

const saveChanges = async () => {
  loading.value = true
  message.value = { text: '', type: '' }
  
  try {
    const response = await fetch(`http://localhost:5000/auth/me/update`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(formData.value)
    })
    
    if (response.ok) {
      await authStore.checkAuth() 
      editing.value = false
      message.value = { 
        text: '✅ Perfil actualizado correctamente', 
        type: 'success' 
      }
      
      setTimeout(() => {
        message.value = { text: '', type: '' }
      }, 3000)
    } else {
      const data = await response.json()
      message.value = { 
        text: `❌ ${data.error || 'Error al actualizar el perfil'}`, 
        type: 'danger' 
      }
    }
  } catch (err) {
    message.value = { 
      text: '❌ Error de conexión. Intenta nuevamente.', 
      type: 'danger' 
    }
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}

// Redirigir si no hay usuario
onMounted(() => {
  if (!user.value && !authStore.loading) {
    router.push('/login')
  }
})
</script>

<template>
  <div class="profile-view">
    <div class="container py-5">
      <!-- Encabezado -->
      <div class="row mb-4">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item">
                <RouterLink to="/">Inicio</RouterLink>
              </li>
              <li class="breadcrumb-item active" aria-current="page">
                Mi Perfil
              </li>
            </ol>
          </nav>
          <h1 class="fw-bold mb-2">
            <i class="bi bi-person-circle me-2 text-primary"></i>
            Mi Perfil
          </h1>
          <p class="text-muted">Gestiona tu información personal</p>
        </div>
      </div>

      <div class="row">
        <!-- Columna izquierda: Avatar y estadísticas -->
        <div class="col-lg-4 mb-4">
          <div class="card shadow-sm border-0 rounded-4">
            <div class="card-body text-center p-4">
                <div class="avatar-container mb-3">
                    <!-- Si tiene imagen de avatar -->
                    <div 
                        v-if="userAvatar" 
                        class="avatar-circle avatar-image"
                        :style="{ backgroundImage: `url(${userAvatar})` }"
                    ></div>
                </div>  

              <!-- Nombre completo -->
              <h3 class="fw-bold mb-1">
                {{ user?.first_name }} {{ user?.last_name }}
              </h3>
              <p class="text-muted mb-3">
                <i class="bi bi-envelope me-1"></i>
                {{ user?.email }}
              </p>

              <!-- Rol/Badge -->
              <div class="mb-3">
                <span v-if="user?.is_admin" class="badge bg-danger rounded-pill px-3 py-2">
                  <i class="bi bi-shield-fill-check me-1"></i>
                  Administrador
                </span>
                <span v-else-if="user?.role" class="badge bg-primary rounded-pill px-3 py-2">
                  <i class="bi bi-person-badge me-1"></i>
                  {{ user.role }}
                </span>
                <span v-else class="badge bg-secondary rounded-pill px-3 py-2">
                  <i class="bi bi-person me-1"></i>
                  Usuario
                </span>
              </div>

              <!-- Estadísticas -->
              <div class="stats-grid mt-4">
                <div class="stat-item">
                  <div class="stat-icon">
                    <i class="bi bi-star-fill text-warning"></i>
                  </div>
                  <div class="stat-label">Reseñas</div>
                  <div class="stat-value">0</div>
                </div>
                <div class="stat-item">
                  <div class="stat-icon">
                    <i class="bi bi-heart-fill text-danger"></i>
                  </div>
                  <div class="stat-label">Favoritos</div>
                  <div class="stat-value">0</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Columna derecha: Información del perfil -->
        <div class="col-lg-8">
          <div class="card shadow-sm border-0 rounded-4">
            <div class="card-body p-4">
              <!-- Header del card -->
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="fw-bold mb-0">
                  <i class="bi bi-person-lines-fill me-2 text-primary"></i>
                  Información Personal
                </h4>
                <button 
                  v-if="!editing" 
                  @click="enableEdit" 
                  class="btn btn-outline-primary"
                >
                  <i class="bi bi-pencil me-1"></i>
                  Editar
                </button>
              </div>

              <!-- Mensaje de feedback -->
              <transition name="slide-fade">
                <div 
                  v-if="message.text" 
                  :class="['alert', `alert-${message.type}`, 'alert-dismissible', 'fade', 'show', 'd-flex', 'align-items-center', 'mb-4']"
                  role="alert"
                >
                  <div class="flex-grow-1">{{ message.text }}</div>
                  <button 
                    type="button" 
                    class="btn-close" 
                    @click="message = { text: '', type: '' }"
                    aria-label="Close"
                  ></button>
                </div>
              </transition>

              <!-- Formulario -->
              <form @submit.prevent="saveChanges">
                <div class="row g-3">
                  <!-- Nombre -->
                  <div class="col-md-6">
                    <label for="first_name" class="form-label fw-semibold">
                      <i class="bi bi-person me-1"></i>
                      Nombre
                    </label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="first_name"
                      v-model="formData.first_name"
                      :disabled="!editing"
                      required
                    >
                  </div>

                  <!-- Apellido -->
                  <div class="col-md-6">
                    <label for="last_name" class="form-label fw-semibold">
                      <i class="bi bi-person me-1"></i>
                      Apellido
                    </label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="last_name"
                      v-model="formData.last_name"
                      :disabled="!editing"
                      required
                    >
                  </div>

                  <!-- Email -->
                  <div class="col-12">
                    <label for="email" class="form-label fw-semibold">
                      <i class="bi bi-envelope me-1"></i>
                      Correo Electrónico
                    </label>
                    <input 
                      type="email" 
                      class="form-control form-control-lg" 
                      id="email"
                      v-model="formData.email"
                      disabled
                    >
                    <small class="text-muted">
                      <i class="bi bi-info-circle me-1"></i>
                      El email no se puede modificar
                    </small>
                  </div>

                  <!-- Botones de acción -->
                  <div v-if="editing" class="col-12 d-flex gap-2 mt-4">
                    <button 
                      type="submit" 
                      class="btn btn-primary btn-lg flex-grow-1"
                      :disabled="loading"
                    >
                      <span v-if="loading">
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        Guardando...
                      </span>
                      <span v-else>
                        <i class="bi bi-check-lg me-2"></i>
                        Guardar Cambios
                      </span>
                    </button>
                    <button 
                      type="button" 
                      @click="cancelEdit" 
                      class="btn btn-outline-secondary btn-lg"
                      :disabled="loading"
                    >
                      <i class="bi bi-x-lg me-1"></i>
                      Cancelar
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>

          <!-- Card de seguridad -->
          <div class="card shadow-sm border-0 rounded-4 mt-4">
            <div class="card-body p-4">
              <h4 class="fw-bold mb-3">
                <i class="bi bi-shield-lock me-2 text-primary"></i>
                Seguridad
              </h4>
              <div class="d-grid gap-2">
                <button class="btn btn-outline-warning btn-lg text-start">
                  <i class="bi bi-key me-2"></i>
                  Cambiar Contraseña
                  <i class="bi bi-chevron-right float-end"></i>
                </button>
                <button class="btn btn-outline-danger btn-lg text-start">
                  <i class="bi bi-trash me-2"></i>
                  Eliminar Cuenta
                  <i class="bi bi-chevron-right float-end"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
}

.breadcrumb {
  background: transparent;
  padding: 0;
  margin-bottom: 1rem;
}

.breadcrumb-item a {
  color: #667eea;
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

/* Avatar */
.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  margin: 0 auto;
}

/* Estadísticas */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #212529;
}

/* Cards */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

/* Formulario */
.form-control:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-control-lg {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  transition: border-color 0.3s ease;
}

.form-control-lg:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

/* Botones */
.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Animaciones */
.slide-fade-enter-active {
  animation: slideDown 0.3s ease;
}

.slide-fade-leave-active {
  animation: slideUp 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* Responsive */
@media (max-width: 991px) {
  .avatar-circle {
    width: 100px;
    height: 100px;
    font-size: 2.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>