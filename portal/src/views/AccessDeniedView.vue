<template>
  <div class="access-denied">
    <h2>🛑 Acceso Bloqueado</h2>
    <p>Estamos temporalmente fuera de servicio.</p>
    <div class="message-box">
      <strong>Mensaje del Servidor:</strong>
      <p>🚧 {{ message }} 🚧</p>
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
.access-denied {
  text-align: center;
  padding: 50px;
}
.message-box {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ff0000;
  background-color: #ffeaea;
  display: inline-block;
}
</style>
