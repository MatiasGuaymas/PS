<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { authStore } from '@/stores/authStore'

const router = useRouter()

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const user = computed(() => authStore.user)
const loading = computed(() => authStore.loading)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const userAvatar = computed(() => {
  if (user.value?.avatar) return user.value.avatar
  return null
})

const userInitials = computed(() => {
  if (!user.value) return '?'
  const f = user.value.first_name || ''
  const l = user.value.last_name || ''
  return `${f.charAt(0)}${l.charAt(0)}`.toUpperCase()
})

const handleLogout = async () => {
  await authStore.logout()
  window.location.href = "/login"
}
</script>

<template>
  <header class="app-header shadow-sm bg-white">
    <nav class="navbar navbar-expand-lg px-3">
      <div class="container-fluid d-flex align-items-center">

        <!-- Logo -->
        <RouterLink to="/" class="navbar-brand d-flex align-items-center gap-2 fw-bold">
          <img src="/Logo.jpg" class="logo-image" />
          <span class="app-title">
            <span class="gradient-text-1">Puff</span>
            <span class="gradient-text-2">-</span>
            <span class="gradient-text-3">Tóricos</span>
          </span>
        </RouterLink>

        <!-- Avatar / Login en móvil -->
        <div class="mobile-user-area d-lg-none">

          <template v-if="loading">
            <div class="spinner-border spinner-border-sm text-primary"></div>
          </template>

          <template v-else-if="isAuthenticated && user">
            <div 
              class="avatar-mobile"
              :style="{ backgroundImage: userAvatar ? `url(${userAvatar})` : null }"
            >
              <span v-if="!userAvatar">{{ userInitials }}</span>
            </div>
          </template>
        </div>

        <!-- Botón hamburguesa -->
        <button
          class="navbar-toggler border-0 shadow-none"
          type="button"
          @click="toggleMenu"
        >
          <i class="bi bi-list fs-1"></i>
        </button>

        <!-- Desktop Menu -->
        <div class="collapse navbar-collapse d-none d-lg-flex">
          <ul class="navbar-nav ms-auto gap-2">
            <li>
              <RouterLink to="/" class="nav-link">
                <i class="bi bi-house me-1"></i>
                Inicio
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/sitios" class="nav-link">
                <i class="bi bi-geo-alt me-1"></i>
                Sitios
              </RouterLink>
            </li>
          </ul>

          <div class="user-area ms-3">

            <!-- Loading -->
            <template v-if="loading">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </template>

            <!-- Logueado -->
            <template v-else-if="isAuthenticated && user">
              <div class="dropdown">
                <button 
                  class="btn btn-outline-primary dropdown-toggle d-flex align-items-center gap-2"
                  data-bs-toggle="dropdown"
                >
                  <div 
                    v-if="userAvatar" 
                    class="avatar-small"
                    :style="{ backgroundImage: `url(${userAvatar})` }"
                  ></div>
                  <div v-else class="avatar-small avatar-initials">{{ userInitials }}</div>
                  <span>{{ user.first_name }}</span>
                </button>

                <ul class="dropdown-menu dropdown-menu-end shadow">
                  <li><RouterLink to="/perfil" class="dropdown-item">Mi Perfil</RouterLink></li>
                  <li><hr class="dropdown-divider" /></li>
                  <li>
                    <button class="dropdown-item text-danger" @click="handleLogout">Cerrar Sesión</button>
                  </li>
                </ul>
              </div>
            </template>

            <!-- No logueado -->
            <template v-else>
              <div class="auth-buttons">
                <RouterLink to="/login" class="btn btn-outline-gradient">
                  <i class="bi bi-box-arrow-in-right me-2"></i>
                  Iniciar Sesión
                </RouterLink>
                <RouterLink to="/registro" class="btn btn-gradient">
                  <i class="bi bi-person-plus me-2"></i>
                  Registrarse
                </RouterLink>
              </div>
            </template>

          </div>
        </div>
      </div>
    </nav>

    <!-- Mobile Menu -->
    <div 
      class="mobile-menu"
      :class="{ open: isMenuOpen }"
    >
      <div class="mobile-menu-content">
        
        <button class="close-btn" @click="toggleMenu">
          <i class="bi bi-x-lg"></i>
        </button>

        <ul class="mobile-links">
          <li>
            <RouterLink to="/" @click="toggleMenu">
              <i class="bi bi-house me-2"></i>
              Inicio
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/sitios" @click="toggleMenu">
              <i class="bi bi-geo-alt me-2"></i>
              Sitios
            </RouterLink>
          </li>
        </ul>

        <hr />

        <!-- Usuario en móvil -->
        <div class="mobile-user">

          <template v-if="isAuthenticated && user">
            <div class="d-flex align-items-center gap-3 mb-3">
              <div 
                class="avatar-large"
                :style="{ backgroundImage: userAvatar ? `url(${userAvatar})` : null }"
              >
                <span v-if="!userAvatar">{{ userInitials }}</span>
              </div>
              <div>
                <strong>{{ user.first_name }} {{ user.last_name }}</strong>
                <p class="text-muted small mb-0">{{ user.email }}</p>
              </div>
            </div>

            <RouterLink to="/perfil" class="mobile-btn" @click="toggleMenu">
              <i class="bi bi-person me-2"></i>
              Mi Perfil
            </RouterLink>

            <button class="mobile-btn danger" @click="handleLogout">
              <i class="bi bi-box-arrow-right me-2"></i>
              Cerrar Sesión
            </button>
          </template>

          <template v-else>
            <RouterLink to="/login" class="mobile-btn outline" @click="toggleMenu">
              <i class="bi bi-box-arrow-in-right me-2"></i>
              Iniciar Sesión
            </RouterLink>
            <RouterLink to="/registro" class="mobile-btn primary" @click="toggleMenu">
              <i class="bi bi-person-plus me-2"></i>
              Registrarse
            </RouterLink>
          </template>

        </div>

      </div>
    </div>
  </header>
</template>

<style scoped>

/* Header */
.app-header {
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 2000;
}

/* Logo */
.logo-image {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  object-fit: cover;
}

.navbar-brand {
  transition: transform 0.2s ease;
  text-decoration: none;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

/* Gradientes del nombre */
.gradient-text-1 { background: linear-gradient(135deg,#667eea,#764ba2); -webkit-background-clip:text; color:transparent; }
.gradient-text-2 { background: linear-gradient(135deg,#764ba2,#f093fb); -webkit-background-clip:text; color:transparent; }
.gradient-text-3 { background: linear-gradient(135deg,#f093fb,#f5576c); -webkit-background-clip:text; color:transparent; }

/* Navegación Desktop */
.nav-link {
  padding: 0.5rem 1rem;
  color: #666;
  border-radius: 6px;
  transition: 0.25s;
  text-decoration: none;
  display: flex;
  align-items: center;
}
.nav-link:hover,
.nav-link.router-link-active {
  background: #eef4ff;
  color: #0d6efd;
}

/* Botones de autenticación */
.auth-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-outline-gradient {
  padding: 0.6rem 1.5rem;
  border: 2px solid transparent;
  background: white;
  background-clip: padding-box;
  position: relative;
  border-radius: 8px;
  font-weight: 600;
  color: #667eea;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-outline-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 8px;
  padding: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

.btn-outline-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.btn-gradient {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  color: white;
}

/* Avatar desktop */
.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-size: cover;
  border: 2px solid #0d6efd;
  flex-shrink: 0;
}
.avatar-initials {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
  font-size: 0.75rem;
}

/* Panel Mobile */
.mobile-menu {
  position: fixed;
  top: 0;
  right: -100%;
  width: 85%;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 12px rgba(0,0,0,0.15);
  transition: 0.35s;
  z-index: 3000;
}
.mobile-menu.open {
  right: 0;
}
.mobile-menu-content {
  padding: 1.5rem;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  float: right;
  cursor: pointer;
}
.mobile-links {
  list-style: none;
  padding: 0;
  margin-top: 2rem;
}
.mobile-links li {
  margin-bottom: 1rem;
}
.mobile-links a {
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  padding: 0.75rem;
  color: #444;
  border-radius: 6px;
  text-decoration: none;
}
.mobile-links a:hover {
  background: #f5f7ff;
  color: #0d6efd;
}

/* Usuario móvil */
.mobile-user-area .avatar-mobile {
  width: 36px;
  height: 36px;
  background-size: cover;
  border-radius: 50%;
  border: 2px solid #0d6efd;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  background-color: #667eea;
  color: white;
}

.user-icon-mobile {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  font-size: 1.5rem;
}

/* Avatar grande móvil */
.avatar-large {
  width: 55px;
  height: 55px;
  border-radius: 50%;
  background-size: cover;
  border: 3px solid #0d6efd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  background-color: #667eea;
}

/* Botones móvil */
.mobile-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  width: 100%;
  text-align: center;
  border-radius: 10px;
  margin-bottom: 0.8rem;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mobile-btn.outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.mobile-btn.outline:hover {
  background: #f5f7ff;
  transform: translateY(-2px);
}

.mobile-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.mobile-btn.primary:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.mobile-btn.danger {
  background: #ffe6e6;
  color: #dc3545;
  border: 2px solid #dc3545;
}

.mobile-btn.danger:hover {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
}
</style>