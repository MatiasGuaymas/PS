import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/stores/authStore'

export function useAuth() {
    const router = useRouter()

    const logout = async () => {
        await authStore.logout()
        router.push('/login')
    }

    onMounted(() => {
        // Solo verificar si aún no se ha verificado
        if (authStore.user === null && !authStore.loading) {
        authStore.checkAuth()
        }
    })

    return {
        user: authStore.user,
        loading: authStore.loading,
        logout,
        checkAuth: authStore.checkAuth.bind(authStore),
        isAuthenticated: authStore.isAuthenticated.bind(authStore)
    }
}