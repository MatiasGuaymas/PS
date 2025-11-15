import { reactive } from 'vue'

export const authStore = reactive({
user: null,
loading: true,

async checkAuth() {
    this.loading = true
    try {
    const res = await fetch('http://localhost:5000/auth/me', {
        credentials: 'include'
    })
    if (res.ok) {
        this.user = await res.json()
    } else {
        this.user = null
    }
    } catch (err) {
    console.error('Error al verificar autenticación:', err)
    this.user = null
    } finally {
    this.loading = false
    }
},

async logout() {
    try {
    await fetch('http://localhost:5000/auth/logout', {
        method: 'GET',
        credentials: 'include'
    })
    this.user = null
    } catch (err) {
    console.error('Error al cerrar sesión:', err)
    }
},

isAuthenticated() {
    return this.user !== null
}
})