import { reactive } from 'vue' 
import axios from 'axios'

const CACHE_WINDOW_MS = 5 * 60 * 1000 
const PORTAL_FLAG_NAME = 'portal-maintenance-flag'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';

// Estado Reactivo
export const maintenanceState = reactive({
  isActive: false,
  message: '',
  lastChecked: 0,
})

let ongoingRequest = null

/**
 * Simula la obtención de la feature flag desde un endpoint del backend.
 * En tu caso, esto debe llamar al mismo endpoint que checkAccessCondition.
 * @param {string} flagName
 * @returns {Promise<{is_enabled: boolean, maintenance_message: string}>}
 */
const getFeatureFlag = async (flagName) => {
  try {
    // Usamos el endpoint que tú ya tenías para la verificación
    const response = await axios.get(`${API_BASE_URL}/api/handler/`)
    
    // Asumimos que la respuesta debe ser: status: "ok" si está disponible
    const isAvailable = response.data.status === "ok";
    
    return {
      is_enabled: !isAvailable, // is_enabled = true si está en mantenimiento
      maintenance_message: response.data.message || 'Portal en mantenimiento.',
    }
    
  } catch (error) {
    let message = 'Error de red o servidor no disponible.'
    if (error.response) {
      if (error.response.status === 503) {
        message = error.response.data?.message || 'El servicio está temporalmente no disponible (503).'
      } else {
        message = `Error ${error.response.status}: ${error.response.data?.message || 'Error del servidor.'}`
      }

    // Si hay cualquier error, tratamos la aplicación como BLOQUEADA y lanzamos el error
    throw new Error(`${message}`)
  }
}


/**
 * Verifica el estado de disponibilidad del portal, utilizando caché.
 * @param {boolean} forceRefresh - Forzar una nueva petición al servidor.
 * @returns {Promise<boolean>} Devuelve true si el portal está ACTIVO (no en mantenimiento).
 */
export const ensurePortalAvailability = async (forceRefresh = false) => {
  const now = Date.now()

  // 1. Uso de Caché: Si no se fuerza el refresh y el caché no ha expirado
  if (
    !forceRefresh &&
    maintenanceState.lastChecked &&
    now - maintenanceState.lastChecked < CACHE_WINDOW_MS
  ) {
    // Devuelve el estado actual SIN hacer la petición
    return maintenanceState.isActive 
  }

  // 2. Ejecución Única: Si no hay una petición en curso, la inicia.
  if (!ongoingRequest) {
    ongoingRequest = getFeatureFlag(PORTAL_FLAG_NAME)
      .then((data) => {
        // La bandera es 'is_enabled' (mantenimiento), así que la guardamos como 'isActive' (mantenimiento)
        maintenanceState.isActive = Boolean(data.is_enabled) 
        maintenanceState.message = data.maintenance_message || ''
        
        
        return maintenanceState.isActive // Retorna el estado de mantenimiento
      })
      .catch((error) => {
        // En caso de error de red, asumimos mantenimiento para evitar el acceso no controlado
        maintenanceState.isActive = true 
        maintenanceState.message = error.message 
        return true // Retorna true (está en mantenimiento/bloqueado)
      })
      .finally(() => {
        maintenanceState.lastChecked = Date.now() // Actualiza el tiempo después de la promesa
        ongoingRequest = null // Libera la solicitud
      })
  }

  // 3. Esperar Petición: Si ya hay una petición en curso, espera por ella.
  return ongoingRequest
}
