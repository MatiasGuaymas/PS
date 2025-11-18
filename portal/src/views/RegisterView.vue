<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '@/stores/authStore'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://admin-grupo21.proyecto2025.linti.unlp.edu.ar';

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})

// Datos del formulario
const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const error = ref('')
const passwordVisible = ref(false)
const confirmPasswordVisible = ref(false)

// ✅ Estado para la imagen
const avatarFile = ref(null)
const avatarPreview = ref(null)

// Validación de contraseña
const passwordStrength = ref({
  score: 0,
  label: '',
  color: ''
})

// Calcular fortaleza de la contraseña
const checkPasswordStrength = () => {
  const password = formData.value.password
  let score = 0
  
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
  if (/\d/.test(password)) score++
  if (/[^a-zA-Z\d]/.test(password)) score++
  
  if (score <= 1) {
    passwordStrength.value = { score, label: 'Débil', color: 'danger' }
  } else if (score <= 3) {
    passwordStrength.value = { score, label: 'Media', color: 'warning' }
  } else {
    passwordStrength.value = { score, label: 'Fuerte', color: 'success' }
  }
}

// ✅ Manejar selección de imagen
const handleImageSelect = (event) => {
  const file = event.target.files[0]
  
  if (!file) return
  
  // Validar tipo de archivo
  if (!file.type.startsWith('image/')) {
    error.value = 'Por favor selecciona una imagen válida (JPG, PNG, GIF, WEBP)'
    event.target.value = ''
    return
  }
  
  // Validar tamaño (max 2MB)
  if (file.size > 2 * 1024 * 1024) {
    error.value = 'La imagen debe ser menor a 2MB'
    event.target.value = ''
    return
  }
  
  avatarFile.value = file
  
  // Crear preview
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  
  // Limpiar error si había
  error.value = ''
}

// ✅ Remover imagen seleccionada
const removeImage = () => {
  avatarFile.value = null
  avatarPreview.value = null
  const fileInput = document.getElementById('avatar')
  if (fileInput) fileInput.value = ''
}

// Validar formulario
const validateForm = () => {
  if (!formData.value.first_name || !formData.value.last_name) {
    error.value = 'Por favor, completa tu nombre y apellido'
    return false
  }
  
  if (!formData.value.email) {
    error.value = 'Por favor, ingresa tu correo electrónico'
    return false
  }
  
  // Validar formato de email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    error.value = 'Por favor, ingresa un correo electrónico válido'
    return false
  }
  
  if (!formData.value.password) {
    error.value = 'Por favor, ingresa una contraseña'
    return false
  }
  
  if (formData.value.password.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres'
    return false
  }
  
  if (formData.value.password !== formData.value.confirmPassword) {
    error.value = 'Las contraseñas no coinciden'
    return false
  }
  
  return true
}

// Manejar registro
const handleRegister = async () => {
  error.value = ''
  
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    console.log('📝 Enviando registro...')
    
    // ✅ Usar FormData si hay imagen, sino JSON
    let requestBody
    let headers = {}
    
    if (avatarFile.value) {
      // Si hay imagen, usar FormData
      const formDataToSend = new FormData()
      formDataToSend.append('first_name', formData.value.first_name)
      formDataToSend.append('last_name', formData.value.last_name)
      formDataToSend.append('email', formData.value.email)
      formDataToSend.append('password', formData.value.password)
      formDataToSend.append('avatar', avatarFile.value)
      
      requestBody = formDataToSend
      // No establecer Content-Type, el navegador lo hará automáticamente con boundary
    } else {
      // Si no hay imagen, usar JSON
      headers['Content-Type'] = 'application/json'
      requestBody = JSON.stringify({
        first_name: formData.value.first_name,
        last_name: formData.value.last_name,
        email: formData.value.email,
        password: formData.value.password
      })
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: headers,
      credentials: 'include',
      body: requestBody
    })
    
    console.log('📡 Respuesta status:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ Registro exitoso:', data)
      
      // Pequeño delay para que la cookie se establezca
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Verificar autenticación
      await authStore.checkAuth()
      
      console.log('👤 Usuario cargado:', authStore.user)
      
      // Redirigir
      router.push('/')
    } else {
      const data = await response.json()
      console.error('❌ Error en registro:', data)
      
      if (response.status === 409) {
        error.value = 'Este correo electrónico ya está registrado'
      } else if (response.status === 400) {
        error.value = data.error || 'Datos inválidos. Verifica los campos.'
      } else {
        error.value = 'Error al crear la cuenta. Intenta nuevamente.'
      }
    }
  } catch (err) {
    console.error('❌ Error de red:', err)
    error.value = 'Error de conexión. Verifica tu internet o intenta más tarde.'
  } finally {
    loading.value = false
  }
}

// Login con Google
const registerWithGoogle = () => {
  window.location.href = `${API_BASE_URL}/auth/login-google?origin=public`
}
</script>

<template>
  <div class="register-view">
    <div class="container py-5">
      <div class="row justify-content-center align-items-center min-vh-80">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body p-5">
              <!-- Logo y título -->
              <div class="text-center mb-4">
                <div class="logo-icon mb-3">
                  <i class="bi bi-compass-fill"></i>
                </div>
                <h1 class="fw-bold mb-2">
                  <span class="gradient-text-1">Puff</span>
                  <span class="gradient-text-2">-</span>
                  <span class="gradient-text-3">Tóricos</span>
                </h1>
                <p class="text-muted">Crea tu cuenta para comenzar</p>
              </div>

              <!-- Formulario de registro -->
              <form @submit.prevent="handleRegister">
                <div class="row g-3">
                  <!-- ✅ Campo de imagen de perfil -->
                  <div class="col-12">
                    <label class="form-label fw-semibold">
                      <i class="bi bi-camera me-1"></i>
                      Foto de Perfil (Opcional)
                    </label>
                    
                    <div class="avatar-upload-container">
                      <!-- Preview del avatar -->
                      <div class="avatar-preview-wrapper">
                        <div 
                          v-if="avatarPreview" 
                          class="avatar-preview"
                          :style="{ backgroundImage: `url(${avatarPreview})` }"
                        >
                          <button 
                            type="button" 
                            class="btn-remove-avatar"
                            @click="removeImage"
                            title="Eliminar imagen"
                          >
                            <i class="bi bi-x-lg"></i>
                          </button>
                        </div>
                        
                        <div v-else class="avatar-placeholder">
                          <i class="bi bi-person-circle"></i>
                          <p class="mb-0 mt-2 small text-muted">Sin foto</p>
                        </div>
                      </div>
                      
                      <!-- Botón para seleccionar archivo -->
                      <div class="avatar-upload-actions">
                        <input 
                          type="file" 
                          id="avatar" 
                          class="d-none"
                          accept="image/*"
                          @change="handleImageSelect"
                        >
                        <label 
                          for="avatar" 
                          class="btn btn-outline-primary btn-sm w-100"
                        >
                          <i class="bi bi-cloud-upload me-1"></i>
                          {{ avatarPreview ? 'Cambiar foto' : 'Seleccionar foto' }}
                        </label>
                        <small class="text-muted d-block mt-2 text-center">
                          JPG, PNG, GIF o WEBP • Máx 2MB
                        </small>
                      </div>
                    </div>
                  </div>

                  <!-- Nombre -->
                  <div class="col-md-6">
                    <label for="first_name" class="form-label fw-semibold">
                      <i class="bi bi-person me-1"></i>
                      Nombre
                    </label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg rounded-3" 
                      :class="{ 'is-invalid': error }"
                      id="first_name" 
                      v-model="formData.first_name"
                      placeholder="Juan"
                      required
                    >
                  </div>

                  <!-- Apellido -->
                  <div class="col-md-6">
                    <label for="last_name" class="form-label fw-semibold">
                      <i class="bi bi-person me-1"></i>
                      Apellido
                    </label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg rounded-3" 
                      :class="{ 'is-invalid': error }"
                      id="last_name" 
                      v-model="formData.last_name"
                      placeholder="Pérez"
                      required
                    >
                  </div>

                  <!-- Email -->
                  <div class="col-12">
                    <label for="email" class="form-label fw-semibold">
                      <i class="bi bi-envelope me-1"></i>
                      Correo Electrónico
                    </label>
                    <input 
                      type="email" 
                      class="form-control form-control-lg rounded-3" 
                      :class="{ 'is-invalid': error }"
                      id="email" 
                      v-model="formData.email"
                      placeholder="tu@email.com"
                      required
                    >
                  </div>

                  <!-- Contraseña -->
                  <div class="col-12">
                    <label for="password" class="form-label fw-semibold">
                      <i class="bi bi-lock me-1"></i>
                      Contraseña
                    </label>
                    <div class="input-group">
                      <input 
                        :type="passwordVisible ? 'text' : 'password'" 
                        class="form-control form-control-lg rounded-start-3" 
                        :class="{ 'is-invalid': error }"
                        id="password" 
                        v-model="formData.password"
                        @input="checkPasswordStrength"
                        placeholder="••••••••"
                        required
                      >
                      <button 
                        class="btn btn-outline-secondary rounded-end-3" 
                        type="button"
                        @click="passwordVisible = !passwordVisible"
                      >
                        <i :class="passwordVisible ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                      </button>
                    </div>
                    
                    <!-- Indicador de fortaleza -->
                    <div v-if="formData.password" class="mt-2">
                      <div class="progress" style="height: 4px;">
                        <div 
                          class="progress-bar" 
                          :class="`bg-${passwordStrength.color}`"
                          :style="{ width: `${(passwordStrength.score / 5) * 100}%` }"
                        ></div>
                      </div>
                      <small :class="`text-${passwordStrength.color}`">
                        Fortaleza: {{ passwordStrength.label }}
                      </small>
                    </div>
                    
                    <small class="text-muted">
                      Mínimo 8 caracteres. Usa mayúsculas, números y símbolos.
                    </small>
                  </div>

                  <!-- Confirmar Contraseña -->
                  <div class="col-12">
                    <label for="confirmPassword" class="form-label fw-semibold">
                      <i class="bi bi-lock-fill me-1"></i>
                      Confirmar Contraseña
                    </label>
                    <div class="input-group">
                      <input 
                        :type="confirmPasswordVisible ? 'text' : 'password'" 
                        class="form-control form-control-lg rounded-start-3" 
                        :class="{ 'is-invalid': error && formData.password !== formData.confirmPassword }"
                        id="confirmPassword" 
                        v-model="formData.confirmPassword"
                        placeholder="••••••••"
                        required
                      >
                      <button 
                        class="btn btn-outline-secondary rounded-end-3" 
                        type="button"
                        @click="confirmPasswordVisible = !confirmPasswordVisible"
                      >
                        <i :class="confirmPasswordVisible ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                      </button>
                    </div>
                    
                    <!-- Validación visual -->
                    <div v-if="formData.confirmPassword" class="mt-2">
                      <small 
                        v-if="formData.password === formData.confirmPassword" 
                        class="text-success"
                      >
                        <i class="bi bi-check-circle-fill me-1"></i>
                        Las contraseñas coinciden
                      </small>
                      <small 
                        v-else 
                        class="text-danger"
                      >
                        <i class="bi bi-x-circle-fill me-1"></i>
                        Las contraseñas no coinciden
                      </small>
                    </div>
                  </div>

                  <!-- Mensaje de error -->
                  <transition name="slide-fade">
                    <div 
                      v-if="error" 
                      class="col-12"
                    >
                      <div class="alert alert-danger alert-dismissible fade show d-flex align-items-center" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2 flex-shrink-0"></i>
                        <div class="flex-grow-1">{{ error }}</div>
                        <button 
                          type="button" 
                          class="btn-close" 
                          @click="error = ''"
                          aria-label="Close"
                        ></button>
                      </div>
                    </div>
                  </transition>

                  <!-- Botón de registro -->
                  <div class="col-12">
                    <button 
                      type="submit" 
                      class="btn btn-primary btn-lg w-100 py-3 rounded-3 fw-bold"
                      :disabled="loading"
                    >
                      <span v-if="loading">
                        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creando cuenta...
                      </span>
                      <span v-else>
                        <i class="bi bi-person-plus me-2"></i>
                        Crear Cuenta
                      </span>
                    </button>
                  </div>
                </div>
              </form>

              <!-- Divider -->
              <div class="position-relative my-4">
                <hr>
                <span class="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
                  O regístrate con
                </span>
              </div>


              <!-- Link de login -->
              <p class="text-center mt-4 mb-0">
                ¿Ya tienes cuenta? 
                <RouterLink to="/login" class="text-primary fw-semibold text-decoration-none">
                  Inicia sesión aquí
                </RouterLink>
              </p>
            </div>
          </div>
        </div>

        <!-- Columna de ilustración -->
        <div class="col-md-6 d-none d-md-flex justify-content-center align-items-center">
          <div class="illustration-container text-center">
            <i class="bi bi-person-plus-fill display-1 text-primary mb-4"></i>
            <h2 class="mt-4 gradient-text-1 fw-bold">
              ¡Únete a nosotros!
            </h2>
            <p class="text-muted px-4">
              Descubre y comparte los mejores lugares turísticos de Argentina
            </p>
            <div class="features mt-4">
              <div class="feature-item">
                <i class="bi bi-star-fill text-warning"></i>
                <span>Escribe reseñas</span>
              </div>
              <div class="feature-item">
                <i class="bi bi-heart-fill text-danger"></i>
                <span>Guarda favoritos</span>
              </div>
              <div class="feature-item">
                <i class="bi bi-map-fill text-primary"></i>
                <span>Explora sitios</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  padding: 2rem 0;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  font-size: 2.5rem;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.gradient-text-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.gradient-text-2 {
  color: #667eea;
}

.avatar-upload-container {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #dee2e6;
  transition: all 0.3s ease;
}

.avatar-upload-container:hover {
  border-color: #667eea;
  background: #f0f3ff;
}

.avatar-preview-wrapper {
  flex-shrink: 0;
}

.avatar-preview,
.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.avatar-preview {
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 3px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-placeholder {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  color: #adb5bd;
  font-size: 3rem;
}

.btn-remove-avatar {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(220, 53, 69, 0.9);
  color: white;
  border: 2px solid white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.75rem;
  padding: 0;
}

.btn-remove-avatar:hover {
  background: #dc3545;
  transform: scale(1.1);
}

.avatar-upload-actions {
  flex-grow: 1;
}

.gradient-text-3 {
  background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card {
  border: none;
}

.form-label {
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-control {
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.form-control.is-invalid {
  border-color: #dc3545;
  animation: shake 0.5s;
}

.btn {
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-light {
  background: white;
  border: 2px solid #e9ecef;
}

.btn-light:hover {
  background: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alert {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
}

.features {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  color: #495057;
}

.feature-item i {
  font-size: 1.5rem;
}

/* Animaciones */
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

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* Responsive */
@media (max-width: 768px) {
  .register-view {
    padding: 1rem 0;
  }
  
  .card-body {
    padding: 2rem !important;
  }
  
  .logo-icon {
    width: 60px;
    height: 60px;
    font-size: 2rem;
  }
}
</style>