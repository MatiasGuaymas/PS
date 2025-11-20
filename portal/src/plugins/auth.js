import { authStore } from '@/stores/authStore'

export default {
  install: (app) => {
    authStore.checkAuth()

    const originalFetch = window.fetch
    window.fetch = async (...args) => {
      let response = await originalFetch(...args)

      if (response.status === 401 && !args[0].includes('/auth/refresh')) {
        
        const refreshed = await authStore.refreshToken()
        
        if (refreshed) {
          response = await originalFetch(...args)
        } else {
          authStore.user = null
          authStore.isAuthenticated = false
        }
      }

      return response
    }

    app.config.globalProperties.$auth = authStore
  }
}