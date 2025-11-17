import { reactive } from 'vue'

const BASE_URL = `${window.location.origin}`

export const authStore = reactive({
  user: null,
  loading: true,
  isAuthenticated: false,  // ✅ Inicializar como propiedad

  async checkAuth() {
    this.loading = true
    try {
      const response = await fetch('http://localhost:5000/auth/me', {
        credentials: 'include'  
      })

      if (response.ok) {
        const data = await response.json()
        this.user = data
        this.isAuthenticated = true
        console.log('✅ Usuario autenticado con JWT:', data)
        console.log('📸 Avatar:', data.avatar)
        return true
      } else if (response.status === 401) {
        console.log('⚠️ Token expirado, intentando refrescar...')
        
        // ✅ Intentar refrescar el token automáticamente
        const refreshed = await this.refreshToken()
        
        if (refreshed) {
          console.log('✅ Token refrescado, reintentando autenticación...')
          return await this.checkAuth()
        } else {
          console.log('❌ No se pudo refrescar el token')
          this.user = null
          this.isAuthenticated = false
          return false
        }
      } else {
        console.error('❌ Error en /auth/me:', response.status)
        this.user = null
        this.isAuthenticated = false
        return false
      }
    } catch (error) {
      console.error('❌ Error verificando autenticación:', error)
      this.user = null
      this.isAuthenticated = false
      return false
    } finally {
      this.loading = false
    }
  },

  async refreshToken() {
    try {
      console.log('🔄 Intentando refrescar token...')
      
      const response = await fetch('http://localhost:5000/auth/refresh', {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        console.log('✅ Token refrescado exitosamente')
        return true
      }
      
      console.log('❌ No se pudo refrescar el token')
      return false
    } catch (error) {
      console.error('❌ Error refrescando token:', error)
      return false
    }
  },

  async logout() {
    try {
      console.log('🚪 Cerrando sesión...')
      
      // ✅ Llamar al endpoint de logout del backend
      const response = await fetch('http://localhost:5000/auth/logout', {
        method: 'POST',  // ✅ Cambiar a POST
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('📡 Respuesta de logout:', response.status)

      // ✅ Limpiar estado local INDEPENDIENTEMENTE de la respuesta
      this.user = null
      this.isAuthenticated = false

      if (response.ok) {
        const data = await response.json()
        console.log('✅ Sesión cerrada en el backend:', data.message)
      } else {
        console.warn('⚠️ Respuesta no OK del backend, pero limpiamos local')
      }
      
      // ✅ FORZAR eliminación de cookies desde el cliente también
      this.clearCookies()
      
      return true
      
    } catch (error) {
      console.error('❌ Error al cerrar sesión:', error)
      // ✅ Limpiar de todas formas
      this.user = null
      this.isAuthenticated = false
      this.clearCookies()
      return false
    }
  },

  // ✅ Nuevo método para limpiar cookies manualmente desde el cliente
  clearCookies() {
    console.log('🍪 Limpiando cookies manualmente...')
    
    // Intentar borrar las cookies configurándolas con fecha de expiración pasada
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax'
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax'
    
    console.log('✅ Cookies limpiadas desde el cliente')
  },

  hasValidSession() {
    return this.isAuthenticated && this.user !== null
  },

  // ✅ Método para verificar sesión válida
  hasValidSession() {
    return this.isAuthenticated && this.user !== null
  }
})