<template>
  <div class="access-denied-container d-flex align-items-center justify-content-center vh-100 bg-light">
    
    <div class="card bg-white text-dark shadow-lg border-0 rounded-4" style="max-width: 500px;">
      <div class="card-body p-5 text-center">
        
        <h1 class="display-1 text-danger mb-4">
          <i class="bi bi-shield-slash-fill"></i> </h1>

        <h2 class="card-title mb-3 fw-bolder">🛑 Acceso Bloqueado</h2>
        
        <p class="lead text-secondary-emphasis">
          Parece que hemos encontrado una barrera. El servicio está temporalmente fuera de servicio.
        </p>

        <hr class="my-4">

        <div class="alert alert-light border border-warning rounded-3 mt-4 p-3 text-start">
          <h5 class="alert-heading text-dark fw-bold mb-2">
            <i class="bi bi-tools me-2 text-warning"></i> Mensaje de Mantenimiento:
          </h5>
          <p class="mb-0 text-dark" style="text-align: center;">
             <strong>{{ message }}</strong> 
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
// Asegúrate de que esta importación sea correcta
import { maintenanceState, ensurePortalAvailability } from '@/utils/maintenanceState' 

const router = useRouter()
const route = useRoute()

// Lógica de mensaje: Si viene codificado en la ruta (del router.beforeEach), úsalo. Si no, usa el estado.
const DEFAULT_MESSAGE = 'El portal se encuentra temporalmente en mantenimiento.'

const routeMessage = computed(() => {
    try {
        return route.params.message ? decodeURIComponent(route.params.message) : null
    } catch (e) {
        return null
    }
})

const message = computed(() => routeMessage.value?.trim() || maintenanceState.message?.trim() || DEFAULT_MESSAGE)


let intervalId = null

const checkAndExit = async () => {
    // Forzar una nueva verificación del estado
    await ensurePortalAvailability(true)

    // Si el mantenimiento se levantó
    if (!maintenanceState.isActive) {
        // Detener la verificación
        clearInterval(intervalId)
        
        // Usar 'replace' para salir de la vista de error. 
        // El router.beforeEach manejará la verificación final antes de mostrar la home.
        router.replace('/')
    } else {
        // se puede sacar es para ver el debug con el timer
        console.log(`🚧 Sitio aún en mantenimiento. Último mensaje: ${message.value}`)
    }
}

onMounted(() => {
    // Verificar inmediatamente al montar, en caso de que el hook del router lo haya fallado
    checkAndExit() 

    // Polling cada 5 segundos
    intervalId = setInterval(checkAndExit, 5000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped>
/* Estilo para asegurar que el fondo claro sea uniforme */
.access-denied-container {
  min-height: 100vh;
  background-color: var(--bs-light) !important; 
}

/* Icono grande y moderno */
.display-1 {
  font-size: 5.5rem; /* Un poco más grande para dominar visualmente */
  color: var(--bs-danger); /* Asegura que el color de alerta sea el Danger de Bootstrap */
}

.card {
  /* Controla el ancho máximo para evitar que se vea muy estirado en pantallas grandes */
  max-width: 500px;
  /* Espacio extra de padding/margin si es necesario */
}
</style>