<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/stores/authStore'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://localhost:5000/auth/authenticate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      credentials: 'include',
      body: new URLSearchParams({
        email: email.value,
        password: password.value
      })
    })
    
    if (response.ok) {
      await authStore.checkAuth()
      
      router.push('/')
    } else {
      const status = response.status
      if (status === 401) {
        error.value = 'Credenciales inválidas. Verifica tu email y contraseña.'
      } else if (status === 400) {
        error.value = 'Por favor, completa todos los campos.'
      } else if (status === 403) {
        error.value = 'Tu cuenta está desactivada. Contacta al administrador.'
      } else {
        error.value = 'Error al iniciar sesión. Intenta nuevamente.'
      }
    }
  } catch (err) {
    error.value = 'Error al iniciar sesión'
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}

const loginWithGoogle = () => {
  window.location.href = 'http://localhost:5000/auth/login-google?origin=public'
}
</script>

<template>
  <div class="login-view">
    <div class="container py-5">
      <div class="row justify-content-center align-items-center min-vh-80">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <img src="/Logo.jpg" alt="Logo" class="logo-image me-2">
                <h1 class="fw-bold mb-2">
                  <span class="gradient-text-1">Puff</span>
                  <span class="gradient-text-2">-</span>
                  <span class="gradient-text-3">Tóricos</span>
                </h1>
                <p class="text-muted">Inicia sesión para continuar</p>
              </div>

              <!-- Formulario tradicional -->
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label fw-semibold">
                    <i class="bi bi-envelope me-1"></i>
                    Correo Electrónico
                  </label>
                  <input 
                    type="email" 
                    class="form-control form-control-lg rounded-3" 
                    id="email" 
                    v-model="email"
                    placeholder="tu@email.com"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label fw-semibold">
                    <i class="bi bi-lock me-1"></i>
                    Contraseña
                  </label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg rounded-3" 
                    id="password" 
                    v-model="password"
                    placeholder="••••••••"
                    required
                  >
                </div>

                <transition name="slide-fade">
                  <div 
                    v-if="error" 
                    class="alert alert-danger alert-dismissible fade show d-flex align-items-center mb-3" 
                    role="alert"
                  >
                    <i class="bi bi-exclamation-triangle-fill me-2 flex-shrink-0"></i>
                    <div class="flex-grow-1">{{ error }}</div>
                    <button 
                      type="button" 
                      class="btn-close" 
                      @click="error = ''"
                      aria-label="Close"
                    ></button>
                  </div>
                </transition>
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg w-100 py-3 rounded-3 fw-bold mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Iniciando sesión...
                  </span>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Iniciar Sesión
                  </span>
                </button>
              </form>

              <div class="position-relative my-4">
                <hr>
                <span class="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
                  O continúa con
                </span>
              </div>

              <button 
                @click="loginWithGoogle" 
                class="btn btn-light btn-lg w-100 py-3 rounded-3 fw-bold d-flex align-items-center justify-content-center gap-2 shadow-sm"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 48 48">
                  <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
                  <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
                  <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
                  <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
                </svg>
                Continuar con Google
              </button>

              <p class="text-center mt-4 mb-0">
                ¿No tienes cuenta? 
                <RouterLink to="/registro" class="text-primary fw-semibold text-decoration-none">
                  Regístrate aquí
                </RouterLink>
              </p>

              <p class="text-center mt-2 mb-0">
                <a href="#" class="text-muted small text-decoration-none">
                  ¿Olvidaste tu contraseña?
                </a>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-6 d-none d-md-flex justify-content-center align-items-center">
          <div class="illustration-container text-center">
            <i class="bi bi-map display-1 text-primary mb-4"></i>
            <h2 class="mt-4 gradient-text-1 fw-bold">
              ¡Bienvenido de nuevo!
            </h2>
            <p class="text-muted px-4">
              Explora los mejores sitios turísticos de La Plata
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  padding-top: 2rem;
}

.min-vh-80 {
  min-height: 80vh;
}

.logo-login {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.98);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15) !important;
}

.gradient-text-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-2 {
  background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-3 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-control {
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.15);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-light {
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.btn-light:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alert {
  border-radius: 12px;
  border: none;
}

.illustration-container {
  animation: fadeInUp 0.8s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .login-view {
    padding-top: 1rem;
  }

  .card-body {
    padding: 2rem !important;
  }

  .logo-login {
    width: 60px;
    height: 60px;
  }
}

.form-control.is-invalid {
  border-color: #dc3545;
  animation: shake 0.5s;
}

.form-control.is-invalid:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

/* Animación de sacudida para inputs inválidos */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* ✅ Estilos mejorados para el alert */
.alert {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.alert .btn-close {
  padding: 0.5rem;
}

/* ✅ Animación de entrada/salida del alert */
.slide-fade-enter-active {
  animation: slideDown 0.3s ease;
}

.slide-fade-leave-active {
  animation: slideUp 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}
</style>