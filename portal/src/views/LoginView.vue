<template>
  <div class="login-page">
    <h1>Bienvenido</h1>
    <p>Inicia sesión con tu cuenta de Google</p>
    <GoogleLoginButton />
  </div>
</template>

<script setup>
import GoogleLoginButton from '@/components/GoogleLogInButton.vue'
</script>

<style scoped>
.login-page {
  max-width: 400px;
  margin: 100px auto;
  text-align: center;
  font-family: 'Roboto', sans-serif;
}

h1 {
  color: #202124;
  margin-bottom: 8px;
}

p {
  color: #5f6368;
  margin-bottom: 32px;
}
</style>