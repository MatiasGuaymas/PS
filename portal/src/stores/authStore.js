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
    console.log('=' .repeat(80))
    console.log('🚪 LOGOUT - authStore')
    
    // ✅ Ver qué cookies hay ANTES del logout
    console.log('📋 Cookies ANTES de logout:', document.cookie)
    
    // ✅ Llamar al backend
    console.log('📡 Enviando POST /auth/logout...')
    
    const response = await fetch('http://localhost:5000/auth/logout', {
      method: 'POST',
      credentials: 'include',  // ✅ Esto envía las cookies
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    console.log(`📡 Respuesta del backend: ${response.status}`)
    
    // ✅ Ver los headers Set-Cookie de la respuesta
    const setCookieHeaders = response.headers.get('set-cookie')
    console.log('📋 Set-Cookie headers recibidos:', setCookieHeaders)

    // ✅ Limpiar estado local
    this.user = null
    this.isAuthenticated = false

    if (response.ok) {
      const data = await response.json()
      console.log('✅ Backend confirmó logout:', data.message)
    } else {
      console.warn('⚠️ Backend error, pero estado local limpiado')
    }
    
    // ✅ Ver qué cookies hay DESPUÉS del logout
    console.log('📋 Cookies DESPUÉS de logout:', document.cookie)
    
    console.log('✅ LOGOUT completado')
    console.log('=' .repeat(80))
    
    return true
    
  } catch (error) {
    console.error('❌ Error en logout:', error)
    this.user = null
    this.isAuthenticated = false
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