import { authStore } from '@/stores/authStore'

export default {
  install: (app) => {
    authStore.checkAuth()

    const originalFetch = window.fetch
    window.fetch = async (...args) => {
      let response = await originalFetch(...args)

      if (response.status === 401 && !args[0].includes('/auth/refresh')) {
        console.log('⚠️ Respuesta 401, intentando refrescar token...')
        
        const refreshed = await authStore.refreshToken()
        
        if (refreshed) {
          console.log('✅ Token refrescado, reintentando petición...')
          response = await originalFetch(...args)
        } else {
          console.log('❌ No se pudo refrescar, cerrando sesión...')
          authStore.user = null
          authStore.isAuthenticated = false
        }
      }

      return response
    }

    app.config.globalProperties.$auth = authStore
  }
}