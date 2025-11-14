<template>
  <div class="access-denied">
    <h2>🛑 Acceso Bloqueado</h2>
    <p>Estamos temporalmente fuera de servicio.</p>
    <div class="message-box">
      <strong>Mensaje del Servidor:</strong>
      <p>{{ decodedMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  props: ['message'],
  computed: {
    decodedMessage() {
      return decodeURIComponent(this.message);
    }
  }
}
</script>

<style scoped>
.access-denied {
  text-align: center;
  padding: 50px;
}
.message-box {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ff0000;
  background-color: #ffeaea;
  display: inline-block;
}
</style>