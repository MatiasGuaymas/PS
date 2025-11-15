<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}
</script>

<template>
  <header class="app-header sticky-top shadow bg-body-tertiary rounded">
    <nav class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <a class="navbar-brand d-flex align-items-center" href="/">
          <img src="/Logo.jpg" alt="Logo" class="logo-image me-2">
          <span class="fw-bold fs-5">
            <span class="gradient-text-1">Puff</span>
            <span class="gradient-text-2">-</span>
            <span class="gradient-text-3">Tóricos</span>
          </span>
        </a>

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
              <a class="nav-link" href="/mapa">
                <i class="bi bi-geo-alt me-1"></i>
                Mapa
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/sobre-nosotros">
                <i class="bi bi-info-circle me-1"></i>
                Sobre Nosotros
              </a>
            </li>
          </ul>

          <div class="d-flex gap-2 align-items-center">
            <a href="/login" class="btn btn-outline-primary">
              <i class="bi bi-box-arrow-in-right me-1"></i>
              Iniciar Sesión
            </a>
            <a href="/registro" class="btn btn-primary">
              <i class="bi bi-person-plus me-1"></i>
              Registrarse
            </a>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  z-index: 1000;
  background-color: var(--bg-header-footer);
  border-bottom: 1px solid var(--border-color);
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
  color: var(--color-primary) !important;
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
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-2 {
  background: var(--gradient-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-3 {
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-link {
  color: var(--text-secondary);
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
}

.nav-link:hover {
  color: #0d6efd;
  background-color: var(--bg-body);
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
  box-shadow: var(--shadow-md);
}

.btn-primary {
  font-weight: 500;
  transition: all 0.3s ease;
  background: var(--gradient-primary);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  background: var(--gradient-secondary);
}

/* Responsive */
@media (max-width: 991px) {
  .navbar-collapse {
    background-color: var(--bg-header-footer);
    padding: 1rem;
    margin-top: 1rem;
    border-radius: 8px;
    box-shadow: var(--shadow-lg);
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
