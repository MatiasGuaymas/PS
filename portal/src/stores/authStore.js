import { reactive } from 'vue'

const BASE_URL = `${window.location.origin}`
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';

export const authStore = reactive({
  user: null,
  loading: true,
  isAuthenticated: false,  // Inicializar como propiedad

  async checkAuth() {
    this.loading = true
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        credentials: 'include'  
      })

      if (response.ok) {
        const data = await response.json()
        this.user = data
        this.isAuthenticated = true
        return true
      } else if (response.status === 401) {
        
        // Intentar refrescar el token automáticamente
        const refreshed = await this.refreshToken()
        
        if (refreshed) {
          return await this.checkAuth()
        } else {
          this.user = null
          this.isAuthenticated = false
          return false
        }
      } else {
        this.user = null
        this.isAuthenticated = false
        return false
      }
    } catch (error) {
      this.user = null
      this.isAuthenticated = false
      return false
    } finally {
      this.loading = false
    }
  },

  async refreshToken() {
    try {
      
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      })

      if (response.ok) {
        return true
      }
      
      return false
    } catch (error) {
      return false
    }
  },

  async logout() {
  try {
        
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',  // Esto envía las cookies
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    
    const setCookieHeaders = response.headers.get('set-cookie')

    this.user = null
    this.isAuthenticated = false

    if (response.ok) {
      const data = await response.json()
    } else {
    }
          
    return true
    
  } catch (error) {
    console.error('Error en logout:', error)
    this.user = null
    this.isAuthenticated = false
    return false
  }
},

  // Nuevo método para limpiar cookies manualmente desde el cliente
  clearCookies() {
    
    // Intentar borrar las cookies configurándolas con fecha de expiración pasada
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax'
    document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax'
    
  },

  hasValidSession() {
    return this.isAuthenticated && this.user !== null
  },

  // Método para verificar sesión válida
  hasValidSession() {
    return this.isAuthenticated && this.user !== null
  }
})