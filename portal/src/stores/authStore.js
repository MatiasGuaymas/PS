import { reactive } from 'vue'

const BASE_URL = `${window.location.origin}`

export const authStore = reactive({
    user: null,
    loading: true,

    async checkAuth() {
        this.loading = true
        try {
            const res = await fetch(`${BASE_URL}/auth/me`, {
                credentials: 'include'
            })
            if (res.ok) {
                this.user = await res.json()
            } else {
                this.user = null
            }
        } catch (err) {
            console.error('Error al verificar autenticación')
            this.user = null
        } finally {
            this.loading = false
        }
    },

    async logout() {
        try {
            await fetch(`${BASE_URL}/auth/logout`, {
                method: 'GET',
                credentials: 'include'
            })
            this.user = null
        } catch (err) {
            console.error('Error al cerrar sesión')
        }
    },

    isAuthenticated() {
        return this.user !== null
    }
})