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

// ✅ Funciones de navegación
const goToReviews = () => {
  router.push('/reviews')
}

const goToFavorites = () => {
  router.push('/favoritos')
}

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
    const response = await fetch(`${API_BASE_URL}auth/me/update`, {
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
        <div class="col text-center">
          <h1 class="fw-bold mb-2">
            <i class="bi bi-person-circle me-2 text-primary"></i>
            Mi Perfil
          </h1>
          <p class="text-muted">Información de tu cuenta</p>
        </div>
      </div>

      <!-- Card centrada con información del usuario -->
      <div class="row justify-content-center">
        <div class="col-lg-6 col-md-8">
          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body text-center p-5">
              
              <!-- Avatar -->
              <div class="avatar-container mb-4">
                <div 
                  v-if="userAvatar" 
                  class="avatar-circle avatar-image"
                  :style="{ backgroundImage: `url(${userAvatar})` }"
                ></div>
                <div v-else class="avatar-circle">
                  <i class="bi bi-person-fill"></i>
                </div>
              </div>

              <!-- Nombre completo -->
              <h2 class="fw-bold mb-2">
                {{ user?.first_name }} {{ user?.last_name }}
              </h2>

              <!-- Email -->
              <p class="text-muted mb-4">
                <i class="bi bi-envelope-fill me-2"></i>
                {{ user?.email }}
              </p>

              <!-- Rol/Badge -->
              <div class="mb-4">
                <span v-if="user?.is_admin" class="badge bg-danger rounded-pill px-4 py-2 fs-6">
                  <i class="bi bi-shield-fill-check me-1"></i>
                  Administrador
                </span>
                <span v-else-if="user?.role" class="badge bg-primary rounded-pill px-4 py-2 fs-6">
                  <i class="bi bi-person-badge me-1"></i>
                  {{ user.role }}
                </span>
                <span v-else class="badge bg-secondary rounded-pill px-4 py-2 fs-6">
                  <i class="bi bi-person me-1"></i>
                  Usuario
                </span>
              </div>

              <!-- Divisor -->
              <hr class="my-4">

              <!-- Estadísticas -->
              <div class="stats-section mb-4">
                <h5 class="fw-bold mb-3 text-start">
                  <i class="bi bi-graph-up me-2 text-primary"></i>
                  Mis Actividades
                </h5>
                <div class="stats-grid">
                  <!-- ✅ Tarjeta Reseñas - Clicable -->
                  <button 
                    @click="goToReviews" 
                    class="stat-item stat-clickable"
                  >
                    <div class="stat-icon">
                      <i class="bi bi-star-fill text-warning"></i>
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">Ver Mis Reseñas</div>
                    </div>
                    <i class="bi bi-chevron-right ms-auto"></i>
                  </button>

                  <!-- ✅ Tarjeta Favoritos - Clicable -->
                  <button 
                    @click="goToFavorites" 
                    class="stat-item stat-clickable"
                  >
                    <div class="stat-icon">
                      <i class="bi bi-heart-fill text-danger"></i>
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">Ver Mis Favoritos</div>
                    </div>
                    <i class="bi bi-chevron-right ms-auto"></i>
                  </button>
                </div>
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
  padding: 2rem 0;
}

/* Card principal */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Avatar */
.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  margin: 0 auto;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.avatar-circle:hover {
  transform: scale(1.05);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
}

.avatar-image {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Estadísticas */
.stats-section {
  text-align: left;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* ✅ Estilo base de las tarjetas */
.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-radius: 16px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* ✅ Tarjeta clicable */
.stat-clickable {
  cursor: pointer;
  background: transparent;
  text-align: left;
  width: 100%;
  border: 2px solid #e9ecef;
}

.stat-clickable::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-clickable:hover::before {
  opacity: 1;
}

.stat-clickable:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.25);
  border-color: #667eea;
}

.stat-clickable:active {
  transform: translateY(-4px) scale(1.01);
}

.stat-icon {
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.stat-content {
  flex: 1;
  text-align: left;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: #212529;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 1rem;
  color: #495057;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* ✅ Chevron animado */
.stat-clickable .bi-chevron-right {
  font-size: 1.5rem;
  color: #667eea;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.stat-clickable:hover .bi-chevron-right {
  transform: translateX(5px);
}

/* Grid de información */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.info-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-content {
  flex: 1;
  text-align: left;
}

.info-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 1.125rem;
  font-weight: bold;
  color: #212529;
}

/* Badges */
.badge {
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Botones */
.btn {
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-outline-primary {
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-outline-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-outline-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Divisor */
hr {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, #e9ecef, transparent);
}

/* Título */
h1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

h2 {
  color: #212529;
  font-weight: 700;
}

/* Responsive */
@media (max-width: 768px) {
  .avatar-circle {
    width: 120px;
    height: 120px;
    font-size: 3rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .card-body {
    padding: 2rem !important;
  }

  h1 {
    font-size: 1.75rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  .btn-lg {
    padding: 0.75rem 2rem !important;
    font-size: 1rem;
  }

  .stat-label {
    font-size: 0.875rem;
  }
}

@media (max-width: 576px) {
  .profile-view {
    padding: 1rem 0;
  }

  .avatar-circle {
    width: 100px;
    height: 100px;
    font-size: 2.5rem;
  }

  .stat-item {
    padding: 1rem;
  }

  .stat-icon {
    font-size: 2rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .info-item {
    padding: 1rem;
  }

  .info-icon {
    font-size: 1.5rem;
  }
}
</style>