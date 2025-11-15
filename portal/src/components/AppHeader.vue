<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { authStore } from '@/stores/authStore'

const isMenuOpen = ref(false)

const user = computed(() => authStore.user)
const loading = computed(() => authStore.loading)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const logout = async () => {
  await authStore.logout()
  // Opcionalmente redirigir
  window.location.href = '/login'
}
</script>

<template>
  <header class="app-header sticky-top bg-white shadow-sm">
    <nav class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <!-- Logo -->
        <RouterLink to="/" class="navbar-brand d-flex align-items-center">
          <img src="@/assets/Logo.jpg" alt="Logo" class="logo-image me-2">
          <span class="fw-bold fs-5">
            <span class="gradient-text-1">Puff</span>
            <span class="gradient-text-2">-</span>
            <span class="gradient-text-3">Tóricos</span>
          </span>
        </RouterLink>

        <!-- Toggle para mobile -->
        <button 
          class="navbar-toggler border-0" 
          type="button" 
          @click="toggleMenu"
          :aria-expanded="isMenuOpen"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div 
          class="collapse navbar-collapse" 
          :class="{ show: isMenuOpen }"
        >
          <!-- Links de navegación -->
          <ul class="navbar-nav mx-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <RouterLink to="/" class="nav-link fw-semibold">
                <i class="bi bi-house-door me-1"></i>
                Inicio
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/sitios" class="nav-link">
                <i class="bi bi-map me-1"></i>
                Explorar Sitios
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/mapa" class="nav-link">
                <i class="bi bi-geo-alt me-1"></i>
                Mapa
              </RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/sobre-nosotros" class="nav-link">
                <i class="bi bi-info-circle me-1"></i>
                Sobre Nosotros
              </RouterLink>
            </li>
          </ul>

          <!-- Botones de autenticación -->
          <div class="d-flex gap-2 align-items-center">
            <!-- Loading state -->
            <template v-if="loading">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
            </template>

            <!-- Usuario autenticado -->
            <template v-else-if="user">
              <div class="dropdown">
                <button 
                  class="btn btn-outline-primary dropdown-toggle d-flex align-items-center gap-2" 
                  type="button" 
                  id="userDropdown" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  <i class="bi bi-person-circle"></i>
                  <span>{{ user.first_name }}</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                  <li>
                    <div class="dropdown-item-text">
                      <small class="text-muted">{{ user.email }}</small>
                    </div>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <RouterLink to="/perfil" class="dropdown-item">
                      <i class="bi bi-person me-2"></i>
                      Mi Perfil
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink to="/mis-reviews" class="dropdown-item">
                      <i class="bi bi-star me-2"></i>
                      Mis Reseñas
                    </RouterLink>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button @click="logout" class="dropdown-item text-danger">
                      <i class="bi bi-box-arrow-right me-2"></i>
                      Cerrar Sesión
                    </button>
                  </li>
                </ul>
              </div>
            </template>

            <!-- Usuario no autenticado -->
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

/* Animación del menú móvil */
.navbar-collapse {
  transition: all 0.3s ease-in-out;
}
</style>
