<template>
<div class="google-container">
    <button v-if="!user && !loading" @click="login" class="google-btn">
    <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google" width="18">
    <span>Iniciar con Google</span>
    </button>

    <div v-else-if="loading" class="loading">
    Verificando sesión...
    </div>

    <div v-else class="user-info">
    <img :src="user.picture" :alt="user.name" class="avatar" />
    <span>{{ user.name }}</span>
    <button @click="logout" class="logout-btn">Cerrar sesión</button>
    </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const loading = ref(true)
const router = useRouter()

const API_BASE_URL = import.meta.env.VITE_API_URL;

const checkSession = async () => {
try {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
    credentials: 'include'
    })
    if (res.ok) {
    user.value = await res.json()
    }
} catch (err) {
    console.error('Error al verificar sesión')
} finally {
    loading.value = false
}
}

const login = () => {
window.location.href = `${API_BASE_URL}/auth/login-google`
}

const logout = async () => {
await fetch(`${API_BASE_URL}/auth/logout`, { credentials: 'include' })
user.value = null
router.push('/')
}

onMounted(() => {
checkSession()
})
</script>

<style scoped>
.google-container {
text-align: center;
padding: 2rem;
}

.google-btn {
display: inline-flex;
align-items: center;
gap: 10px;
background: white;
border: 1px solid #dadce0;
border-radius: 4px;
padding: 10px 20px;
font-family: 'Roboto', sans-serif;
font-size: 14px;
font-weight: 500;
cursor: pointer;
box-shadow: 0 1px 2px rgba(0,0,0,0.1);
transition: all 0.2s;
}

.google-btn:hover {
box-shadow: 0 2px 4px rgba(0,0,0,0.15);
background: #f8f9fa;
}

.loading {
color: #5f6368;
font-style: italic;
}

.user-info {
display: flex;
align-items: center;
gap: 12px;
flex-wrap: wrap;
justify-content: center;
}

.avatar {
width: 40px;
height: 40px;
border-radius: 50%;
object-fit: cover;
}

.logout-btn {
background: #f44336;
color: white;
border: none;
padding: 6px 12px;
border-radius: 4px;
font-size: 13px;
cursor: pointer;
}

.logout-btn:hover {
background: #d32f2f;
}
</style>