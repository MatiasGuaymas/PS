<script setup>
import { defineProps, defineEmits } from 'vue'

// Recibe el texto de búsqueda desde HomeView
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// Define los eventos que este componente puede enviar al padre (HomeView)
const emit = defineEmits(['search', 'update:searchQuery'])

// Cuando el usuario escribe, envía el nuevo valor al padre
const handleInput = (event) => {
  emit('update:searchQuery', event.target.value)
}

// Cuando el usuario hace clic en buscar, notifica al padre
const handleSearch = () => {
  emit('search')
}

// Si el usuario presiona Enter, ejecuta la búsqueda
const handleKeyup = (event) => {
  if (event.key === 'Enter') {
    handleSearch()
  }
}
</script>

<template>
  <section class="py-lg-16 py-8 mb-4">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-6 mb-6 mb-lg-0">
          <div class="animate-fade-in">
            <h1 class="display-3 fw-bold mb-3">
              Descubre los Sitios Históricos de Argentina
            </h1>
            
            <p class="pe-lg-10 mb-4 fs-5">
              Explora los sitios históricos, monumentos y lugares emblemáticos 
              que cuentan la historia y el patrimonio cultural de nuestro país.
            </p>
            
            <form 
              @submit.prevent="handleSearch" 
              class="search-form d-flex gap-2 mb-4 animate-slide-up"
            >
              <input
                :value="searchQuery"
                @input="handleInput"
                @keyup="handleKeyup"
                type="text"
                class="form-control form-control-lg"
                placeholder="Buscar sitios históricos..."
                aria-label="Buscar sitios"
              >
              <button type="submit" class="btn btn-primary btn-lg px-4">
                <i class="bi bi-search"></i>
                <span class="d-none d-sm-inline ms-2">Buscar</span>
              </button>
            </form>
          </div>
        </div>
        
        <div class="col-lg-6 d-flex justify-content-center">
          <div class="position-relative hero-image-container">
            <div class="hero-main-image">
              <img 
                src="https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=600&h=700&fit=crop" 
                alt="Sitios Históricos de Argentina" 
                class="img-fluid rounded-4 shadow-lg"
              >
            </div>

            <div class="decorative-circle circle-1"></div>
            <div class="decorative-circle circle-2"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  position: relative;
  overflow: hidden;
  min-height: 80vh;
}

.hero-image-container {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.hero-main-image {
  position: relative;
  z-index: 2;
}

.hero-main-image img {
  width: 100%;
  height: auto;
  object-fit: cover;
}

/* Badges flotantes */
.floating-badge {
  position: absolute;
  z-index: 3;
}

.badge-1 {
  top: 10%;
  left: -10%;
}

.badge-2 {
  bottom: 10%;
  left: -5%;
}

/* Círculos decorativos */
.decorative-circle {
  position: absolute;
  border-radius: 50%;
  z-index: 1;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.25;
  top: -80px;
  right: -80px;
  animation: pulse 4s ease-in-out infinite;
}

.circle-2 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  opacity: 0.2;
  bottom: -50px;
  left: -50px;
  animation: pulse 4s ease-in-out infinite 0.5s;
}

/* Animaciones */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.25;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.15;
  }
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out 0.4s both;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 3s ease-in-out infinite 0.5s;
}

/* Responsive */
@media (max-width: 991px) {
  .hero-section {
    min-height: auto;
  }
  
  .hero-image-container {
    margin-top: 3rem;
  }
  
  .badge-1, .badge-2 {
    transform: scale(0.8);
  }
  
  /* Ocultar círculos en tablets */
  .decorative-circle {
    display: none;
  }
}

@media (max-width: 576px) {
  .hero-section h1 {
    font-size: 2.5rem;
  }
  
  .search-form {
    flex-direction: column;
  }
  
  .search-form button {
    width: 100%;
  }
  
  .floating-badge {
    display: none;
  }
  
  /* Ocultar círculos en móviles */
  .decorative-circle {
    display: none;
  }
  
  .hero-image-container {
    max-width: 100%;
    overflow: hidden;
  }
}
</style>
