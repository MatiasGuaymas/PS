<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { authStore } from '@/stores/authStore'

const router = useRouter()
const isMenuOpen = ref(false)

const user = computed(() => authStore.user)
const loading = computed(() => authStore.loading)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const userAvatar = computed(() => {
  if (user.value?.avatar) {
    return user.value.avatar
  }
  return null
})

const userInitials = computed(() => {
  if (!user.value) return '?'
  const firstName = user.value.first_name || ''
  const lastName = user.value.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || '?'
})

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleLogout = async () => {
  console.log('=' .repeat(80))
  console.log('🚪 AppHeader - Iniciando logout...')
  
  const success = await authStore.logout()
  
  console.log('📊 Resultado del logout:')
  console.log('   - success:', success)
  console.log('   - user:', authStore.user)
  console.log('   - isAuthenticated:', authStore.isAuthenticated)
  
  console.log('🔄 Forzando recarga completa con window.location.href...')
  console.log('=' .repeat(80))

  setTimeout(() => {
    window.location.href = '/login'
  }, 500)
}

watch(isAuthenticated, (newValue) => {
  console.log('🔄 Estado de autenticación cambió:', newValue)
})

onMounted(() => {
  console.log('🎯 AppHeader montado, usuario:', user.value)
})
</script>

<template>
  <header class="app-header sticky-top shadow bg-body-tertiary rounded">
    <nav class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <RouterLink to="/" class="navbar-brand fw-bold d-flex align-items-center gap-2">
          <img src="/Logo.jpg" alt="Logo" class="logo-image me-2">
          <span>
            <span class="gradient-text-1">Puff</span>
            <span class="gradient-text-2">-</span>
            <span class="gradient-text-3">Tóricos</span>
          </span>
        </RouterLink>

        <button
          class="navbar-toggler"
          type="button"
          @click="toggleMenu"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div :class="['collapse', 'navbar-collapse', { show: isMenuOpen }]">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0 gap-2">
            <li class="nav-item">
              <RouterLink to="/" class="nav-link" active-class="active">
                <i class="bi bi-house me-1"></i>
                Inicio
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/sitios" class="nav-link" active-class="active">
                <i class="bi bi-geo-alt me-1"></i>
                Sitios
              </RouterLink>
            </li>
          </ul>

          <div class="d-flex gap-2 align-items-center ms-lg-3">
            <!-- ✅ Spinner mientras carga -->
            <template v-if="loading">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
            </template>

            <!-- ✅ Usuario autenticado -->
            <template v-else-if="isAuthenticated && user">
              <div class="dropdown">
                <button 
                  class="btn btn-outline-primary dropdown-toggle d-flex align-items-center gap-2" 
                  type="button" 
                  id="userDropdown" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  <!-- Avatar o icono -->
                  <div 
                    v-if="userAvatar" 
                    class="avatar-small"
                    :style="{ backgroundImage: `url(${userAvatar})` }"
                  ></div>
                  <i v-else class="bi bi-person-circle"></i>
                  <span>{{ user.first_name }}</span>
                </button>
                
                <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="userDropdown">
                  <li>
                    <RouterLink to="/perfil" class="dropdown-item">
                      <i class="bi bi-person me-2"></i>
                      Mi Perfil
                    </RouterLink>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button @click="handleLogout" class="dropdown-item text-danger">
                      <i class="bi bi-box-arrow-right me-2"></i>
                      Cerrar Sesión
                    </button>
                  </li>
                </ul>
              </div>
            </template>

            <!-- ✅ Usuario no autenticado -->
            <template v-else>
              <RouterLink to="/login" class="btn btn-outline-primary">
                <i class="bi bi-box-arrow-in-right me-1"></i>
                Iniciar Sesión
              </RouterLink>
              <RouterLink to="/registro" class="btn btn-primary">
                <i class="bi bi-person-plus me-1"></i>
                Registrarse
              </RouterLink>
            </template>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  z-index: 1000;
  border-bottom: 1px solid #e9ecef;
}

.navbar-brand {
  transition: transform 0.2s ease;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

.navbar-brand i {
  transition: color 0.3s ease;
}

.navbar-brand:hover i {
  color: #667eea !important;
}

/* Estilos del logo */
.logo-image {
  width: 50px;
  height: 50px;
  object-fit: contain;
  border-radius: 8px;
}

/* Gradiente en el logo */
.gradient-text-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-2 {
  background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-3 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-link {
  color: #6c757d;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
}

.nav-link:hover {
  color: #0d6efd;
  background-color: #f8f9fa;
}

.nav-link.active {
  color: #0d6efd;
  background-color: #e7f1ff;
}

.nav-link.router-link-active {
  color: #0d6efd;
  background-color: #e7f1ff;
}

.nav-link i {
  font-size: 1rem;
}

.btn-outline-primary {
  border-width: 2px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
}

.btn-primary {
  font-weight: 500;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* Responsive */
@media (max-width: 991px) {
  .navbar-collapse {
    background-color: white;
    padding: 1rem;
    margin-top: 1rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .navbar-nav {
    margin-bottom: 1rem !important;
  }

  .d-flex.gap-2 {
    flex-direction: column;
    width: 100%;
  }

  .d-flex.gap-2 .btn {
    width: 100%;
  }
}

.navbar-collapse {
  transition: all 0.3s ease-in-out;
}
</style>
